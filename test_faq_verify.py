"""
Verify FAQ creation: Navigate to FAQ tab, create entries, and verify they appear in KB.
Also verify via RAG tester that FAQ content is searchable.
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

        # Login to onboarding portal
        page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button').nth(1).click()
        page.wait_for_timeout(5000)
        print("Logged in to onboarding portal")

        # Navigate to Riverie KB
        page.goto(f"{BASE_URL}/hotel/hotel_riviera_cr/kb", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)

        # First check the current FAQ tab state
        print("\n=== CHECKING FAQ TAB ===")
        faq_btn = page.locator('button:has-text("FAQ")')
        if faq_btn.count() > 0:
            faq_btn.first.click()
            page.wait_for_timeout(2000)
            screenshot(page, "FAQ_tab_before")

            body = page.locator('body').inner_text()
            print("Current FAQ tab content:")
            for line in body.split('\n'):
                line = line.strip()
                if line and len(line) > 3:
                    if any(kw in line.lower() for kw in ['category', 'question', 'answer', 'breakfast', 'pool', 'cancel', 'faq', 'add', 'embed']):
                        print(f"  {line}")

        # Now create each FAQ entry
        print("\n=== CREATING FAQ ENTRIES ===")
        for i, faq in enumerate(FAQ_ENTRIES):
            print(f"\nFAQ #{i+1}: {faq['question']}")

            # Make sure we're on the FAQ tab
            page.goto(f"{BASE_URL}/hotel/hotel_riviera_cr/kb", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)

            faq_btn = page.locator('button:has-text("FAQ")')
            if faq_btn.count() > 0:
                faq_btn.first.click()
                page.wait_for_timeout(1500)

            # Analyze the FAQ form structure
            body = page.locator('body').inner_text()

            # Find all inputs and textareas
            inputs = page.locator('input:not([type="file"]):not([type="email"]):not([type="password"])')
            textareas = page.locator('textarea')

            print(f"  Found {inputs.count()} inputs, {textareas.count()} textareas")

            # Log input details
            for j in range(inputs.count()):
                inp = inputs.nth(j)
                placeholder = inp.get_attribute('placeholder') or ''
                inp_type = inp.get_attribute('type') or ''
                name = inp.get_attribute('name') or ''
                visible = inp.is_visible()
                print(f"  Input {j}: type={inp_type}, placeholder='{placeholder}', name='{name}', visible={visible}")

            for j in range(textareas.count()):
                ta = textareas.nth(j)
                placeholder = ta.get_attribute('placeholder') or ''
                name = ta.get_attribute('name') or ''
                visible = ta.is_visible()
                print(f"  Textarea {j}: placeholder='{placeholder}', name='{name}', visible={visible}")

            # Try to fill the form
            # Look for category field
            cat_input = page.locator('input[placeholder*="ategory"], input[placeholder*="category"]')
            if cat_input.count() > 0 and cat_input.first.is_visible():
                cat_input.first.fill("General")
                print(f"  Category filled")

            # Look for question field
            q_input = page.locator('input[placeholder*="uestion"], input[placeholder*="question"]')
            if q_input.count() > 0 and q_input.first.is_visible():
                q_input.first.fill(faq['question'])
                print(f"  Question filled via placeholder")
            else:
                # Try all visible inputs
                for j in range(inputs.count()):
                    inp = inputs.nth(j)
                    if inp.is_visible():
                        placeholder = (inp.get_attribute('placeholder') or '').lower()
                        if 'question' in placeholder or 'q' in placeholder or not placeholder:
                            inp.fill(faq['question'])
                            print(f"  Question filled (input {j})")
                            break

            # Look for answer field
            a_input = page.locator('textarea[placeholder*="nswer"], textarea[placeholder*="answer"]')
            if a_input.count() > 0 and a_input.first.is_visible():
                a_input.first.fill(faq['answer'])
                print(f"  Answer filled via placeholder")
            else:
                # Try visible textareas
                for j in range(textareas.count()):
                    ta = textareas.nth(j)
                    if ta.is_visible():
                        ta.fill(faq['answer'])
                        print(f"  Answer filled (textarea {j})")
                        break

            screenshot(page, f"FAQ_form_filled_{i+1}")

            # Click Add/Embed button
            embed_btn = page.locator('button:has-text("Add & Embed"), button:has-text("Add FAQ"), button:has-text("Embed")')
            if embed_btn.count() > 0:
                embed_btn.first.click()
                print(f"  Clicked embed button")
                page.wait_for_timeout(8000)
            else:
                # Try any button that looks like submit
                btns = page.locator('button')
                for j in range(btns.count()):
                    text = btns.nth(j).inner_text().strip()
                    if any(kw in text.lower() for kw in ['add', 'embed', 'save', 'submit', 'create']):
                        btns.nth(j).click()
                        print(f"  Clicked button: '{text}'")
                        page.wait_for_timeout(8000)
                        break

            screenshot(page, f"FAQ_after_submit_{i+1}")

            # Check result
            body_after = page.locator('body').inner_text()
            if 'error' in body_after.lower() or '⚠' in body_after:
                error_lines = [l.strip() for l in body_after.split('\n') if 'error' in l.lower() or '⚠' in l]
                print(f"  RESULT: ERROR — {error_lines[:2]}")
            elif 'embedded' in body_after.lower() or 'success' in body_after.lower() or 'added' in body_after.lower():
                print(f"  RESULT: SUCCESS")
            else:
                print(f"  RESULT: Need to verify")

        # Verify all FAQs appear in KB
        print("\n=== VERIFYING FAQS IN KB ===")
        page.goto(f"{BASE_URL}/hotel/hotel_riviera_cr/kb", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        screenshot(page, "FAQ_final_kb_state")

        print("\nAll KB documents:")
        for line in body.split('\n'):
            line = line.strip()
            if line and ('chunk' in line.lower() or 'faq' in line.lower() or 'file' in line.lower() or 'website' in line.lower() or 'paste' in line.lower()):
                print(f"  {line}")

        # Scroll down to see full list
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        screenshot(page, "FAQ_final_kb_scrolled")

        # Now verify via RAG tester on dashboard that FAQ content is searchable
        print("\n=== VERIFYING FAQ VIA RAG TESTER ===")
        context2 = browser.new_context(viewport={"width": 1280, "height": 720})
        page2 = context2.new_page()
        page2.set_default_timeout(30000)

        page2.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page2.locator('input[type="email"]').fill(EMAIL)
        page2.locator('input[type="password"]').fill(PASSWORD)
        page2.locator('button[type="submit"]').click()
        page2.wait_for_timeout(5000)

        # Go to Riverie
        page2.locator('text=Riverie').first.click()
        page2.wait_for_timeout(5000)

        # Go to Debug > RAG Tester
        page2.locator('text=Debug').first.click()
        page2.wait_for_timeout(2000)
        page2.locator('button:has-text("RAG Tester")').click()
        page2.wait_for_timeout(2000)

        # Test breakfast query
        query_input = page2.locator('input[placeholder*="Search"]')
        query_input.fill("what time is breakfast served")
        page2.locator('button:has-text("Search RAG")').click()
        page2.wait_for_timeout(10000)

        body_rag = page2.locator('body').inner_text()
        screenshot(page2, "FAQ_rag_breakfast_test")

        if 'breakfast' in body_rag.lower() or '7:00' in body_rag or '10:30' in body_rag:
            print("RAG TESTER: Breakfast FAQ content found in search results!")
        else:
            print("RAG TESTER: Breakfast FAQ content NOT found in search results")

        # Print RAG results
        in_results = False
        for line in body_rag.split('\n'):
            line = line.strip()
            if 'TOTAL RESULTS' in line or 'ABOVE THRESHOLD' in line:
                in_results = True
                print(f"  {line}")
            elif in_results and line and len(line) > 5:
                print(f"  {line}")
                if len(line) > 100:
                    in_results = False

        # Test pool query
        query_input.fill("")
        query_input.fill("does the hotel have a swimming pool")
        page2.locator('button:has-text("Search RAG")').click()
        page2.wait_for_timeout(10000)

        body_rag2 = page2.locator('body').inner_text()
        screenshot(page2, "FAQ_rag_pool_test")

        if 'pool' in body_rag2.lower() or 'infinity' in body_rag2.lower():
            print("\nRAG TESTER: Pool FAQ content found in search results!")
        else:
            print("\nRAG TESTER: Pool FAQ content NOT found in search results")

        context2.close()
        context.close()
        browser.close()

        print("\n=== DONE ===")


if __name__ == "__main__":
    main()
