# AI Concierge Deep Test Report
## HotelIntelliai - Concierge Accuracy Testing
**Date:** March 26, 2026
**Tester:** Anirudha Talmale
**Method:** Automated Playwright testing via Msg Simulator on dashboard.hotelintelliai.com

---

## Executive Summary

Tested 30 questions across 2 hotels (15 per hotel) using the Msg Simulator on the Debug page. Questions were crafted from actual hotel website content to verify the AI concierge provides accurate, factual responses.

| Hotel | Chunks | GOOD | PARTIAL | POOR | NO_INFO | NO_RESPONSE | Accuracy |
|-------|--------|------|---------|------|---------|-------------|----------|
| The Oberoi Udaivilas | 269 | 0 | 2 | 3 | 4 | 6 | 4.4% |
| The Riverie by Katathani | 162 | 5 | 0 | 1 | 4 | 5 | 33.3% |
| **OVERALL** | | **5/30** | **2** | **4** | **8** | **11** | **16.7%** |

**Le Patte:** Could not test - KB ingestion fails with error "Hotel 'lepatte' not found" (case-sensitivity bug in scraper)

---

## Issue Categories

### 1. NO_RESPONSE (11 out of 30 = 37%)
The simulator did not return any agent response within the timeout window. This may indicate:
- Backend processing timeout
- Queue congestion
- API endpoint errors

### 2. NO_INFO (8 out of 30 = 27%)
The AI explicitly says "I don't have information" despite the content existing on the hotel's website. This means the KB ingestion did not capture this content, OR the RAG retrieval is not finding relevant chunks.

### 3. POOR Accuracy (4 out of 30 = 13%)
The AI responds but with incorrect or generic information that doesn't match the hotel's specific details.

### 4. GOOD Responses (5 out of 30 = 17%)
Accurate, detailed responses with correct hotel-specific information.

---

## Hotel 1: The Oberoi Udaivilas (269 chunks)
**Overall: 0/15 GOOD (0% accuracy)**

### Questions & Results

| # | Category | Question | Quality | Notes |
|---|----------|----------|---------|-------|
| 1 | Rooms | What types of rooms and suites do you offer? | NO_RESPONSE | No response from simulator |
| 2 | Dining | What restaurants do you have? | NO_INFO | AI says it doesn't have restaurant details. Website lists: Suryamahal, Chandni, Mewar by Vineet, The Bar, The Promenade |
| 3 | Spa | Tell me about the spa facilities | NO_RESPONSE | No response from simulator |
| 4 | Pool | Do you have a swimming pool? | PARTIAL (33%) | Says "yes" with generic info but missing details: temperature-controlled, Mughal design |
| 5 | Activities | What experiences and activities can I do? | POOR (0%) | Mentions garden walks but misses: yoga, painting school, cook with chef, lakeside dinner |
| 6 | Location | Where is the hotel and how to get from airport? | NO_INFO | AI doesn't have location info. Website says: Lake Pichola, Maharana Pratap Airport 27km |
| 7 | Events | Can you host a wedding or conference? | NO_RESPONSE | No response from simulator |
| 8 | Awards | What awards has the hotel won? | PARTIAL (33%) | Mentions some awards but misses Conde Nast and Michelin Keys specifically |
| 9 | Attractions | What nearby attractions can I visit? | POOR (0%) | Generic response, misses: City Palace, Jagdish Temple, Kumbhalgarh, Ranakpur |
| 10 | Fitness | Do you have a fitness center? | NO_RESPONSE | No response from simulator |
| 11 | Contact | What is the phone number and email? | POOR (0%) | Gives generic Oberoi group email, not the specific +91 294 2433300 |
| 12 | Property | How large is the hotel property? | NO_INFO | Website says 121,000 sqm / 30 acres |
| 13 | Management | Who is the general manager? | NO_INFO | Website says Amit Kaul |
| 14 | Premium Room | Tell me about the Kohinoor Suite | NO_RESPONSE | No response from simulator |
| 15 | Lakeside Dining | Can I dine by the lake? | NO_RESPONSE | No response from simulator |

### Key Finding - Oberoi
Despite 269 chunks in KB, the AI cannot answer most questions accurately. The scraped content appears to be missing critical sections of the Oberoi website (restaurant names, room details, contact info, location). The scraper may have only captured a subset of the website pages.

---

## Hotel 2: The Riverie by Katathani (162 chunks)
**Overall: 5/15 GOOD (33% accuracy)**

### Questions & Results

| # | Category | Question | Quality | Notes |
|---|----------|----------|---------|-------|
| 1 | Rooms | What types of rooms do you have? | GOOD (100%) | Correctly lists all room types with sizes |
| 2 | Pool/Water Park | Do you have a water park? | NO_RESPONSE | No response from simulator |
| 3 | Kids | Do you have facilities for children? | NO_RESPONSE | No response from simulator |
| 4 | Events | Can you host conferences? | NO_RESPONSE | No response from simulator |
| 5 | Location | Where is the hotel located? | NO_INFO | AI doesn't know. Website says: 1129 Kraisorasit Rd, Chiang Rai 57000 |
| 6 | Contact | What is the hotel phone number? | NO_INFO | AI doesn't know. Website says: +66 53 607999 |
| 7 | Spa | Do you have a spa? | NO_INFO | AI doesn't know despite spa being listed on website |
| 8 | Awards | What awards has the hotel won? | GOOD (100%) | Correctly mentions Thailand Tourism Awards 2025 |
| 9 | Theme | What is the cultural theme? | GOOD (100%) | Correctly identifies Lanna/Northern Thai theme |
| 10 | Transport | Do you offer airport transfer? | NO_INFO | AI doesn't have this info |
| 11 | Room Detail | Tell me about the Deluxe River room | NO_RESPONSE | No response from simulator |
| 12 | Dining | What dining options are available? | GOOD (100%) | Correctly names "The Peak Wine & Grill" |
| 13 | Premium Room | Do you have a Royal Suite? | GOOD (100%) | Correctly describes 291 sqm with Jacuzzi |
| 14 | Booking | What is the email to book? | POOR (0%) | Doesn't know booking@theriverie.com |
| 15 | Event Venue | Is there a poolside terrace? | NO_RESPONSE | No response from simulator |

### Key Finding - Riverie
Better than Oberoi with some excellent responses (rooms, awards, theme, dining, royal suite). However, basic information like location, phone number, spa, and contact email are missing from the KB. The ingestion captured some pages well but missed others.

---

## Le Patte (0 chunks) - BLOCKED

### Bug Found
When attempting to ingest le Patte's website via the URL scraper:
- Error message: "Hotel 'lepatte' not found"
- The collection ID is "lePatte" (camelCase) but the scraper converts to lowercase "lepatte"
- This is a case-sensitivity bug in the hotel lookup during scraping
- Additionally, lepatte.com appears to be down (ECONNREFUSED), which would prevent scraping even if the ID issue is fixed

---

## Critical Issues Found

### BUG-001: Simulator Timeout / No Response (HIGH)
37% of questions (11/30) received no response at all from the simulator. The "Simulate" button was clicked but no "AGENT RESPONSE" appeared within 30 seconds.

### BUG-002: KB Content Gaps (HIGH)
Despite successful scraping (269 chunks for Oberoi, 162 for Riverie), many basic hotel details are not retrievable:
- Contact phone numbers
- Location/address
- Spa information
- Event facilities

This suggests either:
- The scraper is not capturing all website pages/sections
- The text extraction is missing content from certain page layouts
- The embedding/retrieval (RAG) is not finding relevant chunks

### BUG-003: Le Patte Hotel ID Case Sensitivity (MEDIUM)
The scraper fails for Le Patte because "lePatte" is lowercased to "lepatte" which doesn't match the hotel record.

### BUG-004: Generic Fallback Responses (MEDIUM)
When the AI lacks specific info, it gives generic responses instead of escalating. For example, asking about Oberoi restaurants returns "I don't have the specific restaurant details" instead of connecting to staff. The escalation feature doesn't trigger on these "I don't know" responses.

---

## Recommendations

1. **Fix simulator reliability** - 37% no-response rate makes the system unreliable. Investigate backend timeout/queue issues.

2. **Improve scraper depth** - Current scraping misses key pages. Consider scraping all linked sub-pages (rooms, dining, facilities, contact pages) not just the homepage.

3. **Fix le Patte hotel ID lookup** - Make the hotel lookup case-insensitive.

4. **Configure escalation triggers** - When AI says "I don't have information," it should escalate to human staff rather than giving a generic "check the website" response.

5. **Add content validation** - After ingestion, verify that key information categories (rooms, dining, contact, location) are present in the KB.

---

## Test Automation

All tests are automated using Playwright + Python. Test script: `deep_concierge_test_v8.py`
Results JSON: `reports/concierge_test_v8_results.json`
Screenshots: `screenshots/v8/` (60 screenshots capturing before/after each question)

To rerun: `python3 deep_concierge_test_v8.py`
