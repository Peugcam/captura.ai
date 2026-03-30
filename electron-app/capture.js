/**
 * GTA Analytics - Capture Module (JavaScript nativo)
 *
 * Substitui o capture.py por completo usando APIs do Electron.
 * Sem Python, sem executáveis externos, sem dependências extras.
 */

const { desktopCapturer } = require('electron');
const axios = require('axios');
const FormData = require('form-data');
const { exec } = require('child_process');

class GTACapture {
    constructor(serverUrl, fps, sendToRenderer) {
        if (!serverUrl || !serverUrl.startsWith('https://')) {
            throw new Error('serverUrl deve começar com https://');
        }
        this.serverUrl = `${serverUrl}/api/frames/upload`;
        this.fps = fps;
        this.interval = 1000 / fps;
        this.running = false;
        this.framesSent = 0;
        this.errors = 0;
        this.startTime = null;
        this.prevFrameBuffer = null;
        this.timer = null;
        this.sendToRenderer = sendToRenderer;
        this.wasGtaPaused = false;
        this.serverWaking = false;       // servidor está acordando
        this.consecutiveErrors = 0;      // erros consecutivos para reconexão
        this.capturing = false;  // mutex para evitar race condition
    }

    /**
     * Verifica se GTA V é a janela ativa
     */
    isGtaActive() {
        return new Promise((resolve) => {
            exec(
                'powershell -NoProfile -Command "Get-Process | Where-Object { $_.MainWindowTitle -match \'Grand Theft Auto\' } | Measure-Object | Select-Object -ExpandProperty Count"',
                { timeout: 2000 },
                (err, stdout) => {
                    if (err) return resolve(true); // Não bloquear se erro
                    const active = parseInt(stdout.trim()) > 0;
                    resolve(active);
                }
            );
        });
    }

    /**
     * Calcula diferença entre frames (filtro de cena estática)
     * Retorna porcentagem de mudança (0-100)
     */
    getFrameDiff(buf1, buf2) {
        if (!buf1 || buf1.length !== buf2.length) return 100;
        let total = 0;
        let count = 0;
        for (let i = 0; i < buf1.length; i += 40) {
            total += Math.abs(buf1[i] - buf2[i]);
            count++;
        }
        return (total / count / 255) * 100;
    }

    /**
     * Envia frame com retry automático (para servidor dormindo)
     */
    async sendWithRetry(jpegBuffer, maxRetries = 4) {
        const form = new FormData();
        form.append('file', jpegBuffer, {
            filename: 'frame.jpg',
            contentType: 'image/jpeg'
        });

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            if (!this.running) return null; // aborta se stop() foi chamado
            try {
                const response = await axios.post(this.serverUrl, form, {
                    headers: form.getHeaders(),
                    timeout: 15000
                });

                // Servidor respondeu — limpa estado de waking
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
                    // Espera crescente: 3s, 5s, 8s
                    const delay = 3000 + (attempt - 1) * 2000;
                    await new Promise(r => setTimeout(r, delay));
                } else {
                    throw err;
                }
            }
        }
    }

    /**
     * Ciclo principal: captura, filtra e envia frame
     */
    async captureAndSend() {
        if (!this.running) return;
        if (this.capturing) return;
        this.capturing = true;

        try {
            // Verifica se GTA V está rodando
            const gtaActive = await this.isGtaActive();
            if (!gtaActive) {
                if (!this.wasGtaPaused) {
                    this.sendToRenderer('log', '⏸️ GTA V não detectado - captura pausada');
                    this.sendToRenderer('gta-status', { active: false });
                    this.wasGtaPaused = true;
                }
                return;
            }
            if (this.wasGtaPaused) {
                this.sendToRenderer('log', '▶️ GTA V detectado - retomando captura');
                this.sendToRenderer('gta-status', { active: true });
                this.wasGtaPaused = false;
            }

            // Captura tela principal via desktopCapturer
            const sources = await desktopCapturer.getSources({
                types: ['screen'],
                thumbnailSize: { width: 1280, height: 720 }
            });

            if (!sources || sources.length === 0) {
                this.sendToRenderer('log', '⚠️ Nenhuma tela encontrada para captura');
                return;
            }

            const img = sources[0].thumbnail;

            const size = img.getSize();
            if (size.width === 0 || size.height === 0) {
                this.sendToRenderer('log', '⚠️ Frame vazio capturado');
                return;
            }

            // Filtro de cena estática
            const rawBuffer = img.toBitmap();
            const diff = this.getFrameDiff(this.prevFrameBuffer, rawBuffer);
            this.prevFrameBuffer = rawBuffer;

            if (diff < 3) return; // skip silencioso

            const jpegBuffer = img.toJPEG(60);

            // Envia com retry automático
            const response = await this.sendWithRetry(jpegBuffer);
            if (!response) return; // stop() foi chamado durante retry

            if (response.status === 200) {
                this.framesSent++;
                const sizeKb = Math.round(jpegBuffer.length / 1024);
                this.sendToRenderer('log', `📸 Frame ${this.framesSent} enviado (${sizeKb} KB)`);
                this.sendToRenderer('status-update', {
                    running: true,
                    framesSent: this.framesSent,
                    errors: this.errors,
                    startTime: this.startTime,
                    lastFrameTime: Date.now()
                });
            } else {
                this.errors++;
                this.sendToRenderer('log', `❌ Servidor retornou ${response.status}`);
            }

        } catch (err) {
            this.errors++;
            this.consecutiveErrors++;
            this.sendToRenderer('log', `❌ Erro: ${err.message}`);
            this.sendToRenderer('server-status', { status: 'offline' });

            // Auto-reconexão: avisa após 3 erros consecutivos
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
            this.capturing = false;
        }
    }

    start() {
        this.running = true;
        this.startTime = Date.now();
        this.framesSent = 0;
        this.errors = 0;
        this.prevFrameBuffer = null;
        this.wasGtaPaused = false;
        this.serverWaking = false;
        this.consecutiveErrors = 0;
        this.capturing = false;

        this.sendToRenderer('log', '🚀 Iniciando captura...');
        this.sendToRenderer('log', `📡 Servidor: ${this.serverUrl}`);
        this.sendToRenderer('log', `🎬 FPS: ${this.fps}`);
        this.sendToRenderer('log', '✅ Captura iniciada com sucesso!');
        this.sendToRenderer('gta-status', { active: false }); // começa verificando
        this.sendToRenderer('server-status', { status: 'online' });

        this.timer = setInterval(() => this.captureAndSend(), this.interval);

        this.sendToRenderer('status-update', {
            running: true,
            framesSent: 0,
            errors: 0,
            startTime: this.startTime,
            lastFrameTime: null
        });

        return { success: true };
    }

    stop() {
        this.running = false;
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }

        this.sendToRenderer('log', '⏹️ Captura parada');
        this.sendToRenderer('log', `📊 Resumo: ${this.framesSent} frames enviados, ${this.errors} erros`);
        this.sendToRenderer('gta-status', { active: false });
        this.sendToRenderer('server-status', { status: 'offline' });
        this.sendToRenderer('status-update', {
            running: false,
            framesSent: this.framesSent,
            errors: this.errors,
            startTime: this.startTime,
            lastFrameTime: null
        });

        return { success: true };
    }
}

module.exports = GTACapture;
