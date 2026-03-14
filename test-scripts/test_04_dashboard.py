"""
Test Suite 4: Dashboard & Command Center
Tests the super admin dashboard and hotel command center pages.
"""
import pytest
from conftest import BASE_URL_DASHBOARD


class TestDashboardHotelSelection:
    """Tests for the hotel selection page on the dashboard."""

    def test_hotel_cards_displayed(self, logged_in_dashboard):
        """Verify hotel cards are shown after login."""
        page = logged_in_dashboard
        body = page.locator('body').inner_text()
        assert "le Patte" in body
        assert "Riverie" in body

    def test_hotel_card_shows_channels(self, logged_in_dashboard):
        """Verify hotel cards show channel badges."""
        page = logged_in_dashboard
        body = page.locator('body').inner_text()
        assert "whatsapp" in body
        assert "telegram" in body

    def test_click_hotel_redirects_to_subdomain(self, logged_in_dashboard):
        """Verify clicking a hotel redirects to its subdomain."""
        page = logged_in_dashboard
        page.locator('text=Riverie').first.click()
        page.wait_for_timeout(5000)

        assert "hotel_riviera_cr.hotelintelliai.com" in page.url


class TestCommandCenter:
    """Tests for the hotel command center (subdomain dashboard)."""

    def _go_to_riverie(self, logged_in_dashboard):
        """Helper to navigate to Riverie command center."""
        page = logged_in_dashboard
        page.locator('text=Riverie').first.click()
        page.wait_for_timeout(5000)
        return page

    def test_overview_page(self, logged_in_dashboard):
        """Verify Overview page shows stats and widgets."""
        page = self._go_to_riverie(logged_in_dashboard)
        body = page.locator('body').inner_text()

        assert "Overview" in body
        assert "TOTAL CONVS" in body
        assert "TODAY" in body
        assert "GUESTS" in body
        assert "MESSAGES" in body
        assert "ESCALATIONS" in body
        assert "CONVERSATIONS / DAY" in body

    def test_sidebar_navigation(self, logged_in_dashboard):
        """Verify all sidebar menu items are present."""
        page = self._go_to_riverie(logged_in_dashboard)
        body = page.locator('body').inner_text()

        assert "Overview" in body
        assert "Conversations" in body
        assert "Guests" in body
        assert "Escalations" in body
        assert "Channels" in body
        assert "Knowledge Base" in body
        assert "Debug" in body

    def test_conversations_page(self, logged_in_dashboard):
        """Verify Conversations page lists conversations."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Conversations').first.click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "Conversations" in body
        assert "RECENT" in body
        assert "THREAD" in body

    def test_guests_page(self, logged_in_dashboard):
        """Verify Guests page shows guest profiles."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Guests').first.click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "Guests" in body
        assert "GUEST PROFILES" in body
        assert "TIER" in body
        assert "LANG" in body

    def test_escalations_page(self, logged_in_dashboard):
        """Verify Escalations page shows open tickets."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Escalations').first.click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "Escalations" in body
        assert "OPEN TICKETS" in body

    def test_channels_page(self, logged_in_dashboard):
        """Verify Channels page shows webhook URLs and status."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Channels').first.click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "Channels" in body
        assert "STATUS" in body
        assert "WEBHOOK URLS" in body
        assert "WHATSAPP" in body
        assert "TELEGRAM" in body
        assert "EMAIL" in body

    def test_debug_page_tabs(self, logged_in_dashboard):
        """Verify Debug page has all diagnostic tool tabs."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Debug').first.click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "Health Check" in body
        assert "RAG Tester" in body
        assert "Msg Simulator" in body
        assert "DB Stats" in body
        assert "Guest Lookup" in body

    def test_health_check(self, logged_in_dashboard):
        """Verify Health Check returns healthy status."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Debug').first.click()
        page.wait_for_timeout(2000)

        page.locator('text=Run Health Check').click()
        page.wait_for_timeout(8000)

        body = page.locator('body').inner_text()
        assert "Hotel is healthy" in body
        assert "HOTEL RECORD" in body
        assert "QDRANT" in body or "VECTORS" in body

    def test_rag_tester(self, logged_in_dashboard):
        """Verify RAG Tester returns results for a query."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Debug').first.click()
        page.wait_for_timeout(2000)
        page.locator('button:has-text("RAG Tester")').click()
        page.wait_for_timeout(2000)

        # Fill query
        query_input = page.locator('input[placeholder*="Search"]')
        query_input.fill("do you have a spa?")
        page.locator('button:has-text("Search RAG")').click()
        page.wait_for_timeout(10000)

        body = page.locator('body').inner_text()
        assert "TOTAL RESULTS" in body
        assert "ABOVE THRESHOLD" in body

    def test_msg_simulator(self, logged_in_dashboard):
        """Verify Msg Simulator returns AI response."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Debug').first.click()
        page.wait_for_timeout(2000)
        page.locator('button:has-text("Msg Simulator")').click()
        page.wait_for_timeout(2000)

        # Fill message
        inputs = page.locator('input')
        inputs.nth(2).fill("What rooms do you have?")
        page.locator('button:has-text("Simulate")').click()
        page.wait_for_timeout(15000)

        body = page.locator('body').inner_text()
        assert "AGENT RESPONSE" in body
        assert "INTENT" in body
        assert "ELAPSED" in body

    def test_db_stats(self, logged_in_dashboard):
        """Verify DB Stats shows table counts."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Debug').first.click()
        page.wait_for_timeout(2000)
        page.locator('button:has-text("DB Stats")').click()
        page.wait_for_timeout(2000)

        page.locator('button:has-text("Refresh")').click()
        page.wait_for_timeout(8000)

        body = page.locator('body').inner_text()
        assert "POSTGRESQL TABLES" in body
        assert "hotels" in body
        assert "guests" in body
        assert "QDRANT COLLECTIONS" in body
