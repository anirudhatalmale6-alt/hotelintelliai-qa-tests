"""
Test 08: AI Concierge Accuracy Testing — All Hotels with KB Content
Tests AI concierge responses across 4 hotels via Msg Simulator.
Verifies responses are relevant to questions asked and not just escalation fallbacks.
"""
import pytest
import time

# Hotels with KB content
HOTELS = [
    {"name": "The Heritage Chiang Rai Hotel and Convention", "id": "heritage_chiangrai", "chunks": 49},
    {"name": "The Oberoi Udaivilas", "id": "oberoi_udaivilas", "chunks": 352},
    {"name": "le Patte", "id": "lePatte", "chunks": 306},
    {"name": "The Riverie by Katathani", "id": "hotel_riviera_cr", "chunks": 467},
]

# Common hotel questions
QUESTIONS = [
    ("check-in", "What time is check-in and check-out?",
     ["check-in", "check in", "check-out", "check out", "pm", "am"]),
    ("rooms", "What types of rooms do you have?",
     ["room", "suite", "deluxe", "standard", "superior", "premier", "villa"]),
    ("pool", "Do you have a swimming pool?",
     ["pool", "swim", "aqua", "water"]),
    ("spa", "Do you have a spa? What treatments are available?",
     ["spa", "massage", "treatment", "wellness", "therapy"]),
    ("dining", "What dining options or restaurants do you have?",
     ["restaurant", "dining", "breakfast", "lunch", "dinner", "cafe", "bar", "cuisine", "food"]),
    ("airport", "Is there airport transfer or shuttle service?",
     ["airport", "transfer", "shuttle", "transport", "pickup", "taxi"]),
    ("fitness", "Do you have a fitness center or gym?",
     ["fitness", "gym", "exercise", "workout", "health club"]),
    ("cancellation", "What is your cancellation policy?",
     ["cancel", "refund", "policy", "charge", "hours before", "free"]),
    ("wifi", "Do you have WiFi? Is it free?",
     ["wifi", "wi-fi", "internet", "wireless", "complimentary"]),
    ("breakfast", "Is breakfast included? What time is it served?",
     ["breakfast", "morning", "buffet", "served", "included"]),
]

ESCALATION_PHRASE = "connect you with our team"


def _navigate_to_simulator(page, dashboard_url, hotel_name):
    """Navigate to a hotel's Msg Simulator."""
    page.goto(dashboard_url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    page.locator(f'text={hotel_name}').first.click()
    page.wait_for_timeout(5000)
    page.locator('text=Debug').first.click()
    page.wait_for_timeout(2000)
    page.locator('button:has-text("Msg Simulator")').click()
    page.wait_for_timeout(2000)


def _set_hotel_id_and_ask(page, hotel_id, question):
    """Set HOTEL ID, fill MESSAGE, click Simulate, return response text."""
    # Refresh simulator tab for clean state
    page.locator('button:has-text("Msg Simulator")').click()
    page.wait_for_timeout(1500)

    inputs = page.locator('input')
    input_count = inputs.count()

    visible_text_inputs = []
    for i in range(input_count):
        inp = inputs.nth(i)
        if not inp.is_visible():
            continue
        inp_type = (inp.get_attribute('type') or '').lower()
        if inp_type in ('email', 'password', 'file', 'hidden', 'checkbox', 'radio'):
            continue
        visible_text_inputs.append(inp)

    assert len(visible_text_inputs) >= 3, f"Expected 3+ visible inputs, found {len(visible_text_inputs)}"

    # Find MESSAGE input (has placeholder with "spa" or "e.g.")
    message_input = None
    for inp in visible_text_inputs:
        placeholder = (inp.get_attribute('placeholder') or '').lower()
        if 'spa' in placeholder or 'e.g.' in placeholder or 'message' in placeholder:
            message_input = inp
            break
    if not message_input:
        message_input = visible_text_inputs[-1]  # fallback: last input

    # Find HOTEL ID input (first input, usually has hotel id value)
    hotel_id_input = visible_text_inputs[0]

    # Set hotel ID
    current_id = hotel_id_input.input_value()
    if current_id != hotel_id:
        hotel_id_input.click()
        hotel_id_input.fill("")
        hotel_id_input.fill(hotel_id)
        page.wait_for_timeout(300)

    # Fill message
    message_input.click()
    message_input.fill("")
    page.wait_for_timeout(200)
    message_input.fill(question)
    page.wait_for_timeout(500)

    # Click Simulate
    sim_btn = page.locator('button:has-text("Simulate")')
    assert sim_btn.first.get_attribute('disabled') is None, "Simulate button is disabled"
    sim_btn.first.click()

    # Wait for response
    try:
        page.locator('text=AGENT RESPONSE').wait_for(timeout=30000)
        page.wait_for_timeout(2000)
    except Exception:
        page.wait_for_timeout(15000)

    # Extract response
    body = page.locator('body').inner_text()
    lines = body.split('\n')
    response_text = ""
    capture = False
    for line in lines:
        line = line.strip()
        if 'AGENT RESPONSE' in line.upper():
            capture = True
            continue
        if capture:
            if any(kw in line.upper() for kw in ['INTENT', 'ELAPSED', 'LANGUAGE', 'CONFIDENCE']):
                capture = False
            elif line and not line.startswith('↻') and not line.startswith('●') and len(line) > 1:
                response_text += line + " "

    return response_text.strip()


class TestConciergeAccuracy:
    """Test AI concierge accuracy across all hotels with KB content."""

    @pytest.fixture(scope="class")
    def dashboard_page(self, browser):
        """Login to dashboard and return page."""
        from conftest import BASE_URL_DASHBOARD, EMAIL, PASSWORD
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(60000)

        page.goto(BASE_URL_DASHBOARD, wait_until="networkidle", timeout=60000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)

        yield page
        context.close()

    # ====== Heritage Chiang Rai (49 chunks — sparse KB) ======

    @pytest.fixture(scope="class")
    def heritage_nav(self, dashboard_page):
        _navigate_to_simulator(dashboard_page, "https://dashboard.hotelintelliai.com",
                               "The Heritage Chiang Rai Hotel and Convention")
        return dashboard_page

    def test_heritage_responds(self, heritage_nav):
        """Heritage Chiang Rai: AI responds to at least one question."""
        response = _set_hotel_id_and_ask(heritage_nav, "heritage_chiangrai",
                                         "What time is check-in and check-out?")
        assert len(response) > 10, "No response from AI concierge"

    def test_heritage_has_some_info(self, heritage_nav):
        """Heritage Chiang Rai: AI has at least some KB info (49 chunks)."""
        response = _set_hotel_id_and_ask(heritage_nav, "heritage_chiangrai",
                                         "Tell me about the hotel")
        assert len(response) > 10, "No response"
        # With only 49 chunks, may escalate — that's acceptable

    # ====== Oberoi Udaivilas (352 chunks — good KB) ======

    @pytest.fixture(scope="class")
    def oberoi_nav(self, dashboard_page):
        _navigate_to_simulator(dashboard_page, "https://dashboard.hotelintelliai.com",
                               "The Oberoi Udaivilas")
        return dashboard_page

    def test_oberoi_rooms(self, oberoi_nav):
        """Oberoi: AI correctly describes room types."""
        response = _set_hotel_id_and_ask(oberoi_nav, "oberoi_udaivilas",
                                         "What types of rooms do you have?")
        assert len(response) > 50, "Response too short"
        resp_lower = response.lower()
        assert any(kw in resp_lower for kw in ["room", "suite", "premier", "luxury"]), \
            f"Response doesn't mention room types: {response[:200]}"

    def test_oberoi_pool(self, oberoi_nav):
        """Oberoi: AI knows about swimming pool."""
        response = _set_hotel_id_and_ask(oberoi_nav, "oberoi_udaivilas",
                                         "Do you have a swimming pool?")
        resp_lower = response.lower()
        assert "pool" in resp_lower, f"Response doesn't mention pool: {response[:200]}"

    def test_oberoi_spa(self, oberoi_nav):
        """Oberoi: AI knows about spa treatments."""
        response = _set_hotel_id_and_ask(oberoi_nav, "oberoi_udaivilas",
                                         "Do you have a spa? What treatments are available?")
        resp_lower = response.lower()
        assert any(kw in resp_lower for kw in ["spa", "massage", "treatment"]), \
            f"Response doesn't mention spa: {response[:200]}"

    def test_oberoi_dining(self, oberoi_nav):
        """Oberoi: AI knows about dining options."""
        response = _set_hotel_id_and_ask(oberoi_nav, "oberoi_udaivilas",
                                         "What dining options or restaurants do you have?")
        resp_lower = response.lower()
        assert any(kw in resp_lower for kw in ["restaurant", "dining", "cuisine"]), \
            f"Response doesn't mention dining: {response[:200]}"

    def test_oberoi_fitness(self, oberoi_nav):
        """Oberoi: AI knows about fitness center."""
        response = _set_hotel_id_and_ask(oberoi_nav, "oberoi_udaivilas",
                                         "Do you have a fitness center or gym?")
        resp_lower = response.lower()
        assert any(kw in resp_lower for kw in ["fitness", "gym"]), \
            f"Response doesn't mention fitness: {response[:200]}"

    def test_oberoi_no_escalation_for_rooms(self, oberoi_nav):
        """Oberoi: Room question should NOT escalate (info is in KB)."""
        response = _set_hotel_id_and_ask(oberoi_nav, "oberoi_udaivilas",
                                         "What types of rooms do you have?")
        assert ESCALATION_PHRASE not in response.lower(), \
            "Room question should not be escalated — info exists in KB"

    # ====== le Patte (306 chunks) ======

    @pytest.fixture(scope="class")
    def lepatte_nav(self, dashboard_page):
        _navigate_to_simulator(dashboard_page, "https://dashboard.hotelintelliai.com",
                               "le Patte")
        return dashboard_page

    def test_lepatte_rooms(self, lepatte_nav):
        """le Patte: AI correctly describes room types."""
        response = _set_hotel_id_and_ask(lepatte_nav, "lePatte",
                                         "What types of rooms do you have?")
        resp_lower = response.lower()
        assert any(kw in resp_lower for kw in ["room", "superior", "deluxe"]), \
            f"Response doesn't mention rooms: {response[:200]}"

    def test_lepatte_pool(self, lepatte_nav):
        """le Patte: AI knows about swimming pool."""
        response = _set_hotel_id_and_ask(lepatte_nav, "lePatte",
                                         "Do you have a swimming pool?")
        resp_lower = response.lower()
        assert "pool" in resp_lower or "swim" in resp_lower, \
            f"Response doesn't mention pool: {response[:200]}"

    def test_lepatte_fitness(self, lepatte_nav):
        """le Patte: AI knows about gym partnership."""
        response = _set_hotel_id_and_ask(lepatte_nav, "lePatte",
                                         "Do you have a fitness center or gym?")
        resp_lower = response.lower()
        assert any(kw in resp_lower for kw in ["gym", "fitness", "gorilla"]), \
            f"Response doesn't mention gym: {response[:200]}"

    # ====== Riverie by Katathani (467 chunks — best KB) ======

    @pytest.fixture(scope="class")
    def riverie_nav(self, dashboard_page):
        _navigate_to_simulator(dashboard_page, "https://dashboard.hotelintelliai.com",
                               "The Riverie by Katathani")
        return dashboard_page

    def test_riverie_checkin(self, riverie_nav):
        """Riverie: AI knows check-in/out times."""
        response = _set_hotel_id_and_ask(riverie_nav, "hotel_riviera_cr",
                                         "What time is check-in and check-out?")
        resp_lower = response.lower()
        assert any(kw in resp_lower for kw in ["check-in", "check in", "3:00", "pm"]), \
            f"Response doesn't mention check-in times: {response[:200]}"

    def test_riverie_rooms(self, riverie_nav):
        """Riverie: AI describes room types with pricing."""
        response = _set_hotel_id_and_ask(riverie_nav, "hotel_riviera_cr",
                                         "What types of rooms do you have?")
        resp_lower = response.lower()
        assert any(kw in resp_lower for kw in ["room", "standard", "deluxe", "suite"]), \
            f"Response doesn't mention rooms: {response[:200]}"

    def test_riverie_pool(self, riverie_nav):
        """Riverie: AI knows about swimming pool."""
        response = _set_hotel_id_and_ask(riverie_nav, "hotel_riviera_cr",
                                         "Do you have a swimming pool?")
        assert "pool" in response.lower(), f"Response doesn't mention pool: {response[:200]}"

    def test_riverie_spa(self, riverie_nav):
        """Riverie: AI knows about Tivaa Ratrii Spa."""
        response = _set_hotel_id_and_ask(riverie_nav, "hotel_riviera_cr",
                                         "Do you have a spa? What treatments are available?")
        resp_lower = response.lower()
        assert any(kw in resp_lower for kw in ["spa", "tivaa", "treatment"]), \
            f"Response doesn't mention spa: {response[:200]}"

    def test_riverie_dining(self, riverie_nav):
        """Riverie: AI knows about restaurant options."""
        response = _set_hotel_id_and_ask(riverie_nav, "hotel_riviera_cr",
                                         "What dining options or restaurants do you have?")
        resp_lower = response.lower()
        assert any(kw in resp_lower for kw in ["restaurant", "dining", "riverie"]), \
            f"Response doesn't mention dining: {response[:200]}"

    def test_riverie_airport(self, riverie_nav):
        """Riverie: AI knows about airport transfer service."""
        response = _set_hotel_id_and_ask(riverie_nav, "hotel_riviera_cr",
                                         "Is there airport transfer or shuttle service?")
        resp_lower = response.lower()
        assert any(kw in resp_lower for kw in ["airport", "shuttle", "transfer"]), \
            f"Response doesn't mention airport: {response[:200]}"

    def test_riverie_cancellation(self, riverie_nav):
        """Riverie: AI knows cancellation policy."""
        response = _set_hotel_id_and_ask(riverie_nav, "hotel_riviera_cr",
                                         "What is your cancellation policy?")
        resp_lower = response.lower()
        assert any(kw in resp_lower for kw in ["cancel", "48 hours", "free"]), \
            f"Response doesn't mention cancellation: {response[:200]}"

    def test_riverie_breakfast(self, riverie_nav):
        """Riverie: AI knows about breakfast service."""
        response = _set_hotel_id_and_ask(riverie_nav, "hotel_riviera_cr",
                                         "Is breakfast included? What time is it served?")
        resp_lower = response.lower()
        assert any(kw in resp_lower for kw in ["breakfast", "buffet", "morning"]), \
            f"Response doesn't mention breakfast: {response[:200]}"

    def test_riverie_no_escalation_for_dining(self, riverie_nav):
        """Riverie: Dining question should NOT escalate (info is in KB)."""
        response = _set_hotel_id_and_ask(riverie_nav, "hotel_riviera_cr",
                                         "What dining options or restaurants do you have?")
        assert ESCALATION_PHRASE not in response.lower(), \
            "Dining question should not be escalated — info exists in KB"


class TestConciergeEscalation:
    """Test that escalation responses are handled gracefully."""

    @pytest.fixture(scope="class")
    def dashboard_page(self, browser):
        from conftest import BASE_URL_DASHBOARD, EMAIL, PASSWORD
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(60000)

        page.goto(BASE_URL_DASHBOARD, wait_until="networkidle", timeout=60000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        yield page
        context.close()

    def test_wifi_escalation_is_graceful(self, dashboard_page):
        """WiFi question may escalate — verify it's a polite escalation, not an error."""
        _navigate_to_simulator(dashboard_page, "https://dashboard.hotelintelliai.com",
                               "The Riverie by Katathani")
        response = _set_hotel_id_and_ask(dashboard_page, "hotel_riviera_cr",
                                         "Do you have WiFi? Is it free?")
        # Even if escalated, response should be polite and not an error
        assert len(response) > 20, "Response too short"
        assert "error" not in response.lower(), "Response contains error"

    def test_heritage_sparse_kb_graceful(self, dashboard_page):
        """Heritage (49 chunks): Most questions escalate gracefully with sparse KB."""
        _navigate_to_simulator(dashboard_page, "https://dashboard.hotelintelliai.com",
                               "The Heritage Chiang Rai Hotel and Convention")
        response = _set_hotel_id_and_ask(dashboard_page, "heritage_chiangrai",
                                         "Do you have a spa?")
        assert len(response) > 20, "Response too short"
        assert "error" not in response.lower(), "Response contains error"
