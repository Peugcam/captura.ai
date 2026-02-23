@echo off
title GTA Analytics V2 - Teste Completo
color 0A

echo ========================================
echo   GTA ANALYTICS V2 - TESTE COMPLETO
echo ========================================
echo.
echo Este script vai:
echo 1. Iniciar Gateway (porta 8000)
echo 2. Iniciar Backend (porta 3000)
echo 3. Aguardar voce processar um video
echo 4. Abrir o dashboard
echo.
echo Pressione qualquer tecla para comecar...
pause >nul

echo.
echo ========================================
echo   PASSO 1: Iniciando Gateway
echo ========================================
echo.
start "Gateway - Porta 8000" cmd /k "cd /d %~dp0gateway && gateway.exe -port=8000 -buffer=200 -webrtc=true -websocket=true -debug=true"

echo [OK] Gateway iniciado!
echo.
echo Aguardando 5 segundos...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   PASSO 2: Iniciando Backend
echo ========================================
echo.
start "Backend - Porta 3000" cmd /k "cd /d %~dp0backend && py main_websocket.py"

echo [OK] Backend iniciado!
echo.
echo Aguardando 10 segundos para o backend carregar...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   PASSO 3: Testando Conexoes
echo ========================================
echo.

echo Testando Gateway...
curl -s http://localhost:8000/health
if %ERRORLEVEL% EQU 0 (
    echo [OK] Gateway respondendo!
) else (
    echo [ERRO] Gateway nao respondeu
    echo Verifique a janela do Gateway
)
echo.

echo Testando Backend...
curl -s http://localhost:3000/health
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend respondendo!
) else (
    echo [ERRO] Backend nao respondeu
    echo Verifique a janela do Backend
)
echo.

echo ========================================
echo   SISTEMA PRONTO!
echo ========================================
echo.
echo Agora voce pode:
echo.
echo OPCAO 1 - Processar um video:
echo ----------------------------------
echo 1. Arraste seu video MP4 para o arquivo:
echo    PROCESSAR-VIDEO.bat
echo.
echo 2. OU execute no terminal:
echo    py captura-video.py --video "C:\caminho\video.mp4" --fps 4
echo.
echo.
echo OPCAO 2 - Abrir dashboard:
echo ----------------------------------
echo 1. Duplo clique em: ABRIR-DASHBOARD.bat
echo.
echo 2. OU abra manualmente: dashboard-tournament.html
echo.
echo.
echo OPCAO 3 - Ver estatisticas:
echo ----------------------------------
echo Gateway:  http://localhost:8000/stats
echo Backend:  http://localhost:3000/stats
echo.
echo.
echo ========================================
echo   INSTRUCOES
echo ========================================
echo.
echo Voce tem um video de GTA salvo?
echo.
echo [S] Sim - Vou processar um video
echo [N] Nao - Preciso gravar primeiro
echo.
choice /c SN /n /m "Escolha [S/N]: "

if %ERRORLEVEL% EQU 1 (
    echo.
    echo Otimo! Siga os passos:
    echo.
    echo 1. Abra a pasta onde esta seu video
    echo 2. Arraste o arquivo MP4 para: PROCESSAR-VIDEO.bat
    echo 3. Aguarde o processamento
    echo 4. Abra: ABRIR-DASHBOARD.bat
    echo.
    echo Ou digite o caminho do video agora:
    echo.
    set /p VIDEO_INPUT="Caminho do video: "

    if not "!VIDEO_INPUT!"=="" (
        echo.
        echo Processando: !VIDEO_INPUT!
        py captura-video.py --video "!VIDEO_INPUT!" --fps 4 --quality 85

        echo.
        echo Processamento concluido!
        echo Abrindo dashboard...
        start "" "%~dp0dashboard-tournament.html"
    )
) else (
    echo.
    echo Sem problemas! Voce pode:
    echo.
    echo 1. Gravar um gameplay no OBS
    echo 2. Ou baixar um video de exemplo do YouTube
    echo 3. Depois arraste o video para: PROCESSAR-VIDEO.bat
    echo.
)

echo.
echo ========================================
echo.
echo Gateway e Backend continuam rodando!
echo.
echo Feche as janelas quando terminar de testar.
echo.
pause
