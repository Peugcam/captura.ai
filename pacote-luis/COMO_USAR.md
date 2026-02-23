# GTA ANALYTICS V2 - GUIA DE USO

## SISTEMA FUNCIONANDO 100%

### O que voce tem:

1. **Dashboard V2 Bonito** com WebSocket conectado
2. **Backend Cloud** funcionando (gta-analytics-backend.fly.dev)
3. **Cliente de Captura** via OBS WebSocket
4. **Sistema completo em tempo real**

---

## COMO USAR

### 1. Abrir o Dashboard

**OPCAO 1 - RECOMENDADO (Dashboard em Nuvem):**
```
https://gta-analytics-v2.fly.dev/strategist
```
✅ Todas as funcionalidades funcionam
✅ Editar times funciona
✅ Acessivel de qualquer dispositivo

**OPCAO 2 (Dashboard Local - apenas visualizacao):**
Duplo-clique no arquivo: `dashboard-v2-strategist.html`
⚠️ Algumas funcionalidades podem nao funcionar (editar times, etc.)

Voce deve ver: **🟢 Conectado** no canto superior esquerdo

---

### 2. Configurar Torneio

No dashboard:
1. Clique em **"⚙️ Configurar Torneio"**
2. Escolha o tipo de torneio:
   - **Etapa 1**: Times variaveis
   - **Etapa 2**: ~100 times
   - **Championship**: 20 times
3. Adicione os times participantes

---

### 3. Iniciar Captura

Abra o terminal e execute:
```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\pacote-luis
py gta-analytics-v2.py
```

Voce deve ver:
```
✅ Gateway online
✅ Conectado ao OBS
✅ Cena atual: [nome da sua cena]
🎬 CAPTURA ATIVA
```

---

### 4. Jogar GTA V / Naruto Online

- O OBS deve estar capturando a janela do jogo
- O cliente vai capturar frames a 1 FPS
- O dashboard vai atualizar em tempo real via WebSocket

---

## CONFIGURACOES

### config.json
```json
{
  "gateway_url": "https://gta-analytics-gateway.fly.dev",
  "fps": 1,
  "kill_feed_region": {
    "x": 1400,
    "y": 0,
    "width": 520,
    "height": 400
  }
}
```

**Ajustar FPS:** Mude o valor de `fps` (1-4 recomendado)
**Ajustar Regiao:** Modifique `kill_feed_region` conforme necessario

---

## OBS - CONFIGURACAO RECOMENDADA

Siga o arquivo: `CONFIGURAR_OBS_JANELA_FIXA.md`

**Resumo:**
1. Remover "Captura de monitor"
2. Adicionar "Captura de Janela"
3. Selecionar janela do jogo
4. Usar metodo "Windows Graphics Capture"

---

## SISTEMA CLOUD

### Backend
- **URL:** https://gta-analytics-backend.fly.dev
- **WebSocket:** wss://gta-analytics-backend.fly.dev/events
- **Status:** https://gta-analytics-backend.fly.dev/health
- **Stats:** https://gta-analytics-backend.fly.dev/stats

### Gateway
- **URL:** https://gta-analytics-gateway.fly.dev
- Encaminha frames para backend antigo

---

## DASHBOARD - RECURSOS

### Prioridade 1 (Luis)
- ✅ Times vivos
- ✅ Contagem de jogadores por time

### Prioridade 2
- ✅ Contagem de kills

### Prioridade 3
- ✅ Rankings

### Funcoes
- 📊 Exportar Excel
- 🎨 Modo Curador (editar dados manualmente)
- ✏️ Editar Times
- 🔄 Resetar Partida
- 🗑️ Limpar Lista

---

## SOLUCAO DE PROBLEMAS

### Dashboard mostra "⚫ Desconectado"
1. Verifique sua conexao com internet
2. Abra o Console do navegador (F12)
3. Procure por erros de WebSocket
4. Atualize a pagina (F5)

### Cliente nao conecta ao OBS
1. Abra o OBS
2. Menu: Ferramentas → Configuracoes do Servidor WebSocket
3. Marque: "Ativar Servidor WebSocket"
4. Porta: 4455
5. **IMPORTANTE:** Anote a SENHA que aparece no OBS
6. Edite o arquivo `gta-analytics-v2.py` e coloque SUA senha na linha 42:
   ```python
   OBS_PASSWORD = "SUA_SENHA_AQUI"
   ```

### Gateway offline
1. Verifique: https://gta-analytics-gateway.fly.dev/health
2. Se retornar erro, o servico pode estar inativo
3. O cliente vai mostrar erros periodicos

---

## ARQUITETURA DO SISTEMA

```
[OBS] → [Cliente Python] → [Gateway] → [Backend] → [Dashboard]
                                                      ↑
                                               WebSocket em tempo real
```

**Fluxo:**
1. OBS captura tela do jogo
2. Cliente Python pega screenshot via WebSocket
3. Recorta regiao do kill feed
4. Envia para Gateway
5. Gateway encaminha para Backend
6. Backend processa com IA (Gemini/GPT-4o)
7. Dashboard recebe atualizacoes via WebSocket

---

## PARA O LUIS

Entregar a pasta inteira: `pacote-luis/`

**Arquivos importantes:**
- ✅ `gta-analytics-v2.py` - Cliente
- ✅ `dashboard-v2-strategist.html` - Dashboard
- ✅ `config.json` - Configuracao
- ✅ `CONFIGURAR_OBS_JANELA_FIXA.md` - Guia OBS
- ✅ `COMO_USAR.md` - Este guia

**Luis precisa:**

1. Instalar dependencias:
```bash
pip install obsws-python requests pillow
```

2. Configurar OBS WebSocket:
   - Abrir OBS
   - Menu: Ferramentas → Configuracoes do Servidor WebSocket
   - Marcar: "Ativar Servidor WebSocket"
   - Porta: 4455
   - Anotar a SENHA que aparece

3. Editar `gta-analytics-v2.py` linha 42:
   ```python
   OBS_PASSWORD = "SENHA_DO_OBS_DO_LUIS"
   ```

---

## SUPORTE

**Criado por:** Paulo
**Data:** 22/02/2026
**Versao:** 2.0.0

**Funcionalidades:**
- ✅ WebSocket 5.0 (OBS 28+)
- ✅ Dashboard em tempo real
- ✅ Backend cloud
- ✅ Processamento com IA
- ✅ Exportar dados
