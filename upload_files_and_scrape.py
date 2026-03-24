"""Upload text files to hotel KBs and try URL scraping for working websites."""
import os
import re
import time
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "/var/lib/freelancer/projects/40298427/screenshots"
CONTENT_DIR = "/var/lib/freelancer/projects/40298427/hotel-content"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Hotels to upload files to
FILE_UPLOADS = [
    {"name": "The Oberoi Udaivilas", "id": "oberoi_udaivilas",
     "file": f"{CONTENT_DIR}/oberoi_udaivilas.txt"},
    {"name": "The Riverie by Katathani", "id": "hotel_riviera_cr",
     "file": f"{CONTENT_DIR}/riverie_by_katathani.txt"},
]

# Hotels to try URL scraping (working websites)
URL_SCRAPES = [
    {"name": "The Riverie by Katathani", "id": "hotel_riviera_cr",
     "url": "https://www.theriverie.com"},
    {"name": "The Oberoi Udaivilas", "id": "oberoi_udaivilas",
     "url": "https://www.oberoihotels.com/hotels-in-udaipur-udaivilas-resort"},
]


def get_chunk_count(page):
    body = page.locator('body').inner_text()
    lines = body.split('\n')
    for i, line in enumerate(lines):
        if 'TOTAL CHUNKS' in line.upper():
            nums = re.findall(r'\d+', line)
            if nums:
                return int(nums[0])
            if i + 1 < len(lines):
                nums = re.findall(r'\d+', lines[i+1])
                if nums:
                    return int(nums[0])
    return 0


def navigate_to_hotel_kb(page, hotel_name):
    page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    page.locator(f'text={hotel_name}').first.click()
    page.wait_for_timeout(5000)
    page.locator('text=Knowledge Base').first.click()
    page.wait_for_timeout(5000)
    try:
        page.wait_for_selector('text=Loading...', state='hidden', timeout=15000)
    except:
        pass
    page.wait_for_timeout(2000)


def upload_file(page, hotel_id, file_path):
    """Upload a file through the File tab."""
    # Click File tab
    for sel in ['button:has-text("File")', 'text=📄 File']:
        try:
            el = page.locator(sel).first
            if el.is_visible():
                el.click()
                page.wait_for_timeout(1500)
                break
        except:
            continue

    # Set the file input
    file_input = page.locator('input[type="file"]')
    if file_input.count() > 0:
        file_input.set_input_files(file_path)
        page.wait_for_timeout(2000)
        print(f"    File set: {os.path.basename(file_path)}")

        # Click Upload & Embed
        for sel in ['button:has-text("Upload")', 'button:has-text("Embed")']:
            try:
                btn = page.locator(sel).first
                if btn.is_visible() and btn.is_enabled():
                    btn.click()
                    print(f"    Clicked upload button")
                    return True
            except:
                continue
    else:
        print(f"    ERROR: No file input found")
    return False


def scrape_url(page, hotel_id, url):
    """Trigger URL scraping through URL tab."""
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

    # Find URL input
    inputs = page.locator('input')
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        if not inp.is_visible():
            continue
        ph = (inp.get_attribute('placeholder') or '').lower()
        if 'url' in ph or 'http' in ph or 'hotel' in ph:
            inp.fill(url)
            print(f"    URL filled: {url}")
            break

    page.wait_for_timeout(500)

    # Click Scrape & Embed
    scrape_btn = page.locator('button:has-text("Scrape")')
    if scrape_btn.count() > 0 and scrape_btn.first.is_visible():
        scrape_btn.first.click()
        print(f"    Scrape triggered")
        return True
    return False


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(60000)

        # Login
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(2000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        print("Logged in\n")

        # === STEP 1: Upload files ===
        print("=" * 60)
        print("STEP 1: UPLOADING TEXT FILES")
        print("=" * 60)

        for hotel in FILE_UPLOADS:
            hid = hotel["id"]
            hname = hotel["name"]
            fpath = hotel["file"]

            print(f"\n  {hname} ({hid}):")
            try:
                navigate_to_hotel_kb(page, hname)
                initial = get_chunk_count(page)
                print(f"    Initial chunks: {initial}")

                if upload_file(page, hid, fpath):
                    # Wait for upload to process
                    print(f"    Waiting 30s for upload to process...")
                    page.wait_for_timeout(30000)
                    page.screenshot(path=f"{SCREENSHOT_DIR}/upload_{hid}.png")

                    # Check chunks
                    body = page.locator('body').inner_text()
                    for line in body.split('\n'):
                        ls = line.strip().lower()
                        if any(kw in ls for kw in ['success', 'error', 'fail', 'upload', 'embed', 'chunks']):
                            if len(line.strip()) > 3 and len(line.strip()) < 200:
                                print(f"    MSG: {line.strip()}")
                    
                    chunks = get_chunk_count(page)
                    print(f"    Chunks after upload: {chunks}")
                else:
                    print(f"    Upload failed")

            except Exception as e:
                print(f"    ERROR: {e}")

        # === STEP 2: Try URL scraping ===
        print(f"\n{'='*60}")
        print("STEP 2: URL SCRAPING")
        print("=" * 60)

        for hotel in URL_SCRAPES:
            hid = hotel["id"]
            hname = hotel["name"]
            url = hotel["url"]

            print(f"\n  {hname} ({hid}):")
            try:
                navigate_to_hotel_kb(page, hname)
                initial = get_chunk_count(page)
                print(f"    Current chunks: {initial}")

                if scrape_url(page, hid, url):
                    page.wait_for_timeout(5000)
                    page.screenshot(path=f"{SCREENSHOT_DIR}/scrape_{hid}.png")
                    body = page.locator('body').inner_text()
                    for line in body.split('\n'):
                        ls = line.strip().lower()
                        if any(kw in ls for kw in ['scraping', 'started', 'error', 'fail']):
                            if len(line.strip()) > 3:
                                print(f"    MSG: {line.strip()[:100]}")

            except Exception as e:
                print(f"    ERROR: {e}")

        # === STEP 3: Wait and verify all ===
        print(f"\n{'='*60}")
        print("STEP 3: WAITING 3 MINUTES THEN VERIFYING ALL HOTELS")
        print("=" * 60)
        time.sleep(180)

        ALL_HOTELS = [
            {"name": "The Heritage Chiang Rai Hotel and Convention", "id": "heritage_chiangrai"},
            {"name": "Grand Vista Chiangrai Hotel", "id": "grand_vista_chiangrai"},
            {"name": "Imperial Mae Ping Hotel", "id": "imperial_mae_ping"},
            {"name": "The Oberoi Udaivilas", "id": "oberoi_udaivilas"},
            {"name": "le Patte", "id": "lePatte"},
            {"name": "The Riverie by Katathani", "id": "hotel_riviera_cr"},
        ]

        print("\nFINAL CHUNK COUNTS:")
        for hotel in ALL_HOTELS:
            try:
                navigate_to_hotel_kb(page, hotel["name"])
                chunks = get_chunk_count(page)
                page.screenshot(path=f"{SCREENSHOT_DIR}/final_{hotel['id']}.png")
                status = "OK" if chunks > 0 else "EMPTY"
                print(f"  [{status}] {hotel['name']}: {chunks} chunks")
            except Exception as e:
                print(f"  [ERROR] {hotel['name']}: {e}")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
