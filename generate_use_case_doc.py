import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from PIL import Image, ImageDraw, ImageFont
import win32com.client

# ==================== 1. DIAGRAM GENERATION ====================
def generate_use_case_diagram(output_path="use_case_diagram.png"):
    width, height = 2400, 1750
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arialbd.ttf", 32)
        font_header = ImageFont.truetype("arialbd.ttf", 24)
        font_bold = ImageFont.truetype("arialbd.ttf", 19)
        font_normal = ImageFont.truetype("arial.ttf", 17)
        font_small = ImageFont.truetype("ariali.ttf", 15)
    except:
        font_title = ImageFont.load_default()
        font_header = font_title
        font_bold = font_title
        font_normal = font_title
        font_small = font_title

    # Colors
    COLOR_BG = (255, 255, 255)
    COLOR_BOUNDARY_BG = (248, 250, 252)
    COLOR_BOUNDARY_BORDER = (148, 163, 184)
    COLOR_HEADER_BG = (30, 41, 59)
    COLOR_HEADER_TEXT = (255, 255, 255)
    
    COLOR_ACTOR_HEAD = (30, 41, 59)
    COLOR_ACTOR_LINE = (30, 41, 59)
    
    COLOR_UC_FILL = (239, 246, 255)
    COLOR_UC_BORDER = (37, 99, 235)
    COLOR_UC_TEXT = (30, 41, 59)
    
    COLOR_LINE = (100, 116, 139)
    COLOR_DASH_LINE = (37, 99, 235)

    # System Boundary Box
    sb_left, sb_top, sb_right, sb_bottom = 460, 130, 1940, 1660
    draw.rectangle([sb_left, sb_top, sb_right, sb_bottom], fill=COLOR_BOUNDARY_BG, outline=COLOR_BOUNDARY_BORDER, width=3)
    
    # Boundary Title
    draw.rectangle([sb_left, sb_top, sb_right, sb_top + 60], fill=COLOR_HEADER_BG)
    draw.text((sb_left + 25, sb_top + 16), "SYSTEM BOUNDARY: UTILITY MANAGEMENT SYSTEM (utilis-app)", fill=COLOR_HEADER_TEXT, font=font_header)

    # Helper: Draw Stick Figure Actor
    def draw_actor(x, y, name, role_type="Primary Actor"):
        r = 26
        # Head
        draw.ellipse([x - r, y - r, x + r, y + r], outline=COLOR_ACTOR_HEAD, width=4, fill=(226, 232, 240))
        # Body
        draw.line([x, y + r, x, y + r + 50], fill=COLOR_ACTOR_LINE, width=4)
        # Arms
        draw.line([x - 38, y + r + 18, x + 38, y + r + 18], fill=COLOR_ACTOR_LINE, width=4)
        # Legs
        draw.line([x, y + r + 50, x - 26, y + r + 100], fill=COLOR_ACTOR_LINE, width=4)
        draw.line([x, y + r + 50, x + 26, y + r + 100], fill=COLOR_ACTOR_LINE, width=4)
        
        # Name Box
        bbox = draw.textbbox((0, 0), name, font=font_bold)
        tw = bbox[2] - bbox[0]
        draw.text((x - tw // 2, y + r + 108), name, fill=COLOR_ACTOR_HEAD, font=font_bold)
        
        bbox_sub = draw.textbbox((0, 0), f"({role_type})", font=font_small)
        tw_sub = bbox_sub[2] - bbox_sub[0]
        draw.text((x - tw_sub // 2, y + r + 132), f"({role_type})", fill=(100, 116, 139), font=font_small)

    # Draw Actors
    draw_actor(230, 320, "System Administrator", "Primary Admin")
    draw_actor(230, 950, "Utility Field Staff", "Field Technician")
    
    draw_actor(2170, 460, "Utility Customer", "Consumer/User")
    draw_actor(2170, 1150, "External Gateway", "Nodemailer / Payment API")

    # Helper: Draw Use Case Ellipse
    def draw_use_case(x, y, uc_id, uc_name, width_uc=330, height_uc=86):
        left = x - width_uc // 2
        top = y - height_uc // 2
        right = x + width_uc // 2
        bottom = y + height_uc // 2
        
        draw.ellipse([left, top, right, bottom], fill=COLOR_UC_FILL, outline=COLOR_UC_BORDER, width=3)
        
        full_text = f"{uc_id}: {uc_name}"
        words = full_text.split()
        lines = []
        cur_line = ""
        for w in words:
            test = (cur_line + " " + w).strip()
            if draw.textbbox((0,0), test, font=font_normal)[2] > width_uc - 35:
                lines.append(cur_line)
                cur_line = w
            else:
                cur_line = test
        if cur_line:
            lines.append(cur_line)
            
        total_h = len(lines) * 20
        start_y = y - total_h // 2
        for line in lines:
            tb = draw.textbbox((0,0), line, font=font_normal)
            lw = tb[2] - tb[0]
            draw.text((x - lw // 2, start_y), line, fill=COLOR_UC_TEXT, font=font_normal)
            start_y += 20

        return (x, y)

    # Positions inside boundary
    uc_pos = {}
    uc_pos["UC01"] = draw_use_case(700, 250, "UC-01", "User Authentication & Profile")
    uc_pos["UC02"] = draw_use_case(700, 440, "UC-02", "Manage Customer Directory")
    uc_pos["UC03"] = draw_use_case(700, 630, "UC-03", "Register Smart Utility Meters")
    uc_pos["UC04"] = draw_use_case(700, 820, "UC-04", "Log Monthly Meter Readings")
    uc_pos["UC05"] = draw_use_case(700, 1010, "UC-05", "Calculate Bills & Apply Tariffs")
    uc_pos["UC06"] = draw_use_case(700, 1200, "UC-06", "Dispatch Email Reminders")

    uc_pos["UC07"] = draw_use_case(1200, 340, "UC-07", "View Bills & Account Ledger")
    uc_pos["UC08"] = draw_use_case(1200, 580, "UC-08", "Process Online Payments")
    uc_pos["UC09"] = draw_use_case(1200, 820, "UC-09", "Submit & Track Support Tickets")
    uc_pos["UC10"] = draw_use_case(1200, 1060, "UC-10", "Field Maintenance Dispatch")
    
    uc_pos["UC11"] = draw_use_case(1680, 460, "UC-11", "View GIS Map & Outage Zones")
    uc_pos["UC12"] = draw_use_case(1680, 920, "UC-12", "Generate Financial Analytics")
    uc_pos["UC13"] = draw_use_case(1680, 1340, "UC-13", "Download Digital Receipts")

    # Connect Actors
    def connect(actor_xy, uc_xy):
        draw.line([actor_xy[0], actor_xy[1], uc_xy[0], uc_xy[1]], fill=COLOR_LINE, width=2)

    admin_xy = (330, 320)
    staff_xy = (330, 950)
    customer_xy = (2030, 460)
    ext_xy = (2030, 1150)

    # Connections: Admin
    connect(admin_xy, uc_pos["UC01"])
    connect(admin_xy, uc_pos["UC02"])
    connect(admin_xy, uc_pos["UC03"])
    connect(admin_xy, uc_pos["UC05"])
    connect(admin_xy, uc_pos["UC06"])
    connect(admin_xy, uc_pos["UC10"])
    connect(admin_xy, uc_pos["UC12"])

    # Connections: Staff
    connect(staff_xy, uc_pos["UC01"])
    connect(staff_xy, uc_pos["UC04"])
    connect(staff_xy, uc_pos["UC09"])
    connect(staff_xy, uc_pos["UC10"])
    connect(staff_xy, uc_pos["UC11"])

    # Connections: Customer
    connect(customer_xy, uc_pos["UC01"])
    connect(customer_xy, uc_pos["UC07"])
    connect(customer_xy, uc_pos["UC08"])
    connect(customer_xy, uc_pos["UC09"])
    connect(customer_xy, uc_pos["UC13"])

    # Connections: External
    connect(ext_xy, uc_pos["UC06"])
    connect(ext_xy, uc_pos["UC08"])

    # Dashed relationships
    def draw_dashed(p1, p2, label="<<include>>"):
        x1, y1 = p1
        x2, y2 = p2
        import math
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist == 0: return
        dash_len = 10
        gap_len = 8
        step = dash_len + gap_len
        num_steps = int(dist / step)
        
        for i in range(num_steps):
            t1 = (i * step) / dist
            t2 = min(((i * step) + dash_len) / dist, 1.0)
            sx = x1 + (x2 - x1) * t1
            sy = y1 + (y2 - y1) * t1
            ex = x1 + (x2 - x1) * t2
            ey = y1 + (y2 - y1) * t2
            draw.line([sx, sy, ex, ey], fill=COLOR_DASH_LINE, width=2)
            
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        tb = draw.textbbox((0,0), label, font=font_small)
        lw = tb[2] - tb[0]
        lh = tb[3] - tb[1]
        draw.rectangle([mx - lw//2 - 4, my - lh//2 - 2, mx + lw//2 + 4, my + lh//2 + 2], fill=(255,255,255), outline=COLOR_DASH_LINE)
        draw.text((mx - lw//2, my - lh//2 - 2), label, fill=COLOR_DASH_LINE, font=font_small)

    draw_dashed(uc_pos["UC05"], uc_pos["UC04"], "<<include>>")
    draw_dashed(uc_pos["UC06"], uc_pos["UC05"], "<<include>>")
    draw_dashed(uc_pos["UC08"], uc_pos["UC07"], "<<include>>")
    draw_dashed(uc_pos["UC13"], uc_pos["UC08"], "<<extend>>")
    draw_dashed(uc_pos["UC10"], uc_pos["UC09"], "<<extend>>")

    # Legend
    leg_x, leg_y = 500, 1500
    draw.rectangle([leg_x, leg_y, leg_x + 680, leg_y + 110], fill=(255, 255, 255), outline=COLOR_BOUNDARY_BORDER, width=2)
    draw.text((leg_x + 15, leg_y + 10), "UML Diagram Legend & Notation:", fill=COLOR_HEADER_BG, font=font_bold)
    draw.line([leg_x + 20, leg_y + 50, leg_x + 100, leg_y + 50], fill=COLOR_LINE, width=2)
    draw.text((leg_x + 110, leg_y + 40), "Solid Line: Actor Association", fill=COLOR_UC_TEXT, font=font_small)
    draw_dashed((leg_x + 20, leg_y + 85), (leg_x + 120, leg_y + 85), "<<include>>")
    draw.text((leg_x + 140, leg_y + 75), "Dashed Arrow: Dependency (<<include>> / <<extend>>)", fill=COLOR_UC_TEXT, font=font_small)

    img.save(output_path, "PNG")
    print("Use Case Diagram saved to:", output_path)
    return output_path

# ==================== 2. DOCX DOCUMENT BUILDER ====================
def build_printable_use_case_docx(docx_path, pdf_path):
    # Ensure diagram image is generated
    img_path = generate_use_case_diagram("use_case_diagram.png")

    doc = docx.Document()

    # Styling Palette
    COLOR_PRIMARY = RGBColor(30, 41, 59)     # #1E293B Navy
    COLOR_ACCENT = RGBColor(37, 99, 235)     # #2563EB Royal Blue
    COLOR_DARK = RGBColor(51, 65, 85)       # Body text
    COLOR_GRAY = RGBColor(100, 116, 139)    # Subtitles/footers
    COLOR_WHITE = RGBColor(255, 255, 255)

    # 1. Page Margins (1.0 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Font default: Times New Roman
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = COLOR_DARK

    # Helpers
    def add_page_number_fields(run_pg, run_num):
        fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
        instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
        fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
        fldChar3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
        run_pg._r.append(fldChar1)
        run_pg._r.append(instrText)
        run_pg._r.append(fldChar2)
        run_pg._r.append(fldChar3)

        fldChar1_b = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
        instrText_b = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> NUMPAGES </w:instrText>')
        fldChar2_b = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
        fldChar3_b = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
        run_num._r.append(fldChar1_b)
        run_num._r.append(instrText_b)
        run_num._r.append(fldChar2_b)
        run_num._r.append(fldChar3_b)

    def set_cell_background(cell, hex_color):
        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading_elm)

    def format_table(table):
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

    def add_h1(text):
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

    def add_h2(text):
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

    def add_p(text, bold_prefix=""):
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
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(100)
    p_title.paragraph_format.space_after = Pt(12)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_title.add_run("SOFTWARE DESIGN SPECIFICATION\nUSE CASE MODEL & SPECIFICATIONS")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(22)
    r.font.bold = True
    r.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(140)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p_sub.add_run("Project: Utility Management System (utilis-app)\nStructured in Accordance with Chapter 5: Software Design Principles")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_ACCENT

    # Student / Author Info Table
    info_table = doc.add_table(rows=5, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        ("Prepared By:", "Jasika Noor"),
        ("Student ID:", "22CSE002"),
        ("Course Title:", "Software Engineering & Software Design"),
        ("Academic Topic:", "Chapter 5: Object-Oriented Software Design & UML Use Case Diagrams"),
        ("Date:", "August 30, 2026")
    ]
    for idx, (label, val) in enumerate(info_data):
        row = info_table.rows[idx]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        
        p0 = cell_lbl.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_l = p0.add_run(label)
        r_l.font.bold = True
        r_l.font.color.rgb = COLOR_PRIMARY
        
        p1 = cell_val.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r_v = p1.add_run(val)
        r_v.font.color.rgb = COLOR_DARK

    doc.add_page_break()

    # Configure Header / Footer for subsequent pages
    body_section = doc.sections[0] # or second section after break
    header = body_section.header
    p_hdr = header.paragraphs[0]
    p_hdr.text = "Utility Management System — Use Case Design Document (Chapter 5)"
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_hdr.style.font.name = 'Times New Roman'
    p_hdr.style.font.size = Pt(8.5)
    p_hdr.style.font.color.rgb = COLOR_GRAY

    footer = body_section.footer
    p_ftr = footer.paragraphs[0]
    p_ftr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_ftr_l = p_ftr.add_run("Student ID: 22CSE002 | Page ")
    r_ftr_l.font.size = Pt(9)
    r_ftr_l.font.color.rgb = COLOR_GRAY
    
    r_pg = p_ftr.add_run()
    r_pg.font.size = Pt(9)
    r_pg.font.color.rgb = COLOR_GRAY
    
    r_mid = p_ftr.add_run(" of ")
    r_mid.font.size = Pt(9)
    r_mid.font.color.rgb = COLOR_GRAY
    
    r_num = p_ftr.add_run()
    r_num.font.size = Pt(9)
    r_num.font.color.rgb = COLOR_GRAY
    
    add_page_number_fields(r_pg, r_num)

    # ==================== SECTION 1: INTRODUCTION ====================
    add_h1("1. Introduction & System Boundary Definition")
    add_p("The Use Case Model provides a formal functional decomposition of the Utility Management System (utilis-app) in accordance with standard software engineering design principles (Chapter 5: Software Design). The model defines the external actors interacting with the system, the system boundary enclosing core utility administration capabilities, and the exact interactions required to fulfill consumer utility needs (Electricity, Water, and Gas).")
    
    add_h2("1.1 System Boundary")
    add_p("The system boundary encloses all automated workflows executed by the application backend (Node.js/Express.js REST APIs and MySQL relational storage) and front-end user portals. Interactivity across the boundary is established strictly via four identified external actors:")
    add_p("Full administrative control over customer registries, smart meter inventories, tiered billing calculations, Nodemailer notification dispatches, field technician job assignments, GIS spatial mapping, and executive revenue reporting.", "1. System Administrator (admin): ")
    add_p("Operational staff handling physical monthly meter reading dispatches, meter health inspections, resolving logged technical complaints, and executing field maintenance tasks.", "2. Utility Field Staff (employee): ")
    add_p("End-user consumers performing self-registration, inspecting active utility bills, settling balances via digital payment channels (bKash, Nagad, Bank), downloading payment receipts, and submitting service tickets.", "3. Utility Customer (customer): ")
    add_p("External services interfacing with the system boundary including Nodemailer SMTP services for automated billing alert dispatches and Payment Gateway APIs for transaction settlement.", "4. External Systems & Gateways: ")

    # ==================== SECTION 2: ACTOR SPECIFICATIONS ====================
    add_h1("2. External Actor Specifications")
    add_p("The table below details all human and system actors interacting with the Utility Management System boundary, including their role classification and operational privilege matrix.")

    actor_table = doc.add_table(rows=5, cols=4)
    format_table(actor_table)
    headers = ["Actor Name", "Actor Type", "System Role & Scope", "Access Permissions & Privileges"]
    for i, h in enumerate(headers):
        actor_table.rows[0].cells[i].paragraphs[0].text = h
    
    actors_info = [
        ("System Administrator", "Primary Human Actor", "Utility Executive & Portal Admin", "Full CRUD operations on customers, meters, bill generation, email dispatch, technician dispatches, and financial dashboards."),
        ("Utility Field Staff", "Primary Human Actor", "Field Engineer & Meter Inspector", "Permission to record monthly meter readings, inspect meter health, update complaint statuses, and resolve maintenance tickets."),
        ("Utility Customer", "Primary Human Actor", "Residential / Commercial Consumer", "Role-restricted access to view personal utility bills, submit payments, log complaints, track tickets, and download receipts."),
        ("External Gateway", "Secondary System Actor", "Third-Party Email / Payment API", "Automated system-to-system interfaces for Nodemailer email delivery and payment transaction verification.")
    ]

    for row_idx, data in enumerate(actors_info, start=1):
        row = actor_table.rows[row_idx]
        for col_idx, text in enumerate(data):
            row.cells[col_idx].paragraphs[0].text = text

    # ==================== SECTION 3: USE CASE DIAGRAM ====================
    add_h1("3. Graphical Use Case Model & Diagram")
    add_p("Figure 1 below illustrates the formal UML Use Case Diagram for the Utility Management System, detailing all 13 core use cases within the system boundary, actor associations, and dependency relationships (<<include>> and <<extend>>).")

    # Embed High-Res Image
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(10)
    p_img.paragraph_format.space_after = Pt(4)
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Inches(6.5))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_after = Pt(14)
    r_cap = p_cap.add_run("Figure 1: Complete UML Use Case Diagram — Utility Management System (utilis-app)")
    r_cap.font.italic = True
    r_cap.font.size = Pt(9.5)
    r_cap.font.color.rgb = COLOR_GRAY

    # Summary Table of Use Cases
    add_h2("3.1 Use Case Inventory & Summary Table")
    uc_summary_table = doc.add_table(rows=14, cols=5)
    format_table(uc_summary_table)
    uc_headers = ["UC ID", "Use Case Name", "Primary Actor", "Secondary Actor", "Summary Description"]
    for i, h in enumerate(uc_headers):
        uc_summary_table.rows[0].cells[i].paragraphs[0].text = h

    uc_list_data = [
        ("UC-01", "User Authentication & Profile", "All Users", "N/A", "Secure user login, registration, session management, and profile update."),
        ("UC-02", "Manage Customer Directory", "Administrator", "N/A", "Create, update, deactivate customer records and link service locations."),
        ("UC-03", "Register Smart Utility Meters", "Administrator", "N/A", "Inventory tracking, assigning meters (Electricity, Water, Gas) to customers."),
        ("UC-04", "Log Monthly Meter Readings", "Field Staff", "Customer", "Record monthly consumption units and calculate usage delta."),
        ("UC-05", "Calculate Bills & Apply Tariffs", "Administrator", "N/A", "Automated billing engine computing amount = consumption * tariff rate."),
        ("UC-06", "Dispatch Email Reminders", "Administrator", "External Gateway", "Trigger automated Nodemailer invoice notices and urgent payment reminders."),
        ("UC-07", "View Bills & Account Ledger", "Customer", "N/A", "Consumer access to active unpaid bills, billing history, and due dates."),
        ("UC-08", "Process Online Payments", "Customer", "External Gateway", "Digital bill settlement (bKash/Nagad/Bank) and automated invoice status update."),
        ("UC-09", "Submit & Track Support Tickets", "Customer", "Field Staff", "Customer complaint filing with interactive comment threads and status updates."),
        ("UC-10", "Field Maintenance Dispatch", "Administrator", "Field Staff", "Schedule emergency meter repairs, assign technicians, and log resolutions."),
        ("UC-11", "View GIS Map & Outage Zones", "Field Staff", "Administrator", "Interactive Leaflet spatial mapping of customer meters and outage zones."),
        ("UC-12", "Generate Financial Analytics", "Administrator", "N/A", "Executive revenue collection charts, utility breakdown, and financial reports."),
        ("UC-13", "Download Digital Receipts", "Customer", "N/A", "Generate printable payment receipts with transaction reference IDs.")
    ]

    for row_idx, data in enumerate(uc_list_data, start=1):
        row = uc_summary_table.rows[row_idx]
        for col_idx, text in enumerate(data):
            row.cells[col_idx].paragraphs[0].text = text

    doc.add_page_break()

    # ==================== SECTION 4: DETAILED USE CASE SPECIFICATIONS ====================
    add_h1("4. Detailed Use Case Specifications")
    add_p("This section presents formal software engineering specifications for each core use case, adhering to the standard Chapter 5 template (Pre-conditions, Post-conditions, Main Success Scenario, and Alternate Flows).")

    specs_data = [
        {
            "id": "UC-01", "name": "User Authentication & Profile Management",
            "actor": "System Administrator, Utility Field Staff, Utility Customer",
            "desc": "Allows any registered user to log into the application portal, maintain active session state, update contact profiles, or log out.",
            "pre": "User has an active account registered in the `users` database table.",
            "post": "Session token/data is stored in client `sessionStorage` with role permissions enforced.",
            "main": [
                "1. User navigates to the Utility Management System portal login modal.",
                "2. User enters registered Username/Email and Password credentials.",
                "3. System validates credentials against stored password hashes in MySQL database.",
                "4. System initializes session state with role type (`admin`, `employee`, or `customer`).",
                "5. System redirects user to their respective role dashboard."
            ],
            "alt": [
                "3a. Invalid Credentials: System displays error message 'Invalid email or password' and prompts retry.",
                "4a. Deactivated Account: System blocks authentication and prompts user to contact Administrator."
            ]
        },
        {
            "id": "UC-02", "name": "Manage Customer Account Directory",
            "actor": "System Administrator",
            "desc": "Provides administrative capabilities to create, edit, search, and update customer profile ledgers.",
            "pre": "Administrator is authenticated with `admin` privileges.",
            "post": "Customer record is updated in the `customers` database table.",
            "main": [
                "1. Administrator selects 'Customer Management' from the navigation sidebar.",
                "2. System retrieves and displays customer records in an interactive data table.",
                "3. Administrator clicks 'Add Customer' button and enters customer details (Name, Address, Phone, Email).",
                "4. Administrator submits form; System validates unique email constraint and persists record.",
                "5. System updates customer table grid with real-time feedback notice."
            ],
            "alt": [
                "4a. Duplicate Email/User: System highlights duplicate field and prevents database submission.",
                "4b. Deactivation: Administrator toggles account status flag to 'inactive'."
            ]
        },
        {
            "id": "UC-03", "name": "Register & Assign Smart Utility Meters",
            "actor": "System Administrator",
            "desc": "Enables registration of new physical utility meters (Electricity, Water, Gas) and assignment to customer service addresses.",
            "pre": "Customer account exists; Physical meter serial number is available.",
            "post": "New meter entry stored in `meters` table linked via foreign key `customer_id`.",
            "main": [
                "1. Administrator opens 'Meter Inventory' module.",
                "2. Administrator clicks 'Register New Meter' modal.",
                "3. Administrator inputs Serial Number, Utility Category (Electricity/Water/Gas), and selects target Customer.",
                "4. System creates meter record with default status 'active'.",
                "5. System confirms successful meter registration."
            ],
            "alt": [
                "3a. Duplicate Serial Number: System alerts administrator that meter serial already exists."
            ]
        },
        {
            "id": "UC-04", "name": "Log Monthly Meter Consumption Readings",
            "actor": "Utility Field Staff / System Administrator",
            "desc": "Logs monthly utility consumption figures recorded by field staff or smart meter telemetry.",
            "pre": "Meter status is marked as 'active'.",
            "post": "New reading record created in `meter_readings` table with consumption delta.",
            "main": [
                "1. Field Staff opens 'Meter Readings' panel.",
                "2. Staff selects target meter serial number and current billing month.",
                "3. Staff enters current meter reading value (`currReading`).",
                "4. System fetches previous reading (`prevReading`) and calculates delta: `consumption = currReading - prevReading`.",
                "5. System saves reading record and logs timestamp."
            ],
            "alt": [
                "4a. Negative Consumption: If `currReading < prevReading`, system rejects input as invalid reading anomaly."
            ]
        },
        {
            "id": "UC-05", "name": "Calculate Utility Bills & Apply Tariffs",
            "actor": "System Administrator",
            "desc": "Automated billing engine computing monthly bill invoice amounts based on consumption and applicable tariff rates.",
            "pre": "Monthly meter reading is recorded for the billing cycle.",
            "post": "Invoice generated in `bills` table with status 'unpaid'.",
            "main": [
                "1. Administrator triggers 'Generate Billing' for current cycle.",
                "2. System fetches all active meter readings for the cycle.",
                "3. System applies tariff formula: `totalAmount = unitsConsumed * tariffRate`.",
                "4. System assigns billing month, billing year, and sets due date (15 days from issue).",
                "5. Invoice is written to database with status 'unpaid'."
            ],
            "alt": [
                "2a. Missing Reading: System skips bill generation for meters without recorded readings and flags alert."
            ]
        },
        {
            "id": "UC-06", "name": "Dispatch Email Notifications & Reminders",
            "actor": "System Administrator (Primary), External Nodemailer Gateway (Secondary)",
            "desc": "Sends automated email billing notices and urgent unpaid bill reminders directly to customer email addresses.",
            "pre": "Bill record exists in `bills` table; SMTP configuration is active.",
            "post": "Email dispatched to customer; notification record logged in `notifications` table.",
            "main": [
                "1. Administrator clicks 'Send Bill Reminder' button on unpaid bill dashboard.",
                "2. Backend fetches customer email, bill invoice ID, utility type, and due amount.",
                "3. Nodemailer constructs formatted HTML email template.",
                "4. System dispatches email via SMTP server.",
                "5. System displays success alert and updates notification log."
            ],
            "alt": [
                "4a. SMTP Failure: System catches email server timeout error, logs failure, and alerts admin to check credentials."
            ]
        },
        {
            "id": "UC-07", "name": "View Bills & Account Ledger",
            "actor": "Utility Customer",
            "desc": "Allows consumers to view their active unpaid bills, historical payment ledgers, and breakdown of charges.",
            "pre": "Customer is logged into portal.",
            "post": "Customer receives full view of billing statements.",
            "main": [
                "1. Customer navigates to 'My Bills' workspace.",
                "2. System queries `bills` table matching customer's linked meter IDs.",
                "3. System renders bill list with status badges ('Paid', 'Unpaid', 'Overdue').",
                "4. Customer clicks 'View Details' to inspect consumption breakdown and due date."
            ],
            "alt": [
                "2a. No Bills Found: System displays friendly notice 'No active billing statements found'."
            ]
        },
        {
            "id": "UC-08", "name": "Process Online Payment Settlement",
            "actor": "Utility Customer (Primary), External Payment API (Secondary)",
            "desc": "Enables customers to pay unpaid bills online using digital mobile payment methods (bKash, Nagad, Bank).",
            "pre": "Bill status is 'unpaid' or 'overdue'.",
            "post": "Payment recorded in `payments` table; Bill status updated to 'paid'.",
            "main": [
                "1. Customer clicks 'Pay Now' next to an unpaid bill invoice.",
                "2. Customer selects payment method (bKash, Nagad, Rocket, Credit Card).",
                "3. Customer enters payment details and transaction reference ID.",
                "4. System verifies transaction input and records payment record.",
                "5. System updates bill status in database to 'paid'."
            ],
            "alt": [
                "4a. Transaction Verification Failure: System prompts user to re-check transaction ID."
            ]
        },
        {
            "id": "UC-09", "name": "Submit & Track Support Complaints",
            "actor": "Utility Customer (Primary), Utility Field Staff / Admin (Secondary)",
            "desc": "Customer ticketing system for lodging service complaints (meter fault, billing error) with live discussion threads.",
            "pre": "Customer is authenticated.",
            "post": "Ticket logged in `complaints` table with status 'Pending'.",
            "main": [
                "1. Customer clicks 'Log Complaint' button.",
                "2. Customer enters Complaint Subject, Utility Category, and detailed issue Description.",
                "3. System generates unique ticket ID and notifies admin dashboard.",
                "4. Staff responds via interactive comment thread and updates status ('In Progress' / 'Resolved')."
            ],
            "alt": [
                "4a. Re-opening Ticket: Customer can add comments if issue remains unresolved."
            ]
        },
        {
            "id": "UC-10", "name": "Field Maintenance Dispatch & Work Orders",
            "actor": "System Administrator (Primary), Utility Field Staff (Secondary)",
            "desc": "Schedules emergency repairs, assigns field technicians to technical service requests, and tracks completion.",
            "pre": "Technical complaint or maintenance request exists.",
            "post": "Work order updated in `maintenance` table with assigned technician ID.",
            "main": [
                "1. Administrator reviews open maintenance requests in dashboard.",
                "2. Administrator assigns available Field Staff technician to ticket.",
                "3. Field Staff technician receives task assignment notification.",
                "4. Technician inspects site, performs repair, and updates work order to 'Completed'."
            ],
            "alt": [
                "4a. Escalation: Technician logs requirement for replacement hardware."
            ]
        },
        {
            "id": "UC-11", "name": "View GIS Spatial Map & Outage Zones",
            "actor": "Utility Field Staff, System Administrator",
            "desc": "Interactive Leaflet GIS map displaying customer meter distribution, transformer nodes, and color-coded outage fault zones.",
            "pre": "Geographical coordinate data (Latitude/Longitude) present for meter locations.",
            "post": "Interactive spatial canvas rendered on screen.",
            "main": [
                "1. User clicks 'GIS Map View' tab in sidebar.",
                "2. System loads Leaflet map canvas centered on utility coverage area.",
                "3. System renders custom color-coded map markers for active, faulty, and outage meters.",
                "4. User clicks map marker to open popup tooltip showing customer details and meter health status."
            ],
            "alt": [
                "3a. No Coordinates: System places unmapped meters in default central substation hub."
            ]
        },
        {
            "id": "UC-12", "name": "Generate Executive Analytics & Revenue Reports",
            "actor": "System Administrator",
            "desc": "Executive dashboard rendering financial collection summaries, monthly consumption trends, and export capabilities.",
            "pre": "Billing and payment records exist in system database.",
            "post": "Analytical charts and summary statistics displayed.",
            "main": [
                "1. Administrator navigates to 'Analytics & Reports' tab.",
                "2. System computes aggregate figures: Total Billed, Total Collected, Unpaid Outstanding, Active Meters.",
                "3. System renders Chart.js bar and pie graphs illustrating utility revenue distribution.",
                "4. Administrator clicks 'Export PDF/Print' to generate official financial report."
            ],
            "alt": [
                "4a. Date Filter: Administrator filters analytics by specific billing year or utility type."
            ]
        },
        {
            "id": "UC-13", "name": "Download Digital Payment Receipts",
            "actor": "Utility Customer",
            "desc": "Generates clean, printable digital payment receipts for completed utility bill transactions.",
            "pre": "Bill payment status is 'paid'.",
            "post": "Printable digital receipt generated with transaction ID.",
            "main": [
                "1. Customer views paid bill entry in account ledger.",
                "2. Customer clicks 'Download Receipt' button.",
                "3. System formats payment receipt containing Customer Name, Meter ID, Amount Paid, Payment Channel, and Transaction ID.",
                "4. System opens browser print preview dialog."
            ],
            "alt": [
                "2a. Unpaid Bill: 'Download Receipt' button remains disabled until payment is verified."
            ]
        }
    ]

    for spec in specs_data:
        add_h2(f"{spec['id']}: {spec['name']}")
        
        t_spec = doc.add_table(rows=6, cols=2)
        format_table(t_spec)
        
        # Col width adjustments
        t_spec.columns[0].width = Inches(1.8)
        t_spec.columns[1].width = Inches(4.7)

        rows_content = [
            ("Use Case ID & Name:", f"{spec['id']} — {spec['name']}"),
            ("Primary Actors:", spec['actor']),
            ("Description:", spec['desc']),
            ("Pre-conditions:", spec['pre']),
            ("Post-conditions:", spec['post']),
            ("Main Success Flow:", "\n".join(spec['main']))
        ]
        
        for idx, (label, val) in enumerate(rows_content):
            row = t_spec.rows[idx]
            c0, c1 = row.cells[0], row.cells[1]
            
            p0 = c0.paragraphs[0]
            r_l = p0.add_run(label)
            r_l.font.bold = True
            r_l.font.color.rgb = COLOR_PRIMARY
            
            p1 = c1.paragraphs[0]
            p1.text = val
            
        # Alt flow paragraph below table
        add_p("\n".join(spec['alt']), "Alternative / Exception Flows: ")

    doc.add_page_break()

    # ==================== SECTION 5: TRACEABILITY MATRIX ====================
    add_h1("5. Requirements Traceability Matrix")
    add_p("The matrix below maps project Functional Requirements (FR-01 to FR-42) to their corresponding Use Case implementations within Chapter 5 Software Design.")

    matrix_table = doc.add_table(rows=11, cols=3)
    format_table(matrix_table)
    m_headers = ["Functional Module", "Functional Requirement Range", "Implemented Use Case(s)"]
    for i, h in enumerate(m_headers):
        matrix_table.rows[0].cells[i].paragraphs[0].text = h

    matrix_data = [
        ("1. User Authentication & Profile", "FR-01, FR-02, FR-03, FR-04, FR-05", "UC-01: User Authentication & Profile"),
        ("2. Customer Account Directory", "FR-06, FR-07, FR-08, FR-09", "UC-02: Manage Customer Directory"),
        ("3. Smart Meter & Reading Tracking", "FR-10, FR-11, FR-12, FR-13, FR-14", "UC-03: Register Smart Meters, UC-04: Log Meter Readings"),
        ("4. Billing Engine & Tariff Processing", "FR-15, FR-16, FR-17, FR-18, FR-19, FR-20", "UC-05: Calculate Bills & Apply Tariffs, UC-07: View Bills"),
        ("5. Automated Email Reminders", "FR-21, FR-22, FR-23, FR-24", "UC-06: Dispatch Email Reminders"),
        ("6. Online Payment Settlement", "FR-25, FR-26, FR-27, FR-28", "UC-08: Process Online Payments, UC-13: Download Receipts"),
        ("7. Complaint Management & Tickets", "FR-29, FR-30, FR-31, FR-32", "UC-09: Submit & Track Support Tickets"),
        ("8. Field Maintenance Operations", "FR-33, FR-34, FR-35, FR-36", "UC-10: Field Maintenance Dispatch"),
        ("9. GIS Spatial Mapping Engine", "FR-37, FR-38, FR-39", "UC-11: View GIS Spatial Map & Outage Zones"),
        ("10. Executive Analytics & Reports", "FR-40, FR-41, FR-42", "UC-12: Generate Financial Analytics")
    ]

    for row_idx, data in enumerate(matrix_data, start=1):
        row = matrix_table.rows[row_idx]
        for col_idx, text in enumerate(data):
            row.cells[col_idx].paragraphs[0].text = text

    # Save DOCX
    doc.save(docx_path)
    print(f"DOCX file created successfully at: {docx_path}")

    # Convert to PDF using win32com
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        abs_docx = os.path.abspath(docx_path)
        abs_pdf = os.path.abspath(pdf_path)
        
        doc_obj = word.Documents.Open(abs_docx)
        doc_obj.SaveAs(abs_pdf, FileFormat=17) # 17 = wdFormatPDF
        doc_obj.Close()
        word.Quit()
        print(f"PDF file generated successfully at: {pdf_path}")
    except Exception as e:
        print(f"PDF conversion note: {e}")

if __name__ == "__main__":
    out_docx = "Utility_Management_System_Use_Case_Document.docx"
    out_pdf = "Utility_Management_System_Use_Case_Document.pdf"
    build_printable_use_case_docx(out_docx, out_pdf)
