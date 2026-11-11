import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from PIL import Image
import win32com.client

from scratch.generate_book_style_diagrams import (
    generate_use_case_diagram_book_style,
    generate_class_diagram_book_style,
    generate_seq_auth_book_style,
    generate_seq_billing_book_style,
    generate_seq_payment_book_style,
    generate_seq_complaint_book_style
)

def build_complete_diagram_document(docx_path, pdf_path):
    print("Generating ultra-clear high-res diagram images...")
    img_uc = generate_use_case_diagram_book_style("use_case_diagram_book_style.png")
    img_cls = generate_class_diagram_book_style("class_diagram_book_style.png")
    img_seq1 = generate_seq_auth_book_style("seq_diagram_auth_book_style.png")
    img_seq2 = generate_seq_billing_book_style("seq_diagram_billing_book_style.png")
    img_seq3 = generate_seq_payment_book_style("seq_diagram_payment_book_style.png")
    img_seq4 = generate_seq_complaint_book_style("seq_diagram_complaint_book_style.png")

    doc = docx.Document()

    COLOR_PRIMARY = RGBColor(30, 41, 59)     # Deep Slate Navy
    COLOR_ACCENT = RGBColor(37, 99, 235)     # Royal Blue
    COLOR_DARK = RGBColor(51, 65, 85)       # Body text
    COLOR_WHITE = RGBColor(255, 255, 255)

    # Tight 0.5 inch margins so diagrams fill maximum printable area!
    for section in doc.sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)

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

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        return p

    def add_p(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        p.add_run(text)
        return p

    # Ensure Footers are EMPTY on every page!
    for s in doc.sections:
        footer = s.footer
        p_f = footer.paragraphs[0]
        p_f.text = ""

    # ==================== COVER PAGE (DELETED SOFTWARE DESIGN SPECIFICATION UML DIAGRAM PACKAGE) ====================
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(140)
    p_title.paragraph_format.space_after = Pt(14)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("UTILITY MANAGEMENT SYSTEM")
    r_t.font.name = 'Times New Roman'
    r_t.font.size = Pt(26)
    r_t.font.bold = True
    r_t.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(60)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s = p_sub.add_run("Use Case Diagram | Class Diagram | Sequence Diagrams")
    r_s.font.name = 'Times New Roman'
    r_s.font.size = Pt(16)
    r_s.font.bold = True
    r_s.font.color.rgb = COLOR_ACCENT

    # Student Info Section (Clean & Prominent)
    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_info.paragraph_format.space_before = Pt(40)
    p_info.paragraph_format.space_after = Pt(10)
    
    r_n_lbl = p_info.add_run("Name: ")
    r_n_lbl.font.bold = True
    r_n_lbl.font.size = Pt(14)
    r_n_lbl.font.color.rgb = COLOR_PRIMARY
    r_n_val = p_info.add_run("Jasika Noor\n")
    r_n_val.font.size = Pt(14)
    
    r_i_lbl = p_info.add_run("Student ID: ")
    r_i_lbl.font.bold = True
    r_i_lbl.font.size = Pt(14)
    r_i_lbl.font.color.rgb = COLOR_PRIMARY
    r_i_val = p_info.add_run("22CSE002\n")
    r_i_val.font.size = Pt(14)
    
    r_c_lbl = p_info.add_run("Course: ")
    r_c_lbl.font.bold = True
    r_c_lbl.font.size = Pt(13)
    r_c_lbl.font.color.rgb = COLOR_PRIMARY
    r_c_val = p_info.add_run("Software Engineering & System Design\n")
    r_c_val.font.size = Pt(13)

    r_d_lbl = p_info.add_run("Date: ")
    r_d_lbl.font.bold = True
    r_d_lbl.font.size = Pt(13)
    r_d_lbl.font.color.rgb = COLOR_PRIMARY
    r_d_val = p_info.add_run("August 30, 2026")
    r_d_val.font.size = Pt(13)

    doc.add_page_break()

    # ==================== SECTION 1: USE CASE DIAGRAM ====================
    add_h1("1. Use Case Diagram")
    add_p("System boundary and actor interaction model for Utility Management System.")

    p_img1 = doc.add_paragraph()
    p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img1.paragraph_format.space_before = Pt(2)
    p_img1.paragraph_format.space_after = Pt(2)
    p_img1.add_run().add_picture("use_case_diagram_book_style.png", width=Inches(7.4))

    doc.add_page_break()

    # ==================== SECTION 2: CLASS DIAGRAM ====================
    add_h1("2. Class Diagram")
    add_p("Object-oriented static class structure detailing entities, attributes, methods, and multiplicities.")

    p_img2 = doc.add_paragraph()
    p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img2.paragraph_format.space_before = Pt(2)
    p_img2.paragraph_format.space_after = Pt(2)
    p_img2.add_run().add_picture("class_diagram_book_style.png", width=Inches(7.4))

    doc.add_page_break()

    # ==================== SECTION 3: SEQUENCE DIAGRAMS ====================
    add_h1("3. Sequence Diagrams")

    # 3.1 Auth
    add_h1("3.1 User Authentication & Session Creation")
    p_img3 = doc.add_paragraph()
    p_img3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img3.paragraph_format.space_before = Pt(2)
    p_img3.paragraph_format.space_after = Pt(2)
    p_img3.add_run().add_picture("seq_diagram_auth_book_style.png", width=Inches(7.2))

    doc.add_page_break()

    # 3.2 Billing
    add_h1("3.2 Meter Reading & Automated Billing Process")
    p_img4 = doc.add_paragraph()
    p_img4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img4.paragraph_format.space_before = Pt(2)
    p_img4.paragraph_format.space_after = Pt(2)
    p_img4.add_run().add_picture("seq_diagram_billing_book_style.png", width=Inches(7.2))

    doc.add_page_break()

    # 3.3 Payment
    add_h1("3.3 Online Bill Payment & Transaction Settlement")
    p_img5 = doc.add_paragraph()
    p_img5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img5.paragraph_format.space_before = Pt(2)
    p_img5.paragraph_format.space_after = Pt(2)
    p_img5.add_run().add_picture("seq_diagram_payment_book_style.png", width=Inches(7.2))

    doc.add_page_break()

    # 3.4 Complaint & Dispatch
    add_h1("3.4 Support Ticket & Field Maintenance Dispatch")
    p_img6 = doc.add_paragraph()
    p_img6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img6.paragraph_format.space_before = Pt(2)
    p_img6.paragraph_format.space_after = Pt(2)
    p_img6.add_run().add_picture("seq_diagram_complaint_book_style.png", width=Inches(7.2))

    doc.add_page_break()

    # ==================== SECTION 4: DIAGRAM SUMMARY TABLE ====================
    add_h1("4. Software Design Diagrams Inventory & Summary")
    diag_table = doc.add_table(rows=7, cols=4)
    format_table(diag_table)
    headers = ["Diagram Name", "UML Type", "Key Lifelines / Entities", "System Design Purpose"]
    for i, h in enumerate(headers):
        diag_table.rows[0].cells[i].paragraphs[0].text = h

    diag_data = [
        ("Use Case Diagram", "Behavioral", "System Boundary, 4 Actors, 10 Use Cases", "Defines complete system functionality and user access permissions."),
        ("Class Diagram", "Structural", "8 Core Classes (User, Customer, Meter, Bill...)", "Models database entities, relationships, attributes, and methods."),
        ("Sequence Diagram 1", "Interaction", "User, LoginUI, AuthController, UserDB", "Triggers user credential validation and session token generation."),
        ("Sequence Diagram 2", "Interaction", "Staff, BillingUI, BillingEngine, BillingDB", "Executes meter reading delta calculation and invoice creation."),
        ("Sequence Diagram 3", "Interaction", "Customer, PaymentUI, PaymentGateway, UtilisDB", "Processes digital bill settlement and transaction status updates."),
        ("Sequence Diagram 4", "Interaction", "Customer, ComplaintUI, Dispatcher, FieldStaff", "Handles customer support ticketing and field technician assignment.")
    ]

    for row_idx, data in enumerate(diag_data, start=1):
        row_cells = diag_table.rows[row_idx].cells
        for col_idx, text in enumerate(data):
            row_cells[col_idx].paragraphs[0].text = text

    # Save DOCX
    doc.save(docx_path)
    print(f"Ultra-clear Diagram DOCX generated: {docx_path}")

    # Convert to PDF
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        abs_docx = os.path.abspath(docx_path)
        abs_pdf = os.path.abspath(pdf_path)
        
        doc_obj = word.Documents.Open(abs_docx)
        doc_obj.SaveAs(abs_pdf, FileFormat=17) # PDF
        doc_obj.Close()
        word.Quit()
        print(f"Ultra-clear Diagram PDF generated: {pdf_path}")
    except Exception as e:
        print(f"PDF conversion note: {e}")

if __name__ == "__main__":
    out_docx = "Utility_Management_System_All_Diagrams.docx"
    out_pdf = "Utility_Management_System_All_Diagrams.pdf"
    build_complete_diagram_document(out_docx, out_pdf)
