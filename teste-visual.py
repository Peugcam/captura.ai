"""
Teste Visual - Mostra a Captura em Tempo Real
Salva frames para você verificar se NÃO está com tela preta
"""
import time
from PIL import Image
import os

print("=" * 70)
print("  TESTE VISUAL - Verificar se a Captura Funciona")
print("=" * 70)
print()

# Criar pasta para salvar frames
output_dir = "frames_teste"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"✓ Pasta criada: {output_dir}/")
else:
    print(f"✓ Usando pasta: {output_dir}/")

print()

# Testar cada método e salvar frame
methods_to_test = []

# ============================================================================
# MÉTODO 1: PIL ImageGrab
# ============================================================================
try:
    from PIL import ImageGrab

    def capture_pil():
        return ImageGrab.grab()

    methods_to_test.append(("PIL_ImageGrab", capture_pil))
    print("✓ PIL ImageGrab disponível")
except Exception as e:
    print(f"✗ PIL ImageGrab falhou: {e}")

# ============================================================================
# MÉTODO 2: MSS
# ============================================================================
try:
    import mss
    from PIL import Image

    sct = mss.mss()

    def capture_mss():
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    methods_to_test.append(("MSS", capture_mss))
    print("✓ MSS disponível")
except ImportError:
    print("✗ MSS não instalado (pip install mss)")
except Exception as e:
    print(f"✗ MSS falhou: {e}")

# ============================================================================
# MÉTODO 3: D3DShot
# ============================================================================
try:
    import d3dshot

    d = d3dshot.create(capture_output="pil")

    def capture_d3d():
        return d.screenshot()

    methods_to_test.append(("D3DShot", capture_d3d))
    print("✓ D3DShot disponível")
except ImportError:
    print("✗ D3DShot não instalado (pip install d3dshot)")
except Exception as e:
    print(f"✗ D3DShot falhou: {e}")

# ============================================================================
# MÉTODO 4: Windows GDI
# ============================================================================
try:
    import win32gui
    import win32ui
    from ctypes import windll
    from PIL import Image

    def capture_gdi():
        hwnd = win32gui.GetDesktopWindow()
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bitmap)
        windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)

        bmpinfo = save_bitmap.GetInfo()
        bmpstr = save_bitmap.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)

        return img

    methods_to_test.append(("Windows_GDI", capture_gdi))
    print("✓ Windows GDI disponível")
except ImportError:
    print("✗ Windows GDI não instalado (pip install pywin32)")
except Exception as e:
    print(f"✗ Windows GDI falhou: {e}")

print()
print("=" * 70)
print()

if not methods_to_test:
    print("❌ ERRO: Nenhum método disponível!")
    print()
    print("Instale as bibliotecas:")
    print("  pip install mss d3dshot pywin32")
    print()
    exit(1)

print(f"📸 Capturando com {len(methods_to_test)} métodos...")
print()
print("IMPORTANTE: Abra o GTA agora (se quiser testar com o jogo)")
print()

# Aguardar 3 segundos para dar tempo de focar no jogo
print("Aguardando 3 segundos...")
for i in range(3, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

print()
print("Capturando agora!")
print()

results = []

for method_name, capture_func in methods_to_test:
    print(f"📷 Testando: {method_name}")

    try:
        start_time = time.time()
        img = capture_func()
        elapsed_ms = (time.time() - start_time) * 1000

        if img:
            # Salvar frame
            filename = f"{output_dir}/{method_name}.jpg"
            img.save(filename, "JPEG", quality=95)

            # Calcular tamanho
            file_size_kb = os.path.getsize(filename) / 1024

            # Verificar se está tudo preto (possível bloqueio)
            import statistics
            pixels = list(img.getdata())
            avg_brightness = statistics.mean([sum(p) / 3 for p in pixels[:1000]])  # Amostra de 1000 pixels

            is_black = avg_brightness < 10

            results.append({
                'method': method_name,
                'time_ms': elapsed_ms,
                'size_kb': file_size_kb,
                'resolution': img.size,
                'is_black': is_black,
                'filename': filename
            })

            status = "⚠️  TELA PRETA!" if is_black else "✓ OK"
            print(f"   {status}")
            print(f"   Tempo: {elapsed_ms:.1f}ms")
            print(f"   Tamanho: {file_size_kb:.1f}KB")
            print(f"   Resolução: {img.size}")
            print(f"   Salvo em: {filename}")
        else:
            print(f"   ✗ Retornou None")

    except Exception as e:
        print(f"   ✗ Erro: {e}")

    print()

# Resumo
print("=" * 70)
print("  RESUMO")
print("=" * 70)
print()

if results:
    print("📁 Frames salvos em:", os.path.abspath(output_dir))
    print()

    # Filtrar métodos que NÃO deram tela preta
    working = [r for r in results if not r['is_black']]

    if working:
        print("✅ MÉTODOS QUE FUNCIONAM (SEM TELA PRETA):")
        print()

        # Ordenar por velocidade
        working.sort(key=lambda x: x['time_ms'])

        for i, result in enumerate(working, 1):
            star = "⭐ RECOMENDADO" if i == 1 else ""
            print(f"  {i}. {result['method']} {star}")
            print(f"     Velocidade: {result['time_ms']:.1f}ms")
            print(f"     Arquivo: {result['filename']}")
            print()

        print("-" * 70)
        print()
        print(f"🎯 MELHOR OPÇÃO: {working[0]['method']}")
        print()

        if working[0]['method'] == "MSS":
            print("   Execute: python captura-nvidia.py")
        elif working[0]['method'] == "D3DShot":
            print("   Execute: python captura-wgc.py")
        elif working[0]['method'] == "Windows_GDI":
            print("   Execute: python captura-gamebar.py")
        elif working[0]['method'] == "PIL_ImageGrab":
            print("   Execute: python captura-simples.py")

    else:
        print("⚠️  ATENÇÃO: Todos os métodos resultaram em tela preta!")
        print()
        print("Possíveis causas:")
        print("  1. Você não estava com o GTA aberto em fullscreen")
        print("  2. O GTA está bloqueando TODOS os métodos (raro)")
        print("  3. Problemas com drivers de vídeo")
        print()
        print("Soluções:")
        print("  1. Abra o GTA em fullscreen e execute novamente")
        print("  2. Tente Windowed Borderless mode no GTA")
        print("  3. Atualize drivers da GPU")

    # Métodos com tela preta
    black_screens = [r for r in results if r['is_black']]
    if black_screens:
        print()
        print("❌ MÉTODOS COM TELA PRETA (NÃO USAR):")
        print()
        for result in black_screens:
            print(f"  • {result['method']}")
        print()

else:
    print("❌ Nenhum frame capturado com sucesso")

print("=" * 70)
print()
print("💡 PRÓXIMOS PASSOS:")
print()
print(f"1. Abra a pasta '{output_dir}/' e verifique os frames visualmente")
print("2. Escolha o método que NÃO está com tela preta")
print("3. Execute o arquivo de captura correspondente")
print()
print("Se TODOS estiverem pretos:")
print("  • Abra o GTA em modo Windowed Borderless")
print("  • Execute este script novamente")
print()
print("=" * 70)
