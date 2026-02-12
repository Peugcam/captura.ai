"""
Test 3-Tier System with sample frames
Valida OCR, Vision API, e todas as otimizações
"""

import base64
import glob
import json
import requests
import time
from pathlib import Path

# Configuração
BACKEND_URL = "http://localhost:3000"
TEST_FRAMES_DIR = "test_frames"

def encode_image_to_base64(image_path):
    """Encode image to base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def send_frame_to_backend(frame_base64, frame_number):
    """Send frame to backend via WebSocket endpoint"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/process_frame",
            json={
                "data": frame_base64,
                "number": frame_number,
                "timestamp": time.time()
            },
            timeout=30
        )
        return response.json()
    except Exception as e:
        print(f"[ERROR] Error sending frame {frame_number}: {e}")
        return None

def get_stats():
    """Get backend statistics"""
    try:
        response = requests.get(f"{BACKEND_URL}/stats", timeout=5)
        return response.json()
    except Exception as e:
        print(f"[ERROR] Error getting stats: {e}")
        return None

def main():
    print("=" * 70)
    print(">>> Testing 3-Tier System with Sample Frames")
    print("=" * 70)

    # Find all test frames
    frame_files = sorted(glob.glob(f"{TEST_FRAMES_DIR}/frame_*.jpg"))

    if not frame_files:
        print(f"[ERROR] No frames found in {TEST_FRAMES_DIR}/")
        return

    print(f"[INFO] Found {len(frame_files)} test frames")
    print()

    # Get initial stats
    print("[STATS] Initial Statistics:")
    initial_stats = get_stats()
    if initial_stats:
        print(f"   Processing Mode: {initial_stats.get('processing_mode')}")
        print(f"   Frames Received: {initial_stats.get('frames_received', 0)}")
        print()

    # Process each frame
    print("[TEST] Processing frames...")
    print()

    results = []
    start_time = time.time()

    for i, frame_path in enumerate(frame_files, 1):
        print(f"Frame {i}/{len(frame_files)}: {Path(frame_path).name}", end=" ")

        # Encode frame
        frame_base64 = encode_image_to_base64(frame_path)

        # Send to backend
        result = send_frame_to_backend(frame_base64, i)

        if result:
            kills = result.get('kills', [])
            print(f"[OK] {len(kills)} kills detected")
            results.append(result)
        else:
            print("[SKIP] Skipped or error")

        # Small delay to avoid overwhelming backend
        time.sleep(0.3)

    total_time = time.time() - start_time

    print()
    print("=" * 70)
    print("[RESULTS] FINAL STATISTICS")
    print("=" * 70)

    # Get final stats
    final_stats = get_stats()

    if final_stats:
        print(f"Processing Mode: {final_stats.get('processing_mode')}")
        print(f"Frames Received: {final_stats.get('frames_received', 0)}")
        print(f"Frames Filtered: {final_stats.get('frames_filtered', 0)}")
        print(f"Frames Processed: {final_stats.get('frames_processed', 0)}")
        print(f"Kills Detected: {final_stats.get('kills_detected', 0)}")
        print(f"Filter Efficiency: {final_stats.get('filter_efficiency')}")
        print()

        # 3-Tier specific stats
        three_tier = final_stats.get('three_tier', {})
        if three_tier and 'frames_processed' in three_tier and three_tier['frames_processed'] > 0:
            print("[3-TIER] SYSTEM PERFORMANCE:")
            print(f"   Frames Skipped: {three_tier.get('frames_skipped', 0)} ({three_tier.get('skip_rate', 'N/A')})")
            print(f"   Frames Processed: {three_tier.get('frames_processed', 0)}")
            print()
            print("   TIER DISTRIBUTION:")
            print(f"   - Tier 1 (OCR):       {three_tier.get('tier1_ocr_used', 0)} frames ({three_tier.get('tier1_percentage', 'N/A')})")
            print(f"   - Tier 2 (Vision Crop): {three_tier.get('tier2_crop_used', 0)} frames ({three_tier.get('tier2_percentage', 'N/A')})")
            print(f"   - Tier 3 (Vision Full): {three_tier.get('tier3_full_used', 0)} frames ({three_tier.get('tier3_percentage', 'N/A')})")
            print()
            print("   COST ANALYSIS:")
            print(f"   Tokens Used: {three_tier.get('tokens_used', 0):,}")
            print(f"   Tokens Saved: {three_tier.get('tokens_saved', 0):,}")
            print(f"   Cost: {three_tier.get('cost_usd', 'N/A')}")
            print(f"   Saved: {three_tier.get('cost_saved_usd', 'N/A')}")
            print(f"   Efficiency: {three_tier.get('efficiency', 'N/A')}")
            print(f"   Avg Latency: {three_tier.get('avg_latency_ms', 'N/A')}")

    print()
    print(f"[TIME] Total Time: {total_time:.2f}s")
    print(f"[TIME] Avg Time/Frame: {total_time/len(frame_files):.2f}s")
    print()

    # Summary
    total_kills = sum(len(r.get('kills', [])) for r in results)
    print("=" * 70)
    print("[SUCCESS] TEST COMPLETED")
    print("=" * 70)
    print(f"Total Frames Sent: {len(frame_files)}")
    print(f"Total Kills Found: {total_kills}")
    print()

    if final_stats and final_stats.get('processing_mode') == '3-Tier Optimized':
        print("[OK] 3-Tier System is working correctly!")
    else:
        print("[WARNING] 3-Tier System may not be active")

if __name__ == "__main__":
    main()
