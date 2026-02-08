# 🎮 Como Testar o Sistema com Naruto Online

## ✅ Configuração Atual

O sistema já está configurado para **Naruto Online**:
- ✅ `GAME_TYPE=naruto`
- ✅ `USE_ROI=false` (analisa tela inteira para detectar combos)
- ✅ `OCR_WORKERS=8` (processamento rápido)
- ✅ Prompt otimizado para detectar: HP bars, damage numbers, jutsu attacks, combos

---

## 🚀 Passos para Testar

### 1️⃣ Iniciar o Sistema Completo

Clique duas vezes em: **`INICIAR-NARUTO.bat`**

Isso abrirá **2 janelas**:
- **Terminal 1**: Go Gateway (porta 8000)
- **Terminal 2**: Python Backend (processador)

Aguarde até ver mensagens como:
```
Gateway rodando na porta 8000...
Backend processando frames...
```

---

### 2️⃣ Abrir o Dashboard

✅ **Já está aberto!** Se fechou, clique em: **`dashboard.html`**

O dashboard mostra:
- Kills em tempo real
- Combos detectados
- Estatísticas de jogadores
- Gráficos de performance

---

### 3️⃣ Abrir o Naruto Online

1. Abra seu navegador
2. Entre no **Naruto Online**
3. Posicione a janela do jogo para ficar **visível**

---

### 4️⃣ Iniciar a Captura

Clique duas vezes em: **`CAPTURAR-NARUTO.bat`**

**Controles:**
- **F9** = Iniciar captura
- **F10** = Parar captura
- **ESC** = Sair do programa

---

### 5️⃣ Testar Combos

1. Entre em uma batalha no Naruto Online
2. Pressione **F9** para começar a capturar
3. Execute combos e ataques
4. Observe o **dashboard** para ver as detecções em tempo real

---

## 🎯 O Que o Sistema Detecta

Para **Naruto Online**, o GPT-4o Vision analisa:

✅ **Combate:**
- Nomes dos personagens atacando/defendendo
- Dano causado (números exibidos)
- Barras de HP (vida)
- Efeitos de jutsu/habilidades
- Battle log (registro de combate)

✅ **Combos:**
- Sequências de ataques
- Chain attacks
- Critical hits
- Buffs/debuffs aplicados

---

## 📊 Verificando Resultados

### No Dashboard:
- Você verá eventos de combate aparecendo em tempo real
- Gráficos de dano por personagem
- Timeline de eventos

### Nos Terminais:
- **Terminal Go**: Mostra frames capturados
- **Terminal Python**: Mostra análises do GPT-4o Vision

### Arquivos Exportados:
- Verifique a pasta: `backend/exports/`
- Arquivos JSON com todos os eventos detectados

---

## 🔧 Troubleshooting

### Gateway não inicia?
- Verifique se a porta 8000 está livre
- Confirme que Go está instalado: `go version`

### Backend não processa?
- Verifique a chave API no `.env`
- Confirme Python instalado: `py --version`

### Captura não funciona?
- Certifique-se que a janela do jogo está **visível**
- Pressione F9 com a janela do captura em foco
- Verifique se o Gateway está rodando (Terminal 1)

---

## 📈 Métricas Esperadas

Com as otimizações de Fase 1:
- ⚡ **2-4 segundos** por batch (vs 5-15s antes)
- 🎯 **95-98% precisão** na detecção de nomes
- ✅ **Menos falsos positivos** (temperatura=0)

---

## 💡 Próximos Passos

Após testar:
1. ✅ Validar precisão das detecções
2. ✅ Verificar velocidade de processamento
3. 🚀 Implementar Fase 2 (otimizações avançadas)

---

**Divirta-se testando! 🎮**
