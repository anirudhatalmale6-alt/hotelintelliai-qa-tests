"""Check what HOTEL ID the simulator auto-populates for each hotel."""
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"

HOTELS = [
    "Imperial Mae Ping Hotel",
    "The Oberoi Udaivilas",
    "The Riverie by Katathani",
    "The Heritage Chiang Rai Hotel and Convention",
    "Grand Vista Chiangrai Hotel",
    "le Patte",
]

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

    for hname in HOTELS:
        # Fresh nav
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
        page.locator(f'text={hname}').first.click()
        page.wait_for_timeout(5000)
        
        # Go to Debug > Msg Simulator
        page.locator('text=Debug').first.click()
        page.wait_for_timeout(3000)
        page.locator('button:has-text("Msg Simulator")').click()
        page.wait_for_timeout(3000)
        
        # Read all visible input values
        inputs = page.locator('input')
        for i in range(inputs.count()):
            inp = inputs.nth(i)
            if inp.is_visible():
                val = inp.input_value() or ''
                ph = inp.get_attribute('placeholder') or ''
                print(f"  [{hname}] Input {i}: value='{val}' placeholder='{ph}'")
        print()

    ctx.close()
    browser.close()
