from flask import Flask, request, jsonify
import sqlite3
import requests

app = Flask(__name__)
DB_NAME = 'iot_platform.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/register', methods=['POST'])
def register_device():
    data = request.get_json()
    name = data.get('name')
    protocol = data.get('protocol')
    tb_token = data.get('tb_token')

    if not all([name, protocol, tb_token]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO Devices (Name, Protocol, ThingsBoardToken) VALUES (?, ?, ?)',
        (name, protocol, tb_token)
    )
    conn.commit()
    device_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Device registered", "device_id": device_id}), 201

@app.route('/api/devices', methods=['GET'])
def get_devices():
    conn = get_db_connection()
    devices = conn.execute('SELECT * FROM Devices').fetchall()
    conn.close()
    return jsonify([dict(row) for row in devices]), 200

@app.route('/api/data/<int:device_id>', methods=['GET'])
def get_device_data(device_id):
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM Telemetry WHERE DeviceID = ?', (device_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in data]), 200


@app.route('/api/telemetry', methods=['POST'])
def receive_telemetry():
    data = request.get_json()
    device_id = data.get('device_id')
    value = data.get('value')

    if not device_id or value is None:
        return jsonify({"error": "Missing device_id or value in payload"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    device = cursor.execute('SELECT * FROM Devices WHERE ID = ?', (device_id,)).fetchone()
    
    if not device:
        conn.close()
        return jsonify({"error": f"Device ID {device_id} not found"}), 404

    tb_token = device['ThingsBoardToken']

    cursor.execute(
        'INSERT INTO Telemetry (DeviceID, Value) VALUES (?, ?)',
        (device_id, value)
    )
    conn.commit()
    conn.close()


    tb_payload = {k: v for k, v in data.items() if k != 'device_id'}
    

    tb_url = f"http://127.0.0.1:8080/api/v1/{tb_token}/telemetry"
    
    try:
        tb_response = requests.post(tb_url, json=tb_payload, timeout=2)
        
        if tb_response.status_code == 200:
            return jsonify({"message": "Data saved locally and forwarded to ThingsBoard"}), 201
        else:
            return jsonify({
                "message": "Data saved locally, but ThingsBoard rejected it", 
                "tb_status": tb_response.status_code
            }), 207
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            "message": "Data saved locally, but could not reach ThingsBoard",
            "error": str(e)
        }), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
