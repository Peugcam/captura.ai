@echo off
echo ===================================================
echo   GTA Analytics V2 - Sistema Completo
echo ===================================================
echo.
echo Iniciando sistema hibrido Go + Python...
echo.

REM Criar diretorio de exports
if not exist "backend\exports" mkdir "backend\exports"

echo [1/2] Iniciando Go Gateway (porta 8000)...
start "Go Gateway" cmd /k "cd gateway && \"C:\Program Files\Go\bin\go.exe\" run main.go websocket.go buffer.go -debug"

timeout /t 3 /nobreak >nul

echo [2/2] Iniciando Python Backend (completo)...
start "Python Backend" cmd /k "cd backend && \"C:\Users\paulo\AppData\Local\Programs\Python\Python313\python.exe\" main_complete.py"

echo.
echo ===================================================
echo   Sistema iniciado!
echo ===================================================
echo.
echo Terminal 1: Go Gateway (porta 8000)
echo Terminal 2: Python Backend (com OCR + GPT-4o)
echo.
echo Endpoints:
echo - WebSocket: ws://localhost:8000/ws
echo - Health: http://localhost:8000/health
echo - Stats: http://localhost:8000/stats
echo.
echo Pressione qualquer tecla para fechar este terminal
echo (os outros terminais continuarao rodando)
echo.
pause >nul
