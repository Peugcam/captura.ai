"""
Brazilian GTA Battle Royale Kill Parser
=======================================

Parser específico para o formato brasileiro do GTA Battle Royale:
Formato: [TEAM] [KILLER] MATOU [ICON] [TEAM] [VICTIM] [DISTANCE]

Exemplo: PPP almeida99 MATOU 💀 LLL pikachu1337 120m

Author: Paulo Eugenio Campos
Cliente: Luis Otavio
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BrazilianKillParser:
    """
    Parser especializado para kill feed do GTA BR

    Detecta:
    - Quem matou (killer + team)
    - Quem morreu (victim + team)
    - Distância
    - Se foi kill confirmada (presença de ícone)
    """

    def __init__(self):
        # Palavras-chave que indicam kill
        self.kill_keywords = [
            'MATOU',
            'ELIMINOU',
            'MATARAM',
            'KILLED',
            'ELIMINATED'
        ]

        # Padrões de teams comuns
        self.team_pattern = r'[A-Z]{2,4}'  # 2-4 letras maiúsculas

        # Padrão de distância
        self.distance_pattern = r'(\d+)m'

    def parse_kill_line(self, text: str) -> Optional[Dict]:
        """
        Parse uma linha do kill feed

        Args:
            text: Texto da linha (OCR)

        Returns:
            Dict com informações da kill ou None
        """
        # Limpar texto
        text = text.strip()

        if not text:
            return None

        # Verificar se tem palavra-chave de kill
        has_kill_keyword = any(keyword in text.upper() for keyword in self.kill_keywords)

        if not has_kill_keyword:
            return None

        # Padrão completo:
        # [TEAM] [KILLER] MATOU [ICON?] [TEAM] [VICTIM] [DISTANCE?]

        # Tentar extrair componentes
        try:
            parts = text.split()

            if len(parts) < 4:  # Mínimo necessário
                return None

            # Encontrar índice da palavra-chave
            keyword_idx = -1
            keyword_found = None

            for idx, part in enumerate(parts):
                if part.upper() in self.kill_keywords:
                    keyword_idx = idx
                    keyword_found = part
                    break

            if keyword_idx == -1:
                return None

            # Antes da palavra-chave: Team + Killer
            before_keyword = parts[:keyword_idx]

            # Depois da palavra-chave: [Icon?] Team + Victim + Distance?
            after_keyword = parts[keyword_idx + 1:]

            # Extrair killer e team
            killer_team = None
            killer_name = None

            if len(before_keyword) >= 2:
                # Último elemento antes do MATOU é o nome
                killer_name = before_keyword[-1]
                # Penúltimo pode ser o team
                if len(before_keyword) >= 2 and re.match(self.team_pattern, before_keyword[-2]):
                    killer_team = before_keyword[-2]

            elif len(before_keyword) == 1:
                killer_name = before_keyword[0]

            # Extrair victim e team
            victim_team = None
            victim_name = None
            distance = None

            # Pular possível ícone (emoji, símbolo)
            # Emojis geralmente não contêm caracteres alfanuméricos
            start_idx = 0
            if len(after_keyword) > 0:
                first_token = after_keyword[0]
                # Considerar ícone APENAS se não tem letras/números (puro emoji/símbolo)
                # Isso permite "BB" (team) mas pula "💀🔫💥" (emojis)
                has_alnum = any(c.isalnum() for c in first_token)
                if not has_alnum:
                    start_idx = 1  # Pular ícone

            remaining = after_keyword[start_idx:]

            if len(remaining) >= 2:
                # Primeiro: team da vítima
                if re.match(self.team_pattern, remaining[0]):
                    victim_team = remaining[0]
                    victim_name = remaining[1]

                    # Distância pode estar depois
                    if len(remaining) >= 3:
                        dist_match = re.search(self.distance_pattern, remaining[2])
                        if dist_match:
                            distance = dist_match.group(1) + 'm'
                else:
                    # Não tem team, só nome
                    victim_name = remaining[0]

                    # Distância pode estar depois
                    if len(remaining) >= 2:
                        dist_match = re.search(self.distance_pattern, remaining[1])
                        if dist_match:
                            distance = dist_match.group(1) + 'm'

            elif len(remaining) == 1:
                victim_name = remaining[0]

            # Validar se extraiu o mínimo
            if not killer_name or not victim_name:
                return None

            # Montar resultado
            kill_data = {
                'killer': killer_name,
                'killer_team': killer_team or 'Unknown',
                'victim': victim_name,
                'victim_team': victim_team or 'Unknown',
                'distance': distance,
                'keyword': keyword_found,
                'timestamp': datetime.now().isoformat(),
                'confirmed': True  # Se detectou no feed, é confirmada
            }

            logger.info(f"Kill parsed: {killer_name} ({killer_team}) -> {victim_name} ({victim_team})")

            return kill_data

        except Exception as e:
            logger.error(f"Erro ao parsear kill: {e}")
            logger.debug(f"Texto: {text}")
            return None

    def parse_kill_feed_frame(self, ocr_results: List[str]) -> List[Dict]:
        """
        Parse múltiplas linhas do kill feed

        Args:
            ocr_results: Lista de linhas detectadas pelo OCR

        Returns:
            Lista de kills detectadas
        """
        kills = []

        for line in ocr_results:
            kill_data = self.parse_kill_line(line)
            if kill_data:
                kills.append(kill_data)

        return kills
