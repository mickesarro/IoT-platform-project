import logging
import asyncio
import json
import requests
import aiocoap.resource as resource
import aiocoap

# Configuration
FLASK_TELEMETRY_URL = "http://127.0.0.1:5000/api/telemetry"

# Setup basic logging to see aiocoap output
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
            # Parse the incoming JSON
            data = json.loads(payload_str)
            
            # Forward to Flask in a background thread to prevent blocking the async loop
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
    # Create the CoAP resource tree
    root = resource.Site()
    
    # Map the endpoint /moisture to our MoistureResource class
    root.add_resource(['moisture'], MoistureResource())

    # Start the CoAP server on default port 5683
    print("Starting CoAP Adapter on port 5683...")
    await aiocoap.Context.create_server_context(root)

    # Keep the server running forever
    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down CoAP Adapter.")
