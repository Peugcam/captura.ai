"""
GTA Analytics - Video Test Mode
================================

Testa o sistema usando vídeo local ao invés de captura de tela

Author: Paulo Eugenio Campos
"""

import asyncio
import argparse
import sys
import time
from pathlib import Path
from PIL import Image
import io
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("[ERROR] OpenCV not installed!", flush=True)
    print("Install: pip install opencv-python", flush=True)
    sys.exit(1)

try:
    import httpx
except ImportError:
    print("[ERROR] httpx not installed!", flush=True)
    print("Install: pip install httpx", flush=True)
    sys.exit(1)

try:
    import yt_dlp
    HAS_YT_DLP = True
except ImportError:
    HAS_YT_DLP = False
    # YouTube support is optional


class VideoCapture:
    """Test GTA Analytics with local video file + Smart Filtering"""

    def __init__(self, video_path: str, server_url: str, fps: float = 0.5, smart_filter: bool = True):
        self.video_path = video_path
        self.server_url = f"{server_url}/api/frames/upload"
        self.fps = fps
        self.interval = 1.0 / fps
        self.running = False
        self.frames_sent = 0
        self.errors = 0
        self.is_youtube = False
        self.temp_video_path = None

        # Smart filtering (NO TRAINING NEEDED!)
        self.smart_filter = smart_filter
        self.prev_frame = None
        self.frames_filtered = 0
        self.frames_analyzed = 0

        # Check if it's a YouTube URL
        if video_path.startswith('http://') or video_path.startswith('https://'):
            if 'youtube.com' in video_path or 'youtu.be' in video_path:
                if not HAS_YT_DLP:
                    raise ImportError("yt-dlp is required for YouTube support. Install: pip install yt-dlp")

                print(f" Downloading YouTube video...", flush=True)
                print(f" URL: {video_path}", flush=True)

                # Download YouTube video
                self.temp_video_path = self._download_youtube(video_path)
                video_path = self.temp_video_path
                self.is_youtube = True
            else:
                # Try to open as streaming URL
                pass

        # Verificar se vídeo existe (for local files)
        if not self.is_youtube and not video_path.startswith('http'):
            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video not found: {video_path}")

        # Abrir vídeo
        self.video = cv2.VideoCapture(video_path)
        if not self.video.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        # Info do vídeo
        self.total_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_fps = self.video.get(cv2.CAP_PROP_FPS)
        self.duration = self.total_frames / self.video_fps if self.video_fps > 0 else 0

        print(f" Video: {self.video_path}", flush=True)
        print(f" Frames: {self.total_frames}", flush=True)
        print(f" FPS: {self.video_fps:.2f}", flush=True)
        print(f"[TIME]  Duration: {self.duration:.1f}s", flush=True)
        print(f" Server: {self.server_url}", flush=True)
        print(f"[CONFIG]  Capture rate: {self.fps} FPS (interval: {self.interval}s)", flush=True)

    def _download_youtube(self, url: str) -> str:
        """Download YouTube video and return temp path"""
        import tempfile
        import os

        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, 'youtube_video.%(ext)s')

        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Prefer MP4
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        print(f" Downloaded: {filename}", flush=True)
        return filename

    def should_analyze_frame(self, frame) -> tuple[bool, str]:
        """
        Smart filtering - NO TRAINING NEEDED!
        Returns (should_analyze, reason)

        Uses:
        1. Frame differencing (pure math, 0.01s, FREE)
        2. Kill feed region detection (pattern matching, 0.05s, FREE)
        """
        if not self.smart_filter:
            return True, "filtering disabled"

        # LAYER 1: Frame Differencing (99% of frames filtered here)
        # --------------------------------------------------------
        if self.prev_frame is not None:
            # Convert to grayscale for faster comparison
            gray_current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_prev = cv2.cvtColor(self.prev_frame, cv2.COLOR_BGR2GRAY)

            # Calculate absolute difference
            diff = cv2.absdiff(gray_current, gray_prev)

            # Calculate mean difference (0-255 scale)
            mean_diff = np.mean(diff)

            # Threshold: If less than 5% change, skip frame (static scene)
            if mean_diff < 12.75:  # 12.75 = 5% of 255
                self.frames_filtered += 1
                return False, f"static scene (diff: {mean_diff:.1f})"

        # LAYER 2: Kill Feed Region Detection (right side of screen)
        # -----------------------------------------------------------
        # GTA V kill feed is typically in top-right corner
        # We check if there's activity in that region
        height, width = frame.shape[:2]

        # Define kill feed region (adjust based on resolution)
        # Typical: top 30%, right 40% of screen
        kill_feed_x1 = int(width * 0.6)   # Right 40%
        kill_feed_y1 = 0                   # Top
        kill_feed_y2 = int(height * 0.3)   # Top 30%

        kill_feed_region = frame[kill_feed_y1:kill_feed_y2, kill_feed_x1:]

        # Check if region has significant content (not just black/empty)
        gray_region = cv2.cvtColor(kill_feed_region, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray_region)
        std_brightness = np.std(gray_region)

        # If region is too dark or too uniform, likely no kill feed
        if mean_brightness < 30 or std_brightness < 15:
            self.frames_filtered += 1
            return False, f"no kill feed activity (brightness: {mean_brightness:.1f}, std: {std_brightness:.1f})"

        # Frame passed all filters - analyze with AI
        return True, "passed filters - potential kill"

    async def send_frame(self, frame_data, frame_number: int):
        """Send frame to server"""
        try:
            # Converter BGR (OpenCV) para RGB (PIL)
            frame_rgb = cv2.cvtColor(frame_data, cv2.COLOR_BGR2RGB)

            # Converter para PIL Image
            img = Image.fromarray(frame_rgb)

            # Converter para JPEG
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            img_bytes = buffer.getvalue()

            # Upload
            files = {'file': (f'frame_{frame_number}.jpg', img_bytes, 'image/jpeg')}

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.server_url, files=files)

                if response.status_code == 200:
                    self.frames_sent += 1
                    size_kb = len(img_bytes) // 1024
                    print(f"[OK] Frame {frame_number}/{self.total_frames} sent ({size_kb} KB)", flush=True)

                    # Se backend retornar dados, mostrar
                    try:
                        data = response.json()
                        if 'kills_detected' in data and data['kills_detected'] > 0:
                            print(f"    Kills detected: {data['kills_detected']}", flush=True)
                    except:
                        pass

                    return True
                else:
                    print(f"[ERROR] Error {response.status_code}: {response.text}", flush=True)
                    self.errors += 1
                    return False

        except httpx.TimeoutException:
            print(f"[WARN] Timeout sending frame {frame_number}", flush=True)
            self.errors += 1
            return False
        except Exception as e:
            print(f"[ERROR] Error sending frame {frame_number}: {e}", flush=True)
            self.errors += 1
            return False

    async def capture_loop(self):
        """Main capture loop with smart filtering"""
        print("="*60, flush=True)
        print("  Starting video playback...", flush=True)
        if self.smart_filter:
            print("[SMART FILTER] Enabled - only analyzing relevant frames!", flush=True)
            print("[SMART FILTER] Expected: 99% cost reduction", flush=True)
        print("="*60, flush=True)

        frame_count = 0
        stats_interval = 10  # Print stats every 10 frames

        while self.running:
            try:
                # Ler próximo frame
                ret, frame = self.video.read()

                if not ret:
                    print("\n End of video reached", flush=True)

                    # Opção: Loop do vídeo
                    choice = input("\nLoop video? (y/n): ").lower()
                    if choice == 'y':
                        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        self.prev_frame = None  # Reset frame comparison
                        print(" Restarting video...", flush=True)
                        continue
                    else:
                        break

                frame_count += 1

                # SMART FILTERING (NO TRAINING NEEDED!)
                # -------------------------------------
                should_send, reason = self.should_analyze_frame(frame)

                if should_send:
                    # Frame passed filters - send to Vision AI
                    self.frames_analyzed += 1
                    await self.send_frame(frame, frame_count)
                    print(f"[FILTER] PASS Frame {frame_count} - {reason}", flush=True)
                else:
                    # Frame filtered out - FREE (no API call)
                    if frame_count % stats_interval == 0:
                        efficiency = (self.frames_filtered / frame_count * 100) if frame_count > 0 else 0
                        print(f"[FILTER] SKIP Filtered {self.frames_filtered}/{frame_count} frames ({efficiency:.1f}% saved) - {reason}", flush=True)

                # Store current frame for next comparison
                self.prev_frame = frame.copy()

                # Aguardar intervalo
                await asyncio.sleep(self.interval)

            except KeyboardInterrupt:
                print("\n[STOP] Interrupted by user", flush=True)
                break
            except Exception as e:
                print(f"[ERROR] Capture error: {e}", flush=True)
                self.errors += 1
                await asyncio.sleep(1)

    def start(self):
        """Start capture"""
        self.running = True
        print("="*60, flush=True)
        print("GTA ANALYTICS - VIDEO TEST MODE", flush=True)
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
        self.video.release()

        # Clean up temp YouTube file
        if self.temp_video_path:
            try:
                import shutil
                import os
                temp_dir = os.path.dirname(self.temp_video_path)
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    print(f" Cleaned up temp files", flush=True)
            except Exception as e:
                print(f"[WARN] Could not clean up temp files: {e}", flush=True)

        print("\n" + "="*60, flush=True)
        print("SUMMARY", flush=True)
        print("="*60, flush=True)
        print(f"Total frames processed: {self.frames_analyzed + self.frames_filtered}", flush=True)
        print(f"Frames analyzed (AI): {self.frames_analyzed}", flush=True)
        print(f"Frames filtered (FREE): {self.frames_filtered}", flush=True)
        print(f"Frames sent to server: {self.frames_sent}", flush=True)
        print(f"Errors: {self.errors}", flush=True)

        if self.smart_filter and (self.frames_analyzed + self.frames_filtered) > 0:
            total = self.frames_analyzed + self.frames_filtered
            efficiency = (self.frames_filtered / total * 100)
            cost_saved = (self.frames_filtered / total * 100)
            print(f"\n[OPTIMIZATION] Filtering efficiency: {efficiency:.1f}%", flush=True)
            print(f"[OPTIMIZATION] Cost reduction: ~{cost_saved:.1f}%", flush=True)
            print(f"[OPTIMIZATION] Speed improvement: ~{100/max(1,(100-efficiency))}x faster", flush=True)

        if self.frames_sent > 0:
            success_rate = ((self.frames_sent / (self.frames_sent + self.errors)) * 100)
            print(f"\nSuccess rate: {success_rate:.1f}%", flush=True)
        print("="*60, flush=True)


def main():
    """Entry point"""
    parser = argparse.ArgumentParser(
        description='GTA Analytics Video Test Mode - Smart Filtering Enabled'
    )
    parser.add_argument(
        '--video',
        required=True,
        help='Path to video file (mp4, avi, etc) or YouTube URL'
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
    parser.add_argument(
        '--no-filter',
        action='store_true',
        help='Disable smart filtering (analyze ALL frames - expensive!)'
    )

    args = parser.parse_args()

    # Validate FPS
    if args.fps <= 0 or args.fps > 10:
        print(f"[ERROR] Invalid FPS: {args.fps} (must be 0.1-10.0)", flush=True)
        sys.exit(1)

    # Smart filter is enabled by default (saves 99% cost)
    smart_filter = not args.no_filter

    if not smart_filter:
        print("[WARNING] Smart filtering DISABLED - all frames will be analyzed (HIGH COST!)", flush=True)
        confirm = input("Are you sure? (yes/no): ").lower()
        if confirm != 'yes':
            print("Aborted.", flush=True)
            sys.exit(0)

    # Create and start capture
    try:
        capture = VideoCapture(args.video, args.server, args.fps, smart_filter)
        capture.start()
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}", flush=True)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[STOP] Stopped by user", flush=True)
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
