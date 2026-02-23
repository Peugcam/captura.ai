# 🎯 CONFIGURAR OBS PARA CAPTURAR SÓ O NARUTO

## ❌ PROBLEMA ATUAL:

Você está usando **"Captura de Monitor"**:
- Captura TODA a tela
- Quando você troca de janela/aba, o OBS captura outra coisa
- Não é ideal para streaming/captura de jogo específico

---

## ✅ SOLUÇÃO: Usar "Captura de Janela"

Isso faz o OBS capturar APENAS o Naruto, mesmo se você mudar para outra janela!

---

## 📋 PASSO A PASSO NO OBS:

### 1. REMOVER A FONTE ATUAL

1. No OBS, vá na seção **"Fontes"** (embaixo)
2. Encontre a fonte: **"Captura de monitor"**
3. **Clique com botão DIREITO** nela
4. Escolha: **"Remover"**
5. Confirme: **"Sim"**

---

### 2. ADICIONAR CAPTURA DE JANELA

1. Clique no botão **`+`** na seção "Fontes"

2. Escolha: **"Captura de Janela"**

3. **Nome da fonte:** "Naruto Online"

4. Clique **OK**

---

### 3. CONFIGURAR A CAPTURA

Uma janela de configuração vai abrir:

#### **Janela:**
- Clique no dropdown **"Janela:"**
- Procure na lista pela janela do Naruto Online
- Pode aparecer como:
  - `[chrome.exe]: Naruto Online`
  - `[firefox.exe]: Naruto Online`
  - `[NarutoLauncher.exe]: Naruto`
  - `[launcher.exe]: Naruto Online`

**IMPORTANTE:** Selecione a janela ESPECÍFICA do jogo!

#### **Método de Captura:**
- Escolha: **"Windows Graphics Capture"** ← RECOMENDADO
- Alternativa: "BitBlt do Windows 10" (se o primeiro não funcionar)

#### **Prioridade de Correspondência:**
- Escolha: **"Título da janela deve corresponder"**

#### **Opções:**
- ☑️ Marque: "Capturar cursor"
- ☐ Desmarque: "Capturar somente clientes" (deixe desmarcado)

#### Clique **OK**

---

### 4. AJUSTAR TAMANHO

1. A janela do Naruto vai aparecer no preview do OBS

2. **Se estiver pequena ou desalinhada:**
   - Clique com botão DIREITO na fonte
   - Escolha: **"Transformar"**
   - Escolha: **"Ajustar à tela"**

3. Pronto! ✅

---

## 🎯 RESULTADO:

**AGORA:**
- ✅ OBS captura APENAS a janela do Naruto Online
- ✅ Você pode abrir Chrome, Discord, etc.
- ✅ OBS continua mostrando só o Naruto
- ✅ Mesmo se minimizar e abrir de novo, OBS mantém o Naruto

**TESTE:**
1. Com o OBS aberto (mostrando Naruto no preview)
2. Abra outra janela (Chrome, Discord, etc.)
3. Olhe no preview do OBS
4. Deve continuar mostrando o Naruto! ✅

---

## ⚠️ PROBLEMAS COMUNS:

### "A janela do Naruto não aparece na lista"

**Solução:**
1. Certifique-se que o Naruto está ABERTO
2. Feche a janela de configuração do OBS
3. Tente adicionar a fonte novamente
4. Se ainda não aparecer, use "Captura de Jogo" ao invés

---

### "Tela preta no OBS"

**Solução 1:** Mude o método de captura
- De: "Captura Automática"
- Para: **"Windows Graphics Capture"**

**Solução 2:** Execute ambos como Admin
1. Feche OBS e Naruto
2. Botão direito no OBS → "Executar como administrador"
3. Botão direito no Naruto → "Executar como administrador"
4. Adicione a fonte novamente

---

### "A janela some quando fecho o Naruto"

**Normal!** A fonte só captura quando o jogo está aberto.

Quando o Naruto fechar, o OBS vai mostrar tela preta até você abrir o jogo novamente.

---

## 🎮 ALTERNATIVA: Captura de Jogo

Se "Captura de Janela" não funcionar:

1. Clique `+` em Fontes
2. Escolha: **"Captura de Jogo"**
3. **Modo:** "Capturar janela específica"
4. **Janela:** Selecione o Naruto Online
5. OK

---

## 📝 VERIFICAÇÃO FINAL:

- [ ] OBS mostra o Naruto no preview
- [ ] Quando você troca de janela, OBS continua mostrando Naruto
- [ ] Quando você volta pro Naruto, continua funcionando
- [ ] Sem tela preta

**Tudo OK?** → Pode executar o capturador novamente! ✅

---

**Me avise se conseguiu configurar ou se precisa de mais ajuda!** 🚀
