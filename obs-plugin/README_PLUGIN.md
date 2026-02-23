# 🎮 GTA Analytics - Plugin OBS

Plugin para captura automática do kill feed do GTA V e envio para análise em tempo real.

---

## 📦 O Que Está Incluído

```
obs-plugin/
├── gta_analytics_plugin.py    # Plugin principal
├── INSTALAR.bat               # Instalador automático
└── README_PLUGIN.md           # Este arquivo
```

---

## 🚀 Instalação Rápida (30 segundos)

### Método 1: Instalador Automático (Recomendado)

1. **Duplo-clique** em `INSTALAR.bat`
2. Pressione qualquer tecla
3. Pronto! Plugin instalado

### Método 2: Manual

1. Copie `gta_analytics_plugin.py`
2. Cole em: `%APPDATA%\obs-studio\scripts\`
3. Pronto!

---

## ⚙️ Configuração no OBS

### Passo 1: Adicionar o Script

1. Abra **OBS Studio**
2. Menu: **Ferramentas** → **Scripts**
3. Clique no botão **+** (Adicionar)
4. Navegue até: `%APPDATA%\obs-studio\scripts\`
5. Selecione: **gta_analytics_plugin.py**
6. Clique em **Abrir**

### Passo 2: Configurar

Na janela de Scripts, você verá as configurações:

```
┌─────────────────────────────────────────┐
│ GTA Analytics - Kill Feed Tracker      │
├─────────────────────────────────────────┤
│                                         │
│ URL do Gateway:                         │
│ http://localhost:8000                   │
│ (Alterar para Fly.io em produção)      │
│                                         │
│ FPS de Captura: 4                       │
│                                         │
│ Kill Feed - Posição X: 1400             │
│ Kill Feed - Posição Y: 0                │
│ Kill Feed - Largura: 520                │
│ Kill Feed - Altura: 400                 │
│                                         │
│ [Testar Conexão com Gateway]           │
│                                         │
│ Status: ✓ Conectado                     │
└─────────────────────────────────────────┘
```

### Passo 3: Testar

1. Clique em **Testar Conexão com Gateway**
2. Se aparecer **✓ Conexão OK!** → Funcionando!
3. Se der erro → Verificar se Gateway está rodando

---

## 🎯 Como Funciona

### Fluxo Automático

```
OBS captura tela
    ↓
Plugin detecta região do kill feed (canto superior direito)
    ↓
Captura apenas essa região (4 FPS)
    ↓
Envia para Gateway via HTTP
    ↓
Backend processa com Vision API
    ↓
Dashboard atualiza em tempo real
```

### O Que o Plugin Faz

- ✅ Roda **automaticamente** quando OBS inicia
- ✅ Captura apenas **região do kill feed** (otimizado)
- ✅ Envia **4 frames por segundo** (configurável)
- ✅ **Invisível** - não aparece na tela
- ✅ **Leve** - não impacta performance

### O Que o Plugin NÃO Faz

- ❌ Não grava vídeo
- ❌ Não muda configurações do OBS
- ❌ Não aparece na transmissão/gravação
- ❌ Não acessa arquivos do PC

---

## 📊 Configurações Avançadas

### Ajustar Região do Kill Feed

Se o kill feed do GTA está em outra posição:

1. No OBS, vá em **Ferramentas** → **Scripts**
2. Selecione **gta_analytics_plugin.py**
3. Ajuste:
   - **Posição X**: Posição horizontal (0 = esquerda, 1920 = direita)
   - **Posição Y**: Posição vertical (0 = topo, 1080 = baixo)
   - **Largura**: Largura da região a capturar
   - **Altura**: Altura da região a capturar

**Valores padrão (GTA em 1080p):**
```
X: 1400 (canto direito)
Y: 0 (topo)
Largura: 520 pixels
Altura: 400 pixels
```

### Ajustar FPS

- **4 FPS**: Recomendado (equilibra qualidade e performance)
- **2 FPS**: Mais leve (se PC estiver travando)
- **8 FPS**: Mais preciso (se PC for potente)

### Conectar ao Fly.io (Produção)

Quando estiver pronto para usar em produção:

1. Altere **URL do Gateway** para:
   ```
   https://gta-analytics-gateway.fly.dev
   ```

2. Clique em **Testar Conexão**

3. Se conectar → Pronto para uso!

---

## 🐛 Troubleshooting

### Erro: "Conexão recusada"

**Causa:** Gateway não está rodando

**Solução:**
```bash
# Local
docker-compose up gateway

# Ou use Fly.io
https://gta-analytics-gateway.fly.dev/health
```

### Plugin não aparece no OBS

**Causa:** Arquivo não está na pasta correta

**Solução:**
1. Copie `gta_analytics_plugin.py`
2. Cole em: `%APPDATA%\obs-studio\scripts\`
3. Reinicie o OBS

### "Erro ao capturar frame"

**Causa:** OBS não está capturando nenhuma fonte

**Solução:**
1. Adicione uma fonte no OBS (Game Capture ou Display Capture)
2. Verifique se a fonte está visível no preview

### Tela preta no backend

**Causa:** Região do kill feed configurada errado

**Solução:**
1. Ajuste as coordenadas X, Y, Largura, Altura
2. Teste diferentes valores
3. Use Display Capture ao invés de Game Capture

---

## 📝 Logs e Debug

### Ver Logs do Plugin

1. No OBS: **Ferramentas** → **Scripts**
2. Seção inferior: **Log de Scripts**
3. Mensagens do plugin aparecerão aqui

### Mensagens Comuns

```
[GTA Analytics] Plugin carregado
→ Plugin iniciou com sucesso

[GTA Analytics] Frame 10 enviado
→ Captura funcionando normalmente

[GTA Analytics] ✓ Conexão OK!
→ Gateway está respondendo

[GTA Analytics] ✗ Erro de conexão
→ Gateway offline ou URL incorreta
```

---

## 🔧 Desinstalação

Se quiser remover o plugin:

1. No OBS: **Ferramentas** → **Scripts**
2. Selecione **gta_analytics_plugin.py**
3. Clique no botão **-** (Remover)
4. Pronto!

Ou delete manualmente:
```
%APPDATA%\obs-studio\scripts\gta_analytics_plugin.py
```

---

## 💰 Custos

**Custo total: R$ 0 (GRÁTIS)**

- ✅ Plugin: Grátis
- ✅ OBS Studio: Grátis
- ✅ Backend Fly.io: $8/mês (já está pagando)

**Nenhum custo adicional!**

---

## 📞 Suporte

**Problemas?** Verifique:

1. ✅ OBS Studio está aberto
2. ✅ Gateway está rodando
3. ✅ Plugin está na pasta correta
4. ✅ URL do Gateway está correta
5. ✅ Botão "Testar Conexão" funciona

Se nada resolver, envie os logs do OBS.

---

## 🎉 Pronto!

O plugin está rodando! Agora:

1. ✅ Jogue GTA normalmente
2. ✅ Kill feed é capturado automaticamente
3. ✅ Acesse o dashboard para ver estatísticas
4. ✅ Tudo funciona em segundo plano

**Boa partida! 🚀**
