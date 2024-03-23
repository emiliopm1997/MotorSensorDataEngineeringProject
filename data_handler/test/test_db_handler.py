import pandas as pd
from pathlib import Path
from tempfile import NamedTemporaryFile
import unittest

from data_base import DataLakeHandler, DataWarehouseHandler

DATA_PATH = Path(
    "/workspaces/MotorSensorDataEngineeringProject/data_handler/test/data"
)


class TestDBHandlers(unittest.TestCase):
    """Abstract DB Handler tests."""

    def setUp(self):
        """Run before every test."""
        self.temp_file = NamedTemporaryFile(
            prefix=self.prefix, suffix='.db', dir=DATA_PATH
        )
        self.file_path = Path(self.temp_file.name)
        self.data_object = self.data_class(self.file_path, set_structure=True)

    def _test_initial_structure(self):
        structure = self.data_object.select("*", self.table_name)
        pd.testing.assert_frame_equal(
            pd.DataFrame(columns=self.table_cols), structure
        )

    def tearDown(self):
        """Run after every test."""
        self.temp_file.close()


class TestDataLake(TestDBHandlers):
    """Test data lake handler."""

    data_class = DataLakeHandler
    prefix = "data_lake_"
    table_cols = ["unix_time", "date_time", "voltage"]
    table_name = "MOTOR_READINGS"

    def _insert_test_data(self):
        start = 1710811768

        for i in range(5):
            unix = start + i
            data_to_insert = (
                unix,
                str(pd.to_datetime(unix, unit='s')),
                i
            )
            self.data_object.insert(self.table_name, data_to_insert)

    def test_initial_structure(self):
        """Test the structure of the db when it is created."""
        return self._test_initial_structure()

    def test_insert_data(self):
        """Test that data is inserted correctly to the db."""
        self._insert_test_data()
        res_data = self.data_object.select("*", self.table_name)
        self.assertEqual(len(res_data), 5)

    def test_update_data(self):
        """Test that data is updated correctly to the db."""
        self._insert_test_data()

        # All voltage values lower than 2.5 must be changed to zero.
        self.data_object.update(
            self.table_name, "voltage = 0", "voltage < 2.5"
        )
        res_data = self.data_object.select("*", self.table_name)

        # Check that 3 values must be zero now.
        self.assertEqual(res_data["voltage"].value_counts().loc[0], 3)

    def test_delete_data(self):
        """Test that data is deleted correctly to the db."""
        self._insert_test_data()

        # All voltage greater lower than 2.5 must be deleted.
        self.data_object.delete(
            self.table_name, "voltage > 2.5"
        )
        res_data = self.data_object.select("*", self.table_name)

        # Check that only 3 observations remained.
        self.assertEqual(len(res_data), 3)


class TestDataWarehouse(TestDBHandlers):
    """Test data warehouse handler."""

    data_class = DataWarehouseHandler
    prefix = "data_warehouse_"

    def _insert_cycles_test_data(self):
        start = 1710811768

        for i in range(5):
            unix = start + i
            data_to_insert = (
                unix,
                str(pd.to_datetime(unix, unit='s')),
                i,
                i * 1.34
            )
            self.data_object.insert("CYCLES", data_to_insert)
        
    def test_initial_structure_cycles_table(self):
        """Test the structure of the CYCLES table when db is created."""
        self.table_cols = ["unix_time", "date_time", "cycle_id", "voltage"]
        self.table_name = "CYCLES"
        return self._test_initial_structure()

    def test_initial_structure_metrics_table(self):
        """Test the structure of the METRICS table when db is created."""
        self.table_cols = [
            "cycle_id", "ref_unix_time", "ref_date_time",
            "metric_name", "metric_value"
        ]
        self.table_name = "METRICS"
        return self._test_initial_structure()

    def test_latest_cycle_data_non_empty(self):
        """Test latest_cycle_time is correct when table isn't empty."""
        self._insert_cycles_test_data()
        self.assertAlmostEqual(
            self.data_object.latest_cycle_time, 1710811772, places=3
        )

    def test_latest_cycle_data_empty(self):
        """Test latest_cycle_time is correct when table is empty."""
        self.assertFalse(self.data_object.latest_cycle_time)

    def test_latest_cycle_time_data_non_empty(self):
        """Test latest_cycle_time is correct when table isn't empty."""
        self._insert_cycles_test_data()
        self.assertAlmostEqual(
            self.data_object.latest_cycle_time, 1710811772, places=3
        )

    def test_latest_cycle_time_data_empty(self):
        """Test latest_cycle_time is correct when table is empty."""
        self.assertFalse(self.data_object.latest_cycle_time)

    def test_latest_cycle_id_data_non_empty(self):
        """Test latest_cycle_id is correct when table isn't empty."""
        self._insert_cycles_test_data()
        self.assertEqual(self.data_object.latest_cycle_id, 4)

    def test_latest_cycle_id_data_empty(self):
        """Test latest_cycle_id is correct when table is empty."""
        self.assertFalse(self.data_object.latest_cycle_id)


if __name__ == '__main__':
    unittest.main()
