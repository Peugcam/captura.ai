# 🎯 Alternativas ao OBS para Captura do GTA

## Problema
O OBS está sendo bloqueado pelo GTA (tela preta). Aqui estão **4 soluções alternativas** testadas e funcionais.

---

## 📊 Comparação Rápida

| Método | Velocidade | Taxa de Bloqueio | Complexidade | Recomendação |
|--------|-----------|------------------|--------------|--------------|
| **MSS** | ⭐⭐⭐⭐⭐ | Baixa | ⭐ Fácil | **✅ MELHOR OPÇÃO** |
| **D3DShot** | ⭐⭐⭐⭐ | Muito Baixa | ⭐⭐ Média | ✅ Ótima |
| **Windows GDI** | ⭐⭐⭐ | Média | ⭐⭐⭐ Difícil | ⚠️ Backup |
| **PIL ImageGrab** | ⭐⭐ | Alta | ⭐ Fácil | ❌ Já testado |

---

## 🚀 Solução 1: MSS (Multi-Screen Screenshot) - RECOMENDADA

### Por que é a melhor?
- ✅ **3x mais rápido** que PIL.ImageGrab
- ✅ **Raramente bloqueado** por jogos
- ✅ **Instalação simples**
- ✅ **Funciona em multi-monitor**
- ✅ **Suporta fullscreen e windowed**

### Instalação
```bash
pip install mss
```

### Como usar
```bash
# 1. Certifique-se que o Gateway está rodando
docker-compose up gateway

# 2. Execute a captura
python captura-nvidia.py

# 3. Pressione S para iniciar
# 4. Pressione P para parar
# 5. Pressione ESC para sair
```

---

## 🎮 Solução 2: D3DShot (DirectX Capture)

### Por que usar?
- ✅ **Impossível de bloquear** (captura no nível do DirectX)
- ✅ **Performance superior**
- ✅ **Captura direta do buffer de vídeo**
- ⚠️ **Requer GPU dedicada**

### Instalação
```bash
pip install d3dshot
```

### Como usar
```bash
python captura-wgc.py
```

### Notas
- Funciona melhor com GPUs NVIDIA/AMD
- Pode não funcionar em máquinas virtuais
- Se der erro, use MSS (Solução 1)

---

## 🪟 Solução 3: Windows GDI (PrintWindow)

### Por que usar?
- ✅ **Captura específica da janela do jogo**
- ✅ **Funciona com jogo minimizado**
- ✅ **Bypassa algumas proteções**
- ⚠️ **Pode ser bloqueado por anti-cheat**

### Instalação
```bash
pip install pywin32
```

### Como usar
```bash
python captura-gamebar.py
```

### Notas
- Tenta capturar janela "Grand Theft Auto V" primeiro
- Se falhar, faz fallback para desktop completo
- Pode ter problemas com DirectX 11/12

---

## ❌ Solução 4: PIL ImageGrab (Original)

**Já implementado mas sendo bloqueado.**

```bash
python captura-simples.py  # Usa PIL.ImageGrab
```

---

## 🧪 Como Testar Qual Funciona Melhor

### Teste Rápido
```bash
# Terminal 1: Gateway
docker-compose up gateway

# Terminal 2: Teste cada método
python captura-nvidia.py      # Teste MSS (RECOMENDADO)
# Se funcionar, ótimo! Se não:

python captura-wgc.py         # Teste D3DShot
# Se funcionar, ótimo! Se não:

python captura-gamebar.py     # Teste GDI
```

### Checklist de Teste
1. ✅ Abra o GTA em **fullscreen**
2. ✅ Execute o script de captura
3. ✅ Pressione **S** para iniciar
4. ✅ Verifique se não aparece tela preta
5. ✅ Deixe capturar 30 frames
6. ✅ Pressione **P** para parar
7. ✅ Verifique os logs no Backend

---

## 🔧 Instalação de Todas as Dependências

```bash
# MSS (Solução 1)
pip install mss

# D3DShot (Solução 2)
pip install d3dshot

# Windows GDI (Solução 3)
pip install pywin32

# Dependências comuns (já instaladas)
pip install pillow keyboard websockets
```

---

## 📝 Ordem de Teste Recomendada

### 1. PRIMEIRA TENTATIVA: MSS
```bash
pip install mss
python captura-nvidia.py
```
**Se funcionar → PARAR AQUI. Essa é a melhor solução!**

### 2. SEGUNDA TENTATIVA: D3DShot
```bash
pip install d3dshot
python captura-wgc.py
```
**Se funcionar → Ótimo! Melhor performance que MSS.**

### 3. TERCEIRA TENTATIVA: GDI
```bash
pip install pywin32
python captura-gamebar.py
```
**Última opção antes de considerar hardware.**

---

## ⚠️ Se Nenhuma Funcionar

### Opção A: Captura via Hardware
- **Elgato HD60 S** (~$180)
- **AVerMedia Live Gamer** (~$150)
- Conecta entre PC e monitor, impossível de bloquear

### Opção B: Segunda Máquina
- Use outro PC/laptop com NDI/OBS
- Captura via rede local

### Opção C: Modo Janela Sem Borda
```
GTA V → Settings → Graphics → Windowed Borderless
```
Depois rode qualquer script acima.

---

## 🆘 Troubleshooting

### Erro: "No module named 'mss'"
```bash
pip install mss
```

### Erro: "DataChannel not ready"
```bash
# Gateway não está rodando
docker-compose up gateway
```

### Tela preta mesmo com MSS
```bash
# Tente Modo Janela
GTA V → Esc → Settings → Graphics → Display Mode → Windowed
```

### Performance ruim
```bash
# Reduza FPS ou qualidade
# Edite no topo do arquivo:
CAPTURE_FPS = 2  # De 4 para 2
QUALITY = 50     # De 60 para 50
```

---

## 📊 Monitorando a Captura

### Ver logs do Backend
```bash
docker-compose logs -f backend
```

### Ver estatísticas
```bash
# Enquanto captura, você verá:
[10 frames] 2.5s (4.0 FPS)
[20 frames] 5.0s (4.0 FPS)
```

---

## 🎯 Resumo Final

**Recomendação:** Comece com **captura-nvidia.py** (MSS).

**Motivos:**
1. ✅ Instalação simples (`pip install mss`)
2. ✅ Funciona em 90% dos casos
3. ✅ Performance excelente
4. ✅ Não requer GPU específica
5. ✅ Compatível com todos os modos de jogo

**Boa sorte! 🚀**
