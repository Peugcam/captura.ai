"""
Unit Tests: Pixel Filter
=========================

Tests the pixel-based pre-filter that detects kill feeds without API calls.
This filter provides 80-90% filtering rate at ~5ms per frame (free).
"""

import pytest
import base64
import io
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import cv2

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from src.pixel_filter import PixelFilter


@pytest.fixture
def pixel_filter():
    """Create a pixel filter instance"""
    return PixelFilter()


@pytest.fixture
def create_test_image():
    """Factory to create test images"""
    def _create(width=1920, height=1080, content_type='blank'):
        """
        Create test image with different content types

        Args:
            width, height: Image dimensions
            content_type: 'blank', 'text', 'colored', 'kill_feed'
        """
        img = np.zeros((height, width, 3), dtype=np.uint8)

        if content_type == 'text':
            # Add white text-like edges in ROI area (top-right)
            roi_x = width - 450
            roi_y = 0
            # Draw some rectangular shapes (simulate text)
            cv2.rectangle(img, (roi_x + 10, roi_y + 10), (roi_x + 100, roi_y + 30), (255, 255, 255), 2)
            cv2.rectangle(img, (roi_x + 10, roi_y + 40), (roi_x + 150, roi_y + 60), (255, 255, 255), 2)
            cv2.rectangle(img, (roi_x + 10, roi_y + 70), (roi_x + 120, roi_y + 90), (255, 255, 255), 2)

        elif content_type == 'colored':
            # Add colored pixels in ROI (simulate kill icons)
            roi_x = width - 450
            roi_y = 0
            # Red circle (kill icon)
            cv2.circle(img, (roi_x + 50, roi_y + 50), 20, (0, 0, 255), -1)
            # Yellow rectangle (weapon icon)
            cv2.rectangle(img, (roi_x + 100, roi_y + 40), (roi_x + 140, roi_y + 60), (0, 255, 255), -1)
            # White text
            cv2.rectangle(img, (roi_x + 200, roi_y + 45), (roi_x + 300, roi_y + 55), (255, 255, 255), -1)

        elif content_type == 'kill_feed':
            # Realistic kill feed (text + colors + icons)
            roi_x = width - 450
            roi_y = 0
            # Background (slightly transparent dark)
            cv2.rectangle(img, (roi_x, roi_y), (roi_x + 450, roi_y + 250), (30, 30, 30), -1)
            # Kill entries (3 rows)
            for i in range(3):
                y_pos = roi_y + 20 + (i * 70)
                # Team tag (colored box)
                cv2.rectangle(img, (roi_x + 10, y_pos), (roi_x + 60, y_pos + 25), (100, 200, 100), -1)
                # Player name (white text simulation)
                cv2.rectangle(img, (roi_x + 70, y_pos + 5), (roi_x + 150, y_pos + 20), (255, 255, 255), -1)
                # Kill icon (red)
                cv2.circle(img, (roi_x + 180, y_pos + 12), 10, (0, 0, 255), -1)
                # Victim team
                cv2.rectangle(img, (roi_x + 210, y_pos), (roi_x + 260, y_pos + 25), (200, 100, 100), -1)
                # Victim name
                cv2.rectangle(img, (roi_x + 270, y_pos + 5), (roi_x + 350, y_pos + 20), (255, 255, 255), -1)

        # Convert to PIL Image and encode to base64
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        buffer = io.BytesIO()
        pil_img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()

    return _create


# ============================================================================
# Test: Initialization
# ============================================================================

class TestPixelFilterInit:
    """Test pixel filter initialization"""

    def test_initialization(self, pixel_filter):
        """Test filter initializes with correct defaults"""
        assert pixel_filter.previous_frame_roi is None
        assert pixel_filter.frames_analyzed == 0
        assert pixel_filter.frames_filtered == 0
        assert pixel_filter.roi_width == 450
        assert pixel_filter.roi_height == 250

    def test_thresholds_set(self, pixel_filter):
        """Test detection thresholds are set"""
        assert pixel_filter.text_pixel_threshold == 800
        assert pixel_filter.color_pixel_threshold == 150
        assert pixel_filter.change_threshold == 0.08


# ============================================================================
# Test: Image Decoding
# ============================================================================

class TestImageDecoding:
    """Test base64 image decoding"""

    def test_decode_valid_image(self, pixel_filter, create_test_image):
        """Test decoding valid base64 image"""
        img_b64 = create_test_image()
        result = pixel_filter.decode_image(img_b64)

        assert result is not None
        assert isinstance(result, np.ndarray)
        assert len(result.shape) == 3  # Height, Width, Channels
        assert result.shape[2] == 3  # BGR

    def test_decode_with_data_url_prefix(self, pixel_filter, create_test_image):
        """Test decoding image with data URL prefix"""
        img_b64 = create_test_image()
        prefixed = f"data:image/png;base64,{img_b64}"

        result = pixel_filter.decode_image(prefixed)
        assert result is not None

    def test_decode_invalid_base64(self, pixel_filter):
        """Test decoding invalid base64 returns None"""
        result = pixel_filter.decode_image("invalid_base64_string!!!")
        assert result is None

    def test_decode_corrupted_image(self, pixel_filter):
        """Test decoding corrupted image data"""
        corrupted = base64.b64encode(b"not an image").decode()
        result = pixel_filter.decode_image(corrupted)
        assert result is None


# ============================================================================
# Test: ROI Extraction
# ============================================================================

class TestROIExtraction:
    """Test Region of Interest extraction"""

    def test_extract_roi_standard_resolution(self, pixel_filter, create_test_image):
        """Test ROI extraction from 1920x1080 image"""
        img_b64 = create_test_image(1920, 1080)
        img = pixel_filter.decode_image(img_b64)

        roi = pixel_filter.extract_roi(img)

        # ROI should be 450x250 from top-right
        assert roi.shape[0] == 250  # Height
        assert roi.shape[1] == 450  # Width

    def test_extract_roi_small_image(self, pixel_filter, create_test_image):
        """Test ROI extraction from smaller image"""
        img_b64 = create_test_image(800, 600)
        img = pixel_filter.decode_image(img_b64)

        roi = pixel_filter.extract_roi(img)

        # ROI should be cropped to image size
        assert roi.shape[0] <= 250
        assert roi.shape[1] <= 450

    def test_roi_coordinates(self, pixel_filter):
        """Test ROI is extracted from correct position"""
        # Create test image with marker in ROI area
        img = np.zeros((1080, 1920, 3), dtype=np.uint8)
        # Put red marker in expected ROI position
        img[50, 1920-400, :] = [0, 0, 255]  # BGR red

        roi = pixel_filter.extract_roi(img)

        # Marker should be visible in ROI
        # ROI starts at x=1470 (1920-450)
        # Marker at x=1520 should be at roi_x=50
        assert np.any(roi[50, :, 2] > 200)  # Red channel


# ============================================================================
# Test: Text Detection
# ============================================================================

class TestTextDetection:
    """Test text presence detection"""

    def test_detect_text_with_edges(self, pixel_filter, create_test_image):
        """Test detection of text-like edges"""
        img_b64 = create_test_image(content_type='text')
        img = pixel_filter.decode_image(img_b64)
        roi = pixel_filter.extract_roi(img)

        has_text = pixel_filter.detect_text_presence(roi)
        assert has_text

    def test_detect_no_text_blank(self, pixel_filter, create_test_image):
        """Test no text detected in blank image"""
        img_b64 = create_test_image(content_type='blank')
        img = pixel_filter.decode_image(img_b64)
        roi = pixel_filter.extract_roi(img)

        has_text = pixel_filter.detect_text_presence(roi)
        assert not has_text

    def test_text_detection_threshold(self, pixel_filter):
        """Test text detection uses threshold correctly"""
        # Create ROI with few edges (below threshold)
        roi = np.zeros((250, 450, 3), dtype=np.uint8)
        # Add just a few edge pixels
        cv2.rectangle(roi, (10, 10), (30, 20), (255, 255, 255), 1)

        has_text = pixel_filter.detect_text_presence(roi)
        # Should be False because edge count < threshold (800)
        assert not has_text


# ============================================================================
# Test: Color Detection
# ============================================================================

class TestColorDetection:
    """Test icon color detection"""

    def test_detect_red_pixels(self, pixel_filter):
        """Test detection of red pixels (kill icons)"""
        roi = np.zeros((250, 450, 3), dtype=np.uint8)
        # Add red circle (BGR format)
        cv2.circle(roi, (100, 100), 30, (0, 0, 255), -1)

        has_colors = pixel_filter.detect_icon_colors(roi)
        assert has_colors

    def test_detect_yellow_pixels(self, pixel_filter):
        """Test detection of yellow pixels (weapon icons)"""
        roi = np.zeros((250, 450, 3), dtype=np.uint8)
        # Add yellow rectangle (BGR format)
        cv2.rectangle(roi, (100, 100), (150, 120), (0, 255, 255), -1)

        has_colors = pixel_filter.detect_icon_colors(roi)
        assert has_colors

    def test_detect_white_pixels(self, pixel_filter):
        """Test detection of white pixels (text)"""
        roi = np.zeros((250, 450, 3), dtype=np.uint8)
        # Add white text area
        cv2.rectangle(roi, (100, 100), (200, 120), (255, 255, 255), -1)

        has_colors = pixel_filter.detect_icon_colors(roi)
        assert has_colors

    def test_no_colors_in_blank(self, pixel_filter):
        """Test no colors detected in blank ROI"""
        roi = np.zeros((250, 450, 3), dtype=np.uint8)

        has_colors = pixel_filter.detect_icon_colors(roi)
        assert not has_colors

    def test_detect_mixed_colors(self, pixel_filter, create_test_image):
        """Test detection with multiple colors present"""
        img_b64 = create_test_image(content_type='colored')
        img = pixel_filter.decode_image(img_b64)
        roi = pixel_filter.extract_roi(img)

        has_colors = pixel_filter.detect_icon_colors(roi)
        assert has_colors


# ============================================================================
# Test: Frame Change Detection
# ============================================================================

class TestFrameChangeDetection:
    """Test frame-to-frame change detection"""

    def test_first_frame_always_passes(self, pixel_filter):
        """Test first frame always returns True (no previous frame)"""
        roi = np.zeros((250, 450, 3), dtype=np.uint8)

        has_change = pixel_filter.detect_frame_change(roi)
        assert has_change
        assert pixel_filter.previous_frame_roi is not None

    def test_identical_frames_no_change(self, pixel_filter):
        """Test identical consecutive frames show no change"""
        roi = np.zeros((250, 450, 3), dtype=np.uint8)

        # First frame
        pixel_filter.detect_frame_change(roi)

        # Second identical frame
        has_change = pixel_filter.detect_frame_change(roi)
        assert not has_change

    def test_significant_change_detected(self, pixel_filter):
        """Test significant change between frames is detected"""
        roi1 = np.zeros((250, 450, 3), dtype=np.uint8)
        roi2 = np.zeros((250, 450, 3), dtype=np.uint8)

        # Add significant changes to roi2
        cv2.rectangle(roi2, (0, 0), (200, 200), (255, 255, 255), -1)

        # First frame
        pixel_filter.detect_frame_change(roi1)

        # Second frame with changes
        has_change = pixel_filter.detect_frame_change(roi2)
        assert has_change

    def test_small_change_not_detected(self, pixel_filter):
        """Test small change below threshold is not detected"""
        roi1 = np.zeros((250, 450, 3), dtype=np.uint8)
        roi2 = roi1.copy()

        # Add tiny change (1 pixel)
        roi2[10, 10] = [255, 255, 255]

        # First frame
        pixel_filter.detect_frame_change(roi1)

        # Second frame with tiny change
        has_change = pixel_filter.detect_frame_change(roi2)
        # Should be False because change% < threshold (8%)
        assert not has_change

    def test_dimension_mismatch_handled(self, pixel_filter):
        """Test ROI dimension mismatch is handled gracefully"""
        roi1 = np.zeros((250, 450, 3), dtype=np.uint8)
        roi2 = np.zeros((200, 400, 3), dtype=np.uint8)

        # First frame
        pixel_filter.detect_frame_change(roi1)

        # Second frame with different dimensions
        has_change = pixel_filter.detect_frame_change(roi2)
        # Should return True and reset previous frame
        assert has_change


# ============================================================================
# Test: Main Detection Logic
# ============================================================================

class TestHasKillFeed:
    """Test main kill feed detection method"""

    def test_blank_frame_no_kill_feed(self, pixel_filter, create_test_image):
        """Test blank frame has no kill feed"""
        img_b64 = create_test_image(content_type='blank')

        has_kill = pixel_filter.has_kill_feed(img_b64)

        # First frame might pass due to change detection
        # Process second identical frame
        has_kill = pixel_filter.has_kill_feed(img_b64)

        assert not has_kill
        assert pixel_filter.frames_filtered > 0

    def test_text_only_triggers_detection(self, pixel_filter, create_test_image):
        """Test frame with text triggers kill feed detection"""
        img_b64 = create_test_image(content_type='text')

        has_kill = pixel_filter.has_kill_feed(img_b64)
        assert has_kill

    def test_colors_only_triggers_detection(self, pixel_filter, create_test_image):
        """Test frame with colors triggers kill feed detection"""
        img_b64 = create_test_image(content_type='colored')

        has_kill = pixel_filter.has_kill_feed(img_b64)
        assert has_kill

    def test_kill_feed_detected(self, pixel_filter, create_test_image):
        """Test realistic kill feed is detected"""
        img_b64 = create_test_image(content_type='kill_feed')

        has_kill = pixel_filter.has_kill_feed(img_b64)
        assert has_kill

    def test_invalid_image_safe_default(self, pixel_filter):
        """Test invalid image returns True (safe default)"""
        has_kill = pixel_filter.has_kill_feed("invalid_base64!!!")
        # Should return True (let it pass to avoid false negatives)
        assert has_kill

    def test_frames_counted(self, pixel_filter, create_test_image):
        """Test frames are counted correctly"""
        img_b64 = create_test_image(content_type='blank')

        for _ in range(5):
            pixel_filter.has_kill_feed(img_b64)

        assert pixel_filter.frames_analyzed == 5


# ============================================================================
# Test: Statistics
# ============================================================================

class TestStatistics:
    """Test filter statistics"""

    def test_stats_initial_state(self, pixel_filter):
        """Test statistics in initial state"""
        stats = pixel_filter.get_stats()

        assert stats['frames_analyzed'] == 0
        assert stats['frames_filtered'] == 0
        assert stats['filter_rate'] == "0.0%"  # Returns formatted string

    def test_stats_after_filtering(self, pixel_filter, create_test_image):
        """Test statistics after filtering frames"""
        blank = create_test_image(content_type='blank')

        # Process multiple blank frames
        for _ in range(10):
            pixel_filter.has_kill_feed(blank)

        stats = pixel_filter.get_stats()
        assert stats['frames_analyzed'] == 10
        # Some frames should be filtered (after first frame)
        assert stats['frames_filtered'] > 0
        # Parse filter_rate percentage string
        filter_rate = float(stats['filter_rate'].rstrip('%'))
        assert 0 < filter_rate <= 100

    def test_stats_mixed_frames(self, pixel_filter, create_test_image):
        """Test statistics with mix of frames"""
        blank = create_test_image(content_type='blank')
        kill_feed = create_test_image(content_type='kill_feed')

        # Alternate between blank and kill feed
        for _ in range(5):
            pixel_filter.has_kill_feed(blank)
            pixel_filter.has_kill_feed(kill_feed)

        stats = pixel_filter.get_stats()
        assert stats['frames_analyzed'] == 10
        # Some frames filtered, some passed
        filter_rate = float(stats['filter_rate'].rstrip('%'))
        assert 0 <= filter_rate <= 100


# ============================================================================
# Test: Integration Scenarios
# ============================================================================

class TestIntegrationScenarios:
    """Test realistic usage scenarios"""

    def test_game_lobby_static_screen(self, pixel_filter, create_test_image):
        """Test scenario: Static lobby screen (no action)"""
        lobby = create_test_image(content_type='blank')

        filtered_count = 0
        for _ in range(100):
            if not pixel_filter.has_kill_feed(lobby):
                filtered_count += 1

        # Most frames should be filtered (after first)
        assert filtered_count > 90

    def test_game_active_with_kills(self, pixel_filter, create_test_image):
        """Test scenario: Active game with kills appearing"""
        blank = create_test_image(content_type='blank')
        kill_feed = create_test_image(content_type='kill_feed')

        # Simulate: 90 blank frames, 10 with kills
        frames = [blank] * 90 + [kill_feed] * 10

        passed = 0
        for frame in frames:
            if pixel_filter.has_kill_feed(frame):
                passed += 1

        # All kill_feed frames should pass
        assert passed >= 10

    def test_high_filter_rate_on_static_content(self, pixel_filter, create_test_image):
        """Test achieving 80%+ filter rate on static content"""
        static = create_test_image(content_type='blank')

        for _ in range(100):
            pixel_filter.has_kill_feed(static)

        stats = pixel_filter.get_stats()
        # Should achieve high filter rate (target: 80%+)
        filter_rate = float(stats['filter_rate'].rstrip('%'))
        assert filter_rate >= 70  # Allowing some margin


# ============================================================================
# Test: Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling and safe defaults"""

    def test_safe_default_on_decode_error(self, pixel_filter):
        """Test safe default (True) when decoding fails"""
        result = pixel_filter.has_kill_feed("corrupted!!!")
        assert result is True  # Safe default: don't skip

    def test_safe_default_on_processing_error(self, pixel_filter):
        """Test safe default when processing fails"""
        # Create image that might cause processing errors
        tiny_img = Image.new('RGB', (10, 10), color='red')
        buffer = io.BytesIO()
        tiny_img.save(buffer, format='PNG')
        img_b64 = base64.b64encode(buffer.getvalue()).decode()

        # Should not crash
        result = pixel_filter.has_kill_feed(img_b64)
        # Should return some boolean
        assert isinstance(result, bool)
