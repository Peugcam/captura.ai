# 🎥 COMO CONFIGURAR OBS PARA CAPTURAR NARUTO ONLINE

## 🔧 SOLUÇÃO RÁPIDA (Escolha UMA das opções abaixo)

---

## ✅ OPÇÃO 1: Captura de Janela (MAIS FÁCIL)

### Passo a passo:

1. **No OBS, na seção "Fontes" (embaixo):**
   - Clique no botão `+` (adicionar)
   - Escolha: **"Captura de Janela"**

2. **Na janela que abrir:**
   - Nome: "Naruto Online" (ou qualquer nome)
   - Clique **OK**

3. **Configure a captura:**
   - **Janela:** Selecione a janela do Naruto Online da lista
     - Pode aparecer como: "Naruto Online - Google Chrome"
     - Ou: "Naruto Online - Mozilla Firefox"
     - Ou: nome do navegador/aplicativo

   - **Método de Captura:**
     - Tente primeiro: "Captura Automática"
     - Se não funcionar: "BitBlt do Windows 10 (mais rápido)"

   - **Prioridade de Correspondência:** "Título da janela deve corresponder"

   - Marque: ☑️ "Capturar cursor"

   - Clique **OK**

4. **Ajuste o tamanho:**
   - Arraste os cantos da fonte no preview
   - Ou clique com botão direito → Transformar → "Ajustar à tela"

---

## ✅ OPÇÃO 2: Captura de Tela (SE OPÇÃO 1 NÃO FUNCIONAR)

### Passo a passo:

1. **No OBS, na seção "Fontes":**
   - Clique no botão `+`
   - Escolha: **"Captura de Tela"**

2. **Configure:**
   - Nome: "Tela Principal"
   - Clique **OK**

3. **Selecione o monitor:**
   - **Tela:** Escolha o monitor onde está o Naruto
     - Normalmente é "Monitor 1" ou "Monitor Principal"

   - Marque: ☑️ "Capturar cursor"

   - Clique **OK**

**DESVANTAGEM:** Vai capturar a tela INTEIRA (incluindo outras janelas abertas)

---

## ✅ OPÇÃO 3: Captura de Navegador (SE FOR JOGO DE NAVEGADOR)

### Se Naruto Online roda no navegador:

1. **No OBS, na seção "Fontes":**
   - Clique no botão `+`
   - Escolha: **"Navegador"** (BrowserSource)

2. **Configure:**
   - Nome: "Naruto Online"
   - **URL:** Cole a URL do jogo (ex: https://narutoonline.com/game)
   - **Largura:** 1920
   - **Altura:** 1080
   - Marque: ☑️ "Desligar fonte quando não estiver visível"
   - Clique **OK**

**OBS:** Isso abre o jogo DENTRO do OBS (pode precisar fazer login de novo)

---

## ⚠️ PROBLEMAS COMUNS

### "Tela preta no OBS"

**Causas possíveis:**

1. **Aceleração de hardware do navegador:**

   **Chrome/Edge:**
   - Abra: `chrome://settings/system`
   - DESLIGUE: ❌ "Usar aceleração de hardware quando disponível"
   - Reinicie o navegador

   **Firefox:**
   - Configurações → Geral → Desempenho
   - DESLIGUE: ❌ "Usar aceleração de hardware quando disponível"
   - Reinicie o Firefox

2. **Execute OBS como Administrador:**
   - Feche o OBS
   - Clique com botão direito no ícone do OBS
   - Escolha: "Executar como administrador"
   - Tente adicionar a fonte novamente

3. **Modo de compatibilidade:**
   - No método de captura, tente trocar:
     - De "Captura Automática" → "BitBlt do Windows"
     - Ou: "Windows Graphics Capture"

---

## 🎮 TESTE RÁPIDO

### Depois de configurar, você deve ver:

**No preview do OBS:**
- ✅ Imagem do Naruto Online aparecendo
- ✅ Movimentos do jogo sendo capturados
- ✅ SEM tela preta

**Se ainda estiver com tela preta:**

1. Mude para "Captura de Tela" (Opção 2)
2. Ou tente "Captura de Jogo" (se for app desktop)

---

## 📋 CHECKLIST DE CONFIGURAÇÃO

- [ ] OBS Studio aberto
- [ ] Fonte adicionada (Janela/Tela/Navegador)
- [ ] Preview mostrando o jogo (NÃO tela preta)
- [ ] WebSocket ativado (Ferramentas → WebSocket)
- [ ] Porta 4455
- [ ] Senha: ZNx3v4LjLVCgbTrO

**Tudo OK? → Pronto para testar a captura!**

---

## 🆘 AINDA NÃO FUNCIONA?

### Alternativa: Use qualquer outra janela para testar

**Para testar se o sistema funciona:**

1. Abra qualquer site/vídeo no navegador
2. Configure OBS para capturar essa janela
3. Execute o teste normalmente

**O objetivo é só ver se:**
- ✅ OBS captura alguma coisa
- ✅ Cliente conecta ao OBS
- ✅ Frames são enviados ao backend

Não precisa ser o Naruto Online especificamente para o teste!

---

## 💡 DICA PRO

Se você só quer testar o sistema (sem o jogo):

1. Abra o YouTube
2. Coloque qualquer vídeo em tela cheia
3. Configure OBS para capturar essa janela
4. Execute o teste

Vai funcionar do mesmo jeito! 🚀
