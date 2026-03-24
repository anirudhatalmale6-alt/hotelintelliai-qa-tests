"""
Deep AI Concierge Test v7 - Correct collection IDs
Uses the actual KB collection names found on each hotel's KB page.
"""
import os
import re
import json
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "/var/lib/freelancer/projects/40298427/screenshots/v7"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Using correct collection IDs from KB pages
HOTELS = [
    {"name": "Imperial Mae Ping Hotel", "collection_id": "hotel_imperial_mae_ping", "chunks": 31},
    {"name": "The Oberoi Udaivilas", "collection_id": "oberoi_udaivilas", "chunks": 3},
    {"name": "The Riverie by Katathani", "collection_id": "hotel_riviera_cr", "chunks": 1},
]

HOTEL_QUESTIONS = {
    "hotel_imperial_mae_ping": [
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


def ask_question(page, collection_id, question):
    """Set correct HOTEL ID (collection), fill message, simulate."""
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

    # Input 0: HOTEL ID -> set to correct collection ID
    old_id = visible[0].input_value()
    visible[0].click(click_count=3)
    visible[0].fill(collection_id)
    page.wait_for_timeout(300)
    new_id = visible[0].input_value()
    print(f"    HOTEL ID: '{old_id}' -> '{new_id}'")

    # Input 1: GUEST IDENTIFIER
    if not visible[1].input_value():
        visible[1].fill("debug_guest_001")

    # Input 2: MESSAGE
    visible[2].click(click_count=3)
    visible[2].fill(question)
    page.wait_for_timeout(500)
    print(f"    MESSAGE: '{visible[2].input_value()[:50]}'")

    # Click Simulate
    sim_btn = page.locator('button:has-text("Simulate")')
    if sim_btn.count() == 0 or sim_btn.first.get_attribute('disabled') is not None:
        print(f"    Simulate button disabled/missing")
        return None

    sim_btn.first.click()
    print(f"    Simulating... (waiting 15s)")
    page.wait_for_timeout(15000)

    body = page.locator('body').inner_text()
    return extract_response(body)


def extract_response(body):
    lines = body.split('\n')
    response = ""
    intent = ""
    elapsed = ""
    escalate = ""

    # Find AGENT RESPONSE section
    capture = False
    for line in lines:
        s = line.strip()
        if 'AGENT RESPONSE' in s.upper():
            capture = True
            continue
        if capture:
            u = s.upper()
            if any(kw in u for kw in ['INTENT', 'LANGUAGE', 'ELAPSED', 'ESCALAT']):
                capture = False
            elif s and len(s) > 1:
                response += s + " "

    # Extract metadata
    for i, line in enumerate(lines):
        s = line.strip()
        u = s.upper()
        if u == 'INTENT' and i + 1 < len(lines):
            intent = lines[i + 1].strip()
        elif 'INTENT' in u and ':' in s:
            intent = s.split(':', 1)[1].strip()
        if u == 'ELAPSED' and i + 1 < len(lines):
            elapsed = lines[i + 1].strip()
        elif 'ELAPSED' in u:
            m = re.findall(r'[\d.]+s', s)
            if m: elapsed = m[0]
        if u == 'ESCALATE' and i + 1 < len(lines):
            escalate = lines[i + 1].strip()
        elif 'ESCALATE' in u:
            escalate = "YES" if "YES" in u else "NO" if "NO" in u else ""

    return {"response": response.strip(), "intent": intent, "elapsed": elapsed, "escalate": escalate}


def evaluate(resp):
    if not resp or len(resp) < 10:
        return "NO_RESPONSE", ["Empty/short"]
    lower = resp.lower()
    if any(p in lower for p in ["let me connect you", "best possible answer", "someone will be in touch"]):
        return "ESCALATION", ["KB missing info"]
    if any(p in lower for p in ["i don't have", "i don't know", "i'm not sure", "i cannot find", "no information"]):
        return "NO_INFO", ["AI lacks info"]
    if 'error' in lower or '⚠' in resp:
        return "ERROR", ["Error"]
    if len(resp) < 30:
        return "PARTIAL", ["Short"]
    return "GOOD", []


def main():
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 720})
        page = ctx.new_page()
        page.set_default_timeout(60000)

        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(2000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        print("Logged in\n")

        for hotel in HOTELS:
            cid = hotel["collection_id"]
            hname = hotel["name"]
            chunks = hotel["chunks"]
            questions = HOTEL_QUESTIONS.get(cid, HOTEL_QUESTIONS["hotel_imperial_mae_ping"])

            print(f"\n{'='*70}")
            print(f"TESTING: {hname} (collection: {cid}) - {chunks} chunks")
            print(f"{'='*70}")

            results[cid] = {"name": hname, "chunks": chunks, "questions": []}

            for qi, q in enumerate(questions):
                print(f"\n  Q{qi+1}: {q}")
                try:
                    navigate_to_simulator(page, hname)
                    screenshot(page, f"{cid}_q{qi+1}_before")

                    resp = ask_question(page, cid, q)
                    screenshot(page, f"{cid}_q{qi+1}_after")

                    if resp and resp.get("response"):
                        quality, issues = evaluate(resp["response"])
                        disp = resp["response"][:200]
                        print(f"  A: {disp}")
                        print(f"  Quality: {quality} | Escalate: {resp.get('escalate','')} | Intent: {resp.get('intent','')}")

                        results[cid]["questions"].append({
                            "question": q, "response": resp["response"][:500],
                            "intent": resp.get("intent",""), "elapsed": resp.get("elapsed",""),
                            "escalate": resp.get("escalate",""), "quality": quality, "issues": issues,
                        })
                    else:
                        print(f"  NO RESPONSE")
                        results[cid]["questions"].append({
                            "question": q, "response": "", "quality": "NO_RESPONSE", "issues": ["No response"],
                        })
                except Exception as e:
                    print(f"  ERROR: {e}")
                    results[cid]["questions"].append({
                        "question": q, "response": "", "quality": "ERROR", "issues": [str(e)[:150]],
                    })

        ctx.close()
        browser.close()

    # Save
    with open("/var/lib/freelancer/projects/40298427/reports/concierge_test_v7_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Summary
    print(f"\n\n{'='*70}")
    print("SUMMARY - AI CONCIERGE ACCURACY")
    print(f"{'='*70}")

    tg = te = tn = tt = 0
    for cid, data in results.items():
        qs = data.get("questions", [])
        counts = {}
        for q in qs:
            qual = q.get("quality", "?")
            counts[qual] = counts.get(qual, 0) + 1

        total = len(qs)
        good = counts.get("GOOD", 0)
        esc = counts.get("ESCALATION", 0)
        tg += good; te += esc; tt += total

        print(f"\n{data['name']} ({cid}) - {data['chunks']} chunks")
        print(f"  {good}/{total} GOOD ({100*good//total if total else 0}%)")
        for qual, c in sorted(counts.items()):
            print(f"    {qual}: {c}")
        for q in qs:
            if q["quality"] != "GOOD":
                print(f"  !! [{q['quality']}] \"{q['question']}\"")
                if q.get("response"):
                    print(f"     -> {q['response'][:100]}")

    print(f"\n{'='*70}")
    print(f"OVERALL: {tg}/{tt} GOOD ({100*tg//tt if tt else 0}%)")
    print(f"ESCALATIONS: {te}/{tt}")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
