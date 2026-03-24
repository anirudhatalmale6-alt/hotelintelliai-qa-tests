import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()
        page.set_default_timeout(60000)
        
        # Login to dashboard → Riverie
        await page.goto("https://dashboard.hotelintelliai.com", wait_until="networkidle", timeout=60000)
        await page.locator('input[type="email"]').fill("anirudhatomeiz@gmail.com")
        await page.locator('input[type="password"]').fill("CHANGEME")
        await page.locator('button[type="submit"]').click()
        await page.wait_for_timeout(5000)
        await page.locator('text=Riverie').first.click()
        await page.wait_for_timeout(5000)
        
        # Navigate to Debug
        await page.locator('text=Debug').first.click()
        await page.wait_for_timeout(2000)
        
        # ===== HEALTH CHECK =====
        print("=" * 60)
        print("HEALTH CHECK")
        print("=" * 60)
        await page.locator('text=Run Health Check').click()
        await page.wait_for_timeout(8000)
        await page.screenshot(path="screenshots/R11_health_check.png")
        body = await page.locator('body').inner_text()
        # Extract just the health check results
        hc_idx = body.find("Hotel is healthy")
        if hc_idx == -1:
            hc_idx = body.find("Hotel")
        print(body[hc_idx:hc_idx+2000] if hc_idx >= 0 else body[:2000])
        
        # Scroll down to see full health check
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshots/R12_health_check_scrolled.png")
        body = await page.locator('body').inner_text()
        # Get the full health data
        for section in ["HOTEL RECORD", "QDRANT", "CHANNEL", "PERSONA", "WEBHOOK"]:
            idx = body.find(section)
            if idx >= 0:
                print(f"\n--- {section} ---")
                print(body[idx:idx+500])
        
        # ===== RAG TESTER - Multiple queries =====
        print("\n" + "=" * 60)
        print("RAG TESTER - Multiple queries")
        print("=" * 60)
        await page.locator('button:has-text("RAG Tester")').click()
        await page.wait_for_timeout(2000)
        
        queries = [
            "What time is check-in?",
            "Tell me about the rooms",
            "Do you have a pool?",
            "What restaurants are available?",
        ]
        
        for query in queries:
            query_input = page.locator('input[placeholder*="Search"]')
            await query_input.fill(query)
            await page.locator('button:has-text("Search RAG")').click()
            await page.wait_for_timeout(8000)
            
            body = await page.locator('body').inner_text()
            results_idx = body.find("TOTAL RESULTS")
            if results_idx >= 0:
                print(f"\n--- Query: {query} ---")
                print(body[results_idx:results_idx+500])
        
        await page.screenshot(path="screenshots/R13_rag_multi.png")
        
        # ===== MSG SIMULATOR - Multiple messages =====
        print("\n" + "=" * 60)
        print("MSG SIMULATOR - Multiple messages")
        print("=" * 60)
        await page.locator('button:has-text("Msg Simulator")').click()
        await page.wait_for_timeout(2000)
        
        # Test with preset buttons (do you have a spa?, what time is check-in?, etc.)
        preset_btns = page.locator('button:has-text("do you have a spa")')
        if await preset_btns.count() > 0:
            # Test using the preset buttons
            print("Testing preset: do you have a spa?")
            await preset_btns.click()
            await page.wait_for_timeout(1000)
            await page.locator('button:has-text("Simulate")').click()
            await page.wait_for_timeout(15000)
            
            body = await page.locator('body').inner_text()
            resp_idx = body.find("AGENT RESPONSE")
            if resp_idx >= 0:
                print(body[resp_idx:resp_idx+1000])
            await page.screenshot(path="screenshots/R14_sim_spa.png")
        
        # Test with custom message
        inputs = page.locator('input')
        await inputs.nth(2).fill("What time is check-in and check-out?")
        await page.locator('button:has-text("Simulate")').click()
        await page.wait_for_timeout(15000)
        
        body = await page.locator('body').inner_text()
        resp_idx = body.find("AGENT RESPONSE")
        if resp_idx >= 0:
            print(f"\n--- check-in/out query ---")
            print(body[resp_idx:resp_idx+1000])
        await page.screenshot(path="screenshots/R15_sim_checkin.png")
        
        # Test with Arabic preset (multilingual)
        await page.locator('button:has-text("Msg Simulator")').click()
        await page.wait_for_timeout(2000)
        arabic_btn = page.locator('text=كيف حالك')
        if await arabic_btn.count() > 0:
            await arabic_btn.click()
            await page.wait_for_timeout(500)
            await page.locator('button:has-text("Simulate")').click()
            await page.wait_for_timeout(15000)
            
            body = await page.locator('body').inner_text()
            resp_idx = body.find("AGENT RESPONSE")
            if resp_idx >= 0:
                print(f"\n--- Arabic test ---")
                print(body[resp_idx:resp_idx+1000])
            await page.screenshot(path="screenshots/R16_sim_arabic.png")
        
        # ===== DB STATS =====
        print("\n" + "=" * 60)
        print("DB STATS")
        print("=" * 60)
        await page.locator('button:has-text("DB Stats")').click()
        await page.wait_for_timeout(2000)
        await page.locator('button:has-text("Refresh")').click()
        await page.wait_for_timeout(8000)
        await page.screenshot(path="screenshots/R17_db_stats.png")
        body = await page.locator('body').inner_text()
        stats_idx = body.find("POSTGRESQL")
        if stats_idx >= 0:
            print(body[stats_idx:stats_idx+1000])
        
        # Scroll to see full stats
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshots/R18_db_stats_scrolled.png")
        
        await browser.close()

asyncio.run(main())
