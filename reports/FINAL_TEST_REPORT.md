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

The HotelIntelliai platform is a well-designed SaaS application for hotel onboarding and AI concierge management. The core onboarding wizard, KB management (FAQ/file upload), and dashboard command center work reliably. However, **7 bugs** were found — 2 critical, 3 moderate, and 2 minor. The most impactful issues are the **URL scraping failure** and the **Guest Lookup backend error**.

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 2 | Needs fix before launch |
| Moderate | 3 | Should fix soon |
| Minor | 2 | Nice to fix |

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

### BUG-001: URL Scraping Fails — "Lost connection to scrape job" [CRITICAL]

**Module:** Knowledge Base → URL Tab
**Severity:** Critical
**Steps to Reproduce:**
1. Navigate to any hotel's Knowledge Base
2. Click the "URL" tab
3. Enter any valid URL (tested: `https://www.oberoihotels.com/...`, `https://www.theriverie.com`)
4. Click "Scrape & Embed"

**Expected:** Website is scraped, content is embedded into the KB
**Actual:** Shows "Scraping in progress..." → "Scraping started, this may take a few minutes..." → "⚠ Lost connection to scrape job"
**Impact:** Hotels cannot be populated with website content automatically — core onboarding functionality is broken
**Screenshot:** `screenshots/74_scrape_lost.png`

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

### BUG-006: Conversation Threads Show "No messages" [MINOR]

**Module:** Dashboard → Conversations
**Severity:** Minor
**Steps to Reproduce:**
1. Go to Riverie command center → Conversations
2. Click on any conversation (e.g., "nick jain" or "njain2000")
3. Thread panel opens on the right

**Expected:** Message history is displayed in the thread panel
**Actual:** Shows "No messages" for all conversations tested
**Impact:** Staff cannot view conversation history from the dashboard
**Screenshot:** `screenshots/36_conversation_thread.png`, `screenshots/49_njain_thread.png`

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
1. **Fix URL scraping** — The WebSocket connection drops during scraping. Check backend scrape worker logs and ensure the connection stays alive for long-running scrapes.
2. **Fix Guest Lookup** — Add the missing `GuestChannel` class to `src/models/schemas.py`.

### Priority 2 (Fix Soon)
3. **Fix dashboard KB page** — Ensure the subdomain-based dashboard resolves the hotel context for the KB section.
4. **Investigate le Patte data inconsistency** — Messages/escalations exist in DB but aren't linked to conversations.
5. **Fix le Patte channel status** — Dashboard should reflect the actual channel configuration from the onboarding setup.

### Priority 3 (Improvements)
6. **Show message history in conversation threads** — The thread panel always shows "No messages".
7. **Prevent duplicate staff invites** — Add validation to block re-inviting the same email with the same role.
8. **Add channel edit capability post-onboarding** — Currently no way to modify channels after initial setup.

---

## Test Environment

- **Browser:** Chromium (headless, via Playwright)
- **Viewport:** 1280 x 720
- **Test Date:** March 14, 2026
- **Existing Hotels:** le Patte (lePatte), The Riverie by Katathani (hotel_riviera_cr)
- **Hotel Created During Test:** The Oberoi Udaivilas (oberoi_udaivilas)
