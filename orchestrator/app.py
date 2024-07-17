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
    # Start start stream generator
    LOGGER.info("Starting stream generator...")
    requests.get(STREAM_GENERATOR_URL)

    # Validate credentials.
    # with open('config.json', 'r') as json_file:
    #     credentials = json.load(json_file)
    # LOGGER.info("Validating credentials...")
    # validation_results = requests.post(
    #     VALIDATE_CREDENTIALS_URL, json=credentials
    # )

    # if validation_results.status_code == 200:
    #     LOGGER.info("Credentials are valid...")

        # Read raw data and save to data lake
        # LOGGER.info("Reading and saving raw data...")
        # requests.get(DATA_HANDLER_URL.format("save_raw_data"))

        # Preprocess data and save it to data warehouse
        # LOGGER.info("Preprocessing and saving data...")
        # requests.get(DATA_HANDLER_URL.format("preprocess_data"))

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

    return jsonify({'message': 'All services started'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
