import os
from PIL import Image, ImageDraw, ImageFont

def get_fonts():
    try:
        font_frame_title = ImageFont.truetype("arialbd.ttf", 34)
        font_header_title = ImageFont.truetype("arialbd.ttf", 30)
        font_header_sub = ImageFont.truetype("arial.ttf", 22)
        font_msg_bold = ImageFont.truetype("arialbd.ttf", 26)
        font_msg_small = ImageFont.truetype("ariali.ttf", 22)
    except:
        font_frame_title = ImageFont.load_default()
        font_header_title = font_frame_title
        font_header_sub = font_frame_title
        font_msg_bold = font_frame_title
        font_msg_small = font_frame_title
    return font_frame_title, font_header_title, font_header_sub, font_msg_bold, font_msg_small

def draw_stunning_sequence_diagram(output_path, title_label, diagram_code, lifelines_data, messages_data):
    width, height = 3600, 3600
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_frame_title, font_header_title, font_header_sub, font_msg_bold, font_msg_small = get_fonts()

    # Color Palette (Professional UML Palette)
    COLOR_BG = (255, 255, 255)
    COLOR_FRAME_BORDER = (148, 163, 184) # Slate border
    COLOR_FRAME_HEADER = (30, 41, 59)    # Deep Navy
    
    # 1. Outer Title Banner (Clean & Elegant)
    draw.rectangle([80, 50, width - 80, 130], fill=(30, 41, 59))
    draw.text((110, 72), f"UML 2.0 SEQUENCE DIAGRAM SPECIFICATION — {diagram_code}", fill=(255, 255, 255), font=font_frame_title)

    # 2. Outer UML SD Frame Box
    frame_left, frame_top, frame_right, frame_bottom = 80, 160, width - 80, height - 80
    draw.rectangle([frame_left, frame_top, frame_right, frame_bottom], fill=(250, 252, 255), outline=COLOR_FRAME_BORDER, width=4)

    # UML SD Pentagonal Header Label
    sd_text = f"sd {title_label}"
    tb_sd = draw.textbbox((0,0), sd_text, font=font_header_title)
    tw_sd = tb_sd[2] - tb_sd[0]
    draw.polygon([(frame_left, frame_top), (frame_left + tw_sd + 60, frame_top), (frame_left + tw_sd + 90, frame_top + 55), (frame_left, frame_top + 55)], fill=(226, 232, 240), outline=COLOR_FRAME_BORDER)
    draw.text((frame_left + 25, frame_top + 10), sd_text, fill=(30, 41, 59), font=font_header_title)

    # Lifeline Calculations
    num_lifelines = len(lifelines_data)
    margin_x = 250
    usable_w = width - 2 * margin_x
    step_x = usable_w // (num_lifelines - 1) if num_lifelines > 1 else usable_w

    x_coords = []
    
    # Render Lifeline Header Cards
    for idx, (obj_name, stereotype, theme_color, bg_tint) in enumerate(lifelines_data):
        cx = margin_x + idx * step_x
        x_coords.append(cx)
        
        w_card, h_card = 360, 120
        top_y = 260
        left_x = cx - w_card // 2
        right_x = cx + w_card // 2
        bottom_y = top_y + h_card

        # Header Card Shadow & Box
        draw.rectangle([left_x + 4, top_y + 4, right_x + 4, bottom_y + 4], fill=(226, 232, 240))
        draw.rectangle([left_x, top_y, right_x, bottom_y], fill=bg_tint, outline=theme_color, width=4)
        
        # Stereotype Top Bar
        draw.rectangle([left_x, top_y, right_x, top_y + 36], fill=theme_color)
        tb_s = draw.textbbox((0,0), f"«{stereotype}»", font=font_msg_small)
        tw_s = tb_s[2] - tb_s[0]
        draw.text((cx - tw_s // 2, top_y + 6), f"«{stereotype}»", fill=(255, 255, 255), font=font_msg_small)

        # Object Name
        tb_n = draw.textbbox((0,0), obj_name, font=font_header_title)
        tw_n = tb_n[2] - tb_n[0]
        draw.text((cx - tw_n // 2, top_y + 55), obj_name, fill=(30, 41, 59), font=font_header_title)

        # Lifeline Dashed Line
        for y_dash in range(bottom_y, height - 120, 24):
            draw.line([cx, y_dash, cx, y_dash + 12], fill=(148, 163, 184), width=3)

    # Render Messages Flow with Activation Boxes
    for src_idx, dst_idx, y_pos, msg_num, msg_sig, is_call in messages_data:
        x1 = x_coords[src_idx]
        x2 = x_coords[dst_idx]

        # Draw Activation Boxes along lifelines
        act_w = 28
        draw.rectangle([x1 - act_w//2, y_pos - 20, x1 + act_w//2, y_pos + 40], fill=(255, 255, 255), outline=(30, 41, 59), width=3)
        draw.rectangle([x2 - act_w//2, y_pos - 20, x2 + act_w//2, y_pos + 40], fill=(255, 255, 255), outline=(30, 41, 59), width=3)

        line_color = (30, 58, 138) if is_call else (15, 118, 110) # Navy for calls, Teal for return

        if is_call:
            # Solid Call Line
            draw.line([x1, y_pos, x2, y_pos], fill=line_color, width=4)
            direction = 1 if x2 > x1 else -1
            # Solid Arrow Head
            draw.polygon([(x2, y_pos), (x2 - direction * 24, y_pos - 12), (x2 - direction * 24, y_pos + 12)], fill=line_color)
        else:
            # Dashed Return Line
            for x_d in range(min(x1, x2), max(x1, x2), 22):
                draw.line([x_d, y_pos, min(x_d + 12, max(x1, x2)), y_pos], fill=line_color, width=4)
            direction = 1 if x2 > x1 else -1
            # Open Arrow Head
            draw.line([(x2, y_pos), (x2 - direction * 20, y_pos - 10)], fill=line_color, width=4)
            draw.line([(x2, y_pos), (x2 - direction * 20, y_pos + 10)], fill=line_color, width=4)

        # Message Badge Label (White background box so label floats cleanly above line)
        full_msg = f"{msg_num}: {msg_sig}"
        tb = draw.textbbox((0,0), full_msg, font=font_msg_bold)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]
        mx = (x1 + x2) // 2
        
        # Badge background
        draw.rectangle([mx - tw//2 - 12, y_pos - th//2 - 28, mx + tw//2 + 12, y_pos + th//2 - 18], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        draw.text((mx - tw//2, y_pos - th//2 - 25), full_msg, fill=line_color, font=font_msg_bold)

    # Save PNG
    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Stunning Sequence Diagram saved to: {output_path}")

# ==================== 4 SEQUENCE DIAGRAM DEFINITIONS ====================

def generate_seq_auth_stunning(output_path="seq_diagram_auth_book_style.png"):
    lifelines = [
        ("User", "Actor", (30, 41, 59), (241, 245, 249)),
        ("LoginUI", "Boundary / View", (37, 99, 235), (239, 246, 255)),
        ("AuthController", "Control / Logic", (13, 148, 136), (240, 253, 250)),
        ("UserDB", "Entity / Database", (5, 150, 105), (236, 253, 245))
    ]
    messages = [
        (0, 1, 480, "1", "enterCredentials(username, password)", True),
        (1, 2, 780, "2", "validateUser(username, passHash)", True),
        (2, 3, 1080, "3", "SELECT * FROM users WHERE username=?", True),
        (3, 2, 1380, "4", "return User Record & Password Hash", False),
        (2, 2, 1680, "5", "verifyHash() & generateSessionToken()", True),
        (2, 1, 1980, "6", "loginSuccess(sessionToken, userRole)", False),
        (1, 0, 2280, "7", "renderRoleDashboard(userRole)", False)
    ]
    draw_stunning_sequence_diagram(output_path, "User Authentication & Session Creation", "SEQ-01", lifelines, messages)

def generate_seq_billing_stunning(output_path="seq_diagram_billing_book_style.png"):
    lifelines = [
        ("FieldStaff", "Actor", (30, 41, 59), (241, 245, 249)),
        ("BillingUI", "Boundary / View", (37, 99, 235), (239, 246, 255)),
        ("BillingEngine", "Control / Engine", (13, 148, 136), (240, 253, 250)),
        ("BillingDB", "Entity / Database", (5, 150, 105), (236, 253, 245))
    ]
    messages = [
        (0, 1, 480, "1", "submitMeterReading(meterId, currReading)", True),
        (1, 2, 780, "2", "processReadingAndBill(meterId, currReading)", True),
        (2, 3, 1080, "3", "SELECT prevReading FROM readings WHERE meterId=?", True),
        (3, 2, 1380, "4", "return prevReading value", False),
        (2, 2, 1680, "5", "computeUnitsDelta() & applyTariffRate()", True),
        (2, 3, 1980, "6", "INSERT INTO bills (customerId, amount, status)", True),
        (3, 2, 2280, "7", "return Bill Created Confirmation (InvoiceID)", False),
        (2, 1, 2580, "8", "displayInvoiceSuccess(billDetails)", False)
    ]
    draw_stunning_sequence_diagram(output_path, "Meter Reading & Automated Billing Process", "SEQ-02", lifelines, messages)

def generate_seq_payment_stunning(output_path="seq_diagram_payment_book_style.png"):
    lifelines = [
        ("Customer", "Actor", (30, 41, 59), (241, 245, 249)),
        ("PaymentUI", "Boundary / View", (37, 99, 235), (239, 246, 255)),
        ("PaymentController", "Control / Logic", (13, 148, 136), (240, 253, 250)),
        ("PaymentGateway", "External API", (217, 119, 6), (254, 243, 199)),
        ("UtilisDB", "Entity / Database", (5, 150, 105), (236, 253, 245))
    ]
    messages = [
        (0, 1, 480, "1", "initiatePayment(billId, method, txnId)", True),
        (1, 2, 780, "2", "verifyAndProcess(billId, txnId)", True),
        (2, 3, 1080, "3", "validateTransaction(txnId, amount)", True),
        (3, 2, 1380, "4", "return Txn Verified Status (SUCCESS)", False),
        (2, 4, 1680, "5", "UPDATE bills SET status='paid' WHERE billId=?", True),
        (2, 4, 1980, "6", "INSERT INTO payments (billId, txnId, amount)", True),
        (4, 2, 2280, "7", "return Payment Record Saved Confirmation", False),
        (2, 1, 2580, "8", "renderReceiptView(transactionId)", False)
    ]
    draw_stunning_sequence_diagram(output_path, "Online Payment Settlement & Receipt Generation", "SEQ-03", lifelines, messages)

def generate_seq_complaint_stunning(output_path="seq_diagram_complaint_book_style.png"):
    lifelines = [
        ("Customer", "Actor", (30, 41, 59), (241, 245, 249)),
        ("ComplaintUI", "Boundary / View", (37, 99, 235), (239, 246, 255)),
        ("DispatchController", "Control / Dispatch", (13, 148, 136), (240, 253, 250)),
        ("FieldStaff", "Actor / Tech", (30, 41, 59), (241, 245, 249)),
        ("SupportDB", "Entity / Database", (5, 150, 105), (236, 253, 245))
    ]
    messages = [
        (0, 1, 480, "1", "submitComplaint(subject, issueDetails)", True),
        (1, 2, 780, "2", "createTicket(customerId, details)", True),
        (2, 4, 1080, "3", "INSERT INTO complaints (status='Pending')", True),
        (2, 3, 1380, "4", "assignFieldTechnician(ticketId, staffId)", True),
        (3, 4, 1680, "5", "UPDATE maintenance SET status='In Progress'", True),
        (3, 2, 1980, "6", "resolveTicket(resolutionNotes)", False),
        (2, 4, 2280, "7", "UPDATE complaints SET status='Resolved'", True),
        (2, 1, 2580, "8", "notifyCustomerTicketResolved(ticketId)", False)
    ]
    draw_stunning_sequence_diagram(output_path, "Support Ticket & Field Maintenance Dispatch", "SEQ-04", lifelines, messages)

if __name__ == "__main__":
    generate_seq_auth_stunning()
    generate_seq_billing_stunning()
    generate_seq_payment_stunning()
    generate_seq_complaint_stunning()
