from flask import Flask, request, jsonify

app = Flask(__name__)

# Hardcoded credentials for demonstration purposes
valid_username = 'user123'
valid_password = 'pass123'


@app.route('/validate', methods=['POST'])
def validate():
    """Validate credentials."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == valid_username and password == valid_password:
        response = {'message': 'Login successful', 'status_code': 200}
    else:
        response = {'message': 'Invalid credentials', 'status_code': 401}

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
