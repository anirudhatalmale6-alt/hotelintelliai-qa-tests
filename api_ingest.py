"""
Try to ingest KB data via API directly for Imperial and Oberoi.
Discover API endpoints by monitoring network traffic on a working hotel.
"""
import os
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(30000)

        # Capture all network requests
        api_requests = []
        page.on("request", lambda req: api_requests.append({
            "url": req.url,
            "method": req.method,
            "post_data": req.post_data[:500] if req.post_data else None,
        }) if 'api' in req.url.lower() or 'scrape' in req.url.lower() or 'kb' in req.url.lower() or 'ingest' in req.url.lower() or 'embed' in req.url.lower() else None)

        # Login
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        print("Logged in")

        # Navigate to Heritage (working hotel) KB
        page.goto("https://heritage_chiangrai.hotelintelliai.com/", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(5000)

        page.locator('text=Knowledge Base').first.click()
        page.wait_for_timeout(3000)

        # Click URL tab
        page.locator('button:has-text("URL")').first.click()
        page.wait_for_timeout(2000)

        # Clear requests so far
        api_requests.clear()

        # Now do a scrape and capture the API call
        inputs = page.locator('input')
        for i in range(inputs.count()):
            inp = inputs.nth(i)
            if inp.is_visible():
                inp_type = (inp.get_attribute('type') or '').lower()
                if inp_type not in ('file', 'hidden', 'checkbox', 'radio', 'email', 'password'):
                    inp.fill("https://www.heritagechiangrai.com/about")
                    page.wait_for_timeout(500)
                    break

        # Click scrape and capture network
        page.locator('button:has-text("Scrape")').first.click()
        page.wait_for_timeout(10000)

        print(f"\nCaptured {len(api_requests)} API requests:")
        for req in api_requests:
            print(f"  {req['method']} {req['url']}")
            if req['post_data']:
                print(f"    POST data: {req['post_data']}")

        # Also capture all XHR from the page load
        print("\n\nNow capturing all network calls for KB page load...")
        all_requests = []
        page.on("request", lambda req: all_requests.append({
            "url": req.url,
            "method": req.method,
        }))

        page.reload()
        page.wait_for_timeout(8000)

        # Filter interesting requests
        for req in all_requests:
            url = req['url']
            if any(kw in url.lower() for kw in ['api', 'scrape', 'kb', 'hotel', 'chunk', 'embed', 'ingest', 'document']):
                print(f"  {req['method']} {url}")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
