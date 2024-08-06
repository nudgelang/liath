from flask import Flask, request, jsonify
from database import Database
import threading

app = Flask(__name__)
db = Database()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if db.authenticate_user(data['username'], data['password']):
        return jsonify({"status": "success", "message": "Logged in successfully"})
    else:
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    try:
        db.create_user(data['username'], data['password'])
        return jsonify({"status": "success", "message": "User created successfully"})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    try:
        result = db.execute_query(data['namespace'], data['query'])
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/create_namespace', methods=['POST'])
def create_namespace():
    data = request.json
    db.create_namespace(data['namespace'])
    return jsonify({"status": "success", "message": f"Namespace {data['namespace']} created"})

@app.route('/list_namespaces', methods=['GET'])
def list_namespaces():
    return jsonify({"status": "success", "namespaces": db.list_namespaces()})

@app.route('/install_package', methods=['POST'])
def install_package():
    data = request.json
    success = db.install_package(data['namespace'], data['package'])
    if success:
        return jsonify({"status": "success", "message": f"Package {data['package']} installed successfully in namespace {data['namespace']}"})
    else:
        return jsonify({"status": "error", "message": f"Failed to install package {data['package']}"}), 400

def run_server():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    print("Server is running on http://0.0.0.0:5000")
    server_thread.join()