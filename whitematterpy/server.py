from flask import Flask, request, jsonify
from database import Database
import threading
from concurrent.futures import ThreadPoolExecutor
import json
import argparse

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=20)  # Adjust the number of workers as needed

def create_app(storage_type='auto'):
    db = Database(storage_type=storage_type)
    app.config['db'] = db
    return app

def execute_query(namespace, query):
    db = app.config['db']
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
    db = app.config['db']
    if db.authenticate_user(data['username'], data['password']):
        return jsonify({"status": "success", "message": "Logged in successfully"})
    else:
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    db = app.config['db']
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
    db = app.config['db']
    db.create_namespace(data['namespace'])
    return jsonify({"status": "success", "message": f"Namespace {data['namespace']} created"})

@app.route('/list_namespaces', methods=['GET'])
def list_namespaces():
    db = app.config['db']
    return jsonify({"status": "success", "namespaces": db.list_namespaces()})

def run_server(host='0.0.0.0', port=5000):
    app.run(host=host, port=port, threaded=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="WhiteMatter Database Server")
    parser.add_argument('--storage', choices=['auto', 'rocksdb', 'leveldb'], default='auto',
                        help="Specify the storage backend to use")
    parser.add_argument('--host', default='0.0.0.0', help="Specify the host to run the server on")
    parser.add_argument('--port', type=int, default=5000, help="Specify the port to run the server on")
    args = parser.parse_args()

    app = create_app(storage_type=args.storage)
    server_thread = threading.Thread(target=run_server, args=(args.host, args.port))
    server_thread.start()
    print(f"Server is running on http://{args.host}:{args.port}")
    server_thread.join()