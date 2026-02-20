"""
Pixel Filter - Pre-filtro gratuito baseado em análise de pixels
================================================================

Detecta presença de kill feed sem usar API:
- Análise de ROI (Region of Interest)
- Detecção de texto (alto contraste)
- Detecção de cores (ícones)
- Detecção de mudanças (frame diff)

Author: Paulo Eugenio Campos
"""

import base64
import io
import logging
from typing import Optional
import numpy as np
from PIL import Image
import cv2

logger = logging.getLogger(__name__)


class PixelFilter:
    """
    Filtro baseado em análise de pixels (sem API, grátis)

    Detecta visualmente se há kill feed na região superior direita.
    Safe default: em caso de dúvida, deixa passar (não descarta kills)
    """

    def __init__(self):
        self.previous_frame_roi = None
        self.frames_analyzed = 0
        self.frames_filtered = 0

        # ROI coordinates (top-right corner where kill feed appears)
        self.roi_x = -450  # 450px from right edge
        self.roi_y = 0     # From top
        self.roi_width = 450
        self.roi_height = 250

        # Detection thresholds
        self.text_pixel_threshold = 800  # Minimum edge pixels for text
        self.color_pixel_threshold = 150  # Minimum colored pixels
        self.change_threshold = 0.08  # 8% change from previous frame

        logger.info("🎨 PixelFilter initialized (free, ~5ms per frame)")

    def decode_image(self, image_base64: str) -> Optional[np.ndarray]:
        """
        Decode base64 image to numpy array

        Args:
            image_base64: Image in base64 format

        Returns:
            numpy array (BGR) or None if error
        """
        try:
            # Remove data URL prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]

            # Decode base64
            image_bytes = base64.b64decode(image_base64)

            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))

            # Convert to numpy array (RGB)
            image_rgb = np.array(pil_image)

            # Convert RGB to BGR (OpenCV format)
            image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

            return image_bgr

        except Exception as e:
            logger.error(f"Error decoding image: {e}")
            return None

    def extract_roi(self, image: np.ndarray) -> np.ndarray:
        """
        Extract Region of Interest (kill feed area)

        Args:
            image: Full frame image (BGR)

        Returns:
            ROI image
        """
        height, width = image.shape[:2]

        # Calculate actual ROI coordinates
        x1 = max(0, width + self.roi_x)  # -450 from right
        y1 = self.roi_y
        x2 = width
        y2 = min(height, self.roi_height)

        roi = image[y1:y2, x1:x2]
        return roi

    def detect_text_presence(self, roi: np.ndarray) -> bool:
        """
        Detect text using edge detection (high contrast areas)

        Args:
            roi: Region of interest

        Returns:
            True if text detected
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)

            # Canny edge detection (text has sharp edges)
            edges = cv2.Canny(blurred, 100, 200)

            # Count edge pixels
            edge_pixels = np.sum(edges > 0)

            has_text = edge_pixels > self.text_pixel_threshold

            if has_text:
                logger.debug(f"✅ Text detected: {edge_pixels} edge pixels")

            return has_text

        except Exception as e:
            logger.error(f"Error detecting text: {e}")
            return True  # Safe default: let it pass

    def detect_icon_colors(self, roi: np.ndarray) -> bool:
        """
        Detect kill feed icon colors (red, yellow, white)

        Args:
            roi: Region of interest

        Returns:
            True if icons detected
        """
        try:
            # Define color ranges in BGR

            # Red (kill icons, blood)
            red_lower = np.array([0, 0, 150])
            red_upper = np.array([100, 100, 255])
            red_mask = cv2.inRange(roi, red_lower, red_upper)
            red_pixels = np.sum(red_mask > 0)

            # Yellow/Orange (weapon icons)
            yellow_lower = np.array([0, 150, 150])
            yellow_upper = np.array([100, 255, 255])
            yellow_mask = cv2.inRange(roi, yellow_lower, yellow_upper)
            yellow_pixels = np.sum(yellow_mask > 0)

            # White (text, player names)
            white_lower = np.array([200, 200, 200])
            white_upper = np.array([255, 255, 255])
            white_mask = cv2.inRange(roi, white_lower, white_upper)
            white_pixels = np.sum(white_mask > 0)

            total_colored = red_pixels + yellow_pixels + white_pixels
            has_colors = total_colored > self.color_pixel_threshold

            if has_colors:
                logger.debug(f"✅ Colors detected: R={red_pixels} Y={yellow_pixels} W={white_pixels}")

            return has_colors

        except Exception as e:
            logger.error(f"Error detecting colors: {e}")
            return True  # Safe default

    def detect_frame_change(self, roi: np.ndarray) -> bool:
        """
        Detect significant change from previous frame
        (Kill feed appears suddenly)

        Args:
            roi: Current ROI

        Returns:
            True if significant change detected
        """
        try:
            # First frame, no comparison possible
            if self.previous_frame_roi is None:
                self.previous_frame_roi = roi.copy()
                return True  # Safe default: let first frame pass

            # Check if dimensions match
            if roi.shape != self.previous_frame_roi.shape:
                logger.warning("ROI dimension mismatch, resetting previous frame")
                self.previous_frame_roi = roi.copy()
                return True

            # Calculate absolute difference
            diff = cv2.absdiff(roi, self.previous_frame_roi)

            # Convert to grayscale for simpler analysis
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

            # Count changed pixels (threshold: 30)
            changed_pixels = np.sum(diff_gray > 30)
            total_pixels = diff_gray.size
            change_percent = changed_pixels / total_pixels

            # Update previous frame
            self.previous_frame_roi = roi.copy()

            has_change = change_percent > self.change_threshold

            if has_change:
                logger.debug(f"✅ Change detected: {change_percent*100:.1f}%")

            return has_change

        except Exception as e:
            logger.error(f"Error detecting frame change: {e}")
            return True  # Safe default

    def has_kill_feed(self, image_base64: str) -> bool:
        """
        Main detection method - combines all checks

        Args:
            image_base64: Frame in base64

        Returns:
            True if kill feed likely present (or uncertain)
            False if definitely no kill feed
        """
        self.frames_analyzed += 1

        try:
            # Decode image
            image = self.decode_image(image_base64)
            if image is None:
                logger.warning("Failed to decode image, letting it pass")
                return True  # Safe default

            # Extract ROI
            roi = self.extract_roi(image)

            if roi.size == 0:
                logger.warning("Empty ROI, letting it pass")
                return True

            # Run all detection methods
            has_text = self.detect_text_presence(roi)
            has_colors = self.detect_icon_colors(roi)
            has_change = self.detect_frame_change(roi)

            # Decision logic: ANY indicator = probably has kill feed
            # This is conservative to avoid false negatives
            has_kill = has_text or has_colors or has_change

            if not has_kill:
                self.frames_filtered += 1
                filter_rate = (self.frames_filtered / self.frames_analyzed) * 100
                logger.info(f"❌ PixelFilter: NO kill feed detected (filtered {self.frames_filtered}/{self.frames_analyzed} = {filter_rate:.1f}%)")
            else:
                logger.debug(f"✅ PixelFilter: Kill feed indicators found (text={has_text}, colors={has_colors}, change={has_change})")

            return has_kill

        except Exception as e:
            logger.error(f"PixelFilter error: {e}", exc_info=True)
            return True  # Safe default: in case of error, let it pass

    def get_stats(self) -> dict:
        """Get filter statistics"""
        filter_rate = (self.frames_filtered / self.frames_analyzed * 100) if self.frames_analyzed > 0 else 0

        return {
            "frames_analyzed": self.frames_analyzed,
            "frames_filtered": self.frames_filtered,
            "frames_passed": self.frames_analyzed - self.frames_filtered,
            "filter_rate": f"{filter_rate:.1f}%",
            "cost_saved": f"${self.frames_filtered * 0.001:.2f}"
        }
