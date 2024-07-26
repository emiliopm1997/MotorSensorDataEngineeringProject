from kafka import KafkaConsumer
from flask import Flask, jsonify, request
from pathlib import Path

import os
import json
import pandas as pd
import requests
import threading
import time
import traceback

from data_base import DataLakeHandler, DataWarehouseHandler
from logger import LOGGER
from utils import ts_to_unix

app = Flask(__name__)

KAFKA_SERVER = 'kafka:9092'
TOPIC = 'motor_voltage'

DATA_DIR = Path('/var/lib/data_handler/data')
DL_PATH = DATA_DIR / 'raw_data.db'
DW_PATH = DATA_DIR / 'preprocessed_data.db'

# Create data directory if it does not exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

PREPROCESSOR_URL = 'http://preprocessors:5004/{}'

# Table names
raw_table_name = "MOTOR_VOLTAGE"


def _read_save_data():
    """Read and save the data."""
    try:
        LOGGER.info("Connecting to data lake for writing...")
        dl = DataLakeHandler(DL_PATH)
        consumer = KafkaConsumer(
            bootstrap_servers=[KAFKA_SERVER], api_version=(2, 0, 2),
            group_id="group1", auto_offset_reset="earliest"
        )
        consumer.subscribe([TOPIC])
        
        #! Change this at the end
        # while True:
        for _ in range(2):
            point_lst = []
            batch_size = 150
        
            LOGGER.info("Collecting {} raw data points...".format(batch_size))
            count = 0
            while count < batch_size:
                msg = consumer.poll(max_records=1)
                if not msg:
                    LOGGER.info("No messages found. Waiting 5 seconds...")
                    time.sleep(5)
                    continue
                
                data_p_byte = list(msg.values())[0][0].value
                data_p = json.loads(data_p_byte.decode("utf-8"))
                point_lst.append(data_p)
                count += 1

            data = pd.DataFrame(point_lst)
            data.to_sql(raw_table_name, dl.conn, if_exists="append", index=False)
            LOGGER.info(
                "Saved {} values to data lake...".format(len(data))
            )

    except Exception as e:
        LOGGER.error(f"{e}\n{traceback.format_exc()}")
        raise e
        

@app.route('/save_raw_data', methods=['GET'])
def save_raw_data():
    """Read and save raw data."""
    LOGGER.info("-" * 30)
    LOGGER.info("Values will start to be read and saved...")
    
    # Read and save values in a background thread
    thread = threading.Thread(target=_read_save_data)
    thread.daemon = True
    thread.start()

    status_code = 200
    response = {
        "message": "Raw data is being saved...", 
        "status_code": status_code}
    return jsonify(response), status_code

def _preprocess_save_data():
    """Preprocesses and save the data."""
    try:
        LOGGER.info("Connecting to data lake for reading...")
        dl = DataLakeHandler(DL_PATH)
        LOGGER.info("Connecting to data warehouse for writing...")
        dw = DataWarehouseHandler(DW_PATH)

        #! Change this at the end
        count = 0
        while count < 2:
        #while True:

            # Prepare data for cycles.
            cycle_info = dict()
            latest_cycle_time = dw.latest_cycle_time
            latest_cycle_id = dw.latest_cycle_id
            additionals = "ORDER BY unix_time DESC LIMIT 1000"
            if latest_cycle_time:
                additionals = (
                    f"WHERE unix_time > {latest_cycle_time} " + additionals
                )

            raw_data = dl.select("*", raw_table_name, additionals)
            raw_data = raw_data.sort_values(
                "unix_time", ignore_index=True, ascending=True
            )

            if len(raw_data) == 0:
                LOGGER.info("No new data was found for preprocessing. Waiting...")
                time.sleep(15)
                continue

            cycle_info["cycle_id_start"] = (
                latest_cycle_id + 1 if latest_cycle_id else 0
            )
            cycle_info["data"] = raw_data.to_dict("records")
            LOGGER.info("New data was found ({} rows)...".format(len(cycle_info["data"])))

            # Calculate cycles.
            LOGGER.info("Calculating cycles for new data...")
            cycles_response = requests.post(
                PREPROCESSOR_URL.format("calculate_cycles"), json=cycle_info
            )
            
            if cycles_response.status_code == 400:
                error_msg = cycles_response.json()["error"]
                raise ValueError(
                    f"Error cutting cycles: {error_msg}"
                )
            elif cycles_response.status_code == 204:
                LOGGER.info("No cycles were found in raw data...")
                time.sleep(15)
                continue

            cycle_data = cycles_response.json()["data"]
            cut_cycle_info = dict()
            cut_cycle_info["data"] = cycle_data

            # Calculate metrics.
            LOGGER.info("Calculating metrics for previous cycles...")
            metrics_response = requests.post(
                PREPROCESSOR_URL.format("calculate_metrics"), json=cut_cycle_info
            )
            if metrics_response.status_code == 400:
                error_msg = metrics_response.json()["error"]
                raise ValueError(
                    f"Error calculating metrics: {error_msg}"
                )
            metrics_data = metrics_response.json()["data"]
            LOGGER.info(f"Total metrics calculated: {len(metrics_data)}")

            # Save data.
            cut_cycles_df = pd.DataFrame(cycle_data)
            cut_cycles_df.to_sql(
                "CYCLES", dw.conn, if_exists="append", index=False
            )
            LOGGER.info(
                "Saved {} cycles to data warehouse...".format(
                    len(cut_cycles_df["cycle_id"].unique())
                )
            )
            metrics_df = pd.DataFrame(metrics_data)
            metrics_df.to_sql(
                "METRICS", dw.conn, if_exists="append", index=False
            )
            LOGGER.info(
                "Saved metrics of {} cycles to data warehouse...".format(
                    len(cut_cycles_df["cycle_id"].unique())
                )
            )
            count += 1
    except Exception as e:
        LOGGER.error(f"{e}\n{traceback.format_exc()}")
        raise e

@app.route('/preprocess_data', methods=['GET'])
def preprocess_data():
    """Preprocess raw data and save it."""
    LOGGER.info("Values will start to be preprocessed and saved...")
    
    # Preprocess and save values in a background thread
    thread = threading.Thread(target=_preprocess_save_data)
    thread.daemon = True
    thread.start()

    status_code = 200
    response = {
        'message': 'Preprocessing and saving data...',
        'status_code': status_code
    }
    return jsonify(response), status_code


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

    status_code = 200
    response = {
        "message": "Data retrieved successfully ...",
        "status_code": status_code,
        "data": data_dict
    }
    return jsonify(response), status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
