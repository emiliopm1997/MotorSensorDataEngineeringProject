import traceback

import pandas as pd
from cycles import CycleCutter
from flask import Flask, jsonify, request
from logger import LOGGER
from metrics import MetricsCalculator

app = Flask(__name__)


@app.route("/calculate_cycles", methods=["POST"])
def calculate_cycles():
    """Calculate the cycles using the raw data."""
    try:
        cycle_info = request.get_json()  # Get JSON data from the request
        cycle_id_start = cycle_info["cycle_id_start"]
        data = pd.DataFrame(cycle_info["data"])

        LOGGER.info("Cutting cycles...")
        processor = CycleCutter()
        processor.run(data=data, cycle_id_start=cycle_id_start)
        processed_data = processor.processed_data

        if len(processed_data) == 0:
            status_code = 404
            response = {
                "error": "No cycles found for cutting...",
                "status_code": status_code,
            }
            return jsonify(response), status_code

        processed_data["date_time"] = processed_data["date_time"].apply(
            lambda x: str(x)
        )

        LOGGER.info(
            "Number of cut cycles: {}".format(
                len(processed_data["cycle_id"].unique())
            )
        )

        dict_data = processed_data.to_dict("records")

        status_code = 200
        response = {
            "message": "Cycles cut successfully...",
            "data": dict_data,
            "status_code": status_code,
        }
    except Exception as e:
        LOGGER.error(f"{e}\n{traceback.format_exc()}")
        status_code = 400
        response = {
            "error": f"{e}\n{traceback.format_exc()}",
            "status_code": status_code,
        }
    return jsonify(response), status_code


@app.route("/calculate_metrics", methods=["POST"])
def calculate_metrics():
    """Calculate multiple metrics using the cycle data."""
    try:
        cut_cycle_info = request.get_json()  # Get JSON data from the request
        data = pd.DataFrame(cut_cycle_info["data"])

        LOGGER.info("Calculating metrics...")
        processor = MetricsCalculator()
        processor.run(data=data)
        processed_data = processor.processed_data

        LOGGER.info(
            "Metrics have been calculated for {} cycles...".format(
                len(processed_data["cycle_id"].unique())
            )
        )
        dict_data = processed_data.to_dict("records")

        response = {
            "message": "Metrics calculated successfully...",
            "data": dict_data,
        }
        status_code = 200
    except Exception as e:
        LOGGER.error(f"{e}\n{traceback.format_exc()}")
        response = {"error": f"{e}\n{traceback.format_exc()}"}
        status_code = 400
    return jsonify(response), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
