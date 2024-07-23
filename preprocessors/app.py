from flask import Flask, jsonify, request

from cycles import CycleCutter
from metrics import MetricsCalculator
from logger import LOGGER

import pandas as pd
import traceback

app = Flask(__name__)


@app.route('/calculate_cycles', methods=['POST'])
def calculate_cycles():
    """Calculate the cycles using the raw data."""
    try:
        cycle_info = request.get_json()  # Get JSON data from the request
        cycle_id_start = cycle_info["cycle_id_start"]
        data = pd.DataFrame(cycle_info["data"])

        LOGGER.info("Cutting cycles...")
        preprocessor = CycleCutter()
        preprocessor.run(data=data, cycle_id_start=cycle_id_start)
        preprocessed_data = preprocessor.preprocessed_data
        preprocessed_data["date_time"] = preprocessed_data["date_time"].apply(
            lambda x: str(x)
        )
        
        LOGGER.info("Cut cycles:\n{}".format(preprocessed_data))

        dict_data = preprocessed_data.to_dict("records")

        response = {
            "message": "Cycles cut successfully...",
            "data": dict_data
        }
        status_code = 200
    except Exception as e:
        LOGGER.error(f"{e}\n{traceback.format_exc()}")
        response = {"error": f"{e}\n{traceback.format_exc()}"}
        status_code = 400
    return jsonify(response), status_code


@app.route('/calculate_metrics', methods=['POST'])
def calculate_metrics():
    """Calculate multiple metrics using the cycle data."""
    try:
        cut_cycle_info = request.get_json()  # Get JSON data from the request
        data = pd.DataFrame(cut_cycle_info["data"])

        LOGGER.info("Calculating metrics...")
        preprocessor = MetricsCalculator()
        preprocessor.run(data=data)
        preprocessed_data = preprocessor.preprocessed_data

        LOGGER.info("Calculated metrics:\n{}".format(preprocessed_data))
        dict_data = preprocessed_data.to_dict("records")

        response = {
            "message": "Metrics calculated successfully...",
            "data": dict_data
        }
        status_code = 200
    except Exception as e:
        LOGGER.error(f"{e}\n{traceback.format_exc()}")
        response = {"error": f"{e}\n{traceback.format_exc()}"}
        status_code = 400
    return jsonify(response), status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
