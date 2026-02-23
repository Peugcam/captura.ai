#!/bin/bash
# Monitor stats em loop

echo "======================================================================"
echo "MONITOR FLY.DEV - Atualizando a cada 2 segundos"
echo "======================================================================"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""

while true; do
    clear
    echo "======================================================================"
    echo "GTA ANALYTICS V2 - ESTATISTICAS AO VIVO"
    echo "======================================================================"
    echo ""
    echo "[$(date '+%H:%M:%S')] Consultando servidor..."
    echo ""

    curl -s https://gta-analytics-v2.fly.dev/stats | grep -o '"frames_received":[^,]*' | sed 's/"frames_received":/Frames Recebidos: /' || echo "Erro ao conectar"
    curl -s https://gta-analytics-v2.fly.dev/stats | grep -o '"frames_processed":[^,]*' | sed 's/"frames_processed":/Frames Processados: /' || echo ""
    curl -s https://gta-analytics-v2.fly.dev/stats | grep -o '"kills_detected":[^,]*' | sed 's/"kills_detected":/Kills Detectadas: /' || echo ""
    curl -s https://gta-analytics-v2.fly.dev/stats | grep -o '"teams":[^,]*' | sed 's/"teams":/Times: /' || echo ""
    curl -s https://gta-analytics-v2.fly.dev/stats | grep -o '"players":[^,]*' | sed 's/"players":/Jogadores: /' || echo ""

    echo ""
    echo "======================================================================"
    echo "Proxima atualizacao em 2 segundos..."
    echo ""

    sleep 2
done
