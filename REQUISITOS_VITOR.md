# 📋 Requisitos do Cliente (Luis via Vitor)

## 🎯 Informações Críticas Recebidas

### 1. Setup do OBS
- ✅ **OBS Studio** (não Streamlabs)
- ✅ **Captura:** Tela inteira do PC
- ✅ **Resolução do jogo:** 1100x1080
- ✅ **Resolução do OBS:** 1080p (1920x1080)
- ✅ **Cliente aceita plugin:** SIM! (copiar arquivo, sem instalação)

### 2. Kill Feed
- ✅ **Posição:** Canto superior direito (FIXO)
- ⚠️ **Aparência:** Pode mudar de servidor para servidor
- 💡 **Oportunidade:** Região fixa = performance otimizada

### 3. Tipos de Campeonato

#### Etapa 1 - Classificatória Aberta
```
Times: Número variável (não fixo)
Lista prévia: NÃO
Solução: Detectar TAGs automaticamente conforme aparecem
```

#### Etapa 2 - Classificatória Fechada
```
Times: ~100 times
Lista prévia: SIM (tem tabela)
Solução: Importar lista antes, facilita detecção
```

#### Campeonato Final
```
Times: 20 times (fixos)
Lista prévia: SIM
Solução: Mais fácil, times conhecidos
```

### 4. Prioridades (Ordem de Importância)

**PRIORIDADE 1 (CRÍTICO):**
- ✅ Saber **quais times estão vivos**
- ✅ Saber **quantos players** cada time tem vivo

**PRIORIDADE 2 (IMPORTANTE):**
- ✅ Quanto cada time **matou**

**PRIORIDADE 3 (DESEJÁVEL):**
- ✅ Ranking geral

### 5. Dashboard
- ✅ **PC:** Sim
- ✅ **Mobile:** Sim (até melhor!)
- 💡 **Estratégia:** Mobile-first design

---

## 🏗️ Nova Arquitetura (Baseada nos Requisitos)

### Solução: Plugin OBS Nativo + Backend Cloud

```
┌─────────────────────────────────────────────────────────────┐
│  PC do Luis                                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  OBS Studio (1080p)                                   │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  GTA V (1100x1080)                              │  │  │
│  │  │  Kill Feed: Superior Direito (fixo)             │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                       │  │
│  │  Plugin OBS (obs-websocket ou script Python)         │  │
│  │  • Captura região do kill feed (otimizado)           │  │
│  │  • Envia apenas essa região (economia de banda)      │  │
│  │  • Roda invisível em background                      │  │
│  └──────────────────────┬────────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          │ WebSocket/WebRTC
                          │ (apenas kill feed region)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Fly.io Cloud (São Paulo)                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Gateway                                             │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Backend (Python FastAPI)                            │   │
│  │  • Vision API (kill feed detection)                  │   │
│  │  • Team tracker                                      │   │
│  │  • Player alive counter                              │   │
│  │  • Kill counter                                      │   │
│  │  • Auto-detect new teams (Etapa 1)                   │   │
│  │  • Import team list (Etapa 2/Camp)                   │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Database (PostgreSQL)                               │   │
│  │  • Match state (real-time)                           │   │
│  │  • Teams alive                                       │   │
│  │  • Players per team                                  │   │
│  │  • Kill count                                        │   │
│  │  • Historical data                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ WebSocket (real-time updates)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Dashboard (Web App - Mobile First)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  📱 MOBILE VIEW (Prioridade)                         │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  🔴 TIMES VIVOS: 15/20                         │  │   │
│  │  │                                                │  │   │
│  │  │  Team Alpha    ✅ 4/4 players  (12 kills)     │  │   │
│  │  │  Team Bravo    ✅ 3/4 players  (8 kills)      │  │   │
│  │  │  Team Charlie  ✅ 2/4 players  (15 kills)     │  │   │
│  │  │  Team Delta    ⚰️ ELIMINATED                  │  │   │
│  │  │  ...                                           │  │   │
│  │  │                                                │  │   │
│  │  │  [Ranking] [Kills] [Timeline]                 │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementação do Plugin OBS

### Opção A: Python Script (RECOMENDADO)
```python
# obs_gta_plugin.py
# Arquivo único que Luis copia para: C:\Program Files\obs-studio\data\obs-plugins\

import obspython as obs
import requests
import base64
from io import BytesIO

GATEWAY_URL = "https://gta-analytics-gateway.fly.dev"
KILL_FEED_REGION = {
    "x": 1400,  # Canto superior direito
    "y": 0,
    "width": 520,
    "height": 400
}

def script_description():
    return "GTA Analytics - Auto Kill Feed Tracker"

def script_update(settings):
    # Configuração automática
    pass

def script_tick(seconds):
    # A cada 0.25s (4 FPS)
    if int(seconds * 4) % 1 == 0:
        capture_kill_feed()

def capture_kill_feed():
    # Captura apenas região do kill feed
    source = obs.obs_get_output_source(0)

    if source:
        # Pega frame atual
        screenshot = obs.obs_source_get_base_width(source)

        # Crop para kill feed region
        cropped = crop_image(screenshot, KILL_FEED_REGION)

        # Envia para gateway
        send_to_gateway(cropped)

        obs.obs_source_release(source)

def send_to_gateway(image_data):
    # Envia apenas região do kill feed (economia de 80% de banda!)
    requests.post(f"{GATEWAY_URL}/frame", json={
        "data": base64.b64encode(image_data).decode(),
        "region": "kill_feed"
    })
```

**Vantagens:**
- ✅ Arquivo único (copiar e colar)
- ✅ Roda automaticamente quando OBS abre
- ✅ Invisível (sem UI)
- ✅ Captura apenas kill feed (otimizado)
- ✅ Não precisa instalar nada

### Opção B: OBS WebSocket (Alternativa)
Se a Opção A não funcionar, usamos WebSocket externo.

---

## 📊 Features por Prioridade

### 🔥 SPRINT 1 - CRÍTICO (Prioridade 1)
**Prazo: 2 dias**

#### Feature 1.1: Detecção de Times Vivos
```python
# backend/src/team_alive_tracker.py

class TeamAliveTracker:
    def __init__(self):
        self.teams = {}  # {team_name: {players_alive: 4, total: 4}}

    def process_kill(self, killer, victim):
        """
        Processa kill e atualiza estado
        """
        victim_team = extract_team_tag(victim)

        if victim_team in self.teams:
            self.teams[victim_team]['players_alive'] -= 1

            # Team eliminado?
            if self.teams[victim_team]['players_alive'] == 0:
                self.emit_team_eliminated(victim_team)

    def get_alive_teams(self):
        """
        Retorna times vivos ordenados por players
        """
        return [
            team for team, data in self.teams.items()
            if data['players_alive'] > 0
        ]
```

#### Feature 1.2: Dashboard Mobile-First
```html
<!-- dashboard/mobile.html -->
<div class="mobile-dashboard">
    <div class="header">
        <h1>🔴 TIMES VIVOS: <span id="alive-count">15</span>/20</h1>
    </div>

    <div class="teams-list">
        <!-- Auto-atualiza via WebSocket -->
        <div class="team alive" data-team="alpha">
            <span class="team-name">Team Alpha</span>
            <span class="players">✅ 4/4</span>
            <span class="kills">12 kills</span>
        </div>

        <div class="team alive" data-team="bravo">
            <span class="team-name">Team Bravo</span>
            <span class="players">⚠️ 2/4</span>
            <span class="kills">8 kills</span>
        </div>

        <div class="team eliminated" data-team="delta">
            <span class="team-name">Team Delta</span>
            <span class="players">⚰️ ELIMINADO</span>
            <span class="kills">5 kills</span>
        </div>
    </div>
</div>

<style>
/* Mobile-first CSS */
.mobile-dashboard {
    max-width: 100%;
    padding: 10px;
    font-size: 16px; /* Legível no celular */
}

.team {
    padding: 15px;
    margin: 10px 0;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
}

.team.alive {
    background: #2d5016;
    border-left: 4px solid #4caf50;
}

.team.eliminated {
    background: #3a1f1f;
    opacity: 0.6;
    border-left: 4px solid #666;
}
</style>
```

### ⚡ SPRINT 2 - IMPORTANTE (Prioridade 2)
**Prazo: +1 dia**

#### Feature 2.1: Contador de Kills por Time
```python
# Já está implementado no backend!
# backend/src/team_tracker.py
```

### 🎯 SPRINT 3 - DESEJÁVEL (Prioridade 3)
**Prazo: +1 dia**

#### Feature 3.1: Ranking Geral
```python
# backend/src/ranking.py

def calculate_ranking(teams):
    """
    Ranking baseado em:
    1. Posição final (times vivos no final)
    2. Kills totais
    3. Sobrevivência individual
    """
    return sorted(teams, key=lambda t: (
        t.placement,  # 1º lugar = menor valor
        -t.total_kills,  # Mais kills = melhor
        -t.players_alive  # Mais players vivos = melhor
    ))
```

---

## 🎮 Detecção Automática de Times (Etapa 1)

```python
# backend/src/auto_team_detector.py

class AutoTeamDetector:
    def __init__(self):
        self.detected_teams = set()
        self.tag_patterns = [
            r'\[([A-Z0-9]{2,5})\]',  # [TAG]PlayerName
            r'([A-Z0-9]{2,5})_',      # TAG_PlayerName
            r'([A-Z0-9]{2,5})\|',     # TAG|PlayerName
        ]

    def extract_team_tag(self, player_name):
        """
        Detecta TAG do time automaticamente
        """
        for pattern in self.tag_patterns:
            match = re.search(pattern, player_name)
            if match:
                tag = match.group(1)
                self.detected_teams.add(tag)
                return tag

        return "NO_TAG"  # Player sem tag = solo

    def get_detected_teams(self):
        """
        Retorna lista de times detectados na partida
        """
        return list(self.detected_teams)
```

### Dashboard de Confirmação
```
🔍 TIMES DETECTADOS AUTOMATICAMENTE:

[ALPHA] (4 players)  ✅ Confirmar  ❌ Remover
[BRAVO] (4 players)  ✅ Confirmar  ❌ Remover
[XYZ]   (1 player)   ⚠️ Possível erro? (1 player só)

[+ Adicionar manualmente]
```

---

## 📂 Importação de Lista de Times (Etapa 2/Camp)

```python
# backend/src/team_importer.py

def import_team_list(file_path):
    """
    Importa lista de times de Excel/CSV

    Formato esperado:
    Team Name, Tag, Players
    Team Alpha, ALPHA, Player1,Player2,Player3,Player4
    Team Bravo, BRAVO, Player5,Player6,Player7,Player8
    """
    teams = []

    with open(file_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            teams.append({
                'name': row['Team Name'],
                'tag': row['Tag'],
                'players': row['Players'].split(','),
                'total_players': len(row['Players'].split(','))
            })

    return teams
```

### Upload via Dashboard
```html
<div class="import-teams">
    <h3>Importar Lista de Times (Etapa 2/Camp)</h3>

    <input type="file" accept=".csv,.xlsx" id="team-list-upload">
    <button onclick="importTeams()">Importar</button>

    <p>Formato: CSV com colunas: Team Name, Tag, Players</p>
    <a href="/template.csv" download>Baixar template</a>
</div>
```

---

## 💰 Custos (Resposta à sua pergunta)

### PLANO B (PyInstaller - o que você pediu)
```
Custo total: R$ 0 (GRÁTIS)
Tempo: 1 hora

Entrega:
• GTA-Analytics.exe (arquivo único)
• Cliente executa e pronto
• Conecta no Fly.io existente

Problema:
• Antivírus pode bloquear
• Cliente pode não confiar
```

### PLANO A (Electron/MS Store - profissional)

#### Opção A1: Electron com Certificado
```
Setup inicial:
• Certificado Code Signing: $100/ano (DigiCert)
• Hospedagem .exe: $0 (GitHub Releases)
• Total: $100/ano

Fly.io (continua igual):
• $8/mês base
• ~$1-2/mês por cliente adicional

Tempo de desenvolvimento:
• 2-3 dias para versão básica
• 1 semana para versão completa

Vantagens:
• Windows não bloqueia
• Auto-update automático
• Profissional
```

#### Opção A2: Microsoft Store
```
Setup inicial:
• Conta desenvolvedor MS: $19 (única vez)
• Hospedagem: $0 (Microsoft cuida)
• Total: $19 (única vez!)

Fly.io (continua igual):
• $8/mês base

Tempo de desenvolvimento:
• 2-3 dias para desenvolvimento
• 7-10 dias para aprovação Microsoft
• Total: ~2 semanas

Vantagens:
• MÁXIMA confiança (loja oficial)
• Auto-update via loja
• Zero bloqueio de antivírus
• MAIS BARATO que certificado!
```

### PLANO C (Plugin OBS - IDEAL para Luis)
```
Custo: R$ 0 (GRÁTIS!)

Tempo: 2 horas

Entrega:
• obs_gta_plugin.py (arquivo único)
• Luis copia para pasta do OBS
• Roda automaticamente
• Invisível, sem UI

Fly.io (continua igual):
• $8/mês base

Vantagens:
• Usa OBS que Luis JÁ TEM
• Não precisa instalar nada
• Captura otimizada (só kill feed)
• ZERO custo adicional
```

---

## 🎯 RECOMENDAÇÃO FINAL

**Para o caso do Luis:**

### Use PLANO C (Plugin OBS)

**Por quê?**
1. ✅ Luis JÁ USA OBS Studio
2. ✅ Aceita copiar arquivo (ele confirmou)
3. ✅ Grátis e instantâneo
4. ✅ Invisível (roda em background)
5. ✅ Otimizado (captura só kill feed)
6. ✅ Funciona no setup atual dele

**Não precisa de:**
- ❌ Cliente instalar programa novo
- ❌ Certificado ($100)
- ❌ Executável .exe suspeito
- ❌ Mudança no workflow dele

---

## 📋 Próximos Passos

**Quer que eu crie:**

1. **Plugin OBS** (2 horas)
   - Captura região kill feed
   - Envia para Fly.io
   - Roda invisível

2. **Dashboard Mobile-First** (4 horas)
   - Times vivos em destaque
   - Players por time
   - Kills
   - Funciona perfeitamente no celular

3. **Auto-detector de times** (2 horas)
   - Para Etapa 1 (classificatória aberta)
   - Detecta TAGs automaticamente

4. **Importador de lista** (1 hora)
   - Para Etapa 2 e Camp
   - Upload CSV/Excel

**Total: ~1 dia de trabalho**

**Me confirma se quer que eu comece pelo Plugin OBS?** 🚀
