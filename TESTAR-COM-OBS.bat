@echo off
echo ========================================
echo   GTA ANALYTICS V2 - TESTE COM OBS
echo ========================================
echo.
echo Este script vai:
echo 1. Iniciar o Gateway (porta 8000)
echo 2. Iniciar o Backend (porta 3000)
echo 3. Abrir o OBS setup no navegador
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

echo.
echo [1/3] Iniciando Gateway Go...
start "Gateway" cmd /k "cd /d %~dp0gateway && gateway.exe -port=8000 -buffer=200 -webrtc=true -websocket=true"

echo [2/3] Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

echo [3/3] Iniciando Backend Python...
start "Backend" cmd /k "cd /d %~dp0backend && python main_websocket.py"

echo.
echo ========================================
echo   SERVICOS INICIADOS!
echo ========================================
echo.
echo Agora siga os passos:
echo.
echo OPCAO 1 - OBS BROWSER SOURCE:
echo ----------------------------
echo 1. Abra o OBS Studio
echo 2. Adicione uma fonte "Browser"
echo 3. URL: file:///%~dp0capture-obs.html
echo 4. Width: 1920, Height: 1080, FPS: 1
echo 5. Permita captura de tela quando pedido
echo 6. Jogue normalmente!
echo.
echo OPCAO 2 - GRAVAR NO OBS + PROCESSAR:
echo ------------------------------------
echo 1. Grave gameplay no OBS normalmente
echo 2. Salve o video (ex: meu-gameplay.mp4)
echo 3. Execute: python captura-video.py --video "caminho\video.mp4"
echo.
echo OPCAO 3 - PROCESSAR VIDEO EXISTENTE:
echo ------------------------------------
echo 1. Tenha um video de GTA salvo
echo 2. Execute: python captura-video.py --video "C:\caminho\video.mp4" --fps 4
echo.
echo ========================================
echo   DASHBOARDS DISPONIVEIS:
echo ========================================
echo.
echo Abra no navegador:
echo - dashboard-tournament.html (Principal)
echo - dashboard-strategist-v2.html (Estrategista)
echo - dashboard-viewer.html (Visualizador)
echo.
echo ========================================
echo   ENDPOINTS:
echo ========================================
echo.
echo - Gateway Health: http://localhost:8000/health
echo - Gateway Stats:  http://localhost:8000/stats
echo - Backend Health: http://localhost:3000/health
echo - Backend Stats:  http://localhost:3000/stats
echo.
echo Pressione qualquer tecla para sair...
pause >nul
