"""
FAQ creation test - fixed to properly fill category, question, and answer fields.
"""
import os
from playwright.sync_api import sync_playwright

BASE_URL = "https://onboarding.hotelintelliai.com"
DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "screenshots"

FAQ_ENTRIES = [
    {
        "question": "What time is breakfast served?",
        "answer": "Breakfast is served daily from 7:00 AM to 10:30 AM in the main restaurant. A continental breakfast is also available via room service from 6:00 AM."
    },
    {
        "question": "Does the hotel have a swimming pool?",
        "answer": "Yes, we have an Olympic-sized infinity pool open from 6:00 AM to 10:00 PM. Pool towels are provided complimentary at the poolside."
    },
    {
        "question": "What is the cancellation policy?",
        "answer": "Free cancellation up to 48 hours before check-in. Cancellations within 48 hours will be charged one night's stay."
    },
]


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

        # Login
        page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button').nth(1).click()
        page.wait_for_timeout(5000)
        print("Logged in")

        # Navigate to Riverie KB > FAQ tab
        page.goto(f"{BASE_URL}/hotel/hotel_riviera_cr/kb", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)
        page.locator('button:has-text("FAQ")').first.click()
        page.wait_for_timeout(1500)

        # Analyze the full form structure
        print("\n=== ANALYZING FAQ FORM ===")

        # Check all form elements
        all_elements = page.locator('input, textarea, select, [contenteditable]')
        for i in range(all_elements.count()):
            el = all_elements.nth(i)
            tag = el.evaluate("el => el.tagName").lower()
            el_type = el.get_attribute('type') or ''
            placeholder = el.get_attribute('placeholder') or ''
            name = el.get_attribute('name') or ''
            cls = el.get_attribute('class') or ''
            visible = el.is_visible()
            if visible and el_type not in ('email', 'password', 'file'):
                print(f"  {tag}: type='{el_type}', placeholder='{placeholder}', name='{name}', class='{cls[:50]}'")

        # Check for select/dropdown elements
        selects = page.locator('select')
        print(f"\n  Select elements: {selects.count()}")
        for i in range(selects.count()):
            sel = selects.nth(i)
            if sel.is_visible():
                options = sel.locator('option')
                opt_texts = []
                for j in range(options.count()):
                    opt_texts.append(options.nth(j).inner_text())
                print(f"  Select {i} options: {opt_texts}")

        # Check for div-based dropdowns or custom selects
        # Look for the CATEGORY label and what follows it
        body = page.locator('body').inner_text()
        lines = body.split('\n')
        for idx, line in enumerate(lines):
            if 'CATEGORY' in line.upper():
                print(f"\n  CATEGORY context: ...{lines[max(0,idx-1):idx+3]}")
                break

        # Get the page HTML around the FAQ form to understand structure
        faq_html = page.evaluate("""() => {
            const faqSection = document.querySelector('[class*="faq"], [class*="FAQ"]') || document.body;
            // Get all labels and their associated elements
            const labels = document.querySelectorAll('label, .label, [class*="label"]');
            let result = [];
            labels.forEach(l => {
                result.push({text: l.textContent.trim(), tag: l.tagName, class: l.className});
            });
            // Also get the category selector
            const selects = document.querySelectorAll('select');
            selects.forEach(s => {
                const opts = Array.from(s.options).map(o => o.text);
                result.push({select: true, options: opts, class: s.className, visible: s.offsetParent !== null});
            });
            return result;
        }""")
        print(f"\n  Form labels/selects: {faq_html}")

        # Now try to create FAQ entries
        print("\n=== CREATING FAQ ENTRIES ===")

        for i, faq in enumerate(FAQ_ENTRIES):
            print(f"\nFAQ #{i+1}: {faq['question']}")

            # Navigate fresh to FAQ tab
            page.goto(f"{BASE_URL}/hotel/hotel_riviera_cr/kb", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)
            page.locator('button:has-text("FAQ")').first.click()
            page.wait_for_timeout(1500)

            # Fill category - try select first, then input
            selects = page.locator('select')
            category_filled = False
            for j in range(selects.count()):
                sel = selects.nth(j)
                if sel.is_visible():
                    try:
                        # Try to select an option
                        options = sel.locator('option')
                        for k in range(options.count()):
                            text = options.nth(k).inner_text().strip()
                            if text and text != '--' and text.lower() != 'select':
                                sel.select_option(index=k)
                                print(f"  Category selected: '{text}' (option {k})")
                                category_filled = True
                                break
                        if category_filled:
                            break
                    except Exception as e:
                        print(f"  Select error: {e}")

            if not category_filled:
                # Try input with category placeholder
                cat_inputs = page.locator('input')
                for j in range(cat_inputs.count()):
                    inp = cat_inputs.nth(j)
                    if inp.is_visible():
                        placeholder = (inp.get_attribute('placeholder') or '').lower()
                        if 'categ' in placeholder:
                            inp.fill("General")
                            category_filled = True
                            print(f"  Category typed: 'General'")
                            break

            # Fill question
            q_input = page.locator('input')
            for j in range(q_input.count()):
                inp = q_input.nth(j)
                if inp.is_visible():
                    placeholder = (inp.get_attribute('placeholder') or '').lower()
                    inp_type = (inp.get_attribute('type') or '').lower()
                    if inp_type not in ('email', 'password', 'file', 'hidden'):
                        if 'question' in placeholder or 'breakfast' in placeholder or not placeholder:
                            inp.fill(faq['question'])
                            print(f"  Question filled")
                            break

            # Fill answer
            ta = page.locator('textarea')
            for j in range(ta.count()):
                textarea = ta.nth(j)
                if textarea.is_visible():
                    textarea.fill(faq['answer'])
                    print(f"  Answer filled")
                    break

            page.wait_for_timeout(500)
            screenshot(page, f"FAQ_v2_filled_{i+1}")

            # Check button state
            add_btn = page.locator('button:has-text("Add FAQ"), button:has-text("Add & Embed"), button:has-text("Embed")')
            if add_btn.count() > 0:
                is_disabled = add_btn.first.get_attribute('disabled')
                btn_text = add_btn.first.inner_text().strip()
                print(f"  Button '{btn_text}': disabled={is_disabled}")

                if is_disabled:
                    print(f"  Button still disabled — category may not be filled")
                    # Try clicking around for category dropdowns
                    # Check if there's a custom dropdown
                    page.evaluate("""() => {
                        // Try to find and click category-related elements
                        const els = document.querySelectorAll('[class*="category"], [class*="select"], [class*="dropdown"]');
                        els.forEach(el => console.log('Found:', el.className, el.textContent.substring(0, 50)));
                    }""")
                else:
                    add_btn.first.click()
                    print(f"  Clicked submit")
                    page.wait_for_timeout(8000)

                    screenshot(page, f"FAQ_v2_result_{i+1}")
                    body_after = page.locator('body').inner_text()

                    if 'embedded' in body_after.lower():
                        print(f"  RESULT: SUCCESS — FAQ embedded")
                    elif 'error' in body_after.lower() or '⚠' in body_after:
                        print(f"  RESULT: ERROR")
                    else:
                        print(f"  RESULT: Submitted (checking...)")
            else:
                print(f"  No add/embed button found")

        # Final verification
        print("\n=== FINAL KB STATE ===")
        page.goto(f"{BASE_URL}/hotel/hotel_riviera_cr/kb", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        screenshot(page, "FAQ_v2_final_state")

        # Count FAQ entries
        faq_count = body.lower().count('faq ·')
        print(f"FAQ entries in KB: {faq_count}")

        for line in body.split('\n'):
            line = line.strip()
            if 'faq' in line.lower() and 'chunk' in line.lower():
                print(f"  {line}")

        # Check total stats
        for line in body.split('\n'):
            line = line.strip()
            if any(kw in line.upper() for kw in ['TOTAL', 'CHUNKS', 'DOCUMENTS', 'VERSION']):
                print(f"  {line}")

        # Now verify via RAG tester
        print("\n=== RAG TESTER VERIFICATION ===")
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)

        page.locator('text=Riverie').first.click()
        page.wait_for_timeout(5000)
        page.locator('text=Debug').first.click()
        page.wait_for_timeout(2000)
        page.locator('button:has-text("RAG Tester")').click()
        page.wait_for_timeout(2000)

        # Test: search for breakfast
        query_input = page.locator('input[placeholder*="Search"]')
        query_input.fill("what time is breakfast")
        page.locator('button:has-text("Search RAG")').click()
        page.wait_for_timeout(10000)

        body_rag = page.locator('body').inner_text()
        screenshot(page, "FAQ_rag_verify_breakfast")

        print("\nRAG results for 'what time is breakfast':")
        capture = False
        for line in body_rag.split('\n'):
            line = line.strip()
            if 'TOTAL RESULTS' in line or 'ABOVE THRESHOLD' in line or 'SCORE' in line:
                capture = True
            if capture and line:
                print(f"  {line}")
                if len(line) > 150:
                    capture = False

        if 'breakfast' in body_rag.lower():
            print("\n  VERIFIED: Breakfast content found in RAG results")
        else:
            print("\n  NOT FOUND: Breakfast content missing from RAG results")

        # Test: search for cancellation
        query_input.fill("")
        query_input.fill("cancellation policy")
        page.locator('button:has-text("Search RAG")').click()
        page.wait_for_timeout(10000)

        body_rag2 = page.locator('body').inner_text()
        screenshot(page, "FAQ_rag_verify_cancellation")

        if 'cancellation' in body_rag2.lower() or '48 hours' in body_rag2.lower():
            print("  VERIFIED: Cancellation policy found in RAG results")
        else:
            print("  NOT FOUND: Cancellation policy missing from RAG results")

        context.close()
        browser.close()
        print("\n=== ALL DONE ===")


if __name__ == "__main__":
    main()
