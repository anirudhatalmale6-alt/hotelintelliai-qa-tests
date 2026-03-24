"""Check KB stats for all hotels after ingestion."""
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

        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        page.goto("https://heritage_chiangrai.hotelintelliai.com/", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        print("KB STATS - All Hotels")
        print("="*50)
        for hid in ['heritage_chiangrai', 'grand_vista_chiangrai', 'imperial_mae_ping', 'oberoi_udaivilas', 'lePatte', 'hotel_riviera_cr']:
            result = page.evaluate(f"""async () => {{
                try {{
                    const resp = await fetch('https://api.hotelintelliai.com/kb/stats/{hid}', {{ credentials: 'include' }});
                    return await resp.json();
                }} catch(e) {{ return {{ error: e.message }}; }}
            }}""")
            chunks = result.get('total_chunks', 'N/A')
            version = result.get('kb_version', 'N/A')
            print(f"  {hid}: {chunks} chunks (v{version})")

        # Also list documents for Grand Vista to see what was scraped
        print(f"\nGrand Vista documents:")
        result = page.evaluate("""async () => {
            try {
                const resp = await fetch('https://api.hotelintelliai.com/kb/list/grand_vista_chiangrai', { credentials: 'include' });
                return await resp.json();
            } catch(e) { return { error: e.message }; }
        }""")
        if isinstance(result, list):
            for doc in result:
                print(f"  - {doc.get('title', doc.get('source', 'unknown'))}: {doc.get('chunks', '?')} chunks")
        else:
            print(f"  {result}")

        # List Heritage documents
        print(f"\nHeritage documents:")
        result = page.evaluate("""async () => {
            try {
                const resp = await fetch('https://api.hotelintelliai.com/kb/list/heritage_chiangrai', { credentials: 'include' });
                return await resp.json();
            } catch(e) { return { error: e.message }; }
        }""")
        if isinstance(result, list):
            for doc in result:
                print(f"  - {doc.get('title', doc.get('source', 'unknown'))}: {doc.get('chunks', '?')} chunks")
        else:
            print(f"  {result}")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
