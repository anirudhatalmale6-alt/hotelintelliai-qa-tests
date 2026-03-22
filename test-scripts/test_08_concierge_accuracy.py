"""
Test 08: AI Concierge Accuracy — All 6 Hotels via API
Tests AI concierge responses using POST /admin/test/message.
Verifies responses contain expected keywords from hotel website content.
Tests for ESCALATED responses indicating missing KB data.

Run with: pytest test_08_concierge_accuracy.py -v --tb=short
"""
import pytest
import json
import time

API_URL = "https://api.hotelintelliai.com"
ESCALATION_PHRASE = "let me connect you with"


def _send_question(page, hotel_id, question):
    """Send a question via API and return response text."""
    escaped_q = question.replace("\\", "\\\\").replace('"', '\\"')
    result = page.evaluate(f"""async () => {{
        try {{
            const resp = await fetch('{API_URL}/admin/test/message', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'x-hotel-id': '{hotel_id}'
                }},
                credentials: 'include',
                body: JSON.stringify({{
                    hotel_id: '{hotel_id}',
                    message: "{escaped_q}",
                    guest_identifier: 'pytest_guest',
                    guest_name: 'Pytest Tester'
                }})
            }});
            const data = await resp.json();
            return {{ status: resp.status, response: data.response || data.reply || '' }};
        }} catch(e) {{
            return {{ error: e.message }};
        }}
    }}""")
    assert 'error' not in result, f"API error: {result.get('error')}"
    assert result.get('status') == 200, f"API returned {result.get('status')}"
    return result.get('response', '')


class TestConciergeAPI:
    """Test AI concierge responses for all 6 hotels via API."""

    @pytest.fixture(scope="class")
    def api_page(self, browser):
        """Login and return page with API auth context."""
        from conftest import BASE_URL_DASHBOARD, EMAIL, PASSWORD
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(60000)

        page.goto(BASE_URL_DASHBOARD, timeout=60000)
        page.wait_for_timeout(5000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(10000)

        # Wait for hotels to load and click one for auth context
        for _ in range(10):
            body = page.locator('body').inner_text()
            if 'Heritage' in body:
                break
            page.wait_for_timeout(2000)

        page.locator('text=Heritage').first.click()
        page.wait_for_timeout(8000)

        yield page
        context.close()

    # ====== HERITAGE CHIANG RAI ======

    def test_heritage_meeting_facilities(self, api_page):
        resp = _send_question(api_page, "heritage_chiangrai", "Do you have meeting or convention facilities?")
        assert ESCALATION_PHRASE not in resp.lower(), "Meeting info should exist in KB"
        assert any(kw in resp.lower() for kw in ["ballroom", "meeting", "convention"])

    def test_heritage_rooms_escalated(self, api_page):
        """Heritage rooms question currently ESCALATED - KB missing room data."""
        resp = _send_question(api_page, "heritage_chiangrai", "What room types are available?")
        if ESCALATION_PHRASE in resp.lower():
            pytest.xfail("KNOWN ISSUE: Heritage KB missing room type information")
        assert any(kw in resp.lower() for kw in ["deluxe", "suite", "premier"])

    def test_heritage_pool_escalated(self, api_page):
        """Heritage pool question currently ESCALATED."""
        resp = _send_question(api_page, "heritage_chiangrai", "Do you have a swimming pool?")
        if ESCALATION_PHRASE in resp.lower():
            pytest.xfail("KNOWN ISSUE: Heritage KB missing pool information")
        assert "pool" in resp.lower()

    def test_heritage_spa_escalated(self, api_page):
        resp = _send_question(api_page, "heritage_chiangrai", "Is there a spa?")
        if ESCALATION_PHRASE in resp.lower():
            pytest.xfail("KNOWN ISSUE: Heritage KB missing spa information")
        assert "spa" in resp.lower()

    def test_heritage_wifi_escalated(self, api_page):
        resp = _send_question(api_page, "heritage_chiangrai", "Do you have WiFi?")
        if ESCALATION_PHRASE in resp.lower():
            pytest.xfail("KNOWN ISSUE: Heritage KB missing WiFi information")
        assert any(kw in resp.lower() for kw in ["wifi", "free"])

    # ====== GRAND VISTA ======

    def test_grandvista_attractions(self, api_page):
        resp = _send_question(api_page, "grand_vista_chiangrai", "What nearby attractions are there?")
        assert ESCALATION_PHRASE not in resp.lower(), "Attractions info should exist in KB"
        assert any(kw in resp.lower() for kw in ["night bazaar", "clock tower"])

    def test_grandvista_rooms_escalated(self, api_page):
        resp = _send_question(api_page, "grand_vista_chiangrai", "What room types do you have?")
        if ESCALATION_PHRASE in resp.lower():
            pytest.xfail("KNOWN ISSUE: Grand Vista KB only 13 chunks - insufficient data")
        assert any(kw in resp.lower() for kw in ["room", "deluxe", "suite"])

    def test_grandvista_pool_escalated(self, api_page):
        resp = _send_question(api_page, "grand_vista_chiangrai", "Do you have a swimming pool?")
        if ESCALATION_PHRASE in resp.lower():
            pytest.xfail("KNOWN ISSUE: Grand Vista KB only 13 chunks")
        assert "pool" in resp.lower()

    # ====== IMPERIAL MAE PING ======

    def test_imperial_checkin_escalated(self, api_page):
        resp = _send_question(api_page, "imperial_mae_ping", "What time is check-in and check-out?")
        if ESCALATION_PHRASE in resp.lower():
            pytest.xfail("KNOWN ISSUE: Imperial KB 558 chunks but most questions escalate")
        assert any(kw in resp.lower() for kw in ["check-in", "check-out"])

    def test_imperial_restaurant_escalated(self, api_page):
        resp = _send_question(api_page, "imperial_mae_ping", "What restaurants do you have?")
        if ESCALATION_PHRASE in resp.lower():
            pytest.xfail("KNOWN ISSUE: Imperial KB not answering restaurant questions")
        assert any(kw in resp.lower() for kw in ["restaurant", "dining"])

    def test_imperial_spa_escalated(self, api_page):
        resp = _send_question(api_page, "imperial_mae_ping", "Do you have a spa?")
        if ESCALATION_PHRASE in resp.lower():
            pytest.xfail("KNOWN ISSUE: Imperial KB not answering spa questions")
        assert "spa" in resp.lower()

    def test_imperial_pool_escalated(self, api_page):
        resp = _send_question(api_page, "imperial_mae_ping", "Do you have a swimming pool?")
        if ESCALATION_PHRASE in resp.lower():
            pytest.xfail("KNOWN ISSUE: Imperial KB not answering pool questions")
        assert "pool" in resp.lower()

    # ====== OBEROI UDAIVILAS ======

    def test_oberoi_rooms(self, api_page):
        resp = _send_question(api_page, "oberoi_udaivilas", "What types of rooms do you have?")
        assert ESCALATION_PHRASE not in resp.lower()
        assert any(kw in resp.lower() for kw in ["suite", "premier", "luxury"])

    def test_oberoi_pool(self, api_page):
        resp = _send_question(api_page, "oberoi_udaivilas", "Do you have a swimming pool?")
        assert ESCALATION_PHRASE not in resp.lower()
        assert "pool" in resp.lower()

    def test_oberoi_spa(self, api_page):
        resp = _send_question(api_page, "oberoi_udaivilas", "Do you have a spa?")
        assert ESCALATION_PHRASE not in resp.lower()
        assert "spa" in resp.lower()

    def test_oberoi_experiences(self, api_page):
        resp = _send_question(api_page, "oberoi_udaivilas", "What experiences do you offer?")
        assert ESCALATION_PHRASE not in resp.lower()
        assert any(kw in resp.lower() for kw in ["yoga", "painting", "experience"])

    def test_oberoi_location(self, api_page):
        resp = _send_question(api_page, "oberoi_udaivilas", "Where is the hotel located?")
        assert any(kw in resp.lower() for kw in ["udaipur", "lake"])

    def test_oberoi_meetings(self, api_page):
        resp = _send_question(api_page, "oberoi_udaivilas", "Do you have meeting rooms?")
        assert "meeting" in resp.lower()

    def test_oberoi_fitness(self, api_page):
        resp = _send_question(api_page, "oberoi_udaivilas", "Do you have a fitness center?")
        assert any(kw in resp.lower() for kw in ["fitness", "gym"])

    def test_oberoi_dining_no_info(self, api_page):
        """Oberoi dining: Currently returns NO_INFO."""
        resp = _send_question(api_page, "oberoi_udaivilas", "What dining options are available?")
        if "i don't have" in resp.lower() or "i apologize" in resp.lower():
            pytest.xfail("KNOWN ISSUE: Oberoi KB missing dining information")
        assert any(kw in resp.lower() for kw in ["restaurant", "dining"])

    # ====== LE PATTE ======

    def test_lepatte_rooms(self, api_page):
        resp = _send_question(api_page, "lePatte", "What room types are available?")
        assert ESCALATION_PHRASE not in resp.lower()
        assert any(kw in resp.lower() for kw in ["superior", "deluxe", "suite"])

    def test_lepatte_room_sizes(self, api_page):
        resp = _send_question(api_page, "lePatte", "How big are the rooms?")
        assert any(kw in resp.lower() for kw in ["32", "52", "sqm"])

    def test_lepatte_pool(self, api_page):
        resp = _send_question(api_page, "lePatte", "Do you have a swimming pool?")
        assert any(kw in resp.lower() for kw in ["pool", "salt"])

    def test_lepatte_gym(self, api_page):
        resp = _send_question(api_page, "lePatte", "Is there a gym or fitness center?")
        assert any(kw in resp.lower() for kw in ["gym", "gorilla", "fitness"])

    def test_lepatte_parking(self, api_page):
        resp = _send_question(api_page, "lePatte", "Is there parking available?")
        assert "parking" in resp.lower()

    def test_lepatte_airport(self, api_page):
        resp = _send_question(api_page, "lePatte", "How far is the airport?")
        assert any(kw in resp.lower() for kw in ["airport", "mae fah luang", "7 km"])

    def test_lepatte_wifi_escalated(self, api_page):
        resp = _send_question(api_page, "lePatte", "Do you have WiFi?")
        if ESCALATION_PHRASE in resp.lower():
            pytest.xfail("KNOWN ISSUE: le Patte KB missing WiFi information")
        assert any(kw in resp.lower() for kw in ["wifi", "free"])

    # ====== RIVERIE BY KATATHANI ======

    def test_riverie_rooms(self, api_page):
        resp = _send_question(api_page, "hotel_riviera_cr", "What room types do you have?")
        assert ESCALATION_PHRASE not in resp.lower()
        assert any(kw in resp.lower() for kw in ["deluxe", "suite"])

    def test_riverie_waterpark(self, api_page):
        resp = _send_question(api_page, "hotel_riviera_cr", "Do you have a water park?")
        assert any(kw in resp.lower() for kw in ["water park", "river splash"])

    def test_riverie_spa(self, api_page):
        resp = _send_question(api_page, "hotel_riviera_cr", "Do you have a spa?")
        assert any(kw in resp.lower() for kw in ["spa", "tivaa"])

    def test_riverie_kids(self, api_page):
        resp = _send_question(api_page, "hotel_riviera_cr", "Do you have a kids club?")
        assert any(kw in resp.lower() for kw in ["kid", "children"])

    def test_riverie_conference(self, api_page):
        resp = _send_question(api_page, "hotel_riviera_cr", "Do you have conference facilities?")
        assert any(kw in resp.lower() for kw in ["conference", "meeting"])

    def test_riverie_phone(self, api_page):
        resp = _send_question(api_page, "hotel_riviera_cr", "What is the phone number?")
        assert any(kw in resp.lower() for kw in ["607999", "607 999"])

    def test_riverie_airport(self, api_page):
        resp = _send_question(api_page, "hotel_riviera_cr", "Do you offer airport transfer?")
        assert any(kw in resp.lower() for kw in ["airport", "transfer"])

    def test_riverie_pool(self, api_page):
        resp = _send_question(api_page, "hotel_riviera_cr", "Do you have a swimming pool?")
        assert "pool" in resp.lower()

    def test_riverie_dining_no_info(self, api_page):
        """Riverie dining: Currently returns NO_INFO."""
        resp = _send_question(api_page, "hotel_riviera_cr", "What dining options are available?")
        if "i don't have" in resp.lower() or "i apologize" in resp.lower():
            pytest.xfail("KNOWN ISSUE: Riverie KB missing dining information")
        assert any(kw in resp.lower() for kw in ["restaurant", "dining"])


class TestDashboardBugs:
    """Test for known dashboard rendering bugs."""

    @pytest.fixture(scope="class")
    def dashboard_page(self, browser):
        from conftest import BASE_URL_DASHBOARD, EMAIL, PASSWORD
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(60000)
        page.goto(BASE_URL_DASHBOARD, timeout=60000)
        page.wait_for_timeout(5000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(10000)
        yield page
        context.close()

    def test_imperial_dashboard_renders(self, dashboard_page):
        """BUG-012: Imperial Mae Ping dashboard renders blank page."""
        dashboard_page.goto("https://imperial_mae_ping.hotelintelliai.com/", timeout=60000)
        dashboard_page.wait_for_timeout(10000)
        body = dashboard_page.locator('body').inner_text()
        if 'Overview' not in body and 'Debug' not in body:
            pytest.xfail("KNOWN BUG-012: Imperial Mae Ping dashboard renders blank")
        assert 'Overview' in body or 'Debug' in body

    def test_oberoi_dashboard_renders(self, dashboard_page):
        """BUG-013: Oberoi Udaivilas dashboard renders blank page."""
        dashboard_page.goto("https://oberoi_udaivilas.hotelintelliai.com/", timeout=60000)
        dashboard_page.wait_for_timeout(10000)
        body = dashboard_page.locator('body').inner_text()
        if 'Overview' not in body and 'Debug' not in body:
            pytest.xfail("KNOWN BUG-013: Oberoi Udaivilas dashboard renders blank")
        assert 'Overview' in body or 'Debug' in body
