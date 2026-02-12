# GTA Analytics V2 - Guia de Teste com Vídeo

## 📹 Pré-requisitos

✅ OpenCV instalado (já está!)
✅ Gateway rodando (port 8000)
✅ Backend rodando (port 3000)
✅ Vídeo de gameplay do GTA salvo no PC

---

## 🚀 Como Usar

### 1. Preparar o Vídeo

Certifique-se que o vídeo:
- Contém gameplay do GTA V ou GTA Battle Royale
- Mostra o kill feed no canto superior direito
- Formato: MP4, AVI, MOV, ou qualquer formato suportado pelo OpenCV
- Resolução: Qualquer (será processada automaticamente)

### 2. Executar o Script de Captura

```bash
# Sintaxe básica
python captura-video.py --video "CAMINHO/PARA/SEU/VIDEO.mp4"

# Exemplo com caminho absoluto
python captura-video.py --video "C:\Users\paulo\Videos\gta-gameplay.mp4"

# Exemplo com configurações customizadas
python captura-video.py \
  --video "C:\Users\paulo\Videos\gta-gameplay.mp4" \
  --fps 4 \
  --quality 85 \
  --gateway http://localhost:8000
```

### Parâmetros Disponíveis

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--video` | Caminho para o arquivo de vídeo (OBRIGATÓRIO) | - |
| `--gateway` | URL do Gateway WebRTC | `http://localhost:8000` |
| `--fps` | Frames por segundo para processar | `4` |
| `--quality` | Qualidade JPEG (1-100) | `85` |

---

## 📊 O Que Acontece Durante o Teste

1. **Conexão WebRTC**: Script se conecta ao Gateway via WebRTC
2. **Extração de Frames**: Lê o vídeo e extrai frames na taxa especificada (--fps)
3. **Codificação JPEG**: Converte frames para JPEG com qualidade especificada
4. **Envio Binário**: Envia frames via WebRTC DataChannel (sem base64!)
5. **Processamento Backend**:
   - Gateway armazena frames no buffer
   - Backend faz polling e recebe frames
   - OCR filtra frames com texto relevante
   - Vision API detecta kills
   - Dashboard atualiza em tempo real

---

## 📈 Monitoramento em Tempo Real

### Terminal 1: Script de Captura
Mostra progresso do processamento de vídeo:
```
📊 Progresso: 45.2% | Frames enviados: 120 | FPS real: 4.01 | Bytes: 15.3 MB
```

### Terminal 2: Gateway Logs
```bash
# Ver logs do Gateway (se rodando em background)
tail -f gateway.log

# Ou verificar stats
curl http://localhost:8000/stats
```

### Terminal 3: Backend Logs
Mostra detecção de kills em tempo real:
```
[INFO] OCR: Detected text in frame (contains 'killed')
[INFO] Vision API: Processing batch of 3 frames
[INFO] KILL DETECTED: PlayerA killed PlayerB with AK-47
```

### Dashboard Web
Abra no navegador: `dashboard-v2.html`
- Veja kills em tempo real
- Gráficos de performance
- Estatísticas de jogadores

---

## ✅ Validação Pós-Teste

### 1. Verificar Stats do Gateway
```bash
curl http://localhost:8000/stats
```

Espera-se ver:
```json
{
  "total_frames": 240,
  "buffer_size": 200,
  "current_frames": 40,
  "websocket_clients": 0,
  "webrtc_peers": 1
}
```

### 2. Verificar Stats do Backend
```bash
curl http://localhost:3000/stats
```

Espera-se ver:
```json
{
  "frames_received": 240,
  "frames_filtered": 180,
  "frames_processed": 60,
  "kills_detected": 15,
  "filter_efficiency": 75.0
}
```

### 3. Exportar Resultados para Excel
```bash
curl http://localhost:3000/export > gta_kills_test.xlsx
```

Abra o arquivo Excel e verifique:
- Kills detectadas corretamente
- Timestamps precisos
- Informações de killer/victim/weapon

---

## 🎯 Cenários de Teste Recomendados

### Teste 1: Vídeo Curto (30-60s)
```bash
python captura-video.py --video "test_short.mp4" --fps 4 --quality 85
```
**Objetivo**: Validar conexão WebRTC e detecção básica

### Teste 2: Vídeo Médio (2-5min)
```bash
python captura-video.py --video "test_medium.mp4" --fps 4 --quality 85
```
**Objetivo**: Testar estabilidade e performance do pipeline

### Teste 3: Vídeo Longo (10-30min)
```bash
python captura-video.py --video "test_long.mp4" --fps 6 --quality 90
```
**Objetivo**: Stress test e validar não há memory leaks

### Teste 4: Alta Taxa de Frames
```bash
python captura-video.py --video "test_action.mp4" --fps 10 --quality 75
```
**Objetivo**: Testar throughput máximo

### Teste 5: Alta Qualidade
```bash
python captura-video.py --video "test_hq.mp4" --fps 2 --quality 95
```
**Objetivo**: Validar detecção com imagens de alta qualidade

---

## 🐛 Troubleshooting

### Erro: "Vídeo não encontrado"
- Verifique o caminho do arquivo
- Use aspas duplas se o caminho tiver espaços
- Exemplo: `"C:\Users\paulo\Meus Vídeos\gta.mp4"`

### Erro: "Gateway inacessível"
```bash
# Verificar se Gateway está rodando
curl http://localhost:8000/health

# Se não estiver, iniciar
cd gateway
./gateway.exe -port=8000 -buffer=200 -webrtc=true
```

### Erro: "DataChannel não abre"
- Verifique firewall (ports UDP 50000-50100)
- Teste primeiro com test_webrtc_connection.py
- Veja logs do Gateway para erros de WebRTC

### Performance Ruim
- Reduza FPS: `--fps 2`
- Reduza qualidade: `--quality 70`
- Verifique uso de CPU/memória

### Nenhum Kill Detectado
- Verifique se o vídeo mostra kill feed no canto superior direito
- Ajuste ROI no backend/.env:
  ```env
  USE_ROI=true
  ROI_X=0.75    # 75% da largura (canto direito)
  ROI_Y=0       # Topo
  ROI_WIDTH=0.25  # 25% da largura
  ROI_HEIGHT=0.35 # 35% da altura
  ```
- Teste com prompt avançado: `USE_ADVANCED_PROMPT=true`

---

## 📊 Métricas de Sucesso

### Bom Desempenho ✅
- FPS real próximo do configurado (±10%)
- Filter efficiency > 50% (OCR economiza > 50% de chamadas Vision API)
- Kills detectadas com precisão > 90%
- Sem crashes ou memory leaks

### Performance Esperada (Hardware Médio)
| FPS | Quality | Throughput | Latência Total |
|-----|---------|------------|----------------|
| 2   | 95      | ~200 KB/s  | ~800ms         |
| 4   | 85      | ~350 KB/s  | ~500ms         |
| 6   | 75      | ~450 KB/s  | ~400ms         |
| 10  | 70      | ~650 KB/s  | ~350ms         |

---

## 🎓 Próximos Passos

Após teste com vídeo bem-sucedido:

1. **Teste com Captura Ao Vivo**
   ```bash
   python captura-webrtc.py --fps 4 --quality 85
   ```

2. **Otimizar Configurações**
   - Ajustar FPS baseado nos resultados
   - Tunar qualidade JPEG para balancear tamanho/precisão
   - Refinar ROI para melhor detecção

3. **Deploy para Cloud** (opcional)
   - Seguir DEPLOY_GUIDE.md
   - Testar com vídeo apontando para cloud: `--gateway https://gta-analytics-gateway.fly.dev`

---

## 💡 Dicas

1. **Use vídeos com resolução 1920x1080** para melhor detecção
2. **Evite vídeos muito comprimidos** (baixa qualidade degrada OCR)
3. **Teste com diferentes partes do vídeo** (início, meio, fim)
4. **Compare resultados manualmente** nas primeiras execuções
5. **Monitore uso de API** (custos!) durante testes longos

---

**Pronto para testar?** 🚀

Forneça o caminho do seu vídeo e eu ajusto o comando!
