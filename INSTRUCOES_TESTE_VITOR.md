# 📋 Instruções de Teste - Sistema de Curadoria Manual

**Para**: Vitor (Cliente)
**De**: Paulo (Desenvolvedor)
**Data**: 18/02/2026
**Assunto**: Como testar o novo Modo Curador

---

## ✅ PROBLEMA RESOLVIDO

Você agora pode **editar manualmente** os status dos jogadores sem que a IA sobrescreva suas edições!

O novo **Modo Curador** dá controle total para você ajustar quem está vivo/morto durante a partida.

---

## 🚀 Como Iniciar o Sistema

### Passo 1: Iniciar o Backend

Abra um terminal (PowerShell ou CMD) e rode:

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\backend

# Se "python" não funcionar, tente um desses:
python main_websocket.py
# OU
python3 main_websocket.py
# OU
py main_websocket.py
```

**Você deve ver**:
```
INFO:     Uvicorn running on http://0.0.0.0:3000
INFO:     WebSocket route registered at /events
```

### Passo 2: Abrir o Dashboard

Abra no navegador (Chrome recomendado):
```
C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\dashboard-tournament.html
```

**Você deve ver**:
- 🟢 Conectado (canto superior direito)
- Botão "⚙️ Configurar Torneio"

---

## 🎮 Como Configurar o Torneio

### Opção A: Inserir Tags Manualmente (RECOMENDADO para teste)

1. Clique em **"⚙️ Configurar Torneio"**
2. Role até **"✏️ Opção 2: Input Manual"**
3. Digite as tags dos times que vão jogar (uma por linha):

```
PPP
MTL
SVV
KUSH
LLL
FPS
GRN
```

4. Clique em **"✅ Iniciar Torneio"**
5. Você verá os times carregados em grid

### Opção B: Upload de Imagem dos Classificados

1. Clique em **"⚙️ Configurar Torneio"**
2. Clique em **"📁 Clique para fazer upload da imagem"**
3. Selecione a screenshot da página de classificados
4. Clique em **"🤖 Extrair Times com IA"**
5. Aguarde extração (5-10 segundos)

---

## 🎨 Como Usar o Modo Curador

### 1. Ativar Modo Curador

Depois de carregar o torneio:

1. Clique no botão **"🎨 Ativar Modo Curador"**
2. Você verá:
   - Indicador laranja: **"🎨 MODO CURADOR ATIVO"** (canto superior direito)
   - Botão muda para: **"🤖 Ativar Modo AI"** (laranja)
   - Notificação: "Modo Curador Ativado"

### 2. Editar Players Manualmente

Agora você pode clicar nos **quadrados dos jogadores**:

- **Quadrado verde** (vivo) → Clique → Fica **cinza** (morto)
- **Quadrado cinza** (morto) → Clique → Fica **verde** (vivo)

**IMPORTANTE**: Com Modo Curador ativado, a IA **NÃO vai sobrescrever** suas edições!

### 3. O que acontece quando a IA detecta kills?

- A IA continua analisando o killfeed em segundo plano
- **MAS** as atualizações automáticas são **bloqueadas**
- Suas edições manuais **permanecem intactas**

### 4. Voltar ao Modo AI

Quando terminar de editar:

1. Clique em **"🤖 Ativar Modo AI"**
2. O sistema sincroniza com o servidor
3. Volta a aceitar atualizações automáticas da IA

---

## 📊 Durante a Partida

### Modo AI (Padrão) - Automático
```
✅ IA detecta kills automaticamente
✅ Atualiza players vivos/mortos em tempo real
❌ Edições manuais podem ser sobrescritas
```

**Use quando**: O jogo está rolando normalmente e você quer monitoramento automático.

### Modo Curador - Manual
```
✅ Você tem controle total
✅ Edições manuais são protegidas
❌ IA não atualiza automaticamente
```

**Use quando**:
- Precisa fazer ajustes manuais
- O killfeed está muito rápido
- Houve erro de detecção da IA

---

## 🧪 TESTE RECOMENDADO

### Teste 1: Edição Manual Básica

1. Configure torneio com 3-5 times
2. **NÃO ative Modo Curador** ainda
3. A IA vai detectar jogadores automaticamente quando você iniciar o jogo
4. Tente clicar em um player box manualmente
5. **Observe**: se a IA detectar um kill logo depois, pode sobrescrever

### Teste 2: Modo Curador Funcionando

1. Configure torneio
2. **ATIVE Modo Curador** (🎨)
3. Clique em vários player boxes para mudar status
4. Inicie o jogo e deixe a IA detectar kills
5. **Observe**: Suas edições **NÃO serão sobrescritas**
6. Verifique no console (F12) as mensagens:
   ```
   🎨 CURATOR MODE: Blocking AI update of type "player_added"
   🎨 CURATOR MODE: Blocking AI update of type "kill"
   ```

### Teste 3: Alternar Entre Modos

1. Inicie com Modo AI
2. Deixe a IA detectar alguns kills
3. **ATIVE Modo Curador**
4. Faça edições manuais
5. **VOLTE para Modo AI**
6. Verifique que o estado sincronizou corretamente

---

## 🔍 Checklist de Funcionalidades

Use esta lista para verificar se tudo está funcionando:

### Configuração Inicial
- [ ] Backend inicia sem erros
- [ ] Dashboard conecta (🟢 Conectado)
- [ ] Consigo carregar torneio manualmente (digitando tags)
- [ ] Grid de times aparece corretamente
- [ ] Botão "🎨 Ativar Modo Curador" aparece

### Modo Curador
- [ ] Clico em "Ativar Modo Curador" e indicador aparece
- [ ] Botão muda para "Ativar Modo AI" (laranja)
- [ ] Notificação aparece confirmando ativação
- [ ] Consigo clicar em player boxes e mudar status (verde ↔ cinza)
- [ ] IA **NÃO sobrescreve** minhas edições
- [ ] Console mostra "🎨 CURATOR MODE: Blocking AI update"

### Modo AI
- [ ] Volto para Modo AI clicando no botão
- [ ] Indicador laranja desaparece
- [ ] Sistema sincroniza com servidor
- [ ] IA volta a atualizar automaticamente

### Durante Partida Real
- [ ] Consigo alternar entre modos durante o jogo
- [ ] Edições manuais são salvas no servidor
- [ ] Status dos times atualiza corretamente
- [ ] Contadores de vivos/mortos/kills funcionam

---

## 🐛 Problemas Comuns e Soluções

### "Python não é reconhecido como comando"

**Solução**:
1. Tente `py main_websocket.py` ou `python3 main_websocket.py`
2. Se não funcionar, verifique se Python está instalado:
   - Baixe em: https://www.python.org/downloads/
   - Durante instalação, marque "Add Python to PATH"

### "⚫ Desconectado" no dashboard

**Solução**:
1. Certifique-se que o backend está rodando
2. Verifique se vê `Uvicorn running on http://0.0.0.0:3000`
3. Recarregue a página do dashboard (F5)

### "Botão Modo Curador não aparece"

**Solução**:
1. Você precisa carregar um torneio primeiro
2. Clique em "Configurar Torneio" e adicione times
3. Depois de carregar, o botão aparece automaticamente

### "Edições não salvam"

**Solução**:
1. Verifique se está conectado (🟢 Conectado)
2. Abra console (F12) e veja se há erros vermelhos
3. Tente desativar e reativar Modo Curador

### "IA ainda sobrescreve no Modo Curador"

**Isso não deveria acontecer!**
1. Abra console (F12)
2. Procure por `🎨 CURATOR MODE: Blocking AI update`
3. Se não aparecer, tire screenshot e me mande

---

## 📞 Feedback Importante

Depois de testar, me responda:

1. **O Modo Curador resolveu o problema?** Consegue editar manualmente agora?
2. **Algum bug encontrado?** Descreva o que aconteceu
3. **A interface está clara?** Ficou fácil de usar?
4. **Sugestões de melhoria?** O que poderia ser melhor?

---

## 📸 Screenshots Úteis

### Como deve ficar quando funcionar:

**Modo AI (Normal)**:
- Botão: "🎨 Ativar Modo Curador" (roxo)
- Sem indicador laranja
- IA atualizando automaticamente

**Modo Curador (Ativo)**:
- Botão: "🤖 Ativar Modo AI" (laranja)
- Indicador: "🎨 MODO CURADOR ATIVO" (canto superior direito)
- Você tem controle total

---

## ⚙️ Informações Técnicas (para referência)

### Arquivos Modificados
- `dashboard-tournament.html` → Adicionado sistema de Modo Curador

### Como Funciona
1. **Modo Curador ON**: Filtro WebSocket bloqueia mensagens da IA (`player_added`, `kill`, `player_detected`)
2. **Modo Curador OFF**: Aceita todas as mensagens da IA normalmente
3. **Edições manuais**: Sempre enviadas ao servidor via `POST /api/tournament/player/status`
4. **Sincronização**: Ao voltar para Modo AI, recarrega estado do servidor

### Logs do Console (F12)
```javascript
// Modo Curador ativo
🎨 CURATOR MODE ACTIVE - AI updates blocked
🎨 CURATOR MODE: Blocking AI update of type "player_added"

// Modo AI ativo
🤖 AI MODE ACTIVE - Syncing with server
📨 Message: {type: "kill", data: {...}}
```

---

## 🎯 Próximos Passos

Se o Modo Curador funcionar bem, posso implementar:

1. **Fase 2**: Proteção automática (não precisa ativar manualmente)
2. **Fase 3**: Updates pontuais (performance melhorada)
3. **Extras**: Histórico de edições, desfazer/refazer, etc.

---

**Boa sorte nos testes! Qualquer dúvida, me chame. 🚀**
