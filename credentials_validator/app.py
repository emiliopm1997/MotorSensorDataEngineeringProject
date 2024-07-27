import json

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/validate", methods=["POST"])
def validate():
    """Validate credentials."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    with open("config.json", "r") as json_file:
        true_credentials = json.load(json_file)

    valid_username = true_credentials["username"]
    valid_password = true_credentials["password"]

    if username == valid_username and password == valid_password:
        status_code = 200
        response = {"message": "Login successful", "status_code": status_code}
    else:
        status_code = 401
        response = {"error": "Invalid credentials", "status_code": status_code}

    return jsonify(response), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
