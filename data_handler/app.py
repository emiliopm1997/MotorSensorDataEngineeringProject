from confluent_kafka import Consumer
from flask import Flask, jsonify, request
from pathlib import Path
import time

import pandas as pd
import requests

from .data_base import DataLakeHandler, DataWarehouseHandler
from .utils import ts_to_unix

app = Flask(__name__)

KAFKA_SERVER = 'kafka:9092'
TOPIC = 'motor_voltage'
DL_PATH = Path('data/raw_data.db')
DW_PATH = Path('data/preprocessed_data.db')

PREPROCESSOR_URL = 'http://preprocessor:5004/{}'


@app.route('/save_raw_data', methods=['GET'])
def save_raw_data():
    """Read and save raw data."""
    db = DataLakeHandler(DL_PATH)
    table_name = "MOTOR_READINGS"

    consumer = Consumer(TOPIC, bootstrap_servers=[KAFKA_SERVER])

    for _ in range(5):
        msg = consumer.poll(max_records=1000)
        data = pd.DataFrame(msg.value.decode())
        data.to_sql(table_name, db.conn, if_exists="append", index=False)

    response = {'message': 'Raw data is being saved...', 'status_code': 200}
    return jsonify(response)


@app.route('/preprocess_data', methods=['GET'])
def preprocess_data():
    """Preprocess raw data and save it."""
    dl = DataLakeHandler(DL_PATH)
    dw = DataWarehouseHandler(DW_PATH)

    for _ in range(5):

        # Prepare data for cycles.
        cycle_info = dict()
        latest_cycle_time = dw.latest_cycle_time
        latest_cycle_id = dw.latest_cycle_id
        additionals = "ORDER BY unix_time DESC LIMIT 1000"
        if latest_cycle_time:
            additionals = (
                f"WHERE unix_time > {latest_cycle_time} " + additionals
            )

        raw_data = dl.select("*", "MOTOR_READINGS", additionals)

        if len(raw_data) == 0:
            time.sleep(5)
            continue

        cycle_info["cycle_id_start"] = (
            latest_cycle_id + 1 if latest_cycle_id else 0
        )
        cycle_info["data"] = raw_data.to_dict("records")

        # Calculate cycles.
        cycles_dict = requests.post(
            PREPROCESSOR_URL.format("calculate_cycles"), data=cycle_info
        )
        cut_cycle_info = dict()
        cut_cycle_info["data"] = cycles_dict.json()["data"]

        # Calculate metrics.
        metrics_dict = requests.post(
            PREPROCESSOR_URL.format("calculate_metrics"), data=cut_cycle_info
        )

        # Save data.
        pd.DataFrame(cycles_dict.json()["data"]).to_sql(
            "CYCLES", dw.conn, if_exists="append", index=False
        )
        pd.DataFrame(metrics_dict.json()["data"]).to_sql(
            "METRICS", dw.conn, if_exists="append", index=False
        )

    response = {
        'message': 'Preprocessed data is being saved...',
        'status_code': 200
    }
    return jsonify(response)


@app.route('/retrieve_data_for_report', methods=['POST'])
def retrieve_data_for_report():
    """Get the data needed for reporting."""
    dl = DataLakeHandler(DL_PATH)
    dw = DataWarehouseHandler(DW_PATH)

    # Get reference times.
    data_dict = dict()
    info_json = request.get_json()  # Get JSON data from the request
    unix_start = ts_to_unix(pd.Timestamp(info_json["date_time_start"]))
    unix_end = ts_to_unix(pd.Timestamp(info_json["date_time_end"]))

    additionals1 = f"WHERE unix_time BETWEEN {unix_start} AND {unix_end}"
    raw_data = dl.select("*", "MOTOR_READINGS", additionals1)
    data_dict["raw_data"] = raw_data.to_dict("records")

    additionals2 = f"WHERE ref_unix_time BETWEEN {unix_start} AND {unix_end}"
    metrics_data = dw.select("*", "METRICS", additionals2)
    data_dict["metrics_data"] = metrics_data.to_dict("records")

    response = {
        "message": "Data retrieved successfully ...",
        "status_code": 200,
        "data": data_dict
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
