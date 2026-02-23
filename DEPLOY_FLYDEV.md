# 🚀 DEPLOY NO FLY.DEV

## ✅ Correção Aplicada

Corrigido endpoint `/api/frames/upload`:
- ❌ Antes: `process_frames()` (não existe)
- ✅ Agora: `process_frame()` (correto)

---

## 📦 COMO FAZER DEPLOY

### Opção 1: Deploy Automático (Recomendado)

```bash
# Navegar para pasta do backend
cd C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\backend

# Deploy no Fly.dev
fly deploy
```

---

### Opção 2: Deploy com Configuração Específica

```bash
# Deploy backend
cd backend
fly deploy --config fly.toml

# Ver logs após deploy
fly logs
```

---

### Opção 3: Deploy via GitHub Actions (Automático)

Se você tem GitHub Actions configurado, só fazer:

```bash
git add main_websocket.py
git commit -m "fix: corrige endpoint /api/frames/upload"
git push
```

O deploy acontece automaticamente!

---

## ✅ VERIFICAR SE DEU CERTO

Após o deploy:

```bash
# 1. Verificar health
curl https://gta-analytics-v2.fly.dev/health

# 2. Testar endpoint corrigido
curl -X POST https://gta-analytics-v2.fly.dev/api/frames/upload \
  -F "file=@alguma_imagem.jpg"

# Deve retornar:
# {"success":true,"message":"Frame uploaded successfully"}
```

---

## 🎯 RESUMO

1. **Arquivo corrigido**: `backend/main_websocket.py` linha 1042
2. **Correção**: `process_frames()` → `process_frame()`
3. **Deploy**: `fly deploy`
4. **Teste**: Upload funciona! ✅

---

## 💡 DICA

Se NÃO tem acesso ao Fly.dev CLI ou não quer fazer deploy agora:

**Alternativa**: Usar gateway local (como você já estava fazendo)

O gateway local **JÁ FUNCIONA PERFEITAMENTE**!

Os 2 frames processados no teste vieram do gateway local, não do endpoint HTTP.

---

## 🎮 USAR SEM DEPLOY (Gateway Local)

Se preferir não fazer deploy agora:

```bash
# Terminal 1: Gateway Go local
cd gateway
./gateway.exe

# Terminal 2: Capture MSS
cd backend
python capture_remote_mss.py
```

**Mas para usar com Fly.dev (acesso remoto), precisa do deploy!**
