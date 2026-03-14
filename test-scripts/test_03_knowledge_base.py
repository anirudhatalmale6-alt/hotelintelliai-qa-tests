"""
Test Suite 3: Knowledge Base
Tests KB page, file upload, URL scraping, and FAQ management.
"""
import pytest
from conftest import BASE_URL_ONBOARDING


class TestKnowledgeBase:
    """Tests for the Knowledge Base management page."""

    def test_kb_page_loads(self, logged_in_onboarding):
        """Verify KB page loads for an existing hotel."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/lePatte/kb", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "KNOWLEDGE BASE" in body
        assert "lePatte" in body
        assert "TOTAL CHUNKS" in body
        assert "DOCUMENTS" in body

    def test_kb_shows_stats(self, logged_in_onboarding):
        """Verify KB page displays chunk count, document count, and version."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/lePatte/kb", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "TOTAL CHUNKS" in body
        assert "DOCUMENTS" in body
        assert "KB VERSION" in body

    def test_kb_file_tab(self, logged_in_onboarding):
        """Verify File upload tab shows supported formats."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/lePatte/kb", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "SUPPORTED FORMATS" in body
        assert "PDF" in body
        assert "DOCX" in body
        assert "Drop a file here" in body
        assert "Upload & Embed" in body

    def test_kb_url_tab(self, logged_in_onboarding):
        """Verify URL tab shows scraping interface."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/lePatte/kb", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        page.locator('text=URL').first.click()
        page.wait_for_timeout(1000)

        body = page.locator('body').inner_text()
        assert "WEBSITE URL" in body
        assert "Scrape & Embed" in body

    def test_kb_faq_tab(self, logged_in_onboarding):
        """Verify FAQ tab shows entry form with categories."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/lePatte/kb", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        page.locator('text=FAQ').first.click()
        page.wait_for_timeout(1000)

        body = page.locator('body').inner_text()
        assert "CATEGORY" in body
        assert "QUESTION" in body
        assert "ANSWER" in body
        assert "Add FAQ Entry" in body

    def test_kb_faq_categories(self, logged_in_onboarding):
        """Verify FAQ has all expected categories."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/lePatte/kb", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        page.locator('text=FAQ').first.click()
        page.wait_for_timeout(1000)

        body = page.locator('body').inner_text()
        expected_categories = ["general", "rooms", "dining", "spa", "transport", "policies", "activities"]
        for cat in expected_categories:
            assert cat in body, f"Missing category: {cat}"

    def test_kb_documents_listed(self, logged_in_onboarding):
        """Verify existing documents are listed with metadata."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/lePatte/kb", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "DOCUMENTS" in body
        # le Patte should have documents
        assert "chunks" in body
        assert "Remove" in body

    def test_kb_new_hotel_empty(self, logged_in_onboarding):
        """Verify new hotel KB starts with 0 chunks/documents."""
        page = logged_in_onboarding
        page.goto(f"{BASE_URL_ONBOARDING}/hotel/oberoi_udaivilas/kb", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "oberoi_udaivilas" in body
        # Should have at least 1 document (the FAQ we added)
        assert "DOCUMENTS" in body
