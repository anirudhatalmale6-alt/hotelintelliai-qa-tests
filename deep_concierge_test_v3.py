"""
Deep AI Concierge Testing v3 — All Hotels with website-specific questions.
Fixed: Properly targets MESSAGE input by placeholder, clears between questions,
verifies HOTEL ID matches, and waits for fresh responses.
"""
import os
import json
import time
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# All 6 hotels in the system
HOTELS = [
    {
        "name": "The Heritage Chiang Rai Hotel and Convention",
        "short_name": "Heritage",
        "id": "heritage_chiangrai",
        "website": "heritagechiangrai.com",
        "questions": [
            ("How many rooms does the hotel have?", ["321"]),
            ("What room types are available?", ["deluxe", "executive", "suite", "premier"]),
            ("Do you have meeting or convention facilities?", ["ballroom", "meeting", "1500", "2000"]),
            ("What restaurants do you have?", ["all-day", "library", "lounge"]),
            ("Do you have a swimming pool?", ["pool", "outdoor"]),
            ("Where is the hotel located?", ["paholyothin", "chiang rai", "sansai"]),
            ("Do you have a fitness center?", ["fitness", "gym"]),
            ("What is the phone number?", ["5205 5888", "52055888"]),
            ("Is there a spa?", ["spa"]),
            ("What are nearby attractions?", ["white temple", "night bazaar", "blue temple", "clock tower"]),
        ]
    },
    {
        "name": "The Oberoi Udaivilas",
        "short_name": "Oberoi",
        "id": "oberoi_udaivilas",
        "website": "oberoihotels.com",
        "questions": [
            ("What types of rooms do you have?", ["kohinoor", "luxury suite", "premier"]),
            ("Do you have a swimming pool?", ["pool", "temperature-controlled", "mughal"]),
            ("What dining options are available?", ["suryamahal", "chandni", "mewar", "vineet", "bar", "promenade"]),
            ("Do you have a spa?", ["spa", "asmi", "oberoi"]),
            ("What experiences do you offer?", ["yoga", "painting", "cook", "dinner"]),
            ("Where is the hotel located?", ["lake pichola", "udaipur"]),
            ("What is the size of the resort?", ["30 acres", "121,000"]),
            ("Do you have meeting rooms?", ["chandra mahal", "meeting", "cocktail"]),
            ("What nearby attractions can I visit?", ["city palace", "jagdish temple", "kumbhalgarh"]),
            ("Do you have a fitness center?", ["fitness", "gym", "cardiovascular"]),
        ]
    },
    {
        "name": "le Patte",
        "short_name": "le Patte",
        "id": "lePatte",
        "website": "lepattachiangrai.com",
        "questions": [
            ("What room types are available?", ["superior", "deluxe", "suite"]),
            ("How big are the rooms?", ["32", "52", "sqm"]),
            ("Do you have a swimming pool?", ["pool", "salt"]),
            ("Is there a gym or fitness center?", ["gym", "gorilla", "fitness"]),
            ("Do you have WiFi?", ["wifi", "free"]),
            ("Where is the hotel located?", ["phaholyothin", "chiang rai"]),
            ("What is nearby the hotel?", ["night bazaar", "clock tower", "walking street"]),
            ("Do you have a restaurant?", ["restaurant", "terrace"]),
            ("Is there parking available?", ["parking", "free"]),
            ("How far is the airport?", ["7 km", "airport", "mae fah luang"]),
        ]
    },
    {
        "name": "The Riverie by Katathani",
        "short_name": "Riverie",
        "id": "hotel_riviera_cr",
        "website": "theriverie.com",
        "questions": [
            ("What room types do you have?", ["deluxe", "family suite", "riverie suite", "royal suite", "two-bedroom"]),
            ("Do you have a water park?", ["water park", "river splash"]),
            ("Do you have a spa?", ["spa", "tivaa"]),
            ("What dining options are available?", ["restaurant", "red lanna", "cuisine"]),
            ("Do you have a kids club?", ["kid", "children"]),
            ("How many rooms does the hotel have?", ["271"]),
            ("Do you have conference facilities?", ["conference", "banquet", "700"]),
            ("Where is the hotel located?", ["kraisorasit", "kok river", "chiang rai"]),
            ("What is the phone number?", ["607999", "53 607"]),
            ("Do you offer airport transfer?", ["airport", "transfer"]),
        ]
    },
    {
        "name": "Grand Vista Chiangrai Hotel",
        "short_name": "Grand Vista",
        "id": "grand_vista_chiangrai",
        "website": "grandvistachiangrai.com",
        "questions": [
            ("How many rooms does the hotel have?", ["80"]),
            ("Do you have a swimming pool?", ["pool", "salt"]),
            ("Do you have a spa?", ["spa", "massage", "body scrub"]),
            ("What dining options are available?", ["restaurant", "vista", "lounge", "bar"]),
            ("Do you have a fitness center?", ["fitness", "gym"]),
            ("Is there WiFi?", ["wifi", "free"]),
            ("Is there parking?", ["parking", "free"]),
            ("Where is the hotel located?", ["chiang rai", "rop wiang"]),
            ("How far is the airport?", ["5 km", "airport"]),
            ("What nearby attractions are there?", ["night bazaar", "clock tower", "night market"]),
        ]
    },
    {
        "name": "Imperial Mae Ping Hotel",
        "short_name": "Imperial Mae Ping",
        "id": "imperial_mae_ping",
        "website": "chiangmai.intercontinental.com",
        "questions": [
            ("What time is check-in and check-out?", ["3:00", "12:00", "check-in", "check-out"]),
            ("What restaurants do you have?", ["hong", "chinese", "kam", "gad lanna", "belen"]),
            ("Do you have a spa?", ["spa", "ii spa", "massage", "lanna"]),
            ("Do you have a swimming pool?", ["pool"]),
            ("Is there a fitness center?", ["fitness", "24-hour", "gym"]),
            ("Where is the hotel located?", ["sridonchai", "chiang mai", "chang khlan"]),
            ("Do you have parking?", ["parking", "valet", "electric vehicle"]),
            ("What is the phone number?", ["52 090 998"]),
            ("Do you have a kids club?", ["kid", "planet trekkers"]),
            ("Do you offer limousine service?", ["limousine", "transportation"]),
        ]
    },
]


def screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    page.screenshot(path=path)
    return path


def login(page):
    """Login to the dashboard."""
    page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)

    # Check if already logged in
    body = page.locator('body').inner_text()
    if 'sign in' in body.lower() or 'log in' in body.lower() or 'password' in body.lower():
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        print("Logged in to dashboard")
    else:
        print("Already logged in")

    # Wait for hotels to load (they load asynchronously)
    for _ in range(10):
        body = page.locator('body').inner_text()
        if 'loading' in body.lower():
            page.wait_for_timeout(2000)
        else:
            break
    page.wait_for_timeout(2000)


def navigate_to_hotel_simulator(page, hotel):
    """Navigate to a specific hotel's Msg Simulator."""
    hname = hotel["name"]
    short = hotel["short_name"]
    hid = hotel["id"]

    # Go to dashboard
    page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)

    # Wait for hotels to load (they load asynchronously)
    for _ in range(10):
        body = page.locator('body').inner_text()
        if 'loading' in body.lower() and 'hotel' not in body.lower().split('loading')[0][-50:]:
            page.wait_for_timeout(2000)
        elif hid not in body and short.lower() not in body.lower():
            page.wait_for_timeout(2000)
        else:
            break
    page.wait_for_timeout(2000)

    # Take a screenshot to debug
    screenshot(page, f"v3_nav_{short.replace(' ','_')}_dashboard")

    # Try multiple strategies to click the hotel card
    clicked = False

    # Strategy 1: Click by hotel_id text (shown as subtitle)
    try:
        el = page.locator(f'text={hid}').first
        if el.count() > 0:
            el.click()
            page.wait_for_timeout(5000)
            clicked = True
    except Exception:
        pass

    # Strategy 2: Click by short name
    if not clicked:
        try:
            el = page.locator(f'text={short}').first
            if el.count() > 0:
                el.click()
                page.wait_for_timeout(5000)
                clicked = True
        except Exception:
            pass

    # Strategy 3: Click by full name
    if not clicked:
        try:
            el = page.locator(f'text={hname}').first
            if el.count() > 0:
                el.click()
                page.wait_for_timeout(5000)
                clicked = True
        except Exception:
            pass

    # Strategy 4: Find clickable element containing hotel name
    if not clicked:
        try:
            # Look for any element with the hotel name and click its parent card
            el = page.locator(f'div:has-text("{short}")').first
            if el.count() > 0:
                el.click()
                page.wait_for_timeout(5000)
                clicked = True
        except Exception:
            pass

    # Strategy 5: Try clicking the arrow button next to the hotel
    if not clicked:
        try:
            # Find all arrow links/buttons
            arrows = page.locator('a[href*="hotel"], button >> text=→, a >> text=→')
            body = page.locator('body').inner_text()
            print(f"    DEBUG: Dashboard body preview: {body[:300]}")
        except Exception:
            pass

    if not clicked:
        raise Exception(f"Could not find hotel: {hname} / {short} / {hid}")

    # Navigate to Debug
    page.locator('text=Debug').first.click()
    page.wait_for_timeout(2000)

    # Click Msg Simulator tab
    page.locator('button:has-text("Msg Simulator")').click()
    page.wait_for_timeout(2000)

    return True


def get_message_input(page):
    """Find the MESSAGE input specifically (the one with placeholder about spa/message)."""
    # Strategy 1: Find by placeholder containing "e.g." or "spa" or "message"
    inputs = page.locator('input')
    count = inputs.count()

    for i in range(count):
        inp = inputs.nth(i)
        if not inp.is_visible():
            continue
        placeholder = (inp.get_attribute('placeholder') or '').lower()
        if any(kw in placeholder for kw in ['e.g.', 'spa', 'message', 'type your', 'ask', 'query']):
            return inp

    # Strategy 2: Find by label "MESSAGE"
    labels = page.locator('label, div, span')
    for i in range(labels.count()):
        lbl = labels.nth(i)
        try:
            if lbl.is_visible() and 'MESSAGE' in (lbl.inner_text() or '').upper():
                # Look for the next sibling input
                parent = lbl.locator('..').first
                inp = parent.locator('input').first
                if inp.count() > 0 and inp.is_visible():
                    return inp
        except Exception:
            continue

    # Strategy 3: The 3rd visible text input (after Hotel ID and Guest Identifier)
    visible_inputs = []
    for i in range(count):
        inp = inputs.nth(i)
        if not inp.is_visible():
            continue
        inp_type = (inp.get_attribute('type') or '').lower()
        if inp_type in ('email', 'password', 'file', 'hidden', 'checkbox', 'radio', 'number'):
            continue
        visible_inputs.append(inp)

    if len(visible_inputs) >= 3:
        return visible_inputs[2]  # Third input = MESSAGE

    return None


def set_hotel_id(page, hotel_id):
    """Set the HOTEL ID field to the correct hotel ID."""
    inputs = page.locator('input')
    count = inputs.count()

    for i in range(count):
        inp = inputs.nth(i)
        if not inp.is_visible():
            continue
        value = inp.input_value() or ''
        placeholder = (inp.get_attribute('placeholder') or '').lower()

        # The Hotel ID field typically has a hotel ID value or "hotel" placeholder
        if 'hotel' in value.lower() or 'hotel' in placeholder:
            if value.lower() != hotel_id.lower():
                inp.click(click_count=3)
                inp.fill(hotel_id)
                page.wait_for_timeout(500)
                print(f"    Updated HOTEL ID from '{value}' to '{hotel_id}'")
            return True

    # Strategy 2: First visible text input is usually HOTEL ID
    visible_inputs = []
    for i in range(count):
        inp = inputs.nth(i)
        if not inp.is_visible():
            continue
        inp_type = (inp.get_attribute('type') or '').lower()
        if inp_type in ('email', 'password', 'file', 'hidden', 'checkbox', 'radio', 'number'):
            continue
        visible_inputs.append(inp)

    if visible_inputs:
        first_input = visible_inputs[0]
        old_val = first_input.input_value() or ''
        first_input.click(click_count=3)
        first_input.fill(hotel_id)
        page.wait_for_timeout(500)
        print(f"    Set first input (HOTEL ID) from '{old_val}' to '{hotel_id}'")
        return True

    return False


def send_question(page, question, hotel_id, q_index):
    """Fill question into MESSAGE input, click Simulate, wait for response."""
    # First ensure HOTEL ID is correct
    set_hotel_id(page, hotel_id)

    # Find the MESSAGE input
    msg_input = get_message_input(page)
    if not msg_input:
        print(f"    ERROR: Could not find MESSAGE input")
        return None

    # Clear and fill the message
    msg_input.click(click_count=3)
    page.wait_for_timeout(200)
    msg_input.fill("")
    page.wait_for_timeout(200)
    msg_input.fill(question)
    page.wait_for_timeout(500)

    # Verify the input has our question
    actual_value = msg_input.input_value()
    if actual_value != question:
        print(f"    WARNING: Input value mismatch. Expected: '{question}', Got: '{actual_value}'")
        msg_input.fill("")
        page.wait_for_timeout(200)
        msg_input.type(question, delay=20)
        page.wait_for_timeout(500)

    # Get any existing response text before clicking (to compare after)
    body_before = page.locator('body').inner_text()

    # Click Simulate button
    sim_btn = page.locator('button:has-text("Simulate")')
    if sim_btn.count() == 0:
        print(f"    ERROR: Simulate button not found")
        return None

    # Check if button is enabled
    is_disabled = sim_btn.first.get_attribute('disabled')
    if is_disabled is not None:
        print(f"    WARNING: Simulate button is disabled")
        return None

    sim_btn.first.click()
    print(f"    Clicked Simulate, waiting for response...")

    # Wait for response - check periodically for new content
    max_wait = 30  # seconds
    waited = 0
    response_found = False

    while waited < max_wait:
        page.wait_for_timeout(3000)
        waited += 3
        body_after = page.locator('body').inner_text()

        # Check if response appeared (body changed and contains AGENT RESPONSE)
        if 'AGENT RESPONSE' in body_after.upper() and body_after != body_before:
            response_found = True
            break
        elif 'AGENT RESPONSE' in body_after.upper():
            # Response section exists, check if it has new content
            response_found = True
            break

    if not response_found:
        # Take screenshot and check what's on screen
        page.wait_for_timeout(10000)  # Extra wait
        body_after = page.locator('body').inner_text()
        if 'AGENT RESPONSE' in body_after.upper():
            response_found = True

    return page.locator('body').inner_text()


def extract_response(body):
    """Extract AI response from page body text."""
    if not body:
        return "", "", ""

    lines = body.split('\n')
    response_text = ""
    intent = ""
    elapsed = ""

    # Find AGENT RESPONSE section
    capture = False
    for line in lines:
        stripped = line.strip()
        upper = stripped.upper()

        if 'AGENT RESPONSE' in upper:
            capture = True
            continue

        if capture:
            # Stop at next section headers
            if any(kw in upper for kw in ['INTENT:', 'ELAPSED', 'LANGUAGE:', 'CONFIDENCE:', 'HOTEL ID', 'GUEST IDENTIFIER']):
                capture = False
                if 'INTENT' in upper and ':' in stripped:
                    intent = stripped.split(':', 1)[1].strip()
                elif 'ELAPSED' in upper:
                    elapsed = stripped
                continue

            # Skip UI elements
            if stripped.startswith('↻') or stripped.startswith('●') or stripped.startswith('►'):
                continue
            if stripped in ('Simulate', 'MESSAGE', 'HOTEL ID', 'GUEST IDENTIFIER'):
                continue
            if len(stripped) <= 1:
                continue

            response_text += stripped + " "

    # Get intent/elapsed if missed
    if not intent or not elapsed:
        for line in lines:
            stripped = line.strip()
            if not intent and 'INTENT' in stripped.upper() and ':' in stripped:
                intent = stripped.split(':', 1)[1].strip()
            if not elapsed and 'ELAPSED' in stripped.upper():
                elapsed = stripped

    return response_text.strip(), intent, elapsed


def evaluate_accuracy(response, expected_keywords):
    """Check if the response contains expected keywords from website content."""
    if not response or len(response) < 10:
        return "NO_RESPONSE", 0, []

    response_lower = response.lower()

    # Check for "don't know" type responses
    no_info_phrases = [
        "i don't have", "i don't know", "i'm not sure",
        "i cannot find", "not available", "no information",
        "i apologize", "sorry, i don't", "unfortunately",
        "i don't have specific",
    ]
    for phrase in no_info_phrases:
        if phrase in response_lower:
            return "NO_INFO", 0, []

    # Check for errors
    if 'error' in response_lower and len(response) < 50:
        return "ERROR", 0, []

    # Check keyword matches
    matched = []
    for kw in expected_keywords:
        if kw.lower() in response_lower:
            matched.append(kw)

    match_pct = len(matched) / len(expected_keywords) * 100 if expected_keywords else 0

    if match_pct >= 50:
        return "ACCURATE", match_pct, matched
    elif match_pct > 0:
        return "PARTIAL", match_pct, matched
    else:
        # Response exists but no keyword matches - could still be relevant
        if len(response) > 50:
            return "UNVERIFIED", 0, matched
        return "WEAK", 0, matched


def main():
    all_results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(30000)

        # Login
        login(page)
        screenshot(page, "v3_dashboard")

        for hotel in HOTELS:
            hid = hotel["id"]
            hname = hotel["name"]
            short = hotel["short_name"]

            print(f"\n{'='*70}")
            print(f"TESTING: {hname} (ID: {hid})")
            print(f"Website: {hotel['website']}")
            print(f"{'='*70}")

            hotel_results = {
                "name": hname,
                "id": hid,
                "website": hotel["website"],
                "questions": [],
                "summary": {}
            }

            # Navigate to hotel's simulator
            try:
                navigate_to_hotel_simulator(page, hotel)
                screenshot(page, f"v3_{short.replace(' ','_')}_sim")
            except Exception as e:
                print(f"  NAVIGATION ERROR: {e}")
                hotel_results["error"] = str(e)
                all_results[hid] = hotel_results
                continue

            # Verify we're on the right hotel by checking Hotel ID
            body = page.locator('body').inner_text()
            print(f"  Simulator loaded")

            for qi, (question, expected_kw) in enumerate(hotel["questions"]):
                print(f"\n  Q{qi+1}: {question}")
                print(f"    Expected keywords: {expected_kw}")

                # For questions after the first, reload the simulator tab
                if qi > 0:
                    try:
                        # Click Msg Simulator tab to reset
                        page.locator('button:has-text("Msg Simulator")').click()
                        page.wait_for_timeout(2000)
                    except Exception:
                        try:
                            navigate_to_hotel_simulator(page, hotel)
                        except Exception as nav_e:
                            print(f"    SKIP - navigation failed: {nav_e}")
                            hotel_results["questions"].append({
                                "q_num": qi + 1,
                                "question": question,
                                "expected_keywords": expected_kw,
                                "response": "",
                                "accuracy": "ERROR",
                                "match_pct": 0,
                                "matched_kw": [],
                                "issues": ["Navigation failed"]
                            })
                            continue

                # Send question and get response
                response_body = send_question(page, question, hid, qi)
                screenshot(page, f"v3_{short.replace(' ','_')}_q{qi+1}")

                if response_body:
                    response, intent, elapsed = extract_response(response_body)
                    accuracy, match_pct, matched_kw = evaluate_accuracy(response, expected_kw)

                    display = response[:200] + "..." if len(response) > 200 else response
                    print(f"    Response: {display}")
                    print(f"    Accuracy: {accuracy} ({match_pct:.0f}%) | Matched: {matched_kw}")
                    print(f"    Intent: {intent} | {elapsed}")
                else:
                    response = ""
                    intent = ""
                    elapsed = ""
                    accuracy = "NO_RESPONSE"
                    match_pct = 0
                    matched_kw = []
                    print(f"    NO RESPONSE received")

                hotel_results["questions"].append({
                    "q_num": qi + 1,
                    "question": question,
                    "expected_keywords": expected_kw,
                    "response": response[:500] if response else "",
                    "intent": intent,
                    "elapsed": elapsed,
                    "accuracy": accuracy,
                    "match_pct": match_pct,
                    "matched_kw": matched_kw,
                })

            # Hotel summary
            questions = hotel_results["questions"]
            total = len(questions)
            accurate = sum(1 for q in questions if q["accuracy"] == "ACCURATE")
            partial = sum(1 for q in questions if q["accuracy"] == "PARTIAL")
            no_info = sum(1 for q in questions if q["accuracy"] == "NO_INFO")
            errors = sum(1 for q in questions if q["accuracy"] in ("ERROR", "NO_RESPONSE"))
            unverified = sum(1 for q in questions if q["accuracy"] == "UNVERIFIED")

            hotel_results["summary"] = {
                "total": total,
                "accurate": accurate,
                "partial": partial,
                "no_info": no_info,
                "unverified": unverified,
                "errors": errors,
                "accuracy_pct": (accurate + partial) / total * 100 if total else 0
            }

            print(f"\n  HOTEL SUMMARY: {accurate} accurate, {partial} partial, {no_info} no-info, {errors} errors out of {total}")

            all_results[hid] = hotel_results

        context.close()
        browser.close()

    # Save results
    os.makedirs("reports", exist_ok=True)
    results_path = "reports/concierge_test_results_v3.json"
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    # Print final summary
    print("\n\n" + "=" * 70)
    print("FINAL SUMMARY — AI CONCIERGE ACCURACY BY HOTEL")
    print("=" * 70)

    grand_total = 0
    grand_accurate = 0

    for hid, data in all_results.items():
        name = data["name"]
        summary = data.get("summary", {})
        error = data.get("error")

        if error:
            print(f"\n{name}: SKIPPED ({error})")
            continue

        total = summary.get("total", 0)
        accurate = summary.get("accurate", 0)
        partial = summary.get("partial", 0)
        no_info = summary.get("no_info", 0)
        errors_count = summary.get("errors", 0)
        pct = summary.get("accuracy_pct", 0)

        grand_total += total
        grand_accurate += accurate + partial

        print(f"\n{name} ({hid})")
        print(f"  Accuracy: {pct:.0f}% ({accurate} accurate + {partial} partial = {accurate+partial}/{total})")
        print(f"  No Info: {no_info} | Errors: {errors_count}")

        # Show failed questions
        for q in data.get("questions", []):
            if q["accuracy"] not in ("ACCURATE",):
                print(f"  [{q['accuracy']}] Q{q['q_num']}: {q['question']}")
                if q.get("response"):
                    print(f"          R: {q['response'][:120]}...")

    overall_pct = grand_accurate / grand_total * 100 if grand_total else 0
    print(f"\n{'='*70}")
    print(f"OVERALL: {grand_accurate}/{grand_total} ({overall_pct:.0f}%)")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
