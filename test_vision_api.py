"""Test Vision API with mock frame containing kill feed"""
import asyncio
import websockets
import json
import base64
import time

GATEWAY_WS = "ws://localhost:8000/ws"

async def send_mock_frame():
    try:
        # Read mock frame with kill feed
        with open("test_frames/mock_kill_feed.jpg", "rb") as f:
            img_bytes = f.read()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        print(f"Connecting to {GATEWAY_WS}...")
        async with websockets.connect(GATEWAY_WS) as ws:
            print("Connected to Gateway!")
            
            # Send frame
            message = {
                "type": "frame",
                "data": img_base64,
                "timestamp": int(time.time())
            }
            
            print("Sending mock frame with kill feed...")
            print("Expected: OCR should detect 'KILLED' and 'WASTED' keywords")
            print("Expected: Frame should pass to Vision API for analysis")
            await ws.send(json.dumps(message))
            print("Frame sent!")
            print("\nCheck Backend logs for:")
            print("  1. OCR detection (should PASS)")
            print("  2. Vision API call")
            print("  3. Kill event extraction")
            
            # Wait for processing
            await asyncio.sleep(5)
            
            print("\nTest complete! Check dashboard for results.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_mock_frame())
