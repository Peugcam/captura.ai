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


class VideoCapture:
    """Test GTA Analytics with local video file"""

    def __init__(self, video_path: str, server_url: str, fps: float = 0.5):
        self.video_path = video_path
        self.server_url = f"{server_url}/api/frames/upload"
        self.fps = fps
        self.interval = 1.0 / fps
        self.running = False
        self.frames_sent = 0
        self.errors = 0

        # Verificar se vídeo existe
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

        print(f" Video: {video_path}", flush=True)
        print(f" Frames: {self.total_frames}", flush=True)
        print(f" FPS: {self.video_fps:.2f}", flush=True)
        print(f"[TIME]  Duration: {self.duration:.1f}s", flush=True)
        print(f" Server: {self.server_url}", flush=True)
        print(f"[CONFIG]  Capture rate: {self.fps} FPS (interval: {self.interval}s)", flush=True)

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
        """Main capture loop"""
        print("="*60, flush=True)
        print("  Starting video playback...", flush=True)
        print("="*60, flush=True)

        frame_count = 0

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
                        print(" Restarting video...", flush=True)
                        continue
                    else:
                        break

                frame_count += 1

                # Enviar frame
                await self.send_frame(frame, frame_count)

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
        description='GTA Analytics Video Test Mode'
    )
    parser.add_argument(
        '--video',
        required=True,
        help='Path to video file (mp4, avi, etc)'
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
        print(f"[ERROR] Invalid FPS: {args.fps} (must be 0.1-10.0)", flush=True)
        sys.exit(1)

    # Create and start capture
    try:
        capture = VideoCapture(args.video, args.server, args.fps)
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
