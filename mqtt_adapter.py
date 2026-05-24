import paho.mqtt.client as mqtt
import requests
import json

# Configuration
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/temp"
FLASK_TELEMETRY_URL = "http://127.0.0.1:5000/api/telemetry"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to Mosquitto broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"[MQTT] Received message on {msg.topic}: {payload}")
    
    try:
        # We expect the payload to be valid JSON, e.g., {"device_id": 1, "value": 25.5}
        data = json.loads(payload)
        
        # Forward to the Flask API
        response = requests.post(FLASK_TELEMETRY_URL, json=data)
        
        if response.status_code in (200, 201):
            print(f"[MQTT Bridge] Successfully forwarded to Flask.")
        else:
            print(f"[MQTT Bridge] Flask rejected data. Status Code: {response.status_code}")
            
    except json.JSONDecodeError:
        print("[MQTT Bridge] Error: Received payload is not valid JSON.")
    except requests.exceptions.ConnectionError:
        print("[MQTT Bridge] Error: Could not connect to Flask API. Is app.py running?")

# Initialize and run the MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    print("Starting MQTT Adapter...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    # Blocking loop to keep the script running and listening
    client.loop_forever()
except KeyboardInterrupt:
    print("\nShutting down MQTT Adapter.")
    client.disconnect()
