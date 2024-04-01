import pandas as pd

from abc import ABC, abstractclassmethod


class Preprocessor(ABC):
    """General preprocessor class."""

    @abstractclassmethod
    def run(cls, **kwargs) -> pd.DataFrame:
        """Preprocess the data.

        Returns
        -------
        pd.DataFrame
            The preprocessed data.
        """
        raise NotImplementedError
