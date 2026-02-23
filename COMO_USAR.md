# 🚀 COMO USAR - GTA Analytics V2

## ✅ TUDO PRONTO!

Você já tem:
- ✅ Servidor Fly.dev: https://gta-analytics-v2.fly.dev
- ✅ Backend Python configurado
- ✅ Gemini Flash FREE ativado ($0/mês!)
- ✅ OpenRouter + OpenAI configurados
- ✅ Dashboard estrategista funcionando
- ✅ App de captura criado

---

## 🎮 USO EM 3 PASSOS

### Passo 1: PC do Jogador

```bash
# Navegar até pasta
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\backend

# Executar captura
python capture_remote_mss.py
```

**O que vai aparecer:**
```
======================================================================
GTA ANALYTICS - CAPTURA REMOTA (MSS)
======================================================================

[*] Servidor: https://gta-analytics-v2.fly.dev/api/frames/upload
[*] Intervalo: 2.0s (smart sampling)
[*] Qualidade: 85
[*] Custo: $0 (Gemini Flash FREE via OpenRouter)
[*] Metodo: MSS (Multi-Screen Screenshot)

======================================================================

[+] Inicializando captura MSS...
[OK] MSS inicializado com sucesso!
     Monitor: 1920x1080

[*] Iniciando captura...

======================================================================

[12:30:15] [OK] Frame 1 enviado (163 KB) | Uptime: 2s | FPS medio: 0.50
[12:30:17] [OK] Frame 2 enviado (165 KB) | Uptime: 4s | FPS medio: 0.50
[12:30:19] [OK] Frame 3 enviado (162 KB) | Uptime: 6s | FPS medio: 0.50
...
```

### Passo 2: PC do Estrategista

```
1. Abrir navegador
2. Acessar: https://gta-analytics-v2.fly.dev/strategist
3. Ver kills em tempo real!
```

### Passo 3: Fim do Evento

```
Jogador: Ctrl+C (para captura)
Estrategista: Clica "Export Excel"
```

---

## 💰 CUSTOS

```
Por evento (3h): $0.00 (Gemini Flash FREE)
Por mês: $0-5 (Fly.dev hosting)
Por ano: $0-60 total

PRATICAMENTE GRÁTIS! ✅
```

---

## 📁 ARQUIVOS IMPORTANTES

```
backend/
├─ capture_remote_mss.py     ← App de captura (PC jogador)
├─ main_websocket.py          ← Backend (Fly.dev)
└─ config.py                  ← Configurações

Documentação:
├─ SOLUCAO_FINAL_CUSTO_ZERO.md    ← Solução completa
├─ SOLUCAO_COMPLETA_FLYDEV.md     ← Arquitetura detalhada
├─ DIAGNOSTICO_PROBLEMA.md        ← Por que OBS não funciona
└─ COMO_USAR.md                   ← Este arquivo
```

---

## 🔧 COMPILAR PARA .EXE (Opcional)

Se quiser distribuir para jogador sem Python:

```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar
cd backend
pyinstaller --onefile --name gta-capture capture_remote_mss.py

# Resultado:
# dist/gta-capture.exe (~50 MB)
```

Jogador só precisa executar `gta-capture.exe`!

---

## ❓ TROUBLESHOOTING

### Problema: "Conexão recusada" ou "Timeout"

**Solução:**
1. Verificar se Fly.dev está online:
   ```bash
   curl https://gta-analytics-v2.fly.dev/health
   ```

2. Ver logs do servidor:
   ```bash
   fly logs
   ```

### Problema: "MSS não inicializa"

**Solução:**
```bash
pip install --upgrade mss
```

### Problema: Frames não aparecem no dashboard

**Solução:**
1. Verificar endpoint está funcionando:
   ```bash
   curl https://gta-analytics-v2.fly.dev/api/frames/upload
   ```

2. Ver logs em tempo real:
   ```bash
   fly logs -a gta-analytics-backend
   ```

---

## 📊 DASHBOARD URLS

```
Estrategista (completo):
https://gta-analytics-v2.fly.dev/strategist

Jogador (simples):
https://gta-analytics-v2.fly.dev/player

Monitor:
https://gta-analytics-v2.fly.dev/monitor

Health check:
https://gta-analytics-v2.fly.dev/health
```

---

## 🎯 PRÓXIMOS PASSOS OPCIONAIS

### 1. Interface Electron (2 semanas)
- Dashboard bonito para jogador
- Auto-update
- ~200MB executável único

### 2. Otimizações Adicionais
- ROI (Region of Interest) para kill feed
- Frame deduplication
- Batch processing inteligente

### 3. Múltiplos Jogadores
- Servidor suporta múltiplos clientes
- Cada jogador roda capture_remote_mss.py
- Estrategista vê todos em um dashboard

---

## ✅ CONCLUSÃO

**Sistema 100% funcional com custo $0/mês!**

Único problema era GTA bloquear OBS/browser.

Solução: MSS captura tela → Fly.dev processa com Gemini FREE → Dashboard mostra ao vivo!

**Pronto para produção!** 🎉
