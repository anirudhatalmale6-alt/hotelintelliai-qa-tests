"""
Final comprehensive dashboard test v3 for Riverie and Le Patte.
Uses subdomain navigation pattern and Debug > Msg Simulator tab.
"""
import json
import time
import os
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "/var/lib/freelancer/projects/40298427/screenshots/final_v3"
RESULTS_FILE = "/var/lib/freelancer/projects/40298427/reports/final_dashboard_results_v3.json"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Hotel subdomain URLs discovered from v2 test
HOTELS = [
    {"name": "Riverie", "id": "hotel_riviera_cr", "subdomain": "hotel_riviera_cr"},
    {"name": "Le Patte", "id": "lePatte", "subdomain": "lePatte"},
]

# Sidebar sections to test (from screenshot)
SIDEBAR_SECTIONS = ["Overview", "Conversations", "Guests", "Escalations", "Channels", "Knowledge Base", "Debug"]

# Debug sub-tabs (from screenshot)
DEBUG_TABS = ["Health Check", "RAG Tester", "Msg Simulator", "DB Stats", "Guest Lookup"]

CONCIERGE_QUESTIONS = {
    "Riverie": [
        "What are the check-in and check-out times?",
        "What types of rooms do you offer?",
        "Do you have a swimming pool?",
        "What dining options are available at the hotel?",
        "Do you offer airport transfer services?",
        "What spa treatments are available?",
        "Is breakfast included in the room rate?",
        "Do you have meeting rooms or event spaces?",
        "What is your cancellation policy?",
        "Is there free WiFi available?",
        "Do you have parking facilities?",
        "What activities or excursions can you arrange?",
        "Are pets allowed at the hotel?",
        "What are the room rates or pricing?",
        "Do you have a fitness center or gym?",
    ],
    "Le Patte": [
        "What are the check-in and check-out times?",
        "What room types do you have?",
        "Do you have a restaurant on site?",
        "Is there a swimming pool?",
        "What spa services do you offer?",
        "Do you provide airport shuttle service?",
        "Is breakfast included?",
        "What are your room rates?",
        "Do you have conference or meeting facilities?",
        "Is there WiFi in the rooms?",
        "What is the cancellation policy?",
        "Do you have a bar or lounge?",
        "What activities are available nearby?",
        "Do you offer laundry service?",
        "Is there parking available?",
    ],
}

def ss(page, name):
    path = f"{SCREENSHOT_DIR}/{name}.png"
    page.screenshot(path=path)
    return path

def login(page):
    page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    if page.locator('input[type="email"]').count() > 0:
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        submit = page.locator('button[type="submit"]')
        if submit.count() > 0:
            submit.click()
        else:
            page.locator('button').filter(has_text="Sign").first.click()
        page.wait_for_timeout(5000)
    ss(page, "00_logged_in")
    print("Logged in successfully")

def goto_hotel(page, hotel):
    """Navigate to hotel via subdomain."""
    url = f"https://{hotel['subdomain']}.hotelintelliai.com/"
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)

    # Check if redirected to login
    if page.locator('input[type="email"]').count() > 0:
        login(page)
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

    current_url = page.url
    print(f"  Navigated to: {current_url}")
    ss(page, f"{hotel['name']}_home")
    return True

def click_sidebar(page, section_name, hotel_name):
    """Click a sidebar item."""
    for sel in [
        f'nav >> text="{section_name}"',
        f'aside >> text="{section_name}"',
        f'a:has-text("{section_name}")',
        f'text="{section_name}"',
    ]:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=2000):
                el.click()
                page.wait_for_timeout(3000)
                return True
        except:
            continue
    return False

def click_debug_tab(page, tab_name, hotel_name):
    """Click a tab within the Debug section."""
    for sel in [
        f'button:has-text("{tab_name}")',
        f'text="{tab_name}"',
        f'[role="tab"]:has-text("{tab_name}")',
    ]:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=2000):
                el.click()
                page.wait_for_timeout(3000)
                return True
        except:
            continue
    return False

def test_all_sections(page, hotel):
    """Test all sidebar sections and capture content."""
    results = {}

    for section in SIDEBAR_SECTIONS:
        print(f"    Testing: {section}")
        goto_hotel(page, hotel)

        if click_sidebar(page, section, hotel["name"]):
            page.wait_for_timeout(2000)
            safe = section.replace(" ", "_")
            ss(page, f"{hotel['name']}_{safe}")

            body = page.inner_text("body", timeout=5000)

            # Check for errors
            has_error = False
            error_detail = ""
            body_lower = body.lower()

            if "error" in body_lower[:200] and "escalation" not in body_lower[:200]:
                has_error = True
                error_detail = "Error detected in page header"
            elif len(body) < 50:
                has_error = True
                error_detail = "Page appears empty"

            results[section] = {
                "accessible": True,
                "content_length": len(body),
                "has_error": has_error,
                "error_detail": error_detail,
                "url": page.url
            }

            # Section-specific checks
            if section == "Overview":
                # Check for stats
                for stat in ["conversation", "guest", "channel", "escalation"]:
                    if stat in body_lower:
                        results[section][f"has_{stat}"] = True

            elif section == "Conversations":
                # Check for conversation list
                results[section]["has_list"] = "conversation" in body_lower or "message" in body_lower

            elif section == "Guests":
                results[section]["has_list"] = "guest" in body_lower

            elif section == "Escalations":
                # Count escalations
                esc_match = re.findall(r'escalat', body_lower)
                results[section]["escalation_mentions"] = len(esc_match)

            elif section == "Channels":
                for ch in ["whatsapp", "line", "web", "email", "telegram", "sms"]:
                    if ch in body_lower:
                        results[section][f"channel_{ch}"] = True

            elif section == "Knowledge Base":
                chunks_match = re.search(r'(\d+)\s*chunks?', body, re.IGNORECASE)
                if chunks_match:
                    results[section]["chunks"] = int(chunks_match.group(1))

                # Test each KB tab
                for tab in ["File", "URL", "FAQ"]:
                    try:
                        tab_btn = page.locator(f'button:has-text("{tab}")').first
                        if tab_btn.is_visible(timeout=2000):
                            tab_btn.click()
                            page.wait_for_timeout(2000)
                            ss(page, f"{hotel['name']}_KB_{tab}")
                            tab_body = page.inner_text("body", timeout=5000)
                            results[section][f"tab_{tab}"] = "accessible"
                    except:
                        results[section][f"tab_{tab}"] = "error"

            elif section == "Debug":
                # Test each debug tab
                for tab in DEBUG_TABS:
                    if click_debug_tab(page, tab, hotel["name"]):
                        page.wait_for_timeout(2000)
                        safe_tab = tab.replace(" ", "_")
                        ss(page, f"{hotel['name']}_Debug_{safe_tab}")
                        tab_body = page.inner_text("body", timeout=5000)
                        results[section][f"tab_{tab}"] = {
                            "accessible": True,
                            "content_length": len(tab_body)
                        }
                    else:
                        results[section][f"tab_{tab}"] = {"accessible": False}

            print(f"      OK - {len(body)} chars" + (f" ERROR: {error_detail}" if has_error else ""))
        else:
            results[section] = {"accessible": False}
            print(f"      FAILED - could not click")

    return results

def test_concierge(page, hotel, questions):
    """Test Msg Simulator with 15 questions."""
    results = {"questions": [], "issues": [], "stats": {}}

    # Navigate to Debug > Msg Simulator
    goto_hotel(page, hotel)
    if not click_sidebar(page, "Debug", hotel["name"]):
        results["issues"].append("Could not navigate to Debug section")
        return results

    page.wait_for_timeout(2000)

    if not click_debug_tab(page, "Msg Simulator", hotel["name"]):
        results["issues"].append("Could not find Msg Simulator tab")
        return results

    page.wait_for_timeout(2000)
    ss(page, f"{hotel['name']}_MsgSimulator_ready")

    # Find inputs - the form has HOTEL ID, GUEST IDENTIFIER, MESSAGE
    all_inputs = page.locator('input:visible, textarea:visible').all()
    print(f"  Found {len(all_inputs)} input fields")

    # Identify each input by placeholder/label
    msg_input = None
    hotel_input = None
    guest_input = None

    for inp in all_inputs:
        try:
            placeholder = (inp.get_attribute("placeholder") or "").lower()
            value = inp.input_value()
            name = (inp.get_attribute("name") or "").lower()

            if "message" in placeholder or "spa" in placeholder or "e.g." in placeholder:
                msg_input = inp
                print(f"    MESSAGE input found (placeholder: {placeholder})")
            elif "hotel" in placeholder or "hotel" in name or hotel["id"] in value:
                hotel_input = inp
                print(f"    HOTEL ID input found (value: {value})")
            elif "guest" in placeholder or "guest" in name or "debug" in value.lower():
                guest_input = inp
                print(f"    GUEST input found (value: {value})")
        except:
            continue

    # Fallback: if 3+ inputs, msg is the last one
    if not msg_input and len(all_inputs) >= 3:
        msg_input = all_inputs[2]  # 3rd input = MESSAGE
        print(f"    Using 3rd input as MESSAGE (fallback)")
    elif not msg_input and len(all_inputs) >= 1:
        msg_input = all_inputs[-1]
        print(f"    Using last input as MESSAGE (fallback)")

    if not msg_input:
        results["issues"].append("Could not find message input")
        return results

    # Find Simulate button
    sim_btn = None
    for sel in ['button:has-text("Simulate")', 'button:has-text("Send")', 'button[type="submit"]']:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                sim_btn = btn
                print(f"    Simulate button found")
                break
        except:
            continue

    if not sim_btn:
        results["issues"].append("Could not find Simulate button")
        return results

    # Test each question
    escalation_count = 0
    relevant_count = 0
    error_count = 0
    prev_response = ""

    for idx, question in enumerate(questions):
        qnum = idx + 1
        print(f"\n  Q{qnum}: {question}")

        try:
            # Before each question, get the current page state to detect response changes
            body_before = page.inner_text("body", timeout=5000)

            # Clear and fill message
            msg_input.click(click_count=3)
            page.wait_for_timeout(300)
            msg_input.press("Backspace")
            page.wait_for_timeout(200)
            msg_input.fill("")
            page.wait_for_timeout(300)
            msg_input.fill(question)
            page.wait_for_timeout(500)

            # Verify input value
            filled = msg_input.input_value()
            if filled != question:
                print(f"    WARNING: Input mismatch - got '{filled[:50]}...'")
                # Try again with type
                msg_input.click(click_count=3)
                msg_input.type(question, delay=20)
                page.wait_for_timeout(300)

            # Click Simulate
            sim_btn.click()

            # Wait for response (AI might take a few seconds)
            page.wait_for_timeout(10000)

            ss(page, f"{hotel['name']}_q{qnum}")

            # Extract response
            body_after = page.inner_text("body", timeout=5000)
            response = extract_response(body_after)

            response_short = response[:300] if response else "(empty)"
            print(f"  A{qnum}: {response_short}")

            # Classify response
            resp_lower = response.lower()
            is_escalation = (
                "connect you with" in resp_lower or
                "best possible answer" in resp_lower or
                "i want to make sure" in resp_lower or
                "let me connect" in resp_lower or
                "reach out to" in resp_lower or
                "contact the hotel" in resp_lower
            )
            is_error = (not response or
                       response == "(could not extract)" or
                       "error" in resp_lower[:30])
            is_duplicate = (response == prev_response and prev_response and
                          len(prev_response) > 20)

            if is_escalation:
                escalation_count += 1
            elif not is_error:
                relevant_count += 1
            if is_error:
                error_count += 1

            q_result = {
                "q_num": qnum,
                "question": question,
                "response": response[:800],
                "classification": "ESCALATION" if is_escalation else ("ERROR" if is_error else "ANSWERED"),
                "is_duplicate": is_duplicate,
            }

            if is_escalation:
                results["issues"].append(
                    f"Q{qnum}: '{question}' -> ESCALATION (KB may not have this info)"
                )
            if is_duplicate:
                results["issues"].append(
                    f"Q{qnum}: '{question}' -> DUPLICATE response (same as Q{qnum-1})"
                )

            results["questions"].append(q_result)
            prev_response = response

        except Exception as e:
            error_count += 1
            err_msg = str(e)[:200]
            print(f"  ERROR: {err_msg}")
            results["questions"].append({
                "q_num": qnum,
                "question": question,
                "response": f"ERROR: {err_msg}",
                "classification": "ERROR"
            })

    results["stats"] = {
        "total": len(questions),
        "answered": relevant_count,
        "escalations": escalation_count,
        "errors": error_count,
        "accuracy_pct": round(relevant_count / len(questions) * 100, 1) if questions else 0
    }

    return results

def extract_response(body_text):
    """Extract AI response from page body."""
    # Look for AGENT RESPONSE section
    patterns = [
        r'(?:AGENT\s*RESPONSE|Agent\s*Response|agent_response)[:\s]*\n?(.*?)(?:\n\s*(?:HOTEL|Hotel|GUEST|Guest|MESSAGE|Message|SIMULATE|Simulate|DEBUG|Debug|Health|RAG|DB Stats|Guest Lookup)\b)',
        r'(?:AGENT\s*RESPONSE|Agent\s*Response)[:\s]*([\s\S]{10,500})',
    ]

    for pattern in patterns:
        match = re.search(pattern, body_text, re.DOTALL | re.IGNORECASE)
        if match:
            resp = match.group(1).strip()
            # Clean up newlines
            lines = [l.strip() for l in resp.split("\n") if l.strip()]
            return " ".join(lines[:20])

    # Fallback: look for response-like content after form area
    # Try to find a block of text that looks like an AI response
    if "Simulate" in body_text:
        after = body_text.split("Simulate")[-1].strip()
        lines = [l.strip() for l in after.split("\n") if l.strip() and len(l.strip()) > 10]
        if lines:
            # Filter out UI elements
            content_lines = [l for l in lines if not any(
                x in l for x in ["Health Check", "RAG Tester", "DB Stats", "Guest Lookup",
                                  "hotel_", "debug_guest", "HOTEL ID", "GUEST IDENTIFIER"]
            )]
            if content_lines:
                return " ".join(content_lines[:10])

    return "(could not extract)"

def test_rag_tester(page, hotel):
    """Test the RAG Tester debug tab."""
    results = {"queries": [], "issues": []}

    goto_hotel(page, hotel)
    click_sidebar(page, "Debug", hotel["name"])
    page.wait_for_timeout(2000)

    if not click_debug_tab(page, "RAG Tester", hotel["name"]):
        results["issues"].append("Could not find RAG Tester tab")
        return results

    page.wait_for_timeout(2000)
    ss(page, f"{hotel['name']}_RAG_Tester")

    body = page.inner_text("body", timeout=5000)
    results["accessible"] = True
    results["content"] = body[:500]
    return results

def test_health_check(page, hotel):
    """Run health check from Debug tab."""
    results = {}

    goto_hotel(page, hotel)
    click_sidebar(page, "Debug", hotel["name"])
    page.wait_for_timeout(2000)

    if not click_debug_tab(page, "Health Check", hotel["name"]):
        results["error"] = "Could not find Health Check tab"
        return results

    page.wait_for_timeout(2000)

    # Click "Run Health Check" button
    try:
        btn = page.locator('button:has-text("Run Health Check")').first
        if btn.is_visible(timeout=3000):
            btn.click()
            page.wait_for_timeout(8000)
            ss(page, f"{hotel['name']}_HealthCheck_result")
            body = page.inner_text("body", timeout=5000)
            results["ran"] = True
            results["content"] = body[:1000]

            # Look for pass/fail indicators
            if "pass" in body.lower():
                results["status"] = "pass indicators found"
            elif "fail" in body.lower():
                results["status"] = "fail indicators found"
            else:
                results["status"] = "unknown"
        else:
            results["error"] = "Run Health Check button not visible"
    except Exception as e:
        results["error"] = str(e)[:200]

    return results

def test_db_stats(page, hotel):
    """Check DB Stats debug tab."""
    results = {}

    goto_hotel(page, hotel)
    click_sidebar(page, "Debug", hotel["name"])
    page.wait_for_timeout(2000)

    if not click_debug_tab(page, "DB Stats", hotel["name"]):
        results["error"] = "Could not find DB Stats tab"
        return results

    page.wait_for_timeout(3000)
    ss(page, f"{hotel['name']}_DB_Stats")
    body = page.inner_text("body", timeout=5000)
    results["accessible"] = True
    results["content"] = body[:1000]

    # Extract key stats
    chunks_match = re.search(r'(\d+)\s*(?:chunks?|documents?|vectors?)', body, re.IGNORECASE)
    if chunks_match:
        results["chunks"] = int(chunks_match.group(1))

    return results

def run_all_tests():
    all_results = {
        "test_date": datetime.now().isoformat(),
        "tester": "Anirudha Talmale",
        "app": "HotelIntelliai Dashboard",
        "scope": "Full staff perspective testing - Riverie & Le Patte",
        "hotels": {}
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(30000)

        print("=" * 70)
        print("FINAL DASHBOARD TEST v3 - Riverie & Le Patte (Staff Perspective)")
        print("=" * 70)

        login(page)

        # First, screenshot the hotel list to see all hotels
        page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
        ss(page, "00_hotel_list_top")
        page.mouse.wheel(0, 500)
        page.wait_for_timeout(1000)
        ss(page, "00_hotel_list_bottom")

        for hotel in HOTELS:
            hname = hotel["name"]
            print(f"\n{'=' * 70}")
            print(f"TESTING: {hname} ({hotel['id']})")
            print(f"{'=' * 70}")

            hotel_results = {
                "name": hname,
                "id": hotel["id"],
                "subdomain": hotel["subdomain"],
                "all_issues": []
            }

            # Test 1: Navigate to hotel dashboard
            print(f"\n  [1/8] Hotel Dashboard Navigation")
            if goto_hotel(page, hotel):
                hotel_results["navigation"] = {"success": True, "url": page.url}
                body = page.inner_text("body", timeout=5000)

                # Check if we actually got the hotel dashboard (not login or error)
                if "Overview" in body or "Conversations" in body:
                    hotel_results["navigation"]["dashboard_loaded"] = True
                    print(f"    Dashboard loaded successfully")
                else:
                    hotel_results["navigation"]["dashboard_loaded"] = False
                    hotel_results["all_issues"].append("Dashboard may not have loaded correctly")
                    print(f"    WARNING: Dashboard content not as expected")
                    print(f"    Body preview: {body[:200]}")
            else:
                hotel_results["navigation"] = {"success": False}
                hotel_results["all_issues"].append("Could not navigate to hotel dashboard")
                all_results["hotels"][hotel["id"]] = hotel_results
                continue

            # Test 2: All sidebar sections
            print(f"\n  [2/8] All Sidebar Sections")
            hotel_results["sections"] = test_all_sections(page, hotel)

            # Test 3: Health Check
            print(f"\n  [3/8] Health Check")
            hotel_results["health_check"] = test_health_check(page, hotel)

            # Test 4: RAG Tester
            print(f"\n  [4/8] RAG Tester")
            hotel_results["rag_tester"] = test_rag_tester(page, hotel)

            # Test 5: DB Stats
            print(f"\n  [5/8] DB Stats")
            hotel_results["db_stats"] = test_db_stats(page, hotel)

            # Test 6: Knowledge Base deep check
            print(f"\n  [6/8] Knowledge Base Deep Check")
            kb_data = hotel_results.get("sections", {}).get("Knowledge Base", {})
            if kb_data.get("accessible"):
                chunks = kb_data.get("chunks", "unknown")
                print(f"    KB Chunks: {chunks}")
                for tab in ["File", "URL", "FAQ"]:
                    tab_status = kb_data.get(f"tab_{tab}", "not checked")
                    print(f"    Tab {tab}: {tab_status}")
            else:
                hotel_results["all_issues"].append("Knowledge Base not accessible")

            # Test 7: Escalations check
            print(f"\n  [7/8] Escalations Check")
            esc_data = hotel_results.get("sections", {}).get("Escalations", {})
            if esc_data.get("accessible"):
                goto_hotel(page, hotel)
                click_sidebar(page, "Escalations", hname)
                page.wait_for_timeout(3000)
                ss(page, f"{hname}_Escalations_detail")
                esc_body = page.inner_text("body", timeout=5000)
                hotel_results["escalations_detail"] = {
                    "content_preview": esc_body[:500],
                    "has_items": len(esc_body) > 200
                }
                print(f"    Escalations content: {len(esc_body)} chars")

            # Test 8: AI Concierge (15 questions)
            print(f"\n  [8/8] AI Concierge - {len(CONCIERGE_QUESTIONS[hname])} Questions")
            hotel_results["concierge"] = test_concierge(page, hotel, CONCIERGE_QUESTIONS[hname])

            # Compile issues
            for section, data in hotel_results.get("sections", {}).items():
                if isinstance(data, dict):
                    if not data.get("accessible"):
                        hotel_results["all_issues"].append(f"Section '{section}' not accessible")
                    elif data.get("has_error"):
                        hotel_results["all_issues"].append(f"Section '{section}' has error: {data.get('error_detail', '')}")

            hotel_results["all_issues"].extend(hotel_results.get("concierge", {}).get("issues", []))

            all_results["hotels"][hotel["id"]] = hotel_results

        browser.close()

    # Save results
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2)

    # Print comprehensive summary
    print(f"\n{'=' * 70}")
    print("COMPREHENSIVE TEST SUMMARY")
    print(f"{'=' * 70}")

    for hid, data in all_results["hotels"].items():
        hname = data["name"]
        concierge = data.get("concierge", {})
        stats = concierge.get("stats", {})
        issues = data.get("all_issues", [])
        sections = data.get("sections", {})

        print(f"\n{'─' * 50}")
        print(f"{hname} ({hid})")
        print(f"{'─' * 50}")

        # Navigation
        nav = data.get("navigation", {})
        print(f"  Navigation: {'OK' if nav.get('success') else 'FAILED'} ({nav.get('url', 'N/A')})")

        # Sections
        accessible = sum(1 for s, d in sections.items() if isinstance(d, dict) and d.get("accessible"))
        total = len(sections)
        print(f"  Sidebar Sections: {accessible}/{total} accessible")
        for s, d in sections.items():
            if isinstance(d, dict):
                status = "OK" if d.get("accessible") and not d.get("has_error") else "ISSUE"
                print(f"    [{status}] {s}")

        # KB
        kb = sections.get("Knowledge Base", {})
        if isinstance(kb, dict) and kb.get("accessible"):
            print(f"  KB Chunks: {kb.get('chunks', 'N/A')}")
            for tab in ["File", "URL", "FAQ"]:
                print(f"    Tab {tab}: {kb.get(f'tab_{tab}', 'N/A')}")

        # Health Check
        hc = data.get("health_check", {})
        print(f"  Health Check: {hc.get('status', hc.get('error', 'not run'))}")

        # Concierge
        if stats:
            print(f"  Concierge: {stats.get('total', 0)} questions")
            print(f"    Answered: {stats.get('answered', 0)}")
            print(f"    Escalations: {stats.get('escalations', 0)}")
            print(f"    Errors: {stats.get('errors', 0)}")
            print(f"    Accuracy: {stats.get('accuracy_pct', 0)}%")

        # All issues
        if issues:
            print(f"  ISSUES ({len(issues)}):")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"  No issues found!")

    print(f"\nResults saved to: {RESULTS_FILE}")
    return all_results

if __name__ == "__main__":
    run_all_tests()
