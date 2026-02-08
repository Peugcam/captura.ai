@echo off
echo ===================================================
echo   GTA Analytics V2 - Live Screen Capture
echo ===================================================
echo.
echo Certifique-se que o sistema esta rodando:
echo   - Go Gateway (porta 8000)
echo   - Python Backend
echo.
echo Se nao estiver, execute: start-system.bat
echo.
pause

cd /d "%~dp0"
"C:\Users\paulo\AppData\Local\Programs\Python\Python313\python.exe" capture-live.py

pause
