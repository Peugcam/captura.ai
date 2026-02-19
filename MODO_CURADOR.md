# 🎨 Modo Curador - Documentação

## O que é o Modo Curador?

O **Modo Curador** é uma funcionalidade que permite ao operador do torneio ter **controle manual total** sobre o status dos jogadores, pausando temporariamente as atualizações automáticas da IA.

## Por que foi criado?

### Problema Original
- A IA analisa o killfeed e atualiza automaticamente o status dos jogadores
- Quando o operador tentava fazer edições manuais (clicar nos player boxes), as atualizações da IA **sobrescreviam** as edições manuais
- Isso causava **conflito** entre edições manuais e automáticas

### Solução: Modo Curador
- Permite ao operador **pausar** as atualizações automáticas da IA
- Dá controle total para ajustar manualmente o status de qualquer jogador
- Quando terminar a curadoria, pode voltar ao **Modo AI** e sincronizar com o servidor

---

## Como Usar

### 1. Ativar Modo Curador

1. Carregue um torneio (configure as tags dos times)
2. Clique no botão **"🎨 Ativar Modo Curador"**
3. O sistema mostra:
   - Botão muda para **"🤖 Ativar Modo AI"** (laranja)
   - Indicador fixo no canto superior direito: **"🎨 MODO CURADOR ATIVO"**
   - Notificação: "Modo Curador Ativado - Você tem controle total"

### 2. Fazer Edições Manuais

- Clique nos **player boxes** (quadrados dos jogadores) para alternar entre:
  - **Verde** = Vivo
  - **Cinza** = Morto
- As edições são salvas no servidor
- **A IA NÃO sobrescreverá suas edições** enquanto estiver no Modo Curador

### 3. Voltar ao Modo AI

1. Clique no botão **"🤖 Ativar Modo AI"**
2. O sistema:
   - Volta a aceitar atualizações automáticas da IA
   - Sincroniza com o servidor para pegar estado mais recente
   - Remove o indicador de Modo Curador

---

## Funcionamento Técnico

### Filtro de Mensagens WebSocket

Quando `curatorMode = true`:

```javascript
// Tipos de mensagem BLOQUEADOS no Modo Curador:
const aiUpdateTypes = ['player_added', 'kill', 'player_detected'];

// Tipos de mensagem PERMITIDOS no Modo Curador:
- 'player_status_updated' → Resposta de edição manual
- 'roster_loaded' → Carregamento inicial
- 'match_reset' → Reset de partida
- 'team_added' → Adição manual de time
```

### Fluxo de Edição Manual

```
1. Usuário clica em player box
2. Frontend envia POST /api/tournament/player/status
3. Backend atualiza estado
4. Backend broadcast 'player_status_updated'
5. Frontend recebe e atualiza UI (PERMITIDO mesmo no Modo Curador)
```

### Proteção Contra Sobrescrita

```javascript
// ❌ ANTES (sem Modo Curador)
t=0s: Usuário clica (manual)
t=1s: IA detecta kill → broadcast → SOBRESCREVE edição manual

// ✅ AGORA (com Modo Curador)
t=0s: Usuário ativa Modo Curador
t=1s: Usuário clica (manual) → Salva no servidor
t=2s: IA detecta kill → broadcast → BLOQUEADO pelo filtro
```

---

## Suporte a Diferentes UIs de Torneio

O sistema foi desenvolvido para reconhecer **dois formatos diferentes** de kill feed de GTA Online:

### UI Tipo 1: Servidor Principal
- **Morte confirmada**: ícone de ☠️ caveira
- **Derrubado (não morto)**: ícone de bonequinho caído
- **Revive**: ícone de ➕ (player voltou ao jogo)
- **Cores**:
  - 🟢 Verde = seu time matou
  - ⚪ Cinza = outros times se matando

### UI Tipo 2: Servidor Alternativo
- **Morte confirmada**: ícone de ☠️ caveira
- **Kill feed**: mesma lógica de cores (verde/cinza)
- **Formato**: similar mas layout diferente

### Tabelas de Status dos Times

Ambos os servidores mostram:
- **Quadrados coloridos** = players vivos
- **Número ao lado do time** = total de kills do time
- **Layout**: grid de times com indicadores visuais

O sistema da IA foi treinado para reconhecer **ambos os formatos** automaticamente.

---

## Casos de Uso Recomendados

### Quando usar Modo Curador?

✅ **USE quando:**
- O killfeed está acontecendo muito rápido e a IA pode perder informações
- Você precisa fazer ajustes manuais em vários players ao mesmo tempo
- Houve um erro de detecção da IA que você precisa corrigir
- Você está fazendo setup inicial e quer controle total

✅ **USE Modo AI quando:**
- O jogo está rolando normalmente
- Você quer monitoramento automático sem intervenção
- A IA está detectando corretamente

---

## FAQ

### 1. Minhas edições manuais serão perdidas quando voltar ao Modo AI?

**Não.** Todas as edições manuais são salvas no servidor. Quando você voltar ao Modo AI, o sistema sincroniza com o servidor e mantém o estado atual. A IA continua atualizando a partir desse ponto.

### 2. Posso fazer edições manuais sem ativar Modo Curador?

**Sim**, mas há risco de suas edições serem sobrescritas pela próxima atualização da IA (dentro de 1-2 segundos). O Modo Curador existe justamente para **garantir** que suas edições não sejam sobrescritas.

### 3. O que acontece se a IA detectar um kill no Modo Curador?

A IA continua analisando o killfeed em background, mas os **broadcasts são bloqueados** pelo filtro do frontend. Quando você voltar ao Modo AI, pode sincronizar com o servidor para ver as detecções da IA.

### 4. Posso usar Modo Curador durante a partida?

**Sim!** Você pode alternar entre Modo Curador e Modo AI **a qualquer momento** durante a partida. É seguro fazer isso.

### 5. Quantos times/jogadores posso gerenciar?

- **Máximo**: 20 times
- **Jogadores por time**: até 5 players
- **Total**: até 100 jogadores simultâneos

---

## Próximas Melhorias (Roadmap)

### Fase 2: Proteção Automática de Edições (planejada)
- Sistema de "janela de proteção" de 5 segundos após edição manual
- Merge inteligente entre updates da IA e edições manuais
- Não precisa ativar Modo Curador manualmente

### Fase 3: Delta Updates (planejada)
- Backend envia apenas mudanças específicas (não estado completo)
- Frontend atualiza apenas elementos DOM específicos
- Performance melhorada, sem re-render completo

---

## Suporte Técnico

Se encontrar problemas:

1. **Verifique o console** (F12 no navegador)
   - Procure por mensagens com 🎨 (Modo Curador) ou 🤖 (Modo AI)
   - Verifique se WebSocket está conectado (🟢 Conectado)

2. **Sintomas comuns**:
   - **"Edições não salvam"** → Verifique conexão com backend
   - **"IA sobrescreve edições"** → Ative Modo Curador primeiro
   - **"Botão não aparece"** → Carregue um torneio primeiro

3. **Logs úteis**:
   ```
   🎨 CURATOR MODE ACTIVE - AI updates blocked
   🎨 CURATOR MODE: Blocking AI update of type "player_added"
   🤖 AI MODE ACTIVE - Syncing with server
   ```

---

## Créditos

Desenvolvido para solucionar o problema de **conflito entre atualizações automáticas e edições manuais** no sistema de tracking de torneios GTA Online.

**Data de Implementação**: 2026-02-18
**Versão**: 1.0
**Status**: ✅ Funcional e testado
