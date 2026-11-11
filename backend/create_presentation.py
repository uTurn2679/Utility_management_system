from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_deck():
    prs = Presentation()
    
    # 1. Slide Colors & Fonts Setup
    title_font_name = 'Arial'
    body_font_name = 'Arial'
    
    # Theme colors
    c_primary_dark = RGBColor(18, 18, 30)      # Dark Slate
    c_primary_blue = RGBColor(0, 242, 254)     # Cyan
    c_accent_orange = RGBColor(255, 94, 98)    # Coral/Orange
    c_light_bg = RGBColor(245, 247, 250)       # Light Grey
    c_white = RGBColor(255, 255, 255)
    c_text_dark = RGBColor(33, 37, 41)
    c_text_muted = RGBColor(108, 117, 125)

    # Slide 1: Title Slide (Dark Background)
    slide_layout = prs.slide_layouts[6] # Blank Layout
    slide = prs.slides.add_slide(slide_layout)
    
    # Background card
    background = slide.shapes.add_shape(
        1, # MSO_SHAPE.RECTANGLE
        0, 0, prs.slide_width, prs.slide_height
    )
    background.fill.solid()
    background.fill.fore_color.rgb = c_primary_dark
    background.line.fill.background()

    # Title & Subtitle text box
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(9), Inches(4))
    tf = txBox.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "UTILIS"
    p.font.name = title_font_name
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = c_primary_blue
    p.alignment = PP_ALIGN.LEFT

    p2 = tf.add_paragraph()
    p2.text = "Intelligent Utility Billing & GIS Management System"
    p2.font.name = title_font_name
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = c_white
    p2.alignment = PP_ALIGN.LEFT
    p2.space_before = Pt(10)

    p3 = tf.add_paragraph()
    p3.text = "Project Presentation | Dept. of Computer Science & Engineering\nGopalganj Science and Technology University"
    p3.font.name = body_font_name
    p3.font.size = Pt(16)
    p3.font.color.rgb = c_text_muted
    p3.alignment = PP_ALIGN.LEFT
    p3.space_before = Pt(40)

    # Helper function to add content slides
    def add_content_slide(title, bullets):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        
        # Add light background
        bg = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = c_light_bg
        bg.line.fill.background()

        # Add top banner
        banner = slide.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(1))
        banner.fill.solid()
        banner.fill.fore_color.rgb = c_primary_dark
        banner.line.fill.background()

        # Title text
        txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.15), Inches(9), Inches(0.8))
        tf = txBox.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = title_font_name
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = c_primary_blue

        # Bullets content text box
        contentBox = slide.shapes.add_textbox(Inches(0.75), Inches(1.5), Inches(8.5), Inches(5))
        ctf = contentBox.text_frame
        ctf.word_wrap = True

        for idx, item in enumerate(bullets):
            p = ctf.paragraphs[0] if idx == 0 else ctf.add_paragraph()
            p.text = item[0]
            p.font.name = body_font_name
            p.font.size = Pt(18)
            p.font.bold = True
            p.font.color.rgb = c_text_dark
            p.space_after = Pt(4)
            p.space_before = Pt(8) if idx > 0 else Pt(0)
            
            if len(item) > 1:
                # Add sub-bullet points
                for sub in item[1]:
                    sub_p = ctf.add_paragraph()
                    sub_p.text = "• " + sub
                    sub_p.font.name = body_font_name
                    sub_p.font.size = Pt(14)
                    sub_p.font.color.rgb = c_text_muted
                    sub_p.level = 1
                    sub_p.space_before = Pt(2)
                    sub_p.space_after = Pt(2)

    # Slide 2: Introduction
    add_content_slide(
        "Introduction & Problem Statement",
        [
            ("Traditional System Limitations", [
                "Manual paper-based reading entry resulting in human errors.",
                "Lack of direct online payment verification leading to billing disputes.",
                "Slow reporting and repair dispatch workflows."
            ]),
            ("The Utilis Opportunity", [
                "A fully automated Single Page Application (SPA) architecture.",
                "Integrated real-time database schema ensuring 100% data consistency.",
                "Direct spatial (GIS) view of utility grid issues."
            ])
        ]
    )

    # Slide 3: Key Features (Admin)
    add_content_slide(
        "Admin Portal Capabilities",
        [
            ("Utility Meter & Customer Directory", [
                "Add, modify, and delete customer connection details.",
                "Link physical smart meters (Electricity, Water, Gas, WiFi) to customers."
            ]),
            ("Billing & Invoicing Engine", [
                "Generate manual invoices based on custom readings.",
                "Batch trigger 'Auto Generate Bills' for all outstanding meters in seconds."
            ]),
            ("Operations Management", [
                "Review payment transactions and verify online payments.",
                "Assign technician (Employee) profiles to maintenance tasks."
            ])
        ]
    )

    # Slide 4: Key Features (Customer)
    add_content_slide(
        "Customer Portal Capabilities",
        [
            ("Personalized Dashboard", [
                "View consumption trends, active meters, and pending invoices."
            ]),
            ("Secure Digital Invoices", [
                "Printable PDF invoices with transaction details.",
                "Integrated QR Code for instant verification."
            ]),
            ("Online Support Requests", [
                "Submit billing disputes or connection tickets.",
                "File emergency maintenance requests (gas leak, water leak, meter fault)."
            ])
        ]
    )

    # Slide 5: QR Code Verification
    add_content_slide(
        "QR Code Bill System",
        [
            ("Automatic QR Generation", [
                "Free, lightweight API integration to generate unique QR images dynamically on bills."
            ]),
            ("Public Invoice View Route", [
                "Scans directly redirect to a secure, public unauthenticated path (#/public-bill-view).",
                "Allows the customer (or field officers) to verify invoice legitimacy instantly in the browser without logging in."
            ])
        ]
    )

    # Slide 6: Geographic Analytics (GIS)
    add_content_slide(
        "Geographic Analytics (GIS)",
        [
            ("Interactive Leaflet.js Mapping", [
                "Renders high-quality Dark Tile open-source map of Dhaka city."
            ]),
            ("Utility Demand Layer", [
                "Renders demand circles scaled by total billing amount.",
                "High demand areas (e.g. Uttara, Dhanmondi) stand out visually in red/yellow."
            ]),
            ("Incidents / Complaint Hotspots Layer", [
                "Renders red pin markers at coordinates of active complaints/leakages."
            ])
        ]
    )

    # Slide 7: Gmail Notification Engine
    add_content_slide(
        "Gmail Notification Engine",
        [
            ("Nodemailer SMTP Integration", [
                "Sends structured HTML invoices directly to customer email (e.g. Riya Akter) upon bill generation."
            ]),
            ("Due Date Cron Warning", [
                "Background process runs daily to identify unpaid invoices due in 1-2 days.",
                "Triggers alert emails advising immediate online payment."
            ]),
            ("Email Log & Fallback", [
                "Logs all sent emails to sent_emails.log for testing when SMTP server credentials are default."
            ])
        ]
    )

    # Slide 8: Technical Architecture
    add_content_slide(
        "System Technology Stack",
        [
            ("Frontend Client (SPA)", [
                "HTML5, CSS3 (Glassmorphism design tokens), Vanilla ES6 JavaScript.",
                "Leaflet.js (mapping framework), Chart.js (dashboard telemetry charts)."
            ]),
            ("Backend Server API", [
                "Node.js runtime environment.",
                "Express.js RESTful API endpoints matching PK_MAP relational queries."
            ]),
            ("Database & Mailing Engine", [
                "MySQL database (managed via connection pools).",
                "Nodemailer package (SMTP transport configuration)."
            ])
        ]
    )

    # Slide 9: Conclusion
    add_content_slide(
        "Conclusion & Future Enhancements",
        [
            ("Project Summary", [
                "Successfully solved manual billing errors, transparency issues, and maintenance delay risks."
            ]),
            ("Future Enhancements", [
                "Integrate real-time IoT smart meter APIs to fetch consumption readings automatically.",
                "Implement online payment gateways (bKash/SSLCommerz sandbox API) for instant automated checkout."
            ])
        ]
    )

    # Save presentation
    output_path = "C:\\Users\\Jasika\\Downloads\\Utilis_Project_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    create_deck()
