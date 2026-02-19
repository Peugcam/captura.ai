"""
Player Identity Manager - Sistema de identificação de jogadores por múltiplos nomes
Permite rastrear jogadores mesmo quando mudam de nickname
"""

import json
import os
import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PlayerIdentity:
    """
    Representa a identidade de um jogador através de múltiplos nomes
    """
    player_id: str  # ID único gerado (ex: "player_001")
    primary_name: str  # Nome principal/mais recente
    aliases: Set[str] = field(default_factory=set)  # Todos os nomes já usados

    # Histórico agregado de TODOS os nomes
    total_tournaments: int = 0
    total_kills: int = 0
    total_deaths: int = 0
    total_wins: int = 0

    # Metadados
    first_seen: str = ""
    last_seen: str = ""
    last_team_tag: str = ""  # Último time onde jogou

    # Tags de times históricos (para detectar mudanças de time)
    team_history: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        data = asdict(self)
        data['aliases'] = list(self.aliases)  # Set não é JSON serializable
        return data

    @classmethod
    def from_dict(cls, data: dict):
        player = cls(
            player_id=data["player_id"],
            primary_name=data["primary_name"],
            aliases=set(data.get("aliases", [])),
            total_tournaments=data.get("total_tournaments", 0),
            total_kills=data.get("total_kills", 0),
            total_deaths=data.get("total_deaths", 0),
            total_wins=data.get("total_wins", 0),
            first_seen=data.get("first_seen", ""),
            last_seen=data.get("last_seen", ""),
            last_team_tag=data.get("last_team_tag", ""),
            team_history=data.get("team_history", [])
        )
        return player

    @property
    def kd_ratio(self) -> float:
        """Kill/Death ratio"""
        return round(self.total_kills / max(self.total_deaths, 1), 2)

    @property
    def avg_kills_per_tournament(self) -> float:
        """Média de kills por torneio"""
        return round(self.total_kills / max(self.total_tournaments, 1), 2)


class PlayerIdentityManager:
    """
    Gerencia identidades de jogadores através de múltiplos nomes

    Características:
    - Detecta quando "John_Pro" é provavelmente o mesmo que "xXJohnXx"
    - Permite linking manual: "Esses 2 nomes são a mesma pessoa"
    - Mantém estatísticas agregadas de todos os nomes
    """

    def __init__(self, identity_file: str = "player_identities.json"):
        self.identity_file = identity_file

        # Estruturas de dados
        self.players: Dict[str, PlayerIdentity] = {}  # player_id -> PlayerIdentity
        self.name_to_id: Dict[str, str] = {}  # name -> player_id (índice reverso)

        self.load_identities()

    def load_identities(self):
        """Carrega identidades do arquivo JSON"""
        if not os.path.exists(self.identity_file):
            logger.info(f"No identity file found at {self.identity_file}, starting fresh")
            return

        try:
            with open(self.identity_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Restore players
            for player_id, player_data in data.get("players", {}).items():
                player = PlayerIdentity.from_dict(player_data)
                self.players[player_id] = player

                # Rebuild name index
                for name in player.aliases:
                    self.name_to_id[name.lower()] = player_id

            logger.info(f"✅ Loaded {len(self.players)} player identities")

        except Exception as e:
            logger.error(f"Error loading identities: {e}")

    def save_identities(self):
        """Salva identidades no arquivo JSON"""
        try:
            data = {
                "players": {player_id: player.to_dict() for player_id, player in self.players.items()},
                "last_saved": datetime.now().isoformat(),
                "total_players": len(self.players)
            }

            with open(self.identity_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Identities saved ({len(self.players)} players)")

        except Exception as e:
            logger.error(f"Error saving identities: {e}")

    def get_or_create_player(self, name: str, team_tag: str = "") -> str:
        """
        Retorna player_id para um nome, criando novo player se necessário

        Args:
            name: Nome do jogador
            team_tag: TAG do time atual (opcional)

        Returns:
            player_id
        """
        name_lower = name.lower()

        # Se nome já existe, retornar ID
        if name_lower in self.name_to_id:
            return self.name_to_id[name_lower]

        # Tentar detectar similaridade com players existentes
        similar_player_id = self._find_similar_player(name, team_tag)

        if similar_player_id:
            # Adicionar como alias de player existente
            player = self.players[similar_player_id]
            player.aliases.add(name)
            player.primary_name = name  # Atualizar para nome mais recente
            self.name_to_id[name_lower] = similar_player_id

            logger.info(f"🔗 Linked '{name}' to existing player {similar_player_id} (aliases: {player.aliases})")
            return similar_player_id

        # Criar novo player
        player_id = f"player_{len(self.players) + 1:04d}"
        now = datetime.now().isoformat()

        player = PlayerIdentity(
            player_id=player_id,
            primary_name=name,
            aliases={name},
            first_seen=now,
            last_seen=now,
            last_team_tag=team_tag,
            team_history=[team_tag] if team_tag else []
        )

        self.players[player_id] = player
        self.name_to_id[name_lower] = player_id

        logger.info(f"🆕 Created new player identity: {player_id} ({name})")
        return player_id

    def _find_similar_player(self, name: str, team_tag: str = "") -> Optional[str]:
        """
        Tenta encontrar player existente similar ao nome fornecido

        Heurísticas:
        1. Similaridade de string (> 70%)
        2. Mesmo time (aumenta confiança)
        3. Prefixos/sufixos comuns (xX...Xx, _Pro, _GG, etc)
        """

        def normalize_name(n: str) -> str:
            """Remove prefixos/sufixos comuns"""
            n = n.lower()
            # Remove prefixos/sufixos comuns
            prefixes = ['xx', 'x_', '_x', 'yt_', 'twitch_', 'tt_']
            suffixes = ['xx', '_x', 'x_', '_pro', '_gg', '_tv', '_ttv', '_yt']

            for prefix in prefixes:
                if n.startswith(prefix):
                    n = n[len(prefix):]

            for suffix in suffixes:
                if n.endswith(suffix):
                    n = n[:-len(suffix)]

            return n.strip('_- ')

        normalized_input = normalize_name(name)

        # Procurar em todos os players
        best_match_id = None
        best_score = 0.0

        for player_id, player in self.players.items():
            # Verificar similaridade com cada alias
            for alias in player.aliases:
                normalized_alias = normalize_name(alias)

                # Similaridade básica
                similarity = self._string_similarity(normalized_input, normalized_alias)

                # Bonus se mesmo time
                if team_tag and player.last_team_tag == team_tag:
                    similarity += 0.2

                if similarity > best_score:
                    best_score = similarity
                    best_match_id = player_id

        # Só aceitar se similaridade > 70%
        if best_score >= 0.7:
            logger.info(f"💡 Found similar player: '{name}' ≈ {self.players[best_match_id].primary_name} (score: {best_score:.0%})")
            return best_match_id

        return None

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calcula similaridade entre duas strings (0.0 a 1.0)"""
        if s1 == s2:
            return 1.0

        # Substring match
        if s1 in s2 or s2 in s1:
            return 0.85

        # Levenshtein simplificado (overlap de caracteres)
        s1_set = set(s1)
        s2_set = set(s2)

        intersection = len(s1_set & s2_set)
        union = len(s1_set | s2_set)

        return intersection / union if union > 0 else 0.0

    def link_players_manually(self, name1: str, name2: str) -> bool:
        """
        Força linking manual de dois nomes (mesclagem)
        Útil quando sistema não detecta automaticamente

        Args:
            name1: Primeiro nome
            name2: Segundo nome

        Returns:
            True se mesclado com sucesso
        """
        id1 = self.name_to_id.get(name1.lower())
        id2 = self.name_to_id.get(name2.lower())

        if not id1 or not id2:
            logger.warning(f"Cannot link: one or both names not found ({name1}, {name2})")
            return False

        if id1 == id2:
            logger.info(f"Names already linked: {name1} and {name2}")
            return True

        # Mesclar player2 em player1
        player1 = self.players[id1]
        player2 = self.players[id2]

        # Transferir aliases
        player1.aliases.update(player2.aliases)

        # Agregar estatísticas
        player1.total_tournaments += player2.total_tournaments
        player1.total_kills += player2.total_kills
        player1.total_deaths += player2.total_deaths
        player1.total_wins += player2.total_wins

        # Atualizar índice
        for alias in player2.aliases:
            self.name_to_id[alias.lower()] = id1

        # Remover player2
        del self.players[id2]

        logger.info(f"🔗 Manually linked {name1} and {name2} → {id1}")
        self.save_identities()
        return True

    def update_player_stats(
        self,
        name: str,
        team_tag: str = "",
        kills: int = 0,
        deaths: int = 0,
        won: bool = False
    ):
        """Atualiza estatísticas de um jogador"""
        player_id = self.get_or_create_player(name, team_tag)
        player = self.players[player_id]

        player.total_kills += kills
        player.total_deaths += deaths
        if won:
            player.total_wins += 1

        player.last_seen = datetime.now().isoformat()

        if team_tag and team_tag not in player.team_history:
            player.team_history.append(team_tag)
            player.last_team_tag = team_tag

    def finish_tournament(self, roster_data: Dict, winner_tag: str = None):
        """Registra um torneio completo"""
        teams = roster_data.get("teams", [])

        for team in teams:
            tag = team["tag"]
            won = (tag == winner_tag)

            for player in team.get("players", []):
                player_name = player["name"]
                kills = player.get("kills", 0)
                deaths = player.get("deaths", 0)

                player_id = self.get_or_create_player(player_name, tag)
                player = self.players[player_id]

                # Incrementar contador de torneios apenas uma vez
                player.total_tournaments += 1
                player.total_kills += kills
                player.total_deaths += deaths
                if won:
                    player.total_wins += 1

                player.last_seen = datetime.now().isoformat()

                if tag not in player.team_history:
                    player.team_history.append(tag)
                player.last_team_tag = tag

        self.save_identities()
        logger.info(f"✅ Tournament recorded for {len(self.players)} players")

    def get_player_stats(self, name: str) -> Optional[Dict]:
        """Retorna estatísticas completas de um jogador"""
        player_id = self.name_to_id.get(name.lower())

        if not player_id:
            return None

        player = self.players[player_id]

        return {
            "player_id": player.player_id,
            "primary_name": player.primary_name,
            "aliases": list(player.aliases),
            "total_tournaments": player.total_tournaments,
            "total_kills": player.total_kills,
            "total_deaths": player.total_deaths,
            "kd_ratio": player.kd_ratio,
            "avg_kills": player.avg_kills_per_tournament,
            "total_wins": player.total_wins,
            "win_rate": round(player.total_wins / max(player.total_tournaments, 1) * 100, 1),
            "team_history": player.team_history,
            "last_team": player.last_team_tag
        }

    def get_top_players(self, metric: str = "kills", limit: int = 10) -> List[Dict]:
        """Retorna ranking de melhores jogadores"""

        sorting_key = {
            "kills": lambda p: p.total_kills,
            "kd": lambda p: p.kd_ratio,
            "wins": lambda p: p.total_wins,
            "tournaments": lambda p: p.total_tournaments
        }.get(metric, lambda p: p.total_kills)

        sorted_players = sorted(
            self.players.values(),
            key=sorting_key,
            reverse=True
        )[:limit]

        return [
            {
                "rank": i + 1,
                "player_id": p.player_id,
                "primary_name": p.primary_name,
                "aliases": list(p.aliases),
                "total_kills": p.total_kills,
                "kd_ratio": p.kd_ratio,
                "total_wins": p.total_wins,
                "tournaments": p.total_tournaments
            }
            for i, p in enumerate(sorted_players)
        ]


# Global instance
_identity_manager = None


def get_identity_manager() -> PlayerIdentityManager:
    """Singleton para acessar o gerenciador"""
    global _identity_manager
    if _identity_manager is None:
        _identity_manager = PlayerIdentityManager()
    return _identity_manager
