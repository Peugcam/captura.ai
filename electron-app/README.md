# 🎮 GTA Analytics - Electron Desktop App

**Aplicação desktop profissional para captura e análise de Battle Royale do GTA V em tempo real.**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📋 Sobre

Sistema completo de analytics em tempo real para campeonatos e torneios de GTA V Battle Royale, desenvolvido para **Luis Otavio** via **Vitor**.

**Features principais:**
- ✅ Captura automática de frames do GTA V
- ✅ Detecção de kills com Vision AI
- ✅ Rastreamento de times em tempo real
- ✅ Dashboard estrategista ao vivo
- ✅ Export Excel personalizado
- ✅ Interface gráfica moderna
- ✅ Tray icon (roda em background)

---

## 🚀 Quick Start (Cliente Final)

### Para usar (sem instalar Python):

1. **Baixar instalador:**
   - `GTA-Analytics-1.0.0-Setup.exe` (~100 MB)

2. **Instalar:**
   - Duplo clique no instalador
   - Next → Next → Finish

3. **Usar:**
   - Abrir "GTA Analytics" do menu Iniciar
   - Clicar em "Iniciar Captura"
   - Pronto! ✅

---

## 💻 Setup Desenvolvimento

### Pré-requisitos

- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Git** (opcional)

> Sem Python necessário. A captura é feita em JavaScript nativo via `desktopCapturer` do Electron.

### Instalação

```bash
# 1. Clone/baixe o projeto
cd gta-analytics-v2/electron-app

# 2. Instalar dependências
npm install

# 3. Rodar em modo dev
npm start
```

---

## 🔨 Build para Distribuição

### Build completo (Windows .exe + instalador):

```bash
# Build Electron (sem Python)
npm run build

# Resultado em:
# dist/GTA-Analytics-1.0.0-Setup.exe    (Instalador NSIS)
# dist/GTA-Analytics-1.0.0-Portable.exe (Versão portável)
```

### Build apenas diretório (mais rápido, para testes):

```bash
npm run build:dir

# Resultado em: dist/win-unpacked/
```

---

## 📁 Estrutura do Projeto

```
electron-app/
├── main.js                    # Electron main process + IPC handlers
├── capture.js                 # Lógica de captura (JavaScript nativo)
├── preload.js                 # IPC bridge seguro
├── package.json               # Config npm
│
├── renderer/                  # Frontend (interface)
│   ├── index.html            # Main page
│   ├── css/
│   │   └── styles.css        # Estilos
│   └── js/
│       └── app.js            # JavaScript frontend
│
├── assets/                    # Ícones e recursos
│   ├── icon.ico              # App icon
│   └── tray-icon.png         # Tray icon
│
└── dist/                      # Build output (gerado)
    └── GTA-Analytics-*.exe   # Instaladores finais
```

---

## ⚙️ Configuração

### Servidor Backend

Editar no app ou direto no código:

```javascript
// main.js
const CONFIG = {
    serverUrl: 'https://gta-analytics-v2.fly.dev',  // Seu servidor
    fps: 0.5,                                        // Taxa captura
    autoStart: false                                 // Auto-iniciar
};
```

### Personalização

```json
// package.json - Metadados
{
  "name": "gta-analytics",
  "version": "1.0.0",
  "description": "GTA V Battle Royale Analytics",
  "author": "Paulo Eugenio Campos"
}
```

---

## 🎯 Como Funciona

### Arquitetura

```
┌─────────────────────────────────┐
│  GTA-Analytics.exe              │
│  ├─ Electron (Interface)        │
│  ├─ capture.js (desktopCapturer)│
│  └─ IPC Bridge (preload.js)     │
└─────────────────────────────────┘
         │
         │ HTTPS (multipart/form-data JPEG)
         ▼
┌─────────────────────────────────┐
│  Fly.io Backend                 │
│  ├─ GPT-4o Vision processing    │
│  ├─ Team tracking               │
│  └─ WebSocket broadcast         │
└─────────────────────────────────┘
```

### Fluxo de Captura

1. **Usuário** clica "Iniciar Captura"
2. **GTACapture** verifica se `GTA5.exe` está rodando (via PowerShell)
3. **desktopCapturer** captura frame da tela principal (1280×720)
4. **Frame diff** filtra cenas estáticas (skip se mudança < 3%)
5. **JPEG** é enviado via HTTPS POST para o backend no Fly.io
6. **Backend** processa com GPT-4o Vision e transmite kills ao vivo
7. **Dashboard** mostra o kill feed em tempo real

---

## 🔧 Troubleshooting

### App não abre

```bash
# Verificar logs
%APPDATA%\gta-analytics\logs\
```

### Antivírus bloqueia

**Opção 1:** Adicionar exceção no antivírus

**Opção 2:** Code signing (requer certificado)
```bash
# Com certificado DigiCert
signtool sign /f certificate.pfx /p password GTA-Analytics.exe
```

### GTA não captura (tela preta)

**Soluções:**
1. Rodar GTA em **Windowed Borderless** (não fullscreen)
2. Atualizar drivers GPU
3. Desabilitar overlay Discord/Steam temporariamente
4. Verificar se Windows 10 versão 1803+

---

## 📊 Performance

### Requisitos Sistema

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **OS** | Windows 10 1803+ | Windows 11 |
| **RAM** | 4 GB | 8 GB |
| **GPU** | DirectX 11.1+ | DirectX 12 |
| **Internet** | 5 Mbps | 10 Mbps |

### Uso de Recursos

| Aspecto | Valor |
|---------|-------|
| **RAM (app)** | ~200-250 MB |
| **CPU (idle)** | <1% |
| **CPU (capturing)** | 5-10% |
| **Network** | ~50 KB/frame |

### Custos Operacionais

| Métrica | Valor |
|---------|-------|
| **Por frame** | $0.00015 |
| **Por hora (0.5 FPS)** | ~$0.13 |
| **Evento 3h** | ~$0.40 |

---

## 🎨 Customização

### Mudar cores/tema

Editar `renderer/css/styles.css`:

```css
:root {
    --color-primary: #e94560;      /* Cor principal */
    --bg-primary: #1a1a2e;         /* Background */
    /* ... */
}
```

### Adicionar features

1. **Frontend:** Editar `renderer/index.html` e `renderer/js/app.js`
2. **Backend:** Adicionar handlers em `main.js`
3. **IPC:** Expor API em `preload.js`

---

## 📦 Distribuição

### GitHub Releases (Recomendado)

```bash
# 1. Build
npm run build

# 2. Criar release GitHub
gh release create v1.0.0 \
  dist/GTA-Analytics-1.0.0-Setup.exe \
  --title "GTA Analytics v1.0.0" \
  --notes "Initial release"

# URL download:
# https://github.com/user/repo/releases/download/v1.0.0/GTA-Analytics-1.0.0-Setup.exe
```

### Auto-Update (Futuro)

```javascript
// main.js - Já configurado
const { autoUpdater } = require('electron-updater');
autoUpdater.checkForUpdatesAndNotify();
```

---

## 🐛 Debug

### Mode Desenvolvimento

```bash
# Rodar com DevTools aberto
npm run dev

# Ou
npm start -- --dev
```

### Logs

```javascript
// Frontend (Console do browser)
console.log(window.gtaAnalytics.getStatus());

// Backend (Terminal)
// Logs aparecem automaticamente
```

---

## 📝 TODO / Roadmap

- [ ] Auto-update via GitHub Releases
- [ ] Code signing (DigiCert)
- [ ] MacOS build (via Tauri)
- [ ] Linux build (via Tauri)
- [ ] Settings persistentes (LocalStorage)
- [ ] Multiple capture profiles
- [ ] Hotkeys globais (F9 start/stop)
- [ ] Notifications nativas

---

## 🤝 Contribuindo

Este é um projeto comercial privado para **Luis Otavio**.

Para suporte ou modificações, contatar:
- **Developer:** Paulo Eugenio Campos
- **Cliente:** Luis Otavio (via Vitor)

---

## 📄 Licença

MIT License - Copyright © 2026 Paulo Eugenio Campos

---

## 🙏 Créditos

**Tecnologias:**
- Electron - Framework desktop
- desktopCapturer - Screen capture nativo (sem Python)
- axios - HTTP client
- form-data - Multipart frame upload

**Backend:**
- FastAPI - Server framework
- GPT-4o Vision - Processamento de frames
- Fly.io - Cloud hosting

**Desenvolvido para:**
- **Cliente:** Luis Otavio
- **Contato:** Vitor
- **Uso:** Torneios GTA V Battle Royale

---

**v1.0.0** | Desenvolvido com ❤️ por Paulo Eugenio Campos
