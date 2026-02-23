/**
 * GTA Analytics - Electron Main Process
 *
 * Gerencia janela principal, processo Python e IPC
 *
 * @author Paulo Eugenio Campos
 * @version 1.0.0
 */

const { app, BrowserWindow, ipcMain, Menu, Tray, shell, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Variáveis globais
let mainWindow = null;
let tray = null;
let pythonProcess = null;
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
            contextIsolation: true,
            enableRemoteModule: false,
            sandbox: true
        },
        autoHideMenuBar: true,
        frame: true,
        show: false, // Mostrar apenas quando pronto
        center: true
    });

    // Carregar interface
    mainWindow.loadFile(path.join(__dirname, 'renderer/index.html'));

    // Mostrar quando pronto
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();

        if (isDev) {
            mainWindow.webContents.openDevTools();
        }
    });

    // Evento fechar
    mainWindow.on('close', (event) => {
        if (pythonProcess && !app.isQuitting) {
            event.preventDefault();
            mainWindow.hide();
        }
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Abrir links externos no browser
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
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
 * Iniciar captura Python
 */
async function startPythonCapture(serverUrl, fps) {
    if (pythonProcess) {
        sendToRenderer('log', '⚠️ Captura já está rodando!');
        return { success: false, error: 'Already running' };
    }

    try {
        // Caminho para Python embutido
        const pythonExePath = getPythonPath();

        if (!fs.existsSync(pythonExePath)) {
            throw new Error(`Python não encontrado: ${pythonExePath}`);
        }

        sendToRenderer('log', '🚀 Iniciando captura...');
        sendToRenderer('log', `📡 Servidor: ${serverUrl}`);
        sendToRenderer('log', `🎬 FPS: ${fps}`);

        // Spawn processo Python
        pythonProcess = spawn(pythonExePath, [
            '--server', serverUrl,
            '--fps', fps.toString()
        ], {
            cwd: path.dirname(pythonExePath)
        });

        // Atualizar status
        captureStatus.running = true;
        captureStatus.startTime = Date.now();
        captureStatus.framesSent = 0;
        captureStatus.errors = 0;

        // Stdout
        pythonProcess.stdout.on('data', (data) => {
            const output = data.toString().trim();
            console.log('Python:', output);
            sendToRenderer('log', output);

            // Parsear frames enviados
            const frameMatch = output.match(/Frame (\d+)/i);
            if (frameMatch) {
                captureStatus.framesSent = parseInt(frameMatch[1]);
                captureStatus.lastFrameTime = Date.now();
                sendToRenderer('status-update', captureStatus);
            }
        });

        // Stderr
        pythonProcess.stderr.on('data', (data) => {
            const error = data.toString().trim();
            console.error('Python Error:', error);
            sendToRenderer('log', `❌ ${error}`);
            captureStatus.errors++;
        });

        // Exit
        pythonProcess.on('exit', (code) => {
            console.log(`Python process exited with code ${code}`);
            sendToRenderer('log', code === 0
                ? '✅ Captura finalizada'
                : `❌ Captura encerrada com erro (código ${code})`
            );

            pythonProcess = null;
            captureStatus.running = false;
            sendToRenderer('status-update', captureStatus);
            updateTrayMenu();
        });

        // Error
        pythonProcess.on('error', (err) => {
            console.error('Python spawn error:', err);
            sendToRenderer('log', `❌ Erro ao iniciar Python: ${err.message}`);
            pythonProcess = null;
            captureStatus.running = false;
            sendToRenderer('status-update', captureStatus);
        });

        sendToRenderer('log', '✅ Captura iniciada com sucesso!');
        sendToRenderer('status-update', captureStatus);
        updateTrayMenu();

        return { success: true };

    } catch (error) {
        console.error('Error starting Python:', error);
        sendToRenderer('log', `❌ Erro: ${error.message}`);
        return { success: false, error: error.message };
    }
}

/**
 * Iniciar captura de vídeo
 */
async function startVideoCapture(serverUrl, fps, videoSource) {
    if (pythonProcess) {
        sendToRenderer('log', 'Captura ja esta rodando!');
        return { success: false, error: 'Already running' };
    }

    try {
        // Caminho para executavel capture_video.exe
        const captureVideoExe = getVideoCapturePath();

        if (!fs.existsSync(captureVideoExe)) {
            throw new Error(`Executavel capture_video.exe nao encontrado: ${captureVideoExe}`);
        }

        sendToRenderer('log', 'Iniciando captura de video...');
        sendToRenderer('log', `Video: ${videoSource}`);
        sendToRenderer('log', `Servidor: ${serverUrl}`);
        sendToRenderer('log', `FPS: ${fps}`);

        // Spawn processo Python para vídeo
        pythonProcess = spawn(captureVideoExe, [
            '--video', videoSource,
            '--server', serverUrl,
            '--fps', String(fps)
        ]);

        // Capturar output
        pythonProcess.stdout.on('data', (data) => {
            const output = data.toString().trim();
            if (output) {
                sendToRenderer('log', output);

                // Parse stats
                const frameMatch = output.match(/Frame (\d+)/);
                if (frameMatch) {
                    captureStatus.framesSent = parseInt(frameMatch[1]);
                    captureStatus.lastFrameTime = Date.now();
                    sendToRenderer('status-update', captureStatus);
                }
            }
        });

        pythonProcess.stderr.on('data', (data) => {
            const error = data.toString().trim();
            if (error && !error.includes('UserWarning')) {
                sendToRenderer('log', `Erro: ${error}`);
                captureStatus.errors++;
            }
        });

        pythonProcess.on('close', (code) => {
            sendToRenderer('log', `Processo encerrado (codigo: ${code})`);
            pythonProcess = null;
            captureStatus.running = false;
            sendToRenderer('status-update', captureStatus);
        });

        // Update status
        captureStatus.running = true;
        captureStatus.startTime = Date.now();
        captureStatus.framesSent = 0;
        captureStatus.errors = 0;

        sendToRenderer('status-update', captureStatus);

        return { success: true };

    } catch (error) {
        sendToRenderer('log', `Erro ao iniciar: ${error.message}`);
        return { success: false, error: error.message };
    }
}

/**
 * Parar captura Python
 */
function stopPythonCapture() {
    if (!pythonProcess) {
        sendToRenderer('log', '⚠️ Nenhuma captura rodando');
        return { success: false, error: 'Not running' };
    }

    try {
        sendToRenderer('log', '⏹️ Parando captura...');

        const pid = pythonProcess.pid;

        // No Windows, precisa matar a árvore de processos
        if (process.platform === 'win32') {
            // Usar taskkill para matar processo e seus filhos
            const { execSync } = require('child_process');
            try {
                execSync(`taskkill /pid ${pid} /T /F`, { stdio: 'ignore' });
                sendToRenderer('log', '✅ Processo Python finalizado (PID: ' + pid + ')');
            } catch (killError) {
                console.error('Error killing process tree:', killError);
                // Fallback: tentar kill normal
                pythonProcess.kill();
            }
        } else {
            // Linux/Mac: SIGTERM funciona
            pythonProcess.kill('SIGTERM');

            // Force kill após 3s se não parar
            setTimeout(() => {
                if (pythonProcess && !pythonProcess.killed) {
                    pythonProcess.kill('SIGKILL');
                }
            }, 3000);
        }

        // Resetar variável imediatamente
        pythonProcess = null;
        captureStatus.running = false;
        sendToRenderer('status-update', captureStatus);
        updateTrayMenu();

        return { success: true };

    } catch (error) {
        console.error('Error stopping Python:', error);
        sendToRenderer('log', `❌ Erro ao parar: ${error.message}`);
        pythonProcess = null; // Resetar mesmo em erro
        captureStatus.running = false;
        sendToRenderer('status-update', captureStatus);
        return { success: false, error: error.message };
    }
}

/**
 * Obter caminho do Python embutido
 */
function getPythonPath() {
    if (isDev) {
        // Modo desenvolvimento: usar Python local
        return path.join(process.cwd(), 'python/dist/capture.exe');
    } else {
        // Modo produção: Python embutido no app
        return path.join(process.resourcesPath, 'python/capture.exe');
    }
}

/**
 * Obter caminho do executavel de captura de video
 */
function getVideoCapturePath() {
    if (isDev) {
        // Modo desenvolvimento: usar executavel local
        // Use process.cwd() que sempre retorna o diretório correto
        return path.join(process.cwd(), 'python/dist/capture_video.exe');
    } else {
        // Modo produção: executavel embutido no app
        return path.join(process.resourcesPath, 'python/capture_video.exe');
    }
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

    if (mode === 'video' && videoSource) {
        return await startVideoCapture(serverUrl, fps, videoSource);
    } else {
        return await startPythonCapture(serverUrl, fps);
    }
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
        // Mas no Windows, só fecha se não tiver Python rodando
        if (!pythonProcess) {
            app.quit();
        }
    }
});

/**
 * Antes de sair
 */
app.on('before-quit', () => {
    app.isQuitting = true;

    // Parar Python se rodando
    if (pythonProcess) {
        console.log('Killing Python process on app quit...');
        const pid = pythonProcess.pid;

        if (process.platform === 'win32') {
            // Windows: matar árvore de processos
            const { execSync } = require('child_process');
            try {
                execSync(`taskkill /pid ${pid} /T /F`, { stdio: 'ignore' });
                console.log(`Python process ${pid} killed`);
            } catch (error) {
                console.error('Error killing Python on quit:', error);
            }
        } else {
            pythonProcess.kill('SIGTERM');
        }

        pythonProcess = null;
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
