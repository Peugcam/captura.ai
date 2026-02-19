# 🏆 Guia Rápido - Sistema de Torneio GTA

## Para: Vitor (Cliente)
## Data: 18 de Fevereiro de 2026

---

## ✅ O Que o Sistema Faz

Este sistema rastreia **até 20 times** em **tempo real** durante partidas de Battle Royale no GTA V.

**Principais recursos:**
- ✅ **Extração automática de tags** via IA a partir da imagem de classificados
- ✅ **Input manual simples** (apenas tags, sem precisar dos nomes dos players)
- ✅ **Rastreamento automático** de kills e mortes durante o jogo
- ✅ **Correção manual** como fallback (clique nos quadrados)
- ✅ **Visual em quadrados** (estilo do campeonato oficial)
- ✅ **Mostra kills dentro dos quadrados** de cada player
- ✅ **Interface 100% em português**

---

## 🚀 Como Usar (Passo a Passo)

### 1️⃣ Iniciar o Sistema

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\backend
python main_websocket.py
```

Depois, abra no navegador:
```
http://localhost:3000/api/tournament
```

---

### 2️⃣ Configurar o Torneio

Você tem **2 opções**:

#### **Opção A: Upload de Imagem (Recomendado)**

1. Clique em **"⚙️ Configurar Torneio"**
2. Vá em **"Opção 1: Upload de Imagem"**
3. Faça upload da **screenshot da página de classificados** do site do campeonato
4. Clique em **"🤖 Extrair Times com IA"**
5. Aguarde 5-10 segundos
6. ✅ Pronto! Os times foram carregados automaticamente

#### **Opção B: Input Manual**

Se a IA não conseguir extrair ou você preferir digitar:

1. Clique em **"⚙️ Configurar Torneio"**
2. Vá em **"Opção 2: Input Manual"**
3. Digite as **tags dos times**, uma por linha:

```
PPP
MTL
SVV
KUSH
LLL
RVL
BRK
```

4. Clique em **"✅ Iniciar Torneio"**
5. ✅ Pronto!

**IMPORTANTE:** Você **NÃO precisa** digitar os nomes dos players! A IA irá detectar automaticamente durante a partida.

---

### 3️⃣ Durante a Partida

O sistema funciona **automaticamente**:

- ✅ Detecta kills no killfeed
- ✅ Atualiza os quadrados (verde = vivo, cinza = morto)
- ✅ Mostra kills dentro de cada quadrado
- ✅ Atualiza contador de kills por time
- ✅ Mostra total de players vivos/mortos

**Se precisar corrigir manualmente:**
- Clique no **quadrado verde** → Marca como morto
- Clique no **quadrado cinza** → Marca como vivo (revive)

---

### 4️⃣ Entre Partidas

**Para começar uma nova partida com os mesmos times:**

1. Clique em **"🔄 Resetar Partida"**
2. Confirme
3. ✅ Todos voltam vivos, kills zeradas, roster mantido

**Para sair do modo torneio completamente:**

1. Clique em **"🗑️ Limpar Lista"**
2. Confirme
3. ✅ Volta para tela inicial

---

## 🎯 Visual do Dashboard

### Tela Principal

```
┌─────────────────────────────────────────┐
│  🏆 Rastreador de Torneio GTA          │
│                                         │
│  [⚙️ Configurar] [🔄 Reset] [🗑️ Limpar]│
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Times: 18 | Vivos: 72 | Mortos: 18     │
│ Total Kills: 18                         │
└─────────────────────────────────────────┘

┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ PPP  │ │ MTL  │ │ SVV  │ │KUSH  │
│ 4/5  │ │ 3/5  │ │ 5/5  │ │ 2/5  │
│ 🎯12 │ │ 🎯 8 │ │ 🎯15 │ │ 🎯 5 │
│      │ │      │ │      │ │      │
│🟩🟩🟩🟩⬜│ │🟩🟩🟩⬜⬜│ │🟩🟩🟩🟩🟩│ │🟩🟩⬜⬜⬜│
└──────┘ └──────┘ └──────┘ └──────┘
```

### Cada Quadrado de Player

- **🟩 Verde** = Player vivo
- **⬜ Cinza** = Player morto
- **Número dentro** = Kills daquele player
- **Clique** = Alterna vivo/morto

---

## 💡 Dicas Importantes

1. **Prepare o roster ANTES da partida começar**
   - Envie a imagem de classificados
   - Ou digite as tags manualmente

2. **Deixe a IA trabalhar durante o jogo**
   - O sistema detecta automaticamente
   - Você só corrige quando necessário

3. **Use a imagem de classificados**
   - É mais rápido que digitar
   - Screenshot da página do campeonato funciona perfeitamente

4. **Não precisa dos nomes dos players**
   - A IA identifica durante o jogo
   - Sistema cria placeholders automáticos (PPP_P1, PPP_P2, etc.)

5. **Reset entre partidas**
   - Mantém os times configurados
   - Economiza tempo entre rounds

---

## 🐛 Resolução de Problemas

### A IA não extraiu os times corretamente

**Solução:** Use o input manual (Opção 2) e digite apenas as tags.

### Sistema não está detectando kills

**Causas possíveis:**
- Killfeed não está visível na tela capturada
- Qualidade de imagem muito baixa

**Solução temporária:** Use a correção manual (clique nos quadrados)

### Quadrados mostram "PPP_P1, PPP_P2" em vez de nomes reais

**Isso é normal!** O sistema criou placeholders porque você não forneceu os nomes. A IA irá tentar detectar os nomes reais durante o jogo. Se não detectar, você pode continuar usando os placeholders - funciona perfeitamente.

### Preciso adicionar/remover times durante a partida

**Ainda não implementado.** Por enquanto:
1. Clique em "🗑️ Limpar Lista"
2. Configure novamente com a lista correta

---

## 📊 Informações Técnicas

### Capacidade
- **Máximo de 20 times** simultaneamente
- **5 players por time** (padrão Battle Royale)
- **Atualização em tempo real** via WebSocket

### Requisitos
- **Backend rodando** (Python FastAPI)
- **Navegador moderno** (Chrome, Edge, Firefox)
- **Porta 3000** disponível

### Tecnologias
- **IA de Visão** (GPT-4o) para extração de tags
- **OCR em tempo real** para detecção de kills
- **WebSocket** para sincronização instantânea

---

## 🆘 Suporte

**Desenvolvedor:** Paulo Eugênio Campos

**Contato:** Através do Luís

**Projeto:** GTA Analytics V2 - Tournament Edition

---

## 📝 Changelog desta Versão

**18/02/2026 - Versão Tournament**

✅ Implementado:
- Upload de imagem de classificados com extração IA
- Input manual simplificado (só tags)
- Visual em quadrados (estilo campeonato)
- Kills mostradas dentro dos quadrados
- Interface 100% em português
- Suporte para times sem nomes de players
- Sistema de placeholder automático
- Prompt IA otimizado para página de classificados

🔄 Melhorado:
- Layout mais compacto
- Cores mais visíveis
- Fluxo mais simples e rápido
- Documentação em português

---

**Desenvolvido com 🚀 por Paulo Eugênio Campos**
