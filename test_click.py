from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # Open dashboard
    page.goto('file:///C:/Users/paulo/OneDrive/Desktop/gta-analytics-v2/dashboard-tournament.html')
    
    # Wait for connection
    time.sleep(2)
    
    # Check if we see player boxes
    player_boxes = page.locator('.player-box').all()
    print(f"Found {len(player_boxes)} player boxes")
    
    if len(player_boxes) > 0:
        # Try to click the first one
        print("Clicking first player box...")
        player_boxes[0].click()
        time.sleep(1)
        
        # Check console logs
        print("Checking for console messages...")
    
    # Take screenshot
    page.screenshot(path='dashboard_screenshot.png')
    print("Screenshot saved to dashboard_screenshot.png")
    
    time.sleep(5)
    browser.close()
