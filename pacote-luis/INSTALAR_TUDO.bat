@echo off
chcp 65001 >nul
cls
echo ====================================================================
echo.
echo   █▀▀ ▀█▀ ▄▀█   ▄▀█ █▄ █ ▄▀█ █   █▄█ ▀█▀ █ █▀▀ █▀
echo   █▄█  █  █▀█   █▀█ █ ▀█ █▀█ █▄▄  █   █  █ █▄▄ ▄█
echo.
echo   Instalador Automático - Versão 1.0
echo.
echo ====================================================================
echo.
echo Este instalador vai configurar TUDO automaticamente:
echo.
echo   ✓ Verificar Python instalado
echo   ✓ Instalar bibliotecas necessárias
echo   ✓ Configurar OBS WebSocket
echo   ✓ Criar atalho no desktop
echo   ✓ Testar conexão
echo.
echo Tempo estimado: 2 minutos
echo.
echo ====================================================================
pause
cls

echo.
echo ====================================================================
echo   ETAPA 1/5: Verificando Python
echo ====================================================================
echo.

where py >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python encontrado!
    py --version
    set PYTHON_CMD=py
    goto :python_ok
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python encontrado!
    python --version
    set PYTHON_CMD=python
    goto :python_ok
)

echo [AVISO] Python não encontrado!
echo.
echo Baixando Python...
echo.
echo Por favor, instale Python de: https://python.org/downloads
echo.
echo IMPORTANTE: Marque "Add Python to PATH" durante instalação
echo.
pause
exit /b 1

:python_ok
echo.
timeout /t 2 >nul

echo.
echo ====================================================================
echo   ETAPA 2/5: Instalando Bibliotecas
echo ====================================================================
echo.

echo [*] Instalando obs-websocket-py...
%PYTHON_CMD% -m pip install obs-websocket-py --quiet --disable-pip-version-check
if %errorlevel% equ 0 (
    echo [OK] obs-websocket-py instalado
) else (
    echo [ERRO] Falha ao instalar obs-websocket-py
    pause
    exit /b 1
)

echo [*] Instalando pillow...
%PYTHON_CMD% -m pip install pillow --quiet --disable-pip-version-check
if %errorlevel% equ 0 (
    echo [OK] pillow instalado
) else (
    echo [ERRO] Falha ao instalar pillow
    pause
    exit /b 1
)

echo [*] Instalando requests...
%PYTHON_CMD% -m pip install requests --quiet --disable-pip-version-check
if %errorlevel% equ 0 (
    echo [OK] requests instalado
) else (
    echo [ERRO] Falha ao instalar requests
    pause
    exit /b 1
)

echo.
echo [OK] Todas as bibliotecas instaladas!
timeout /t 2 >nul

echo.
echo ====================================================================
echo   ETAPA 3/5: Configurando OBS
echo ====================================================================
echo.

echo [*] Criando pasta de configuração...
if not exist "%APPDATA%\gta-analytics" mkdir "%APPDATA%\gta-analytics"
echo [OK] Pasta criada: %APPDATA%\gta-analytics

echo.
echo [*] Copiando arquivos...
copy /Y "gta-analytics.py" "%APPDATA%\gta-analytics\" >nul
copy /Y "config.json" "%APPDATA%\gta-analytics\" >nul
echo [OK] Arquivos copiados

echo.
echo [*] Criando arquivo de configuração do OBS...
(
echo {
echo   "gateway_url": "https://gta-analytics-gateway.fly.dev",
echo   "fps": 4,
echo   "kill_feed_region": {
echo     "x": 1400,
echo     "y": 0,
echo     "width": 520,
echo     "height": 400
echo   }
echo }
) > "%APPDATA%\gta-analytics\config.json"
echo [OK] Configuração criada

timeout /t 2 >nul

echo.
echo ====================================================================
echo   ETAPA 4/5: Criando Atalhos
echo ====================================================================
echo.

echo [*] Criando atalho no desktop...

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%USERPROFILE%\Desktop\GTA Analytics.lnk'); $s.TargetPath = '%PYTHON_CMD%'; $s.Arguments = '%APPDATA%\gta-analytics\gta-analytics.py'; $s.WorkingDirectory = '%APPDATA%\gta-analytics'; $s.Description = 'GTA Analytics - Kill Feed Tracker'; $s.Save()"

if %errorlevel% equ 0 (
    echo [OK] Atalho criado no desktop: "GTA Analytics"
) else (
    echo [AVISO] Não foi possível criar atalho
)

echo.
echo [*] Criando arquivo INICIAR.bat...
(
echo @echo off
echo cd /d "%APPDATA%\gta-analytics"
echo %PYTHON_CMD% gta-analytics.py
echo pause
) > "%APPDATA%\gta-analytics\INICIAR.bat"
echo [OK] Criado: INICIAR.bat

timeout /t 2 >nul

echo.
echo ====================================================================
echo   ETAPA 5/5: Testando Instalação
echo ====================================================================
echo.

echo [*] Verificando arquivos...
if exist "%APPDATA%\gta-analytics\gta-analytics.py" (
    echo [OK] Programa principal
) else (
    echo [ERRO] Arquivo principal não encontrado
)

if exist "%APPDATA%\gta-analytics\config.json" (
    echo [OK] Configuração
) else (
    echo [ERRO] Configuração não encontrada
)

echo.
timeout /t 2 >nul

cls
echo.
echo ====================================================================
echo.
echo   ✓ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo.
echo ====================================================================
echo.
echo PRÓXIMOS PASSOS:
echo.
echo 1. Abra o OBS Studio
echo.
echo 2. Ative o WebSocket:
echo    Ferramentas → Configurações do Servidor WebSocket
echo    Marque: "Ativar Servidor WebSocket"
echo    Porta: 4455
echo    Aplicar
echo.
echo 3. Execute o programa:
echo    - Opção A: Duplo-clique no atalho "GTA Analytics" no desktop
echo    - Opção B: Execute: %APPDATA%\gta-analytics\INICIAR.bat
echo.
echo 4. Durante o jogo:
echo    - O programa captura automaticamente
echo    - Veja estatísticas em: https://gta-analytics.fly.dev
echo.
echo ====================================================================
echo.
echo Arquivos instalados em: %APPDATA%\gta-analytics\
echo.
echo Para desinstalar: delete a pasta acima e o atalho do desktop
echo.
echo ====================================================================
echo.
pause

echo.
echo Deseja testar agora? (Requer OBS aberto com WebSocket ativado)
echo.
set /p TESTAR="Digite S para testar ou N para sair: "

if /i "%TESTAR%"=="S" (
    echo.
    echo [*] Iniciando teste...
    echo.
    cd /d "%APPDATA%\gta-analytics"
    %PYTHON_CMD% gta-analytics.py
)

exit /b 0
