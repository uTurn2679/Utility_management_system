import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import os
import shutil
import win32com.client

def build_printable_srs_docx(output_docx_path):
    doc = docx.Document()

    # Color Palette for Print Optimization (Professional Blue/Slate)
    COLOR_PRIMARY = RGBColor(30, 41, 59)     # #1E293B
    COLOR_ACCENT = RGBColor(37, 99, 235)     # #2563EB
    COLOR_DARK = RGBColor(51, 65, 85)       # Body text
    COLOR_GRAY = RGBColor(100, 116, 139)    # Headers/footers/subtitles
    COLOR_WHITE = RGBColor(255, 255, 255)

    # 1. Page Margins (Standard 1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Set Default Font Style (Times New Roman for Formal Academic / Professional Print)
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = COLOR_DARK

    # Helper Functions
    def add_page_number_field(run):
        fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
        instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
        fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
        fldChar3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
        run._r.append(fldChar1)
        run._r.append(instrText)
        run._r.append(fldChar2)
        run._r.append(fldChar3)

    def add_numpages_field(run):
        fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
        instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> NUMPAGES </w:instrText>')
        fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
        fldChar3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
        run._r.append(fldChar1)
        run._r.append(instrText)
        run._r.append(fldChar2)
        run._r.append(fldChar3)

    def set_cell_background(cell, hex_color):
        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading_elm)

    def set_table_styling(table):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for row_idx, row in enumerate(table.rows):
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

            if row_idx == 0:
                trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
                for cell in row.cells:
                    set_cell_background(cell, "1E293B")
                    for p in cell.paragraphs:
                        p.paragraph_format.space_before = Pt(4)
                        p.paragraph_format.space_after = Pt(4)
                        for run in p.runs:
                            run.font.bold = True
                            run.font.color.rgb = COLOR_WHITE
            else:
                bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
                for cell in row.cells:
                    set_cell_background(cell, bg_color)
                    for p in cell.paragraphs:
                        p.paragraph_format.space_before = Pt(3)
                        p.paragraph_format.space_after = Pt(3)

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = COLOR_ACCENT
        return p

    def add_heading_3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        return p

    def add_body_p(text, bold_prefix=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.font.bold = True
            run_b.font.color.rgb = COLOR_PRIMARY
        run_t = p.add_run(text)
        return p

    # ==================== COVER PAGE ====================
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(120)
    title_p.paragraph_format.space_after = Pt(15)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = title_p.add_run("SOFTWARE REQUIREMENTS SPECIFICATION")
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(24)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(150)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = sub_p.add_run("Project: Utility Management System")
    r_sub.font.name = 'Times New Roman'
    r_sub.font.size = Pt(16)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_ACCENT

    meta_p = doc.add_paragraph()
    meta_p.paragraph_format.space_after = Pt(4)
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # AUTHOR INFO ONLY (Prepared for, Standard Compliance, Version, Date deleted as requested)
    r_prep = meta_p.add_run("Prepared by:\n")
    r_prep.font.bold = True
    r_prep.font.size = Pt(12)
    r_name = meta_p.add_run("Jasika Noor\n")
    r_name.font.bold = True
    r_name.font.size = Pt(14)
    r_name.font.color.rgb = COLOR_PRIMARY
    r_id = meta_p.add_run("Student ID: 22CSE002")
    r_id.font.bold = True
    r_id.font.size = Pt(12)

    # Cover page break
    doc.add_page_break()

    # Setup Section Headers & Footers for Document Body
    body_section = doc.sections[-1]
    header = body_section.header
    header_p = header.paragraphs[0]
    header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hdr = header_p.add_run("SOFTWARE REQUIREMENTS SPECIFICATION | UTILITY MANAGEMENT SYSTEM")
    r_hdr.font.size = Pt(8.5)
    r_hdr.font.color.rgb = COLOR_GRAY

    footer = body_section.footer
    footer_p = footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ftr = footer_p.add_run("Page ")
    r_ftr.font.size = Pt(9)
    r_ftr.font.color.rgb = COLOR_GRAY
    add_page_number_field(r_ftr)
    r_ftr2 = footer_p.add_run(" of ")
    r_ftr2.font.size = Pt(9)
    r_ftr2.font.color.rgb = COLOR_GRAY
    add_numpages_field(r_ftr2)

    # ==================== 1. INTRODUCTION ====================
    add_heading_1("1. Introduction")
    add_heading_2("1.1 Purpose")
    add_body_p("The purpose of this document is to define the full Software Requirements Specification (SRS) for the Utility Management System. This document outlines both functional and non-functional requirements, system architecture, database schema, user roles, external interface specifications, and data flow models. This specification serves as the official reference for software developers, database administrators, system architects, utility company operators, and project stakeholders.")

    add_heading_2("1.2 Scope")
    add_body_p("Utility Management System is an enterprise-grade, web-based utility administration and customer service portal designed to digitize and automate multi-utility management (Electricity, Water, and Gas). The application encompasses:")
    
    scope_points = [
        "Multi-Role Authentication & Access Control for Administrators, Utility Staff/Employees, and Consumers/Customers.",
        "Customer Directory & Profile Management linked to meter accounts and addresses.",
        "Smart Meter Registration & Consumption Tracking (Electricity, Water, Gas meter inventory and monthly reading logs).",
        "Automated Billing Engine & Tariff Rate Processing calculating bill amounts based on consumption delta (currReading - prevReading).",
        "Automated Email Notification System providing instant invoice notifications, due-date reminders, and payment receipts.",
        "Digital Payment Processing supporting multi-channel payment records (bKash, Nagad, Rocket, Bank Transfer, Credit Card).",
        "Customer Support Ticketing & Complaint Management with live comment threads and status pipelines.",
        "Field Maintenance Service Request System for technical repairs, meter installation, and field technician assignment.",
        "Geographic Information System (GIS) Mapping for spatial customer/meter distribution, substation tracking, and outage zone visualization.",
        "Analytics & Revenue Reporting generating monthly utility consumption charts, financial collection trends, and PDF export capabilities."
    ]
    for pt in scope_points:
        p_pt = doc.add_paragraph(style='List Bullet')
        p_pt.paragraph_format.space_after = Pt(3)
        p_pt.paragraph_format.line_spacing = 1.15
        p_pt.add_run(pt)

    add_heading_2("1.3 Definitions, Acronyms, and Abbreviations")
    tbl_terms = doc.add_table(rows=11, cols=2)
    tbl_terms.autofit = False
    tbl_terms.columns[0].width = Inches(2.2)
    tbl_terms.columns[1].width = Inches(4.3)
    terms_data = [
        ("Term / Acronym", "Meaning & Context"),
        ("SRS", "Software Requirements Specification"),
        ("UMS / utilis-app", "Utility Management System Platform"),
        ("FR / NFR", "Functional Requirement / Non-Functional Requirement"),
        ("GIS", "Geographic Information System (Spatial Map Visualization)"),
        ("SPA", "Single Page Application (Client-side dynamic UI)"),
        ("REST", "Representational State Transfer (HTTP API Architecture)"),
        ("CRUD", "Create, Read, Update, Delete database operations"),
        ("DFD", "Data Flow Diagram (Level 1 Process Architecture)"),
        ("ERD", "Entity Relationship Diagram (Database Schema Model)"),
        ("PK / FK", "Primary Key / Foreign Key in relational database design")
    ]
    for r_idx, (t_term, t_meaning) in enumerate(terms_data):
        row_cells = tbl_terms.rows[r_idx].cells
        row_cells[0].paragraphs[0].text = t_term
        row_cells[1].paragraphs[0].text = t_meaning
    set_table_styling(tbl_terms)

    add_heading_2("1.4 References")
    refs = [
        "IEEE Std 830-1998: IEEE Recommended Practice for Software Requirements Specifications.",
        "IEEE Std 29148-2018: Systems and software engineering — Life cycle processes — Requirements engineering.",
        "Sommerville, Ian. Software Engineering (10th Edition), Addison-Wesley.",
        "Express.js API Reference: https://expressjs.com/",
        "MySQL 8.0 Reference Manual: https://dev.mysql.com/doc/refman/8.0/en/",
        "Leaflet.js Interactive Maps: https://leafletjs.com/"
    ]
    for r_idx, ref in enumerate(refs, 1):
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_after = Pt(3)
        p_ref.add_run(f"{r_idx}. ").bold = True
        p_ref.add_run(ref)

    add_heading_2("1.5 Overview")
    add_body_p("This document is organized into seven core chapters:")
    chapters = [
        "Section 2: Overall Description (Product Perspective, User Classes, Operating Environment, Constraints).",
        "Section 3: System Features & Functional Requirements (FR-01 to FR-42 across 10 core modules).",
        "Section 4: External Interface Requirements (UI, Hardware, Software, Communication).",
        "Section 5: Non-Functional Requirements (Performance, Security, Reliability, Usability, Portability).",
        "Section 6: Other Requirements (Regulatory Compliance, Tariff Policies & Data Privacy).",
        "Section 7: Appendices (Data Flow Diagram Level 1 & Complete ERD Database Schema)."
    ]
    for ch in chapters:
        p_ch = doc.add_paragraph(style='List Bullet')
        p_ch.paragraph_format.space_after = Pt(3)
        p_ch.add_run(ch)

    # ==================== 2. OVERALL DESCRIPTION ====================
    add_heading_1("2. Overall Description")
    add_heading_2("2.1 Product Perspective")
    add_body_p("utilis-app is a self-contained full-stack web application designed with a decoupled architecture. The backend service layer operates using Node.js and Express.js interacting with a MySQL relational database (utilis_db). The frontend is a modern, responsive Single Page Application (SPA) communicating asynchronously via REST API endpoints.")

    add_heading_2("2.2 Product Functions")
    pf_items = [
        "User Authentication & Session Handling: Secure login, self-registration for customers, role-based session storage, and logout.",
        "Customer Master Directory: Centralized management of consumer personal details, contact info, utility service locations, and linked meters.",
        "Smart Meter Management: Meter inventory tracking, meter serial numbers, utility type classification (Electricity/Water/Gas), status flags, and customer assignments.",
        "Meter Reading & Consumption Calculation: Monthly meter reading logging, automatic delta consumption computation (currReading - prevReading).",
        "Tariff Rate & Automated Billing Engine: Tiered tariff calculations, invoice generation, due date enforcement, and billing status tracking (Paid/Unpaid/Overdue).",
        "Email & Notification Engine: Automated Nodemailer integration sending bill generation notices, urgent unpaid bill reminders, and resolution alerts.",
        "Online Payment Settlement: Recording customer payments with payment method tracking (bKash, Nagad, Bank), transaction IDs, and receipt downloads.",
        "Complaint & Support Ticket System: Customer submission of service issues (faulty meter, wrong billing, power outage) with admin assignment and status updates.",
        "Field Maintenance Dispatch: Scheduling emergency repair and maintenance jobs, assigning field technicians, and updating job status.",
        "GIS Spatial Outage & Meter Map: Interactive geographical map placing customer meters, transformer nodes, and color-coded fault markers.",
        "Reports & Financial Dashboard: Revenue graphs, utility breakdown analytics, billing summary cards, and PDF invoice printing."
    ]
    for pf in pf_items:
        p_pf = doc.add_paragraph(style='List Bullet')
        p_pf.paragraph_format.space_after = Pt(3)
        p_pf.add_run(pf)

    add_heading_2("2.3 User Classes and Characteristics")
    tbl_users = doc.add_table(rows=4, cols=3)
    tbl_users.autofit = False
    tbl_users.columns[0].width = Inches(1.8)
    tbl_users.columns[1].width = Inches(2.0)
    tbl_users.columns[2].width = Inches(2.7)
    users_data = [
        ("User Role", "Target Audience", "Key Responsibilities & Permissions"),
        ("System Administrator (admin)", "Utility Executive & System Manager", "Full access to customer records, meter management, billing generation, financial reports, GIS map overview, technician assignment, and system settings."),
        ("Utility Field Staff (employee)", "Field Engineers & Meter Readers", "Logs monthly meter readings, updates maintenance ticket statuses, resolves technical complaints, and inspects GIS meter locations."),
        ("Utility Customer (customer)", "Residential & Commercial Consumers", "Views current & historical utility bills, submits meter readings, pays bills online, tracks payment history, files complaints/maintenance requests, and updates profile.")
    ]
    for r_idx, u_row in enumerate(users_data):
        row_cells = tbl_users.rows[r_idx].cells
        for c_idx, val in enumerate(u_row):
            row_cells[c_idx].paragraphs[0].text = val
    set_table_styling(tbl_users)

    add_heading_2("2.4 Operating Environment")
    add_body_p("Server Environment: Node.js runtime (v18.0+), Express.js framework (port 5000), Nodemailer service.", "Server: ")
    add_body_p("Database Environment: MySQL Server (v8.0+), relational schema utilis_db.", "Database: ")
    add_body_p("Client Environment: Web browser execution (Chrome v100+, Firefox v100+, Edge, Safari), HTTP static server (port 8080).", "Client: ")
    add_body_p("Libraries & Extensions: FontAwesome icons, Chart.js analytics engine, Leaflet.js GIS spatial engine.", "Libraries: ")

    add_heading_2("2.5 Design and Implementation Constraints")
    add_body_p("Dual-Port Architecture: Backend API executes on http://localhost:5000 while static SPA assets serve on http://localhost:8080.")
    add_body_p("Relational Integrity: Foreign key constraints strictly enforced across 9 SQL tables (users, customers, meters, meter_readings, bills, payments, complaints, notifications, maintenance).")
    add_body_p("Calculated Metric Boundaries: Consumption cannot be negative (currReading >= prevReading). Tariff rates must reflect positive double-precision numbers.")

    add_heading_2("2.6 User Documentation")
    add_body_p("Complete installation and operational guides are documented in README.md within the root project directory.")

    add_heading_2("2.7 Assumptions and Dependencies")
    add_body_p("Users access the system via standard web browsers over HTTP/HTTPS connections.")
    add_body_p("MySQL database server is running locally or remotely with appropriate database user permissions.")
    add_body_p("SMTP email server credentials are provided in .env for email reminder dispatch.")

    # ==================== 3. SYSTEM FEATURES ====================
    add_heading_1("3. System Features (Functional Requirements)")

    modules_fr = [
        ("3.1 Module 1: User Authentication & Profile Management", [
            ("FR-01", "The system shall allow users to log in using a valid username/email and password."),
            ("FR-02", "The system shall maintain session state (sessionStorage) with role-based permissions (admin, employee, customer)."),
            ("FR-03", "The system shall allow new customers to self-register with full name, username, email, password, phone, address, and optional meter serial number."),
            ("FR-04", "The system shall allow logged-in customers to view and update their personal profile information."),
            ("FR-05", "The system shall provide a secure log-out capability that clears session state and redirects to the public landing portal.")
        ]),
        ("3.2 Module 2: Customer Account Management", [
            ("FR-06", "The system shall maintain a customer registry linking customer profile details to user authentication accounts."),
            ("FR-07", "The system shall allow administrators to view, add, update, and search customer records by name, email, or phone."),
            ("FR-08", "The system shall allow administrators to activate or deactivate customer accounts."),
            ("FR-09", "The system shall allow administrators to link or re-assign utility meter units to specific customer accounts.")
        ]),
        ("3.3 Module 3: Smart Meter & Reading Tracking", [
            ("FR-10", "The system shall maintain a master meter inventory recording meter ID, meter serial number, utility type (Electricity, Water, Gas), status, and installation date."),
            ("FR-11", "The system shall allow administrators and field staff to register new utility meters into the system."),
            ("FR-12", "The system shall record monthly meter readings containing meter ID, billing month, and units consumed."),
            ("FR-13", "The system shall display meter status indicators (active, faulty, inactive)."),
            ("FR-14", "The system shall allow filtering meter records by utility category (Electricity, Water, Gas) and assignment status.")
        ]),
        ("3.4 Module 4: Consumption Billing & Tariff Calculation", [
            ("FR-15", "The system shall generate monthly utility bills for customers based on meter consumption data."),
            ("FR-16", "The system shall automatically compute utility consumption delta: consumption = currReading - prevReading."),
            ("FR-17", "The system shall calculate billing amounts by multiplying unit consumption by applicable utility tariff rates (amount = consumption * tariffRate)."),
            ("FR-18", "The system shall enforce due dates, billing months, and billing years for every generated invoice record."),
            ("FR-19", "The system shall allow administrators to manually trigger single or batch bill generation."),
            ("FR-20", "The system shall mark bill statuses dynamically as unpaid, paid, or overdue.")
        ]),
        ("3.5 Module 5: Automated Email Notification & Reminder System", [
            ("FR-21", "The system shall automatically dispatch an email notification to the customer upon bill generation."),
            ("FR-22", "The system shall provide an administrative feature to trigger urgent email reminders (/api/send-bill-reminder) for unpaid utility bills."),
            ("FR-23", "The system shall render HTML-formatted email reminder templates containing invoice ID, utility type, due date, and amount due."),
            ("FR-24", "The system shall store in-app user notifications in the database with unread/read state tracking.")
        ]),
        ("3.6 Module 6: Payment Processing & Financial Accounting", [
            ("FR-25", "The system shall allow customers to submit bill payments choosing digital channels (bKash, Nagad, Rocket, Bank Transfer, Credit Card)."),
            ("FR-26", "The system shall validate payment inputs and record unique transaction reference IDs (transactionId)."),
            ("FR-27", "The system shall automatically update bill status from unpaid to paid upon successful payment verification."),
            ("FR-28", "The system shall generate printable digital payment receipts for completed utility transactions.")
        ]),
        ("3.7 Module 7: Complaint Management & Support Ticketing", [
            ("FR-29", "The system shall allow customers to submit support complaints selecting subject, description, and utility category."),
            ("FR-30", "The system shall track complaint status through a defined workflow pipeline (Pending, In Progress, Resolved)."),
            ("FR-31", "The system shall allow administrators and employees to assign complaints to technical staff members."),
            ("FR-32", "The system shall support interactive JSON comment threads attached to each complaint ticket for communication between customers and staff.")
        ]),
        ("3.8 Module 8: Field Maintenance & Technical Operations", [
            ("FR-33", "The system shall allow customers and staff to lodge maintenance requests (e.g., Meter Inspection, Leak Repair, Line Maintenance)."),
            ("FR-34", "The system shall record maintenance request type, description, customer link, assigned technician, and creation timestamp."),
            ("FR-35", "The system shall allow field staff to update maintenance task progress and log resolution notes."),
            ("FR-36", "The system shall display active maintenance request metrics on administrative dashboards.")
        ]),
        ("3.9 Module 9: Geographic Information System (GIS) & Spatial Mapping", [
            ("FR-37", "The system shall integrate Leaflet GIS interactive map visualization displaying spatial distribution of customer meters."),
            ("FR-38", "The system shall plot custom map markers indicating customer locations, meter health status, and utility types."),
            ("FR-39", "The system shall highlight active utility fault areas and substation coverage zones on the GIS map canvas.")
        ]),
        ("3.10 Module 10: Reports & Executive Analytics Engine", [
            ("FR-40", "The system shall render analytical summary charts (Chart.js) illustrating monthly consumption trends and revenue collection figures."),
            ("FR-41", "The system shall generate summary statistics for total registered customers, active meters, total billed revenue, and unpaid balances."),
            ("FR-42", "The system shall allow exporting billing summaries and customer ledgers to printable format / PDF.")
        ])
    ]

    for m_title, fr_list in modules_fr:
        add_heading_2(m_title)
        tbl_fr = doc.add_table(rows=len(fr_list)+1, cols=2)
        tbl_fr.autofit = False
        tbl_fr.columns[0].width = Inches(1.2)
        tbl_fr.columns[1].width = Inches(5.3)

        tbl_fr.rows[0].cells[0].paragraphs[0].text = "ID"
        tbl_fr.rows[0].cells[1].paragraphs[0].text = "Requirement Statement"

        for idx, (fr_id, fr_stmt) in enumerate(fr_list, 1):
            tbl_fr.rows[idx].cells[0].paragraphs[0].text = fr_id
            tbl_fr.rows[idx].cells[1].paragraphs[0].text = fr_stmt
        set_table_styling(tbl_fr)

    # ==================== 4. EXTERNAL INTERFACE REQUIREMENTS ====================
    add_heading_1("4. External Interface Requirements")
    add_heading_2("4.1 User Interfaces")
    add_body_p("The user interface is constructed as a modern, responsive Single Page Application (SPA) utilizing HTML5, CSS3, and JavaScript ES6 modules. Key UI design highlights:")
    ui_highlights = [
        "Navigation Sidebar: Role-specific dynamic navigation rendering appropriate workspace menus.",
        "KPI Summary Cards: Overview counters displaying total customers, active meters, revenue, and open tickets.",
        "Data Tables: Interactive grids featuring real-time filtering, search inputs, pagination, and action buttons.",
        "Modal Dialogs: Styled overlays for customer registration, meter addition, bill generation, payment processing, and complaint creation.",
        "GIS Canvas: Embedded interactive map container supporting zoom, tile layering, and popup tooltips."
    ]
    for ui_h in ui_highlights:
        p_ui = doc.add_paragraph(style='List Bullet')
        p_ui.paragraph_format.space_after = Pt(3)
        p_ui.add_run(ui_h)

    add_heading_2("4.2 Hardware Interfaces")
    add_body_p("Server Hardware: x86-64 server or virtual machine (Minimum: 2 Core CPU, 4 GB RAM, 20 GB Storage).")
    add_body_p("Client Hardware: Desktop computers, laptops, tablets, or mobile smartphones with standard screen resolution (1024x768 and above recommended).")

    add_heading_2("4.3 Software Interfaces")
    add_body_p("Operating System: Windows 10/11, Linux (Ubuntu 20.04+), or macOS.")
    add_body_p("Node.js Environment: Version 18.0.0 or higher.")
    add_body_p("Database Engine: MySQL Server 8.0+ running engine InnoDB with UTF-8 character encoding.")
    add_body_p("Web Server: Express.js HTTP framework and static web server.")

    add_heading_2("4.4 Communication Interfaces")
    add_body_p("Protocol: HTTP/1.1 or HTTPS for API and static resource delivery.")
    add_body_p("API Architecture: RESTful API endpoints exchanging JSON data payloads (Content-Type: application/json).")
    add_body_p("CORS Configuration: Cross-Origin Resource Sharing enabled on backend port 5000 to accept requests from frontend origin port 8080.")
    add_body_p("Email Protocol: SMTP (Simple Mail Transfer Protocol) for outbound email reminder dispatch via Nodemailer.")

    # ==================== 5. NON-FUNCTIONAL REQUIREMENTS ====================
    add_heading_1("5. Non-Functional Requirements")
    tbl_nfr = doc.add_table(rows=6, cols=3)
    tbl_nfr.autofit = False
    tbl_nfr.columns[0].width = Inches(1.2)
    tbl_nfr.columns[1].width = Inches(1.8)
    tbl_nfr.columns[2].width = Inches(3.5)

    nfr_data = [
        ("ID", "Category", "Specification"),
        ("NFR-01", "Performance", "API response time shall remain under 1.5 seconds for database queries and under 3.0 seconds for email dispatches."),
        ("NFR-02", "Security", "User passwords shall be stored securely. Session state must be bounded by browser session boundaries with role validation on API routes."),
        ("NFR-03", "Reliability", "The database layer shall use InnoDB foreign keys with cascading delete/update constraints to maintain data integrity with 99.9% consistency."),
        ("NFR-04", "Usability", "The UI shall provide clear visual status badges, actionable confirmation prompts, and immediate toast feedback for user actions."),
        ("NFR-05", "Portability", "The web interface shall execute across modern standard web browsers (Google Chrome, Mozilla Firefox, Microsoft Edge, Safari) without plugin requirements.")
    ]
    for r_idx, n_row in enumerate(nfr_data):
        row_cells = tbl_nfr.rows[r_idx].cells
        for c_idx, val in enumerate(n_row):
            row_cells[c_idx].paragraphs[0].text = val
    set_table_styling(tbl_nfr)

    # ==================== 6. OTHER REQUIREMENTS ====================
    add_heading_1("6. Other Requirements")
    add_heading_2("6.1 Regulatory Compliance & Tariff Policies")
    add_body_p("The system enforces standard utility tariff structures approved by national utility regulatory commissions. Tariff rates are applied uniformly per unit based on utility type (Electricity per kWh, Water per Litre/Unit, Gas per Unit/Cubic Meter).")

    add_heading_2("6.2 Data Privacy & Billing Audit Trail")
    add_body_p("All financial transactions, payments, and bill updates are timestamped and linked to specific customer and invoice IDs, establishing an immutable audit trail for accounting and auditing purposes.")

    # ==================== 7. APPENDICES ====================
    add_heading_1("7. Appendices")
    add_heading_2("7.1 Appendix A: Data Flow Diagram (DFD Level 1)")
    dfd_steps = [
        "Customer → [Login / Registration] → User Authentication Process → [Store Session] → users & customers DB",
        "Field Staff / Employee → [Meter Reading Data] → Reading Log Process → [Store Consumption Delta] → meter_readings DB",
        "Billing Engine → [Fetch Readings & Tariff] → Billing Generation Process → [Compute Amount] → bills DB → [Send Email] → Customer",
        "Customer → [Payment Details & Transaction ID] → Payment Gateway Process → [Verify & Update Status] → payments & bills DB",
        "Customer → [Complaint / Maintenance Request] → Support Ticket Process → [Assign Staff & Log Status] → complaints & maintenance DB",
        "Administrator → [Request GIS & Analytics] → Reporting Engine → [Aggregate Metrics & Map Data] → gis & reports Dashboard"
    ]
    for idx, dfd in enumerate(dfd_steps, 1):
        p_dfd = doc.add_paragraph()
        p_dfd.paragraph_format.space_after = Pt(4)
        p_dfd.add_run(f"{idx}. ").bold = True
        p_dfd.add_run(dfd)

    # CLEAN 7.2 TABLE ONLY (DIAGRAMS REMOVED AS REQUESTED)
    add_heading_2("7.2 Appendix B: Entity Relationship Diagram (ERD) & Database Schema")
    tbl_erd = doc.add_table(rows=10, cols=3)
    tbl_erd.autofit = False
    tbl_erd.columns[0].width = Inches(1.5)
    tbl_erd.columns[1].width = Inches(3.0)
    tbl_erd.columns[2].width = Inches(2.0)

    erd_data = [
        ("Database Table", "Attributes & Keys", "Description"),
        ("users", "id (PK), name, username (UQ), email, password, role, status", "Stores authentication credentials and user role (admin, employee, customer)."),
        ("customers", "customer_id (PK), user_id (FK -> users.id), phone, address", "Stores customer profile details linked to a user login account."),
        ("meters", "meter_id (PK), customer_id (FK -> customers.customer_id), meter_number (UQ), utilityType, status, installDate", "Stores utility meter records (Electricity, Water, Gas) and customer ownership."),
        ("meter_readings", "reading_id (PK), meter_id (FK -> meters.meter_id), month, unit_consumed", "Tracks monthly consumption units logged per meter."),
        ("bills", "bill_id (PK), customer_id (FK -> customers.customer_id), amount, due_date, status, billingMonth, billingYear, meterId (FK -> meters.meter_id), prevReading, currReading, consumption, tariffRate, createdAt, paymentDate", "Stores calculated utility bills, reading deltas, tariff rates, due dates, and statuses."),
        ("payments", "payment_id (PK), bill_id (FK -> bills.bill_id), amount, payment_date, method, transactionId, status", "Records payment transactions, methods (bKash, Nagad, Bank), and transaction IDs."),
        ("complaints", "complaint_id (PK), customer_id (FK -> customers.customer_id), subject, description, status, assignedTo, createdAt, comments (JSON)", "Manages customer support tickets, status pipeline, assigned staff, and comment logs."),
        ("notifications", "id (PK), userId (FK -> users.id), message, type, date, isRead", "Stores system notifications and unread/read indicators for users."),
        ("maintenance", "maintenance_id (PK), customer_id (FK -> customers.customer_id), request_type, description, status, assigned_to, createdAt, comments (JSON)", "Manages technical field maintenance requests, assigned technicians, and status tracking.")
    ]
    for r_idx, e_row in enumerate(erd_data):
        row_cells = tbl_erd.rows[r_idx].cells
        for c_idx, val in enumerate(e_row):
            row_cells[c_idx].paragraphs[0].text = val
    set_table_styling(tbl_erd)

    # Save DOCX
    doc.save(output_docx_path)
    print(f"Printable DOCX generated at: {output_docx_path}")

def convert_docx_to_pdf(docx_path, pdf_path):
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    doc = word.Documents.Open(os.path.abspath(docx_path))
    # 17 represents wdFormatPDF
    doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)
    doc.Close()
    word.Quit()
    print(f"PDF generated successfully at: {pdf_path}")

if __name__ == "__main__":
    base_dir = r"d:\utility Management system"
    docx_file = os.path.join(base_dir, "SRS_Printable_Utility.docx")
    pdf_file = os.path.join(base_dir, "SRS_Printable_Utility.pdf")

    # Build DOCX
    build_printable_srs_docx(docx_file)
    
    # Also save as SRS_Document_Utility.docx
    docx_alt = os.path.join(base_dir, "SRS_Document_Utility.docx")
    shutil.copy2(docx_file, docx_alt)

    # Convert to PDF
    convert_docx_to_pdf(docx_file, pdf_file)
    
    # Copy PDF to SRS_Document_Utility.pdf
    pdf_alt = os.path.join(base_dir, "SRS_Document_Utility.pdf")
    shutil.copy2(pdf_file, pdf_alt)

    # Copy to User's Downloads folder
    downloads_dir = r"C:\Users\Jasika\Downloads"
    if os.path.exists(downloads_dir):
        shutil.copy2(pdf_file, os.path.join(downloads_dir, "SRS_Printable_Utility.pdf"))
        shutil.copy2(pdf_file, os.path.join(downloads_dir, "SRS_Document_Utility.pdf"))
        shutil.copy2(docx_file, os.path.join(downloads_dir, "SRS_Printable_Utility.docx"))
        shutil.copy2(docx_file, os.path.join(downloads_dir, "SRS_Document_Utility.docx"))
        print("Successfully copied updated PDF and DOCX files to Downloads folder!")
