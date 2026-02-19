"""
Tournament Progress Tracker - Acompanhamento em tempo real do torneio
Cruza dados do torneio atual com histórico para insights em tempo real
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from team_history import get_history_manager

logger = logging.getLogger(__name__)


@dataclass
class PlayerLiveStats:
    """Estatísticas ao vivo de um jogador"""
    name: str
    team_tag: str
    kills_today: int = 0
    deaths_today: int = 0
    alive: bool = True

    # Histórico
    avg_kills: float = 0.0
    total_appearances: int = 0
    validation_status: str = "unknown"  # "confirmed", "warning", "new"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TeamLiveStats:
    """Estatísticas ao vivo de um time"""
    tag: str
    full_name: str
    players_alive: int = 0
    total_kills: int = 0

    # Comparação com histórico
    avg_kills_per_tournament: float = 0.0
    tournament_count: int = 0
    performance_vs_avg: str = "average"  # "above", "below", "average"

    def to_dict(self) -> dict:
        return asdict(self)


class TournamentTracker:
    """
    Rastreia progresso do torneio e fornece insights em tempo real
    """

    def __init__(self):
        self.history_manager = get_history_manager()
        self.tournament_start_time = None
        self.current_teams: Dict[str, TeamLiveStats] = {}
        self.current_players: Dict[str, PlayerLiveStats] = {}

    def start_tracking(self, roster_data: Dict):
        """Inicia tracking do torneio"""
        self.tournament_start_time = datetime.now()
        self.current_teams.clear()
        self.current_players.clear()

        teams = roster_data.get("teams", [])

        for team in teams:
            tag = team["tag"]

            # Buscar stats históricas
            hist_stats = self.history_manager.get_team_stats(tag)

            team_stats = TeamLiveStats(
                tag=tag,
                full_name=team.get("full_name", ""),
                tournament_count=hist_stats["tournament_count"] if hist_stats else 0,
                avg_kills_per_tournament=hist_stats["total_kills"] / max(hist_stats["tournament_count"], 1) if hist_stats else 0.0
            )

            self.current_teams[tag] = team_stats

            # Inicializar jogadores
            for player in team.get("players", []):
                player_name = player["name"] if isinstance(player, dict) else player

                # Validar jogador
                validation = self.history_manager.validate_player_team(player_name, tag)

                # Buscar média histórica
                avg_kills = 0.0
                appearances = 0
                if tag in self.history_manager.teams:
                    if player_name in self.history_manager.teams[tag].known_players:
                        hist_player = self.history_manager.teams[tag].known_players[player_name]
                        avg_kills = hist_player.total_kills / max(hist_player.total_appearances, 1)
                        appearances = hist_player.total_appearances

                player_stats = PlayerLiveStats(
                    name=player_name,
                    team_tag=tag,
                    avg_kills=avg_kills,
                    total_appearances=appearances,
                    validation_status="confirmed" if validation["valid"] else "warning"
                )

                self.current_players[f"{tag}_{player_name}"] = player_stats

        logger.info(f"✅ Tournament tracking started with {len(self.current_teams)} teams, {len(self.current_players)} players")

    def update_player_kill(self, team_tag: str, player_name: str):
        """Registra kill de um jogador"""
        key = f"{team_tag}_{player_name}"

        if key in self.current_players:
            self.current_players[key].kills_today += 1
        else:
            # Novo jogador detectado
            logger.info(f"🆕 New player detected: {player_name} from {team_tag}")

            # Tentar corrigir nome
            suggestion = self.history_manager.suggest_player_correction(player_name, team_tag)
            if suggestion:
                logger.info(f"💡 Correcting '{player_name}' to '{suggestion}'")
                player_name = suggestion
                key = f"{team_tag}_{player_name}"

            # Criar novo player
            validation = self.history_manager.validate_player_team(player_name, team_tag)

            self.current_players[key] = PlayerLiveStats(
                name=player_name,
                team_tag=team_tag,
                kills_today=1,
                validation_status="new"
            )

        # Atualizar team
        if team_tag in self.current_teams:
            self.current_teams[team_tag].total_kills += 1

    def update_player_death(self, team_tag: str, player_name: str):
        """Registra morte de um jogador"""
        key = f"{team_tag}_{player_name}"

        if key in self.current_players:
            self.current_players[key].deaths_today += 1
            self.current_players[key].alive = False

        # Atualizar contagem de vivos no time
        if team_tag in self.current_teams:
            alive_count = sum(
                1 for p in self.current_players.values()
                if p.team_tag == team_tag and p.alive
            )
            self.current_teams[team_tag].players_alive = alive_count

    def get_live_dashboard_data(self) -> Dict:
        """Retorna dados consolidados para o dashboard"""

        # Calcular performance vs média para cada time
        for team in self.current_teams.values():
            if team.avg_kills_per_tournament > 0:
                ratio = team.total_kills / team.avg_kills_per_tournament
                if ratio > 1.2:
                    team.performance_vs_avg = "above"
                elif ratio < 0.8:
                    team.performance_vs_avg = "below"
                else:
                    team.performance_vs_avg = "average"

        # Top performers
        top_players = sorted(
            self.current_players.values(),
            key=lambda p: p.kills_today,
            reverse=True
        )[:10]

        # Alertas
        alerts = []

        # Alertas de jogadores em times errados
        for player in self.current_players.values():
            if player.validation_status == "warning":
                validation = self.history_manager.validate_player_team(player.name, player.team_tag)
                if not validation["valid"]:
                    alerts.append({
                        "type": "warning",
                        "message": validation["suggestion"]
                    })

        # Alertas de performances excepcionais
        for player in self.current_players.values():
            if player.avg_kills > 0 and player.kills_today > player.avg_kills * 2:
                alerts.append({
                    "type": "highlight",
                    "message": f"🔥 {player.name} ({player.team_tag}): {player.kills_today} kills - 2x acima da média!"
                })

        return {
            "tournament_duration": (datetime.now() - self.tournament_start_time).seconds if self.tournament_start_time else 0,
            "teams": [team.to_dict() for team in self.current_teams.values()],
            "top_players": [p.to_dict() for p in top_players],
            "alerts": alerts,
            "total_kills": sum(t.total_kills for t in self.current_teams.values()),
            "teams_alive": sum(1 for t in self.current_teams.values() if t.players_alive > 0)
        }

    def finish_tournament(self, winner_tag: str = None):
        """Finaliza torneio e salva no histórico"""

        # Preparar dados para histórico
        roster_data = {
            "teams": []
        }

        for team in self.current_teams.values():
            team_players = [
                p.to_dict() for p in self.current_players.values()
                if p.team_tag == team.tag
            ]

            roster_data["teams"].append({
                "tag": team.tag,
                "full_name": team.full_name,
                "players": team_players
            })

        # Registrar no histórico
        self.history_manager.record_tournament(roster_data, winner_tag)

        logger.info(f"✅ Tournament finished and recorded. Winner: {winner_tag or 'TBD'}")


# Global instance
_tracker = None


def get_tracker() -> TournamentTracker:
    """Singleton para acessar o tracker"""
    global _tracker
    if _tracker is None:
        _tracker = TournamentTracker()
    return _tracker
