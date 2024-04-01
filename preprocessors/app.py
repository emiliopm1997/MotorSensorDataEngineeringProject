from flask import Flask, jsonify, request
from .cycles import CycleCutter

import pandas as pd

app = Flask(__name__)

@app.route('/calculate_cycles', methods=['POST'])
def calculate_cycles():
    """Calculate the cycles using the raw data."""
    cycle_info = request.get_json()  # Get JSON data from the request
    cycle_id_start = cycle_info["cycle_id_start"]
    data = pd.DataFrame(cycle_info["data"])

    preprocessor = CycleCutter()
    preprocessor.run(data=data, cycle_id_start=cycle_id_start)
    preprocessed_data = preprocessor.preprocessed_data.to_dict("records")

    response = {
        "message": "Cycles cut successfully...",
        "status_code": 200,
        "data": preprocessed_data
    }
    return jsonify(response)


@app.route('/calculate_metrics', methods=['POST'])
def calculate_metrics():
    """Calculate multiple metrics using the cycle data."""
    cut_cycle_info = request.get_json()  # Get JSON data from the request
    data = pd.DataFrame(cut_cycle_info["data"])

    # Call preprocessor object.
    
    # Run preprocessor and get processed data.
    
    # Convert preprocessed data to dictionary and send back.
    
    response = {
        'status': 'success', 
        'message': 'Metrics calculated successfully...'
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
