from flask import Flask, jsonify
import json
import requests

from logger import LOGGER

app = Flask(__name__)

STREAM_GENERATOR_URL = 'http://stream_generator:5001/start_generating_values'
DATA_HANDLER_URL = 'http://data_handler:5002/{}'
VALIDATE_CREDENTIALS_URL = 'http://credentials_validator:5003/validate'


@app.route('/start_pipeline', methods=['GET'])
def start_pipeline():
    """Start the pipeline."""
    LOGGER.info("-" * 30)
    
    # Start start stream generator
    LOGGER.info("Starting stream generator...")
    requests.get(STREAM_GENERATOR_URL)

    # Validate credentials.
    with open('config.json', 'r') as json_file:
        credentials = json.load(json_file)
    LOGGER.info("Validating credentials...")
    validation_results = requests.post(
        VALIDATE_CREDENTIALS_URL, json=credentials
    )

    if validation_results.status_code == 200:
        LOGGER.info("Credentials are valid...")

        # Read raw data and save to data lake
        LOGGER.info("Starting data collection and storage service...")
        requests.get(DATA_HANDLER_URL.format("save_raw_data"))

        # Preprocess data and save it to data warehouse
        LOGGER.info("Starting data preprocessing and storing service...")
        requests.get(DATA_HANDLER_URL.format("preprocess_data"))

        # Get data for report. This should be done by the front end.
        # info_json = dict()
        # info_json["date_time_start"] = (
        #     pd.Timestamp.now() - pd.Timedelta(seconds=60)
        # )
        # info_json["date_time_end"] = (
        #     pd.Timestamp.now() - pd.Timedelta(seconds=30)
        # )
        # data_dict = requests.post(
        #     DATA_HANDLER_URL.format("retrieve_data_for_report"),
        #     data=info_json
        # )
        # raw_data = pd.DataFrame(data_dict.json()["raw_data"])
        # metrics_data = pd.DataFrame(data_dict.json()["metrics_data"])
        status_code = 200
        message = "All services started."
    else:
        status_code = 400
        error_msg = validation_results.json()["error"]
        message = f"Error: {error_msg}"

    return (
        jsonify(
            {"message": message, "status_code": status_code}
        ), status_code
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
