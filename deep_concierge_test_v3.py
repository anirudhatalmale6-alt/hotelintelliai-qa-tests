"""
Deep AI Concierge Testing v3 — Fixed input targeting
Properly sets HOTEL ID, targets MESSAGE input by placeholder, waits for fresh responses.
"""
import os
import json
import time
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "screenshots"

# Hotels with KB content (skip Grand Vista and Imperial Mae Ping — 0 chunks)
HOTELS = [
    {"name": "The Heritage Chiang Rai Hotel and Convention", "id": "heritage_chiangrai", "chunks": 49},
    {"name": "The Oberoi Udaivilas", "id": "oberoi_udaivilas", "chunks": 352},
    {"name": "le Patte", "id": "lePatte", "chunks": 306},
    {"name": "The Riverie by Katathani", "id": "hotel_riviera_cr", "chunks": 467},
]

QUESTIONS = [
    "What time is check-in and check-out?",
    "What types of rooms do you have?",
    "Do you have a swimming pool?",
    "Do you have a spa? What treatments are available?",
    "What dining options or restaurants do you have?",
    "Is there airport transfer or shuttle service?",
    "Do you have a fitness center or gym?",
    "What is your cancellation policy?",
    "Do you have WiFi? Is it free?",
    "Is breakfast included? What time is it served?",
]


def screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    page.screenshot(path=path)


def navigate_to_hotel_simulator(page, hotel_name):
    """Navigate from dashboard to a hotel's Msg Simulator."""
    page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)

    # Click on hotel
    page.locator(f'text={hotel_name}').first.click()
    page.wait_for_timeout(5000)

    # Navigate to Debug > Msg Simulator
    page.locator('text=Debug').first.click()
    page.wait_for_timeout(2000)
    page.locator('button:has-text("Msg Simulator")').click()
    page.wait_for_timeout(2000)

    return True


def set_hotel_id_and_message(page, hotel_id, message):
    """Set the HOTEL ID field and MESSAGE field correctly.

    From the screenshot, the form layout is:
    - Input 1: HOTEL ID (label "HOTEL ID")
    - Input 2: GUEST IDENTIFIER (label "GUEST IDENTIFIER")
    - Input 3: MESSAGE (placeholder "e.g. do you have a spa?")
    """
    inputs = page.locator('input')
    input_count = inputs.count()

    # Identify inputs by their characteristics
    hotel_id_input = None
    message_input = None

    visible_text_inputs = []
    for i in range(input_count):
        inp = inputs.nth(i)
        if not inp.is_visible():
            continue
        inp_type = (inp.get_attribute('type') or '').lower()
        if inp_type in ('email', 'password', 'file', 'hidden', 'checkbox', 'radio'):
            continue
        visible_text_inputs.append(inp)

    # The MESSAGE input has a specific placeholder
    for inp in visible_text_inputs:
        placeholder = (inp.get_attribute('placeholder') or '').lower()
        if 'spa' in placeholder or 'e.g.' in placeholder or 'message' in placeholder:
            message_input = inp
            break

    # The HOTEL ID input is the first visible text input (or the one with hotel-like value)
    for inp in visible_text_inputs:
        if inp == message_input:
            continue
        value = (inp.input_value() or '').lower()
        placeholder = (inp.get_attribute('placeholder') or '').lower()
        # Hotel ID input typically has a hotel ID value or hotel-related placeholder
        if any(hid in value for hid in ['hotel', 'heritage', 'oberoi', 'patte', 'riviera', 'vista', 'imperial', 'lepatte']):
            hotel_id_input = inp
            break
        if 'hotel' in placeholder:
            hotel_id_input = inp
            break

    # Fallback: if we have 3+ visible inputs, first is hotel ID, third is message
    if not hotel_id_input and len(visible_text_inputs) >= 1:
        hotel_id_input = visible_text_inputs[0]
    if not message_input and len(visible_text_inputs) >= 3:
        message_input = visible_text_inputs[2]
    elif not message_input and len(visible_text_inputs) >= 2:
        # Try the last visible text input
        message_input = visible_text_inputs[-1]

    if not message_input:
        print(f"    ERROR: Could not find MESSAGE input (found {len(visible_text_inputs)} visible text inputs)")
        return False

    # Step 1: Set HOTEL ID
    if hotel_id_input:
        current_hotel_id = hotel_id_input.input_value()
        if current_hotel_id != hotel_id:
            print(f"    Updating HOTEL ID: {current_hotel_id} -> {hotel_id}")
            hotel_id_input.click()
            hotel_id_input.fill("")
            hotel_id_input.fill(hotel_id)
            page.wait_for_timeout(300)

    # Step 2: Clear and fill MESSAGE
    message_input.click()
    message_input.fill("")
    page.wait_for_timeout(200)
    message_input.fill(message)
    page.wait_for_timeout(500)

    # Verify Simulate button is enabled
    sim_btn = page.locator('button:has-text("Simulate")')
    if sim_btn.count() > 0:
        is_disabled = sim_btn.first.get_attribute('disabled')
        if is_disabled is None:
            return True
        else:
            print(f"    WARNING: Simulate button still disabled after filling inputs")
            return False

    print(f"    ERROR: Simulate button not found")
    return False


def extract_response(body):
    """Extract AI response, intent, and elapsed time from page body."""
    lines = body.split('\n')
    response_text = ""
    intent = ""
    elapsed = ""

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

    # Get intent and elapsed separately
    for line in lines:
        line = line.strip()
        if 'INTENT' in line.upper() and ':' in line:
            intent = line.split(':', 1)[1].strip()
        if 'ELAPSED' in line.upper():
            elapsed = line

    return response_text.strip(), intent, elapsed


def evaluate_quality(question, response):
    """Evaluate response quality — check if it actually answers the question asked."""
    if not response or len(response) < 10:
        return "NO_RESPONSE", ["Empty or very short response"]

    response_lower = response.lower()
    question_lower = question.lower()

    if 'error' in response_lower or '⚠' in response:
        return "ERROR", ["Error in response"]

    if any(phrase in response_lower for phrase in [
        "i don't have", "i don't know", "i'm not sure",
        "i cannot find", "not available in", "no information",
        "i apologize, but i don't", "sorry, i don't have",
        "i don't have specific information",
        "unfortunately, i don't",
    ]):
        return "NO_INFO", ["AI lacks information to answer"]

    # Check if response is relevant to the question
    issues = []

    # Map questions to expected keywords in a good response
    relevance_checks = {
        "check-in": ["check-in", "check in", "check-out", "check out", "pm", "am", "noon"],
        "rooms": ["room", "suite", "deluxe", "standard", "superior", "premier", "villa", "accommodation"],
        "swimming pool": ["pool", "swim", "aqua", "water"],
        "spa": ["spa", "massage", "treatment", "wellness", "therapy", "facial", "body"],
        "dining": ["restaurant", "dining", "breakfast", "lunch", "dinner", "cafe", "bar", "cuisine", "food"],
        "airport": ["airport", "transfer", "shuttle", "transport", "pickup", "taxi", "car"],
        "fitness": ["fitness", "gym", "exercise", "workout", "health club"],
        "cancellation": ["cancel", "refund", "policy", "free cancellation", "charge", "notice", "hours before"],
        "wifi": ["wifi", "wi-fi", "internet", "wireless", "complimentary", "free"],
        "breakfast": ["breakfast", "morning", "buffet", "served", "included", "complimentary"],
    }

    # Find which topic the question is about
    question_topic = None
    for topic, keywords in relevance_checks.items():
        if topic in question_lower:
            question_topic = topic
            break

    if question_topic:
        expected_keywords = relevance_checks[question_topic]
        has_relevant_keyword = any(kw in response_lower for kw in expected_keywords)
        if not has_relevant_keyword:
            issues.append(f"Response may not answer the question about '{question_topic}'")
            # Check if it's just the check-in response repeated
            if "check-in" in response_lower and question_topic != "check-in":
                return "WRONG_ANSWER", [f"Response answers check-in question instead of '{question_topic}'"]

    if len(response) < 30:
        issues.append("Response seems short")

    if issues:
        return "PARTIAL", issues

    return "GOOD", []


def main():
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(30000)

        # Login to dashboard
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        print("Logged in to dashboard\n")

        for hotel in HOTELS:
            hid = hotel["id"]
            hname = hotel["name"]
            chunks = hotel["chunks"]

            print(f"\n{'='*60}")
            print(f"TESTING: {hname} ({hid}) — {chunks} chunks")
            print(f"{'='*60}")

            results[hid] = {"name": hname, "chunks": chunks, "questions": []}

            try:
                navigate_to_hotel_simulator(page, hname)
            except Exception as e:
                print(f"  NAVIGATION ERROR: {e}")
                try:
                    short = hname.split()[0:2]
                    navigate_to_hotel_simulator(page, ' '.join(short))
                except Exception as e2:
                    print(f"  RETRY FAILED: {e2}")
                    results[hid]["error"] = str(e2)
                    continue

            screenshot(page, f"V3_{hid}_sim_ready")
            print(f"  Simulator page loaded")

            for qi, question in enumerate(QUESTIONS):
                print(f"\n  Q{qi+1}: {question}")

                # For each question, refresh the Msg Simulator tab to get clean state
                try:
                    page.locator('button:has-text("Msg Simulator")').click()
                    page.wait_for_timeout(1500)
                except Exception:
                    try:
                        navigate_to_hotel_simulator(page, hname)
                    except Exception:
                        print(f"  SKIP — could not navigate back")
                        results[hid]["questions"].append({
                            "question": question, "response": "",
                            "intent": "", "elapsed": "",
                            "quality": "ERROR", "issues": ["Navigation failed"]
                        })
                        continue

                # Set hotel ID and message
                filled = set_hotel_id_and_message(page, hid, question)
                if not filled:
                    print(f"  SKIP — could not fill simulator inputs")
                    screenshot(page, f"V3_{hid}_q{qi+1}_nofill")
                    results[hid]["questions"].append({
                        "question": question, "response": "",
                        "intent": "", "elapsed": "",
                        "quality": "ERROR", "issues": ["Could not fill inputs"]
                    })
                    continue

                # Screenshot before clicking Simulate
                screenshot(page, f"V3_{hid}_q{qi+1}_before")

                # Click Simulate
                try:
                    page.locator('button:has-text("Simulate")').first.click()
                    # Wait for response — look for AGENT RESPONSE to appear
                    try:
                        page.locator('text=AGENT RESPONSE').wait_for(timeout=30000)
                        page.wait_for_timeout(2000)  # Extra wait for full response
                    except Exception:
                        page.wait_for_timeout(15000)  # Fallback wait
                except Exception as e:
                    print(f"  ERROR clicking Simulate: {e}")
                    results[hid]["questions"].append({
                        "question": question, "response": "",
                        "intent": "", "elapsed": "",
                        "quality": "ERROR", "issues": [str(e)[:100]]
                    })
                    continue

                # Extract response
                body = page.locator('body').inner_text()
                screenshot(page, f"V3_{hid}_q{qi+1}_after")

                response, intent, elapsed = extract_response(body)
                quality, issues = evaluate_quality(question, response)

                # Display
                if response:
                    display = response[:200] + "..." if len(response) > 200 else response
                    print(f"  A: {display}")
                    print(f"  Quality: {quality} | Intent: {intent}")
                    if elapsed:
                        print(f"  {elapsed}")
                    if issues:
                        print(f"  Issues: {', '.join(issues)}")
                else:
                    print(f"  NO RESPONSE")
                    for line in body.split('\n'):
                        if '⚠' in line or 'error' in line.lower():
                            print(f"  {line.strip()}")

                results[hid]["questions"].append({
                    "question": question,
                    "response": response[:500] if response else "",
                    "intent": intent,
                    "elapsed": elapsed,
                    "quality": quality,
                    "issues": issues,
                })

        context.close()
        browser.close()

    # Save results
    os.makedirs("reports", exist_ok=True)
    with open("reports/concierge_test_results_v3.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n\n" + "=" * 70)
    print("SUMMARY — AI CONCIERGE ACCURACY BY HOTEL")
    print("=" * 70)

    total_good = 0
    total_tested = 0
    total_wrong = 0

    for hid, data in results.items():
        name = data["name"]
        chunks = data["chunks"]
        questions = data.get("questions", [])

        print(f"\n{name} ({hid}) — {chunks} chunks")

        if not questions:
            print(f"  SKIPPED (error or no data)")
            continue

        quality_counts = {}
        for q in questions:
            qual = q.get("quality", "UNKNOWN")
            quality_counts[qual] = quality_counts.get(qual, 0) + 1

        total = len(questions)
        good = quality_counts.get("GOOD", 0)
        wrong = quality_counts.get("WRONG_ANSWER", 0)
        total_good += good
        total_wrong += wrong
        total_tested += total

        print(f"  Results: {good}/{total} GOOD ({100*good//total if total else 0}%)")
        for qual, count in sorted(quality_counts.items()):
            print(f"    {qual}: {count}")

        # List problematic answers
        for q in questions:
            if q.get("quality") not in ("GOOD",):
                print(f"  !! [{q['quality']}] \"{q['question']}\"")
                if q.get("response"):
                    print(f"     Response: {q['response'][:120]}...")
                if q.get("issues"):
                    print(f"     Issues: {', '.join(q['issues'])}")

    print(f"\n{'='*60}")
    print(f"OVERALL: {total_good}/{total_tested} GOOD ({100*total_good//total_tested if total_tested else 0}%)")
    if total_wrong > 0:
        print(f"WRONG ANSWERS: {total_wrong}/{total_tested} — AI returned irrelevant response")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
