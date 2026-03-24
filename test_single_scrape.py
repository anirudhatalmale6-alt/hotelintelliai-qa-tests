"""Test scraping a single hotel and monitor the process closely."""
import os
import re
import time
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "/var/lib/freelancer/projects/40298427/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

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
    print("Logged in")

    # Go to Heritage Chiang Rai
    page.locator('text=The Heritage Chiang Rai').first.click()
    page.wait_for_timeout(5000)

    # KB
    page.locator('text=Knowledge Base').first.click()
    page.wait_for_timeout(5000)
    
    # Wait for loading
    try:
        page.wait_for_selector('text=Loading...', state='hidden', timeout=15000)
    except:
        pass
    page.wait_for_timeout(2000)
    
    # Screenshot initial state
    page.screenshot(path=f"{SCREENSHOT_DIR}/test_scrape_initial.png")
    body = page.locator('body').inner_text()
    print("\n=== KB PAGE (initial) ===")
    print(body[:2000])
    
    # Click URL tab
    for sel in ['button:has-text("URL")', 'text=🌐 URL']:
        try:
            el = page.locator(sel).first
            if el.is_visible():
                el.click()
                page.wait_for_timeout(2000)
                print(f"\nClicked URL tab: {sel}")
                break
        except:
            continue
    
    page.screenshot(path=f"{SCREENSHOT_DIR}/test_scrape_url_tab.png")
    body = page.locator('body').inner_text()
    print("\n=== URL TAB ===")
    print(body[:2000])
    
    # List all visible inputs
    inputs = page.locator('input')
    print(f"\n=== ALL INPUTS ({inputs.count()}) ===")
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        if inp.is_visible():
            ph = inp.get_attribute('placeholder') or ''
            val = inp.input_value() or ''
            itype = inp.get_attribute('type') or ''
            name = inp.get_attribute('name') or ''
            print(f"  [{i}] type={itype} name={name} placeholder='{ph}' value='{val}'")
    
    # List all visible buttons
    btns = page.locator('button')
    print(f"\n=== ALL BUTTONS ({btns.count()}) ===")
    for i in range(btns.count()):
        btn = btns.nth(i)
        if btn.is_visible():
            txt = btn.inner_text().strip()[:60]
            disabled = btn.get_attribute('disabled')
            print(f"  [{i}] '{txt}' disabled={disabled}")
    
    # Fill URL
    url = "https://www.theheritage-chiangrai.com"
    inputs_visible = []
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        if inp.is_visible():
            ph = (inp.get_attribute('placeholder') or '').lower()
            itype = (inp.get_attribute('type') or '').lower()
            if itype not in ('email', 'password', 'file', 'hidden', 'checkbox', 'radio'):
                inputs_visible.append((i, inp, ph))
    
    # Fill the URL input (should have placeholder with 'url' or 'hotel')
    for idx, inp, ph in inputs_visible:
        if 'url' in ph or 'hotel' in ph or 'http' in ph:
            inp.fill(url)
            print(f"\nFilled input [{idx}] with URL (ph: {ph})")
            break
    
    page.wait_for_timeout(1000)
    page.screenshot(path=f"{SCREENSHOT_DIR}/test_scrape_filled.png")
    
    # Click Scrape & Embed
    scrape_btn = page.locator('button:has-text("Scrape")')
    if scrape_btn.count() > 0:
        print(f"\nScrape button found, clicking...")
        scrape_btn.first.click()
        
        # Monitor the page for changes over 2 minutes
        for check in range(12):
            page.wait_for_timeout(10000)  # 10 seconds
            page.screenshot(path=f"{SCREENSHOT_DIR}/test_scrape_wait_{check+1}.png")
            body = page.locator('body').inner_text()
            
            # Check for status messages
            status_lines = []
            for line in body.split('\n'):
                ls = line.strip().lower()
                if any(kw in ls for kw in ['scraping', 'processing', 'error', 'fail', 'success', 'complete', 'chunks', 'embedded', 'scraped']):
                    if len(line.strip()) > 3:
                        status_lines.append(line.strip()[:120])
            
            # Get chunk count
            chunks = 0
            lines = body.split('\n')
            for i, line in enumerate(lines):
                if 'TOTAL CHUNKS' in line.upper():
                    nums = re.findall(r'\d+', line)
                    if nums:
                        chunks = int(nums[0])
                    elif i + 1 < len(lines):
                        nums = re.findall(r'\d+', lines[i+1])
                        if nums:
                            chunks = int(nums[0])
            
            elapsed = (check + 1) * 10
            print(f"  [{elapsed}s] Chunks: {chunks} | Status: {'; '.join(status_lines[:3]) if status_lines else 'no status'}")
            
            if chunks > 0:
                print(f"\n  SUCCESS! {chunks} chunks loaded!")
                break
    else:
        print("Scrape button NOT found!")
    
    page.screenshot(path=f"{SCREENSHOT_DIR}/test_scrape_final.png")
    
    context.close()
    browser.close()
