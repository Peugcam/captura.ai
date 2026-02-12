"""
Unit Tests: BrazilianKillParser
================================

Tests the kill feed parser for Brazilian GTA Battle Royale format.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from src.brazilian_kill_parser import BrazilianKillParser


class TestBrazilianKillParser:
    """Test suite for BrazilianKillParser"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return BrazilianKillParser()
    
    # ========================================================================
    # Test: Standard Format Parsing
    # ========================================================================
    
    def test_parse_standard_format_with_distance(self, parser):
        """Test parsing standard format: TEAM KILLER MATOU ICON TEAM VICTIM DISTANCE"""
        text = "PPP almeida99 MATOU 💀 LLL pikachu1337 120m"
        
        result = parser.parse_kill_line(text)
        
        assert result is not None
        assert result['killer'] == 'almeida99'
        assert result['killer_team'] == 'PPP'
        assert result['victim'] == 'pikachu1337'
        assert result['victim_team'] == 'LLL'
        assert result['distance'] == '120m'
        assert result['keyword'] == 'MATOU'
        assert result['confirmed'] is True
    
    def test_parse_without_distance(self, parser):
        """Test parsing without distance"""
        text = "AAA jogador123 ELIMINOU 🔫 BBB player456"
        
        result = parser.parse_kill_line(text)
        
        assert result is not None
        assert result['killer'] == 'jogador123'
        assert result['killer_team'] == 'AAA'
        assert result['victim'] == 'player456'
        assert result['victim_team'] == 'BBB'
        assert result['distance'] is None
        assert result['keyword'] == 'ELIMINOU'
    
    def test_parse_without_teams(self, parser):
        """Test parsing without team tags"""
        text = "killer123 MATOU victim456 50m"
        
        result = parser.parse_kill_line(text)
        
        assert result is not None
        assert result['killer'] == 'killer123'
        assert result['victim'] == 'victim456'
        # Should default to 'Unknown' when no team detected
        assert result['killer_team'] in ['Unknown', 'killer123']
        assert result['distance'] == '50m'
    
    # ========================================================================
    # Test: Different Keywords
    # ========================================================================
    
    def test_parse_with_matou_keyword(self, parser):
        """Test MATOU keyword (Portuguese)"""
        text = "PPP player1 MATOU LLL player2"
        result = parser.parse_kill_line(text)
        
        assert result is not None
        assert result['keyword'] == 'MATOU'
    
    def test_parse_with_eliminou_keyword(self, parser):
        """Test ELIMINOU keyword (Portuguese)"""
        text = "AAA player1 ELIMINOU BBB player2"
        result = parser.parse_kill_line(text)
        
        assert result is not None
        assert result['keyword'] == 'ELIMINOU'
    
    def test_parse_with_killed_keyword(self, parser):
        """Test KILLED keyword (English)"""
        text = "CCC sniper99 KILLED DDD target777"
        result = parser.parse_kill_line(text)
        
        assert result is not None
        assert result['keyword'] == 'KILLED'
    
    def test_parse_with_eliminated_keyword(self, parser):
        """Test ELIMINATED keyword (English)"""
        text = "EEE player1 ELIMINATED FFF player2 100m"
        result = parser.parse_kill_line(text)
        
        assert result is not None
        assert result['keyword'] == 'ELIMINATED'
    
    # ========================================================================
    # Test: Invalid Input Handling
    # ========================================================================
    
    def test_parse_empty_string(self, parser):
        """Test parsing empty string"""
        result = parser.parse_kill_line("")
        assert result is None
    
    def test_parse_whitespace_only(self, parser):
        """Test parsing whitespace only"""
        result = parser.parse_kill_line("   \n\t  ")
        assert result is None
    
    def test_parse_no_kill_keyword(self, parser):
        """Test parsing line without kill keyword"""
        text = "PPP almeida99 did something to LLL pikachu1337"
        result = parser.parse_kill_line(text)
        assert result is None
    
    def test_parse_too_short(self, parser):
        """Test parsing line that's too short"""
        text = "MATOU player"
        result = parser.parse_kill_line(text)
        assert result is None
    
    def test_parse_invalid_format(self, parser):
        """Test parsing completely invalid format"""
        text = "This is not a kill feed line at all"
        result = parser.parse_kill_line(text)
        assert result is None
    
    # ========================================================================
    # Test: Edge Cases
    # ========================================================================
    
    def test_parse_with_special_characters_in_names(self, parser):
        """Test parsing with special characters in player names"""
        text = "PPP player_123 MATOU LLL victim-456 75m"
        result = parser.parse_kill_line(text)
        
        assert result is not None
        assert 'player_123' in result['killer'] or 'player' in result['killer']
        assert 'victim-456' in result['victim'] or 'victim' in result['victim']
    
    def test_parse_case_insensitive_keyword(self, parser):
        """Test that keyword detection is case-insensitive"""
        text = "PPP player1 matou LLL player2"
        result = parser.parse_kill_line(text)
        
        # Should still detect 'matou' even though it's lowercase
        assert result is not None
    
    def test_parse_with_multiple_icons(self, parser):
        """Test parsing with multiple emoji icons"""
        text = "PPP killer MATOU 💀🔫💥 LLL victim 200m"
        result = parser.parse_kill_line(text)
        
        assert result is not None
        assert result['killer'] == 'killer'
        assert result['victim'] == 'victim'
    
    # ========================================================================
    # Test: Multiple Lines (Kill Feed Frame)
    # ========================================================================
    
    def test_parse_kill_feed_frame_multiple_kills(self, parser, mock_kill_feed_lines):
        """Test parsing multiple kill lines from a frame"""
        results = parser.parse_kill_feed_frame(mock_kill_feed_lines)
        
        # Should detect at least 4 valid kills (excluding invalid line)
        assert len(results) >= 3
        
        # Verify first kill
        assert results[0]['killer'] == 'almeida99'
        assert results[0]['victim'] == 'pikachu1337'
    
    def test_parse_kill_feed_frame_empty_list(self, parser):
        """Test parsing empty kill feed"""
        results = parser.parse_kill_feed_frame([])
        assert results == []
    
    def test_parse_kill_feed_frame_all_invalid(self, parser):
        """Test parsing kill feed with all invalid lines"""
        invalid_lines = [
            "No kill here",
            "Just some text",
            "Another invalid line"
        ]
        results = parser.parse_kill_feed_frame(invalid_lines)
        assert results == []
    
    def test_parse_kill_feed_frame_mixed_valid_invalid(self, parser):
        """Test parsing kill feed with mix of valid and invalid lines"""
        mixed_lines = [
            "PPP player1 MATOU LLL player2",
            "Invalid line",
            "AAA player3 KILLED BBB player4 100m",
            "Another invalid",
            "CCC player5 ELIMINOU DDD player6"
        ]
        results = parser.parse_kill_feed_frame(mixed_lines)
        
        # Should detect exactly 3 valid kills
        assert len(results) == 3
    
    # ========================================================================
    # Test: Distance Parsing
    # ========================================================================
    
    def test_parse_various_distances(self, parser):
        """Test parsing various distance formats"""
        test_cases = [
            ("PPP p1 MATOU LLL p2 50m", "50m"),
            ("PPP p1 MATOU LLL p2 150m", "150m"),
            ("PPP p1 MATOU LLL p2 999m", "999m"),
        ]
        
        for text, expected_distance in test_cases:
            result = parser.parse_kill_line(text)
            assert result is not None
            assert result['distance'] == expected_distance
    
    # ========================================================================
    # Test: Team Pattern Matching
    # ========================================================================
    
    def test_parse_various_team_formats(self, parser):
        """Test parsing various team tag formats"""
        test_cases = [
            ("AA p1 MATOU BB p2", "AA", "BB"),  # 2 letters
            ("AAA p1 MATOU BBB p2", "AAA", "BBB"),  # 3 letters
            ("AAAA p1 MATOU BBBB p2", "AAAA", "BBBB"),  # 4 letters
        ]
        
        for text, expected_killer_team, expected_victim_team in test_cases:
            result = parser.parse_kill_line(text)
            assert result is not None
            assert result['killer_team'] == expected_killer_team
            assert result['victim_team'] == expected_victim_team


# ============================================================================
# Integration-style tests (testing parser with realistic data)
# ============================================================================

class TestBrazilianKillParserIntegration:
    """Integration tests with realistic kill feed data"""
    
    @pytest.fixture
    def parser(self):
        return BrazilianKillParser()
    
    def test_realistic_gta_kill_feed(self, parser):
        """Test with realistic GTA BR kill feed data"""
        realistic_feed = [
            "PPP almeida99 MATOU 💀 LLL pikachu1337 120m",
            "AAA jogador123 ELIMINOU 🔫 BBB player456 85m",
            "CCC sniper99 KILLED 💥 DDD target777",
            "EEE killer MATOU FFF victim 200m",
            "GGG pro_player ELIMINOU HHH noob_123 15m"
        ]
        
        results = parser.parse_kill_feed_frame(realistic_feed)
        
        assert len(results) == 5
        
        # Verify all kills have required fields
        for kill in results:
            assert 'killer' in kill
            assert 'victim' in kill
            assert 'killer_team' in kill
            assert 'victim_team' in kill
            assert 'keyword' in kill
            assert 'confirmed' in kill
            assert kill['confirmed'] is True
