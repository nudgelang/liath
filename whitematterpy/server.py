from flask import Flask, request, jsonify
from database import Database
import threading
from concurrent.futures import ThreadPoolExecutor
import json

app = Flask(__name__)
db = Database()
executor = ThreadPoolExecutor(max_workers=20)  # Adjust the number of workers as needed

def execute_query(namespace, query):
    try:
        result = db.execute_query(namespace, query)
        if isinstance(result, (dict, list)):
            return json.dumps(result)
        elif isinstance(result, str):
            return result
        else:
            return json.dumps({"result": str(result)})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

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
    future = executor.submit(execute_query, data['namespace'], data['query'])
    result = future.result()
    return result, 200, {'Content-Type': 'application/json'}

@app.route('/create_namespace', methods=['POST'])
def create_namespace():
    data = request.json
    db.create_namespace(data['namespace'])
    return jsonify({"status": "success", "message": f"Namespace {data['namespace']} created"})

@app.route('/list_namespaces', methods=['GET'])
def list_namespaces():
    return jsonify({"status": "success", "namespaces": db.list_namespaces()})

def run_server():
    app.run(host='0.0.0.0', port=5000, threaded=True)

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    print("Server is running on http://0.0.0.0:5000")
    server_thread.join()