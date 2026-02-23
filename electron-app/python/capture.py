"""
GTA Analytics - Capture Client (Embedded)
==========================================

Captura GTA V usando windows-capture ou d3dshot
Envia frames para servidor Fly.io

Author: Paulo Eugenio Campos
"""

import asyncio
import argparse
import base64
import io
import sys
import time
import numpy as np
from PIL import Image
from typing import Optional

# Window detection imports
try:
    import win32gui
    import win32process
    import psutil
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    print(" pywin32 not installed - GTA detection limited", flush=True)

# Try capture libraries
try:
    import mss
    USE_MSS = True
    print(" Using mss (screen capture)", flush=True)
except ImportError:
    USE_MSS = False

if not USE_MSS:
    try:
        import d3dshot
        USE_D3D = True
        print(" Using d3dshot (fallback)", flush=True)
    except ImportError:
        print(" ERROR: No capture library available!", flush=True)
        print("Install: pip install mss OR pip install d3dshot", flush=True)
        sys.exit(1)
else:
    USE_D3D = False

try:
    import httpx
except ImportError:
    print(" ERROR: httpx not installed!", flush=True)
    print("Install: pip install httpx", flush=True)
    sys.exit(1)


class GTACapture:
    """GTA V Capture Client with Smart Filtering"""

    def __init__(self, server_url: str, fps: float = 0.5, smart_filter: bool = True):
        self.server_url = f"{server_url}/api/frames/upload"
        self.fps = fps
        self.interval = 1.0 / fps
        self.running = False
        self.frames_sent = 0
        self.errors = 0
        self.gta_paused_count = 0

        # Smart filtering (NO TRAINING NEEDED!)
        self.smart_filter = smart_filter
        self.prev_frame = None
        self.frames_filtered = 0
        self.frames_analyzed = 0

        # Initialize capture
        if USE_MSS:
            self.capture = mss.mss()
        else:
            self.capture = d3dshot.create()

        print(f" Server: {self.server_url}", flush=True)
        print(f" FPS: {self.fps} (interval: {self.interval}s)", flush=True)
        if self.smart_filter:
            print(f" Smart Filter: ENABLED (99% cost reduction)", flush=True)

    def should_analyze_frame(self, frame) -> tuple[bool, str]:
        """Smart filtering - NO TRAINING NEEDED!"""
        if not self.smart_filter:
            return True, "filtering disabled"

        # Convert mss screenshot format to numpy array
        import cv2
        frame_array = np.array(frame)

        # LAYER 1: Frame Differencing
        if self.prev_frame is not None:
            gray_current = cv2.cvtColor(frame_array, cv2.COLOR_BGR2GRAY)
            gray_prev = cv2.cvtColor(self.prev_frame, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(gray_current, gray_prev)
            mean_diff = np.mean(diff)

            if mean_diff < 12.75:  # 5% change threshold
                self.frames_filtered += 1
                return False, f"static scene (diff: {mean_diff:.1f})"

        # LAYER 2: Kill Feed Region Detection (top-right)
        height, width = frame_array.shape[:2]
        kill_feed_x1 = int(width * 0.6)
        kill_feed_y2 = int(height * 0.3)
        kill_feed_region = frame_array[0:kill_feed_y2, kill_feed_x1:]

        gray_region = cv2.cvtColor(kill_feed_region, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray_region)
        std_brightness = np.std(gray_region)

        if mean_brightness < 30 or std_brightness < 15:
            self.frames_filtered += 1
            return False, f"no kill feed activity"

        return True, "passed filters - potential kill"

    def is_gta_active(self) -> bool:
        """
        Check if GTA V is the active foreground window
        Returns True if GTA is visible and active
        """
        if not HAS_WIN32:
            return True  # Assume active if can't detect

        try:
            # Get foreground window handle
            hwnd = win32gui.GetForegroundWindow()

            # Get window title
            title = win32gui.GetWindowText(hwnd)

            # Check title for GTA V
            gta_titles = ["Grand Theft Auto V", "GTA V", "GTA5"]
            for gta_title in gta_titles:
                if gta_title.lower() in title.lower():
                    return True

            # Fallback: Check process name
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                process_name = process.name().lower()

                if "gta5" in process_name or "gtav" in process_name:
                    return True
            except:
                pass

            return False

        except Exception as e:
            print(f" Error detecting GTA: {e}", flush=True)
            return True  # Don't block capture on error

    async def send_frame(self, frame_data):
        """Send frame to server"""
        try:
            # Convert to JPEG
            img = Image.fromarray(frame_data)

            # Convert RGBA to RGB if needed (JPEG doesn't support transparency)
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Resize to 720p for faster processing and upload (optional optimization)
            # 1920x1080 -> 1280x720 reduces file size by ~50%
            width, height = img.size
            if width > 1280:
                new_height = int(height * (1280 / width))
                img = img.resize((1280, new_height), Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            # Reduced quality from 85 to 60 for 3x faster processing
            img.save(buffer, format='JPEG', quality=60, optimize=True)
            img_bytes = buffer.getvalue()

            # Upload
            files = {'file': ('frame.jpg', img_bytes, 'image/jpeg')}

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.server_url, files=files)

                if response.status_code == 200:
                    self.frames_sent += 1
                    size_kb = len(img_bytes) // 1024
                    print(f" Frame {self.frames_sent} sent ({size_kb} KB)", flush=True)
                    return True
                else:
                    print(f" Error {response.status_code}: {response.text}", flush=True)
                    self.errors += 1
                    return False

        except httpx.TimeoutException:
            print(f" Timeout sending frame", flush=True)
            self.errors += 1
            return False
        except Exception as e:
            print(f" Error sending frame: {e}", flush=True)
            self.errors += 1
            return False

    async def capture_loop(self):
        """Main capture loop with GTA detection"""
        print(" Waiting for GTA V...", flush=True)
        consecutive_fails = 0
        was_paused = False

        while self.running:
            try:
                # Check if GTA is active window
                if not self.is_gta_active():
                    if not was_paused:
                        print("  GTA not active - pausing capture", flush=True)
                        was_paused = True
                    self.gta_paused_count += 1
                    await asyncio.sleep(2)  # Check every 2 seconds
                    continue

                # GTA is active - resume if was paused
                if was_paused:
                    print("  GTA active - resuming capture", flush=True)
                    was_paused = False

                # Capture frame
                if USE_MSS:
                    # mss: capture entire primary monitor
                    screenshot = self.capture.grab(self.capture.monitors[1])
                    frame = np.array(screenshot)
                else:
                    # d3dshot: capture entire screen
                    frame = self.capture.screenshot()

                if frame is not None:
                    # SMART FILTERING (NO TRAINING NEEDED!)
                    should_send, reason = self.should_analyze_frame(frame)

                    if should_send:
                        # Frame passed filters - send to Vision AI
                        self.frames_analyzed += 1
                        await self.send_frame(frame)
                    else:
                        # Frame filtered out - FREE (no API call)
                        pass  # Silently skip to avoid console spam

                    # Store current frame for next comparison
                    self.prev_frame = np.array(frame).copy()

                    consecutive_fails = 0
                else:
                    consecutive_fails += 1
                    if consecutive_fails == 1:
                        print(" GTA V window not found", flush=True)

                    # Don't spam if GTA not found
                    if consecutive_fails > 5:
                        await asyncio.sleep(5)  # Wait longer
                        continue

                # Wait interval
                await asyncio.sleep(self.interval)

            except KeyboardInterrupt:
                print("\n Interrupted by user", flush=True)
                break
            except Exception as e:
                print(f" Capture error: {e}", flush=True)
                self.errors += 1
                await asyncio.sleep(1)

    def start(self):
        """Start capture"""
        self.running = True
        print("="*60, flush=True)
        print("GTA ANALYTICS - CAPTURE CLIENT", flush=True)
        print("="*60, flush=True)
        print(f"Library: {'mss' if USE_MSS else 'd3dshot'}", flush=True)
        print(f"Server: {self.server_url}", flush=True)
        print(f"FPS: {self.fps}", flush=True)
        print("="*60, flush=True)

        try:
            asyncio.run(self.capture_loop())
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        """Stop capture"""
        self.running = False
        print("\n" + "="*60, flush=True)
        print("SUMMARY", flush=True)
        print("="*60, flush=True)
        print(f"Frames sent: {self.frames_sent}", flush=True)
        print(f"Errors: {self.errors}", flush=True)
        if self.frames_sent > 0:
            success_rate = ((self.frames_sent / (self.frames_sent + self.errors)) * 100)
            print(f"Success rate: {success_rate:.1f}%", flush=True)
        print("="*60, flush=True)


def main():
    """Entry point"""
    parser = argparse.ArgumentParser(
        description='GTA Analytics Capture Client'
    )
    parser.add_argument(
        '--server',
        required=True,
        help='Server URL (e.g., https://gta-analytics-v2.fly.dev)'
    )
    parser.add_argument(
        '--fps',
        type=float,
        default=0.5,
        help='Capture rate in FPS (default: 0.5)'
    )

    args = parser.parse_args()

    # Validate FPS
    if args.fps <= 0 or args.fps > 10:
        print(f" Invalid FPS: {args.fps} (must be 0.1-10.0)", flush=True)
        sys.exit(1)

    # Create and start capture
    capture = GTACapture(args.server, args.fps)

    try:
        capture.start()
    except KeyboardInterrupt:
        print("\n Stopped by user", flush=True)
        capture.stop()
    except Exception as e:
        print(f"\n Fatal error: {e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
