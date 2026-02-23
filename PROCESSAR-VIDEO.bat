@echo off
echo ========================================
echo   PROCESSAR VIDEO COM GTA ANALYTICS
echo ========================================
echo.

REM Verificar se o video foi fornecido como argumento
if "%~1"=="" (
    echo ERRO: Voce precisa arrastar o video para este arquivo!
    echo.
    echo OU executar assim:
    echo PROCESSAR-VIDEO.bat "C:\caminho\para\video.mp4"
    echo.
    pause
    exit /b 1
)

set VIDEO_PATH=%~1
echo Video: %VIDEO_PATH%
echo.

REM Verificar se o arquivo existe
if not exist "%VIDEO_PATH%" (
    echo ERRO: Video nao encontrado!
    echo Caminho: %VIDEO_PATH%
    echo.
    pause
    exit /b 1
)

echo [OK] Video encontrado!
echo.
echo Iniciando processamento...
echo - FPS: 4 frames por segundo
echo - Qualidade: 85%%
echo.
echo Pressione Ctrl+C para cancelar
echo.
timeout /t 3 /nobreak

REM Executar captura de video
py captura-video.py --video "%VIDEO_PATH%" --fps 4 --quality 85

echo.
echo ========================================
echo   PROCESSAMENTO CONCLUIDO!
echo ========================================
echo.
echo Abra o dashboard para ver os resultados:
echo - dashboard-tournament.html
echo.
echo Ou exporte para Excel:
echo - curl http://localhost:3000/export ^> resultados.xlsx
echo.
pause
