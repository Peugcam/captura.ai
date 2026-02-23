@echo off
echo ====================================================================
echo   TESTE COM QUALQUER JOGO
echo ====================================================================
echo.
echo INSTRUCOES:
echo.
echo 1. Abra o OBS Studio
echo 2. Configure uma fonte de captura (Captura de Jogo ou Janela)
echo 3. Deixe o jogo visivel no OBS
echo 4. Execute este arquivo
echo.
echo O programa vai capturar por 30 segundos e mostrar estatisticas.
echo Voce podera ver:
echo  - Quantos frames foram capturados
echo  - Quantos foram enviados para o backend
echo  - Se houve erros de conexao
echo.
echo Nao precisa ter kills! So queremos ver se funciona.
echo.
pause

echo.
echo ====================================================================
echo   INICIANDO CAPTURA (30 segundos)
echo ====================================================================
echo.

cd /d "%~dp0"
timeout /t 30 /nobreak >nul 2>&1 & py gta-analytics-v2.py

echo.
echo ====================================================================
echo   TESTE CONCLUIDO
echo ====================================================================
echo.
echo Agora vamos verificar as estatisticas do backend...
echo.
pause

echo.
echo Consultando backend...
echo.
curl https://gta-analytics-backend.fly.dev/stats
echo.
echo.
echo ====================================================================
echo   INTERPRETACAO DOS RESULTADOS
echo ====================================================================
echo.
echo frames_received   = Quantos frames o backend recebeu
echo frames_filtered   = Quantos foram descartados (duplicados)
echo frames_processed  = Quantos foram analisados pela Vision API
echo kills_detected    = Kills detectadas (pode ser 0 se nao for GTA)
echo.
echo Se frames_received estiver aumentando = FUNCIONANDO!
echo.
pause
