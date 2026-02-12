"""
Unit Tests: TeamTracker
========================

Tests the team tracking system for real-time match statistics.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from src.team_tracker import TeamTracker, Team, Player


class TestTeamTracker:
    """Test suite for TeamTracker"""
    
    @pytest.fixture
    def tracker(self):
        """Create tracker instance"""
        return TeamTracker(total_players=100)
    
    # ========================================================================
    # Test: Initialization
    # ========================================================================
    
    def test_initialization(self, tracker):
        """Test tracker initializes correctly"""
        assert tracker.total_players == 100
        assert len(tracker.teams) == 0
        assert len(tracker.kills_history) == 0
    
    # ========================================================================
    # Test: Kill Registration
    # ========================================================================
    
    def test_register_single_kill(self, tracker):
        """Test registering a single kill"""
        success = tracker.register_kill(
            killer_name="player1",
            killer_team="TeamA",
            victim_name="player2",
            victim_team="TeamB",
            distance="100m"
        )
        
        assert success is True
        assert len(tracker.kills_history) == 1
        assert len(tracker.teams) == 2
    
    def test_register_multiple_kills(self, tracker, mock_multiple_kills):
        """Test registering multiple kills"""
        for kill in mock_multiple_kills:
            tracker.register_kill(
                killer_name=kill['killer'],
                killer_team=kill['killer_team'],
                victim_name=kill['victim'],
                victim_team=kill['victim_team'],
                distance=kill.get('distance')
            )
        
        assert len(tracker.kills_history) == 3
        assert len(tracker.teams) >= 2
    
    def test_register_kill_updates_killer_stats(self, tracker):
        """Test that registering a kill updates killer stats"""
        tracker.register_kill(
            killer_name="player1",
            killer_team="TeamA",
            victim_name="player2",
            victim_team="TeamB"
        )
        
        team_a = tracker.teams['TeamA']
        player1 = team_a.players['player1']
        
        assert player1.kills == 1
        assert player1.deaths == 0
        assert player1.alive is True
    
    def test_register_kill_updates_victim_stats(self, tracker):
        """Test that registering a kill updates victim stats"""
        tracker.register_kill(
            killer_name="player1",
            killer_team="TeamA",
            victim_name="player2",
            victim_team="TeamB"
        )
        
        team_b = tracker.teams['TeamB']
        player2 = team_b.players['player2']
        
        assert player2.kills == 0
        assert player2.deaths == 1
        assert player2.alive is False
    
    def test_register_kill_updates_team_stats(self, tracker):
        """Test that registering a kill updates team stats"""
        tracker.register_kill(
            killer_name="player1",
            killer_team="TeamA",
            victim_name="player2",
            victim_team="TeamB"
        )
        
        team_a = tracker.teams['TeamA']
        team_b = tracker.teams['TeamB']
        
        assert team_a.total_kills == 1
        assert team_a.total_deaths == 0
        assert team_b.total_kills == 0
        assert team_b.total_deaths == 1
    
    # ========================================================================
    # Test: Team Statistics
    # ========================================================================
    
    def test_get_team_stats(self, tracker):
        """Test getting stats for a specific team"""
        tracker.register_kill("p1", "TeamA", "p2", "TeamB")
        tracker.register_kill("p3", "TeamA", "p4", "TeamC")
        
        stats = tracker.get_team_stats("TeamA")
        
        assert stats is not None
        assert stats['name'] == 'TeamA'
        assert stats['total_kills'] == 2
        assert stats['alive'] == 2
        assert stats['dead'] == 0
    
    def test_get_team_stats_nonexistent_team(self, tracker):
        """Test getting stats for non-existent team"""
        stats = tracker.get_team_stats("NonExistentTeam")
        assert stats is None
    
    def test_get_all_teams_stats(self, tracker):
        """Test getting stats for all teams"""
        tracker.register_kill("p1", "TeamA", "p2", "TeamB")
        tracker.register_kill("p3", "TeamC", "p4", "TeamD")
        
        all_stats = tracker.get_all_teams_stats()
        
        assert len(all_stats) == 4
        assert all(isinstance(stat, dict) for stat in all_stats)
    
    # ========================================================================
    # Test: Player Counts
    # ========================================================================
    
    def test_alive_count(self, tracker):
        """Test counting alive players"""
        tracker.register_kill("p1", "TeamA", "p2", "TeamB")
        tracker.register_kill("p3", "TeamA", "p4", "TeamB")
        
        # 2 players killed, 2 killers alive
        assert tracker.get_total_alive() == 2
    
    def test_dead_count(self, tracker):
        """Test counting dead players"""
        tracker.register_kill("p1", "TeamA", "p2", "TeamB")
        tracker.register_kill("p3", "TeamA", "p4", "TeamB")
        
        assert tracker.get_total_dead() == 2
    
    def test_active_teams_count(self, tracker):
        """Test counting teams with alive players"""
        tracker.register_kill("p1", "TeamA", "p2", "TeamB")
        tracker.register_kill("p3", "TeamC", "p4", "TeamD")
        
        # TeamA and TeamC have alive players (the killers)
        active = tracker.get_active_teams_count()
        assert active >= 2
    
    # ========================================================================
    # Test: Leaderboard
    # ========================================================================
    
    def test_leaderboard_ordering(self, tracker):
        """Test leaderboard is ordered by kills"""
        tracker.register_kill("player1", "TeamA", "victim1", "TeamB")
        tracker.register_kill("player1", "TeamA", "victim2", "TeamB")
        tracker.register_kill("player1", "TeamA", "victim3", "TeamB")
        tracker.register_kill("player2", "TeamC", "victim4", "TeamD")
        
        leaderboard = tracker.get_leaderboard(limit=10)
        
        assert len(leaderboard) >= 2
        # player1 should be first with 3 kills
        assert leaderboard[0]['name'] == 'player1'
        assert leaderboard[0]['kills'] == 3
    
    def test_leaderboard_limit(self, tracker):
        """Test leaderboard respects limit parameter"""
        for i in range(15):
            tracker.register_kill(f"killer{i}", "TeamA", f"victim{i}", "TeamB")
        
        leaderboard = tracker.get_leaderboard(limit=5)
        assert len(leaderboard) <= 5
    
    # ========================================================================
    # Test: Match Summary
    # ========================================================================
    
    def test_match_summary(self, tracker):
        """Test getting complete match summary"""
        tracker.register_kill("p1", "TeamA", "p2", "TeamB")
        tracker.register_kill("p3", "TeamA", "p4", "TeamC")
        
        summary = tracker.get_match_summary()
        
        assert 'total_kills' in summary
        assert 'total_players' in summary
        assert 'alive_players' in summary
        assert 'dead_players' in summary
        assert 'active_teams' in summary
        assert 'teams' in summary
        assert 'leaderboard' in summary
        
        assert summary['total_kills'] == 2
        assert summary['dead_players'] == 2
    
    # ========================================================================
    # Test: Export to Dict
    # ========================================================================
    
    def test_export_to_dict(self, tracker):
        """Test exporting tracker state to dictionary"""
        tracker.register_kill("p1", "TeamA", "p2", "TeamB")
        
        exported = tracker.export_to_dict()
        
        assert 'teams' in exported
        assert 'kills_history' in exported
        assert 'total_players' in exported
        assert exported['total_players'] == 100
    
    # ========================================================================
    # Test: Edge Cases
    # ========================================================================
    
    def test_same_player_multiple_kills(self, tracker):
        """Test same player getting multiple kills"""
        tracker.register_kill("killer", "TeamA", "victim1", "TeamB")
        tracker.register_kill("killer", "TeamA", "victim2", "TeamB")
        tracker.register_kill("killer", "TeamA", "victim3", "TeamB")
        
        team_a = tracker.teams['TeamA']
        killer = team_a.players['killer']
        
        assert killer.kills == 3
        assert killer.deaths == 0
    
    def test_player_killed_after_killing(self, tracker):
        """Test player who killed someone then gets killed"""
        tracker.register_kill("player1", "TeamA", "player2", "TeamB")
        tracker.register_kill("player3", "TeamC", "player1", "TeamA")
        
        team_a = tracker.teams['TeamA']
        player1 = team_a.players['player1']
        
        assert player1.kills == 1
        assert player1.deaths == 1
        assert player1.alive is False
    
    def test_team_elimination(self, tracker):
        """Test when all players from a team are eliminated"""
        # Create team with 3 players
        tracker.register_kill("p1", "TeamA", "victim1", "TeamB")
        tracker.register_kill("p2", "TeamA", "victim2", "TeamB")
        tracker.register_kill("p3", "TeamA", "victim3", "TeamB")
        
        # Kill all TeamA players
        tracker.register_kill("enemy1", "TeamC", "p1", "TeamA")
        tracker.register_kill("enemy2", "TeamC", "p2", "TeamA")
        tracker.register_kill("enemy3", "TeamC", "p3", "TeamA")
        
        team_a = tracker.teams['TeamA']
        assert team_a.alive_count() == 0
        assert team_a.dead_count() == 3
    
    def test_empty_tracker_stats(self, tracker):
        """Test getting stats from empty tracker"""
        assert tracker.get_total_alive() == 0
        assert tracker.get_total_dead() == 0
        assert tracker.get_active_teams_count() == 0
        assert tracker.get_leaderboard() == []
        
        summary = tracker.get_match_summary()
        assert summary['total_kills'] == 0


# ============================================================================
# Test Team and Player Classes
# ============================================================================

class TestTeamClass:
    """Test Team dataclass"""
    
    def test_team_alive_count(self):
        """Test Team.alive_count()"""
        team = Team(name="TestTeam")
        team.players['p1'] = Player(name='p1', team='TestTeam', alive=True)
        team.players['p2'] = Player(name='p2', team='TestTeam', alive=False)
        team.players['p3'] = Player(name='p3', team='TestTeam', alive=True)
        
        assert team.alive_count() == 2
    
    def test_team_dead_count(self):
        """Test Team.dead_count()"""
        team = Team(name="TestTeam")
        team.players['p1'] = Player(name='p1', team='TestTeam', alive=True)
        team.players['p2'] = Player(name='p2', team='TestTeam', alive=False)
        team.players['p3'] = Player(name='p3', team='TestTeam', alive=False)
        
        assert team.dead_count() == 2
    
    def test_team_get_alive_players(self):
        """Test Team.get_alive_players()"""
        team = Team(name="TestTeam")
        team.players['p1'] = Player(name='p1', team='TestTeam', alive=True)
        team.players['p2'] = Player(name='p2', team='TestTeam', alive=False)
        
        alive = team.get_alive_players()
        assert len(alive) == 1
        assert alive[0].name == 'p1'
    
    def test_team_get_dead_players(self):
        """Test Team.get_dead_players()"""
        team = Team(name="TestTeam")
        team.players['p1'] = Player(name='p1', team='TestTeam', alive=True)
        team.players['p2'] = Player(name='p2', team='TestTeam', alive=False)
        
        dead = team.get_dead_players()
        assert len(dead) == 1
        assert dead[0].name == 'p2'
