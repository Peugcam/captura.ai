// Mock do módulo electron antes de qualquer require
jest.mock('electron', () => ({
    desktopCapturer: {
        getSources: jest.fn()
    }
}));

jest.mock('axios');
jest.mock('form-data');
jest.mock('child_process');

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

    test('retorna 100 quando buffers são completamente diferentes', () => {
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
    beforeEach(() => {
        jest.clearAllMocks();
    });

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

    test('lança erro após esgotar todas as tentativas com erro não-conexão', async () => {
        const { capture } = makeCapture();
        capture.running = true;
        const genericError = new Error('server error');
        axios.post.mockRejectedValue(genericError);
        await expect(capture.sendWithRetry(Buffer.alloc(100), 1)).rejects.toThrow('server error');
    });

    test('tenta novamente em erro de conexão e retorna response na 2ª tentativa', async () => {
        const { capture } = makeCapture();
        capture.running = true;
        const connError = Object.assign(new Error('connection refused'), { code: 'ECONNREFUSED' });
        const mockResponse = { status: 200 };
        axios.post
            .mockRejectedValueOnce(connError)
            .mockResolvedValueOnce(mockResponse);
        // Substituir setTimeout para não esperar delay real
        jest.useFakeTimers();
        const promise = capture.sendWithRetry(Buffer.alloc(100), 2);
        await jest.runAllTimersAsync();
        const result = await promise;
        expect(result).toEqual(mockResponse);
        expect(axios.post).toHaveBeenCalledTimes(2);
        jest.useRealTimers();
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

    test('lança erro se serverUrl é null', () => {
        const sendToRenderer = jest.fn();
        expect(() => new GTACapture(null, 1.0, sendToRenderer))
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
    test('segunda chamada retorna imediatamente se já há uma em andamento', async () => {
        const { capture } = makeCapture();
        capture.running = true;
        capture.capturing = true;
        const spy = jest.spyOn(capture, 'isGtaActive');
        await capture.captureAndSend();
        expect(spy).not.toHaveBeenCalled();
    });

    test('running é false após stop()', () => {
        const { capture } = makeCapture();
        capture.running = true;
        capture.capturing = true;
        capture.stop();
        expect(capture.running).toBe(false);
    });
});
