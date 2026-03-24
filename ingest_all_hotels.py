"""
Ingest website URLs for all 6 hotels into their Knowledge Base.
Steps per hotel: Navigate to hotel > Knowledge Base > URL tab > Enter URL > Scrape & Embed
"""
import os
import re
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "/var/lib/freelancer/projects/40298427/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

HOTELS = [
    {"name": "The Heritage Chiang Rai Hotel and Convention", "id": "heritage_chiangrai",
     "url": "https://www.theheritage-chiangrai.com"},
    {"name": "Grand Vista Chiangrai Hotel", "id": "grand_vista_chiangrai",
     "url": "https://www.grandvistachiangrai.com"},
    {"name": "Imperial Mae Ping Hotel", "id": "imperial_mae_ping",
     "url": "https://www.imperialmaeping.com"},
    {"name": "The Oberoi Udaivilas", "id": "oberoi_udaivilas",
     "url": "https://www.oberoihotels.com/hotels-in-udaipur-udaivilas-resort"},
    {"name": "le Patte", "id": "lePatte",
     "url": "https://www.lepatte.com"},
    {"name": "The Riverie by Katathani", "id": "hotel_riviera_cr",
     "url": "https://www.theriverie.com"},
]

def screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, f"ingest_{name}.png")
    page.screenshot(path=path)

def get_chunk_count(page):
    body = page.locator('body').inner_text()
    matches = re.findall(r'(\d+)\s*(?:chunks?|documents?|vectors?)', body.lower())
    if matches:
        return int(matches[0])
    matches = re.findall(r'total[:\s]*(\d+)', body.lower())
    if matches:
        return int(matches[0])
    return -1

def main():
    results = {}
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
        print("Logged in to dashboard\n")

        for hotel in HOTELS:
            hid = hotel["id"]
            hname = hotel["name"]
            url = hotel["url"]

            print(f"\n{'='*60}")
            print(f"HOTEL: {hname} ({hid})")
            print(f"URL: {url}")
            print(f"{'='*60}")

            try:
                # Navigate to hotel
                page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(3000)
                page.locator(f'text={hname}').first.click()
                page.wait_for_timeout(5000)

                # Navigate to Knowledge Base
                page.locator('text=Knowledge Base').first.click()
                page.wait_for_timeout(3000)
                screenshot(page, f"{hid}_kb")

                # Check initial chunks
                initial_chunks = get_chunk_count(page)
                print(f"  Initial chunks: {initial_chunks}")

                # Click URL tab
                url_tab_clicked = False
                for sel in ['button:has-text("URL")', 'text=🌐 URL', '[class*="tab"]:has-text("URL")']:
                    try:
                        el = page.locator(sel).first
                        if el.is_visible():
                            el.click()
                            page.wait_for_timeout(1500)
                            url_tab_clicked = True
                            break
                    except:
                        continue

                if not url_tab_clicked:
                    print(f"  ERROR: Could not click URL tab")
                    results[hid] = {"status": "FAILED", "error": "URL tab not found"}
                    continue

                screenshot(page, f"{hid}_url_tab")

                # Find and fill URL input
                url_filled = False
                inputs = page.locator('input')
                for i in range(inputs.count()):
                    inp = inputs.nth(i)
                    if not inp.is_visible():
                        continue
                    placeholder = (inp.get_attribute('placeholder') or '').lower()
                    inp_type = (inp.get_attribute('type') or '').lower()
                    if inp_type in ('email', 'password', 'file', 'hidden', 'checkbox', 'radio', 'number'):
                        continue
                    if 'url' in placeholder or 'http' in placeholder or 'website' in placeholder or 'enter' in placeholder or 'scrape' in placeholder:
                        inp.fill(url)
                        url_filled = True
                        print(f"  Filled URL in input with placeholder: '{placeholder}'")
                        break

                if not url_filled:
                    # Try first visible text input
                    for i in range(inputs.count()):
                        inp = inputs.nth(i)
                        if inp.is_visible():
                            inp_type = (inp.get_attribute('type') or '').lower()
                            if inp_type not in ('email', 'password', 'file', 'hidden', 'checkbox', 'radio', 'number'):
                                val = inp.input_value()
                                if not val or 'hotel' not in val.lower():
                                    inp.fill(url)
                                    url_filled = True
                                    print(f"  Filled URL in first available input")
                                    break

                if not url_filled:
                    print(f"  ERROR: Could not find URL input")
                    results[hid] = {"status": "FAILED", "error": "URL input not found"}
                    continue

                page.wait_for_timeout(1000)
                screenshot(page, f"{hid}_url_filled")

                # Click Scrape/Embed button
                btn_clicked = False
                for sel in ['button:has-text("Scrape")', 'button:has-text("Embed")', 'button:has-text("Ingest")',
                            'button:has-text("Add URL")', 'button:has-text("Add")', 'button:has-text("Submit")',
                            'button:has-text("Fetch")', 'button:has-text("Load")']:
                    try:
                        btn = page.locator(sel).first
                        if btn.is_visible() and btn.is_enabled():
                            btn.click()
                            btn_clicked = True
                            print(f"  Clicked: {sel}")
                            break
                    except:
                        continue

                if not btn_clicked:
                    print(f"  ERROR: Could not find action button")
                    # Print all visible buttons for debugging
                    btns = page.locator('button')
                    for i in range(btns.count()):
                        b = btns.nth(i)
                        if b.is_visible():
                            print(f"    Button: '{b.inner_text().strip()[:50]}'")
                    results[hid] = {"status": "FAILED", "error": "Action button not found"}
                    continue

                # Wait for ingestion (can take 30-90 seconds)
                print(f"  Waiting for ingestion (60s)...")
                page.wait_for_timeout(60000)
                screenshot(page, f"{hid}_after_ingest")

                # Check for messages
                body = page.locator('body').inner_text()
                for line in body.split('\n'):
                    line_s = line.strip()
                    if any(kw in line_s.lower() for kw in ['success', 'error', 'fail', 'chunks', 'scraped', 'embedded', 'complete']):
                        if len(line_s) > 3 and len(line_s) < 200:
                            print(f"  MSG: {line_s}")

                # Check final chunks
                final_chunks = get_chunk_count(page)
                print(f"  Final chunks: {final_chunks}")

                results[hid] = {
                    "status": "OK",
                    "url": url,
                    "initial_chunks": initial_chunks,
                    "final_chunks": final_chunks,
                }

            except Exception as e:
                print(f"  ERROR: {e}")
                screenshot(page, f"{hid}_error")
                results[hid] = {"status": "FAILED", "error": str(e)[:200]}

        context.close()
        browser.close()

    # Summary
    print(f"\n\n{'='*60}")
    print("INGESTION SUMMARY")
    print(f"{'='*60}")
    for hid, data in results.items():
        hname = next((h["name"] for h in HOTELS if h["id"] == hid), hid)
        status = data.get("status", "?")
        init = data.get("initial_chunks", "?")
        final = data.get("final_chunks", "?")
        err = data.get("error", "")
        print(f"  {hname}: {status} | Chunks: {init} -> {final} {err}")

if __name__ == "__main__":
    main()
