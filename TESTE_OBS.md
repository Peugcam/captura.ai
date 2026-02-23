# 🎮 Guia de Teste OBS - GTA Analytics V2

## Pré-requisitos

1. **OBS Studio** instalado
2. **Go Gateway** rodando (porta 8080)
3. **Backend Python** rodando (porta 8000)

---

## 📋 Passo a Passo

### 1. Iniciar o Go Gateway

```bash
cd gateway
go run main.go
```

**Verificar**: Deve aparecer `🚀 Gateway listening on :8080`

---

### 2. Iniciar o Backend Python

```bash
cd backend
python main_websocket.py
```

**Verificar**: Deve aparecer `✅ Backend iniciado em http://0.0.0.0:8000`

---

### 3. Configurar OBS

#### Opção A: Plugin WebSocket (Recomendado)

1. Instale o plugin **obs-websocket** (já vem no OBS 28+)
2. Configure o gateway personalizado:
   - Vá em `Ferramentas` → `WebSocket Server Settings`
   - Habilite o servidor
   - Configure para enviar para `ws://localhost:8080`

#### Opção B: Usando Virtual Camera

1. No OBS, configure uma `Virtual Camera`
2. O gateway irá capturar frames da câmera virtual

---

### 4. Rodar o Monitor de Frames

```bash
cd backend
python test_obs_realtime.py
```

Você verá em tempo real:
```
==============================================================
⏱️  14:30:45
==============================================================
📊 Total de Frames Recebidos: 1250
🎬 FPS Médio: 30.0 fps
⚡ Frames/segundo atual: 30
==============================================================
```

---

## 🔍 O que o Monitor Mostra

### Métricas em Tempo Real

- **Total de Frames Recebidos**: Contador geral desde o início
- **FPS Médio**: Taxa de frames por segundo (média dos últimos 10 segundos)
- **Frames/segundo atual**: Taxa instantânea

### Indicadores de Saúde

✅ **Gateway OK**: Conectado ao gateway Go
✅ **Backend OK**: Backend Python respondendo
📦 **Frames sendo recebidos**: Pipeline funcionando

---

## ⚠️ Troubleshooting

### Gateway não conecta

```
❌ Erro ao conectar no Gateway
```

**Solução**:
1. Verifique se o gateway está rodando: `http://localhost:8080/health`
2. Confira se a porta 8080 está livre
3. Reinicie o gateway

---

### Backend não conecta

```
❌ Backend retornou status 500
```

**Solução**:
1. Verifique se o backend está rodando: `http://localhost:8000/health`
2. Confira os logs do backend
3. Verifique as API keys no `.env`

---

### Nenhum frame sendo recebido

```
📦 Recebidos 0 frames
```

**Solução**:
1. Verifique se o OBS está transmitindo/gravando
2. Confira a configuração do WebSocket no OBS
3. Teste manualmente: `curl http://localhost:8080/poll`

---

## 🎯 Testes Recomendados

### Teste 1: Verificar FPS
- **Objetivo**: Confirmar que está recebendo ~30 fps
- **Como**: Observe o "FPS Médio" no monitor
- **Esperado**: Entre 25-30 fps (depende do OBS)

### Teste 2: Latência
- **Objetivo**: Medir delay entre OBS e processamento
- **Como**: Compare timestamp do frame com hora atual
- **Esperado**: < 1 segundo de delay

### Teste 3: Processamento Contínuo
- **Objetivo**: Sistema processa sem parar
- **Como**: Deixe rodando por 5 minutos
- **Esperado**: Total de frames aumentando constantemente

### Teste 4: Kill Feed Detection
- **Objetivo**: Verificar se detecta kills em tempo real
- **Como**: Jogue GTA e observe os logs do backend
- **Esperado**: Mensagens `🎯 KILL DETECTED!` quando houver kills

---

## 📊 Métricas de Sucesso

| Métrica | Valor Esperado | Status |
|---------|----------------|--------|
| FPS | 25-30 | ⏳ |
| Latência | < 1s | ⏳ |
| Uptime | > 30min | ⏳ |
| Detecção de Kills | > 80% | ⏳ |

---

## 🚀 Próximos Passos

Depois de validar que os frames estão chegando:

1. ✅ Frames chegando em tempo real
2. ⏳ **Processar frames com Vision API**
3. ⏳ **Detectar kills**
4. ⏳ **Atualizar dashboard via WebSocket**
5. ⏳ **Exportar para Excel**

---

## 🆘 Ajuda

Se encontrar problemas:

1. Verifique os logs:
   - Gateway: Terminal do Go
   - Backend: `backend/backend.log`

2. Teste os endpoints:
   - Gateway Health: `http://localhost:8080/health`
   - Backend Health: `http://localhost:8000/health`
   - Polling: `http://localhost:8080/poll`

3. Reinicie tudo:
   ```bash
   # Parar tudo (Ctrl+C)
   # Reiniciar gateway
   cd gateway && go run main.go

   # Reiniciar backend (nova janela)
   cd backend && python main_websocket.py
   ```
