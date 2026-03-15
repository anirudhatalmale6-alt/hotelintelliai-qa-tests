"""Create test files in various formats for KB upload testing."""
import os

# 1. Plain text file (.txt)
with open("test_hotel_info.txt", "w") as f:
    f.write("Hotel Riverie Test Document\n\n")
    f.write("Check-in time: 3:00 PM\nCheck-out time: 11:00 AM\n")
    f.write("Pool hours: 6:00 AM to 10:00 PM\n")
    f.write("Breakfast is served from 7:00 AM to 10:30 AM in the main restaurant.\n")
    f.write("The hotel has 150 rooms across 5 categories.\n")

# 2. CSV file (.csv)
with open("test_room_rates.csv", "w") as f:
    f.write("Room Type,Rate (USD),Max Guests,Size (sqm)\n")
    f.write("Standard,150,2,28\n")
    f.write("Deluxe,220,2,35\n")
    f.write("Suite,380,4,55\n")
    f.write("Presidential Suite,750,4,95\n")
    f.write("Villa,1200,6,150\n")

# 3. JSON file (.json)
import json
data = {
    "hotel": "The Riverie Test",
    "amenities": ["Pool", "Spa", "Gym", "Restaurant", "Bar", "Business Center"],
    "contact": {"phone": "+66-123-456-789", "email": "info@riverie-test.com"},
    "policies": {
        "pets": "Small pets allowed with $50 deposit",
        "smoking": "Non-smoking property",
        "parking": "Complimentary valet parking"
    }
}
with open("test_amenities.json", "w") as f:
    json.dump(data, f, indent=2)

# 4. Markdown file (.md)
with open("test_spa_menu.md", "w") as f:
    f.write("# Tivaa Ratrii Spa Menu\n\n")
    f.write("## Thai Massage\n- Traditional Thai: 60 min - $80\n- Aromatic Thai: 90 min - $120\n\n")
    f.write("## Body Treatments\n- Salt Scrub: 45 min - $60\n- Herbal Wrap: 60 min - $90\n\n")
    f.write("## Facial Treatments\n- Classic Facial: 60 min - $75\n- Anti-aging: 90 min - $130\n")

# 5. PDF file (.pdf) - use reportlab if available, otherwise create minimal PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    c = canvas.Canvas("test_dining_guide.pdf", pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, "The Riverie - Dining Guide")
    c.setFont("Helvetica", 12)
    c.drawString(72, 720, "Main Restaurant: Open 7 AM - 11 PM")
    c.drawString(72, 700, "Poolside Bar: Open 10 AM - 8 PM")
    c.drawString(72, 680, "Room Service: Available 24 hours")
    c.drawString(72, 650, "Breakfast Buffet: 7 AM - 10:30 AM ($25 per person)")
    c.drawString(72, 630, "Sunday Brunch: 10 AM - 2 PM ($45 per person)")
    c.save()
    print("PDF created with reportlab")
except ImportError:
    # Minimal valid PDF
    pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 120>>stream
BT /F1 14 Tf 72 750 Td (The Riverie - Dining Guide) Tj 0 -20 Td /F1 11 Tf (Main Restaurant: Open 7 AM - 11 PM) Tj ET
endstream endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000438 00000 n 
trailer<</Size 6/Root 1 0 R>>
startxref
509
%%EOF"""
    with open("test_dining_guide.pdf", "wb") as f:
        f.write(pdf_content)
    print("PDF created (minimal)")

# 6. DOCX file (.docx) - use python-docx if available
try:
    from docx import Document
    doc = Document()
    doc.add_heading("The Riverie - Guest Policies", level=1)
    doc.add_paragraph("Check-in: 3:00 PM | Check-out: 11:00 AM")
    doc.add_paragraph("Early check-in available upon request (subject to availability)")
    doc.add_paragraph("Late check-out until 2:00 PM: $30 surcharge")
    doc.add_paragraph("Children under 12 stay free when sharing parents' room")
    doc.add_paragraph("Complimentary airport shuttle service (advance booking required)")
    doc.save("test_guest_policies.docx")
    print("DOCX created with python-docx")
except ImportError:
    print("DOCX skipped (python-docx not available)")

# 7. HTML file (.html)
with open("test_facilities.html", "w") as f:
    f.write("<html><head><title>Hotel Facilities</title></head><body>\n")
    f.write("<h1>The Riverie - Facilities</h1>\n")
    f.write("<h2>Swimming Pool</h2><p>Olympic-sized infinity pool, open 6 AM to 10 PM</p>\n")
    f.write("<h2>Fitness Center</h2><p>24-hour gym with personal trainers available</p>\n")
    f.write("<h2>Business Center</h2><p>Meeting rooms, printing, and video conferencing</p>\n")
    f.write("</body></html>")

print("\nAll test files created:")
for f in sorted(os.listdir(".")):
    if f.startswith("test_"):
        print(f"  {f} ({os.path.getsize(f)} bytes)")
