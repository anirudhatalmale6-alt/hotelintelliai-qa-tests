import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()
        page.set_default_timeout(30000)
        
        # Login to onboarding portal
        await page.goto("https://onboarding.hotelintelliai.com", wait_until="networkidle", timeout=60000)
        await page.locator('input[type="email"]').fill("anirudhatomeiz@gmail.com")
        await page.locator('input[type="password"]').fill("CHANGEME")
        await page.locator('button').nth(1).click()
        await page.wait_for_timeout(5000)
        
        # ===== RIVERIE KB from onboarding =====
        print("=" * 60)
        print("RIVERIE KB (onboarding portal)")
        print("=" * 60)
        await page.goto("https://onboarding.hotelintelliai.com/hotel/hotel_riviera_cr/kb", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path="screenshots/R20_riverie_kb_onboarding.png")
        body = await page.locator('body').inner_text()
        print(body[:2500])
        
        # Click URL tab
        await page.locator('text=URL').first.click()
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshots/R21_riverie_kb_url.png")
        body = await page.locator('body').inner_text()
        print(f"\nURL tab:\n{body[:1500]}")
        
        # Click FAQ tab
        await page.locator('text=FAQ').first.click()
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshots/R22_riverie_kb_faq.png")
        body = await page.locator('body').inner_text()
        print(f"\nFAQ tab:\n{body[:1500]}")
        
        # ===== OBEROI KB - Check if scraping actually worked =====
        print("\n" + "=" * 60)
        print("OBEROI KB (check if scraping worked in background)")
        print("=" * 60)
        await page.goto("https://onboarding.hotelintelliai.com/hotel/oberoi_udaivilas/kb", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path="screenshots/R23_oberoi_kb_check.png")
        body = await page.locator('body').inner_text()
        print(body[:2500])
        
        # ===== Test Riverie channel editing from onboarding =====
        print("\n" + "=" * 60)
        print("CHANNEL EDITING TEST")
        print("=" * 60)
        await page.goto("https://onboarding.hotelintelliai.com", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Check all elements on hotel cards for clickable channel items
        hotel_card_html = await page.evaluate('''() => {
            const body = document.body.innerHTML;
            // Find all elements with class containing 'channel'
            const els = document.querySelectorAll('[class*="channel"], [class*="badge"], [class*="tag"]');
            return Array.from(els).slice(0, 20).map(e => ({
                tag: e.tagName,
                class: e.className.substring(0, 80),
                text: e.innerText.substring(0, 60),
                cursor: getComputedStyle(e).cursor,
                clickable: e.onclick !== null || e.tagName === 'A' || e.tagName === 'BUTTON'
            }));
        }''')
        print("Channel-related elements on hotel cards:")
        for el in hotel_card_html:
            print(f"  {el['tag']}.{el['class'][:40]} -> '{el['text'][:40]}' cursor={el['cursor']}")
        
        # Check if clicking on a channel badge opens anything
        whatsapp_badges = page.locator('.channel-badge, [class*="channel"][class*="badge"]')
        badge_count = await whatsapp_badges.count()
        print(f"\nChannel badges found: {badge_count}")
        
        # Try clicking the whatsapp text on the Riverie card
        # Find the second whatsapp (for Riverie, not le Patte)
        all_wa = page.locator('text=whatsapp')
        wa_count = await all_wa.count()
        print(f"Whatsapp text elements: {wa_count}")
        
        if wa_count >= 2:
            # Click Riverie's whatsapp
            await all_wa.nth(1).click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/R24_whatsapp_click.png")
            new_url = page.url
            body = await page.locator('body').inner_text()
            print(f"\nAfter clicking Riverie whatsapp: URL={new_url}")
            if new_url != "https://onboarding.hotelintelliai.com/":
                print(f"Navigated to: {new_url}")
                print(f"Body: {body[:500]}")
        
        # ===== Test the refresh button on dashboard =====
        print("\n" + "=" * 60)
        print("DASHBOARD REFRESH BUTTON")
        print("=" * 60)
        await page.goto("https://dashboard.hotelintelliai.com", wait_until="networkidle", timeout=60000)
        await page.locator('input[type="email"]').fill("anirudhatomeiz@gmail.com")
        await page.locator('input[type="password"]').fill("CHANGEME")
        await page.locator('button[type="submit"]').click()
        await page.wait_for_timeout(5000)
        await page.locator('text=Riverie').first.click()
        await page.wait_for_timeout(5000)
        
        # Test the refresh button (↻)
        refresh_btn = page.locator('text=↻')
        if await refresh_btn.count() > 0:
            print("Refresh button found, clicking...")
            await refresh_btn.first.click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path="screenshots/R25_after_refresh.png")
            body = await page.locator('body').inner_text()
            print(f"After refresh - TOTAL CONVS: ", end="")
            idx = body.find("TOTAL CONVS")
            if idx >= 0:
                print(body[idx:idx+100])
        
        # Test the timestamp display
        time_el = await page.evaluate('''() => {
            const body = document.body.innerText;
            const timeMatch = body.match(/\\d{1,2}:\\d{2}:\\d{2}\\s*[AP]M/);
            return timeMatch ? timeMatch[0] : 'no timestamp';
        }''')
        print(f"\nDashboard timestamp: {time_el}")
        
        # Check the green dot (online indicator)
        green_dot = await page.evaluate('''() => {
            const els = document.querySelectorAll('[class*="online"], [class*="status"], [class*="dot"]');
            return Array.from(els).map(e => ({
                class: e.className.substring(0, 50),
                text: e.innerText.substring(0, 20)
            }));
        }''')
        print(f"Status indicators: {green_dot}")
        
        await browser.close()

asyncio.run(main())
