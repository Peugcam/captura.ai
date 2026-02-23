# 📊 DASHBOARDS DISPONÍVEIS - GTA ANALYTICS

## 🌐 URLs dos Dashboards

### 1️⃣ Dashboard do Jogador (Minimalista)
```
https://gta-analytics-backend.fly.dev/player
```
**Para:** Jogador acompanhar suas próprias estatísticas
**Mostra:** Stats básicas, kills, deaths

---

### 2️⃣ Dashboard do Espectador/Estrategista
```
https://gta-analytics-backend.fly.dev/viewer
```
**Para:** Vitor e equipe acompanharem em tempo real
**Mostra:** Dashboard completo com edição e gerenciamento

---

### 3️⃣ Dashboard de Torneio (RECOMENDADO PARA LUIS)
```
https://gta-analytics-backend.fly.dev/tournament
```
**Para:** Torneios e campeonatos
**Mostra:**
- Times vivos / eliminados
- Contagem de jogadores por time
- Rankings em tempo real
- Permite editar rosters
- Gerenciar times

---

## 📱 COMO ACESSAR NO CELULAR (Para Luis)

### Passo a passo:

1. **No celular, abra o navegador**
   - Chrome, Safari, Firefox, qualquer um

2. **Digite a URL:**
   ```
   https://gta-analytics-backend.fly.dev/tournament
   ```

3. **Adicione à tela inicial (opcional):**

   **No iPhone:**
   - Safari → Compartilhar → "Adicionar à Tela Inicial"

   **No Android:**
   - Chrome → Menu (3 pontos) → "Adicionar à tela inicial"

4. **Deixe aberto durante o torneio:**
   - Atualiza automaticamente via WebSocket
   - Não precisa ficar dando refresh

---

## 💻 TESTANDO AGORA (No PC)

### Abra no navegador:

**Dashboard de Torneio:**
```
https://gta-analytics-backend.fly.dev/tournament
```

Ou cole este HTML para testar localmente:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GTA Analytics - Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #1a1a2e;
            color: #eee;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: #16213e;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-value {
            font-size: 3em;
            font-weight: bold;
            color: #00d9ff;
        }
        .stat-label {
            font-size: 1em;
            color: #888;
            margin-top: 10px;
        }
        .status {
            padding: 10px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .status.online {
            background: #00aa00;
        }
        .status.offline {
            background: #aa0000;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 GTA Analytics - Dashboard ao Vivo</h1>

        <div id="status" class="status">
            Conectando...
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="frames">-</div>
                <div class="stat-label">Frames Recebidos</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="processed">-</div>
                <div class="stat-label">Frames Processados</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="kills">-</div>
                <div class="stat-label">Kills Detectadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="teams">-</div>
                <div class="stat-label">Times Ativos</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="alive">-</div>
                <div class="stat-label">Jogadores Vivos</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="efficiency">-</div>
                <div class="stat-label">Eficiência do Filtro</div>
            </div>
        </div>

        <div style="margin-top: 40px; padding: 20px; background: #16213e; border-radius: 10px;">
            <h3>📡 Status da Conexão WebSocket</h3>
            <p id="ws-status">Desconectado</p>
            <button onclick="connectWebSocket()" style="padding: 10px 20px; margin-top: 10px;">Reconectar</button>
        </div>
    </div>

    <script>
        let ws = null;

        function updateStats() {
            fetch('https://gta-analytics-backend.fly.dev/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('frames').textContent = data.frames_received;
                    document.getElementById('processed').textContent = data.frames_processed;
                    document.getElementById('kills').textContent = data.kills_detected;
                    document.getElementById('teams').textContent = data.teams;
                    document.getElementById('alive').textContent = data.alive;
                    document.getElementById('efficiency').textContent = data.filter_efficiency;

                    document.getElementById('status').className = 'status online';
                    document.getElementById('status').textContent = '✅ Sistema Online - Atualizando a cada 2 segundos';
                })
                .catch(err => {
                    document.getElementById('status').className = 'status offline';
                    document.getElementById('status').textContent = '❌ Erro de conexão';
                });
        }

        function connectWebSocket() {
            ws = new WebSocket('wss://gta-analytics-backend.fly.dev/ws/dashboard');

            ws.onopen = () => {
                document.getElementById('ws-status').textContent = '✅ WebSocket Conectado - Atualizações em tempo real';
                console.log('WebSocket conectado');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log('Atualização recebida:', data);

                if (data.type === 'stats_update') {
                    // Atualiza stats em tempo real
                    updateStats();
                }
            };

            ws.onerror = (error) => {
                console.error('Erro WebSocket:', error);
                document.getElementById('ws-status').textContent = '❌ Erro na conexão WebSocket';
            };

            ws.onclose = () => {
                document.getElementById('ws-status').textContent = '⚠️ WebSocket Desconectado - Tentando reconectar em 5s...';
                setTimeout(connectWebSocket, 5000);
            };
        }

        // Atualiza via polling a cada 2 segundos
        setInterval(updateStats, 2000);

        // Primeira atualização imediata
        updateStats();

        // Tenta conectar WebSocket
        connectWebSocket();
    </script>
</body>
</html>
```

---

## 🧪 TESTE RÁPIDO

### 1. Verifique se o dashboard existe:

```bash
curl -I https://gta-analytics-backend.fly.dev/tournament
```

Se retornar `200 OK` → Dashboard disponível ✅

### 2. Veja os dados JSON diretamente:

```bash
curl https://gta-analytics-backend.fly.dev/stats
```

Retorna:
```json
{
  "frames_received": 242,
  "frames_processed": 94,
  "kills_detected": 2,
  "teams": 4,
  "players": 4,
  "alive": 2,
  "dead": 2
}
```

---

## 🎯 PARA O LUIS

**URL para enviar ao Luis:**
```
https://gta-analytics-backend.fly.dev/tournament
```

**Instruções:**
1. Abra no celular durante o torneio
2. Deixe a tela ligada
3. Dashboard atualiza sozinho
4. Mostra em tempo real:
   - Times vivos
   - Jogadores vivos por time
   - Kill counts
   - Rankings

---

**Quer testar o dashboard agora?** Abra a URL no seu navegador! 🚀
