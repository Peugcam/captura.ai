# 🔒 Documentação de Segurança - GTA Analytics V2

**Versão:** 2.0.0
**Data:** 08/02/2026
**Autor:** Análise de Segurança Automatizada

---

## 📋 Índice

1. [Sumário Executivo](#sumário-executivo)
2. [Análise de Vulnerabilidades](#análise-de-vulnerabilidades)
3. [Melhorias Implementadas](#melhorias-implementadas)
4. [Configuração Segura](#configuração-segura)
5. [Boas Práticas de Desenvolvimento](#boas-práticas-de-desenvolvimento)
6. [Checklist de Segurança](#checklist-de-segurança)
7. [Resposta a Incidentes](#resposta-a-incidentes)

---

## 🎯 Sumário Executivo

### Status de Segurança

**Nível de Risco Atual:** ⚠️ **MÉDIO**

### Principais Descobertas

#### ✅ Pontos Fortes
- ✅ Nenhum uso de funções perigosas (`eval`, `exec`, `__import__`)
- ✅ Dependências atualizadas (FastAPI 0.109.0, Uvicorn 0.27.0)
- ✅ `.gitignore` configurado corretamente para excluir `.env`
- ✅ Sanitização básica de entrada em OCR
- ✅ Uso de tipos seguros (type hints em todo código)

#### 🚨 Vulnerabilidades Críticas Identificadas

1. **[CRÍTICO] Exposição de API Keys em Texto Plano**
   - **Arquivo:** `backend/.env` (linha 19)
   - **Impacto:** Vazamento de credenciais sensíveis
   - **Status:** ⚠️ **REQUER AÇÃO IMEDIATA**

2. **[ALTO] CORS Permissivo**
   - **Arquivo:** `backend/main_websocket.py` (linha 257)
   - **Impacto:** Permite requisições de qualquer origem
   - **Status:** ✅ **CORRIGIDO** (agora com warning e configuração)

3. **[MÉDIO] Falta de Rate Limiting Global**
   - **Impacto:** Vulnerável a ataques de negação de serviço
   - **Status:** ✅ **PARCIALMENTE CORRIGIDO** (implementado no WebSocket)

4. **[MÉDIO] Logs Podem Expor Dados Sensíveis**
   - **Impacto:** API keys podem aparecer em logs
   - **Status:** ✅ **CORRIGIDO** (sanitização implementada)

5. **[BAIXO] Falta de Validação de Path no Export**
   - **Impacto:** Possível path traversal
   - **Status:** ✅ **CORRIGIDO**

---

## 🔍 Análise de Vulnerabilidades

### 1. Gerenciamento de Credenciais

#### Problema Identificado
```env
# backend/.env (EXEMPLO DE CONFIGURAÇÃO INSEGURA)
API_KEYS=sk-proj-ueD-NGhe_QIov3USzlrg...,sk-or-v1-256a8c3d...
```

**Risco:** Chaves API em texto plano no sistema de arquivos

#### Impacto
- 🔴 **Crítico:** Se o arquivo `.env` for commitado, as chaves são expostas publicamente
- 🔴 **Crítico:** Acesso ao sistema de arquivos = acesso às chaves
- 🟡 **Médio:** Logs de erro podem expor as chaves

#### Mitigação Implementada
```python
# backend/config.py - Validação e sanitização de API keys
def validate_api_key(key: str) -> bool:
    """Valida formato e detecta placeholders"""
    # Valida tamanho, formato e detecta chaves de exemplo

def sanitize_config_value(value: str, is_sensitive: bool = False) -> str:
    """Mascara dados sensíveis em logs"""
    # Mostra apenas sk-proj...RlAA ao invés da chave completa
```

### 2. WebSocket Security

#### Vulnerabilidades Encontradas
- ❌ Sem limite de conexões simultâneas
- ❌ Sem rate limiting de mensagens
- ❌ Sem validação de tamanho de mensagem
- ❌ CORS muito permissivo

#### Melhorias Implementadas

```python
class ConnectionManager:
    def __init__(self, max_connections: int = 100):
        # Limite de 100 conexões simultâneas

    async def connect(self, websocket: WebSocket):
        # Rejeita conexões acima do limite
        if len(self.active_connections) >= self.max_connections:
            await websocket.close(code=1008)
```

**Rate Limiting:**
```python
# 60 mensagens/minuto por cliente
# Mensagens maiores que 1KB são rejeitadas
message_count = 0
if message_count > 60:
    logger.warning("Client exceeded rate limit")
    continue
```

### 3. Path Traversal Protection

#### Vulnerabilidade Original
```python
# INSEGURO
filepath = f"{config.EXPORT_DIR}/{filename}"
backend.processor.export_to_excel(filepath)
```

**Ataque possível:**
```
filename = "../../etc/passwd"
# Resultaria em: ./exports/../../etc/passwd
```

#### Correção Implementada
```python
# SEGURO
export_dir_abs = os.path.abspath(config.EXPORT_DIR)
filepath_abs = os.path.abspath(os.path.join(export_dir_abs, filename))

if not filepath_abs.startswith(export_dir_abs):
    raise HTTPException(status_code=400, detail="Invalid file path")
```

### 4. Input Validation

#### Validações Adicionadas

**Formato de Export:**
```python
valid_formats = ["luis", "standard", "advanced"]
if format not in valid_formats:
    raise HTTPException(status_code=400)
```

**Nome de Arquivo:**
```python
# Sanitiza caracteres perigosos
safe_format = "".join(c for c in format if c.isalnum())
```

---

## ✅ Melhorias Implementadas

### 1. Módulo de Segurança Centralizado

**Arquivo:** `backend/src/security.py`

#### Funcionalidades

```python
from src.security import SecurityValidator

# Validação de arquivos
SecurityValidator.validate_filename("report.xlsx", allowed_extensions=['.xlsx'])

# Proteção contra path traversal
safe_path = SecurityValidator.validate_path(user_input, base_dir)

# Sanitização de logs
safe_log = SecurityValidator.sanitize_log_message(user_input)

# Máscara de dados sensíveis
masked = SecurityValidator.mask_sensitive_data(api_key)  # "sk-pr...RlAA"
```

### 2. Rate Limiter

```python
from src.security import RateLimiter

limiter = RateLimiter(max_requests=100, window_seconds=60)

if not limiter.is_allowed(client_id):
    raise HTTPException(status_code=429, detail="Rate limit exceeded")
```

### 3. Configuração CORS Melhorada

```env
# backend/.env
ALLOWED_ORIGINS=http://localhost:8080,https://yourdomain.com
```

```python
# main_websocket.py
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if "*" in ALLOWED_ORIGINS:
    logger.warning("CORS configured for all origins (*)")
```

### 4. Logging Seguro

```python
# Antes (INSEGURO)
logger.info(f"API key: {api_key}")

# Depois (SEGURO)
logger.info(f"API key loaded: {sanitize_config_value(api_key, is_sensitive=True)}")
```

---

## 🔧 Configuração Segura

### Variáveis de Ambiente

#### Template Seguro (`.env.example`)

```env
# =============================================================================
# SECURITY: Never commit the real .env file!
# =============================================================================

# API Keys (SENSITIVE)
API_KEYS=your_openai_key_here,your_openrouter_key_here

# CORS (Production)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=3000

# Logging (Production: WARNING or ERROR)
LOG_LEVEL=INFO
```

#### Configuração de Produção vs Desenvolvimento

| Configuração | Desenvolvimento | Produção |
|-------------|----------------|----------|
| `LOG_LEVEL` | `DEBUG` | `WARNING` |
| `ALLOWED_ORIGINS` | `*` | Lista específica |
| `BACKEND_HOST` | `127.0.0.1` | `0.0.0.0` |
| API Keys | Chaves de teste | Chaves de produção |

### Permissões de Arquivo (Linux/Mac)

```bash
# Proteger arquivo .env
chmod 600 backend/.env

# Diretório de exportação
chmod 755 backend/exports

# Logs
chmod 640 backend/*.log
```

### Firewall e Rede

```bash
# Permitir apenas tráfego necessário
ufw allow 3000/tcp  # Backend
ufw allow 8000/tcp  # Gateway
ufw enable
```

---

## 👨‍💻 Boas Práticas de Desenvolvimento

### 1. Nunca Commitar Credenciais

#### Git Hooks (Pre-commit)

Crie `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Verifica se .env será commitado
if git diff --cached --name-only | grep -q "\.env$"; then
    echo "❌ ERRO: Tentativa de commitar arquivo .env!"
    echo "📝 Use .env.example ao invés disso."
    exit 1
fi

# Procura por padrões de API keys
if git diff --cached -U0 | grep -E "(sk-[a-zA-Z0-9]{20,}|api[_-]?key.*=.*[a-zA-Z0-9]{20,})"; then
    echo "⚠️  AVISO: Possível API key detectada no commit!"
    read -p "Continuar? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

### 2. Rotação Regular de Chaves

#### Checklist de Rotação (a cada 90 dias)

1. ✅ Gerar novas API keys nos provedores
2. ✅ Atualizar `backend/.env` com novas chaves
3. ✅ Reiniciar backend
4. ✅ Validar funcionamento
5. ✅ Revogar chaves antigas
6. ✅ Documentar data da rotação

### 3. Monitoramento de Segurança

#### Logs a Monitorar

```python
# Padrões suspeitos nos logs
SUSPICIOUS_PATTERNS = [
    "Path traversal detected",
    "Rate limit exceeded",
    "Invalid API key",
    "Connection limit reached",
    "Invalid file path"
]
```

#### Alertas Recomendados

- 🔴 **Crítico:** Mais de 10 tentativas de path traversal em 1 hora
- 🟡 **Médio:** Mais de 50 conexões WebSocket simultâneas
- 🟡 **Médio:** API key inválida detectada
- 🔵 **Info:** Export realizado (auditoria)

### 4. Testes de Segurança

#### Suite de Testes Recomendada

```python
# tests/security_tests.py

def test_path_traversal():
    """Tenta exportar para path malicioso"""
    response = client.post("/export", json={
        "format": "../../../etc/passwd"
    })
    assert response.status_code == 400

def test_rate_limiting():
    """Testa limite de requisições"""
    for i in range(101):
        response = client.get("/stats")
    assert response.status_code == 429

def test_invalid_api_key():
    """Testa detecção de API key inválida"""
    os.environ["API_KEYS"] = "invalid_key"
    with pytest.raises(ValueError):
        import config
```

---

## ✅ Checklist de Segurança

### Antes de Deploy

- [ ] ✅ Arquivo `.env` está no `.gitignore`
- [ ] ✅ API keys de produção geradas e configuradas
- [ ] ✅ `ALLOWED_ORIGINS` configurado com domínios específicos
- [ ] ✅ `LOG_LEVEL` configurado para `WARNING` ou `ERROR`
- [ ] ✅ HTTPS configurado (certificado SSL válido)
- [ ] ✅ Firewall configurado
- [ ] ✅ Backup de configuração realizado
- [ ] ✅ Testes de segurança executados
- [ ] ✅ Documentação atualizada

### Após Deploy

- [ ] ✅ Validar que `.env` não foi commitado
- [ ] ✅ Verificar logs por mensagens de erro
- [ ] ✅ Testar endpoints de produção
- [ ] ✅ Configurar alertas de monitoramento
- [ ] ✅ Documentar credenciais de forma segura (gerenciador de senhas)

### Manutenção Regular (Mensal)

- [ ] ✅ Revisar logs de segurança
- [ ] ✅ Verificar vulnerabilidades de dependências
  ```bash
  pip install safety
  safety check
  ```
- [ ] ✅ Atualizar dependências
  ```bash
  pip list --outdated
  ```
- [ ] ✅ Verificar tamanho dos logs (rotação se necessário)
- [ ] ✅ Revisar acessos e permissões

### Rotação de Chaves (Trimestral - 90 dias)

- [ ] ✅ Gerar novas API keys
- [ ] ✅ Atualizar `.env` de produção
- [ ] ✅ Reiniciar serviços
- [ ] ✅ Revogar chaves antigas
- [ ] ✅ Documentar data da rotação

---

## 🚨 Resposta a Incidentes

### Cenário 1: Exposição de API Key

#### Sintomas
- Custo inesperado nas APIs
- Alertas de uso anômalo
- API key encontrada em repositório público

#### Ações Imediatas (15 minutos)

1. **REVOGAR** a chave exposta imediatamente
   - OpenAI: https://platform.openai.com/api-keys
   - OpenRouter: https://openrouter.ai/keys

2. **GERAR** nova chave

3. **ATUALIZAR** `.env` em produção
   ```bash
   ssh production
   cd /path/to/gta-analytics-v2/backend
   nano .env  # Atualizar API_KEYS
   ```

4. **REINICIAR** o backend
   ```bash
   systemctl restart gta-analytics-backend
   # ou
   pm2 restart gta-analytics
   ```

5. **VERIFICAR** logs por uso não autorizado
   ```bash
   grep "API" /var/log/gta-analytics/*.log | grep -v "200 OK"
   ```

#### Ações de Seguimento (24 horas)

1. ✅ Analisar como a chave foi exposta
2. ✅ Verificar se outras credenciais foram comprometidas
3. ✅ Revisar commits recentes no Git
4. ✅ Implementar proteções adicionais
5. ✅ Documentar o incidente

### Cenário 2: Ataque de Negação de Serviço (DoS)

#### Sintomas
- Backend lento ou não responsivo
- Logs mostram "Rate limit exceeded"
- Muitas conexões WebSocket simultâneas

#### Ações Imediatas

1. **VERIFICAR** logs para identificar atacante
   ```bash
   tail -f /var/log/gta-analytics/main_websocket.log | grep "Rate limit"
   ```

2. **BLOQUEAR** IP do atacante
   ```bash
   ufw deny from 123.45.67.89
   ```

3. **REINICIAR** o serviço se necessário
   ```bash
   systemctl restart gta-analytics-backend
   ```

4. **REDUZIR** limites temporariamente
   ```env
   # .env
   MAX_WEBSOCKET_CONNECTIONS=50  # De 100 para 50
   ```

---

## 📚 Recursos Adicionais

### Ferramentas de Segurança

```bash
# Análise de vulnerabilidades em dependências
pip install safety
safety check

# Análise estática de código
pip install bandit
bandit -r backend/

# Verificar secrets no Git
pip install detect-secrets
detect-secrets scan
```

### Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/secrets.html)

---

## 📞 Contato

**Em caso de descoberta de vulnerabilidade:**
- 📧 Email: security@yourdomain.com
- 🔒 GPG Key: [Link para chave pública]
- 📝 Responsible Disclosure Policy: [Link]

---

**Última Atualização:** 08/02/2026
**Próxima Revisão:** 08/05/2026 (Trimestral)
