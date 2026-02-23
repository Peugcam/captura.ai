# 🎮 COMO TESTAR O GTA ANALYTICS

## ✅ O Que Já Está Configurado

Você já completou estas etapas:

1. ✅ Gateway Fly.io online (https://gta-analytics-gateway.fly.dev)
2. ✅ Backend Fly.io online (https://gta-analytics-backend.fly.dev)
3. ✅ OBS WebSocket configurado (senha: ZNx3v4LjLVCgbTrO)
4. ✅ Cliente de captura funcionando (`gta-analytics-v2.py`)
5. ✅ Conexão testada com sucesso

## 🧪 TESTE RÁPIDO (2 Minutos)

### Passo 1: Prepare o OBS

1. Abra o OBS Studio
2. Coloque qualquer conteúdo na cena (pode ser uma janela do navegador)
3. Certifique-se que o WebSocket está ativo (Ferramentas → Configurações do Servidor WebSocket)

### Passo 2: Execute o Capturador

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\pacote-luis
py gta-analytics-v2.py
```

Você deve ver:

```
======================================================================
   GTA ANALYTICS - KILL FEED TRACKER
   OBS WebSocket 5.0
======================================================================

[OK] Gateway online: https://gta-analytics-gateway.fly.dev
[OK] Conectado ao OBS (localhost:4455)
[OK] Cena atual: [nome da sua cena]

======================================================================
   CAPTURA ATIVA
======================================================================

[20 frames] 5s | 4.0 FPS | 0 erros
[40 frames] 10s | 4.0 FPS | 0 erros
```

**Se você vê isso → Sistema está capturando e enviando frames! ✅**

### Passo 3: Verifique se o Backend Está Recebendo

Abra outro terminal e execute:

```bash
curl https://gta-analytics-gateway.fly.dev/stats
```

Deve retornar algo como:

```json
{
  "frames_received": 40,
  "last_frame": "2024-01-15T10:30:00Z"
}
```

## 🎯 TESTE COMPLETO COM JOGO

### Preparação:

1. Abra o GTA (ou qualquer jogo com kill feed no canto superior direito)
2. Configure OBS para capturar o jogo:
   - Adicione fonte: "Captura de Jogo" ou "Captura de Janela"
   - Resolução de saída: 1920x1080

### Ajuste a Região do Kill Feed:

Edite `config.json` se necessário:

```json
{
  "kill_feed_region": {
    "x": 1400,    ← Ajuste se o kill feed estiver em outra posição
    "y": 0,       ← Distância do topo
    "width": 520,  ← Largura da região
    "height": 400  ← Altura da região
  }
}
```

Para GTA V padrão em 1920x1080, esses valores já estão corretos.

### Execute Durante o Jogo:

1. Inicie o jogo
2. Execute `py gta-analytics-v2.py`
3. Jogue normalmente (ou assista kills acontecerem)
4. O sistema vai:
   - Capturar kill feed a cada 0.25s (4 FPS)
   - Enviar para Gateway
   - Gateway envia para Backend
   - Backend processa com Vision API (Gemini/GPT-4o)
   - Kills são salvos no banco de dados

## 📊 VERIFICAR RESULTADOS

### Método 1: Logs do Backend

```bash
flyctl logs -a gta-analytics-backend
```

Procure por linhas como:

```
[KILL] Player123 killed Player456 with AK-47
[TEAM] TeamA: 3 players alive
```

### Método 2: Dashboard (se estiver implementado)

Acesse: `https://gta-analytics-backend.fly.dev/dashboard`

### Método 3: API Direta

```bash
curl https://gta-analytics-backend.fly.dev/api/recent-kills
```

Deve retornar lista de kills detectadas nos últimos minutos.

## ⚠️ PROBLEMAS COMUNS

### "0 erros" mas nenhuma kill detectada

**Causa:** Vision API pode não estar configurada ou kill feed está em posição errada

**Solução:**
1. Verifique se `GEMINI_API_KEY` ou `OPENAI_API_KEY` está configurada no Backend
2. Ajuste coordenadas do kill feed no `config.json`
3. Tire uma screenshot manual da região e verifique se o kill feed está visível

### "X erros" crescendo

**Causa:** Gateway não está recebendo os frames

**Solução:**
1. Verifique internet
2. Teste: `curl https://gta-analytics-gateway.fly.dev/health`
3. Verifique firewall não está bloqueando

### FPS muito baixo

**Causa:** OBS ou jogo consumindo muita CPU

**Solução:**
1. Reduza FPS no `config.json` de 4 para 2
2. Reduza resolução de captura no código (de 1920x1080 para 1280x720)

## 🚀 PRÓXIMOS PASSOS

Depois que confirmar que está funcionando:

1. **Para Luis:**
   - Executar `INSTALAR_TUDO.bat` (quando pronto)
   - Configurar OBS uma vez
   - Usar atalho do desktop sempre que jogar

2. **Dashboard Mobile:**
   - Implementar interface responsiva
   - Mostrar teams alive + player counts
   - Mostrar kill counts em tempo real

3. **Features dos Torneios:**
   - Importar lista de teams do Excel
   - Rastrear eliminações por equipe
   - Rankings automáticos

## 📝 CHECKLIST DE TESTE

- [ ] Gateway online (curl health)
- [ ] Backend online (curl health)
- [ ] OBS conectado via WebSocket
- [ ] Frames sendo capturados (ver contador no programa)
- [ ] Frames sendo enviados sem erros
- [ ] Backend recebendo frames (verificar logs)
- [ ] Kills sendo detectadas (verificar API/logs)
- [ ] Dashboard mostrando dados (se implementado)

---

**Tudo funcionando?** → Pronto para empacotar para o Luis!

**Algum problema?** → Verifique os logs e ajuste configurações acima.
