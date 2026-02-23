# 📦 GTA ANALYTICS - PACOTE PARA LUIS

## ✅ O QUE ESTÁ INCLUÍDO:

```
pacote-luis/
├── gta-analytics-v2.py           ← Programa principal
├── config.json                    ← Configurações
├── INSTALAR_TUDO.bat             ← Instalador (se precisar)
├── TESTAR.bat                     ← Script de teste
└── Documentação completa
```

---

## 🎯 DASHBOARD DO TORNEIO:

**URL para Luis acessar no celular:**
```
https://gta-analytics-v2.fly.dev/strategist
```

**O que mostra:**
- 🏆 Times vivos vs eliminados
- 👥 Número de jogadores vivos por time
- 💀 Kill counts individuais e por time
- 📊 Rankings em tempo real
- ⚙️ Gerenciamento de roster (upload Excel/CSV)

---

## 📱 COMO USAR (LUIS):

### ANTES DO TORNEIO (Configuração - 1x):

1. **Instalar Python:**
   - Baixe: https://python.org/downloads
   - ☑️ IMPORTANTE: Marque "Add Python to PATH"
   - Instale normalmente

2. **Instalar biblioteca OBS:**
   - Abra CMD/PowerShell
   - Execute: `pip install obsws-python`

3. **Configurar OBS WebSocket:**
   - Abra OBS Studio
   - Menu: Ferramentas → Configurações do Servidor WebSocket
   - ☑️ Marque: "Ativar Servidor WebSocket"
   - Porta: `4455`
   - Anote a senha (ou use: `ZNx3v4LjLVCgbTrO`)
   - Clique "Aplicar"

---

### DURANTE O TORNEIO:

#### **NO PC:**

1. **Abra o OBS Studio**
   - Configure captura do GTA V
   - Use: "Captura de Jogo" ou "Captura de Janela"
   - NÃO use "Captura de Monitor" (captura tela inteira)

2. **Execute o Capturador:**
   - Duplo-clique em: `gta-analytics-v2.py`
   - Deve aparecer: "CAPTURA ATIVA"
   - Deixe rodando em segundo plano

3. **Jogue normalmente!**
   - O programa captura automaticamente
   - Não interfere no jogo
   - Leve impacto de performance

#### **NO CELULAR:**

1. **Abra o Dashboard:**
   - Navegador (Chrome/Safari)
   - URL: `https://gta-analytics-v2.fly.dev/strategist`
   - Adicione à tela inicial (opcional)

2. **Acompanhe em Tempo Real:**
   - Dashboard atualiza sozinho
   - Mostra times vivos
   - Mostra jogadores vivos por time
   - Mostra kill counts

3. **Durante o Torneio:**
   - Deixe o celular ligado
   - Dashboard atualiza automaticamente
   - Use para anunciar eliminações, rankings, etc.

---

## 🎮 TIPOS DE TORNEIO:

### **Etapa 1 (Teams Variáveis):**
- Sistema detecta tags automaticamente
- Ex: [TAG] PlayerName
- Rastreia teams dinamicamente

### **Etapa 2 (~100 times):**
- Upload lista de times (Excel/CSV)
- Dashboard mostra todos os times
- Rastreamento automático

### **Championship (20 times):**
- Upload roster completo
- Lista de jogadores por time
- Tracking preciso de eliminações

---

## ⚙️ CONFIGURAÇÕES (config.json):

```json
{
  "gateway_url": "https://gta-analytics-v2.fly.dev",
  "fps": 4,
  "kill_feed_region": {
    "x": 1400,
    "y": 0,
    "width": 520,
    "height": 400
  }
}
```

**Ajustes possíveis:**

- **fps:** Frames por segundo (1-10)
  - 4 = Recomendado
  - Maior = Mais preciso, mais processamento
  - Menor = Menos processamento

- **kill_feed_region:** Posição do kill feed na tela
  - x: Distância da esquerda (1400 para 1920x1080)
  - y: Distância do topo (0 = canto superior)
  - width: Largura da região (520)
  - height: Altura da região (400)

---

## 💰 CUSTOS:

**Para Luis:**
```
GRÁTIS - R$ 0
```

**Para Você (desenvolvedor):**
```
Fly.io: ~$8/mês (já está pagando)
Sem custo adicional
```

---

## 📊 ESTATÍSTICAS:

O sistema captura:
- ✅ Kills (quem matou quem)
- ✅ Armas usadas
- ✅ Times ativos
- ✅ Players vivos por time
- ✅ Ordem de eliminação

---

## 🆘 SUPORTE:

**Problemas comuns:**

### "Programa não inicia"
- Instale Python 3.x
- Execute: `pip install obsws-python requests pillow`

### "OBS WebSocket não conecta"
- Verifique se OBS está aberto
- Verifique se WebSocket está ativado
- Porta: 4455

### "Dashboard não atualiza"
- Verifique conexão com internet
- Tente atualizar página (F5)
- Dashboard atualiza a cada 2 segundos

### "Kills não são detectadas"
- Verifique se kill feed está visível no OBS
- Ajuste coordenadas no config.json
- Kill feed deve estar no canto superior direito

---

## ✅ CHECKLIST RÁPIDO:

**Antes do torneio:**
- [ ] Python instalado
- [ ] OBS WebSocket configurado
- [ ] Biblioteca obsws-python instalada
- [ ] Teste feito (TESTAR.bat)

**Durante o torneio:**
- [ ] OBS aberto e capturando GTA
- [ ] gta-analytics-v2.py rodando
- [ ] Dashboard aberto no celular
- [ ] Sistema capturando frames (ver contador)

---

## 🎯 URL DO DASHBOARD:

```
https://gta-analytics-v2.fly.dev/strategist
```

**Salve nos favoritos!** ⭐

---

**Dúvidas?** Entre em contato com Paulo

**Bom torneio! 🏆**
