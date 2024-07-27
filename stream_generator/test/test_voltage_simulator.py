import unittest

import numpy as np
import pandas as pd
from helper_functions import ts_to_unix
from voltage_simulator import VoltageSensorSimulator


class TestVoltageSimulator(unittest.TestCase):
    """Test the VoltageSensorSimulator class."""

    @classmethod
    def setUpClass(cls):
        """Run once before everything."""
        cls.simulator = VoltageSensorSimulator(t_cycle=2, peak=10, base=0)

    def test_amplitude(self):
        """Test the amplitude of the wave is what it is expected."""
        self.assertEqual(self.simulator.amplitude, 10)

    def test_period(self):
        """Test the period of the wave is what it is expected."""
        self.assertAlmostEqual(self.simulator.period, np.pi, delta=0.0001)

    def test_simulated_voltage(self):
        """Test the simulated voltage is what it is expected."""
        exp_array = np.array(
            [
                4.76566084e-07,
                9.84807805e00,
                0.00000000e00,
                0.00000000e00,
                6.42788039e00,
                6.42788179e00,
                0.00000000e00,
                0.00000000e00,
                9.84807774e00,
                2.30485229e-06,
            ]
        )
        start = pd.Timestamp("2024-02-24 02:00:00")
        end = pd.Timestamp("2024-02-24 02:00:05")
        u_array = np.linspace(ts_to_unix(start), ts_to_unix(end), 10)

        voltages = self.simulator.simulate(u_array, noise=False)
        np.testing.assert_almost_equal(voltages, exp_array, decimal=3)


if __name__ == "__main__":
    unittest.main()
