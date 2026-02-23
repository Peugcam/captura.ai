# COMO TESTAR COM NARUTO ONLINE

## PASSO 1: Executar o Programa

Abra o terminal na pasta e execute:

```bash
py naruto-analytics.py
```

Você verá:
```
✅ Conectado ao OBS
✅ Cena atual: narutoonline
🎬 CAPTURA ATIVA - MODO DEBUG
```

---

## PASSO 2: Abrir o Dashboard

Duplo-clique no arquivo:
```
naruto-dashboard.html
```

O dashboard abrirá no navegador e mostrará:
- 📊 Frames Capturados
- ⚡ Combos Detectados
- 🔮 Exotéricas Detectadas
- ⏱️ Tempo Ativo
- 📜 Log de Ações
- 🎬 Último Frame Capturado

---

## PASSO 3: Jogar Naruto Online

- Entre em uma batalha
- O sistema vai:
  1. Capturar frames a cada 0.5 segundos
  2. Salvar em `naruto_frames/`
  3. Atualizar o dashboard em tempo real
  4. Mostrar o último frame capturado

---

## O QUE VOCÊ VAI VER:

### No Terminal:
```
[1 frames] 3s | 0.3 FPS | Salvo: naruto_frames/frame_0001.jpg
[5 frames] 18s | 0.3 FPS | Salvo: naruto_frames/frame_0005.jpg
[10 frames] 37s | 0.3 FPS | Salvo: naruto_frames/frame_0010.jpg
```

### No Dashboard:
- Contador de frames aumentando
- Último frame sendo exibido
- Log mostrando cada captura
- Status: 🟢 Conectado

---

## PROXIMOS PASSOS:

1. Deixe capturar alguns frames
2. Abra a pasta `naruto_frames` e veja as capturas
3. Me mostre:
   - Onde aparecem os combos no jogo
   - Onde aparecem as exotéricas
4. Vou ajustar a região de captura
5. Vou adicionar detecção com IA

---

## AJUSTAR REGIAO DE CAPTURA:

Se quiser capturar outra parte da tela, edite `naruto-analytics.py` linha 28:

```python
COMBAT_REGION = {
    "x": 0,        # Posição X (0 = esquerda)
    "y": 300,      # Posição Y (0 = topo)
    "width": 400,  # Largura
    "height": 400  # Altura
}
```

**Exemplos:**
- Canto superior direito: `x=1520, y=0`
- Centro da tela: `x=760, y=340`
- Parte inferior: `x=0, y=680`

---

## CONTROLES DO DASHBOARD:

- 🗑️ **Limpar Log** - Remove todas as entradas do log
- 🔄 **Resetar Estatísticas** - Zera os contadores

---

✅ **Sistema pronto para testar!**
