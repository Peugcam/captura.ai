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
import os

# Configure Tesseract path for Windows
if os.name == 'nt':  # Windows
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

# Import local modules
from src.brazilian_kill_parser import BrazilianKillParser
from src.team_tracker import TeamTracker
from src.multi_api_client import MultiAPIClient
import config

logger = logging.getLogger(__name__)


class VisionPreFilter:
    """Vision API pré-filtro em baixa resolução (econômico e preciso)"""

    def __init__(self, api_keys: list, model: str):
        from src.multi_api_client import MultiAPIClient
        self.client = MultiAPIClient(api_keys)
        self.model = model
        self.executor = ThreadPoolExecutor(max_workers=config.OCR_WORKERS)

    def resize_image_low_res(self, image_base64: str, target_width: int = 320) -> str:
        """
        Reduz imagem para baixa resolução (economia de tokens)

        Args:
            image_base64: Imagem em base64
            target_width: Largura alvo (padrão 320px)

        Returns:
            Imagem reduzida em base64
        """
        try:
            # Decode base64
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))

            # Calcular nova altura mantendo aspect ratio
            width, height = image.size
            aspect_ratio = height / width
            target_height = int(target_width * aspect_ratio)

            # Resize
            resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)

            # Encode de volta
            buffer = io.BytesIO()
            resized.save(buffer, format='JPEG', quality=70)
            resized_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            reduction = (1 - (target_width * target_height) / (width * height)) * 100
            logger.debug(f"Image resized: {width}x{height} → {target_width}x{target_height} ({reduction:.1f}% reduction)")

            return resized_base64

        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return image_base64

    def has_kill_feed(self, image_base64: str) -> bool:
        """
        Verifica se frame tem kill feed usando Vision API em baixa res

        Args:
            image_base64: Frame em base64

        Returns:
            True se detectou kill feed
        """
        try:
            # Reduzir para 320px (75% economia de tokens)
            low_res_image = self.resize_image_low_res(image_base64, target_width=320)

            # Prompt simples e rápido
            prompt = """Look at this GTA V screenshot.

Question: Is there a KILL FEED visible in the top-right corner?

A kill feed shows player kills with format: [PlayerName] [icon/text] [PlayerName]

Answer ONLY with: YES or NO"""

            # Chamar Vision API (usando vision_chat_multiple com 1 frame)
            responses = self.client.vision_chat_multiple(
                model=self.model,
                prompt=prompt,
                images_base64=[low_res_image],  # Lista com 1 imagem
                temperature=0,
                max_tokens=10  # Só precisa de "YES" ou "NO"
            )

            # Extrair primeira resposta
            response = responses[0] if responses else {'success': False, 'error': 'No response'}

            if not response['success']:
                logger.error(f"Vision pre-filter error: {response.get('error')}")
                return True  # Em caso de erro, deixa passar (safe default)

            answer = response['content'].strip().upper()
            has_kill = 'YES' in answer or 'SIM' in answer

            if has_kill:
                logger.info(f"✅ Vision pre-filter: KILL FEED detected")
            else:
                logger.debug(f"❌ Vision pre-filter: NO kill feed")

            return has_kill

        except Exception as e:
            logger.error(f"Vision pre-filter error: {e}")
            return True  # Em caso de erro, deixa passar


class OCRPreFilter:
    """OCR pré-filtro para detectar frames com kills (LEGACY - não usado mais)"""

    def __init__(self, keywords: List[str]):
        self.keywords = keywords
        self.executor = ThreadPoolExecutor(max_workers=config.OCR_WORKERS)

    def extract_roi(self, frame, game_type: str):
        """
        Extrai região de interesse (ROI) baseada no tipo de jogo

        Args:
            frame: Frame OpenCV (numpy array)
            game_type: Tipo do jogo ('gta' ou 'naruto')

        Returns:
            ROI extraído ou frame inteiro se USE_ROI=false
        """
        if not config.USE_ROI:
            return frame

        height, width = frame.shape[:2]

        if game_type == "gta":
            # Kill feed GTA: canto superior direito (OTIMIZADO - Gemini Refined)
            # ROI menor = OCR mais rápido + menos falsos positivos
            # Utiliza apenas 25% da largura e 25% da altura no canto superior direito
            x1 = int(width * 0.75)   # 75% da largura (mais focado)
            y1 = int(height * 0.05)  # 5% do topo (pula barra de título/bordas)
            x2 = width               # Até o final
            y2 = int(height * 0.30)  # 30% do topo (aumentado levemente para segurança)

        else:  # naruto ou outros
            # Para Naruto Online: tela inteira (combate acontece em toda tela)
            x1, y1 = 0, 0
            x2, y2 = width, height

        # Ensure valid coordinates
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(width, x2)
        y2 = min(height, y2)

        return frame[y1:y2, x1:x2]

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

            # Extrair ROI baseado no tipo de jogo
            roi = self.extract_roi(frame, config.GAME_TYPE)

            # OCR na ROI (mais rápido e preciso que tela inteira)
            text = pytesseract.image_to_string(
                roi,
                lang='eng+por',  # Inglês + Português para suporte bilíngue
                config='--psm 6'
            )

            # Check SOMENTE keywords (mais preciso, menos falsos positivos)
            text_upper = text.upper()
            # Keywords já estão em UPPERCASE no config.py
            has_keyword = any(kw in text_upper for kw in self.keywords)

            # Log para debug (mostra texto detectado)
            if has_keyword:
                matching_keywords = [kw for kw in self.keywords if kw in text_upper]
                logger.info(f"✅ OCR detected keywords: {matching_keywords}")
                logger.debug(f"   OCR text preview: {text_upper[:100]}...")
            else:
                logger.debug(f"❌ OCR no keywords found. Text preview: {text_upper[:50]}...")

            # OTIMIZAÇÃO: Detecção de números desabilitada para evitar falsos positivos
            # (FPS counter, munição, dinheiro, etc não são kills)
            # Keywords são suficientes para detectar 95%+ das kills no GTA

            return has_keyword  # Retorna TRUE somente se tem keyword real de kill

        except Exception as e:
            logger.error(f"OCR error: {e}")
            return True  # Em caso de erro, deixa passar (safe default)

    def process_async(self, image_base64: str):
        """Process frame async"""
        return self.executor.submit(self.has_kill_keywords, image_base64)


class VisionProcessor:
    """Processa frames com GPT-4o Vision (+ Gemini fallback)"""

    def __init__(self, api_keys: list, model: str):
        self.client = MultiAPIClient(api_keys)
        self.model = model
        self.parser = BrazilianKillParser()

        # NASA-Level Optimization: Gemini Flash 2.0 Fallback (via OpenRouter)
        self.use_gemini_fallback = config.USE_GEMINI_FALLBACK
        self.gemini_model = config.GEMINI_MODEL
        if self.use_gemini_fallback:
            logger.info(f"🤖 Gemini fallback enabled: {self.gemini_model} (90% cheaper, via OpenRouter)")
        else:
            logger.debug("⚠️ Gemini fallback disabled")

    def get_prompt_for_game(self, game_type: str) -> str:
        """
        Retorna prompt otimizado baseado no tipo de jogo

        Args:
            game_type: Tipo do jogo ('gta' ou 'naruto')

        Returns:
            Prompt otimizado
        """
        if game_type == "gta":
            return """Analyze these GTA V Battle Royale gameplay screenshots for KILL NOTIFICATIONS.

🎯 PRIMARY FOCUS: KILL FEED in TOP-RIGHT CORNER

IMPORTANT: This is BATTLE ROYALE mode - players have TEAM/FACTION PREFIXES!

PLAYER NAME FORMAT IN BATTLE ROYALE:
[FACTION]PlayerName or [FACTION].PlayerName

Common factions: PPP, LLL, MTL, NLS, VVV, AAA, etc. (always 3 letters)

Examples:
- "PPP.almeida99" → killer="PPP.almeida99", killer_team="PPP"
- "MTL ibra7b" → killer="MTL ibra7b", killer_team="MTL"
- "LLLmanetzz" → victim="LLLmanetzz", victim_team="LLL"
- "NLS_player" → victim="NLS_player", victim_team="NLS"

DETECT ALL COMBAT EVENTS and CLASSIFY them correctly!

EVENT TYPES TO DETECT:
1. **KILL** (💀 skull icon) - Confirmed death
2. **DAMAGE/PROXIMITY** - Damage dealt but no death (no skull, shows distance like "sniped", "shot")
3. **HEAL** (✚ cross icon) - Healing event
4. **FALL** - Fall damage
5. **OTHER** - Any other combat-related event

CRITICAL: Use the "event_type" field to classify:
- If has SKULL (💀) → event_type="kill"
- If has weapon/distance but NO skull → event_type="damage"
- If has CROSS (✚) → event_type="heal"
- If fall-related → event_type="fall"
- Other → event_type="other"

KILL TYPES TO CLASSIFY (for event_type="kill" only):
Use "kill_type" field to classify HOW the death happened:

1. **weapon** - Death by firearms (pistols, rifles, SMG, sniper, shotgun)
   - Verbs: shot, sniped, plugged, rifled, drilled, riddled, floored, ended, devastated, etc.
   - Distance shown (e.g., "97m", "50m")

2. **explosion** - Death by explosives (grenades, rockets, C4, sticky bombs)
   - Verbs: erased, destroyed, obliterated, vaporized, blasted, exploded
   - Objects: grenade, RPG, sticky bomb, C4, proximity mine

3. **fall** - Death by falling from height (ENVIRONMENTAL - no killer)
   - Verbs: fell, dropped, plummeted
   - Context: "fell to death", "fell from height", fall damage
   - For fall deaths, set killer="QUEDA" and killer_team="AMBIENTE"

4. **vehicle** - Death by vehicle collision or runover
   - Verbs: ran over, crushed, hit, splattered, roadkilled
   - Objects: car, truck, bike, motorcycle

5. **fire** - Death by fire/burning
   - Verbs: burned, fried, incinerated, scorched
   - Objects: molotov, flamethrower, fire

6. **melee** - Death by melee weapons (knife, bat, fists)
   - Verbs: stabbed, slashed, beaten, punched, knocked out
   - Objects: knife, bat, crowbar, fists

7. **drowning** - Death by drowning (ENVIRONMENTAL - no killer)
   - Verbs: drowned
   - Context: water-related death
   - For drowning deaths, set killer="AFOGAMENTO" and killer_team="AMBIENTE"

8. **suicide** - Self-inflicted death (ENVIRONMENTAL - no killer)
   - Context: player killing themselves (grenade suicide, fall suicide)
   - For suicide deaths, set killer="SUICÍDIO" and killer_team="AMBIENTE"

9. **unknown** - Cannot determine kill type from available info

WHAT TO EXTRACT:
1. **Event type** - Classify using icon/context (kill/damage/heal/fall/other)
2. **Kill type** - For event_type="kill", classify HOW they died (weapon/explosion/fall/vehicle/fire/melee/drowning/suicide/unknown)
3. **Player names** on both sides
4. **Faction prefixes** (PPP, MTL, EMPI, paIN, LLL, NLS, etc.)
5. **Distance/weapon** if shown

EXAMPLES:
- "EMPI Drethafps 💀 paIN Cloud" → event_type="kill" ✅
- "EMPI Drethafps sniped paIN Cloud 97m" → event_type="damage" ✅
- "Player ✚ Player" → event_type="heal" ✅

WEAPON-SPECIFIC VERBS (GTA V):
- Pistols: plugged, shot, popped, blasted
- SMGs: riddled, drilled, ruined
- Rifles: rifled, floored, ended, shot down
- Shotguns: devastated, pulverized, shotgunned
- Snipers: sniped, picked off, scoped
- Explosives: erased, destroyed, obliterated, vaporized
- Fire: burned, fried

RETURN JSON FORMAT:
{
  "description": "what you see in the kill feed",
  "has_combat": true/false,
  "kills": [
    {
      "event_type": "kill|damage|heal|fall|other",
      "kill_type": "weapon|explosion|fall|vehicle|fire|melee|drowning|suicide|unknown (ONLY for event_type=kill)",
      "killer": "exact killer name WITH faction prefix",
      "killer_team": "extracted faction (3 letters) or Unknown",
      "victim": "exact victim name WITH faction prefix",
      "victim_team": "extracted faction (3 letters) or Unknown",
      "distance": "weapon/method/distance (e.g., '97m', 'AK-47', 'headshot')"
    }
  ]
}

IMPORTANT:
- "kill_type" is ONLY used when event_type="kill"
- For event_type="damage", "heal", etc., you can omit "kill_type" or set it to null

CRITICAL RULES:
✅ Detect ALL combat events (kills, damage, heal, etc.)
✅ Classify correctly using event_type field
✅ Extract FULL names including faction prefixes (PPP, MTL, LLL, EMPI, paIN, etc.)
✅ Extract faction from name: "PPP.player" → team="PPP", "EMPI player" → team="EMPI"
✅ If faction is visible, extract it; otherwise use "Unknown"
✅ Include distance/weapon in the distance field
❌ Do NOT hallucinate - only report visible events
❌ If no events visible → {"has_combat": false, "kills": []}

EXAMPLES:

Example 1 (Weapon KILL with skull and distance):
{
  "description": "Kill feed shows: PPP.almeida99 💀 sniped LLLmanetzz 120m",
  "has_combat": true,
  "kills": [
    {
      "event_type": "kill",
      "kill_type": "weapon",
      "killer": "PPP.almeida99",
      "killer_team": "PPP",
      "victim": "LLLmanetzz",
      "victim_team": "LLL",
      "distance": "120m"
    }
  ]
}

Example 2 (Explosion KILL):
{
  "description": "Kill feed shows: MTL player 💀 obliterated NLS target with grenade",
  "has_combat": true,
  "kills": [
    {
      "event_type": "kill",
      "kill_type": "explosion",
      "killer": "MTL player",
      "killer_team": "MTL",
      "victim": "NLS target",
      "victim_team": "NLS",
      "distance": "grenade"
    }
  ]
}

Example 3 (Fall KILL - Environmental death, no killer):
{
  "description": "Kill feed shows: PPP.player 💀 fell to death",
  "has_combat": true,
  "kills": [
    {
      "event_type": "kill",
      "kill_type": "fall",
      "killer": "QUEDA",
      "killer_team": "AMBIENTE",
      "victim": "PPP.player",
      "victim_team": "PPP",
      "distance": "fall"
    }
  ]
}

Example 4 (DAMAGE event - no skull):
{
  "description": "Kill feed shows: EMPI Drethafps sniped paIN Cloud 97m",
  "has_combat": true,
  "kills": [
    {
      "event_type": "damage",
      "killer": "EMPI Drethafps",
      "killer_team": "EMPI",
      "victim": "paIN Cloud",
      "victim_team": "paIN",
      "distance": "97m"
    }
  ]
}

Example 5 (Vehicle KILL):
{
  "description": "Kill feed shows: LLL driver 💀 ran over AAA pedestrian",
  "has_combat": true,
  "kills": [
    {
      "event_type": "kill",
      "kill_type": "vehicle",
      "killer": "LLL driver",
      "killer_team": "LLL",
      "victim": "AAA pedestrian",
      "victim_team": "AAA",
      "distance": "vehicle"
    }
  ]
}

REMEMBER: The SKULL ICON 💀 is your best friend! Always look for it in the top-right corner!"""

        else:  # naruto
            return """Analyze these Naruto Online game screenshots for COMBO COUNTERS and COMBAT.

🎯 PRIMARY FOCUS: Look for COMBO TEXT on screen!

COMBO COUNTER FORMAT IN NARUTO ONLINE:
- "2 COMBO" or "2 combo" or "2COMBO"
- "3 COMBO" or "3 combo" or "3COMBO"
- "4 COMBO", "5 COMBO", "10 COMBO", etc.
- May appear as "X HIT" or "X HITS" instead
- Usually appears in CENTER or near attacking character

YOUR JOB:
1. **FIRST** - Look for text showing combo count ("2 COMBO", "3 COMBO", etc.)
2. **SECOND** - Look for damage numbers (any size, any color)
3. **THIRD** - Look for visual combat effects

RETURN JSON FORMAT:
{
  "description": "describe what you see - MENTION COMBO TEXT if visible",
  "has_combat": true/false,
  "kills": [
    {
      "killer": "player",
      "killer_team": "unknown",
      "victim": "enemy",
      "victim_team": "unknown",
      "distance": "COMBO: X hits - damage: [numbers] - effects: [description]"
    }
  ]
}

EXAMPLES:

Example 1 (Combo counter visible):
{
  "description": "Battle scene with '5 COMBO' text visible on screen, damage numbers 1234, 5678",
  "has_combat": true,
  "kills": [
    {
      "killer": "player",
      "killer_team": "unknown",
      "victim": "enemy",
      "victim_team": "unknown",
      "distance": "COMBO: 5 hits - damage: 1234, 5678 - effects: energy blast"
    }
  ]
}

Example 2 (Small combo):
{
  "description": "I can see '2 COMBO' text appearing, single damage number 3421",
  "has_combat": true,
  "kills": [
    {
      "killer": "player",
      "killer_team": "unknown",
      "victim": "enemy",
      "victim_team": "unknown",
      "distance": "COMBO: 2 hits - damage: 3421"
    }
  ]
}

Example 3 (No combo text but damage):
{
  "description": "Characters fighting, damage numbers 15234 visible but no combo counter",
  "has_combat": true,
  "kills": [
    {
      "killer": "player",
      "killer_team": "unknown",
      "victim": "enemy",
      "victim_team": "unknown",
      "distance": "COMBO: 1 hit - damage: 15234"
    }
  ]
}

Example 4 (Large combo):
{
  "description": "Big combo! Text shows '12 COMBO', multiple damage numbers cascading",
  "has_combat": true,
  "kills": [
    {
      "killer": "player",
      "killer_team": "unknown",
      "victim": "enemy",
      "victim_team": "unknown",
      "distance": "COMBO: 12 hits - damage: multiple numbers - effects: massive combo chain"
    }
  ]
}

CRITICAL: Pay CLOSE attention to any text that looks like "X COMBO" or "X HIT" - this is the most important info!"""

    def extract_roi_coords(self, width: int, height: int, game_type: str):
        """
        Calcula coordenadas do ROI baseado no tipo de jogo
        UNIFICADO com OCRPreFilter.extract_roi() para consistência

        Args:
            width: Largura da imagem
            height: Altura da imagem
            game_type: Tipo do jogo

        Returns:
            Tuple (x1, y1, x2, y2)
        """
        if game_type == "gta":
            # Kill feed GTA: canto superior direito (UNIFICADO com OCR)
            x1 = int(width * 0.75)   # 75% da largura
            y1 = int(height * 0.05)  # 5% do topo
            x2 = width               # Até o final
            y2 = int(height * 0.30)  # 30% do topo
        else:  # naruto ou outros
            x1, y1 = 0, 0
            x2, y2 = width, height

        return (x1, y1, x2, y2)

    def apply_roi_to_base64(self, image_base64: str) -> str:
        """
        Aplica ROI em imagem base64 e retorna nova imagem base64

        Args:
            image_base64: Imagem em base64

        Returns:
            Imagem com ROI aplicado em base64
        """
        if not config.USE_ROI:
            return image_base64

        try:
            # Decode base64
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))

            # Extrair coordenadas ROI
            width, height = image.size
            x1, y1, x2, y2 = self.extract_roi_coords(width, height, config.GAME_TYPE)

            # Cortar imagem
            roi_image = image.crop((x1, y1, x2, y2))

            # Encode de volta pra base64
            buffer = io.BytesIO()
            roi_image.save(buffer, format='JPEG', quality=85)
            roi_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            logger.debug(f"ROI applied: {width}x{height} -> {x2-x1}x{y2-y1} ({((x2-x1)*(y2-y1)/(width*height))*100:.1f}% of original)")

            return roi_base64

        except Exception as e:
            logger.error(f"Error applying ROI: {e}")
            return image_base64  # Retorna original em caso de erro

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

        # Aplicar ROI se habilitado
        if config.USE_ROI:
            logger.info(f"✂️ Applying ROI to {len(frames_base64)} frames")
            frames_base64 = [self.apply_roi_to_base64(frame) for frame in frames_base64]

        # Obter prompt otimizado baseado no tipo de jogo
        prompt = self.get_prompt_for_game(config.GAME_TYPE)

        try:
            logger.info(f"🤖 Sending {len(frames_base64)} frames to GPT-4o")

            response = self.client.vision_chat_multiple(
                model=self.model,
                prompt=prompt,
                images_base64=frames_base64,
                temperature=0,  # Zero para máxima determinismo e consistência
                max_tokens=2000
            )

            if not response['success']:
                logger.error(f"GPT-4o error: {response.get('error')}")

                # NASA-Level Optimization: Gemini Flash 2.0 Fallback (via OpenRouter)
                if self.use_gemini_fallback:
                    logger.warning(f"⚠️ GPT-4o failed, trying Gemini fallback via OpenRouter...")
                    try:
                        gemini_response = self.client.vision_chat_multiple(
                            model=self.gemini_model,  # google/gemini-2.0-flash-exp:free
                            prompt=prompt,
                            images_base64=frames_base64,
                            temperature=0,
                            max_tokens=2000
                        )

                        if gemini_response['success']:
                            logger.info(f"✅ Gemini fallback successful! (Saved ~90% cost)")
                            response = gemini_response  # Usar resposta do Gemini
                        else:
                            logger.error(f"❌ Gemini fallback also failed: {gemini_response.get('error')}")
                            return []
                    except Exception as e:
                        logger.error(f"❌ Gemini fallback error: {e}")
                        return []
                else:
                    return []

            # Parse response
            import json
            content = response['content']

            # LOG COMPLETO PARA DEBUG
            logger.info(f"📝 GPT-4o Response: {content[:500]}")

            # Extract JSON from response
            start = content.find('{')
            end = content.rfind('}') + 1

            if start != -1 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)

                # Log description if available
                if 'description' in data:
                    logger.info(f"🔍 Scene: {data['description']}")
                    logger.info(f"⚔️ Combat: {data.get('has_combat', False)}")

                kills = data.get('kills', [])

                logger.info(f"✅ GPT-4o detected {len(kills)} kills")

                return kills

        except Exception as e:
            logger.error(f"Vision processing error: {e}")

        return []


class FrameProcessor:
    """Processador completo de frames"""

    def __init__(self):
        # NASA-Level Optimization: Frame Deduplication
        self.deduplicator = None
        if config.USE_FRAME_DEDUP:
            from src.frame_deduplicator import FrameDeduplicator
            self.deduplicator = FrameDeduplicator(
                similarity_threshold=config.FRAME_SIMILARITY_THRESHOLD
            )
            logger.info(f"🔄 Frame Deduplication enabled (threshold: {config.FRAME_SIMILARITY_THRESHOLD:.0%})")

        # Usar Vision Pre-Filter (mais confiável que OCR)
        self.vision_filter = None
        if config.OCR_ENABLED:
            logger.info("🔍 Vision Pre-Filter enabled (low-res API calls for filtering)")
            self.vision_filter = VisionPreFilter(
                api_keys=config.API_KEYS,
                model=config.VISION_MODEL
            )
        else:
            logger.info("⚠️ Vision Pre-Filter disabled - all frames will be processed")

        self.vision = VisionProcessor(
            api_keys=config.API_KEYS,
            model=config.VISION_MODEL
        )

        self.tracker = TeamTracker()
        self.parser = BrazilianKillParser()

        # Stats
        self.frames_received = 0
        self.frames_filtered = 0
        self.frames_processed = 0
        self.kills_detected = 0

        # Deduplicação de kills
        self.recent_kills = {}  # {kill_hash: timestamp}
        self.dedup_window = 60  # segundos para considerar duplicata (proteção contra delays)

        # Agrupamento inteligente de frames (Perfil Híbrido)
        self.pending_frames = []  # Fila de frames aguardando processamento
        self.first_frame_time = None  # Timestamp do primeiro frame na fila
        self.last_frame_time = None  # Timestamp do último frame adicionado

        # Configurações baseadas em pesquisa científica (carregadas do .env)
        self.quick_timeout = config.QUICK_TIMEOUT  # Timeout rápido para frame isolado
        self.grouping_window = config.GROUPING_WINDOW
        self.max_frames_batch = config.MAX_FRAMES_BATCH
        self.max_total_wait = config.MAX_TOTAL_WAIT
        self.min_frames_to_process = config.MIN_FRAMES_TO_PROCESS

        logger.info("📊 Kill Grouping System enabled (Hybrid Profile)")
        logger.info(f"   Quick timeout (isolated): {self.quick_timeout}s")
        logger.info(f"   Grouping window (multiple): {self.grouping_window}s")
        logger.info(f"   Max frames/batch: {self.max_frames_batch}")
        logger.info(f"   Max total wait: {self.max_total_wait}s")
        logger.info(f"   Min frames to process: {self.min_frames_to_process}")

    def _should_process_batch(self) -> bool:
        """
        Decide se deve processar o batch atual baseado nas regras de agrupamento

        Lógica Ultra-Responsiva com Auto-Flush:
        - Frame isolado: processa após 1s desde PRIMEIRO frame
        - Múltiplos frames: processa após 2.5s desde PRIMEIRO frame
        - Auto-flush: se nenhum frame novo há 0.5s, processa imediatamente

        Exemplo (team fight):
        t=0s: Kill 1 → Timer inicia
        t=0.3s: Kill 2 → Continua aguardando
        t=0.8s: Kill 3 → Continua aguardando
        t=1.3s: [NENHUM FRAME NOVO]
        t=1.8s: AUTO-FLUSH! (0.5s sem frames novos) → PROCESSA 3 kills

        Returns:
            True se deve processar agora
        """
        import time

        if not self.pending_frames:
            return False

        current_time = time.time()
        num_frames = len(self.pending_frames)

        # Regra 1: Atingiu máximo de frames no batch
        if num_frames >= self.max_frames_batch:
            logger.info(f"🔥 Processing batch: MAX FRAMES reached ({num_frames}/{self.max_frames_batch})")
            return True

        # Regra 2: AUTO-FLUSH - Se nenhum frame novo há 0.5s, processa imediatamente
        # Isso garante que quando a captura para, processamos tudo em até 0.5s
        if self.last_frame_time:
            time_since_last = current_time - self.last_frame_time
            if time_since_last >= 0.5:  # 500ms sem frames novos
                logger.info(f"🚀 Processing batch: AUTO-FLUSH (no new frames for {time_since_last:.1f}s, {num_frames} frame(s) pending)")
                return True

        # Regra 3 & 4: Timeout desde PRIMEIRO frame (valores reduzidos!)
        if self.first_frame_time:
            time_since_first = current_time - self.first_frame_time

            # Frame isolado há 1s: processa rápido
            if num_frames == 1 and time_since_first >= self.quick_timeout:
                logger.info(f"⚡ Processing batch: QUICK TIMEOUT for isolated frame ({time_since_first:.1f}s / {self.quick_timeout}s)")
                return True

            # Múltiplos frames há 2.5s: processa batch
            if num_frames >= 2 and time_since_first >= self.grouping_window:
                logger.info(f"📦 Processing batch: GROUPING WINDOW expired ({time_since_first:.1f}s / {self.grouping_window}s, {num_frames} frames)")
                return True

            # Proteção: timeout total (3s) - raramente chega aqui
            if time_since_first >= self.max_total_wait:
                logger.info(f"⏰ Processing batch: TOTAL TIMEOUT ({time_since_first:.1f}s / {self.max_total_wait}s, {num_frames} frames)")
                return True

        return False

    async def process_frame(self, frame: Dict) -> Optional[List[Dict]]:
        """
        Processa um frame individual com agrupamento inteligente

        Args:
            frame: Dict com data (base64), timestamp, number

        Returns:
            Lista de kills ou None (se ainda aguardando agrupamento)
        """
        import time

        self.frames_received += 1
        frame_data = frame.get('data', '')

        # NASA-Level Optimization #1: Frame Deduplication
        if self.deduplicator and self.deduplicator.is_duplicate(frame_data):
            logger.debug(f"⏭️ Frame #{self.frames_received} skipped (duplicate/similar)")
            self.frames_filtered += 1
            return None

        # Vision Pre-Filter (baixa resolução)
        if self.vision_filter and config.OCR_ENABLED:
            has_kill_feed = self.vision_filter.has_kill_feed(frame_data)
            if has_kill_feed:
                logger.info(f"✅ Vision Pre-Filter: Frame #{self.frames_received} HAS kill feed")
            else:
                logger.debug(f"❌ Vision Pre-Filter: Frame #{self.frames_received} NO kill feed")
                self.frames_filtered += 1
                return None
        else:
            logger.debug(f"⚠️ Vision Pre-Filter disabled, accepting frame #{self.frames_received}")

        # Adicionar à fila de frames pendentes
        current_time = time.time()
        self.pending_frames.append(frame_data)
        self.last_frame_time = current_time

        if not self.first_frame_time:
            self.first_frame_time = current_time

        logger.debug(f"📥 Frame added to queue: {len(self.pending_frames)} frame(s) pending")

        # Verificar se deve processar agora
        if self._should_process_batch():
            # Processar batch
            kills = self.process_batch(self.pending_frames)

            # Limpar fila
            self.pending_frames = []
            self.first_frame_time = None
            self.last_frame_time = None

            return kills

        # Ainda aguardando mais frames
        return None

    async def flush_pending_frames(self) -> Optional[List[Dict]]:
        """
        Força o processamento de frames pendentes (útil quando captura para)

        Returns:
            Lista de kills ou None se não há frames pendentes
        """
        if not self.pending_frames:
            return None

        logger.info(f"🚨 FORCE FLUSH: Processing {len(self.pending_frames)} pending frame(s)")

        # Processar batch
        kills = self.process_batch(self.pending_frames)

        # Limpar fila
        self.pending_frames = []
        self.first_frame_time = None
        self.last_frame_time = None

        return kills

    def _is_duplicate_kill(self, kill: Dict) -> bool:
        """
        Verifica se kill é duplicata (mesmo kill em frames consecutivos)

        Args:
            kill: Dict com killer, victim, etc.

        Returns:
            True se for duplicata
        """
        import time
        import hashlib

        # Criar hash único do kill (killer + victim)
        killer = kill.get('killer', '').lower().strip()
        victim = kill.get('victim', '').lower().strip()
        kill_hash = hashlib.md5(f"{killer}:{victim}".encode()).hexdigest()

        current_time = time.time()

        # Limpar kills antigos (mais de dedup_window segundos)
        expired = [h for h, t in self.recent_kills.items() if current_time - t > self.dedup_window]
        for h in expired:
            del self.recent_kills[h]

        # Verificar se já vimos este kill recentemente
        if kill_hash in self.recent_kills:
            time_since = current_time - self.recent_kills[kill_hash]
            logger.info(f"🔄 Duplicate kill ignored: {killer} -> {victim} (seen {time_since:.1f}s ago)")
            return True

        # Registrar este kill
        self.recent_kills[kill_hash] = current_time
        return False

    def process_batch(self, frames_data: List[str]) -> List[Dict]:
        """
        Processa batch de frames com Vision AI

        Args:
            frames_data: Lista de frames base64

        Returns:
            Lista de kills (sem duplicatas)
        """
        if not frames_data:
            return []

        # GPT-4o Vision
        kills = self.vision.process_batch(frames_data)

        # Filtrar duplicatas e registrar no tracker
        unique_kills = []
        for kill in kills:
            if not self._is_duplicate_kill(kill):
                event_type = kill.get('event_type', 'kill')

                # Apenas registrar MORTES (não dano/proximidade) no tracker
                if event_type == 'kill':
                    self.tracker.register_kill(
                        killer_name=kill.get('killer', ''),
                        killer_team=kill.get('killer_team', 'Unknown'),
                        victim_name=kill.get('victim', ''),
                        victim_team=kill.get('victim_team', 'Unknown'),
                        distance=kill.get('distance')
                    )
                    self.kills_detected += 1

                # Mas adicionar TODOS os eventos únicos para retornar
                unique_kills.append(kill)

        self.frames_processed += len(frames_data)

        return unique_kills

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

        # Converter dados do tracker para formato esperado pelo ExcelExporter
        match_summary = self.tracker.get_match_summary()

        # Montar estrutura de dados no formato esperado
        match_data = {
            'total_players': match_summary['total_players'],
            'total_alive': match_summary['alive'],
            'total_dead': match_summary['dead'],
            'total_teams': match_summary['teams'],
            'total_kills': self.kills_detected,
            'teams': {},
            'recent_events': []
        }

        # Preencher dados dos times
        for team_name in self.tracker.teams:
            team_stats = self.tracker.get_team_stats(team_name)
            team_obj = self.tracker.teams[team_name]

            players_data = []
            for player_name in team_obj.players:
                player_obj = self.tracker.players[player_name]
                players_data.append({
                    'name': player_obj.name,
                    'team': player_obj.team,
                    'kills': player_obj.kills,
                    'deaths': player_obj.deaths,
                    'alive': player_obj.alive,
                    'first_seen': player_obj.first_seen.isoformat() if player_obj.first_seen else '',
                    'last_seen': player_obj.last_seen.isoformat() if player_obj.last_seen else ''
                })

            match_data['teams'][team_name] = {
                'total': team_stats['total'],
                'alive': team_stats['alive'],
                'dead': team_stats['dead'],
                'total_kills': team_stats.get('total_kills', team_stats.get('kills', 0)),
                'players': players_data
            }

        # Converter kill history para eventos
        for kill in self.tracker.kills_history:
            match_data['recent_events'].append({
                'event_type': 'kill',
                'timestamp': kill.get('timestamp', ''),
                'data': {
                    'killer': kill.get('killer', '?'),
                    'victim': kill.get('victim', '?'),
                    'killer_team': kill.get('killer_team', 'Unknown'),
                    'victim_team': kill.get('victim_team', 'Unknown'),
                    'weapon': kill.get('distance', '-')  # "distance" é usado como arma
                }
            })

        # Exportar no formato Luis (3 abas: VIVOS, RANKING, KILL FEED)
        exporter.export_match(match_data, filename, format='luis')
        logger.info(f"📊 Exported to {filename}")
