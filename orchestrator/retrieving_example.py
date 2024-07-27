import pandas as pd
import requests

DATA_HANDLER_URL = "http://data_handler:5002/{}"


def main():
    """Simulate data retreival for dashboard."""
    # Get data for report. This should be done by the front end.
    print("Setting periods ...")
    info_json = dict()
    ts_start = pd.Timestamp.now() - pd.Timedelta(seconds=45)
    ts_end = pd.Timestamp.now() - pd.Timedelta(seconds=15)
    info_json["date_time_start"] = str(ts_start)
    info_json["date_time_end"] = str(ts_end)

    print("Sending request ...")
    result = requests.post(
        DATA_HANDLER_URL.format("retrieve_data_for_report"), json=info_json
    )

    # Catch errors in request.
    if result.status_code in [400, 404]:
        error_msg = result.json()["error"]
        if result.status_code == 404:
            error_msg += ". Try again soon."
        print(f"Error ({result.status_code}): {error_msg}")
        return

    # This is the way to retrieve data for a dashboard.
    print("Data retrieved successfully ...")
    raw_data = pd.DataFrame(result.json()["data"]["raw_data"])
    metrics_data = pd.DataFrame(result.json()["data"]["metrics_data"])

    # This is only to ensure that data is being retreived.
    print(f"\nRaw data contains {len(raw_data)} lines. Showing bottom:")
    print(raw_data.tail(15))
    print(
        f"\nMetrics data contains {len(metrics_data)} lines. "
        "Showing bottom:"
    )
    print(metrics_data.tail(15))


if __name__ == "__main__":
    main()
