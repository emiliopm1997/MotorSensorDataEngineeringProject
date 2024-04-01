import json
import numpy as np
import pandas as pd
import threading
import time

from confluent_kafka import Producer
from flask import Flask, jsonify

from .helper_functions import ts_to_unix, unix_to_ts
from .voltage_simulator import VoltageSensorSimulator

app = Flask(__name__)

KAFKA_SERVER = 'kafka:9092'
TOPIC = 'motor_voltage'

producer = Producer(bootstrap_servers=[KAFKA_SERVER])


def send_sensor_values():
    """Send sensor values."""
    start = pd.Timestamp.now()

    # while True:
    for _ in range(10):
        end = start + pd.Timedelta(seconds=15)

        # Get data and convert it.
        data = get_voltage_data(start, end)
        message = data.to_dict("records")

        # Send stream.
        producer.send(TOPIC, json.dumps(message).encode())
        producer.flush()

        start = end
        now = pd.Timestamp.now()
        if now < end:
            t_diff_s = (end - now).total_seconds()
            time.sleep(t_diff_s)  # Wait until the current time is reached.


def get_voltage_data(start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Get voltage data based on two timestamps.

    Parameters
    ----------
    start : pd.Timestamp
        The starting point.
    end : pd.Timestamp
        The ending point (the last value is not considered).

    Returns
    -------
    pd.DataFrame
        The mappings between timestamp and voltage.
    """
    data = pd.DataFrame()

    # Set unix and timestamp data.
    data["unix_time"] = np.linspace(
        ts_to_unix(start),
        ts_to_unix(end),
        1200
    )[:-1]
    data["date_time"] = data["unix_time"].apply(unix_to_ts)

    # Simulate data
    simulator = VoltageSensorSimulator()
    data["voltage"] = simulator.simulate(data["unix_time"])

    return data


@app.route('/start_generating_values', methods=['GET'])
def start_generating_values():
    """Generate sensor values."""
    # Start generating values in a background thread
    thread = threading.Thread(target=send_sensor_values)
    thread.daemon = True
    thread.start()
    return jsonify({'message': 'Streaming data started'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
