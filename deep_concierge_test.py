"""
Deep AI Concierge Testing — All Hotels
Tests the AI concierge responses against real hotel website content.
For each hotel: checks KB, runs questions via Msg Simulator, verifies accuracy.
"""
import os
import json
import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://onboarding.hotelintelliai.com"
DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "screenshots"

# All hotels discovered in the system
HOTELS = [
    {
        "name": "The Heritage Chiang Rai Hotel and Convention",
        "id": "heritage_chiangrai",
        "channels": ["whatsapp", "line", "web", "telegram"],
    },
    {
        "name": "Grand Vista Chiangrai Hotel",
        "id": "grand_vista_chiangrai",
        "channels": ["whatsapp", "line", "email"],
    },
    {
        "name": "Imperial Mae Ping Hotel",
        "id": "imperial_mae_ping",
        "channels": ["whatsapp", "line", "web"],
    },
    {
        "name": "The Oberoi Udaivilas",
        "id": "oberoi_udaivilas",
        "channels": ["web"],
    },
    {
        "name": "le Patte",
        "id": "lePatte",
        "channels": ["whatsapp", "telegram", "line", "email", "web"],
    },
    {
        "name": "The Riverie by Katathani",
        "id": "hotel_riviera_cr",
        "channels": ["whatsapp", "telegram", "line", "email"],
    },
]

# Questions to ask each hotel's AI concierge
COMMON_QUESTIONS = [
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


def main():
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # ===== PHASE 1: Check KB stats for all hotels =====
        print("=" * 70)
        print("PHASE 1: KB STATUS CHECK FOR ALL HOTELS")
        print("=" * 70)

        context1 = browser.new_context(viewport={"width": 1280, "height": 720})
        page1 = context1.new_page()
        page1.set_default_timeout(30000)

        # Login to onboarding
        page1.goto(BASE_URL, wait_until="networkidle", timeout=60000)
        page1.locator('input[type="email"]').fill(EMAIL)
        page1.locator('input[type="password"]').fill(PASSWORD)
        page1.locator('button').nth(1).click()
        page1.wait_for_timeout(5000)
        print("Logged in to onboarding portal\n")

        for hotel in HOTELS:
            hid = hotel["id"]
            print(f"\n--- {hotel['name']} ({hid}) ---")

            page1.goto(f"{BASE_URL}/hotel/{hid}/kb", wait_until="networkidle", timeout=30000)
            page1.wait_for_timeout(3000)

            body = page1.locator('body').inner_text()
            screenshot(page1, f"H_{hid}_kb")

            # Parse KB stats
            lines = body.split('\n')
            kb_info = {"chunks": 0, "documents": 0, "version": 0, "docs_list": []}

            for idx, line in enumerate(lines):
                line = line.strip()
                if 'TOTAL CHUNKS' in line and idx + 1 < len(lines):
                    try:
                        kb_info["chunks"] = int(lines[idx + 1].strip())
                    except ValueError:
                        pass
                elif 'DOCUMENTS' == line and idx + 1 < len(lines):
                    try:
                        kb_info["documents"] = int(lines[idx + 1].strip())
                    except ValueError:
                        pass
                elif 'KB VERSION' in line and idx + 1 < len(lines):
                    try:
                        kb_info["version"] = int(lines[idx + 1].strip())
                    except ValueError:
                        pass
                elif 'chunks' in line and '·' in line:
                    kb_info["docs_list"].append(line)

            hotel["kb"] = kb_info
            print(f"  Chunks: {kb_info['chunks']}, Documents: {kb_info['documents']}, Version: {kb_info['version']}")
            print(f"  Document list:")
            for doc in kb_info["docs_list"]:
                print(f"    {doc}")

            results[hid] = {
                "name": hotel["name"],
                "kb": kb_info,
                "questions": [],
            }

        context1.close()

        # ===== PHASE 2: Test AI Concierge for each hotel =====
        print("\n" + "=" * 70)
        print("PHASE 2: AI CONCIERGE TESTING VIA MSG SIMULATOR")
        print("=" * 70)

        context2 = browser.new_context(viewport={"width": 1280, "height": 720})
        page2 = context2.new_page()
        page2.set_default_timeout(60000)

        # Login to dashboard
        page2.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page2.locator('input[type="email"]').fill(EMAIL)
        page2.locator('input[type="password"]').fill(PASSWORD)
        page2.locator('button[type="submit"]').click()
        page2.wait_for_timeout(5000)
        print("Logged in to dashboard\n")

        for hotel in HOTELS:
            hid = hotel["id"]
            kb_chunks = hotel.get("kb", {}).get("chunks", 0)

            print(f"\n{'='*60}")
            print(f"TESTING: {hotel['name']} ({hid})")
            print(f"KB: {kb_chunks} chunks")
            print(f"{'='*60}")

            if kb_chunks == 0:
                print(f"  SKIP — No KB content (0 chunks)")
                results[hid]["skip_reason"] = "No KB content"
                continue

            # Navigate to this hotel's command center
            page2.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
            page2.wait_for_timeout(3000)

            # Click on this hotel
            try:
                hotel_link = page2.locator(f'text={hotel["name"]}')
                if hotel_link.count() > 0:
                    hotel_link.first.click()
                    page2.wait_for_timeout(5000)
                else:
                    # Try partial name
                    short_name = hotel["name"].split()[0:3]
                    for part in short_name:
                        link = page2.locator(f'text={part}')
                        if link.count() > 0:
                            link.first.click()
                            page2.wait_for_timeout(5000)
                            break
            except Exception as e:
                print(f"  ERROR navigating to hotel: {e}")
                results[hid]["skip_reason"] = f"Navigation error: {e}"
                continue

            # Verify we're on the hotel's command center
            current_url = page2.url
            print(f"  URL: {current_url}")

            # Go to Debug > Msg Simulator
            try:
                page2.locator('text=Debug').first.click()
                page2.wait_for_timeout(2000)
                page2.locator('button:has-text("Msg Simulator")').click()
                page2.wait_for_timeout(2000)
            except Exception as e:
                print(f"  ERROR navigating to Msg Simulator: {e}")
                results[hid]["skip_reason"] = f"Debug nav error: {e}"
                continue

            screenshot(page2, f"H_{hid}_simulator")

            # Test each question
            for qi, question in enumerate(COMMON_QUESTIONS):
                print(f"\n  Q{qi+1}: {question}")

                try:
                    # Find the message input
                    inputs = page2.locator('input')
                    msg_input = None
                    for i in range(inputs.count()):
                        inp = inputs.nth(i)
                        if inp.is_visible():
                            placeholder = (inp.get_attribute('placeholder') or '').lower()
                            inp_type = (inp.get_attribute('type') or '').lower()
                            if inp_type not in ('email', 'password', 'file', 'hidden', 'number'):
                                if 'message' in placeholder or 'guest' in placeholder or 'type' in placeholder or 'ask' in placeholder or 'query' in placeholder or not placeholder:
                                    msg_input = inp
                                    break

                    if not msg_input:
                        # Fallback: use the last visible text input
                        for i in range(inputs.count() - 1, -1, -1):
                            inp = inputs.nth(i)
                            if inp.is_visible():
                                inp_type = (inp.get_attribute('type') or '').lower()
                                if inp_type not in ('email', 'password', 'file', 'hidden', 'number'):
                                    msg_input = inp
                                    break

                    if msg_input:
                        msg_input.fill("")
                        msg_input.fill(question)

                        # Click Simulate button
                        sim_btn = page2.locator('button:has-text("Simulate")')
                        sim_btn.first.click()
                        page2.wait_for_timeout(20000)  # AI response may take time

                        body = page2.locator('body').inner_text()
                        screenshot(page2, f"H_{hid}_q{qi+1}")

                        # Extract the AI response
                        response_text = ""
                        intent = ""
                        elapsed = ""
                        language = ""

                        lines = body.split('\n')
                        capture_response = False
                        for line in lines:
                            line = line.strip()
                            if 'AGENT RESPONSE' in line:
                                capture_response = True
                                continue
                            if capture_response and line and 'INTENT' not in line and 'ELAPSED' not in line and 'LANGUAGE' not in line and 'CONFIDENCE' not in line:
                                if not line.startswith('↻') and not line.startswith('●'):
                                    response_text += line + " "
                            if 'INTENT' in line:
                                capture_response = False
                                # Get intent value from next line or same line
                                parts = line.split(':')
                                if len(parts) > 1:
                                    intent = parts[1].strip()
                            if 'ELAPSED' in line:
                                parts = line.split(':')
                                if len(parts) > 1:
                                    elapsed = parts[1].strip()

                        response_text = response_text.strip()

                        if response_text:
                            # Truncate for display
                            display_resp = response_text[:200] + "..." if len(response_text) > 200 else response_text
                            print(f"  A: {display_resp}")
                            if intent:
                                print(f"  Intent: {intent}")
                            if elapsed:
                                print(f"  Elapsed: {elapsed}")

                            # Evaluate response quality
                            quality = "GOOD"
                            issues = []

                            # Check for empty/error responses
                            if len(response_text) < 20:
                                quality = "BAD"
                                issues.append("Response too short")
                            if 'error' in response_text.lower() or '⚠' in response_text:
                                quality = "ERROR"
                                issues.append("Error in response")
                            if "i don't" in response_text.lower() and "know" in response_text.lower():
                                quality = "NO_INFO"
                                issues.append("AI doesn't have the information")
                            if "i'm not sure" in response_text.lower() or "i cannot" in response_text.lower():
                                quality = "UNCERTAIN"
                                issues.append("AI is uncertain")
                            if "sorry" in response_text.lower() and "don't have" in response_text.lower():
                                quality = "NO_INFO"
                                issues.append("Information not in KB")

                            print(f"  Quality: {quality}")
                            if issues:
                                print(f"  Issues: {', '.join(issues)}")
                        else:
                            quality = "NO_RESPONSE"
                            issues = ["No agent response found"]
                            print(f"  NO RESPONSE FOUND")

                            # Check for errors in body
                            if 'error' in body.lower() or '⚠' in body:
                                for line in lines:
                                    if 'error' in line.lower() or '⚠' in line:
                                        print(f"  Error: {line.strip()}")

                        results[hid]["questions"].append({
                            "question": question,
                            "response": response_text[:500],
                            "intent": intent,
                            "elapsed": elapsed,
                            "quality": quality,
                            "issues": issues if issues else [],
                        })

                    else:
                        print(f"  ERROR: Could not find message input")
                        results[hid]["questions"].append({
                            "question": question,
                            "response": "",
                            "quality": "ERROR",
                            "issues": ["Could not find message input"],
                        })

                except Exception as e:
                    print(f"  ERROR: {e}")
                    results[hid]["questions"].append({
                        "question": question,
                        "response": "",
                        "quality": "ERROR",
                        "issues": [str(e)],
                    })

        context2.close()
        browser.close()

    # ===== Save results =====
    results_path = os.path.join("reports", "concierge_test_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    # ===== Print Summary =====
    print("\n" + "=" * 70)
    print("SUMMARY — AI CONCIERGE ACCURACY BY HOTEL")
    print("=" * 70)

    for hid, data in results.items():
        name = data["name"]
        kb = data.get("kb", {})
        questions = data.get("questions", [])
        skip = data.get("skip_reason", "")

        print(f"\n{name} ({hid})")
        print(f"  KB: {kb.get('chunks', 0)} chunks, {kb.get('documents', 0)} docs")

        if skip:
            print(f"  SKIPPED: {skip}")
            continue

        if not questions:
            print(f"  No questions tested")
            continue

        # Count quality
        quality_counts = {}
        for q in questions:
            qual = q.get("quality", "UNKNOWN")
            quality_counts[qual] = quality_counts.get(qual, 0) + 1

        total = len(questions)
        good = quality_counts.get("GOOD", 0)
        print(f"  Tested: {total} questions")
        print(f"  Results: {good}/{total} GOOD ({100*good//total}%)")
        for qual, count in sorted(quality_counts.items()):
            if qual != "GOOD":
                print(f"    {qual}: {count}")

        # List problematic questions
        for q in questions:
            if q.get("quality") != "GOOD":
                print(f"  !! {q['quality']}: \"{q['question']}\"")
                if q.get("issues"):
                    print(f"     Issues: {', '.join(q['issues'])}")


if __name__ == "__main__":
    main()
