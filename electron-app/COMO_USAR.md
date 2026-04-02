# 🎯 GTA ANALYTICS - GUIA COMPLETO DE USO

**Para:** Luis Otavio (Cliente Final)
**Desenvolvido por:** Paulo Eugenio Campos

---

## 📥 INSTALAÇÃO (PRIMEIRA VEZ)

### Passo 1: Baixar

Baixe o instalador:
- **GTA-Analytics-1.0.0-Setup.exe** (~100 MB)

### Passo 2: Instalar

1. Duplo clique no arquivo baixado
2. Windows pode mostrar aviso "Unknown Publisher"
   - Clique **"More info"** → **"Run anyway"**
3. Instalador abre → Clique **"Next"**
4. Escolha pasta (padrão: `C:\Program Files\GTA Analytics`)
5. Clique **"Install"**
6. Aguarde instalação (~30 segundos)
7. Clique **"Finish"**

✅ **Pronto! App instalado.**

---

## 🚀 USAR O APP

### Primeira Vez

1. **Abrir app:**
   - Menu Iniciar → "GTA Analytics"
   - Ou ícone na área de trabalho

2. **Configurar servidor (apenas 1x):**
   - Clique no ícone ⚙️ (canto superior direito)
   - Verificar URL do servidor: `https://gta-analytics-v2.fly.dev`
   - Ajustar FPS se necessário (0.5 = recomendado)
   - Clicar **"💾 Salvar Configurações"**

3. **Iniciar GTA V:**
   - Abrir GTA V
   - Entrar no servidor Battle Royale
   - Aguardar partida começar

4. **Iniciar captura:**
   - Voltar para GTA Analytics app
   - Clicar **"▶️ Iniciar Captura"**
   - Status muda para 🟢 "Capturando..."

5. **Monitorar:**
   - Ver frames enviados em tempo real
   - Log mostra cada frame capturado
   - Dashboard estrategista (abrir link)

6. **Parar quando terminar:**
   - Clicar **"⏹️ Parar"**
   - Status muda para ⚫ "Parado"

---

## 💡 USAR EM EVENTOS/TORNEIOS

### Setup Pré-Evento

**1-2 dias antes:**
- ✅ Testar captura com GTA
- ✅ Confirmar dashboard funciona
- ✅ Verificar internet (10 Mbps+)

**1 hora antes:**
- ✅ Abrir GTA Analytics
- ✅ Verificar servidor online
- ✅ Deixar preparado

### Durante Evento

**Início:**
1. GTA V abre → partida inicia
2. Clicar **"Iniciar Captura"** no app
3. Minimizar app (continua rodando)
4. **Estrategista** abre dashboard no celular/tablet
5. Jogar normalmente!

**Durante partida:**
- App roda em background
- Ícone na bandeja do sistema (🎮)
- Estrategista vê kills ao vivo

**Fim:**
- Clicar **"Parar"** quando partida terminar
- Ver resumo no log

### Múltiplas Partidas

Não precisa fechar o app:
- Partida 1: Iniciar → Parar
- Partida 2: Iniciar → Parar
- Partida 3: Iniciar → Parar
- Etc.

---

## 📊 DASHBOARD ESTRATEGISTA

### Abrir Dashboard

**Opção 1:** Pelo app
- Clicar ícone 📊 (canto superior)
- Abre browser automaticamente

**Opção 2:** Manualmente
- Browser: `https://gta-analytics-v2.fly.dev/strategist`

**Opção 3:** Celular/Tablet
- Mesmo link funciona!
- Mobile-first design

### O Que o Estrategista Vê

- ✅ **Kills em tempo real** (feed atualiza sozinho)
- ✅ **Times vivos** (quantos players cada time tem)
- ✅ **Ranking geral** (quem matou mais)
- ✅ **Estatísticas** (total kills, mortos, vivos)
- ✅ **Export Excel** (botão para baixar relatório)

---

## ⚙️ CONFIGURAÇÕES

### FPS (Taxa de Captura)

**O que é:**
- Quantos frames por segundo capturar
- **0.5 FPS** = 1 frame a cada 2 segundos (padrão)
- **1.0 FPS** = 1 frame por segundo
- **2.0 FPS** = 2 frames por segundo

**Recomendação:**
- **Eventos curtos (1h):** 1.0 FPS
- **Eventos médios (3h):** 0.5 FPS ⭐
- **Eventos longos (6h):** 0.3 FPS

**Por quê:**
- Mais FPS = mais responsivo, mas mais custo API
- Menos FPS = mais econômico

**Custos estimados:**
| FPS | Custo/hora | Custo evento 3h |
|-----|------------|-----------------|
| 0.3 | $0.08 | $0.24 |
| 0.5 | $0.13 | $0.40 ⭐ |
| 1.0 | $0.27 | $0.80 |
| 2.0 | $0.54 | $1.60 |

### Mudar Servidor

**Quando:**
- Se tiver servidor próprio
- Se Fly.io mudar URL

**Como:**
1. Clique ⚙️ Configurações
2. Edite "Servidor Backend"
3. Formato: `https://seu-servidor.com`
4. Clique "Salvar"

---

## 🎮 DICAS E TRUQUES

### Para Melhor Captura

✅ **Faça:**
- Rodar GTA em **Windowed Borderless** (melhor captura)
- Manter app aberto durante partida
- Verificar internet estável

❌ **Evite:**
- Fullscreen exclusivo (pode dar tela preta)
- Fechar app durante captura
- Internet instável (4G fraco)

### Economizar Custos

- ✅ Usar FPS 0.5 ou menos
- ✅ Parar captura entre partidas
- ✅ Testar com FPS 0.3 (eventos longos)

### Performance

Se PC está lento:
- ✅ Fechar programas desnecessários
- ✅ Reduzir FPS para 0.3
- ✅ Fechar Discord/Overlays

---

## 🔧 PROBLEMAS E SOLUÇÕES

### App não abre

**Problema:** Duplo clique não funciona

**Soluções:**
1. Clicar direito → "Executar como administrador"
2. Verificar antivírus não bloqueou
3. Reinstalar app

---

### GTA não captura (0 frames)

**Problema:** App diz "GTA não detectado"

**Soluções:**
1. **Mudar modo de tela GTA:**
   - GTA Settings → Graphics → Display Mode
   - Trocar para **"Windowed Borderless"** ⭐
   - Aplicar e testar

2. **Verificar processo:**
   - Abrir Task Manager (Ctrl+Shift+Esc)
   - Procurar "GTA5.exe"
   - Se não estiver, GTA não iniciou

3. **Atualizar drivers GPU:**
   - NVIDIA: GeForce Experience
   - AMD: Adrenalin

> O app detecta o GTA automaticamente pelo processo `GTA5.exe`. Não é necessário nenhuma configuração extra.

---

### Antivírus bloqueia

**Problema:** Windows Defender ou outro antivírus bloqueia

**Solução:**
1. Adicionar exceção:
   - Windows Security → Virus & threat protection
   - Manage settings → Add exclusion
   - Escolher pasta: `C:\Program Files\GTA Analytics`

2. Ou clicar "Allow" quando aviso aparecer

---

### Frames não chegam no servidor

**Problema:** App captura mas dashboard não atualiza

**Verificar:**
1. **Internet funcionando?**
   - Testar: abrir google.com

2. **Servidor online?**
   - Abrir: `https://gta-analytics-v2.fly.dev/monitor`
   - Deve mostrar "Server Online"

3. **Firewall bloqueando?**
   - Adicionar exceção para GTA Analytics

---

### Dashboard não abre

**Problema:** Clicar 📊 não faz nada

**Solução:**
- Abrir manualmente no browser:
- `https://gta-analytics-v2.fly.dev/strategist`

---

## 📱 CELULAR/TABLET

### Estrategista Mobile

**Como:**
1. Conectar celular/tablet na mesma WiFi
2. Abrir browser (Chrome, Safari)
3. Ir para: `https://gta-analytics-v2.fly.dev/strategist`
4. Adicionar à tela inicial (opcional)

**Funciona:**
- ✅ Android (Chrome)
- ✅ iOS/iPhone (Safari)
- ✅ Tablet
- ✅ Auto-atualiza

---

## 💾 EXPORTAR RELATÓRIO EXCEL

### Durante Partida

1. Abrir dashboard estrategista
2. Scroll até final da página
3. Clicar **"📊 Exportar Excel"**
4. Escolher formato:
   - **Luis Format** (3 abas: Vivos, Ranking, Kill Feed) ⭐
   - Standard Format
   - Advanced Format

5. Arquivo baixa automaticamente
6. Abrir no Excel/LibreOffice

### Após Partida

Mesmo processo! Dados ficam salvos.

---

## 🎯 CHECKLIST PRÉ-EVENTO

**1 semana antes:**
- [ ] Instalar GTA Analytics (não precisa instalar Python)
- [ ] Testar captura 1x
- [ ] Confirmar dashboard funciona

**1 dia antes:**
- [ ] Testar novamente
- [ ] Verificar versão app (deve ser 1.0.0+)
- [ ] Confirmar internet estável

**1 hora antes:**
- [ ] Abrir GTA Analytics
- [ ] Verificar servidor online
- [ ] Testar com GTA (5 min)
- [ ] Avisar estrategista abrir dashboard

**Durante evento:**
- [ ] Iniciar captura quando partida começar
- [ ] Minimizar app
- [ ] Jogar!

**Após evento:**
- [ ] Parar captura
- [ ] Exportar Excel
- [ ] Fechar app (ou deixar para próxima)

---

## 📞 SUPORTE

**Problemas?**

1. **Verificar este guia primeiro** (99% das dúvidas estão aqui)
2. **Ver log do app** (mostra erros específicos)
3. **Contatar desenvolvedor:**
   - Developer: Paulo Eugenio Campos
   - Via: Vitor (seu contato)

**Informações úteis para suporte:**
- Versão do app (ex: 1.0.0)
- Versão Windows (ex: Windows 11)
- Mensagem de erro exata
- Screenshot do problema

---

## 🎉 PRONTO!

Agora você sabe tudo para usar GTA Analytics!

**Resumo simples:**
1. Instalar app (1x)
2. Abrir GTA V
3. Clicar "Iniciar Captura"
4. Estrategista abre dashboard
5. Jogar!

**Qualquer dúvida:** Consultar este guia ou contatar suporte.

---

**Bom jogo! 🎮**
