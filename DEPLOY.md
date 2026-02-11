# 🚀 Guia de Deploy - GTA Analytics V2

Sistema de análise de kill feed em tempo real para GTA V Battle Royale.

**Cliente:** Luis Otavio
**Repositório:** https://github.com/Peugcam/captura.ai

---

## 📊 Orçamento Mensal (1 Torneio/Mês)

### Cenário Produção (Recomendado)
```
Infrastructure:
├─ Fly.io (VM 1GB, 1 vCPU)......... $15-20/mês
├─ Domínio personalizado........... $1/mês
└─ Certificado SSL................. Grátis (Let's Encrypt)

Vision API (1 torneio × 20 partidas):
├─ OpenAI GPT-4o................... $32.40/mês
└─ OU OpenRouter GPT-4o............ $21.60/mês (33% mais barato)

TOTAL: $48-53/mês (~R$ 240-265/mês)
```

### Cenário Econômico
```
Infrastructure:
├─ Fly.io (VM 512MB)............... $5-8/mês
└─ Domínio......................... $1/mês

Vision API (GPT-4o mini):
└─ Custo reduzido.................. $10/mês

TOTAL: $16-19/mês (~R$ 80-95/mês)
```

---

## 🔧 Pré-requisitos

1. **Conta Fly.io**
   ```bash
   # Instalar Fly CLI
   curl -L https://fly.io/install.sh | sh

   # Autenticar
   flyctl auth login
   ```

2. **OpenAI API Key**
   - Criar conta em: https://platform.openai.com
   - Gerar API key em: https://platform.openai.com/api-keys
   - Adicionar créditos (mínimo $5)

3. **OpenRouter API Key (Opcional - Mais barato)**
   - Criar conta em: https://openrouter.ai
   - Gerar API key em: https://openrouter.ai/keys
   - Adicionar créditos

---

## 📦 Deploy no Fly.io

### Passo 1: Configurar Variáveis de Ambiente

```bash
# Navegar para o projeto
cd gta-analytics-v2

# Configurar secrets no Fly.io
flyctl secrets set OPENAI_API_KEY="sk-..." \
                   VISION_MODEL="gpt-4o" \
                   VISION_PRE_FILTER="true" \
                   USE_ROI="false" \
                   OCR_PRE_FILTER="false"

# (Opcional) Usar OpenRouter em vez de OpenAI
flyctl secrets set OPENROUTER_API_KEY="sk-or-..." \
                   VISION_MODEL="gpt-4o"
```

### Passo 2: Criar Volume Persistente

```bash
# Criar volume para exports de Excel
flyctl volumes create gta_analytics_data \
  --region gru \
  --size 1
```

### Passo 3: Deploy da Aplicação

```bash
# Deploy inicial (criar app)
flyctl launch --no-deploy

# Responder:
# - App name: gta-analytics-v2 (ou nome customizado)
# - Region: gru (São Paulo)
# - PostgreSQL: No
# - Redis: No

# Deploy
flyctl deploy

# Aguardar deploy concluir
# ✅ Sistema estará disponível em: https://gta-analytics-v2.fly.dev
```

### Passo 4: Verificar Deployment

```bash
# Ver status da aplicação
flyctl status

# Ver logs em tempo real
flyctl logs

# Testar health check
curl https://gta-analytics-v2.fly.dev/health
```

---

## 🌐 Acessar Dashboard

Após deploy bem-sucedido:

1. **Dashboard OBS**: `https://gta-analytics-v2.fly.dev/dashboard-obs.html`
2. **API Backend**: `https://gta-analytics-v2.fly.dev/api/`
3. **WebSocket Events**: `wss://gta-analytics-v2.fly.dev/events`

---

## 📱 Uso do Sistema

### Para o Suporte do Luis

1. **Abrir Dashboard**
   - Acessar: `https://gta-analytics-v2.fly.dev/dashboard-obs.html`

2. **Capturar Stream Discord**
   - Clicar em "Iniciar Captura"
   - Selecionar janela do Discord (compartilhamento de tela)
   - Confirmar compartilhamento

3. **Monitorar Partida**
   - Centro: Preview do jogo
   - Esquerda: Kill feed em tempo real
   - Direita: Ranking de jogadores

4. **Exportar Resultados**
   - Clicar em "Exportar Excel"
   - Baixar arquivo `kill_feed_[timestamp].xlsx`
   - Planilha contém 3 abas:
     - **VIVOS**: Jogadores vivos por time
     - **RANKING**: Top jogadores por kills
     - **KILL FEED**: Histórico completo

---

## 🔍 Monitoramento

### Ver Logs
```bash
# Logs em tempo real
flyctl logs

# Últimas 100 linhas
flyctl logs --count 100

# Filtrar por nível
flyctl logs | grep ERROR
flyctl logs | grep "Kill detectada"
```

### Ver Métricas
```bash
# Status da VM
flyctl status

# Uso de recursos
flyctl vm status

# Histórico de deploys
flyctl releases
```

### Escalar Recursos
```bash
# Aumentar memória para 2GB (se necessário)
flyctl scale memory 2048

# Aumentar CPUs
flyctl scale count 2

# Ver configuração atual
flyctl scale show
```

---

## 🐛 Troubleshooting

### Problema: "Out of Memory"
```bash
# Aumentar memória
flyctl scale memory 2048
```

### Problema: "Vision API Error"
```bash
# Verificar se API key está configurada
flyctl secrets list

# Reconfigurar OpenAI key
flyctl secrets set OPENAI_API_KEY="sk-..."

# Ver logs de erro
flyctl logs | grep "Vision API"
```

### Problema: "WebSocket Connection Failed"
```bash
# Reiniciar aplicação
flyctl apps restart

# Verificar health check
curl https://gta-analytics-v2.fly.dev/health
```

### Problema: "No Kills Detected"
```bash
# Ver logs do processor
flyctl logs | grep "processor"

# Verificar se Vision Pre-Filter está ativo
flyctl secrets list | grep VISION_PRE_FILTER

# Desabilitar Vision Pre-Filter (processar todos frames)
flyctl secrets set VISION_PRE_FILTER="false"
```

---

## 💰 Controle de Custos

### Monitorar Gastos OpenAI
1. Acessar: https://platform.openai.com/usage
2. Ver consumo por dia/mês
3. Configurar limite de gastos:
   - Settings → Billing → Usage limits
   - Definir: $50/mês (1 torneio)

### Monitorar Gastos Fly.io
```bash
# Ver fatura atual
flyctl billing status

# Ver histórico
flyctl billing history
```

### Otimizar Custos

**Opção 1: Usar GPT-4o mini (80% mais barato)**
```bash
flyctl secrets set VISION_MODEL="gpt-4o-mini"
```

**Opção 2: Usar OpenRouter (33% mais barato)**
```bash
flyctl secrets set OPENROUTER_API_KEY="sk-or-..." \
                   VISION_MODEL="gpt-4o"
```

**Opção 3: Reduzir tamanho da VM**
```bash
flyctl scale memory 512  # Mínimo
```

---

## 🔄 Atualizar Sistema

```bash
# Fazer pull das últimas mudanças
git pull origin master

# Deploy da nova versão
flyctl deploy

# Verificar se deploy foi bem-sucedido
flyctl status
```

---

## 🗑️ Remover Aplicação

```bash
# Deletar app e todos os recursos
flyctl apps destroy gta-analytics-v2

# Confirmar digitando o nome do app
```

---

## 📞 Suporte

- **GitHub Issues**: https://github.com/Peugcam/captura.ai/issues
- **Fly.io Docs**: https://fly.io/docs
- **OpenAI Docs**: https://platform.openai.com/docs

---

## ✅ Checklist de Deploy

- [ ] Criar conta Fly.io
- [ ] Instalar Fly CLI
- [ ] Obter OpenAI API Key
- [ ] Configurar secrets no Fly.io
- [ ] Criar volume persistente
- [ ] Deploy da aplicação
- [ ] Testar dashboard
- [ ] Testar captura de stream
- [ ] Verificar detecção de kills
- [ ] Testar export Excel
- [ ] Configurar limites de gasto
- [ ] Documentar URL do dashboard para o Luis

---

**Sistema pronto para produção!** 🎉

Desenvolvido com Claude Code para Luis Otavio
