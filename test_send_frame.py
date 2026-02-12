"""Quick test to send a test frame to the gateway"""
import asyncio
import websockets
import json
import base64

GATEWAY_WS = "ws://localhost:8000/ws"

async def send_test_frame():
    try:
        # Read test frame
        with open("test_frames/frame_0001.jpg", "rb") as f:
            img_bytes = f.read()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        print(f"Connecting to {GATEWAY_WS}...")
        async with websockets.connect(GATEWAY_WS) as ws:
            print("OK Connected!")
            
            # Send frame
            message = {
                "type": "frame",
                "data": img_base64,
                "timestamp": 1234567890
            }
            
            print("Sending test frame...")
            await ws.send(json.dumps(message))
            print("Frame sent!")
            
            # Wait a bit
            await asyncio.sleep(2)
            
            print("Test complete!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_test_frame())
