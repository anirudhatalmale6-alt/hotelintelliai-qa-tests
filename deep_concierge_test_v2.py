"""
Deep AI Concierge Testing v2 — All Hotels with KB content
Uses the correct Msg Simulator input approach (nth index method).
"""
import os
import json
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


def find_and_fill_simulator_input(page, message):
    """Find the correct message input in the Msg Simulator and fill it.
    The Msg Simulator has multiple inputs — we need the message/query input.
    Returns True if successfully filled and Simulate button is enabled."""

    # Strategy 1: Try each visible text input until Simulate button becomes enabled
    inputs = page.locator('input')
    input_count = inputs.count()

    for i in range(input_count):
        inp = inputs.nth(i)
        if not inp.is_visible():
            continue

        inp_type = (inp.get_attribute('type') or '').lower()
        if inp_type in ('email', 'password', 'file', 'hidden', 'checkbox', 'radio'):
            continue

        placeholder = inp.get_attribute('placeholder') or ''
        value = inp.input_value() or ''

        # Skip inputs that already have hotel ID or collection name
        if 'hotel' in value.lower() or '_cr' in value or '_chiangrai' in value or '_ping' in value or '_udaivilas' in value or 'lePatte' in value:
            continue

        # Skip number inputs (top_k, threshold)
        if inp_type == 'number':
            continue

        # Try filling this input
        inp.fill(message)
        page.wait_for_timeout(500)

        # Check if Simulate button is now enabled
        sim_btn = page.locator('button:has-text("Simulate")')
        if sim_btn.count() > 0:
            is_disabled = sim_btn.first.get_attribute('disabled')
            if is_disabled is None:  # not disabled = enabled
                return True
            else:
                # Clear and try next input
                inp.fill("")

    # Strategy 2: Try textareas
    textareas = page.locator('textarea')
    for i in range(textareas.count()):
        ta = textareas.nth(i)
        if ta.is_visible():
            ta.fill(message)
            page.wait_for_timeout(500)
            sim_btn = page.locator('button:has-text("Simulate")')
            if sim_btn.count() > 0:
                is_disabled = sim_btn.first.get_attribute('disabled')
                if is_disabled is None:
                    return True

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
                if 'INTENT' in line.upper():
                    parts = line.split('\n')[0]  # just first line
                elif 'ELAPSED' in line.upper():
                    elapsed = line
            elif line and not line.startswith('↻') and not line.startswith('●') and len(line) > 1:
                response_text += line + " "

    # Get intent separately
    for line in lines:
        line = line.strip()
        if 'INTENT' in line.upper() and ':' in line:
            intent = line.split(':', 1)[1].strip() if ':' in line else line
        if 'ELAPSED' in line.upper():
            elapsed = line

    return response_text.strip(), intent, elapsed


def evaluate_quality(response):
    """Evaluate response quality."""
    if not response or len(response) < 10:
        return "NO_RESPONSE", ["Empty or very short response"]

    issues = []
    response_lower = response.lower()

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
                # Try with shorter name
                try:
                    short = hname.split()[0:2]
                    navigate_to_hotel_simulator(page, ' '.join(short))
                except Exception as e2:
                    print(f"  RETRY FAILED: {e2}")
                    results[hid]["error"] = str(e2)
                    continue

            screenshot(page, f"H_{hid}_sim_ready")

            # First, analyze the form to understand input layout
            body = page.locator('body').inner_text()
            print(f"  Simulator page loaded")

            for qi, question in enumerate(QUESTIONS):
                print(f"\n  Q{qi+1}: {question}")

                # Re-navigate to simulator for each question (clean state)
                if qi > 0:
                    try:
                        # Just refresh the Debug > Msg Simulator tab
                        page.locator('button:has-text("Msg Simulator")').click()
                        page.wait_for_timeout(1500)
                    except Exception:
                        try:
                            navigate_to_hotel_simulator(page, hname)
                        except Exception:
                            print(f"  SKIP — could not navigate back")
                            results[hid]["questions"].append({
                                "question": question, "response": "",
                                "quality": "ERROR", "issues": ["Navigation failed"]
                            })
                            continue

                # Fill the message and simulate
                filled = find_and_fill_simulator_input(page, question)
                if not filled:
                    print(f"  SKIP — could not fill simulator input")
                    screenshot(page, f"H_{hid}_q{qi+1}_nofill")
                    results[hid]["questions"].append({
                        "question": question, "response": "",
                        "quality": "ERROR", "issues": ["Could not fill message input"]
                    })
                    continue

                # Click Simulate
                try:
                    page.locator('button:has-text("Simulate")').first.click()
                    page.wait_for_timeout(20000)  # Wait for AI response
                except Exception as e:
                    print(f"  ERROR clicking Simulate: {e}")
                    results[hid]["questions"].append({
                        "question": question, "response": "",
                        "quality": "ERROR", "issues": [str(e)[:100]]
                    })
                    continue

                # Extract response
                body = page.locator('body').inner_text()
                screenshot(page, f"H_{hid}_q{qi+1}")

                response, intent, elapsed = extract_response(body)
                quality, issues = evaluate_quality(response)

                # Display
                if response:
                    display = response[:200] + "..." if len(response) > 200 else response
                    print(f"  A: {display}")
                    print(f"  Quality: {quality} | Intent: {intent}")
                    if elapsed:
                        print(f"  {elapsed}")
                else:
                    print(f"  NO RESPONSE")
                    # Check for error messages
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
    with open("reports/concierge_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n\n" + "=" * 70)
    print("SUMMARY — AI CONCIERGE ACCURACY BY HOTEL")
    print("=" * 70)

    total_good = 0
    total_tested = 0

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
        total_good += good
        total_tested += total

        print(f"  Results: {good}/{total} GOOD ({100*good//total if total else 0}%)")
        for qual, count in sorted(quality_counts.items()):
            print(f"    {qual}: {count}")

        # List problematic answers
        for q in questions:
            if q.get("quality") not in ("GOOD",):
                print(f"  !! [{q['quality']}] \"{q['question']}\"")
                if q.get("response"):
                    print(f"     Response: {q['response'][:100]}...")

    print(f"\n{'='*60}")
    print(f"OVERALL: {total_good}/{total_tested} GOOD ({100*total_good//total_tested if total_tested else 0}%)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
