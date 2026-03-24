"""
Ingest more URLs for Grand Vista (only 13 chunks) and Heritage (55 chunks).
Also ingest additional pages for Imperial and Oberoi.
"""
import os
import time
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(30000)

        # Login and navigate to working hotel for API context
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        page.goto("https://heritage_chiangrai.hotelintelliai.com/", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(5000)
        print("Logged in and on Heritage dashboard")

        # Grand Vista needs lots more content
        grand_vista_urls = [
            "https://www.grandvistachiangrai.com",
            "https://www.grandvistachiangrai.com/rooms",
            "https://www.grandvistachiangrai.com/facilities",
            "https://www.grandvistachiangrai.com/restaurant",
            "https://www.grandvistachiangrai.com/dining",
            "https://www.grandvistachiangrai.com/spa",
            "https://www.grandvistachiangrai.com/gallery",
            "https://www.grandvistachiangrai.com/about",
            "https://www.grandvistachiangrai.com/contact",
            "https://www.grandvistachiangrai.com/location",
            "https://www.grandvistachiangrai.com/pool",
            "https://www.grandvistachiangrai.com/fitness",
            "https://www.grandvistachiangrai.com/meetings",
            "https://www.grandvistachiangrai.com/amenities",
            "https://www.grandvistachiangrai.com/services",
            "https://grandvistachiangrai.com",
        ]

        # Heritage needs more specific pages
        heritage_urls = [
            "https://www.heritagechiangrai.com/about",
            "https://www.heritagechiangrai.com/rooms-suites",
            "https://www.heritagechiangrai.com/meetings-and-events",
            "https://www.heritagechiangrai.com/recreation",
            "https://www.heritagechiangrai.com/attractions",
            "https://www.heritagechiangrai.com/pool",
            "https://www.heritagechiangrai.com/fitness",
            "https://www.heritagechiangrai.com/services",
            "https://heritagechiangrai.com",
        ]

        # Imperial Mae Ping - more subpages
        imperial_urls = [
            "https://www.imperialmaeping.com/rooms",
            "https://www.imperialmaeping.com/dining",
            "https://www.imperialmaeping.com/facilities",
            "https://www.imperialmaeping.com/spa",
            "https://www.imperialmaeping.com/about",
            "https://www.imperialmaeping.com/contact",
            "https://www.imperialmaeping.com/meetings",
            "https://www.imperialmaeping.com/location",
            "https://www.imperialmaeping.com/gallery",
            "https://www.imperialmaeping.com/pool",
        ]

        # Oberoi - more subpages
        oberoi_urls = [
            "https://www.oberoihotels.com/hotels-in-udaipur-udaivilas-resort/experiences",
            "https://www.oberoihotels.com/hotels-in-udaipur-udaivilas-resort/meetings-and-events",
            "https://www.oberoihotels.com/hotels-in-udaipur-udaivilas-resort/gallery",
            "https://www.oberoihotels.com/hotels-in-udaipur-udaivilas-resort/location",
        ]

        all_ingestion = {
            "grand_vista_chiangrai": grand_vista_urls,
            "heritage_chiangrai": heritage_urls,
            "imperial_mae_ping": imperial_urls,
            "oberoi_udaivilas": oberoi_urls,
        }

        for hotel_id, urls in all_ingestion.items():
            print(f"\n{'='*60}")
            print(f"INGESTING: {hotel_id} ({len(urls)} URLs)")
            print(f"{'='*60}")

            success = 0
            for url in urls:
                result = page.evaluate(f"""async () => {{
                    try {{
                        const formData = new FormData();
                        formData.append('url', '{url}');
                        formData.append('title', '');
                        const resp = await fetch('https://api.hotelintelliai.com/kb/url/{hotel_id}', {{
                            method: 'POST',
                            body: formData,
                            credentials: 'include',
                        }});
                        const text = await resp.text();
                        return {{ status: resp.status, data: text.substring(0, 200) }};
                    }} catch(e) {{
                        return {{ error: e.message }};
                    }}
                }}""")
                status = result.get('status', 'error')
                print(f"  [{status}] {url}")
                if status == 200:
                    success += 1

            print(f"  => {success}/{len(urls)} accepted")

        # Wait for processing
        print("\nWaiting 30s for scraping jobs to process...")
        time.sleep(30)

        # Final stats
        print(f"\n{'='*60}")
        print("FINAL KB STATS")
        print(f"{'='*60}")
        for hid in ['heritage_chiangrai', 'grand_vista_chiangrai', 'imperial_mae_ping', 'oberoi_udaivilas', 'lePatte', 'hotel_riviera_cr']:
            result = page.evaluate(f"""async () => {{
                try {{
                    const resp = await fetch('https://api.hotelintelliai.com/kb/stats/{hid}', {{
                        credentials: 'include',
                    }});
                    return await resp.json();
                }} catch(e) {{
                    return {{ error: e.message }};
                }}
            }}""")
            chunks = result.get('total_chunks', 'N/A')
            print(f"  {hid}: {chunks} chunks")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
