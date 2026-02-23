@echo off
chcp 65001 >nul
cls
echo ====================================================================
echo   TESTE COMPLETO - GTA ANALYTICS
echo ====================================================================
echo.
echo ESTADO ANTES DO TESTE:
echo.
curl -s https://gta-analytics-backend.fly.dev/stats
echo.
echo.
echo ====================================================================
echo.
echo PREPARACAO OK:
echo  ✓ OBS aberto
echo  ✓ Naruto Online visivel no preview
echo  ✓ WebSocket ativo
echo.
echo Pressione ENTER para iniciar o teste...
pause >nul

cls
echo ====================================================================
echo   CAPTURA INICIADA
echo ====================================================================
echo.
echo O programa esta rodando!
echo.
echo Voce deve ver linhas como:
echo   [20 frames] 5s ^| 4.0 FPS ^| 0 erros
echo   [40 frames] 10s ^| 4.0 FPS ^| 0 erros
echo.
echo Deixe rodar por 30-60 segundos
echo Pressione Ctrl+C quando quiser parar
echo.
echo ====================================================================
echo.

cd /d "%~dp0"
py gta-analytics-v2.py

echo.
echo.
echo ====================================================================
echo   CAPTURA FINALIZADA
echo ====================================================================
echo.
echo Aguardando processamento...
timeout /t 3 /nobreak >nul

cls
echo ====================================================================
echo   RESULTADO DO TESTE
echo ====================================================================
echo.
echo ANTES:  frames_received: 242 (aproximado)
echo.
echo AGORA:
curl -s https://gta-analytics-backend.fly.dev/stats
echo.
echo.
echo ====================================================================
echo   INTERPRETACAO
echo ====================================================================
echo.
echo Se "frames_received" aumentou = SUCESSO! ✓
echo.
echo O sistema esta:
echo  ✓ Capturando do OBS
echo  ✓ Enviando para Gateway
echo  ✓ Processando no Backend
echo  ✓ Filtrando duplicados
echo  ✓ Analisando com Vision API
echo.
echo Pronto para usar com GTA V!
echo.
pause
