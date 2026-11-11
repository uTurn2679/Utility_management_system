import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import os
import shutil
from docx2pdf import convert

def build_print_large_text_utility_srs(output_docx_path):
    doc = docx.Document()

    # 0.55 in margins for larger readable font layout
    for section in doc.sections:
        section.top_margin = Inches(0.55)
        section.bottom_margin = Inches(0.55)
        section.left_margin = Inches(0.65)
        section.right_margin = Inches(0.65)

    COLOR_TITLE = RGBColor(15, 23, 42)     # Deep Slate #0F172A
    COLOR_HEADING = RGBColor(30, 41, 59)   # Slate Blue #1E293B
    COLOR_BODY = RGBColor(15, 23, 42)      # Sharp Dark Text

    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(10)
    style_normal.font.color.rgb = COLOR_BODY

    def add_p(text="", bold=False, italic=False, size=10, space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.LEFT):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.05
        if text:
            run = p.add_run(text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.italic = italic
            run.font.color.rgb = COLOR_BODY
        return p

    def add_h1(text, space_before=5, space_after=2):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = COLOR_HEADING
        return p

    def add_h2(text, space_before=3.5, space_after=1.5):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_HEADING
        return p

    def add_bullet(text, bold_prefix="", space_before=0, space_after=1.5):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.05
        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.font.name = 'Times New Roman'
            run_b.font.size = Pt(10)
            run_b.font.bold = True
            run_b.font.color.rgb = COLOR_BODY
        run_t = p.add_run(text)
        run_t.font.name = 'Times New Roman'
        run_t.font.size = Pt(10)
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

    def style_table(table, col_widths, font_size=9):
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
                    set_cell_background(cell, "F1F5F9")  # Slate Gray header
                else:
                    if row_idx % 2 == 1:
                        set_cell_background(cell, "FAFAFA") # Zebra row

                set_cell_border(cell,
                                top={"sz": 4, "val": "single", "color": "475569"},
                                bottom={"sz": 4, "val": "single", "color": "475569"},
                                left={"sz": 4, "val": "single", "color": "475569"},
                                right={"sz": 4, "val": "single", "color": "475569"})

                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(1.5)
                    p.paragraph_format.space_after = Pt(1.5)
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
    add_p("Software Requirements Specification (SRS)", bold=True, size=12, space_after=2)
    add_p("Utility Management System", bold=True, size=13.5, space_after=5)

    add_p("Student Name: Jasika Noor", size=10, space_after=1)
    add_p("Student ID: 22CSE002", size=10, space_after=1)
    add_p("Session: 2022-2023", size=10, space_after=1)
    add_p("Course Code: CSE356 | Course Title: Software Engineering Sessional", size=10, space_after=1)
    add_p("Department of Computer Science and Engineering, GSTU", size=10, space_after=1)
    add_p("Submitted To: Dr. Mrinal Kanti Baowaly (Professor, Dept. of CSE)", italic=True, size=10, space_after=6)

    add_h1("1. Introduction")

    add_h2("1.1 Purpose")
    add_p("This SRS specifies requirements, architecture, and database models for the web-based Utility Management System (UMS).", space_after=3)

    add_h2("1.2 Scope")
    add_p("UMS automates multi-utility (Electricity, Water, Gas) operations. Core features:", space_after=1.5)
    add_bullet(" Role-based access (`admin`, `employee`, `customer`).", bold_prefix="Auth:")
    add_bullet(" Smart meter inventory & reading tracking.", bold_prefix="Meters:")
    add_bullet(" Automated tariff billing & PDF invoices.", bold_prefix="Billing:")
    add_bullet(" Instant SMTP email invoice reminders.", bold_prefix="Notifications:")
    add_bullet(" Digital payments, complaints, GIS map & reports.", bold_prefix="Services:", space_after=3)

    add_h2("1.3 Definitions, Acronyms, and Abbreviations")
    t1 = doc.add_table(rows=6, cols=2)
    headers = ["Term", "Definition & Context"]
    t1_data = [
        ["SRS", "Software Requirements Specification"],
        ["UMS", "Utility Management System Platform"],
        ["UI / SPA", "User Interface / Single Page Application"],
        ["REST / API", "Representational State Transfer / HTTP API"],
        ["GIS / ERD", "Geographic Information System / Entity Relationship Diagram"]
    ]
    for c_idx, h in enumerate(headers):
        p = t1.rows[0].cells[c_idx].paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
    for r_idx, row_data in enumerate(t1_data):
        for c_idx, val in enumerate(row_data):
            p = t1.rows[r_idx+1].cells[c_idx].paragraphs[0]
            p.add_run(val)
    style_table(t1, [1.4, 5.8], font_size=9)

    add_h2("1.4 References")
    add_bullet("IEEE Std 830-1998 & IEEE Std 29148-2018 Standards.")
    add_bullet("Express.js, MySQL 8.0, and Leaflet.js Technical Docs.", space_after=3)

    add_h2("1.5 Overview")
    add_p("Document organized into 7 sections: System Overview, Functions, Requirements (FR-01 to FR-41), Interfaces, NFRs, Policies, and DFD/ERD.", space_after=3)

    add_h1("2. Overall Description")
    add_h2("2.1 Product Perspective")
    add_p("UMS is a full-stack SPA. Backend runs on Node.js/Express.js with MySQL (`utilis_db`) via REST API.", space_after=3)

    add_h2("2.2 Product Functions")
    add_bullet("User authentication & role session control.")
    add_bullet("Customer directory & profile management.")
    add_bullet("Smart meter registration & classification (Electricity/Water/Gas).")
    add_bullet("Monthly reading logs & delta calculation (`curr - prev`).")
    add_bullet("Tariff billing calculation & PDF invoice creation.")
    add_bullet("SMTP email dispatch for bill alerts & reminders.")
    add_bullet("Digital payments (bKash, Nagad, Card, Bank).")
    add_bullet("Support ticketing with JSON comment logs.")
    add_bullet("Field maintenance task assignment for staff.")
    add_bullet("Leaflet GIS spatial outage map visualization.")
    add_bullet("Executive analytics dashboard with Chart.js charts.", space_after=4)

    # PAGE BREAK TO PAGE 2
    doc.add_page_break()

    # ================= PAGE 2 =================
    add_h2("2.3 User Classes and Characteristics")
    t2 = doc.add_table(rows=4, cols=2)
    t2_headers = ["User Role", "Responsibilities & Permissions"]
    t2_data = [
        ["System Administrator (admin)", "Full control over customer records, meter setup, billing, GIS map, staff assignment, and financial reports."],
        ["Utility Field Staff (employee)", "Logs monthly meter readings, updates technical tickets, and checks GIS meter locations."],
        ["Utility Customer (customer)", "Views/pays utility bills online, submits meter readings, logs complaints, and tracks payment receipts."]
    ]
    for c_idx, h in enumerate(t2_headers):
        p = t2.rows[0].cells[c_idx].paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
    for r_idx, row_data in enumerate(t2_data):
        for c_idx, val in enumerate(row_data):
            p = t2.rows[r_idx+1].cells[c_idx].paragraphs[0]
            p.add_run(val)
    style_table(t2, [1.8, 5.4], font_size=9)

    add_h2("2.4 Operating Environment")
    add_bullet(" Node.js v18+, Express.js, Nodemailer.", bold_prefix="Server:")
    add_bullet(" MySQL Server v8.0+ (`utilis_db`).", bold_prefix="Database:")
    add_bullet(" Chrome, Firefox, Edge, Safari running SPA.", bold_prefix="Client:", space_after=3)

    add_h2("2.5 Design and Implementation Constraints")
    add_bullet("Dual-port runtime: Express REST API port 5000, HTTP frontend port 8080.")
    add_bullet("InnoDB foreign key constraints across 9 relational tables.")
    add_bullet("Non-negative consumption delta enforcement (`currReading >= prevReading`).", space_after=3)

    add_h2("2.6 User Documentation")
    add_bullet("Installation & API operational guide in root `README.md`.", space_after=3)

    add_h2("2.7 Assumptions and Dependencies")
    add_bullet("Users have browser internet access; MySQL DB & SMTP servers active.", space_after=4)

    add_h1("3. System Features (Functional Requirements)")

    add_h2("3.1 Module 1: User Authentication & Profile Management")
    add_bullet("FR-01: User login via valid username/email and password.")
    add_bullet("FR-02: `sessionStorage` state with role permissions (`admin`, `employee`, `customer`).")
    add_bullet("FR-03: Self-registration for customers with meter details.")
    add_bullet("FR-04: User profile edit; FR-05: Secure session logout.", space_after=2)

    add_h2("3.2 Module 2: Customer Account Management")
    add_bullet("FR-06: Customer directory linking profiles to user logins.")
    add_bullet("FR-07: Admin customer search & edits; FR-08: Account activation/deactivation.")
    add_bullet("FR-09: Assign and re-link smart meters to customer accounts.", space_after=2)

    add_h2("3.3 Module 3: Smart Meter & Reading Tracking")
    add_bullet("FR-10: Meter inventory with serial, utility type (Electricity/Water/Gas), and status.")
    add_bullet("FR-11: Register smart meters; FR-12: Log monthly reading units.")
    add_bullet("FR-13: Display meter status flags (`active`, `faulty`, `inactive`).", space_after=2)

    add_h2("3.4 Module 4: Consumption Billing & Tariff Calculation")
    add_bullet("FR-14: Filter meters by category; FR-15: Auto-calculate `consumption = curr - prev`.")
    add_bullet("FR-16: Compute bill totals using tariff rates; FR-17: Enforce due dates & billing months.")
    add_bullet("FR-18: Admin manual/batch billing; FR-19: Set status (`unpaid`, `paid`, `overdue`).", space_after=2)

    add_h2("3.5 Module 5: Automated Email Notification & Reminder System")
    add_bullet("FR-20: Auto-dispatch invoice emails on bill creation.")
    add_bullet("FR-21: Admin `/api/send-bill-reminder` for unpaid bills.")
    add_bullet("FR-22: Render HTML templates with bill details; FR-23: Store in-app notifications.", space_after=4)

    # PAGE BREAK TO PAGE 3
    doc.add_page_break()

    # ================= PAGE 3 =================
    add_h2("3.6 Module 6: Payment Processing & Financial Accounting")
    add_bullet("FR-24: Digital payments (bKash, Nagad, Rocket, Bank, Card).")
    add_bullet("FR-25: Validate inputs & record transaction IDs (`transactionId`).")
    add_bullet("FR-26: Auto-update status to `paid`; FR-27: Generate digital payment receipts.", space_after=2)

    add_h2("3.7 Module 7: Complaint Management & Support Ticketing")
    add_bullet("FR-28: Customer complaint submission with category selection.")
    add_bullet("FR-29: Track ticket status (`Pending`, `In Progress`, `Resolved`); FR-30: Staff assignment.")
    add_bullet("FR-31: Interactive JSON comment threads between customer and staff.", space_after=2)

    add_h2("3.8 Module 8: Field Maintenance & Technical Operations")
    add_bullet("FR-32: Log maintenance requests (Meter Repair, Leak Check, Line Maintenance).")
    add_bullet("FR-33: Record maintenance type, customer link, technician ID, and timestamp.")
    add_bullet("FR-34: Field staff progress updates; FR-35: Admin dashboard maintenance counters.", space_after=2)

    add_h2("3.9 Module 9: Geographic Information System (GIS) & Spatial Mapping")
    add_bullet("FR-36: Integrate Leaflet GIS map displaying spatial meter distribution.")
    add_bullet("FR-37: Plot custom map markers for meter health & utility categories.")
    add_bullet("FR-38: Highlight active utility outage zones and transformer substation nodes.", space_after=2)

    add_h2("3.10 Module 10: Reports & Executive Analytics Engine")
    add_bullet("FR-39: Render Chart.js analytics for monthly consumption and revenue.")
    add_bullet("FR-40: Executive KPIs for customer count, meters, revenue, and unpaid balances.")
    add_bullet("FR-41: Export customer ledgers and billing summaries to PDF format.", space_after=4)

    add_h1("4. External Interface Requirements")
    add_h2("4.1 User Interfaces")
    add_p("Web UI built as responsive SPA using HTML5, CSS3, and JavaScript ES6:", space_after=1.5)
    add_bullet("Role-specific sidebar navigation; KPI summary metric cards.")
    add_bullet("Interactive data tables with search & filter; Styled modal dialogs.")
    add_bullet("Embedded Leaflet GIS map canvas with zoom & tooltip overlays.", space_after=3)

    add_h2("4.2 Hardware Interfaces")
    add_bullet(" Server: 2-Core CPU, 4 GB RAM, 20 GB SSD.", bold_prefix="Server:")
    add_bullet(" Client: PC, laptop, tablet, or smartphone (1024x768 display).", bold_prefix="Client:", space_after=3)

    add_h2("4.3 Software Interfaces")
    add_bullet("OS: Windows 10/11, Linux (Ubuntu 20.04+), or macOS.")
    add_bullet("Runtime: Node.js v18.0+, Express.js HTTP framework; DB: MySQL 8.0+ `InnoDB` UTF-8.", space_after=3)

    add_h2("4.4 Communication Interfaces")
    add_bullet("HTTP/HTTPS REST API exchange (`application/json`) on port 5000; CORS enabled port 8080; SMTP email.", space_after=4)

    add_h1("5. Non-Functional Requirements")
    t_nfr = doc.add_table(rows=6, cols=3)
    t_nfr_headers = ["ID", "Category", "Specification & Benchmark"]
    t_nfr_data = [
        ["NFR-01", "Performance", "API response < 1.5s for DB queries; < 3.0s for email dispatches."],
        ["NFR-02", "Security", "Passwords hashed securely; REST routes protected with session role checks."],
        ["NFR-03", "Reliability", "InnoDB relational foreign key constraints ensure 99.9% data integrity."],
        ["NFR-04", "Usability", "Responsive layout with clear status badges, toast feedback, and modal forms."],
        ["NFR-05", "Portability", "Cross-browser execution across Chrome, Firefox, Edge, and Safari."]
    ]
    for c_idx, h in enumerate(t_nfr_headers):
        p = t_nfr.rows[0].cells[c_idx].paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
    for r_idx, row_data in enumerate(t_nfr_data):
        for c_idx, val in enumerate(row_data):
            p = t_nfr.rows[r_idx+1].cells[c_idx].paragraphs[0]
            p.add_run(val)
    style_table(t_nfr, [0.8, 1.2, 5.2], font_size=9)

    # PAGE BREAK TO PAGE 4
    doc.add_page_break()

    # ================= PAGE 4 =================
    add_h1("6. Other Requirements")
    add_h2("6.1 Regulatory Compliance & Tariff Policies")
    add_p("The system enforces standardized tariff structures approved by national utility commissions, applying per-unit charges based on utility category (Electricity per kWh, Water per Litre, Gas per Unit).", space_after=3)

    add_h2("6.2 Data Privacy & Billing Audit Trail")
    add_p("All financial transactions, bill generations, and payments record exact creation timestamps and user links to maintain an immutable accounting audit trail.", space_after=4)

    add_h1("7. Appendices")
    add_h2("7.1 Appendix A: Data Flow Diagram (DFD Level 1)")
    add_bullet("Customer → [Login / Register] → User Authentication → Stores Session → `users` & `customers` DB.")
    add_bullet("Field Staff → [Meter Reading Data] → Reading Log Process → Stores Consumption Delta → `meter_readings` DB.")
    add_bullet("Billing Engine → [Fetch Readings & Tariff] → Billing Process → Computes Amount → `bills` DB → Sends Email.")
    add_bullet("Customer → [Payment Details] → Payment Gateway → Updates Status → `payments` & `bills` DB.")
    add_bullet("Customer → [Complaint / Request] → Support Ticket Process → Assigns Staff → `complaints` & `maintenance` DB.")
    add_bullet("Administrator → [Request GIS & Analytics] → Reporting Engine → Aggregates Map & Financial Graphs.", space_after=4)

    add_h2("7.2 Appendix B: Entity Relationship Diagram (ERD) & Database Schema")
    add_p("The `utilis_db` relational database comprises nine core tables structured as follows:", space_after=3)

    t_erd = doc.add_table(rows=10, cols=3)
    t_erd_headers = ["Table", "Keys & Attributes", "Functional Purpose"]
    t_erd_data = [
        ["users", "id (PK), name, username (UQ), email, password, role, status", "Stores user authentication credentials & roles (admin, employee, customer)."],
        ["customers", "customer_id (PK), user_id (FK -> users.id), phone, address", "Stores customer profile details linked to login account."],
        ["meters", "meter_id (PK), customer_id (FK), meter_number (UQ), utilityType, status", "Stores smart meter inventory (Electricity, Water, Gas) & customer link."],
        ["meter_readings", "reading_id (PK), meter_id (FK), month, unit_consumed", "Tracks monthly consumption units logged per meter."],
        ["bills", "bill_id (PK), customer_id (FK), amount, due_date, status, meterId, prevReading, currReading, tariffRate", "Stores calculated utility bills, reading deltas, tariff rates, due dates, & status."],
        ["payments", "payment_id (PK), bill_id (FK), amount, payment_date, method, transactionId", "Records payment transactions, channels (bKash, Nagad, Bank), & transaction IDs."],
        ["complaints", "complaint_id (PK), customer_id (FK), subject, description, status, assignedTo, comments (JSON)", "Manages customer support tickets, status pipeline, staff assignment, & comments."],
        ["notifications", "id (PK), userId (FK -> users.id), message, type, date, isRead", "Stores in-app system notifications and read/unread indicators."],
        ["maintenance", "maintenance_id (PK), customer_id (FK), request_type, description, status, assigned_to", "Manages technical field maintenance requests, assigned technicians, & progress."]
    ]
    for c_idx, h in enumerate(t_erd_headers):
        p = t_erd.rows[0].cells[c_idx].paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
    for r_idx, row_data in enumerate(t_erd_data):
        for c_idx, val in enumerate(row_data):
            p = t_erd.rows[r_idx+1].cells[c_idx].paragraphs[0]
            p.add_run(val)
    style_table(t_erd, [1.1, 2.7, 3.4], font_size=8.5)

    doc.save(output_docx_path)
    print(f"Docx generated at: {output_docx_path}")

if __name__ == "__main__":
    docx_path = r"d:\utility Management system\SRS_Utility_Management_System_4Page_Condensed.docx"
    downloads_pdf = r"C:\Users\Jasika\Downloads\srs_utility_management_system.pdf"
    workspace_pdf = r"d:\utility Management system\SRS_Utility_Management_System_4Page_Condensed.pdf"

    build_print_large_text_utility_srs(docx_path)
    
    convert(docx_path, workspace_pdf)
    print(f"Workspace PDF generated at: {workspace_pdf}")

    targets_pdf = [
        r"d:\utility Management system\SRS_Document_Utility.pdf",
        r"d:\utility Management system\SRS_Printable_Utility.pdf",
        r"d:\utility Management system\SRS_Utility_Management_System_4Page.pdf",
        r"C:\Users\Jasika\Downloads\SRS_Document_Utility.pdf",
        r"C:\Users\Jasika\Downloads\SRS_Printable_Utility.pdf",
        r"C:\Users\Jasika\Downloads\srs_utility_management_system.pdf"
    ]
    for t in targets_pdf:
        shutil.copy(workspace_pdf, t)
        print(f"Updated: {t}")
