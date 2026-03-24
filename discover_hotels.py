"""Discover all hotels in the system and their KB status."""
import os
from playwright.sync_api import sync_playwright

BASE_URL = "https://onboarding.hotelintelliai.com"
DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "screenshots"


def screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    page.screenshot(path=path)
    print(f"  Screenshot: {path}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(30000)

        # Login to onboarding portal
        page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button').nth(1).click()
        page.wait_for_timeout(5000)
        print("Logged in to onboarding portal")

        # Get hotel listing
        body = page.locator('body').inner_text()
        screenshot(page, "HOTELS_listing")

        print("\n=== HOTEL LISTING PAGE ===")
        for line in body.split('\n'):
            line = line.strip()
            if line and len(line) > 2:
                print(f"  {line}")

        # Scroll down to see all hotels
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        screenshot(page, "HOTELS_listing_scrolled")
        body2 = page.locator('body').inner_text()
        # Print any new lines
        for line in body2.split('\n'):
            line = line.strip()
            if line and len(line) > 2 and line not in body:
                print(f"  (scrolled) {line}")

        # Now get all hotel links/cards
        print("\n=== FINDING HOTEL IDs ===")
        links = page.locator('a')
        hotel_ids = set()
        for i in range(links.count()):
            href = links.nth(i).get_attribute('href') or ''
            if '/hotel/' in href:
                parts = href.split('/hotel/')
                if len(parts) > 1:
                    hotel_id = parts[1].split('/')[0]
                    if hotel_id:
                        hotel_ids.add(hotel_id)
                        print(f"  Found hotel ID: {hotel_id} (href: {href})")

        print(f"\nTotal hotels found: {len(hotel_ids)}")
        print(f"Hotel IDs: {sorted(hotel_ids)}")

        # For each hotel, check KB stats
        print("\n=== KB STATUS PER HOTEL ===")
        for hotel_id in sorted(hotel_ids):
            print(f"\n--- {hotel_id} ---")
            page.goto(f"{BASE_URL}/hotel/{hotel_id}/kb", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)

            body = page.locator('body').inner_text()
            screenshot(page, f"HOTELS_kb_{hotel_id}")

            # Extract key stats
            lines = body.split('\n')
            for idx, line in enumerate(lines):
                line = line.strip()
                if any(kw in line.upper() for kw in ['TOTAL CHUNKS', 'DOCUMENTS', 'KB VERSION', 'CHUNKS']):
                    # Get the value (usually next line)
                    if idx + 1 < len(lines):
                        print(f"  {line}: {lines[idx+1].strip()}")
                    else:
                        print(f"  {line}")

            # List documents
            print(f"  Documents:")
            for line in lines:
                line = line.strip()
                if 'chunks' in line.lower() and '·' in line:
                    print(f"    {line}")
                elif line.startswith('website') or line.startswith('file') or line.startswith('faq') or line.startswith('paste'):
                    continue  # Skip type-only lines

        # Now check dashboard for hotel names and subdomain IDs
        print("\n=== DASHBOARD HOTEL CARDS ===")
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)

        body = page.locator('body').inner_text()
        screenshot(page, "HOTELS_dashboard")

        print("Dashboard content:")
        for line in body.split('\n'):
            line = line.strip()
            if line and len(line) > 2:
                print(f"  {line}")

        # Scroll to see all
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        screenshot(page, "HOTELS_dashboard_scrolled")

        context.close()
        browser.close()
        print("\n=== DONE ===")


if __name__ == "__main__":
    main()
