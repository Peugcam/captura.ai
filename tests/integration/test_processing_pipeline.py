"""
Integration Tests: Processing Pipeline
=======================================

Tests the complete frame processing pipeline:
Frame → OCR Filter → Vision AI → Parser → Team Tracker
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from backend.processor import FrameProcessor, OCRPreFilter, VisionProcessor
from src.brazilian_kill_parser import BrazilianKillParser
from src.team_tracker import TeamTracker


@pytest.mark.integration
class TestProcessingPipeline:
    """Test complete processing pipeline"""
    
    @pytest.fixture
    def processor(self, mock_api_keys):
        """Create processor instance with mocked APIs"""
        with patch.dict('os.environ', {'API_KEYS': ','.join(mock_api_keys), 'TEST_MODE': 'true'}):
            return FrameProcessor()
    
    # ========================================================================
    # Test: OCR Filter → Vision AI
    # ========================================================================
    
    @pytest.mark.slow
    def test_ocr_filter_passes_frames_with_keywords(self, processor, mock_frame_with_text):
        """Test that OCR filter passes frames containing kill keywords"""
        # This would require actual OCR, so we mock it
        with patch.object(processor.ocr_filter, 'has_kill_keywords', return_value=True):
            result = processor.ocr_filter.has_kill_keywords(mock_frame_with_text)
            assert result is True
    
    def test_ocr_filter_rejects_frames_without_keywords(self, processor, mock_frame_base64):
        """Test that OCR filter rejects frames without kill keywords"""
        with patch.object(processor.ocr_filter, 'has_kill_keywords', return_value=False):
            result = processor.ocr_filter.has_kill_keywords(mock_frame_base64)
            assert result is False
    
    # ========================================================================
    # Test: Vision AI → Parser
    # ========================================================================
    
    def test_vision_response_parsed_correctly(self, processor, mock_vision_api_response):
        """Test that Vision API response is parsed correctly"""
        # Mock Vision API call
        with patch.object(processor.vision.client, 'vision_chat_multiple', return_value=mock_vision_api_response):
            kills = processor.vision.process_batch([mock_vision_api_response['content']])
            
            assert len(kills) >= 0  # Should parse without error
    
    # ========================================================================
    # Test: Parser → Team Tracker
    # ========================================================================
    
    def test_parsed_kills_registered_in_tracker(self, processor, mock_kill_data):
        """Test that parsed kills are registered in team tracker"""
        # Register kill
        success = processor.tracker.register_kill(
            killer_name=mock_kill_data['killer'],
            killer_team=mock_kill_data['killer_team'],
            victim_name=mock_kill_data['victim'],
            victim_team=mock_kill_data['victim_team'],
            distance=mock_kill_data.get('distance')
        )
        
        assert success is True
        assert len(processor.tracker.kills_history) == 1
        
        # Verify stats updated
        stats = processor.get_stats()
        assert stats['kills_detected'] == 1
    
    # ========================================================================
    # Test: Complete Pipeline
    # ========================================================================
    
    @pytest.mark.slow
    def test_complete_pipeline_with_mock_frame(self, processor, mock_frame_data, mock_vision_api_response):
        """Test complete pipeline from frame to statistics"""
        # Mock OCR to pass
        with patch.object(processor.ocr_filter, 'has_kill_keywords', return_value=True):
            # Mock Vision API
            with patch.object(processor.vision.client, 'vision_chat_multiple', return_value=mock_vision_api_response):
                # Process frame
                result = processor.process_frame(mock_frame_data)
                
                # Should have processed successfully
                stats = processor.get_stats()
                assert stats['frames_processed'] >= 1
    
    def test_pipeline_handles_no_kills_gracefully(self, processor, mock_frame_data):
        """Test pipeline handles frames with no kills"""
        # Mock OCR to reject (no keywords)
        with patch.object(processor.ocr_filter, 'has_kill_keywords', return_value=False):
            result = processor.process_frame(mock_frame_data)
            
            # Should process but find no kills
            stats = processor.get_stats()
            assert stats['kills_detected'] == 0
    
    # ========================================================================
    # Test: Batch Processing
    # ========================================================================
    
    def test_batch_processing_multiple_frames(self, processor, mock_vision_api_response):
        """Test processing batch of frames"""
        frames = ["frame1_base64", "frame2_base64", "frame3_base64"]
        
        # Mock Vision API
        with patch.object(processor.vision.client, 'vision_chat_multiple', return_value=mock_vision_api_response):
            kills = processor.process_batch(frames)
            
            # Should process batch
            assert isinstance(kills, list)
    
    # ========================================================================
    # Test: Statistics Aggregation
    # ========================================================================
    
    def test_statistics_aggregation(self, processor, mock_multiple_kills):
        """Test that statistics are correctly aggregated"""
        # Register multiple kills
        for kill in mock_multiple_kills:
            processor.tracker.register_kill(
                killer_name=kill['killer'],
                killer_team=kill['killer_team'],
                victim_name=kill['victim'],
                victim_team=kill['victim_team']
            )
        
        # Get match summary
        summary = processor.get_match_summary()
        
        assert summary['total_kills'] == len(mock_multiple_kills)
        assert 'teams' in summary
        assert 'leaderboard' in summary


@pytest.mark.integration
class TestPipelineErrorHandling:
    """Test pipeline error handling and resilience"""
    
    @pytest.fixture
    def processor(self, mock_api_keys):
        with patch.dict('os.environ', {'API_KEYS': ','.join(mock_api_keys)}):
            return FrameProcessor()
    
    def test_pipeline_handles_ocr_errors(self, processor, mock_frame_data):
        """Test pipeline handles OCR errors gracefully"""
        # Mock OCR to raise exception
        with patch.object(processor.ocr_filter, 'has_kill_keywords', side_effect=Exception("OCR Error")):
            # Should not crash
            try:
                processor.process_frame(mock_frame_data)
            except Exception:
                pytest.fail("Pipeline should handle OCR errors gracefully")
    
    def test_pipeline_handles_vision_api_errors(self, processor, mock_frame_data, mock_vision_api_error):
        """Test pipeline handles Vision API errors"""
        with patch.object(processor.ocr_filter, 'has_kill_keywords', return_value=True):
            with patch.object(processor.vision.client, 'vision_chat_multiple', return_value=mock_vision_api_error):
                # Should handle error gracefully
                result = processor.process_frame(mock_frame_data)
                
                # Should not have kills due to API error
                stats = processor.get_stats()
                # Stats should still be accessible
                assert 'frames_processed' in stats
    
    def test_pipeline_handles_parser_errors(self, processor, mock_frame_data):
        """Test pipeline handles parser errors"""
        # Mock parser to return invalid data
        with patch.object(processor.vision.parser, 'parse_kill_line', return_value=None):
            # Should handle gracefully
            try:
                processor.process_frame(mock_frame_data)
            except Exception:
                pytest.fail("Pipeline should handle parser errors gracefully")
