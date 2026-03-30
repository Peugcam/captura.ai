# GTA Analytics — Melhorias do App Electron — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aplicar 4 melhorias sequenciais ao app Electron: corrigir bugs, auditar segurança, adicionar testes e polir a UI.

**Architecture:** Cada tarefa é independente e valida a anterior. Debugging elimina bugs antes da auditoria de segurança; segurança corrige vulnerabilidades antes de testá-las; testes bloqueiam regressões antes de mexer na UI.

**Tech Stack:** Electron 33, Node.js, Jest (testes), HTML/CSS/JS (renderer)

---

## Arquivos Envolvidos

| Arquivo | Ação |
|---------|------|
| `electron-app/capture.js` | Modificar — fixes de debug e segurança |
| `electron-app/main.js` | Modificar — fix de segurança (openExternal) |
| `electron-app/preload.js` | Modificar — fix de segurança (openExternal) |
| `electron-app/renderer/js/app.js` | Modificar — segurança + UI |
| `electron-app/renderer/index.html` | Modificar — UI |
| `electron-app/renderer/css/styles.css` | Modificar — UI (animações) |
| `electron-app/tests/capture.test.js` | Criar — testes Jest |
| `electron-app/package.json` | Modificar — adicionar jest |

---

## Tarefa 1: Fix Race Condition no captureAndSend

**Problema:** `captureAndSend` é async e chamada por `setInterval`. Se uma execução demorar mais que o intervalo (retry = até 16s), a próxima inicia antes da anterior terminar — múltiplas chamadas acumulam.

**Arquivo:** `electron-app/capture.js`

- [ ] **Passo 1: Adicionar flag `this.capturing` para mutex simples**

Em `capture.js`, no constructor, adicionar `this.capturing = false;` após `this.consecutiveErrors = 0;`:

```javascript
constructor(serverUrl, fps, sendToRenderer) {
    // ... existente ...
    this.wasGtaPaused = false;
    this.serverWaking = false;
    this.consecutiveErrors = 0;
    this.capturing = false;  // NOVO: mutex para evitar race condition
}
```

- [ ] **Passo 2: Usar o mutex no início e fim de captureAndSend**

Substituir o início de `captureAndSend`:

```javascript
async captureAndSend() {
    if (!this.running) return;
    if (this.capturing) return; // já tem uma execução em andamento
    this.capturing = true;

    try {
        // ... resto do método existente ...
    } catch (err) {
        this.errors++;
        this.consecutiveErrors++;
        this.sendToRenderer('log', `❌ Erro: ${err.message}`);
        this.sendToRenderer('server-status', { status: 'offline' });
        if (this.consecutiveErrors === 3) {
            this.sendToRenderer('log', '🔁 Tentando reconectar automaticamente...');
        }
        this.sendToRenderer('status-update', {
            running: true,
            framesSent: this.framesSent,
            errors: this.errors,
            startTime: this.startTime,
            lastFrameTime: null
        });
    } finally {
        this.capturing = false; // SEMPRE libera o mutex
    }
}
```

- [ ] **Passo 3: Adicionar `this.capturing = false` no start()**

No método `start()`, junto com os outros resets:

```javascript
start() {
    this.running = true;
    this.startTime = Date.now();
    this.framesSent = 0;
    this.errors = 0;
    this.prevFrameBuffer = null;
    this.wasGtaPaused = false;
    this.serverWaking = false;
    this.consecutiveErrors = 0;
    this.capturing = false; // NOVO
    // ... resto igual ...
}
```

- [ ] **Passo 4: Commit**

```bash
git add electron-app/capture.js
git commit -m "fix: mutex em captureAndSend previne race condition com setInterval"
```

---

## Tarefa 2: Fix Stop Durante Retry

**Problema:** se `stop()` for chamado enquanto `sendWithRetry` está no `await new Promise(r => setTimeout(r, delay))`, a captura continua enviando até o retry terminar.

**Arquivo:** `electron-app/capture.js`

- [ ] **Passo 1: Checar `this.running` dentro do loop de retry**

No método `sendWithRetry`, substituir o bloco de espera:

```javascript
async sendWithRetry(jpegBuffer, maxRetries = 4) {
    const form = new FormData();
    form.append('file', jpegBuffer, {
        filename: 'frame.jpg',
        contentType: 'image/jpeg'
    });

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        if (!this.running) return null; // NOVO: aborta se stop() foi chamado

        try {
            const response = await axios.post(this.serverUrl, form, {
                headers: form.getHeaders(),
                timeout: 15000
            });

            if (this.serverWaking) {
                this.serverWaking = false;
                this.sendToRenderer('log', '✅ Servidor acordou! Captura retomada.');
                this.sendToRenderer('server-status', { status: 'online' });
            }
            this.consecutiveErrors = 0;
            return response;

        } catch (err) {
            const isConnectionErr = err.code === 'ECONNREFUSED' || err.code === 'ECONNRESET'
                || err.code === 'ETIMEDOUT' || (err.response && err.response.status >= 500);

            if (isConnectionErr && attempt < maxRetries) {
                if (!this.serverWaking) {
                    this.serverWaking = true;
                    this.sendToRenderer('log', '🔄 Servidor acordando, aguardando...');
                    this.sendToRenderer('server-status', { status: 'waking' });
                }
                const delay = 3000 + (attempt - 1) * 2000;
                await new Promise(r => setTimeout(r, delay));
            } else {
                throw err;
            }
        }
    }
}
```

- [ ] **Passo 2: Tratar retorno `null` de sendWithRetry em captureAndSend**

Após a chamada `const response = await this.sendWithRetry(jpegBuffer);`, adicionar:

```javascript
const response = await this.sendWithRetry(jpegBuffer);
if (!response) return; // NOVO: stop() foi chamado durante retry
```

- [ ] **Passo 3: Commit**

```bash
git add electron-app/capture.js
git commit -m "fix: abortar sendWithRetry imediatamente quando stop() é chamado"
```

---

## Tarefa 3: Segurança — Validar URL e openExternal

**Arquivos:** `electron-app/main.js`, `electron-app/preload.js`, `electron-app/renderer/js/app.js`

- [ ] **Passo 1: Restringir openExternal a https:// no main.js**

No handler IPC `open-external` em `main.js`, substituir:

```javascript
ipcMain.handle('open-external', async (event, url) => {
    // Só permite https:// para evitar file:// ou javascript:
    if (!url || !url.startsWith('https://')) {
        return { success: false, error: 'Apenas URLs https:// são permitidas' };
    }
    await shell.openExternal(url);
    return { success: true };
});
```

- [ ] **Passo 2: Validar URL do servidor antes de passar ao axios**

Em `capture.js`, no constructor, adicionar validação:

```javascript
constructor(serverUrl, fps, sendToRenderer) {
    if (!serverUrl.startsWith('https://')) {
        throw new Error('serverUrl deve começar com https://');
    }
    this.serverUrl = `${serverUrl}/api/frames/upload`;
    // ... resto igual ...
}
```

- [ ] **Passo 3: Confirmar escapeHtml em todos os pontos de log**

Em `renderer/js/app.js`, a função `addLog` já usa `escapeHtml`. Verificar que nenhum outro ponto insere HTML diretamente. Substituir qualquer `innerHTML` que receba dados externos por `textContent`:

```javascript
// ANTES (inseguro se message vier de fonte externa):
entry.innerHTML = `<span class="log-timestamp">[${timestamp}]</span>
    <span class="log-message">${escapeHtml(message)}</span>`;

// Já está correto — escapeHtml está aplicado. Manter assim.
```

Verificar também `updateUICapturing` e `updateUIStopped` — usam apenas strings literais, sem dados externos. OK.

- [ ] **Passo 4: Commit**

```bash
git add electron-app/main.js electron-app/capture.js
git commit -m "security: validar URLs https:// em openExternal e serverUrl"
```

---

## Tarefa 4: Configurar Jest e Criar Testes de capture.js

**Arquivos:** `electron-app/package.json`, `electron-app/tests/capture.test.js` (novo)

- [ ] **Passo 1: Adicionar jest ao package.json**

Em `electron-app/package.json`, adicionar em `devDependencies` e um script `test`:

```json
{
  "scripts": {
    "start": "electron .",
    "dev": "electron . --dev",
    "build": "electron-builder --win --x64",
    "build:dir": "electron-builder --win --x64 --dir",
    "pack": "electron-builder --dir",
    "dist": "electron-builder",
    "test": "jest --testPathPattern=tests/"
  },
  "devDependencies": {
    "electron": "^33.0.0",
    "electron-builder": "^25.0.0",
    "jest": "^29.0.0"
  }
}
```

- [ ] **Passo 2: Instalar jest**

```bash
cd electron-app
npm install --save-dev jest
```

Esperado: `jest@29.x.x` adicionado a `node_modules`.

- [ ] **Passo 3: Criar o arquivo de testes**

Criar `electron-app/tests/capture.test.js`:

```javascript
// Mock do módulo electron antes de qualquer require
jest.mock('electron', () => ({
    desktopCapturer: {
        getSources: jest.fn()
    }
}));

jest.mock('axios');
jest.mock('form-data');

const axios = require('axios');
const GTACapture = require('../capture');

// Helper para criar instância com sendToRenderer mockado
function makeCapture(overrides = {}) {
    const sendToRenderer = jest.fn();
    const capture = new GTACapture(
        overrides.serverUrl || 'https://test-server.fly.dev',
        overrides.fps || 1.0,
        sendToRenderer
    );
    return { capture, sendToRenderer };
}

// ============================================================
// getFrameDiff
// ============================================================

describe('getFrameDiff', () => {
    test('retorna 100 quando buf1 é null', () => {
        const { capture } = makeCapture();
        const buf2 = Buffer.alloc(100, 128);
        expect(capture.getFrameDiff(null, buf2)).toBe(100);
    });

    test('retorna 100 quando tamanhos são diferentes', () => {
        const { capture } = makeCapture();
        const buf1 = Buffer.alloc(100, 0);
        const buf2 = Buffer.alloc(200, 0);
        expect(capture.getFrameDiff(buf1, buf2)).toBe(100);
    });

    test('retorna 0 quando buffers são idênticos', () => {
        const { capture } = makeCapture();
        const buf = Buffer.alloc(400, 128);
        expect(capture.getFrameDiff(buf, buf)).toBe(0);
    });

    test('retorna valor > 0 quando buffers diferem', () => {
        const { capture } = makeCapture();
        const buf1 = Buffer.alloc(400, 0);
        const buf2 = Buffer.alloc(400, 255);
        expect(capture.getFrameDiff(buf1, buf2)).toBe(100);
    });
});

// ============================================================
// isGtaActive
// ============================================================

describe('isGtaActive', () => {
    const { exec } = require('child_process');
    jest.mock('child_process');

    test('retorna true quando GTA V está rodando (count = 1)', async () => {
        const { capture } = makeCapture();
        const mockExec = require('child_process').exec;
        mockExec.mockImplementation((cmd, opts, cb) => cb(null, '1\n', ''));
        const result = await capture.isGtaActive();
        expect(result).toBe(true);
    });

    test('retorna false quando GTA V não está rodando (count = 0)', async () => {
        const { capture } = makeCapture();
        const mockExec = require('child_process').exec;
        mockExec.mockImplementation((cmd, opts, cb) => cb(null, '0\n', ''));
        const result = await capture.isGtaActive();
        expect(result).toBe(false);
    });

    test('retorna true quando PowerShell dá erro (não bloqueia captura)', async () => {
        const { capture } = makeCapture();
        const mockExec = require('child_process').exec;
        mockExec.mockImplementation((cmd, opts, cb) => cb(new Error('timeout'), '', ''));
        const result = await capture.isGtaActive();
        expect(result).toBe(true);
    });
});

// ============================================================
// sendWithRetry
// ============================================================

describe('sendWithRetry', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        // Mock form-data
        const FormData = require('form-data');
        FormData.mockImplementation(() => ({
            append: jest.fn(),
            getHeaders: jest.fn().mockReturnValue({})
        }));
    });

    test('retorna response na 1ª tentativa quando servidor responde', async () => {
        const { capture } = makeCapture();
        capture.running = true;
        const mockResponse = { status: 200 };
        axios.post.mockResolvedValueOnce(mockResponse);
        const result = await capture.sendWithRetry(Buffer.alloc(100));
        expect(result).toEqual(mockResponse);
        expect(axios.post).toHaveBeenCalledTimes(1);
    });

    test('retorna null imediatamente se running=false (stop durante retry)', async () => {
        const { capture } = makeCapture();
        capture.running = false;
        const result = await capture.sendWithRetry(Buffer.alloc(100));
        expect(result).toBeNull();
        expect(axios.post).not.toHaveBeenCalled();
    });

    test('lança erro após esgotar todas as tentativas', async () => {
        const { capture } = makeCapture();
        capture.running = true;
        const connError = Object.assign(new Error('connection refused'), { code: 'ECONNREFUSED' });
        axios.post.mockRejectedValue(connError);
        await expect(capture.sendWithRetry(Buffer.alloc(100), 2)).rejects.toThrow('connection refused');
    });
});

// ============================================================
// constructor — validação de URL
// ============================================================

describe('constructor', () => {
    test('lança erro se serverUrl não começa com https://', () => {
        const sendToRenderer = jest.fn();
        expect(() => new GTACapture('http://insecure.com', 1.0, sendToRenderer))
            .toThrow('serverUrl deve começar com https://');
    });

    test('aceita URL https:// sem erro', () => {
        const sendToRenderer = jest.fn();
        expect(() => new GTACapture('https://valid.fly.dev', 1.0, sendToRenderer))
            .not.toThrow();
    });
});

// ============================================================
// Race condition — mutex capturing
// ============================================================

describe('mutex capturing', () => {
    test('segunda chamada a captureAndSend retorna imediatamente se já há uma em andamento', async () => {
        const { capture } = makeCapture();
        capture.running = true;
        capture.capturing = true; // simula execução em andamento
        const spy = jest.spyOn(capture, 'isGtaActive');
        await capture.captureAndSend();
        expect(spy).not.toHaveBeenCalled(); // retornou antes de fazer qualquer coisa
    });
});
```

- [ ] **Passo 4: Rodar os testes**

```bash
cd electron-app
npm test
```

Esperado: todos os testes passam. Se algum falhar, ajustar implementação até passar.

- [ ] **Passo 5: Commit**

```bash
git add electron-app/package.json electron-app/tests/capture.test.js
git commit -m "test: testes Jest para capture.js (getFrameDiff, isGtaActive, sendWithRetry, mutex)"
```

---

## Tarefa 5: Interface Visual — Animações e Melhorias

**Arquivos:** `electron-app/renderer/css/styles.css`, `electron-app/renderer/index.html`, `electron-app/renderer/js/app.js`

- [ ] **Passo 1: Adicionar animações CSS nos indicadores**

Em `styles.css`, adicionar após o bloco `.indicator-badge.active-red`:

```css
/* Animação de pulso para indicadores ativos */
@keyframes pulse-green {
    0%, 100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.4); }
    50%       { box-shadow: 0 0 0 6px rgba(76, 175, 80, 0); }
}

@keyframes pulse-yellow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255, 152, 0, 0.4); }
    50%       { box-shadow: 0 0 0 6px rgba(255, 152, 0, 0); }
}

.indicator-badge.active-green {
    animation: pulse-green 2s infinite;
}

.indicator-badge.active-yellow {
    animation: pulse-yellow 1s infinite;
}

/* Barra de progresso para servidor acordando */
.waking-bar {
    display: none;
    height: 3px;
    background: linear-gradient(90deg, transparent, #ff9800, transparent);
    background-size: 200% 100%;
    animation: waking-slide 1.5s linear infinite;
    border-radius: 2px;
    margin: 8px 0 0;
}

@keyframes waking-slide {
    0%   { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

.waking-bar.visible {
    display: block;
}

/* Transição suave no status card */
#status-text, #status-detail {
    transition: all 0.3s ease;
}

/* Botão iniciar mais destacado */
.btn-primary.btn-large {
    background: linear-gradient(135deg, #4a5f3a, #6b8e4e);
    box-shadow: 0 4px 15px rgba(74, 95, 58, 0.4);
    transition: all 0.2s ease;
}

.btn-primary.btn-large:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(74, 95, 58, 0.6);
}

.btn-primary.btn-large:active:not(:disabled) {
    transform: translateY(0);
}
```

- [ ] **Passo 2: Adicionar barra de progresso "acordando" no HTML**

Em `index.html`, após a `<section class="controls-section">`, adicionar:

```html
<!-- Barra de progresso: servidor acordando -->
<div class="waking-bar" id="waking-bar"></div>
```

- [ ] **Passo 3: Controlar a barra via JS no handler de server-status**

Em `renderer/js/app.js`, dentro do `onServerStatus`, adicionar controle da barra:

```javascript
window.electronAPI.onServerStatus(({ status }) => {
    const badge = document.getElementById('server-indicator');
    const dot = badge.querySelector('.indicator-dot');
    const text = document.getElementById('server-indicator-text');
    const wakingBar = document.getElementById('waking-bar');

    if (status === 'online') {
        badge.className = 'indicator-badge active-green';
        dot.textContent = '🟢';
        text.textContent = 'Online';
        wakingBar.classList.remove('visible');
    } else if (status === 'waking') {
        badge.className = 'indicator-badge active-yellow';
        dot.textContent = '🟡';
        text.textContent = 'Acordando...';
        wakingBar.classList.add('visible');
    } else {
        badge.className = 'indicator-badge active-red';
        dot.textContent = '🔴';
        text.textContent = 'Offline';
        wakingBar.classList.remove('visible');
    }
});
```

- [ ] **Passo 4: Uniformizar cores do log terminal**

Em `renderer/js/app.js`, na função `addLog`, substituir a lógica de detecção de tipo:

```javascript
function addLog(message) {
    const terminal = document.getElementById('log-terminal');
    const entry = document.createElement('div');
    entry.className = 'log-entry';

    if (message.includes('❌') || message.toLowerCase().includes('erro')) {
        entry.classList.add('log-error');
    } else if (message.includes('⚠️') || message.toLowerCase().includes('aviso')) {
        entry.classList.add('log-warning');
    } else if (message.includes('✅') || message.includes('🚀') || message.includes('▶️')) {
        entry.classList.add('log-success');
    } else if (message.includes('📸')) {
        entry.classList.add('log-frame');
    }

    const now = new Date();
    const timestamp = now.toLocaleTimeString('pt-BR');

    entry.innerHTML = `
        <span class="log-timestamp">[${timestamp}]</span>
        <span class="log-message">${escapeHtml(message)}</span>
    `;

    terminal.appendChild(entry);
    terminal.scrollTop = terminal.scrollHeight;

    while (terminal.children.length > 500) {
        terminal.removeChild(terminal.firstChild);
    }
}
```

- [ ] **Passo 5: Adicionar `.log-success` e `.log-frame` ao CSS**

Em `styles.css`, buscar o bloco de estilos do log terminal e adicionar:

```css
.log-entry.log-success .log-message {
    color: #6b8e4e;
}

.log-entry.log-frame .log-message {
    color: #5f7a68;
}
```

- [ ] **Passo 6: Build e copiar para pasta do cliente**

```bash
cd electron-app
npm run build:dir
cp -r dist/win-unpacked/. "C:/Users/paulo/OneDrive/Desktop/Atalhos/GTA Analytics/"
```

- [ ] **Passo 7: Commit**

```bash
git add electron-app/renderer/css/styles.css electron-app/renderer/index.html electron-app/renderer/js/app.js
git commit -m "feat(ui): animações nos indicadores, barra de waking, log com cores uniformes"
```

---

## Resumo de Commits Esperados

```
fix: mutex em captureAndSend previne race condition com setInterval
fix: abortar sendWithRetry imediatamente quando stop() é chamado
security: validar URLs https:// em openExternal e serverUrl
test: testes Jest para capture.js (getFrameDiff, isGtaActive, sendWithRetry, mutex)
feat(ui): animações nos indicadores, barra de waking, log com cores uniformes
```
