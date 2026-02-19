"""
Team History Manager - Mantém histórico de jogadores por TAG de time
Permite preenchimento automático inteligente baseado em participações anteriores
"""

import json
import os
import logging
from typing import Dict, List, Set, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class PlayerHistoryEntry:
    """Histórico de um jogador"""
    name: str
    first_seen: str  # ISO datetime
    last_seen: str   # ISO datetime
    total_appearances: int = 0
    total_kills: int = 0
    total_deaths: int = 0
    win_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class TeamHistory:
    """Histórico de um time"""
    tag: str
    full_name: str = ""
    known_players: Dict[str, PlayerHistoryEntry] = field(default_factory=dict)
    tournament_count: int = 0
    last_updated: str = ""

    def to_dict(self) -> dict:
        return {
            "tag": self.tag,
            "full_name": self.full_name,
            "known_players": {name: player.to_dict() for name, player in self.known_players.items()},
            "tournament_count": self.tournament_count,
            "last_updated": self.last_updated
        }

    @classmethod
    def from_dict(cls, data: dict):
        team = cls(
            tag=data["tag"],
            full_name=data.get("full_name", ""),
            tournament_count=data.get("tournament_count", 0),
            last_updated=data.get("last_updated", "")
        )

        # Restore players
        for player_name, player_data in data.get("known_players", {}).items():
            team.known_players[player_name] = PlayerHistoryEntry.from_dict(player_data)

        return team


class TeamHistoryManager:
    """
    Gerencia histórico de times e jogadores para preenchimento automático inteligente
    """

    def __init__(self, history_file: str = "team_history.json"):
        self.history_file = history_file
        self.teams: Dict[str, TeamHistory] = {}
        self.load_history()

    def load_history(self):
        """Carrega histórico do arquivo JSON"""
        if not os.path.exists(self.history_file):
            logger.info(f"No history file found at {self.history_file}, starting fresh")
            return

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Restore teams
            for tag, team_data in data.get("teams", {}).items():
                self.teams[tag] = TeamHistory.from_dict(team_data)

            logger.info(f"✅ Loaded history for {len(self.teams)} teams")

        except Exception as e:
            logger.error(f"Error loading history: {e}")

    def save_history(self):
        """Salva histórico no arquivo JSON"""
        try:
            data = {
                "teams": {tag: team.to_dict() for tag, team in self.teams.items()},
                "last_saved": datetime.now().isoformat()
            }

            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 History saved for {len(self.teams)} teams")

        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def get_known_players(self, team_tag: str, limit: int = 5) -> List[str]:
        """
        Retorna lista de jogadores conhecidos para uma TAG de time
        Ordenados por: mais recentes e com mais aparições

        Args:
            team_tag: TAG do time (ex: "PPP", "MTL")
            limit: Número máximo de jogadores a retornar

        Returns:
            Lista de nomes de jogadores
        """
        team_tag = team_tag.strip().upper()

        if team_tag not in self.teams:
            logger.info(f"No history found for team {team_tag}")
            return []

        team = self.teams[team_tag]

        # Ordenar jogadores por: último visto (mais recente primeiro) + aparições
        sorted_players = sorted(
            team.known_players.values(),
            key=lambda p: (p.last_seen, p.total_appearances),
            reverse=True
        )

        player_names = [p.name for p in sorted_players[:limit]]

        logger.info(f"🎮 Found {len(player_names)} known players for {team_tag}: {player_names}")
        return player_names

    def update_player(
        self,
        team_tag: str,
        player_name: str,
        kills: int = 0,
        deaths: int = 0,
        won: bool = False
    ):
        """
        Atualiza ou adiciona jogador ao histórico de um time

        Args:
            team_tag: TAG do time
            player_name: Nome do jogador
            kills: Kills nesta partida
            deaths: Deaths nesta partida
            won: Se o time ganhou o torneio
        """
        team_tag = team_tag.strip().upper()

        # Criar time se não existir
        if team_tag not in self.teams:
            self.teams[team_tag] = TeamHistory(tag=team_tag)

        team = self.teams[team_tag]
        now = datetime.now().isoformat()

        # Atualizar ou criar jogador
        if player_name in team.known_players:
            player = team.known_players[player_name]
            player.last_seen = now
            player.total_appearances += 1
            player.total_kills += kills
            player.total_deaths += deaths
            if won:
                player.win_count += 1
        else:
            team.known_players[player_name] = PlayerHistoryEntry(
                name=player_name,
                first_seen=now,
                last_seen=now,
                total_appearances=1,
                total_kills=kills,
                total_deaths=deaths,
                win_count=1 if won else 0
            )

        team.last_updated = now

    def update_team_info(self, team_tag: str, full_name: str = None):
        """Atualiza informações do time"""
        team_tag = team_tag.strip().upper()

        if team_tag not in self.teams:
            self.teams[team_tag] = TeamHistory(tag=team_tag)

        if full_name:
            self.teams[team_tag].full_name = full_name

    def record_tournament(self, roster_data: Dict, winner_tag: str = None):
        """
        Registra um torneio completo no histórico

        Args:
            roster_data: Dados do roster após o torneio (com stats)
            winner_tag: TAG do time vencedor (opcional)
        """
        try:
            teams = roster_data.get("teams", [])

            for team in teams:
                tag = team["tag"]
                full_name = team.get("full_name", "")
                won = (tag == winner_tag)

                # Update team info
                self.update_team_info(tag, full_name)

                # Update each player
                for player in team.get("players", []):
                    player_name = player["name"]
                    kills = player.get("kills", 0)
                    deaths = player.get("deaths", 0)

                    self.update_player(tag, player_name, kills, deaths, won)

                # Increment tournament count
                if tag in self.teams:
                    self.teams[tag].tournament_count += 1

            # Save after recording
            self.save_history()
            logger.info(f"✅ Recorded tournament with {len(teams)} teams")

        except Exception as e:
            logger.error(f"Error recording tournament: {e}")

    def get_team_stats(self, team_tag: str) -> Optional[Dict]:
        """Retorna estatísticas de um time"""
        team_tag = team_tag.strip().upper()

        if team_tag not in self.teams:
            return None

        team = self.teams[team_tag]

        return {
            "tag": team.tag,
            "full_name": team.full_name,
            "tournament_count": team.tournament_count,
            "player_count": len(team.known_players),
            "total_kills": sum(p.total_kills for p in team.known_players.values()),
            "top_players": [
                {
                    "name": p.name,
                    "appearances": p.total_appearances,
                    "kills": p.total_kills,
                    "kd_ratio": round(p.total_kills / max(p.total_deaths, 1), 2)
                }
                for p in sorted(
                    team.known_players.values(),
                    key=lambda x: x.total_kills,
                    reverse=True
                )[:5]
            ]
        }

    def get_all_team_tags(self) -> List[str]:
        """Retorna lista de todas as TAGs conhecidas"""
        return sorted(self.teams.keys())

    def validate_player_team(self, player_name: str, team_tag: str) -> Dict:
        """
        Valida se um jogador pertence ao time indicado baseado no histórico

        Args:
            player_name: Nome do jogador
            team_tag: TAG do time

        Returns:
            Dict com validação:
            {
                "valid": bool,
                "confidence": float (0-1),
                "known_team": str or None,
                "suggestion": str
            }
        """
        team_tag = team_tag.strip().upper()

        # Procurar jogador em todos os times
        player_teams = []
        for tag, team in self.teams.items():
            if player_name in team.known_players:
                player = team.known_players[player_name]
                player_teams.append({
                    "tag": tag,
                    "appearances": player.total_appearances,
                    "last_seen": player.last_seen
                })

        # Se não tem histórico, aceitar
        if not player_teams:
            return {
                "valid": True,
                "confidence": 0.5,
                "known_team": None,
                "suggestion": f"New player detected: {player_name}"
            }

        # Se jogador sempre jogou por este time
        if len(player_teams) == 1 and player_teams[0]["tag"] == team_tag:
            return {
                "valid": True,
                "confidence": 1.0,
                "known_team": team_tag,
                "suggestion": f"✅ {player_name} confirmed for {team_tag}"
            }

        # Se jogador apareceu em múltiplos times
        most_frequent = max(player_teams, key=lambda x: x["appearances"])

        if most_frequent["tag"] == team_tag:
            return {
                "valid": True,
                "confidence": 0.8,
                "known_team": team_tag,
                "suggestion": f"⚠️ {player_name} played for multiple teams, but most for {team_tag}"
            }

        # Jogador está em time diferente do histórico
        return {
            "valid": False,
            "confidence": 0.2,
            "known_team": most_frequent["tag"],
            "suggestion": f"❌ Warning: {player_name} historically plays for {most_frequent['tag']}, not {team_tag}"
        }

    def suggest_player_correction(self, detected_name: str, team_tag: str) -> Optional[str]:
        """
        Sugere correção de nome baseado em similaridade com jogadores conhecidos do time

        Args:
            detected_name: Nome detectado pela IA (pode ter erro OCR)
            team_tag: TAG do time

        Returns:
            Nome sugerido ou None
        """
        team_tag = team_tag.strip().upper()

        if team_tag not in self.teams:
            return None

        team = self.teams[team_tag]
        known_names = list(team.known_players.keys())

        if not known_names:
            return None

        # Função simples de similaridade (Levenshtein simplificado)
        def similarity(s1: str, s2: str) -> float:
            s1, s2 = s1.lower(), s2.lower()
            if s1 == s2:
                return 1.0

            # Check if one contains the other
            if s1 in s2 or s2 in s1:
                return 0.8

            # Simple character overlap
            common = len(set(s1) & set(s2))
            total = len(set(s1) | set(s2))
            return common / total if total > 0 else 0.0

        # Encontrar nome mais similar
        best_match = None
        best_score = 0.0

        for known_name in known_names:
            score = similarity(detected_name, known_name)
            if score > best_score:
                best_score = score
                best_match = known_name

        # Só sugerir se similaridade > 60%
        if best_score > 0.6:
            logger.info(f"💡 Suggesting '{best_match}' instead of '{detected_name}' (confidence: {best_score:.0%})")
            return best_match

        return None

    def smart_fill_roster(self, team_tags: List[str]) -> Dict:
        """
        Preenche roster automaticamente com jogadores conhecidos

        Args:
            team_tags: Lista de TAGs de times

        Returns:
            Roster data com jogadores preenchidos
        """
        teams = []

        for tag in team_tags:
            tag = tag.strip().upper()
            known_players = self.get_known_players(tag, limit=5)

            team_data = {
                "tag": tag,
                "full_name": self.teams.get(tag, TeamHistory(tag=tag)).full_name,
                "players": known_players  # Lista de nomes apenas
            }

            teams.append(team_data)

        return {
            "tournament_name": "Auto-filled from history",
            "teams": teams
        }

    def merge_with_extracted_teams(self, extracted_teams: List[Dict]) -> List[Dict]:
        """
        Mescla times extraídos da imagem com histórico conhecido
        Se a TAG é conhecida, preenche jogadores automaticamente

        Args:
            extracted_teams: Times extraídos da imagem pela IA

        Returns:
            Times com jogadores preenchidos quando possível
        """
        merged = []

        for team in extracted_teams:
            tag = team["tag"]

            # Se temos jogadores na extração, usar eles
            if team.get("players") and len(team["players"]) > 0:
                merged.append(team)
                logger.info(f"✅ Team {tag}: Using {len(team['players'])} players from image")
                continue

            # Caso contrário, buscar do histórico
            known_players = self.get_known_players(tag, limit=5)

            if known_players:
                team["players"] = known_players
                logger.info(f"🎮 Team {tag}: Auto-filled with {len(known_players)} known players from history")
            else:
                # Sem histórico, deixar vazio (backend criará placeholders)
                team["players"] = []
                logger.info(f"⚠️ Team {tag}: No history, will use placeholders")

            merged.append(team)

        return merged


# Global instance
_history_manager = None


def get_history_manager() -> TeamHistoryManager:
    """Singleton para acessar o gerenciador de histórico"""
    global _history_manager
    if _history_manager is None:
        _history_manager = TeamHistoryManager()
    return _history_manager
