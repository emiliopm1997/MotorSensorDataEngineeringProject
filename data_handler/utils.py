import pandas as pd


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
