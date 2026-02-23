"""
Teste Simples de Captura - MSS para Gateway
"""
import mss
import base64
import requests
import time
from PIL import Image
import io

# Config
GATEWAY_URL = "http://localhost:8000"
FPS = 2
MAX_FRAMES = 10

print("=" * 60)
print("  TESTE DE CAPTURA MSS")
print("=" * 60)
print()
print(f"Gateway: {GATEWAY_URL}")
print(f"FPS: {FPS}")
print(f"Frames: {MAX_FRAMES}")
print()

# Test Gateway
try:
    r = requests.get(f"{GATEWAY_URL}/health", timeout=5)
    print(f"[OK] Gateway: {r.json()}")
except Exception as e:
    print(f"[ERRO] Gateway offline: {e}")
    exit(1)

print()

# MSS Setup
sct = mss.mss()
monitor = sct.monitors[1]

print("Capturando e enviando frames...")
print("-" * 60)

sent = 0
for i in range(MAX_FRAMES):
    # Capture
    img_raw = sct.grab(monitor)
    img = Image.frombytes("RGB", img_raw.size, img_raw.bgra, "raw", "BGRX")

    # To JPEG
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=60)
    img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Send as multipart/form-data
    try:
        files = {'file': ('frame.jpg', buffer.getvalue(), 'image/jpeg')}
        r = requests.post(
            f"{GATEWAY_URL}/upload",
            files=files,
            timeout=5
        )
        if r.status_code == 200:
            sent += 1
            print(f"[{sent}/{MAX_FRAMES}] Frame sent | Size: {len(buffer.getvalue())/1024:.1f} KB")
        else:
            print(f"[ERRO] Upload failed: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"[ERRO] Send failed: {e}")

    time.sleep(1.0 / FPS)

print("-" * 60)
print()
print(f"[OK] {sent} frames sent!")
print()
print("Check backend logs for processing...")
print()
