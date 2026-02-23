@echo off
echo ====================================================================
echo   GTA ANALYTICS - INSTALADOR DO PLUGIN OBS
echo ====================================================================
echo.
echo Este script vai instalar o plugin automaticamente no OBS Studio.
echo.
pause

echo.
echo [1/3] Localizando pasta de scripts do OBS...

set OBS_SCRIPTS=%APPDATA%\obs-studio\scripts

if not exist "%OBS_SCRIPTS%" (
    echo.
    echo Criando pasta de scripts: %OBS_SCRIPTS%
    mkdir "%OBS_SCRIPTS%"
)

echo OK: %OBS_SCRIPTS%
echo.

echo [2/3] Copiando plugin...

copy /Y "gta_analytics_plugin.py" "%OBS_SCRIPTS%\gta_analytics_plugin.py"

if %errorlevel% equ 0 (
    echo OK: Plugin copiado com sucesso!
) else (
    echo ERRO: Falha ao copiar plugin
    pause
    exit /b 1
)

echo.
echo [3/3] Instalacao concluida!
echo.
echo ====================================================================
echo   PROXIMO PASSO: ATIVAR NO OBS
echo ====================================================================
echo.
echo 1. Abra o OBS Studio
echo 2. Va em: Ferramentas ^> Scripts
echo 3. Clique no botao "+" (Adicionar)
echo 4. Selecione: gta_analytics_plugin.py
echo 5. Configure a URL do Gateway
echo 6. Clique em "Testar Conexao"
echo 7. Pronto!
echo.
echo O plugin vai rodar automaticamente em segundo plano.
echo.
echo ====================================================================
pause
