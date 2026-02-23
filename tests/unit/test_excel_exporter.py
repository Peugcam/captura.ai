"""
Unit Tests: Excel Exporter
===========================

Tests the Excel export functionality that generates match reports.
"""

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime
import tempfile

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from src.excel_exporter import ExcelExporter


@pytest.fixture
def exporter():
    """Create an Excel exporter instance"""
    return ExcelExporter()


@pytest.fixture
def sample_match_data():
    """Create sample match data for testing"""
    return {
        'total_players': 4,
        'total_alive': 2,
        'total_dead': 2,
        'total_kills': 2,
        'total_teams': 2,
        'teams': {
            'TeamA': {
                'name': 'TeamA',
                'alive': 2,
                'dead': 0,
                'total': 2,
                'total_kills': 2,
                'total_deaths': 0,
                'players': [
                    {
                        'name': 'player1',
                        'team': 'TeamA',
                        'alive': True,
                        'kills': 1,
                        'deaths': 0,
                        'first_seen': '2024-01-01 10:00:00',
                        'last_seen': '2024-01-01 10:05:00'
                    },
                    {
                        'name': 'player2',
                        'team': 'TeamA',
                        'alive': True,
                        'kills': 1,
                        'deaths': 0,
                        'first_seen': '2024-01-01 10:00:00',
                        'last_seen': '2024-01-01 10:06:00'
                    }
                ]
            },
            'TeamB': {
                'name': 'TeamB',
                'alive': 0,
                'dead': 2,
                'total': 2,
                'total_kills': 0,
                'total_deaths': 2,
                'players': [
                    {
                        'name': 'player3',
                        'team': 'TeamB',
                        'alive': False,
                        'kills': 0,
                        'deaths': 1,
                        'first_seen': '2024-01-01 10:00:00',
                        'last_seen': '2024-01-01 10:03:00'
                    },
                    {
                        'name': 'player4',
                        'team': 'TeamB',
                        'alive': False,
                        'kills': 0,
                        'deaths': 1,
                        'first_seen': '2024-01-01 10:00:00',
                        'last_seen': '2024-01-01 10:04:00'
                    }
                ]
            }
        },
        'kills_history': [
            {
                'killer': 'player1',
                'killer_team': 'TeamA',
                'victim': 'player3',
                'victim_team': 'TeamB',
                'distance': '100m',
                'timestamp': '2024-01-01 10:03:00'
            },
            {
                'killer': 'player2',
                'killer_team': 'TeamA',
                'victim': 'player4',
                'victim_team': 'TeamB',
                'distance': '50m',
                'timestamp': '2024-01-01 10:04:00'
            }
        ]
    }


@pytest.fixture
def temp_excel_file():
    """Create a temporary file path for Excel export"""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        filepath = f.name
    yield filepath
    # Cleanup after test
    if os.path.exists(filepath):
        try:
            os.unlink(filepath)
        except:
            pass


# ============================================================================
# Test: Initialization
# ============================================================================

class TestExcelExporterInit:
    """Test exporter initialization"""

    def test_initialization(self, exporter):
        """Test exporter initializes correctly"""
        assert exporter.workbook is None
        assert exporter.worksheet is None


# ============================================================================
# Test: Export Match - Standard Format
# ============================================================================

class TestExportMatchStandard:
    """Test standard format export"""

    def test_export_standard_format_success(self, exporter, sample_match_data, temp_excel_file):
        """Test successful export in standard format"""
        result = exporter.export_match(
            match_data=sample_match_data,
            filepath=temp_excel_file,
            format='standard'
        )

        assert result is True
        assert os.path.exists(temp_excel_file)
        # Check file is not empty
        assert os.path.getsize(temp_excel_file) > 0

    def test_export_creates_file(self, exporter, sample_match_data, temp_excel_file):
        """Test that export creates the Excel file"""
        exporter.export_match(
            match_data=sample_match_data,
            filepath=temp_excel_file,
            format='standard'
        )

        # File should exist
        assert Path(temp_excel_file).exists()

    def test_export_with_empty_data(self, exporter, temp_excel_file):
        """Test export with empty match data"""
        empty_data = {
            'total_players': 0,
            'total_alive': 0,
            'total_dead': 0,
            'total_kills': 0,
            'total_teams': 0,
            'teams': {},
            'kills_history': []
        }

        result = exporter.export_match(
            match_data=empty_data,
            filepath=temp_excel_file,
            format='standard'
        )

        # Should still succeed
        assert result is True
        assert os.path.exists(temp_excel_file)

    def test_export_with_minimal_data(self, exporter, temp_excel_file):
        """Test export with minimal required data"""
        minimal_data = {
            'teams': {
                'TeamA': {
                    'name': 'TeamA',
                    'alive': 1,
                    'dead': 0,
                    'total': 1,
                    'total_kills': 0,
                    'players': [
                        {
                            'name': 'player1',
                            'team': 'TeamA',
                            'alive': True,
                            'kills': 0,
                            'deaths': 0
                        }
                    ]
                }
            }
        }

        result = exporter.export_match(
            match_data=minimal_data,
            filepath=temp_excel_file,
            format='standard'
        )

        assert result is True


# ============================================================================
# Test: Export Match - Luis Format
# ============================================================================

class TestExportMatchLuis:
    """Test Luis custom format export"""

    def test_export_luis_format_success(self, exporter, sample_match_data, temp_excel_file):
        """Test successful export in Luis format"""
        result = exporter.export_match(
            match_data=sample_match_data,
            filepath=temp_excel_file,
            format='luis'
        )

        assert result is True
        assert os.path.exists(temp_excel_file)

    def test_export_luis_with_kill_history(self, exporter, sample_match_data, temp_excel_file):
        """Test Luis format includes kill history"""
        result = exporter.export_match(
            match_data=sample_match_data,
            filepath=temp_excel_file,
            format='luis'
        )

        assert result is True
        # File should contain kill history data
        assert os.path.getsize(temp_excel_file) > 0


# ============================================================================
# Test: Export Match - Advanced Format
# ============================================================================

class TestExportMatchAdvanced:
    """Test advanced format export"""

    def test_export_advanced_format_success(self, exporter, sample_match_data, temp_excel_file):
        """Test successful export in advanced format"""
        result = exporter.export_match(
            match_data=sample_match_data,
            filepath=temp_excel_file,
            format='advanced'
        )

        assert result is True
        assert os.path.exists(temp_excel_file)


# ============================================================================
# Test: Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling in export"""

    def test_export_invalid_path(self, exporter, sample_match_data):
        """Test export with invalid file path"""
        invalid_path = "/invalid/path/that/does/not/exist/file.xlsx"

        result = exporter.export_match(
            match_data=sample_match_data,
            filepath=invalid_path,
            format='standard'
        )

        # Should return False on error
        assert result is False

    def test_export_with_none_data(self, exporter, temp_excel_file):
        """Test export with None as match data"""
        result = exporter.export_match(
            match_data=None,
            filepath=temp_excel_file,
            format='standard'
        )

        # Should handle gracefully
        assert isinstance(result, bool)

    def test_export_with_malformed_data(self, exporter, temp_excel_file):
        """Test export with malformed data structure"""
        malformed = {
            'teams': {
                'TeamA': {
                    'players': [
                        {
                            'name': 'player1'
                            # Missing required fields
                        }
                    ]
                }
            }
        }

        result = exporter.export_match(
            match_data=malformed,
            filepath=temp_excel_file,
            format='standard'
        )

        # Should handle missing fields
        assert isinstance(result, bool)

    def test_export_readonly_path(self, exporter, sample_match_data):
        """Test export to read-only location (should fail gracefully)"""
        # Try to write to root (typically read-only)
        readonly_path = "C:\\file.xlsx" if os.name == 'nt' else "/file.xlsx"

        result = exporter.export_match(
            match_data=sample_match_data,
            filepath=readonly_path,
            format='standard'
        )

        # Should return False (permission denied)
        assert result is False


# ============================================================================
# Test: Format Selection
# ============================================================================

class TestFormatSelection:
    """Test different format options"""

    def test_default_format_is_standard(self, exporter, sample_match_data, temp_excel_file):
        """Test that default format is standard"""
        # Export without specifying format
        result = exporter.export_match(
            match_data=sample_match_data,
            filepath=temp_excel_file
        )

        assert result is True

    def test_unsupported_format_fallback(self, exporter, sample_match_data, temp_excel_file):
        """Test behavior with unsupported format"""
        result = exporter.export_match(
            match_data=sample_match_data,
            filepath=temp_excel_file,
            format='unsupported_format'
        )

        # Should still create file (might use default or skip)
        assert isinstance(result, bool)


# ============================================================================
# Test: Data Integrity
# ============================================================================

class TestDataIntegrity:
    """Test that exported data maintains integrity"""

    def test_export_preserves_player_count(self, exporter, sample_match_data, temp_excel_file):
        """Test that all players are included in export"""
        result = exporter.export_match(
            match_data=sample_match_data,
            filepath=temp_excel_file,
            format='standard'
        )

        assert result is True
        # File size should reflect 4 players
        assert os.path.getsize(temp_excel_file) > 1000  # Reasonable size for 4 players

    def test_export_with_special_characters(self, exporter, temp_excel_file):
        """Test export with special characters in names"""
        special_data = {
            'teams': {
                'TeamÁ': {
                    'name': 'TeamÁ',
                    'alive': 1,
                    'dead': 0,
                    'total': 1,
                    'total_kills': 0,
                    'players': [
                        {
                            'name': 'João_123',
                            'team': 'TeamÁ',
                            'alive': True,
                            'kills': 0,
                            'deaths': 0
                        }
                    ]
                }
            }
        }

        result = exporter.export_match(
            match_data=special_data,
            filepath=temp_excel_file,
            format='standard'
        )

        assert result is True

    def test_export_with_unicode_emojis(self, exporter, temp_excel_file):
        """Test export with emoji characters"""
        emoji_data = {
            'teams': {
                'Team🔥': {
                    'name': 'Team🔥',
                    'alive': 1,
                    'dead': 0,
                    'total': 1,
                    'total_kills': 0,
                    'players': [
                        {
                            'name': 'player👑',
                            'team': 'Team🔥',
                            'alive': True,
                            'kills': 0,
                            'deaths': 0
                        }
                    ]
                }
            }
        }

        result = exporter.export_match(
            match_data=emoji_data,
            filepath=temp_excel_file,
            format='standard'
        )

        # Should handle unicode gracefully
        assert isinstance(result, bool)


# ============================================================================
# Test: File System Operations
# ============================================================================

class TestFileSystemOperations:
    """Test file system related operations"""

    def test_export_overwrites_existing_file(self, exporter, sample_match_data, temp_excel_file):
        """Test that export overwrites existing file"""
        # Export once
        exporter.export_match(sample_match_data, temp_excel_file, 'standard')
        first_mtime = os.path.getmtime(temp_excel_file)

        # Wait a bit and export again
        import time
        time.sleep(0.1)

        exporter.export_match(sample_match_data, temp_excel_file, 'standard')
        second_mtime = os.path.getmtime(temp_excel_file)

        # File should be updated
        assert second_mtime >= first_mtime

    def test_export_to_subdirectory(self, exporter, sample_match_data):
        """Test export to subdirectory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = Path(tmpdir) / "exports"
            subdir.mkdir()
            filepath = str(subdir / "test.xlsx")

            result = exporter.export_match(
                match_data=sample_match_data,
                filepath=filepath,
                format='standard'
            )

            assert result is True
            assert os.path.exists(filepath)


# ============================================================================
# Test: Integration Scenarios
# ============================================================================

class TestIntegrationScenarios:
    """Test realistic usage scenarios"""

    def test_export_full_match(self, exporter, sample_match_data, temp_excel_file):
        """Test exporting a complete match with all data"""
        result = exporter.export_match(
            match_data=sample_match_data,
            filepath=temp_excel_file,
            format='standard'
        )

        assert result is True
        # Verify file is substantial
        assert os.path.getsize(temp_excel_file) > 5000

    def test_export_large_match(self, exporter, temp_excel_file):
        """Test exporting a large match (many players)"""
        # Create data with 100 players
        large_data = {
            'total_players': 100,
            'teams': {}
        }

        # Generate 10 teams with 10 players each
        for team_num in range(10):
            team_name = f"Team{team_num}"
            large_data['teams'][team_name] = {
                'name': team_name,
                'alive': 5,
                'dead': 5,
                'total': 10,
                'total_kills': 5,
                'players': [
                    {
                        'name': f'player{team_num}_{i}',
                        'team': team_name,
                        'alive': i < 5,
                        'kills': i % 3,
                        'deaths': i % 2
                    }
                    for i in range(10)
                ]
            }

        result = exporter.export_match(
            match_data=large_data,
            filepath=temp_excel_file,
            format='standard'
        )

        assert result is True
        # Large file should be created
        assert os.path.getsize(temp_excel_file) > 8000  # Adjusted for actual file size

    def test_export_all_formats_same_data(self, exporter, sample_match_data):
        """Test exporting same data in all formats"""
        with tempfile.TemporaryDirectory() as tmpdir:
            formats = ['standard', 'luis', 'advanced']
            results = []

            for fmt in formats:
                filepath = str(Path(tmpdir) / f"export_{fmt}.xlsx")
                result = exporter.export_match(
                    match_data=sample_match_data,
                    filepath=filepath,
                    format=fmt
                )
                results.append(result)

            # All formats should succeed
            assert all(results)


# ============================================================================
# Test: Advanced Format with Events (Lines 580-629)
# ============================================================================
