@echo off
echo ====================================================================
echo   GTA ANALYTICS - TESTE RAPIDO
echo ====================================================================
echo.
echo Este teste captura frames do OBS e envia para o backend.
echo.
echo REQUISITOS:
echo   1. OBS Studio aberto
echo   2. WebSocket ativado (Ferramentas -^> Configuracoes WebSocket)
echo   3. Gateway rodando (docker-compose up gateway)
echo.
pause

echo.
echo [*] Iniciando captura...
echo.

py obs-capture-client.py

pause
