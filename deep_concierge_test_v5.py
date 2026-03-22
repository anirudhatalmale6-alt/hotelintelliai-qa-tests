"""
Deep AI Concierge Testing v5 — All 6 Hotels via API
Uses POST https://api.hotelintelliai.com/admin/test/message for ALL hotels.
This avoids UI navigation issues (blank dashboards, wrong hotel ID in input).
"""
import os
import json
import time
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
API_URL = "https://api.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "screenshots/v5"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

HOTELS = [
    {
        "name": "The Heritage Chiang Rai Hotel and Convention",
        "id": "heritage_chiangrai",
        "website": "heritagechiangrai.com",
        "questions": [
            ("How many rooms does the hotel have?", ["321"]),
            ("What room types are available?", ["deluxe", "executive", "suite", "premier"]),
            ("Do you have meeting or convention facilities?", ["ballroom", "meeting"]),
            ("What restaurants do you have?", ["restaurant", "dining"]),
            ("Do you have a swimming pool?", ["pool"]),
            ("Where is the hotel located?", ["chiang rai"]),
            ("Do you have a fitness center?", ["fitness", "gym"]),
            ("Is there a spa?", ["spa"]),
            ("What are nearby attractions?", ["white temple", "night bazaar", "clock tower"]),
            ("Do you have WiFi?", ["wifi", "free"]),
        ]
    },
    {
        "name": "Grand Vista Chiangrai Hotel",
        "id": "grand_vista_chiangrai",
        "website": "grandvistachiangrai.com",
        "questions": [
            ("What room types do you have?", ["superior", "deluxe", "suite"]),
            ("Do you have a swimming pool?", ["pool"]),
            ("Do you have a spa?", ["spa", "massage"]),
            ("What dining options are available?", ["restaurant", "bar"]),
            ("Do you have a fitness center?", ["fitness", "gym"]),
            ("Is there WiFi?", ["wifi"]),
            ("Is there parking?", ["parking"]),
            ("Where is the hotel located?", ["chiang rai"]),
            ("How far is the airport?", ["airport"]),
            ("What nearby attractions are there?", ["night bazaar", "clock tower"]),
        ]
    },
    {
        "name": "Imperial Mae Ping Hotel",
        "id": "imperial_mae_ping",
        "website": "imperialmaeping.com",
        "questions": [
            ("What time is check-in and check-out?", ["check-in", "check-out"]),
            ("What restaurants do you have?", ["restaurant", "dining"]),
            ("Do you have a spa?", ["spa", "massage"]),
            ("Do you have a swimming pool?", ["pool"]),
            ("Is there a fitness center?", ["fitness", "gym"]),
            ("Where is the hotel located?", ["chiang mai"]),
            ("Do you have parking?", ["parking"]),
            ("Do you have meeting rooms?", ["meeting", "conference", "banquet"]),
            ("Do you offer airport transfer?", ["airport", "transfer"]),
            ("Do you have WiFi?", ["wifi"]),
        ]
    },
    {
        "name": "The Oberoi Udaivilas",
        "id": "oberoi_udaivilas",
        "website": "oberoihotels.com",
        "questions": [
            ("What types of rooms do you have?", ["suite", "premier", "luxury"]),
            ("Do you have a swimming pool?", ["pool"]),
            ("What dining options are available?", ["restaurant", "dining"]),
            ("Do you have a spa?", ["spa"]),
            ("What experiences do you offer?", ["yoga", "painting", "experience"]),
            ("Where is the hotel located?", ["udaipur", "lake"]),
            ("Do you have meeting rooms?", ["meeting", "conference"]),
            ("What nearby attractions can I visit?", ["palace", "temple"]),
            ("Do you have a fitness center?", ["fitness", "gym"]),
            ("Do you offer airport transfer?", ["airport", "transfer"]),
        ]
    },
    {
        "name": "le Patte",
        "id": "lePatte",
        "website": "lepattachiangrai.com",
        "questions": [
            ("What room types are available?", ["superior", "deluxe", "suite"]),
            ("How big are the rooms?", ["32", "52", "sqm"]),
            ("Do you have a swimming pool?", ["pool", "salt"]),
            ("Is there a gym or fitness center?", ["gym", "gorilla", "fitness"]),
            ("Do you have WiFi?", ["wifi"]),
            ("Where is the hotel located?", ["chiang rai"]),
            ("What is nearby the hotel?", ["night bazaar", "clock tower"]),
            ("Do you have a restaurant?", ["restaurant"]),
            ("Is there parking available?", ["parking"]),
            ("How far is the airport?", ["7 km", "airport", "mae fah luang"]),
        ]
    },
    {
        "name": "The Riverie by Katathani",
        "id": "hotel_riviera_cr",
        "website": "theriverie.com",
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


def evaluate_accuracy(response, expected_keywords):
    if not response or len(response) < 10:
        return "NO_RESPONSE", 0, []

    response_lower = response.lower()

    if "let me connect you with" in response_lower or "best possible answer" in response_lower:
        return "ESCALATED", 0, []

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

    matched = [kw for kw in expected_keywords if kw.lower() in response_lower]
    match_pct = len(matched) / len(expected_keywords) * 100 if expected_keywords else 0

    if match_pct >= 50:
        return "ACCURATE", match_pct, matched
    elif match_pct > 0:
        return "PARTIAL", match_pct, matched
    elif len(response) > 50:
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
        page.goto(DASHBOARD_URL, timeout=60000)
        page.wait_for_timeout(5000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(10000)

        # Navigate to any working hotel to get auth context
        body = page.locator('body').inner_text()
        if 'Heritage' not in body:
            for _ in range(10):
                page.wait_for_timeout(2000)
                body = page.locator('body').inner_text()
                if 'Heritage' in body:
                    break

        page.locator('text=Heritage').first.click()
        page.wait_for_timeout(8000)
        print("Logged in and on Heritage dashboard\n")

        # Get auth token
        auth_token = page.evaluate("""() => {
            // Look in cookies and localStorage
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                const val = localStorage.getItem(key);
                if (val && val.startsWith('eyJ')) return val;
            }
            return null;
        }""")

        # Get KB stats for all hotels
        print("KB Stats:")
        for hotel in HOTELS:
            hid = hotel["id"]
            r = page.evaluate(f"""async () => {{
                try {{
                    const resp = await fetch('{API_URL}/kb/stats/{hid}', {{credentials: 'include'}});
                    return await resp.json();
                }} catch(e) {{ return {{error: e.message}}; }}
            }}""")
            chunks = r.get('total_chunks', 'N/A')
            print(f"  {hid}: {chunks} chunks")

        print()

        # Test each hotel via API
        for hotel in HOTELS:
            hid = hotel["id"]
            hname = hotel["name"]

            print(f"\n{'='*70}")
            print(f"TESTING: {hname} (ID: {hid})")
            print(f"{'='*70}")

            hotel_results = {
                "name": hname,
                "id": hid,
                "website": hotel["website"],
                "questions": [],
            }

            for qi, (question, expected_kw) in enumerate(hotel["questions"]):
                print(f"\n  Q{qi+1}: {question}")

                escaped_q = question.replace("\\", "\\\\").replace('"', '\\"')

                result = page.evaluate(f"""async () => {{
                    try {{
                        const resp = await fetch('{API_URL}/admin/test/message', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                                'x-hotel-id': '{hid}'
                            }},
                            credentials: 'include',
                            body: JSON.stringify({{
                                hotel_id: '{hid}',
                                message: "{escaped_q}",
                                guest_identifier: 'qa_test_{qi+1}',
                                guest_name: 'QA Tester'
                            }})
                        }});
                        const data = await resp.json();
                        return {{ status: resp.status, data: data }};
                    }} catch(e) {{
                        return {{ error: e.message }};
                    }}
                }}""")

                response = ""
                intent = ""
                elapsed_ms = ""

                if result.get('error'):
                    print(f"    ERROR: {result['error']}")
                elif result.get('status') == 200:
                    data = result.get('data', {})
                    response = data.get('response', data.get('reply', data.get('message', '')))
                    intent = data.get('intent', '')
                    elapsed_ms = str(data.get('elapsed_ms', data.get('elapsed', '')))

                    if isinstance(response, dict):
                        response = json.dumps(response)
                else:
                    print(f"    HTTP {result.get('status')}: {json.dumps(result.get('data', ''))[:200]}")
                    # Try to extract error message
                    data = result.get('data', {})
                    if isinstance(data, dict):
                        response = data.get('detail', data.get('error', ''))

                accuracy, match_pct, matched = evaluate_accuracy(response, expected_kw)

                if response:
                    display = response[:200] + "..." if len(response) > 200 else response
                    print(f"    A: {display}")
                    print(f"    [{accuracy}] Keywords: {len(matched)}/{len(expected_kw)} | Intent: {intent}")
                else:
                    print(f"    NO RESPONSE")

                hotel_results["questions"].append({
                    "q_num": qi + 1,
                    "question": question,
                    "expected_keywords": expected_kw,
                    "response": response[:1000] if response else "",
                    "intent": intent,
                    "elapsed_ms": elapsed_ms,
                    "accuracy": accuracy,
                    "match_pct": round(match_pct, 1),
                    "matched_kw": matched,
                })

                # Small delay to avoid rate limiting
                time.sleep(2)

            # Summary
            questions = hotel_results["questions"]
            total = len(questions)
            accurate = sum(1 for q in questions if q["accuracy"] == "ACCURATE")
            partial = sum(1 for q in questions if q["accuracy"] == "PARTIAL")
            no_info = sum(1 for q in questions if q["accuracy"] == "NO_INFO")
            escalated = sum(1 for q in questions if q["accuracy"] == "ESCALATED")
            unverified = sum(1 for q in questions if q["accuracy"] == "UNVERIFIED")
            errors = sum(1 for q in questions if q["accuracy"] in ("ERROR", "NO_RESPONSE", "WEAK"))

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

            print(f"\n  >> {hname}: {accurate} accurate, {partial} partial, {escalated} escalated, {no_info} no_info")
            print(f"  >> Accuracy: {hotel_results['summary']['accuracy_pct']}%")

            all_results[hid] = hotel_results

        context.close()
        browser.close()

    # Save results
    os.makedirs("reports", exist_ok=True)
    with open("reports/concierge_test_results_v5.json", "w") as f:
        json.dump(all_results, f, indent=2)

    # Print final summary
    print(f"\n\n{'='*70}")
    print("FINAL SUMMARY — AI CONCIERGE ACCURACY")
    print(f"{'='*70}")

    total_all = 0
    answered_all = 0

    for hid, data in all_results.items():
        s = data.get("summary", {})
        total = s.get("total", 0)
        acc = s.get("accurate", 0)
        par = s.get("partial", 0)
        esc = s.get("escalated", 0)
        ni = s.get("no_info", 0)
        pct = s.get("accuracy_pct", 0)

        total_all += total
        answered_all += acc + par

        print(f"\n{data['name']}")
        print(f"  Accuracy: {pct}% ({acc} accurate, {par} partial / {total} questions)")
        if esc:
            print(f"  ESCALATED (KB missing): {esc} questions")
        if ni:
            print(f"  No Info (AI lacks data): {ni} questions")

        for q in data.get("questions", []):
            if q["accuracy"] in ("ESCALATED", "NO_INFO", "ERROR", "NO_RESPONSE"):
                print(f"    !! [{q['accuracy']}] Q{q['q_num']}: {q['question']}")

    overall = round(answered_all / total_all * 100, 1) if total_all else 0
    print(f"\n{'='*70}")
    print(f"OVERALL: {answered_all}/{total_all} answered correctly ({overall}%)")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
