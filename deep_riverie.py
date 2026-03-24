import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()
        page.set_default_timeout(30000)
        
        # Login to dashboard → Riverie
        await page.goto("https://dashboard.hotelintelliai.com", wait_until="networkidle", timeout=60000)
        await page.locator('input[type="email"]').fill("anirudhatomeiz@gmail.com")
        await page.locator('input[type="password"]').fill("CHANGEME")
        await page.locator('button[type="submit"]').click()
        await page.wait_for_timeout(5000)
        await page.locator('text=Riverie').first.click()
        await page.wait_for_timeout(5000)
        
        # ===== OVERVIEW =====
        print("=" * 60)
        print("OVERVIEW")
        print("=" * 60)
        await page.screenshot(path="screenshots/R01_overview.png")
        body = await page.locator('body').inner_text()
        print(body[:2500])
        
        # ===== CONVERSATIONS - Click each one =====
        print("\n" + "=" * 60)
        print("CONVERSATIONS")
        print("=" * 60)
        await page.locator('text=Conversations').first.click()
        await page.wait_for_timeout(3000)
        
        body = await page.locator('body').inner_text()
        print(f"Conversations list:\n{body[:1500]}")
        
        # Click each conversation and capture thread
        conv_names = ["nick jain"]  # Start with nick jain
        for name in conv_names:
            loc = page.locator(f'text={name}').first
            if await loc.count() > 0:
                await loc.click()
                await page.wait_for_timeout(3000)
                await page.screenshot(path=f"screenshots/R02_conv_{name.replace(' ','_')}.png")
                body = await page.locator('body').inner_text()
                thread_idx = body.find("THREAD")
                if thread_idx >= 0:
                    print(f"\n--- Thread: {name} ---")
                    print(body[thread_idx:thread_idx+1500])
        
        # Click each njain2000 conversation (multiple)
        njain_els = page.locator('text=njain2000')
        njain_count = await njain_els.count()
        print(f"\nnjain2000 entries: {njain_count}")
        
        for i in range(min(njain_count, 5)):
            await njain_els.nth(i).click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path=f"screenshots/R03_conv_njain_{i}.png")
            body = await page.locator('body').inner_text()
            thread_idx = body.find("THREAD")
            if thread_idx >= 0:
                thread_text = body[thread_idx:thread_idx+800]
                print(f"\n--- njain2000 conv {i} ---")
                print(thread_text)
        
        # Click the ? (unknown line user) conversation
        unknown_loc = page.locator('text=?')
        # This might be tricky - let's look for the line conversation
        line_loc = page.locator('text=line')
        line_count = await line_loc.count()
        print(f"\nLine text items: {line_count}")
        
        # ===== GUESTS - Click each guest =====
        print("\n" + "=" * 60)
        print("GUESTS")
        print("=" * 60)
        await page.locator('text=Guests').first.click()
        await page.wait_for_timeout(3000)
        await page.screenshot(path="screenshots/R04_guests.png")
        body = await page.locator('body').inner_text()
        print(body[:2000])
        
        # Check VIP tab
        vip_tab = page.locator('text=VIP')
        if await vip_tab.count() > 0:
            await vip_tab.first.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/R05_guests_vip.png")
            body = await page.locator('body').inner_text()
            print(f"\nVIP tab:\n{body[:1000]}")
        
        # Click on a guest to see their profile
        nick_loc = page.locator('text=nick jain')
        if await nick_loc.count() > 0:
            await page.locator('text=ALL').first.click()
            await page.wait_for_timeout(1000)
            await nick_loc.first.click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path="screenshots/R06_guest_profile_nick.png")
            body = await page.locator('body').inner_text()
            print(f"\nGuest profile nick jain:\n{body[:2000]}")
        
        # ===== ESCALATIONS - Click each one =====
        print("\n" + "=" * 60)
        print("ESCALATIONS")
        print("=" * 60)
        await page.locator('text=Escalations').first.click()
        await page.wait_for_timeout(3000)
        await page.screenshot(path="screenshots/R07_escalations.png")
        body = await page.locator('body').inner_text()
        print(body[:2000])
        
        # Try clicking an escalation
        esc_items = page.locator('text=unresolved')
        esc_count = await esc_items.count()
        print(f"\nUnresolved escalations: {esc_count}")
        if esc_count > 0:
            await esc_items.first.click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path="screenshots/R08_escalation_detail.png")
            body = await page.locator('body').inner_text()
            print(f"\nEscalation detail:\n{body[:2000]}")
        
        # ===== CHANNELS =====
        print("\n" + "=" * 60)
        print("CHANNELS")
        print("=" * 60)
        await page.locator('text=Channels').first.click()
        await page.wait_for_timeout(3000)
        await page.screenshot(path="screenshots/R09_channels.png")
        body = await page.locator('body').inner_text()
        print(body[:2000])
        
        # Check if channel status items are clickable
        channel_items = page.locator('text=WHATSAPP')
        if await channel_items.count() > 0:
            await channel_items.first.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/R10_channel_whatsapp_click.png")
            body2 = await page.locator('body').inner_text()
            if body2 != body[:len(body2)]:
                print(f"\nAfter clicking WHATSAPP:\n{body2[:1000]}")
        
        await browser.close()

asyncio.run(main())
