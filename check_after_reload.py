"""Reload each hotel's KB page to check if chunks have been added (scraping might have completed in background)."""
import os
import re
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "/var/lib/freelancer/projects/40298427/screenshots"

HOTELS = [
    {"name": "The Heritage Chiang Rai Hotel and Convention", "id": "heritage_chiangrai"},
    {"name": "Grand Vista Chiangrai Hotel", "id": "grand_vista_chiangrai"},
    {"name": "Imperial Mae Ping Hotel", "id": "imperial_mae_ping"},
    {"name": "The Oberoi Udaivilas", "id": "oberoi_udaivilas"},
    {"name": "le Patte", "id": "lePatte"},
    {"name": "The Riverie by Katathani", "id": "hotel_riviera_cr"},
]

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

    for hotel in HOTELS:
        hid = hotel["id"]
        hname = hotel["name"]

        try:
            # Fresh navigation
            page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)
            page.locator(f'text={hname}').first.click()
            page.wait_for_timeout(5000)
            page.locator('text=Knowledge Base').first.click()
            page.wait_for_timeout(8000)  # Wait longer

            # Wait for loading to finish
            try:
                page.wait_for_selector('text=Loading...', state='hidden', timeout=20000)
            except:
                pass
            page.wait_for_timeout(2000)

            body = page.locator('body').inner_text()
            page.screenshot(path=f"{SCREENSHOT_DIR}/reload_{hid}.png")

            # Extract metrics
            lines = body.split('\n')
            chunks = 0
            docs = 0
            uploads = 0
            for i, line in enumerate(lines):
                s = line.strip()
                if 'TOTAL CHUNKS' in s.upper():
                    if i + 1 < len(lines):
                        nums = re.findall(r'\d+', lines[i+1].strip())
                        if nums:
                            chunks = int(nums[0])
                elif s.upper() == 'DOCUMENTS':
                    if i + 1 < len(lines):
                        nums = re.findall(r'\d+', lines[i+1].strip())
                        if nums:
                            docs = int(nums[0])
                elif 'KB UPLOADS' in s.upper():
                    if i + 1 < len(lines):
                        nums = re.findall(r'\d+', lines[i+1].strip())
                        if nums:
                            uploads = int(nums[0])

            status = "OK" if chunks > 0 else "EMPTY"
            print(f"[{status}] {hname}: {chunks} chunks | {docs} docs | {uploads} uploads")
            
            # Check for document entries
            in_doc_section = False
            for line in lines:
                s = line.strip()
                if 'read-only' in s.lower():
                    in_doc_section = True
                    continue
                if in_doc_section and s and len(s) > 3:
                    if 'no document' in s.lower():
                        print(f"  -> {s}")
                    elif any(c in s.lower() for c in ['.com', 'http', 'url', 'scrape', 'file']):
                        print(f"  -> {s[:100]}")
                    in_doc_section = False

        except Exception as e:
            print(f"ERROR {hname}: {e}")

    context.close()
    browser.close()
