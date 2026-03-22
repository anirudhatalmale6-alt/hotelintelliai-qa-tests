"""
Ingest missing hotel websites into KB via the dashboard URL tab.
Hotels: Grand Vista Chiang Rai, Imperial Mae Ping
"""
import time
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"

HOTELS_TO_INGEST = [
    {
        "name": "Grand Vista",
        "urls": [
            "https://grand-vista-chiangrai.gochiangraihotels.com/en/",
        ]
    },
    {
        "name": "Imperial Mae Ping",
        "urls": [
            "https://chiangmai.intercontinental.com/en",
            "https://chiangmai.intercontinental.com/en/the-hotel",
        ]
    },
]


def main():
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
        page.screenshot(path="screenshots/ingest_login.png")
        print("Logged in to dashboard")

        for hotel in HOTELS_TO_INGEST:
            hname = hotel["name"]
            print(f"\n{'='*50}")
            print(f"Processing: {hname}")
            print(f"{'='*50}")

            # Navigate to dashboard home
            page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)

            # Click on the hotel
            hotel_link = page.locator(f'text={hname}').first
            if hotel_link.count() == 0:
                print(f"  ERROR: Could not find hotel '{hname}' on dashboard")
                # Try partial match
                all_text = page.locator('body').inner_text()
                print(f"  Page text (first 500): {all_text[:500]}")
                page.screenshot(path=f"screenshots/ingest_{hname.replace(' ','_')}_notfound.png")
                continue

            hotel_link.click()
            page.wait_for_timeout(5000)
            page.screenshot(path=f"screenshots/ingest_{hname.replace(' ','_')}_hotel.png")

            # Navigate to Knowledge Base
            kb_link = page.locator('text=Knowledge Base').first
            if kb_link.count() == 0:
                print(f"  ERROR: Could not find Knowledge Base link")
                continue
            kb_link.click()
            page.wait_for_timeout(3000)
            page.screenshot(path=f"screenshots/ingest_{hname.replace(' ','_')}_kb.png")

            # Click on URL tab
            url_tab_selectors = [
                'button:has-text("URL")',
                'text=🌐 URL',
                '[class*="tab"]:has-text("URL")',
            ]
            url_tab_clicked = False
            for sel in url_tab_selectors:
                try:
                    tab = page.locator(sel).first
                    if tab.count() > 0 and tab.is_visible():
                        tab.click()
                        url_tab_clicked = True
                        print(f"  Clicked URL tab via: {sel}")
                        break
                except Exception:
                    continue

            if not url_tab_clicked:
                print(f"  ERROR: Could not click URL tab")
                continue

            page.wait_for_timeout(2000)
            page.screenshot(path=f"screenshots/ingest_{hname.replace(' ','_')}_urltab.png")

            # Get current chunk count
            body_text = page.locator('body').inner_text()
            print(f"  Current KB state (looking for chunks)...")

            # For each URL, ingest it
            for url in hotel["urls"]:
                print(f"\n  Ingesting URL: {url}")

                # Find URL input field
                url_input = None
                for sel in ['input[type="url"]', 'input[placeholder*="url" i]', 'input[placeholder*="URL"]', 'input[placeholder*="http"]', 'input[placeholder*="Enter"]']:
                    try:
                        inp = page.locator(sel).first
                        if inp.count() > 0 and inp.is_visible():
                            url_input = inp
                            print(f"    Found URL input via: {sel}")
                            break
                    except Exception:
                        continue

                if not url_input:
                    # Try all visible text inputs
                    inputs = page.locator('input[type="text"], input:not([type])')
                    for i in range(inputs.count()):
                        inp = inputs.nth(i)
                        if inp.is_visible():
                            placeholder = inp.get_attribute('placeholder') or ''
                            if any(kw in placeholder.lower() for kw in ['url', 'http', 'web', 'site', 'enter', 'scrape']):
                                url_input = inp
                                print(f"    Found URL input via placeholder: {placeholder}")
                                break

                if not url_input:
                    # Just try the first visible input on the URL tab
                    inputs = page.locator('input')
                    for i in range(inputs.count()):
                        inp = inputs.nth(i)
                        if inp.is_visible():
                            inp_type = (inp.get_attribute('type') or '').lower()
                            if inp_type not in ('email', 'password', 'file', 'hidden', 'checkbox', 'radio', 'number'):
                                url_input = inp
                                print(f"    Using first available input")
                                break

                if not url_input:
                    print(f"    ERROR: Could not find URL input")
                    page.screenshot(path=f"screenshots/ingest_{hname.replace(' ','_')}_no_input.png")
                    continue

                # Fill URL
                url_input.fill(url)
                page.wait_for_timeout(1000)

                # Look for scrape/submit button
                submit_btn = None
                for sel in [
                    'button:has-text("Scrape")',
                    'button:has-text("Embed")',
                    'button:has-text("Add")',
                    'button:has-text("Ingest")',
                    'button:has-text("Submit")',
                    'button:has-text("Upload")',
                    'button:has-text("Fetch")',
                ]:
                    try:
                        btn = page.locator(sel).first
                        if btn.count() > 0 and btn.is_visible():
                            disabled = btn.get_attribute('disabled')
                            if disabled is None:
                                submit_btn = btn
                                print(f"    Found submit button via: {sel}")
                                break
                    except Exception:
                        continue

                if not submit_btn:
                    print(f"    ERROR: Could not find submit button")
                    page.screenshot(path=f"screenshots/ingest_{hname.replace(' ','_')}_no_btn.png")
                    continue

                # Click and wait for processing
                page.screenshot(path=f"screenshots/ingest_{hname.replace(' ','_')}_before_scrape.png")
                submit_btn.click()
                print(f"    Clicked submit, waiting for scrape/embedding...")

                # Wait up to 120 seconds for processing
                page.wait_for_timeout(30000)
                page.screenshot(path=f"screenshots/ingest_{hname.replace(' ','_')}_after_30s.png")

                # Check if still processing
                body = page.locator('body').inner_text()
                if any(kw in body.lower() for kw in ['processing', 'embedding', 'loading', 'progress', 'scraping']):
                    print(f"    Still processing, waiting more...")
                    page.wait_for_timeout(60000)
                    page.screenshot(path=f"screenshots/ingest_{hname.replace(' ','_')}_after_90s.png")

                # Check result
                body = page.locator('body').inner_text()
                if 'error' in body.lower() and 'chunk' not in body.lower():
                    print(f"    WARNING: Possible error in result")

                # Look for chunk count or success message
                for line in body.split('\n'):
                    line = line.strip()
                    if any(kw in line.lower() for kw in ['chunk', 'document', 'embed', 'success', 'added', 'scraped']):
                        print(f"    >> {line}")

                page.screenshot(path=f"screenshots/ingest_{hname.replace(' ','_')}_result.png")
                print(f"    Done with URL: {url}")

            print(f"\n  Finished ingesting {hname}")

        context.close()
        browser.close()
        print("\n\nAll ingestion complete!")


if __name__ == "__main__":
    main()
