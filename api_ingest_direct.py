"""
Ingest KB URLs for Imperial Mae Ping and Oberoi via direct API calls.
API: POST https://api.hotelintelliai.com/kb/url/{hotel_id}
"""
import os
import json
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

        # Login to get auth token
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        print("Logged in")

        # Navigate to a working hotel to get auth context
        page.goto("https://heritage_chiangrai.hotelintelliai.com/", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        # Get auth token from localStorage or cookies
        auth_data = page.evaluate("""() => {
            const data = {};
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key.toLowerCase().includes('token') || key.toLowerCase().includes('auth') || key.toLowerCase().includes('session')) {
                    data[key] = localStorage.getItem(key);
                }
            }
            // Also check for tokens in cookies
            data['cookies'] = document.cookie;
            return data;
        }""")
        print(f"Auth data keys: {list(auth_data.keys())}")
        for k, v in auth_data.items():
            if v and len(str(v)) > 10:
                print(f"  {k}: {str(v)[:80]}...")

        # Get the auth token by intercepting a real API call
        captured_headers = {}
        def capture_headers(request):
            if 'api.hotelintelliai.com' in request.url:
                for k, v in request.headers.items():
                    if k.lower() in ('authorization', 'cookie', 'x-hotel-id'):
                        captured_headers[k] = v
        page.on("request", capture_headers)

        # Trigger an API call
        page.locator('text=Knowledge Base').first.click()
        page.wait_for_timeout(5000)

        print(f"\nCaptured headers: {list(captured_headers.keys())}")
        for k, v in captured_headers.items():
            print(f"  {k}: {v[:80]}...")

        # Now use fetch() from the browser to call the API for Imperial and Oberoi
        hotels_to_ingest = {
            "imperial_mae_ping": [
                "https://www.imperialmaeping.com",
                "https://imperialmaeping.com",
            ],
            "oberoi_udaivilas": [
                "https://www.oberoihotels.com/hotels-in-udaipur-udaivilas-resort/",
                "https://www.oberoihotels.com/hotels-in-udaipur-udaivilas-resort/rooms",
                "https://www.oberoihotels.com/hotels-in-udaipur-udaivilas-resort/dining",
                "https://www.oberoihotels.com/hotels-in-udaipur-udaivilas-resort/spa",
            ],
        }

        # First check current KB stats for each hotel
        for hotel_id in hotels_to_ingest:
            print(f"\n{'='*60}")
            print(f"Checking KB stats for: {hotel_id}")
            result = page.evaluate(f"""async () => {{
                try {{
                    const resp = await fetch('https://api.hotelintelliai.com/kb/stats/{hotel_id}', {{
                        credentials: 'include',
                    }});
                    return {{ status: resp.status, data: await resp.text() }};
                }} catch(e) {{
                    return {{ error: e.message }};
                }}
            }}""")
            print(f"  Stats: {result}")

            result2 = page.evaluate(f"""async () => {{
                try {{
                    const resp = await fetch('https://api.hotelintelliai.com/kb/list/{hotel_id}', {{
                        credentials: 'include',
                    }});
                    return {{ status: resp.status, data: await resp.text() }};
                }} catch(e) {{
                    return {{ error: e.message }};
                }}
            }}""")
            data2 = result2.get('data', '')
            print(f"  List: status={result2.get('status')} data_len={len(data2)}")
            if len(data2) < 500:
                print(f"  List data: {data2}")

        # Now ingest URLs
        for hotel_id, urls in hotels_to_ingest.items():
            print(f"\n{'='*60}")
            print(f"INGESTING URLs for: {hotel_id}")
            print(f"{'='*60}")

            for url in urls:
                print(f"\n  URL: {url}")

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
                        return {{ status: resp.status, data: text.substring(0, 500) }};
                    }} catch(e) {{
                        return {{ error: e.message }};
                    }}
                }}""")
                print(f"  Result: {result}")

        # Check stats after ingestion
        print(f"\n\n{'='*60}")
        print("POST-INGESTION STATS")
        print(f"{'='*60}")

        import time
        time.sleep(10)  # Wait for processing

        for hotel_id in hotels_to_ingest:
            result = page.evaluate(f"""async () => {{
                try {{
                    const resp = await fetch('https://api.hotelintelliai.com/kb/stats/{hotel_id}', {{
                        credentials: 'include',
                    }});
                    return {{ status: resp.status, data: await resp.text() }};
                }} catch(e) {{
                    return {{ error: e.message }};
                }}
            }}""")
            print(f"  {hotel_id}: {result}")

        # Also check all 6 hotels
        print(f"\n{'='*60}")
        print("ALL HOTEL KB STATS")
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
            print(f"  {hid}: {result}")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
