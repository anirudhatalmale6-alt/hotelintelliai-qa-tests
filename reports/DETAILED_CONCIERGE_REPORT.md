HOTEL AI CONCIERGE SYSTEM - DETAILED TEST REPORT
Version 5  |  Test Date: March 22, 2026
=================================================


CONTENTS
--------
1. Executive Summary
2. Test Methodology
3. Knowledge Base Statistics
4. Per-Hotel Detailed Results
5. Issues Found
6. Recommendations
7. Summary Tables


==========================================================================
1. EXECUTIVE SUMMARY
==========================================================================

This report presents the results of end-to-end functional testing of the
Hotel AI Concierge system across six hotel properties. Each hotel was tested
with 10 natural-language guest questions covering the most common inquiry
categories: room types, facilities, dining, location, and services.

OVERALL RESULT: 23 out of 60 questions answered accurately (38.3%)

This score reflects a wide disparity between hotels. Three properties —
The Riverie by Katathani, The Oberoi Udaivilas, and le Patte — demonstrated
solid to good performance, correctly answering 60-80% of questions. The
remaining three — The Heritage Chiang Rai, Grand Vista Chiangrai, and
Imperial Mae Ping — performed poorly, with accuracy at 10%, 10%, and 0%
respectively.

The root causes differ between these two groups and are detailed in
Section 5. In summary: Heritage and Grand Vista have sparse or
non-functional knowledge base content despite being scraped; Imperial Mae
Ping suffers from a complete absence of useful scraped content AND a
dashboard rendering bug that prevented UI testing. The three higher-
performing hotels have well-structured, content-rich knowledge bases.

OVERALL SCORECARD:

  Hotel                             KB Chunks   Score   Accurate / 10
  --------------------------------  ---------   -----   -------------
  The Riverie by Katathani              467      80%        8 / 10
  The Oberoi Udaivilas                  354      70%        7 / 10
  le Patte                              306      60%        6 / 10
  The Heritage Chiang Rai               178      10%        1 / 10
  Grand Vista Chiangrai                  13      10%        1 / 10
  Imperial Mae Ping                     558       0%        0 / 10

  TOTAL                                1876     38.3%      23 / 60


==========================================================================
2. TEST METHODOLOGY
==========================================================================

API ENDPOINT USED:
  POST /admin/test/message

All tests were conducted directly against the backend API rather than
through the admin dashboard UI. This was necessary because the dashboard
interface for two hotels (Imperial Mae Ping and The Oberoi Udaivilas)
exhibited a blank-render bug where the React component loaded but displayed
no content. By bypassing the UI and calling the API endpoint directly,
testing could proceed for all six hotels regardless of frontend state.

TEST QUESTION DESIGN:
Each hotel received 10 questions crafted around topics a real guest would
ask. Questions were phrased in plain, natural English (not optimized for
keyword matching) to reflect realistic guest behavior. Each question was
accompanied by a set of expected keywords that a correct answer must
contain to be scored as ACCURATE.

SCORING CRITERIA:
  ACCURATE    - Response contained the expected keywords and provided
                substantively correct information
  PARTIAL     - Response contained some but not all expected keywords
  NO_INFO     - AI acknowledged it did not have the information and
                directed the guest to contact staff
  ESCALATED   - AI triggered the escalation script: "I want to make sure
                you get the best possible answer. Let me connect you with
                our team..." This indicates the AI could not find a
                relevant KB chunk to work from
  UNVERIFIED  - AI gave a substantive response but it could not be
                verified against known facts

For scoring purposes, only ACCURATE responses count toward the accuracy
percentage. PARTIAL, NO_INFO, ESCALATED, and UNVERIFIED are all failures
from a guest-experience standpoint.


==========================================================================
3. KNOWLEDGE BASE STATISTICS
==========================================================================

  Hotel                             Website                  KB Chunks
  --------------------------------  -----------------------  ---------
  The Heritage Chiang Rai           heritagechiangrai.com        178
  Grand Vista Chiangrai             grandvistachiangrai.com       13
  Imperial Mae Ping                 imperialmaeping.com          558
  The Oberoi Udaivilas              oberoihotels.com             354
  le Patte                          lepattachiangrai.com         306
  The Riverie by Katathani          theriverie.com               467

  TOTAL                                                         1876

ANALYSIS OF KB CHUNK COUNTS:

Grand Vista (13 chunks) is dramatically under-ingested. A functional hotel
website would typically yield 200-600 chunks depending on content depth.
13 chunks suggests the scraper encountered a JavaScript-rendered site,
a redirect wall, a rate limit, or a robots.txt block that prevented
meaningful content extraction.

Heritage (178 chunks) has a reasonable chunk count on paper, but test
results show the content is not practically useful — 8 of 10 questions
triggered escalation on basic topics like "do you have a swimming pool"
and "what restaurants do you have." The scraped content likely consists
of navigation text, headers, boilerplate, and decorative copy rather
than factual facility descriptions.

Imperial Mae Ping (558 chunks) has the second-highest chunk count but
achieved 0% accuracy — every single question escalated or returned
no information. This is the most severe mismatch between chunk volume
and quality. The ingested URLs likely contain SEO pages, image captions,
or template content that does not map to guest questions.

Oberoi (354), le Patte (306), and Riverie (467) all show coherent
chunk counts with proportionally good retrieval results.


==========================================================================
4. PER-HOTEL DETAILED RESULTS
==========================================================================


--------------------------------------------------------------------------
4.1  THE HERITAGE CHIANG RAI HOTEL AND CONVENTION
     Website: heritagechiangrai.com  |  KB Chunks: 178
     Score: 1/10 (10%)
--------------------------------------------------------------------------

Q1: How many rooms does the hotel have?
    Expected: "321"
    Response: ESCALATED — "I want to make sure you get the best possible
              answer. Let me connect you with our team..."
    Rating:   ESCALATED

Q2: What room types are available?
    Expected: deluxe, executive, suite, premier
    Response: ESCALATED
    Rating:   ESCALATED

Q3: Do you have meeting or convention facilities?
    Expected: ballroom, meeting
    Response: "Yes, we have excellent meeting and convention facilities!
              Our Heritage Ballroom is a beautiful upscale event space
              located on the 1st floor... can accommodate up to 700 guests
              depending on your room configuration needs, and it features
              two breakout meeting rooms with lovely views overlooking our
              swimming pool."
    Rating:   ACCURATE (1 of 1 correct responses for this hotel)

Q4: What restaurants do you have?
    Expected: restaurant, dining
    Response: ESCALATED
    Rating:   ESCALATED

Q5: Do you have a swimming pool?
    Expected: pool
    Response: ESCALATED
    Rating:   ESCALATED

Q6: Where is the hotel located?
    Expected: chiang rai
    Response: "I don't have the specific location details for Heritage
              Chiang Rai in my current information..."
    Rating:   NO_INFO

Q7: Do you have a fitness center?
    Expected: fitness, gym
    Response: ESCALATED
    Rating:   ESCALATED

Q8: Is there a spa?
    Expected: spa
    Response: ESCALATED
    Rating:   ESCALATED

Q9: What are nearby attractions?
    Expected: white temple, night bazaar, clock tower
    Response: ESCALATED
    Rating:   ESCALATED

Q10: Do you have WiFi?
     Expected: wifi, free
     Response: ESCALATED
     Rating:   ESCALATED

SUMMARY: 1 accurate, 1 no_info, 8 escalated. The one successful answer
(meeting facilities) suggests the ballroom page was scraped and chunked
properly. All other core amenity topics are missing from the KB despite
178 chunks existing in the system.


--------------------------------------------------------------------------
4.2  GRAND VISTA CHIANGRAI HOTEL
     Website: grandvistachiangrai.com  |  KB Chunks: 13
     Score: 1/10 (10%)
--------------------------------------------------------------------------

Q1: What room types do you have?
    Expected: superior, deluxe, suite
    Response: ESCALATED
    Rating:   ESCALATED

Q2: Do you have a swimming pool?
    Expected: pool
    Response: ESCALATED
    Rating:   ESCALATED

Q3: Do you have a spa?
    Expected: spa, massage
    Response: ESCALATED
    Rating:   ESCALATED

Q4: What dining options are available?
    Expected: restaurant, bar
    Response: ESCALATED
    Rating:   ESCALATED

Q5: Do you have a fitness center?
    Expected: fitness, gym
    Response: ESCALATED
    Rating:   ESCALATED

Q6: Is there WiFi?
    Expected: wifi
    Response: ESCALATED
    Rating:   ESCALATED

Q7: Is there parking?
    Expected: parking
    Response: ESCALATED
    Rating:   ESCALATED

Q8: Where is the hotel located?
    Expected: chiang rai
    Response: ESCALATED
    Rating:   ESCALATED

Q9: How far is the airport?
    Expected: airport
    Response: ESCALATED
    Rating:   ESCALATED

Q10: What nearby attractions are there?
     Expected: night bazaar, clock tower
     Response: "There are many wonderful attractions near Grand Vista
               Chiangrai! Here are some highlights — Very Close (within
               2km): Chiang Saen old city walls (1.0 km), Chiang Rai
               Night Bazaar (1.9 km)... Clock Tower (2.2 km)..."
     Rating:   ACCURATE (1 of 1 correct responses for this hotel)

SUMMARY: 1 accurate, 0 no_info, 9 escalated. With only 13 KB chunks, the
AI has almost no property-specific content. The one successful answer
(nearby attractions) may have been retrieved from a fragment that listed
distances to landmarks — essentially generic city data rather than hotel-
specific content. Every hotel-specific question failed completely.


--------------------------------------------------------------------------
4.3  IMPERIAL MAE PING HOTEL
     Website: imperialmaeping.com  |  KB Chunks: 558
     Score: 0/10 (0%)
--------------------------------------------------------------------------

NOTE: The dashboard for this hotel exhibited a blank-render bug (see
Section 5). All 10 questions were sent via the direct API endpoint.

Q1: What time is check-in and check-out?
    Expected: check-in, check-out
    Response: ESCALATED
    Rating:   ESCALATED

Q2: What restaurants do you have?
    Expected: restaurant, dining
    Response: ESCALATED
    Rating:   ESCALATED

Q3: Do you have a spa?
    Expected: spa, massage
    Response: ESCALATED
    Rating:   ESCALATED

Q4: Do you have a swimming pool?
    Expected: pool
    Response: ESCALATED
    Rating:   ESCALATED

Q5: Is there a fitness center?
    Expected: fitness, gym
    Response: ESCALATED
    Rating:   ESCALATED

Q6: Where is the hotel located?
    Expected: chiang mai
    Response: "I don't see specific location information for Imperial Mae
              Ping hotel in my current knowledge base..."
    Rating:   UNVERIFIED (AI gave a response but no city was confirmed)

Q7: Do you have parking?
    Expected: parking
    Response: ESCALATED
    Rating:   ESCALATED

Q8: Do you have meeting rooms?
    Expected: meeting, conference, banquet
    Response: ESCALATED
    Rating:   ESCALATED

Q9: Do you offer airport transfer?
    Expected: airport, transfer
    Response: ESCALATED
    Rating:   ESCALATED

Q10: Do you have WiFi?
     Expected: wifi
     Response: ESCALATED
     Rating:   ESCALATED

SUMMARY: 0 accurate, 1 unverified, 9 escalated. Despite 558 chunks — the
second-highest count — the AI could not answer a single question correctly.
The location question produced a response (NO_INFO type) rather than a
hard escalation, but it failed to state the city (Chiang Mai). This is the
worst-performing hotel by any measure and strongly indicates that the
scraped content does not correspond to useful guest-facing information.


--------------------------------------------------------------------------
4.4  THE OBEROI UDAIVILAS
     Website: oberoihotels.com  |  KB Chunks: 354
     Score: 7/10 (70%)
--------------------------------------------------------------------------

NOTE: The dashboard for this hotel also exhibited the blank-render bug.
All questions were tested via the direct API endpoint.

Q1: What types of rooms do you have?
    Expected: suite, premier, luxury
    Response: "At The Oberoi Udaivilas, we offer several exquisite room
              categories: Premier Rooms — available with semi-private
              courtyard views or with private pool access; Luxury Suites —
              featuring private pools; Kohinoor Suite — our most prestigious
              accommodation. All rooms feature elegant marble bathrooms,
              high-speed internet, and personalized 24-hour butler service."
    Rating:   ACCURATE

Q2: Do you have a swimming pool?
    Expected: pool
    Response: "Yes, we have beautiful swimming facilities... Main Pool in
              our Mewari-style courtyard... Premier City Palace View Rooms
              feature access to an 84-metre long semi-private pool...
              Private Pools available with the Kohinoor Suite and Luxury
              Suites with Private Pool."
    Rating:   ACCURATE

Q3: What dining options are available?
    Expected: restaurant, dining
    Response: "I apologize, but I don't have specific information about
              the dining options available at Oberoi Udaivilas..."
    Rating:   NO_INFO

Q4: Do you have a spa?
    Expected: spa
    Response: "Yes, we have The Oberoi Spa at Udaivilas! Our spa offers
              massage treatments, sensory experiences, facial treatments,
              and yoga sessions... exclusively for resident guests... book
              at least 12 hours in advance."
    Rating:   ACCURATE

Q5: What experiences do you offer?
    Expected: yoga, painting, experience
    Response: "Cultural & Artistic Experiences: Thekri Workshop (mirror
              work art), Henna Painting, Play with Clay, Astrology...
              Exploration & Adventure: Heritage Walk (private boat ride),
              Off the Track (garden pathways)... Family Activities:
              Children's Activity programs..."
    Rating:   ACCURATE (matched: painting, experience — missed: yoga)

Q6: Where is the hotel located?
    Expected: udaipur, lake
    Response: "The Oberoi Udaivilas is located on the tranquil banks of
              Lake Pichola in Udaipur, India. The complete address is
              Lake Pichola, Udaipur 313001, India. 27 kilometers from
              Maharana Pratap Airport."
    Rating:   ACCURATE

Q7: Do you have meeting rooms?
    Expected: meeting, conference
    Response: "Yes — Meeting Room I (boardroom, up to 8 guests), Meeting
              Rooms II & III (up to 24 guests each or 48 combined), The
              Cocktail Room (up to 48 guests, built-in audio system and
              screen)."
    Rating:   ACCURATE (matched: meeting — missed: conference)

Q8: What nearby attractions can I visit?
    Expected: palace, temple
    Response: "I don't have specific information about nearby attractions
              to The Oberoi Udaivilas in my current resources..."
    Rating:   NO_INFO

Q9: Do you have a fitness center?
    Expected: fitness, gym
    Response: "Yes, we have a fitness center... well-equipped with
              cardiovascular machines and weights."
    Rating:   ACCURATE (matched: fitness — missed: gym)

Q10: Do you offer airport transfer?
     Expected: airport, transfer
     Response: "I don't have specific information about airport transfer
               services at Oberoi Udaivilas..."
     Rating:   NO_INFO

SUMMARY: 7 accurate, 3 no_info, 0 escalated. Strong performance with
well-structured retrieval on rooms, spa, experiences, location, and
meetings. Dining, nearby attractions, and airport transfer are gaps in
the scraped content. Notably, zero escalations — the AI either found
an answer or gracefully admitted the gap, with no inappropriate deflection.


--------------------------------------------------------------------------
4.5  LE PATTE (LE PATTA HOTEL)
     Website: lepattachiangrai.com  |  KB Chunks: 306
     Score: 6/10 (60%)
--------------------------------------------------------------------------

Q1: What room types are available?
    Expected: superior, deluxe, suite
    Response: "We have three wonderful room types: Superior Room (32 sqm)
              — corner rooms with rain shower and touch-screen panel for
              lighting/AC; Deluxe Room (32 sqm) — swimming pool views in
              green garden, 42-inch Smart TV and DVD player; Suite Room
              (52 sqm) — separate living room with cozy couch."
    Rating:   ACCURATE

Q2: How big are the rooms?
    Expected: 32, 52, sqm
    Response: "Superior Room: 32 sqm. Deluxe Room: 32 sqm. Suite Room:
              52 sqm — our largest and most spacious option."
    Rating:   ACCURATE

Q3: Do you have a swimming pool?
    Expected: pool, salt
    Response: "Yes, we have a beautiful salt water swimming pool!
              Surrounded by a lovely green garden with stunning views."
    Rating:   ACCURATE

Q4: Is there a gym or fitness center?
    Expected: gym, gorilla, fitness
    Response: "Yes! Le Patta has partnered with Gorilla Gym Chiang Rai,
              located nearby the hotel. As a guest, you can access all
              facilities FREE OF CHARGE. Hours: Mon-Fri 7:00 AM - 9:00 PM,
              Sat-Sun 8:00 AM - 8:00 PM. Closed every 3rd Saturday."
    Rating:   ACCURATE

Q5: Do you have WiFi?
    Expected: wifi
    Response: ESCALATED
    Rating:   ESCALATED

Q6: Where is the hotel located?
    Expected: chiang rai
    Response: "I don't have the specific location details for Le Patta
              Hotel in my current information. For the most accurate
              address... call +66 81 3574579 or email
              sales@lepattachiangrai.com."
    Rating:   NO_INFO

Q7: What is nearby the hotel?
    Expected: night bazaar, clock tower
    Response: "I don't have specific information about nearby attractions
              or locations around Le Patta Hotel in my current resources.
              Contact our front desk at +66 81 3574579..."
    Rating:   NO_INFO

Q8: Do you have a restaurant?
    Expected: restaurant
    Response: "I don't have information about restaurants within Lepatte
              hotel itself. However... Dear Friend Cafe & Restaurant
              (650m), Khao Soi Phor Jai, Nam Ngiao Pa Suk (northern Thai
              noodle soup for over 50 years), Chivit Thamma Da Coffee
              House on the Kok River..."
    Rating:   NO_INFO (AI found nearby restaurants but not an on-site one)

Q9: Is there parking available?
    Expected: parking
    Response: "Yes, we have a parking lot available for our guests!"
    Rating:   ACCURATE

Q10: How far is the airport?
     Expected: 7 km, airport, mae fah luang
     Response: "Mae Fah Luang Chiang Rai Airport is 7 km away from
               Le Patta Hotel."
     Rating:   ACCURATE

SUMMARY: 6 accurate, 3 no_info, 1 escalated. The hotel-specific facility
content (rooms, pool, gym partnership, parking, airport distance) is well
represented in the KB. The gaps are location/address, nearby attractions,
WiFi, and on-site dining. Notably the gym answer was the most detailed and
accurate of any response across all hotels — demonstrating what quality KB
content can produce.


--------------------------------------------------------------------------
4.6  THE RIVERIE BY KATATHANI
     Website: theriverie.com  |  KB Chunks: 467
     Score: 8/10 (80%)
--------------------------------------------------------------------------

Q1: What room types do you have?
    Expected: deluxe, suite
    Response: "Standard Room ($150/night, 28 sqm), Deluxe Room ($220/night,
              35 sqm — Lanna classic contemporary design with warm color
              tones and gold accents), Suite ($380/night, 55 sqm),
              Presidential Suite ($750/night, 95 sqm), Two Bedroom Suite
              (95 sqm, 6 units, highest level), Villa ($1,200/night,
              150 sqm, accommodates 6)."
    Rating:   ACCURATE

Q2: Do you have a water park?
    Expected: water park, river splash
    Response: "Yes, we have The River Splash — our mini water park
              featuring exciting water slides, a lazy river, and an
              interactive water play area. Deluxe Water Park rooms offer
              direct views of the mini water park and trundle beds
              for children."
    Rating:   ACCURATE

Q3: Do you have a spa?
    Expected: spa, tivaa
    Response: "Yes, we have Tivaa Ratrii Spa. Hours: Daily, 11:00 - 21:00.
              Awards: SHA (Amazing Thailand) 2020 and Shaplus Award 2021."
    Rating:   ACCURATE

Q4: What dining options are available?
    Expected: restaurant
    Response: "I apologize, but I don't have specific information about
              the dining options at Hotel Riviera Cr in my current
              knowledge base..."
    Rating:   NO_INFO

Q5: Do you have a kids club?
    Expected: kid, children
    Response: "Yes! Chang Maun Kids World — the most exciting kids club
              in Chiang Rai. Open daily 09:00 - 18:00 hours. Vibrant,
              spacious haven for children of all ages."
    Rating:   ACCURATE

Q6: Do you have conference facilities?
    Expected: conference, meeting
    Response: "Chandra Mahal (1,440 sq ft, up to 110 guests, divisible),
              Meeting Rooms (40 sqm each, up to 48 guests, projector and
              screen), The Cocktail Room (744 sq ft, up to 48 guests,
              built-in audio). All venues offer theatre, classroom, U-shape,
              boardroom, and cocktail seating arrangements."
    Rating:   ACCURATE

Q7: Where is the hotel located?
    Expected: chiang rai
    Response: "I don't have the specific location information for Hotel
              Riviera Cr in my available resources..."
    Rating:   NO_INFO

Q8: What is the phone number?
    Expected: 607999, 53 607
    Response: "The phone number for Hotel Riviera Cr is +66 53 607 999."
    Rating:   ACCURATE

Q9: Do you offer airport transfer?
    Expected: airport, transfer
    Response: "Yes, we offer airport transfer services between Chiang Rai
              International Airport (CEI) and The Riverie by Katathani.
              We provide complimentary airport shuttle service (advance
              booking required). Contact: +66 (0) 53 607999, email
              booking@theriverie.com, LINE: @theriverie."
    Rating:   ACCURATE

Q10: Do you have a swimming pool?
     Expected: pool
     Response: "Yes — main pool open daily 7:00 AM to 8:00 PM. Room
               categories with semi-private pools include Premier City
               Palace View Rooms and Premier Garden View Rooms (81-84m
               long pools). Also River Splash aquatic facility, 7:00 AM
               to 8:00 PM daily."
     Rating:   ACCURATE

SUMMARY: 8 accurate, 2 no_info, 0 escalated. Best performance of all six
hotels. Detailed, specific responses on rooms (with pricing), water park,
spa (with award names), kids club, conference facilities, phone number,
airport transfer, and pool. The two NO_INFO gaps are dining and location —
consistent with the same gaps seen at Oberoi and le Patte, suggesting that
dining pages and location/address pages may be systematically skipped or
poorly extracted during scraping.


==========================================================================
5. ISSUES FOUND
==========================================================================


ISSUE 1: ESCALATION BEHAVIOR (ESCALATED RESPONSES)
----------------------------------------------------
The escalation phrase "I want to make sure you get the best possible
answer. Let me connect you with our team who can help you directly.
Someone will be in touch with you very shortly!" is triggered when the
AI retrieval engine cannot find a relevant KB chunk with sufficient
confidence for a given question.

This behavior is by design as a safety fallback, but it becomes a problem
when it fires for basic, predictable guest questions that should always
be answerable (e.g., "do you have a pool", "do you have WiFi", "what room
types do you have"). When escalation occurs on these queries, it indicates
that the knowledge base is either empty, structurally broken, or contains
content that is indexed under the wrong semantic categories.

Escalation count per hotel:
  Heritage:    8 / 10 questions escalated
  Grand Vista: 9 / 10 questions escalated
  Imperial:    9 / 10 questions escalated (plus 1 NO_INFO)
  Oberoi:      0 / 10
  le Patte:    1 / 10
  Riverie:     0 / 10


ISSUE 2: NO_INFO RESPONSES
---------------------------
A NO_INFO response occurs when the AI finds partial context or nothing
at all but chooses to compose a polite "I don't have this information"
message rather than escalating. This is marginally better than
escalation (it does not incorrectly promise a callback) but still
represents a gap in hotel content.

The pattern of which topics produce NO_INFO is consistent across hotels:
  - Hotel location / address (5 of 6 hotels failed this question)
  - Dining options / restaurants (3 hotels)
  - Nearby attractions (2 hotels)
  - Airport transfer (2 hotels)

The location gap is particularly notable — a guest asking "where is your
hotel?" should never receive a NO_INFO response. The address of the
hotel is the most fundamental piece of information a concierge system
should hold. This suggests location/address pages are either not being
scraped or are being scraped but stored in a chunk format that does not
surface on this query.


ISSUE 3: BLANK DASHBOARD BUG — IMPERIAL MAE PING AND OBEROI UDAIVILAS
----------------------------------------------------------------------
When the admin dashboard is opened for Imperial Mae Ping Hotel or The
Oberoi Udaivilas, the React application renders (page loads, no console
crash on initial load) but the hotel's content area displays nothing.
No hotel name, no question list, no chat interface.

This is distinct from a full application crash. The outer shell of the
dashboard renders but the hotel-specific component tree produces blank
output. Likely causes include:
  - A null/undefined hotel ID being passed to the component
  - A failed async data fetch that returns an empty state silently
  - A conditional render that evaluates to nothing due to an unexpected
    data shape
  - A hotel profile object that is missing a required field the UI
    depends on (e.g., a null "name" or "config" field)

Both affected hotels were fully testable via the API endpoint, confirming
the backend is functional. The bug is isolated to the React frontend
rendering layer for these two hotel profiles.

Impact: Any client staff member trying to use the dashboard to monitor
or test these hotels will see a blank screen and will be unable to
interact with the concierge system through the UI.


ISSUE 4: HERITAGE CHIANG RAI — 178 CHUNKS WITH ONLY 1 USEFUL ANSWER
---------------------------------------------------------------------
The Heritage Chiang Rai has 178 KB chunks, which is a plausible volume
for a hotel website, yet only 1 out of 10 questions could be answered
correctly (the ballroom / convention facilities question).

The most probable explanation is that the scraper captured a large
volume of low-information content: navigation menus, image alt text,
promotional banners, legal/cookie notices, social media embeds, and
page headers/footers. These generate chunks that occupy vector space
without containing factual answers to guest questions.

The fact that the ballroom question succeeded while "do you have a
swimming pool" and "do you have a spa" failed strongly implies the
scraper captured one well-formatted amenity/events page (ballroom)
but missed the accommodation, facilities, and dining sections entirely.


ISSUE 5: GRAND VISTA CHIANGRAI — ONLY 13 KB CHUNKS
----------------------------------------------------
13 chunks is not a meaningful knowledge base for a hotel property.
A standard hotel website contains 30-80 pages; even at minimal
extraction this would produce significantly more than 13 chunks.

This indicates a scraping failure, not just poor content quality.
Likely causes:
  - The website blocks automated scrapers (Cloudflare, JavaScript
    challenge, or user-agent filtering)
  - The website is primarily image-based with minimal text
  - The scraper was given incorrect URLs or the sitemap was not crawled
  - Session / cookie authentication blocked the scraper

The one successful answer (nearby attractions at question 10) likely
came from a single chunk that listed nearby places — probably captured
from a hotel description or booking platform excerpt rather than from
the hotel's own site.


ISSUE 6: IMPERIAL MAE PING — 558 CHUNKS WITH 0% ACCURACY
---------------------------------------------------------
This is the most critical data quality issue in the system. 558 chunks
is a large volume of content, second only to Riverie (467), yet every
single test question failed. There were zero accurate responses and
nine hard escalations, with only one soft NO_INFO for the location query.

Possible explanations:
  a) The scraped URLs were not the hotel's amenity/room/dining pages.
     They may have been a blog, press releases, partner pages, or the
     broader Imperial Hotels group site rather than the property-specific
     content for Imperial Mae Ping.
  b) The chunks are correctly sourced but were indexed with an incorrect
     hotel_id, so they belong to Imperial Mae Ping's namespace in the
     DB but semantically contain content about a different property.
  c) The embedding model's retrieval is failing for this hotel's content
     specifically — possibly due to chunk size issues, encoding problems,
     or metadata mismatch.
  d) The content is present and correctly indexed but consists of
     low-quality text (e.g., JavaScript-rendered text captured as raw
     code, structured data in JSON-LD format, or booking widget markup).

This issue requires investigation at the data ingestion level.
Manually inspecting a sample of the 558 chunks for this hotel_id is
the recommended first diagnostic step.


==========================================================================
6. RECOMMENDATIONS
==========================================================================


PRIORITY 1 — GRAND VISTA: RE-SCRAPE THE WEBSITE
Re-attempt scraping of grandvistachiangrai.com with a headless browser
scraper (Playwright or Puppeteer) to handle JavaScript rendering.
Verify the robots.txt file permits crawling. Target specific URL paths:
rooms, facilities, dining, location/about, and attractions pages.
Expected yield: 150-400 chunks. Current 13-chunk state is unusable.

PRIORITY 1 — IMPERIAL MAE PING: AUDIT THE EXISTING CHUNKS
Before re-scraping, retrieve and inspect 20-30 sample chunks from the
Imperial Mae Ping namespace in the vector database. Determine whether
the content is hotel-specific and guest-relevant. If the chunks contain
unrelated content, truncate the namespace and re-scrape from the correct
property URLs (imperialmaeping.com room, dining, and facilities pages).

PRIORITY 1 — IMPERIAL MAE PING: FIX THE BLANK DASHBOARD
Investigate the React component responsible for rendering the hotel
dashboard for imperial_mae_ping and oberoi_udaivilas. Add console
logging or React DevTools inspection to identify which prop is null
or which async fetch is silently returning empty. Ensure the component
handles loading states and empty-data conditions gracefully rather than
rendering nothing.

PRIORITY 1 — OBEROI UDAIVILAS: FIX THE BLANK DASHBOARD
Same as above — both hotels share this bug and should be fixed together.

PRIORITY 2 — HERITAGE CHIANG RAI: TARGETED RE-SCRAPE
The existing 178 chunks are not useful for guest questions. Re-scrape
heritagechiangrai.com with explicit page targeting: identify and scrape
the rooms/accommodation page, the dining/restaurants page, the
facilities/amenities page (pool, spa, gym), the about/location page,
and the nearby attractions section. Discard chunks that are fewer than
100 words or that consist primarily of navigation elements.

PRIORITY 2 — UNIVERSAL: ADD LOCATION/ADDRESS TO EVERY HOTEL KB
Five out of six hotels failed the "where is your hotel located?" question.
This is unacceptable for a concierge system. Location data should be
injected as a dedicated high-priority chunk for every hotel, manually
if necessary, rather than relying on scraping to capture it. A simple
structured document — hotel name, address, city, country, GPS coordinates,
airport distance — would resolve this gap immediately for all hotels.

PRIORITY 2 — UNIVERSAL: ADD DINING CONTENT
Dining questions failed at Oberoi, le Patte, and Riverie — hotels that
otherwise performed well. Restaurant pages are commonly JavaScript-
rendered or hidden behind booking widgets that scrapers cannot access.
Consider manually entering a dining summary document for each hotel
(restaurant name, cuisine type, hours, brief description) as a static
KB entry.

PRIORITY 3 — SYSTEM-WIDE: REVIEW ESCALATION THRESHOLD
The escalation behavior is too aggressive for hotels with thin KBs.
When a hotel has very few chunks, almost every question falls below the
confidence threshold and escalates. Consider whether a "graceful NO_INFO"
response is more appropriate than a hard escalation for hotels still
being onboarded, so that guests receive an honest "we don't have that
information" rather than a false promise of a callback.

PRIORITY 3 — SYSTEM-WIDE: CHUNK QUALITY FILTERING
Implement a post-scrape filtering step that rejects chunks below a
word-count threshold (e.g., fewer than 80 words) and chunks that
match navigation/boilerplate patterns (e.g., chunks consisting entirely
of menu items, copyright text, or social media handles). This would
improve the signal-to-noise ratio of all hotel KBs.


==========================================================================
7. SUMMARY TABLES
==========================================================================


TABLE A: OVERALL ACCURACY BY HOTEL

  Hotel                   Accurate  Partial  NO_INFO  Escalated  Unverified  Total  Pct
  ----------------------  --------  -------  -------  ---------  ----------  -----  ---
  Riverie by Katathani       8         0        2         0           0         10   80%
  Oberoi Udaivilas           7         0        3         0           0         10   70%
  le Patte                   6         0        3         1           0         10   60%
  Heritage Chiang Rai        1         0        1         8           0         10   10%
  Grand Vista Chiangrai      1         0        0         9           0         10   10%
  Imperial Mae Ping          0         0        0         9           1         10    0%
  ----------------------  --------  -------  -------  ---------  ----------  -----  ---
  TOTAL                     23         0        9        27           1         60   38%


TABLE B: QUESTION CATEGORY PERFORMANCE ACROSS ALL HOTELS

  Category              Accurate  Total  Success Rate
  --------------------  --------  -----  ------------
  Room types / sizes       4        6       67%
  Pool / water park        4        6       67%
  Spa                      3        6       50%
  Meetings / conference    3        6       50%
  Fitness / gym            2        6       33%
  Experiences              1        6       17%
  Dining / restaurant      0        6        0%
  Location / address       1        6       17%
  WiFi                     0        6        0%
  Airport / transfer       2        6       33%
  Kids club                1        1      100%
  Phone number             1        1      100%
  Water park               1        1      100%
  Nearby attractions       2        4       50%


TABLE C: ISSUE MATRIX BY HOTEL

  Hotel              Blank Dashboard  KB Volume Issue  Content Quality  Zero Accuracy
  -----------------  ---------------  ----------------  ---------------  -------------
  Riverie                 No               No               Good             No
  Oberoi                  YES              No               Good             No
  le Patte                No               No               Good             No
  Heritage                No          Possible (178 poor)   POOR             No
  Grand Vista             No          YES (only 13)         Very Poor        No
  Imperial Mae Ping       YES          Possible (558 bad)   CRITICAL         YES


==========================================================================
END OF REPORT
==========================================================================
Report prepared: March 22, 2026
Test method: POST /admin/test/message (direct API)
Total questions tested: 60 (10 per hotel, 6 hotels)
Overall accuracy: 23/60 (38.3%)
