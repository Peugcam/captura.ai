@echo off
echo ====================================================================
echo   ABRINDO DASHBOARD DE TORNEIO
echo ====================================================================
echo.
echo Abrindo dashboard profissional do Fly.io...
echo.
echo URL: https://gta-analytics-backend.fly.dev/strategist
echo.
echo O dashboard vai abrir no navegador e mostrar:
echo  - Times vivos / eliminados
echo  - Jogadores vivos por time
echo  - Kill counts
echo  - Rankings em tempo real
echo  - Gerenciamento de roster
echo.
echo Atualizacao automatica via WebSocket!
echo.
pause

start "" "https://gta-analytics-backend.fly.dev/strategist"

echo.
echo Dashboard aberto!
echo.
echo IMPORTANTE:
echo  - Funciona em PC, celular e tablet
echo  - Atualiza sozinho (nao precisa dar refresh)
echo  - Para Luis: envie este link no WhatsApp
echo.
echo URL para copiar e enviar:
echo https://gta-analytics-backend.fly.dev/strategist
echo.
pause
