"""Get the correct hotel collection IDs from the KB pages."""
import re
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
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
        page.locator(f'text={hname}').first.click()
        page.wait_for_timeout(5000)
        
        # Check Overview page for hotel ID
        body = page.locator('body').inner_text()
        # Look for hotel_id patterns
        hotel_ids = re.findall(r'hotel_\w+', body)
        # Also look for "Knowledge base · xxx" pattern
        kb_patterns = re.findall(r'Knowledge base\s*·?\s*(\S+)', body)
        
        # Also check the URL
        current_url = page.url
        
        print(f"{hname}:")
        print(f"  URL: {current_url}")
        if hotel_ids:
            # Deduplicate
            unique_ids = list(dict.fromkeys(hotel_ids))
            print(f"  Hotel IDs found: {unique_ids[:5]}")
        if kb_patterns:
            print(f"  KB patterns: {kb_patterns[:5]}")
        
        # Now check KB page
        page.locator('text=Knowledge Base').first.click()
        page.wait_for_timeout(5000)
        try:
            page.wait_for_selector('text=Loading...', state='hidden', timeout=15000)
        except:
            pass
        
        body = page.locator('body').inner_text()
        hotel_ids = re.findall(r'hotel_\w+', body)
        kb_patterns = re.findall(r'Knowledge base\s*·?\s*(\S+)', body)
        
        # Look for collection name
        for line in body.split('\n'):
            if 'knowledge base' in line.lower() and '·' in line:
                print(f"  KB line: {line.strip()}")
        
        if hotel_ids:
            unique_ids = list(dict.fromkeys(hotel_ids))
            print(f"  KB Hotel IDs: {unique_ids[:5]}")
        print()

    ctx.close()
    browser.close()
