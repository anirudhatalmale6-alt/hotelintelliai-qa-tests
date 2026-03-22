"""Check KB status for all hotels - see chunk counts."""
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"

HOTELS = [
    "The Heritage Chiang Rai Hotel and Convention",
    "The Oberoi Udaivilas",
    "Le Patta",
    "The Riverie by Katathani",
    "Grand Vista",
    "Imperial Mae Ping",
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 720})
    page = context.new_page()
    page.set_default_timeout(30000)

    # Login
    page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    page.locator('input[type="email"]').fill(EMAIL)
    page.locator('input[type="password"]').fill(PASSWORD)
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(5000)
    print("Logged in\n")

    for hname in HOTELS:
        print(f"--- {hname} ---")
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(2000)

        try:
            page.locator(f'text={hname}').first.click()
            page.wait_for_timeout(4000)

            # Go to Knowledge Base
            page.locator('text=Knowledge Base').first.click()
            page.wait_for_timeout(3000)

            # Get page text to find chunk count
            body = page.locator('body').inner_text()
            for line in body.split('\n'):
                line = line.strip()
                if any(kw in line.upper() for kw in ['CHUNK', 'DOCUMENT', 'TOTAL']):
                    if line and len(line) < 100:
                        print(f"  {line}")

            page.screenshot(path=f"screenshots/kb_status_{hname.replace(' ','_')[:20]}.png")
        except Exception as e:
            print(f"  ERROR: {e}")

    context.close()
    browser.close()
