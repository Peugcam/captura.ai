# Script de instalação do Go para Windows
# Execute com: powershell -ExecutionPolicy Bypass -File install-go.ps1

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   GTA Analytics V2 - Instalador Go" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# URL do instalador Go (atualizar versão conforme necessário)
$goVersion = "1.21.6"
$goUrl = "https://go.dev/dl/go$goVersion.windows-amd64.msi"
$installerPath = "$env:TEMP\go-installer.msi"

Write-Host "1. Baixando Go $goVersion..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $goUrl -OutFile $installerPath -ErrorAction Stop
    Write-Host "   ✓ Download concluído!" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Erro ao baixar. Baixe manualmente de: https://go.dev/dl/" -ForegroundColor Red
    Write-Host "   Após instalar, execute: go version" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "2. Instalando Go..." -ForegroundColor Yellow
Write-Host "   (Uma janela de instalação vai abrir)" -ForegroundColor Gray

# Executar instalador
Start-Process msiexec.exe -ArgumentList "/i `"$installerPath`" /quiet /norestart" -Wait

Write-Host "   ✓ Instalação concluída!" -ForegroundColor Green
Write-Host ""

# Atualizar PATH na sessão atual
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "3. Verificando instalação..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

try {
    $goVersionOutput = & go version
    Write-Host "   ✓ $goVersionOutput" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Go instalado, mas PATH não atualizado nesta sessão." -ForegroundColor Yellow
    Write-Host "   Feche e abra um novo terminal, depois execute: go version" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Próximos passos:" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "1. Abra um NOVO terminal (PowerShell ou cmd)" -ForegroundColor White
Write-Host "2. Navegue até: cd gateway" -ForegroundColor White
Write-Host "3. Execute: go mod download" -ForegroundColor White
Write-Host "4. Execute: go run main.go websocket.go buffer.go" -ForegroundColor White
Write-Host ""
Write-Host "Documentação: QUICKSTART.md" -ForegroundColor Gray
Write-Host ""

# Limpar instalador temporário
Remove-Item $installerPath -ErrorAction SilentlyContinue
