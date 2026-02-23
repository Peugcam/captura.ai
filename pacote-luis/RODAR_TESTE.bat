@echo off
chcp 65001 >nul
cls
echo ====================================================================
echo   TESTE NARUTO ONLINE - GTA ANALYTICS
echo ====================================================================
echo.
echo ESTADO ATUAL DO SISTEMA:
echo.
curl -s https://gta-analytics-backend.fly.dev/stats
echo.
echo.
echo ====================================================================
echo.
echo PREPARACAO:
echo  1. Abra o OBS Studio
echo  2. Certifique-se que Naruto Online esta visivel no OBS
echo  3. WebSocket deve estar ativo (porta 4455)
echo.
echo Quando estiver pronto, pressione qualquer tecla...
pause >nul

cls
echo ====================================================================
echo   INICIANDO CAPTURA
echo ====================================================================
echo.
echo O programa vai rodar por 30 segundos capturando frames.
echo.
echo Voce deve ver algo como:
echo   [20 frames] 5s ^| 4.0 FPS ^| 0 erros
echo   [40 frames] 10s ^| 4.0 FPS ^| 0 erros
echo.
echo Se aparecer "0 erros" = FUNCIONANDO!
echo.
echo ====================================================================
echo.

cd /d "%~dp0"
py gta-analytics-v2.py

echo.
echo ====================================================================
echo   CAPTURA INTERROMPIDA
echo ====================================================================
echo.
echo Aguarde 5 segundos para processar...
timeout /t 5 /nobreak >nul

cls
echo ====================================================================
echo   RESULTADO DO TESTE
echo ====================================================================
echo.
echo Consultando backend...
echo.
curl -s https://gta-analytics-backend.fly.dev/stats
echo.
echo.
echo ====================================================================
echo   COMO INTERPRETAR:
echo ====================================================================
echo.
echo frames_received   = Frames que chegaram no backend
echo                     (deve ter aumentado!)
echo.
echo frames_processed  = Frames analisados pela Vision API
echo                     (deve ter aumentado!)
echo.
echo kills_detected    = Kills encontradas
echo                     (normal ser 0 no Naruto)
echo.
echo filter_efficiency = %% de frames duplicados descartados
echo                     (50-70%% e bom)
echo.
echo ====================================================================
echo.
echo Se frames_received aumentou = SISTEMA FUNCIONANDO! ✓
echo.
pause
