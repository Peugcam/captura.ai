# GTA Analytics V2 - Guia de Deploy para Fly.io

## 📋 Pré-requisitos

- ✅ Sistema testado localmente (CONCLUÍDO)
- ✅ Docker instalado (para build)
- ⏳ Fly CLI (vamos instalar agora)
- ⏳ Conta Fly.io (gratuita)

---

## 🚀 Passo 1: Instalar Fly CLI

### Windows (PowerShell como Administrador):

```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

Ou baixar direto: https://fly.io/docs/hands-on/install-flyctl/

Após instalar, **reinicie o terminal** e teste:

```bash
fly version
```

---

## 🔐 Passo 2: Criar Conta e Fazer Login

```bash
# Criar conta (abre navegador)
fly auth signup

# Ou fazer login se já tem conta
fly auth login
```

**IMPORTANTE:** Fly.io free tier requer cartão de crédito, mas:
- Não cobra se ficar dentro do free tier
- Free tier: 3 VMs shared-cpu-1x (256MB RAM cada)
- Nosso setup usa 2 VMs: Gateway (256MB) + Backend (1GB)
- **Custo estimado:** ~$0-5/mês (dentro do free tier)

---

## 📦 Passo 3: Criar Apps no Fly.io

### 3.1 - Criar Gateway App

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\gateway

# Criar app (escolha nome único)
fly apps create gta-analytics-gateway

# Ou deixar Fly.io gerar nome automaticamente
fly apps create

# Anotar o nome gerado (ex: gta-analytics-gateway-wispy-cloud-1234)
```

### 3.2 - Criar Backend App

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\backend

# Criar app
fly apps create gta-analytics-backend

# Criar volume para exports
fly volumes create gta_exports --region gru --size 1 --app gta-analytics-backend
```

---

## 🔑 Passo 4: Configurar Secrets (API Keys)

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\backend

# Configurar API keys como secrets
fly secrets set \
  OPENAI_API_KEY="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" \
  OPENROUTER_API_KEY="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" \
  --app gta-analytics-backend

# Verificar secrets configurados
fly secrets list --app gta-analytics-backend
```

---

## 🌍 Passo 5: Atualizar Configurações (fly.toml)

### 5.1 - Atualizar Gateway fly.toml

Edite `gateway/fly.toml` e ajuste o nome do app:

```toml
app = "gta-analytics-gateway"  # Use o nome criado no Passo 3.1
primary_region = "gru"
```

### 5.2 - Atualizar Backend fly.toml

Edite `backend/fly.toml` e ajuste:

```toml
app = "gta-analytics-backend"  # Use o nome criado no Passo 3.2
primary_region = "gru"

[env]
  # Ajuste para apontar para o Gateway interno
  GATEWAY_URL = "http://gta-analytics-gateway.internal:8000"
  GATEWAY_IPC_MODE = "unix"  # Usar Unix Socket no Linux (Fly.io)
  # ... resto das configs
```

---

## 🚢 Passo 6: Deploy

### 6.1 - Deploy Gateway

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\gateway

# Build e deploy
fly deploy --ha=false

# Aguardar build (2-3 minutos)
# Output esperado:
# ✓ Building image
# ✓ Pushing image
# ✓ Deploying
# ✓ Health checks passing
```

**Verificar deployment:**

```bash
fly status --app gta-analytics-gateway
fly logs --app gta-analytics-gateway
```

URL pública: `https://gta-analytics-gateway.fly.dev`

### 6.2 - Deploy Backend

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\backend

# Build e deploy
fly deploy --ha=false

# Aguardar build (3-5 minutos - Tesseract + deps Python)
```

**Verificar deployment:**

```bash
fly status --app gta-analytics-backend
fly logs --app gta-analytics-backend
```

URL pública: `https://gta-analytics-backend.fly.dev`

---

## ✅ Passo 7: Testar Cloud Deployment

### 7.1 - Testar Gateway Cloud

```bash
# Health check
curl https://gta-analytics-gateway.fly.dev/health

# Stats
curl https://gta-analytics-gateway.fly.dev/stats
```

### 7.2 - Testar Backend Cloud

```bash
# Stats
curl https://gta-analytics-backend.fly.dev/stats
```

### 7.3 - Testar WebRTC Cloud

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2

# Teste de conexão WebRTC
python test_webrtc_connection.py --gateway https://gta-analytics-gateway.fly.dev
```

### 7.4 - Captura de Frames Cloud

```bash
# Capturar frames e enviar para cloud
python captura-webrtc.py \
  --gateway https://gta-analytics-gateway.fly.dev \
  --fps 4 \
  --quality 85 \
  --duration 120
```

---

## 📊 Passo 8: Monitoramento

### Ver Logs em Tempo Real

```bash
# Gateway
fly logs --app gta-analytics-gateway -f

# Backend
fly logs --app gta-analytics-backend -f
```

### Métricas

```bash
# Dashboard Fly.io
fly dashboard --app gta-analytics-backend

# Abrir no navegador
https://fly.io/apps/gta-analytics-backend
```

### SSH no Container

```bash
# Gateway
fly ssh console --app gta-analytics-gateway

# Backend
fly ssh console --app gta-analytics-backend
```

---

## 🔄 Passo 9: Atualizações

Quando fizer mudanças no código:

```bash
# Rebuild e redeploy Gateway
cd gateway
fly deploy

# Rebuild e redeploy Backend
cd backend
fly deploy
```

Fly.io faz **zero-downtime deployment** automaticamente!

---

## 💰 Custos Estimados

### Free Tier (Fly.io)

- **Recursos inclusos:**
  - 3 shared-cpu-1x VMs (256MB RAM)
  - 3GB persistent volumes
  - 160GB outbound data transfer

### Nosso Setup

- **Gateway:** 1 VM (256MB) = $0 (dentro do free tier)
- **Backend:** 1 VM (1GB) = ~$5/mês (excede free tier)
- **Volume:** 1GB = $0.15/mês
- **Bandwidth:** Depende do uso (~$0.02/GB após 160GB)

**Total estimado:** **$5-10/mês**

### Economia com Together AI

Se adicionar Together AI (Llama-3.2-Vision):

- **Custo Vision API:**
  - Antes: $2.50/1M tokens (GPT-4o)
  - Depois: $0.30/1M tokens (Llama)
  - **Economia:** $2.20/1M tokens (88%)

Para 1M frames/mês:
- **Economia:** ~$2,000/mês
- **Custo infra Fly.io:** ~$10/mês
- **ROI:** 200x

---

## 🐛 Troubleshooting

### Gateway não inicia

```bash
fly logs --app gta-analytics-gateway

# Verificar:
# - Build completo?
# - Ports expostos (8000)?
# - Health check passando?
```

### Backend não conecta ao Gateway

Verifique `GATEWAY_URL` no `backend/fly.toml`:

```toml
GATEWAY_URL = "http://gta-analytics-gateway.internal:8000"
```

O `.internal` é importante para comunicação privada entre apps.

### WebRTC não conecta

- Verifique se ports UDP estão abertos (50000-50100)
- Teste de rede local primeiro
- STUN server acessível?

### Volume não montado

```bash
# Listar volumes
fly volumes list --app gta-analytics-backend

# Criar se não existir
fly volumes create gta_exports --region gru --size 1
```

---

## 🎯 Próximos Passos Após Deploy

1. **Teste com GTA rodando**
   - Conecte ao cloud: `python captura-webrtc.py --gateway https://...`
   - Verifique kills detectadas

2. **Configure domínio customizado** (opcional)
   ```bash
   fly certs add gta-analytics.seudominio.com --app gta-analytics-backend
   ```

3. **Setup monitoramento** (opcional)
   - Grafana Cloud integration
   - Prometheus metrics

4. **Adicione Together AI** para reduzir custos
   - Crie conta: https://api.together.xyz/
   - Adicione key: `fly secrets set TOGETHER_API_KEY=xxx`
   - Habilite: `USE_LITELLM=true` no `.env`

---

## 📝 Comandos Úteis

```bash
# Ver apps
fly apps list

# Ver status
fly status --app gta-analytics-gateway

# Escalar
fly scale count 2 --app gta-analytics-backend

# Pausar (economizar)
fly scale count 0 --app gta-analytics-gateway

# Destruir app
fly apps destroy gta-analytics-gateway --yes
```

---

## ✅ Checklist Final

- [ ] Fly CLI instalado
- [ ] Conta Fly.io criada
- [ ] Apps criados (Gateway + Backend)
- [ ] Secrets configurados
- [ ] Gateway deployed
- [ ] Backend deployed
- [ ] Health checks passando
- [ ] WebRTC testado
- [ ] Captura de frames cloud funcionando
- [ ] Dashboard conectado
- [ ] Exports funcionando

---

**Pronto para deploy!** 🚀

Siga os passos na ordem e qualquer erro, consulte a seção Troubleshooting.

**Suporte:** https://community.fly.io/
