"""
GTA Analytics - Plugin OBS
Captura automatica do kill feed e envia para o backend

INSTALACAO:
1. Copie este arquivo para: %APPDATA%\obs-studio\scripts\
2. No OBS: Ferramentas -> Scripts -> + (Adicionar)
3. Selecione este arquivo
4. Configure a URL do Gateway
5. Pronto! Roda automaticamente
"""

import obspython as obs
import urllib.request
import urllib.error
import json
import base64
import time
from io import BytesIO

# ============================================================================
# CONFIGURACOES (editaveis pelo usuario no OBS)
# ============================================================================

GATEWAY_URL = "http://localhost:8000"  # Alterar para Fly.io em producao
CAPTURE_FPS = 4  # Frames por segundo
KILL_FEED_REGION = {
    "x": 1400,      # Posicao X (canto superior direito)
    "y": 0,         # Posicao Y
    "width": 520,   # Largura da regiao
    "height": 400   # Altura da regiao
}

# ============================================================================
# VARIAVEIS GLOBAIS
# ============================================================================

last_capture_time = 0
capture_interval = 1.0 / CAPTURE_FPS
frame_count = 0
enabled = False

# ============================================================================
# FUNCOES DO PLUGIN
# ============================================================================

def script_description():
    """Descricao que aparece no OBS"""
    return """<h2>GTA Analytics - Kill Feed Tracker</h2>

    <p>Captura automaticamente o kill feed do GTA e envia para analise em tempo real.</p>

    <p><b>Como usar:</b></p>
    <ol>
        <li>Configure a URL do Gateway abaixo</li>
        <li>Clique em "Iniciar Captura"</li>
        <li>Acesse o dashboard para ver as estatisticas</li>
    </ol>

    <p><b>Regiao capturada:</b> Canto superior direito (kill feed)</p>
    <p><b>FPS:</b> 4 frames por segundo (otimizado)</p>
    """

def script_properties():
    """Propriedades editaveis no OBS"""
    props = obs.obs_properties_create()

    # URL do Gateway
    obs.obs_properties_add_text(
        props,
        "gateway_url",
        "URL do Gateway",
        obs.OBS_TEXT_DEFAULT
    )

    # FPS
    obs.obs_properties_add_int_slider(
        props,
        "fps",
        "FPS de Captura",
        1, 10, 1
    )

    # Regiao do kill feed
    obs.obs_properties_add_int(
        props,
        "region_x",
        "Kill Feed - Posicao X",
        0, 3840, 1
    )

    obs.obs_properties_add_int(
        props,
        "region_y",
        "Kill Feed - Posicao Y",
        0, 2160, 1
    )

    obs.obs_properties_add_int(
        props,
        "region_width",
        "Kill Feed - Largura",
        100, 1920, 10
    )

    obs.obs_properties_add_int(
        props,
        "region_height",
        "Kill Feed - Altura",
        100, 1080, 10
    )

    # Botao de teste
    obs.obs_properties_add_button(
        props,
        "test_connection",
        "Testar Conexao com Gateway",
        test_connection_callback
    )

    # Status
    obs.obs_properties_add_text(
        props,
        "status",
        "Status",
        obs.OBS_TEXT_INFO
    )

    return props

def script_defaults(settings):
    """Valores padrao"""
    obs.obs_data_set_default_string(settings, "gateway_url", GATEWAY_URL)
    obs.obs_data_set_default_int(settings, "fps", CAPTURE_FPS)
    obs.obs_data_set_default_int(settings, "region_x", KILL_FEED_REGION["x"])
    obs.obs_data_set_default_int(settings, "region_y", KILL_FEED_REGION["y"])
    obs.obs_data_set_default_int(settings, "region_width", KILL_FEED_REGION["width"])
    obs.obs_data_set_default_int(settings, "region_height", KILL_FEED_REGION["height"])

def script_update(settings):
    """Atualiza configuracoes quando usuario muda"""
    global GATEWAY_URL, capture_interval, KILL_FEED_REGION

    GATEWAY_URL = obs.obs_data_get_string(settings, "gateway_url")
    fps = obs.obs_data_get_int(settings, "fps")
    capture_interval = 1.0 / max(fps, 1)

    KILL_FEED_REGION = {
        "x": obs.obs_data_get_int(settings, "region_x"),
        "y": obs.obs_data_get_int(settings, "region_y"),
        "width": obs.obs_data_get_int(settings, "region_width"),
        "height": obs.obs_data_get_int(settings, "region_height")
    }

    print(f"[GTA Analytics] Configuracoes atualizadas: {GATEWAY_URL}, {fps} FPS")

def script_load(settings):
    """Chamado quando plugin carrega"""
    global enabled
    enabled = True
    print("[GTA Analytics] Plugin carregado")

def script_unload():
    """Chamado quando plugin descarrega"""
    global enabled
    enabled = False
    print("[GTA Analytics] Plugin descarregado")

def script_tick(seconds):
    """
    Chamado a cada frame do OBS
    Captura frames em intervalos regulares
    """
    global last_capture_time, frame_count

    if not enabled:
        return

    current_time = time.time()

    # Verifica se passou tempo suficiente
    if current_time - last_capture_time >= capture_interval:
        try:
            capture_and_send_frame()
            last_capture_time = current_time
            frame_count += 1
        except Exception as e:
            print(f"[GTA Analytics] Erro ao capturar frame: {e}")

# ============================================================================
# CAPTURA E ENVIO
# ============================================================================

def capture_and_send_frame():
    """Captura frame atual do OBS e envia para o Gateway"""

    # Pega a source de saida (o que esta sendo transmitido/gravado)
    source = obs.obs_frontend_get_current_scene()

    if not source:
        return

    try:
        # Pega dimensoes da source
        width = obs.obs_source_get_width(source)
        height = obs.obs_source_get_height(source)

        if width == 0 or height == 0:
            obs.obs_source_release(source)
            return

        # Cria staging surface para captura
        with obs.obs_enter_graphics():
            stagesurface = obs.gs_stagesurface_create(width, height, obs.GS_RGBA)

            # Renderiza source
            obs.obs_source_inc_showing(source)
            texture = obs.gs_texrender_create(obs.GS_RGBA, obs.GS_ZS_NONE)

            obs.gs_texrender_reset(texture)

            if obs.gs_texrender_begin(texture, width, height):
                obs.obs_source_video_render(source)
                obs.gs_texrender_end(texture)

                # Copia para staging surface
                tex = obs.gs_texrender_get_texture(texture)
                obs.gs_stage_texture(stagesurface, tex)

            obs.obs_source_dec_showing(source)

            # Le pixels
            data, linesize = obs.gs_stagesurface_map(stagesurface)

            if data:
                # Converte para imagem
                # TODO: Crop para regiao do kill feed aqui

                # Por enquanto envia frame completo (otimizar depois)
                send_frame_to_gateway(data, width, height)

                obs.gs_stagesurface_unmap(stagesurface)

            obs.gs_stagesurface_destroy(stagesurface)
            obs.gs_texrender_destroy(texture)

    except Exception as e:
        print(f"[GTA Analytics] Erro na captura: {e}")

    finally:
        obs.obs_source_release(source)

def send_frame_to_gateway(image_data, width, height):
    """Envia frame para o Gateway via HTTP"""

    try:
        # Converte para base64 (simplificado)
        # Em producao, usar JPEG compression
        img_b64 = base64.b64encode(image_data).decode('utf-8')

        # Prepara payload
        payload = {
            "type": "frame",
            "data": img_b64,
            "width": width,
            "height": height,
            "region": "kill_feed",
            "timestamp": int(time.time() * 1000)
        }

        # Envia para Gateway
        req = urllib.request.Request(
            f"{GATEWAY_URL}/frame",
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )

        response = urllib.request.urlopen(req, timeout=5)

        if frame_count % 10 == 0:
            print(f"[GTA Analytics] Frame {frame_count} enviado")

    except urllib.error.URLError as e:
        if frame_count % 30 == 0:  # Log a cada 30 frames (evitar spam)
            print(f"[GTA Analytics] Erro de conexao: {e}")
    except Exception as e:
        print(f"[GTA Analytics] Erro ao enviar: {e}")

def test_connection_callback(props, prop):
    """Callback do botao de teste"""
    try:
        req = urllib.request.Request(f"{GATEWAY_URL}/health")
        response = urllib.request.urlopen(req, timeout=5)

        if response.status == 200:
            print("[GTA Analytics] ✓ Conexao OK!")
            return True
        else:
            print(f"[GTA Analytics] ✗ Gateway retornou status {response.status}")
            return False

    except Exception as e:
        print(f"[GTA Analytics] ✗ Erro: {e}")
        return False
