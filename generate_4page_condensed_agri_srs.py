import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import os
import shutil
from docx2pdf import convert

def build_print_perfect_agri_srs(output_docx_path):
    doc = docx.Document()

    # 0.65 in margins for executive print balance
    for section in doc.sections:
        section.top_margin = Inches(0.65)
        section.bottom_margin = Inches(0.65)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    COLOR_TITLE = RGBColor(15, 23, 42)     # Deep Slate #0F172A
    COLOR_HEADING = RGBColor(30, 41, 59)   # Slate Blue #1E293B
    COLOR_BODY = RGBColor(15, 23, 42)      # Sharp Dark Text

    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(9.5)
    style_normal.font.color.rgb = COLOR_BODY

    def add_p(text="", bold=False, italic=False, size=9.5, space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.LEFT):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.08
        if text:
            run = p.add_run(text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.italic = italic
            run.font.color.rgb = COLOR_BODY
        return p

    def add_h1(text, space_before=6, space_after=2.5):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = COLOR_HEADING
        return p

    def add_h2(text, space_before=4, space_after=1.5):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.color.rgb = COLOR_HEADING
        return p

    def add_bullet(text, bold_prefix="", space_before=0, space_after=1.5):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.08
        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.font.name = 'Times New Roman'
            run_b.font.size = Pt(9.5)
            run_b.font.bold = True
            run_b.font.color.rgb = COLOR_BODY
        run_t = p.add_run(text)
        run_t.font.name = 'Times New Roman'
        run_t.font.size = Pt(9.5)
        run_t.font.color.rgb = COLOR_BODY
        return p

    def set_cell_background(cell, hex_color):
        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading_elm)

    def set_cell_border(cell, **kwargs):
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = tcPr.first_child_found_in("w:tcBorders")
        if tcBorders is None:
            tcBorders = OxmlElement('w:tcBorders')
            tcPr.append(tcBorders)
        for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
            edge_data = kwargs.get(edge)
            if edge_data:
                tag = f'w:{edge}'
                element = tcBorders.find(qn(tag))
                if element is None:
                    element = OxmlElement(tag)
                    tcBorders.append(element)
                for key in ["sz", "val", "color", "space"]:
                    if key in edge_data:
                        element.set(qn(f'w:{key}'), str(edge_data[key]))

    def style_table(table, col_widths, font_size=8.5):
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        for row_idx, row in enumerate(table.rows):
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

            is_header = (row_idx == 0)
            if is_header:
                trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

            for col_idx, cell in enumerate(row.cells):
                cell.width = Inches(col_widths[col_idx])
                if is_header:
                    set_cell_background(cell, "F1F5F9")  # Elegant slate gray header background for print
                else:
                    if row_idx % 2 == 1:
                        set_cell_background(cell, "FAFAFA") # Subtle zebra row

                set_cell_border(cell,
                                top={"sz": 4, "val": "single", "color": "475569"},
                                bottom={"sz": 4, "val": "single", "color": "475569"},
                                left={"sz": 4, "val": "single", "color": "475569"},
                                right={"sz": 4, "val": "single", "color": "475569"})

                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.05
                    for run in p.runs:
                        run.font.name = 'Times New Roman'
                        run.font.size = Pt(font_size)
                        if is_header:
                            run.font.bold = True
                            run.font.color.rgb = COLOR_TITLE
                        else:
                            run.font.color.rgb = COLOR_BODY

    # ================= PAGE 1 =================
    add_p("Software Requirements Specification (SRS)", bold=True, size=11.5, space_after=2)
    add_p("BazarDor – Digital Agricultural Supply Chain System", bold=True, size=12.5, space_after=6)

    add_p("Student Name: Alif Rudaba Ronja", size=9.5, space_after=1.5)
    add_p("Student ID: 22CSE037", size=9.5, space_after=1.5)
    add_p("Session: 2022-2023", size=9.5, space_after=1.5)
    add_p("Course Code: CSE356 | Course Title: Software Engineering Sessional", size=9.5, space_after=1.5)
    add_p("Department of Computer Science and Engineering, GSTU", size=9.5, space_after=1.5)
    add_p("Submitted To: Dr. Mrinal Kanti Baowaly (Professor, Dept. of CSE)", italic=True, size=9.5, space_after=7)

    add_h1("1. Introduction")

    add_h2("1.1 Purpose")
    add_p("This Software Requirements Specification (SRS) defines functional and non-functional requirements, system architecture, user roles, interface specifications, and database models for the BazarDor Digital Agricultural Supply Chain System.", space_after=3.5)

    add_h2("1.2 Scope")
    add_p("BazarDor digitizes agricultural supply chains, eliminating middlemen, regulating daily district crop rates, and facilitating direct farm sales. Core capabilities include:", space_after=2)
    add_bullet(" Multi-role access control (`farmer`, `buyer`, `consumer`, `supervisor`).", bold_prefix="Authentication & Roles:")
    add_bullet(" Farm registration, acreage logging, and crop verification.", bold_prefix="Farm Management:")
    add_bullet(" District daily price regulation & immutable audit logs.", bold_prefix="Price Regulation:")
    add_bullet(" Farmer harvest posts, direct buyer procurement, and buy request feed.", bold_prefix="Direct Trading:")
    add_bullet(" Consumer storefront, market analytics, and Recharts forecasting.", bold_prefix="Storefront & Analytics:", space_after=3.5)

    add_h2("1.3 Definitions, Acronyms, and Abbreviations")
    t1 = doc.add_table(rows=6, cols=2)
    headers = ["Term", "Definition & Context"]
    t1_data = [
        ["SRS", "Software Requirements Specification"],
        ["BazarDor", "Digital Agricultural Supply Chain System"],
        ["UI / SPA", "User Interface / Single Page Application (React 18 + Vite)"],
        ["Prisma ORM", "Next-gen Object-Relational Mapper for MySQL Database"],
        ["REST / JWT", "Representational State Transfer API / JSON Web Token Auth"]
    ]
    for c_idx, h in enumerate(headers):
        p = t1.rows[0].cells[c_idx].paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
    for r_idx, row_data in enumerate(t1_data):
        for c_idx, val in enumerate(row_data):
            p = t1.rows[r_idx+1].cells[c_idx].paragraphs[0]
            p.add_run(val)
    style_table(t1, [1.5, 5.5], font_size=8.5)

    add_h2("1.4 References")
    add_bullet("IEEE Std 830-1998 & IEEE Std 29148-2018 SRS Standards.")
    add_bullet("Prisma ORM, React 18, Vite, and Express.js Documentation.", space_after=3.5)

    add_h2("1.5 Overview")
    add_p("Document organized into 7 core sections: System Overview, Product Functions, Requirements (FR-01 to FR-41), Interfaces, NFRs, Policies, and DFD/ERD Appendices.", space_after=3.5)

    add_h1("2. Overall Description")
    add_h2("2.1 Product Perspective")
    add_p("BazarDor is a full-stack web platform connecting farmers, buyers, consumers, and regulators over a central MySQL database (`bazardoor_db`) via Node.js REST API.", space_after=3.5)

    add_h2("2.2 Product Functions")
    add_bullet("Role-based login, signup, and district assignment.")
    add_bullet("Farm registration, field logging, and verification status.")
    add_bullet("District market price cap regulation (wholesale & retail).")
    add_bullet("Farmer harvest sale postings with quantity, unit rate, and photos.")
    add_bullet("Direct wholesale orders and buyer sourcing request feed.")
    add_bullet("Consumer retail storefront with official district price caps.")
    add_bullet("Crop catalog addition request and supervisor approval workflow.")
    add_bullet("Recharts historical price trends and market audit logging.", space_after=4)

    # PAGE BREAK TO PAGE 2
    doc.add_page_break()

    # ================= PAGE 2 =================
    add_h2("2.3 User Classes and Characteristics")
    t2 = doc.add_table(rows=5, cols=2)
    t2_headers = ["User Role", "Responsibilities & System Permissions"]
    t2_data = [
        ["Agro Farmer (farmer)", "Registers farms/fields, posts harvest sales, responds to buyer sourcing requests, tracks order fulfillment."],
        ["Wholesale Buyer (buyer)", "Browses verified farm listings, buys directly without middlemen, posts crop sourcing requests, manages inventory."],
        ["General Consumer (consumer)", "Browses verified retail catalog, tracks market price trends, orders online at official district rates."],
        ["Market Supervisor (supervisor)", "Manages master crop catalog, approves product requests, sets daily wholesale/retail price caps, reviews audit logs."]
    ]
    for c_idx, h in enumerate(t2_headers):
        p = t2.rows[0].cells[c_idx].paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
    for r_idx, row_data in enumerate(t2_data):
        for c_idx, val in enumerate(row_data):
            p = t2.rows[r_idx+1].cells[c_idx].paragraphs[0]
            p.add_run(val)
    style_table(t2, [1.8, 5.2], font_size=8.5)

    add_h2("2.4 Operating Environment")
    add_bullet(" Node.js v18+, Express.js framework, port 5000.", bold_prefix="Server:")
    add_bullet(" MySQL Server v8.0+, managed via Prisma ORM.", bold_prefix="Database:")
    add_bullet(" React 18, Vite (port 5173), Tailwind CSS, Recharts.", bold_prefix="Frontend:", space_after=3.5)

    add_h2("2.5 Design and Implementation Constraints")
    add_bullet("Dual-port monorepo execution: Express API port 5000 and Vite dev port 5173.")
    add_bullet("District price cap integrity: Selling prices validated against supervisor rate caps.")
    add_bullet("Strict relational integrity enforced via Prisma schema across 17 models.", space_after=3.5)

    add_h2("2.6 User Documentation")
    add_bullet("Operational setup guides provided in root `User_Manual.md` and `readme.txt`.", space_after=3.5)

    add_h2("2.7 Assumptions and Dependencies")
    add_bullet("Users have internet access; MySQL DB `bazardoor_db` and seed district datasets exist.", space_after=4.5)

    add_h1("3. System Features (Functional Requirements)")

    add_h2("3.1 Module 1: User Authentication & Role Management")
    add_bullet("FR-01: Registration with name, phone, password, role, and district ID.")
    add_bullet("FR-02: Authenticate via bcrypt passwords & return role-based JWT session tokens.")
    add_bullet("FR-03: Role-based access control (RBAC) on protected pages.")
    add_bullet("FR-04: Profile view & update capability; FR-05: Secure session logout.", space_after=2.5)

    add_h2("3.2 Module 2: Farm & Field Management (Agro Farmers)")
    add_bullet("FR-06: Farm registration with location, district, size, and photo.")
    add_bullet("FR-07: Verification badge status (`is_verified`); FR-08: Update farm size capacity.")
    add_bullet("FR-09: Link farm profile to district price limits; FR-10: Delete/archive farm records.", space_after=2.5)

    add_h2("3.3 Module 3: Master Crop Catalog & Request Management")
    add_bullet("FR-11: Maintain master crop catalog (name, unit, category, description, image).")
    add_bullet("FR-12: Farmers/buyers submit product requests for unlisted crop varieties.")
    add_bullet("FR-13: Supervisor review/approval workflow; FR-14: Auto-insert approved crops.")
    add_bullet("FR-15: Notify requesting user upon supervisor decision.", space_after=2.5)

    add_h2("3.4 Module 4: Daily Price Regulation & Auditing (Supervisors)")
    add_bullet("FR-16: Supervisors set daily wholesale & retail price caps per district.")
    add_bullet("FR-17: Log price changes into `price_audit_logs`; FR-18: Maintain historical price records.")
    add_bullet("FR-19: Display price bounds (`min_price`, `max_price`); FR-20: Calculate district supply metrics.", space_after=2.5)

    add_h2("3.5 Module 5: Farmer Harvest Sale Posting & Direct Sourcing")
    add_bullet("FR-21: Post harvest lots specifying crop, qty, unit rate, and harvest date.")
    add_bullet("FR-22: Display active posts in marketplace; FR-23: Track view & purchase counts.")
    add_bullet("FR-24: Direct wholesale order placement; FR-25: Auto-deduct ordered stock.", space_after=4.5)

    # PAGE BREAK TO PAGE 3
    doc.add_page_break()

    # ================= PAGE 3 =================
    add_h2("3.6 Module 6: Buyer Sourcing Requests (Buy Requests Feed)")
    add_bullet("FR-26: Buyers publish sourcing demand requests (`buyer_buy_requests`).")
    add_bullet("FR-27: Capture required crop, target qty, price, and district notes.")
    add_bullet("FR-28: Dedicated Buyer Requests Feed for farmers; FR-29: Request status tracking.")
    add_bullet("FR-30: Filter buy requests by district and crop category.", space_after=2.5)

    add_h2("3.7 Module 7: Consumer Storefront & Retail Purchasing")
    add_bullet("FR-31: Consumer storefront displaying crops at official district price rates.")
    add_bullet("FR-32: Cart & retail checkout (`consumer_orders`); FR-33: Link to buyer inventory.")
    add_bullet("FR-34: Order history (`ConsumerBuyingRecords`); FR-35: Generate digital invoices.", space_after=2.5)

    add_h2("3.8 Module 8: Market Analytics & Price Forecasting")
    add_bullet("FR-36: Recharts trend line charts for historical price visualization.")
    add_bullet("FR-37: Regional district rate comparison; FR-38: Price warning alerts in Forecast Hub.")
    add_bullet("FR-39: Track search terms (`search_analytics`) for emerging crop demand trends.", space_after=2.5)

    add_h2("3.9 Module 9: System Notifications & Audit Logging")
    add_bullet("FR-40: Auto-generate notifications for order updates and product approvals.")
    add_bullet("FR-41: Maintain immutable audit logs for regulatory price compliance.", space_after=4.5)

    add_h1("4. External Interface Requirements")
    add_h2("4.1 User Interfaces")
    add_p("Web UI built with React 18, Vite, Tailwind CSS, and Lucide React icons:", space_after=2)
    add_bullet("Role-specific sidebars for farmer, buyer, consumer, and supervisor control panels.")
    add_bullet("Market overview cards showing total farms, active posts, orders, and price averages.")
    add_bullet("Recharts graphical trend charts; Responsive grid & flexbox layouts.", space_after=3.5)

    add_h2("4.2 Hardware Interfaces")
    add_bullet(" Server: Standard x86/ARM instance (2 Core CPU, 4GB RAM, 10GB SSD).", bold_prefix="Server:")
    add_bullet(" Client: PC, laptop, tablet, or smartphone.", bold_prefix="Client:", space_after=3.5)

    add_h2("4.3 Software Interfaces")
    add_bullet("OS: Windows 10/11, Linux Ubuntu 20.04+, or macOS.")
    add_bullet("Runtime: Node.js v18+, Express.js API; DB: MySQL 8.0+ managed via Prisma ORM.", space_after=3.5)

    add_h2("4.4 Communication Interfaces")
    add_bullet("HTTP/HTTPS REST API exchange (`application/json`) port 5000; CORS enabled for Vite port 5173.", space_after=4.5)

    add_h1("5. Non-Functional Requirements")
    t_nfr = doc.add_table(rows=6, cols=3)
    t_nfr_headers = ["ID", "Category", "Specification & Quality Benchmark"]
    t_nfr_data = [
        ["NFR-01", "Performance", "API response time < 2.0s for standard queries; < 3.0s under peak loads."],
        ["NFR-02", "Security", "Passwords encrypted using bcrypt (salt rounds 10); JWT bearer auth headers."],
        ["NFR-03", "Reliability", "Achieve 99.5% uptime during peak harvest and market trading hours."],
        ["NFR-04", "Usability", "Self-explanatory UI with intuitive navigation, status badges, and toast alerts."],
        ["NFR-05", "Portability", "Cross-browser functionality across Chrome, Edge, Firefox, and Safari."]
    ]
    for c_idx, h in enumerate(t_nfr_headers):
        p = t_nfr.rows[0].cells[c_idx].paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
    for r_idx, row_data in enumerate(t_nfr_data):
        for c_idx, val in enumerate(row_data):
            p = t_nfr.rows[r_idx+1].cells[c_idx].paragraphs[0]
            p.add_run(val)
    style_table(t_nfr, [0.8, 1.2, 5.0], font_size=8.5)

    # PAGE BREAK TO PAGE 4
    doc.add_page_break()

    # ================= PAGE 4 =================
    add_h1("6. Other Requirements")
    add_h2("6.1 Regulatory Compliance & Price Regulation")
    add_p("The system enforces government district price regulations by requiring supervisors to set daily price bounds, preventing artificial inflation by intermediaries.", space_after=3.5)

    add_h2("6.2 Data Privacy & Regulatory Audit Trail")
    add_p("Every price change is immutable and recorded in `price_audit_logs` with supervisor identification, ensuring complete transparency for government agricultural audits.", space_after=4.5)

    add_h1("7. Appendices")
    add_h2("7.1 Appendix A: Data Flow Diagram (DFD Level 1)")
    add_bullet("Farmer → [Farm Info & Sale Posts] → Farm Management Process → `farms` & `farmer_sale_posts` DB.")
    add_bullet("Buyer → [Order Request] → Procurement Process → `crops` & `district_prices` DB.")
    add_bullet("Procurement Process → [Deduct Stock & Create Invoice] → `farmer_orders` DB → Farmer.")
    add_bullet("Supervisor → [Daily Price Update] → Price Regulation → `district_prices` & `price_audit_logs` DB.")
    add_bullet("Consumer → [Retail Purchase] → Storefront Process → `consumer_orders` & `buyer_inventory` DB.", space_after=4.5)

    add_h2("7.2 Appendix B: Entity Relationship Diagram (ERD) & Database Schema")
    add_p("The `bazardoor_db` relational database comprises 17 core Prisma schema models structured as follows:", space_after=3.5)

    t_erd = doc.add_table(rows=11, cols=2)
    t_erd_headers = ["Prisma Model", "Attributes, Keys & Functional Purpose"]
    t_erd_data = [
        ["users", "user_id (PK), full_name, role (farmer/buyer/consumer/supervisor), phone (UQ), password, district_id (FK)."],
        ["farms", "farm_id (PK), farmer_id (FK), farm_name, location, district_id (FK), is_verified, farm_size, contact_info."],
        ["crops", "crop_id (PK), crop_name, unit, available_qty, current_price, image_url, category, description."],
        ["district_prices", "price_id (PK), district_id (FK), crop_id (FK), price_date, wholesale_price, consumer_price, supervisor_id."],
        ["price_audit_logs", "audit_id (PK), district_id (FK), crop_id (FK), wholesale_price, consumer_price, supervisor_id, updated_at."],
        ["farmer_sale_posts", "post_id (PK), farm_id (FK), crop_id (FK), available_qty, selling_price, harvest_date, status, views_count."],
        ["farmer_orders", "order_id (PK), buyer_id (FK), farm_id (FK), order_date, total_amount, status, farmer_order_items."],
        ["buyer_buy_requests", "request_id (PK), buyer_id (FK), crop_id (FK), quantity, target_price, district_id (FK), notes, status."],
        ["consumer_orders", "order_id (PK), consumer_id (FK), buyer_id (FK), order_date, total_amount, status, order_items."],
        ["product_requests", "request_id (PK), requester_id (FK), crop_name, unit, category, status, rejection_reason, approvals."]
    ]
    for c_idx, h in enumerate(t_erd_headers):
        p = t_erd.rows[0].cells[c_idx].paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
    for r_idx, row_data in enumerate(t_erd_data):
        for c_idx, val in enumerate(row_data):
            p = t_erd.rows[r_idx+1].cells[c_idx].paragraphs[0]
            p.add_run(val)
    style_table(t_erd, [1.6, 5.4], font_size=8)

    doc.save(output_docx_path)
    print(f"Docx generated at: {output_docx_path}")

if __name__ == "__main__":
    docx_path = r"C:\Users\Jasika\Desktop\agri(2)\agri\SRS_Document_agri_4Page.docx"
    workspace_pdf = r"C:\Users\Jasika\Desktop\agri(2)\agri\SRS_Document_agri_4Page.pdf"

    build_print_perfect_agri_srs(docx_path)
    
    convert(docx_path, workspace_pdf)
    print(f"Workspace PDF generated at: {workspace_pdf}")
    
    downloads_pdf = r"C:\Users\Jasika\Downloads\srs_agri.pdf"
    downloads_pdf2 = r"C:\Users\Jasika\Downloads\SRS_Document_agri.pdf"
    downloads_pdf3 = r"C:\Users\Jasika\Downloads\SRS_Printable_agri.pdf"
    agri_pdf_orig = r"C:\Users\Jasika\Desktop\agri(2)\agri\SRS_Document_agri.pdf"
    agri_pdf_printable = r"C:\Users\Jasika\Desktop\agri(2)\agri\SRS_Printable_agri.pdf"

    for p in [downloads_pdf, downloads_pdf2, downloads_pdf3, agri_pdf_orig, agri_pdf_printable]:
        shutil.copy(workspace_pdf, p)
        print(f"Copied to: {p}")
