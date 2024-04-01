import pandas as pd
from pathlib import Path
import unittest

from cycles import CycleCutter

DATA_PATH = Path(
    "/workspaces/MotorSensorDataEngineeringProject/preprocessors/test/data"
)


class TestCycleCutter(unittest.TestCase):
    """Test Cycle cutter components."""

    @classmethod
    def setUpClass(cls):
        """Run once before everything."""
        cls.raw_data = pd.read_csv(DATA_PATH / "raw_data_for_test.csv")
        # cls.raw_data = raw_data.iloc[:-2, :]

        cls.cycle_periods = pd.read_csv(DATA_PATH / "cycle_periods.csv")
        cls.cycle_periods["cycle_start"] = cls.cycle_periods["cycle_start"]\
            .apply(pd.Timestamp)
        cls.cycle_periods["cycle_end"] = cls.cycle_periods["cycle_end"]\
            .apply(pd.Timestamp)

        cls.preprocessed_data = pd.read_csv(
            DATA_PATH / "preprocessed_data.csv"
        )
        cls.preprocessed_data["date_time"] = (
            cls.preprocessed_data["date_time"].apply(pd.Timestamp)
        )

    def test_get_cycle_beginning_and_end(self):
        """Test that beginnings and ends of cycles are as expected."""
        result = CycleCutter.get_cycle_beginnings_and_endings(self.raw_data)
        pd.testing.assert_frame_equal(result, self.cycle_periods)

    def test_cut_cycles(self):
        """Test that the cycles are cut as expected."""
        result = CycleCutter.cut_cycles(self.raw_data, self.cycle_periods)
        pd.testing.assert_frame_equal(result, self.preprocessed_data)

    def test_run(self):
        """Test that preprocessor runs as expected."""
        preprocessor = CycleCutter()
        preprocessor.run(data=self.raw_data)
        result = preprocessor.preprocessed_data

        pd.testing.assert_frame_equal(result, self.preprocessed_data)

        # Check that 9 cycles are cut.
        max_id = sorted(result["cycle_id"].unique())[-1]
        self.assertEqual(max_id, 8)

    def test_run_data_starts_within_cycle(self):
        """Test that preprocessor runs excludes incomplete cycle (start)."""
        raw_data = self.raw_data.copy(deep=True).iloc[10:, :]
        preprocessor = CycleCutter()
        preprocessor.run(data=raw_data)
        result = preprocessor.preprocessed_data

        # Check that 8 cycles are cut.
        max_id = sorted(result["cycle_id"].unique())[-1]
        self.assertEqual(max_id, 7)

    def test_run_data_ends_within_cycle(self):
        """Test that preprocessor runs excludes incomplete cycle (end)."""
        raw_data = self.raw_data.copy(deep=True).iloc[:-8, :]
        preprocessor = CycleCutter()
        preprocessor.run(data=raw_data)
        result = preprocessor.preprocessed_data

        # Check that 8 cycles are cut.
        max_id = sorted(result["cycle_id"].unique())[-1]
        self.assertEqual(max_id, 7)


if __name__ == '__main__':
    unittest.main()
