"""
Test Suite 6: Deep Riverie Testing
Automated regression tests for bugs found during deep testing of The Riverie by Katathani.
Covers BUG-006 (conversation threads), BUG-008 (charts), BUG-009 (VIP filter),
BUG-010 (guest profile drill-down), BUG-011 (escalation drill-down).
"""
import pytest
from conftest import BASE_URL_DASHBOARD


class TestRiverieDeep:
    """Deep tests for The Riverie by Katathani hotel command center."""

    def _go_to_riverie(self, logged_in_dashboard):
        """Navigate to Riverie command center."""
        page = logged_in_dashboard
        page.locator('text=Riverie').first.click()
        page.wait_for_timeout(5000)
        return page

    # --- BUG-006: Conversation Threads Show "No messages" ---

    def test_conversation_list_has_entries(self, logged_in_dashboard):
        """Verify Riverie has conversations listed."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Conversations').first.click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "RECENT" in body
        # Should have at least one conversation entry
        assert "nick" in body.lower() or "njain" in body.lower() or "anirudha" in body.lower()

    def test_conversation_thread_shows_messages(self, logged_in_dashboard):
        """BUG-006: Clicking a conversation thread should show messages.
        EXPECTED TO FAIL until BUG-006 is fixed."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Conversations').first.click()
        page.wait_for_timeout(3000)

        # Click on the first conversation in the list
        conversations = page.locator('.conversation-item, [class*="conversation"], [class*="conv-"]')
        if conversations.count() > 0:
            conversations.first.click()
            page.wait_for_timeout(3000)
        else:
            # Fallback: click on any text that looks like a conversation name
            page.locator('text=nick jain').first.click()
            page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        # This assertion will FAIL until BUG-006 is fixed
        # When fixed, thread panel should NOT show "No messages"
        assert "No messages" not in body, \
            "BUG-006: Conversation thread shows 'No messages' — messages exist in DB but aren't rendered"

    def test_multiple_conversation_threads_have_messages(self, logged_in_dashboard):
        """BUG-006: Verify multiple conversation threads load messages.
        EXPECTED TO FAIL until BUG-006 is fixed."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Conversations').first.click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        empty_threads = 0

        # Try clicking different conversations
        conversation_names = ["nick jain", "njain2000", "njain200"]
        for name in conversation_names:
            try:
                page.locator(f'text={name}').first.click(timeout=3000)
                page.wait_for_timeout(2000)
                thread_body = page.locator('body').inner_text()
                if "No messages" in thread_body:
                    empty_threads += 1
            except Exception:
                continue

        # This will FAIL until BUG-006 is fixed
        assert empty_threads == 0, \
            f"BUG-006: {empty_threads} conversation thread(s) show 'No messages'"

    # --- BUG-008: Overview Charts Show "No data" ---

    def test_overview_stats_counters(self, logged_in_dashboard):
        """Verify Overview page shows non-zero stats (proves data exists)."""
        page = self._go_to_riverie(logged_in_dashboard)
        body = page.locator('body').inner_text()

        # Stats counters should show data
        assert "TOTAL CONVS" in body
        assert "MESSAGES" in body
        assert "GUESTS" in body
        assert "ESCALATIONS" in body

    def test_overview_conversations_chart_has_data(self, logged_in_dashboard):
        """BUG-008: Conversations/Day chart should show data when conversations exist.
        EXPECTED TO FAIL until BUG-008 is fixed."""
        page = self._go_to_riverie(logged_in_dashboard)
        body = page.locator('body').inner_text()

        # Check for chart area
        assert "CONVERSATIONS / DAY" in body

        # This will FAIL until BUG-008 is fixed
        # The chart should render data, not show "No data"
        chart_section = body[body.index("CONVERSATIONS / DAY"):]
        assert "No data" not in chart_section[:200], \
            "BUG-008: 'Conversations / Day' chart shows 'No data' despite having conversations"

    def test_overview_channel_chart_has_data(self, logged_in_dashboard):
        """BUG-008: By Channel chart should show data when channels have conversations.
        EXPECTED TO FAIL until BUG-008 is fixed."""
        page = self._go_to_riverie(logged_in_dashboard)
        body = page.locator('body').inner_text()

        if "BY CHANNEL" in body:
            channel_section = body[body.index("BY CHANNEL"):]
            assert "No data" not in channel_section[:200], \
                "BUG-008: 'By Channel' chart shows 'No data' despite having channel conversations"

    # --- BUG-009: VIP Tab Doesn't Filter Guests ---

    def test_guests_all_tab_shows_guests(self, logged_in_dashboard):
        """Verify ALL tab shows guests."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Guests').first.click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "GUEST PROFILES" in body
        # Should have guests listed
        assert "nick" in body.lower() or "anirudha" in body.lower()

    def test_guests_vip_tab_filters_correctly(self, logged_in_dashboard):
        """BUG-009: VIP tab should show only VIP-tier guests, not all guests.
        EXPECTED TO FAIL until BUG-009 is fixed."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Guests').first.click()
        page.wait_for_timeout(3000)

        # Get ALL tab guest count
        all_body = page.locator('body').inner_text()

        # Click VIP tab
        page.locator('text=VIP').first.click()
        page.wait_for_timeout(2000)

        vip_body = page.locator('body').inner_text()

        # Count guest names in each tab
        guest_names = ["nick jain", "anirudha", "njain2000", "njain200"]
        all_count = sum(1 for name in guest_names if name.lower() in all_body.lower())
        vip_count = sum(1 for name in guest_names if name.lower() in vip_body.lower())

        # VIP tab should show fewer guests than ALL tab (only VIP tier)
        # This will FAIL until BUG-009 is fixed
        assert vip_count < all_count, \
            f"BUG-009: VIP tab shows {vip_count} guests, same as ALL tab ({all_count}). VIP filter is not working."

    # --- BUG-010: Guest Profiles Not Clickable ---

    def test_guest_profile_clickable(self, logged_in_dashboard):
        """BUG-010: Clicking a guest should open a detailed profile view.
        EXPECTED TO FAIL until BUG-010 is fixed."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Guests').first.click()
        page.wait_for_timeout(3000)

        body_before = page.locator('body').inner_text()

        # Try clicking on a guest name
        try:
            page.locator('text=nick jain').first.click(timeout=3000)
            page.wait_for_timeout(2000)
        except Exception:
            pytest.fail("BUG-010: Guest row is not clickable — no interaction handler")

        body_after = page.locator('body').inner_text()

        # After clicking, page content should change to show detailed profile
        # Look for detailed profile indicators (conversation history, full preferences, etc.)
        has_detail = (
            "conversation" in body_after.lower()
            or "history" in body_after.lower()
            or "activity" in body_after.lower()
            or "profile detail" in body_after.lower()
            or body_after != body_before  # At minimum, something should change
        )

        assert has_detail, \
            "BUG-010: Clicking guest did not open a detailed profile view"

    # --- BUG-011: Escalation Items Not Expandable ---

    def test_escalation_list_has_entries(self, logged_in_dashboard):
        """Verify Escalations page lists open tickets."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Escalations').first.click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()
        assert "OPEN TICKETS" in body

    def test_escalation_item_expandable(self, logged_in_dashboard):
        """BUG-011: Clicking an escalation should expand it or open details.
        EXPECTED TO FAIL until BUG-011 is fixed."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Escalations').first.click()
        page.wait_for_timeout(3000)

        body_before = page.locator('body').inner_text()

        # Try clicking on an escalation item
        escalation_items = page.locator('.escalation-item, [class*="escalation"], [class*="ticket"]')
        if escalation_items.count() > 0:
            escalation_items.first.click()
            page.wait_for_timeout(2000)
        else:
            # Fallback: try clicking within the escalations area
            try:
                page.locator('[class*="card"]').nth(1).click(timeout=3000)
                page.wait_for_timeout(2000)
            except Exception:
                pytest.fail("BUG-011: Escalation items are not clickable elements")

        body_after = page.locator('body').inner_text()

        # After clicking, should see expanded details (resolution, assignment, context)
        has_expanded = (
            "resolution" in body_after.lower()
            or "assign" in body_after.lower()
            or "respond" in body_after.lower()
            or body_after != body_before
        )

        assert has_expanded, \
            "BUG-011: Clicking escalation did not expand or show detail view"

    # --- BUG-002: Guest Lookup Backend Error ---

    def test_guest_lookup_returns_result(self, logged_in_dashboard):
        """BUG-002: Guest Lookup should return guest info, not a backend error.
        EXPECTED TO FAIL until BUG-002 is fixed."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Debug').first.click()
        page.wait_for_timeout(2000)

        # Click Guest Lookup tab
        page.locator('button:has-text("Guest Lookup")').click()
        page.wait_for_timeout(2000)

        # Find the identifier input and fill it
        inputs = page.locator('input')
        for i in range(inputs.count()):
            placeholder = inputs.nth(i).get_attribute('placeholder') or ''
            if 'guest' in placeholder.lower() or 'lookup' in placeholder.lower() or 'identifier' in placeholder.lower() or 'search' in placeholder.lower():
                inputs.nth(i).fill("njain2000")
                break
        else:
            # Fallback: use the last visible input
            inputs.last.fill("njain2000")

        # Click the Lookup action button (not the tab button)
        buttons = page.locator('button')
        for i in range(buttons.count()):
            text = buttons.nth(i).inner_text()
            if "Lookup" in text and "Guest" not in text:
                buttons.nth(i).click()
                break
        page.wait_for_timeout(5000)

        body = page.locator('body').inner_text()

        # This will FAIL until BUG-002 is fixed
        assert "cannot import name" not in body, \
            "BUG-002: Guest Lookup returns import error — GuestChannel missing from schemas.py"
        assert "Error" not in body or "⚠" not in body, \
            "BUG-002: Guest Lookup returns a backend error"

    # --- BUG-003: Dashboard KB Shows "No hotel assigned" ---

    def test_dashboard_kb_shows_hotel_content(self, logged_in_dashboard):
        """BUG-003: Dashboard KB page should show KB content for the selected hotel.
        EXPECTED TO FAIL until BUG-003 is fixed."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Knowledge Base').first.click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()

        # This will FAIL until BUG-003 is fixed
        assert "No hotel assigned" not in body, \
            "BUG-003: Dashboard KB shows 'No hotel assigned' instead of hotel KB content"

    # --- Riverie Channel Verification ---

    def test_riverie_channels_live_status(self, logged_in_dashboard):
        """Verify Riverie channels show correct live/off status."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Channels').first.click()
        page.wait_for_timeout(3000)

        body = page.locator('body').inner_text()

        # WhatsApp, Telegram, LINE, Email should be live
        assert "WHATSAPP" in body
        assert "TELEGRAM" in body
        assert "LINE" in body
        assert "EMAIL" in body

        # Should have webhook URLs displayed
        assert "api.hotelintelliai.com" in body or "webhook" in body.lower()

    # --- Riverie Debug Tools Verification ---

    def test_riverie_health_check_healthy(self, logged_in_dashboard):
        """Verify Riverie health check shows healthy status with KB stats."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Debug').first.click()
        page.wait_for_timeout(2000)

        page.locator('text=Run Health Check').click()
        page.wait_for_timeout(8000)

        body = page.locator('body').inner_text()
        assert "Hotel is healthy" in body
        assert "HOTEL RECORD" in body

    def test_riverie_msg_simulator_responds(self, logged_in_dashboard):
        """Verify AI concierge responds to a guest query via Msg Simulator."""
        page = self._go_to_riverie(logged_in_dashboard)
        page.locator('text=Debug').first.click()
        page.wait_for_timeout(2000)
        page.locator('button:has-text("Msg Simulator")').click()
        page.wait_for_timeout(2000)

        # Fill in a test message
        inputs = page.locator('input')
        inputs.nth(2).fill("do you have a spa?")
        page.locator('button:has-text("Simulate")').click()
        page.wait_for_timeout(15000)

        body = page.locator('body').inner_text()
        assert "AGENT RESPONSE" in body
        assert "INTENT" in body
        assert "ELAPSED" in body
        # Response should mention spa-related content
        assert "spa" in body.lower() or "tivaa" in body.lower() or "wellness" in body.lower()
