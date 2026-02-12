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

logging.basicConfig(level=logging.INFO)
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
