# 🎮 Sistema Inteligente de Roster com Histórico

## 📋 Visão Geral

Sistema que **cruza dados históricos** com o torneio atual para:
- ✅ Preencher automaticamente jogadores conhecidos
- ✅ Validar jogadores durante a partida
- ✅ Corrigir nomes detectados incorretamente pela IA
- ✅ Fornecer estatísticas comparativas em tempo real

---

## 🚀 Funcionalidades Implementadas

### 1. **Histórico de Times e Jogadores** 📊

**Arquivo:** `backend/team_history.py`

**O que faz:**
- Mantém banco de dados JSON com **todos os jogadores** que já participaram de torneios
- Organizado por **TAG de time** (ex: PPP, MTL, SVV)
- Rastreia para cada jogador:
  - Total de aparições
  - Total de kills/deaths
  - Primeira e última participação
  - Vitórias em torneios

**Exemplo de dados salvos:**
```json
{
  "teams": {
    "PPP": {
      "tag": "PPP",
      "full_name": "Peppers",
      "tournament_count": 5,
      "known_players": {
        "John": {
          "name": "John",
          "total_appearances": 5,
          "total_kills": 42,
          "total_deaths": 15,
          "win_count": 2
        },
        "Carlos": {
          "name": "Carlos",
          "total_appearances": 3,
          "total_kills": 28,
          "total_deaths": 12,
          "win_count": 1
        }
      }
    }
  }
}
```

---

### 2. **Preenchimento Automático (Smart Fill)** 🤖

**Como funciona:**

#### **Método 1: Upload de Imagem**

1. Você faz upload da imagem do torneio
2. IA extrai TAGs dos times (PPP, MTL, SVV...)
3. **AUTOMATICAMENTE** busca jogadores conhecidos de cada time
4. Preenche o roster com os jogadores históricos

```
Imagem extraída: PPP, MTL, SVV

Sistema busca histórico:
✅ PPP → John, Carlos, Mike, Ana, Pedro
✅ MTL → Lucas, Maria, José, Paula, Ricardo
✅ SVV → (sem histórico) → cria placeholders SVV_P1, SVV_P2...
```

#### **Método 2: Entrada Manual**

- Digite apenas as TAGs: `PPP, MTL, SVV`
- Sistema **preenche automaticamente** com jogadores conhecidos
- Se não houver histórico, cria placeholders que serão substituídos quando a IA detectar nomes reais

---

### 3. **Validação em Tempo Real** ⚠️

**Arquivo:** `backend/tournament_tracker.py`

**Durante o torneio:**

#### **Cenário 1: Jogador no Time Correto ✅**
```
Kill detectada: John (PPP) matou alguém
Histórico: John sempre jogou pelo PPP
Ação: ✅ Confirma e registra normalmente
```

#### **Cenário 2: Jogador no Time Errado ⚠️**
```
Kill detectada: Carlos (MTL) matou alguém
Histórico: Carlos SEMPRE jogou pelo PPP
Ação: ❌ Alerta enviado ao dashboard
Dashboard mostra: "⚠️ Carlos historicamente joga pelo PPP, não MTL"
```

#### **Cenário 3: Correção Automática de Nome 🔄**
```
IA detecta: "J0HN" (erro de OCR)
Histórico: Time PPP tem jogador "John"
Similaridade: 80%
Ação: 💡 Corrige automaticamente para "John"
```

---

### 4. **Estatísticas Comparativas em Tempo Real** 📈

**Endpoint:** `GET /api/tournament/live/stats`

**Retorna:**
```json
{
  "teams": [
    {
      "tag": "PPP",
      "total_kills": 15,
      "avg_kills_per_tournament": 12.5,
      "performance_vs_avg": "above",
      "tournament_count": 5
    }
  ],
  "top_players": [
    {
      "name": "John",
      "team_tag": "PPP",
      "kills_today": 8,
      "avg_kills": 5.2,
      "validation_status": "confirmed"
    }
  ],
  "alerts": [
    {
      "type": "highlight",
      "message": "🔥 John (PPP): 8 kills - 2x acima da média!"
    },
    {
      "type": "warning",
      "message": "⚠️ Carlos historicamente joga pelo PPP, não MTL"
    }
  ]
}
```

---

## 🔄 Fluxo Completo do Sistema

### **ANTES DO TORNEIO:**

```
1. Upload de imagem OU entrada manual de TAGs
2. IA extrai: PPP, MTL, SVV
3. Sistema busca histórico:
   ✅ PPP → 5 jogadores conhecidos
   ✅ MTL → 5 jogadores conhecidos
   ⚠️ SVV → sem histórico, cria placeholders
4. Roster preenchido automaticamente!
```

### **DURANTE O TORNEIO:**

```
Kill detectada: "J0HN" matou "Player2"

1. Sistema recebe: team="PPP", player="J0HN"

2. Correção de nome:
   - Busca similaridade com jogadores conhecidos de PPP
   - Encontra "John" com 80% de similaridade
   - Corrige "J0HN" → "John"

3. Validação:
   - John está no time PPP?
   - Histórico confirma: John sempre jogou pelo PPP
   - Status: ✅ CONFIRMADO

4. Estatísticas:
   - John: 1 kill hoje
   - Média histórica: 5.2 kills
   - Dashboard atualizado em tempo real

5. Se performance excepcional:
   - John faz 10 kills (2x a média)
   - Alerta enviado: "🔥 John está em chamas!"
```

### **APÓS O TORNEIO:**

```
1. Chamar: POST /api/tournament/finish?winner_tag=PPP

2. Sistema salva no histórico:
   - Todos os jogadores participantes
   - Kills e deaths de cada um
   - Time vencedor
   - Data do torneio

3. Próximo torneio terá dados atualizados!
```

---

## 🛠️ APIs Disponíveis

### **Histórico**

```bash
# Listar todos os times conhecidos
GET /api/tournament/history/teams

# Estatísticas de um time específico
GET /api/tournament/history/team/PPP

# Jogadores conhecidos de um time
GET /api/tournament/history/players/PPP?limit=5
```

### **Tempo Real**

```bash
# Estatísticas ao vivo com comparação histórica
GET /api/tournament/live/stats

# Finalizar torneio e salvar histórico
POST /api/tournament/finish?winner_tag=PPP
```

---

## 📁 Arquivos de Dados

### **team_history.json** (criado automaticamente)
```
Localização: backend/team_history.json
Formato: JSON
Backup: Recomendado fazer backup após cada torneio
```

**Dados armazenados:**
- TAGs de times
- Nomes completos dos times
- Lista de jogadores por time
- Estatísticas individuais
- Histórico de participações

---

## 💡 Casos de Uso

### **Caso 1: Novo Torneio com Times Conhecidos**

```
1. Upload da imagem mostrando: PPP, MTL, SVV
2. Sistema preenche automaticamente:
   - PPP: John, Carlos, Mike, Ana, Pedro
   - MTL: Lucas, Maria, José, Paula, Ricardo
   - SVV: placeholders (time novo)
3. Durante jogo: IA detecta jogadores reais de SVV
4. Placeholders substituídos automaticamente
```

### **Caso 2: Detecção de Erro da IA**

```
IA detecta: "CAARL0S" (nome mal lido)
Sistema: "Parece com 'Carlos' do time PPP (80% similar)"
Correção automática: CAARL0S → Carlos
Dashboard: ✅ Nome corrigido automaticamente
```

### **Caso 3: Jogador no Time Errado**

```
Kill: "John (MTL) matou Player2"
Histórico: John SEMPRE jogou pelo PPP (5 torneios)
Dashboard mostra: ⚠️ ALERTA - John deve estar no PPP
Vitor pode: Editar manualmente e mover John para PPP
```

### **Caso 4: Performance Excepcional**

```
John histórico: 5.2 kills/torneio
John hoje: 12 kills
Dashboard: 🔥 John (PPP): 12 kills - 230% acima da média!
Chat: Casters podem comentar a performance
```

---

## ✅ Vantagens do Sistema

1. **Menos Trabalho Manual** 📝
   - Não precisa digitar todos os nomes
   - Sistema preenche automaticamente

2. **Correção Automática** 🔄
   - IA pode errar nomes (OCR)
   - Sistema corrige baseado no histórico

3. **Validação Contínua** ✅
   - Detecta jogadores em times errados
   - Alerta em tempo real

4. **Insights em Tempo Real** 📊
   - "Time PPP está 50% acima da média!"
   - "John nunca fez tantos kills!"

5. **Histórico Crescente** 📈
   - Quanto mais torneios, mais preciso
   - Banco de dados se auto-aprimora

---

## 🎯 Próximos Passos (Opcional)

### **Melhorias Futuras:**

1. **Dashboard de Insights**
   - Gráfico de performance vs média
   - Ranking histórico de jogadores
   - Times com melhor winrate

2. **Exportação Avançada**
   - Relatório com comparação histórica
   - Gráficos de evolução por torneio
   - Export para sites de torneio

3. **Machine Learning**
   - Predição de vencedor baseado em histórico
   - Identificação de "combos" fortes (jogadores que jogam bem juntos)

---

## 📞 Como Usar

### **Setup Inicial:**

```bash
# Backend já está configurado!
# Apenas certifique-se que está rodando:
cd backend
python main_websocket.py
```

### **Primeiro Torneio:**

```
1. Abra dashboard-strategist-v2.html
2. Clique em "Configurar Torneio"
3. Upload da imagem OU digite tags manualmente
4. Sistema preenche automaticamente
5. Inicie partida normalmente
6. Ao final: POST /api/tournament/finish?winner_tag=PPP
```

### **Torneios Seguintes:**

```
Mesmos passos, mas agora:
✅ Sistema JÁ conhece jogadores
✅ Preenchimento automático
✅ Validação em tempo real
✅ Comparação com histórico
```

---

## 🎉 Resumo

Você agora tem um **sistema inteligente** que:

- ✅ **Aprende** com cada torneio
- ✅ **Preenche** automaticamente jogadores
- ✅ **Valida** em tempo real
- ✅ **Corrige** erros da IA
- ✅ **Compara** com histórico
- ✅ **Alerta** sobre anomalias

**SIM, o cruzamento durante o torneio é MUITO relevante!** 🚀
