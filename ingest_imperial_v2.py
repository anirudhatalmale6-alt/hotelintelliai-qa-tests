"""
Ingest Imperial Mae Ping and Oberoi - try direct URL navigation
instead of clicking from dashboard (blank page workaround).
"""
import os
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, f"imp2_{name}.png")
    page.screenshot(path=path)
    print(f"  Screenshot: {path}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(45000)

        # Login
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        print("Logged in")

        # Try clicking Imperial Mae Ping with arrow button
        body = page.locator('body').inner_text()

        # Find all arrow/link elements that navigate to hotel dashboard
        # The dashboard shows hotels with an arrow "→" - let's try clicking the right one

        # Method 1: Try clicking the arrow next to Imperial Mae Ping
        # First find all elements, look for pattern near "Imperial"
        all_elements = page.locator('*')

        # Try direct URL patterns - the dashboard might use hash routes or query params
        test_urls = [
            f"{DASHBOARD_URL}/hotel/imperial_mae_ping",
            f"{DASHBOARD_URL}/#/hotel/imperial_mae_ping",
            f"{DASHBOARD_URL}?hotel=imperial_mae_ping",
            f"{DASHBOARD_URL}/imperial_mae_ping",
            f"{DASHBOARD_URL}/#imperial_mae_ping",
        ]

        # First, let's see what URL we get when clicking a working hotel (Heritage)
        print("\nTesting with Heritage (known working)...")
        page.locator('text=Heritage').first.click()
        page.wait_for_timeout(8000)
        heritage_url = page.url
        print(f"Heritage URL: {heritage_url}")
        screenshot(page, "heritage_url_check")

        # Check the sidebar
        sidebar = page.locator('body').inner_text()
        for line in sidebar.split('\n')[:30]:
            if line.strip():
                print(f"  {line.strip()}")

        # Now go back and try Imperial
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(5000)

        # The URL pattern for Heritage might tell us the pattern for Imperial
        # Let's try constructing the Imperial URL based on Heritage pattern
        if 'heritage' in heritage_url.lower() or '/' in heritage_url.replace(DASHBOARD_URL, ''):
            imperial_url = heritage_url.replace('heritage_chiangrai', 'imperial_mae_ping')
            print(f"\nTrying constructed URL: {imperial_url}")
            page.goto(imperial_url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(10000)
            screenshot(page, "imperial_direct_url")

            body2 = page.locator('body').inner_text()
            print(f"Page text: {body2[:500]}")

            if 'Knowledge Base' in body2 or 'Overview' in body2 or 'Debug' in body2:
                print("Imperial loaded via direct URL!")
                # Navigate to KB
                page.locator('text=Knowledge Base').first.click()
                page.wait_for_timeout(3000)
                screenshot(page, "imperial_kb")

                # Click URL tab
                page.locator('button:has-text("URL")').first.click()
                page.wait_for_timeout(2000)

                # Check chunks
                kb_body = page.locator('body').inner_text()
                for line in kb_body.split('\n'):
                    if 'chunk' in line.lower():
                        print(f"  Imperial KB: {line.strip()}")

                # Try ingesting
                urls_to_ingest = [
                    "https://www.imperialmaeping.com",
                    "https://imperialmaeping.com",
                ]

                for url in urls_to_ingest:
                    try:
                        inputs = page.locator('input')
                        for ii in range(inputs.count()):
                            inp = inputs.nth(ii)
                            if inp.is_visible():
                                inp_type = (inp.get_attribute('type') or '').lower()
                                if inp_type not in ('file', 'hidden', 'checkbox', 'radio', 'email', 'password'):
                                    inp.fill(url)
                                    page.wait_for_timeout(500)
                                    try:
                                        page.locator('button:has-text("Scrape")').first.click()
                                        page.wait_for_timeout(15000)
                                        print(f"  Scraped: {url}")
                                        screenshot(page, f"imperial_scraped")
                                    except Exception:
                                        print(f"  Scrape button not found for {url}")
                                    break
                    except Exception as e:
                        print(f"  Error: {e}")
            else:
                print("Direct URL didn't work for Imperial")
                # Try clicking from dashboard with longer wait
                page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(5000)

                # Try clicking the arrow next to Imperial
                # The text shows: "Imperial Mae Ping Hotel\nimperial_mae_ping · Asia/Bangkok\nwhatsapp\nline\nweb\n→"
                # Let's try clicking on the row/card
                try:
                    # Click the hotel card - might be a div container
                    imperial_card = page.locator(':text("Imperial Mae Ping")').first
                    box = imperial_card.bounding_box()
                    if box:
                        # Click to the right of the text (where the arrow might be)
                        page.mouse.click(box['x'] + box['width'] + 50, box['y'] + box['height'] / 2)
                        page.wait_for_timeout(10000)
                        screenshot(page, "imperial_arrow_click")
                        body3 = page.locator('body').inner_text()
                        print(f"After arrow click: {body3[:500]}")
                except Exception as e:
                    print(f"Arrow click failed: {e}")

        # Now try Oberoi with the same URL pattern
        if 'heritage' in heritage_url.lower():
            oberoi_url = heritage_url.replace('heritage_chiangrai', 'oberoi_udaivilas')
            print(f"\n\nTrying Oberoi URL: {oberoi_url}")
            page.goto(oberoi_url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(10000)
            screenshot(page, "oberoi_direct_url")

            body4 = page.locator('body').inner_text()
            print(f"Oberoi page: {body4[:500]}")

            if 'Knowledge Base' in body4 or 'Overview' in body4:
                print("Oberoi loaded!")
                page.locator('text=Knowledge Base').first.click()
                page.wait_for_timeout(3000)

                kb_body2 = page.locator('body').inner_text()
                for line in kb_body2.split('\n'):
                    if 'chunk' in line.lower():
                        print(f"  Oberoi KB: {line.strip()}")
                screenshot(page, "oberoi_kb")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
