"""
Deep AI Concierge Test v8 - Comprehensive testing for Oberoi & Riverie
Tests accuracy of AI responses against known hotel website facts.
Each question targets specific factual information from the hotel's website.
"""
import os
import re
import json
import time
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "/var/lib/freelancer/projects/40298427/screenshots/v8"
REPORT_DIR = "/var/lib/freelancer/projects/40298427/reports"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

HOTELS = [
    {
        "name": "The Oberoi Udaivilas",
        "collection_id": "oberoi_udaivilas",
        "chunks": 269,
    },
    {
        "name": "The Riverie by Katathani",
        "collection_id": "hotel_riviera_cr",
        "chunks": 162,
    },
]

# Detailed questions with expected facts for verification
HOTEL_QUESTIONS = {
    "oberoi_udaivilas": [
        {
            "q": "What types of rooms and suites do you offer?",
            "expected_keywords": ["kohinoor", "luxury suite", "premier", "pool", "garden", "city palace"],
            "category": "Rooms",
        },
        {
            "q": "What restaurants do you have and what cuisine do they serve?",
            "expected_keywords": ["suryamahal", "chandni", "mewar", "vineet", "bar", "promenade"],
            "category": "Dining",
        },
        {
            "q": "Tell me about the spa facilities",
            "expected_keywords": ["asmi", "oberoi", "spa"],
            "category": "Spa",
        },
        {
            "q": "Do you have a swimming pool?",
            "expected_keywords": ["pool", "temperature", "mughal"],
            "category": "Pool",
        },
        {
            "q": "What experiences and activities can I do at the hotel?",
            "expected_keywords": ["yoga", "painting", "cook", "dinner", "lakeside"],
            "category": "Activities",
        },
        {
            "q": "Where is the hotel located and how do I get there from the airport?",
            "expected_keywords": ["pichola", "udaipur", "airport", "maharana pratap"],
            "category": "Location",
        },
        {
            "q": "Can you host a wedding or conference at the hotel?",
            "expected_keywords": ["chandra mahal", "meeting", "cocktail"],
            "category": "Events",
        },
        {
            "q": "What awards has the hotel won recently?",
            "expected_keywords": ["conde nast", "michelin", "award"],
            "category": "Awards",
        },
        {
            "q": "What nearby attractions can I visit?",
            "expected_keywords": ["city palace", "jagdish", "kumbhalgarh", "ranakpur"],
            "category": "Attractions",
        },
        {
            "q": "Do you have a fitness center?",
            "expected_keywords": ["fitness", "gym", "cardiovascular", "weight"],
            "category": "Fitness",
        },
        {
            "q": "What is the phone number and email to contact the hotel?",
            "expected_keywords": ["294", "2433300", "oberoihotels"],
            "category": "Contact",
        },
        {
            "q": "How large is the hotel property?",
            "expected_keywords": ["121", "30 acre", "landscaped", "garden"],
            "category": "Property",
        },
        {
            "q": "Who is the general manager of the hotel?",
            "expected_keywords": ["amit kaul"],
            "category": "Management",
        },
        {
            "q": "Tell me about the Kohinoor Suite",
            "expected_keywords": ["kohinoor", "private pool", "suite"],
            "category": "Premium Room",
        },
        {
            "q": "Can I dine by the lake?",
            "expected_keywords": ["promenade", "lakeside", "al fresco"],
            "category": "Lakeside Dining",
        },
    ],
    "hotel_riviera_cr": [
        {
            "q": "What types of rooms do you have?",
            "expected_keywords": ["deluxe", "family suite", "riverie suite", "royal suite", "two-bedroom"],
            "category": "Rooms",
        },
        {
            "q": "Do you have a water park or swimming pool?",
            "expected_keywords": ["river splash", "water", "pool"],
            "category": "Pool/Water Park",
        },
        {
            "q": "Do you have facilities for children?",
            "expected_keywords": ["kid", "club", "children"],
            "category": "Kids",
        },
        {
            "q": "Can you host conferences or large events?",
            "expected_keywords": ["conference", "banquet", "700"],
            "category": "Events",
        },
        {
            "q": "Where is the hotel located?",
            "expected_keywords": ["chiang rai", "kraisorasit", "1129"],
            "category": "Location",
        },
        {
            "q": "What is the hotel phone number?",
            "expected_keywords": ["53 607999", "607999"],
            "category": "Contact",
        },
        {
            "q": "Do you have a spa?",
            "expected_keywords": ["spa"],
            "category": "Spa",
        },
        {
            "q": "What awards has the hotel won?",
            "expected_keywords": ["thailand tourism", "hall of fame", "sustainability", "excellence"],
            "category": "Awards",
        },
        {
            "q": "What is the cultural theme of the hotel?",
            "expected_keywords": ["lanna", "northern thai", "cultural"],
            "category": "Theme",
        },
        {
            "q": "Do you offer airport transfer?",
            "expected_keywords": ["airport", "transfer"],
            "category": "Transport",
        },
        {
            "q": "Tell me about the Deluxe River room",
            "expected_keywords": ["deluxe", "river"],
            "category": "Room Detail",
        },
        {
            "q": "What dining options are available?",
            "expected_keywords": ["restaurant", "dining"],
            "category": "Dining",
        },
        {
            "q": "Do you have a Royal Suite?",
            "expected_keywords": ["royal suite"],
            "category": "Premium Room",
        },
        {
            "q": "What is the email to book a room?",
            "expected_keywords": ["booking@theriverie", "theriverie"],
            "category": "Booking Contact",
        },
        {
            "q": "Is there a poolside terrace for events?",
            "expected_keywords": ["poolside", "terrace"],
            "category": "Event Venue",
        },
    ],
}


def screenshot(page, name):
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"{name}.png"))


def navigate_to_simulator(page, hotel_name):
    """Navigate to the Msg Simulator for a given hotel."""
    page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)

    # Click hotel
    clicked = False
    for sel in [f'text="{hotel_name}"', f'text={hotel_name}']:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=3000):
                el.click()
                clicked = True
                break
        except:
            continue

    if not clicked:
        # Try partial match
        words = hotel_name.split()[:3]
        partial = ' '.join(words)
        page.locator(f'text={partial}').first.click()

    page.wait_for_timeout(5000)

    # Click Debug in sidebar
    page.locator('text=Debug').first.click()
    page.wait_for_timeout(3000)

    # Click Msg Simulator tab
    sim_clicked = False
    for sel in ['button:has-text("Msg Simulator")', 'text=Msg Simulator']:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=3000):
                el.click()
                sim_clicked = True
                break
        except:
            continue

    if not sim_clicked:
        # Print what's on the debug page
        body = page.locator('body').inner_text()
        print(f"    Debug page text: {body[:500]}")

    page.wait_for_timeout(3000)


def ask_question(page, collection_id, question):
    """Fill in simulator form and get response."""
    inputs = page.locator('input')
    visible = []
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        if inp.is_visible():
            itype = (inp.get_attribute('type') or '').lower()
            if itype not in ('email', 'password', 'file', 'hidden', 'checkbox', 'radio', 'number'):
                visible.append(inp)

    if len(visible) < 3:
        print(f"    WARNING: Only {len(visible)} inputs found, need 3")
        # Try to find inputs with different approach
        all_inputs = page.locator('input:visible')
        print(f"    Total visible inputs: {all_inputs.count()}")
        return None

    # Input 0: HOTEL ID
    visible[0].click(click_count=3)
    visible[0].fill(collection_id)
    page.wait_for_timeout(300)

    # Input 1: GUEST IDENTIFIER
    if not visible[1].input_value():
        visible[1].fill("qa_tester_001")

    # Input 2: MESSAGE
    visible[2].click(click_count=3)
    page.wait_for_timeout(200)
    visible[2].fill(question)
    page.wait_for_timeout(500)

    # Verify message was set
    actual_msg = visible[2].input_value()
    if actual_msg != question:
        print(f"    WARNING: Message mismatch. Expected: '{question[:40]}' Got: '{actual_msg[:40]}'")
        visible[2].fill("")
        page.wait_for_timeout(200)
        visible[2].type(question, delay=20)
        page.wait_for_timeout(300)

    # Click Simulate
    sim_btn = page.locator('button:has-text("Simulate")')
    if sim_btn.count() == 0:
        print(f"    No Simulate button found")
        return None

    if not sim_btn.first.is_enabled():
        print(f"    Simulate button is disabled")
        return None

    sim_btn.first.click()
    print(f"    Simulating...")

    # Wait for response (up to 30s, checking every 5s)
    for wait in range(6):
        page.wait_for_timeout(5000)
        body = page.locator('body').inner_text()
        if 'AGENT RESPONSE' in body.upper():
            break

    body = page.locator('body').inner_text()
    return extract_response(body)


def extract_response(body):
    """Parse the simulator response."""
    lines = body.split('\n')
    response = ""
    intent = ""
    elapsed = ""
    escalate = ""
    language = ""

    # Find AGENT RESPONSE section
    capture = False
    for line in lines:
        s = line.strip()
        upper = s.upper()
        if 'AGENT RESPONSE' in upper:
            capture = True
            continue
        if capture:
            if any(kw in upper for kw in ['INTENT', 'LANGUAGE', 'ELAPSED', 'ESCALAT', 'HOTEL ID', 'GUEST']):
                capture = False
            elif s and len(s) > 1:
                response += s + " "

    # Extract metadata
    for i, line in enumerate(lines):
        s = line.strip()
        upper = s.upper()
        if 'INTENT' in upper and ':' in s:
            intent = s.split(':', 1)[1].strip()
        elif upper == 'INTENT' and i + 1 < len(lines):
            intent = lines[i + 1].strip()
        if 'ELAPSED' in upper:
            m = re.findall(r'[\d.]+\s*s', s)
            if m:
                elapsed = m[0]
            elif i + 1 < len(lines):
                elapsed = lines[i + 1].strip()
        if 'ESCALAT' in upper:
            if 'YES' in upper:
                escalate = "YES"
            elif 'NO' in upper:
                escalate = "NO"
            elif i + 1 < len(lines):
                escalate = lines[i + 1].strip()
        if 'LANGUAGE' in upper:
            if ':' in s:
                language = s.split(':', 1)[1].strip()
            elif i + 1 < len(lines):
                language = lines[i + 1].strip()

    return {
        "response": response.strip(),
        "intent": intent,
        "elapsed": elapsed,
        "escalate": escalate,
        "language": language,
    }


def evaluate_response(resp_text, expected_keywords):
    """Evaluate response quality and accuracy."""
    if not resp_text or len(resp_text) < 10:
        return "NO_RESPONSE", 0, ["Empty or very short response"]

    lower = resp_text.lower()

    # Check for escalation (means KB doesn't have the info)
    if any(p in lower for p in ["let me connect you", "best possible answer", "someone will be in touch",
                                  "i want to make sure you get"]):
        return "ESCALATION", 0, ["Response escalated - KB missing this information"]

    # Check for explicit "don't know"
    if any(p in lower for p in ["i don't have", "i don't know", "i'm not sure", "i cannot find",
                                  "no information available"]):
        return "NO_INFO", 0, ["AI couldn't find information in KB"]

    # Check for errors
    if 'error' in lower and len(resp_text) < 50:
        return "ERROR", 0, ["Error in response"]

    # Check keyword accuracy
    found = []
    missed = []
    for kw in expected_keywords:
        if kw.lower() in lower:
            found.append(kw)
        else:
            missed.append(kw)

    accuracy = len(found) / len(expected_keywords) * 100 if expected_keywords else 100

    if accuracy >= 60:
        quality = "GOOD"
    elif accuracy >= 30:
        quality = "PARTIAL"
    else:
        quality = "POOR"

    issues = []
    if missed:
        issues.append(f"Missing keywords: {', '.join(missed)}")
    if len(resp_text) < 30:
        issues.append("Response too short")
        quality = "PARTIAL" if quality == "GOOD" else quality

    return quality, accuracy, issues


def main():
    all_results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 720})
        page = ctx.new_page()
        page.set_default_timeout(30000)

        # Login
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(2000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        print("Logged in\n")

        for hotel in HOTELS:
            hname = hotel["name"]
            cid = hotel["collection_id"]
            chunks = hotel["chunks"]
            questions = HOTEL_QUESTIONS.get(cid, [])

            print(f"\n{'='*70}")
            print(f"HOTEL: {hname}")
            print(f"Collection: {cid} | KB Chunks: {chunks}")
            print(f"Questions: {len(questions)}")
            print(f"{'='*70}")

            hotel_results = {
                "name": hname,
                "collection_id": cid,
                "chunks": chunks,
                "questions": [],
                "summary": {},
            }

            for qi, qdata in enumerate(questions):
                q = qdata["q"]
                expected = qdata["expected_keywords"]
                category = qdata["category"]

                print(f"\n  Q{qi+1}/{len(questions)} [{category}]: {q}")

                try:
                    # Navigate fresh for each question to avoid stale state
                    navigate_to_simulator(page, hname)
                    screenshot(page, f"{cid}_q{qi+1}_before")

                    resp = ask_question(page, cid, q)
                    screenshot(page, f"{cid}_q{qi+1}_after")

                    if resp and resp.get("response"):
                        quality, accuracy, issues = evaluate_response(resp["response"], expected)
                        resp_preview = resp["response"][:250]

                        print(f"  A: {resp_preview}")
                        print(f"  Quality: {quality} | Accuracy: {accuracy:.0f}%")
                        if resp.get("escalate"):
                            print(f"  Escalate: {resp['escalate']}")
                        if issues:
                            for iss in issues:
                                print(f"  Issue: {iss}")

                        hotel_results["questions"].append({
                            "question": q,
                            "category": category,
                            "response": resp["response"][:1000],
                            "quality": quality,
                            "accuracy": accuracy,
                            "issues": issues,
                            "intent": resp.get("intent", ""),
                            "elapsed": resp.get("elapsed", ""),
                            "escalate": resp.get("escalate", ""),
                            "expected_keywords": expected,
                            "found_keywords": [kw for kw in expected if kw.lower() in resp["response"].lower()],
                            "missed_keywords": [kw for kw in expected if kw.lower() not in resp["response"].lower()],
                        })
                    else:
                        print(f"  NO RESPONSE RECEIVED")
                        hotel_results["questions"].append({
                            "question": q,
                            "category": category,
                            "response": "",
                            "quality": "NO_RESPONSE",
                            "accuracy": 0,
                            "issues": ["No response received from simulator"],
                        })

                except Exception as e:
                    print(f"  ERROR: {e}")
                    screenshot(page, f"{cid}_q{qi+1}_error")
                    hotel_results["questions"].append({
                        "question": q,
                        "category": category,
                        "response": "",
                        "quality": "ERROR",
                        "accuracy": 0,
                        "issues": [str(e)[:200]],
                    })

            # Compute summary
            qs = hotel_results["questions"]
            total = len(qs)
            good = sum(1 for q in qs if q["quality"] == "GOOD")
            partial = sum(1 for q in qs if q["quality"] == "PARTIAL")
            poor = sum(1 for q in qs if q["quality"] == "POOR")
            escalated = sum(1 for q in qs if q["quality"] == "ESCALATION")
            no_resp = sum(1 for q in qs if q["quality"] in ("NO_RESPONSE", "ERROR"))
            no_info = sum(1 for q in qs if q["quality"] == "NO_INFO")
            avg_acc = sum(q.get("accuracy", 0) for q in qs) / total if total else 0

            hotel_results["summary"] = {
                "total": total,
                "good": good,
                "partial": partial,
                "poor": poor,
                "escalated": escalated,
                "no_response": no_resp,
                "no_info": no_info,
                "avg_accuracy": round(avg_acc, 1),
                "good_rate": f"{100*good//total}%" if total else "0%",
            }

            all_results[cid] = hotel_results

        ctx.close()
        browser.close()

    # Save results
    results_path = os.path.join(REPORT_DIR, "concierge_test_v8_results.json")
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    # Print summary
    print(f"\n\n{'='*70}")
    print("DEEP CONCIERGE ACCURACY REPORT")
    print(f"{'='*70}")

    total_good = 0
    total_all = 0

    for cid, data in all_results.items():
        s = data["summary"]
        print(f"\n{data['name']} ({cid})")
        print(f"  KB: {data['chunks']} chunks")
        print(f"  Results: {s['good']}/{s['total']} GOOD ({s['good_rate']})")
        print(f"  Avg Accuracy: {s['avg_accuracy']}%")
        print(f"  Breakdown: GOOD={s['good']} PARTIAL={s['partial']} POOR={s['poor']} ESCALATED={s['escalated']} NO_RESPONSE={s['no_response']} NO_INFO={s['no_info']}")

        total_good += s["good"]
        total_all += s["total"]

        # Show problem questions
        for q in data["questions"]:
            if q["quality"] not in ("GOOD",):
                print(f"  !! [{q['quality']}] [{q.get('category','')}] \"{q['question']}\"")
                if q.get("issues"):
                    for iss in q["issues"]:
                        print(f"       {iss}")
                if q.get("response"):
                    print(f"       Response: {q['response'][:150]}")

    print(f"\n{'='*70}")
    overall_rate = f"{100*total_good//total_all}%" if total_all else "0%"
    print(f"OVERALL: {total_good}/{total_all} GOOD ({overall_rate})")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
