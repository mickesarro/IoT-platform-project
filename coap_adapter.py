import logging
import asyncio
import json
import requests
import aiocoap.resource as resource
import aiocoap

FLASK_TELEMETRY_URL = "http://127.0.0.1:5000/api/telemetry"

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.INFO)

class MoistureResource(resource.Resource):
    """
    This resource supports the PUT method.
    It expects a JSON payload containing device_id and value.
    """
    async def render_put(self, request):
        payload_str = request.payload.decode('utf8')
        print(f"[CoAP] Received PUT request on /moisture: {payload_str}")
        
        try:
            data = json.loads(payload_str)
            
            response = await asyncio.to_thread(requests.post, FLASK_TELEMETRY_URL, json=data)
            
            if response.status_code in (200, 201):
                print(f"[CoAP Bridge] Successfully forwarded to Flask.")
                return aiocoap.Message(code=aiocoap.CHANGED, payload=b"Data forwarded successfully")
            else:
                print(f"[CoAP Bridge] Flask rejected data. Status: {response.status_code}")
                return aiocoap.Message(code=aiocoap.INTERNAL_SERVER_ERROR)
                
        except json.JSONDecodeError:
            print("[CoAP Bridge] Error: Payload is not valid JSON.")
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"Invalid JSON")
        except requests.exceptions.ConnectionError:
            print("[CoAP Bridge] Error: Could not connect to Flask API.")
            return aiocoap.Message(code=aiocoap.INTERNAL_SERVER_ERROR, payload=b"Flask API unreachable")

async def main():
    root = resource.Site()
    
    root.add_resource(['moisture'], MoistureResource())

    print("Starting CoAP Adapter on port 5683")
    await aiocoap.Context.create_server_context(root)

    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down CoAP adapter")
