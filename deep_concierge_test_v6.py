"""
Deep AI Concierge Test v6 - Fixed HOTEL ID handling
Key fix: Explicitly sets HOTEL ID field to match current hotel before each question.
"""
import os
import re
import json
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "/var/lib/freelancer/projects/40298427/screenshots/v6"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

HOTELS = [
    {"name": "Imperial Mae Ping Hotel", "id": "imperial_mae_ping", "chunks": 31},
    {"name": "The Oberoi Udaivilas", "id": "oberoi_udaivilas", "chunks": 3},
    {"name": "The Riverie by Katathani", "id": "hotel_riviera_cr", "chunks": 1},
]

HOTEL_QUESTIONS = {
    "imperial_mae_ping": [
        "What time is check-in and check-out?",
        "What types of rooms do you have?",
        "Do you have a swimming pool?",
        "Do you have a spa?",
        "What restaurants do you have?",
        "Is there WiFi available?",
        "Do you offer airport transfer?",
        "What is your cancellation policy?",
        "Is breakfast included?",
        "Where is the hotel located?",
    ],
    "oberoi_udaivilas": [
        "What types of rooms and suites do you have?",
        "Do you have a swimming pool?",
        "Tell me about the spa",
        "What restaurants do you have?",
        "Do you offer yoga sessions?",
        "What experiences and activities are available?",
        "Do you have event or conference facilities?",
        "Where is the hotel located?",
        "What awards has the hotel won?",
        "Do you have a fitness center?",
    ],
    "hotel_riviera_cr": [
        "What types of rooms do you have?",
        "Do you have a swimming pool or water park?",
        "Do you have a spa?",
        "What dining options do you have?",
        "Do you have a kids club?",
        "Can you host weddings or conferences?",
        "Do you offer airport transfers?",
        "Where is the hotel located?",
        "What is the hotel phone number?",
        "What awards has the hotel won?",
    ],
}


def screenshot(page, name):
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"{name}.png"))


def navigate_to_simulator(page, hotel_name):
    page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    page.locator(f'text={hotel_name}').first.click()
    page.wait_for_timeout(5000)
    page.locator('text=Debug').first.click()
    page.wait_for_timeout(3000)
    page.locator('button:has-text("Msg Simulator")').click()
    page.wait_for_timeout(3000)


def ask_question(page, hotel_id, question):
    """Fill HOTEL ID, MESSAGE, and click Simulate. Returns response dict."""
    inputs = page.locator('input')
    visible = []
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        if inp.is_visible():
            itype = (inp.get_attribute('type') or '').lower()
            if itype not in ('email', 'password', 'file', 'hidden', 'checkbox', 'radio', 'number'):
                visible.append(inp)

    if len(visible) < 3:
        print(f"    Only {len(visible)} inputs found")
        return None

    # Input 0: HOTEL ID - SET IT TO THE CORRECT HOTEL
    hotel_input = visible[0]
    current_hotel_id = hotel_input.input_value()
    print(f"    Hotel ID field: '{current_hotel_id}' -> setting to '{hotel_id}'")
    hotel_input.click()
    hotel_input.fill("")
    hotel_input.fill(hotel_id)
    page.wait_for_timeout(300)

    # Input 1: GUEST IDENTIFIER - leave as is
    guest_id = visible[1].input_value()
    if not guest_id:
        visible[1].fill("debug_guest_001")

    # Input 2: MESSAGE - fill with question
    msg_input = visible[2]
    msg_input.click()
    msg_input.fill("")
    msg_input.fill(question)
    page.wait_for_timeout(500)

    # Verify
    actual_hotel = visible[0].input_value()
    actual_msg = msg_input.input_value()
    print(f"    Hotel ID: '{actual_hotel}' | Message: '{actual_msg[:50]}'")

    # Click Simulate
    sim_btn = page.locator('button:has-text("Simulate")')
    if sim_btn.count() == 0 or sim_btn.first.get_attribute('disabled') is not None:
        print(f"    Simulate button not available")
        return None

    sim_btn.first.click()
    print(f"    Simulating...")
    page.wait_for_timeout(15000)

    # Extract response
    body = page.locator('body').inner_text()
    return extract_response(body)


def extract_response(body):
    lines = body.split('\n')
    response_text = ""
    intent = ""
    elapsed = ""
    escalate = ""

    capture = False
    for line in lines:
        s = line.strip()
        if 'AGENT RESPONSE' in s.upper():
            capture = True
            continue
        if capture:
            u = s.upper()
            if any(kw in u for kw in ['INTENT', 'ELAPSED', 'LANGUAGE', 'CONFIDENCE', 'ESCALAT']):
                capture = False
            elif s and len(s) > 1 and not s.startswith('↻') and not s.startswith('●'):
                response_text += s + " "

    for line in lines:
        s = line.strip()
        u = s.upper()
        if 'INTENT' in u and not response_text or 'INTENT' in u:
            if ':' in s:
                intent = s.split(':', 1)[1].strip() if ':' in s else ""
            else:
                # Next line might have intent value
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    intent = lines[idx + 1].strip()
        if 'ELAPSED' in u:
            parts = re.findall(r'[\d.]+s', s)
            if parts:
                elapsed = parts[0]
            else:
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    elapsed = lines[idx + 1].strip()
        if 'ESCALATE' in u:
            if 'YES' in u:
                escalate = "YES"
            elif 'NO' in u:
                escalate = "NO"
            else:
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    escalate = lines[idx + 1].strip()

    return {
        "response": response_text.strip(),
        "intent": intent,
        "elapsed": elapsed,
        "escalate": escalate,
    }


def evaluate_quality(response_text):
    if not response_text or len(response_text) < 10:
        return "NO_RESPONSE", ["Empty or very short response"]

    lower = response_text.lower()

    if any(p in lower for p in [
        "let me connect you with", "best possible answer",
        "connect you with our", "transfer you to",
        "someone will be in touch",
    ]):
        return "ESCALATION", ["AI escalated - KB missing info for this question"]

    if 'error' in lower or '⚠' in response_text:
        return "ERROR", ["Error in response"]

    if any(p in lower for p in [
        "i don't have", "i don't know", "i'm not sure",
        "i cannot find", "no information",
        "i apologize", "unfortunately",
    ]):
        return "NO_INFO", ["AI lacks information"]

    if len(response_text) < 30:
        return "PARTIAL", ["Short response"]

    return "GOOD", []


def main():
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 720})
        page = ctx.new_page()
        page.set_default_timeout(60000)

        # Login
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(2000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        print("Logged in\n")

        for hotel in HOTELS:
            hid = hotel["id"]
            hname = hotel["name"]
            chunks = hotel["chunks"]
            questions = HOTEL_QUESTIONS.get(hid, HOTEL_QUESTIONS["imperial_mae_ping"])

            print(f"\n{'='*70}")
            print(f"TESTING: {hname} ({hid}) - {chunks} chunks")
            print(f"{'='*70}")

            results[hid] = {"name": hname, "chunks": chunks, "questions": []}

            for qi, question in enumerate(questions):
                print(f"\n  Q{qi+1}: {question}")

                try:
                    # Fresh navigation for each question
                    navigate_to_simulator(page, hname)
                    screenshot(page, f"{hid}_q{qi+1}_before")

                    resp = ask_question(page, hid, question)
                    screenshot(page, f"{hid}_q{qi+1}_after")

                    if resp and resp.get("response"):
                        quality, issues = evaluate_quality(resp["response"])
                        display = resp["response"][:200]
                        print(f"  A: {display}")
                        print(f"  Quality: {quality} | Intent: {resp.get('intent','')} | Escalate: {resp.get('escalate','')}")

                        results[hid]["questions"].append({
                            "question": question,
                            "response": resp["response"][:500],
                            "intent": resp.get("intent", ""),
                            "elapsed": resp.get("elapsed", ""),
                            "escalate": resp.get("escalate", ""),
                            "quality": quality,
                            "issues": issues,
                        })
                    else:
                        print(f"  NO RESPONSE")
                        results[hid]["questions"].append({
                            "question": question, "response": "",
                            "quality": "NO_RESPONSE", "issues": ["No response"],
                        })

                except Exception as e:
                    print(f"  ERROR: {e}")
                    results[hid]["questions"].append({
                        "question": question, "response": "",
                        "quality": "ERROR", "issues": [str(e)[:150]],
                    })

        ctx.close()
        browser.close()

    # Save
    os.makedirs("/var/lib/freelancer/projects/40298427/reports", exist_ok=True)
    with open("/var/lib/freelancer/projects/40298427/reports/concierge_test_v6_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Summary
    print(f"\n\n{'='*70}")
    print("SUMMARY - AI CONCIERGE ACCURACY BY HOTEL")
    print(f"{'='*70}")

    total_good = total_esc = total_noinfo = total_tested = 0

    for hid, data in results.items():
        qs = data.get("questions", [])
        print(f"\n{data['name']} ({hid}) - {data['chunks']} chunks")

        counts = {}
        for q in qs:
            qual = q.get("quality", "UNKNOWN")
            counts[qual] = counts.get(qual, 0) + 1

        total = len(qs)
        good = counts.get("GOOD", 0)
        esc = counts.get("ESCALATION", 0)
        noinfo = counts.get("NO_INFO", 0)
        total_good += good
        total_esc += esc
        total_noinfo += noinfo
        total_tested += total

        print(f"  {good}/{total} GOOD ({100*good//total if total else 0}%)")
        for qual, c in sorted(counts.items()):
            print(f"    {qual}: {c}")

        for q in qs:
            if q.get("quality") != "GOOD":
                print(f"  !! [{q['quality']}] \"{q['question']}\"")
                if q.get("response"):
                    print(f"     -> {q['response'][:120]}")

    print(f"\n{'='*70}")
    print(f"OVERALL: {total_good}/{total_tested} GOOD ({100*total_good//total_tested if total_tested else 0}%)")
    print(f"ESCALATIONS: {total_esc}/{total_tested}")
    print(f"NO INFO: {total_noinfo}/{total_tested}")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
