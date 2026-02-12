import openpyxl
import sys
from collections import defaultdict

file_path = sys.argv[1] if len(sys.argv) > 1 else "backend/exports/gta_match_20260211_140025_luis.xlsx"

wb = openpyxl.load_workbook(file_path)
ws = wb["KILL FEED"]

print(f"=== VERIFICANDO DUPLICATAS EM: {file_path} ===\n")

kills = []
for i, row in enumerate(ws.iter_rows(values_only=True, min_row=2), 2):  # Pular header
    if row[0] is None:  # Linha vazia
        break

    num, hora, matou, team_matou, skull, morreu, team_morreu, tipo, arma = row

    kills.append({
        'linha': i,
        'num': num,
        'hora': hora,
        'matou': matou,
        'team_matou': team_matou,
        'morreu': morreu,
        'team_morreu': team_morreu,
        'tipo': tipo,
        'arma': arma
    })

print(f"Total de kills: {len(kills)}\n")

# Verificar duplicatas exatas (mesmo killer + victim)
duplicates = defaultdict(list)
for kill in kills:
    key = f"{kill['matou']} -> {kill['morreu']}"
    duplicates[key].append(kill)

print("=== KILLS DUPLICADAS (MESMO KILLER + VICTIM) ===")
found_duplicates = False
for key, instances in duplicates.items():
    if len(instances) > 1:
        found_duplicates = True
        print(f"\nDUPLICATA DETECTADA: {key}")
        for inst in instances:
            print(f"   Linha {inst['linha']}: {inst['hora']} | {inst['matou']} ({inst['team_matou']}) -> {inst['morreu']} ({inst['team_morreu']}) | [{inst['tipo']}] ({inst['arma']})")

if not found_duplicates:
    print("OK - Nenhuma duplicata exata encontrada!\n")

# Verificar kills similares (mesmo killer/victim em intervalo de tempo curto)
print("\n=== KILLS SIMILARES (MESMO JOGADOR EM <30s) ===")
from datetime import datetime

for i in range(len(kills)):
    for j in range(i+1, len(kills)):
        k1 = kills[i]
        k2 = kills[j]

        # Mesmo killer ou mesmo victim
        if k1['matou'] == k2['matou'] or k1['morreu'] == k2['morreu']:
            # Calcular diferença de tempo
            try:
                t1 = datetime.fromisoformat(k1['hora'])
                t2 = datetime.fromisoformat(k2['hora'])
                diff = abs((t2 - t1).total_seconds())

                if diff < 30:  # Menos de 30 segundos
                    print(f"\nSUSPEITA ({diff:.1f}s):")
                    print(f"   Linha {k1['linha']}: {k1['matou']} -> {k1['morreu']} | {k1['hora']}")
                    print(f"   Linha {k2['linha']}: {k2['matou']} -> {k2['morreu']} | {k2['hora']}")
            except:
                pass

print("\n=== TODAS AS KILLS (ORDENADAS POR TEMPO) ===")
for kill in kills:
    print(f"{kill['num']}. [{kill['hora']}] {kill['matou']} ({kill['team_matou']}) -> {kill['morreu']} ({kill['team_morreu']}) | {kill['tipo']} | {kill['arma']}")
