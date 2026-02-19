# 🏆 GTA Tournament Tracker - Guia de Uso

## Para o Vitor - Como Usar o Sistema de Torneios

### ✅ O Que Foi Implementado

O sistema agora tem **TUDO** que você precisa para acompanhar torneios em tempo real:

1. **✅ Upload de Imagem do Bracket** - A IA extrai automaticamente os times
2. **✅ Input Manual de Fallback** - Se a IA falhar, você digita manualmente
3. **✅ Grade Visual de 20 Times** - Mostra todos os times simultaneamente
4. **✅ Indicadores de Jogadores Vivos** - 5 bolinhas por time (verde = vivo, cinza = morto)
5. **✅ Contador de Kills por Time** - Atualizado automaticamente
6. **✅ Correção Manual** - Clique nas bolinhas para marcar vivo/morto manualmente
7. **✅ Reset de Partida** - Reseta stats mas mantém o roster
8. **✅ Atualização em Tempo Real** - WebSocket broadcast para todos conectados

---

## 🚀 Como Iniciar o Sistema

### Passo 1: Iniciar o Backend

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\backend
python main_websocket.py
```

O servidor vai iniciar em: `http://localhost:3000`

### Passo 2: Abrir o Dashboard de Torneio

No navegador, acesse:

```
http://localhost:3000/api/tournament
```

---

## 📋 Como Configurar um Torneio

### Método 1: Upload de Imagem (Recomendado)

1. **Clique em "⚙️ Setup Tournament"**
2. **Vá em "Option 1: Upload Bracket Image"**
3. **Clique em "📁 Click to upload tournament bracket image"**
4. **Selecione a imagem do bracket do site do torneio**
5. **Clique em "🤖 Extract Teams with AI"**
6. **Aguarde a IA processar** (5-10 segundos)

**Resultados possíveis:**
- ✅ **Sucesso**: Times extraídos automaticamente e dashboard atualizado
- ⚠️ **Falha**: Mensagem de erro → Use o Método 2 (Manual)

### Método 2: Input Manual (Fallback)

Se a IA não conseguir extrair os times da imagem:

1. **Role para "Option 2: Manual Input"**
2. **Preencha cada linha:**
   - **TAG**: Sigla do time (ex: PPP, MTL, LLL)
   - **Players**: Nome dos 5 jogadores (deixe vazio se não souber)
3. **Clique em "➕ Add Team"** para adicionar mais times
4. **Clique em "✅ Start Tournament"** quando terminar

**Exemplo:**
```
TAG: PPP
Players: almeida99, player2, player3, player4, player5

TAG: MTL
Players: ibra7b, player2, player3

TAG: SVV
Players: (deixe vazio se não souber os nomes)
```

---

## 🎮 Durante a Partida

### Visualização Automática

O sistema detecta kills automaticamente e atualiza:
- ✅ Bolinhas verdes → Jogadores vivos
- ❌ Bolinhas cinzas → Jogadores mortos
- 🔢 Contador de kills por time
- 📊 Estatísticas gerais (total alive/dead)

### Correção Manual

Se o sistema errar ou você quiser corrigir:

1. **Clique na bolinha do jogador**
2. **Verde → Cinza** (marcar morto)
3. **Cinza → Verde** (marcar vivo / reviver)

**Exemplo de uso:**
- Sistema não detectou uma kill → Clique na bolinha para marcar morto
- Jogador foi revivido → Clique na bolinha para marcar vivo

---

## 🔄 Resetar Partida

Quando uma partida terminar e começar a próxima:

1. **Clique em "🔄 Reset Match"**
2. **Confirme**
3. **Todos os jogadores voltam vivos**
4. **Kills zeradas**
5. **Roster mantido** (não precisa reconfigurar)

---

## 🗑️ Limpar Roster

Para sair do modo torneio completamente:

1. **Clique em "🗑️ Clear Roster"**
2. **Confirme**
3. **Volta para tela inicial**

---

## 🎯 Recursos Principais

### Grid de Times

Cada box de time mostra:
- **TAG do time** (PPP, MTL, etc.)
- **Jogadores vivos** (ex: 4/5)
- **Total de kills** (ex: 12)
- **5 indicadores visuais** (bolinhas verde/cinza)

### Barra de Status

No topo mostra:
- **Total de teams** no torneio
- **Total de players alive**
- **Total de players dead**
- **Total de kills** na partida

### Status de Conexão

Canto superior direito:
- 🟢 **Connected** - Sistema funcionando
- ⚫ **Disconnected** - Reconectando automaticamente

---

## ⚡ Atalhos e Dicas

### Dicas de Uso

1. **Prepare o roster ANTES da partida começar**
2. **Use a imagem do bracket** para economizar tempo
3. **Deixe o dashboard aberto em tela cheia**
4. **Clique nas bolinhas apenas para correções**
5. **Reset entre partidas** para manter o roster

### Solução de Problemas

**A IA não extraiu os times corretamente?**
- Use o input manual
- Digite apenas as tags dos times (nomes dos players são opcionais)

**Sistema não está detectando kills?**
- Verifique se o kill feed está visível na tela
- Use correção manual temporariamente

**Precisa adicionar/remover times durante partida?**
- Ainda não implementado (planejado para v2)
- Por enquanto, use "Clear Roster" e reconfigure

---

## 📊 API Endpoints (Para Desenvolvedores)

### Upload de Imagem
```
POST /api/tournament/roster/upload
Content-Type: multipart/form-data
Body: file (imagem do bracket)
```

### Input Manual
```
POST /api/tournament/roster/manual
Content-Type: application/json
Body: {
  "teams": [
    {"tag": "PPP", "players": ["player1", "player2", ...]},
    {"tag": "MTL", "players": ["player1", "player2", ...]}
  ]
}
```

### Atualizar Status de Jogador
```
POST /api/tournament/player/status
Content-Type: application/json
Body: {
  "team_tag": "PPP",
  "player_name": "almeida99",
  "alive": false
}
```

### Resetar Partida
```
POST /api/tournament/match/reset
```

### Limpar Roster
```
POST /api/tournament/roster/clear
```

### Obter Roster Atual
```
GET /api/tournament/roster
```

---

## 🎨 Capturas de Tela (Descrição)

### Tela Inicial
- Botão grande "Setup Tournament"
- Mensagem: "No Tournament Loaded"

### Setup Modal
- Seção 1: Upload de imagem com preview
- Seção 2: Input manual com grid de times
- Botões: Extract AI, Add Team, Start Tournament

### Dashboard Ativo
- Grid de 20 boxes (4x5 ou responsivo)
- Cada box: Tag, Alive count, Kill count, 5 bolinhas
- Barra de status no topo
- Botões: Reset Match, Clear Roster

---

## 📝 Próximos Passos (Futuro)

- [ ] Detecção automática de revives via IA
- [ ] Exportar resultados do torneio em Excel
- [ ] Modo espectador (apenas visualização)
- [ ] Histórico de partidas
- [ ] Gráficos de performance por time

---

## 🆘 Suporte

**Problemas ou dúvidas?**
- Contate: Paulo (desenvolvedor)
- Issues: GitHub do projeto

---

**Desenvolvido com 🚀 por Paulo Eugênio Campos**
**GTA Analytics V2 - Tournament Edition**
