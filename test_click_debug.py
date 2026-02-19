"""
Script para debugar problema de cliques no dashboard
"""
from playwright.sync_api import sync_playwright
import time

def test_dashboard_clicks():
    with sync_playwright() as p:
        # Abrir navegador
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Abrir dashboard
        dashboard_path = r'C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\dashboard-tournament.html'
        page.goto(f'file:///{dashboard_path}')

        print("✅ Dashboard aberto")
        time.sleep(2)

        # Verificar se tournamentGrid existe
        grid = page.query_selector('#tournamentGrid')
        if grid:
            print("✅ tournamentGrid encontrado")
        else:
            print("❌ tournamentGrid NÃO encontrado")
            browser.close()
            return

        # Verificar se função handlePlayerBoxClick existe
        has_function = page.evaluate("typeof handlePlayerBoxClick")
        print(f"handlePlayerBoxClick tipo: {has_function}")

        # Esperar um pouco
        time.sleep(1)

        # Tentar encontrar player boxes
        player_boxes = page.query_selector_all('.player-box:not(.empty)')
        print(f"📦 Player boxes encontrados: {len(player_boxes)}")

        if len(player_boxes) > 0:
            # Clicar no primeiro player box
            print(f"\n🖱️ Tentando clicar no primeiro player box...")

            # Habilitar console listener
            page.on('console', lambda msg: print(f"CONSOLE: {msg.text}"))

            # Clicar
            player_boxes[0].click()

            print("✅ Clique executado!")
            time.sleep(2)

            # Verificar se algo mudou
            new_player_boxes = page.query_selector_all('.player-box.alive')
            print(f"📦 Player boxes vivos após clique: {len(new_player_boxes)}")
        else:
            print("❌ Nenhum player box encontrado para clicar")

        # Manter navegador aberto
        print("\n⏸️ Navegador ficará aberto por 30s para você testar manualmente...")
        time.sleep(30)

        browser.close()

if __name__ == "__main__":
    test_dashboard_clicks()
