"""
Test Suite 7: Knowledge Base — File Uploads & FAQ Creation
Tests all supported file formats for upload and FAQ entry creation + embedding.
Verifies uploaded content is searchable via RAG tester.

Supported formats (per UI): PDF, DOCX, ODT, TXT, MD, CSV, PNG, JPG, WEBP
Unsupported formats tested: JSON, HTML (should show error)
"""
import os
import pytest
from conftest import BASE_URL_ONBOARDING, BASE_URL_DASHBOARD


# ---- Helpers ----

TEST_FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test-files")


def _go_to_riverie_kb(page):
    """Navigate to Riverie hotel KB on onboarding portal."""
    page.goto(
        f"{BASE_URL_ONBOARDING}/hotel/hotel_riviera_cr/kb",
        wait_until="networkidle",
        timeout=30000,
    )
    page.wait_for_timeout(3000)


def _click_files_tab(page):
    """Ensure we are on the File tab on the KB page.
    The KB page defaults to showing the file upload area.
    The tab may be a button, div, or other element with '📄 File' text."""
    # Try multiple selectors for the File tab
    for selector in ['button:has-text("File")', 'text=📄 File', '[class*="tab"]:has-text("File")']:
        tab = page.locator(selector)
        if tab.count() > 0:
            try:
                tab.first.click(timeout=3000)
                page.wait_for_timeout(1000)
                return
            except Exception:
                continue
    # KB page defaults to file view — no click needed


def _click_faq_tab(page):
    """Click the FAQ tab on the KB page."""
    page.locator('button:has-text("FAQ")').first.click()
    page.wait_for_timeout(1000)


def _upload_file(page, filename, wait_ms=10000):
    """Upload a file to KB and return the page body text after upload."""
    filepath = os.path.abspath(os.path.join(TEST_FILES_DIR, filename))
    file_input = page.locator('input[type="file"]')
    file_input.first.set_input_files(filepath)
    page.wait_for_timeout(2000)

    upload_btn = page.locator(
        'button:has-text("Upload"), button:has-text("Embed"), button:has-text("Upload & Embed")'
    )
    if upload_btn.count() > 0:
        upload_btn.first.click()
        page.wait_for_timeout(wait_ms)

    return page.locator("body").inner_text()


# ---- File Upload Tests ----


class TestKBFileUpload:
    """Tests for KB file upload functionality across all supported formats."""

    def test_supported_formats_listed(self, logged_in_onboarding):
        """Verify the KB file upload page shows all supported formats."""
        page = logged_in_onboarding
        _go_to_riverie_kb(page)
        _click_files_tab(page)

        body = page.locator("body").inner_text()
        assert "SUPPORTED FORMATS" in body
        # Core formats that must be listed
        for fmt in ["PDF", "DOCX", "TXT", "MD", "CSV"]:
            assert fmt in body, f"Format {fmt} not listed in supported formats"

    def test_upload_txt(self, logged_in_onboarding):
        """Test uploading a .txt file — should embed successfully."""
        page = logged_in_onboarding
        _go_to_riverie_kb(page)
        _click_files_tab(page)

        body = _upload_file(page, "test_hotel_info.txt")
        assert "Embedded" in body or "test_hotel_info" in body, \
            "TXT file upload did not produce embedded chunks"

    def test_upload_csv(self, logged_in_onboarding):
        """Test uploading a .csv file — should embed successfully."""
        page = logged_in_onboarding
        _go_to_riverie_kb(page)
        _click_files_tab(page)

        body = _upload_file(page, "test_room_rates.csv")
        assert "Embedded" in body or "test_room_rates" in body, \
            "CSV file upload did not produce embedded chunks"

    def test_upload_pdf(self, logged_in_onboarding):
        """Test uploading a .pdf file — should embed successfully."""
        page = logged_in_onboarding
        _go_to_riverie_kb(page)
        _click_files_tab(page)

        body = _upload_file(page, "test_dining_guide.pdf")
        assert "Embedded" in body or "test_dining_guide" in body, \
            "PDF file upload did not produce embedded chunks"

    def test_upload_docx(self, logged_in_onboarding):
        """Test uploading a .docx file — should embed successfully."""
        page = logged_in_onboarding
        _go_to_riverie_kb(page)
        _click_files_tab(page)

        body = _upload_file(page, "test_guest_policies.docx")
        assert "Embedded" in body or "test_guest_policies" in body, \
            "DOCX file upload did not produce embedded chunks"

    def test_upload_md(self, logged_in_onboarding):
        """Test uploading a .md file — should embed successfully."""
        page = logged_in_onboarding
        _go_to_riverie_kb(page)
        _click_files_tab(page)

        body = _upload_file(page, "test_spa_menu.md")
        assert "Embedded" in body or "test_spa_menu" in body, \
            "MD file upload did not produce embedded chunks"

    def test_upload_json_unsupported(self, logged_in_onboarding):
        """Test uploading a .json file — should show unsupported error after embed attempt."""
        page = logged_in_onboarding
        _go_to_riverie_kb(page)
        _click_files_tab(page)

        # Upload and click embed — error shows after embed attempt
        body = _upload_file(page, "test_amenities.json", wait_ms=5000)
        # JSON is not in supported formats — should show extraction error
        assert "Unsupported file type" in body or "Could not extract" in body, \
            "JSON file should show unsupported file type error after embed attempt"

    def test_upload_html_unsupported(self, logged_in_onboarding):
        """Test uploading a .html file — should show unsupported error after embed attempt."""
        page = logged_in_onboarding
        _go_to_riverie_kb(page)
        _click_files_tab(page)

        # Upload and click embed — error shows after embed attempt
        body = _upload_file(page, "test_facilities.html", wait_ms=5000)
        assert "Unsupported file type" in body or "Could not extract" in body, \
            "HTML file should show unsupported file type error after embed attempt"

    def test_uploaded_files_appear_in_document_list(self, logged_in_onboarding):
        """Verify uploaded test files appear in the documents list."""
        page = logged_in_onboarding
        _go_to_riverie_kb(page)

        body = page.locator("body").inner_text()
        # Check that at least some of our test files appear
        test_files_found = 0
        for filename in ["test_hotel_info", "test_room_rates", "test_dining_guide",
                         "test_guest_policies", "test_spa_menu"]:
            if filename in body:
                test_files_found += 1

        assert test_files_found >= 3, \
            f"Only {test_files_found} test files found in document list (expected >= 3)"


# ---- FAQ Tests ----


class TestKBFAQ:
    """Tests for KB FAQ entry creation and embedding."""

    def test_faq_tab_has_form_fields(self, logged_in_onboarding):
        """Verify FAQ tab has category, question, and answer fields."""
        page = logged_in_onboarding
        _go_to_riverie_kb(page)
        _click_faq_tab(page)

        body = page.locator("body").inner_text()
        assert "CATEGORY" in body, "FAQ form missing CATEGORY field"
        assert "QUESTION" in body, "FAQ form missing QUESTION field"
        assert "ANSWER" in body, "FAQ form missing ANSWER field"

    def test_faq_add_button_disabled_when_empty(self, logged_in_onboarding):
        """Verify Add FAQ button is disabled when fields are empty."""
        page = logged_in_onboarding
        _go_to_riverie_kb(page)
        _click_faq_tab(page)

        add_btn = page.locator('button:has-text("Add FAQ"), button:has-text("Add & Embed")')
        if add_btn.count() > 0:
            is_disabled = add_btn.first.get_attribute("disabled")
            assert is_disabled is not None, \
                "Add FAQ button should be disabled when fields are empty"

    def test_create_faq_entry(self, logged_in_onboarding):
        """Test creating a new FAQ entry with question and answer."""
        page = logged_in_onboarding
        _go_to_riverie_kb(page)
        _click_faq_tab(page)

        # Fill question
        q_input = page.locator("input").first
        for i in range(page.locator("input").count()):
            inp = page.locator("input").nth(i)
            if inp.is_visible():
                inp_type = (inp.get_attribute("type") or "").lower()
                if inp_type not in ("email", "password", "file", "hidden"):
                    q_input = inp
                    break
        q_input.fill("What are the gym hours?")

        # Fill answer
        ta = page.locator("textarea")
        for i in range(ta.count()):
            if ta.nth(i).is_visible():
                ta.nth(i).fill(
                    "The fitness center is open 24 hours a day for all hotel guests. "
                    "Personal trainers are available by appointment from 6 AM to 9 PM."
                )
                break

        # Button should now be enabled — click it
        add_btn = page.locator('button:has-text("Add FAQ"), button:has-text("Add & Embed"), button:has-text("Embed")')
        page.wait_for_timeout(500)
        add_btn.first.click()
        page.wait_for_timeout(8000)

        # Verify: navigate back to KB and check document list
        _go_to_riverie_kb(page)
        body = page.locator("body").inner_text()

        faq_count = body.lower().count("faq ·")
        assert faq_count >= 1, "No FAQ entries found in KB after creation"

    def test_faq_entries_exist_in_kb(self, logged_in_onboarding):
        """Verify FAQ entries appear in the KB document list."""
        page = logged_in_onboarding
        _go_to_riverie_kb(page)

        body = page.locator("body").inner_text()
        faq_count = body.lower().count("faq ·")
        assert faq_count >= 1, \
            "No FAQ entries found in KB document list"


# ---- RAG Verification Tests ----


class TestKBRAGVerification:
    """Verify uploaded files and FAQ entries are searchable via RAG tester."""

    def _search_rag(self, page, query, wait_ms=10000):
        """Run a RAG search query on Riverie and return body text."""
        query_input = page.locator('input[placeholder*="Search"]')
        query_input.fill("")
        query_input.fill(query)
        page.locator('button:has-text("Search RAG")').click()
        page.wait_for_timeout(wait_ms)
        return page.locator("body").inner_text()

    def _go_to_rag_tester(self, logged_in_dashboard):
        """Navigate to Riverie Debug > RAG Tester."""
        page = logged_in_dashboard
        page.locator("text=Riverie").first.click()
        page.wait_for_timeout(5000)
        page.locator("text=Debug").first.click()
        page.wait_for_timeout(2000)
        page.locator('button:has-text("RAG Tester")').click()
        page.wait_for_timeout(2000)
        return page

    def test_rag_finds_faq_breakfast(self, logged_in_dashboard):
        """Verify RAG returns breakfast FAQ content."""
        page = self._go_to_rag_tester(logged_in_dashboard)
        body = self._search_rag(page, "what time is breakfast served")

        assert "TOTAL RESULTS" in body
        assert "ABOVE THRESHOLD" in body
        assert "breakfast" in body.lower(), \
            "RAG search for breakfast did not return FAQ content"

    def test_rag_finds_csv_room_rates(self, logged_in_dashboard):
        """Verify RAG returns CSV room rates data."""
        page = self._go_to_rag_tester(logged_in_dashboard)
        body = self._search_rag(page, "room rates deluxe suite")

        assert "TOTAL RESULTS" in body
        # CSV content should include room type data
        has_room_data = any(kw in body.lower() for kw in ["standard", "deluxe", "suite", "rate"])
        assert has_room_data, \
            "RAG search for room rates did not return CSV content"

    def test_rag_finds_txt_hotel_info(self, logged_in_dashboard):
        """Verify RAG returns TXT file hotel info content."""
        page = self._go_to_rag_tester(logged_in_dashboard)
        body = self._search_rag(page, "check-in check-out time pool hours")

        assert "TOTAL RESULTS" in body
        has_info = any(kw in body.lower() for kw in ["check-in", "check-out", "pool"])
        assert has_info, \
            "RAG search for hotel info did not return TXT file content"

    def test_rag_finds_pdf_dining(self, logged_in_dashboard):
        """Verify RAG returns PDF dining guide content."""
        page = self._go_to_rag_tester(logged_in_dashboard)
        body = self._search_rag(page, "dining guide restaurant room service")

        assert "TOTAL RESULTS" in body
        has_dining = any(kw in body.lower() for kw in ["restaurant", "dining", "room service", "buffet"])
        assert has_dining, \
            "RAG search for dining did not return PDF content"

    def test_rag_finds_md_spa_menu(self, logged_in_dashboard):
        """Verify RAG returns Markdown spa menu content."""
        page = self._go_to_rag_tester(logged_in_dashboard)
        body = self._search_rag(page, "spa massage treatment facial")

        assert "TOTAL RESULTS" in body
        has_spa = any(kw in body.lower() for kw in ["massage", "spa", "facial", "scrub"])
        assert has_spa, \
            "RAG search for spa did not return Markdown file content"

    def test_rag_finds_faq_cancellation(self, logged_in_dashboard):
        """Verify RAG returns cancellation policy FAQ content."""
        page = self._go_to_rag_tester(logged_in_dashboard)
        body = self._search_rag(page, "cancellation policy")

        assert "TOTAL RESULTS" in body
        has_cancel = any(kw in body.lower() for kw in ["cancellation", "48 hours", "one night"])
        assert has_cancel, \
            "RAG search for cancellation policy did not return FAQ content"
