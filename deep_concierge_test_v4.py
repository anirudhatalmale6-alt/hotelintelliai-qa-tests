"""
Deep AI Concierge Testing v4 — All 6 Hotels
Uses Msg Simulator UI for accessible hotels and direct API for those with
blank dashboard issues (Imperial Mae Ping, Oberoi Udaivilas).
"""
import os
import json
import time
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
API_URL = "https://api.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "screenshots/v4"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# All 6 hotels with hotel-specific questions based on website content
HOTELS = [
    {
        "name": "The Heritage Chiang Rai Hotel and Convention",
        "short_name": "Heritage",
        "id": "heritage_chiangrai",
        "website": "heritagechiangrai.com",
        "dashboard_works": True,
        "questions": [
            ("How many rooms does the hotel have?", ["321"]),
            ("What room types are available?", ["deluxe", "executive", "suite", "premier"]),
            ("Do you have meeting or convention facilities?", ["ballroom", "meeting"]),
            ("What restaurants do you have?", ["all-day", "library", "lounge"]),
            ("Do you have a swimming pool?", ["pool", "outdoor"]),
            ("Where is the hotel located?", ["chiang rai"]),
            ("Do you have a fitness center?", ["fitness", "gym"]),
            ("Is there a spa?", ["spa"]),
            ("What are nearby attractions?", ["white temple", "night bazaar", "blue temple", "clock tower"]),
            ("Do you have WiFi?", ["wifi", "free"]),
        ]
    },
    {
        "name": "Grand Vista Chiangrai Hotel",
        "short_name": "Grand Vista",
        "id": "grand_vista_chiangrai",
        "website": "grandvistachiangrai.com",
        "dashboard_works": True,
        "questions": [
            ("What room types do you have?", ["superior", "deluxe", "suite"]),
            ("Do you have a swimming pool?", ["pool"]),
            ("Do you have a spa?", ["spa", "massage"]),
            ("What dining options are available?", ["restaurant", "bar"]),
            ("Do you have a fitness center?", ["fitness", "gym"]),
            ("Is there WiFi?", ["wifi", "free"]),
            ("Is there parking?", ["parking"]),
            ("Where is the hotel located?", ["chiang rai"]),
            ("How far is the airport?", ["airport"]),
            ("What nearby attractions are there?", ["night bazaar", "clock tower"]),
        ]
    },
    {
        "name": "Imperial Mae Ping Hotel",
        "short_name": "Imperial Mae Ping",
        "id": "imperial_mae_ping",
        "website": "imperialmaeping.com",
        "dashboard_works": False,  # Blank page bug
        "questions": [
            ("What time is check-in and check-out?", ["check-in", "check-out"]),
            ("What restaurants do you have?", ["restaurant", "dining"]),
            ("Do you have a spa?", ["spa", "massage"]),
            ("Do you have a swimming pool?", ["pool"]),
            ("Is there a fitness center?", ["fitness", "gym"]),
            ("Where is the hotel located?", ["chiang mai"]),
            ("Do you have parking?", ["parking"]),
            ("What is the phone number?", ["phone", "tel"]),
            ("Do you have meeting rooms?", ["meeting", "conference", "banquet"]),
            ("Do you offer airport transfer?", ["airport", "transfer"]),
        ]
    },
    {
        "name": "The Oberoi Udaivilas",
        "short_name": "Oberoi",
        "id": "oberoi_udaivilas",
        "website": "oberoihotels.com",
        "dashboard_works": False,  # Blank page bug
        "questions": [
            ("What types of rooms do you have?", ["kohinoor", "luxury", "suite", "premier"]),
            ("Do you have a swimming pool?", ["pool"]),
            ("What dining options are available?", ["suryamahal", "chandni", "restaurant"]),
            ("Do you have a spa?", ["spa", "oberoi"]),
            ("What experiences do you offer?", ["yoga", "painting", "cook"]),
            ("Where is the hotel located?", ["lake pichola", "udaipur"]),
            ("Do you have meeting rooms?", ["meeting", "conference"]),
            ("What nearby attractions can I visit?", ["city palace", "temple"]),
            ("Do you have a fitness center?", ["fitness", "gym"]),
            ("Do you offer airport transfer?", ["airport", "transfer"]),
        ]
    },
    {
        "name": "le Patte",
        "short_name": "le Patte",
        "id": "lePatte",
        "website": "lepattachiangrai.com",
        "dashboard_works": True,
        "questions": [
            ("What room types are available?", ["superior", "deluxe", "suite"]),
            ("How big are the rooms?", ["32", "52", "sqm"]),
            ("Do you have a swimming pool?", ["pool", "salt"]),
            ("Is there a gym or fitness center?", ["gym", "gorilla", "fitness"]),
            ("Do you have WiFi?", ["wifi", "free"]),
            ("Where is the hotel located?", ["chiang rai"]),
            ("What is nearby the hotel?", ["night bazaar", "clock tower"]),
            ("Do you have a restaurant?", ["restaurant"]),
            ("Is there parking available?", ["parking"]),
            ("How far is the airport?", ["7 km", "airport", "mae fah luang"]),
        ]
    },
    {
        "name": "The Riverie by Katathani",
        "short_name": "Riverie",
        "id": "hotel_riviera_cr",
        "website": "theriverie.com",
        "dashboard_works": True,
        "questions": [
            ("What room types do you have?", ["deluxe", "suite"]),
            ("Do you have a water park?", ["water park", "river splash"]),
            ("Do you have a spa?", ["spa", "tivaa"]),
            ("What dining options are available?", ["restaurant"]),
            ("Do you have a kids club?", ["kid", "children"]),
            ("Do you have conference facilities?", ["conference", "meeting"]),
            ("Where is the hotel located?", ["chiang rai"]),
            ("What is the phone number?", ["607999", "53 607"]),
            ("Do you offer airport transfer?", ["airport", "transfer"]),
            ("Do you have a swimming pool?", ["pool"]),
        ]
    },
]


def screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    page.screenshot(path=path)
    return path


def login(page):
    page.goto(DASHBOARD_URL, timeout=60000)
    page.wait_for_timeout(5000)
    body = page.locator('body').inner_text()
    if 'sign in' in body.lower() or 'password' in body.lower():
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(10000)
        print("Logged in")
    # Wait for hotels list
    for _ in range(15):
        body = page.locator('body').inner_text()
        if 'Heritage' in body or 'Riverie' in body:
            break
        page.wait_for_timeout(2000)
    page.wait_for_timeout(2000)


def navigate_to_simulator_ui(page, hotel):
    """Navigate to hotel Msg Simulator via UI."""
    hid = hotel["id"]
    short = hotel["short_name"]

    page.goto(DASHBOARD_URL, timeout=60000)
    page.wait_for_timeout(5000)

    # Wait for hotels
    for _ in range(10):
        body = page.locator('body').inner_text()
        if hid in body or short in body:
            break
        page.wait_for_timeout(2000)

    # Click hotel
    for selector in [f'text={hid}', f'text={short}', f'text={hotel["name"]}']:
        try:
            el = page.locator(selector).first
            el.click(timeout=5000)
            page.wait_for_timeout(8000)

            # Verify it loaded (not blank)
            body = page.locator('body').inner_text()
            if 'Debug' in body or 'Overview' in body:
                break
            else:
                print(f"    Blank page after clicking {selector}, trying next...")
                page.goto(DASHBOARD_URL, timeout=60000)
                page.wait_for_timeout(5000)
                continue
        except Exception:
            continue

    # Click Debug
    page.locator('text=Debug').first.click(timeout=10000)
    page.wait_for_timeout(2000)

    # Click Msg Simulator
    page.locator('button:has-text("Msg Simulator")').click()
    page.wait_for_timeout(2000)


def send_question_ui(page, question, hotel_id, q_index):
    """Send question via UI Msg Simulator."""
    # Set HOTEL ID (first visible text input)
    inputs = page.locator('input')
    visible_text_inputs = []
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        if not inp.is_visible():
            continue
        inp_type = (inp.get_attribute('type') or '').lower()
        if inp_type in ('email', 'password', 'file', 'hidden', 'checkbox', 'radio', 'number'):
            continue
        visible_text_inputs.append(inp)

    if len(visible_text_inputs) < 3:
        print(f"    ERROR: Found {len(visible_text_inputs)} text inputs, need 3")
        return None

    # Input 0 = HOTEL ID, Input 1 = GUEST IDENTIFIER, Input 2 = MESSAGE
    hotel_id_input = visible_text_inputs[0]
    msg_input = visible_text_inputs[2]

    # Verify/fix HOTEL ID
    current_hid = hotel_id_input.input_value()
    if current_hid != hotel_id:
        hotel_id_input.click(click_count=3)
        hotel_id_input.fill(hotel_id)
        page.wait_for_timeout(300)

    # Clear and fill MESSAGE
    msg_input.click(click_count=3)
    page.wait_for_timeout(200)
    msg_input.fill("")
    page.wait_for_timeout(200)
    msg_input.fill(question)
    page.wait_for_timeout(500)

    # Verify
    actual = msg_input.input_value()
    if actual != question:
        msg_input.fill("")
        msg_input.type(question, delay=20)
        page.wait_for_timeout(300)

    # Screenshot before
    screenshot(page, f"{hotel_id}_q{q_index+1}_before")

    # Click Simulate
    sim_btn = page.locator('button:has-text("Simulate")')
    if sim_btn.count() == 0 or sim_btn.first.get_attribute('disabled') is not None:
        print(f"    Simulate button not available")
        return None

    sim_btn.first.click()

    # Wait for response
    for _ in range(15):
        page.wait_for_timeout(2000)
        body = page.locator('body').inner_text()
        if 'AGENT RESPONSE' in body.upper():
            break

    page.wait_for_timeout(3000)
    screenshot(page, f"{hotel_id}_q{q_index+1}_after")
    return page.locator('body').inner_text()


def send_question_api(page, question, hotel_id, q_index):
    """Send question via direct API call (for hotels with blank dashboards)."""
    result = page.evaluate(f"""async () => {{
        try {{
            const resp = await fetch('https://api.hotelintelliai.com/simulate', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                credentials: 'include',
                body: JSON.stringify({{
                    hotel_id: '{hotel_id}',
                    guest_id: 'debug_guest_001',
                    message: `{question.replace('`', '\\`').replace("'", "\\'")}`
                }})
            }});
            const text = await resp.text();
            return {{ status: resp.status, data: text }};
        }} catch(e) {{
            return {{ error: e.message }};
        }}
    }}""")

    status = result.get('status', 0)
    data = result.get('data', '')
    error = result.get('error', '')

    if error:
        print(f"    API Error: {error}")
        return None

    if status == 200:
        try:
            parsed = json.loads(data)
            response = parsed.get('response', parsed.get('message', parsed.get('reply', '')))
            intent = parsed.get('intent', '')
            elapsed = parsed.get('elapsed', '')
            return f"AGENT RESPONSE\n{response}\nINTENT: {intent}\nELAPSED: {elapsed}"
        except json.JSONDecodeError:
            return f"AGENT RESPONSE\n{data}"
    elif status == 404:
        # Try alternative API endpoints
        for endpoint in ['/chat/simulate', '/msg/simulate', '/debug/simulate', '/concierge/simulate']:
            result2 = page.evaluate(f"""async () => {{
                try {{
                    const resp = await fetch('https://api.hotelintelliai.com{endpoint}', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        credentials: 'include',
                        body: JSON.stringify({{
                            hotel_id: '{hotel_id}',
                            guest_id: 'debug_guest_001',
                            message: `{question.replace('`', '\\`').replace("'", "\\'")}`
                        }})
                    }});
                    return {{ status: resp.status, data: (await resp.text()).substring(0, 500) }};
                }} catch(e) {{
                    return {{ error: e.message }};
                }}
            }}""")
            if result2.get('status') == 200:
                print(f"    Found working endpoint: {endpoint}")
                try:
                    parsed = json.loads(result2.get('data', ''))
                    response = parsed.get('response', parsed.get('message', ''))
                    return f"AGENT RESPONSE\n{response}"
                except:
                    return f"AGENT RESPONSE\n{result2.get('data', '')}"
        print(f"    API returned {status}: {data[:200]}")
        return None
    else:
        print(f"    API returned {status}: {data[:200]}")
        return None


def extract_response(body):
    if not body:
        return "", "", ""

    lines = body.split('\n')
    response_text = ""
    intent = ""
    elapsed = ""
    capture = False

    for line in lines:
        stripped = line.strip()
        upper = stripped.upper()

        if 'AGENT RESPONSE' in upper:
            capture = True
            continue

        if capture:
            if any(kw in upper for kw in ['INTENT:', 'INTENT ', 'ELAPSED', 'LANGUAGE:', 'CONFIDENCE:', 'HOTEL ID', 'GUEST IDENTIFIER', 'MESSAGE']):
                capture = False
                if 'INTENT' in upper:
                    parts = stripped.split(':', 1) if ':' in stripped else [stripped]
                    intent = parts[1].strip() if len(parts) > 1 else stripped
                elif 'ELAPSED' in upper:
                    elapsed = stripped
                continue

            if stripped.startswith(('↻', '●', '►', '▶')):
                continue
            if stripped in ('Simulate', 'MESSAGE', 'HOTEL ID', 'GUEST IDENTIFIER'):
                continue
            if len(stripped) <= 1:
                continue

            # Handle inline INTENT/LANGUAGE at end of response
            if 'INTENT ' in stripped and 'LANGUAGE' in stripped:
                parts = stripped.split('INTENT')
                response_text += parts[0].strip() + " "
                intent = parts[1].strip().split()[0] if parts[1].strip() else ""
                continue

            response_text += stripped + " "

    return response_text.strip(), intent, elapsed


def evaluate_accuracy(response, expected_keywords):
    if not response or len(response) < 10:
        return "NO_RESPONSE", 0, []

    response_lower = response.lower()

    # Check for "connect you with team" (no KB data)
    if "let me connect you with" in response_lower or "best possible answer" in response_lower:
        return "ESCALATED", 0, []

    # Check for "don't know" responses
    no_info_phrases = [
        "i don't have", "i don't know", "i'm not sure",
        "i cannot find", "not available", "no information",
        "i apologize", "sorry, i don't", "unfortunately",
    ]
    for phrase in no_info_phrases:
        if phrase in response_lower:
            return "NO_INFO", 0, []

    if 'error' in response_lower and len(response) < 50:
        return "ERROR", 0, []

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

        login(page)

        # First, discover the simulate API endpoint
        print("\nDiscovering simulate API endpoint...")
        # Navigate to a working hotel's simulator to capture the API call
        page.goto(DASHBOARD_URL, timeout=60000)
        page.wait_for_timeout(8000)

        api_calls = []
        page.on("request", lambda req: api_calls.append({
            "url": req.url, "method": req.method,
            "post": req.post_data[:500] if req.post_data else None
        }) if ('simulate' in req.url.lower() or 'chat' in req.url.lower() or 'msg' in req.url.lower()) and req.method == 'POST' else None)

        # Navigate to Heritage simulator
        navigate_to_simulator_ui(page, HOTELS[0])  # Heritage

        # Send a test question to capture the API
        send_question_ui(page, "hello", HOTELS[0]["id"], 99)

        print(f"Captured {len(api_calls)} simulate API calls:")
        simulate_endpoint = None
        for call in api_calls:
            print(f"  {call['method']} {call['url']}")
            if call['post']:
                print(f"    Body: {call['post'][:200]}")
            simulate_endpoint = call['url']

        if simulate_endpoint:
            print(f"\nSimulate endpoint: {simulate_endpoint}")

        # Now test all hotels
        for hotel in HOTELS:
            hid = hotel["id"]
            hname = hotel["name"]
            short = hotel["short_name"]
            works = hotel["dashboard_works"]

            print(f"\n\n{'='*70}")
            print(f"TESTING: {hname} (ID: {hid})")
            print(f"Dashboard works: {works}")
            print(f"{'='*70}")

            hotel_results = {
                "name": hname,
                "id": hid,
                "website": hotel["website"],
                "dashboard_works": works,
                "questions": [],
            }

            if works:
                # Navigate to simulator UI
                try:
                    navigate_to_simulator_ui(page, hotel)
                    screenshot(page, f"{hid}_sim_ready")
                except Exception as e:
                    print(f"  NAVIGATION ERROR: {e}")
                    hotel_results["error"] = str(e)[:200]
                    all_results[hid] = hotel_results
                    continue

            for qi, (question, expected_kw) in enumerate(hotel["questions"]):
                print(f"\n  Q{qi+1}: {question}")

                if works:
                    # Reset simulator tab between questions
                    if qi > 0:
                        try:
                            page.locator('button:has-text("Msg Simulator")').click()
                            page.wait_for_timeout(2000)
                        except Exception:
                            pass

                    body = send_question_ui(page, question, hid, qi)
                else:
                    # Use API for hotels with blank dashboards
                    if simulate_endpoint:
                        # Use the discovered endpoint
                        escaped_q = question.replace("'", "\\'").replace("`", "\\`").replace('"', '\\"')
                        result = page.evaluate(f"""async () => {{
                            try {{
                                const resp = await fetch('{simulate_endpoint}', {{
                                    method: 'POST',
                                    headers: {{ 'Content-Type': 'application/json', 'x-hotel-id': '{hid}' }},
                                    credentials: 'include',
                                    body: JSON.stringify({{
                                        hotel_id: '{hid}',
                                        guest_id: 'debug_guest_001',
                                        message: "{escaped_q}"
                                    }})
                                }});
                                return {{ status: resp.status, data: (await resp.text()).substring(0, 2000) }};
                            }} catch(e) {{
                                return {{ error: e.message }};
                            }}
                        }}""")

                        if result.get('status') == 200:
                            try:
                                parsed = json.loads(result.get('data', '{}'))
                                resp_text = parsed.get('response', parsed.get('reply', parsed.get('message', '')))
                                intent_val = parsed.get('intent', '')
                                body = f"AGENT RESPONSE\n{resp_text}\nINTENT: {intent_val}"
                            except json.JSONDecodeError:
                                body = f"AGENT RESPONSE\n{result.get('data', '')}"
                        else:
                            print(f"    API Error: {result}")
                            body = None
                    else:
                        body = send_question_api(page, question, hid, qi)

                response, intent, elapsed = extract_response(body) if body else ("", "", "")
                accuracy, match_pct, matched = evaluate_accuracy(response, expected_kw)

                # Display
                if response:
                    display = response[:200] + "..." if len(response) > 200 else response
                    print(f"    A: {display}")
                    print(f"    Accuracy: {accuracy} | Keywords: {len(matched)}/{len(expected_kw)} matched")
                else:
                    print(f"    NO RESPONSE")

                hotel_results["questions"].append({
                    "q_num": qi + 1,
                    "question": question,
                    "expected_keywords": expected_kw,
                    "response": response[:500] if response else "",
                    "intent": intent,
                    "elapsed": elapsed,
                    "accuracy": accuracy,
                    "match_pct": match_pct,
                    "matched_kw": matched,
                })

            # Calculate summary
            questions = hotel_results["questions"]
            total = len(questions)
            accurate = sum(1 for q in questions if q["accuracy"] == "ACCURATE")
            partial = sum(1 for q in questions if q["accuracy"] == "PARTIAL")
            no_info = sum(1 for q in questions if q["accuracy"] == "NO_INFO")
            escalated = sum(1 for q in questions if q["accuracy"] == "ESCALATED")
            unverified = sum(1 for q in questions if q["accuracy"] == "UNVERIFIED")
            errors = sum(1 for q in questions if q["accuracy"] in ("ERROR", "NO_RESPONSE"))

            hotel_results["summary"] = {
                "total": total,
                "accurate": accurate,
                "partial": partial,
                "no_info": no_info,
                "escalated": escalated,
                "unverified": unverified,
                "errors": errors,
                "accuracy_pct": round((accurate + partial) / total * 100, 1) if total else 0,
            }

            print(f"\n  SUMMARY: {accurate} accurate, {partial} partial, {escalated} escalated, {no_info} no_info, {unverified} unverified, {errors} errors")
            print(f"  Accuracy: {hotel_results['summary']['accuracy_pct']}%")

            all_results[hid] = hotel_results

        context.close()
        browser.close()

    # Save results
    os.makedirs("reports", exist_ok=True)
    with open("reports/concierge_test_results_v4.json", "w") as f:
        json.dump(all_results, f, indent=2)

    # Print final summary
    print(f"\n\n{'='*70}")
    print("FINAL SUMMARY — AI CONCIERGE ACCURACY BY HOTEL")
    print(f"{'='*70}")

    total_accurate = 0
    total_tested = 0

    for hid, data in all_results.items():
        summary = data.get("summary", {})
        total = summary.get("total", 0)
        acc = summary.get("accurate", 0)
        partial = summary.get("partial", 0)
        escalated = summary.get("escalated", 0)
        no_info = summary.get("no_info", 0)
        acc_pct = summary.get("accuracy_pct", 0)

        total_accurate += acc + partial
        total_tested += total

        print(f"\n{data['name']} ({hid})")
        print(f"  Accuracy: {acc_pct}% ({acc} accurate, {partial} partial out of {total})")
        print(f"  Escalated (missing KB): {escalated}")
        print(f"  No Info: {no_info}")

        # List failed questions
        for q in data.get("questions", []):
            if q["accuracy"] in ("ESCALATED", "NO_INFO", "ERROR", "NO_RESPONSE"):
                print(f"  !! [{q['accuracy']}] Q{q['q_num']}: {q['question']}")

    overall = round(total_accurate / total_tested * 100, 1) if total_tested else 0
    print(f"\n{'='*70}")
    print(f"OVERALL: {total_accurate}/{total_tested} answered ({overall}% accuracy)")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
