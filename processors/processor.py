import pandas as pd

from abc import ABC, abstractclassmethod


class Processor(ABC):
    """General processor class."""

    @abstractclassmethod
    def run(cls, **kwargs) -> pd.DataFrame:
        """Process the data.

        Returns
        -------
        pd.DataFrame
            The processed data.
        """
        raise NotImplementedError
