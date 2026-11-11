import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from PIL import Image, ImageDraw, ImageFont
import win32com.client

# ==================== 1. GENERATE PORTRAIT USE CASE DIAGRAM ====================
def generate_portrait_use_case_diagram(output_path="use_case_diagram_portrait.png"):
    width, height = 2400, 3100
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arialbd.ttf", 36)
        font_header = ImageFont.truetype("arialbd.ttf", 28)
        font_bold = ImageFont.truetype("arialbd.ttf", 22)
        font_normal = ImageFont.truetype("arial.ttf", 19)
        font_small = ImageFont.truetype("ariali.ttf", 17)
    except:
        font_title = ImageFont.load_default()
        font_header = font_title
        font_bold = font_title
        font_normal = font_title
        font_small = font_title

    # Color Palette
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

    # 1. Outer Header Title
    draw.text((100, 60), "UTILITY MANAGEMENT SYSTEM (utilis-app)", fill=COLOR_HEADER_BG, font=font_title)
    draw.text((100, 115), "UML Use Case Diagram Architecture", fill=(37, 99, 235), font=font_header)
    draw.line([100, 160, 2300, 160], fill=COLOR_BOUNDARY_BORDER, width=3)

    # 2. System Boundary Box
    sb_left, sb_top, sb_right, sb_bottom = 440, 210, 1960, 2800
    draw.rectangle([sb_left, sb_top, sb_right, sb_bottom], fill=COLOR_BOUNDARY_BG, outline=COLOR_BOUNDARY_BORDER, width=4)
    
    # Boundary Header Bar
    draw.rectangle([sb_left, sb_top, sb_right, sb_top + 70], fill=COLOR_HEADER_BG)
    draw.text((sb_left + 30, sb_top + 18), "SYSTEM BOUNDARY: UTILITY MANAGEMENT SYSTEM", fill=COLOR_HEADER_TEXT, font=font_header)

    # Helper: Draw Actor Stick Figure
    def draw_actor(x, y, name, role_type="Primary Actor"):
        r = 30
        # Head
        draw.ellipse([x - r, y - r, x + r, y + r], outline=COLOR_ACTOR_HEAD, width=5, fill=(226, 232, 240))
        # Body
        draw.line([x, y + r, x, y + r + 60], fill=COLOR_ACTOR_LINE, width=5)
        # Arms
        draw.line([x - 45, y + r + 22, x + 45, y + r + 22], fill=COLOR_ACTOR_LINE, width=5)
        # Legs
        draw.line([x, y + r + 60, x - 30, y + r + 120], fill=COLOR_ACTOR_LINE, width=5)
        draw.line([x, y + r + 60, x + 30, y + r + 120], fill=COLOR_ACTOR_LINE, width=5)
        
        # Name Box
        bbox = draw.textbbox((0, 0), name, font=font_bold)
        tw = bbox[2] - bbox[0]
        draw.text((x - tw // 2, y + r + 130), name, fill=COLOR_ACTOR_HEAD, font=font_bold)
        
        bbox_sub = draw.textbbox((0, 0), f"({role_type})", font=font_small)
        tw_sub = bbox_sub[2] - bbox_sub[0]
        draw.text((x - tw_sub // 2, y + r + 160), f"({role_type})", fill=(100, 116, 139), font=font_small)

    # Draw Actors
    draw_actor(220, 500, "System Administrator", "Primary Admin")
    draw_actor(220, 1750, "Utility Field Staff", "Field Engineer")
    
    draw_actor(2180, 800, "Utility Customer", "Consumer/User")
    draw_actor(2180, 2100, "External Gateway", "Nodemailer / Payment API")

    # Helper: Draw Use Case Ellipse
    def draw_use_case(x, y, uc_id, uc_name, width_uc=350, height_uc=100):
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
            if draw.textbbox((0,0), test, font=font_normal)[2] > width_uc - 40:
                lines.append(cur_line)
                cur_line = w
            else:
                cur_line = test
        if cur_line:
            lines.append(cur_line)
            
        total_h = len(lines) * 24
        start_y = y - total_h // 2
        for line in lines:
            tb = draw.textbbox((0,0), line, font=font_normal)
            lw = tb[2] - tb[0]
            draw.text((x - lw // 2, start_y), line, fill=COLOR_UC_TEXT, font=font_normal)
            start_y += 24

        return (x, y)

    # Positions inside vertical layout
    uc_pos = {}
    # Left Column (Admin / Field Ops)
    uc_pos["UC01"] = draw_use_case(720, 360, "UC-01", "User Authentication & Profile")
    uc_pos["UC02"] = draw_use_case(720, 560, "UC-02", "Manage Customer Directory")
    uc_pos["UC03"] = draw_use_case(720, 760, "UC-03", "Register Smart Utility Meters")
    uc_pos["UC04"] = draw_use_case(720, 960, "UC-04", "Log Monthly Meter Readings")
    uc_pos["UC05"] = draw_use_case(720, 1160, "UC-05", "Calculate Bills & Apply Tariffs")
    uc_pos["UC06"] = draw_use_case(720, 1360, "UC-06", "Dispatch Email Notifications")
    uc_pos["UC10"] = draw_use_case(720, 1560, "UC-10", "Field Maintenance Dispatch")
    uc_pos["UC12"] = draw_use_case(720, 1760, "UC-12", "Generate Financial Analytics")

    # Right Column (Customer & External API)
    uc_pos["UC07"] = draw_use_case(1680, 500, "UC-07", "View Bills & Account Ledger")
    uc_pos["UC08"] = draw_use_case(1680, 800, "UC-08", "Process Online Payments")
    uc_pos["UC09"] = draw_use_case(1680, 1100, "UC-09", "Submit & Track Support Tickets")
    uc_pos["UC11"] = draw_use_case(1680, 1400, "UC-11", "View GIS Map & Outage Zones")
    uc_pos["UC13"] = draw_use_case(1680, 1700, "UC-13", "Download Digital Receipts")

    # Connect Actors
    def connect(actor_xy, uc_xy):
        draw.line([actor_xy[0], actor_xy[1], uc_xy[0], uc_xy[1]], fill=COLOR_LINE, width=3)

    admin_xy = (330, 500)
    staff_xy = (330, 1750)
    customer_xy = (2070, 800)
    ext_xy = (2070, 2100)

    # Admin connections
    connect(admin_xy, uc_pos["UC01"])
    connect(admin_xy, uc_pos["UC02"])
    connect(admin_xy, uc_pos["UC03"])
    connect(admin_xy, uc_pos["UC05"])
    connect(admin_xy, uc_pos["UC06"])
    connect(admin_xy, uc_pos["UC10"])
    connect(admin_xy, uc_pos["UC12"])

    # Staff connections
    connect(staff_xy, uc_pos["UC01"])
    connect(staff_xy, uc_pos["UC04"])
    connect(staff_xy, uc_pos["UC09"])
    connect(staff_xy, uc_pos["UC10"])
    connect(staff_xy, uc_pos["UC11"])

    # Customer connections
    connect(customer_xy, uc_pos["UC01"])
    connect(customer_xy, uc_pos["UC07"])
    connect(customer_xy, uc_pos["UC08"])
    connect(customer_xy, uc_pos["UC09"])
    connect(customer_xy, uc_pos["UC13"])

    # External Gateway connections
    connect(ext_xy, uc_pos["UC06"])
    connect(ext_xy, uc_pos["UC08"])

    # Dashed relationships
    def draw_dashed(p1, p2, label="<<include>>"):
        x1, y1 = p1
        x2, y2 = p2
        import math
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist == 0: return
        dash_len = 12
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
            draw.line([sx, sy, ex, ey], fill=COLOR_DASH_LINE, width=3)
            
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        tb = draw.textbbox((0,0), label, font=font_small)
        lw = tb[2] - tb[0]
        lh = tb[3] - tb[1]
        draw.rectangle([mx - lw//2 - 6, my - lh//2 - 3, mx + lw//2 + 6, my + lh//2 + 3], fill=(255,255,255), outline=COLOR_DASH_LINE)
        draw.text((mx - lw//2, my - lh//2 - 3), label, fill=COLOR_DASH_LINE, font=font_small)

    draw_dashed(uc_pos["UC05"], uc_pos["UC04"], "<<include>>")
    draw_dashed(uc_pos["UC06"], uc_pos["UC05"], "<<include>>")
    draw_dashed(uc_pos["UC08"], uc_pos["UC07"], "<<include>>")
    draw_dashed(uc_pos["UC13"], uc_pos["UC08"], "<<extend>>")
    draw_dashed(uc_pos["UC10"], uc_pos["UC09"], "<<extend>>")

    # Diagram Legend Box inside Boundary
    leg_x, leg_y = 480, 2620
    draw.rectangle([leg_x, leg_y, leg_x + 750, leg_y + 130], fill=(255, 255, 255), outline=COLOR_BOUNDARY_BORDER, width=2)
    draw.text((leg_x + 20, leg_y + 12), "UML Diagram Notation Legend:", fill=COLOR_HEADER_BG, font=font_bold)
    draw.line([leg_x + 25, leg_y + 60, leg_x + 125, leg_y + 60], fill=COLOR_LINE, width=3)
    draw.text((leg_x + 140, leg_y + 48), "Solid Line: Actor Association / Interaction", fill=COLOR_UC_TEXT, font=font_small)
    draw_dashed((leg_x + 25, leg_y + 98), (leg_x + 145, leg_y + 98), "<<include>>")
    draw.text((leg_x + 165, leg_y + 86), "Dashed Arrow: Use Case Dependency", fill=COLOR_UC_TEXT, font=font_small)

    # Save
    img.save(output_path, "PNG")
    print(f"Portrait diagram saved to: {output_path}")
    return output_path

# ==================== 2. BUILD DOCX & PDF (DIAGRAM ONLY) ====================
def build_diagram_only_docx(docx_path, pdf_path):
    img_path = generate_portrait_use_case_diagram("use_case_diagram_portrait.png")

    doc = docx.Document()

    COLOR_PRIMARY = RGBColor(30, 41, 59)
    COLOR_ACCENT = RGBColor(37, 99, 235)
    COLOR_DARK = RGBColor(51, 65, 85)
    COLOR_GRAY = RGBColor(100, 116, 139)
    COLOR_WHITE = RGBColor(255, 255, 255)

    # Margins (0.75 inch for max printable area)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = COLOR_DARK

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

    # PAGE 1: TITLE & DIAGRAM
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("UTILITY MANAGEMENT SYSTEM (utilis-app)")
    r_t.font.name = 'Times New Roman'
    r_t.font.size = Pt(18)
    r_t.font.bold = True
    r_t.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(8)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s = p_sub.add_run("UML Use Case Diagram Architecture | Student: Jasika Noor (ID: 22CSE002)")
    r_s.font.name = 'Times New Roman'
    r_s.font.size = Pt(12)
    r_s.font.bold = True
    r_s.font.color.rgb = COLOR_ACCENT

    # Diagram Image
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(4)
    p_img.paragraph_format.space_after = Pt(4)
    r_img = p_img.add_run()
    r_img.add_picture(img_path, width=Inches(6.8))

    doc.add_page_break()

    # PAGE 2: DIAGRAM ACTOR & USE CASE LEGEND TABLE
    p_h2 = doc.add_paragraph()
    p_h2.paragraph_format.space_before = Pt(10)
    p_h2.paragraph_format.space_after = Pt(6)
    r_h2 = p_h2.add_run("Use Case Diagram Elements & Actor Summary Legend")
    r_h2.font.name = 'Times New Roman'
    r_h2.font.size = Pt(14)
    r_h2.font.bold = True
    r_h2.font.color.rgb = COLOR_PRIMARY

    # Use Case Table
    uc_table = doc.add_table(rows=14, cols=4)
    format_table(uc_table)
    headers = ["UC ID", "Use Case Name", "Associated Actor(s)", "Core Functionality"]
    for i, h in enumerate(headers):
        uc_table.rows[0].cells[i].paragraphs[0].text = h

    uc_data = [
        ("UC-01", "User Authentication & Profile", "Admin, Field Staff, Customer", "Secure portal login, self-registration, session handling, and profile updates."),
        ("UC-02", "Manage Customer Directory", "System Administrator", "Create, edit, search customer profiles and link service addresses."),
        ("UC-03", "Register Smart Utility Meters", "System Administrator", "Register utility meters (Electricity, Water, Gas) and assign to customers."),
        ("UC-04", "Log Monthly Meter Readings", "Field Staff, Customer", "Log monthly consumption units and calculate delta (currReading - prevReading)."),
        ("UC-05", "Calculate Bills & Apply Tariffs", "System Administrator", "Automated billing engine computing bill amount based on tiered tariffs."),
        ("UC-06", "Dispatch Email Notifications", "Admin, External Nodemailer API", "Automated Nodemailer email dispatch for new invoices and urgent payment reminders."),
        ("UC-07", "View Bills & Account Ledger", "Utility Customer", "Consumer access to unpaid bills, historical ledgers, and payment due dates."),
        ("UC-08", "Process Online Payments", "Customer, External Payment API", "Digital bill payment (bKash, Nagad, Bank) and automated bill status update."),
        ("UC-09", "Submit & Track Support Tickets", "Customer, Field Staff", "Customer complaint filing with interactive comment threads and status updates."),
        ("UC-10", "Field Maintenance Dispatch", "Admin, Field Staff", "Schedule emergency repair work orders, assign field technicians, and log resolutions."),
        ("UC-11", "View GIS Map & Outage Zones", "Field Staff, Admin", "Interactive Leaflet spatial mapping of customer meters and outage fault zones."),
        ("UC-12", "Generate Financial Analytics", "System Administrator", "Executive revenue collection charts, utility breakdown, and financial reports."),
        ("UC-13", "Download Digital Receipts", "Utility Customer", "Generate printable payment receipts featuring unique transaction reference IDs.")
    ]

    for row_idx, data in enumerate(uc_data, start=1):
        row = uc_table.rows[row_idx]
        for col_idx, text in enumerate(data):
            row.cells[col_idx].paragraphs[0].text = text

    # Save DOCX
    doc.save(docx_path)
    print(f"Diagram Only DOCX created: {docx_path}")

    # Convert to PDF
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        abs_docx = os.path.abspath(docx_path)
        abs_pdf = os.path.abspath(pdf_path)
        
        doc_obj = word.Documents.Open(abs_docx)
        doc_obj.SaveAs(abs_pdf, FileFormat=17) # PDF format
        doc_obj.Close()
        word.Quit()
        print(f"Diagram Only PDF created: {pdf_path}")
    except Exception as e:
        print(f"PDF conversion note: {e}")

if __name__ == "__main__":
    out_docx = "Utility_Management_System_Use_Case_Diagram_Only.docx"
    out_pdf = "Utility_Management_System_Use_Case_Diagram_Only.pdf"
    build_diagram_only_docx(out_docx, out_pdf)
