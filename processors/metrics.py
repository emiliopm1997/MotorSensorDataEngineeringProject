import math
import pandas as pd

from abc import ABC, abstractmethod
from typing import List

from processor import Processor


class Metric(ABC):
    """Generalized class metrics."""

    def __init__(self, data: pd.DataFrame):
        """Initialize attributes."""
        self.data = data
        self._value = None

    @property
    def value(self) -> float:
        """Get the value."""
        if not self._value:
            raise ValueError("Metric has not been run yet.")
        return self._value

    @value.setter
    def value(self, val):
        """Disable setting this value manually."""
        raise TypeError("Property cannot be set.")

    @abstractmethod
    def run(self):
        """Calculate the value of the metric."""
        raise NotImplementedError("'run' method hasn't been run yet.")


class MaxPoint(Metric):
    """The maximum point of the cycle."""

    name = "max_point"

    def run(self):
        """Calculate the value of the metric."""
        self._value = self.data["voltage"].max()


class Median(Metric):
    """The median of the cycle."""

    name = "median"

    def run(self):
        """Calculate the value of the metric."""
        self._value = self.data["voltage"].median()


class RMS(Metric):
    """The root mean squared of the cycle."""

    name = "root_mean_squared"

    def run(self):
        """Calculate the value of the metric."""
        self._value = math.sqrt(
            self.data["voltage"].apply(lambda x: x**2).sum() / len(self.data)
        )


class MetricsCalculator(Processor):
    """Calculate the metrics on the cut cycles."""

    metric_classes = [MaxPoint, Median, RMS]

    @classmethod
    def run(cls, **kwargs) -> pd.DataFrame:
        """Process the data.

        Returns
        -------
        pd.DataFrame
            The processed data.
        """
        data = kwargs.get("data")
        processed_data = pd.DataFrame()

        for cycle_id in data["cycle_id"].unique():
            metric_df = cls._get_metrics_data(data, cycle_id)
            processed_data = pd.concat(
                [processed_data, metric_df], axis=0, ignore_index=True
            )

        cls.processed_data = processed_data

    @staticmethod
    def _get_metric_ids(cycle_id: int, length: int) -> List[int]:
        suffixes = [
            f"0{x}"[-2:] for x in range(1, length + 1)
        ]
        return [int(f"{cycle_id}{suffix}") for suffix in suffixes]

    @classmethod
    def _calculate_metrics(cls, data: pd.DataFrame) -> List['Metric']:
        metrics = []
        for metric_class in cls.metric_classes:
            metric = metric_class(data)
            metric.run()
            metrics.append(metric)

        return metrics

    @classmethod
    def _get_metrics_data(
        cls,
        data: pd.DataFrame,
        cycle_id: int
    ) -> pd.DataFrame:
        data_portion = data[data["cycle_id"] == cycle_id]
        ref_unix_time = (
            data_portion["unix_time"].max()
            + data_portion["unix_time"].min()
        ) / 2

        ref_date_time = str(pd.to_datetime(ref_unix_time, unit='s'))
        
        metrics = cls._calculate_metrics(data_portion)
        
        metric_df = pd.DataFrame(
            {
                "metric_id": cls._get_metric_ids(
                    cycle_id, len(metrics)
                ),
                "cycle_id": [cycle_id for _ in range(len(metrics))],
                "ref_unix_time": [
                    ref_unix_time for _ in range(len(metrics))
                ],
                "ref_date_time": [
                    ref_date_time for _ in range(len(metrics))
                ],
                "metric_name": [metric.name for metric in metrics],
                "metric_value": [metric.value for metric in metrics],
            }
        )
        return metric_df

