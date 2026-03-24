"""Verify chunk counts for all hotels after waiting for scraping to complete."""
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
            page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)
            page.locator(f'text={hname}').first.click()
            page.wait_for_timeout(5000)
            page.locator('text=Knowledge Base').first.click()
            page.wait_for_timeout(5000)  # Wait longer for KB to load

            # Wait for "Loading..." to disappear
            try:
                page.wait_for_selector('text=Loading...', state='hidden', timeout=15000)
            except:
                pass
            page.wait_for_timeout(2000)

            page.screenshot(path=f"{SCREENSHOT_DIR}/verify_{hid}.png")

            body = page.locator('body').inner_text()
            
            # Extract TOTAL CHUNKS, DOCUMENTS, KB UPLOADS values
            lines = body.split('\n')
            chunks = 0
            docs = 0
            uploads = 0
            
            for i, line in enumerate(lines):
                stripped = line.strip().upper()
                if 'TOTAL CHUNKS' in stripped:
                    # Number could be on same line or next line
                    nums = re.findall(r'\d+', stripped)
                    if nums:
                        chunks = int(nums[0])
                    elif i + 1 < len(lines):
                        nums = re.findall(r'\d+', lines[i+1].strip())
                        if nums:
                            chunks = int(nums[0])
                elif 'DOCUMENTS' in stripped and 'NO DOCUMENTS' not in stripped:
                    nums = re.findall(r'\d+', stripped)
                    if nums:
                        docs = int(nums[0])
                    elif i + 1 < len(lines):
                        nums = re.findall(r'\d+', lines[i+1].strip())
                        if nums:
                            docs = int(nums[0])
                elif 'KB UPLOADS' in stripped:
                    nums = re.findall(r'\d+', stripped)
                    if nums:
                        uploads = int(nums[0])
                    elif i + 1 < len(lines):
                        nums = re.findall(r'\d+', lines[i+1].strip())
                        if nums:
                            uploads = int(nums[0])

            print(f"{hname}:")
            print(f"  Chunks: {chunks} | Documents: {docs} | Uploads: {uploads}")
            
            # Also print any document entries in the DOCUMENTS section
            in_docs = False
            for line in lines:
                stripped = line.strip()
                if 'DOCUMENTS' in stripped.upper():
                    in_docs = True
                    continue
                if in_docs and stripped and len(stripped) > 5:
                    if any(kw in stripped.lower() for kw in ['no document', 'upload file', 'add url', 'create faq']):
                        print(f"  -> {stripped[:100]}")
                        in_docs = False
                    elif any(kw in stripped.lower() for kw in ['.com', '.org', '.net', 'http', 'url', 'file', 'faq', 'scrape']):
                        print(f"  -> Doc: {stripped[:100]}")

        except Exception as e:
            print(f"{hname}: ERROR - {e}")

    context.close()
    browser.close()
