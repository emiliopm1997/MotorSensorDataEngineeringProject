from flask import Flask, jsonify
import requests

app = Flask(__name__)

STREAM_GENERATOR_URL = 'http://stream_generator:5001/start_generating_values'
RAW_DATA_HANDLER_URL = 'http://raw_data_handler:5002/save_to_data_lake'


@app.route('/start_pipeline', methods=['GET'])
def start_pipeline():
    """Start the pipeline."""
    # Start start stream generator
    requests.get(STREAM_GENERATOR_URL)
    # Read data and save to data lake
    requests.get(RAW_DATA_HANDLER_URL)

    return jsonify({'message': 'All services started'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)