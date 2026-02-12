"""
Frame Deduplication - NASA-Level Optimization
==============================================

Evita processar frames idênticos ou muito similares consecutivos.
Economia: ~70% de redução de tokens em partidas com pouca ação.

Author: Paulo Eugenio Campos
"""

import base64
import io
import logging
from typing import Optional
import numpy as np
from PIL import Image
import imagehash

logger = logging.getLogger(__name__)


class FrameDeduplicator:
    """
    Deduplica frames similares usando perceptual hashing.

    Usa imagehash (pHash) para detectar frames visualmente idênticos,
    mesmo com pequenas diferenças de compressão.
    """

    def __init__(self, similarity_threshold: float = 0.95):
        """
        Inicializa o deduplicador.

        Args:
            similarity_threshold: Threshold de similaridade (0-1)
                                  0.95 = 95% similar = skip
        """
        self.similarity_threshold = similarity_threshold
        self.last_frame_hash: Optional[imagehash.ImageHash] = None
        self.last_frame_base64: Optional[str] = None

        # Estatísticas
        self.total_frames = 0
        self.skipped_frames = 0

        logger.info(f"🔄 Frame Deduplicator initialized (threshold: {similarity_threshold:.0%})")

    def is_duplicate(self, frame_base64: str) -> bool:
        """
        Verifica se o frame é duplicado/similar ao anterior.

        Args:
            frame_base64: Frame em base64

        Returns:
            True se o frame é similar ao anterior (deve pular)
        """
        self.total_frames += 1

        try:
            # Primeiro frame sempre processa
            if self.last_frame_hash is None:
                self._update_last_frame(frame_base64)
                return False

            # Calcular hash do frame atual
            current_hash = self._calculate_hash(frame_base64)

            # Comparar com último frame
            similarity = 1 - (current_hash - self.last_frame_hash) / 64.0

            # Se muito similar, pular
            if similarity >= self.similarity_threshold:
                self.skipped_frames += 1
                logger.debug(f"📸 Frame skipped (similarity: {similarity:.1%})")
                return True

            # Frame diferente, atualizar
            self._update_last_frame(frame_base64, current_hash)
            return False

        except Exception as e:
            logger.error(f"❌ Error checking frame similarity: {e}")
            # Em caso de erro, não pular (melhor processar que perder)
            return False

    def _calculate_hash(self, frame_base64: str) -> imagehash.ImageHash:
        """Calcula perceptual hash da imagem."""
        try:
            # Decode base64
            image_data = base64.b64decode(frame_base64)
            image = Image.open(io.BytesIO(image_data))

            # Calcular pHash (perceptual hash)
            # Mais robusto que MD5/SHA para detectar similaridade visual
            phash = imagehash.phash(image, hash_size=8)

            return phash

        except Exception as e:
            logger.error(f"❌ Error calculating hash: {e}")
            raise

    def _update_last_frame(self, frame_base64: str, frame_hash: Optional[imagehash.ImageHash] = None):
        """Atualiza referência do último frame."""
        if frame_hash is None:
            frame_hash = self._calculate_hash(frame_base64)

        self.last_frame_hash = frame_hash
        self.last_frame_base64 = frame_base64

    def reset(self):
        """Reset do estado (útil entre partidas)."""
        self.last_frame_hash = None
        self.last_frame_base64 = None
        logger.debug("🔄 Deduplicator reset")

    def get_stats(self) -> dict:
        """Retorna estatísticas de economia."""
        if self.total_frames == 0:
            return {
                "total_frames": 0,
                "skipped_frames": 0,
                "skip_rate": 0.0,
                "savings": 0.0
            }

        skip_rate = self.skipped_frames / self.total_frames

        return {
            "total_frames": self.total_frames,
            "skipped_frames": self.skipped_frames,
            "skip_rate": skip_rate,
            "savings": skip_rate  # Economia direta em API calls
        }

    def log_stats(self):
        """Log das estatísticas."""
        stats = self.get_stats()

        if stats["total_frames"] > 0:
            logger.info(f"📊 Frame Deduplication Stats:")
            logger.info(f"   Total frames: {stats['total_frames']}")
            logger.info(f"   Skipped: {stats['skipped_frames']} ({stats['skip_rate']:.1%})")
            logger.info(f"   💰 Token savings: {stats['savings']:.1%}")
