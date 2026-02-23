@echo off
chcp 65001 >nul
cls
echo ====================================================================
echo   DEPLOY BACKEND PARA FLY.IO
echo ====================================================================
echo.
echo Isso vai atualizar o backend no Fly.io com:
echo  ✓ Dashboards HTML atualizados
echo  ✓ Código Python mais recente
echo  ✓ Todas as mudanças locais
echo.
echo Tempo estimado: 3-5 minutos
echo.
echo IMPORTANTE: Você precisa ter o Fly.io CLI instalado!
echo.
pause

cd /d "%~dp0"

echo.
echo ====================================================================
echo   [1/4] Verificando autenticação Fly.io...
echo ====================================================================
echo.
flyctl auth whoami

if errorlevel 1 (
    echo.
    echo ❌ Não está logado no Fly.io!
    echo.
    echo Abrindo navegador para fazer login...
    flyctl auth login

    if errorlevel 1 (
        echo.
        echo ❌ Login falhou!
        echo.
        echo SOLUÇÃO:
        echo  1. Instale Fly.io CLI: https://fly.io/docs/hands-on/install-flyctl/
        echo  2. Execute novamente este script
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ✓ Autenticado com sucesso!

echo.
echo ====================================================================
echo   [2/4] Verificando arquivos...
echo ====================================================================
echo.

if not exist "dashboard-player.html" (
    echo ❌ dashboard-player.html não encontrado!
    pause
    exit /b 1
)

if not exist "dashboard-strategist-v2.html" (
    echo ❌ dashboard-strategist-v2.html não encontrado!
    pause
    exit /b 1
)

if not exist "Dockerfile" (
    echo ❌ Dockerfile não encontrado!
    pause
    exit /b 1
)

echo ✓ dashboard-player.html
echo ✓ dashboard-strategist-v2.html
echo ✓ dashboard-viewer.html
echo ✓ Dockerfile
echo ✓ fly.toml
echo.
echo Todos os arquivos encontrados!

echo.
echo ====================================================================
echo   [3/4] Fazendo deploy...
echo ====================================================================
echo.
echo Isso pode demorar alguns minutos...
echo.

flyctl deploy -a gta-analytics-backend

if errorlevel 1 (
    echo.
    echo ❌ Deploy falhou!
    echo.
    echo Verifique os erros acima e tente novamente.
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo   [4/4] Verificando status...
echo ====================================================================
echo.

flyctl status -a gta-analytics-backend

echo.
echo ====================================================================
echo   ✅ DEPLOY CONCLUÍDO COM SUCESSO
echo ====================================================================
echo.
echo Dashboards atualizados e disponíveis em:
echo.
echo  🎮 Dashboard do Jogador:
echo     https://gta-analytics-backend.fly.dev/player
echo.
echo  📊 Dashboard do Estrategista (PRINCIPAL):
echo     https://gta-analytics-backend.fly.dev/strategist
echo.
echo  👁️  Dashboard do Espectador:
echo     https://gta-analytics-backend.fly.dev/viewer
echo.
echo  📈 Stats API:
echo     https://gta-analytics-backend.fly.dev/stats
echo.
echo ====================================================================
echo.
echo Testando dashboard principal...
echo.

timeout /t 5 /nobreak >nul

start "" "https://gta-analytics-backend.fly.dev/strategist"

echo.
echo Dashboard aberto no navegador!
echo.
pause
