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
                    resolve(parseInt(stdout.trim()) > 0);
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
        // Amostra 1 pixel a cada 40 bytes para velocidade (canal R apenas)
        for (let i = 0; i < buf1.length; i += 40) {
            total += Math.abs(buf1[i] - buf2[i]);
            count++;
        }
        return (total / count / 255) * 100;
    }

    /**
     * Ciclo principal: captura, filtra e envia frame
     */
    async captureAndSend() {
        if (!this.running) return;

        try {
            // Captura tela principal via desktopCapturer
            const sources = await desktopCapturer.getSources({
                types: ['screen'],
                thumbnailSize: { width: 1280, height: 720 }
            });

            if (!sources || sources.length === 0) {
                this.sendToRenderer('log', '⚠️ Nenhuma tela encontrada para captura');
                return;
            }

            const img = sources[0].thumbnail; // NativeImage já redimensionado

            // Verifica se imagem tem conteúdo
            const size = img.getSize();
            if (size.width === 0 || size.height === 0) {
                this.sendToRenderer('log', '⚠️ Frame vazio capturado');
                return;
            }

            // Filtro de cena estática (não envia se tela não mudou)
            const rawBuffer = img.toBitmap();
            const diff = this.getFrameDiff(this.prevFrameBuffer, rawBuffer);
            this.prevFrameBuffer = rawBuffer;

            if (diff < 3) return; // Menos de 3% de mudança - skip silencioso

            // Converte para JPEG qualidade 60
            const jpegBuffer = img.toJPEG(60);

            // Envia para o servidor
            const form = new FormData();
            form.append('file', jpegBuffer, {
                filename: 'frame.jpg',
                contentType: 'image/jpeg'
            });

            const response = await axios.post(this.serverUrl, form, {
                headers: form.getHeaders(),
                timeout: 30000
            });

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
            this.sendToRenderer('log', `❌ Erro: ${err.message}`);
        }
    }

    start() {
        this.running = true;
        this.startTime = Date.now();
        this.framesSent = 0;
        this.errors = 0;
        this.prevFrameBuffer = null;
        this.wasGtaPaused = false;

        this.sendToRenderer('log', '🚀 Iniciando captura...');
        this.sendToRenderer('log', `📡 Servidor: ${this.serverUrl}`);
        this.sendToRenderer('log', `🎬 FPS: ${this.fps}`);
        this.sendToRenderer('log', '✅ Captura iniciada com sucesso!');

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
