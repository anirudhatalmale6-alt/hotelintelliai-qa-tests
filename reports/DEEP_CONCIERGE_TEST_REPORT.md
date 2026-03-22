# HotelIntelliai — Deep AI Concierge Test Report

**Date:** March 22, 2026
**Tester:** Anirudha Talmale
**Platform:** dashboard.hotelintelliai.com
**Test Method:** Automated Playwright tests via Msg Simulator (Debug panel)
**Test Scope:** 6 hotels, 10 questions each based on actual hotel website content

---

## Executive Summary

| Hotel | KB Chunks | Questions | Accurate | Partial | No Info | Escalated | Score |
|-------|-----------|-----------|----------|---------|---------|-----------|-------|
| The Riverie by Katathani | 467 | 10 | 5 | 3 | 2 | 0 | **80%** |
| le Patte | 306 | 10 | 6 | 0 | 3 | 1 | **60%** |
| The Heritage Chiang Rai | 48 | 10 | 1 | 0 | 1 | 8 | **10%** |
| Grand Vista Chiangrai | 13 | 10 | 1 | 0 | 0 | 9 | **10%** |
| Imperial Mae Ping | 0 | 10 | 0 | 0 | 0 | 9 | **0%** |
| The Oberoi Udaivilas | ~352 | 0 | - | - | - | - | **SKIPPED** |

**Overall Score: 16/50 tested questions answered correctly (32%)**

---

## Critical Finding: Excessive Escalation to Human Support

The most significant issue discovered is the **"escalation fallback" response pattern**:

> "I want to make sure you get the best possible answer. Let me connect you with our team who can help you directly. Someone will be in touch with you very shortly!"

This response was returned for **27 out of 50 questions (54%)** — even for basic hotel FAQs like "Do you have a pool?" or "Is there WiFi?" that should be answerable from the KB.

**Root Cause Analysis:**
- Hotels with MORE KB chunks (Riverie: 467, le Patte: 306) produce useful answers
- Hotels with FEWER chunks (Heritage: 48, Grand Vista: 13, Imperial: 0) almost always escalate
- The AI confidence threshold appears too high — it escalates instead of attempting to answer from available KB data
- This defeats the purpose of the AI concierge, as guests expect instant answers

**Recommendation:** Lower the confidence threshold for triggering escalation, or implement a two-tier response: provide the best available answer AND offer to connect with the team for more details.

---

## Hotel-by-Hotel Detailed Results

### 1. The Riverie by Katathani (hotel_riviera_cr) — 80% Accuracy

**KB Status:** 467 chunks (website + files + FAQs)
**Website:** theriverie.com

| # | Question | Result | Response Summary |
|---|----------|--------|-----------------|
| 1 | What room types do you have? | PARTIAL | Lists Standard/Deluxe/Suite but misses Family Suite, Riverie Suite, Royal Suite, Two-Bedroom Suite from website |
| 2 | Do you have a water park? | ACCURATE | Correctly identifies "The River Splash" with water slides, lazy river |
| 3 | Do you have a spa? | ACCURATE | Correctly names "Tivaa Ratrii Spa" with hours (11AM-9PM) |
| 4 | What dining options are available? | PARTIAL | Lists "Madam Chow" but misses "Red Lanna" restaurant from website |
| 5 | Do you have a kids club? | ACCURATE | Correctly identifies "Chang Maun Kids World" |
| 6 | How many rooms does the hotel have? | NO_INFO | Cannot provide the 271 room count from website |
| 7 | Do you have conference facilities? | PARTIAL | Mentions conference but says "Chandra Mahal" (Oberoi's venue name, NOT Riverie's) — cross-contamination |
| 8 | Where is the hotel located? | NO_INFO | Cannot provide address (Kraisorasit Rd, Kok River) |
| 9 | What is the phone number? | ACCURATE | Correctly provides +66 53 607 999 |
| 10 | Do you offer airport transfer? | ACCURATE | Confirms airport shuttle service available |

**Issues Found:**
- BUG-C1: Conference room names confused with another hotel (Oberoi's "Chandra Mahal" mentioned for Riverie)
- BUG-C2: Room types incomplete — KB has only generic types, not full list from theriverie.com
- BUG-C3: Location/address not in KB despite being on website

---

### 2. le Patte (lePatte) — 60% Accuracy

**KB Status:** 306 chunks (website + files + FAQs)
**Website:** lepattachiangrai.com

| # | Question | Result | Response Summary |
|---|----------|--------|-----------------|
| 1 | What room types are available? | ACCURATE | Correctly lists Superior (32sqm), Deluxe (32sqm), Suite (52sqm) |
| 2 | How big are the rooms? | ACCURATE | Provides correct dimensions: 32sqm and 52sqm |
| 3 | Do you have a swimming pool? | ACCURATE | Correctly identifies salt water swimming pool |
| 4 | Is there a gym or fitness center? | ACCURATE | Correctly mentions Gorilla Gym partnership (free for guests) |
| 5 | Do you have WiFi? | ESCALATED | Generic escalation instead of confirming free WiFi |
| 6 | Where is the hotel located? | NO_INFO | Cannot provide address despite it being on website |
| 7 | What is nearby the hotel? | NO_INFO | Cannot identify Night Bazaar (200m), Clock Tower, Walking Street |
| 8 | Do you have a restaurant? | NO_INFO | Says "I don't have information about restaurants" — misses The Terrace Restaurant |
| 9 | Is there parking available? | ACCURATE | Confirms complimentary parking |
| 10 | How far is the airport? | ACCURATE | Correctly states "7 km from Mae Fah Luang Airport" |

**Issues Found:**
- BUG-C4: WiFi info not in KB despite being prominently advertised
- BUG-C5: Location/address missing from KB
- BUG-C6: Nearby attractions not scraped from website
- BUG-C7: On-site restaurant (The Terrace) not recognized in KB

---

### 3. The Heritage Chiang Rai (heritage_chiangrai) — 10% Accuracy

**KB Status:** 48 chunks (website only)
**Website:** heritagechiangrai.com

| # | Question | Result | Response Summary |
|---|----------|--------|-----------------|
| 1 | How many rooms does the hotel have? | ESCALATED | Should answer "321 rooms" |
| 2 | What room types are available? | ESCALATED | Should list Deluxe, Executive, Premier, Suite types |
| 3 | Do you have meeting facilities? | ACCURATE | Correctly mentions Grand Ballroom, 1000 guests |
| 4 | What restaurants do you have? | ESCALATED | Should mention All-Day Restaurant, Library Lounge |
| 5 | Do you have a swimming pool? | ESCALATED | Should confirm outdoor pool |
| 6 | Where is the hotel located? | NO_INFO | Cannot provide Paholyothin Road address |
| 7 | Do you have a fitness center? | ESCALATED | Should confirm fitness center |
| 8 | What is the phone number? | ESCALATED | Should provide +66 5205 5888 |
| 9 | Is there a spa? | ESCALATED | Should confirm spa services |
| 10 | What are nearby attractions? | ESCALATED | Should mention White Temple, Night Bazaar |

**Issues Found:**
- BUG-C8: Only 48 chunks scraped — website has significantly more content
- BUG-C9: 8 out of 10 questions trigger escalation for a hotel with KB data
- BUG-C10: Scraper may have failed to extract key pages (rooms, dining, facilities)

---

### 4. Grand Vista Chiangrai Hotel (grand_vista_chiangrai) — 10% Accuracy

**KB Status:** 13 chunks (just ingested from third-party listing)
**Website:** grandvistachiangrai.com (SSL cert issue, used alternate URL)

| # | Question | Result | Response Summary |
|---|----------|--------|-----------------|
| 1 | How many rooms does the hotel have? | ESCALATED | Should answer "80 rooms" |
| 2 | Do you have a swimming pool? | ESCALATED | Should confirm saltwater pool |
| 3 | Do you have a spa? | ESCALATED | Should confirm spa with massage services |
| 4 | What dining options are available? | ESCALATED | Should mention Vista restaurant, lounge, bar |
| 5 | Do you have a fitness center? | ESCALATED | Should confirm fitness center |
| 6 | Is there WiFi? | ESCALATED | Should confirm free WiFi |
| 7 | Is there parking? | ESCALATED | Should confirm free parking |
| 8 | Where is the hotel located? | ESCALATED | Should provide Chiang Rai location |
| 9 | How far is the airport? | ESCALATED | Should answer "5 km" |
| 10 | What nearby attractions are there? | ACCURATE | Correctly lists Night Bazaar, Clock Tower, nearby attractions |

**Issues Found:**
- BUG-C11: Only 13 chunks — far too few to answer basic questions
- BUG-C12: Official website has SSL certificate issue, preventing direct scraping
- BUG-C13: Need to scrape more pages or use alternative sources

---

### 5. Imperial Mae Ping Hotel (imperial_mae_ping) — 0% Accuracy

**KB Status:** 0 chunks (no documents)
**Website:** chiangmai.intercontinental.com (now InterContinental)

| # | Question | Result | Response Summary |
|---|----------|--------|-----------------|
| 1-9 | All questions | ESCALATED | All return escalation response |
| 10 | Do you offer limousine service? | NO_RESPONSE | No response at all |

**Issues Found:**
- BUG-C14: KB completely empty — no website content ingested
- BUG-C15: Hotel website (InterContinental) may block scraping
- BUG-C16: URL scraping attempted but produced 0 chunks — needs manual content upload or different URL

---

### 6. The Oberoi Udaivilas (oberoi_udaivilas) — SKIPPED

**KB Status:** ~352 chunks (from previous test run data)
**Website:** oberoihotels.com

**Issue:** Could not access Debug panel — "Debug" menu link not found after navigating to hotel. The Oberoi hotel card may have a different dashboard layout or Debug access may be restricted.

**Bug:** BUG-C17: Debug/Msg Simulator not accessible for The Oberoi Udaivilas hotel

---

## Bug Summary

### Critical Bugs (Blocking)

| Bug ID | Description | Affected Hotels | Impact |
|--------|-------------|-----------------|--------|
| BUG-C14 | Imperial Mae Ping KB empty (0 chunks) | Imperial Mae Ping | 100% questions fail |
| BUG-C8 | Heritage has only 48 chunks — insufficient KB coverage | Heritage | 90% questions escalate |
| BUG-C11 | Grand Vista has only 13 chunks — insufficient KB coverage | Grand Vista | 90% questions escalate |

### High Severity Bugs

| Bug ID | Description | Affected Hotels | Impact |
|--------|-------------|-----------------|--------|
| BUG-C9 | Escalation threshold too aggressive | Heritage, Grand Vista, Imperial | Simple FAQs escalate to human |
| BUG-C1 | Cross-contamination between hotels (Oberoi venue names in Riverie responses) | Riverie | Incorrect information given |
| BUG-C17 | Debug panel not accessible for Oberoi Udaivilas | Oberoi | Cannot test concierge |

### Medium Severity Bugs

| Bug ID | Description | Affected Hotels |
|--------|-------------|-----------------|
| BUG-C3 | Hotel address/location not in KB | Heritage, Le Patte, Riverie |
| BUG-C5 | Nearby attractions not scraped | Le Patte |
| BUG-C6 | Website content not fully scraped (missing pages) | Heritage, Grand Vista |
| BUG-C7 | On-site restaurant not recognized | Le Patte |
| BUG-C2 | Room types incomplete | Riverie |

### Low Severity Bugs

| Bug ID | Description | Affected Hotels |
|--------|-------------|-----------------|
| BUG-C4 | WiFi information not in KB | Le Patte |
| BUG-C12 | grandvistachiangrai.com has SSL cert issue | Grand Vista |

---

## Recommendations

### Immediate Actions
1. **Re-scrape Heritage Chiang Rai website** — 48 chunks is insufficient. The website has detailed room, dining, facility, and event content that wasn't captured. Try scraping individual pages: /accommodation, /facilities, /dining, etc.

2. **Fix Imperial Mae Ping ingestion** — Try uploading content manually (PDF/TXT) or use a third-party listing URL that the scraper can access (InterContinental's website may block scrapers).

3. **Re-scrape Grand Vista** — 13 chunks too few. The official site has SSL issues; try the Booking.com or Agoda listing pages which have comprehensive hotel info.

4. **Fix Oberoi Debug access** — Investigate why the Debug panel is not available for this hotel.

### Architecture Improvements
5. **Lower escalation confidence threshold** — The AI should attempt to answer from available KB data before escalating. A response like "Based on our available information, [answer]. For more details, please contact our team." is far better than immediate escalation.

6. **Add location/address to all hotel KBs** — This is basic information every guest asks. Ensure the scraper captures contact/location pages.

7. **Implement KB content validation** — After scraping, verify that key topics (rooms, dining, location, amenities) are present in the KB. Flag hotels with gaps.

8. **Fix cross-hotel contamination** — Riverie's conference response mentioned "Chandra Mahal" which is an Oberoi venue. KB vector search may be matching across hotel collections.

---

## Test Automation

All tests are automated using Playwright (Python). Test scripts are in the GitHub repository and can be re-run at any time:

- `deep_concierge_test_v3.py` — Main concierge accuracy test (60 questions across 6 hotels)
- `test_07_kb_files_faq.py` — KB upload/FAQ test suite (19 tests)
- `test_06_deep_riverie.py` — Riverie feature regression tests (16 tests)
- `ingest_missing_hotels.py` — KB website ingestion script
- `check_kb_status.py` — Quick KB chunk count checker

**To run tests:**
```bash
cd /path/to/hotelintelliai-qa-tests
python3 deep_concierge_test_v3.py
```

Results are saved to `reports/concierge_test_results_v3.json` and screenshots in `screenshots/`.

---

## Appendix: Test Questions Source

All test questions were created based on actual content found on each hotel's official website. Expected keywords were extracted from the same source to verify accuracy. This ensures we're testing whether the AI concierge correctly reflects the hotel's own published information.

| Hotel | Website Scraped | Key Info Found |
|-------|----------------|----------------|
| Heritage Chiang Rai | heritagechiangrai.com | 321 rooms, 6 room types, 2 ballrooms, restaurant, pool, spa |
| Oberoi Udaivilas | oberoihotels.com | Suites with private pools, Asmi spa, 4 restaurants, Lake Pichola |
| le Patte | lepattachiangrai.com | 3 room types (32-52sqm), salt pool, Gorilla Gym, 39 rooms |
| Riverie by Katathani | theriverie.com | 8 room types, 271 rooms, water park, Tivaa spa, kids club |
| Grand Vista Chiangrai | grand-vista-chiangrai.gochiangraihotels.com | 80 rooms, saltwater pool, spa, 4-star, airport 5km |
| Imperial Mae Ping | chiangmai.intercontinental.com | 305 rooms, 5 restaurants, ii Spa, check-in 3PM/out 12PM |
