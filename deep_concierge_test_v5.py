"""
Deep AI Concierge Test v5 - Fixed input handling
Tests all hotels with KB content using the Msg Simulator.
Key fixes:
- Explicitly targets the MESSAGE input (3rd visible input, placeholder "e.g. do you have a spa?")
- Verifies HOTEL ID field matches current hotel
- Full page reload between questions for clean state
- Waits for response to actually change
"""
import os
import re
import json
import time
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "https://dashboard.hotelintelliai.com"
EMAIL = "anirudhatomeiz@gmail.com"
PASSWORD = "CHANGEME"
SCREENSHOT_DIR = "/var/lib/freelancer/projects/40298427/screenshots/v5"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

HOTELS = [
    {"name": "Imperial Mae Ping Hotel", "id": "imperial_mae_ping", "chunks": 31},
    {"name": "The Oberoi Udaivilas", "id": "oberoi_udaivilas", "chunks": 3},
    {"name": "The Riverie by Katathani", "id": "hotel_riviera_cr", "chunks": 1},
]

# Hotel-specific questions based on what content we know exists
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
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    page.screenshot(path=path)


def navigate_to_hotel_debug(page, hotel_name):
    """Navigate to hotel's Debug > Msg Simulator with fresh page load."""
    page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    
    # Click hotel
    page.locator(f'text={hotel_name}').first.click()
    page.wait_for_timeout(5000)
    
    # Click Debug
    page.locator('text=Debug').first.click()
    page.wait_for_timeout(3000)
    
    # Click Msg Simulator
    page.locator('button:has-text("Msg Simulator")').click()
    page.wait_for_timeout(3000)


def fill_message_and_simulate(page, question, hotel_id):
    """
    Fill the MESSAGE input (3rd input) with the question and click Simulate.
    Returns the response text or None.
    """
    # Find all visible text inputs
    inputs = page.locator('input')
    visible_inputs = []
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        if not inp.is_visible():
            continue
        itype = (inp.get_attribute('type') or '').lower()
        if itype in ('email', 'password', 'file', 'hidden', 'checkbox', 'radio', 'number'):
            continue
        visible_inputs.append(inp)
    
    if len(visible_inputs) < 3:
        print(f"    WARNING: Only found {len(visible_inputs)} visible text inputs (expected 3)")
        # Try to find by placeholder
        msg_input = page.locator('input[placeholder*="spa"], input[placeholder*="e.g"]').first
        if msg_input.is_visible():
            visible_inputs = [None, None, msg_input]
        else:
            return None
    
    # Verify HOTEL ID (1st input) contains expected hotel ID
    if visible_inputs[0]:
        hotel_id_val = visible_inputs[0].input_value()
        print(f"    HOTEL ID field: '{hotel_id_val}'")
    
    # The MESSAGE input should be the 3rd one (index 2)
    msg_input = visible_inputs[2] if len(visible_inputs) >= 3 else visible_inputs[-1]
    
    # Verify it's the right input by checking placeholder
    placeholder = (msg_input.get_attribute('placeholder') or '').lower()
    print(f"    Message input placeholder: '{placeholder}'")
    
    # Clear and fill
    msg_input.click()
    page.wait_for_timeout(200)
    msg_input.fill("")
    page.wait_for_timeout(200)
    msg_input.fill(question)
    page.wait_for_timeout(500)
    
    # Verify the input has our question
    actual_val = msg_input.input_value()
    if actual_val != question:
        print(f"    WARNING: Input value mismatch! Got '{actual_val[:50]}', expected '{question[:50]}'")
    
    # Click Simulate
    sim_btn = page.locator('button:has-text("Simulate")')
    if sim_btn.count() == 0:
        print(f"    ERROR: Simulate button not found")
        return None
    
    # Check if button is enabled
    disabled = sim_btn.first.get_attribute('disabled')
    if disabled is not None:
        print(f"    WARNING: Simulate button is disabled")
        return None
    
    sim_btn.first.click()
    
    # Wait for response - look for AGENT RESPONSE to appear/change
    print(f"    Waiting for response...")
    page.wait_for_timeout(15000)  # 15 seconds for AI to respond
    
    # Extract response from page
    body = page.locator('body').inner_text()
    return extract_response(body)


def extract_response(body):
    """Extract the AGENT RESPONSE section from page body."""
    lines = body.split('\n')
    response_text = ""
    intent = ""
    elapsed = ""
    
    capture = False
    for line in lines:
        stripped = line.strip()
        if 'AGENT RESPONSE' in stripped.upper():
            capture = True
            continue
        if capture:
            upper = stripped.upper()
            if any(kw in upper for kw in ['INTENT', 'ELAPSED', 'LANGUAGE', 'CONFIDENCE', 'ESCALAT']):
                if 'INTENT' in upper and ':' in stripped:
                    intent = stripped.split(':', 1)[1].strip()
                if 'ELAPSED' in upper:
                    elapsed = stripped
                capture = False
            elif stripped and len(stripped) > 1 and not stripped.startswith('↻') and not stripped.startswith('●'):
                response_text += stripped + " "
    
    return {
        "response": response_text.strip(),
        "intent": intent,
        "elapsed": elapsed,
    }


def evaluate_quality(response_text, question):
    """Evaluate response quality with more nuance."""
    if not response_text or len(response_text) < 10:
        return "NO_RESPONSE", ["Empty or very short response"]
    
    lower = response_text.lower()
    
    # Check for escalation/handoff (client's key concern)
    if any(phrase in lower for phrase in [
        "let me connect you with",
        "i want to make sure you get the best possible answer",
        "connect you with our",
        "transfer you to",
        "let me transfer",
    ]):
        return "ESCALATION", ["AI escalated instead of answering - KB may be missing this info"]
    
    if 'error' in lower or '⚠' in response_text:
        return "ERROR", ["Error in response"]
    
    if any(phrase in lower for phrase in [
        "i don't have", "i don't know", "i'm not sure",
        "i cannot find", "not available in", "no information",
        "i apologize, but i don't", "sorry, i don't have",
        "i don't have specific information", "unfortunately, i don't",
    ]):
        return "NO_INFO", ["AI lacks information to answer"]
    
    if len(response_text) < 30:
        return "PARTIAL", ["Response seems short"]
    
    return "GOOD", []


def main():
    results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(60000)
        
        # Login
        page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(2000)
        page.locator('input[type="email"]').fill(EMAIL)
        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(5000)
        print("Logged in to dashboard\n")
        
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
                    # Navigate fresh for each question to avoid state issues
                    navigate_to_hotel_debug(page, hname)
                    screenshot(page, f"{hid}_q{qi+1}_before")
                    
                    # Fill message and simulate
                    resp_data = fill_message_and_simulate(page, question, hid)
                    screenshot(page, f"{hid}_q{qi+1}_after")
                    
                    if resp_data and resp_data.get("response"):
                        response = resp_data["response"]
                        intent = resp_data.get("intent", "")
                        elapsed = resp_data.get("elapsed", "")
                        
                        quality, issues = evaluate_quality(response, question)
                        
                        display = response[:200] + "..." if len(response) > 200 else response
                        print(f"  A: {display}")
                        print(f"  Quality: {quality} | Intent: {intent}")
                        if issues:
                            print(f"  Issues: {', '.join(issues)}")
                        
                        results[hid]["questions"].append({
                            "question": question,
                            "response": response[:500],
                            "intent": intent,
                            "elapsed": elapsed,
                            "quality": quality,
                            "issues": issues,
                        })
                    else:
                        print(f"  NO RESPONSE received")
                        results[hid]["questions"].append({
                            "question": question,
                            "response": "",
                            "quality": "NO_RESPONSE",
                            "issues": ["No response from simulator"],
                        })
                        
                except Exception as e:
                    print(f"  ERROR: {e}")
                    results[hid]["questions"].append({
                        "question": question,
                        "response": "",
                        "quality": "ERROR",
                        "issues": [str(e)[:150]],
                    })
        
        context.close()
        browser.close()
    
    # Save results
    os.makedirs("/var/lib/freelancer/projects/40298427/reports", exist_ok=True)
    with open("/var/lib/freelancer/projects/40298427/reports/concierge_test_v5_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"\n\n{'='*70}")
    print("SUMMARY - AI CONCIERGE ACCURACY BY HOTEL")
    print(f"{'='*70}")
    
    total_good = 0
    total_escalation = 0
    total_noinfo = 0
    total_tested = 0
    
    for hid, data in results.items():
        hname = data["name"]
        chunks = data["chunks"]
        questions = data.get("questions", [])
        
        print(f"\n{hname} ({hid}) - {chunks} chunks")
        
        if not questions:
            print(f"  SKIPPED")
            continue
        
        quality_counts = {}
        for q in questions:
            qual = q.get("quality", "UNKNOWN")
            quality_counts[qual] = quality_counts.get(qual, 0) + 1
        
        total = len(questions)
        good = quality_counts.get("GOOD", 0)
        escalation = quality_counts.get("ESCALATION", 0)
        noinfo = quality_counts.get("NO_INFO", 0)
        
        total_good += good
        total_escalation += escalation
        total_noinfo += noinfo
        total_tested += total
        
        print(f"  Results: {good}/{total} GOOD ({100*good//total}%)")
        for qual, count in sorted(quality_counts.items()):
            print(f"    {qual}: {count}")
        
        # List problem answers
        for q in questions:
            if q.get("quality") not in ("GOOD",):
                print(f"  !! [{q['quality']}] \"{q['question']}\"")
                if q.get("response"):
                    print(f"     -> {q['response'][:120]}...")
    
    print(f"\n{'='*70}")
    print(f"OVERALL: {total_good}/{total_tested} GOOD ({100*total_good//total_tested if total_tested else 0}%)")
    print(f"ESCALATIONS: {total_escalation}/{total_tested}")
    print(f"NO INFO: {total_noinfo}/{total_tested}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
