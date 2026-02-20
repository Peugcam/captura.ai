# 🎥 Guia Rápido - Testar com OBS

## ⚡ Início Rápido (5 minutos)

### **Método 1: OBS Browser Source** ⭐ RECOMENDADO

#### **Passo 1: Iniciar Sistema**
Execute o arquivo: **`TESTAR-COM-OBS.bat`**

Isso vai abrir 2 janelas:
- ✅ Gateway (porta 8000)
- ✅ Backend (porta 3000)

#### **Passo 2: Configurar OBS**

1. **Abra o OBS Studio**

2. **Adicionar Browser Source:**
   - Na área **"Sources"** (embaixo), clique no **"+"**
   - Escolha **"Browser"**
   - Nome: `GTA Analytics`
   - Clique **OK**

3. **Configurar URL:**
   ```
   URL: file:///C:/Users/paulo/OneDrive/Desktop/gta-analytics-v2/capture-obs.html
   Width: 1920
   Height: 1080
   FPS: 1
   ```

   **Marque:**
   - ☑️ Refresh browser when scene becomes active
   - ☑️ Shutdown source when not visible

   Clique **OK**

4. **Permitir Captura:**
   - Janela do Windows vai pedir permissão
   - Selecione **"Janela: GTA V"** ou **"Tela Inteira"**
   - Clique **"Compartilhar"**

5. **Verificar Status:**
   Você deve ver no OBS:
   ```
   🟢 Conectado
   Frames capturados: 0
   Uploads sucesso: 0
   ```

#### **Passo 3: Jogar!**
- Abra o GTA V (ou qualquer jogo)
- Os frames serão capturados automaticamente
- Abra `dashboard-tournament.html` para ver em tempo real

---

### **Método 2: Gravar no OBS + Processar Depois**

#### **Passo 1: Gravar Gameplay**
1. Abra o OBS
2. Configure sua cena de captura do jogo
3. Clique **"Start Recording"**
4. Jogue normalmente
5. Clique **"Stop Recording"**
6. Vídeo salvo em `C:\Users\paulo\Videos\` (ou onde configurou)

#### **Passo 2: Processar Vídeo**
1. Execute: **`TESTAR-COM-OBS.bat`**
2. Em um novo terminal:
   ```bash
   cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2

   python captura-video.py --video "C:\Users\paulo\Videos\2024-02-20 18-30-45.mp4" --fps 4 --quality 85
   ```

#### **Passo 3: Ver Resultados**
- Abra `dashboard-tournament.html`
- Ou exporte para Excel: `curl http://localhost:3000/export > resultados.xlsx`

---

## 📊 **Verificar se Está Funcionando**

### **1. Testar Gateway:**
```bash
curl http://localhost:8000/health
```
Deve retornar: `{"status":"healthy","timestamp":...}`

### **2. Testar Backend:**
```bash
curl http://localhost:3000/health
```
Deve retornar: `{"status":"healthy"}`

### **3. Ver Estatísticas:**
```bash
# Stats do Gateway
curl http://localhost:8000/stats

# Stats do Backend
curl http://localhost:3000/stats
```

---

## 🎯 **Configurações Recomendadas**

### **Para Teste Rápido:**
```
FPS: 2
Quality: 70
```
- Mais rápido
- Menos custos de API
- Bom para validar funcionamento

### **Para Uso Normal:**
```
FPS: 4
Quality: 85
```
- Balanceado
- Boa detecção
- Custo razoável

### **Para Alta Precisão:**
```
FPS: 6
Quality: 95
```
- Melhor detecção
- Mais lento
- Mais custos

---

## 🐛 **Problemas Comuns**

### **"Gateway inacessível":**
```bash
# Verificar se está rodando
curl http://localhost:8000/health

# Se não estiver, iniciar manualmente
cd gateway
.\gateway.exe -port=8000
```

### **"Permissão de captura negada":**
- Clique direito na fonte "GTA Analytics" no OBS
- Escolha "Interact"
- Aperte F5 para recarregar
- Permita novamente quando pedido

### **"Frames capturados aumenta mas uploads fica em 0":**
- Verifique se o Gateway está rodando
- Verifique sua internet
- Veja os logs do terminal do Gateway

### **"Nenhum kill detectado":**
- Verifique se o vídeo/jogo mostra o kill feed no canto superior direito
- Ajuste o ROI no `backend/.env`:
  ```env
  ENABLE_ROI=true
  ROI_X=0.75
  ROI_Y=0
  ROI_WIDTH=0.25
  ROI_HEIGHT=0.35
  ```

---

## 💡 **Dicas**

1. **Teste primeiro com um vídeo curto** (30s-1min)
2. **Use resolução 1920x1080** se possível
3. **Monitore os logs** dos terminais para ver o que está acontecendo
4. **Abra o dashboard antes** de iniciar a captura
5. **Esconda a fonte no OBS** (Ctrl+H) se não quiser ver

---

## 📂 **Estrutura de Arquivos**

```
gta-analytics-v2/
├── TESTAR-COM-OBS.bat          # Script para iniciar tudo
├── capture-obs.html            # Página para OBS Browser Source
├── captura-video.py            # Script para processar vídeos
├── dashboard-tournament.html   # Dashboard principal
├── dashboard-strategist-v2.html # Dashboard estrategista
├── dashboard-viewer.html       # Dashboard visualizador
│
├── gateway/
│   └── gateway.exe             # Servidor Gateway
│
└── backend/
    ├── main_websocket.py       # Servidor Backend
    └── .env                    # Configurações
```

---

## 🚀 **Fluxo Completo**

```
OBS Browser Source (capture-obs.html)
    ↓ Captura tela do jogo
    ↓ Envia frames HTTP
Gateway Go (porta 8000)
    ↓ Armazena em buffer
    ↓ Disponibiliza via HTTP
Backend Python (porta 3000)
    ↓ Polling de frames
    ↓ OCR pré-filtro
    ↓ Vision AI
    ↓ Kill parsing
    ↓ Team tracking
Dashboard HTML
    ↓ Recebe via WebSocket
    ↓ Mostra em tempo real
```

---

## 📞 **Precisa de Ajuda?**

Verifique os logs nos terminais:
- **Gateway**: Mostra frames recebidos
- **Backend**: Mostra detecção de kills

Se tiver dúvidas, compartilhe os logs!

---

**Última atualização:** 20/02/2026
**Versão:** 2.0
