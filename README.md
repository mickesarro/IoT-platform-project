# Lightweight Multi-Protocol IoT Platform

A lightweight IoT middleware that bridges physical edge devices and cloud-based visualization platforms. This platform handles device registration, local data ingestion, persistent storage, and data forwarding, while supporting multiple application-level protocols simultaneously (HTTP, MQTT, and CoAP).

## Features

* **Multi-Protocol Support:** Handles HTTP, MQTT, and CoAP telemetry simultaneously.
* **Decoupled Architecture:** Standalone protocol adapters prevent blocking issues within the central API.
* **Local Storage:** Edge persistence using a lightweight SQLite database.
* **Dashboard Integration:** Automated data forwarding to a containerized ThingsBoard instance.

## Prerequisites

* Docker & Docker Compose
* Python 3.x

## Installation & Setup

1. **Start Containerized Services (Mosquitto & ThingsBoard):**
```bash
docker-compose up -d

```


*(Note: This maps Mosquitto to port 1883 and the ThingsBoard UI to port 8080).*

2. **Set up the Python Environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install Flask requests paho-mqtt aiocoap

```


3. **Initialize the Database:**
```bash
python3 init_db.py

```



## Running the Platform

Because of the decoupled architecture, the core API and the protocol adapters must be started in separate terminal windows (with the virtual environment activated in each):

1. **Start the core REST API:**
```bash
python3 app.py

```


2. **Start the MQTT Adapter:**
```bash
python3 mqtt_adapter.py

```


3. **Start the CoAP Adapter:**
```bash
python3 coap_adapter.py

```



## Testing / Simulating Data

1. **Register a Device:**
Before sending data, register a device to map it to a ThingsBoard token.
```bash
curl -X POST http://127.0.0.1:5000/api/register \
     -H "Content-Type: application/json" \
     -d '{"name": "TempSensor_1", "protocol": "MQTT", "tb_token": "YOUR_SECRET_TOKEN"}'

```


2. **Run Simulators:**
Update the `DEVICE_ID` variable in the simulator files to match the ID returned from your device registration, then run:
```bash
python3 simulators/mqtt_temp_sim.py

```


*or for CoAP:*
```bash
python3 simulators/coap_moist_sim.py

```


3. **Verify Data:**
You can view local historical telemetry by calling the API:
```bash
curl -X GET http://localhost:5000/api/data/<device_id>

```


Or visit `http://127.0.0.1:8080` to see the live data in your ThingsBoard dashboard.
