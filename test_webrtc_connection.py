"""
Test WebRTC connection handshake with Gateway
Validates offer/answer/ICE exchange without sending frames
"""

import asyncio
import json
import logging

import aiohttp
from aiortc import RTCPeerConnection, RTCSessionDescription

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def test_webrtc_handshake(gateway_url: str = "http://localhost:8000"):
    """Test WebRTC signaling handshake"""
    logger.info(f"Testing WebRTC handshake with {gateway_url}")

    # Step 1: Create PeerConnection
    pc = RTCPeerConnection()
    logger.info("✓ PeerConnection created")

    # Step 2: Create DataChannel
    dc = pc.createDataChannel("test", ordered=True)
    logger.info("✓ DataChannel created")

    connection_established = asyncio.Event()

    @dc.on("open")
    def on_open():
        logger.info("✓ DataChannel opened!")
        connection_established.set()

    @dc.on("close")
    def on_close():
        logger.info("✗ DataChannel closed")

    @pc.on("iceconnectionstatechange")
    async def on_ice_state_change():
        logger.info(f"ICE Connection State: {pc.iceConnectionState}")

    # Step 3: Create offer
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    logger.info("✓ SDP offer created")
    logger.debug(f"Offer SDP:\n{pc.localDescription.sdp[:200]}...")

    # Step 4: Send offer to Gateway
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{gateway_url}/offer",
                json={
                    "sdp": pc.localDescription.sdp,
                    "type": pc.localDescription.type
                },
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"✗ Gateway returned {response.status}: {text}")
                    return False

                answer_data = await response.json()
                logger.info("✓ Received SDP answer from Gateway")
                logger.debug(f"Answer SDP:\n{answer_data['sdp'][:200]}...")

                # Step 5: Set remote description
                answer = RTCSessionDescription(
                    sdp=answer_data["sdp"],
                    type=answer_data["type"]
                )
                await pc.setRemoteDescription(answer)
                logger.info("✓ Remote description set")

        except aiohttp.ClientError as e:
            logger.error(f"✗ HTTP request failed: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Unexpected error: {e}")
            return False

    # Step 6: Wait for connection
    logger.info("Waiting for DataChannel to open (max 10s)...")
    try:
        await asyncio.wait_for(connection_established.wait(), timeout=10)
        logger.info("✓ WebRTC connection established successfully!")

        # Send test message
        if dc.readyState == "open":
            dc.send("Hello from test client!")
            logger.info("✓ Test message sent")

        await asyncio.sleep(1)
        return True

    except asyncio.TimeoutError:
        logger.error("✗ DataChannel failed to open within 10 seconds")
        logger.error(f"ICE State: {pc.iceConnectionState}")
        logger.error(f"Connection State: {pc.connectionState}")
        return False

    finally:
        await pc.close()
        logger.info("PeerConnection closed")


async def test_gateway_health(gateway_url: str = "http://localhost:8000"):
    """Test if Gateway is reachable"""
    logger.info(f"Testing Gateway health at {gateway_url}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"{gateway_url}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✓ Gateway is healthy: {data}")
                    return True
                else:
                    logger.error(f"✗ Gateway returned {response.status}")
                    return False

        except aiohttp.ClientError as e:
            logger.error(f"✗ Cannot reach Gateway: {e}")
            return False


async def main():
    """Run all tests"""
    import argparse

    parser = argparse.ArgumentParser(description="Test WebRTC connection to Gateway")
    parser.add_argument("--gateway", default="http://localhost:8000", help="Gateway URL")
    args = parser.parse_args()

    print("\n" + "="*60)
    print("GTA Analytics V2 - WebRTC Connection Test")
    print("="*60 + "\n")

    # Test 1: Gateway health
    print("TEST 1: Gateway Health Check")
    print("-" * 60)
    health_ok = await test_gateway_health(args.gateway)
    print()

    if not health_ok:
        print("✗ Gateway is not reachable. Please start the Gateway first.")
        print("  Run: cd gateway && go run main.go websocket.go buffer.go webrtc.go")
        return

    # Test 2: WebRTC handshake
    print("TEST 2: WebRTC Signaling Handshake")
    print("-" * 60)
    handshake_ok = await test_webrtc_handshake(args.gateway)
    print()

    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Gateway Health:      {'✓ PASS' if health_ok else '✗ FAIL'}")
    print(f"WebRTC Handshake:    {'✓ PASS' if handshake_ok else '✗ FAIL'}")
    print()

    if health_ok and handshake_ok:
        print("✓ All tests passed! WebRTC is ready to use.")
        print("\nNext steps:")
        print("  1. Run: python captura-webrtc.py --fps 4 --duration 30")
        print("  2. Check Gateway logs for incoming frames")
        print("  3. Verify Backend receives frames via /frames endpoint")
    else:
        print("✗ Some tests failed. Check the logs above for details.")


if __name__ == "__main__":
    asyncio.run(main())
