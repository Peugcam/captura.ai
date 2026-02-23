@echo off
echo Abrindo Dashboard em Tempo Real...
echo.
echo O dashboard vai abrir no seu navegador padrao.
echo Aguarde alguns segundos para carregar os dados.
echo.

start "" "%~dp0dashboard-tempo-real.html"

echo.
echo Dashboard aberto!
echo.
echo O que voce vai ver:
echo  - Frames recebidos (atualizando em tempo real)
echo  - Frames processados
echo  - Kills detectadas
echo  - Times e jogadores rastreados
echo  - Eficiencia do filtro
echo.
echo Atualiza automaticamente a cada 2 segundos!
echo.
pause
