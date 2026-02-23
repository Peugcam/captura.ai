# GTA Analytics V2 - Cloud-Native Edition 🚀

Real-time kill feed analytics for GTA V and Naruto Online with **WebRTC**, **Unix Domain Sockets**, **LiteLLM multi-model support**, and **100% cloud deployment** on Fly.io.

---

## 🌟 Key Features

### **Ultra-Low Latency Architecture**
- **WebRTC DataChannel**: Binary frame transport via UDP (eliminates 33% base64 overhead)  
- **Unix Domain Sockets**: Zero-network latency for Gateway↔Backend IPC  
- **Optimized Frame Pipeline**: OCR pre-filter → Vision API → Kill parsing in <500ms

### **AI-Powered Cost Optimization**
- **LiteLLM Multi-Model Routing**: Intelligent fallback chain reduces costs by 80%
  - **Llama-3.2-Vision** (Together AI): $0.30/1M tokens - Primary  
  - **Qwen2-VL** (SiliconFlow): $0.40/1M tokens - Fallback #1  
  - **GPT-4o** (OpenRouter): $2.00/1M tokens - Fallback #2  
  - **GPT-4o** (OpenAI Direct): $2.50/1M tokens - Last Resort  
- **Automatic Failover**: Seamless switching on errors or rate limits

### **Production-Ready Cloud Deployment**
- **100% Cloud-Native**: Runs entirely on Fly.io (São Paulo region)  
- **Docker Multi-Stage Builds**: Optimized images (<500MB total)  
- **Auto-Scaling**: Handles variable load automatically  
- **Zero-Downtime Deploys**: Blue-green deployment strategy

---

## 📊 Architecture Overview

\`\`\`
┌─────────────────────────────────────────────────────────────────────┐
│  CLIENT (Python)                                                    │
│  - Screen capture (PIL.ImageGrab)                                   │
│  - WebRTC signaling (aiortc)                                        │
│  - Binary JPEG transport (no base64)                                │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     │ WebRTC DataChannel (UDP)
                     │ Raw JPEG bytes (~100ms latency)
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│  GATEWAY (Go) - Fly.io                                              │
│  - WebRTC signaling server (pion/webrtc)                            │
│  - WebSocket support (backward compatibility)                       │
│  - Ring buffer (200 frames, drop-oldest)                            │
│  - Unix Domain Socket server (Linux)                                │
│  - Named Pipe server (Windows)                                      │
│  - HTTP REST API (fallback)                                         │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     │ Unix Domain Socket (IPC)
                     │ /tmp/gta-gateway.sock (~30% faster than HTTP)
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│  BACKEND (Python) - Fly.io                                          │
│  - FastAPI server                                                   │
│  - IPC client (auto-detects Unix/HTTP)                              │
│  - OCR pre-filter (Tesseract, 4 workers)                            │
│  - LiteLLM Vision client (multi-model fallback)                     │
│  - Team tracker + Kill parser                                       │
│  - Excel exporter                                                   │
│  - WebSocket server (dashboard events)                              │
└─────────────────────────────────────────────────────────────────────┘
\`\`\`

---

## 🚀 Quick Start

### **Prerequisites**
- **Docker** (for local development)
- **Python 3.11+** (for client capture)
- **Fly CLI** (for cloud deployment): https://fly.io/docs/hands-on/install-flyctl/

### **1. Local Development**

\`\`\`bash
# Clone and configure
cd gta-analytics-v2
cd backend && cp .env.example .env
# Edit .env and add API keys

# Start services
docker-compose up -d

# Test health
curl http://localhost:8000/health  # Gateway
curl http://localhost:3000/health  # Backend
\`\`\`

### **2. Capture Frames**

#### **⚠️ OBS sendo bloqueado pelo GTA?**

Temos **3 métodos alternativos** que funcionam:

\`\`\`bash
# PASSO 1: Instalar bibliotecas alternativas
pip install mss d3dshot pywin32

# PASSO 2: Testar qual método funciona melhor
python testar-capturas.py

# PASSO 3: Usar o método recomendado
python captura-nvidia.py    # MSS - Funciona em 90% dos casos
python captura-wgc.py       # D3DShot - Melhor performance
python captura-gamebar.py   # Windows GDI - Backup
\`\`\`

📖 **Guia completo:** [INICIO_RAPIDO.txt](INICIO_RAPIDO.txt)
📊 **Comparação de métodos:** [ALTERNATIVAS_CAPTURA.md](ALTERNATIVAS_CAPTURA.md)

#### **WebRTC (Método Original)**

\`\`\`bash
# Install dependencies
pip install -r backend/requirements.txt aiortc aiohttp Pillow

# Test WebRTC connection
python test_webrtc_connection.py

# Start capture (4 FPS)
python captura-webrtc.py --fps 4 --quality 85
\`\`\`

---

## ☁️ Cloud Deployment

\`\`\`bash
# Login and deploy
fly auth login
make fly-create-gateway
make fly-create-backend
make fly-secrets
make fly-deploy

# Connect to cloud
python captura-webrtc.py --gateway https://gta-analytics-gateway.fly.dev --fps 4
\`\`\`

---

## 📈 Performance Benchmarks

| Metric | V1 | V2 | Improvement |
|--------|----|----|-------------|
| Frame Transport | ~200ms | ~100ms | 2x faster |
| Gateway↔Backend | ~50ms | ~15ms | 3x faster |
| Total Latency | ~500ms | ~300ms | 40% reduction |
| Payload Size | 1.33MB | 1MB | 33% smaller |
| Vision API Cost | $2.50/1M | $0.30/1M | 80% cheaper |

---

## 🛠️ Makefile Commands

\`\`\`bash
make help                 # Show all commands
make up                  # Start local services
make test                # Test all services
make fly-deploy          # Deploy to Fly.io
\`\`\`

---

## 📞 Support

For issues or questions, open an issue on GitHub.

**Built with ❤️ for the GTA Analytics community**
