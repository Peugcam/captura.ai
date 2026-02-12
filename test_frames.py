"""
Test Frame Analysis Script
Testa o pipeline completo com frames extraídos do vídeo
"""
import sys
import os
import base64
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import backend modules
from processor import OCRPreFilter, VisionProcessor
import config

def load_frame_as_base64(image_path: str) -> str:
    """Load image file and convert to base64"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')

def test_ocr_filter(frames_dir: str):
    """Test OCR pre-filter on extracted frames"""
    logger.info("=" * 80)
    logger.info("🔍 TESTING OCR PRE-FILTER")
    logger.info("=" * 80)

    # Initialize OCR filter
    ocr_filter = OCRPreFilter(config.OCR_KEYWORDS)

    logger.info(f"📋 OCR Keywords ({len(config.OCR_KEYWORDS)}): {config.OCR_KEYWORDS}")
    logger.info(f"🎮 Game Type: {config.GAME_TYPE}")
    logger.info(f"✂️ ROI Enabled: {config.USE_ROI}")
    logger.info("")

    # Get all frame files
    frames_path = Path(frames_dir)
    frame_files = sorted(frames_path.glob("frame_*.jpg"))

    if not frame_files:
        logger.error(f"❌ No frames found in {frames_dir}")
        return []

    logger.info(f"📦 Found {len(frame_files)} frames to test")
    logger.info("")

    # Test each frame
    passed_frames = []
    for i, frame_file in enumerate(frame_files, 1):
        logger.info(f"Frame {i}/{len(frame_files)}: {frame_file.name}")

        # Load frame as base64
        frame_b64 = load_frame_as_base64(str(frame_file))

        # Test OCR filter
        has_keywords = ocr_filter.has_kill_keywords(frame_b64)

        if has_keywords:
            logger.info(f"  ✅ PASSED - Kill keywords detected!")
            passed_frames.append((frame_file, frame_b64))
        else:
            logger.info(f"  ❌ REJECTED - No kill keywords found")

        logger.info("")

    logger.info("=" * 80)
    logger.info(f"📊 OCR FILTER RESULTS:")
    logger.info(f"  Total frames: {len(frame_files)}")
    logger.info(f"  Passed: {len(passed_frames)}")
    logger.info(f"  Rejected: {len(frame_files) - len(passed_frames)}")
    logger.info(f"  Pass rate: {(len(passed_frames) / len(frame_files) * 100):.1f}%")
    logger.info("=" * 80)
    logger.info("")

    return passed_frames

def test_vision_api(frames_with_b64):
    """Test Vision API on frames that passed OCR filter"""
    if not frames_with_b64:
        logger.warning("⚠️ No frames passed OCR filter - skipping Vision API test")
        return

    logger.info("=" * 80)
    logger.info("🤖 TESTING VISION API")
    logger.info("=" * 80)

    # Initialize Vision processor
    vision = VisionProcessor(config.API_KEYS, config.VISION_MODEL)

    logger.info(f"🔑 API Keys: {len(config.API_KEYS)} configured")
    logger.info(f"🧠 Model: {config.VISION_MODEL}")
    logger.info(f"📦 Processing {len(frames_with_b64)} frames")
    logger.info("")

    # Extract just base64 data
    frames_b64 = [frame_b64 for _, frame_b64 in frames_with_b64]

    # Process batch
    kills = vision.process_batch(frames_b64)

    logger.info("")
    logger.info("=" * 80)
    logger.info(f"📊 VISION API RESULTS:")
    logger.info(f"  Frames processed: {len(frames_b64)}")
    logger.info(f"  Kills detected: {len(kills)}")
    logger.info("=" * 80)

    if kills:
        logger.info("")
        logger.info("🎯 DETECTED KILLS:")
        for i, kill in enumerate(kills, 1):
            logger.info(f"  Kill {i}:")
            logger.info(f"    Killer: {kill.get('killer', 'Unknown')}")
            logger.info(f"    Victim: {kill.get('victim', 'Unknown')}")
            logger.info(f"    Weapon/Method: {kill.get('distance', 'Unknown')}")
            logger.info(f"    Killer Team: {kill.get('killer_team', 'Unknown')}")
            logger.info(f"    Victim Team: {kill.get('victim_team', 'Unknown')}")

    logger.info("")
    return kills

def main():
    """Run complete pipeline test"""
    # Frames directory
    frames_dir = "test_frames"

    logger.info("")
    logger.info("🚀 STARTING GTA ANALYTICS PIPELINE TEST")
    logger.info("")

    # Test 1: OCR Filter
    passed_frames = test_ocr_filter(frames_dir)

    # Test 2: Vision API (only if frames passed OCR)
    if passed_frames:
        kills = test_vision_api(passed_frames)
    else:
        logger.warning("⚠️ No frames passed OCR filter - Vision API test skipped")
        logger.warning("💡 This might indicate:")
        logger.warning("   - Frames don't contain kill feed text")
        logger.warning("   - OCR keywords need adjustment")
        logger.warning("   - ROI settings need tuning")

    logger.info("")
    logger.info("✅ TEST COMPLETE")
    logger.info("")

if __name__ == "__main__":
    main()
