@echo off
echo ================================================================
echo GTA ANALYTICS - TESTE COMPLETO
echo ================================================================
echo.
echo Este script vai:
echo 1. Criar um video de teste sintetico
echo 2. Enviar frames para o backend
echo 3. Mostrar resultados
echo.
echo Pressione qualquer tecla para continuar...
pause > nul

echo.
echo [1/3] Criando video de teste...
echo ================================================================
C:\Users\paulo\AppData\Local\Programs\Python\Python313\python.exe criar_video_teste.py

if not exist "test_gta_synthetic.mp4" (
    echo.
    echo [ERRO] Falha ao criar video!
    pause
    exit /b 1
)

echo.
echo [2/3] Iniciando envio de frames...
echo ================================================================
echo.
echo Dashboard: https://gta-analytics-v2.fly.dev/strategist
echo.
echo Abra o dashboard no navegador para ver resultados em tempo real!
echo.
timeout /t 3

echo Iniciando captura em 3 segundos...
timeout /t 3

C:\Users\paulo\AppData\Local\Programs\Python\Python313\python.exe capture_video.py ^
  --video test_gta_synthetic.mp4 ^
  --server https://gta-analytics-v2.fly.dev ^
  --fps 1.0

echo.
echo [3/3] Teste finalizado!
echo ================================================================
echo.
echo Verificar resultados:
echo 1. Abra: https://gta-analytics-v2.fly.dev/strategist
echo 2. Veja kills detectados
echo 3. Confira scoreboard
echo.
echo Video de teste: test_gta_synthetic.mp4 (pode deletar depois)
echo.
pause
