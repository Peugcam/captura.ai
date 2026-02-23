"""
Teste Simples de Captura OBS
"""
import obsws_python as obs
import time

OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "ZNx3v4LjLVCgbTrO"

print("=" * 60)
print("TESTE DE CAPTURA OBS")
print("=" * 60)
print()

try:
    print("[1/4] Conectando ao OBS...")
    cl = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=OBS_PASSWORD, timeout=3)
    print("[OK] Conectado!")
    print()

    print("[2/4] Obtendo cena atual...")
    current_scene = cl.get_current_program_scene()
    scene_name = current_scene.current_program_scene_name
    print(f"[OK] Cena atual: {scene_name}")
    print()

    print("[3/4] Testando captura de screenshot...")
    print("Aguarde...")

    start = time.time()
    response = cl.get_source_screenshot(
        name=scene_name,
        img_format="png",
        width=1920,
        height=1080,
        quality=-1
    )
    elapsed = time.time() - start

    print(f"[OK] Screenshot capturado em {elapsed:.2f}s")
    print(f"     Tamanho dos dados: {len(response.image_data)} bytes")
    print()

    print("[4/4] Teste de 5 capturas...")
    for i in range(1, 6):
        start = time.time()
        response = cl.get_source_screenshot(
            name=scene_name,
            img_format="png",
            width=1920,
            height=1080,
            quality=-1
        )
        elapsed = time.time() - start
        print(f"  [{i}/5] Captura em {elapsed:.2f}s - {len(response.image_data)} bytes")
        time.sleep(0.25)  # 4 FPS

    print()
    print("=" * 60)
    print("TESTE CONCLUIDO COM SUCESSO!")
    print("=" * 60)
    print()
    print("CONCLUSAO:")
    print("  - OBS esta funcionando corretamente")
    print("  - Capturas estao sendo realizadas")
    print("  - Pronto para usar o sistema completo")
    print()

except Exception as e:
    print()
    print("=" * 60)
    print("ERRO NO TESTE")
    print("=" * 60)
    print()
    print(f"Erro: {e}")
    print()
    print("SOLUCAO:")
    print("  1. Verifique se OBS esta aberto")
    print("  2. Verifique se WebSocket esta ativo")
    print("  3. Verifique a senha do WebSocket")
    print()

input("Pressione Enter para sair...")
