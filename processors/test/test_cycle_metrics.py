import pandas as pd
from pathlib import Path
import unittest

from metrics import MetricsCalculator

DATA_PATH = Path(
    "/workspaces/MotorSensorDataEngineeringProject/processors/test/data"
)


class TestMetricsCalculator(unittest.TestCase):
    """Test metrics calculator components."""

    @classmethod
    def setUpClass(cls):
        """Run once before everything."""
        cls.raw_data = pd.read_csv(
            DATA_PATH / "cut_cycles_data.csv"
        )
        cls.metrics_data = pd.read_csv(
            DATA_PATH / "cycle_metrics.csv"
        )

    def test_run(self):
        """Test that processor runs as expected."""
        processor = MetricsCalculator()
        processor.run(data=self.raw_data)
        result = processor.processed_data
        pd.testing.assert_frame_equal(result, self.metrics_data)


if __name__ == '__main__':
    unittest.main()
