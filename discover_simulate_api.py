"""Discover the simulate API endpoint by capturing ALL requests when clicking Simulate."""
import os
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "screenshots"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 720})
        page = ctx.new_page()
        page.set_default_timeout(30000)

        # Login
        page.goto(DASHBOARD_URL, timeout=60000)
        page.wait_for_timeout(5000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(10000)

        # Go to Heritage
        page.locator('text=Heritage').first.click()
        page.wait_for_timeout(8000)

        # Go to Debug > Msg Simulator
        page.locator('text=Debug').first.click()
        page.wait_for_timeout(2000)
        page.locator('button:has-text("Msg Simulator")').click()
        page.wait_for_timeout(2000)

        # Now capture ALL requests
        all_requests = []
        page.on("request", lambda req: all_requests.append({
            "url": req.url,
            "method": req.method,
            "post": req.post_data[:500] if req.post_data else None,
            "headers": {k: v for k, v in req.headers.items() if k.lower() in ('content-type', 'authorization', 'x-hotel-id')}
        }))

        # Fill message and click Simulate
        inputs = page.locator('input')
        visible = []
        for i in range(inputs.count()):
            inp = inputs.nth(i)
            if inp.is_visible():
                t = (inp.get_attribute('type') or '').lower()
                if t not in ('file', 'hidden', 'checkbox', 'radio', 'email', 'password', 'number'):
                    visible.append(inp)

        print(f"Found {len(visible)} visible text inputs")
        if len(visible) >= 3:
            visible[2].fill("hello, do you have a spa?")
        page.wait_for_timeout(500)

        # Clear captured requests
        all_requests.clear()

        # Click Simulate
        page.locator('button:has-text("Simulate")').first.click()
        page.wait_for_timeout(15000)

        # Print ALL captured requests
        print(f"\nCaptured {len(all_requests)} requests after clicking Simulate:")
        for req in all_requests:
            if 'hotelintelliai' in req['url'] or req['method'] == 'POST':
                print(f"\n  {req['method']} {req['url']}")
                if req['post']:
                    print(f"    Body: {req['post'][:300]}")
                if req['headers']:
                    print(f"    Headers: {req['headers']}")

        # Also check for WebSocket connections
        ws_urls = page.evaluate("""() => {
            return window.__ws_urls || [];
        }""")
        print(f"\nWebSocket URLs: {ws_urls}")

        ctx.close()
        browser.close()


if __name__ == "__main__":
    main()
