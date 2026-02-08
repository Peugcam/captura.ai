# 🎮 Como Usar o Dashboard - Naruto Online

## 📋 Passo a Passo:

### 1️⃣ Abrir o Dashboard
- Duplo clique em `dashboard.html`
- Ou abra manualmente no navegador

### 2️⃣ Preparar o Jogo
- Abra Naruto Online
- Entre em combate
- Deixe o jogo visível na tela

### 3️⃣ Iniciar Captura
1. No dashboard, clique em **"▶️ INICIAR CAPTURA"**
2. O navegador vai pedir para selecionar uma janela
3. **IMPORTANTE:** Selecione a aba/janela do **Naruto Online**
4. Clique em **"Compartilhar"**

### 4️⃣ Durante a Captura
- O dashboard mostra:
  - ✅ Frames capturados
  - ✅ Tempo decorrido
  - ✅ FPS médio
  - ✅ Log de eventos

### 5️⃣ Parar a Captura

**OPÇÃO 1 - Botão Stop (pode travar):**
- Clique em **"⏹️ PARAR CAPTURA"**
- Se travar, use a Opção 2

**OPÇÃO 2 - Fechar a aba (recomendado):**
- Simplesmente **feche a aba** do dashboard
- Os frames já foram enviados e estão sendo processados
- ✅ Não perde nada!

**OPÇÃO 3 - Recarregar a página:**
- Pressione **F5** ou **CTRL+R**
- Isso para a captura e reseta o dashboard

### 6️⃣ Ver Resultados

**No terminal do backend:**
```
Frames Received: 50
Kills Detected: 15
```

**No diretório `backend/exports/`:**
- Arquivo Excel com todos os eventos
- Nome: `naruto_stats_YYYYMMDD_HHMMSS.xlsx`

---

## ⚙️ Configurações do Dashboard

**FPS de Captura:**
- 1 FPS = Econômico (1 frame por segundo)
- 2 FPS = Recomendado (2 frames por segundo)
- 3 FPS = Alta frequência (3 frames por segundo)

**Qualidade JPEG:**
- 50% = Rápido, menos qualidade
- 60% = Balanceado (recomendado)
- 80% = Alta qualidade, mais lento

---

## 🐛 Problemas Comuns

### Dashboard travou ao parar?
✅ **Solução:** Feche a aba e abra de novo
- Os dados já foram salvos
- Nada é perdido

### Não conecta ao gateway?
✅ **Verifique:** Backend está rodando?
```bash
# Deve estar rodando:
backend/main_complete.py
```

### Não captura nada?
✅ **Verifique:**
- Selecionou a janela certa?
- Naruto Online está aberto?
- Gateway está rodando? (localhost:8000)

---

## 💡 Dicas

1. **Deixe o jogo em modo janela** (não fullscreen)
2. **Resolução 1920x1080 ou maior** para melhor detecção
3. **Capture durante combate ativo** para mais eventos
4. **Feche o dashboard** quando terminar (mais seguro que o botão Stop)

---

## 📊 O que o Sistema Detecta

✅ Dano causado/recebido
✅ Jutsus e habilidades usadas
✅ Nomes de ninjas/jogadores
✅ Barras de HP e Chakra
✅ Combos e critical hits
✅ Mensagens de vitória/derrota
✅ Battle log completo

---

**Criado por:** Paulo Eugenio Campos
**Data:** 2026-02-06
**Sistema:** GTA Analytics V2 (adaptado para Naruto Online)
