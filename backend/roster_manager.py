"""
Tournament Roster Manager
Handles team roster initialization from images or manual input
"""

import base64
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from src.multi_api_client import MultiAPIClient
from .team_history import get_history_manager

logger = logging.getLogger(__name__)


@dataclass
class TournamentPlayer:
    """Represents a player in tournament mode"""
    name: str
    alive: bool = True
    kills: int = 0
    deaths: int = 0
    revive_count: int = 0


@dataclass
class TournamentTeam:
    """Represents a team in tournament mode"""
    tag: str  # 3-5 letter team tag (e.g., "PPP", "MTL")
    full_name: str = ""  # Optional full team name
    players: Dict[str, TournamentPlayer] = field(default_factory=dict)
    total_kills: int = 0
    max_players: int = 5

    @property
    def alive_count(self) -> int:
        """Count of alive players"""
        return sum(1 for p in self.players.values() if p.alive)

    @property
    def dead_count(self) -> int:
        """Count of dead players"""
        return len(self.players) - self.alive_count

    @property
    def player_count(self) -> int:
        """Total player count"""
        return len(self.players)

    def can_add_player(self) -> bool:
        """Check if team can accept more players"""
        return len(self.players) < self.max_players


class RosterManager:
    """Manages tournament rosters and team initialization"""

    def __init__(self, api_client: MultiAPIClient):
        self.api_client = api_client
        self.teams: Dict[str, TournamentTeam] = {}
        self.tournament_mode = False
        self.history_manager = get_history_manager()

    # Prompt for extracting roster from tournament bracket images
    ROSTER_EXTRACTION_PROMPT = """
Analyze this GTA V Battle Royale tournament image to extract team information.

This image may be:
1. A tournament bracket/roster with team names and player lists
2. A "classificados" (qualified teams) page showing team tags/logos with full names
3. A tournament standings/leaderboard page

YOUR MAIN TASK: Extract ALL teams with their tags AND full names when visible

LOOK FOR:
- Team tags (2-5 letter abbreviations like PPP, MTL, SVV, KUSH, LLL)
- Full team names (like "Peppers", "Metal", "Savage", "Kush Gang", "Legacy")
- Teams shown in tables, lists, or grids
- Team logos with text labels
- Any format showing: TAG - Full Name (e.g., "PPP - Peppers", "MTL | Metal Squad")

IMPORTANT:
- If you see BOTH tag and full name, extract both
- If you see ONLY the tag, leave "full_name" as empty string ""
- Player names are NOT needed - leave "players" as empty array []

Return ONLY valid JSON in this exact format (no markdown, no extra text):
{
  "tournament_name": "extracted tournament name if visible, otherwise null",
  "teams": [
    {"tag": "PPP", "full_name": "Peppers", "players": []},
    {"tag": "MTL", "full_name": "Metal Squad", "players": []},
    {"tag": "SVV", "full_name": "", "players": []},
    {"tag": "KUSH", "full_name": "Kush Gang", "players": []}
  ]
}

CRITICAL RULES:
1. Extract ALL teams visible (up to 20 teams)
2. Team tags MUST be uppercase (PPP, not ppp)
3. Full names can be mixed case (capitalize properly: "Metal Squad" not "METAL SQUAD")
4. Leave "players" as empty array [] - we'll detect them during gameplay
5. TRY to extract full_name when visible, but leave "" if not clear
6. Return ONLY the JSON object, nothing else
7. If you cannot find any teams, return: {"tournament_name": null, "teams": []}

EXAMPLES:
- "PPP - Peppers" → {"tag": "PPP", "full_name": "Peppers", "players": []}
- "MTL | Metal Squad" → {"tag": "MTL", "full_name": "Metal Squad", "players": []}
- Just "SVV" → {"tag": "SVV", "full_name": "", "players": []}
"""

    async def load_from_image(self, image_base64: str) -> Dict:
        """
        Extract tournament roster from bracket/roster image using Vision API
        AGORA VERDADEIRAMENTE ASYNC com retry logic - não bloqueia event loop

        Args:
            image_base64: Base64 encoded tournament bracket image

        Returns:
            Dict with tournament_name and teams list
        """
        logger.info("Extracting roster from tournament image...")

        # Retry logic com exponential backoff
        max_retries = 3
        import asyncio

        for attempt in range(max_retries):
            try:
                # Executar Vision API em thread pool para não bloquear event loop
                loop = asyncio.get_event_loop()

                logger.info(f"🔄 Attempt {attempt + 1}/{max_retries} to extract roster...")

                response = await loop.run_in_executor(
                    None,  # Default executor (ThreadPoolExecutor)
                    lambda: self.api_client.vision_chat_multiple(
                        model="openai/gpt-4o",  # Use best model for accurate extraction
                        prompt=self.ROSTER_EXTRACTION_PROMPT,
                        images_base64=[image_base64],  # vision_chat_multiple expects a list
                        temperature=0.1,  # Low temperature for consistency
                        max_tokens=2000
                    )
                )

                # Se chegou aqui, sucesso!
                logger.info(f"✅ Roster extraction successful on attempt {attempt + 1}")

                # Response is already a dict from vision_chat_multiple
                # Just extract the content
                if isinstance(response, dict) and 'content' in response:
                    response_text = response['content']
                else:
                    response_text = str(response)

                # Parse JSON response
                roster_data = self._parse_roster_response(response_text)

                # Validate and clean data
                roster_data = self._validate_roster_data(roster_data)

                # 🎮 SMART FILL: Merge com histórico de jogadores conhecidos
                teams = roster_data.get('teams', [])
                merged_teams = self.history_manager.merge_with_extracted_teams(teams)
                roster_data['teams'] = merged_teams

                logger.info(f"✅ Extracted {len(merged_teams)} teams from image (smart-filled with history)")
                return roster_data

            except Exception as e:
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")

                # Se foi última tentativa, retornar vazio
                if attempt == max_retries - 1:
                    logger.error(f"❌ All {max_retries} attempts failed. Returning empty roster.")
                    return {"tournament_name": None, "teams": []}

                # Exponential backoff antes de tentar de novo
                backoff_time = 2 ** attempt  # 1s, 2s, 4s
                logger.info(f"⏳ Waiting {backoff_time}s before retry...")
                await asyncio.sleep(backoff_time)

    def _parse_roster_response(self, response: str) -> Dict:
        """Parse Vision API response to extract JSON"""
        try:
            # Try to parse as JSON directly
            return json.loads(response)
        except json.JSONDecodeError:
            # Sometimes AI wraps JSON in markdown code blocks
            # Try to extract JSON from markdown
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Try to find JSON object in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

            logger.warning("Could not parse JSON from Vision API response")
            return {"tournament_name": None, "teams": []}

    def _validate_roster_data(self, roster_data: Dict) -> Dict:
        """Validate and clean roster data"""
        if not isinstance(roster_data, dict):
            return {"tournament_name": None, "teams": []}

        # Ensure required fields exist
        if "teams" not in roster_data:
            roster_data["teams"] = []

        if "tournament_name" not in roster_data:
            roster_data["tournament_name"] = None

        # Validate teams
        valid_teams = []
        for team in roster_data["teams"]:
            if not isinstance(team, dict):
                continue

            # Team must have a tag
            if "tag" not in team or not team["tag"]:
                continue

            # Ensure tag is uppercase and stripped
            team["tag"] = str(team["tag"]).strip().upper()

            # Skip invalid tags (too short or too long)
            if len(team["tag"]) < 2 or len(team["tag"]) > 10:
                continue

            # Ensure full_name exists
            if "full_name" not in team:
                team["full_name"] = ""

            # Ensure players is a list
            if "players" not in team or not isinstance(team["players"], list):
                team["players"] = []

            # Limit to 5 players max
            team["players"] = team["players"][:5]

            # Clean player names (filter out empty strings)
            team["players"] = [str(p).strip() for p in team["players"] if p and str(p).strip()]

            # IMPORTANT: Teams can have ZERO players initially
            # The AI will detect and add players during gameplay
            valid_teams.append(team)

        roster_data["teams"] = valid_teams[:20]  # Max 20 teams
        return roster_data

    def load_from_manual_input(self, teams_data: List[Dict]) -> Dict:
        """
        Load roster from manual form input

        Args:
            teams_data: List of team dicts with tag, full_name, players

        Returns:
            Validated roster data
        """
        roster_data = {
            "tournament_name": "Manual Input",
            "teams": teams_data
        }

        # Validate using same validation function
        return self._validate_roster_data(roster_data)

    def initialize_tournament_roster(self, roster_data: Dict) -> bool:
        """
        Initialize tournament mode with roster data

        Args:
            roster_data: Dict with tournament_name and teams list

        Returns:
            True if successful
        """
        try:
            self.teams.clear()

            for team_data in roster_data.get("teams", []):
                tag = team_data["tag"]

                # Create tournament team
                team = TournamentTeam(
                    tag=tag,
                    full_name=team_data.get("full_name", "")
                )

                # Add players (if provided)
                player_list = team_data.get("players", [])

                if player_list:
                    # Players were provided - use them
                    for player_name in player_list:
                        if player_name and player_name.strip():
                            team.players[player_name] = TournamentPlayer(name=player_name)
                else:
                    # No players provided - create 5 generic placeholders
                    # AI will detect real player names during gameplay and update them
                    for i in range(5):
                        placeholder_name = f"{tag}_P{i+1}"
                        team.players[placeholder_name] = TournamentPlayer(name=placeholder_name)

                self.teams[tag] = team

            self.tournament_mode = True
            logger.info(f"Tournament mode initialized with {len(self.teams)} teams")
            return True

        except Exception as e:
            logger.error(f"Error initializing tournament roster: {e}")
            return False

    def add_team(self, tag: str, full_name: str = "", players: List[str] = None) -> bool:
        """
        Manually add a team to tournament

        Args:
            tag: Team tag (e.g., "PPP")
            full_name: Optional full team name
            players: List of player names

        Returns:
            True if successful
        """
        try:
            tag = tag.strip().upper()

            if tag in self.teams:
                logger.warning(f"Team {tag} already exists")
                return False

            team = TournamentTeam(tag=tag, full_name=full_name)

            if players:
                for player_name in players[:5]:  # Max 5 players
                    if player_name:
                        team.players[player_name] = TournamentPlayer(name=player_name)

            self.teams[tag] = team
            logger.info(f"Added team {tag} with {len(team.players)} players")
            return True

        except Exception as e:
            logger.error(f"Error adding team: {e}")
            return False

    def update_team(self, tag: str, full_name: str = None, players: List[str] = None) -> bool:
        """
        Update existing team information

        Args:
            tag: Team tag
            full_name: New full name (optional)
            players: New player list (optional)

        Returns:
            True if successful
        """
        try:
            tag = tag.strip().upper()

            if tag not in self.teams:
                logger.warning(f"Team {tag} not found")
                return False

            team = self.teams[tag]

            if full_name is not None:
                team.full_name = full_name

            if players is not None:
                # Preserve player stats if updating names
                new_players = {}
                for player_name in players[:5]:
                    if not player_name:
                        continue

                    # If player already exists, keep their stats
                    if player_name in team.players:
                        new_players[player_name] = team.players[player_name]
                    else:
                        new_players[player_name] = TournamentPlayer(name=player_name)

                team.players = new_players

            logger.info(f"Updated team {tag}")
            return True

        except Exception as e:
            logger.error(f"Error updating team: {e}")
            return False

    def remove_team(self, tag: str) -> bool:
        """Remove team from tournament"""
        tag = tag.strip().upper()
        if tag in self.teams:
            del self.teams[tag]
            logger.info(f"Removed team {tag}")
            return True
        return False

    def get_team(self, tag: str) -> Optional[TournamentTeam]:
        """Get team by tag"""
        return self.teams.get(tag.strip().upper())

    def get_all_teams(self) -> List[Dict]:
        """Get all teams as serializable dicts"""
        return [
            {
                "tag": team.tag,
                "full_name": team.full_name,
                "players": [
                    {
                        "name": player.name,
                        "alive": player.alive,
                        "kills": player.kills,
                        "deaths": player.deaths,
                        "revive_count": player.revive_count
                    }
                    for player in team.players.values()
                ],
                "alive_count": team.alive_count,
                "dead_count": team.dead_count,
                "total_kills": team.total_kills
            }
            for team in self.teams.values()
        ]

    def reset_match(self) -> None:
        """Reset all teams for new match (keep roster, reset stats)"""
        for team in self.teams.values():
            team.total_kills = 0
            for player in team.players.values():
                player.alive = True
                player.kills = 0
                player.deaths = 0
                player.revive_count = 0

        logger.info("Match reset - all players alive, stats cleared")

    def clear_roster(self) -> None:
        """Clear all teams (exit tournament mode)"""
        self.teams.clear()
        self.tournament_mode = False
        logger.info("Tournament roster cleared")

    def add_or_replace_player(self, team_tag: str, player_name: str) -> bool:
        """
        Adiciona player real ao time, substituindo placeholder se necessário

        Args:
            team_tag: Tag do time
            player_name: Nome do player real detectado

        Returns:
            True se adicionado/substituído com sucesso
        """
        try:
            team_tag = team_tag.strip().upper()
            team = self.teams.get(team_tag)

            if not team:
                logger.warning(f"Team {team_tag} not found in roster")
                return False

            # Verificar se player já existe
            if player_name in team.players:
                logger.debug(f"Player {player_name} already in team {team_tag}")
                return True

            # Verificar se time está cheio (5 players reais)
            real_players = [name for name in team.players.keys() if not name.startswith(f"{team_tag}_P")]

            if len(real_players) >= 5:
                logger.warning(f"Team {team_tag} already has 5 real players")
                return False

            # Encontrar primeiro placeholder para substituir
            placeholder_to_remove = None
            for name in team.players.keys():
                if name.startswith(f"{team_tag}_P"):
                    placeholder_to_remove = name
                    break

            # Substituir placeholder ou adicionar
            if placeholder_to_remove:
                logger.info(f"🔄 Replacing placeholder {placeholder_to_remove} with real player {player_name} in {team_tag}")
                del team.players[placeholder_to_remove]

            team.players[player_name] = TournamentPlayer(name=player_name)
            logger.info(f"✅ Added real player {player_name} to team {team_tag}")
            return True

        except Exception as e:
            logger.error(f"Error adding player to roster: {e}")
            return False

    def update_player_stats(self, team_tag: str, player_name: str, killed: bool = False, died: bool = False, kills_to_add: int = 0) -> bool:
        """
        Atualiza estatísticas de player de forma thread-safe

        Args:
            team_tag: Tag do time
            player_name: Nome do player
            killed: Se o player matou alguém
            died: Se o player morreu
            kills_to_add: Número de kills para adicionar

        Returns:
            True se atualizado com sucesso
        """
        try:
            team_tag = team_tag.strip().upper()
            team = self.teams.get(team_tag)

            if not team:
                logger.warning(f"Team {team_tag} not found")
                return False

            if player_name not in team.players:
                logger.warning(f"Player {player_name} not found in team {team_tag}")
                return False

            player = team.players[player_name]

            # Atualizar stats
            if killed or kills_to_add > 0:
                player.kills += max(1 if killed else 0, kills_to_add)
                team.total_kills += max(1 if killed else 0, kills_to_add)
                logger.debug(f"📊 {player_name} ({team_tag}): +{kills_to_add} kills → {player.kills} total")

            if died and player.alive:
                player.alive = False
                player.deaths += 1
                logger.debug(f"💀 {player_name} ({team_tag}): marked as dead")

            return True

        except Exception as e:
            logger.error(f"Error updating player stats: {e}")
            return False
