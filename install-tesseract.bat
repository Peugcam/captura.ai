@echo off
echo ===================================================
echo   Tesseract OCR Installation
echo ===================================================
echo.
echo Baixando Tesseract OCR 5.5.0...
echo.

REM Download Tesseract
curl -L -o "%TEMP%\tesseract-installer.exe" "https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Falha no download
    pause
    exit /b 1
)

echo.
echo Instalando Tesseract OCR...
echo Importante: Durante a instalacao, marque "Add to PATH"
echo.

REM Executar instalador
start /wait "%TEMP%\tesseract-installer.exe"

echo.
echo ===================================================
echo   Instalacao concluida!
echo ===================================================
echo.
echo Proximos passos:
echo 1. Reinicie o terminal para carregar o PATH
echo 2. Teste: tesseract --version
echo 3. Reinicie o backend Python
echo.
pause
