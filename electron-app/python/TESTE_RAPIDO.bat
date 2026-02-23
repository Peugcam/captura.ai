@echo off
echo ================================================================
echo GTA ANALYTICS - TESTE RAPIDO COM VIDEO
echo ================================================================
echo.

REM Verifica se tem vídeo de teste
if not exist "test_video.mp4" (
    echo [AVISO] Nenhum video de teste encontrado
    echo.
    echo Opcoes:
    echo 1. Baixar video do YouTube com yt-dlp
    echo 2. Usar video existente
    echo.
    set /p VIDEO_PATH="Digite o caminho completo do video (ou ENTER para baixar): "

    if "%VIDEO_PATH%"=="" (
        echo.
        echo Instalando yt-dlp...
        pip install yt-dlp

        echo.
        echo Exemplos de videos bons:
        echo - GTA V Battle Royale gameplay
        echo - Videos com kill feed visivel
        echo.
        set /p YT_URL="Cole a URL do YouTube: "

        echo.
        echo Baixando video...
        yt-dlp -f "best[height<=720]" -o "test_video.mp4" "%YT_URL%"

        set VIDEO_PATH=test_video.mp4
    )
) else (
    echo [OK] Usando test_video.mp4
    set VIDEO_PATH=test_video.mp4
)

echo.
echo ================================================================
echo INICIANDO TESTE
echo ================================================================
echo Video: %VIDEO_PATH%
echo Server: https://gta-analytics-v2.fly.dev
echo FPS: 0.5 (1 frame a cada 2 segundos)
echo.
echo Pressione Ctrl+C para parar
echo ================================================================
echo.

REM Rodar script
C:\Users\paulo\AppData\Local\Programs\Python\Python313\python.exe capture_video.py ^
  --video "%VIDEO_PATH%" ^
  --server https://gta-analytics-v2.fly.dev ^
  --fps 0.5

echo.
echo ================================================================
echo TESTE FINALIZADO
echo ================================================================
echo.
echo Abra o dashboard para ver resultados:
echo https://gta-analytics-v2.fly.dev/strategist
echo.
pause
