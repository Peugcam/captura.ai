# 🎬 TESTE COM VÍDEO LOCAL

**Por quê testar com vídeo?**
- ✅ NÃO precisa ter GTA V instalado
- ✅ Testa todo o pipeline (upload → backend → AI → dashboard)
- ✅ Pode usar qualquer vídeo de gameplay do YouTube
- ✅ Controla exatamente o conteúdo testado

---

## 📋 REQUISITOS

1. **Python 3.10+** instalado
2. **OpenCV** instalado: `pip install opencv-python`
3. **Vídeo de gameplay GTA V** (qualquer formato: MP4, AVI, MKV)

---

## 🎥 ONDE CONSEGUIR VÍDEOS DE TESTE

### Opção 1: YouTube (Recomendado)

**Baixar vídeo de Battle Royale GTA V**:

1. Ir para YouTube e buscar: "GTA V Battle Royale gameplay"

2. Copiar URL do vídeo (exemplo): `https://www.youtube.com/watch?v=XXXXX`

3. Usar yt-dlp para baixar:
```bash
# Instalar yt-dlp
pip install yt-dlp

# Baixar vídeo (720p, MP4)
yt-dlp -f "best[height<=720]" -o "gta_test.mp4" "URL_DO_VIDEO"
```

**Exemplo vídeos bons**:
- GTA V Battle Royale com kill feed visível
- Gameplay com múltiplos kills
- Vídeos de 2-5 minutos

### Opção 2: Gravar Próprio Gameplay

Se você tem GTA V:
```bash
# Usar OBS Studio ou Windows Game Bar
# Gravar 2-3 minutos de gameplay
# Salvar como MP4
```

### Opção 3: Vídeo de Teste Simples

Criar vídeo sintético (apenas para testar pipeline):
```python
# Criar vídeo de teste (opcional)
import cv2
import numpy as np

# Criar vídeo 1280x720, 30fps, 10 segundos
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('test.mp4', fourcc, 30.0, (1280, 720))

for i in range(300):  # 10 segundos
    frame = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
    # Adicionar texto
    cv2.putText(frame, f"Frame {i}", (100, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    out.write(frame)

out.release()
print("test.mp4 created")
```

---

## 🚀 COMO TESTAR

### Passo 1: Preparar Vídeo

```bash
# Verificar que vídeo existe
ls gta_test.mp4

# Informações do vídeo
ffprobe gta_test.mp4  # Se tiver ffmpeg
```

### Passo 2: Rodar Script de Teste

```bash
cd python

# Testar com servidor Fly.io
python capture_video.py \
  --video C:\path\to\gta_test.mp4 \
  --server https://gta-analytics-v2.fly.dev \
  --fps 0.5
```

**Parâmetros**:
- `--video`: Caminho completo para arquivo de vídeo
- `--server`: URL do backend Fly.io
- `--fps`: Quantos frames por segundo enviar (0.5 = 1 frame a cada 2 segundos)

### Passo 3: Observar Output

```
================================================================
GTA ANALYTICS - VIDEO TEST MODE
================================================================
📹 Video: gta_test.mp4
📊 Frames: 1800
🎬 FPS: 30.00
⏱️  Duration: 60.0s
📡 Server: https://gta-analytics-v2.fly.dev/api/frames/upload
⚙️  Capture rate: 0.5 FPS (interval: 2.0s)
================================================================
▶️  Starting video playback...
================================================================
✅ Frame 1/1800 sent (342 KB)
   🎯 Kills detected: 2
✅ Frame 2/1800 sent (338 KB)
✅ Frame 3/1800 sent (345 KB)
   🎯 Kills detected: 1
...
```

### Passo 4: Verificar Dashboard

Abrir no navegador:
```
https://gta-analytics-v2.fly.dev/strategist
```

**Deve ver**:
- ✅ Kills aparecendo em tempo real
- ✅ Scoreboard atualizando
- ✅ Gráficos de performance

---

## 🎯 CASOS DE TESTE

### Teste 1: Upload Básico
**Objetivo**: Verificar que frames chegam ao backend

```bash
python capture_video.py \
  --video test.mp4 \
  --server https://gta-analytics-v2.fly.dev \
  --fps 0.2
```

**Esperado**:
- ✅ Sem erros de conexão
- ✅ Status code 200
- ✅ Frames enviados com sucesso

### Teste 2: Detecção de Kills
**Objetivo**: Verificar que Vision AI detecta kills

**Requisitos**:
- Vídeo com kill feed visível
- Múltiplos kills durante vídeo

**Verificar**:
- ✅ Console mostra "🎯 Kills detected: N"
- ✅ Dashboard atualiza em tempo real
- ✅ Nomes dos jogadores corretos

### Teste 3: Performance
**Objetivo**: Verificar latência e throughput

```bash
# FPS maior para stress test
python capture_video.py \
  --video test.mp4 \
  --server https://gta-analytics-v2.fly.dev \
  --fps 1.0
```

**Métricas**:
- ✅ Tempo de resposta < 5 segundos
- ✅ Success rate > 95%
- ✅ Sem timeouts frequentes

### Teste 4: Loop de Vídeo
**Objetivo**: Testar estabilidade longa duração

```bash
# Rodar vídeo
python capture_video.py \
  --video short_test.mp4 \
  --server https://gta-analytics-v2.fly.dev \
  --fps 0.5

# Quando terminar, escolher "y" para loop
# Loop video? (y/n): y
```

**Verificar**:
- ✅ Deduplicação funciona (não duplica kills)
- ✅ Memória estável (não cresce infinitamente)
- ✅ Conexão mantém estável

---

## 📊 EXEMPLO COMPLETO

```bash
# 1. Baixar vídeo de teste do YouTube
yt-dlp -f "best[height<=720]" -o "gta_br_test.mp4" \
  "https://www.youtube.com/watch?v=EXAMPLE"

# 2. Verificar vídeo
ls -lh gta_br_test.mp4

# 3. Rodar teste
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\electron-app\python

python capture_video.py \
  --video C:\Users\paulo\Downloads\gta_br_test.mp4 \
  --server https://gta-analytics-v2.fly.dev \
  --fps 0.5

# 4. Abrir dashboard em paralelo
start https://gta-analytics-v2.fly.dev/strategist

# 5. Observar resultados
```

---

## 🐛 TROUBLESHOOTING

### Erro: "Video not found"
```
❌ Video not found: test.mp4
```

**Solução**: Usar caminho absoluto
```bash
python capture_video.py \
  --video "C:\Users\paulo\Downloads\test.mp4" \
  --server https://gta-analytics-v2.fly.dev \
  --fps 0.5
```

### Erro: "Cannot open video"
```
❌ Cannot open video: test.mp4
```

**Causas**:
- Formato não suportado
- Arquivo corrompido
- Codec faltando

**Solução**: Converter para MP4 padrão
```bash
ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4
```

### Erro: "OpenCV not installed"
```
❌ OpenCV not installed!
```

**Solução**:
```bash
pip install opencv-python
```

### Timeout frequente
```
⚠️ Timeout sending frame
```

**Causas**:
- Conexão lenta
- Backend sobrecarregado
- Frames muito grandes

**Soluções**:
1. Reduzir FPS: `--fps 0.2`
2. Usar vídeo menor (720p ao invés de 1080p)
3. Verificar internet

---

## ✅ CHECKLIST DE TESTE

Antes de enviar para cliente, verificar:

- [ ] ✅ Upload de frames funciona
- [ ] ✅ Backend processa sem erros
- [ ] ✅ Vision AI detecta kills
- [ ] ✅ Dashboard atualiza tempo real
- [ ] ✅ Deduplicação evita duplicatas
- [ ] ✅ Team tracking funciona
- [ ] ✅ WebSocket mantém conexão
- [ ] ✅ Success rate > 95%
- [ ] ✅ Sem memory leaks (teste longo)

---

## 🎉 VANTAGENS DO TESTE COM VÍDEO

1. **Reproduzível**: Mesmo vídeo = mesmo resultado
2. **Controlado**: Sabe exatamente quantos kills esperar
3. **Rápido**: Não precisa jogar 1 hora
4. **Completo**: Testa todo pipeline end-to-end
5. **Debug**: Pode pausar e analisar frames específicos

---

## 📝 PRÓXIMOS PASSOS

Após teste com vídeo bem-sucedido:

1. ✅ Confirmar que backend funciona
2. ✅ Confirmar que Vision AI detecta kills
3. ✅ Confirmar que dashboard atualiza
4. 🚀 **Então testar com GTA V real**
5. 📦 **Distribuir para cliente Luis**

---

**Boa sorte nos testes!** 🎬🚀
