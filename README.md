# GTA Analytics V2 - Hybrid Architecture

Sistema de análise de gameplay GTA V com arquitetura híbrida otimizada.

## 🎯 Objetivo

Resolver os 7 problemas críticos do sistema anterior:
1. ✅ Frame loss 93% → 5% (WebSocket Gateway em Go)
2. ✅ Latência OCR 300ms → 30ms (Worker pool)
3. ✅ Latência API 2-8s → 1-4s (Connection pooling)
4. ✅ Uso de memória -50% (Buffer lock-free)
5. ✅ GIL Python (Componentes críticos em Go)
6. ✅ Encoding base64 overhead (Binary WebSocket)
7. ✅ Single worker (Arquitetura distribuída)

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (JS)                        │
│              test_capture.html                          │
└────────────────────┬────────────────────────────────────┘
                     │ WebSocket Binary
                     ▼
┌─────────────────────────────────────────────────────────┐
│          WEBSOCKET GATEWAY (Go) - NOVO                  │
│  - Goroutine per connection (1000+ concurrent)          │
│  - Lock-free ring buffer                                │
│  - Zero-copy frame handling                             │
│  - Binary WebSocket (no base64)                         │
│  - Backpressure management                              │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/gRPC
                     ▼
┌─────────────────────────────────────────────────────────┐
│             PYTHON BACKEND (FastAPI)                    │
│  - GPT-4o Vision API calls                              │
│  - Business logic (team_tracker, parser)                │
│  - Excel/PDF export                                     │
│  - Dashboard REST API                                   │
└─────────────────────────────────────────────────────────┘
```

## 📁 Estrutura do Projeto

```
gta-analytics-v2/
├── gateway/          # WebSocket Gateway (Go)
│   ├── main.go
│   ├── websocket.go
│   ├── buffer.go
│   └── go.mod
├── backend/          # Python Backend (FastAPI)
│   ├── main.py
│   ├── processor.py
│   └── requirements.txt
├── shared/           # Schemas compartilhados
│   └── protocol.proto
└── docs/             # Documentação
```

## 🚀 Performance Esperada

| Métrica | V1 (Python) | V2 (Hybrid) | Melhoria |
|---------|-------------|-------------|----------|
| Frame delivery | 7% | 95%+ | 13x |
| OCR latency | 300ms | 30ms | 10x |
| API latency | 2-8s | 1-4s | 2x |
| Memory usage | 500MB-1GB | 200-400MB | 2-3x |
| Max throughput | 1 FPS | 10+ FPS | 10x |

## 📝 Status

- [x] Estrutura do projeto criada
- [ ] WebSocket Gateway em Go
- [ ] Buffer lock-free
- [ ] Integração com Python backend
- [ ] Testes de carga
- [ ] Deploy

## 🔗 Repositório Anterior

Versão Python: https://github.com/Peugcam/screen-data-analyzer
