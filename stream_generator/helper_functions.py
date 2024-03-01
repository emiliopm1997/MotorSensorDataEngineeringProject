import numpy as np
import pandas as pd

from typing import Union


def ts_to_unix(ts: pd.Timestamp) -> int:
    """Transform timestamp to unix.

    Parameters
    ----------
    ts : pd.Timestamp
        A timestamp object.

    Returns
    -------
    int
        Its corresponding unix time.
    """
    reference_time = pd.Timestamp(day=1, month=1, year=1970)
    return (ts - reference_time).total_seconds()


def unix_to_ts(unix: Union[float, int]) -> pd.Timestamp:
    """Transform unix to timestamp.

    Parameters
    ----------
    unix : float or int
        A timestamp value.

    Returns
    -------
    pd.Timestamp
        The corresponding timestamp.
    """
    return pd.to_datetime(unix, unit='s')


