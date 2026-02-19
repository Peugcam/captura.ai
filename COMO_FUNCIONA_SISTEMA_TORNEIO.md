# 🏆 Como Funciona o Sistema de Torneio - Documentação Técnica

## Para: Paulo (Desenvolvedor)
## Data: 18 de Fevereiro de 2026

---

## 📋 Fluxo Completo do Sistema

### 1️⃣ **Setup Inicial (Antes do Jogo)**

O Vitor tem **2 opções** para configurar o torneio:

#### **Opção A: Upload de Imagem de Classificados**

```
[Vitor] → Upload screenshot da página de classificados
         ↓
[Frontend] → POST /api/tournament/roster/upload (multipart/form-data)
         ↓
[Backend] → RosterManager.load_from_image()
         ↓
[Vision API] → Extrai tags dos times (PPP, MTL, SVV, etc.)
         ↓
[Backend] → RosterManager.initialize_tournament_roster()
         ↓
[Backend] → Cria times com players placeholders (PPP_P1, PPP_P2, etc.)
         ↓
[WebSocket] → Broadcast "roster_loaded" event
         ↓
[Frontend] → Renderiza grid de times
```

**Resultado:**
```python
{
  "PPP": {
    "tag": "PPP",
    "players": {
      "PPP_P1": {alive: True, kills: 0},
      "PPP_P2": {alive: True, kills: 0},
      "PPP_P3": {alive: True, kills: 0},
      "PPP_P4": {alive: True, kills: 0},
      "PPP_P5": {alive: True, kills: 0}
    }
  },
  "MTL": { ... },
  "SVV": { ... }
}
```

#### **Opção B: Input Manual de Tags**

```
[Vitor] → Digita tags manualmente (textarea):
          PPP
          MTL
          SVV
          KUSH
         ↓
[Frontend] → POST /api/tournament/roster/manual (JSON)
         ↓
[Backend] → RosterManager.initialize_tournament_roster()
         ↓
[Backend] → Cria times com players placeholders
         ↓
[WebSocket] → Broadcast "roster_loaded" event
         ↓
[Frontend] → Renderiza grid de times
```

---

### 2️⃣ **Durante o Jogo (Detecção Automática)**

```
[GTA V] → Kill acontece: [PPP]almeida99 mata [MTL]ibra7b
       ↓
[Go Gateway] → Captura screenshot do killfeed
       ↓
[Backend] → FrameProcessor.process_frame()
       ↓
[Vision API] → OCR + GPT-4o Vision detecta:
              {
                killer: "almeida99",
                killer_team: "PPP",
                victim: "ibra7b",
                victim_team: "MTL"
              }
       ↓
[Backend] → FrameProcessor._register_player_in_tournament()
       ↓
[Backend] → Verifica se time "PPP" existe no torneio
       ↓
[Backend] → Verifica se player "almeida99" já existe
       ↓
[Backend] → CASO 1: Player NÃO existe
            - Substitui placeholder "PPP_P1" por "almeida99"
            - Atualiza kills: almeida99.kills = 1
            - Log: "✅ NEW PLAYER added to tournament: almeida99 (PPP)"
       ↓
[Backend] → CASO 2: Player JÁ existe
            - Atualiza kills: almeida99.kills += 1
            - Log: "📊 Updated almeida99 (PPP): 5 kills, alive"
       ↓
[Backend] → Atualiza victim "ibra7b"
            - ibra7b.alive = False
            - ibra7b.deaths += 1
       ↓
[WebSocket] → Broadcast "kill" event
       ↓
[Frontend] → Atualiza grid automaticamente
            - Quadrado de almeida99: verde com "5"
            - Quadrado de ibra7b: cinza
```

**Fluxo Visual:**

```
ANTES (Setup):
┌─────────┐
│   PPP   │
│  5/5 🎯0│
│🟩🟩🟩🟩🟩│  ← Todos placeholders (PPP_P1, PPP_P2, etc.)
└─────────┘

DEPOIS (1ª kill detectada):
┌─────────┐
│   PPP   │
│  5/5 🎯1│
│🟩🟩🟩🟩🟩│  ← PPP_P1 substituído por "almeida99"
│ 1       │  ← Mostra kill no quadrado
└─────────┘

DEPOIS (almeida99 mata novamente):
┌─────────┐
│   PPP   │
│  5/5 🎯2│
│🟩🟩🟩🟩🟩│
│ 2       │  ← Kill count atualizado
└─────────┘
```

---

### 3️⃣ **Correção Manual (Fallback)**

Se a IA errar ou não detectar algo:

```
[Vitor] → Clica no quadrado verde
       ↓
[Frontend] → POST /api/tournament/player/status
            {
              team_tag: "PPP",
              player_name: "almeida99",
              alive: false
            }
       ↓
[Backend] → RosterManager atualiza status
       ↓
[WebSocket] → Broadcast "player_status_updated"
       ↓
[Frontend] → Quadrado fica cinza
```

---

## 🔧 Arquitetura Técnica

### Backend Components

```
main_websocket.py
├── GTAAnalyticsBackend
│   ├── FrameProcessor (com roster_manager)
│   │   ├── VisionProcessor (GPT-4o Vision)
│   │   ├── TeamTracker
│   │   └── _register_player_in_tournament() ← NOVO!
│   └── ConnectionManager (WebSocket)
│
└── RosterManager
    ├── load_from_image() - Extrai tags da imagem
    ├── initialize_tournament_roster() - Cria times
    ├── get_team() - Busca time por tag
    └── TournamentTeam
        └── TournamentPlayer[] (max 5)
```

### Integração FrameProcessor ↔ RosterManager

**processor.py linha 631:**
```python
def __init__(self, roster_manager=None):
    self.roster_manager = roster_manager
    if roster_manager:
        logger.info("🏆 Tournament Mode: Roster Manager connected")
```

**processor.py linha 870:**
```python
def _register_player_in_tournament(self, player_name, team_tag, is_kill):
    if not self.roster_manager or not self.roster_manager.tournament_mode:
        return

    team = self.roster_manager.get_team(team_tag)
    if not team:
        return

    if player_name in team.players:
        # Atualizar stats
        player = team.players[player_name]
        if is_kill:
            player.kills += 1
            team.total_kills += 1
        else:
            player.alive = False
            player.deaths += 1
    else:
        # Adicionar novo player
        if team.can_add_player():
            new_player = TournamentPlayer(
                name=player_name,
                alive=not is_kill,
                kills=1 if is_kill else 0,
                deaths=0 if is_kill else 1
            )
            team.players[player_name] = new_player
            logger.info(f"✅ NEW PLAYER added: {player_name} ({team_tag})")
```

**processor.py linha 956:**
```python
if event_type == 'kill':
    # ... detecção de kill ...

    # 🏆 TOURNAMENT MODE: Auto-register players
    if self.roster_manager and self.roster_manager.tournament_mode:
        self._register_player_in_tournament(killer_name, killer_team, is_kill=True)
        self._register_player_in_tournament(victim_name, victim_team, is_kill=False)
```

---

## 🎯 Casos de Uso Importantes

### Caso 1: Time sem players (só tags)

**Setup:**
```json
{
  "teams": [
    {"tag": "PPP", "players": []},
    {"tag": "MTL", "players": []}
  ]
}
```

**Backend cria:**
```python
{
  "PPP": {
    "players": {
      "PPP_P1": {...},
      "PPP_P2": {...},
      "PPP_P3": {...},
      "PPP_P4": {...},
      "PPP_P5": {...}
    }
  }
}
```

**Primeira kill detectada:**
- `[PPP]almeida99 mata [MTL]ibra7b`
- `PPP_P1` é substituído por `almeida99`
- `MTL_P1` é substituído por `ibra7b`

### Caso 2: Player novo além dos 5

Se um time já tem 5 players e um 6º aparece:

```python
if team.can_add_player():  # False (já tem 5)
    # Não adiciona
    logger.warning(f"⚠️ Cannot add {player_name}: team is full")
```

### Caso 3: Revive (player morto volta vivo)

```
[Vitor] → Clica no quadrado cinza
       ↓
[Frontend] → POST /api/tournament/player/status {alive: true}
       ↓
[Backend] → player.alive = True
       ↓
[Frontend] → Quadrado fica verde novamente
```

---

## 📊 Dados Trafegados

### WebSocket Events

**roster_loaded:**
```json
{
  "type": "roster_loaded",
  "data": {
    "teams": [
      {
        "tag": "PPP",
        "players": [
          {"name": "almeida99", "alive": true, "kills": 5},
          {"name": "PPP_P2", "alive": true, "kills": 0}
        ],
        "alive_count": 5,
        "total_kills": 5
      }
    ]
  }
}
```

**kill:**
```json
{
  "type": "kill",
  "data": {
    "killer": "almeida99",
    "killer_team": "PPP",
    "victim": "ibra7b",
    "victim_team": "MTL"
  }
}
```

**player_status_updated:**
```json
{
  "type": "player_status_updated",
  "data": {
    "team_tag": "PPP",
    "player_name": "almeida99",
    "alive": false,
    "teams": [...]  // Estado completo atualizado
  }
}
```

---

## 🔐 Segurança

- Upload de imagem limitado a **10MB**
- Validação de team tags (2-10 caracteres)
- Máximo **20 teams** por torneio
- Máximo **5 players** por time
- Rate limiting nos endpoints

---

## 🚀 Performance

### Otimizações Implementadas

1. **Frame Deduplication** - Ignora frames duplicados
2. **Vision Pre-Filter** - Filtra frames sem killfeed (low-res)
3. **Batch Processing** - Processa múltiplas kills em grupo
4. **Kill Deduplication** - Evita registrar mesmo kill 2x
5. **WebSocket Broadcasting** - Atualização em tempo real

### Custos de API

- **Upload de imagem:** 1 chamada GPT-4o Vision (tags extraction)
- **Por kill detectada:** 1 chamada GPT-4o Vision (killfeed OCR)
- **Pré-filtro:** Chamadas low-res (320px) para filtrar frames

---

## 📝 Logs Importantes

```
🏆 Tournament Mode: Roster Manager connected
✅ NEW PLAYER added to tournament: almeida99 (PPP)
📊 Updated almeida99 (PPP): 5 kills, alive
⚠️ Team PPP not in tournament roster
⚠️ Cannot add player6 to PPP: team is full (5/5)
```

---

## 🔄 Reset e Limpeza

### Match Reset (preserva roster)
```
POST /api/tournament/match/reset
→ Todos players ficam vivos
→ Kills/deaths zerados
→ Roster mantido
```

### Clear Roster (sai do modo torneio)
```
POST /api/tournament/roster/clear
→ Limpa todos os times
→ tournament_mode = False
→ Volta para modo normal
```

---

**Implementado por:** Paulo Eugênio Campos
**Cliente:** Vitor (via Luís)
**Data:** 18 de Fevereiro de 2026
