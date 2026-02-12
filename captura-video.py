#!/usr/bin/env python3
"""
GTA Analytics V2 - Video Frame Extraction and WebRTC Transport
Extracts frames from a saved video file and sends via WebRTC to Gateway
"""

import asyncio
import argparse
import json
import io
import time
from pathlib import Path
from typing import Optional

import cv2
import aiohttp
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCDataChannel
from PIL import Image


class VideoFrameCapture:
    def __init__(self, video_path: str, gateway_url: str, fps: int = 4, quality: int = 85):
        self.video_path = Path(video_path)
        self.gateway_url = gateway_url
        self.fps = fps
        self.quality = quality

        self.pc: Optional[RTCPeerConnection] = None
        self.data_channel: Optional[RTCDataChannel] = None
        self.channel_ready = asyncio.Event()

        self.frames_sent = 0
        self.bytes_sent = 0
        self.start_time = None

    async def connect_webrtc(self):
        """Establish WebRTC connection with Gateway"""
        print(f"Conectando ao Gateway: {self.gateway_url}")

        # Health check
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.gateway_url}/health") as resp:
                    if resp.status != 200:
                        raise Exception(f"Gateway no est saudvel: {resp.status}")
                    print("Gateway online")
            except Exception as e:
                raise Exception(f"Gateway inacessvel: {e}")

        # Create PeerConnection
        self.pc = RTCPeerConnection()

        # Create DataChannel
        self.data_channel = self.pc.createDataChannel("frames", ordered=True, maxRetransmits=0)

        @self.data_channel.on("open")
        def on_open():
            print("DataChannel aberto!")
            self.channel_ready.set()

        @self.data_channel.on("close")
        def on_close():
            print("DataChannel fechado")
            self.channel_ready.clear()

        # Create and send offer
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)

        print(" Enviando SDP offer...")
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
                    raise Exception(f"Offer rejeitado: {response.status}")

                answer_data = await response.json()
                answer = RTCSessionDescription(
                    sdp=answer_data["sdp"],
                    type=answer_data["type"]
                )
                await self.pc.setRemoteDescription(answer)
                print("SDP answer recebido")

        # Wait for DataChannel to open
        print("Aguardando DataChannel...")
        await asyncio.wait_for(self.channel_ready.wait(), timeout=10.0)

    async def send_frame(self, frame_bytes: bytes):
        """Send binary JPEG frame via DataChannel"""
        if not self.data_channel or self.data_channel.readyState != "open":
            print("DataChannel no est aberto, pulando frame")
            return

        try:
            self.data_channel.send(frame_bytes)
            self.frames_sent += 1
            self.bytes_sent += len(frame_bytes)
        except Exception as e:
            print(f"Erro ao enviar frame: {e}")

    async def process_video(self):
        """Extract frames from video and send via WebRTC"""
        if not self.video_path.exists():
            raise FileNotFoundError(f"Vdeo no encontrado: {self.video_path}")

        print(f"\n Abrindo vdeo: {self.video_path.name}")
        cap = cv2.VideoCapture(str(self.video_path))

        if not cap.isOpened():
            raise Exception(f"No foi possvel abrir o vdeo: {self.video_path}")

        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / video_fps if video_fps > 0 else 0

        print(f"   Total de frames: {total_frames}")
        print(f"   FPS do vdeo: {video_fps:.2f}")
        print(f"   Durao: {duration:.1f}s")
        print(f"   FPS de captura: {self.fps}")
        print(f"   Qualidade JPEG: {self.quality}%")

        # Calculate frame skip interval
        frame_interval = max(1, int(video_fps / self.fps))
        print(f"   Processando 1 a cada {frame_interval} frames\n")

        self.start_time = time.time()
        frame_count = 0
        processed_count = 0

        print(" Iniciando processamento de frames...\n")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1

                # Skip frames to match desired FPS
                if frame_count % frame_interval != 0:
                    continue

                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)

                # Encode to JPEG
                buffer = io.BytesIO()
                pil_image.save(buffer, format="JPEG", quality=self.quality, optimize=True)
                frame_bytes = buffer.getvalue()

                # Send via WebRTC
                await self.send_frame(frame_bytes)

                processed_count += 1

                # Progress update
                if processed_count % 10 == 0:
                    elapsed = time.time() - self.start_time
                    fps_actual = processed_count / elapsed if elapsed > 0 else 0
                    progress = (frame_count / total_frames) * 100

                    print(f" Progresso: {progress:.1f}% | "
                          f"Frames enviados: {processed_count} | "
                          f"FPS real: {fps_actual:.2f} | "
                          f"Bytes: {self.bytes_sent / 1024 / 1024:.2f} MB")

                # Respect target FPS timing
                await asyncio.sleep(1.0 / self.fps)

        finally:
            cap.release()

    async def cleanup(self):
        """Close connections"""
        if self.data_channel:
            self.data_channel.close()
        if self.pc:
            await self.pc.close()

    def print_summary(self):
        """Print final statistics"""
        elapsed = time.time() - self.start_time if self.start_time else 0

        print("\n" + "="*60)
        print(" RESUMO DA CAPTURA")
        print("="*60)
        print(f"   Frames enviados:     {self.frames_sent}")
        print(f"   Bytes enviados:      {self.bytes_sent / 1024 / 1024:.2f} MB")
        print(f"   Tempo decorrido:     {elapsed:.2f}s")

        if elapsed > 0:
            print(f"   FPS mdio:           {self.frames_sent / elapsed:.2f}")
            print(f"   Throughput:          {self.bytes_sent / elapsed / 1024:.2f} KB/s")

        if self.frames_sent > 0:
            avg_frame_size = self.bytes_sent / self.frames_sent / 1024
            print(f"   Tamanho mdio/frame: {avg_frame_size:.2f} KB")

        print("="*60 + "\n")


async def main():
    parser = argparse.ArgumentParser(
        description="GTA Analytics V2 - Video Frame Capture via WebRTC"
    )
    parser.add_argument(
        "--video",
        type=str,
        required=True,
        help="Caminho para o arquivo de vdeo (MP4, AVI, etc.)"
    )
    parser.add_argument(
        "--gateway",
        type=str,
        default="http://localhost:8000",
        help="URL do Gateway WebRTC (padro: http://localhost:8000)"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=4,
        help="Frames por segundo para enviar (padro: 4)"
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="Qualidade JPEG 1-100 (padro: 85)"
    )

    args = parser.parse_args()

    print("\n" + "="*60)
    print("GTA ANALYTICS V2 - VIDEO FRAME CAPTURE")
    print("="*60 + "\n")

    capture = VideoFrameCapture(
        video_path=args.video,
        gateway_url=args.gateway,
        fps=args.fps,
        quality=args.quality
    )

    try:
        # Connect to Gateway
        await capture.connect_webrtc()

        # Process video
        await capture.process_video()

        # Show summary
        capture.print_summary()

        print("Processamento concludo!")
        print("\n Verifique os resultados:")
        print(f"   - Gateway stats: {args.gateway}/stats")
        print(f"   - Backend stats: http://localhost:3000/stats")
        print(f"   - Dashboard: Abra dashboard-v2.html no navegador")
        print(f"   - Export Excel: curl http://localhost:3000/export > kills.xlsx\n")

    except KeyboardInterrupt:
        print("\n\nCaptura interrompida pelo usurio")
        capture.print_summary()

    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await capture.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
