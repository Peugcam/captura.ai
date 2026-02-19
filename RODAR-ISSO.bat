@echo off
echo ========================================
echo GTA Analytics - Envio para Nuvem
echo ========================================
echo.
echo Iniciando gateway local...
start "Gateway" cmd /k "cd gateway && gateway.exe -port=8000"
timeout /t 3 /nobreak > nul

echo.
echo Iniciando envio automatico para nuvem...
start "Send to Cloud" cmd /k ".venv\Scripts\python.exe send-to-cloud.py"

echo.
echo ========================================
echo PRONTO! Tudo funcionando!
echo ========================================
echo.
echo Dashboard: https://gta-analytics-v2.fly.dev/viewer
echo.
echo Mantenha essas janelas abertas enquanto usa!
echo.
pause
