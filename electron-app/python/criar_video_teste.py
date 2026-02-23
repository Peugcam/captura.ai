"""
Cria vídeo de teste sintético para GTA Analytics
Simula um kill feed do GTA V
"""

import cv2
import numpy as np
from datetime import datetime

print("Criando vídeo de teste...")

# Configurações
width, height = 1280, 720
fps = 30
duration = 30  # segundos
total_frames = fps * duration

# Criar video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('test_gta_synthetic.mp4', fourcc, fps, (width, height))

# Simular kills em frames específicos
kills = [
    (90, "xXSniperXx eliminated NoobPlayer"),
    (180, "ProGamer killed Camper123"),
    (270, "xXSniperXx eliminated TryHard"),
    (360, "ProGamer killed xXSniperXx"),
    (450, "Camper123 eliminated NewPlayer"),
    (540, "ProGamer eliminated NoobPlayer"),
    (630, "xXSniperXx killed Camper123"),
    (720, "TryHard eliminated ProGamer"),
]

kill_texts = {}
for frame_num, text in kills:
    kill_texts[frame_num] = text

print(f"Gerando {total_frames} frames ({duration}s @ {fps}fps)...")

for i in range(total_frames):
    # Frame base (preto com gradiente)
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # Gradiente de fundo (simula céu/chão)
    for y in range(height):
        color = int(50 + (y / height) * 100)
        frame[y, :] = (color // 3, color // 2, color)

    # Título (simula HUD do GTA)
    cv2.putText(frame, "GTA V - Battle Royale Test",
                (width // 2 - 300, 50),
                cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)

    # Timestamp
    timestamp = f"Frame: {i}/{total_frames}"
    cv2.putText(frame, timestamp, (20, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    # Kill feed (canto superior direito - onde fica no GTA)
    kill_feed_x = width - 500
    kill_feed_y = 100

    # Mostrar kills recentes (últimos 5 segundos = 150 frames)
    active_kills = []
    for kill_frame, kill_text in kill_texts.items():
        if kill_frame <= i < kill_frame + 150:  # 5 segundos
            age = i - kill_frame
            alpha = max(0, 1 - (age / 150))  # Fade out
            active_kills.append((kill_text, alpha))

    # Renderizar kill feed
    for idx, (kill_text, alpha) in enumerate(active_kills[-5:]):  # Max 5 kills
        y_pos = kill_feed_y + (idx * 40)

        # Background semi-transparente
        overlay = frame.copy()
        cv2.rectangle(overlay,
                     (kill_feed_x - 10, y_pos - 25),
                     (kill_feed_x + 490, y_pos + 10),
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Texto do kill
        color = tuple([int(c * alpha) for c in (255, 50, 50)])  # Vermelho fade
        cv2.putText(frame, kill_text, (kill_feed_x, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Se é frame de novo kill, adicionar efeito
    if i in kill_texts:
        # Flash vermelho nas bordas
        cv2.rectangle(frame, (0, 0), (width, height), (0, 0, 255), 20)

    # Contador de kills total
    total_kills = sum(1 for f in kill_texts.keys() if f <= i)
    cv2.putText(frame, f"Total Kills: {total_kills}",
                (20, 100),
                cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 0), 2)

    # Escrever frame
    out.write(frame)

    # Progress
    if i % 30 == 0:
        progress = (i / total_frames) * 100
        print(f"  Progresso: {progress:.1f}% ({i}/{total_frames} frames)")

# Finalizar
out.release()

print("\n[OK] Vídeo criado: test_gta_synthetic.mp4")
print(f"   Duração: {duration}s")
print(f"   Resolução: {width}x{height}")
print(f"   FPS: {fps}")
print(f"   Kills simulados: {len(kills)}")
print("\nUse este vídeo para testar:")
print(f"  python capture_video.py --video test_gta_synthetic.mp4 --server https://gta-analytics-v2.fly.dev --fps 0.5")
