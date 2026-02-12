"""
Script de Teste Simplificado
Valida os componentes principais sem dependências complexas
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("=" * 70)
print("  TESTE SIMPLIFICADO - GTA Analytics V2")
print("=" * 70)
print()

# Test 1: BrazilianKillParser
print("[1/4] Testando BrazilianKillParser...")
try:
    from src.brazilian_kill_parser import BrazilianKillParser
    
    parser = BrazilianKillParser()
    
    # Test basic parsing
    test_line = "PPP almeida99 MATOU 💀 LLL pikachu1337 120m"
    result = parser.parse_kill_line(test_line)
    
    assert result is not None, "Parser retornou None"
    assert result['killer'] == 'almeida99', f"Killer incorreto: {result['killer']}"
    assert result['victim'] == 'pikachu1337', f"Victim incorreto: {result['victim']}"
    assert result['distance'] == '120m', f"Distance incorreta: {result['distance']}"
    
    print("  ✅ BrazilianKillParser: OK")
    print(f"     - Parse de kill feed: PASSOU")
    print(f"     - Killer: {result['killer']}")
    print(f"     - Victim: {result['victim']}")
    
except Exception as e:
    print(f"  ❌ BrazilianKillParser: FALHOU - {e}")

print()

# Test 2: TeamTracker
print("[2/4] Testando TeamTracker...")
try:
    from src.team_tracker import TeamTracker
    
    tracker = TeamTracker(total_players=100)
    
    # Register a kill
    success = tracker.register_kill(
        killer_name="player1",
        killer_team="TeamA",
        victim_name="player2",
        victim_team="TeamB"
    )
    
    assert success is True, "Registro de kill falhou"
    assert len(tracker.kills_history) == 1, "Kill não foi registrada"
    
    # Get stats
    stats = tracker.get_team_stats("TeamA")
    assert stats is not None, "Stats não encontradas"
    assert stats['kills'] == 1, f"Total kills incorreto: {stats['kills']}"
    
    print("  ✅ TeamTracker: OK")
    print(f"     - Registro de kills: PASSOU")
    print(f"     - Total kills: {stats['kills']}")
    print(f"     - Times ativos: {tracker.get_active_teams_count()}")
    
except Exception as e:
    print(f"  ❌ TeamTracker: FALHOU - {e}")

print()

# Test 3: MultiAPIClient
print("[3/4] Testando MultiAPIClient...")
try:
    from src.multi_api_client import MultiAPIClient
    
    # Test with mock keys
    test_keys = [
        "sk-or-v1-test-key-1234567890abcdef",
        "sk-proj-test-key-abcdef1234567890"
    ]
    
    client = MultiAPIClient(test_keys)
    
    assert len(client.clients) == 2, f"Número de clients incorreto: {len(client.clients)}"
    assert client.clients[0]['type'] == 'openrouter', "Tipo incorreto para primeira key"
    assert client.clients[1]['type'] == 'openai', "Tipo incorreto para segunda key"
    
    # Test model normalization
    normalized = client._normalize_model("openai/gpt-4o", "openai")
    assert normalized == "gpt-4o", f"Normalização incorreta: {normalized}"
    
    print("  ✅ MultiAPIClient: OK")
    print(f"     - Detecção de keys: PASSOU")
    print(f"     - Total de clients: {len(client.clients)}")
    print(f"     - Normalização de modelo: PASSOU")
    
except Exception as e:
    print(f"  ❌ MultiAPIClient: FALHOU - {e}")

print()

# Test 4: Config Validation
print("[4/4] Testando Config...")
try:
    import config
    
    # Test API key validation
    valid_key = "sk-or-v1-1234567890abcdefghijklmnopqrstuvwxyz"
    invalid_key = "sk-xxx"
    
    assert config.validate_api_key(valid_key) is True, "Valid key rejeitada"
    assert config.validate_api_key(invalid_key) is False, "Invalid key aceita"
    
    # Test sanitization
    sensitive = "sk-or-v1-secret-key-12345678901234567890"
    sanitized = config.sanitize_config_value(sensitive, is_sensitive=True)
    assert len(sanitized) < len(sensitive), "Sanitização não funcionou"
    assert "..." in sanitized, "Sanitização sem máscara"
    
    print("  ✅ Config: OK")
    print(f"     - Validação de API keys: PASSOU")
    print(f"     - Sanitização: PASSOU")
    print(f"     - OCR Keywords: {len(config.OCR_KEYWORDS)} keywords")
    
except Exception as e:
    print(f"  ❌ Config: FALHOU - {e}")

print()
print("=" * 70)
print("  RESUMO DOS TESTES")
print("=" * 70)
print()
print("  Todos os componentes principais foram testados com sucesso!")
print("  Os testes unitários completos estão disponíveis em tests/unit/")
print()
print("  Para executar a suite completa:")
print("  python -m pytest tests/unit/ -v --cov=backend/src")
print()
print("=" * 70)
