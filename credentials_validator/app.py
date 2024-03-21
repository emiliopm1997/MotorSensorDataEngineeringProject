from flask import Flask, request, jsonify
import json

app = Flask(__name__)


@app.route('/validate', methods=['POST'])
def validate():
    """Validate credentials."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    with open('config.json', 'r') as json_file:
        true_credentials = json.load(json_file)

    valid_username = true_credentials["username"]
    valid_password = true_credentials["password"]

    if username == valid_username and password == valid_password:
        response = {'message': 'Login successful', 'status_code': 200}
    else:
        response = {'message': 'Invalid credentials', 'status_code': 401}

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
