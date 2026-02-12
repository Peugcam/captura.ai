"""
GTA Analytics V2 - Python Backend COMPLETO
===========================================

Backend com TODAS as features:
- Polling HTTP do gateway Go
- OCR pré-filtro em thread pool
- GPT-4o Vision API batch processing
- Team tracking em tempo real
- Excel export

Author: Paulo Eugenio Campos
"""

import asyncio
import httpx
import logging
import time
from typing import List, Dict
from datetime import datetime
from collections import deque
import config
from processor import FrameProcessor

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
                if frames:
                    logger.info(f"📥 Fetched {len(frames)} frames from gateway")
                return frames

        except Exception as e:
            logger.error(f"Error fetching frames: {e}")

        return []

    async def close(self):
        """Close the HTTP client to release connections"""
        await self.client.aclose()
        logger.info("🔌 HTTP client closed")

    async def start_polling(self, callback, interval: float = 1.0):
        """Start continuous polling"""
        logger.info(f"🔄 Started polling gateway every {interval}s")

        while True:
            frames = await self.fetch_frames()

            if frames:
                await callback(frames)

            await asyncio.sleep(interval)


class GTAAnalyticsBackend:
    """Main backend application with all features"""

    def __init__(self):
        self.poller = FramePoller(config.GATEWAY_URL)
        self.processor = FrameProcessor()
        # BACKPRESSURE (Gemini Optimization): Limit buffer size
        # 30 frames max to prevent OOM. Drops older frames if full.
        self.frame_buffer = deque(maxlen=30)
        self.frames_dropped_buffer = 0
        
        self.last_batch_time = time.time()

        logger.info("✅ Frame Processor initialized")
        logger.info(f"   OCR Enabled: {config.OCR_ENABLED}")
        logger.info(f"   OCR Workers: {config.OCR_WORKERS}")
        logger.info(f"   Vision Model: {config.VISION_MODEL}")
        logger.info(f"   Quick Batch: {config.BATCH_SIZE_QUICK} frames / {config.QUICK_BATCH_INTERVAL}s")
        logger.info(f"   Deep Batch: {config.BATCH_SIZE_DEEP} frames / {config.DEEP_BATCH_INTERVAL}s")

    async def process_frames(self, frames: List[Dict]):
        """Process batch of frames"""
        for frame in frames:
            # OCR pré-filtro
            frame_data = await self.processor.process_frame(frame)

            if frame_data:
                self.frame_buffer.append(frame_data)
                # deque(maxlen=30) auto-drops oldest when full

        # Check se deve processar batch
        await self.check_batch_processing()

    async def check_batch_processing(self):
        """Verifica se deve processar batch"""
        current_time = time.time()
        elapsed = current_time - self.last_batch_time

        # Quick batch (a cada 2s se tiver 5+ frames)
        if elapsed >= config.QUICK_BATCH_INTERVAL and len(self.frame_buffer) >= config.BATCH_SIZE_QUICK:
            await self.process_batch(config.BATCH_SIZE_QUICK)

        # Deep batch (a cada 60s se tiver 15+ frames)
        elif elapsed >= config.DEEP_BATCH_INTERVAL and len(self.frame_buffer) >= config.BATCH_SIZE_DEEP:
            await self.process_batch(config.BATCH_SIZE_DEEP)

    async def process_batch(self, batch_size: int):
        """Processa batch de frames com GPT-4o"""
        if not self.frame_buffer:
            return

        # Pegar batch
        batch = list(self.frame_buffer)[:batch_size]
        # Remove consumed items from deque
        for _ in range(min(batch_size, len(self.frame_buffer))):
            self.frame_buffer.popleft()

        logger.info(f"🔄 Processing batch of {len(batch)} frames...")

        # Processar com Vision AI
        kills = self.processor.process_batch(batch)

        if kills:
            logger.info(f"🎯 Detected {len(kills)} kills!")
            for kill in kills:
                logger.info(f"   {kill['killer']} ({kill['killer_team']}) -> {kill['victim']} ({kill['victim_team']})")

        # Mostrar stats
        stats = self.processor.get_stats()
        logger.info(f"📊 Stats: {stats['frames_processed']} processed | {stats['kills_detected']} kills | {stats['alive']} alive")

        self.last_batch_time = time.time()

    async def stats_reporter(self):
        """Reporta estatísticas periodicamente"""
        while True:
            await asyncio.sleep(30)  # A cada 30s

            stats = self.processor.get_stats()
            logger.info("="*60)
            logger.info("📊 STATISTICS REPORT")
            logger.info("="*60)
            logger.info(f"Frames Received: {stats['frames_received']}")
            logger.info(f"Frames Filtered (OCR): {stats['frames_filtered']} ({stats['filter_efficiency']})")
            logger.info(f"Frames Processed (AI): {stats['frames_processed']}")
            logger.info(f"Kills Detected: {stats['kills_detected']}")
            logger.info(f"Teams: {stats['teams']} | Players: {stats['players']}")
            logger.info(f"Alive: {stats['alive']} | Dead: {stats['dead']}")
            logger.info("="*60)

    async def run(self):
        """Run backend"""
        logger.info("="*60)
        logger.info("🚀 Starting GTA Analytics Backend V2 - COMPLETE")
        logger.info("="*60)
        logger.info(f"📡 Gateway: {config.GATEWAY_URL}")
        logger.info(f"⚙️  OCR Workers: {config.OCR_WORKERS}")
        logger.info(f"🤖 Vision Model: {config.VISION_MODEL}")
        logger.info(f"💾 Export Dir: {config.EXPORT_DIR}")
        logger.info("="*60)

        # Start stats reporter
        asyncio.create_task(self.stats_reporter())

        # Start polling
        await self.poller.start_polling(self.process_frames, config.POLL_INTERVAL)


if __name__ == "__main__":
    backend = GTAAnalyticsBackend()

    try:
        asyncio.run(backend.run())
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down...")
        logger.info("📊 Generating final report...")

        # Export final results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{config.EXPORT_DIR}/gta_match_{timestamp}.xlsx"

        try:
            backend.processor.export_to_excel(filename)
            logger.info(f"✅ Results exported to: {filename}")
        except Exception as e:
            logger.error(f"Export error: {e}")

        # Close HTTP client to prevent connection leaks
        try:
            asyncio.get_event_loop().run_until_complete(backend.poller.close())
        except Exception:
            pass

        logger.info("👋 Goodbye!")
