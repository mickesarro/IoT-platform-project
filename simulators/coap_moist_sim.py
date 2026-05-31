import asyncio
import json
import random
from aiocoap import *

# Configuration
URI = "coap://127.0.0.1/moisture"
DEVICE_ID = 2
INTERVAL = 5

async def main():
    protocol = await Context.create_client_context()
    print(f"Starting CoAP Moisture Simulator targeting {URI}...")
    
    try:
        while True:
            moisture = round(random.uniform(40.0, 60.0), 2)
            
            payload_dict = {"device_id": DEVICE_ID, "value": moisture}
            payload_bytes = json.dumps(payload_dict).encode('utf-8')
            
            request = Message(code=PUT, payload=payload_bytes, uri=URI)
            
            try:
                response = await protocol.request(request).response
                print(f"[CoAP Sim] Sent: {payload_dict} | Adapter Response Code: {response.code}")
            except Exception as e:
                print(f"[CoAP Sim] Failed to send: {e}")
                
            await asyncio.sleep(INTERVAL)
            
    except asyncio.CancelledError:
        print("\nShutting down CoAP Simulator")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
