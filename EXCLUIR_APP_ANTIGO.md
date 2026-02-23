# 🗑️ EXCLUIR APP ANTIGO DO FLY.IO

## 📋 Apps no Fly.io:

```
✅ MANTER: gta-analytics-v2.fly.dev
   - Dashboard funcionando
   - Versão atual

❌ EXCLUIR: gta-analytics-backend.fly.dev
   - Versão antiga
   - Dashboard desatualizado
```

---

## 🚀 COMO EXCLUIR O APP ANTIGO:

### Passo 1: Listar todos os apps

```bash
flyctl apps list
```

Você deve ver algo como:
```
NAME                          OWNER       STATUS
gta-analytics-backend         personal    running
gta-analytics-v2              personal    running
gta-analytics-gateway         personal    running
```

### Passo 2: Verificar qual vai excluir

```bash
flyctl status -a gta-analytics-backend
```

Certifique-se que é o app correto (antigo)!

### Passo 3: Excluir o app antigo

```bash
flyctl apps destroy gta-analytics-backend
```

Vai pedir confirmação:
```
? Destroy app gta-analytics-backend? Yes
```

Digite: `Yes` (com Y maiúsculo)

### Passo 4: Confirmar exclusão

```bash
flyctl apps list
```

O app `gta-analytics-backend` NÃO deve mais aparecer! ✅

---

## ⚠️ ANTES DE EXCLUIR:

### Certifique-se que:

1. ✅ O V2 está funcionando:
```bash
curl https://gta-analytics-v2.fly.dev/health
```

2. ✅ O dashboard V2 está acessível:
```
https://gta-analytics-v2.fly.dev/strategist
```

3. ✅ O config.json foi atualizado para V2:
```json
{
  "gateway_url": "https://gta-analytics-v2.fly.dev",
  ...
}
```

4. ✅ Teste enviando alguns frames pro V2

---

## 💰 ECONOMIA:

Excluindo o app antigo você economiza:

- **CPU/RAM:** ~$5-10/mês
- **Armazenamento:** Depende do banco de dados
- **Mais limpo:** Menos apps para gerenciar

---

## 📝 SCRIPT AUTOMÁTICO:

Crie `EXCLUIR_BACKEND_ANTIGO.bat`:

```batch
@echo off
echo ====================================================================
echo   EXCLUIR APP ANTIGO DO FLY.IO
echo ====================================================================
echo.
echo ATENCAO: Isso vai EXCLUIR PERMANENTEMENTE:
echo   - gta-analytics-backend.fly.dev
echo   - Todos os dados desse app
echo   - Configuracoes e secrets
echo.
echo CERTIFIQUE-SE que o V2 esta funcionando ANTES de continuar!
echo.
pause

echo.
echo [1/3] Listando apps...
flyctl apps list

echo.
echo [2/3] Verificando app antigo...
flyctl status -a gta-analytics-backend

echo.
echo Confirme novamente: Deseja EXCLUIR este app?
pause

echo.
echo [3/3] Excluindo app...
flyctl apps destroy gta-analytics-backend --yes

echo.
echo ====================================================================
echo   APP ANTIGO EXCLUIDO
echo ====================================================================
echo.
echo Apps restantes:
flyctl apps list

echo.
pause
```

---

## 🔄 ALTERNATIVA: PAUSAR AO INVÉS DE EXCLUIR

Se quiser manter o app mas não pagar:

```bash
# Suspender app (para de rodar mas mantém dados)
flyctl apps suspend gta-analytics-backend
```

Para reativar depois:
```bash
flyctl apps resume gta-analytics-backend
```

---

## 🎯 RESUMO RÁPIDO:

**Para excluir o app antigo:**

```bash
# 1. Verifique
flyctl apps list

# 2. Exclua
flyctl apps destroy gta-analytics-backend

# 3. Confirme "Yes"

# 4. Verifique
flyctl apps list
```

**Pronto! App antigo removido!** ✅

---

**Quer excluir agora?** Execute os comandos acima ou use o script! 🗑️
