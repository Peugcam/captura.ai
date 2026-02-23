# 🔨 GTA ANALYTICS - GUIA DE BUILD

**Como compilar e gerar o executável final para distribuição**

---

## 📋 PRÉ-REQUISITOS

### Software Necessário

1. **Node.js 18+**
   - Download: https://nodejs.org/
   - Versão LTS recomendada
   - Verificar: `node --version`

2. **Python 3.10+**
   - Download: https://www.python.org/downloads/
   - ⚠️ **IMPORTANTE:** Marcar "Add Python to PATH" durante instalação
   - Verificar: `python --version`

3. **Git** (opcional)
   - Download: https://git-scm.com/
   - Para clonar repositório

### Ferramentas Adicionais (Windows)

4. **Visual Studio Build Tools** (para PyInstaller)
   - Download: https://visualstudio.microsoft.com/downloads/
   - Baixar "Build Tools for Visual Studio 2022"
   - Instalar workload: "Desktop development with C++"

---

## 🚀 PROCESSO DE BUILD COMPLETO

### Passo 1: Setup Inicial (apenas 1x)

```bash
# Navegar para pasta do projeto
cd gta-analytics-v2/electron-app

# Instalar dependências Node.js
npm install

# Verificar instalação
npm list electron
npm list electron-builder
```

**Resultado esperado:**
```
✅ electron@28.0.0
✅ electron-builder@24.9.0
```

---

### Passo 2: Build Python Executable

```bash
# Navegar para pasta Python
cd python

# Instalar dependências Python
pip install -r requirements.txt

# Instalar PyInstaller
pip install pyinstaller

# Build executável
pyinstaller --onefile --name capture --icon=../assets/icon.ico --console capture.py

# Ou simplesmente rodar o script batch (Windows)
build.bat
```

**Resultado esperado:**
```
✅ dist/capture.exe criado (~50-80 MB)
```

**Testar executável:**
```bash
cd dist
capture.exe --server https://gta-analytics-v2.fly.dev --fps 0.5
```

Se funcionar (captura frames), está OK! ✅

---

### Passo 3: Voltar para Electron

```bash
# Voltar para pasta electron-app
cd ..  # (se estava em python/)
```

---

### Passo 4: Build Electron App

#### Opção A: Build Completo (Instalador + Portável)

```bash
npm run build
```

**Tempo:** ~3-5 minutos

**Arquivos gerados:**
```
dist/
├── GTA-Analytics-1.0.0-Setup.exe        (~85-100 MB) ⭐ PRINCIPAL
├── GTA-Analytics-1.0.0-Portable.exe     (~85-100 MB)
└── win-unpacked/                         (pasta com arquivos)
```

#### Opção B: Build Apenas Diretório (Mais Rápido)

```bash
npm run build:dir
```

**Tempo:** ~1-2 minutos

**Arquivos gerados:**
```
dist/
└── win-unpacked/
    ├── GTA-Analytics.exe
    ├── resources/
    └── ...
```

**Usar:** Rodar `win-unpacked/GTA-Analytics.exe` diretamente

---

### Passo 5: Testar Build

```bash
# Testar instalador
cd dist
start GTA-Analytics-1.0.0-Setup.exe

# Ou testar versão unpacked
cd win-unpacked
start GTA-Analytics.exe
```

**Verificar:**
- ✅ App abre normalmente
- ✅ Interface carrega
- ✅ Botão "Iniciar Captura" funciona
- ✅ Python executa (ver log)

---

## 📦 DISTRIBUIÇÃO

### GitHub Releases (Recomendado)

1. **Fazer commit das mudanças:**
```bash
git add .
git commit -m "Release v1.0.0"
git tag v1.0.0
git push origin v1.0.0
```

2. **Criar release:**
```bash
# Usando GitHub CLI
gh release create v1.0.0 \
  dist/GTA-Analytics-1.0.0-Setup.exe \
  dist/GTA-Analytics-1.0.0-Portable.exe \
  --title "GTA Analytics v1.0.0" \
  --notes "Initial release - Desktop app para analytics GTA V"

# Ou manualmente no GitHub:
# https://github.com/user/repo/releases/new
```

3. **URL de download:**
```
https://github.com/seu-usuario/gta-analytics/releases/download/v1.0.0/GTA-Analytics-1.0.0-Setup.exe
```

### Alternativas

**Google Drive:**
- Upload `GTA-Analytics-1.0.0-Setup.exe`
- Compartilhar link "Anyone with the link"

**Dropbox / OneDrive:**
- Mesmo processo

---

## ⚙️ CONFIGURAÇÕES DE BUILD

### Personalizar Metadados

Editar `package.json`:

```json
{
  "name": "gta-analytics",
  "version": "1.0.0",              // ⬅️ Mudar versão aqui
  "description": "...",
  "author": "Seu Nome",            // ⬅️ Seu nome
  "build": {
    "appId": "com.seu-dominio.app", // ⬅️ Seu app ID
    "productName": "GTA Analytics"
  }
}
```

### Personalizar Instalador

Editar `package.json` → `build.nsis`:

```json
"nsis": {
  "oneClick": false,                        // Instalador customizável
  "allowToChangeInstallationDirectory": true,
  "createDesktopShortcut": true,           // Ícone desktop
  "createStartMenuShortcut": true,         // Menu Iniciar
  "shortcutName": "GTA Analytics"
}
```

### Ícones Customizados

**Formatos necessários:**
- `assets/icon.ico` (256x256, Windows)
- `assets/icon.png` (512x512, Tray icon)

**Converter PNG para ICO:**
- Online: https://convertico.com/
- Ou Photoshop / GIMP

---

## 🔐 CODE SIGNING (Opcional mas Recomendado)

### Por Quê?

- ✅ Remove aviso "Unknown Publisher"
- ✅ Usuários confiam mais
- ✅ Antivírus bloqueia menos

### Como Obter Certificado

**Opção 1: DigiCert ($100-300/ano)**
- https://www.digicert.com/code-signing/

**Opção 2: Sectigo (mais barato)**
- https://sectigo.com/ssl-certificates-tls/code-signing

**Opção 3: SignPath (GRÁTIS para open source)**
- https://about.signpath.io/product/open-source

### Assinar Executável

```bash
# Com certificado .pfx
signtool sign /f certificate.pfx /p senha /t http://timestamp.digicert.com /fd SHA256 dist/GTA-Analytics-1.0.0-Setup.exe

# Verificar assinatura
signtool verify /pa dist/GTA-Analytics-1.0.0-Setup.exe
```

### Integrar no Build

Editar `package.json`:

```json
"win": {
  "certificateFile": "certificate.pfx",
  "certificatePassword": "sua-senha",  // ⚠️ NÃO commitar isso!
  "signingHashAlgorithms": ["sha256"],
  "timestampUrl": "http://timestamp.digicert.com"
}
```

**Melhor:** Usar variáveis de ambiente

```bash
# Definir variáveis
set CSC_LINK=C:\path\to\certificate.pfx
set CSC_KEY_PASSWORD=sua-senha

# Build (pega certificado automaticamente)
npm run build
```

---

## 🐛 TROUBLESHOOTING

### Erro: "Python not found"

**Solução:**
```bash
# Adicionar Python ao PATH
# Windows: Pesquisar "Environment Variables"
# Adicionar: C:\Users\usuario\AppData\Local\Programs\Python\Python310
```

### Erro: "electron-builder not found"

**Solução:**
```bash
npm install --save-dev electron-builder
```

### Erro: PyInstaller "Failed to execute script"

**Solução:**
```bash
# Recompilar com verbose
pyinstaller --onefile --console --debug all capture.py

# Ver erros específicos
dist/capture.exe
```

### Build demora muito

**Normal!** Electron build pode demorar 3-5 minutos.

**Acelerar:**
- Usar SSD
- Fechar programas desnecessários
- Desabilitar antivírus temporariamente (apenas durante build)

### Antivírus deleta arquivo durante build

**Solução:**
- Adicionar exceção para pasta `electron-app/`
- Ou desabilitar temporariamente

---

## 📊 CHECKLIST FINAL

Antes de distribuir, verificar:

- [ ] ✅ App abre normalmente
- [ ] ✅ Interface carrega completa
- [ ] ✅ Configurações salvam
- [ ] ✅ Captura funciona (testar com GTA)
- [ ] ✅ Python embedded funciona
- [ ] ✅ Log mostra mensagens
- [ ] ✅ Links externos abrem
- [ ] ✅ Tray icon aparece
- [ ] ✅ Fechar/minimizar funciona
- [ ] ✅ Tamanho arquivo OK (~85-100 MB)
- [ ] ✅ Instalador cria atalhos
- [ ] ✅ Desinstalar funciona

### Testar em PC Limpo

**IMPORTANTE:** Testar em PC sem Node.js/Python instalado!

1. VM Windows limpa
2. Ou PC de amigo/colega
3. Instalar e verificar tudo funciona

---

## 🎯 QUICK REFERENCE

### Comandos Rápidos

```bash
# Development
npm start                  # Rodar em dev mode
npm run dev                # Rodar com DevTools

# Build
npm run build              # Build completo (instalador + portable)
npm run build:dir          # Build apenas diretório (mais rápido)
npm run pack               # Pack sem build (apenas compactar)

# Python
cd python
build.bat                  # Build Python (Windows)
```

### Estrutura de Arquivos Importante

```
electron-app/
├── main.js                  # ⚠️ Backend Electron
├── preload.js               # ⚠️ IPC Bridge
├── package.json             # ⚠️ Config build
├── renderer/
│   └── index.html           # ⚠️ Frontend
└── python/
    ├── capture.py           # ⚠️ Script captura
    └── dist/capture.exe     # ⚠️ Executável (gerado)
```

### Arquivos Gerados (NÃO commitar)

```
node_modules/          # Dependencies (npm install)
dist/                  # Build output (npm run build)
python/build/          # PyInstaller temp
python/dist/           # Python executable
```

---

## 🚀 PRÓXIMOS PASSOS

Após build bem-sucedido:

1. **Distribuir:** GitHub Releases ou Google Drive
2. **Documentar:** Enviar `COMO_USAR.md` para cliente
3. **Suporte:** Estar disponível para dúvidas
4. **Updates:** Quando fizer mudanças, aumentar versão e rebuild

---

**Sucesso no build! 🎉**
