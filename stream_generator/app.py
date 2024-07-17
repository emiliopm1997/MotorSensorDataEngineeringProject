import json
import numpy as np
import pandas as pd
import threading
import time

from kafka import KafkaProducer
from flask import Flask, jsonify

from helper_functions import ts_to_unix, unix_to_ts
from logger import LOGGER
from voltage_simulator import VoltageSensorSimulator

app = Flask(__name__)

KAFKA_SERVER = 'kafka:9092'
TOPIC = 'motor_voltage'

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER], api_version=(2, 0, 2)
)


def send_sensor_values():
    """Send sensor values."""
    start = pd.Timestamp.now()

    # while True:
    for x in range(3):
        LOGGER.info("Iteration {}".format(x))
        end = start + pd.Timedelta(seconds=15)

        # Get data and convert it.
        data = get_voltage_data(start, end)
        message = data.to_dict("records")
        LOGGER.info("{} rows will be sent.".format(len(data)))

        # Send stream.
        producer.send(TOPIC, json.dumps(message).encode("utf-8"))
        producer.flush()
        LOGGER.info("Message was sent at {}".format(pd.Timestamp.now()))

        start = end
        now = pd.Timestamp.now()
        if now < end:
            t_diff_s = (end - now).total_seconds()
            LOGGER.info("Waiting {} seconds...".format(t_diff_s))
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
        151
    )[:-1]
    data["date_time"] = data["unix_time"].apply(unix_to_ts).astype(str)

    # Simulate data
    simulator = VoltageSensorSimulator()
    data["voltage"] = simulator.simulate(data["unix_time"])

    return data


@app.route('/start_generating_values', methods=['GET'])
def start_generating_values():
    """Generate sensor values."""
    LOGGER.info("-" * 15)
    LOGGER.info("Values will start to be generated.")
    # Start generating values in a background thread
    thread = threading.Thread(target=send_sensor_values)
    thread.daemon = True
    thread.start()
    return jsonify({'message': 'Streaming data started'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
