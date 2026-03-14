# HotelIntelliai — Full Usability & QA Test Report

**Date:** March 14, 2026
**Tester:** Anirudha Talmale
**Application:** HotelIntelliai SaaS Platform
**URLs Tested:**
- `onboarding.hotelintelliai.com` — Hotel onboarding portal
- `dashboard.hotelintelliai.com` — Super admin dashboard
- `{hotelid}.hotelintelliai.com` — Hotel-specific command centers

**Credentials Used:** `anirudhatomeiz@gmail.com` / `CHANGEME`

---

## Executive Summary

The HotelIntelliai platform is a well-designed SaaS application for hotel onboarding and AI concierge management. The core onboarding wizard, KB management (FAQ/file upload), and dashboard command center work reliably. A **deep dive into The Riverie by Katathani** (per client request) confirmed that most dashboard features display data correctly, but uncovered additional UX and data issues. In total, **11 bugs** were found — 2 critical, 5 moderate, and 4 minor. The most impactful issues are the **Guest Lookup backend error** and the **scraper embedding invalid content**.

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 2 | Needs fix before launch |
| Moderate | 5 | Should fix soon |
| Minor | 4 | Nice to fix |

**Note:** le Patte data is acknowledged by the client as incomplete. le Patte-specific bugs (BUG-004, BUG-005) may be expected behavior for an incomplete hotel setup.

---

## Test Scope

### Modules Tested
1. **Authentication** — Login/logout for both portals
2. **Hotel Management** — Listing, creation wizard (4-step), deletion
3. **Knowledge Base** — File upload, URL scraping, FAQ entry
4. **Dashboard Command Center** — Overview, Conversations, Guests, Escalations, Channels, KB, Debug
5. **Debug Tools** — Health Check, RAG Tester, Msg Simulator, DB Stats, Guest Lookup
6. **Staff Management** — Invite, roles, current/pending lists
7. **Channel Configuration** — Toggle switches, webhook status

---

## Bug Report

### BUG-001: URL Scraping — WebSocket Disconnects + Embeds Invalid Content [CRITICAL → MODERATE UX + CRITICAL data]

**Module:** Knowledge Base → URL Tab
**Severity:** Moderate (UX) + Critical (data quality)

**Part A — Misleading UX (Moderate):**
**Steps to Reproduce:**
1. Navigate to any hotel's Knowledge Base → URL tab
2. Enter any valid URL and click "Scrape & Embed"

**Expected:** Progress indicator shows scraping status until completion
**Actual:** Shows "Scraping in progress..." → "⚠ Lost connection to scrape job" — but **scraping actually continues and completes in the background**. Refreshing the KB page after a few minutes shows new documents have been embedded successfully.
**Impact:** Users think scraping failed when it actually works. The WebSocket connection drops before the job finishes, but the backend worker completes successfully.
**Evidence:** Oberoi Udaivilas KB was scraped successfully — 352 chunks created despite "Lost connection" message.
**Screenshot:** `screenshots/74_scrape_lost.png`, `screenshots/R23_oberoi_kb_check.png`

**Part B — Scraper Embeds 404 Error Pages (Critical):**
**Steps to Reproduce:**
1. Scrape a URL that contains links to non-existent pages
2. Check the KB documents list

**Expected:** Scraper should validate HTTP responses and skip error pages
**Actual:** The scraper followed links to pages returning HTTP 404 and embedded their error page content. The Oberoi KB contains **87 chunks from a "404 Not Found" page** — including generic error text like "The page you were looking for could not be found."
**Impact:** Pollutes the hotel KB with garbage content. When guests ask the AI concierge questions, it may retrieve 404 error page text as "knowledge" and provide nonsensical responses.
**Screenshot:** `screenshots/R23_oberoi_kb_check.png`

---

### BUG-002: Guest Lookup — Backend Import Error [CRITICAL]

**Module:** Dashboard → Debug → Guest Lookup
**Severity:** Critical
**Steps to Reproduce:**
1. Go to any hotel's command center
2. Navigate to Debug → Guest Lookup
3. Enter any identifier (e.g., "njain2000")
4. Click "Lookup"

**Expected:** Guest profile information is displayed
**Actual:** Error: `⚠ cannot import name 'GuestChannel' from 'src.models.schemas' (/app/src/models/schemas.py)`
**Impact:** Guest lookup feature is completely non-functional. The Python backend is missing the `GuestChannel` class in its schema definitions.
**Screenshot:** `screenshots/48_guest_lookup_result.png`

---

### BUG-003: Dashboard KB Shows "No hotel assigned" [MODERATE]

**Module:** Dashboard → Knowledge Base (sidebar)
**Severity:** Moderate
**Steps to Reproduce:**
1. Log in to dashboard.hotelintelliai.com
2. Select any hotel (le Patte or Riverie)
3. Click "Knowledge Base" in the sidebar

**Expected:** KB content for the selected hotel is displayed
**Actual:** Shows "No hotel assigned to your account."
**Note:** The KB works correctly on the **onboarding portal** (`onboarding.hotelintelliai.com/hotel/{id}/kb`), but NOT on the dashboard command center. Likely a permission/context issue where the dashboard KB page doesn't resolve the hotel from the subdomain.
**Screenshot:** `screenshots/51_lepatte_kb_dashboard.png`

---

### BUG-004: le Patte — Data Inconsistency (Messages vs Conversations) [MODERATE]

**Module:** Dashboard → le Patte Command Center
**Severity:** Moderate
**Steps to Reproduce:**
1. Select le Patte from the dashboard
2. View Overview page: shows **MESSAGES: 36** and **ESCALATIONS: 4**
3. Click Conversations: shows **0 total**
4. Click Escalations: shows **0 open**

**Expected:** If there are 36 messages, there should be conversations. If there are 4 escalations in Overview, Escalations page should also show 4.
**Actual:** Overview stats don't match the detail pages. Messages exist in the DB but aren't associated with conversations for this hotel.
**Impact:** Confusing for hotel staff — dashboard shows activity but detail pages are empty.
**Screenshot:** `screenshots/25_lepatte_dashboard.png`, `screenshots/50_lepatte_conversations.png`

---

### BUG-005: le Patte — All Channels Show "off" in Dashboard [MODERATE]

**Module:** Dashboard → le Patte → Channels
**Severity:** Moderate
**Steps to Reproduce:**
1. Select le Patte from the dashboard
2. Click "Channels" in sidebar

**Expected:** Channels should show live status matching the onboarding portal (whatsapp, telegram, line, email, web all configured)
**Actual:** All 5 channels show "off" with no webhook URLs
**Note:** The onboarding portal correctly shows these channels as active on le Patte's card. The dashboard's channel status doesn't reflect the actual configuration.
**Screenshot:** `screenshots/52_lepatte_channels.png`

---

### BUG-006: Conversation Threads Show "No messages" — All Conversations [MODERATE]

**Module:** Dashboard → Conversations
**Severity:** Moderate (upgraded from Minor after deep testing)
**Steps to Reproduce:**
1. Go to Riverie command center → Conversations
2. Click on **any** conversation thread

**Expected:** Message history is displayed in the thread panel
**Actual:** Shows "No messages" for **every single conversation** tested. Deep-tested all 8 Riverie conversations (nick jain, njain2000, njain200, njain20, njain2, njain, Anirudha) — all show "No messages" in the thread panel.
**Impact:** Staff cannot view any conversation history from the dashboard. This is a significant functional gap — the messages exist in the DB (36 total per overview stats) but are never loaded into the thread view.
**Screenshot:** `screenshots/36_conversation_thread.png`, `screenshots/R02_conv_nick_jain.png`, `screenshots/R03_conv_njain_0.png`

---

### BUG-007: Duplicate Pending Invites Allowed [MINOR]

**Module:** Onboarding → Staff Management
**Severity:** Minor
**Steps to Reproduce:**
1. Go to le Patte → Staff
2. Observe Pending Invites section

**Current State:** 6 pending invites, most to `njain2000@gmail.com` with overlapping roles and identical expiration dates
**Expected:** System should prevent duplicate invites to the same email with the same role, or at least warn
**Impact:** Clutters the staff list; invitee may receive multiple invitation emails
**Screenshot:** `screenshots/07_le_patte_staff.png`

---

### BUG-008: Overview Charts Show "No data" Despite Having Data [MODERATE]

**Module:** Dashboard → Overview
**Severity:** Moderate
**Steps to Reproduce:**
1. Go to Riverie command center → Overview
2. Observe the "Conversations / Day" chart area
3. Observe the "By Channel" chart area

**Expected:** Charts should display data visualization based on the 8 conversations and 36 messages
**Actual:** Both chart areas show "No data" — no graph, no chart, just empty placeholder text
**Impact:** Hotel managers cannot see conversation trends or channel distribution. The stats counters at the top (8 conversations, 36 messages) show data exists, but the visual charts don't render it.
**Screenshot:** `screenshots/R01_overview.png`

---

### BUG-009: VIP Tab Doesn't Filter Guests [MINOR]

**Module:** Dashboard → Guests
**Severity:** Minor
**Steps to Reproduce:**
1. Go to Riverie command center → Guests
2. Click the "ALL" tab — shows 4 guests
3. Click the "VIP" tab

**Expected:** VIP tab should filter to show only VIP-tier guests
**Actual:** VIP tab shows the exact same 4 guests as the ALL tab. No filtering occurs.
**Impact:** VIP guest segmentation is non-functional. Staff cannot quickly identify high-priority guests.
**Screenshot:** `screenshots/R04_guests.png`, `screenshots/R05_guests_vip.png`

---

### BUG-010: Guest Profiles Not Clickable — No Detail View [MINOR]

**Module:** Dashboard → Guests
**Severity:** Minor
**Steps to Reproduce:**
1. Go to Riverie command center → Guests
2. Click on any guest row (e.g., "nick jain")

**Expected:** Clicking a guest should open a detailed profile view with full preferences, conversation history, and activity
**Actual:** Guest rows are not clickable. No drill-down to individual guest details. The guest list is read-only.
**Impact:** Staff can see summary guest info but cannot access detailed profiles for personalized service.
**Screenshot:** `screenshots/R06_guest_profile_nick.png`

---

### BUG-011: Escalation Items Not Expandable — No Detail View [MINOR]

**Module:** Dashboard → Escalations
**Severity:** Minor
**Steps to Reproduce:**
1. Go to Riverie command center → Escalations
2. See 4 open escalation tickets listed
3. Click on any escalation item

**Expected:** Clicking an escalation should expand it or open a detail view with conversation context, resolution options, and assignment
**Actual:** Escalation items are not clickable or expandable. They display severity and summary text but cannot be acted upon from the dashboard.
**Impact:** Staff can see escalations exist but cannot manage, assign, or resolve them from this view.
**Screenshot:** `screenshots/R07_escalations.png`, `screenshots/R08_escalation_detail.png`

---

## Deep Dive: The Riverie by Katathani

A thorough deep test of the Riverie hotel was performed per client request. Here is a summary of all modules tested:

### Overview
- Stats: 8 conversations, 4 guests, 36 messages, 4 escalations — **all correct**
- Charts (Conversations/Day, By Channel): **"No data"** — see BUG-008

### Conversations
- 8 conversations listed with correct channel icons and timestamps
- **All 8 threads tested** — every single one shows "No messages" — see BUG-006

### Guests
- 4 guests displayed: nick jain (VIP), Anirudha (Standard), njain2000 (Standard), njain200 (Standard)
- Guest cards show tier, preferences, language correctly
- VIP filter broken — see BUG-009
- Guest profiles not clickable — see BUG-010

### Escalations
- 4 open tickets displayed with severity levels
- Items not actionable — see BUG-011

### Channels
- WhatsApp: **live** — webhook URL displayed
- Telegram: **live** — webhook URL displayed
- LINE: **live** — webhook URL displayed
- Email: **live** — webhook URL displayed
- Web: **off** (no webhook URL)
- All channel statuses **correct and matching** the onboarding configuration

### Debug Tools (All Working)
- **Health Check:** Hotel healthy, DB record found, Qdrant connected, KB v7, 450 vectors
- **RAG Tester:** Multiple queries tested — returns ranked results with similarity scores (top_k=3, threshold=0.3)
- **Msg Simulator:** AI concierge responds correctly — tested spa query (detailed Tivaa Ratrii Spa response in 5.23s), check-in/out times, Arabic language query (responded in Arabic)
- **DB Stats:** PostgreSQL tables (hotels=3, guests=4, conversations=8, messages=36, escalations=4) + 3 Qdrant collections
- **Guest Lookup:** Broken — see BUG-002

### Knowledge Base (via Onboarding Portal)
- 450 chunks, 11 documents, KB version 7
- File uploads working, FAQ creation working
- URL scraping has issues — see BUG-001

---

## Features Working Correctly

| Feature | Status | Notes |
|---------|--------|-------|
| Login (email/password) | ✅ Pass | Both portals |
| Google OAuth button | ✅ Present | Redirects to Google |
| Hotel listing | ✅ Pass | Shows all hotels with channels |
| Onboarding wizard (4 steps) | ✅ Pass | Validation, navigation, review all work |
| Channel toggles (Step 2) | ✅ Pass | Custom CSS toggles, Web on by default |
| Agent personality selection | ✅ Pass | 3 options + escalation email |
| Hotel launch/provisioning | ✅ Pass | Creates hotel, KB collection, channels |
| KB — File upload tab | ✅ Pass | Drag-drop area, supported formats listed |
| KB — FAQ creation | ✅ Pass | Categories, question/answer, embedding works |
| KB — Document listing | ✅ Pass | Shows chunks, type, date, remove button |
| Dashboard — Hotel selection | ✅ Pass | Cards with channels, redirects to subdomain |
| Dashboard — Overview stats | ✅ Pass | Conversations, guests, messages, escalations |
| Dashboard — Guests page | ✅ Pass | Profiles, tiers, preferences, language |
| Dashboard — Escalations | ✅ Pass | Open tickets with severity |
| Dashboard — Channels page | ✅ Pass | Webhook URLs and live/off status (Riverie) |
| Debug — Health Check | ✅ Pass | DB record, Qdrant connection, vector count |
| Debug — RAG Tester | ✅ Pass | Returns ranked results with scores |
| Debug — Msg Simulator | ✅ Pass | AI response with intent, language, elapsed time |
| Debug — DB Stats | ✅ Pass | PostgreSQL tables + Qdrant collections |
| Staff — Invite form | ✅ Pass | Email + role dropdown + send button |
| Staff — Role management | ✅ Pass | Hotel Admin / Hotel Staff roles |
| Sign Out | ✅ Pass | Returns to login page |

---

## Automated Test Suite

**Location:** `test-scripts/`
**Framework:** Playwright + Pytest
**Total Tests:** 51
**Coverage:** Authentication, Hotel Management, Knowledge Base, Dashboard, Staff

### How to Run

```bash
# Install dependencies
pip install pytest pytest-html playwright
playwright install chromium

# Run all tests with HTML report
pytest -v --html=report.html --self-contained-html

# Run specific test file
pytest test_01_auth.py -v

# Run specific test class
pytest test_02_hotel_management.py::TestOnboardingWizard -v
```

### Test Files

| File | Tests | Covers |
|------|-------|--------|
| `test_01_auth.py` | 8 | Login, logout, invalid credentials, empty form |
| `test_02_hotel_management.py` | 15 | Hotel listing, wizard steps 1-4, validation, navigation |
| `test_03_knowledge_base.py` | 8 | KB stats, file/URL/FAQ tabs, categories, documents |
| `test_04_dashboard.py` | 13 | Hotel selection, command center pages, debug tools |
| `test_05_staff.py` | 7 | Staff listing, roles, invites, new hotel empty state |

### Configuration

- `conftest.py` — Shared fixtures (browser, context, page, logged-in sessions)
- `pytest.ini` — Pytest config with HTML report generation
- `requirements.txt` — Python dependencies

---

## Recommendations

### Priority 1 (Fix Before Launch)
1. **Fix scraper content validation** — Scraper embeds 404 error pages into the KB. Add HTTP status code checking — skip pages that return 4xx/5xx responses. Also add a way to remove/purge bad documents from the KB.
2. **Fix Guest Lookup** — Add the missing `GuestChannel` class to `src/models/schemas.py`.
3. **Fix scraping WebSocket UX** — The WebSocket disconnects during long scrapes, showing "Lost connection" even though scraping succeeds in the background. Either keep the WebSocket alive or show a proper "Scraping in progress, you can close this page" message.

### Priority 2 (Fix Soon)
4. **Fix conversation thread loading** — All conversation threads show "No messages" across every conversation tested (8/8 in Riverie). Messages exist in DB (36) but aren't rendered in the thread panel.
5. **Fix dashboard KB page** — Ensure the subdomain-based dashboard resolves the hotel context for the KB section.
6. **Fix Overview charts** — "Conversations / Day" and "By Channel" charts show "No data" despite having 8 conversations across multiple channels.
7. **Investigate le Patte data inconsistency** — Messages/escalations exist in DB but aren't linked to conversations (client acknowledged le Patte data is incomplete).
8. **Fix le Patte channel status** — Dashboard should reflect the actual channel configuration from the onboarding setup.

### Priority 3 (Improvements)
9. **Fix VIP tab filtering** — Currently shows same guests as ALL tab.
10. **Add guest profile drill-down** — Guest rows should be clickable to show detailed profile views.
11. **Add escalation management** — Escalation items should be clickable/expandable with resolution and assignment options.
12. **Prevent duplicate staff invites** — Add validation to block re-inviting the same email with the same role.
13. **Add channel edit capability post-onboarding** — Currently no way to modify channels after initial setup.

---

## Test Environment

- **Browser:** Chromium (headless, via Playwright)
- **Viewport:** 1280 x 720
- **Test Date:** March 14, 2026
- **Existing Hotels:** le Patte (lePatte), The Riverie by Katathani (hotel_riviera_cr)
- **Hotel Created During Test:** The Oberoi Udaivilas (oberoi_udaivilas)
