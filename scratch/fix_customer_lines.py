import os
from PIL import Image, ImageDraw, ImageFont

def generate_fixed_class_diagram(output_path="class_diagram_book_style.png"):
    width, height = 4500, 4800
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_main_title = ImageFont.truetype("georgiai.ttf", 80)
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

    # Header & Subtitle
    draw_t_b = draw.textbbox((0,0), "Software Design", font=font_main_title)
    tw_t = draw_t_b[2] - draw_t_b[0]
    draw.text(((width - tw_t) // 2, 45), "Software Design", fill=(30, 58, 138), font=font_main_title)
    draw.line([100, 145, width - 100, 145], fill=(220, 38, 38), width=8)

    draw.text((120, 175), "Class diagram of entity classes", fill=(0, 0, 0), font=font_sub_title)

    caption_text = "Class diagram of entity classes"
    tb_c = draw.textbbox((0,0), caption_text, font=font_caption)
    tw_c = tb_c[2] - tb_c[0]
    draw.text(((width - tw_c) // 2, height - 90), caption_text, fill=(30, 41, 59), font=font_caption)

    # Helper: Draw 3-Compartment Class Box and return exact bounding box dictionary!
    def draw_class_box(x, y, w, title, attributes, methods):
        line_h = 50
        h_title = 75
        h_attr = len(attributes) * line_h + 25
        h_meth = len(methods) * line_h + 25
        total_h = h_title + h_attr + h_meth
        
        # Outer box (Clean 4px line)
        draw.rectangle([x, y, x + w, y + total_h], fill=(255, 255, 255), outline=(0, 0, 0), width=4)
        # Separator line 1
        draw.line([x, y + h_title, x + w, y + h_title], fill=(0, 0, 0), width=4)
        # Separator line 2
        draw.line([x, y + h_title + h_attr, x + w, y + h_title + h_attr], fill=(0, 0, 0), width=4)
        
        # Title Text
        tb = draw.textbbox((0,0), title, font=font_cls_title)
        tw = tb[2] - tb[0]
        draw.text((x + (w - tw) // 2, y + 14), title, fill=(0, 0, 0), font=font_cls_title)
        
        # Attributes with Bullet points
        cur_y = y + h_title + 14
        for attr in attributes:
            text_str = f"•  {attr}"
            draw.text((x + 25, cur_y), text_str, fill=(0, 0, 0), font=font_cls_body)
            cur_y += line_h
            
        # Methods with Bullet points
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

    # Grid Placement
    # Row 1 (Y = 260)
    user_box  = draw_class_box(200, 260, 850, "User Details", 
                               ["User Id", "User Name", "Password", "User Role"], 
                               ["Add()", "Delete()", "Update()"])

    cust_box  = draw_class_box(1350, 260, 920, "Customer Details", 
                               ["Customer Barcode Id", "Customer Roll No", "Name", "Service Address", "Phone Number"], 
                               ["Get Customer Details()", "Add Customer()", "Delete Customer()", "Update Customer()"])

    admin_box = draw_class_box(2550, 260, 850, "Administrator Details", 
                               ["Admin Id", "Department", "Email Access"], 
                               ["Manage Customers()", "Generate Bills()", "Assign Staff()"])

    staff_box = draw_class_box(3600, 260, 800, "Field Staff Details", 
                               ["Staff Id", "Designation", "Zone Code"], 
                               ["Log Readings()", "Resolve Complaints()"])

    # Row 2 (Y = 1700)
    meter_box   = draw_class_box(200, 1700, 880, "Meter Details", 
                                 ["Meter Id", "Serial Number", "Utility Type", "Meter Status"], 
                                 ["Get Consumption()", "Update Status()", "Assign Customer()"])

    reading_box = draw_class_box(1350, 1700, 920, "Meter Reading Details", 
                                 ["Reading Id", "Meter Serial No", "Current Reading", "Previous Reading", "Units Consumed"], 
                                 ["Calculate Delta()", "Validate Reading()"])

    bill_box    = draw_class_box(2550, 1700, 840, "Bill Details", 
                                 ["Bill Invoice Id", "Billing Month", "Amount Due", "Due Date", "Payment Status"], 
                                 ["Calculate Amount()", "Update Status()", "Send Reminder()"])

    pay_box     = draw_class_box(3600, 1700, 800, "Payment Details", 
                                 ["Payment Id", "Invoice Id", "Amount Paid", "Payment Channel", "Transaction Id"], 
                                 ["Process Payment()", "Generate Receipt()"])

    # Row 3 (Y = 3200)
    ticket_box = draw_class_box(850, 3200, 1000, "Support Ticket Details", 
                                ["Ticket Reference Id", "Customer Barcode Id", "Complaint Subject", "Ticket Status"], 
                                ["Add Comment()", "Update Status()", "Dispatch Technician()"])

    maint_box  = draw_class_box(2550, 3200, 1000, "Maintenance Work Details", 
                                ["Work Order Id", "Ticket Reference Id", "Assigned Staff Id", "Issue Description"], 
                                ["Update Progress()", "Complete Work Order()"])

    # Helper: Draw Orthogonal Lines
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

    # STRICT ZERO-OVERWRITE ROUTING FROM EXACT OUTER EDGES:

    # 1. User Details (Right Edge: 1050, 500) ---> Customer Details (Left Edge: 1350, 500)
    draw_orthogonal_line([(user_box["right"], 500), (cust_box["left"], 500)])

    # 2. Customer Details (Bottom Edge: 1500, cust_box["bottom"]=835) ---> Meter Details (Top Edge: 640, 1700)
    # Route: Down to Y=1200 in Horizontal Gutter 1, Left to X=640, Down to Meter Top (1700)
    draw_orthogonal_line([(1500, cust_box["bottom"]), (1500, 1200), (640, 1200), (640, meter_box["top"])], dashed=True)

    # 3. Meter Details (Right Edge: 1080, 1950) ---> Meter Reading Details (Left Edge: 1350, 1950)
    draw_orthogonal_line([(meter_box["right"], 1950), (reading_box["left"], 1950)])

    # 4. Customer Details (Bottom Edge: 2100, cust_box["bottom"]=835) ---> Bill Details (Top Edge: 2975, 1700)
    # Route: Down to Y=1400 in Horizontal Gutter 1, Right to X=2975, Down to Bill Top (1700)
    draw_orthogonal_line([(2100, cust_box["bottom"]), (2100, 1400), (2975, 1400), (2975, bill_box["top"])])

    # 5. Bill Details (Right Edge: 3390, 1950) ---> Payment Details (Left Edge: 3600, 1950)
    draw_orthogonal_line([(bill_box["right"], 1950), (pay_box["left"], 1950)])

    # 6. Customer Details (Bottom Edge: 1800, cust_box["bottom"]=835) ---> Support Ticket Details (Top Edge: 1215, 3200)
    # Route: Down to Y=1300 in Gutter 1, Left to X=1215 (Channel 1), Down Channel 1 past Row 2 to Ticket Top (3200)
    draw_orthogonal_line([(1800, cust_box["bottom"]), (1800, 1300), (1215, 1300), (1215, ticket_box["top"])], dashed=True)

    # 7. Support Ticket Details (Right Edge: 1850, 3450) ---> Maintenance Work Details (Left Edge: 2550, 3450)
    draw_orthogonal_line([(ticket_box["right"], 3450), (maint_box["left"], 3450)])

    # 8. Field Staff Details (Bottom Edge: 4000, staff_box["bottom"]=635) ---> Maintenance Work Details (Top Edge: 3500, 3200)
    # Route: Down to Y=1100 in Gutter 1, Left to X=3500 (Channel 3), Down Channel 3 to Maint Top (3200)
    draw_orthogonal_line([(4000, staff_box["bottom"]), (4000, 1100), (3500, 1100), (3500, maint_box["top"])])

    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Fixed Customer lines Class diagram saved to: {output_path}")

if __name__ == "__main__":
    generate_fixed_class_diagram()
