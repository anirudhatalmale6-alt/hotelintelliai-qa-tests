"""Retry ingesting Imperial Mae Ping with alternative URLs."""
from playwright.sync_api import sync_playwright
import time

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"

# Try alternative URLs for Imperial Mae Ping
URLS_TO_TRY = [
    "https://imperial-mae-ping-hotel.hotelschiangmai.net/en/",
    "https://www.chiang-maihotels.com/en/property/imperial-mae-ping-hotel.html",
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
    print("Logged in")

    # Navigate to Imperial Mae Ping
    page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(2000)

    # First let's see all hotels on dashboard
    body = page.locator('body').inner_text()
    print("\nDashboard hotels:")
    for line in body.split('\n'):
        line = line.strip()
        if line and len(line) > 3 and len(line) < 80:
            if any(kw in line.lower() for kw in ['hotel', 'oberoi', 'patt', 'vista', 'riverie', 'heritage', 'imperial', 'mae']):
                print(f"  > {line}")

    page.screenshot(path="screenshots/dashboard_hotels_list.png")

    # Click Imperial Mae Ping
    try:
        page.locator('text=Imperial Mae Ping').first.click()
        page.wait_for_timeout(4000)
    except Exception:
        try:
            page.locator('text=Imperial').first.click()
            page.wait_for_timeout(4000)
        except Exception as e:
            print(f"ERROR: Could not find Imperial Mae Ping: {e}")
            context.close()
            browser.close()
            exit(1)

    # Go to KB > URL tab
    page.locator('text=Knowledge Base').first.click()
    page.wait_for_timeout(2000)

    # Click URL tab
    page.locator('button:has-text("URL")').click()
    page.wait_for_timeout(1000)

    for url in URLS_TO_TRY:
        print(f"\nTrying URL: {url}")

        # Fill URL
        url_input = page.locator('input[placeholder*="http"]').first
        url_input.fill(url)
        page.wait_for_timeout(500)

        # Click Scrape
        page.locator('button:has-text("Scrape")').first.click()
        print("  Scrape clicked, waiting 3 minutes...")

        # Wait up to 3 minutes
        for i in range(18):  # 18 * 10s = 180s
            page.wait_for_timeout(10000)
            body = page.locator('body').inner_text()

            # Check for success or completion
            if 'chunks' in body.lower():
                for line in body.split('\n'):
                    line = line.strip()
                    if 'chunk' in line.lower() and len(line) < 100:
                        print(f"  {line}")

            # Check if scraping is done (no more processing indicators)
            if 'scraping started' not in body.lower() and 'processing' not in body.lower():
                if 'no documents yet' not in body.lower():
                    print(f"  Scraping appears complete after {(i+1)*10}s")
                    break
                elif i > 8:  # After 90s if still no docs, move on
                    print(f"  Still no documents after {(i+1)*10}s, trying next URL")
                    break

        page.screenshot(path=f"screenshots/imperial_retry_{URLS_TO_TRY.index(url)+1}.png")

        # Check result
        body = page.locator('body').inner_text()
        if 'no documents yet' not in body.lower():
            for line in body.split('\n'):
                if 'chunk' in line.lower() or 'document' in line.lower() or 'website' in line.lower():
                    if len(line.strip()) < 100:
                        print(f"  RESULT: {line.strip()}")
            print("  SUCCESS - documents ingested!")
            break
        else:
            print("  No documents created, trying next URL...")

    # Final check
    page.screenshot(path="screenshots/imperial_final_kb.png")
    body = page.locator('body').inner_text()
    print(f"\nFinal KB state:")
    for line in body.split('\n'):
        line = line.strip()
        if any(kw in line.upper() for kw in ['CHUNK', 'DOCUMENT', 'TOTAL']):
            if line and len(line) < 100:
                print(f"  {line}")

    context.close()
    browser.close()
