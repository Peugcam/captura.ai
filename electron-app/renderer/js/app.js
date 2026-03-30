/**
 * GTA Analytics - Frontend JavaScript
 *
 * Gerencia interface e comunicação com main process
 *
 * @author Paulo Eugenio Campos
 */

// Estado global
let isCapturing = false;
let startTime = null;
let uptimeInterval = null;
let currentMode = 'live'; // 'live' or 'video'
let currentConfig = {
    serverUrl: 'https://gta-analytics-v2.fly.dev',
    fps: 0.5,
    videoSource: ''
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('App initialized');

    // Carregar configurações salvas
    await loadConfig();

    // Setup event listeners
    setupEventListeners();

    // Setup IPC listeners
    setupIPCListeners();

    // Verificar status inicial
    await checkInitialStatus();

    // Animações de entrada
    document.querySelectorAll('.status-card, .controls-section, .log-section, .quick-links')
        .forEach((el, index) => {
            el.style.animation = `slideUp 0.5s ease ${index * 0.1}s both`;
        });
});

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
    // Botões principais
    document.getElementById('start-btn').addEventListener('click', handleStartCapture);
    document.getElementById('stop-btn').addEventListener('click', handleStopCapture);

    // Mode selection
    document.getElementById('mode-live-btn').addEventListener('click', () => setMode('live'));
    document.getElementById('mode-video-btn').addEventListener('click', () => setMode('video'));
    document.getElementById('browse-video-btn').addEventListener('click', handleBrowseVideo);

    // Settings
    document.getElementById('btn-settings').addEventListener('click', toggleSettings);
    document.getElementById('save-settings-btn').addEventListener('click', handleSaveSettings);

    // Dashboard
    document.getElementById('btn-dashboard').addEventListener('click', () => {
        openExternal(currentConfig.serverUrl + '/strategist');
    });

    // FPS Slider
    const fpsSlider = document.getElementById('fps-slider');
    fpsSlider.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value);
        document.getElementById('fps-value').textContent = value.toFixed(1);
        updateCostEstimate(value);
    });

    // Clear log
    document.getElementById('clear-log-btn').addEventListener('click', clearLog);

    // Quick links
    document.querySelectorAll('.link-card').forEach(card => {
        card.addEventListener('click', () => {
            const url = card.getAttribute('data-url');
            if (url) openExternal(url);
        });
    });
}

// ============================================================================
// MODE SELECTION
// ============================================================================

function setMode(mode) {
    currentMode = mode;

    // Update button states
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`mode-${mode}-btn`).classList.add('active');

    // Show/hide video input
    const videoInputGroup = document.getElementById('video-input-group');
    videoInputGroup.style.display = mode === 'video' ? 'block' : 'none';

    addLog(`📌 Modo alterado para: ${mode === 'live' ? 'Captura ao Vivo' : 'Vídeo Gravado'}`);
}

async function handleBrowseVideo() {
    try {
        const result = await window.electronAPI.selectVideoFile();
        if (result.success && result.filePath) {
            document.getElementById('video-input').value = result.filePath;
            currentConfig.videoSource = result.filePath;
            addLog(`📁 Vídeo selecionado: ${result.filePath}`);
        }
    } catch (error) {
        addLog(`❌ Erro ao selecionar vídeo: ${error.message}`);
    }
}

function setupIPCListeners() {
    window.electronAPI.onLog((log) => {
        addLog(log);
    });

    window.electronAPI.onStatusUpdate((status) => {
        updateStatus(status);
    });

    // Status do GTA V
    window.electronAPI.onGtaStatus(({ active }) => {
        const badge = document.getElementById('gta-indicator');
        const dot = badge.querySelector('.indicator-dot');
        const text = document.getElementById('gta-indicator-text');

        badge.className = 'indicator-badge ' + (active ? 'active-green' : 'active-red');
        dot.textContent = active ? '🟢' : '🔴';
        text.textContent = active ? 'Detectado' : 'Não detectado';
    });

    // Status do servidor
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
        } else if (status === 'offline') {
            badge.className = 'indicator-badge active-red';
            dot.textContent = '🔴';
            text.textContent = 'Offline';
            wakingBar.classList.remove('visible');
        } else {
            badge.className = 'indicator-badge';
            dot.textContent = '⚫';
            text.textContent = 'Aguardando';
            wakingBar.classList.remove('visible');
        }
    });
}

// ============================================================================
// CAPTURE CONTROLS
// ============================================================================

async function handleStartCapture() {
    const serverUrl = document.getElementById('server-url').value.trim();
    const fps = parseFloat(document.getElementById('fps-slider').value);

    if (!serverUrl) {
        alert('Por favor, configure o URL do servidor!');
        return;
    }

    // Validar URL
    try {
        new URL(serverUrl);
    } catch (e) {
        alert('URL inválida! Use formato: https://servidor.com');
        return;
    }

    // Validar modo vídeo
    let videoSource = '';
    if (currentMode === 'video') {
        videoSource = document.getElementById('video-input').value.trim();
        if (!videoSource) {
            alert('Por favor, selecione um vídeo ou URL do YouTube!');
            return;
        }
    }

    addLog('Iniciando captura...');

    try {
        const result = await window.electronAPI.startCapture(serverUrl, fps, currentMode, videoSource);

        if (result.success) {
            isCapturing = true;
            startTime = Date.now();

            // Update UI
            updateUICapturing();

            // Start uptime counter
            uptimeInterval = setInterval(updateUptime, 1000);

            addLog('✅ Captura iniciada com sucesso!');
        } else {
            addLog(`❌ Erro ao iniciar: ${result.error}`);
            alert(`Erro ao iniciar captura: ${result.error}`);
        }
    } catch (error) {
        addLog(`❌ Erro: ${error.message}`);
        alert(`Erro ao iniciar captura: ${error.message}`);
    }
}

async function handleStopCapture() {
    addLog('⏹️ Parando captura...');

    try {
        const result = await window.electronAPI.stopCapture();

        if (result.success) {
            isCapturing = false;

            // Update UI
            updateUIStopped();

            // Stop uptime counter
            if (uptimeInterval) {
                clearInterval(uptimeInterval);
                uptimeInterval = null;
            }

            addLog('✅ Captura parada');
        } else {
            addLog(`❌ Erro ao parar: ${result.error}`);
        }
    } catch (error) {
        addLog(`❌ Erro: ${error.message}`);
    }
}

async function checkInitialStatus() {
    try {
        const status = await window.electronAPI.getStatus();
        updateStatus(status);

        if (status.running) {
            isCapturing = true;
            startTime = status.startTime;
            updateUICapturing();

            uptimeInterval = setInterval(updateUptime, 1000);
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

// ============================================================================
// UI UPDATES
// ============================================================================

function updateUICapturing() {
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const statusDetail = document.getElementById('status-detail');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');

    statusDot.textContent = '🟢';
    statusDot.classList.add('active');
    statusText.textContent = 'Capturando GTA V...';
    statusDetail.textContent = 'Enviando frames para o servidor';

    startBtn.disabled = true;
    stopBtn.disabled = false;
}

function updateUIStopped() {
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const statusDetail = document.getElementById('status-detail');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');

    statusDot.textContent = '⚫';
    statusDot.classList.remove('active');
    statusText.textContent = 'Captura parada';
    statusDetail.textContent = 'Aguardando início';

    startBtn.disabled = false;
    stopBtn.disabled = true;
}

function updateStatus(status) {
    // Update stats
    document.getElementById('frames-count').textContent = status.framesSent || 0;
    document.getElementById('errors-count').textContent = status.errors || 0;

    // Calculate FPS
    if (status.lastFrameTime && status.startTime) {
        const duration = (status.lastFrameTime - status.startTime) / 1000;
        const fps = duration > 0 ? (status.framesSent / duration).toFixed(2) : '0.00';
        document.getElementById('current-fps').textContent = fps;
    }
}

function updateUptime() {
    if (!startTime) return;

    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const hours = Math.floor(elapsed / 3600);
    const minutes = Math.floor((elapsed % 3600) / 60);
    const seconds = elapsed % 60;

    const display = hours > 0
        ? `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
        : `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

    document.getElementById('uptime').textContent = display;
}

function updateCostEstimate(fps) {
    // Cálculo baseado em Together AI: $0.30/1M tokens
    // Estimativa: 1 frame = ~500 tokens
    const tokensPerFrame = 500;
    const costPer1MTokens = 0.30;

    const framesPerHour = fps * 3600;
    const tokensPerHour = framesPerHour * tokensPerFrame;
    const costPerHour = (tokensPerHour / 1000000) * costPer1MTokens;
    const costPerEvent = costPerHour * 3;

    document.getElementById('cost-hour').textContent = `$${costPerHour.toFixed(2)}`;
    document.getElementById('cost-event').textContent = `$${costPerEvent.toFixed(2)}`;
}

// ============================================================================
// SETTINGS
// ============================================================================

function toggleSettings() {
    const panel = document.getElementById('settings-panel');
    const isVisible = panel.style.display !== 'none';

    panel.style.display = isVisible ? 'none' : 'block';

    if (!isVisible) {
        panel.style.animation = 'slideUp 0.3s ease both';
    }
}

async function handleSaveSettings() {
    const serverUrl = document.getElementById('server-url').value.trim();
    const fps = parseFloat(document.getElementById('fps-slider').value);

    if (!serverUrl) {
        alert('URL do servidor não pode estar vazio!');
        return;
    }

    // Validar URL
    try {
        new URL(serverUrl);
    } catch (e) {
        alert('URL inválida! Use formato: https://servidor.com');
        return;
    }

    currentConfig.serverUrl = serverUrl;
    currentConfig.fps = fps;

    try {
        await window.electronAPI.saveConfig(currentConfig);
        addLog('💾 Configurações salvas com sucesso!');

        // Feedback visual
        const btn = document.getElementById('save-settings-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span>✅ Salvo!</span>';
        btn.disabled = true;

        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 2000);

    } catch (error) {
        addLog(`❌ Erro ao salvar: ${error.message}`);
        alert('Erro ao salvar configurações!');
    }
}

async function loadConfig() {
    try {
        const config = await window.electronAPI.getConfig();

        currentConfig = config;

        document.getElementById('server-url').value = config.serverUrl;
        document.getElementById('fps-slider').value = config.fps;
        document.getElementById('fps-value').textContent = config.fps.toFixed(1);

        updateCostEstimate(config.fps);

        console.log('Config loaded:', config);
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

// ============================================================================
// LOG TERMINAL
// ============================================================================

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

function clearLog() {
    const terminal = document.getElementById('log-terminal');
    terminal.innerHTML = `
        <div class="log-entry log-info">
            <span class="log-timestamp">[${new Date().toLocaleTimeString('pt-BR')}]</span>
            <span class="log-message">Log limpo</span>
        </div>
    `;
}

// ============================================================================
// UTILITIES
// ============================================================================

async function openExternal(url) {
    try {
        await window.electronAPI.openExternal(url);
        addLog(`🔗 Abrindo: ${url}`);
    } catch (error) {
        console.error('Error opening URL:', error);
        addLog(`❌ Erro ao abrir URL: ${error.message}`);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================================
// EXPORTS (for debugging)
// ============================================================================

window.gtaAnalytics = {
    getStatus: () => ({ isCapturing, startTime, currentConfig }),
    addLog,
    clearLog
};

console.log('✅ GTA Analytics frontend loaded');
