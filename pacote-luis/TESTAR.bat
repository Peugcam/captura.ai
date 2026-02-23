@echo off
echo ====================================================================
echo   TESTE DO GTA ANALYTICS
echo ====================================================================
echo.
echo Requisitos:
echo  - OBS Studio aberto
echo  - WebSocket ativado (porta 4455)
echo  - Senha: ZNx3v4LjLVCgbTrO
echo.
echo O programa vai capturar por 10 segundos e mostrar estatisticas.
echo.
pause

echo.
echo Executando...
echo.

cd /d "%~dp0"
py gta-analytics-v2.py

pause
