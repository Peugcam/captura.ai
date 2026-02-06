@echo off
echo ================================================
echo   INSTALADOR GO - GTA Analytics V2
echo ================================================
echo.
echo O arquivo ja foi baixado em:
echo C:\Users\paulo\AppData\Local\Temp\go-installer.msi
echo.
echo Instalando Go (vai pedir permissao de admin)...
echo.

msiexec /i "C:\Users\paulo\AppData\Local\Temp\go-installer.msi" /qb

echo.
echo Aguardando instalacao...
timeout /t 5 /nobreak >nul
echo.
echo Verificando instalacao...

"C:\Program Files\Go\bin\go.exe" version 2>nul

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo   GO INSTALADO COM SUCESSO!
    echo ================================================
    echo.
    "C:\Program Files\Go\bin\go.exe" version
    echo.
    echo Proximo passo: test-gateway.bat
) else (
    echo.
    echo ================================================
    echo   AVISO: Go instalado mas PATH nao atualizado
    echo ================================================
    echo.
    echo Feche este terminal e abra um NOVO terminal
    echo Depois execute: go version
)

echo.
pause
