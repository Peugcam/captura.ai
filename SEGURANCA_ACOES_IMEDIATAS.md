# 🚨 AÇÕES DE SEGURANÇA IMEDIATAS

## ⚠️ ATENÇÃO: API Keys Expostas no .env

Suas chaves API estão **em texto plano** no arquivo `backend/.env`.

---

## 🔴 AÇÃO CRÍTICA NECESSÁRIA

### 1. **ROTACIONAR as API Keys IMEDIATAMENTE**

As seguintes chaves foram detectadas e precisam ser rotacionadas:

```
sk-proj-ueD-NGhe_QIov3USzlrg... (OpenAI)
sk-or-v1-256a8c3dffcc6e109b5... (OpenRouter)
```

#### Como Rotacionar:

**OpenAI:**
1. Acesse: https://platform.openai.com/api-keys
2. Revogue a chave antiga: `sk-proj-ueD-NGhe_QIov3USzlrg...`
3. Crie uma nova chave
4. Atualize o arquivo `backend/.env`

**OpenRouter:**
1. Acesse: https://openrouter.ai/keys
2. Revoque a chave antiga: `sk-or-v1-256a8c3dffcc6e109b5...`
3. Crie uma nova chave
4. Atualize o arquivo `backend/.env`

### 2. **VERIFICAR o Histórico do Git**

```bash
cd "C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2"

# Verificar se .env foi commitado alguma vez
git log --all --pretty=format:"%H" -- backend/.env

# Se retornar algo, SUAS CHAVES ESTÃO NO HISTÓRICO!
```

**Se o arquivo `.env` apareceu no histórico:**
```bash
# OPÇÃO 1: Limpar histórico (CUIDADO - reescreve histórico)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/.env" \
  --prune-empty --tag-name-filter cat -- --all

# OPÇÃO 2: Mais seguro - tornar repositório privado
# No GitHub: Settings > General > Danger Zone > Change visibility > Make private
```

### 3. **TORNAR o Repositório Privado**

Se o repositório está no GitHub/GitLab público:

1. Vá em **Settings** do repositório
2. **Danger Zone** > **Change visibility**
3. Selecione **Private**

---

## ✅ Melhorias de Segurança Implementadas

Durante a análise, as seguintes melhorias foram aplicadas:

### 1. Validação de API Keys
- ✅ Detecta chaves de exemplo/placeholder
- ✅ Valida formato básico
- ✅ Mascara chaves nos logs (`sk-pr...RlAA` ao invés da chave completa)

**Arquivo:** `backend/config.py`

### 2. Proteção contra Path Traversal
- ✅ Valida que arquivos exportados ficam no diretório correto
- ✅ Previne acesso a arquivos sensíveis do sistema

**Arquivo:** `backend/main_websocket.py` (linha 353-360)

### 3. Rate Limiting no WebSocket
- ✅ Máximo 100 conexões simultâneas
- ✅ Máximo 60 mensagens/minuto por cliente
- ✅ Mensagens limitadas a 1KB

**Arquivo:** `backend/main_websocket.py` (linha 410-425)

### 4. CORS Configurável
- ✅ Agora configurável via variável `ALLOWED_ORIGINS`
- ✅ Aviso se configurado para aceitar todas origens

**Arquivo:** `backend/main_websocket.py` (linha 255-267)

### 5. Módulo de Segurança Centralizado
- ✅ Validadores reutilizáveis
- ✅ Sanitização de logs
- ✅ Proteção contra path traversal
- ✅ Rate limiter genérico

**Arquivo:** `backend/src/security.py`

### 6. Template .env Atualizado
- ✅ Documentação de segurança inline
- ✅ Placeholders seguros
- ✅ Boas práticas documentadas

**Arquivo:** `backend/.env.example`

---

## 📋 Checklist Pós-Implementação

Execute estas verificações agora:

### Imediato (próximos 30 minutos):

- [ ] 🔴 **CRÍTICO:** Rotacionar API keys no OpenAI e OpenRouter
- [ ] 🔴 **CRÍTICO:** Atualizar `backend/.env` com novas chaves
- [ ] 🟡 Verificar se `.env` foi commitado ao Git
- [ ] 🟡 Tornar repositório privado (se público)

### Hoje:

- [ ] ✅ Testar que o backend ainda funciona com novas chaves
  ```bash
  cd backend
  python main_websocket.py
  ```
- [ ] ✅ Verificar logs por erros de autenticação
- [ ] ✅ Configurar `ALLOWED_ORIGINS` no `.env` (se em produção)

### Esta Semana:

- [ ] ✅ Ler documentação completa em `SECURITY.md`
- [ ] ✅ Configurar Git hooks (ver `SECURITY.md`)
- [ ] ✅ Configurar alertas de monitoramento
- [ ] ✅ Fazer backup seguro das credenciais (gerenciador de senhas)

---

## 🔧 Exemplo de .env Seguro

Seu `backend/.env` deve ficar assim após rotação:

```env
# =============================================================================
# GTA Analytics V2 - Environment Configuration
# =============================================================================
# SECURITY: Never commit this file to version control!
# =============================================================================

# Gateway Configuration
GATEWAY_URL=http://localhost:8000
POLL_INTERVAL=1.0
FRAMES_BATCH_SIZE=10

# OCR Configuration
OCR_ENABLED=true
OCR_WORKERS=4

# Game Configuration
GAME_TYPE=gta
USE_ROI=false

# API Keys (SENSITIVE - ROTATED)
# Format: key1,key2,key3
API_KEYS=sk-proj-[NOVA_CHAVE_OPENAI],sk-or-v1-[NOVA_CHAVE_OPENROUTER]

# Vision Model
VISION_MODEL=openai/gpt-4o
BATCH_SIZE_QUICK=3
BATCH_SIZE_DEEP=5
QUICK_BATCH_INTERVAL=0.5
DEEP_BATCH_INTERVAL=5.0

# Backend Server
BACKEND_PORT=3000
BACKEND_HOST=0.0.0.0

# CORS (Production: specific origins only)
ALLOWED_ORIGINS=http://localhost:8080

# Export
EXPORT_DIR=./exports

# Logging (Production: WARNING or ERROR)
LOG_LEVEL=INFO
```

---

## 📚 Próximos Passos

1. ✅ **Leia:** `SECURITY.md` para entender todas as melhorias
2. ✅ **Configure:** Git hooks para prevenir commits acidentais
3. ✅ **Agende:** Rotação de chaves trimestral (próxima: 08/05/2026)
4. ✅ **Monitore:** Logs de segurança regularmente

---

## ❓ FAQ

### "Já commitei o .env, e agora?"

1. Rotacione TODAS as chaves imediatamente
2. Torne o repositório privado
3. Use `git filter-branch` para limpar histórico (avançado)
4. Considere criar novo repositório limpo

### "Como saber se minhas chaves foram usadas indevidamente?"

**OpenAI:**
- Acesse: https://platform.openai.com/usage
- Verifique uso nos últimos 30 dias
- Procure por picos ou horários incomuns

**OpenRouter:**
- Acesse: https://openrouter.ai/activity
- Verifique histórico de requisições
- Procure por IPs desconhecidos

### "Posso continuar usando o sistema enquanto rotaciono?"

Não. Pare o backend, rotacione as chaves, atualize o `.env`, e reinicie.

```bash
# 1. Parar
taskkill /F /IM python.exe

# 2. Rotacionar chaves (via web)

# 3. Editar .env
notepad backend\.env

# 4. Reiniciar
cd backend
python main_websocket.py
```

---

## 📞 Precisa de Ajuda?

- 📖 Documentação completa: `SECURITY.md`
- 🔍 Análise detalhada: Ver seção "Análise de Vulnerabilidades"
- 🛠️ Ferramentas de segurança: Ver seção "Recursos Adicionais"

---

**Data desta Análise:** 08/02/2026
**Status:** ⚠️ Ação Imediata Necessária
**Prioridade:** 🔴 Crítica
