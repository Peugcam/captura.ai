"""
Script de Teste Rapido - Testa Todos os Metodos de Captura
Descobre automaticamente qual metodo NAO esta sendo bloqueado
"""
import time
from PIL import Image
import io
import sys

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("  TESTE DE METODOS DE CAPTURA - GTA Analytics")
print("=" * 70)
print()
print("Este script vai testar 4 métodos diferentes de captura de tela.")
print("Vamos descobrir qual NÃO está sendo bloqueado pelo GTA.")
print()
print("=" * 70)
print()

results = {}

# ============================================================================
# TESTE 1: PIL ImageGrab (Original)
# ============================================================================
print("📷 TESTE 1: PIL ImageGrab (Método Original)")
print("-" * 70)
try:
    from PIL import ImageGrab

    start = time.time()
    img = ImageGrab.grab()
    elapsed = (time.time() - start) * 1000

    # Salvar teste
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    size_kb = len(buffer.getvalue()) / 1024

    results['PIL ImageGrab'] = {
        'status': '✅ FUNCIONA',
        'time_ms': elapsed,
        'size_kb': size_kb,
        'resolution': img.size
    }

    print(f"✅ Sucesso!")
    print(f"   Tempo: {elapsed:.1f}ms")
    print(f"   Tamanho: {size_kb:.1f}KB")
    print(f"   Resolução: {img.size}")

except Exception as e:
    results['PIL ImageGrab'] = {'status': f'❌ ERRO: {e}'}
    print(f"❌ Falhou: {e}")

print()

# ============================================================================
# TESTE 2: MSS (Multi-Screen Screenshot)
# ============================================================================
print("📷 TESTE 2: MSS (Multi-Screen Screenshot)")
print("-" * 70)
try:
    import mss
    from PIL import Image

    sct = mss.mss()
    monitor = sct.monitors[1]

    start = time.time()
    sct_img = sct.grab(monitor)
    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    elapsed = (time.time() - start) * 1000

    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    size_kb = len(buffer.getvalue()) / 1024

    results['MSS'] = {
        'status': '✅ FUNCIONA',
        'time_ms': elapsed,
        'size_kb': size_kb,
        'resolution': img.size
    }

    print(f"✅ Sucesso!")
    print(f"   Tempo: {elapsed:.1f}ms")
    print(f"   Tamanho: {size_kb:.1f}KB")
    print(f"   Resolução: {img.size}")

except ImportError:
    results['MSS'] = {'status': '⚠️ NÃO INSTALADO (pip install mss)'}
    print(f"⚠️  Não instalado. Execute: pip install mss")
except Exception as e:
    results['MSS'] = {'status': f'❌ ERRO: {e}'}
    print(f"❌ Falhou: {e}")

print()

# ============================================================================
# TESTE 3: D3DShot (DirectX Capture)
# ============================================================================
print("📷 TESTE 3: D3DShot (DirectX Capture)")
print("-" * 70)
try:
    import d3dshot

    d = d3dshot.create(capture_output="pil")

    start = time.time()
    img = d.screenshot()
    elapsed = (time.time() - start) * 1000

    if img:
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        size_kb = len(buffer.getvalue()) / 1024

        results['D3DShot'] = {
            'status': '✅ FUNCIONA',
            'time_ms': elapsed,
            'size_kb': size_kb,
            'resolution': img.size
        }

        print(f"✅ Sucesso!")
        print(f"   Tempo: {elapsed:.1f}ms")
        print(f"   Tamanho: {size_kb:.1f}KB")
        print(f"   Resolução: {img.size}")
    else:
        results['D3DShot'] = {'status': '❌ Retornou None (GPU incompatível?)'}
        print(f"❌ Retornou None - Sua GPU pode não ser compatível")

except ImportError:
    results['D3DShot'] = {'status': '⚠️ NÃO INSTALADO (pip install d3dshot)'}
    print(f"⚠️  Não instalado. Execute: pip install d3dshot")
except Exception as e:
    results['D3DShot'] = {'status': f'❌ ERRO: {e}'}
    print(f"❌ Falhou: {e}")

print()

# ============================================================================
# TESTE 4: Windows GDI (PrintWindow)
# ============================================================================
print("📷 TESTE 4: Windows GDI (PrintWindow)")
print("-" * 70)
try:
    import win32gui
    import win32ui
    import win32con
    from ctypes import windll
    from PIL import Image

    hwnd = win32gui.GetDesktopWindow()
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    start = time.time()

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

    elapsed = (time.time() - start) * 1000

    win32gui.DeleteObject(save_bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    size_kb = len(buffer.getvalue()) / 1024

    results['Windows GDI'] = {
        'status': '✅ FUNCIONA',
        'time_ms': elapsed,
        'size_kb': size_kb,
        'resolution': img.size
    }

    print(f"✅ Sucesso!")
    print(f"   Tempo: {elapsed:.1f}ms")
    print(f"   Tamanho: {size_kb:.1f}KB")
    print(f"   Resolução: {img.size}")

except ImportError:
    results['Windows GDI'] = {'status': '⚠️ NÃO INSTALADO (pip install pywin32)'}
    print(f"⚠️  Não instalado. Execute: pip install pywin32")
except Exception as e:
    results['Windows GDI'] = {'status': f'❌ ERRO: {e}'}
    print(f"❌ Falhou: {e}")

print()

# ============================================================================
# RESUMO
# ============================================================================
print("=" * 70)
print("  RESUMO DOS TESTES")
print("=" * 70)
print()

# Encontrar o mais rápido
working_methods = {k: v for k, v in results.items() if isinstance(v.get('status'), str) and '✅' in v['status']}

if working_methods:
    print("✅ MÉTODOS QUE FUNCIONAM:")
    print()

    # Ordenar por velocidade
    sorted_methods = sorted(working_methods.items(), key=lambda x: x[1]['time_ms'])

    for i, (method, data) in enumerate(sorted_methods, 1):
        star = "⭐ RECOMENDADO" if i == 1 else ""
        print(f"  {i}. {method} {star}")
        print(f"     Velocidade: {data['time_ms']:.1f}ms")
        print(f"     Tamanho: {data['size_kb']:.1f}KB")
        print()

    best_method = sorted_methods[0][0]

    print("-" * 70)
    print()
    print(f"🎯 MELHOR OPÇÃO: {best_method}")
    print()

    # Recomendação de arquivo
    if best_method == "MSS":
        print("   Execute: python captura-nvidia.py")
    elif best_method == "D3DShot":
        print("   Execute: python captura-wgc.py")
    elif best_method == "Windows GDI":
        print("   Execute: python captura-gamebar.py")
    elif best_method == "PIL ImageGrab":
        print("   Execute: python captura-simples.py")
        print("   (mas pode ser bloqueado pelo GTA)")

else:
    print("❌ NENHUM MÉTODO FUNCIONOU!")
    print()
    print("Possíveis causas:")
    print("  1. Bibliotecas não instaladas")
    print("  2. Permissões de administrador necessárias")
    print("  3. Problemas com GPU/drivers")
    print()
    print("Instale as dependências:")
    print("  pip install mss d3dshot pywin32")

print()

# Métodos que precisam instalação
needs_install = [k for k, v in results.items() if 'NÃO INSTALADO' in str(v.get('status', ''))]
if needs_install:
    print("-" * 70)
    print()
    print("⚠️  MÉTODOS NÃO TESTADOS (faltam bibliotecas):")
    print()
    for method in needs_install:
        if 'MSS' in method:
            print(f"  • {method}: pip install mss")
        elif 'D3DShot' in method:
            print(f"  • {method}: pip install d3dshot")
        elif 'GDI' in method:
            print(f"  • {method}: pip install pywin32")
    print()

print("=" * 70)
print()
print("💡 PRÓXIMOS PASSOS:")
print()
print("1. Instale as bibliotecas faltantes (se houver)")
print("2. Execute o método recomendado acima")
print("3. Abra o GTA e teste se a captura funciona")
print("4. Se estiver sendo bloqueado, tente o próximo da lista")
print()
print("=" * 70)
