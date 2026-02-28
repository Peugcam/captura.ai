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
  OPENAI_API_KEY="your_openai_api_key_here" \
  OPENROUTER_API_KEY="your_openrouter_api_key_here" \
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

## 🏆 Por Que Fly.io? Análise Comparativa

### Comparação com Outras Plataformas

| Critério | Fly.io | Railway | Render | GCP Run | AWS Fargate |
|----------|---------|---------|--------|---------|-------------|
| **Região São Paulo** | ✅ GRU | ❌ | ❌ | ✅ | ✅ |
| **Latência Brasil** | <10ms | 150-200ms | 150-200ms | <10ms | <10ms |
| **WebSocket Nativo** | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| **Multi-Container** | ✅ Excelente | ⚠️ | ✅ | ✅ | ✅ |
| **Custo (10 partidas)** | $7-13 | $21-36 | $30-59 | $18-33 | $40-65 |
| **Custo (50 partidas)** | $55-90 | $131-211 | $146-241 | $90-145 | $190-330 |
| **Unix Sockets** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Edge Network** | ✅ Anycast | ❌ | ❌ | ✅ | ✅ |

### Veredito: **Fly.io é a melhor escolha** ✅

**Motivos:**
1. **Latência crítica:** São Paulo (GRU) < 10ms vs 150-200ms competidores sem SA
2. **Custo-benefício:** 2-4x mais barato que alternativas
3. **Simplicidade:** Multi-service deployment nativo
4. **Escalabilidade:** Anycast global se expandir para fora do Brasil

---

## 💰 Análise Detalhada de Custos

### Cenário 1: 10 Partidas Simultâneas

**Infraestrutura (Fly.io):**
| Componente | Recursos | Custo/Mês |
|------------|----------|-----------|
| Gateway | 1 CPU, 512MB | $0 (free tier) |
| Backend | 2 CPUs, 2GB | $7 |
| Storage | 5GB volume | $0.75 |
| Bandwidth | ~100GB | $2 |
| **Total Infra** | | **$9.75** |

**API Costs (com otimizações NASA):**
- Frames/hora: 14,400 × 10 = 144,000
- Após dedup + filtros: 95% redução = ~7,200 processados
- Tokens: 19.7M tokens × 10 = 197M/mês
- Custo GPT-4o: $0.30/hora × 10 = $3/hora = **$2,160/mês**
- **Com Gemini Flash (90% cheaper): $216/mês**

**Total Cenário 1:**
- Infra + API (Gemini): **$226/mês**
- Otimizações adicionais: **~$45-60/mês** (80% redução)

### Cenário 2: 50 Partidas Simultâneas

**Infraestrutura (Fly.io):**
| Componente | Recursos | Custo/Mês |
|------------|----------|-----------|
| Gateway | 2×(2 CPU, 1GB) | $15 |
| Backend | 3×(4 CPU, 4GB) | $60 |
| Storage | 20GB volume | $3 |
| Bandwidth | ~500GB | $10 |
| **Total Infra** | | **$88** |

**API Costs (com otimizações):**
- Com Gemini Flash: **$1,080/mês**
- Otimizações adicionais: **~$230-300/mês** (80% redução)

**Total Cenário 2: $318-388/mês**

### Estratégias de Redução de Custos

**Prioridade Alta (já implementadas):**
1. ✅ **Gemini Flash 2.0 Fallback** → 90% redução (já ativo)
2. ✅ **Frame Deduplication** → 70% redução (já ativo)
3. ✅ **Vision Pre-Filter** → 60% frames filtrados (já ativo)
4. ✅ **ROI Cropping** → 75% tokens reduzidos (já ativo)
5. ✅ **Kill Grouping** → 20% economia (já ativo)

**Efeito combinado:** 99.5% de redução vs sem otimizações

**Próximas Otimizações:**
- [ ] Aumentar `FRAME_SKIP_INTERVAL=3` (33% economia adicional)
- [ ] Implementar LRU cache para Vision API (10-15% economia)
- [ ] Usar Gemini como primário (não fallback)

---

## 📈 Recomendações de Recursos por Escala

### Fase 1: Início (1-10 partidas)

**Gateway:**
```toml
[vm]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512  # Aumentado para segurança
```

**Backend:**
```toml
[vm]
  cpu_kind = "shared"
  cpus = 2
  memory_mb = 2048  # Aumentado para OCR workers

[env]
  OCR_WORKERS = "8"
```

**Quando escalar:** CPU >70% ou Memory >80% por 15min

---

### Fase 2: Crescimento (10-30 partidas)

**Gateway - Escalar horizontalmente:**
```bash
fly scale count 2 --app gta-analytics-gateway
```

**Backend - Aumentar recursos:**
```bash
fly scale vm shared-cpu-4x --app gta-analytics-backend
# OU escalar horizontalmente:
fly scale count 2 --app gta-analytics-backend
```

**Adicionar Redis para session state:**
```bash
fly redis create --name gta-redis --region gru
# Atualizar GATEWAY_URL para usar Redis pub/sub
```

**Custo adicional:** +$5-10/mês (Redis)

---

### Fase 3: Alto Volume (30-50 partidas)

**Gateway:**
```toml
[vm]
  cpu_kind = "shared"
  cpus = 2
  memory_mb = 1024
```

**Backend (3 instâncias):**
```bash
fly scale count 3 --app gta-analytics-backend
fly scale vm shared-cpu-4x --app gta-analytics-backend

# Atualizar .env
OCR_WORKERS=16
```

**Adicionar PostgreSQL para analytics histórico:**
```bash
fly postgres create --name gta-analytics-db --region gru
```

**Custo adicional:** +$10-25/mês (Postgres)

---

### Fase 4: Escala Global (50+ partidas)

**Deploy multi-região:**
```toml
primary_region = "gru"  # São Paulo
regions = ["gru", "scl"]  # Santiago como backup
```

**Auto-scaling (quando disponível):**
```bash
fly autoscale set \
  --app gta-analytics-backend \
  --min 3 \
  --max 10 \
  --balance-regions \
  --metric cpu \
  --value 70
```

**Considerar:**
- Cloudflare CDN para dashboards (free tier)
- Load balancer dedicado
- Migrar para AWS/GCP se >200 partidas

---

## ⚡ Checklist de Otimização de Performance

### Rede

- [x] **Região São Paulo (GRU)** - Latência <10ms
- [x] **Unix Sockets** para IPC Gateway↔Backend
- [ ] **HTTP/2** habilitado (verificar)
- [x] **WebSocket sem compressão** (correto para binary)
- [ ] **Connection pooling** para Vision API
- [x] **Anycast routing** (Fly.io automático)

### Memória

- [x] **Ring buffer com drop policy** (Gateway)
- [x] **Frame deduplication** (95% threshold)
- [ ] **LRU cache** para Vision API responses (implementar)
- [x] **Limit WebSocket connections** (100 max)
- [ ] **Memory profiling** (`memory_profiler`)
- [ ] **GC tuning** (Go: GOGC=100, Python: gc.collect())

### CPU

- [x] **OCR thread pool** (8 workers async)
- [x] **Async I/O** para Vision API (httpx.AsyncClient)
- [x] **Frame skip** (processar 50%)
- [ ] **CPU profiling** (`go tool pprof` + `py-spy`)
- [ ] **Otimizar image preprocessing** (NumPy vectorization)
- [ ] **GPU acceleration** (considerar para >100 partidas)

### Caching

**Implementar API Response Cache:**
```python
# Adicionar em processor.py
from cachetools import TTLCache

vision_cache = TTLCache(maxsize=100, ttl=300)  # 5min TTL

def process_frame_cached(frame):
    frame_hash = hash_frame(frame)
    if frame_hash in vision_cache:
        return vision_cache[frame_hash]
    result = process_frame(frame)
    vision_cache[frame_hash] = result
    return result
```

**Economia esperada:** 10-15% de API calls

---

## 📊 Monitoramento e Observabilidade

### Métricas Críticas

**Infraestrutura:**
- CPU utilization (target: <70% média)
- Memory usage (target: <80% alocado)
- Network throughput (ingress/egress)
- Disk I/O (volume exports)

**Aplicação:**
- Frames received/segundo (Gateway)
- Frames processed/segundo (Backend)
- Frame drop rate (target: <5%)
- WebSocket connections count
- OCR processing latency
- Vision API latency
- Kill detection rate (target: >85%)

**Negócio:**
- Partidas ativas
- Total kills detectados
- API tokens consumidos
- Custo por partida
- User satisfaction (dashboard responsiveness)

### Ferramentas Recomendadas

**Fly.io Built-in (Grátis):**
```bash
# Métricas em tempo real
fly dashboard --app gta-analytics-backend

# Logs
fly logs --app gta-analytics-backend -f

# SSH para debug
fly ssh console --app gta-analytics-backend
```

**Grafana Cloud (Free tier - Recomendado):**
```toml
# Adicionar em fly.toml
[metrics]
  port = 9091
  path = "/metrics"
```

**Setup:**
1. Criar conta Grafana Cloud (grátis)
2. Instalar Prometheus exporter no Backend
3. Configurar remote_write para Grafana
4. Importar dashboard template

**Custo:** Free tier cobre <50k metrics/mês

**Better Stack (Logs - Opcional):**
```python
# backend/main_websocket.py
from logtail import LogtailHandler

handler = LogtailHandler(source_token="your_token")
logger.addHandler(handler)
```

**Custo:** Free tier cobre 1GB logs/mês

**Sentry (Erro tracking - Recomendado):**
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your_dsn",
    environment="production",
    traces_sample_rate=0.1
)
```

**Custo:** Free tier cobre 5k events/mês

### Alertas

**Críticos (PagerDuty/Slack):**
- ❌ Backend service down (health check fails)
- ❌ Gateway service down
- ⚠️ CPU >90% por 5 minutos
- ⚠️ Memory >95% por 2 minutos
- ⚠️ Frame drop rate >20%
- ⚠️ API error rate >10%

**Warnings (Email):**
- 📧 CPU >70% por 15 minutos
- 📧 Memory >80% por 10 minutos
- 📧 Frame drop rate >10%
- 📧 Disk usage >80%
- 📧 API cost >$100/dia (spike inesperado)

**Info (Dashboard):**
- ℹ️ Nova partida iniciada
- ℹ️ Export gerado
- ℹ️ Service deployed
- ℹ️ Config alterada

---

## 🔄 Quando Considerar Outras Plataformas

**Migrar APENAS se:**

1. **Expansão significativa fora da América do Sul** (100+ partidas globais)
   - Considerar: AWS Fargate multi-região
   - Custo: 2-3x mais caro, mas melhor latência global

2. **Custo excede $500/mês consistentemente**
   - Considerar: GCP Run ou Kubernetes customizado
   - Economia: ~20-30% em alta escala

3. **Necessidade de features avançadas de database**
   - Adicionar: PostgreSQL managed (pode manter Fly.io)
   - Ou migrar para: AWS RDS/Aurora

4. **Compliance/Certificações empresariais**
   - Migrar para: AWS/GCP para enterprise SLAs
   - Custo: Significativamente maior

**Veredito atual:** Fly.io é ótimo para 0-200 partidas simultâneas

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
