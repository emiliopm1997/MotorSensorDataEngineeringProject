from typing import List, Optional

import pandas as pd
from logger import LOGGER
from processor import Processor


class CycleCutter(Processor):
    """Cut the cycles based on the raw data."""

    voltage_threshold = 4  # kV
    time_threshold = 2  # s

    @classmethod
    def run(cls, **kwargs) -> pd.DataFrame:
        """Process the data.

        Returns
        -------
        pd.DataFrame
            The processed data.
        """
        data = kwargs.get("data")
        data["date_time"] = data["date_time"].apply(pd.Timestamp)
        cycle_id_start = kwargs.get("cycle_id_start", 0)

        cycle_periods_data = cls.get_cycle_beginnings_and_endings(
            data, cycle_id_start
        )

        cls.processed_data = cls.cut_cycles(data, cycle_periods_data)

    @classmethod
    def get_cycle_beginnings_and_endings(
        cls, data: pd.DataFrame, cycle_id_start: Optional[int] = 0
    ) -> pd.DataFrame:
        """Find the beginning and endings of cycles.

        Parameters
        ----------
        data : pd.DataFrame
            The data to extract cycles from.
        cycle_id_start : Optional[int]
            The starting id to categorize cycles.
        Returns
        -------
        pd.DataFrame
            The information of the cycles.
        """
        data["date_time"] = data["date_time"].apply(pd.Timestamp)
        data_h_voltage = data[data["voltage"] > cls.voltage_threshold]

        # This strictly occurs when there are no high voltages.
        if data_h_voltage.empty:
            LOGGER.warning("There are no cycles within the data...")
            return pd.DataFrame()

        # Check if is incomplete.
        exclude_last_cycle = (
            data["date_time"].iloc[-1] == data_h_voltage["date_time"].iloc[-1]
        )

        cycle_starts = cls._get_cycle_starts(data_h_voltage.copy(True))
        cycle_ends = cls._get_cycle_ends(
            data_h_voltage.copy(True), exclude_last_cycle
        )

        # This could occur when a cycle is incomplete
        if (len(cycle_starts) == 0) or (len(cycle_ends) == 0):
            LOGGER.warning("There are no cycles within the data...")
            return pd.DataFrame()

        return cls._get_periods_data(cycle_starts, cycle_ends, cycle_id_start)

    @classmethod
    def _get_cycle_starts(cls, cycle_df: pd.DataFrame) -> List[pd.Timestamp]:
        """Get a list of all the cycles' starting points."""
        cycle_df["lagged_ts_f"] = cycle_df["date_time"].shift(1)
        cycle_df["diff_ts_f"] = cycle_df["date_time"] - cycle_df["lagged_ts_f"]
        cycle_starts = cycle_df[
            cycle_df["diff_ts_f"] > pd.Timedelta(seconds=cls.time_threshold)
        ]["date_time"].to_list()
        return cycle_starts

    @classmethod
    def _get_cycle_ends(
        cls, cycle_df: pd.DataFrame, exclude_last_cycle: Optional[bool] = False
    ) -> List[pd.Timestamp]:
        """Get a list of all the cycles' ending points."""
        cycle_df["lagged_ts_b"] = cycle_df["date_time"].shift(-1)
        cycle_df["diff_ts_b"] = cycle_df["lagged_ts_b"] - cycle_df["date_time"]
        cycle_ends = cycle_df[
            cycle_df["diff_ts_b"] > pd.Timedelta(seconds=cls.time_threshold)
        ]["date_time"].to_list()

        # So last cycle is not excluded unless it is incomplete.
        if not exclude_last_cycle:
            cycle_ends += [cycle_df["date_time"].iloc[-1]]
        return cycle_ends

    @classmethod
    def _get_periods_data(
        cls,
        cycle_starts: List[pd.Timestamp],
        cycle_ends: List[pd.Timestamp],
        id_start: int,
    ) -> pd.DataFrame:
        """Merge the information and assign an id.

        Parameters
        ----------
        cycle_starts : List[pd.Timestamp]
            The list of the different cycle starts.
        cycle_ends : List[pd.Timestamp]
            The list of the different cycle ends.
        id_start : int
            The starting id to be assigned to the cycles.

        Returns
        -------
        pd.DataFrame
            _description_
        """
        # Sort timestamps
        cycle_starts = sorted(cycle_starts)
        cycle_ends = sorted(cycle_ends)

        # Filter out incomplete cycles
        if cycle_starts[0] > cycle_ends[0]:
            cycle_ends = cycle_ends[1:]
        if cycle_starts[-1] > cycle_ends[-1]:
            cycle_starts = cycle_starts[:-1]

        ids = [i + id_start for i in range(len(cycle_starts))]
        df_periods = pd.DataFrame(
            {
                "cycle_id": ids,
                "cycle_start": cycle_starts,
                "cycle_end": cycle_ends,
            }
        )
        return df_periods

    @classmethod
    def cut_cycles(
        cls, data: pd.DataFrame, cycle_period_data: pd.DataFrame
    ) -> pd.DataFrame:
        """Cut the data cycles.

        Parameters
        ----------
        data : pd.DataFrame
            The data to extract cycles from.
        cycle_period_data : pd.DataFrame
            The data with beginnings and endings of the cycles.

        Returns
        -------
        pd.DataFrame
            The data within the cycles.
        """
        cycles_data = pd.DataFrame()
        data["date_time"] = data["date_time"].apply(pd.Timestamp)

        for index, row in cycle_period_data.iterrows():
            cycle_id = row["cycle_id"]
            start = row["cycle_start"]
            end = row["cycle_end"]
            filtering_cond = (data["date_time"] >= start) & (
                data["date_time"] <= end
            )
            cycle_data = data[filtering_cond]
            cycles_data = pd.concat(
                [
                    cycles_data,
                    pd.DataFrame(
                        {
                            "unix_time": cycle_data["unix_time"].to_list(),
                            "date_time": cycle_data["date_time"].to_list(),
                            "cycle_id": [
                                cycle_id for _ in range(len(cycle_data))
                            ],
                            "voltage": cycle_data["voltage"].to_list(),
                        }
                    ),
                ],
                axis=0,
                ignore_index=True,
            )

        return cycles_data
