import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import os
import win32com.client
from docx2pdf import convert

def build_utility_srs_docx(output_docx_path):
    doc = docx.Document()

    # Set margins to match original PDF (~0.8 - 1 inch)
    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    # Base font style: Times New Roman
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = RGBColor(0, 0, 0)

    def add_p(text="", bold=False, italic=False, size=11, space_before=0, space_after=4, align=WD_ALIGN_PARAGRAPH.LEFT):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if text:
            run = p.add_run(text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.italic = italic
            run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_bullet(text, bold_prefix="", space_before=0, space_after=3):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.font.name = 'Times New Roman'
            run_b.font.size = Pt(11)
            run_b.font.bold = True
            run_b.font.color.rgb = RGBColor(0, 0, 0)
        run_t = p.add_run(text)
        run_t.font.name = 'Times New Roman'
        run_t.font.size = Pt(11)
        run_t.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def set_cell_border(cell, **kwargs):
        """
        Set cell's border
        Usage: set_cell_border(cell, top={"sz": 4, "val": "single", "color": "000000"})
        """
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

    def style_table(table, col_widths):
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        for row_idx, row in enumerate(table.rows):
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
            for col_idx, cell in enumerate(row.cells):
                cell.width = Inches(col_widths[col_idx])
                set_cell_border(cell,
                                top={"sz": 4, "val": "single", "color": "000000"},
                                bottom={"sz": 4, "val": "single", "color": "000000"},
                                left={"sz": 4, "val": "single", "color": "000000"},
                                right={"sz": 4, "val": "single", "color": "000000"})
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(3)
                    p.paragraph_format.space_after = Pt(3)
                    for run in p.runs:
                        run.font.name = 'Times New Roman'
                        run.font.size = Pt(10.5)
                        if row_idx == 0:
                            run.font.bold = True

    # ================= PAGE 1 =================
    add_p("Software Requirements Specification (SRS)", bold=True, size=12, space_after=4)
    add_p("Utility Management System", bold=True, size=13, space_after=12)

    add_p("Student Name: Farjana Islam Ria", size=11, space_after=3)
    add_p("Student ID: 22CSE022", size=11, space_after=3)
    add_p("Session: 2022-2023", size=11, space_after=3)
    add_p("Course Code: CSE356 | Course Title: Software Engineering Sessional", size=11, space_after=3)
    add_p("Department of Computer Science and Engineering, GSTU", size=11, space_after=3)
    add_p("Submitted To: Dr. Mrinal Kanti Baowaly (Professor, Dept. of CSE)", italic=True, size=11, space_after=14)

    add_heading_1("1. Introduction")

    add_heading_2("1.1 Purpose")
    add_p("The purpose of this Software Requirements Specification (SRS) is to define the functional and non-functional requirements for the Utility Management System (UMS), a web-based platform that allows users to manage utility bills online, track energy and water consumption, record meter readings, and access system analytics and customer support.", space_after=8)

    add_heading_2("1.2 Scope")
    add_p("The Utility Management System is an online application that aims to centralize utility tracking, reduce manual billing errors, and improve customer self-service efficiency. The system includes two primary user roles:", space_after=4)
    add_bullet(" who register to manage utility bills, track consumption, pay invoices, and raise support tickets.", bold_prefix="Customers")
    add_bullet(" who manage overall system health, users, utility rate tariffs, bill generation, and system reports.", bold_prefix="Administrators", space_after=8)

    add_heading_2("1.3 Definitions, Acronyms, and Abbreviations")
    t1 = doc.add_table(rows=6, cols=2)
    headers = ["Term", "Definition"]
    t1_data = [
        ["SRS", "Software Requirements Specification"],
        ["UI", "User Interface"],
        ["UMS", "Utility Management System"],
        ["DB", "Database"],
        ["API", "Application Programming Interface"]
    ]
    for c_idx, h in enumerate(headers):
        p = t1.rows[0].cells[c_idx].paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
    for r_idx, row_data in enumerate(t1_data):
        for c_idx, val in enumerate(row_data):
            p = t1.rows[r_idx+1].cells[c_idx].paragraphs[0]
            p.add_run(val)
    style_table(t1, [1.4, 5.2])

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(6)
    p_space.paragraph_format.space_after = Pt(2)

    add_heading_2("1.4 References")
    add_bullet("IEEE 830 / IEEE 29148 Standard", space_after=4)

    # PAGE BREAK TO PAGE 2
    doc.add_page_break()

    # ================= PAGE 2 =================
    add_bullet("Software Engineering Best Practices", space_after=8)

    add_heading_2("1.5 Overview")
    add_p("This document describes the overall system, functional requirements, interface requirements, and non-functional requirements of the Utility Management System.", space_after=10)

    add_heading_1("2. Overall Description")

    add_heading_2("2.1 Product Perspective")
    add_p("The Utility Management System is a web-based application that integrates a local database with automated tariff billing engines and online payment modules. It acts as an all-in-one digital utility hub.", space_after=8)

    add_heading_2("2.2 Product Functions")
    add_p("The system provides the following major functions:", space_after=4)
    add_bullet("Customer login and secure authentication")
    add_bullet("Bill management (View, calculate, pay, and download PDF invoices)")
    add_bullet("Meter reading & consumption tracking system")
    add_bullet("Customer support & complaint management system")
    add_bullet("Progress tracking (Dashboard/Analytics summary)", space_after=8)

    add_heading_2("2.3 User Classes and Characteristics")
    t2 = doc.add_table(rows=3, cols=2)
    t2_headers = ["User", "Description"]
    t2_data = [
        ["Customer", "Main user. Manages utility bills, tracks consumption trends, submits support requests."],
        ["Administrator", "Manages overall system health, users, tariff rates, and automated bill generation."]
    ]
    for c_idx, h in enumerate(t2_headers):
        p = t2.rows[0].cells[c_idx].paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
    for r_idx, row_data in enumerate(t2_data):
        for c_idx, val in enumerate(row_data):
            p = t2.rows[r_idx+1].cells[c_idx].paragraphs[0]
            p.add_run(val)
    style_table(t2, [1.5, 5.1])

    p_space2 = doc.add_paragraph()
    p_space2.paragraph_format.space_before = Pt(6)
    p_space2.paragraph_format.space_after = Pt(2)

    add_heading_2("2.4 Operating Environment")
    add_p("Web browser (Chrome, Firefox, Edge)", space_after=2)
    add_p("Server OS: Windows / Linux (Node.js / Express).", space_after=2)
    add_p("Database: JSON / SQLite / MySQL", space_after=8)

    add_heading_2("2.5 Design and Implementation Constraints")
    add_bullet("Must have an active internet connection for online payments and real-time updates.")
    add_bullet("Secure login and session management are required.")
    add_bullet("Must support responsive design for different devices.", space_after=8)

    add_heading_2("2.6 User Documentation")
    add_bullet("User manual or tooltips for customers on the UI.", space_after=8)

    add_heading_2("2.7 Assumptions and Dependencies")

    # PAGE BREAK TO PAGE 3
    doc.add_page_break()

    # ================= PAGE 3 =================
    add_bullet("Customers have internet access.")
    add_bullet("Database and payment gateway services remain available and responsive.", space_after=8)

    add_heading_1("3. System Features (Functional Requirements)")

    add_heading_2("3.1 User Authentication")
    add_p("Description", bold=True, space_after=2)
    add_p("The system shall authenticate users to protect their billing data.", space_after=4)
    add_p("Functional Requirements", bold=True, space_after=2)
    add_p("FR-1 The system shall allow users to register and log in using email/username and password.", space_after=2)
    add_p("FR-2 The system shall maintain secure user sessions with logout functionality.", space_after=8)

    add_heading_2("3.2 Bill & Payment Management")
    add_p("Description", bold=True, space_after=2)
    add_p("Customers can manage and pay their monthly utility bills online.", space_after=4)
    add_p("Functional Requirements", bold=True, space_after=2)
    add_p("FR-3 The system shall allow users to view detailed utility bills and download PDF invoices.", space_after=2)
    add_p("FR-4 The system shall allow users to pay bills online and update payment statuses in real time.", space_after=8)

    add_heading_2("3.3 Meter Reading & Consumption Analytics")
    add_p("Description", bold=True, space_after=2)
    add_p("Customers can record meter readings and track monthly usage.", space_after=4)
    add_p("Functional Requirements", bold=True, space_after=2)
    add_p("FR-5 The system shall allow users to record utility meter readings and track daily/monthly usage.", space_after=2)
    add_p("FR-6 The system shall visualize consumption data through interactive summary charts.", space_after=8)

    add_heading_2("3.4 Support & Complaint System")
    add_p("Description", bold=True, space_after=2)
    add_p("Customers can raise support tickets for billing or meter queries.", space_after=4)
    add_p("Functional Requirements", bold=True, space_after=2)
    add_p("FR-7 The system shall connect to a support ticketing service to receive user queries and complaints.", space_after=2)
    add_p("FR-8 The system shall display support responses in a clear, accessible customer portal.", space_after=10)

    add_heading_1("4. External Interface Requirements")

    add_heading_2("4.1 User Interfaces")
    add_bullet("Web-based, responsive graphical interface.", space_after=4)

    # PAGE BREAK TO PAGE 4
    doc.add_page_break()

    # ================= PAGE 4 =================
    add_bullet("Simple and user-friendly layout.", space_after=8)

    add_heading_2("4.2 Hardware Interfaces")
    add_bullet("Standard web server hardware.")
    add_bullet("User devices (PC, laptop, tablet, mobile).", space_after=8)

    add_heading_2("4.3 Software Interfaces")
    add_p("The system shall interface with:", space_after=4)
    add_bullet("Local or Hosted Database System.")
    add_bullet("Payment Gateway API service.", space_after=8)

    add_heading_2("4.4 Communication Interfaces")
    add_p("The platform shall use:", space_after=4)
    add_bullet("HTTP/HTTPS protocol for web requests.", space_after=10)

    add_heading_1("5. Non-Functional Requirements")

    add_heading_2("5.1 Performance Requirements")
    add_bullet("System response time for standard page loads shall be less than 2 seconds.")
    add_bullet("Payment processing and bill calculation should be displayed efficiently.", space_after=8)

    add_heading_2("5.2 Security Requirements")
    add_bullet("Passwords must be securely hashed in the database.")
    add_bullet("User data must be isolated (users can only see their own bills/meter data).", space_after=8)

    add_heading_2("5.3 Reliability Requirements")
    add_bullet("System availability should be 99% during typical operating hours.", space_after=8)

    add_heading_2("5.4 Usability Requirements")
    add_bullet("The platform must be easy to learn for first-time users.")
    add_bullet("Clear error messages (e.g., \"Invalid Login\", \"Payment Failed\", \"DB Error\").", space_after=8)

    add_heading_2("5.5 Portability Requirements")
    add_p("Accessible on different browsers (Chrome, Firefox, Edge) and devices.", space_after=10)

    add_heading_1("6. Other Requirements")
    add_bullet("Compliance with basic data privacy protection.")
    add_bullet("Adherence to utility service terms and regulatory standards.", space_after=8)

    doc.save(output_docx_path)
    print(f"Docx generated at: {output_docx_path}")

if __name__ == "__main__":
    docx_path = r"d:\utility Management system\SRS_Utility_Management_System_4Page.docx"
    downloads_pdf = r"C:\Users\Jasika\Downloads\srs_utility_management_system.pdf"
    workspace_pdf = r"d:\utility Management system\SRS_Utility_Management_System_4Page.pdf"

    build_utility_srs_docx(docx_path)
    
    # Convert docx to pdf
    convert(docx_path, workspace_pdf)
    print(f"Workspace PDF generated at: {workspace_pdf}")
    
    import shutil
    shutil.copy(workspace_pdf, downloads_pdf)
    print(f"Copied to Downloads at: {downloads_pdf}")
