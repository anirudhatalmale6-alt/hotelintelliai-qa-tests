# AI Concierge Accuracy Report — All Hotels

**Date**: 2026-03-22
**Test Method**: Playwright automation via Msg Simulator (Debug panel)
**Questions**: 10 common hotel questions per hotel
**Hotels Tested**: 4 (2 skipped — 0 KB chunks)

---

## Overall Results: 21/40 GOOD (52%)

| Hotel | KB Chunks | GOOD | NO_INFO | ESCALATED | Score |
|-------|-----------|------|---------|-----------|-------|
| Heritage Chiang Rai | 49 | 1 | 0 | 9 | 10% |
| Oberoi Udaivilas | 352 | 6 | 3 | 1 | 60% |
| le Patte | 306 | 5 | 2 | 3 | 50% |
| Riverie by Katathani | 467 | 9 | 0 | 1 | 90% |

**Hotels Skipped** (0 KB chunks): Grand Vista Chiangrai, Imperial Mae Ping

---

## Key Findings

### 1. KB Size Directly Correlates with Accuracy
- Riverie (467 chunks, 28 docs) → 90% accuracy
- Oberoi (352 chunks, 3 docs) → 60% accuracy
- le Patte (306 chunks, 2 docs) → 50% accuracy
- Heritage (49 chunks, 1 doc) → 10% accuracy

### 2. WiFi Question Fails Across ALL Hotels
Every hotel escalated the WiFi question to human support. This suggests WiFi info is not being captured during website scraping or is not present on hotel websites.

### 3. Heritage Chiang Rai Has Insufficient KB
With only 49 chunks from 1 document, 9/10 questions trigger the escalation fallback. More website content or FAQ entries are needed.

### 4. Escalation Behavior is Graceful
When the AI doesn't know the answer, it responds with: "I want to make sure you get the best possible answer. Let me connect you with our team who can help you directly." — This is professional and not an error.

### 5. Topics Consistently Missing from KB

| Topic | Heritage | Oberoi | le Patte | Riverie |
|-------|----------|--------|----------|---------|
| Check-in/out | ESCALATED | NO_INFO | ESCALATED | GOOD |
| Rooms | ESCALATED | GOOD | GOOD | GOOD |
| Pool | ESCALATED | GOOD | GOOD | GOOD |
| Spa | ESCALATED | GOOD | NO_INFO | GOOD |
| Dining | ESCALATED | GOOD | GOOD | GOOD |
| Airport | ESCALATED | GOOD | ESCALATED | GOOD |
| Fitness | ESCALATED | GOOD | GOOD | GOOD |
| Cancellation | ESCALATED | NO_INFO | ESCALATED | GOOD |
| WiFi | ESCALATED | ESCALATED | ESCALATED | ESCALATED |
| Breakfast | ESCALATED | NO_INFO | NO_INFO | GOOD |

---

## Recommendations

### Critical
1. **Add WiFi info to all hotel KBs** — FAQ entry or website scrape update needed
2. **Enrich Heritage Chiang Rai KB** — Only 49 chunks; add more website pages, FAQs, or documents

### Important
3. **Add check-in/checkout times** as FAQ entries for Oberoi and le Patte
4. **Add cancellation policy** as FAQ entries for Oberoi and le Patte
5. **Add breakfast info** as FAQ entries for Oberoi and le Patte
6. **Add airport transfer info** for le Patte

### Nice to Have
7. **Add spa info** for le Patte (currently NO_INFO)
8. **Onboard Grand Vista and Imperial Mae Ping** — both have 0 KB chunks

---

## Test Scripts

- `deep_concierge_test_v3.py` — Standalone test (runs all 40 questions, generates JSON report)
- `test-scripts/test_08_concierge_accuracy.py` — Pytest/Playwright automated tests (22 test cases)

## Files Generated

- `reports/concierge_test_results_v3.json` — Raw test results
- `screenshots/V3_*.png` — Screenshots of every question/response
