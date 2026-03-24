"""
Ingest Imperial Mae Ping Hotel KB - special handling for navigation issues.
Also check Oberoi Udaivilas KB status.
"""
import os
import time
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, f"imp_{name}.png")
    page.screenshot(path=path)
    print(f"  Screenshot: {path}")


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
        screenshot(page, "login")

        # Get page text to see all hotels listed
        body = page.locator('body').inner_text()
        print("Dashboard text (first 2000 chars):")
        print(body[:2000])
        print("\n---")

        # Look for all clickable links/text that might be hotel names
        links = page.locator('a, [role="button"], [class*="hotel"], [class*="card"]')
        print(f"\nFound {links.count()} clickable elements")
        for i in range(min(links.count(), 30)):
            el = links.nth(i)
            try:
                text = el.inner_text()[:100].strip()
                if text and len(text) > 3:
                    print(f"  [{i}] {text}")
            except Exception:
                pass

        screenshot(page, "dashboard_overview")

        # Try to find Imperial Mae Ping with various selectors
        imperial_selectors = [
            'text=Imperial Mae Ping',
            'text=Imperial',
            'text=Mae Ping',
            'text=imperial',
        ]

        found_imperial = False
        for sel in imperial_selectors:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=3000):
                    print(f"\nFound Imperial with selector: {sel}")
                    loc.click()
                    page.wait_for_timeout(8000)
                    screenshot(page, "imperial_clicked")

                    # Check if page loaded
                    body2 = page.locator('body').inner_text()
                    print(f"Page text after click (first 500): {body2[:500]}")

                    found_imperial = True
                    break
            except Exception as e:
                print(f"  Selector '{sel}' failed: {str(e)[:80]}")

        if not found_imperial:
            print("\nCould not find Imperial Mae Ping hotel in dashboard")
            # Let's try scrolling or checking if it's there
            screenshot(page, "no_imperial_found")

            # Check if we need to scroll
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            screenshot(page, "dashboard_scrolled")
            body3 = page.locator('body').inner_text()
            print(f"\nAfter scroll: {body3[:2000]}")
        else:
            # Try to navigate to KB
            print("\nLooking for sidebar navigation...")
            sidebar_text = ""
            try:
                # Look for sidebar or navigation
                nav_selectors = [
                    'nav',
                    '[class*="sidebar"]',
                    '[class*="nav"]',
                    'aside',
                ]
                for nsel in nav_selectors:
                    try:
                        nav = page.locator(nsel).first
                        if nav.is_visible(timeout=2000):
                            sidebar_text = nav.inner_text()
                            print(f"Sidebar ({nsel}): {sidebar_text[:300]}")
                            break
                    except Exception:
                        pass
            except Exception:
                pass

            # Try Knowledge Base click
            kb_selectors = [
                'text=Knowledge Base',
                'text=Knowledge',
                'a:has-text("Knowledge")',
                '[href*="knowledge"]',
                '[href*="kb"]',
            ]
            for ksel in kb_selectors:
                try:
                    kbloc = page.locator(ksel).first
                    if kbloc.is_visible(timeout=3000):
                        kbloc.click()
                        page.wait_for_timeout(3000)
                        screenshot(page, "imperial_kb")
                        print(f"Clicked KB with: {ksel}")

                        # Now find URL tab
                        page.locator('button:has-text("URL")').first.click()
                        page.wait_for_timeout(2000)
                        screenshot(page, "imperial_url_tab")

                        # Check current chunks
                        body_kb = page.locator('body').inner_text()
                        for line in body_kb.split('\n'):
                            if 'chunk' in line.lower():
                                print(f"  KB: {line.strip()}")

                        # Ingest URLs
                        imperial_urls = [
                            "https://www.imperialmaeping.com",
                            "https://imperialmaeping.com",
                            "https://www.imperialhotels.com/mae-ping",
                        ]

                        for url in imperial_urls:
                            try:
                                # Find URL input
                                inputs = page.locator('input')
                                for ii in range(inputs.count()):
                                    inp = inputs.nth(ii)
                                    if inp.is_visible():
                                        inp_type = (inp.get_attribute('type') or '').lower()
                                        placeholder = (inp.get_attribute('placeholder') or '').lower()
                                        if inp_type not in ('file', 'hidden', 'checkbox', 'radio', 'email', 'password'):
                                            if 'url' in placeholder or 'http' in placeholder or ii == 0:
                                                inp.fill(url)
                                                page.wait_for_timeout(500)
                                                # Click scrape
                                                try:
                                                    page.locator('button:has-text("Scrape")').first.click()
                                                    page.wait_for_timeout(15000)
                                                    print(f"  Scraped: {url}")
                                                except Exception:
                                                    print(f"  Could not click Scrape for {url}")
                                                break
                            except Exception as e:
                                print(f"  Error ingesting {url}: {e}")

                        screenshot(page, "imperial_after_ingest")
                        break
                except Exception as e:
                    print(f"  KB selector '{ksel}' failed: {str(e)[:80]}")

        # Now also check Oberoi Udaivilas KB status
        print(f"\n\n{'='*60}")
        print("Checking Oberoi Udaivilas KB status...")
        print(f"{'='*60}")

        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        try:
            page.locator('text=Oberoi').first.click(timeout=10000)
            page.wait_for_timeout(5000)
            screenshot(page, "oberoi_hotel")

            page.locator('text=Knowledge Base').first.click()
            page.wait_for_timeout(3000)
            screenshot(page, "oberoi_kb")

            body_ob = page.locator('body').inner_text()
            for line in body_ob.split('\n'):
                if 'chunk' in line.lower():
                    print(f"  Oberoi KB: {line.strip()}")

        except Exception as e:
            print(f"  Oberoi check failed: {e}")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
