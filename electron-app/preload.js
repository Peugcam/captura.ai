/**
 * GTA Analytics - Electron Preload Script
 *
 * Bridge seguro entre renderer e main process
 *
 * @author Paulo Eugenio Campos
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expor API segura para renderer
contextBridge.exposeInMainWorld('electronAPI', {
    /**
     * Iniciar captura
     * @param {string} serverUrl - URL do servidor
     * @param {number} fps - Frames por segundo
     * @param {string} mode - Modo: 'live' ou 'video'
     * @param {string} videoSource - Caminho do vídeo (se mode === 'video')
     * @returns {Promise<{success: boolean, error?: string}>}
     */
    startCapture: (serverUrl, fps, mode, videoSource) => {
        return ipcRenderer.invoke('start-capture', { serverUrl, fps, mode, videoSource });
    },

    /**
     * Selecionar arquivo de vídeo
     * @returns {Promise<{success: boolean, filePath?: string, error?: string}>}
     */
    selectVideoFile: () => {
        return ipcRenderer.invoke('select-video-file');
    },

    /**
     * Parar captura
     * @returns {Promise<{success: boolean, error?: string}>}
     */
    stopCapture: () => {
        return ipcRenderer.invoke('stop-capture');
    },

    /**
     * Obter status da captura
     * @returns {Promise<Object>}
     */
    getStatus: () => {
        return ipcRenderer.invoke('get-status');
    },

    /**
     * Salvar configurações
     * @param {Object} config - Configurações
     * @returns {Promise<{success: boolean}>}
     */
    saveConfig: (config) => {
        return ipcRenderer.invoke('save-config', config);
    },

    /**
     * Obter configurações
     * @returns {Promise<Object>}
     */
    getConfig: () => {
        return ipcRenderer.invoke('get-config');
    },

    /**
     * Abrir URL externa
     * @param {string} url - URL para abrir
     * @returns {Promise<{success: boolean}>}
     */
    openExternal: (url) => {
        return ipcRenderer.invoke('open-external', url);
    },

    /**
     * Receber logs do Python
     * @param {Function} callback - Função callback
     */
    onLog: (callback) => {
        ipcRenderer.on('log', (event, data) => callback(data));
    },

    /**
     * Receber atualizações de status
     * @param {Function} callback - Função callback
     */
    onStatusUpdate: (callback) => {
        ipcRenderer.on('status-update', (event, data) => callback(data));
    },

    /**
     * Remover listener de logs
     */
    removeLogListener: () => {
        ipcRenderer.removeAllListeners('log');
    },

    /**
     * Remover listener de status
     */
    removeStatusListener: () => {
        ipcRenderer.removeAllListeners('status-update');
    }
});

// Log para debug
console.log('Preload script loaded successfully');
