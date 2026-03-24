"""
Debug: Check why Imperial and Oberoi hotel dashboards show blank pages.
Check console errors, network requests, DNS, etc.
"""
import os
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(30000)

        # Capture console messages
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))

        # Capture network errors
        net_errors = []
        page.on("requestfailed", lambda req: net_errors.append(f"FAILED: {req.url} - {req.failure}"))

        # Login
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        print("Logged in\n")

        # Clear console
        console_msgs.clear()
        net_errors.clear()

        # Try Imperial Mae Ping
        print("="*60)
        print("IMPERIAL MAE PING - Direct URL")
        print("="*60)

        page.goto("https://imperial_mae_ping.hotelintelliai.com/", timeout=30000)
        page.wait_for_timeout(10000)

        print(f"Final URL: {page.url}")
        print(f"Title: {page.title()}")

        # Check HTML content
        html = page.content()
        print(f"HTML length: {len(html)}")
        print(f"HTML preview: {html[:500]}")

        print(f"\nConsole messages ({len(console_msgs)}):")
        for msg in console_msgs[-20:]:
            print(f"  {msg}")

        print(f"\nNetwork errors ({len(net_errors)}):")
        for err in net_errors[-10:]:
            print(f"  {err}")

        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "dbg_imperial.png"))

        # Clear and try Oberoi
        console_msgs.clear()
        net_errors.clear()

        print("\n" + "="*60)
        print("OBEROI UDAIVILAS - Direct URL")
        print("="*60)

        page.goto("https://oberoi_udaivilas.hotelintelliai.com/", timeout=30000)
        page.wait_for_timeout(10000)

        print(f"Final URL: {page.url}")
        print(f"Title: {page.title()}")

        html2 = page.content()
        print(f"HTML length: {len(html2)}")
        print(f"HTML preview: {html2[:500]}")

        print(f"\nConsole messages ({len(console_msgs)}):")
        for msg in console_msgs[-20:]:
            print(f"  {msg}")

        print(f"\nNetwork errors ({len(net_errors)}):")
        for err in net_errors[-10:]:
            print(f"  {err}")

        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "dbg_oberoi.png"))

        # Now try clicking from dashboard with console monitoring
        console_msgs.clear()
        net_errors.clear()

        print("\n" + "="*60)
        print("DASHBOARD CLICK - Imperial")
        print("="*60)

        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(5000)

        # Check what elements are around Imperial text
        imperial_el = page.locator('text=Imperial Mae Ping').first
        box = imperial_el.bounding_box()
        print(f"Imperial element box: {box}")

        # Get parent elements
        parent_html = page.evaluate("""() => {
            const el = document.querySelector('[class*="hotel"]') ||
                       Array.from(document.querySelectorAll('*')).find(e => e.textContent.includes('Imperial Mae Ping') && e.children.length < 5);
            if (el) return el.outerHTML.substring(0, 500);
            return 'not found';
        }""")
        print(f"Parent HTML: {parent_html}")

        # Get all hotel cards/links
        hotel_links = page.evaluate("""() => {
            const links = [];
            document.querySelectorAll('a').forEach(a => {
                if (a.href && a.href.includes('hotelintelliai')) {
                    links.push({href: a.href, text: a.textContent.trim().substring(0, 100)});
                }
            });
            return links;
        }""")
        print(f"\nHotel links found: {len(hotel_links)}")
        for link in hotel_links:
            print(f"  {link}")

        # Also check for onclick handlers or data attributes
        hotel_cards = page.evaluate("""() => {
            const cards = [];
            // Find elements that contain hotel names
            const hotelNames = ['Heritage', 'Grand Vista', 'Imperial', 'Oberoi', 'le Patte', 'Riverie'];
            for (const name of hotelNames) {
                const els = Array.from(document.querySelectorAll('*')).filter(e =>
                    e.textContent.includes(name) && e.children.length < 3 && e.textContent.length < 200
                );
                for (const el of els.slice(0, 2)) {
                    const parent = el.closest('a, [onclick], [role="link"], [role="button"]');
                    cards.push({
                        name: name,
                        tag: el.tagName,
                        text: el.textContent.trim().substring(0, 80),
                        parentTag: parent ? parent.tagName : 'none',
                        parentHref: parent ? (parent.href || parent.getAttribute('onclick') || '') : '',
                        classes: el.className || '',
                    });
                }
            }
            return cards;
        }""")
        print(f"\nHotel card elements:")
        for card in hotel_cards:
            print(f"  {card}")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
