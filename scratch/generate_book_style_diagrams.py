import os
from PIL import Image, ImageDraw, ImageFont

from scratch.test_huge_seq_diagrams import (
    generate_seq_auth_huge,
    generate_seq_billing_huge,
    generate_seq_payment_huge,
    generate_seq_complaint_huge
)

def get_fonts():
    try:
        font_main_title = ImageFont.truetype("arialbd.ttf", 46)
        font_sub_title = ImageFont.truetype("arialbd.ttf", 44)
        font_caption = ImageFont.truetype("arial.ttf", 36)
        font_header = ImageFont.truetype("arialbd.ttf", 38)
        font_bold = ImageFont.truetype("arialbd.ttf", 34)
        font_normal = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except:
        font_main_title = ImageFont.load_default()
        font_sub_title = font_main_title
        font_caption = font_main_title
        font_header = font_main_title
        font_bold = font_main_title
        font_normal = font_main_title
        font_small = font_main_title
    return font_main_title, font_sub_title, font_caption, font_header, font_bold, font_normal, font_small

def draw_clean_top_header(draw, width, height, title_text, caption_text=""):
    font_main_title, font_sub_title, font_caption, font_header, font_bold, font_normal, font_small = get_fonts()
    draw.text((100, 60), title_text, fill=(0, 0, 0), font=font_sub_title)
    if caption_text:
        tb_c = draw.textbbox((0,0), caption_text, font=font_caption)
        tw_c = tb_c[2] - tb_c[0]
        draw.text(((width - tw_c) // 2, height - 90), caption_text, fill=(30, 41, 59), font=font_caption)

# Helper: Draw Actor Stick Figure
def draw_actor(draw, x, y, name, font_bold):
    r = 40
    draw.ellipse([x - r, y - r, x + r, y + r], outline=(0, 0, 0), width=5, fill=(255, 255, 255))
    draw.line([x, y + r, x, y + r + 80], fill=(0, 0, 0), width=5)
    draw.line([x - 55, y + r + 28, x + 55, y + r + 28], fill=(0, 0, 0), width=5)
    draw.line([x, y + r + 80, x - 40, y + r + 140], fill=(0, 0, 0), width=5)
    draw.line([x, y + r + 80, x + 40, y + r + 140], fill=(0, 0, 0), width=5)
    
    tb = draw.textbbox((0, 0), name, font=font_bold)
    tw = tb[2] - tb[0]
    draw.text((x - tw // 2, y + r + 155), name, fill=(0, 0, 0), font=font_bold)

# ==================== 1. USE CASE DIAGRAM ====================
def generate_use_case_diagram_book_style(output_path="use_case_diagram_book_style.png"):
    width, height = 3600, 4200
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    _, font_sub_title, font_caption, font_header, font_bold, font_normal, font_small = get_fonts()

    draw_clean_top_header(draw, width, height, "Use case diagram for utility management system", "Use case diagram for utility management system")

    sb_left, sb_top, sb_right, sb_bottom = 900, 180, 2700, 3950
    draw.rectangle([sb_left, sb_top, sb_right, sb_bottom], fill=(255, 255, 255), outline=(0, 0, 0), width=6)

    draw_actor(draw, 450, 750, "Administrator", font_bold)
    draw_actor(draw, 450, 2450, "Field Staff", font_bold)

    draw_actor(draw, 3150, 1300, "Customer", font_bold)
    draw_actor(draw, 3150, 3000, "Payment / Gateway", font_bold)

    use_cases = [
        ("1. Login & Auth", 450),
        ("2. Maintain Customer Details", 780),
        ("3. Register Utility Meters", 1110),
        ("4. Log Monthly Readings", 1440),
        ("5. Calculate Utility Bills", 1770),
        ("6. Dispatch Email Reminders", 2100),
        ("7. View Bills & Ledger", 2430),
        ("8. Process Online Payment", 2760),
        ("9. Submit Support Ticket", 3090),
        ("10. Field Maintenance Dispatch", 3420),
    ]

    uc_pos = {}
    for text, cy in use_cases:
        cx = 1800
        w_uc, h_uc = 680, 170
        left, top = cx - w_uc // 2, cy - h_uc // 2
        right, bottom = cx + w_uc // 2, cy + h_uc // 2
        
        draw.ellipse([left, top, right, bottom], fill=(255, 255, 255), outline=(0, 0, 0), width=4)
        
        tb = draw.textbbox((0, 0), text, font=font_bold)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]
        draw.text((cx - tw // 2, cy - th // 2), text, fill=(0, 0, 0), font=font_bold)
        uc_pos[text] = (cx, cy)

    admin_xy = (580, 770)
    staff_xy = (580, 2470)
    customer_xy = (3020, 1320)
    ext_xy = (3020, 3020)

    for uc_key in ["1. Login & Auth", "2. Maintain Customer Details", "3. Register Utility Meters", "5. Calculate Utility Bills", "6. Dispatch Email Reminders", "10. Field Maintenance Dispatch"]:
        uc_xy = uc_pos[uc_key]
        draw.line([admin_xy[0], admin_xy[1], uc_xy[0] - 340, uc_xy[1]], fill=(0, 0, 0), width=4)

    for uc_key in ["1. Login & Auth", "4. Log Monthly Readings", "9. Submit Support Ticket", "10. Field Maintenance Dispatch"]:
        uc_xy = uc_pos[uc_key]
        draw.line([staff_xy[0], staff_xy[1], uc_xy[0] - 340, uc_xy[1]], fill=(0, 0, 0), width=4)

    for uc_key in ["1. Login & Auth", "7. View Bills & Ledger", "8. Process Online Payment", "9. Submit Support Ticket"]:
        uc_xy = uc_pos[uc_key]
        draw.line([customer_xy[0], customer_xy[1], uc_xy[0] + 340, uc_xy[1]], fill=(0, 0, 0), width=4)

    for uc_key in ["6. Dispatch Email Reminders", "8. Process Online Payment"]:
        uc_xy = uc_pos[uc_key]
        draw.line([ext_xy[0], ext_xy[1], uc_xy[0] + 340, uc_xy[1]], fill=(0, 0, 0), width=4)

    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Clean Use Case diagram saved: {output_path}")

# ==================== 2. CLASS DIAGRAM ====================
def generate_class_diagram_book_style(output_path="class_diagram_book_style.png"):
    width, height = 4500, 4800
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_main_title = ImageFont.truetype("arialbd.ttf", 46)
        font_sub_title = ImageFont.truetype("arialbd.ttf", 44)
        font_caption = ImageFont.truetype("arial.ttf", 36)
        font_cls_title = ImageFont.truetype("arialbd.ttf", 44)
        font_cls_body = ImageFont.truetype("arial.ttf", 32)
    except:
        font_main_title = ImageFont.load_default()
        font_sub_title = font_main_title
        font_caption = font_main_title
        font_cls_title = font_main_title
        font_cls_body = font_main_title

    draw_clean_top_header(draw, width, height, "Class diagram of entity classes", "Class diagram of entity classes")

    def draw_class_box(x, y, w, title, attributes, methods):
        line_h = 50
        h_title = 75
        h_attr = len(attributes) * line_h + 25
        h_meth = len(methods) * line_h + 25
        total_h = h_title + h_attr + h_meth
        
        draw.rectangle([x, y, x + w, y + total_h], fill=(255, 255, 255), outline=(0, 0, 0), width=4)
        draw.line([x, y + h_title, x + w, y + h_title], fill=(0, 0, 0), width=4)
        draw.line([x, y + h_title + h_attr, x + w, y + h_title + h_attr], fill=(0, 0, 0), width=4)
        
        tb = draw.textbbox((0,0), title, font=font_cls_title)
        tw = tb[2] - tb[0]
        draw.text((x + (w - tw) // 2, y + 14), title, fill=(0, 0, 0), font=font_cls_title)
        
        cur_y = y + h_title + 14
        for attr in attributes:
            text_str = f"•  {attr}"
            draw.text((x + 25, cur_y), text_str, fill=(0, 0, 0), font=font_cls_body)
            cur_y += line_h
            
        cur_y = y + h_title + h_attr + 14
        for meth in methods:
            text_str = f"•  {meth}"
            draw.text((x + 25, cur_y), text_str, fill=(0, 0, 0), font=font_cls_body)
            cur_y += line_h

        return {
            "x": x, "y": y, "w": w, "h": total_h,
            "top": y, "bottom": y + total_h,
            "left": x, "right": x + w,
            "cx": x + w // 2, "cy": y + total_h // 2
        }

    user_box  = draw_class_box(200, 200, 850, "User Details", 
                               ["User Id", "User Name", "Password", "User Role"], 
                               ["Add()", "Delete()", "Update()"])

    cust_box  = draw_class_box(1350, 200, 920, "Customer Details", 
                               ["Customer Barcode Id", "Customer Roll No", "Name", "Service Address", "Phone Number"], 
                               ["Get Customer Details()", "Add Customer()", "Delete Customer()", "Update Customer()"])

    admin_box = draw_class_box(2550, 200, 850, "Administrator Details", 
                               ["Admin Id", "Department", "Email Access"], 
                               ["Manage Customers()", "Generate Bills()", "Assign Staff()"])

    staff_box = draw_class_box(3600, 200, 800, "Field Staff Details", 
                               ["Staff Id", "Designation", "Zone Code"], 
                               ["Log Readings()", "Resolve Complaints()"])

    meter_box   = draw_class_box(200, 1650, 880, "Meter Details", 
                                 ["Meter Id", "Serial Number", "Utility Type", "Meter Status"], 
                                 ["Get Consumption()", "Update Status()", "Assign Customer()"])

    reading_box = draw_class_box(1350, 1650, 920, "Meter Reading Details", 
                                 ["Reading Id", "Meter Serial No", "Current Reading", "Previous Reading", "Units Consumed"], 
                                 ["Calculate Delta()", "Validate Reading()"])

    bill_box    = draw_class_box(2550, 1650, 840, "Bill Details", 
                                 ["Bill Invoice Id", "Billing Month", "Amount Due", "Due Date", "Payment Status"], 
                                 ["Calculate Amount()", "Update Status()", "Send Reminder()"])

    pay_box     = draw_class_box(3600, 1650, 800, "Payment Details", 
                                 ["Payment Id", "Invoice Id", "Amount Paid", "Payment Channel", "Transaction Id"], 
                                 ["Process Payment()", "Generate Receipt()"])

    ticket_box = draw_class_box(850, 3150, 1000, "Support Ticket Details", 
                                ["Ticket Reference Id", "Customer Barcode Id", "Complaint Subject", "Ticket Status"], 
                                ["Add Comment()", "Update Status()", "Dispatch Technician()"])

    maint_box  = draw_class_box(2550, 3150, 1000, "Maintenance Work Details", 
                                ["Work Order Id", "Ticket Reference Id", "Assigned Staff Id", "Issue Description"], 
                                ["Update Progress()", "Complete Work Order()"])

    def draw_orthogonal_line(pts, dashed=False):
        for i in range(len(pts) - 1):
            p1 = pts[i]
            p2 = pts[i+1]
            if dashed:
                step = 16
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                dist = (dx**2 + dy**2)**0.5
                if dist == 0: continue
                ux, uy = dx / dist, dy / dist
                curr = 0
                while curr < dist:
                    next_pt = min(curr + 10, dist)
                    sx, sy = p1[0] + ux * curr, p1[1] + uy * curr
                    ex, ey = p1[0] + ux * next_pt, p1[1] + uy * next_pt
                    draw.line([sx, sy, ex, ey], fill=(0,0,0), width=4)
                    curr += step
            else:
                draw.line([p1[0], p1[1], p2[0], p2[1]], fill=(0,0,0), width=4)

    draw_orthogonal_line([(user_box["right"], 440), (cust_box["left"], 440)])
    draw_orthogonal_line([(1500, cust_box["bottom"]), (1500, 1150), (640, 1150), (640, meter_box["top"])], dashed=True)
    draw_orthogonal_line([(meter_box["right"], 1900), (reading_box["left"], 1900)])
    draw_orthogonal_line([(2100, cust_box["bottom"]), (2100, 1350), (2975, 1350), (2975, bill_box["top"])])
    draw_orthogonal_line([(bill_box["right"], 1900), (pay_box["left"], 1900)])
    draw_orthogonal_line([(1800, cust_box["bottom"]), (1800, 1250), (1215, 1250), (1215, ticket_box["top"])], dashed=True)
    draw_orthogonal_line([(ticket_box["right"], 3400), (maint_box["left"], 3400)])
    draw_orthogonal_line([(4000, staff_box["bottom"]), (4000, 1050), (3500, 1050), (3500, maint_box["top"])])

    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Fixed Class diagram saved to: {output_path}")

# ==================== 3. ULTRA HUGE SEQUENCE DIAGRAMS ====================
def generate_seq_auth_book_style(output_path="seq_diagram_auth_book_style.png"):
    generate_seq_auth_huge()

def generate_seq_billing_book_style(output_path="seq_diagram_billing_book_style.png"):
    generate_seq_billing_huge()

def generate_seq_payment_book_style(output_path="seq_diagram_payment_book_style.png"):
    generate_seq_payment_huge()

def generate_seq_complaint_book_style(output_path="seq_diagram_complaint_book_style.png"):
    generate_seq_complaint_huge()

if __name__ == "__main__":
    generate_use_case_diagram_book_style()
    generate_class_diagram_book_style()
    generate_seq_auth_book_style()
    generate_seq_billing_book_style()
    generate_seq_payment_book_style()
    generate_seq_complaint_book_style()
