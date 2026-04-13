# GTA Analytics V2

**Análise de torneios em tempo real com visão por IA para GTA V**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

---

## O que faz

Sistema que captura gameplay em tempo real, extrai kill feed via **GPT-4o Vision** e entrega estatísticas instantâneas para torneios de GTA V.

**Pipeline:**
1. Captura de tela do jogo
2. Transporte via WebRTC (binary JPEG, sem overhead de base64)
3. Análise de visão com GPT-4o
4. Parsing de kills e tracking de times
5. Dashboard em tempo real via WebSocket
6. Exportação para Excel

## Arquitetura

```
Client (Python)  →  Gateway (Go/Fly.io)  →  Backend (Python/FastAPI/Fly.io)
  Captura de tela     WebRTC + Buffer         GPT-4o Vision + Dashboard
```

- **Client:** Captura de tela e envio via WebRTC
- **Gateway:** Servidor Go no Fly.io, gerencia conexões WebRTC e buffer de frames
- **Backend:** FastAPI no Fly.io, processa frames com GPT-4o Vision, serve dashboard

## Stack

- **Backend:** Python, FastAPI
- **Gateway:** Go, WebRTC (pion/webrtc)
- **Desktop:** Electron
- **IA:** GPT-4o Vision (OpenAI)
- **Deploy:** Fly.io (São Paulo), Docker
- **Integração:** OBS Studio plugin

## Estrutura

```
backend/       → API FastAPI + processamento de visão
gateway/       → Servidor WebRTC em Go
electron-app/  → App desktop para captura
obs-plugin/    → Plugin para OBS Studio
tests/         → Testes automatizados
docs/          → Documentação
```

## Status

Em produção — construído sob demanda para organizador de torneios que fazia tracking manual em planilha.

## Licença

[GNU AGPL v3.0](LICENSE) — Código aberto para transparência e auditabilidade em torneios.
