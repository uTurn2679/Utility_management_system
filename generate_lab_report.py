import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Lab Report: Software Project Scheduling")
            self.drawRightString(612 - 54, 750, "Jasika Noor | 22CSE002")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 612 - 54, 742)
            
        # Footer (All pages)
        self.drawString(612 - 110, 36, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def create_report(output_filename):
    # Page setup: Letter size is 612 x 792 pt. Margins 54pt (0.75in) left/right, top 54pt, bottom 54pt.
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1E293B"),
        alignment=1, # Center
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#475569"),
        alignment=1, # Center
        spaceAfter=14
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        alignment=1, # Center
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1E293B")
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0F172A")
    )

    gantt_cell_style = ParagraphStyle(
        'GanttCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=1
    )

    story = []

    # Title Block
    story.append(Spacer(1, 10))
    story.append(Paragraph("Lab Report", title_style))
    story.append(Paragraph("Software Project Scheduling", subtitle_style))
    story.append(Paragraph("<b>Project:</b> Utility Management System<br/><b>Prepared By:</b> Jasika Noor | <b>ID:</b> 22CSE002 | <b>Session:</b> 2022-2023 | <b>Course:</b> Software Engineering (Lab)<br/><b>Submission Date:</b> August 23, 2026", meta_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=14))

    # 1. Introduction
    story.append(Paragraph("1. Introduction", h1_style))
    story.append(Paragraph(
        "This lab report applies software project scheduling principles to the <b>Utility Management System</b> project. "
        "The Utility Management System is an integrated, enterprise-grade web application designed to streamline "
        "multi-utility operations including electricity, water, and gas monitoring, automated meter reading, dynamic billing engine, "
        "online payment processing, GIS spatial mapping of infrastructure, outage/maintenance management, and customer complaint resolution. "
        "Proper project scheduling ensures that high-risk modules (such as real-time meter ingestion and billing calculation engines) are "
        "systematically planned, resource-allocated, and executed within a 15-week academic semester timeline using Work Breakdown Structure (WBS), "
        "PERT estimation, and Critical Path Analysis.",
        body_style
    ))

    # 2. Steps in Software Project Scheduling
    story.append(Paragraph("2. Steps in Software Project Scheduling (Applied to This Project)", h1_style))
    
    story.append(Paragraph("Step 1: Define Scope and Objectives", h2_style))
    story.append(Paragraph(
        "Develop an end-to-end Utility Management System that automates utility meter tracking (electricity, water, gas), generates monthly invoices "
        "with tiered pricing structures, supports online payment gateways, maps utility grids via GIS, tracks infrastructure maintenance/outages, "
        "and handles customer tickets with real-time reporting.",
        body_style
    ))

    story.append(Paragraph("Step 2: Create Work Breakdown Structure (WBS)", h2_style))
    story.append(Paragraph(
        "Decompose the project into 6 core phases: Requirement Analysis & Systems Architecture, Database Schema & Security Design, "
        "Core Backend Services & Meter Integration, Frontend UI & Dashboard Development, GIS & Payment Gateway Integration, "
        "and System Testing, Security Audit & Cloud Deployment.",
        body_style
    ))

    story.append(Paragraph("Step 3: Identify Task Dependencies", h2_style))
    story.append(Paragraph(
        "Establish logical task precedence — e.g., Automated Billing Engine relies on Database Schema & Meter Data models, "
        "Payment Gateway Integration depends on Billing API completion, and System Security Testing depends on complete frontend/backend integration.",
        body_style
    ))

    story.append(Paragraph("Step 4: Estimate Task Duration", h2_style))
    story.append(Paragraph(
        "Apply expert judgment and PERT 3-point estimation (Optimistic, Most Likely, Pessimistic) for complex, high-uncertainty tasks "
        "such as meter data ingestion algorithms, real-time consumption anomaly detection, and payment gateway webhooks.",
        body_style
    ))

    story.append(Paragraph("Step 5: Assign Resources", h2_style))
    story.append(Paragraph(
        "Allocate core specialized roles across the project timeline: Project Manager, Full-Stack / Backend Developer, Frontend UI/UX Developer, "
        "Database Administrator, GIS Specialist, QA/Security Tester, and DevOps Engineer.",
        body_style
    ))

    story.append(Paragraph("Step 6: Develop Schedule", h2_style))
    story.append(Paragraph(
        "Construct a detailed Gantt chart aligning tasks with a 15-week academic semester timeline, ensuring parallel execution of decoupled frontend "
        "and backend modules.",
        body_style
    ))

    story.append(Paragraph("Step 7: Monitor and Control", h2_style))
    story.append(Paragraph(
        "Track weekly milestone progress against planned duration, monitor API response latency, run regression tests, and adjust schedules "
        "if third-party integrations (e.g., payment gateway APIs) experience delays.",
        body_style
    ))

    story.append(Spacer(1, 10))

    # 3. Work Breakdown Structure (WBS)
    story.append(Paragraph("3. Work Breakdown Structure (WBS)", h1_style))
    
    wbs_data = [
        [Paragraph("Phase", table_header_style), Paragraph("Tasks", table_header_style)],
        [Paragraph("Planning", table_cell_bold), Paragraph("Feasibility study, stakeholder requirement gathering, utility domain analysis, SRS documentation", table_cell_style)],
        [Paragraph("Design", table_cell_bold), Paragraph("System architecture, relational database schema (meters, bills, payments, customers, GIS), UI mockups", table_cell_style)],
        [Paragraph("Development", table_cell_bold), Paragraph("Database setup, REST APIs (Meters, Bills, Payments, Complaints, Maintenance), Auth & Access Control", table_cell_style)],
        [Paragraph("Integration", table_cell_bold), Paragraph("GIS spatial mapping integration, automated billing calculation engine, payment gateway API integration", table_cell_style)],
        [Paragraph("Testing", table_cell_bold), Paragraph("Unit & integration testing, billing calculation accuracy verification, security audit, load testing", table_cell_style)],
        [Paragraph("Deployment", table_cell_bold), Paragraph("Server configuration, database migration, production build deployment, user manual & handover", table_cell_style)],
    ]
    
    t_wbs = Table(wbs_data, colWidths=[110, 394])
    t_wbs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_wbs)
    story.append(Spacer(1, 12))

    # 4. Task Duration and Dependencies
    story.append(Paragraph("4. Task Duration and Dependencies", h1_style))
    
    dep_data = [
        [Paragraph("Task", table_header_style), Paragraph("Duration", table_header_style), Paragraph("Dependency", table_header_style)],
        [Paragraph("Requirement Analysis & SRS", table_cell_style), Paragraph("3 weeks", table_cell_style), Paragraph("—", table_cell_style)],
        [Paragraph("Database & Architecture Design", table_cell_style), Paragraph("2 weeks", table_cell_style), Paragraph("Requirement Analysis", table_cell_style)],
        [Paragraph("Core Backend & Meter APIs", table_cell_style), Paragraph("4 weeks", table_cell_style), Paragraph("Database & Architecture Design", table_cell_style)],
        [Paragraph("Billing & Payment Integration", table_cell_style), Paragraph("3 weeks", table_cell_style), Paragraph("Core Backend & Meter APIs", table_cell_style)],
        [Paragraph("Frontend UI & GIS Integration", table_cell_style), Paragraph("3 weeks", table_cell_style), Paragraph("Core Backend & Meter APIs", table_cell_style)],
        [Paragraph("Testing & Security Audit", table_cell_style), Paragraph("2 weeks", table_cell_style), Paragraph("Billing, Payment & Frontend Integration", table_cell_style)],
        [Paragraph("Deployment & Documentation", table_cell_style), Paragraph("1 week", table_cell_style), Paragraph("Testing & Security Audit", table_cell_style)],
    ]

    t_dep = Table(dep_data, colWidths=[200, 90, 214])
    t_dep.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_dep)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Total estimated project duration: 15 weeks</b> (approx. one academic semester), utilizing parallel execution paths for frontend UI/GIS and billing engine integration.",
        body_style
    ))
    story.append(Spacer(1, 12))

    # 5. Gantt Chart (Textual)
    story.append(Paragraph("5. Gantt Chart (Textual)", h1_style))
    
    gantt_headers = [Paragraph("Task", table_header_style)] + [Paragraph(f"W{i}", table_header_style) for i in range(1, 16)]
    
    # Task active weeks: 
    # Req: W1-3
    # Design: W4-5
    # Backend: W6-9
    # Billing/Payment: W10-12
    # Frontend/GIS: W10-12
    # Testing: W13-14
    # Deploy: W15
    gantt_rows = [
        ("Requirements & SRS", [1, 2, 3]),
        ("Architecture & DB Design", [4, 5]),
        ("Core Backend & Meter APIs", [6, 7, 8, 9]),
        ("Billing & Payment Engine", [10, 11, 12]),
        ("Frontend UI & GIS Integration", [10, 11, 12]),
        ("Testing & Security Audit", [13, 14]),
        ("Deployment & Handover", [15])
    ]

    gantt_data = [gantt_headers]
    for task_name, active_weeks in gantt_rows:
        row = [Paragraph(task_name, table_cell_style)]
        for w in range(1, 16):
            if w in active_weeks:
                row.append(Paragraph("■", gantt_cell_style))
            else:
                row.append(Paragraph("", gantt_cell_style))
        gantt_data.append(row)

    col_widths = [170] + [22] * 15
    t_gantt = Table(gantt_data, colWidths=col_widths)
    t_gantt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_gantt)
    story.append(Spacer(1, 12))

    # 6. PERT Estimation Example
    story.append(Paragraph("6. PERT Estimation Example", h1_style))
    story.append(Paragraph(
        "Program Evaluation and Review Technique (PERT) is used to calculate Expected Task Duration (TE) under uncertainty using the formula "
        "<b>TE = (O + 4M + P) / 6</b>, where <b>O</b> = Optimistic time, <b>M</b> = Most Likely time, and <b>P</b> = Pessimistic time. "
        "This technique is applied to key complex tasks in the Utility Management System:",
        body_style
    ))

    pert_data = [
        [Paragraph("Task", table_header_style), Paragraph("O (days)", table_header_style), Paragraph("M (days)", table_header_style), Paragraph("P (days)", table_header_style), Paragraph("TE (days)", table_header_style)],
        [Paragraph("Smart Meter Data Ingestion Pipeline Tuning", table_cell_style), Paragraph("4", table_cell_style), Paragraph("7", table_cell_style), Paragraph("14", table_cell_style), Paragraph("7.7", table_cell_style)],
        [Paragraph("Automated Tiered Billing & Invoice Calculation Engine", table_cell_style), Paragraph("3", table_cell_style), Paragraph("6", table_cell_style), Paragraph("12", table_cell_style), Paragraph("6.5", table_cell_style)],
        [Paragraph("GIS Spatial Map Layering & Utility Outage Tracking", table_cell_style), Paragraph("3", table_cell_style), Paragraph("5", table_cell_style), Paragraph("10", table_cell_style), Paragraph("5.5", table_cell_style)],
        [Paragraph("Payment Gateway Webhooks & Reconciliation Engine", table_cell_style), Paragraph("2", table_cell_style), Paragraph("4", table_cell_style), Paragraph("9", table_cell_style), Paragraph("4.5", table_cell_style)]
    ]

    t_pert = Table(pert_data, colWidths=[200, 75, 75, 75, 79])
    t_pert.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_pert)
    story.append(Spacer(1, 12))

    # 7. Critical Path Analysis
    story.append(Paragraph("7. Critical Path Analysis", h1_style))
    story.append(Paragraph(
        "<b>Critical Path:</b> Requirement Analysis & SRS → Database & Architecture Design → Core Backend & Meter APIs → Billing & Payment Engine → Testing & Security Audit → Deployment & Handover",
        body_style
    ))
    story.append(Paragraph(
        "<b>Total Critical Duration: 15 weeks.</b> The critical path represents the longest sequential sequence of dependent tasks. "
        "Any delay in core backend development or billing engine validation will directly push back the final deployment date of the Utility Management System.",
        body_style
    ))
    story.append(Spacer(1, 12))

    # 8. Resource Allocation
    story.append(Paragraph("8. Resource Allocation", h1_style))
    
    resource_data = [
        [Paragraph("Role", table_header_style), Paragraph("Responsibility", table_header_style)],
        [Paragraph("Project Manager", table_cell_bold), Paragraph("Project planning, scheduling, risk mitigation, stakeholder reporting, and milestone tracking.", table_cell_style)],
        [Paragraph("Backend / DB Developer", table_cell_bold), Paragraph("Database schema design, RESTful API implementation, authentication, and core business logic.", table_cell_style)],
        [Paragraph("Frontend / UX Developer", table_cell_bold), Paragraph("Responsive web interface, admin dashboard, customer billing portal, and meter charts.", table_cell_style)],
        [Paragraph("GIS Specialist", table_cell_bold), Paragraph("Spatial map integration, utility grid layout rendering, and outage zone mapping.", table_cell_style)],
        [Paragraph("QA / Security Tester", table_cell_bold), Paragraph("Automated unit/integration testing, security audit, payment transaction validation, and load testing.", table_cell_style)],
        [Paragraph("DevOps / SysAdmin", table_cell_bold), Paragraph("Cloud infrastructure deployment, CI/CD pipeline setup, database backups, and SSL/TLS security.", table_cell_style)],
    ]

    t_res = Table(resource_data, colWidths=[130, 374])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_res)
    story.append(Spacer(1, 12))

    # 9. Risks and Mitigation
    story.append(Paragraph("9. Risks and Mitigation", h1_style))
    
    risk_data = [
        [Paragraph("Risk", table_header_style), Paragraph("Mitigation Strategy", table_header_style)],
        [Paragraph("Meter Data Ingestion Latency / Packet Loss", table_cell_bold), Paragraph("Implement asynchronous message queue (e.g., RabbitMQ/Kafka) and local caching for meter readings.", table_cell_style)],
        [Paragraph("Billing Calculation Inaccuracies under Tiered Tariffs", table_cell_bold), Paragraph("Develop rigorous automated unit test suites verifying tier transitions and currency rounding edge cases.", table_cell_style)],
        [Paragraph("Payment Gateway Timeout / Webhook Failure", table_cell_bold), Paragraph("Implement idempotent webhook handlers, automated retry mechanisms, and background reconciliation jobs.", table_cell_style)],
        [Paragraph("Unauthorized Access to Utility Grid / Customer Data", table_cell_bold), Paragraph("Enforce Role-Based Access Control (RBAC), API rate limiting, TLS 1.3 encryption, and OWASP security practices.", table_cell_style)]
    ]

    t_risk = Table(risk_data, colWidths=[180, 324])
    t_risk.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_risk)
    story.append(Spacer(1, 14))

    # 10. Conclusion
    story.append(Paragraph("10. Conclusion", h1_style))
    story.append(Paragraph(
        "Applying the structured software project scheduling methodology to the <b>Utility Management System</b> ensures a disciplined, transparent, "
        "and achievable 15-week delivery roadmap. By leveraging Work Breakdown Structure (WBS), 3-point PERT estimation, and Critical Path Analysis, "
        "the project team can systematically mitigate risks, optimize resource utilization, and guarantee high system reliability from requirements gathering "
        "through final deployment.",
        body_style
    ))
    story.append(Spacer(1, 15))
    story.append(Paragraph("— <i>End of Report</i> —", ParagraphStyle('EndReport', parent=body_style, alignment=1, textColor=colors.HexColor("#64748B"))))

    # Build document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {output_filename}")

if __name__ == "__main__":
    out_path = r"d:\utility Management system\22CSE002_Lab_Report_Utility_Management_System.pdf"
    downloads_path = r"C:\Users\Jasika\Downloads\22CSE002.pdf"
    
    create_report(out_path)
    create_report(downloads_path)
