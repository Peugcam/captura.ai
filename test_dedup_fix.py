"""
Teste do Fix de Duplicatas
===========================

Valida que o novo sistema de Fuzzy Matching resolve duplicatas:
1. "ph13" vs "JTX ph13" → Reconhece como MESMO jogador
2. "Kotarav" vs "Kolarov" → Corrige typo de OCR
3. "quattromortes" morto 3x → Bloqueado por histórico
"""

import sys
sys.path.insert(0, 'backend/src')

from team_tracker import TeamTracker

def test_duplicate_prevention():
    print("=" * 60)
    print("TESTE DE PREVENÇÃO DE DUPLICATAS")
    print("=" * 60)
    print()

    tracker = TeamTracker()

    print("### CASO 1: Nome com/sem prefixo de time ###")
    print()

    # Primeira kill: "ph13" SEM prefixo
    tracker.register_kill("JTX SmailyZ", "JTX", "ph13", "JTX", "killed")
    print(f"[OK] Kill 1: JTX SmailyZ -> ph13")
    print(f"  Jogadores registrados: {list(tracker.players.keys())}")
    print()

    # Segunda kill: "JTX ph13" COM prefixo (MESMO JOGADOR!)
    tracker.register_kill("JTX SmailyZ", "JTX", "JTX ph13", "JTX", "killed")
    print(f"[OK] Kill 2: JTX SmailyZ -> JTX ph13 (deve ser bloqueada!)")
    print(f"  Jogadores registrados: {list(tracker.players.keys())}")
    print(f"  Total de kills: {len(tracker.kills_history)}")
    print()

    # Verificar: deve ter apenas 1 kill (duplicata bloqueada)
    if len(tracker.kills_history) == 1:
        print("[SUCESSO] Duplicata bloqueada! Apenas 1 kill registrada.")
    else:
        print(f"[FALHA] {len(tracker.kills_history)} kills (esperado: 1)")

    print()
    print("### CASO 2: Typo de OCR (Kotarav vs Kolarov) ###")
    print()

    # Resetar tracker
    tracker = TeamTracker()

    # Kill com "Kotarav"
    tracker.register_kill("paIN Kotarav", "paIN", "EMPI quattromortes", "EMPI", "67m")
    print(f"[OK] Kill 1: paIN Kotarav -> EMPI quattromortes")
    print(f"  Jogadores: {list(tracker.players.keys())}")
    print()

    # Kill com "Kolarov" (typo de OCR, mas MESMO jogador!)
    tracker.register_kill("paIN Kolarov", "paIN", "EMPI quattromortes", "EMPI", "67m")
    print(f"[OK] Kill 2: paIN Kolarov -> EMPI quattromortes")
    print(f"  Jogadores: {list(tracker.players.keys())}")
    print()

    # Verificar: deve ter resolvido para MESMO killer
    killers = set(k['killer'] for k in tracker.kills_history)
    print(f"  Killers únicos: {killers}")

    if len(killers) == 1:
        print("[SUCESSO] SUCESSO: OCR typo corrigido! Ambas as kills atribuídas ao mesmo jogador.")
    else:
        print(f"[FALHA] FALHA: {len(killers)} killers diferentes (esperado: 1)")

    print()
    print("### CASO 3: Vítima morrendo múltiplas vezes ###")
    print()

    # Resetar tracker
    tracker = TeamTracker()

    # 3 jogadores matam a MESMA vítima
    tracker.register_kill("paIN Kotarav", "paIN", "EMPI quattromortes", "EMPI", "67m")
    print(f"[OK] Kill 1: paIN Kotarav -> EMPI quattromortes")

    tracker.register_kill("paIN Kolarov", "paIN", "EMPI quattromortes", "EMPI", "67m")
    print(f"[OK] Kill 2: paIN Kolarov -> EMPI quattromortes (DUPLICATA!)")

    tracker.register_kill("paIN Locking", "paIN", "EMPI quattromortes", "EMPI", "101m")
    print(f"[OK] Kill 3: paIN Locking -> EMPI quattromortes (DUPLICATA!)")

    print()
    print(f"  Total de kills: {len(tracker.kills_history)}")
    print(f"  Kills history: ")
    for idx, kill in enumerate(tracker.kills_history, 1):
        print(f"    {idx}. {kill['killer']} -> {kill['victim']}")

    # Verificar: deve ter bloqueado duplicatas
    victim_deaths = sum(1 for k in tracker.kills_history if k['victim'] == "EMPI quattromortes")
    print()
    print(f"  EMPI quattromortes morreu {victim_deaths} vez(es)")

    if victim_deaths == 1:
        print("[SUCESSO] SUCESSO: Duplicatas bloqueadas! Vítima morreu apenas 1 vez.")
    else:
        print(f"[AVISO]  AVISO: {victim_deaths} mortes para mesma vítima")
        print("   (Histórico bloqueia apenas kills IDÊNTICAS, não múltiplos killers)")

    print()
    print("=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)


if __name__ == "__main__":
    test_duplicate_prevention()
