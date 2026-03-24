"""Check all hotels in the system and their KB status."""
import os
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "/var/lib/freelancer/projects/40298427/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 720})
    page = context.new_page()
    page.set_default_timeout(30000)

    # Login
    page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(2000)
    page.locator('input[type="email"]').fill(EMAIL)
    page.locator('input[type="password"]').fill(PASSWORD)
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(5000)
    page.screenshot(path=f"{SCREENSHOT_DIR}/dashboard_hotels.png")

    # Get the page text to find all hotels
    body = page.locator('body').inner_text()
    print("=== DASHBOARD PAGE TEXT ===")
    print(body[:3000])
    print("===========================")

    # Look for hotel cards/links
    # Try to find all clickable hotel elements
    hotel_links = page.locator('a, button, [role="button"], div[class*="hotel"], div[class*="card"]')
    count = hotel_links.count()
    print(f"\nFound {count} potential hotel elements")

    for i in range(min(count, 50)):
        el = hotel_links.nth(i)
        text = el.inner_text().strip()[:100] if el.is_visible() else ""
        if text and len(text) > 3:
            tag = el.evaluate("el => el.tagName")
            href = el.get_attribute("href") or ""
            print(f"  [{tag}] {text[:80]} | href={href[:60]}")

    context.close()
    browser.close()
