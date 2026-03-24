"""Verify FAQ and file upload content is searchable via RAG tester."""
import os
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "screenshots"


def screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    page.screenshot(path=path)
    print(f"  Screenshot: {path}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(30000)

        # Login to dashboard
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        print("Logged in to dashboard")

        # Go to Riverie
        page.locator('text=Riverie').first.click()
        page.wait_for_timeout(5000)

        # Go to Debug > RAG Tester
        page.locator('text=Debug').first.click()
        page.wait_for_timeout(2000)
        page.locator('button:has-text("RAG Tester")').click()
        page.wait_for_timeout(2000)

        queries = [
            ("what time is breakfast", "FAQ: breakfast time"),
            ("swimming pool hours", "FAQ: pool info"),
            ("cancellation policy", "FAQ: cancellation"),
            ("room rates deluxe suite", "FILE: CSV room rates"),
            ("spa massage treatment", "FILE: MD spa menu"),
            ("check-in check-out time", "FILE: TXT hotel info"),
            ("dining guide restaurant", "FILE: PDF dining"),
        ]

        for query, desc in queries:
            print(f"\n--- RAG Query: '{query}' ({desc}) ---")

            query_input = page.locator('input[placeholder*="Search"]')
            query_input.fill("")
            query_input.fill(query)
            page.locator('button:has-text("Search RAG")').click()
            page.wait_for_timeout(10000)

            body = page.locator('body').inner_text()
            safe_name = query.replace(' ', '_')[:30]
            screenshot(page, f"RAG_verify_{safe_name}")

            # Extract results
            lines = body.split('\n')
            for idx, line in enumerate(lines):
                line = line.strip()
                if 'TOTAL RESULTS' in line or 'ABOVE THRESHOLD' in line:
                    print(f"  {line}")
                if 'SCORE' in line.upper() and 'CHUNK' in lines[idx-1].upper() if idx > 0 else False:
                    print(f"  {lines[idx-1].strip()}")
                    print(f"  {line}")

            # Check if relevant content appears in results
            keywords = query.split()
            found = any(kw.lower() in body.lower() for kw in keywords if len(kw) > 3)
            if found:
                print(f"  FOUND: Relevant content in results")
            else:
                print(f"  NOT FOUND: No matching content")

        context.close()
        browser.close()
        print("\n=== DONE ===")


if __name__ == "__main__":
    main()
