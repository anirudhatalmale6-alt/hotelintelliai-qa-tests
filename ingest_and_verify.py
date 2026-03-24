"""
Phase 1: Trigger scraping for all 6 hotels
Phase 2: Wait, then verify chunk counts
"""
import os
import re
import time
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

def get_chunk_count(page):
    body = page.locator('body').inner_text()
    # Look for the TOTAL CHUNKS section with a number
    lines = body.split('\n')
    for i, line in enumerate(lines):
        if 'TOTAL CHUNKS' in line.upper():
            # The number might be on this line or the next
            nums = re.findall(r'\d+', line)
            if nums:
                return int(nums[0])
            if i + 1 < len(lines):
                nums = re.findall(r'\d+', lines[i+1])
                if nums:
                    return int(nums[0])
    # Fallback
    matches = re.findall(r'(\d+)\s*(?:chunks?|documents?)', body.lower())
    if matches:
        return int(matches[0])
    return 0

def main():
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
        print("Logged in\n")

        # ===== PHASE 1: Trigger all scrapes =====
        print("=" * 60)
        print("PHASE 1: TRIGGERING SCRAPES FOR ALL HOTELS")
        print("=" * 60)

        for hotel in HOTELS:
            hid = hotel["id"]
            hname = hotel["name"]
            url = hotel["url"]

            print(f"\n  Scraping: {hname} -> {url}")

            try:
                # Go to dashboard
                page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(3000)

                # Click hotel
                page.locator(f'text={hname}').first.click()
                page.wait_for_timeout(5000)

                # Click Knowledge Base
                page.locator('text=Knowledge Base').first.click()
                page.wait_for_timeout(3000)

                # Check initial chunks
                initial = get_chunk_count(page)
                print(f"    Initial chunks: {initial}")

                if initial > 0:
                    print(f"    SKIP - Already has {initial} chunks")
                    continue

                # Click URL tab
                for sel in ['button:has-text("URL")', 'text=🌐 URL']:
                    try:
                        el = page.locator(sel).first
                        if el.is_visible():
                            el.click()
                            page.wait_for_timeout(1500)
                            break
                    except:
                        continue

                # Fill URL
                url_input = page.locator('input').filter(has_text="").first
                # Find input by placeholder
                inputs = page.locator('input')
                for i in range(inputs.count()):
                    inp = inputs.nth(i)
                    if not inp.is_visible():
                        continue
                    ph = (inp.get_attribute('placeholder') or '').lower()
                    if 'url' in ph or 'hotel' in ph or 'http' in ph or 'website' in ph:
                        inp.fill(url)
                        print(f"    Filled URL (placeholder: {ph[:40]})")
                        break

                page.wait_for_timeout(500)

                # Click Scrape & Embed
                scrape_btn = page.locator('button:has-text("Scrape")')
                if scrape_btn.count() > 0 and scrape_btn.first.is_visible():
                    scrape_btn.first.click()
                    print(f"    Scrape triggered!")
                    page.wait_for_timeout(5000)  # Brief wait to confirm it started
                    
                    # Check for immediate error
                    body = page.locator('body').inner_text()
                    if 'error' in body.lower() and ('scrape' in body.lower() or 'fail' in body.lower()):
                        for line in body.split('\n'):
                            if 'error' in line.lower() or 'fail' in line.lower():
                                print(f"    !! {line.strip()[:100]}")
                    elif 'scraping started' in body.lower() or 'processing' in body.lower():
                        print(f"    Confirmed: scraping started")
                else:
                    print(f"    ERROR: Scrape button not found")

                page.screenshot(path=f"{SCREENSHOT_DIR}/ph1_{hid}.png")

            except Exception as e:
                print(f"    ERROR: {e}")

        # ===== PHASE 2: Wait and verify =====
        print(f"\n\n{'='*60}")
        print("PHASE 2: WAITING 3 MINUTES FOR SCRAPING TO COMPLETE...")
        print(f"{'='*60}")
        time.sleep(180)

        print("\nVerifying chunk counts for all hotels...\n")
        results = {}

        for hotel in HOTELS:
            hid = hotel["id"]
            hname = hotel["name"]

            try:
                page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(3000)
                page.locator(f'text={hname}').first.click()
                page.wait_for_timeout(5000)
                page.locator('text=Knowledge Base').first.click()
                page.wait_for_timeout(3000)

                chunks = get_chunk_count(page)
                page.screenshot(path=f"{SCREENSHOT_DIR}/ph2_{hid}_chunks.png")

                # Also get documents count and KB uploads count
                body = page.locator('body').inner_text()
                docs = 0
                uploads = 0
                lines = body.split('\n')
                for i, line in enumerate(lines):
                    if 'DOCUMENTS' in line.upper() and 'NO DOCUMENTS' not in line.upper():
                        nums = re.findall(r'\d+', line)
                        if nums:
                            docs = int(nums[0])
                        elif i + 1 < len(lines):
                            nums = re.findall(r'\d+', lines[i+1])
                            if nums:
                                docs = int(nums[0])
                    if 'KB UPLOADS' in line.upper() or 'UPLOAD' in line.upper():
                        nums = re.findall(r'\d+', line)
                        if nums:
                            uploads = int(nums[0])

                results[hid] = {"name": hname, "chunks": chunks, "docs": docs}
                print(f"  {hname}: {chunks} chunks, {docs} docs")

            except Exception as e:
                print(f"  {hname}: ERROR - {e}")
                results[hid] = {"name": hname, "chunks": 0, "error": str(e)[:100]}

        # Summary
        print(f"\n{'='*60}")
        print("FINAL SUMMARY")
        print(f"{'='*60}")
        total_chunks = 0
        for hid, data in results.items():
            c = data.get("chunks", 0)
            total_chunks += c
            status = "OK" if c > 0 else "EMPTY"
            print(f"  [{status}] {data['name']}: {c} chunks")
        print(f"\n  Total chunks across all hotels: {total_chunks}")

        context.close()
        browser.close()

if __name__ == "__main__":
    main()
