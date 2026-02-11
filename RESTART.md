# GTA Analytics V2 - Guia de Restart Rápido

## 🚀 Reiniciar Sistema Completo

### 1. Fechar Processos

No **Task Manager** (Ctrl+Shift+Esc):
- Encontre todos os processos **python.exe**
- Clique com botão direito → **End Task**
- Encontre o processo **gateway.exe**
- Clique com botão direito → **End Task**

Ou via **terminal**:
```bash
taskkill /F /IM python.exe
taskkill /F /IM gateway.exe
```

### 2. Iniciar Gateway

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\gateway
.\gateway.exe -port=8000 -buffer=200 -webrtc=true -websocket=true -ipc=true
```

**Deixe este terminal aberto!**

### 3. Iniciar Backend (Nova Janela)

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\backend
python main_websocket.py
```

**Deixe este terminal aberto!**

### 4. Verificar Status

```bash
# Gateway
curl http://localhost:8000/health

# Backend
curl http://localhost:3000/stats
```

### 5. Abrir Dashboard

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2
start dashboard-v2.html
```

---

## ⚙️ Configurações Atuais

### backend/.env

```env
# OCR Configuration
OCR_ENABLED=false  # <-- DESABILITADO para teste

# Game Configuration
USE_ROI=false      # <-- Processa tela inteira
```

### O que esperar:

- **OCR_ENABLED=false**: Todos os frames vão para Vision API
- **USE_ROI=false**: Processa frame completo (não só canto direito)
- **Custo**: ~$0.01 por 10 segundos de captura (com OCR desabilitado)

---

## 🧪 Teste Rápido (10 segundos)

1. **Abra imagem do GTA** com kills visíveis
2. **Dashboard** → Clique "INICIAR CAPTURA"
3. **Selecione a janela** com GTA
4. **Aguarde 10 segundos**
5. **Pare a captura**
6. **Verifique** se apareceram kills no dashboard

Se detectar kills: ✅ **Sistema funcionando!**

---

## 🔧 Troubleshooting

### "Port 3000 already in use"

Mate todos os Python:
```bash
taskkill /F /IM python.exe
```

### "Port 8000 already in use"

Mate o Gateway:
```bash
taskkill /F /IM gateway.exe
```

### Dashboard não conecta

1. Recarregue a página (F5)
2. Verifique se Gateway e Backend estão rodando
3. Veja os logs nos terminais

### Nenhum kill detectado

Verifique se:
- [ ] Imagem do GTA está visível (não terminal preto na frente)
- [ ] Kill feed está presente na imagem
- [ ] Backend está processando: `curl http://localhost:3000/stats`
- [ ] OCR desabilitado: `frames_processed` deve ser > 0

---

## 📊 Comandos Úteis

### Ver Stats

```bash
# Backend
curl http://localhost:3000/stats

# Gateway
curl http://localhost:8000/stats
```

### Exportar Excel

```bash
curl http://localhost:3000/export > kills.xlsx
```

### Limpar Dados

```bash
# Via dashboard: Botão RESET
# Ou reiniciar o backend
```

---

## 🎯 Próximos Passos Após Teste Bem-Sucedido

1. **Reabilitar OCR** (para economizar API):
   ```env
   OCR_ENABLED=true
   ```

2. **Ajustar ROI** (se necessário):
   ```env
   USE_ROI=true
   ROI_X=0.75  # Ajuste conforme necessário
   ```

3. **Deploy para Cloud** (opcional):
   - Seguir `DEPLOY_GUIDE.md`

---

**Última atualização**: 2026-02-10 22:47
