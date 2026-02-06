"""
GTA Analytics V2 - Python Backend
==================================

Backend otimizado que consome frames do Go Gateway
- Polling HTTP do gateway Go
- OCR pré-filtro em thread pool
- GPT-4o Vision API
- Team tracking e export

Author: Paulo Eugenio Campos
"""

import asyncio
import httpx
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional
import config

# Setup logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FramePoller:
    """Poll frames from Go Gateway"""

    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def fetch_frames(self) -> List[Dict]:
        """Fetch batch of frames from gateway"""
        try:
            response = await self.client.get(f"{self.gateway_url}/frames")

            if response.status_code == 204:  # No content
                return []

            if response.status_code == 200:
                data = response.json()
                frames = data.get('frames', [])
                logger.info(f"📥 Fetched {len(frames)} frames from gateway")
                return frames

        except Exception as e:
            logger.error(f"Error fetching frames: {e}")

        return []

    async def start_polling(self, callback, interval: float = 1.0):
        """Start continuous polling"""
        logger.info(f"🔄 Started polling gateway every {interval}s")

        while True:
            frames = await self.fetch_frames()

            if frames:
                await callback(frames)

            await asyncio.sleep(interval)


class GTAAnalyticsBackend:
    """Main backend application"""

    def __init__(self):
        self.poller = FramePoller(config.GATEWAY_URL)
        self.frame_queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor(max_workers=config.OCR_WORKERS)

        # Stats
        self.stats = {
            'frames_received': 0,
            'frames_processed': 0,
            'kills_detected': 0
        }

    async def process_frames(self, frames: List[Dict]):
        """Process batch of frames"""
        for frame in frames:
            await self.frame_queue.put(frame)
            self.stats['frames_received'] += 1

    async def worker(self):
        """Frame processing worker"""
        logger.info("🔧 Worker started")

        while True:
            frame = await self.frame_queue.get()

            try:
                # TODO: Add OCR pre-filter
                # TODO: Add GPT-4o vision processing
                # TODO: Add kill parsing and team tracking

                self.stats['frames_processed'] += 1

                if self.stats['frames_processed'] % 10 == 0:
                    logger.info(f"📊 Stats: {self.stats}")

            except Exception as e:
                logger.error(f"Error processing frame: {e}")

            finally:
                self.frame_queue.task_done()

    async def run(self):
        """Run backend"""
        logger.info("🚀 Starting GTA Analytics Backend V2")
        logger.info(f"📡 Gateway: {config.GATEWAY_URL}")
        logger.info(f"⚙️  OCR Workers: {config.OCR_WORKERS}")
        logger.info(f"🤖 Vision Model: {config.VISION_MODEL}")

        # Start workers
        workers = [asyncio.create_task(self.worker()) for _ in range(config.OCR_WORKERS)]

        # Start polling
        await self.poller.start_polling(self.process_frames, config.POLL_INTERVAL)


if __name__ == "__main__":
    backend = GTAAnalyticsBackend()

    try:
        asyncio.run(backend.run())
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")
