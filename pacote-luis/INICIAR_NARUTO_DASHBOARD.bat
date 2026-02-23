@echo off
cls
echo ======================================================================
echo.
echo    NARUTO ANALYTICS - INICIANDO SISTEMA
echo.
echo ======================================================================
echo.
echo [1/2] Iniciando servidor web...
echo.

cd /d "%~dp0"

start "Naruto Server" cmd /k "py naruto-server.py"

timeout /t 3 /nobreak > nul

echo [2/2] Abrindo dashboard no navegador...
echo.

start http://localhost:8000/naruto-dashboard.html

echo.
echo ======================================================================
echo.
echo    SISTEMA INICIADO!
echo.
echo    Dashboard: http://localhost:8000/naruto-dashboard.html
echo.
echo    IMPORTANTE:
echo    - Deixe o servidor rodando (nao feche a janela preta)
echo    - Execute naruto-analytics.py em outro terminal
echo.
echo ======================================================================
echo.

pause
