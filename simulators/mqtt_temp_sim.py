import time
import json
import random
import paho.mqtt.client as mqtt

# Configuration
BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "sensors/temp"
DEVICE_ID = 2
INTERVAL = 5

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"Simulator connected to Mosquitto at {BROKER}:{PORT}")
    else:
        print(f"Failed to connect: {reason_code}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Temp_Simulator")
client.on_connect = on_connect

print("Starting MQTT Temperature Simulator")
client.connect(BROKER, PORT, 60)
client.loop_start()

try:
    while True:
        temperature = round(random.uniform(20.0, 25.0), 2)
        
        payload_dict = {"device_id": DEVICE_ID, "value": temperature}
        payload_json = json.dumps(payload_dict)
        
        client.publish(TOPIC, payload_json)
        print(f"[MQTT Sim] Published to {TOPIC}: {payload_json}")
        
        time.sleep(INTERVAL)
except KeyboardInterrupt:
    print("\nShutting down MQTT Simulator")
    client.loop_stop()
    client.disconnect()
