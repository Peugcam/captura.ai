# 🌐 URLs CORRETAS DO SISTEMA

## ✅ CONFIGURAÇÃO CORRETA (V2)

### Apps no Fly.io:

```
1. Gateway:
   https://gta-analytics-gateway.fly.dev

2. Backend V2 (ATUAL - COM DASHBOARD):
   https://gta-analytics-v2.fly.dev

3. Backend Antigo (DESCONTINUADO):
   https://gta-analytics-backend.fly.dev
```

---

## 🔧 PROBLEMA DETECTADO:

O **Gateway está enviando frames para o Backend ANTIGO**

**Solução:** Atualizar configuração do Gateway para enviar ao V2

---

## 📊 DASHBOARDS DISPONÍVEIS (V2):

### ✅ Dashboard Principal (Estrategista):
```
https://gta-analytics-v2.fly.dev/strategist
```

**Este é o dashboard CORRETO para Luis!**

Mostra:
- Times vivos/eliminados
- Jogadores por time
- Kill counts
- Rankings
- Gerenciamento de roster

---

## 🎯 PARA TESTAR AGORA:

**Opção 1:** Abra o dashboard V2:
```
https://gta-analytics-v2.fly.dev/strategist
```

**Opção 2:** Verifique stats V2:
```
https://gta-analytics-v2.fly.dev/stats
```

Atualmente mostra:
```json
{
  "frames_received": 2,
  "frames_processed": 2,
  "kills_detected": 0,
  "teams": 0
}
```

---

## ⚙️ CONFIGURAR GATEWAY PARA ENVIAR AO V2:

Você precisa atualizar o Gateway para enviar os frames ao backend V2:

1. **No projeto do Gateway (Go):**
   - Encontre a variável de ambiente `BACKEND_URL`
   - Mude de: `https://gta-analytics-backend.fly.dev`
   - Para: `https://gta-analytics-v2.fly.dev`

2. **Fazer deploy do Gateway:**
```bash
cd gateway
flyctl deploy -a gta-analytics-gateway
```

---

## 📝 ALTERNATIVA RÁPIDA (SEM MUDAR GATEWAY):

**Cliente envia direto para Backend V2:**

Edite `config.json`:

```json
{
  "gateway_url": "https://gta-analytics-v2.fly.dev",
  "fps": 4,
  "kill_feed_region": {
    "x": 1400,
    "y": 0,
    "width": 520,
    "height": 400
  }
}
```

**Prós:**
- ✅ Funciona imediatamente
- ✅ Dados vão direto para o backend com dashboard

**Contras:**
- ❌ Pula o Gateway (mas ainda funciona)

---

## 🚀 RECOMENDAÇÃO:

**AGORA (TESTE RÁPIDO):**

1. Mude `config.json` para:
```json
{
  "gateway_url": "https://gta-analytics-v2.fly.dev",
  ...
}
```

2. Execute o capturador novamente
3. Abra o dashboard: `https://gta-analytics-v2.fly.dev/strategist`
4. Veja os dados aparecendo em tempo real!

**DEPOIS (PRODUÇÃO):**

1. Atualize o Gateway para enviar ao V2
2. Volte `config.json` para usar o Gateway
3. Sistema completo: Cliente → Gateway → Backend V2

---

**Quer que eu mude o config.json agora para testar com o V2?** 🚀
