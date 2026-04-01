"""
Final test for Le Patta Hotel with correct hotel ID: lepatta
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
RESULTS_FILE = "/var/lib/freelancer/projects/40298427/reports/final_lepatta_results.json"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

HOTEL = {"name": "LePatta", "id": "lepatta", "subdomain": "lepatta"}

SIDEBAR_SECTIONS = ["Overview", "Conversations", "Guests", "Escalations", "Channels", "Knowledge Base", "Debug"]
DEBUG_TABS = ["Health Check", "RAG Tester", "Msg Simulator", "DB Stats", "Guest Lookup"]

QUESTIONS = [
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
]

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
    print("Logged in")

def goto_hotel(page):
    url = f"https://{HOTEL['subdomain']}.hotelintelliai.com/"
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    if page.locator('input[type="email"]').count() > 0:
        login(page)
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
    return True

def click_sidebar(page, section):
    for sel in [f'a:has-text("{section}")', f'text="{section}"']:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=2000):
                el.click()
                page.wait_for_timeout(3000)
                return True
        except:
            continue
    return False

def click_debug_tab(page, tab):
    for sel in [f'button:has-text("{tab}")', f'text="{tab}"']:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=2000):
                el.click()
                page.wait_for_timeout(3000)
                return True
        except:
            continue
    return False

def extract_response(body_text):
    patterns = [
        r'(?:AGENT\s*RESPONSE|Agent\s*Response|agent_response)[:\s]*\n?(.*?)(?:\n\s*(?:HOTEL|Hotel|GUEST|Guest|MESSAGE|Message|SIMULATE|Simulate|DEBUG|Debug|Health|RAG|DB Stats|Guest Lookup)\b)',
        r'(?:AGENT\s*RESPONSE|Agent\s*Response)[:\s]*([\s\S]{10,500})',
    ]
    for pattern in patterns:
        match = re.search(pattern, body_text, re.DOTALL | re.IGNORECASE)
        if match:
            resp = match.group(1).strip()
            lines = [l.strip() for l in resp.split("\n") if l.strip()]
            return " ".join(lines[:20])

    if "Simulate" in body_text:
        after = body_text.split("Simulate")[-1].strip()
        lines = [l.strip() for l in after.split("\n") if l.strip() and len(l.strip()) > 10]
        content_lines = [l for l in lines if not any(
            x in l for x in ["Health Check", "RAG Tester", "DB Stats", "Guest Lookup",
                              "hotel_", "debug_guest", "HOTEL ID", "GUEST IDENTIFIER"]
        )]
        if content_lines:
            return " ".join(content_lines[:10])

    return "(could not extract)"

def run():
    results = {"test_date": datetime.now().isoformat(), "hotel": HOTEL}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(30000)

        print("=" * 60)
        print(f"TESTING: Le Patta Hotel (lepatta)")
        print("=" * 60)

        login(page)
        goto_hotel(page)

        body = page.inner_text("body", timeout=5000)
        ss(page, "LePatta_home")
        print(f"Dashboard loaded: {len(body)} chars")
        print(f"URL: {page.url}")

        if "error" in body.lower()[:100] or "not found" in body.lower()[:100]:
            print(f"ERROR: {body[:200]}")
            results["error"] = body[:200]
            browser.close()
            with open(RESULTS_FILE, "w") as f:
                json.dump(results, f, indent=2)
            return

        dashboard_loaded = "Overview" in body or "Conversations" in body
        results["dashboard_loaded"] = dashboard_loaded
        print(f"Dashboard sections visible: {dashboard_loaded}")

        # Test all sidebar sections
        print(f"\n--- Sidebar Sections ---")
        results["sections"] = {}
        for section in SIDEBAR_SECTIONS:
            goto_hotel(page)
            if click_sidebar(page, section):
                page.wait_for_timeout(2000)
                safe = section.replace(" ", "_")
                ss(page, f"LePatta_{safe}")
                body = page.inner_text("body", timeout=5000)

                section_result = {
                    "accessible": True,
                    "content_length": len(body),
                    "url": page.url
                }

                if section == "Knowledge Base":
                    chunks_match = re.search(r'(\d+)\s*chunks?', body, re.IGNORECASE)
                    if chunks_match:
                        section_result["chunks"] = int(chunks_match.group(1))
                    for tab in ["File", "URL", "FAQ"]:
                        try:
                            tab_btn = page.locator(f'button:has-text("{tab}")').first
                            if tab_btn.is_visible(timeout=2000):
                                tab_btn.click()
                                page.wait_for_timeout(2000)
                                ss(page, f"LePatta_KB_{tab}")
                                section_result[f"tab_{tab}"] = "accessible"
                        except:
                            section_result[f"tab_{tab}"] = "error"

                elif section == "Channels":
                    for ch in ["whatsapp", "telegram", "line", "email", "web", "sms"]:
                        if ch in body.lower():
                            section_result[f"channel_{ch}"] = True

                elif section == "Debug":
                    for tab in DEBUG_TABS:
                        if click_debug_tab(page, tab):
                            page.wait_for_timeout(2000)
                            safe_tab = tab.replace(" ", "_")
                            ss(page, f"LePatta_Debug_{safe_tab}")
                            tab_body = page.inner_text("body", timeout=5000)
                            section_result[f"tab_{tab}"] = {"accessible": True, "length": len(tab_body)}

                            if tab == "Health Check":
                                try:
                                    btn = page.locator('button:has-text("Run Health Check")').first
                                    if btn.is_visible(timeout=2000):
                                        btn.click()
                                        page.wait_for_timeout(8000)
                                        ss(page, "LePatta_HealthCheck_result")
                                        hc_body = page.inner_text("body", timeout=5000)
                                        section_result["health_check_result"] = hc_body[:500]
                                except:
                                    pass
                        else:
                            section_result[f"tab_{tab}"] = {"accessible": False}

                results["sections"][section] = section_result
                print(f"  [{section}] OK - {len(body)} chars")
            else:
                results["sections"][section] = {"accessible": False}
                print(f"  [{section}] FAILED")

        # Concierge test
        print(f"\n--- AI Concierge ({len(QUESTIONS)} questions) ---")
        goto_hotel(page)
        click_sidebar(page, "Debug")
        page.wait_for_timeout(2000)
        click_debug_tab(page, "Msg Simulator")
        page.wait_for_timeout(2000)
        ss(page, "LePatta_MsgSimulator_ready")

        all_inputs = page.locator('input:visible, textarea:visible').all()
        print(f"Found {len(all_inputs)} inputs")

        msg_input = None
        for inp in all_inputs:
            try:
                placeholder = (inp.get_attribute("placeholder") or "").lower()
                if "message" in placeholder or "spa" in placeholder or "e.g." in placeholder:
                    msg_input = inp
                    print(f"  MESSAGE input: placeholder='{placeholder}'")
                    break
            except:
                continue

        if not msg_input and len(all_inputs) >= 3:
            msg_input = all_inputs[2]
            print(f"  Using 3rd input as MESSAGE (fallback)")

        sim_btn = None
        for sel in ['button:has-text("Simulate")', 'button:has-text("Send")']:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    sim_btn = btn
                    break
            except:
                continue

        concierge = {"questions": [], "issues": []}
        escalation_count = 0
        answered_count = 0
        error_count = 0

        if msg_input and sim_btn:
            prev_resp = ""
            for idx, q in enumerate(QUESTIONS):
                qnum = idx + 1
                print(f"\n  Q{qnum}: {q}")
                try:
                    msg_input.click(click_count=3)
                    page.wait_for_timeout(200)
                    msg_input.fill("")
                    page.wait_for_timeout(200)
                    msg_input.fill(q)
                    page.wait_for_timeout(500)

                    sim_btn.click()
                    page.wait_for_timeout(10000)

                    ss(page, f"LePatta_q{qnum}")
                    body = page.inner_text("body", timeout=5000)
                    response = extract_response(body)
                    print(f"  A{qnum}: {response[:300]}")

                    resp_lower = response.lower()
                    is_esc = ("connect you with" in resp_lower or "best possible answer" in resp_lower or "i want to make sure" in resp_lower)
                    is_err = (not response or response == "(could not extract)")
                    is_dup = (response == prev_resp and prev_resp and len(prev_resp) > 20)

                    if is_esc:
                        escalation_count += 1
                        concierge["issues"].append(f"Q{qnum}: '{q}' -> ESCALATION")
                    elif not is_err:
                        answered_count += 1
                    if is_err:
                        error_count += 1

                    concierge["questions"].append({
                        "q_num": qnum,
                        "question": q,
                        "response": response[:800],
                        "classification": "ESCALATION" if is_esc else ("ERROR" if is_err else "ANSWERED"),
                        "is_duplicate": is_dup
                    })
                    prev_resp = response

                except Exception as e:
                    error_count += 1
                    print(f"  ERROR: {str(e)[:100]}")
                    concierge["questions"].append({
                        "q_num": qnum, "question": q,
                        "response": f"ERROR: {str(e)[:200]}",
                        "classification": "ERROR"
                    })
        else:
            concierge["issues"].append("Could not find msg input or simulate button")

        concierge["stats"] = {
            "total": len(QUESTIONS),
            "answered": answered_count,
            "escalations": escalation_count,
            "errors": error_count,
            "accuracy_pct": round(answered_count / len(QUESTIONS) * 100, 1)
        }
        results["concierge"] = concierge

        browser.close()

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # Summary
    print(f"\n{'=' * 60}")
    print("LE PATTA SUMMARY")
    print(f"{'=' * 60}")
    print(f"Dashboard: {'loaded' if results.get('dashboard_loaded') else 'FAILED'}")
    for s, d in results.get("sections", {}).items():
        status = "OK" if d.get("accessible") else "FAILED"
        extra = ""
        if "chunks" in d:
            extra = f" ({d['chunks']} chunks)"
        print(f"  [{status}] {s}{extra}")
    stats = concierge.get("stats", {})
    print(f"\nConcierge: {stats.get('total')} questions")
    print(f"  Answered: {stats.get('answered')}")
    print(f"  Escalations: {stats.get('escalations')}")
    print(f"  Errors: {stats.get('errors')}")
    print(f"  Accuracy: {stats.get('accuracy_pct')}%")
    if concierge.get("issues"):
        print(f"\nIssues:")
        for i in concierge["issues"]:
            print(f"  - {i}")

if __name__ == "__main__":
    run()
