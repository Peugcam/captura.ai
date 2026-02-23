# 🍥 TESTE COM NARUTO ONLINE

## 📋 PREPARAÇÃO (1 minuto)

### 1. Configure o OBS:

1. **Abra o OBS Studio**
2. **Adicione Naruto Online como fonte:**
   - Botão `+` em "Fontes"
   - Escolha: **"Captura de Janela"** ou **"Captura de Navegador"**
   - Selecione a janela do Naruto Online
   - Certifique-se que o jogo aparece no preview do OBS

3. **Verifique WebSocket:**
   - Menu: Ferramentas → Configurações do Servidor WebSocket
   - Deve estar marcado: ✅ "Ativar Servidor WebSocket"
   - Porta: 4455
   - Senha: ZNx3v4LjLVCgbTrO

---

## 🚀 EXECUTAR TESTE

### Abra 2 terminais:

**TERMINAL 1 - Capturador:**
```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\pacote-luis
py gta-analytics-v2.py
```

**TERMINAL 2 - Monitoramento (deixe aberto):**
```bash
# A cada 10 segundos, veja as estatísticas:
while true; do curl https://gta-analytics-backend.fly.dev/stats; echo ""; sleep 10; done
```

Ou no Windows (PowerShell):
```powershell
while ($true) { curl https://gta-analytics-backend.fly.dev/stats; Start-Sleep 10 }
```

---

## 👀 O QUE OBSERVAR

### No Terminal 1 (Capturador):

Deve mostrar:

```
======================================================================
   GTA ANALYTICS - KILL FEED TRACKER
======================================================================

[OK] Gateway online: https://gta-analytics-gateway.fly.dev
[OK] Conectado ao OBS (localhost:4455)
[OK] Cena atual: narutoonline  ← Deve aparecer o nome da sua cena!

======================================================================
   CAPTURA ATIVA
======================================================================

[20 frames] 5s | 4.0 FPS | 0 erros    ← Contador aumentando
[40 frames] 10s | 4.0 FPS | 0 erros
[60 frames] 15s | 4.0 FPS | 0 erros
```

**✅ SE VOCÊ VÊ ISSO → CAPTURA FUNCIONANDO!**

### No Terminal 2 (Stats):

```json
{
  "frames_received": 60,        ← Aumentando a cada consulta ✅
  "frames_filtered": 35,
  "frames_processed": 25,
  "kills_detected": 0,          ← Normal (Naruto não tem kill feed GTA)
  "filter_efficiency": "58.3%",
  "teams": 0,
  "players": 0
}
```

**✅ SE `frames_received` AUMENTA → BACKEND RECEBENDO!**

---

## 🎯 O QUE CADA NÚMERO SIGNIFICA

### `frames_received`
- Quantos frames chegaram no Gateway
- Deve aumentar ~4 por segundo (4 FPS)
- Se aumenta → Cliente → Gateway OK ✅

### `frames_filtered`
- Frames descartados por serem duplicados
- Filtro pixel economiza chamadas à Vision API
- Normal ser ~50-60% dos frames recebidos

### `frames_processed`
- Frames únicos enviados para Vision API
- Estes são analisados pelo Gemini/GPT-4o
- Se aumenta → Vision API funcionando ✅

### `kills_detected`
- Kills encontradas pela Vision API
- Será 0 no Naruto (normal!)
- No GTA deve aumentar quando kills acontecem

### `filter_efficiency`
- % de frames descartados como duplicados
- Quanto maior, menos gasto com Vision API
- 50-70% é bom!

---

## 🧪 TESTE PASSO A PASSO

### 1. Antes de começar:

```bash
curl https://gta-analytics-backend.fly.dev/stats
```

Anote o valor de `frames_received` (ex: 242)

### 2. Execute o capturador:

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\pacote-luis
py gta-analytics-v2.py
```

Deixe rodar por **30 segundos**

### 3. Pare com Ctrl+C

### 4. Verifique novamente:

```bash
curl https://gta-analytics-backend.fly.dev/stats
```

**COMPARAÇÃO:**
```
Antes:  frames_received: 242
Depois: frames_received: 362

DIFERENÇA: 362 - 242 = 120 frames

120 frames em 30 segundos = 4 FPS ✅ PERFEITO!
```

---

## ✅ CHECKLIST DE SUCESSO

Marque conforme testa:

- [ ] OBS mostrando Naruto Online no preview
- [ ] WebSocket ativado (porta 4455)
- [ ] `py gta-analytics-v2.py` roda sem erros
- [ ] Mostra "Conectado ao OBS"
- [ ] Mostra "Cena atual: narutoonline" (ou nome da sua cena)
- [ ] Contador de frames aumenta (20, 40, 60...)
- [ ] `0 erros` (sem erros de envio)
- [ ] `curl /stats` mostra `frames_received` aumentando
- [ ] Diferença de ~4 frames por segundo

**Se todos marcados → SISTEMA FUNCIONANDO 100%! 🎉**

---

## ⚠️ PROBLEMAS COMUNS

### "Erro: Não foi possível conectar ao OBS"
**Solução:**
1. Verifique se OBS está aberto
2. Verifique se WebSocket está ativo
3. Tente reiniciar o OBS

### "Frames enviados mas stats não aumenta"
**Solução:**
1. Aguarde ~10 segundos (pode ter delay)
2. Verifique internet
3. Tente: `curl https://gta-analytics-gateway.fly.dev/health`

### "Muitos erros aparecendo"
**Solução:**
1. Verifique conexão com internet
2. Gateway pode estar sobrecarregado (aguarde 1 min)
3. Tente reiniciar o capturador

### "FPS muito baixo (< 3)"
**Solução:**
1. Normal se PC estiver lento
2. Feche outros programas
3. Reduza qualidade no OBS

---

## 📊 DEPOIS DO TESTE

### Se tudo funcionou:

**Você confirmou:**
1. ✅ Cliente captura do OBS
2. ✅ Envia para Gateway
3. ✅ Gateway repassa para Backend
4. ✅ Backend processa frames
5. ✅ Filtro pixel funciona
6. ✅ Vision API analisa frames

**Sistema está 100% pronto para GTA!**

### Próximos passos:

1. Testar com GTA V (para ver kills sendo detectadas)
2. Configurar teams/roster para torneio do Luis
3. Testar dashboard no celular
4. Empacotar tudo para enviar

---

## 🎮 DICA PARA TESTE VISUAL

Se quiser VER o que está sendo capturado:

1. Durante o teste, tire um print da tela
2. A região capturada é:
   - X: 1400px da esquerda
   - Y: 0px do topo
   - Largura: 520px
   - Altura: 400px

No Naruto, isso vai capturar o canto superior direito da tela.
No GTA, é exatamente onde fica o kill feed!

---

**Pronto para testar? Execute e me mostre os resultados!** 🚀
