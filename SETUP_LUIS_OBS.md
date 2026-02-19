# 🎮 GUIA DE CONFIGURAÇÃO - LUIS (JOGADOR)

## Sistema OBS Browser Source para GTA Analytics

---

## 📋 **O QUE VOCÊ VAI PRECISAR:**

1. **OBS Studio** (grátis) - https://obsproject.com
2. **Conexão com internet**
3. **5-10 minutos** para configurar (só primeira vez)

---

## ⚙️ **CONFIGURAÇÃO INICIAL (FAZER 1x)**

### **PASSO 1: Baixar e Instalar OBS**

1. Abra https://obsproject.com
2. Clique em **"Download"**
3. Baixe a versão **Windows** (aproximadamente 300MB)
4. Instale (Next → Next → Finish)
5. Abra o **OBS Studio**

**Tempo:** 5-10 minutos

---

### **PASSO 2: Adicionar Browser Source**

1. No OBS, olhe na área **"Sources"** (parte de baixo da janela)
2. Clique no botão **"+"** (adicionar fonte)
3. Escolha **"Browser"** da lista
4. Digite um nome: **"GTA Analytics"**
5. Clique **OK**

![Adicionar Browser Source](https://i.imgur.com/example.png)

---

### **PASSO 3: Configurar a URL**

Na janela que abrir, preencha **EXATAMENTE** assim:

```
URL: https://gta-analytics-v2.fly.dev/capture-obs
Width: 1920
Height: 1080
FPS: 1
```

**Marque as caixas:**
- ☑️ **Refresh browser when scene becomes active**
- ☑️ **Shutdown source when not visible**

Clique **OK**

![Configurar URL](https://i.imgur.com/example2.png)

---

### **PASSO 4: Permitir Captura de Tela (IMPORTANTE!)**

Quando a página carregar no OBS, ela vai pedir permissão para capturar a tela.

1. Uma janela do Windows vai aparecer perguntando qual tela você quer compartilhar
2. **ESCOLHA UMA DAS OPÇÕES ABAIXO:**

**🎯 OPÇÃO 1 (RECOMENDADA): Janela do GTA V**
- Selecione **"Janela: Grand Theft Auto V"** da lista
- ✅ Funciona com **QUALQUER RESOLUÇÃO** (1920x1080, 1100x1080, etc.)
- ✅ Captura **SÓ O JOGO** (não pega Discord, Spotify, etc.)
- ✅ **Mais eficiente** (menos dados, upload mais rápido)
- ✅ **Melhor para resoluções competitivas** (1100x1080, 1440x1080, etc.)

**🖥️ OPÇÃO 2: Tela Inteira**
- Selecione **"Tela Inteira"** ou **"Este Monitor"**
- ⚠️ Captura TUDO que está na tela (incluindo Discord, navegador, etc.)
- ⚠️ Pode ter informações pessoais visíveis

3. Clique em **"Compartilhar"**

**⚠️ ATENÇÃO:** Você precisa fazer isso **TODA VEZ** que abrir o OBS. É limitação de segurança do navegador, não tem como automatizar. **MAS SÃO APENAS 2 CLIQUES!**

---

### ✅ **PRONTO! Configuração completa**

Você deve ver na fonte do OBS:

```
🟢 Conectado
📐 Resolução detectada: 1100x1080 (ou a resolução que você joga)
Frames capturados: 0
Uploads sucesso: 0
Último upload: --:--:--
```

**O sistema detecta automaticamente sua resolução!** Não precisa configurar nada.

---

## 🎮 **USO DIÁRIO (TODA VEZ QUE FOR JOGAR)**

### **Passo 1: Abrir OBS**
- Abra o **OBS Studio**
- Aguarde 2-3 segundos
- A página vai carregar automaticamente

### **Passo 2: Permitir Captura**
- Janela do Windows aparece
- Selecione **"Tela Inteira"** ou **"GTA V"**
- Clique **"Compartilhar"**
- Status muda para **🟢 Conectado**

### **Passo 3: Jogar**
- Abra o **GTA V**
- Entre no servidor
- **JOGUE NORMALMENTE**
- Não precisa fazer mais NADA

O sistema vai:
- ✅ Capturar 1 frame por segundo automaticamente
- ✅ Enviar para nuvem
- ✅ Processar com AI
- ✅ Mostrar no dashboard do Vitor em tempo real

---

## 📊 **MONITORANDO O SISTEMA**

Dentro do OBS, você vai ver:

```
┌─────────────────────────────────┐
│ 🟢 Conectado                    │
│ Frames capturados: 1247         │
│ Uploads sucesso: 1247           │
│ Erros: 0                        │
│ Último upload: 18:45:32         │
└─────────────────────────────────┘
```

**Se estiver assim, está funcionando!**

---

## ❓ **PERGUNTAS FREQUENTES (FAQ)**

### **P: Jogo em 1100x1080 (resolução competitiva), vai funcionar?**
✅ **SIM!** O sistema detecta automaticamente sua resolução. Não importa se é 1920x1080, 1100x1080, 1440x900, ou qualquer outra. **Funciona com TODAS as resoluções.**

### **P: Preciso abrir o site no navegador como antes?**
❌ **NÃO!** Agora você só precisa abrir o OBS. A captura acontece dentro do OBS, não precisa navegador aberto.

### **P: O OBS que eu já uso para gravar vai funcionar?**
✅ **SIM!** Você pode usar o mesmo OBS que já tem. Só adiciona mais uma "fonte" (Browser Source). **NÃO INTERFERE** com suas gravações/streams.

### **P: Tem conflito se eu estiver gravando/streamando ao mesmo tempo?**
❌ **NÃO!** O Analytics funciona em paralelo. Você pode:
- Gravar gameplay
- Fazer live na Twitch/YouTube
- Usar o Analytics
**TUDO AO MESMO TEMPO** sem conflito.

### **P: Toda vez que abrir o OBS precisa permitir captura?**
✅ **SIM.** É limitação de segurança do navegador. **MAS SÃO APENAS 2 CLIQUES:**
1. Selecionar "Janela: Grand Theft Auto V"
2. Clicar "Compartilhar"

**Leva 5 segundos!**

### **P: E se eu esquecer de permitir a captura?**
⚠️ O sistema vai mostrar **"Permissão negada"** no status. É só apertar F5 na fonte do OBS e permitir de novo.

---

## ⚠️ **PROBLEMAS E SOLUÇÕES**

### **Problema: Status mostra 🔴 Erro**

**Solução:**
1. Clique direito na fonte "GTA Analytics"
2. Escolha **"Interact"**
3. Veja a mensagem de erro
4. Aperte F5 para recarregar

---

### **Problema: Frames capturados aumenta mas uploads fica em 0**

**Solução:**
- Verifique sua internet
- Tente recarregar a fonte (F5)
- Se continuar, avise o suporte

---

### **Problema: Janela de permissão não aparece**

**Solução:**
1. Remova a fonte "GTA Analytics"
2. Adicione novamente seguindo o PASSO 2
3. Quando a página carregar, permita captura

---

### **Problema: OBS está lento/travando**

**Solução:**
- Verifique se tem outros programas pesados abertos
- OBS usa ~200MB de RAM, é normal
- Se travar muito, feche e abra o OBS novamente

---

## 💡 **DICAS PROFISSIONAIS**

### **Dica 1: Esconder a fonte**
Se não quiser ver a página do analytics no OBS:
1. Clique na fonte "GTA Analytics"
2. Aperte **Ctrl+H** (ocultar)
3. Continua funcionando em background!

### **Dica 2: Fazer stream + Analytics**
Você pode fazer live E usar o analytics ao mesmo tempo:
- Adicione o "GTA Analytics" em uma cena separada
- Stream em outra cena
- Ambos funcionam simultaneamente!

### **Dica 3: Ver os logs**
Para debug:
1. Clique direito na fonte
2. **"Interact"**
3. Aperte **F12**
4. Veja o console com logs detalhados

---

## 📞 **SUPORTE**

Se tiver qualquer problema:
1. Tire print da tela do OBS
2. Tire print do erro (se houver)
3. Envie para o suporte

**Links úteis:**
- Dashboard (Vitor vê aqui): https://gta-analytics-v2.fly.dev/viewer
- Status do sistema: https://gta-analytics-gateway.fly.dev/health

---

## 🔄 **ATUALIZAÇÕES**

O sistema atualiza automaticamente. Você não precisa fazer nada!

Se houver mudanças importantes, você será avisado.

---

## ✅ **CHECKLIST RÁPIDO**

Antes de cada partida, verifique:

- [ ] OBS aberto
- [ ] Fonte "GTA Analytics" visível (ou oculta)
- [ ] Status: 🟢 Conectado
- [ ] Frames capturados aumentando
- [ ] Uploads sucesso aumentando
- [ ] Erros = 0

**Se todos ✅ = Tudo funcionando!**

---

**Última atualização:** 19/02/2026
**Versão do sistema:** 2.0 (OBS Browser Source)
