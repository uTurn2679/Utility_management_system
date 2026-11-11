import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def replace_picture(slide, old_shape, new_img_path):
    if not os.path.exists(new_img_path):
        print(f"Warning: image path not found: {new_img_path}")
        return old_shape
    left, top, width, height = old_shape.left, old_shape.top, old_shape.width, old_shape.height
    sp = old_shape._element
    sp.getparent().remove(sp)
    new_pic = slide.shapes.add_picture(new_img_path, left, top, width, height)
    return new_pic

def set_font_run(run, text, font_name="Times New Roman", size_pt=20, bold=False, color_rgb=(30,30,30)):
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(*color_rgb)

def generate_presentation():
    template_path = 'Presentation3.pptx'
    out_path = 'Utility_Management_System_Presentation.pptx'

    prs = Presentation(template_path)
    print(f"Loaded {template_path}, total slides: {len(prs.slides)}")

    FONT_FAMILY = "Times New Roman"

    # =========================================================================
    # SLIDE 1: Welcome Slide
    # =========================================================================
    slide1 = prs.slides[0]
    for s in slide1.shapes:
        if s.name == "TextBox 5":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r1 = p.add_run()
            set_font_run(r1, "Welcome To ", FONT_FAMILY, 28, True, (20, 20, 20))
            r2 = p.add_run()
            set_font_run(r2, "Utility Management System", FONT_FAMILY, 28, True, (0, 75, 140))
        elif s.shape_type == 13: # Picture 4
            # Hero picture - Use GIS / Dashboard overview
            replace_picture(slide1, s, 'scratch/existing_media/image3.png')

    # =========================================================================
    # SLIDE 2: Project Details & Team Member
    # =========================================================================
    slide2 = prs.slides[1]
    for s in slide2.shapes:
        if s.name == "Title 1":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            set_font_run(r, "Project name: Utility Management System", FONT_FAMILY, 28, True, (0, 75, 140))
        elif s.name == "TextBox 6":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            set_font_run(r, "Multi-Utility Metering, Billing, GIS & Service Automation", FONT_FAMILY, 20, False, (70, 70, 70))
        elif s.name == "TextBox 7":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            r = p.add_run()
            set_font_run(r, "Project Contributor & Author :", FONT_FAMILY, 24, True, (0, 75, 140))
        elif s.name == "TextBox 2":
            # Student Profile
            s.text_frame.clear()
            lines = [
                ("NAME : JASIKA NOOR", True),
                ("ID : 22CSE002", True),
                ("SESSION : 2022-2023", True),
                ("DEPT : CSE", True)
            ]
            for idx, (txt, bold) in enumerate(lines):
                p = s.text_frame.paragraphs[0] if idx == 0 else s.text_frame.add_paragraph()
                r = p.add_run()
                set_font_run(r, txt, FONT_FAMILY, 20, bold, (30, 30, 30))
                p.space_after = Pt(4)
        elif s.name == "TextBox 4":
            # Project & Academic Context
            s.text_frame.clear()
            lines = [
                ("COURSE : Software Engineering (Lab)", True),
                ("ROLE : Full-Stack Developer & Analyst", True),
                ("TECH : Node.js, Express, MySQL, Leaflet", True),
                ("METHODOLOGY : SDLC Framework", True)
            ]
            for idx, (txt, bold) in enumerate(lines):
                p = s.text_frame.paragraphs[0] if idx == 0 else s.text_frame.add_paragraph()
                r = p.add_run()
                set_font_run(r, txt, FONT_FAMILY, 20, bold, (30, 30, 30))
                p.space_after = Pt(4)

    # =========================================================================
    # SLIDE 3: Introduction
    # =========================================================================
    slide3 = prs.slides[2]
    for s in slide3.shapes:
        if s.name == "Title 1":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            set_font_run(r, "Introduction", FONT_FAMILY, 32, True, (0, 75, 140))
        elif s.name == "TextBox 2":
            s.text_frame.clear()
            paras = [
                "Utility Management System is an enterprise-grade web application designed to digitize, streamline, and automate multi-utility operations (Electricity, Water, and Gas). The platform integrates automated meter consumption tracking, a dynamic tiered billing engine, Leaflet.js GIS spatial mapping, and digital payment processing into a single unified solution.",
                "It provides dedicated panels for Customers, Field Staff/Engineers, and System Administrators, along with features such as Smart Meter Inventory, Consumption Delta Tracking, Automated Invoicing with Due-Date Alerts via Nodemailer, QR Code Bill Verification, and Maintenance Ticket Dispatch.",
                "The system was developed following the Software Development Life Cycle (SDLC) methodology to ensure system reliability, transactional accuracy, robust security, and scalability."
            ]
            for idx, text in enumerate(paras):
                p = s.text_frame.paragraphs[0] if idx == 0 else s.text_frame.add_paragraph()
                r = p.add_run()
                set_font_run(r, text, FONT_FAMILY, 21, False, (30, 30, 30))
                p.space_after = Pt(14)

    # =========================================================================
    # SLIDE 4: SDLC Life Cycle
    # =========================================================================
    slide4 = prs.slides[3]
    for s in slide4.shapes:
        if s.name == "Title 1":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            set_font_run(r, "SDLC life cycle :", FONT_FAMILY, 28, True, (0, 75, 140))
        # Keep Picture 6 (universal SDLC lifecycle diagram)

    # =========================================================================
    # SLIDE 5: Planning Phase
    # =========================================================================
    slide5 = prs.slides[4]
    for s in slide5.shapes:
        if s.name == "Title 1":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            set_font_run(r, "Planning :", FONT_FAMILY, 28, True, (0, 75, 140))
        elif s.name == "TextBox 10":
            s.text_frame.clear()
            p0 = s.text_frame.paragraphs[0]
            r0 = p0.add_run()
            set_font_run(r0, "Planning Phase", FONT_FAMILY, 24, True, (0, 75, 140))
            p0.space_after = Pt(8)

            bullets = [
                "Identified the critical need to digitize manual, error-prone meter readings and paper-based utility billing operations.",
                "Defined project goals, scope, and target user classes (Customers, Field Staff/Technicians, and Administrators).",
                "Structured a 6-phase Work Breakdown Structure (WBS) decomposing high-risk modules (billing calculation and GIS mapping).",
                "Applied PERT 3-point estimation (Optimistic, Most Likely, Pessimistic) to compute Expected Task Duration: TE = (O + 4M + P) / 6.",
                "Constructed a 15-week academic semester Gantt chart roadmap and identified the project Critical Path."
            ]
            for b in bullets:
                p = s.text_frame.add_paragraph()
                r = p.add_run()
                set_font_run(r, b, FONT_FAMILY, 21, False, (30, 30, 30))
                p.space_after = Pt(8)

            p_out = s.text_frame.add_paragraph()
            r_label = p_out.add_run()
            set_font_run(r_label, "Outcome: ", FONT_FAMILY, 21, True, (0, 75, 140))
            r_val = p_out.add_run()
            set_font_run(r_val, "A structured project plan, resource allocation matrix, and risk mitigation roadmap guiding systematic execution.", FONT_FAMILY, 21, False, (30, 30, 30))

    # =========================================================================
    # SLIDE 6: Requirement Analysis
    # =========================================================================
    slide6 = prs.slides[5]
    for s in slide6.shapes:
        if s.name == "Title 1":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            set_font_run(r, "Requirement analysis :", FONT_FAMILY, 28, True, (0, 75, 140))
        elif s.name == "TextBox 2":
            s.text_frame.clear()
            p0 = s.text_frame.paragraphs[0]
            r0 = p0.add_run()
            set_font_run(r0, "Requirements Analysis", FONT_FAMILY, 22, True, (0, 75, 140))
            p0.space_after = Pt(8)

            bullets = [
                "Identified 42 functional requirements (FR-01 to FR-42 across 10 modules) and non-functional requirements (NFRs).",
                "Defined user roles: Customer, Utility Field Staff, and System Administrator with strict role-based access control.",
                "Captured domain requirements for multi-utility meter tracking (Electricity, Water, Gas), reading delta calculation, and tiered tariff billing.",
                "Specified digital payment records (bKash, Nagad, Bank), QR code bill verification, and Leaflet.js GIS spatial mapping.",
                "Established performance (<1s API latency), security (SQL injection prevention, password hashing), and relational integrity standards."
            ]
            for b in bullets:
                p = s.text_frame.add_paragraph()
                r = p.add_run()
                set_font_run(r, b, FONT_FAMILY, 19, False, (30, 30, 30))
                p.space_after = Pt(8)
        elif s.shape_type == 13: # Picture 4
            # Replace with Use Case Diagram
            replace_picture(slide6, s, 'use_case_diagram_book_style.png')

    # =========================================================================
    # SLIDE 7: Feasibility Study
    # =========================================================================
    slide7 = prs.slides[6]
    for s in slide7.shapes:
        if s.name == "Title 1":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            set_font_run(r, "Feasibility study :", FONT_FAMILY, 28, True, (0, 75, 140))
        elif s.name == "TextBox 2":
            s.text_frame.clear()
            p0 = s.text_frame.paragraphs[0]
            r0 = p0.add_run()
            set_font_run(r0, "Feasibility Study", FONT_FAMILY, 22, True, (0, 75, 140))
            p0.space_after = Pt(8)

            bullets = [
                "Evaluated the project across technical, economic, legal, operational, and schedule dimensions.",
                "Technical Feasibility: Confirmed availability and maturity of Node.js, Express.js REST APIs, MySQL 8.0, Leaflet.js, and Chart.js.",
                "Economic Feasibility: Built entirely on open-source web technologies with zero licensing fees; automated billing drastically reduces utility operating costs.",
                "Operational Feasibility: Intuitive glassmorphic web UI requires minimal operator training and enables consumer self-service.",
                "Legal & Ethical Feasibility: Strictly complies with utility tariff policies, data privacy guidelines, and consumer financial security standards.",
                "Schedule Feasibility: 15-week academic semester schedule validated via Critical Path Analysis, ensuring timely completion."
            ]
            for b in bullets:
                p = s.text_frame.add_paragraph()
                r = p.add_run()
                set_font_run(r, b, FONT_FAMILY, 19, False, (30, 30, 30))
                p.space_after = Pt(8)
        # Keep Picture 4 (feasibility graphic)

    # =========================================================================
    # SLIDE 8: System Design
    # =========================================================================
    slide8 = prs.slides[7]
    for s in slide8.shapes:
        if s.name == "Title 1":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            set_font_run(r, "Design: System Design", FONT_FAMILY, 28, True, (0, 75, 140))
        elif s.name == "TextBox 3":
            s.text_frame.clear()
            p0 = s.text_frame.paragraphs[0]
            r0 = p0.add_run()
            set_font_run(r0, "System Design", FONT_FAMILY, 22, True, (0, 75, 140))
            p0.space_after = Pt(8)

            bullets = [
                "Designed a Decoupled Three-Tier Architecture: Presentation Layer (SPA), Business Logic Layer (Express APIs), and Data Layer (MySQL).",
                "Structured normalized relational database schema with 9 tables (users, customers, meters, readings, bills, payments, complaints, notifications, maintenance).",
                "Modeled comprehensive UML specifications: Class Diagram, Sequence Diagrams (Auth, Billing, Payment, Complaint), and DFD Level 1.",
                "Established secure dual-port architecture with CORS protection, connection pooling, and bcrypt password hashing.",
                "Developed responsive, user-friendly dashboards tailored to Customer, Field Staff, and Administrator workflows."
            ]
            for b in bullets:
                p = s.text_frame.add_paragraph()
                r = p.add_run()
                set_font_run(r, b, FONT_FAMILY, 19, False, (30, 30, 30))
                p.space_after = Pt(8)
        elif s.shape_type == 13: # Picture 4
            # Replace with Class Diagram
            replace_picture(slide8, s, 'class_diagram_book_style.png')

    # =========================================================================
    # SLIDE 9: Building & Implementation - Customer Section
    # =========================================================================
    slide9 = prs.slides[8]
    for s in slide9.shapes:
        if s.name == "Title 1":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            set_font_run(r, "Building and implementation :", FONT_FAMILY, 28, True, (0, 75, 140))
        elif s.name == "TextBox 2":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            r = p.add_run()
            set_font_run(r, "Customer section :", FONT_FAMILY, 22, True, (0, 75, 140))

    # Replace pictures on slide 9 (Customer UI Screenshots)
    # Picture 4, 6, 8 (top row); Picture 10, 12, 14 (bottom row)
    cust_images = [
        ("Picture 4", "scratch/existing_media/image3.png"),             # Customer Dashboard
        ("Picture 6", "scratch/existing_media/image5.png"),             # Bills & Invoices
        ("Picture 8", "scratch/existing_media/image6.png"),             # QR Code Verification
        ("Picture 10", "seq_diagram_payment_book_style.png"),          # Payment Sequence
        ("Picture 12", "seq_diagram_auth_book_style.png"),             # Auth Sequence
        ("Picture 14", "scratch/existing_media/image9.png")             # Support Ticket
    ]
    for s in list(slide9.shapes):
        for pic_name, img_path in cust_images:
            if s.name == pic_name:
                replace_picture(slide9, s, img_path)

    # =========================================================================
    # SLIDE 10: Building & Implementation - Field Staff Section
    # =========================================================================
    slide10 = prs.slides[9]
    for s in slide10.shapes:
        if s.name == "TextBox 1":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            r = p.add_run()
            set_font_run(r, "Field Staff & Technician section :", FONT_FAMILY, 24, True, (0, 75, 140))

    # Replace pictures on slide 10 (Field Staff UI & Sequence)
    # Picture 3, 5, 7 (top row); Picture 9, 11, 13 (middle row); Picture 15 (bottom row)
    staff_images = [
        ("Picture 3", "scratch/existing_media/image4.png"),             # Meter Readings
        ("Picture 5", "scratch/existing_media/image7.png"),             # GIS Outage Map
        ("Picture 7", "scratch/existing_media/image9.png"),             # Maintenance Jobs
        ("Picture 9", "seq_diagram_billing_book_style.png"),           # Billing Sequence
        ("Picture 11", "seq_diagram_complaint_book_style.png"),        # Complaint Sequence
        ("Picture 13", "scratch/existing_media/image8.jpg"),            # Nodemailer Alerts
        ("Picture 15", "scratch/existing_media/image3.png")             # Analytics Overview
    ]
    for s in list(slide10.shapes):
        for pic_name, img_path in staff_images:
            if s.name == pic_name:
                replace_picture(slide10, s, img_path)

    # =========================================================================
    # SLIDE 11: Building & Implementation - Admin Section
    # =========================================================================
    slide11 = prs.slides[10]
    for s in slide11.shapes:
        if s.name == "TextBox 1":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            r = p.add_run()
            set_font_run(r, "Admin section :", FONT_FAMILY, 24, True, (0, 75, 140))

    # Replace pictures on slide 11 (Admin UI Screenshots)
    # Picture 3, 5 (top row); Picture 7, 9, 11 (bottom row)
    admin_images = [
        ("Picture 3", "scratch/existing_media/image3.png"),             # Admin Dashboard KPIs
        ("Picture 5", "scratch/existing_media/image4.png"),             # Customer & Meter Directory
        ("Picture 7", "scratch/existing_media/image5.png"),             # Batch Billing Engine
        ("Picture 9", "scratch/existing_media/image7.png"),             # GIS Spatial Map
        ("Picture 11", "scratch/existing_media/image8.jpg")             # Email Alert Hub
    ]
    for s in list(slide11.shapes):
        for pic_name, img_path in admin_images:
            if s.name == pic_name:
                replace_picture(slide11, s, img_path)

    # =========================================================================
    # SLIDE 12: Testing Phase
    # =========================================================================
    slide12 = prs.slides[11]
    for s in slide12.shapes:
        if s.name == "Title 1":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            set_font_run(r, "Testing :", FONT_FAMILY, 28, True, (0, 75, 140))
        elif s.name == "TextBox 2":
            s.text_frame.clear()
            p0 = s.text_frame.paragraphs[0]
            r0 = p0.add_run()
            set_font_run(r0, "Testing Phase", FONT_FAMILY, 24, True, (0, 75, 140))
            p0.space_after = Pt(8)

            tests = [
                ("Unit Testing: ", "Verified arithmetic accuracy of tiered billing calculation algorithms, tariff tier boundaries, and consumption delta logic."),
                ("Integration Testing: ", "Validated REST API endpoints, MySQL connection pool transaction rollback, and Nodemailer SMTP relay integration."),
                ("System Testing: ", "Executed full end-to-end workflows: meter reading entry -> invoice generation -> payment settlement -> receipt dispatch."),
                ("Security Testing: ", "Verified parameterized SQL queries preventing SQL injection, bcrypt password hashing, and role-based route guards."),
                ("User Acceptance Testing (UAT): ", "Tested real-world operational workflows across Customer, Field Staff, and Administrator user personas.")
            ]
            for label, desc in tests:
                p = s.text_frame.add_paragraph()
                r1 = p.add_run()
                set_font_run(r1, label, FONT_FAMILY, 20, True, (0, 75, 140))
                r2 = p.add_run()
                set_font_run(r2, desc, FONT_FAMILY, 20, False, (30, 30, 30))
                p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 13: Deployment Phase
    # =========================================================================
    slide13 = prs.slides[12]
    for s in slide13.shapes:
        if s.name == "Title 1":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            set_font_run(r, "Deployment :", FONT_FAMILY, 28, True, (0, 75, 140))
        elif s.name == "TextBox 7":
            s.text_frame.clear()
            p0 = s.text_frame.paragraphs[0]
            r0 = p0.add_run()
            set_font_run(r0, "Deployment Phase", FONT_FAMILY, 22, True, (0, 75, 140))
            p0.space_after = Pt(8)

            steps = [
                "Configured Node.js production runtime with Express backend listening on API port 5000.",
                "Provisioned MySQL 8.0 relational database schema (utilis_db) with client connection pooling.",
                "Deployed modern Single Page Application (SPA) frontend served via lightweight HTTP static server on port 8080.",
                "Implemented CORS policies and environment variable configuration (.env) for database credentials and Nodemailer SMTP relay.",
                "Verified sub-second API latency, high availability, and secure SSL/HTTPS configuration before release.",
                "The backend is powered by Node.js/Express, database on MySQL, and frontend on modern SPA server."
            ]
            for step in steps:
                p = s.text_frame.add_paragraph()
                r = p.add_run()
                set_font_run(r, step, FONT_FAMILY, 19, False, (30, 30, 30))
                p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 14: Maintenance Phase
    # =========================================================================
    slide14 = prs.slides[13]
    for s in slide14.shapes:
        if s.name == "Title 1":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            set_font_run(r, "Maintenance: ", FONT_FAMILY, 28, True, (0, 75, 140))
        elif s.name == "TextBox 2":
            s.text_frame.clear()
            p0 = s.text_frame.paragraphs[0]
            r0 = p0.add_run()
            set_font_run(r0, "Maintenance Phase", FONT_FAMILY, 24, True, (0, 75, 140))
            p0.space_after = Pt(8)

            maint = [
                "Regularly monitored REST API response latency, server throughput, and MySQL database connection pool performance.",
                "Optimized email notification dispatch by implementing asynchronous background processing to prevent API latency.",
                "Performed scheduled database maintenance, transaction archiving, and disaster recovery backup procedures.",
                "Updated tariff rates, utility pricing tiers, and system configurations based on regulatory updates.",
                "Applied routine software updates, security patches, and resolved user-reported bug tickets."
            ]
            for m in maint:
                p = s.text_frame.add_paragraph()
                r = p.add_run()
                set_font_run(r, m, FONT_FAMILY, 21, False, (30, 30, 30))
                p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 15: Conclusion
    # =========================================================================
    slide15 = prs.slides[14]
    for s in slide15.shapes:
        if s.name == "Title 4":
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            set_font_run(r, "Conclusion :", FONT_FAMILY, 28, True, (0, 75, 140))
        elif s.name == "TextBox 6":
            s.text_frame.clear()
            points = [
                "Utility Management System successfully provides a modern, automated, and secure multi-utility management platform.",
                "The system integrates automated consumption tracking, dynamic tiered billing, Leaflet.js GIS spatial mapping, and digital payments into a single ecosystem.",
                "Dedicated Customer, Field Staff, and Admin portals eliminate manual billing errors and streamline utility operations.",
                "Rigorous adherence to the Software Development Life Cycle (SDLC) ensured structured execution, robust software quality, and on-time delivery.",
                "Significantly enhances utility administrative efficiency, reduces billing disputes, and provides an extensible foundation for future smart city IoT integration."
            ]
            for idx, pt in enumerate(points):
                p = s.text_frame.paragraphs[0] if idx == 0 else s.text_frame.add_paragraph()
                r = p.add_run()
                set_font_run(r, pt, FONT_FAMILY, 21, False, (30, 30, 30))
                p.space_after = Pt(10)

    # =========================================================================
    # SLIDE 16: Closing / Thank You
    # =========================================================================
    slide16 = prs.slides[15]
    for s in slide16.shapes:
        if s.name == "TextBox 1":
            s.text_frame.clear()
            p0 = s.text_frame.paragraphs[0]
            p0.alignment = PP_ALIGN.CENTER
            r0 = p0.add_run()
            set_font_run(r0, "Thank you all", FONT_FAMILY, 52, True, (0, 75, 140))
            p0.space_after = Pt(16)

            p1 = s.text_frame.add_paragraph()
            p1.alignment = PP_ALIGN.CENTER
            r1 = p1.add_run()
            set_font_run(r1, "Utility Management System", FONT_FAMILY, 26, True, (30, 30, 30))
            p1.space_after = Pt(8)

            p2 = s.text_frame.add_paragraph()
            p2.alignment = PP_ALIGN.CENTER
            r2 = p2.add_run()
            set_font_run(r2, "Jasika Noor | ID: 22CSE002 | Session: 2022-2023 | Dept of CSE", FONT_FAMILY, 20, False, (70, 70, 70))
            p2.space_after = Pt(12)

            p3 = s.text_frame.add_paragraph()
            p3.alignment = PP_ALIGN.CENTER
            r3 = p3.add_run()
            set_font_run(r3, "Questions & Discussion", FONT_FAMILY, 22, True, (0, 75, 140))

    prs.save(out_path)
    print(f"Successfully generated: {out_path}")

if __name__ == "__main__":
    generate_presentation()

