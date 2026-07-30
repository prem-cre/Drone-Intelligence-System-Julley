import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(DATA_DIR, "data", "sample_pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

def create_pdf(filename: str, title: str, subtitle: str, content_blocks: list):
    pdf_path = os.path.join(PDF_DIR, filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        'DocHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0369a1'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )
    
    story = [
        Paragraph(title, title_style),
        Paragraph(subtitle, subtitle_style),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=12)
    ]
    
    for block in content_blocks:
        if block['type'] == 'heading':
            story.append(Paragraph(block['text'], heading_style))
        elif block['type'] == 'paragraph':
            story.append(Paragraph(block['text'], body_style))
        elif block['type'] == 'table':
            t = Table(block['data'], colWidths=block.get('widths'))
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284c7')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8.5),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))
            
    doc.build(story)
    print(f"Generated PDF -> {pdf_path}")

def generate_all_pdfs():
    # 1. DGCA Drone Rules 2021 Official PDF
    create_pdf(
        "DGCA_Drone_Rules_2021_Official.pdf",
        "Government of India — DGCA Drone Rules 2021",
        "Ministry of Civil Aviation | Published Gazette Notification G.S.R. 589(E)",
        [
            {"type": "heading", "text": "1. Classification of Unmanned Aircraft Systems"},
            {"type": "paragraph", "text": "Under Rule 5 of the Drone Rules 2021 (amended 2023), all drones operating in Indian airspace are classified based on Maximum Take-Off Weight (MTOW):"},
            {
                "type": "table",
                "widths": [90, 110, 80, 100, 120],
                "data": [
                    ["Category", "Weight Range (MTOW)", "Speed Limit", "Registration (UIN)", "Remote Pilot Cert."],
                    ["Nano", "<= 250 grams", "15 m/s", "Exempted", "Not Required"],
                    ["Micro", "250 grams - 2 kg", "25 m/s", "Required on DigitalSky", "Required for Commercial"],
                    ["Small", "2 kg - 25 kg", "25 m/s", "Required on DigitalSky", "Required (RPC)"],
                    ["Medium", "25 kg - 150 kg", "Limited by TC", "Required on DigitalSky", "Required (RPC)"],
                    ["Large", "> 150 kg", "Strict Clearance", "Required on DigitalSky", "Required (RPC)"]
                ]
            },
            {"type": "heading", "text": "2. DigitalSky Airspace Zoning & Permits"},
            {"type": "paragraph", "text": "Airspace over India is partitioned into Green, Yellow, and Red zones on the DigitalSky platform. No flight permission is required for operating micro and small drones in Green Zones up to 400 feet (120 meters) AGL."},
            {"type": "heading", "text": "3. NPNT Hardware Compliance & Penalties"},
            {"type": "paragraph", "text": "No Permission No Take-off (NPNT) is a hardware firmware protocol. Flying in a Red Zone or without valid UIN registration constitutes an offense under Rule 24, subject to penalties up to Rs. 1,00,000 under the Aircraft Act, 1934."}
        ]
    )

    # 2. Namo Drone Didi Scheme Guidelines PDF
    create_pdf(
        "Namo_Drone_Didi_Scheme_Guidelines.pdf",
        "Namo Drone Didi Scheme — Central Sector Policy Guidelines",
        "Ministry of Agriculture & Farmers Welfare | Government of India Initiative",
        [
            {"type": "heading", "text": "1. Executive Summary & Objective"},
            {"type": "paragraph", "text": "The Namo Drone Didi scheme aims to empower 15,000 women Self-Help Groups (SHGs) by providing agricultural drones for liquid fertilizer (Nano Urea) and pesticide spraying across rural India."},
            {"type": "heading", "text": "2. Financial Subsidy & Support Architecture"},
            {
                "type": "table",
                "widths": [140, 160, 200],
                "data": [
                    ["Beneficiary Category", "Government Capital Subsidy", "Max Financial Support"],
                    ["Women Self-Help Groups (SHGs)", "80% of Drone Package Cost", "Up to Rs. 8,00,000 per SHG"],
                    ["Custom Hiring Centers (CHCs)", "40% - 50% Subsidy", "Up to Rs. 5,00,000"],
                    ["Individual Farmers", "40% Subsidy", "Up to Rs. 4,00,000"]
                ]
            },
            {"type": "heading", "text": "3. Operational Training & RPTO Licensing"},
            {"type": "paragraph", "text": "Selected women SHG members undergo a 15-day mandatory training program (5-day mandatory remote pilot training at DGCA-approved Remote Pilot Training Organizations + 10-day agricultural application module)."}
        ]
    )

    # 3. Agricultural Drone Spraying SOP PDF
    create_pdf(
        "Agricultural_Drone_Spraying_SOP.pdf",
        "Standard Operating Procedure (SOP): Agricultural Drone Spraying",
        "ICAR & Directorate of Plant Protection, Quarantine & Storage",
        [
            {"type": "heading", "text": "1. Field Execution Protocol"},
            {"type": "paragraph", "text": "Drone spraying achieves high precision micro-droplet deposition. Pilots must maintain an altitude of 1.5 to 2.0 meters above crop canopy with a swath width of 3.5 to 4.5 meters."},
            {"type": "heading", "text": "2. Efficiency Comparison: Manual vs Drone Spraying"},
            {
                "type": "table",
                "widths": [120, 140, 140, 100],
                "data": [
                    ["Metric", "Manual Labor Spraying", "Drone Spraying", "Improvement"],
                    ["Water Volume", "200 - 250 Liters / Acre", "10 - 12 Liters / Acre", "95% Reduction"],
                    ["Chemical Savings", "100% Standard Dosage", "75% Ultra-Low Volume", "25% Savings"],
                    ["Operational Speed", "3.5 Hours / Acre", "7 - 10 Minutes / Acre", "25x Faster"],
                    ["Labor Health Risk", "High Dermal Exposure", "Zero Direct Contact", "100% Safe"]
                ]
            },
            {"type": "heading", "text": "3. Weather Limitations & Safety Limits"},
            {"type": "paragraph", "text": "Do not operate drones when wind speed exceeds 25 km/h, ambient temperature exceeds 40 degrees C, or during heavy precipitation/fog."}
        ]
    )

    # 4. ideaForge NETRA v4 Technical Manual PDF
    create_pdf(
        "ideaForge_NETRA_v4_Technical_Manual.pdf",
        "ideaForge NETRA v4 — Technical Specifications & Operations",
        "ideaForge Technology Limited | DGCA Type Certified UAV System",
        [
            {"type": "heading", "text": "1. System Specifications"},
            {"type": "paragraph", "text": "The NETRA v4 is a high-altitude surveillance UAV equipped with dual optical thermal payloads for intelligence, surveillance, and reconnaissance (ISR)."},
            {
                "type": "table",
                "widths": [150, 180, 170],
                "data": [
                    ["Specification Parameter", "Value / Rating", "Notes"],
                    ["MTOW (Weight)", "2.2 kg", "Micro Drone Category"],
                    ["Battery Capacity", "12,000 mAh LiPo", "Custom Smart Battery"],
                    ["Max Flight Time", "45 Minutes", "At Mean Sea Level"],
                    ["Operational Range", "10.0 km Line-of-Sight", "Encrypted HD Video Link"],
                    ["Max Altitude", "3,000m Above Ground", "High Altitude Capable"],
                    ["Payload", "Day Optical + Night Thermal", "Dual Gimbal Stabilized"]
                ]
            },
            {"type": "heading", "text": "2. Fail-Safe Protocols"},
            {"type": "paragraph", "text": "Includes Automatic Return-to-Home (RTH) on Low Battery, Fail-Safe on Signal Loss, Geofence Enforcement, and Emergency Parachute Recovery."}
        ]
    )

if __name__ == "__main__":
    generate_all_pdfs()
