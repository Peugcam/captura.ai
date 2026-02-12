"""
GTA Analytics V2 - WebRTC Frame Capture Client
Captures screen and sends frames via WebRTC DataChannel (binary, no base64)
"""

import asyncio
import io
import json
import logging
import sys
import time
from typing import Optional

import aiohttp
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCDataChannel
from aiortc.contrib.media import MediaPlayer
from PIL import ImageGrab
import av

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebRTCFrameCapture:
    """WebRTC client for sending screen capture frames to Gateway"""

    def __init__(self, gateway_url: str = "http://localhost:8000"):
        self.gateway_url = gateway_url
        self.pc: Optional[RTCPeerConnection] = None
        self.data_channel: Optional[RTCDataChannel] = None
        self.is_capturing = False
        self.frame_count = 0
        self.start_time = None

    async def connect(self):
        """Connect to Gateway via WebRTC signaling"""
        logger.info(f"Connecting to Gateway at {self.gateway_url}")

        # Create PeerConnection
        self.pc = RTCPeerConnection()

        # Create DataChannel for binary frames
        self.data_channel = self.pc.createDataChannel("frames", ordered=True)

        # Setup DataChannel handlers
        @self.data_channel.on("open")
        def on_open():
            logger.info("DataChannel opened - ready to send frames")
            self.is_capturing = True
            self.start_time = time.time()

        @self.data_channel.on("close")
        def on_close():
            logger.info("DataChannel closed")
            self.is_capturing = False

        @self.data_channel.on("message")
        def on_message(message):
            logger.debug(f"Received message: {message}")

        # Setup ICE connection state handler
        @self.pc.on("iceconnectionstatechange")
        async def on_ice_connection_state_change():
            logger.info(f"ICE connection state: {self.pc.iceConnectionState}")
            if self.pc.iceConnectionState == "failed":
                logger.error("ICE connection failed")
                await self.pc.close()

        # Create offer
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)

        # Send offer to Gateway and get answer
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.gateway_url}/offer",
                json={
                    "sdp": self.pc.localDescription.sdp,
                    "type": self.pc.localDescription.type
                },
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get answer: {response.status}")

                answer_data = await response.json()
                logger.info("Received SDP answer from Gateway")

                # Set remote description (answer)
                answer = RTCSessionDescription(
                    sdp=answer_data["sdp"],
                    type=answer_data["type"]
                )
                await self.pc.setRemoteDescription(answer)

        logger.info("WebRTC negotiation completed successfully")

        # Wait for DataChannel to open
        max_wait = 10  # seconds
        waited = 0
        while not self.is_capturing and waited < max_wait:
            await asyncio.sleep(0.1)
            waited += 0.1

        if not self.is_capturing:
            raise Exception("DataChannel failed to open within timeout")

    async def send_frame(self, frame_bytes: bytes):
        """Send a frame via DataChannel (binary)"""
        if not self.data_channel or self.data_channel.readyState != "open":
            logger.warning("DataChannel not ready, skipping frame")
            return False

        try:
            # Send raw JPEG bytes (no base64 encoding!)
            self.data_channel.send(frame_bytes)
            self.frame_count += 1

            if self.frame_count % 10 == 0:
                elapsed = time.time() - self.start_time
                fps = self.frame_count / elapsed if elapsed > 0 else 0
                logger.info(
                    f"Sent {self.frame_count} frames "
                    f"({fps:.2f} FPS, {len(frame_bytes)/1024:.1f}KB)"
                )

            return True

        except Exception as e:
            logger.error(f"Failed to send frame: {e}")
            return False

    def capture_screen(self, quality: int = 85) -> bytes:
        """Capture screen and return JPEG bytes"""
        try:
            # Capture screen
            screenshot = ImageGrab.grab()

            # Convert to JPEG bytes
            buffer = io.BytesIO()
            screenshot.save(buffer, format="JPEG", quality=quality)
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            return None

    async def start_capture(self, fps: int = 4, quality: int = 85, duration: Optional[int] = None):
        """Start capturing and sending frames"""
        logger.info(f"Starting capture at {fps} FPS, quality {quality}, duration {duration}s")

        frame_interval = 1.0 / fps
        start_time = time.time()

        try:
            while self.is_capturing:
                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    logger.info(f"Capture duration limit reached ({duration}s)")
                    break

                # Capture frame
                frame_bytes = self.capture_screen(quality=quality)
                if frame_bytes:
                    # Send frame
                    await self.send_frame(frame_bytes)

                # Wait for next frame
                await asyncio.sleep(frame_interval)

        except KeyboardInterrupt:
            logger.info("Capture interrupted by user")
        finally:
            await self.stop()

    async def stop(self):
        """Stop capture and close connection"""
        logger.info("Stopping capture...")
        self.is_capturing = False

        if self.data_channel:
            self.data_channel.close()

        if self.pc:
            await self.pc.close()

        if self.start_time:
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            logger.info(
                f"Capture stopped. Total: {self.frame_count} frames "
                f"in {elapsed:.1f}s ({fps:.2f} FPS)"
            )


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="GTA Analytics WebRTC Frame Capture")
    parser.add_argument("--gateway", default="http://localhost:8000", help="Gateway URL")
    parser.add_argument("--fps", type=int, default=4, help="Frames per second (default: 4)")
    parser.add_argument("--quality", type=int, default=85, help="JPEG quality 1-100 (default: 85)")
    parser.add_argument("--duration", type=int, help="Capture duration in seconds (default: unlimited)")

    args = parser.parse_args()

    # Create client
    client = WebRTCFrameCapture(gateway_url=args.gateway)

    try:
        # Connect via WebRTC
        await client.connect()

        # Start capturing
        await client.start_capture(
            fps=args.fps,
            quality=args.quality,
            duration=args.duration
        )

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
