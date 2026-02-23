# 🎮 CAPTURAR LAUNCHER DO NARUTO ONLINE NO OBS

## 🚀 SOLUÇÃO PARA JOGOS DE LAUNCHER

---

## ✅ MÉTODO 1: Captura de Jogo (RECOMENDADO)

### Passo a passo:

1. **PRIMEIRO: Abra o Naruto Online (launcher)**
   - Execute o jogo ANTES de configurar o OBS
   - Deixe o jogo rodando

2. **No OBS:**
   - Clique no `+` em "Fontes"
   - Escolha: **"Captura de Jogo"**

3. **Configure:**
   - **Nome:** "Naruto Online"
   - Clique **OK**

4. **Configurações da Captura:**
   - **Modo:** "Capturar qualquer janela em tela cheia"
   - OU: **Modo:** "Capturar janela específica"
     - **Janela:** Selecione o Naruto Online da lista

   - **Método de Captura:** "Captura automática"

   - Marque: ☑️ "Capturar cursor"

   - **Se tela preta:**
     - Mude para: "Windows 10 (1903 e superior)"
     - Ou: "Compatibilidade com anticheat"

   - Clique **OK**

5. **Aguarde alguns segundos**
   - A captura pode demorar 5-10 segundos para aparecer
   - Se não aparecer, veja "Solução para Tela Preta" abaixo

---

## ✅ MÉTODO 2: Captura de Janela (MAIS COMPATÍVEL)

### Se o Método 1 não funcionar:

1. **No OBS:**
   - Clique no `+` em "Fontes"
   - Escolha: **"Captura de Janela"**

2. **Configure:**
   - **Nome:** "Naruto Launcher"
   - Clique **OK**

3. **Configurações:**
   - **Janela:** Procure por "Naruto" ou nome do launcher
     - Pode aparecer como: "[NarutoOnline.exe]"
     - Ou: "[launcher.exe]: Naruto Online"

   - **Método de Captura:** Tente nesta ordem:
     1. "Windows Graphics Capture" ← TENTE ESTE PRIMEIRO
     2. "BitBlt do Windows 10"
     3. "Captura Automática"

   - Marque: ☑️ "Capturar cursor"

   - Clique **OK**

---

## ✅ MÉTODO 3: Captura de Tela (SEMPRE FUNCIONA)

### Garantido para qualquer jogo:

1. **No OBS:**
   - Clique no `+` em "Fontes"
   - Escolha: **"Captura de Tela"**

2. **Configure:**
   - **Tela:** Selecione o monitor onde está o jogo
   - Marque: ☑️ "Capturar cursor"
   - Clique **OK**

**NOTA:** Vai capturar TUDO que estiver na tela (outras janelas, barra de tarefas, etc)

---

## ⚠️ SOLUÇÃO PARA TELA PRETA

### Se qualquer método mostrar tela preta:

### 1. Execute OBS como Administrador:

```
1. Feche o OBS
2. Feche o Naruto Online
3. Clique com botão direito no OBS
4. "Executar como administrador"
5. Abra o Naruto Online novamente
6. Adicione a fonte novamente
```

### 2. Execute Naruto como Administrador:

```
1. Feche o Naruto
2. Feche o OBS
3. Clique com botão direito no launcher do Naruto
4. "Executar como administrador"
5. Abra o OBS normalmente
6. Adicione a fonte
```

### 3. Mude o Método de Captura:

Na configuração da fonte:

- **Se estava:** "Captura de Jogo"
  → **Mude para:** "Captura de Janela"

- **Se estava:** "BitBlt"
  → **Mude para:** "Windows Graphics Capture"

- **Se estava:** "Automático"
  → **Mude para:** "Windows 10 (1903 e superior)"

### 4. Compatibilidade com Anticheat:

Alguns jogos têm proteção contra captura:

1. Na fonte de "Captura de Jogo"
2. Marque: ☑️ "Compatibilidade com anticheat"
3. Marque: ☑️ "Capturar terceiros (como sobreposições)"

---

## 🎯 TESTE RÁPIDO

### Verificar se está funcionando:

**No preview do OBS você deve ver:**
- ✅ O jogo Naruto Online rodando
- ✅ Movimentos e animações
- ✅ NÃO tela preta
- ✅ NÃO apenas ícone/logo estático

---

## 💡 DICA: Qual método escolher?

### Para Naruto Online (launcher):

**1ª TENTATIVA:** Captura de Janela + Windows Graphics Capture
- Funciona em 90% dos casos
- Baixo impacto de performance

**2ª TENTATIVA:** Captura de Jogo + Compatibilidade com anticheat
- Funciona se o jogo tiver proteção

**3ª TENTATIVA (GARANTIDA):** Captura de Tela
- Sempre funciona
- Captura tudo (não só o jogo)

---

## 📋 CHECKLIST

Antes de rodar o teste:

- [ ] Naruto Online aberto e rodando
- [ ] OBS mostrando o jogo no preview (NÃO tela preta)
- [ ] Você consegue ver animações/movimentos do jogo no OBS
- [ ] WebSocket ativado (Ferramentas → WebSocket)
- [ ] Porta: 4455
- [ ] Senha: ZNx3v4LjLVCgbTrO

**Tudo OK? → Pode executar `RODAR_TESTE.bat`!**

---

## 🆘 AINDA NÃO FUNCIONA?

### Última solução (SEMPRE FUNCIONA):

1. Coloque o Naruto Online em **modo janela** (não tela cheia)
2. Use **"Captura de Tela"** no OBS
3. Execute o teste

Isso captura tudo, mas GARANTE que vai funcionar!

---

## 🎮 CONFIGURAÇÕES DO JOGO (IMPORTANTE)

### Para melhor captura:

**No Naruto Online (configurações gráficas):**

1. **Modo de Tela:**
   - TELA CHEIA → Pode dar tela preta no OBS
   - **JANELA** ou **JANELA SEM BORDAS** → Funciona melhor

2. **VSync:**
   - Pode deixar ligado (não afeta)

3. **Resolução:**
   - 1920x1080 (mesmo que configuramos no script)

---

**Me avisa qual método funcionou para você!** 🚀

Depois que o jogo aparecer no OBS, é só executar `RODAR_TESTE.bat` e testar! 👍
