"""
Deep KB Testing: File Uploads (all formats) + FAQ Creation
Tests on The Riverie by Katathani hotel KB via onboarding portal.
"""
import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://onboarding.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "screenshots"
TEST_FILES_DIR = "test-files"

# Test files to upload
TEST_FILES = [
    ("test_hotel_info.txt", "TXT"),
    ("test_room_rates.csv", "CSV"),
    ("test_amenities.json", "JSON"),
    ("test_spa_menu.md", "Markdown"),
    ("test_dining_guide.pdf", "PDF"),
    ("test_guest_policies.docx", "DOCX"),
    ("test_facilities.html", "HTML"),
]

# FAQ entries to create
FAQ_ENTRIES = [
    {
        "category": "Dining",
        "question": "What time is breakfast served?",
        "answer": "Breakfast is served daily from 7:00 AM to 10:30 AM in the main restaurant. A continental breakfast is also available via room service from 6:00 AM."
    },
    {
        "category": "Facilities",
        "question": "Does the hotel have a swimming pool?",
        "answer": "Yes, we have an Olympic-sized infinity pool open from 6:00 AM to 10:00 PM. Pool towels are provided complimentary at the poolside."
    },
    {
        "category": "Policies",
        "question": "What is the cancellation policy?",
        "answer": "Free cancellation up to 48 hours before check-in. Cancellations within 48 hours will be charged one night's stay."
    },
]


def screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    page.screenshot(path=path)
    print(f"  Screenshot: {path}")


def login(page):
    page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
    page.locator('input[type="email"]').fill(EMAIL)
    page.locator('input[type="password"]').fill(PASSWORD)
    page.locator('button').nth(1).click()
    page.wait_for_timeout(5000)
    print("Logged in to onboarding portal")


def navigate_to_riverie_kb(page):
    """Navigate to Riverie hotel KB page."""
    # Find Riverie hotel card and click KB/manage
    body = page.locator('body').inner_text()
    if "Riverie" not in body:
        print("ERROR: Riverie hotel not found on listing page")
        return False

    # Look for the KB link for Riverie
    # The hotel cards should have links to KB
    links = page.locator('a')
    for i in range(links.count()):
        href = links.nth(i).get_attribute('href') or ''
        if 'hotel_riviera_cr' in href and 'kb' in href:
            links.nth(i).click()
            page.wait_for_timeout(3000)
            print("Navigated to Riverie KB")
            return True

    # Fallback: try direct URL
    page.goto(f"{BASE_URL}/hotel/hotel_riviera_cr/kb", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)
    print("Navigated to Riverie KB (direct URL)")
    return True


def get_kb_stats(page):
    """Get current KB stats (chunks, documents)."""
    body = page.locator('body').inner_text()
    stats = {}
    for line in body.split('\n'):
        line = line.strip()
        if 'chunk' in line.lower():
            stats['chunks_line'] = line
        if 'document' in line.lower() or 'doc' in line.lower():
            stats['docs_line'] = line
    return stats


def test_file_uploads(page):
    """Test uploading each file format to the KB."""
    print("\n=== TESTING FILE UPLOADS ===\n")
    results = []

    for filename, file_type in TEST_FILES:
        filepath = os.path.abspath(os.path.join(TEST_FILES_DIR, filename))
        if not os.path.exists(filepath):
            print(f"SKIP: {filename} not found")
            results.append((file_type, filename, "SKIPPED", "File not found"))
            continue

        print(f"\nTesting {file_type} upload: {filename}")

        # Make sure we're on the KB page, Files tab
        navigate_to_riverie_kb(page)
        page.wait_for_timeout(2000)

        # Click the Files tab
        try:
            files_tab = page.locator('button:has-text("Files"), [role="tab"]:has-text("Files"), text=Files')
            files_tab.first.click()
            page.wait_for_timeout(1000)
        except Exception as e:
            print(f"  Could not click Files tab: {e}")

        screenshot(page, f"KB_files_tab_{file_type}")

        # Get stats before upload
        body_before = page.locator('body').inner_text()

        # Look for file input (may be hidden behind a drag-drop area)
        file_input = page.locator('input[type="file"]')
        if file_input.count() > 0:
            # Set file on the input
            try:
                file_input.first.set_input_files(filepath)
                print(f"  File set on input: {filename}")
                page.wait_for_timeout(3000)

                # Look for upload/submit button
                upload_btn = page.locator('button:has-text("Upload"), button:has-text("Embed"), button:has-text("Submit"), button:has-text("Process")')
                if upload_btn.count() > 0:
                    upload_btn.first.click()
                    print(f"  Clicked upload button")
                    page.wait_for_timeout(10000)  # Wait for processing
                else:
                    print(f"  No upload button found — file may auto-upload")
                    page.wait_for_timeout(10000)

                screenshot(page, f"KB_upload_result_{file_type}")

                # Check result
                body_after = page.locator('body').inner_text()
                if "error" in body_after.lower() and "error" not in body_before.lower():
                    error_lines = [l for l in body_after.split('\n') if 'error' in l.lower() or '⚠' in l]
                    error_msg = error_lines[0] if error_lines else "Unknown error"
                    results.append((file_type, filename, "FAILED", error_msg))
                    print(f"  RESULT: FAILED — {error_msg}")
                elif filename.lower() in body_after.lower() or "success" in body_after.lower() or "embedded" in body_after.lower() or "processed" in body_after.lower():
                    results.append((file_type, filename, "PASSED", "File uploaded and processed"))
                    print(f"  RESULT: PASSED")
                else:
                    # Check if chunk count changed
                    results.append((file_type, filename, "UNCERTAIN", "No clear success/error message"))
                    print(f"  RESULT: UNCERTAIN — checking further...")

            except Exception as e:
                results.append((file_type, filename, "ERROR", str(e)))
                print(f"  RESULT: ERROR — {e}")
                screenshot(page, f"KB_upload_error_{file_type}")
        else:
            print(f"  No file input found on page")
            results.append((file_type, filename, "BLOCKED", "No file input element found"))
            screenshot(page, f"KB_no_input_{file_type}")

    return results


def test_faq_creation(page):
    """Test creating FAQ entries in the KB."""
    print("\n=== TESTING FAQ CREATION ===\n")
    results = []

    for i, faq in enumerate(FAQ_ENTRIES):
        print(f"\nTesting FAQ #{i+1}: {faq['question']}")

        # Navigate to KB and click FAQ tab
        navigate_to_riverie_kb(page)
        page.wait_for_timeout(2000)

        # Click the FAQ tab
        try:
            faq_tab = page.locator('button:has-text("FAQ"), [role="tab"]:has-text("FAQ"), text=FAQ')
            faq_tab.first.click()
            page.wait_for_timeout(1000)
        except Exception as e:
            print(f"  Could not click FAQ tab: {e}")

        screenshot(page, f"KB_faq_tab_{i+1}")

        body = page.locator('body').inner_text()

        # Look for category input/select
        try:
            # Try to find category field
            category_inputs = page.locator('input[placeholder*="ategory"], input[placeholder*="Category"], select')
            if category_inputs.count() > 0:
                cat_el = category_inputs.first
                tag = cat_el.evaluate("el => el.tagName").lower()
                if tag == 'select':
                    # It's a dropdown — try to select or type
                    cat_el.select_option(label=faq['category'])
                else:
                    cat_el.fill(faq['category'])
                print(f"  Category set: {faq['category']}")
            else:
                print(f"  No category input found — checking for other fields")

            # Find question field
            question_input = page.locator('input[placeholder*="uestion"], input[placeholder*="Question"], textarea[placeholder*="uestion"]')
            if question_input.count() > 0:
                question_input.first.fill(faq['question'])
                print(f"  Question filled")
            else:
                # Try labeled inputs
                inputs = page.locator('input, textarea')
                for j in range(inputs.count()):
                    placeholder = inputs.nth(j).get_attribute('placeholder') or ''
                    if 'question' in placeholder.lower() or 'q' == placeholder.lower():
                        inputs.nth(j).fill(faq['question'])
                        print(f"  Question filled (by placeholder: {placeholder})")
                        break

            # Find answer field
            answer_input = page.locator('textarea[placeholder*="nswer"], textarea[placeholder*="Answer"], input[placeholder*="nswer"]')
            if answer_input.count() > 0:
                answer_input.first.fill(faq['answer'])
                print(f"  Answer filled")
            else:
                textareas = page.locator('textarea')
                if textareas.count() > 0:
                    textareas.last.fill(faq['answer'])
                    print(f"  Answer filled (last textarea)")

            screenshot(page, f"KB_faq_filled_{i+1}")

            # Click add/submit button
            add_btn = page.locator('button:has-text("Add"), button:has-text("Save"), button:has-text("Create"), button:has-text("Embed"), button:has-text("Submit")')
            if add_btn.count() > 0:
                add_btn.first.click()
                print(f"  Clicked submit button")
                page.wait_for_timeout(8000)
            else:
                print(f"  No submit button found")

            screenshot(page, f"KB_faq_result_{i+1}")

            # Check result
            body_after = page.locator('body').inner_text()
            if "error" in body_after.lower() and "error" not in body.lower():
                error_lines = [l for l in body_after.split('\n') if 'error' in l.lower() or '⚠' in l]
                error_msg = error_lines[0] if error_lines else "Unknown error"
                results.append((faq['question'], "FAILED", error_msg))
                print(f"  RESULT: FAILED — {error_msg}")
            elif faq['question'].split()[0:3] == faq['question'].split()[0:3]:
                # Check if the FAQ appears in the document list or success message
                if "success" in body_after.lower() or "added" in body_after.lower() or "embedded" in body_after.lower():
                    results.append((faq['question'], "PASSED", "FAQ created and embedded"))
                    print(f"  RESULT: PASSED")
                else:
                    results.append((faq['question'], "UNCERTAIN", "No clear confirmation"))
                    print(f"  RESULT: UNCERTAIN")

        except Exception as e:
            results.append((faq['question'], "ERROR", str(e)))
            print(f"  RESULT: ERROR — {e}")
            screenshot(page, f"KB_faq_error_{i+1}")

    return results


def verify_kb_after_tests(page):
    """Check KB stats after all uploads and FAQ entries."""
    print("\n=== VERIFYING KB STATS AFTER TESTS ===\n")

    navigate_to_riverie_kb(page)
    page.wait_for_timeout(3000)

    body = page.locator('body').inner_text()
    screenshot(page, "KB_final_stats")

    print("Final KB page content (relevant lines):")
    for line in body.split('\n'):
        line = line.strip()
        if any(kw in line.lower() for kw in ['chunk', 'document', 'vector', 'version', 'total', 'file', 'faq']):
            print(f"  {line}")

    # Also check the documents list
    # Click on Files tab to see uploaded documents
    try:
        files_tab = page.locator('button:has-text("Files"), [role="tab"]:has-text("Files"), text=Files')
        files_tab.first.click()
        page.wait_for_timeout(2000)
        screenshot(page, "KB_final_files_list")

        body = page.locator('body').inner_text()
        print("\nDocuments list:")
        for line in body.split('\n'):
            line = line.strip()
            if 'test_' in line.lower() or '.pdf' in line.lower() or '.txt' in line.lower() or '.csv' in line.lower() or '.docx' in line.lower() or '.json' in line.lower() or '.md' in line.lower() or '.html' in line.lower():
                print(f"  {line}")
    except Exception:
        pass

    # Check FAQ tab
    try:
        faq_tab = page.locator('button:has-text("FAQ"), [role="tab"]:has-text("FAQ"), text=FAQ')
        faq_tab.first.click()
        page.wait_for_timeout(2000)
        screenshot(page, "KB_final_faq_list")

        body = page.locator('body').inner_text()
        print("\nFAQ entries:")
        for line in body.split('\n'):
            line = line.strip()
            if 'breakfast' in line.lower() or 'pool' in line.lower() or 'cancellation' in line.lower() or 'category' in line.lower():
                print(f"  {line}")
    except Exception:
        pass

    return body


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(30000)

        try:
            login(page)

            # First, take a screenshot of the KB before testing to get baseline
            navigate_to_riverie_kb(page)
            page.wait_for_timeout(2000)
            screenshot(page, "KB_before_tests")
            body_before = page.locator('body').inner_text()
            print("\nKB state before tests:")
            for line in body_before.split('\n'):
                line = line.strip()
                if any(kw in line.lower() for kw in ['chunk', 'document', 'vector', 'version', 'total']):
                    print(f"  {line}")

            # Test file uploads
            file_results = test_file_uploads(page)

            # Test FAQ creation
            faq_results = test_faq_creation(page)

            # Verify final state
            final_body = verify_kb_after_tests(page)

            # Print summary
            print("\n" + "="*60)
            print("SUMMARY")
            print("="*60)

            print("\nFILE UPLOAD RESULTS:")
            for file_type, filename, status, detail in file_results:
                icon = "✅" if status == "PASSED" else "❌" if status in ("FAILED", "ERROR") else "⚠️"
                print(f"  {icon} {file_type:8s} ({filename}): {status} — {detail}")

            print("\nFAQ CREATION RESULTS:")
            for question, status, detail in faq_results:
                icon = "✅" if status == "PASSED" else "❌" if status in ("FAILED", "ERROR") else "⚠️"
                print(f"  {icon} {question[:50]}: {status} — {detail}")

        except Exception as e:
            print(f"\nFATAL ERROR: {e}")
            screenshot(page, "KB_fatal_error")
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
