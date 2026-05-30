import time
import json
import random
import paho.mqtt.client as mqtt

# Configuration
BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "sensors/temp"
DEVICE_ID = 2
INTERVAL = 5   # Send data every 5 seconds

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"Simulator connected to Mosquitto at {BROKER}:{PORT}")
    else:
        print(f"Failed to connect, return code {reason_code}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Temp_Simulator")
client.on_connect = on_connect

print("Starting MQTT Temperature Simulator...")
client.connect(BROKER, PORT, 60)
client.loop_start()  # Start network loop in the background

try:
    while True:
        # Generate a random temperature between 20.0 and 25.0
        temperature = round(random.uniform(20.0, 25.0), 2)
        
        # Create the JSON payload that your mqtt_adapter expects
        payload_dict = {"device_id": DEVICE_ID, "value": temperature}
        payload_json = json.dumps(payload_dict)
        
        client.publish(TOPIC, payload_json)
        print(f"[MQTT Sim] Published to {TOPIC}: {payload_json}")
        
        time.sleep(INTERVAL)
except KeyboardInterrupt:
    print("\nShutting down MQTT Simulator...")
    client.loop_stop()
    client.disconnect()
