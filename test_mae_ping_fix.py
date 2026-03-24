"""Quick test: Try imperial_mae_ping as HOTEL ID for Imperial Mae Ping."""
import os
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "/var/lib/freelancer/projects/40298427/screenshots/v7"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    page.set_default_timeout(60000)

    page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(2000)
    page.locator('input[type="email"]').fill(EMAIL)
    page.locator('input[type="password"]').fill(PASSWORD)
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(5000)

    # Navigate to Imperial Mae Ping > Debug > Msg Simulator
    page.locator('text=Imperial Mae Ping').first.click()
    page.wait_for_timeout(5000)
    page.locator('text=Debug').first.click()
    page.wait_for_timeout(3000)
    page.locator('button:has-text("Msg Simulator")').click()
    page.wait_for_timeout(3000)

    inputs = page.locator('input')
    visible = []
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        if inp.is_visible():
            itype = (inp.get_attribute('type') or '').lower()
            if itype not in ('email','password','file','hidden','checkbox','radio','number'):
                visible.append(inp)

    # Set HOTEL ID to imperial_mae_ping (subdomain format)
    visible[0].click(click_count=3)
    visible[0].fill("imperial_mae_ping")
    
    # Set message
    visible[2].click(click_count=3)
    visible[2].fill("What time is check-in and check-out?")
    page.wait_for_timeout(500)

    print(f"HOTEL ID: {visible[0].input_value()}")
    print(f"MESSAGE: {visible[2].input_value()}")

    # Click Simulate
    page.locator('button:has-text("Simulate")').first.click()
    page.wait_for_timeout(15000)
    
    page.screenshot(path=f"{SCREENSHOT_DIR}/mae_ping_fix_test.png")
    
    body = page.locator('body').inner_text()
    # Find response
    lines = body.split('\n')
    for i, line in enumerate(lines):
        if 'AGENT RESPONSE' in line.upper() or 'not found' in line.lower() or 'error' in line.lower():
            print(f">> {line.strip()}")
            # Print next few lines
            for j in range(1, 5):
                if i+j < len(lines) and lines[i+j].strip():
                    print(f"   {lines[i+j].strip()[:150]}")

    ctx.close()
    browser.close()
