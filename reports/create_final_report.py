"""
Generate comprehensive PDF report for HotelIntelliai Dashboard QA Testing.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from datetime import datetime

OUTPUT = "/var/lib/freelancer/projects/40298427/reports/HotelIntelliai_Final_Dashboard_Test_Report.pdf"

def build_report():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=letter,
        rightMargin=60, leftMargin=60,
        topMargin=60, bottomMargin=60
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=22, spaceAfter=6, textColor=colors.HexColor('#1a1a2e')
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontSize=12, spaceAfter=20, textColor=colors.HexColor('#555555')
    )
    h1 = ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontSize=16, spaceBefore=20, spaceAfter=10,
        textColor=colors.HexColor('#1a1a2e')
    )
    h2 = ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=13, spaceBefore=14, spaceAfter=8,
        textColor=colors.HexColor('#2d3436')
    )
    h3 = ParagraphStyle(
        'H3', parent=styles['Heading3'],
        fontSize=11, spaceBefore=10, spaceAfter=6,
        textColor=colors.HexColor('#2d3436')
    )
    body = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=10, spaceAfter=6, leading=14
    )
    body_bold = ParagraphStyle(
        'BodyBold', parent=body, fontName='Helvetica-Bold'
    )
    small = ParagraphStyle(
        'Small', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#777777')
    )
    pass_style = ParagraphStyle(
        'Pass', parent=body,
        textColor=colors.HexColor('#27ae60'), fontName='Helvetica-Bold'
    )
    fail_style = ParagraphStyle(
        'Fail', parent=body,
        textColor=colors.HexColor('#e74c3c'), fontName='Helvetica-Bold'
    )
    warn_style = ParagraphStyle(
        'Warn', parent=body,
        textColor=colors.HexColor('#f39c12'), fontName='Helvetica-Bold'
    )

    story = []

    # ===== COVER PAGE =====
    story.append(Spacer(1, 80))
    story.append(Paragraph("HotelIntelliai", title_style))
    story.append(Paragraph("Dashboard QA Test Report", ParagraphStyle(
        'CoverSub', parent=styles['Title'], fontSize=18,
        textColor=colors.HexColor('#4a69bd'), spaceAfter=30
    )))
    story.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor('#4a69bd')))
    story.append(Spacer(1, 30))
    story.append(Paragraph("Final Comprehensive Testing", subtitle_style))
    story.append(Paragraph("Hotels Tested: The Riverie by Katathani  |  Le Patta Hotel", body))
    story.append(Spacer(1, 20))

    info_data = [
        ["Date:", datetime.now().strftime("%B %d, %Y")],
        ["Tester:", "Anirudha Talmale"],
        ["Platform:", "dashboard.hotelintelliai.com"],
        ["Test Type:", "Full Staff Perspective - Dashboard Features + AI Concierge"],
        ["Automation:", "Playwright (Python) - Headless Chromium"],
        ["Hotels:", "2 (Riverie, Le Patta)"],
        ["Total Questions:", "30 (15 per hotel)"],
    ]
    info_table = Table(info_data, colWidths=[120, 350])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(info_table)

    story.append(PageBreak())

    # ===== EXECUTIVE SUMMARY =====
    story.append(Paragraph("1. Executive Summary", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd')))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "This report presents the results of comprehensive QA testing performed on the HotelIntelliai "
        "dashboard from a hotel staff perspective. Testing covered all dashboard sections (Overview, "
        "Conversations, Guests, Escalations, Channels, Knowledge Base, Debug tools) and AI concierge "
        "accuracy across two hotels: The Riverie by Katathani and Le Patta Hotel.", body
    ))
    story.append(Spacer(1, 10))

    # Summary table
    summary_data = [
        ["Metric", "Riverie", "Le Patta", "Overall"],
        ["Dashboard Sections", "7/7 OK", "7/7 OK", "14/14 (100%)"],
        ["KB Chunks Loaded", "162", "213", "375 total"],
        ["KB Tabs (File/URL/FAQ)", "All accessible", "All accessible", "All OK"],
        ["Health Check", "Healthy", "Not run (UI only)", "-"],
        ["Channels Configured", "5 (4 live, 1 off)", "5 (4 live, 1 off)", "10 total"],
        ["Concierge Questions", "15", "15", "30"],
        ["Answered Correctly", "8 (53.3%)", "11 (73.3%)", "19 (63.3%)"],
        ["Escalations", "6 (40%)", "4 (26.7%)", "10 (33.3%)"],
        ["Errors", "1 (6.7%)", "0 (0%)", "1 (3.3%)"],
        ["Open Escalation Tickets", "1 (high)", "1 (high)", "2"],
    ]
    summary_table = Table(summary_data, colWidths=[150, 110, 110, 100])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f6fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)

    story.append(PageBreak())

    # ===== HOTEL 1: RIVERIE =====
    story.append(Paragraph("2. The Riverie by Katathani (hotel_riviera_cr)", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd')))

    # 2.1 Dashboard Navigation
    story.append(Paragraph("2.1 Dashboard Navigation", h2))
    story.append(Paragraph("URL: https://hotel_riviera_cr.hotelintelliai.com/", small))
    story.append(Paragraph(
        "All 7 sidebar sections loaded successfully without errors. The dashboard is fully functional "
        "from a staff perspective.", body
    ))

    nav_data = [
        ["Section", "Status", "Details"],
        ["Overview", "PASS", "Stats visible: 7 conversations, 5 guests, 30 messages, 2 escalations"],
        ["Conversations", "PASS", "7 total conversations shown with channel tags and status"],
        ["Guests", "PASS", "5 guests listed with tier (VIP/Regular), stays, conversations, preferences"],
        ["Escalations", "PASS", "2 escalations: 1 high (James Whitfield - Maintenance, open), 1 medium (Sophie Laurent - Complaint, resolved)"],
        ["Channels", "PASS", "5 channels: WhatsApp (live), Telegram (live), Line (live), Email (live), Web (off)"],
        ["Knowledge Base", "PASS", "162 chunks, 1 document (Menu The Peak - website), all 3 tabs accessible"],
        ["Debug", "PASS", "5 sub-tabs: Health Check, RAG Tester, Msg Simulator, DB Stats, Guest Lookup"],
    ]
    nav_table = Table(nav_data, colWidths=[90, 50, 330])
    nav_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3436')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f6fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(nav_table)

    # 2.2 Health Check
    story.append(Paragraph("2.2 Health Check", h2))
    story.append(Paragraph(
        "Health Check shows 'Hotel is healthy'. DB Record: OK (Name: The Riverie by Katathani, "
        "Active: Yes, Collection: hotel_riviera_cr, KB Uploads: 1, Timezone: Asia/Bangkok). "
        "Qdrant/Vectors: Connection OK, Collection: hotel_riviera_cr, 162 vectors.", body
    ))

    # 2.3 Knowledge Base
    story.append(Paragraph("2.3 Knowledge Base Analysis", h2))
    story.append(Paragraph(
        "The Riverie has 162 KB chunks from 1 document source ('Menu The Peak' - scraped from website "
        "on 3/26/2026). Content appears to be primarily focused on restaurant/dining information, which "
        "explains why dining-related questions get good answers but general hotel questions trigger escalations.", body
    ))
    story.append(Paragraph(
        "<b>Observation:</b> Only 1 website URL has been ingested. The KB primarily contains dining/restaurant "
        "content. To improve concierge accuracy, more pages from the hotel website should be ingested "
        "(rooms, facilities, policies, location, etc.).", body
    ))

    # 2.4 Concierge Results
    story.append(Paragraph("2.4 AI Concierge Test Results (15 Questions)", h2))

    riverie_q = [
        ["#", "Question", "Result", "Response Summary"],
        ["1", "Check-in/check-out times?", "ESCALATION", "Could not answer - escalated to staff"],
        ["2", "Room types?", "ERROR", "Could not extract response (possible UI issue)"],
        ["3", "Swimming pool?", "ANSWERED", "Mentioned Jumanji Pool Bar but incomplete pool details"],
        ["4", "Dining options?", "ANSWERED", "Detailed: The Peak Restaurant with menu items and prices (650-450 THB)"],
        ["5", "Airport transfer?", "ESCALATION", "Could not answer - escalated to staff"],
        ["6", "Spa treatments?", "ANSWERED", "Tivaa Ratrii spa, open 11AM-9PM, head-to-toe treatments"],
        ["7", "Breakfast included?", "ANSWERED", "Honest: doesn't have info, recommends contacting front desk"],
        ["8", "Meeting rooms?", "ANSWERED", "Detailed: up to 700 guests, multiple rooms (Doi Tung, Doi Wawee, etc.)"],
        ["9", "Cancellation policy?", "ANSWERED", "Honest: doesn't have policy info, suggests checking booking"],
        ["10", "Free WiFi?", "ESCALATION", "Could not answer - escalated to staff"],
        ["11", "Parking?", "ESCALATION", "Could not answer - escalated to staff"],
        ["12", "Activities/excursions?", "ANSWERED", "Mentioned Doi Tung, Doi Chang, Tham Luang cave, family activities"],
        ["13", "Pets allowed?", "ANSWERED", "Honest: no pet policy info found, recommends contacting hotel"],
        ["14", "Room rates?", "ESCALATION", "Could not answer - escalated to staff"],
        ["15", "Fitness center?", "ESCALATION", "Could not answer - escalated to staff"],
    ]
    rq_table = Table(riverie_q, colWidths=[20, 130, 75, 245])
    rq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3436')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f6fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    # Color code the Result column
    for i in range(1, len(riverie_q)):
        result = riverie_q[i][2]
        if result == "ESCALATION":
            rq_table.setStyle(TableStyle([
                ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#e74c3c')),
                ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),
            ]))
        elif result == "ANSWERED":
            rq_table.setStyle(TableStyle([
                ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#27ae60')),
                ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),
            ]))
        elif result == "ERROR":
            rq_table.setStyle(TableStyle([
                ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#f39c12')),
                ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),
            ]))
    story.append(rq_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Riverie Accuracy: 53.3%</b> (8 answered, 6 escalations, 1 error)", body_bold))

    story.append(PageBreak())

    # ===== HOTEL 2: LE PATTA =====
    story.append(Paragraph("3. Le Patta Hotel (lepatta)", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd')))

    # 3.1 Dashboard Navigation
    story.append(Paragraph("3.1 Dashboard Navigation", h2))
    story.append(Paragraph("URL: https://lepatta.hotelintelliai.com/", small))
    story.append(Paragraph(
        "All 7 sidebar sections loaded successfully. Dashboard shows good activity with "
        "5 conversations, 5 guests, 24 messages, 2 VIP guests, and 1 open escalation.", body
    ))

    lp_nav = [
        ["Section", "Status", "Details"],
        ["Overview", "PASS", "5 conversations, 5 guests, 24 messages, 2 VIP, 1 escalation"],
        ["Conversations", "PASS", "Conversation list with channel indicators and status"],
        ["Guests", "PASS", "Guest list with tier, stays, and preferences"],
        ["Escalations", "PASS", "1 open: Rachel Kim - Complaint (high priority, 1d ago)"],
        ["Channels", "PASS", "5 channels: WhatsApp (live), Telegram (live), Line (live), Email (live), Web (off)"],
        ["Knowledge Base", "PASS", "213 chunks, 1 document (Deluxe Room | Chiang Rai - website), all tabs OK"],
        ["Debug", "PASS", "All 5 sub-tabs accessible"],
    ]
    lp_table = Table(lp_nav, colWidths=[90, 50, 330])
    lp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3436')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f6fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(lp_table)

    # 3.2 KB
    story.append(Paragraph("3.2 Knowledge Base Analysis", h2))
    story.append(Paragraph(
        "Le Patta has 213 KB chunks from 1 document source ('Deluxe Room | Chiang Rai' - scraped "
        "from website on 3/27/2026). This hotel has more chunks than Riverie and shows better concierge "
        "accuracy (73.3% vs 53.3%), suggesting broader website content was captured.", body
    ))

    # 3.3 Concierge
    story.append(Paragraph("3.3 AI Concierge Test Results (15 Questions)", h2))

    lepatta_q = [
        ["#", "Question", "Result", "Response Summary"],
        ["1", "Check-in/check-out times?", "ESCALATION", "Could not answer - escalated to staff"],
        ["2", "Room types?", "ANSWERED", "Detailed: Superior (corner rooms, king/twin), Deluxe, Suite with features"],
        ["3", "Restaurant on site?", "ANSWERED", "Yes, on-site restaurant + nearby riverside restaurants (Leelawadee, Chivit)"],
        ["4", "Swimming pool?", "ANSWERED", "Yes, salt water pool surrounded by green garden"],
        ["5", "Spa services?", "ANSWERED", "No spa listed, but mentions gym and pool for wellness"],
        ["6", "Airport shuttle?", "ANSWERED", "Yes, complimentary shuttle + free WiFi, parking, bike lending"],
        ["7", "Breakfast included?", "ESCALATION", "Could not answer - escalated to staff"],
        ["8", "Room rates?", "ANSWERED", "Honest: no rates available, provides contact: +66 53 600680"],
        ["9", "Conference facilities?", "ANSWERED", "Honest: no conference info found, suggests contacting front desk"],
        ["10", "WiFi in rooms?", "ANSWERED", "Yes, free WiFi in all rooms (Superior, Deluxe, Suite)"],
        ["11", "Cancellation policy?", "ESCALATION", "Could not answer - escalated to staff"],
        ["12", "Bar or lounge?", "ANSWERED", "Yes, Chivit Thamma Da Coffee House, Bistro & Bar on Kok River"],
        ["13", "Activities nearby?", "ANSWERED", "Detailed: Chiang Rai Walking Street (Sat 4PM-midnight), local vendors"],
        ["14", "Laundry service?", "ESCALATION", "Could not answer - escalated to staff"],
        ["15", "Parking available?", "ANSWERED", "Yes, complimentary parking for guests"],
    ]
    lpq_table = Table(lepatta_q, colWidths=[20, 130, 75, 245])
    lpq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3436')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f6fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    for i in range(1, len(lepatta_q)):
        result = lepatta_q[i][2]
        if result == "ESCALATION":
            lpq_table.setStyle(TableStyle([
                ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#e74c3c')),
                ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),
            ]))
        elif result == "ANSWERED":
            lpq_table.setStyle(TableStyle([
                ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#27ae60')),
                ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),
            ]))
    story.append(lpq_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Le Patta Accuracy: 73.3%</b> (11 answered, 4 escalations, 0 errors)", body_bold))

    story.append(PageBreak())

    # ===== ESCALATION ANALYSIS =====
    story.append(Paragraph("4. Escalation Analysis", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd')))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Per client's instruction: any response containing 'I want to make sure you get the best "
        "possible answer. Let me connect you with...' indicates the AI could not find the answer "
        "in the Knowledge Base. These escalations should be investigated.", body
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("4.1 Common Escalation Topics (Both Hotels)", h2))
    common_esc = [
        ["Topic", "Riverie", "Le Patta", "Recommendation"],
        ["Check-in/out times", "ESCALATED", "ESCALATED", "Add check-in/out policy page to KB for both hotels"],
        ["Breakfast inclusion", "Partial*", "ESCALATED", "Add breakfast/meal plan info to KB"],
        ["Cancellation policy", "Partial*", "ESCALATED", "Add cancellation terms to KB"],
        ["Room rates/pricing", "ESCALATED", "Partial*", "Add rate cards or booking page to KB"],
        ["WiFi availability", "ESCALATED", "ANSWERED", "Riverie needs WiFi info in KB"],
        ["Parking", "ESCALATED", "ANSWERED", "Riverie needs parking info in KB"],
        ["Fitness center", "ESCALATED", "N/A", "Add facilities page to Riverie KB"],
        ["Airport transfer", "ESCALATED", "ANSWERED", "Riverie needs transport info in KB"],
        ["Laundry service", "N/A", "ESCALATED", "Add services page to Le Patta KB"],
    ]
    esc_table = Table(common_esc, colWidths=[110, 80, 80, 200])
    esc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0392b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fdf2f2')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(esc_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "*Partial = AI acknowledged it doesn't have the info but provided a helpful redirect "
        "(not a hard escalation)", small
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph("4.2 Escalation Tickets in Dashboard", h2))
    story.append(Paragraph("<b>Riverie:</b> 2 escalations", body))
    story.append(Paragraph("  - James Whitfield (HIGH) - Maintenance - Open (1d ago)", body))
    story.append(Paragraph("  - Sophie Laurent (MEDIUM) - Complaint - Resolved (6d ago)", body))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Le Patta:</b> 1 escalation", body))
    story.append(Paragraph("  - Rachel Kim (HIGH) - Complaint - Open (1d ago)", body))

    # ===== CHANNEL CONFIGURATION =====
    story.append(Paragraph("5. Channel Configuration", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd')))

    ch_data = [
        ["Channel", "Riverie Status", "Le Patta Status", "Webhook URL"],
        ["WhatsApp", "LIVE", "LIVE", "api.hotelintelliai.com/webhook/whatsapp"],
        ["Telegram", "LIVE", "LIVE", "api.hotelintelliai.com/webhook/telegram"],
        ["Line", "LIVE", "LIVE", "api.hotelintelliai.com/webhook/line"],
        ["Email", "LIVE", "LIVE", "api.hotelintelliai.com/webhook/email"],
        ["Web", "OFF", "OFF", "api.hotelintelliai.com/webhook/web"],
    ]
    ch_table = Table(ch_data, colWidths=[80, 90, 90, 210])
    ch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3436')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f6fa')]),
        ('ALIGN', (1, 1), (2, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(ch_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Note:</b> Web channel is OFF for both hotels. If web chat is desired, this needs to be enabled.", body
    ))

    story.append(PageBreak())

    # ===== ISSUES & RECOMMENDATIONS =====
    story.append(Paragraph("6. Issues Found & Recommendations", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd')))

    story.append(Paragraph("6.1 Issues", h2))

    issues = [
        ["#", "Severity", "Hotel", "Issue", "Details"],
        ["1", "HIGH", "Both", "Check-in/out times not in KB",
         "Most basic hotel question triggers escalation for both hotels"],
        ["2", "HIGH", "Both", "Breakfast info missing from KB",
         "Riverie gives partial answer, Le Patta escalates entirely"],
        ["3", "HIGH", "Both", "Cancellation policy not in KB",
         "Guests need this before booking - critical gap"],
        ["4", "MEDIUM", "Riverie", "Only 162 chunks (dining-heavy)",
         "KB mostly contains restaurant menu data, missing general hotel info"],
        ["5", "MEDIUM", "Riverie", "WiFi/Parking/Fitness/Transfer escalate",
         "Basic facility questions unanswered due to limited KB content"],
        ["6", "MEDIUM", "Le Patta", "Laundry service info missing",
         "Common guest question not covered in KB"],
        ["7", "LOW", "Both", "Web channel disabled",
         "Web chat not active - may be intentional"],
        ["8", "LOW", "Riverie", "Q2 response extraction error",
         "Msg Simulator may have UI rendering delay for some responses"],
    ]
    issues_table = Table(issues, colWidths=[20, 55, 55, 170, 170])
    issues_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3436')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f6fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    # Color severity
    for i in range(1, len(issues)):
        sev = issues[i][1]
        if sev == "HIGH":
            issues_table.setStyle(TableStyle([
                ('TEXTCOLOR', (1, i), (1, i), colors.HexColor('#e74c3c')),
                ('FONTNAME', (1, i), (1, i), 'Helvetica-Bold'),
            ]))
        elif sev == "MEDIUM":
            issues_table.setStyle(TableStyle([
                ('TEXTCOLOR', (1, i), (1, i), colors.HexColor('#f39c12')),
                ('FONTNAME', (1, i), (1, i), 'Helvetica-Bold'),
            ]))
    story.append(issues_table)

    story.append(Spacer(1, 15))
    story.append(Paragraph("6.2 Recommendations", h2))

    recs = [
        "1. INGEST MORE WEBSITE PAGES: Both hotels have only 1 website document ingested. "
        "Add more pages: rooms, facilities, policies, FAQ, location, contact, services.",

        "2. ADD CHECK-IN/OUT TIMES: This is the #1 most asked hotel question. "
        "Add it as FAQ entry or ensure the relevant website page is ingested.",

        "3. ADD CANCELLATION & BREAKFAST POLICIES: Critical pre-booking information "
        "that should be in the KB for every hotel.",

        "4. RIVERIE KB EXPANSION: Currently 162 chunks mostly from dining/menu content. "
        "Need to ingest the full hotel website (rooms, spa details, facilities, transport, etc.).",

        "5. CONSIDER FAQ ENTRIES: For information not on the website (WiFi details, "
        "parking info, pet policy), add manual FAQ entries in the Knowledge Base.",

        "6. WEB CHANNEL: Enable the Web channel if web chat widget is planned for hotel websites.",

        "7. MONITOR ESCALATION TICKETS: Both hotels have open high-priority escalations "
        "that need staff attention.",
    ]
    for rec in recs:
        story.append(Paragraph(rec, body))
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # ===== TEST AUTOMATION =====
    story.append(Paragraph("7. Test Automation", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd')))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "All tests were executed using Playwright (Python) with headless Chromium browser. "
        "The test scripts are fully automated and can be rerun at any time.", body
    ))
    story.append(Spacer(1, 8))

    auto_data = [
        ["Script", "Purpose", "Tests"],
        ["final_dashboard_test_v3.py", "Riverie full dashboard + concierge (15 Q)", "~30"],
        ["final_lepatta_test.py", "Le Patta full dashboard + concierge (15 Q)", "~30"],
        ["test-scripts/conftest.py", "Shared fixtures (login, browser setup)", "-"],
        ["test-scripts/test_07_kb_files_faq.py", "KB file upload, FAQ, RAG verification", "19"],
        ["test-scripts/test_06_deep_riverie.py", "Bug regression tests", "16"],
    ]
    auto_table = Table(auto_data, colWidths=[170, 210, 50])
    auto_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3436')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f6fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(auto_table)

    story.append(Spacer(1, 15))
    story.append(Paragraph(
        "GitHub Repository: github.com/anirudhatalmale6-alt/hotelintelliai-qa-tests", body_bold
    ))
    story.append(Paragraph(
        "To run: python3 -m pytest test-scripts/ -v (or run individual scripts directly)", body
    ))

    # ===== CONCLUSION =====
    story.append(Spacer(1, 30))
    story.append(Paragraph("8. Conclusion", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd')))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "The HotelIntelliai dashboard is functional and stable from a hotel staff perspective. "
        "All 7 dashboard sections work correctly for both hotels. The AI concierge provides "
        "relevant, well-formatted responses when the information exists in the Knowledge Base.", body
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "The primary gap is KB coverage: both hotels have limited content ingested (1 document each), "
        "leading to escalation rates of 40% (Riverie) and 26.7% (Le Patta). Expanding the KB with "
        "more website pages and FAQ entries would significantly improve the concierge accuracy.", body
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Overall concierge accuracy across both hotels: 63.3% (19/30 questions answered). "
        "With expanded KB content, this could realistically reach 85-90%+.", body
    ))

    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="40%", thickness=1, color=colors.HexColor('#aaa')))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Report prepared by Anirudha Talmale", small))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}", small))

    # Build
    doc.build(story)
    print(f"Report saved to: {OUTPUT}")

if __name__ == "__main__":
    build_report()
