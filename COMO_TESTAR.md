# 🧪 Guia Rápido - Como Testar as Correções

## ⚡ Início Rápido (2 minutos)

### 1️⃣ Iniciar o Backend
```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\backend
python main_websocket.py
```

**Saída esperada:**
```
INFO - 🚀 GTA Analytics Backend iniciado na porta 3000
INFO - 🔒 CORS configurado com origens específicas
INFO - 📡 WebSocket server rodando em ws://localhost:3000/events
```

---

### 2️⃣ Abrir Página de Testes

**Opção A - Teste Rápido:**
```
Abrir no navegador: test_dashboard.html
```

**Opção B - Dashboard Principal:**
```
Abrir no navegador: dashboard-tournament.html
```

---

### 3️⃣ Executar Testes Básicos

#### No `test_dashboard.html`:

1. **Clicar em "Testar Conexão HTTP"**
   - ✅ Verde = Backend funcionando
   - ❌ Vermelho = Backend offline

2. **Clicar em "Testar WebSocket"**
   - ✅ Verde = WebSocket conectado
   - ❌ Vermelho = Erro de conexão

3. **Clicar em "Carregar Roster de Teste"**
   - ✅ Verde = 3 times carregados
   - Ver mensagem WebSocket no log

4. **Clicar em "Toggle Player Status"**
   - ✅ Verde = Toggle funcionando
   - Ver mensagem no log

---

## 🎮 Teste Completo do Dashboard

### Passo 1: Carregar Roster Manual

1. Abrir `dashboard-tournament.html`
2. Clicar em **"⚙️ Configurar Torneio"**
3. Na seção "Opção 2: Input Manual", colar:

```
PPP
MTL
SVV
KUSH
LLL
```

4. Clicar em **"✅ Iniciar Torneio"**

**Resultado esperado:**
- Modal fecha
- 5 times aparecem na tela
- Cada time tem 5 caixas de jogadores (verdes = vivos)
- Status bar mostra: "5 times, 25 players vivos"

---

### Passo 2: Testar Toggle de Status

1. **Passar mouse sobre qualquer caixa de jogador**
   - Deve aumentar de tamanho (scale 1.1)
   - Deve brilhar mais

2. **Clicar em uma caixa verde (vivo)**
   - Deve ficar cinza (morto)
   - Contador de vivos diminui
   - Tooltip mostra "Morto"

3. **Clicar novamente**
   - Deve voltar verde (vivo)
   - Contador de vivos aumenta
   - Animação de "revive pulse"

4. **Abrir Console (F12)**
   - Deve mostrar:
   ```
   🎯 Click detected on player box: PPP - PPP_P1
   🔄 Toggling player: PPP - PPP_P1 (true → false)
   ✅ Response: {success: true, ...}
   📨 Message: {type: "player_status_updated", ...}
   ```

---

### Passo 3: Testar Upload de Imagem

1. Clicar em **"⚙️ Configurar Torneio"**
2. Na seção "Opção 1: Upload de Imagem"
3. Fazer upload de uma imagem de classificados
4. Clicar em **"🤖 Extrair Times com IA"**

**Resultado esperado:**
- Botão mostra "⏳ Extracting..."
- Após 3-5 segundos: "✅ Extracted X teams"
- Modal fecha
- Times aparecem com nomes completos

---

### Passo 4: Testar Reset

1. Clicar em **"🔄 Resetar Partida"**
   - Confirmar
   - Todos jogadores ficam vivos
   - Kills zeradas

2. Clicar em **"🗑️ Limpar Lista"**
   - Confirmar
   - Todos times removidos
   - Volta para empty state

---

## 🔍 Checklist de Validação

### ✅ Backend
- [ ] Backend inicia sem erros
- [ ] Porta 3000 está aberta
- [ ] Logs mostram CORS configurado
- [ ] Roster manager inicializado

### ✅ Conexões
- [ ] HTTP GET /api/tournament/roster funciona
- [ ] WebSocket conecta (🟢 verde no canto)
- [ ] WebSocket recebe mensagens
- [ ] CORS não bloqueia requisições

### ✅ Roster Loading
- [ ] Manual input aceita tags
- [ ] Image upload aceita imagens
- [ ] IA extrai times corretamente
- [ ] Times aparecem no grid
- [ ] Placeholders criados (5 por time)

### ✅ Player Toggle (CRÍTICO)
- [ ] Hover mostra scale + brilho
- [ ] Click muda cor verde → cinza
- [ ] Click novamente volta cinza → verde
- [ ] Console mostra logs de debug
- [ ] WebSocket broadcast funciona
- [ ] UI atualiza automaticamente

### ✅ Status Bar
- [ ] Conta times corretamente
- [ ] Conta players vivos
- [ ] Conta players mortos
- [ ] Atualiza em tempo real

### ✅ Match Controls
- [ ] Reset Match funciona
- [ ] Clear Roster funciona
- [ ] Confirmações aparecem

---

## 🐛 Debug - O Que Verificar

### Se cliques não funcionam:

1. **Abrir Console do Navegador (F12)**
   - Ver se aparecem erros JavaScript
   - Ver se aparecem mensagens de click

2. **Verificar Network Tab**
   - Ver se POST /api/tournament/player/status é enviado
   - Status deve ser 200 OK

3. **Verificar WebSocket Tab**
   - Deve estar conectado (WS)
   - Mensagens devem aparecer quando clicar

4. **Inspecionar Elemento**
   - Player box deve ter data-team-tag
   - Player box deve ter data-player-name
   - Player box deve ter data-player-alive

---

## 📊 Comportamento Esperado

### Ao clicar em jogador VIVO:
```
UI: Verde → Cinza
API: POST {team_tag: "PPP", player_name: "PPP_P1", alive: false}
Backend: ✏️ Manual correction: PPP_P1 (PPP) marked as dead
WebSocket: {type: "player_status_updated", ...}
UI: Atualiza automaticamente
Status Bar: Players Vivos 25 → 24
```

### Ao clicar em jogador MORTO:
```
UI: Cinza → Verde (com animação revive pulse)
API: POST {team_tag: "PPP", player_name: "PPP_P1", alive: true}
Backend: ✏️ Manual correction: PPP_P1 (PPP) revived
WebSocket: {type: "player_status_updated", ...}
UI: Atualiza automaticamente
Status Bar: Players Vivos 24 → 25
```

---

## ⚠️ Problemas Comuns

### Problema: "Failed to fetch"
**Causa:** Backend não está rodando
**Solução:** Iniciar backend primeiro

### Problema: CORS Error
**Causa:** Origem não está em ALLOWED_ORIGINS
**Solução:** Verificar se "null" está na lista (para file://)

### Problema: WebSocket disconnected
**Causa:** Backend caiu ou firewall bloqueou
**Solução:** Reiniciar backend, verificar firewall

### Problema: Cliques não registram
**Causa:** JavaScript não carregou corretamente
**Solução:**
1. Verificar console para erros
2. Fazer hard refresh (Ctrl+Shift+R)
3. Verificar se handlePlayerBoxClick existe

---

## 🎯 Teste de Carga

### Roster Máximo (20 times):
```
FIR, 4SK, 32X, 7D, AF, LGC, PPP, MTL, SVV, KUSH,
LLL, ABC, XYZ, TST, QWE, ASD, ZXC, RTY, FGH, VBN
```

**Resultado esperado:**
- 20 times carregados
- 100 players total (5 por time)
- UI responsiva
- Toggle funciona em todos

---

## ✅ Teste Passou Se:

1. ✅ Backend inicia sem erros
2. ✅ WebSocket conecta (🟢 verde)
3. ✅ Roster carrega (manual ou imagem)
4. ✅ **Clicar em player box altera status**
5. ✅ UI atualiza em tempo real
6. ✅ Status bar reflete mudanças
7. ✅ Console mostra logs corretos
8. ✅ Reset e Clear funcionam

---

**Tempo estimado de teste completo:** 5-10 minutos

**Se TODOS os itens acima passarem → Sistema 100% funcional! 🎉**
