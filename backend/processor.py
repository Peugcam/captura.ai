"""
Frame Processor - OCR + Vision AI + Team Tracking
==================================================

Processa frames do Go Gateway:
1. OCR pré-filtro (thread pool)
2. GPT-4o Vision API (batch)
3. Kill parsing
4. Team tracking

Author: Paulo Eugenio Campos
"""

import base64
import io
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional
import cv2
import numpy as np
from PIL import Image
import pytesseract

# Import local modules
from src.brazilian_kill_parser import BrazilianKillParser
from src.team_tracker import TeamTracker
from src.simple_openrouter import SimpleOpenRouter
import config

logger = logging.getLogger(__name__)


class OCRPreFilter:
    """OCR pré-filtro para detectar frames com kills"""

    def __init__(self, keywords: List[str]):
        self.keywords = keywords
        self.executor = ThreadPoolExecutor(max_workers=config.OCR_WORKERS)

    def has_kill_keywords(self, image_base64: str) -> bool:
        """
        Verifica se frame tem keywords de kill via OCR

        Args:
            image_base64: Frame em base64

        Returns:
            True se detectou keywords
        """
        try:
            # Decode base64
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))

            # Convert para OpenCV
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Crop kill feed area (top-right 40%)
            height, width = frame.shape[:2]
            x1 = int(width * 0.6)
            y1 = 0
            x2 = width
            y2 = int(height * 0.4)

            kill_feed_roi = frame[y1:y2, x1:x2]

            # OCR
            text = pytesseract.image_to_string(
                kill_feed_roi,
                lang='por',
                config='--psm 6'
            )

            # Check keywords
            text_upper = text.upper()
            has_keyword = any(kw in text_upper for kw in self.keywords)

            if has_keyword:
                logger.info(f"🔍 OCR detected kill keyword in frame")

            return has_keyword

        except Exception as e:
            logger.error(f"OCR error: {e}")
            return True  # Em caso de erro, deixa passar (safe default)

    def process_async(self, image_base64: str):
        """Process frame async"""
        return self.executor.submit(self.has_kill_keywords, image_base64)


class VisionProcessor:
    """Processa frames com GPT-4o Vision"""

    def __init__(self, api_key: str, model: str):
        self.client = SimpleOpenRouter(api_key)
        self.model = model
        self.parser = BrazilianKillParser()

    def process_batch(self, frames_base64: List[str]) -> List[Dict]:
        """
        Processa batch de frames com GPT-4o

        Args:
            frames_base64: Lista de frames em base64

        Returns:
            Lista de kills detectadas
        """
        if not frames_base64:
            return []

        prompt = """Analise estas imagens do jogo GTA V Battle Royale.

Identifique TODAS as kills que aparecem no kill feed (canto superior direito).

Formato brasileiro: [TEAM] [KILLER] MATOU [TEAM] [VICTIM] [DISTANCE]

Retorne JSON:
{
  "kills": [
    {
      "killer": "nome_jogador",
      "killer_team": "SIGLA",
      "victim": "nome_vitima",
      "victim_team": "SIGLA",
      "distance": "120m"
    }
  ]
}

Se não houver kills, retorne: {"kills": []}"""

        try:
            logger.info(f"🤖 Sending {len(frames_base64)} frames to GPT-4o")

            response = self.client.vision_chat_multiple(
                model=self.model,
                prompt=prompt,
                images_base64=frames_base64,
                temperature=0.1,
                max_tokens=2000
            )

            if not response['success']:
                logger.error(f"GPT-4o error: {response.get('error')}")
                return []

            # Parse response
            import json
            content = response['content']

            # Extract JSON from response
            start = content.find('{')
            end = content.rfind('}') + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)
                kills = data.get('kills', [])

                logger.info(f"✅ GPT-4o detected {len(kills)} kills")

                return kills

        except Exception as e:
            logger.error(f"Vision processing error: {e}")

        return []


class FrameProcessor:
    """Processador completo de frames"""

    def __init__(self):
        self.ocr_filter = None
        if config.OCR_ENABLED:
            self.ocr_filter = OCRPreFilter(config.OCR_KEYWORDS)

        self.vision = VisionProcessor(
            api_key=config.OPENROUTER_API_KEY,
            model=config.VISION_MODEL
        )

        self.tracker = TeamTracker()
        self.parser = BrazilianKillParser()

        # Stats
        self.frames_received = 0
        self.frames_filtered = 0
        self.frames_processed = 0
        self.kills_detected = 0

    async def process_frame(self, frame: Dict) -> Optional[List[Dict]]:
        """
        Processa um frame individual

        Args:
            frame: Dict com data (base64), timestamp, number

        Returns:
            Lista de kills ou None
        """
        self.frames_received += 1
        frame_data = frame.get('data', '')

        # OCR pré-filtro
        if self.ocr_filter and config.OCR_ENABLED:
            has_kill = self.ocr_filter.has_kill_keywords(frame_data)
            if not has_kill:
                self.frames_filtered += 1
                return None

        # Se passou pelo OCR ou OCR desabilitado, processar
        return frame_data

    def process_batch(self, frames_data: List[str]) -> List[Dict]:
        """
        Processa batch de frames com Vision AI

        Args:
            frames_data: Lista de frames base64

        Returns:
            Lista de kills
        """
        if not frames_data:
            return []

        # GPT-4o Vision
        kills = self.vision.process_batch(frames_data)

        # Registrar no tracker
        for kill in kills:
            self.tracker.register_kill(
                killer_name=kill.get('killer', ''),
                killer_team=kill.get('killer_team', 'Unknown'),
                victim_name=kill.get('victim', ''),
                victim_team=kill.get('victim_team', 'Unknown'),
                distance=kill.get('distance')
            )
            self.kills_detected += 1

        self.frames_processed += len(frames_data)

        return kills

    def get_stats(self) -> Dict:
        """Retorna estatísticas do processador"""
        return {
            'frames_received': self.frames_received,
            'frames_filtered': self.frames_filtered,
            'frames_processed': self.frames_processed,
            'kills_detected': self.kills_detected,
            'filter_efficiency': f"{(self.frames_filtered / max(self.frames_received, 1)) * 100:.1f}%",
            'teams': len(self.tracker.teams),
            'players': len(self.tracker.players),
            'alive': self.tracker.get_total_alive(),
            'dead': self.tracker.get_total_dead()
        }

    def get_match_summary(self) -> Dict:
        """Retorna resumo da partida"""
        return self.tracker.get_match_summary()

    def export_to_excel(self, filename: str):
        """Exporta resultados para Excel"""
        from src.excel_exporter import ExcelExporter

        exporter = ExcelExporter()
        data = self.tracker.export_to_dict()

        exporter.export(data, filename)
        logger.info(f"📊 Exported to {filename}")
