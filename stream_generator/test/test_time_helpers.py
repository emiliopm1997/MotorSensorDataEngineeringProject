import unittest

import pandas as pd
from helper_functions import ts_to_unix, unix_to_ts


class TestTimeHelpers(unittest.TestCase):
    """Test helper functions."""

    def test_unix_to_ts(self):
        """Test unix conversion to timestamp."""
        ut = 1708740464
        ts = unix_to_ts(ut)
        self.assertEqual(ts, pd.Timestamp("2024-02-24 02:07:44"))

    def test_ts_to_unix(self):
        """Test timestamp conversion to unix."""
        ts = pd.Timestamp("2024-02-24 02:07:44")
        ut = ts_to_unix(ts)
        self.assertEqual(ut, 1708740464)


if __name__ == "__main__":
    unittest.main()
