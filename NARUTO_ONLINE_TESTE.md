# 🍥 Teste com Naruto Online

## 🎯 O que o sistema vai detectar:

✅ **Danos causados/recebidos**
✅ **Kills e derrotas**
✅ **Habilidades/Jutsus usados**
✅ **Combos e critical hits**
✅ **Nomes de jogadores**
✅ **Log de combate/chat**
✅ **Eventos de batalha**

## 🚀 Como testar (3 passos):

### 1. Preparar o jogo

```
Abra Naruto Online
│
├─ Modo JANELA (não tela cheia)
├─ Entre em uma batalha/combate
└─ Deixe o log de combate visível (se houver)
```

### 2. Executar o teste

```bash
# Certifique-se que o sistema está rodando
# (Go Gateway + Python Backend devem estar ativos)

# Execute o script de teste
py test-naruto.py
```

**O script vai:**
- ✅ Capturar tela por 30 segundos (2 FPS = 60 frames)
- ✅ Enviar para análise
- ✅ GPT-4o Vision vai detectar eventos
- ✅ Gerar Excel com estatísticas

### 3. Ver resultados

**Durante o teste:**
- Veja o terminal do backend mostrando detecções em tempo real

**Após o teste:**
```
backend/exports/
└── naruto_stats_YYYYMMDD_HHMMSS.xlsx
```

## 📊 O que esperar:

**Console do Backend (exemplo):**
```
📥 Fetched 10 frames from gateway
🔄 Processing batch of 5 frames...
🤖 Sending 5 frames to GPT-4o
✅ GPT-4o detected 3 combat events
   - PlayerX used Rasengan on PlayerY (1250 damage)
   - PlayerZ defeated PlayerW
   - PlayerX received 890 damage
📊 Stats: 15 processed | 3 events | 5 players
```

**Excel gerado:**
- Planilha com eventos de combate
- Dano total por jogador
- Kills/derrotas
- Timeline de eventos
- Habilidades mais usadas

## ⚙️ Ajustes (se necessário):

### Aumentar duração do teste:
Edite `test-naruto.py`:
```python
TEST_DURATION = 60  # 60 segundos ao invés de 30
```

### Capturar mais frames:
```python
CAPTURE_FPS = 3  # 3 FPS ao invés de 2
```

### Melhorar qualidade:
```python
QUALITY = 80  # 80% ao invés de 60%
```

## 🎮 Dicas para melhor detecção:

1. **Zoom adequado**: Não deixe UI muito pequeno
2. **Log visível**: Se Naruto tem chat/log de combate, deixe aberto
3. **Combate ativo**: Quanto mais ação, mais eventos detectados
4. **Resolução**: 1080p ou maior é ideal
5. **Modo janela**: Facilita captura

## 🐛 Troubleshooting:

**"Nenhum evento detectado"**
- Log de combate está visível?
- Teve combate durante os 30s?
- Tente aumentar CAPTURE_FPS para 3

**"Muitos frames, processamento lento"**
- Reduza TEST_DURATION para 20s
- Reduza CAPTURE_FPS para 1

**"Sistema não conecta"**
- Verifique se start-system.bat está rodando
- Teste: curl http://localhost:8000/health

## 📈 Após o teste:

O sistema vai gerar um relatório completo com:

**Estatísticas por jogador:**
- Total de dano causado
- Total de dano recebido
- Kills
- Deaths
- Habilidades usadas
- KDA (se aplicável)

**Timeline:**
- Todos os eventos em ordem cronológica
- Timestamp de cada ação
- Detalhes completos

**Gráficos** (se usar análise posterior):
- Dano por minuto
- Kills over time
- Player performance

---

## 🎯 Exemplo de uso:

```bash
# 1. Certifique sistema rodando
curl http://localhost:8000/health

# 2. Abra Naruto Online (modo janela)

# 3. Entre em batalha

# 4. Execute teste
py test-naruto.py

# 5. [Aguarde mensagem] Pressione ENTER quando pronto

# 6. Jogue por 30 segundos

# 7. Veja resultados no backend/exports/
```

---

**Criado por:** Paulo Eugenio Campos
**Sistema:** GTA Analytics V2 (adaptado para Naruto Online)
**Data:** 2026-02-06
