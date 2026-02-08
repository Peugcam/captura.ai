@echo off
cls
echo ===================================================
echo   Naruto Online Analytics - Sistema Completo
echo ===================================================
echo.
echo [!] Configuracao atual: GAME_TYPE=naruto
echo.
echo Iniciando sistema hibrido Go + Python...
echo.

REM Criar diretorio de exports
if not exist "backend\exports" mkdir "backend\exports"

echo [1/2] Iniciando Go Gateway (porta 8000)...
start "Go Gateway" cmd /k "cd gateway && go run main.go websocket.go buffer.go -debug"

timeout /t 3 /nobreak >nul

echo [2/2] Iniciando Python Backend (processador Naruto)...
start "Python Backend" cmd /k "cd backend && py main_complete.py"

echo.
echo ===================================================
echo   Sistema iniciado para NARUTO ONLINE!
echo ===================================================
echo.
echo Terminal 1: Go Gateway (porta 8000)
echo Terminal 2: Python Backend (processador com OCR + GPT-4o)
echo.
echo Configuracao ativa:
echo - GAME_TYPE: naruto
echo - USE_ROI: false (analisa tela inteira)
echo - OCR_WORKERS: 8
echo - Vision Model: GPT-4o
echo.
echo Endpoints:
echo - WebSocket: ws://localhost:8000/ws
echo - Health: http://localhost:8000/health
echo - Stats: http://localhost:8000/stats
echo.
echo Proximos passos:
echo 1. Abra o Naruto Online no navegador
echo 2. Execute CAPTURAR-NARUTO.bat para comecar a captura
echo.
echo Pressione qualquer tecla para fechar este terminal
echo (os outros terminais continuarao rodando)
echo.
pause >nul
