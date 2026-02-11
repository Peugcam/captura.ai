"""
Team Tracker - Sistema de Tracking de Times em Tempo Real
=========================================================

Mantém estado de cada time durante a partida:
- Jogadores vivos/mortos por equipe
- Estatísticas em tempo real
- Histórico de kills

Requisito do Luis:
"Quero saber quantos vivos tem em cada equipe em tempo real"

Author: Paulo Eugenio Campos
Cliente: Luis Otavio
"""

from typing import Dict, List, Set, Optional
from datetime import datetime
from dataclasses import dataclass, field
import logging
import difflib

logger = logging.getLogger(__name__)


@dataclass
class Player:
    """Representa um jogador"""
    name: str
    team: str
    alive: bool = True
    kills: int = 0
    deaths: int = 0
    last_seen: datetime = field(default_factory=datetime.now)
    first_seen: datetime = field(default_factory=datetime.now)


@dataclass
class Team:
    """Representa um time"""
    name: str
    players: Dict[str, Player] = field(default_factory=dict)
    total_kills: int = 0
    total_deaths: int = 0

    @property
    def alive_count(self) -> int:
        """Jogadores vivos no time"""
        return sum(1 for p in self.players.values() if p.alive)

    @property
    def dead_count(self) -> int:
        """Jogadores mortos no time"""
        return sum(1 for p in self.players.values() if not p.alive)

    @property
    def total_players(self) -> int:
        """Total de jogadores no time"""
        return len(self.players)

    def get_alive_players(self) -> List[Player]:
        """Lista de jogadores vivos"""
        return [p for p in self.players.values() if p.alive]

    def get_dead_players(self) -> List[Player]:
        """Lista de jogadores mortos"""
        return [p for p in self.players.values() if not p.alive]


class TeamTracker:
    """
    Sistema de tracking de times em tempo real

    Mantém estado atualizado de todos os times e jogadores
    """

    def __init__(self, total_players: int = 100):
        """
        Inicializa tracker

        Args:
            total_players: Total de jogadores na partida
        """
        self.teams: Dict[str, Team] = {}
        self.players: Dict[str, Player] = {}
        self.total_players = total_players
        self.kills_history: List[Dict] = []
        self.match_start_time = datetime.now()

    def register_kill(self, killer_name: str, killer_team: str,
                     victim_name: str, victim_team: str,
                     distance: Optional[str] = None) -> bool:
        """
        Registra uma kill e atualiza estado dos times

        Args:
            killer_name: Nome do killer
            killer_team: Time do killer
            victim_name: Nome da vítima
            victim_team: Time da vítima
            distance: Distância (opcional)

        Returns:
            True se registrou com sucesso
        """
        try:
            # FUZZY MATCHING MELHORADO (com detecção de prefixo de time)
            # Find existing players with similar names to avoid OCR duplicates
            # IMPORTANTE: Passar team para detectar "ph13" vs "JTX ph13" como mesmo jogador
            real_killer_name = self._find_player_fuzzy(killer_name, team=killer_team) or killer_name
            real_victim_name = self._find_player_fuzzy(victim_name, team=victim_team) or victim_name

            # Use resolved names
            killer_name = real_killer_name
            victim_name = real_victim_name

            # Criar/atualizar killer
            if killer_name not in self.players:
                self.players[killer_name] = Player(
                    name=killer_name,
                    team=killer_team
                )

            # Criar/atualizar victim
            if victim_name not in self.players:
                self.players[victim_name] = Player(
                    name=victim_name,
                    team=victim_team
                )

            # Criar teams se não existirem
            if killer_team not in self.teams:
                self.teams[killer_team] = Team(name=killer_team)

            if victim_team not in self.teams:
                self.teams[victim_team] = Team(name=victim_team)

            # Adicionar jogadores aos times
            if killer_name not in self.teams[killer_team].players:
                self.teams[killer_team].players[killer_name] = self.players[killer_name]

            if victim_name not in self.teams[victim_team].players:
                self.teams[victim_team].players[victim_name] = self.players[victim_name]

            # Atualizar estatísticas
            self.players[killer_name].kills += 1
            self.players[killer_name].last_seen = datetime.now()

            self.players[victim_name].deaths += 1
            self.players[victim_name].alive = False  # MORTO!
            self.players[victim_name].last_seen = datetime.now()

            self.teams[killer_team].total_kills += 1
            self.teams[victim_team].total_deaths += 1

            # Verificar duplicata no histórico (segunda camada de proteção)
            kill_signature = f"{killer_name}:{victim_name}"
            for existing_kill in reversed(self.kills_history[-20:]):  # Verificar últimas 20 kills
                if (existing_kill['killer'] == killer_name and
                    existing_kill['victim'] == victim_name):
                    # Kill duplicada! Não adicionar ao histórico
                    logger.warning(f"⚠️ Kill duplicada bloqueada no TeamTracker: {killer_name} -> {victim_name}")
                    return True  # Retorna True mas não adiciona ao histórico

            # Adicionar ao histórico
            kill_record = {
                'killer': killer_name,
                'killer_team': killer_team,
                'victim': victim_name,
                'victim_team': victim_team,
                'distance': distance,
                'timestamp': datetime.now().isoformat()
            }
            self.kills_history.append(kill_record)

            logger.info(f"Kill registrada: {killer_name} ({killer_team}) -> {victim_name} ({victim_team})")

            return True

        except Exception as e:
            logger.error(f"Erro ao registrar kill: {e}")
            return False

    def get_team_stats(self, team_name: str) -> Optional[Dict]:
        """
        Obtém estatísticas de um time

        Args:
            team_name: Nome do time

        Returns:
            Dict com estatísticas ou None
        """
        if team_name not in self.teams:
            return None

        team = self.teams[team_name]

        return {
            'name': team.name,
            'alive': team.alive_count,
            'dead': team.dead_count,
            'total': team.total_players,
            'kills': team.total_kills,
            'deaths': team.total_deaths,
            'players': [
                {
                    'name': p.name,
                    'alive': p.alive,
                    'kills': p.kills,
                    'deaths': p.deaths
                }
                for p in team.players.values()
            ]
        }

    def get_all_teams_stats(self) -> List[Dict]:
        """
        Obtém estatísticas de todos os times

        Returns:
            Lista de dicts com estatísticas
        """
        stats = []

        for team_name in self.teams:
            team_stats = self.get_team_stats(team_name)
            if team_stats:
                stats.append(team_stats)

        # Ordenar por jogadores vivos (descendente)
        stats.sort(key=lambda x: x['alive'], reverse=True)

        return stats

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """
        Obtém leaderboard de jogadores

        Args:
            limit: Número máximo de jogadores

        Returns:
            Lista de jogadores ordenada por kills
        """
        players_list = []

        for player in self.players.values():
            players_list.append({
                'name': player.name,
                'team': player.team,
                'alive': player.alive,
                'kills': player.kills,
                'deaths': player.deaths
            })

        # Ordenar por kills (descendente)
        players_list.sort(key=lambda x: x['kills'], reverse=True)

        return players_list[:limit]

    def get_total_alive(self) -> int:
        """Total de jogadores vivos"""
        return sum(1 for p in self.players.values() if p.alive)

    def get_total_dead(self) -> int:
        """Total de jogadores mortos"""
        return sum(1 for p in self.players.values() if not p.alive)

    def get_active_teams_count(self) -> int:
        """Número de times com jogadores vivos"""
        return sum(1 for team in self.teams.values() if team.alive_count > 0)

    def get_match_summary(self) -> Dict:
        """
        Resumo completo da partida

        Returns:
            Dict com todas as estatísticas
        """
        duration = datetime.now() - self.match_start_time

        return {
            'total_kills': len(self.kills_history),
            'total_players': len(self.players),
            'alive': self.get_total_alive(),
            'dead': self.get_total_dead(),
            'teams_active': self.get_active_teams_count(),
            'teams_total': len(self.teams),
            'duration': str(duration).split('.')[0],  # HH:MM:SS
            'teams': self.get_all_teams_stats(),
            'leaderboard': self.get_leaderboard(10),
            'kills_history': self.kills_history[-50:]  # Últimas 50 kills
        }

    def export_to_dict(self) -> Dict:
        """Exporta todo o estado para dict"""
        return {
            'match': {
                'start_time': self.match_start_time.isoformat(),
                'duration': str(datetime.now() - self.match_start_time).split('.')[0]
            },
            'summary': self.get_match_summary(),
            'teams': {name: self.get_team_stats(name) for name in self.teams},
            'kills_history': self.kills_history
        }


    def _normalize_name(self, name: str, team: str) -> str:
        """
        Normaliza nome removendo prefixo de time duplicado
        Exemplo: "JTX ph13" com team="JTX" → "ph13"
                 "ph13" com team="JTX" → "ph13"

        Args:
            name: Nome do jogador
            team: Time do jogador

        Returns:
            Nome normalizado sem prefixo duplicado
        """
        # Se nome começa com o prefixo do time + espaço, remover
        if team and name.startswith(f"{team} "):
            normalized = name[len(team)+1:]  # Remove "TEAM "
            logger.debug(f"🔧 Normalizando nome: '{name}' -> '{normalized}' (team={team})")
            return normalized

        return name

    def _find_player_fuzzy(self, name: str, team: str = None, threshold: float = 0.70) -> Optional[str]:
        """
        Busca jogador existente com nome similar (Fuzzy Matching)
        Útil para corrigir erros de OCR (ex: 'Player1' vs 'Player|')

        MELHORADO: Detecta nomes com/sem prefixo de time
        - "ph13" == "JTX ph13" (mesmo jogador!)
        - "Kotarav" ~= "Kolarov" (typo de OCR)

        Args:
            name: Nome para buscar
            team: Time do jogador (para detectar prefixo duplicado)
            threshold: Nível de similaridade (0.0 a 1.0)

        Returns:
            Nome correto existente ou None se não encontrar similar
        """
        # Normalizar nome removendo prefixo de time se duplicado
        normalized_name = self._normalize_name(name, team) if team else name

        # Se nome exato (normalizado) existe, retorna ele
        if normalized_name in self.players:
            if normalized_name != name:
                logger.debug(f"🧩 Match exato após normalização: '{name}' -> '{normalized_name}'")
            return normalized_name

        # Tentar encontrar com nome original também
        if name != normalized_name and name in self.players:
            return name

        # Buscar variantes: nome pode estar registrado COM ou SEM prefixo
        # Exemplo: procurando "ph13", mas existe "JTX ph13"
        possible_variants = [
            normalized_name,  # Nome sem prefixo
            f"{team} {normalized_name}" if team else normalized_name,  # Nome com prefixo
        ]

        for variant in possible_variants:
            if variant in self.players:
                logger.debug(f"🧩 Match por variante: '{name}' -> '{variant}'")
                return variant

        # Buscar similar na lista de jogadores existentes (fuzzy)
        # IMPORTANTE: Só fazer match se for do MESMO TIME!
        all_names = list(self.players.keys())

        # Filtrar jogadores do mesmo time
        same_team_names = [
            p_name for p_name in all_names
            if team and self.players[p_name].team == team
        ] if team else all_names

        # Tentar match com nome normalizado (apenas jogadores do mesmo time)
        matches = difflib.get_close_matches(normalized_name, same_team_names, n=1, cutoff=threshold)

        if matches:
            similar_name = matches[0]
            logger.debug(f"🧩 Fuzzy match (mesmo time): '{name}' -> '{similar_name}'")
            return similar_name

        # Tentar match também com versões normalizadas dos nomes existentes
        # Para detectar "Kotarav" vs "Kolarov" mesmo com prefixos diferentes
        # TAMBÉM filtrado por mesmo time!
        normalized_existing = {}
        for existing_name in same_team_names:  # Usar same_team_names em vez de all_names
            # Extrair parte sem prefixo de cada nome existente
            parts = existing_name.split(" ", 1)
            base_name = parts[1] if len(parts) > 1 else parts[0]
            normalized_existing[base_name] = existing_name

        matches = difflib.get_close_matches(normalized_name, normalized_existing.keys(), n=1, cutoff=threshold)

        if matches:
            base_match = matches[0]
            original_name = normalized_existing[base_match]
            logger.debug(f"🧩 Fuzzy match (base name, mesmo time): '{name}' -> '{original_name}' (via '{base_match}')")
            return original_name

        return None


# Função de teste
def test_team_tracker():
    """Teste do tracker"""
    print("="*60)
    print("TESTE DO TEAM TRACKER")
    print("="*60)
    print()

    tracker = TeamTracker()

    # Simular kills baseadas na imagem
    kills = [
        ('almeida99', 'PPP', 'pikachu1337', 'LLL', '120m'),
        ('almeida99', 'PPP', 'OneShOt', 'LLL', '121m'),
        ('Mitsuke', 'HH', 'rafinha', 'AWYS', '85m'),
        ('califofx', 'HH', 'r3cAe', 'HH', '30m'),  # Friendly fire
    ]

    for killer, k_team, victim, v_team, dist in kills:
        tracker.register_kill(killer, k_team, victim, v_team, dist)
        print(f"✓ {killer} ({k_team}) matou {victim} ({v_team}) - {dist}")

    print()
    print("="*60)
    print("ESTATÍSTICAS DOS TIMES:")
    print("="*60)

    for team_stats in tracker.get_all_teams_stats():
        print(f"\n{team_stats['name']}:")
        print(f"  Vivos: {team_stats['alive']}/{team_stats['total']}")
        print(f"  Kills: {team_stats['kills']}")
        print(f"  Jogadores:")
        for player in team_stats['players']:
            status = "🟢 VIVO" if player['alive'] else "🔴 MORTO"
            print(f"    - {player['name']}: {player['kills']} kills | {status}")

    print()
    print("="*60)
    print("LEADERBOARD:")
    print("="*60)

    for idx, player in enumerate(tracker.get_leaderboard(5), 1):
        status = "VIVO" if player['alive'] else "MORTO"
        print(f"{idx}. {player['name']} ({player['team']}) - {player['kills']} kills | {status}")

    print()
    print("="*60)


if __name__ == "__main__":
    test_team_tracker()
