"""
GTA Analytics - Cliente para Backend V2
"""
import sys, io, os, json, time, base64
from PIL import Image

try:
    import obsws_python as obs
    import requests
except ImportError:
    print("[ERRO] Instale: pip install obsws-python requests pillow")
    sys.exit(1)

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
config = json.load(open(CONFIG_FILE)) if os.path.exists(CONFIG_FILE) else {"backend_url": "https://gta-analytics-v2.fly.dev", "fps": 1, "kill_feed_region": {"x": 1400, "y": 0, "width": 520, "height": 400}}

OBS_HOST, OBS_PORT, OBS_PASSWORD = "localhost", 4455, "ZNx3v4LjLVCgbTrO"
BACKEND_URL = "https://gta-analytics-v2.fly.dev"
CAPTURE_FPS = config["fps"]
KILL_FEED_REGION = config["kill_feed_region"]
frame_count, errors = 0, 0

def crop_kill_feed(image):
    if image.mode == 'RGBA':
        rgb_image = Image.new('RGB', image.size, (0, 0, 0))
        rgb_image.paste(image, mask=image.split()[3])
        image = rgb_image
    elif image.mode != 'RGB':
        image = image.convert('RGB')
    left, top = KILL_FEED_REGION["x"], KILL_FEED_REGION["y"]
    right, bottom = left + KILL_FEED_REGION["width"], top + KILL_FEED_REGION["height"]
    return image.crop((left, top, right, bottom))

def send_frame(image_data):
    global errors
    try:
        buffer = io.BytesIO()
        image_data.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        files = {'file': ('frame.jpg', buffer, 'image/jpeg')}
        response = requests.post(f"{BACKEND_URL}/api/frames/upload", files=files, timeout=10)
        if response.status_code == 200:
            errors = 0
            return True
        else:
            errors += 1
            if errors % 10 == 1:
                print(f"[ERRO] HTTP {response.status_code}")
            return False
    except Exception as e:
        errors += 1
        if errors % 10 == 1:
            print(f"[ERRO] {e}")
        return False

def main():
    global frame_count
    print("=" * 70)
    print("   GTA ANALYTICS V2 - BACKEND")
    print(f"   Dashboard: {BACKEND_URL}/strategist")
    print("=" * 70)
    print()
    
    try:
        cl = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=OBS_PASSWORD, timeout=3)
        current_scene = cl.get_current_program_scene()
        scene_name = current_scene.current_program_scene_name
        print(f"[OK] OBS conectado | Cena: {scene_name}")
        print("[*] CAPTURA ATIVA - Pressione Ctrl+C para parar")
        print()
        
        start_time = time.time()
        frame_interval = 1.0 / CAPTURE_FPS
        last_frame_time = 0
        
        while True:
            current_time = time.time()
            if current_time - last_frame_time >= frame_interval:
                try:
                    response = cl.get_source_screenshot(name=scene_name, img_format="png", width=1920, height=1080, quality=-1)
                    img_data = response.image_data
                    if img_data and ',' in img_data:
                        img_data = img_data.split(',', 1)[1]
                    img_bytes = base64.b64decode(img_data)
                    img = Image.open(io.BytesIO(img_bytes))
                    kill_feed = crop_kill_feed(img)
                    
                    if send_frame(kill_feed):
                        frame_count += 1
                        if frame_count % 5 == 0 or frame_count == 1:
                            elapsed = time.time() - start_time
                            fps = frame_count / elapsed
                            print(f"[{frame_count} frames] {elapsed:.0f}s | {fps:.1f} FPS | {errors} erros")
                    
                    last_frame_time = current_time
                except Exception as e:
                    if frame_count % 10 == 0:
                        print(f"[ERRO] Captura: {e}")
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\n[*] Interrompido")
    finally:
        print(f"\nTotal: {frame_count} frames")

if __name__ == "__main__":
    main()
