import os
from PIL import Image, ImageDraw, ImageFont

def generate_ultra_class_diagram(output_path="class_diagram_book_style.png"):
    width, height = 4500, 4800
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_main_title = ImageFont.truetype("georgiai.ttf", 80)
        font_caption = ImageFont.truetype("arialbd.ttf", 44)
        font_cls_title = ImageFont.truetype("arialbd.ttf", 46)   # Very Large Class Title
        font_cls_body = ImageFont.truetype("arialbd.ttf", 34)    # Very Large Bold Class Attributes & Methods
        font_cls_assoc = ImageFont.truetype("arialbd.ttf", 34)   # Very Large Multiplicity & Association text
    except:
        font_main_title = ImageFont.load_default()
        font_caption = font_main_title
        font_cls_title = font_main_title
        font_cls_body = font_main_title
        font_cls_assoc = font_main_title

    # Header "Software Design"
    tb_t = draw.textbbox((0,0), "Software Design", font=font_main_title)
    tw_t = tb_t[2] - tb_t[0]
    draw.text(((width - tw_t) // 2, 50), "Software Design", fill=(30, 58, 138), font=font_main_title)
    draw.line([100, 160, width - 100, 160], fill=(220, 38, 38), width=8)

    # Caption at Bottom
    caption_text = "Class diagram for utility management system"
    tb_c = draw.textbbox((0,0), caption_text, font=font_caption)
    tw_c = tb_c[2] - tb_c[0]
    draw.text(((width - tw_c) // 2, height - 120), caption_text, fill=(30, 41, 59), font=font_caption)

    # Helper: Draw 3-Compartment Class Box with Generous Padding & Line Heights
    def draw_class_box(x, y, w, title, attributes, methods):
        line_h = 52
        h_title = 80
        h_attr = len(attributes) * line_h + 30
        h_meth = len(methods) * line_h + 30
        total_h = h_title + h_attr + h_meth
        
        # Outer border
        draw.rectangle([x, y, x + w, y + total_h], fill=(255, 255, 255), outline=(0, 0, 0), width=5)
        # Header tint
        draw.rectangle([x, y, x + w, y + h_title], fill=(241, 245, 249), outline=(0, 0, 0), width=5)
        # Separator line between attributes and methods
        draw.line([x, y + h_title + h_attr, x + w, y + h_title + h_attr], fill=(0, 0, 0), width=4)
        
        # Title Text
        tb = draw.textbbox((0,0), title, font=font_cls_title)
        tw = tb[2] - tb[0]
        draw.text((x + (w - tw) // 2, y + 16), title, fill=(15, 23, 42), font=font_cls_title)
        
        # Attributes Text
        cur_y = y + h_title + 16
        for attr in attributes:
            draw.text((x + 25, cur_y), attr, fill=(0, 0, 0), font=font_cls_body)
            cur_y += line_h
            
        # Methods Text
        cur_y = y + h_title + h_attr + 16
        for meth in methods:
            draw.text((x + 25, cur_y), meth, fill=(0, 0, 0), font=font_cls_body)
            cur_y += line_h

        return (x, y, w, total_h)

    # Grid Locations
    # Row 1 (y = 260)
    c_user = draw_class_box(200, 260, 820, "User", 
                            ["+ id: int", "+ username: String", "+ email: String", "+ role: String"], 
                            ["+ login(): boolean", "+ logout(): void", "+ updateProfile(): void"])

    c_cust = draw_class_box(1300, 260, 880, "Customer", 
                            ["+ customerId: int", "+ userId: int", "+ fullName: String", "+ address: String", "+ phone: String"], 
                            ["+ getAccountDetails()", "+ getBills()", "+ getMeters()"])

    c_admin = draw_class_box(2420, 260, 840, "Administrator", 
                            ["+ adminId: int", "+ department: String"], 
                            ["+ manageCustomers()", "+ generateBills()", "+ assignTechnicians()"])

    c_staff = draw_class_box(3480, 260, 820, "FieldStaff", 
                            ["+ staffId: int", "+ designation: String"], 
                            ["+ logReadings()", "+ resolveTickets()", "+ updateStatus()"])

    # Row 2 (y = 1700)
    c_meter = draw_class_box(200, 1700, 860, "Meter", 
                             ["+ meterId: int", "+ customerId: int", "+ serialNo: String", "+ utilityType: String", "+ status: String"], 
                             ["+ getConsumption()", "+ updateStatus()", "+ assignCustomer()"])

    c_reading = draw_class_box(1300, 1700, 880, "MeterReading", 
                               ["+ readingId: int", "+ meterId: int", "+ readingMonth: String", "+ currReading: double", "+ prevReading: double"], 
                               ["+ calculateDelta(): double", "+ validateReading()"])

    c_bill = draw_class_box(2420, 1700, 840, "Bill", 
                            ["+ billId: int", "+ customerId: int", "+ month: String", "+ amount: double", "+ dueDate: Date", "+ status: String"], 
                            ["+ calculateAmount()", "+ updateStatus()", "+ sendReminder()"])

    c_pay = draw_class_box(3480, 1700, 820, "Payment", 
                           ["+ paymentId: int", "+ billId: int", "+ amount: double", "+ method: String", "+ transactionId: String"], 
                           ["+ processPayment()", "+ generateReceipt()"])

    # Row 3 (y = 3150)
    c_ticket = draw_class_box(850, 3150, 950, "ComplaintTicket", 
                              ["+ ticketId: int", "+ customerId: int", "+ subject: String", "+ status: String", "+ createdAt: Date"], 
                              ["+ addComment()", "+ updateStatus()", "+ assignStaff()"])

    c_maint = draw_class_box(2500, 3150, 980, "MaintenanceWorkOrder", 
                             ["+ workOrderId: int", "+ ticketId: int", "+ technicianId: int", "+ issueDetails: String", "+ status: String"], 
                             ["+ updateProgress()", "+ completeTask()", "+ logNotes()"])

    # Association Line Helper with zero text overlap
    def draw_assoc_line(p1, p2, mult1="", mult2="", label=""):
        draw.line([p1[0], p1[1], p2[0], p2[1]], fill=(0,0,0), width=5)
        
        # Position labels cleanly near endpoints
        if mult1:
            draw.text((p1[0] + 15, p1[1] - 45), mult1, fill=(0,0,0), font=font_cls_assoc)
        if mult2:
            draw.text((p2[0] - 45, p2[1] - 45), mult2, fill=(0,0,0), font=font_cls_assoc)
        if label:
            mx = (p1[0] + p2[0]) // 2
            my = (p1[1] + p2[1]) // 2
            tb = draw.textbbox((0,0), label, font=font_cls_assoc)
            lw = tb[2] - tb[0]
            lh = tb[3] - tb[1]
            # White background box for label to prevent line intersection
            draw.rectangle([mx - lw//2 - 10, my - lh//2 - 6, mx + lw//2 + 10, my + lh//2 + 6], fill=(255,255,255), outline=(30, 58, 138), width=3)
            draw.text((mx - lw//2, my - lh//2 - 4), label, fill=(30, 58, 138), font=font_cls_assoc)

    # Connections
    # User --- Customer
    draw_assoc_line((1020, 500), (1300, 500), "1", "1", "links")
    # Customer --- Meter
    draw_assoc_line((630, 800), (630, 1700), "1", "*", "owns")
    # Meter --- MeterReading
    draw_assoc_line((1060, 1950), (1300, 1950), "1", "*", "logs")
    # Customer --- Bill
    draw_assoc_line((2180, 800), (2840, 1700), "1", "*", "receives")
    # Bill --- Payment
    draw_assoc_line((3260, 1950), (3480, 1950), "1", "0..1", "settled by")
    # Customer --- ComplaintTicket
    draw_assoc_line((1740, 800), (1325, 3150), "1", "*", "submits")
    # ComplaintTicket --- MaintenanceWorkOrder
    draw_assoc_line((1800, 3450), (2500, 3450), "0..1", "1", "dispatches")
    # FieldStaff --- MaintenanceWorkOrder
    draw_assoc_line((3890, 800), (2990, 3150), "1", "*", "assigned to")

    img.save(output_path, "PNG")
    print(f"Ultra-large Class Diagram created at: {output_path}")

if __name__ == "__main__":
    generate_ultra_class_diagram()
