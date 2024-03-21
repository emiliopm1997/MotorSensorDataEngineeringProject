from flask import Flask, jsonify
import json
import requests

app = Flask(__name__)

STREAM_GENERATOR_URL = 'http://stream_generator:5001/start_generating_values'
DATA_HANDLER_URL = 'http://data_handler:5002/{}'
VALIDATE_CREDENTIALS_URL = 'http://credentials_validator:5003/validate'


@app.route('/start_pipeline', methods=['GET'])
def start_pipeline():
    """Start the pipeline."""
    # Start start stream generator
    requests.get(STREAM_GENERATOR_URL)

    # Validate credentials.
    with open('config.json', 'r') as json_file:
        credentials = json.load(json_file)
    validation_results = requests.post(
        VALIDATE_CREDENTIALS_URL, json=credentials
    )

    if validation_results.status_code == 200:
        print("Credentials are valid...")

        # Read raw data and save to data lake
        requests.get(DATA_HANDLER_URL.format("save_raw_data"))

        # Preprocess data and save it to data warehouse

        # Serve data to report feeder

    return jsonify({'message': 'All services started'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)