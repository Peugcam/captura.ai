# 🚀 ATUALIZAR DASHBOARDS NO FLY.IO

## 📋 Situação Atual

**Dashboards locais (atualizados):**
- `backend/dashboard-player.html` (19 fev)
- `backend/dashboard-strategist-v2.html` (19 fev)
- `backend/dashboard-viewer.html` (19 fev)

**Fly.io:**
- Dashboard pode estar desatualizado
- Precisa fazer novo deploy para atualizar

---

## 🔧 OPÇÃO 1: Deploy Completo (RECOMENDADO)

### Passo a passo:

1. **Abra o terminal na pasta backend:**
```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\backend
```

2. **Verifique se está logado no Fly.io:**
```bash
flyctl auth whoami
```

Se não estiver logado:
```bash
flyctl auth login
```

3. **Faça o deploy:**
```bash
flyctl deploy
```

Isso vai:
- ✅ Construir nova imagem Docker
- ✅ Incluir os dashboards HTML atualizados
- ✅ Fazer deploy no Fly.io
- ✅ Atualizar o app automaticamente

**Tempo:** 3-5 minutos

---

## 🔧 OPÇÃO 2: Deploy Rápido (Só Backend)

Se só o backend mudou:

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\backend
flyctl deploy --ha=false
```

---

## 🔧 OPÇÃO 3: Verificar o Que Está Rodando

Antes de fazer deploy, verifique o que está no Fly.io:

```bash
# Ver logs do backend
flyctl logs -a gta-analytics-backend

# Ver status
flyctl status -a gta-analytics-backend

# Ver informações do app
flyctl info -a gta-analytics-backend
```

---

## ⚡ SCRIPT AUTOMÁTICO

Crie um arquivo `DEPLOY_BACKEND.bat`:

```batch
@echo off
echo ====================================================================
echo   DEPLOY BACKEND PARA FLY.IO
echo ====================================================================
echo.
echo Isso vai atualizar o backend no Fly.io com:
echo  - Dashboards HTML atualizados
echo  - Codigo Python mais recente
echo  - Todas as mudancas locais
echo.
echo Tempo estimado: 3-5 minutos
echo.
pause

cd /d "%~dp0"

echo.
echo [1/3] Verificando autenticacao...
flyctl auth whoami

if errorlevel 1 (
    echo.
    echo Nao esta logado! Fazendo login...
    flyctl auth login
)

echo.
echo [2/3] Iniciando deploy...
flyctl deploy

echo.
echo [3/3] Verificando status...
flyctl status -a gta-analytics-backend

echo.
echo ====================================================================
echo   DEPLOY CONCLUIDO
echo ====================================================================
echo.
echo Dashboards atualizados em:
echo  https://gta-analytics-backend.fly.dev/player
echo  https://gta-analytics-backend.fly.dev/viewer
echo  https://gta-analytics-backend.fly.dev/strategist
echo.
pause
```

---

## 🧪 TESTAR DEPOIS DO DEPLOY

Depois que o deploy terminar:

```bash
# 1. Verificar health
curl https://gta-analytics-backend.fly.dev/health

# 2. Testar dashboard
curl -I https://gta-analytics-backend.fly.dev/strategist

# 3. Abrir no navegador
start https://gta-analytics-backend.fly.dev/strategist
```

---

## ⚠️ PROBLEMAS COMUNS

### "flyctl: command not found"

**Solução:** Instale Fly.io CLI

```bash
# Windows (PowerShell como Admin)
iwr https://fly.io/install.ps1 -useb | iex
```

Ou baixe de: https://fly.io/docs/hands-on/install-flyctl/

### "Error: failed to fetch an image or build from source"

**Solução:**
1. Verifique se `Dockerfile` existe
2. Verifique conexão com internet
3. Tente novamente

### "Error: You are not signed in"

**Solução:**
```bash
flyctl auth login
```

---

## 📝 VERIFICAR O QUE VAI SER ENVIADO

Antes do deploy, veja o que mudou:

```bash
# Ver arquivos que serão incluídos
cat Dockerfile

# Ver configuração do Fly.io
cat fly.toml

# Listar arquivos HTML
ls -la *.html
```

---

## 🎯 RESUMO RÁPIDO

**Para atualizar dashboards no Fly.io:**

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\backend
flyctl deploy
```

**Aguarde 3-5 minutos e pronto!** ✅

Dashboards atualizados em:
- `https://gta-analytics-backend.fly.dev/strategist`

---

**Quer fazer o deploy agora?** Execute os comandos acima! 🚀
