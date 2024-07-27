import json
import os
import threading
import time
import traceback
from pathlib import Path

import pandas as pd
import requests
from data_base import DataLakeHandler, DataWarehouseHandler
from flask import Flask, jsonify, request
from kafka import KafkaConsumer
from logger import LOGGERS
from utils import ts_to_unix

app = Flask(__name__)

KAFKA_SERVER = "kafka:9092"
TOPIC = "motor_voltage"

DATA_DIR = Path("/var/lib/data_handler/data")
DL_PATH = DATA_DIR / "raw_data.db"
DW_PATH = DATA_DIR / "processed_data.db"

DC_LOGGER = LOGGERS[0]  # Data consumer logger
DP_LOGGER = LOGGERS[1]  # Data processor logger
DR_LOGGER = LOGGERS[2]  # Data retriever logger

# Create data directory if it does not exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

PROCESSOR_URL = "http://processors:5004/{}"

# Table names
raw_table_name = "MOTOR_VOLTAGE"
cycles_table_name = "CYCLES"
metrics_table_name = "METRICS"


def _read_save_data():
    """Read and save the data."""
    try:
        DC_LOGGER.info("Connecting to data lake for writing...")
        dl = DataLakeHandler(DL_PATH)
        consumer = KafkaConsumer(
            bootstrap_servers=[KAFKA_SERVER],
            api_version=(2, 0, 2),
            group_id="group1",
            auto_offset_reset="earliest",
        )
        consumer.subscribe([TOPIC])

        while True:
            point_lst = []
            batch_size = 150

            DC_LOGGER.info(
                "Collecting {} raw data points...".format(batch_size)
            )
            count = 0
            while count < batch_size:
                msg = consumer.poll(max_records=1)
                if not msg:
                    DC_LOGGER.info("No messages found. Waiting 5 seconds...")
                    time.sleep(5)
                    continue

                data_p_byte = list(msg.values())[0][0].value
                data_p = json.loads(data_p_byte.decode("utf-8"))
                point_lst.append(data_p)
                count += 1

            data = pd.DataFrame(point_lst)
            data.to_sql(
                raw_table_name, dl.conn, if_exists="append", index=False
            )
            DC_LOGGER.info("Saved {} values to data lake...".format(len(data)))

    except Exception as e:
        DC_LOGGER.error(f"{e}\n{traceback.format_exc()}")
        raise e


@app.route("/save_raw_data", methods=["GET"])
def save_raw_data():
    """Read and save raw data."""
    DC_LOGGER.info("-" * 30)
    DC_LOGGER.info("Values will start to be read and saved...")

    # Read and save values in a background thread
    thread = threading.Thread(target=_read_save_data)
    thread.daemon = True
    thread.start()

    status_code = 200
    response = {
        "message": "Raw data is being saved...",
        "status_code": status_code,
    }
    return jsonify(response), status_code


def _process_save_data():
    """Process and saves the data."""
    try:
        DP_LOGGER.info("Connecting to data lake for reading...")
        dl = DataLakeHandler(DL_PATH)
        DP_LOGGER.info("Connecting to data warehouse for writing...")
        dw = DataWarehouseHandler(DW_PATH)

        while True:

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
                DP_LOGGER.info(
                    "No new data was found for processing. Waiting..."
                )
                time.sleep(15)
                continue

            cycle_info["cycle_id_start"] = (
                latest_cycle_id + 1 if latest_cycle_id is not None else 0
            )
            cycle_info["data"] = raw_data.to_dict("records")
            DP_LOGGER.info(
                "New data was found ({} rows)...".format(
                    len(cycle_info["data"])
                )
            )

            # Calculate cycles.
            DP_LOGGER.info("Calculating cycles for new data...")
            cycles_response = requests.post(
                PROCESSOR_URL.format("calculate_cycles"), json=cycle_info
            )

            if cycles_response.status_code == 400:
                error_msg = cycles_response.json()["error"]
                raise ValueError(f"Error cutting cycles: {error_msg}")
            elif cycles_response.status_code == 404:
                DP_LOGGER.info("No cycles were found in raw data...")
                time.sleep(15)
                continue

            cycle_data = cycles_response.json()["data"]
            cut_cycle_info = dict()
            cut_cycle_info["data"] = cycle_data

            # Calculate metrics.
            DP_LOGGER.info("Calculating metrics for previous cycles...")
            metrics_response = requests.post(
                PROCESSOR_URL.format("calculate_metrics"), json=cut_cycle_info
            )
            if metrics_response.status_code == 400:
                error_msg = metrics_response.json()["error"]
                raise ValueError(f"Error calculating metrics: {error_msg}")
            metrics_data = metrics_response.json()["data"]
            DP_LOGGER.info(f"Total metrics calculated: {len(metrics_data)}")

            # Save data.
            cut_cycles_df = pd.DataFrame(cycle_data)
            cut_cycles_df.to_sql(
                cycles_table_name, dw.conn, if_exists="append", index=False
            )
            DP_LOGGER.info(
                "Saved {} cycles to data warehouse...".format(
                    len(cut_cycles_df["cycle_id"].unique())
                )
            )
            metrics_df = pd.DataFrame(metrics_data)
            metrics_df.to_sql(
                metrics_table_name, dw.conn, if_exists="append", index=False
            )
            DP_LOGGER.info(
                "Saved metrics of {} cycles to data warehouse...".format(
                    len(cut_cycles_df["cycle_id"].unique())
                )
            )
    except Exception as e:
        DP_LOGGER.error(f"{e}\n{traceback.format_exc()}")
        raise e


@app.route("/process_data", methods=["GET"])
def process_data():
    """Process raw data and save it."""
    DP_LOGGER.info("-" * 30)
    DP_LOGGER.info("Values will start to be processed and saved...")

    # Process and save values in a background thread
    thread = threading.Thread(target=_process_save_data)
    thread.daemon = True
    thread.start()

    status_code = 200
    response = {
        "message": "Processing and saving data...",
        "status_code": status_code,
    }
    return jsonify(response), status_code


@app.route("/retrieve_data_for_report", methods=["POST"])
def retrieve_data_for_report():
    """Get the data needed for reporting."""
    try:
        DR_LOGGER.info("Connecting to data lake for reading...")
        dl = DataLakeHandler(DL_PATH)
        DR_LOGGER.info("Connecting to data warehouse for reading...")
        dw = DataWarehouseHandler(DW_PATH)

        # Get reference times.
        DR_LOGGER.info("Retreiving request info ...")
        data_dict = dict()
        info_json = request.get_json()  # Get JSON data from the request
        ts_start = pd.Timestamp(info_json.get("date_time_start"))
        ts_end = pd.Timestamp(info_json.get("date_time_end"))
        unix_start = ts_to_unix(ts_start)
        unix_end = ts_to_unix(ts_end)

        # Get raw data.
        DR_LOGGER.info(
            "Getting raw data between {} and {}...".format(ts_start, ts_end)
        )
        additionals1 = f"WHERE unix_time BETWEEN {unix_start} AND {unix_end}"
        raw_data = dl.select("*", raw_table_name, additionals1)
        if len(raw_data) == 0:
            msg = "No raw data was found between {} and {}.".format(
                str(ts_start), str(ts_end)
            )
            DR_LOGGER.warning(msg)
            status_code = 404
            response = {"error": msg, "status_code": status_code}
            return jsonify(response), status_code
        data_dict["raw_data"] = raw_data.to_dict("records")

        # Get metrics data.
        DR_LOGGER.info(
            "Getting cycle metrics between {} and {}...".format(
                ts_start, ts_end
            )
        )
        additionals2 = (
            f"WHERE ref_unix_time BETWEEN {unix_start} AND {unix_end}"
        )
        metrics_data = dw.select("*", metrics_table_name, additionals2)
        if len(metrics_data) == 0:
            msg = "No metrics data was found between {} and {}.".format(
                str(ts_start), str(ts_end)
            )
            DR_LOGGER.warning(msg)
            status_code = 404
            response = {"error": msg, "status_code": status_code}
            return jsonify(response), status_code
        data_dict["metrics_data"] = metrics_data.to_dict("records")

        status_code = 200
        response = {
            "message": "Data retrieved successfully ...",
            "status_code": status_code,
            "data": data_dict,
        }
    except Exception as e:
        DR_LOGGER.error(f"{e}\n{traceback.format_exc()}")
        status_code = 400
        response = {
            "error": f"{e}\n{traceback.format_exc()}",
            "status_code": status_code,
        }

    return jsonify(response), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
