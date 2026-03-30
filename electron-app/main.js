/**
 * GTA Analytics - Electron Main Process
 *
 * Gerencia janela principal, processo Python e IPC
 *
 * @author Paulo Eugenio Campos
 * @version 1.0.0
 */

const { app, BrowserWindow, ipcMain, Menu, Tray, shell, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const GTACapture = require('./capture');

// Variáveis globais
let mainWindow = null;
let tray = null;
let captureInstance = null;
let captureStatus = {
    running: false,
    framesSent: 0,
    errors: 0,
    startTime: null,
    lastFrameTime: null
};

// Configurações
const isDev = !app.isPackaged; // Detecta modo desenvolvimento automaticamente
const CONFIG = {
    serverUrl: 'https://gta-analytics-v2.fly.dev',
    fps: 1.0,  // Changed from 0.5 to 1.0 for better kill detection
    autoStart: false
};

/**
 * Criar janela principal
 */
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 900,
        height: 700,
        minWidth: 800,
        minHeight: 600,
        backgroundColor: '#1a1a2e',
        icon: path.join(__dirname, 'assets/icon.ico'),
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true
        },
        autoHideMenuBar: true,
        frame: true,
        show: true,
        center: true
    });

    // Carregar interface
    mainWindow.loadFile(path.join(__dirname, 'renderer/index.html'));

    // Fallback: mostrar após 3s mesmo se ready-to-show não disparar
    setTimeout(() => { if (mainWindow && !mainWindow.isDestroyed()) mainWindow.show(); }, 3000);

    // Mostrar quando pronto
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();

        // DevTools desativado (use Ctrl+Shift+I para abrir manualmente)
        // if (isDev) { mainWindow.webContents.openDevTools(); }
    });

    // Evento fechar
    mainWindow.on('close', (event) => {
        if (captureInstance && !app.isQuitting) {
            event.preventDefault();
            mainWindow.hide();
        }
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Abrir links externos no browser
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        if (url.startsWith('https://')) {
            shell.openExternal(url);
        }
        return { action: 'deny' };
    });
}

/**
 * Criar tray icon
 */
function createTray() {
    try {
        const trayIconPath = path.join(__dirname, 'assets/tray-icon.png');
        const iconIcoPath = path.join(__dirname, 'assets/icon.ico');

        // Tenta achar um ícone válido
        let iconPath;
        if (fs.existsSync(trayIconPath)) {
            iconPath = trayIconPath;
        } else if (fs.existsSync(iconIcoPath)) {
            iconPath = iconIcoPath;
        } else {
            // Sem ícone customizado, tray não será criado
            console.warn('Tray icons not found, skipping tray creation');
            return;
        }

        tray = new Tray(iconPath);
    } catch (error) {
        console.error('Error creating tray:', error);
        return; // Continue sem tray se falhar
    }

    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Abrir GTA Analytics',
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                }
            }
        },
        { type: 'separator' },
        {
            label: captureStatus.running ? 'Parar Captura' : 'Iniciar Captura',
            click: () => {
                if (captureStatus.running) {
                    stopPythonCapture();
                } else {
                    startPythonCapture(CONFIG.serverUrl, CONFIG.fps);
                }
            }
        },
        { type: 'separator' },
        {
            label: 'Sair',
            click: () => {
                app.isQuitting = true;
                app.quit();
            }
        }
    ]);

    tray.setContextMenu(contextMenu);
    tray.setToolTip('GTA Analytics');

    tray.on('click', () => {
        if (mainWindow) {
            if (mainWindow.isVisible()) {
                mainWindow.hide();
            } else {
                mainWindow.show();
            }
        }
    });
}

/**
 * Iniciar captura (JavaScript nativo - sem Python)
 */
async function startPythonCapture(serverUrl, fps) {
    if (captureInstance && captureStatus.running) {
        sendToRenderer('log', '⚠️ Captura já está rodando!');
        return { success: false, error: 'Already running' };
    }

    captureInstance = new GTACapture(serverUrl, fps, sendToRenderer);
    const result = captureInstance.start();

    captureStatus.running = true;
    captureStatus.startTime = Date.now();
    captureStatus.framesSent = 0;
    captureStatus.errors = 0;
    updateTrayMenu();

    return result;
}

/**
 * Parar captura
 */
function stopPythonCapture() {
    if (!captureInstance || !captureStatus.running) {
        sendToRenderer('log', '⚠️ Nenhuma captura rodando');
        return { success: false, error: 'Not running' };
    }

    const result = captureInstance.stop();
    captureInstance = null;
    captureStatus.running = false;
    updateTrayMenu();

    return result;
}

/**
 * Enviar mensagem para renderer
 */
function sendToRenderer(channel, data) {
    if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send(channel, data);
    }
}

/**
 * Atualizar menu do tray
 */
function updateTrayMenu() {
    if (!tray) return;

    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Abrir GTA Analytics',
            click: () => mainWindow?.show()
        },
        { type: 'separator' },
        {
            label: captureStatus.running ? '⏹️ Parar Captura' : '▶️ Iniciar Captura',
            click: () => {
                if (captureStatus.running) {
                    stopPythonCapture();
                } else {
                    startPythonCapture(CONFIG.serverUrl, CONFIG.fps);
                }
            }
        },
        {
            label: `Status: ${captureStatus.running ? 'Capturando 🟢' : 'Parado ⚫'}`,
            enabled: false
        },
        {
            label: `Frames: ${captureStatus.framesSent}`,
            enabled: false
        },
        { type: 'separator' },
        {
            label: 'Sair',
            click: () => {
                app.isQuitting = true;
                app.quit();
            }
        }
    ]);

    tray.setContextMenu(contextMenu);
}

// ============================================================================
// IPC HANDLERS
// ============================================================================

/**
 * Iniciar captura
 */
ipcMain.handle('start-capture', async (event, { serverUrl, fps, mode, videoSource }) => {
    CONFIG.serverUrl = serverUrl;
    CONFIG.fps = fps;

    return await startPythonCapture(serverUrl, fps);
});

/**
 * Selecionar arquivo de vídeo
 */
ipcMain.handle('select-video-file', async (event) => {
    try {
        const result = await dialog.showOpenDialog(mainWindow, {
            properties: ['openFile'],
            filters: [
                { name: 'Videos', extensions: ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'] },
                { name: 'All Files', extensions: ['*'] }
            ]
        });

        if (result.canceled || result.filePaths.length === 0) {
            return { success: false };
        }

        return {
            success: true,
            filePath: result.filePaths[0]
        };
    } catch (error) {
        return {
            success: false,
            error: error.message
        };
    }
});

/**
 * Parar captura
 */
ipcMain.handle('stop-capture', async (event) => {
    return stopPythonCapture();
});

/**
 * Obter status
 */
ipcMain.handle('get-status', async (event) => {
    return captureStatus;
});

/**
 * Salvar configurações
 */
ipcMain.handle('save-config', async (event, config) => {
    Object.assign(CONFIG, config);
    return { success: true };
});

/**
 * Obter configurações
 */
ipcMain.handle('get-config', async (event) => {
    return CONFIG;
});

/**
 * Abrir URL externa
 */
ipcMain.handle('open-external', async (event, url) => {
    if (!url || !url.startsWith('https://')) {
        return { success: false, error: 'Apenas URLs https:// são permitidas' };
    }
    await shell.openExternal(url);
    return { success: true };
});

// ============================================================================
// APP EVENTS
// ============================================================================

/**
 * App pronto
 */
app.whenReady().then(() => {
    createWindow();
    createTray();

    // macOS: recriar janela quando ícone do dock clicado
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

/**
 * Fechar todas as janelas
 */
app.on('window-all-closed', () => {
    // No macOS, apps ficam ativos até Cmd+Q
    if (process.platform !== 'darwin') {
        if (!captureStatus.running) {
            app.quit();
        }
    }
});

/**
 * Antes de sair
 */
app.on('before-quit', () => {
    app.isQuitting = true;

    // Parar captura se estiver rodando
    if (captureInstance && captureStatus.running) {
        captureInstance.stop();
        captureInstance = null;
    }
});

/**
 * Sair
 */
app.on('will-quit', () => {
    // Cleanup
    if (tray) {
        tray.destroy();
    }
});

// Prevenir múltiplas instâncias
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
    app.quit();
} else {
    app.on('second-instance', () => {
        // Alguém tentou abrir segunda instância
        if (mainWindow) {
            if (mainWindow.isMinimized()) mainWindow.restore();
            mainWindow.focus();
            mainWindow.show();
        }
    });
}
