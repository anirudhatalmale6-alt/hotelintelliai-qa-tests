# HotelIntelliai - Deep AI Concierge Testing Report
**Date:** March 24, 2026
**Tester:** Anirudha Talmale
**Platform:** dashboard.hotelintelliai.com

---

## Executive Summary

Tested AI concierge responses across 3 hotels with KB data using the Msg Simulator (Debug panel). 
30 questions total (10 per hotel). Asked common guest questions about rooms, amenities, dining, spa, location, etc.

**Overall Score: 5/30 questions answered correctly (16%)**
- GOOD responses: 5 (16%)
- ESCALATION responses: 12 (40%) - "Let me connect you with our team..."
- NO_INFO responses: 3 (10%)
- NO_RESPONSE (error): 10 (33%) - Imperial Mae Ping hotel_id was rejected

---

## Critical Bugs Found

### BUG-012: Msg Simulator HOTEL ID Never Updates (CRITICAL)
**Location:** Debug > Msg Simulator  
**Issue:** The HOTEL ID field always defaults to "hotel_riviera_cr" (The Riverie) regardless of which hotel you navigate to. It never auto-updates when switching between hotels.  
**Impact:** If a user doesn't manually change the HOTEL ID field, ALL queries go to The Riverie's KB, producing wrong answers for every other hotel.  
**Expected:** HOTEL ID should auto-populate with the current hotel's ID when navigating to Debug > Msg Simulator.

### BUG-013: Imperial Mae Ping - "Hotel not found" with collection ID (MODERATE)
**Location:** Msg Simulator  
**Issue:** Using "hotel_imperial_mae_ping" (the KB collection name shown on the KB page) returns "Hotel 'hotel_imperial_mae_ping' not found". Using "imperial_mae_ping" (the subdomain format) works but returns escalation for all questions.  
**Root cause:** The HOTEL ID in the simulator expects the subdomain format, but the KB page shows the collection name format. These are inconsistent.

### BUG-014: Imperial Mae Ping KB Contains Spam Content (CRITICAL)
**Location:** Knowledge Base for Imperial Mae Ping  
**Issue:** The domain imperialmaeping.com has been taken over by a gambling/spam site. The 31 chunks currently in the KB contain casino/poker content, NOT hotel information. All 10 hotel-related questions resulted in escalation responses.  
**Fix needed:** Delete all KB content for Imperial Mae Ping and re-ingest from the correct hotel website.

### BUG-015: URL Scraping Never Completes (CRITICAL)
**Location:** Knowledge Base > URL tab > Scrape & Embed  
**Issue:** Clicking "Scrape & Embed" shows "Scraping started, this may take a few minutes..." but never completes. After 3+ minutes of monitoring, chunks remain at 0. Tested with multiple hotels including working websites (theriverie.com, oberoihotels.com).  
**Workaround:** File upload via the File tab works correctly. I uploaded .txt files with hotel content and they were embedded into chunks successfully.  
**Impact:** Hotels cannot ingest their website content through the URL scraping feature.

### BUG-016: Three Hotel Websites Unreachable (INFO)
**Websites tested:**
- theheritage-chiangrai.com - Connection refused (site down)
- grandvistachiangrai.com - SSL certificate error
- lepatte.com - Connection refused (site down)

These cannot be scraped even if the URL scraper was working.

---

## Hotel-by-Hotel Results

### 1. Imperial Mae Ping Hotel (imperial_mae_ping) - 31 chunks
**Score: 0/10 (0%)**  
**Issue:** Hotel ID "hotel_imperial_mae_ping" returned "not found" error. With correct ID "imperial_mae_ping", all questions escalate because KB contains gambling/spam content from hijacked domain.

| # | Question | Result | Response |
|---|----------|--------|----------|
| 1 | Check-in/out time? | NO_RESPONSE | Hotel not found error |
| 2 | Room types? | NO_RESPONSE | Hotel not found error |
| 3 | Swimming pool? | NO_RESPONSE | Hotel not found error |
| 4 | Spa? | NO_RESPONSE | Hotel not found error |
| 5 | Restaurants? | NO_RESPONSE | Hotel not found error |
| 6 | WiFi? | NO_RESPONSE | Hotel not found error |
| 7 | Airport transfer? | NO_RESPONSE | Hotel not found error |
| 8 | Cancellation policy? | NO_RESPONSE | Hotel not found error |
| 9 | Breakfast? | NO_RESPONSE | Hotel not found error |
| 10 | Location? | NO_RESPONSE | Hotel not found error |

### 2. The Oberoi Udaivilas (oberoi_udaivilas) - 3 chunks
**Score: 4/10 (40%)**  
**Analysis:** With only 3 chunks of content (from uploaded text file), the AI answered 4 questions well using the general Oberoi brand knowledge in the KB. Questions about specific amenities (pool, restaurants, fitness) escalated due to missing details.

| # | Question | Result | Response Summary |
|---|----------|--------|-----------------|
| 1 | Room types/suites? | ESCALATION | "Let me connect you with our team..." |
| 2 | Swimming pool? | ESCALATION | "Let me connect you with our team..." |
| 3 | Spa details? | NO_INFO | Acknowledged lack of info, provided phone number |
| 4 | Restaurants? | ESCALATION | "Let me connect you with our team..." |
| 5 | Yoga sessions? | GOOD | Detailed answer about Yoga Stretch & Daily Reflections program, Asmi wellness |
| 6 | Experiences/activities? | GOOD | Listed wellness, swimming, fitness, signature experiences (some mixed with other Oberoi properties) |
| 7 | Event/conference facilities? | GOOD | Detailed capacities (theatre 238, classroom 60, boardroom 80, cocktail 180) |
| 8 | Location? | ESCALATION | "Let me connect you with our team..." |
| 9 | Awards? | GOOD | Mentioned Oberoi brand awards (noted they were for Amarvilas, not Udaivilas specifically) |
| 10 | Fitness center? | ESCALATION | "Let me connect you with our team..." |

**Key finding:** When the AI has relevant KB content, it gives excellent detailed responses (5-8 seconds response time). When it doesn't have info, it escalates instantly (~2 seconds). The escalation vs answer pattern clearly maps to what's in the KB.

### 3. The Riverie by Katathani (hotel_riviera_cr) - 1 chunk
**Score: 1/10 (10%)**  
**Analysis:** With only 1 chunk of content, the AI could only answer the room types question (which was well-covered in the uploaded text). Everything else escalated.

| # | Question | Result | Response Summary |
|---|----------|--------|-----------------|
| 1 | Room types? | GOOD | Excellent answer listing all 8 room types with sizes (Family Suite 62-75sqm, Riverie Suite 70-100sqm) |
| 2 | Pool/water park? | ESCALATION | "Let me connect you with our team..." |
| 3 | Spa? | NO_INFO | Acknowledged no spa info in KB |
| 4 | Dining? | ESCALATION | "Let me connect you with our team..." |
| 5 | Kids club? | ESCALATION | "Let me connect you with our team..." |
| 6 | Weddings/conferences? | ESCALATION | "Let me connect you with our team..." |
| 7 | Airport transfers? | NO_INFO | Acknowledged no transfer info |
| 8 | Location? | ESCALATION | "Let me connect you with our team..." |
| 9 | Phone number? | ESCALATION | "Let me connect you with our team..." |
| 10 | Awards? | ESCALATION | "Let me connect you with our team..." |

---

## Hotels Not Tested (0 KB chunks)

| Hotel | Reason | Website Status |
|-------|--------|----------------|
| Heritage Chiang Rai | 0 chunks, website down | theheritage-chiangrai.com - ECONNREFUSED |
| Grand Vista Chiangrai | 0 chunks, SSL error | grandvistachiangrai.com - TLS_CERT_ALTNAME_INVALID |
| le Patte | 0 chunks, website down | lepatte.com - ECONNREFUSED |

---

## Escalation Pattern Analysis

The client's observation is correct: "anything which says 'I want to make sure you get the best possible answer. Let me connect you with...' should be investigated."

This response occurs when:
1. The AI's RAG search finds NO relevant KB chunks for the question
2. The confidence threshold is not met
3. ESCALATE flag is set to YES

Pattern observed:
- ESCALATION responses take ~1.7-2.8 seconds (fast = no KB search match)
- GOOD responses take ~5-8 seconds (slower = found KB content, generated answer)
- This timing difference is a reliable indicator of KB coverage

---

## Recommendations

1. **Fix URL Scraper (BUG-015):** The scraping backend is not processing jobs. This is the main blocker for loading KB content.

2. **Fix Hotel ID auto-population (BUG-012):** The Msg Simulator should auto-detect the current hotel context.

3. **Clean Imperial Mae Ping KB:** Delete the 31 spam chunks and re-ingest from the correct hotel website (Imperial Hotels group or booking platform).

4. **Get correct URLs for broken websites:** Heritage Chiang Rai, Grand Vista, and le Patte websites are all unreachable. Need alternative sources for their content.

5. **More KB content needed:** Hotels with only 1-3 chunks can only answer a fraction of guest questions. Recommend ingesting multiple pages (rooms, dining, spa, amenities, policies, FAQ) to achieve 50+ chunks per hotel for comprehensive coverage.

---

## Test Environment
- Browser: Chromium (headless), 1280x720 viewport
- Framework: Playwright + Python
- Test script: deep_concierge_test_v7.py
- All 30 questions tested with before/after screenshots
- Results saved in: reports/concierge_test_v7_results.json

## Automated Test Scripts
All Playwright test scripts are available in the GitHub repository:
https://github.com/anirudhatalmale6-alt/hotelintelliai-qa-tests

