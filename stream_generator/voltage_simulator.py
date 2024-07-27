from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class VoltageSensorSimulator:
    """Class that simulates the voltage of a motor."""

    t_cycle: Optional[float] = 6.0  # seconds
    peak: Optional[float] = 13.0  # kV
    base: Optional[float] = 1.0  # kV
    noise_mean: Optional[float] = 0.0
    noise_std_dev: Optional[float] = 0.3

    @property
    def amplitude(self) -> float:
        """Get amplitude."""
        return self.peak - self.base

    @property
    def period(self) -> float:
        """Get period."""
        return 2 * np.pi / self.t_cycle

    def simulate(
        self, t: np.ndarray, noise: Optional[bool] = True
    ) -> np.ndarray:
        """Simulate the based on a timestamp in unix.

        Parameters
        ----------
        t : np.ndarray
            Array representing unix timestamp.
        noise : Optional[bool], default=True
            Whether to add noise to the data or not.

        Returns
        -------
        np.ndarray
            An array with voltage values based on the timestamp.
        """
        v = self.amplitude * np.sin(self.period * t) + self.base

        if noise:
            v += np.random.normal(self.noise_mean, self.noise_std_dev, len(t))

        return np.where(v > self.base, v, self.base)
