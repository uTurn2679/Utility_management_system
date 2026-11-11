import os
from PIL import Image, ImageDraw, ImageFont

def generate_no_overlap_class_diagram(output_path="class_diagram_book_style.png"):
    width, height = 4500, 4800
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_main_title = ImageFont.truetype("georgiai.ttf", 80)
        font_sub_title = ImageFont.truetype("arialbd.ttf", 44)
        font_caption = ImageFont.truetype("arial.ttf", 36)
        font_cls_title = ImageFont.truetype("arialbd.ttf", 44)   # Class Title
        font_cls_body = ImageFont.truetype("arial.ttf", 32)      # Textbook font with bullet points
        font_cls_bold = ImageFont.truetype("arialbd.ttf", 32)
    except:
        font_main_title = ImageFont.load_default()
        font_sub_title = font_main_title
        font_caption = font_main_title
        font_cls_title = font_main_title
        font_cls_body = font_main_title
        font_cls_bold = font_main_title

    # Header "Software Design"
    tb_t = draw.textbbox((0,0), "Software Design", font=font_main_title)
    tw_t = tb_t[2] - tb_t[0]
    draw.text(((width - tw_t) // 2, 45), "Software Design", fill=(30, 58, 138), font=font_main_title)
    draw.line([100, 145, width - 100, 145], fill=(220, 38, 38), width=8)

    # Subtitle top left
    draw.text((120, 175), "Class diagram of entity classes", fill=(0, 0, 0), font=font_sub_title)

    # Bottom Caption
    caption_text = "Class diagram of entity classes"
    tb_c = draw.textbbox((0,0), caption_text, font=font_caption)
    tw_c = tb_c[2] - tb_c[0]
    draw.text(((width - tw_c) // 2, height - 90), caption_text, fill=(30, 41, 59), font=font_caption)

    # Helper: Draw 3-Compartment Class Box
    def draw_class_box(x, y, w, title, attributes, methods):
        line_h = 50
        h_title = 75
        h_attr = len(attributes) * line_h + 25
        h_meth = len(methods) * line_h + 25
        total_h = h_title + h_attr + h_meth
        
        # Outer box (Clean 4px line)
        draw.rectangle([x, y, x + w, y + total_h], fill=(255, 255, 255), outline=(0, 0, 0), width=4)
        # Title separator line
        draw.line([x, y + h_title, x + w, y + h_title], fill=(0, 0, 0), width=4)
        # Methods separator line
        draw.line([x, y + h_title + h_attr, x + w, y + h_title + h_attr], fill=(0, 0, 0), width=4)
        
        # Title Text (Centered Bold)
        tb = draw.textbbox((0,0), title, font=font_cls_title)
        tw = tb[2] - tb[0]
        draw.text((x + (w - tw) // 2, y + 14), title, fill=(0, 0, 0), font=font_cls_title)
        
        # Attributes with Bullet points (•)
        cur_y = y + h_title + 14
        for attr in attributes:
            text_str = f"•  {attr}"
            draw.text((x + 25, cur_y), text_str, fill=(0, 0, 0), font=font_cls_body)
            cur_y += line_h
            
        # Methods with Bullet points (•)
        cur_y = y + h_title + h_attr + 14
        for meth in methods:
            text_str = f"•  {meth}"
            draw.text((x + 25, cur_y), text_str, fill=(0, 0, 0), font=font_cls_body)
            cur_y += line_h

        return (x, y, w, total_h)

    # Grid Placement (Clean 3-Row Layout)
    # Row 1 (y = 260)
    # Box 1: User (200..1050)
    box_user = draw_class_box(200, 260, 850, "User Details", 
                             ["User Id", "User Name", "Password", "User Role"], 
                             ["Add()", "Delete()", "Update()"])

    # Box 2: Customer (1350..2270)
    box_cust = draw_class_box(1350, 260, 920, "Customer Details", 
                             ["Customer Barcode Id", "Customer Roll No", "Name", "Service Address", "Phone Number"], 
                             ["Get Customer Details()", "Add Customer()", "Delete Customer()", "Update Customer()"])

    # Box 3: Administrator (2550..3400)
    box_admin = draw_class_box(2550, 260, 850, "Administrator Details", 
                              ["Admin Id", "Department", "Email Access"], 
                              ["Manage Customers()", "Generate Bills()", "Assign Staff()"])

    # Box 4: FieldStaff (3600..4400)
    box_staff = draw_class_box(3600, 260, 800, "Field Staff Details", 
                              ["Staff Id", "Designation", "Zone Code"], 
                              ["Log Readings()", "Resolve Complaints()"])

    # Row 2 (y = 1700)
    # Box 1: Meter (200..1080)
    box_meter = draw_class_box(200, 1700, 880, "Meter Details", 
                              ["Meter Id", "Serial Number", "Utility Type", "Meter Status"], 
                              ["Get Consumption()", "Update Status()", "Assign Customer()"])

    # Box 2: MeterReading (1350..2270)
    box_reading = draw_class_box(1350, 1700, 920, "Meter Reading Details", 
                                ["Reading Id", "Meter Serial No", "Current Reading", "Previous Reading", "Units Consumed"], 
                                ["Calculate Delta()", "Validate Reading()"])

    # Box 3: Bill (2550..3390)
    box_bill = draw_class_box(2550, 1700, 840, "Bill Details", 
                             ["Bill Invoice Id", "Billing Month", "Amount Due", "Due Date", "Payment Status"], 
                             ["Calculate Amount()", "Update Status()", "Send Reminder()"])

    # Box 4: Payment (3600..4400)
    box_pay = draw_class_box(3600, 1700, 800, "Payment Details", 
                            ["Payment Id", "Invoice Id", "Amount Paid", "Payment Channel", "Transaction Id"], 
                            ["Process Payment()", "Generate Receipt()"])

    # Row 3 (y = 3200)
    # Box 1: Support Ticket (850..1850)
    box_ticket = draw_class_box(850, 3200, 1000, "Support Ticket Details", 
                               ["Ticket Reference Id", "Customer Barcode Id", "Complaint Subject", "Ticket Status"], 
                               ["Add Comment()", "Update Status()", "Dispatch Technician()"])

    # Box 2: Maintenance Work Details (2550..3550)
    box_maint = draw_class_box(2550, 3200, 1000, "Maintenance Work Details", 
                              ["Work Order Id", "Ticket Reference Id", "Assigned Staff Id", "Issue Description"], 
                              ["Update Progress()", "Complete Work Order()"])

    # Helper: Draw STRICT ORTHOGONAL Lines (Only Horizontal and Vertical segments)
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

    # ZERO-BOX-INTERSECTION ROUTING:
    
    # 1. User Details (1050, 500) --- Customer Details (1350, 500) [Channel 1]
    draw_orthogonal_line([(1050, 500), (1350, 500)])

    # 2. Customer Details (1500, 750) --- Meter Details (640, 1700) [Gutter 1]
    draw_orthogonal_line([(1500, 750), (1500, 1200), (640, 1200), (640, 1700)], dashed=True)

    # 3. Meter Details (1080, 2050) --- Meter Reading Details (1350, 2050) [Channel 1]
    draw_orthogonal_line([(1080, 2050), (1350, 2050)])

    # 4. Customer Details (2100, 750) --- Bill Details (2975, 1700) [Gutter 1]
    draw_orthogonal_line([(2100, 750), (2100, 1350), (2975, 1350), (2975, 1700)])

    # 5. Bill Details (3390, 2050) --- Payment Details (3600, 2050) [Channel 3]
    draw_orthogonal_line([(3390, 2050), (3600, 2050)])

    # 6. Customer Details (1650, 750) --- Support Ticket Details (1350, 3200) [Channel 1]
    draw_orthogonal_line([(1650, 750), (1650, 1100), (1215, 1100), (1215, 3200)], dashed=True)

    # 7. Support Ticket Details (1850, 3450) --- Maintenance Work Details (2550, 3450) [Channel between Tickets]
    draw_orthogonal_line([(1850, 3450), (2550, 3450)])

    # 8. Field Staff Details (4000, 650) --- Maintenance Work Details (3050, 3200) [Channel 3]
    draw_orthogonal_line([(4000, 650), (4000, 1100), (3500, 1100), (3500, 3200)])

    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Zero box intersection Class diagram created: {output_path}")

if __name__ == "__main__":
    generate_no_overlap_class_diagram()
