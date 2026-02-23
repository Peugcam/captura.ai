@echo off
echo ====================================================================
echo   INSTALACAO DE METODOS ALTERNATIVOS DE CAPTURA
echo   GTA Analytics V2 - Anti-Block Solutions
echo ====================================================================
echo.

echo [1/4] Instalando MSS (Multi-Screen Screenshot)...
pip install mss
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar MSS
) else (
    echo OK: MSS instalado com sucesso
)
echo.

echo [2/4] Instalando D3DShot (DirectX Capture)...
pip install d3dshot
if %errorlevel% neq 0 (
    echo AVISO: Falha ao instalar D3DShot (pode requerer GPU dedicada)
) else (
    echo OK: D3DShot instalado com sucesso
)
echo.

echo [3/4] Instalando PyWin32 (Windows GDI)...
pip install pywin32
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar PyWin32
) else (
    echo OK: PyWin32 instalado com sucesso
)
echo.

echo [4/4] Verificando dependencias comuns...
pip install pillow keyboard websockets aiohttp
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias comuns
) else (
    echo OK: Dependencias comuns instaladas
)
echo.

echo ====================================================================
echo   INSTALACAO CONCLUIDA
echo ====================================================================
echo.
echo Proximo passo: Execute o teste para descobrir qual metodo funciona
echo.
echo   python testar-capturas.py
echo.
echo ====================================================================
pause
