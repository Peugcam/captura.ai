# 🎮 GTA Analytics V2 - Guia de Uso

## 📋 Visão Geral

Sistema de análise em tempo real para partidas de GTA Battle Royale com **dois dashboards separados**:

- **Dashboard do Jogador**: Interface minimalista que não atrapalha o gameplay
- **Dashboard do Estrategista**: Interface completa com todos os dados e estatísticas

---

## 🚀 Como Usar

### Para o JOGADOR:

1. **Iniciar o backend** (se ainda não estiver rodando):
   ```bash
   cd backend
   python main_websocket.py
   ```

2. **Abrir o dashboard do jogador**:
   - Local: `http://localhost:3000/player`
   - Produção: `https://seu-app.fly.dev/player`

3. **Iniciar a captura**:
   - Clique no botão "▶️ Iniciar" no botão flutuante
   - Selecione a janela/aba do jogo GTA quando solicitado
   - O botão ficará verde e mostrará "Capturando"

4. **Durante o jogo**:
   - O botão flutuante pode ser **arrastado** para qualquer canto da tela
   - Clique em **"−"** para minimizar (vira um círculo pequeno)
   - Clique em **"+"** para expandir novamente
   - Pressione **F9** para parar/iniciar a captura (atalho de teclado)

5. **Parar a captura**:
   - Clique no botão "⏹️ Parar"
   - Ou pressione **F9**

6. **Transmitir o gameplay** (para o estrategista ver o vídeo):
   - Continue usando YouTube/Discord para transmitir o vídeo
   - O sistema só captura dados, não transmite vídeo

---

### Para o ESTRATEGISTA/SUPORTE:

1. **Abrir o dashboard do estrategista**:
   - Local: `http://localhost:3000/viewer`
   - Produção: `https://seu-app.fly.dev/viewer`

2. **Conectar automaticamente**:
   - O dashboard se conecta automaticamente ao backend
   - Status "Conectado" aparece no topo

3. **Acompanhar a partida**:
   - **Kill Feed**: Todos os kills em tempo real (painel esquerdo)
   - **Estatísticas**: Total de kills, jogadores ativos, times (centro)
   - **Status dos Times**: Quais times estão vivos, eliminados (centro inferior)
   - **Top 10 Jogadores**: Ranking com kills/deaths (painel direito)

4. **Ver o vídeo do gameplay**:
   - Assistir a transmissão do YouTube/Discord do jogador
   - Os dados no dashboard aparecem ~1 segundo antes do vídeo (sem delay)

5. **Exportar dados**:
   - Clique no botão "📊 Exportar Excel" no topo
   - Baixa planilha com todos os dados da partida

---

## 🎯 Fluxo Completo

```
┌─────────────────────────────────────────────────────────────┐
│                        ANTES DA PARTIDA                      │
└─────────────────────────────────────────────────────────────┘

1. JOGADOR:
   - Abre: http://localhost:3000/player
   - Inicia transmissão no YouTube/Discord
   - Clica "Iniciar" no botão flutuante
   - Seleciona janela do jogo

2. ESTRATEGISTA:
   - Abre: http://localhost:3000/viewer
   - Abre stream do YouTube/Discord do jogador
   - Aguarda dados aparecerem


┌─────────────────────────────────────────────────────────────┐
│                      DURANTE A PARTIDA                       │
└─────────────────────────────────────────────────────────────┘

JOGADOR:
   ✓ Joga normalmente
   ✓ Botão flutuante discreto no canto
   ✓ Transmite no YouTube/Discord

ESTRATEGISTA:
   ✓ Assiste YouTube/Discord (vídeo fluido)
   ✓ Vê dashboard (dados em tempo real)
   ✓ Kill feed atualiza automaticamente
   ✓ Estatísticas atualizadas a cada kill
   ✓ Ranking atualizado em tempo real


┌─────────────────────────────────────────────────────────────┐
│                        APÓS A PARTIDA                        │
└─────────────────────────────────────────────────────────────┘

1. JOGADOR:
   - Clica "Parar" no botão flutuante
   - Fecha transmissão

2. ESTRATEGISTA:
   - Clica "Exportar Excel"
   - Baixa planilha com análise completa
   - Revisa dados para estratégia
```

---

## 📊 O Que o Estrategista Vê

### Kill Feed (Painel Esquerdo)
```
⚔️ KILL FEED EM TEMPO REAL
┌────────────────────────────────┐
│ 10:30:15          weapon       │
│ MTL.venom  💀  LLL.ghost       │
│ Team MTL       Team LLL        │
└────────────────────────────────┘
```

### Estatísticas (Centro)
```
📊 ESTATÍSTICAS GERAIS
┌─────────────┬─────────────┐
│ ⚔️ Kills    │ 👥 Players │
│    47       │    23       │
└─────────────┴─────────────┘
┌─────────────┬─────────────┐
│ 🏆 Times    │ ⏱️ Tempo   │
│    8        │   15:32     │
└─────────────┴─────────────┘
```

### Status dos Times
```
📊 STATUS DOS TIMES
┌────────────────────────────────┐
│ MTL              [5 vivos]     │
│ Total: 10 | Kills: 23          │
├────────────────────────────────┤
│ LLL              [3 vivos]     │
│ Total: 8  | Kills: 15          │
├────────────────────────────────┤
│ XYZ              [0 vivos]     │  ← Eliminado
│ Total: 5  | Kills: 8           │
└────────────────────────────────┘
```

### Top 10 Jogadores (Painel Direito)
```
🏆 TOP 10 JOGADORES
┌────────────────────────────────┐
│ #1 🟢 MTL.venom                │
│       Team MTL                  │
│       8 Kills | 2 Deaths        │
├────────────────────────────────┤
│ #2 🟢 LLL.ghost                │
│       Team LLL                  │
│       7 Kills | 1 Deaths        │
├────────────────────────────────┤
│ #3 🔴 XYZ.player               │  ← Morto
│       Team XYZ                  │
│       6 Kills | 3 Deaths        │
└────────────────────────────────┘
```

---

## 🎨 Interface do Jogador

```
┌──────────────────────────┐
│ 🟢 GTA Analytics         │
│    Capturando            │
│                          │
│ 📸 234  ⏱️ 45s          │
│                          │
│ [⏹️ Parar]  [−]         │
└──────────────────────────┘
     ↕️ (arrastável)
```

**Recursos:**
- ✅ Botão flutuante arrastável
- ✅ Minimizável (vira círculo pequeno)
- ✅ Semi-transparente
- ✅ Atalho F9 para iniciar/parar
- ✅ Contador de frames e tempo
- ✅ Indicador visual (verde = ativo)

---

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```bash
# Backend
BACKEND_PORT=3000

# Gateway (se usar)
GATEWAY_HOST=http://localhost
GATEWAY_PORT=8000

# OpenAI API
OPENAI_API_KEY=sk-...

# OpenRouter API (fallback)
OPENROUTER_API_KEY=sk-or-...
```

---

## 🐛 Troubleshooting

### Problema: Dashboard do jogador não abre
**Solução:**
```bash
# Verificar se backend está rodando
cd backend
python main_websocket.py

# Verificar URL
# Local: http://localhost:3000/player
```

### Problema: Estrategista não vê dados
**Solução:**
1. Verificar se jogador iniciou a captura
2. Verificar se status mostra "Conectado" (topo do dashboard)
3. Verificar logs do backend

### Problema: "Erro ao capturar tela"
**Solução:**
1. Usar navegador atualizado (Chrome, Edge, Firefox)
2. Permitir permissões de captura quando solicitado
3. Verificar se o jogo está rodando em tela cheia

### Problema: Kills não aparecem
**Solução:**
1. Verificar se o jogo está em português brasileiro
2. Verificar se o kill feed está visível no jogo (canto superior direito)
3. Verificar logs do backend para erros de processamento

---

## 💰 Custos

**Custo adicional: $0 (zero)**

O sistema usa a mesma infraestrutura existente:
- ✅ Frames já são capturados para processamento de IA
- ✅ WebSocket já está implementado
- ✅ Broadcast automático sem custo adicional
- ✅ Apenas compartilha dados (JSON), não vídeo

**Estimativa mensal:** ~$30/mês (apenas APIs de IA)

---

## 📞 Suporte

**Problemas ou dúvidas?**
1. Verificar logs do backend
2. Verificar console do navegador (F12)
3. Verificar conexão com backend (status no topo)

**Logs importantes:**
```bash
# Backend
cd backend
python main_websocket.py

# Ver logs em tempo real
# Linux/Mac: tail -f logs.txt
# Windows: Get-Content logs.txt -Wait
```

---

## 🎯 Resumo Rápido

| Item | Jogador | Estrategista |
|------|---------|--------------|
| **URL** | `/player` | `/viewer` |
| **Interface** | Botão flutuante | Dashboard completo |
| **Vê dados?** | Não (tela limpa) | Sim (tudo) |
| **Captura?** | Sim | Não |
| **Vê vídeo?** | Não precisa | YouTube/Discord |
| **Export?** | Não | Sim (Excel) |

---

**Desenvolvido por Paulo Eugenio Campos**
**Versão: 2.0 - Fevereiro 2026**
