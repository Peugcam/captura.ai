# ⚡ TESTE RÁPIDO - 2 MINUTOS

## ✅ O QUE VOCÊ JÁ TEM PRONTO

- Gateway online ✅
- Backend online ✅
- OBS com WebSocket ativado ✅
- Cliente de captura funcionando ✅

---

## 🎯 TESTE AGORA (2 PASSOS)

### PASSO 1: Execute o capturador

Abra o terminal e rode:

```bash
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\pacote-luis
py gta-analytics-v2.py
```

**O que você deve ver:**

```
======================================================================
   GTA ANALYTICS - KILL FEED TRACKER
======================================================================

[OK] Gateway online: https://gta-analytics-gateway.fly.dev
[OK] Conectado ao OBS (localhost:4455)
[OK] Cena atual: narutoonline

======================================================================
   CAPTURA ATIVA
======================================================================

[20 frames] 5s | 4.0 FPS | 0 erros
[40 frames] 10s | 4.0 FPS | 0 erros
[60 frames] 15s | 4.0 FPS | 0 erros
```

**Deixe rodando por 20-30 segundos...**

### PASSO 2: Verifique se está funcionando

Abra outro terminal e rode:

```bash
curl https://gta-analytics-backend.fly.dev/stats
```

**Você deve ver algo como:**

```json
{
  "frames_received": 80,      ← Deve estar aumentando!
  "frames_filtered": 45,
  "frames_processed": 35,
  "kills_detected": 0,        ← Normal se não tiver jogo
  "filter_efficiency": "56.2%",
  "teams": 0,
  "players": 0,
  "alive": 0,
  "dead": 0
}
```

**✅ SE `frames_received` ESTÁ AUMENTANDO → FUNCIONANDO!**

---

## 🎮 PRÓXIMO TESTE (COM JOGO)

### Se você quiser testar com jogo agora:

1. **Abra qualquer jogo que tenha kill feed no canto superior direito**
   - GTA V Online
   - CS:GO
   - Valorant
   - Qualquer FPS

2. **Configure OBS:**
   - Adicione fonte: "Captura de Jogo"
   - Selecione o jogo
   - Certifique-se que aparece no OBS

3. **Execute novamente:**
```bash
py gta-analytics-v2.py
```

4. **Jogue e deixe kills acontecerem**

5. **Verifique detecção:**
```bash
curl https://gta-analytics-backend.fly.dev/stats
```

Agora `"kills_detected"` deve estar > 0!

---

## 📊 DASHBOARDS PARA VER RESULTADO

### Dashboard Principal:
```
https://gta-analytics-backend.fly.dev/player
```

### Dashboard de Torneio:
```
https://gta-analytics-backend.fly.dev/tournament
```

Abra no navegador (PC ou celular)

---

## ⚠️ TROUBLESHOOTING

### "Erro ao conectar OBS"
→ Verifique se OBS está aberto
→ Verifique se WebSocket está ativo (Ferramentas → WebSocket)

### "Gateway offline"
→ Verifique internet
→ Teste: `curl https://gta-analytics-gateway.fly.dev/health`

### "0 frames" ou não aumenta
→ OBS precisa ter uma cena ativa
→ Tente trocar de cena no OBS

### "Kills não são detectadas"
→ Normal se não tiver jogo rodando
→ Precisa ter kill feed visível na tela
→ Kill feed precisa estar no canto superior direito

---

## ✅ CHECKLIST DE SUCESSO

Execute e marque:

- [ ] `py gta-analytics-v2.py` roda sem erros
- [ ] Mostra "CAPTURA ATIVA"
- [ ] Contador de frames aumenta (20, 40, 60...)
- [ ] `curl /stats` mostra `frames_received` > 0
- [ ] `frames_received` aumenta a cada chamada
- [ ] Nenhum erro no terminal

**Se todos marcados → SISTEMA 100% FUNCIONAL! 🎉**

---

## 🚀 DEPOIS DO TESTE

Se tudo funcionou, próximos passos:

1. **Testar com GTA real** (opcional)
2. **Criar instalador final** (INSTALAR_TUDO.bat)
3. **Zipar pacote para Luis**
4. **Enviar para Vitor**

---

**Qualquer dúvida, veja `STATUS_DO_SISTEMA.md` para detalhes técnicos.**
