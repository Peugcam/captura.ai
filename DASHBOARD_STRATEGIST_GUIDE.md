# Dashboard Estrategista - Guia Completo

## Visão Geral

O **Dashboard Estrategista** (`dashboard-strategist.html`) é a interface unificada que combina:
- 📊 **Análise em tempo real** (do dashboard-viewer.html)
- 🎮 **Controle de torneio** (do dashboard-tournament.html)
- 🎨 **Modo Curador** para edição manual
- 🛡️ **Auto-proteção** de edições manuais
- 🌐 **Detecção automática** de servidores GTA

## Layout do Dashboard

```
┌─────────────────────────────────────────────────────────┐
│                    HEADER + CONTROLES                    │
├─────────────┬───────────────────────┬────────────────────┤
│  KILL FEED  │   TOURNAMENT GRID     │    LEADERBOARD     │
│   (400px)   │     (1fr - flex)      │     (400px)        │
│             │                       │                    │
│ Kill Feed   │  ┌─────┬─────┬─────┐  │  #1 PlayerA (15K) │
│ em tempo    │  │ PPP │ MTL │ SVV │  │  #2 PlayerB (12K) │
│ real com    │  │█████│█████│█████│  │  #3 PlayerC (10K) │
│ detalhes    │  └─────┴─────┴─────┘  │  ...              │
│             │                       │                    │
└─────────────┴───────────────────────┴────────────────────┘
```

### Indicadores Fixos (Top-Right)
```
🟢 Conectado                    (20px do topo)
🎨 MODO CURADOR ATIVO          (70px do topo)
🛡️ Proteção: 3 edições ativas  (120px do topo)
🎮 Servidor 1 detectado (95%)  (170px do topo)
```

## Funcionalidades Principais

### 1️⃣ **Painel Esquerdo - Kill Feed**
- Exibe kills em tempo real conforme acontecem
- Mostra: killer, victim, teams, weapon, distance
- Animação slideIn para novos eventos
- Máximo de 50 kills recentes mantidos

### 2️⃣ **Painel Central - Tournament Grid**
- Grid responsivo com boxes de times
- 5 indicadores de jogadores por time (verde = vivo, cinza = morto)
- Clique nos jogadores para alternar status (vivo/morto)
- Stats por time: vivos/total, kills
- Times eliminados ficam translúcidos

### 3️⃣ **Painel Direito - Leaderboard**
- Top 10 jogadores por kills
- Mostra: rank, nome, time, kills, deaths, K/D
- Indicador visual de status (vivo/morto)
- Ordenação automática por kills

### 4️⃣ **Barra de Status (Top)**
- Total de kills na partida
- Jogadores vivos/mortos
- Times ativos
- Tempo de partida (contador automático)

## Modo Curador 🎨

### O que é?
Sistema que permite ao estrategista **controlar manualmente** o estado dos jogadores, **bloqueando atualizações da AI**.

### Como Ativar
1. Clique no botão **"🎨 Ativar Modo Curador"**
2. Indicador aparece no canto superior direito
3. Agora você tem controle total!

### Modo Curador ATIVO
- ✅ Cliques manuais funcionam normalmente
- ❌ AI **NÃO** pode alterar status de jogadores
- ❌ Mensagens WebSocket bloqueadas: `player_added`, `kill`, `player_detected`
- 🎨 Indicador rosa piscando no canto

### Modo AI ATIVO (padrão)
- ✅ AI atualiza automaticamente
- ✅ Sistema sincroniza com servidor
- ⚠️ Edições manuais podem ser sobrescritas

### Quando Usar Modo Curador?
- ✅ Correção de erros da AI
- ✅ Durante intervalos/pausas do torneio
- ✅ Quando você tem informação que a AI não vê
- ❌ Não recomendado durante gameplay ativo

## Auto-Proteção 🛡️

### O que é?
Sistema **automático** que protege edições manuais por 5 segundos, mesmo no modo AI.

### Como Funciona
1. Você clica num jogador para alterar status
2. Sistema registra override com timestamp
3. Por **5 segundos**, esse jogador não pode ser alterado pela AI
4. Após 5s, proteção expira e AI pode atualizar novamente

### Vantagens
- ✅ Funciona **sem ativar Modo Curador**
- ✅ Proteção temporária automática
- ✅ Ideal para correções rápidas durante jogo
- ✅ Indicador mostra quantas edições estão protegidas

### Indicador
```
🛡️ Proteção Automática: 3 edições ativas
```
- Aparece automaticamente quando há edições protegidas
- Some quando todas expirarem (após 5s cada)

## Detecção de Servidor 🌐

### O que é?
Sistema que detecta automaticamente qual servidor GTA está sendo usado (Server 1 ou Server 2) baseado no layout visual da UI.

### Como Funciona
- AI analisa a imagem e detecta características visuais
- Seleciona o prompt correto para o servidor detectado
- Mostra confiança % da detecção

### Indicadores Visuais
```
🎮 Servidor 1 detectado (95%)  (laranja)
🎮 Servidor 2 detectado (88%)  (turquesa)
🎮 Detectando servidor...      (roxo - aguardando)
```

### Configuração Manual
Se a detecção automática falhar, você pode forçar no backend:
```env
GTA_SERVER_TYPE=server1  # ou server2
```

## Configuração de Torneio

### Método 1: Upload de Imagem (AI)
1. Clique em **"⚙️ Configurar Torneio"**
2. Upload screenshot da página de classificados
3. Clique **"🤖 Extrair Times com IA"**
4. AI extrai tags automaticamente
5. Durante o jogo, AI detecta nomes dos jogadores

### Método 2: Input Manual
1. Clique em **"⚙️ Configurar Torneio"**
2. Digite tags dos times (uma por linha):
   ```
   PPP
   MTL
   SVV
   KUSH
   LLL
   ```
3. Clique **"✅ Iniciar Torneio"**
4. Durante o jogo, AI detecta jogadores automaticamente

## Editar Times/Jogadores

### Quando Usar
- Corrigir nomes detectados incorretamente pela AI
- Adicionar jogadores manualmente
- Renomear times

### Como Fazer
1. Clique em **"✏️ Editar Times"**
2. Modal abre com todos os times
3. Edite:
   - TAG do time
   - Nome completo do time
   - Nomes dos 5 jogadores
4. Clique **"💾 Salvar Alterações"**
5. Sistema atualiza via API

## Controles Principais

| Botão | Função |
|-------|--------|
| ⚙️ **Configurar Torneio** | Abre modal para setup inicial |
| ✏️ **Editar Times** | Abre modal para editar roster |
| 🎨 **Ativar Modo Curador** | Ativa controle manual total |
| 🔄 **Resetar Partida** | Marca todos como vivos, zera kills |
| 🗑️ **Limpar Lista** | Remove todos os times (sai do modo torneio) |
| 📊 **Exportar Excel** | Baixa planilha com estatísticas |

## Atalhos e Dicas

### Interação com Jogadores
- **Clique** numa caixinha verde (vivo) → marca como morto
- **Clique** numa caixinha cinza (morto) → marca como vivo
- **Hover** sobre caixinha → mostra tooltip com nome e kills

### Visualização de Times
- **Times com jogadores vivos** → border colorida, opacidade 100%
- **Times eliminados** → opacidade 40%, overlay vermelho

### WebSocket Status
- 🟢 **Conectado** → sistema funcionando normalmente
- ⚫ **Desconectado** → tentando reconectar automaticamente
- ⚠️ Se desconectado > 10s → verificar se backend está rodando

## Fluxo de Trabalho Recomendado

### Pré-Torneio
1. ✅ Iniciar backend: `cd backend && python main_websocket.py`
2. ✅ Abrir dashboard: `dashboard-strategist.html`
3. ✅ Configurar torneio (upload ou manual)
4. ✅ Verificar conexão (🟢 Conectado)

### Durante Torneio
1. ✅ Modo AI ativo (padrão)
2. ✅ Monitorar kill feed e grid
3. ⚠️ Se AI errar, fazer edição manual (auto-proteção ativa)
4. ⚠️ Para múltiplas correções, ativar Modo Curador

### Pós-Torneio
1. ✅ Exportar planilha Excel
2. ✅ Resetar partida ou Limpar lista
3. ✅ Fechar backend

## Troubleshooting

### Dashboard não conecta
```bash
# Verificar se backend está rodando
cd backend
python main_websocket.py
# Deve mostrar: WebSocket server started on ws://localhost:3000/events
```

### Cliques não funcionam
- ✔️ Verifique se há jogadores cadastrados (não são caixinhas vazias)
- ✔️ Verifique indicador de conexão (deve estar verde)
- ✔️ Abra console do navegador (F12) e procure erros

### AI não detecta jogadores
- ✔️ Verifique se modo torneio está ativo (teams carregados)
- ✔️ Verifique se captura de tela está ativa no backend
- ✔️ Verifique logs do backend para ver se frames estão sendo processados

### Servidor detectado errado
```env
# Forçar servidor no .env
GTA_SERVER_TYPE=server1
```

## Arquitetura Técnica

### WebSocket Events
| Event Type | Descrição |
|------------|-----------|
| `roster_loaded` | Times carregados com sucesso |
| `player_status_updated` | Status de jogador alterado manualmente |
| `kill` | Nova kill detectada |
| `player_added` | Novo jogador detectado |
| `match_reset` | Partida resetada |
| `roster_cleared` | Lista de times limpa |
| `server_detected` | Servidor GTA detectado |

### API Endpoints
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/tournament/roster` | GET | Buscar roster atual |
| `/api/tournament/roster/upload` | POST | Upload imagem para extração |
| `/api/tournament/roster/manual` | POST | Cadastrar times manualmente |
| `/api/tournament/player/status` | POST | Alterar status de jogador |
| `/api/tournament/match/reset` | POST | Resetar partida |
| `/api/tournament/roster/clear` | POST | Limpar roster |
| `/api/tournament/team/{tag}` | PUT | Editar time |
| `/export` | GET | Exportar Excel |

### Estado do Dashboard
```javascript
{
  ws: WebSocket,              // Conexão WebSocket
  teams: Array,               // Lista de times
  curatorMode: Boolean,       // Modo curador ativo?
  manualOverrides: Map,       // Edições protegidas (auto-proteção)
  PROTECTION_WINDOW: 5000     // 5 segundos de proteção
}
```

## Comparação de Dashboards

| Feature | Player | Viewer | Tournament | **Strategist** |
|---------|--------|--------|------------|----------------|
| Kill Feed | ❌ | ✅ | ❌ | ✅ |
| Leaderboard | ❌ | ✅ | ❌ | ✅ |
| Tournament Grid | ❌ | ❌ | ✅ | ✅ |
| Modo Curador | ❌ | ❌ | ✅ | ✅ |
| Auto-Proteção | ❌ | ❌ | ✅ | ✅ |
| Dual-Server | ❌ | ❌ | ✅ | ✅ |
| Export Excel | ❌ | ✅ | ❌ | ✅ |
| Layout 3-col | ❌ | ✅ | ❌ | ✅ |

## Conclusão

O **Dashboard Estrategista** é a interface **definitiva** para gerenciar torneios GTA, combinando:
- 📊 Análise em tempo real completa
- 🎮 Controle total sobre o estado do torneio
- 🎨 Flexibilidade entre modo AI e manual
- 🛡️ Proteção inteligente de edições
- 🌐 Suporte automático para múltiplos servidores

**Arquivo:** `dashboard-strategist.html` (1607 linhas, 53KB)
**Backend:** `backend/main_websocket.py`
**Porta:** `http://localhost:3000` (backend) + arquivo HTML

---

**Última atualização:** 18 de Fevereiro de 2026
**Versão:** 2.0 (Unified Strategist Dashboard)
