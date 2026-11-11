import os
from PIL import Image, ImageDraw, ImageFont

def draw_uml_actor(draw, x, y, label, font):
    # Head
    r = 22
    draw.ellipse([x - r, y - 55 - r, x + r, y - 55 + r], outline=(0,0,0), width=4, fill=(255,255,255))
    # Body
    draw.line([x, y - 33, x, y + 20], fill=(0,0,0), width=4)
    # Arms
    draw.line([x - 30, y - 15, x + 30, y - 15], fill=(0,0,0), width=4)
    # Legs
    draw.line([x, y + 20, x - 22, y + 55], fill=(0,0,0), width=4)
    draw.line([x, y + 20, x + 22, y + 55], fill=(0,0,0), width=4)
    # Text below
    tb = draw.textbbox((0,0), label, font=font)
    tw = tb[2] - tb[0]
    draw.text((x - tw // 2, y + 70), label, fill=(0,0,0), font=font)

def draw_uml_boundary(draw, x, y, label, font):
    r = 30
    cx, cy = x + 10, y
    # Circle
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0,0,0), width=4, fill=(245,245,245))
    # Vertical T-bar
    draw.line([x - 25, y - 32, x - 25, y + 32], fill=(0,0,0), width=4)
    # Horizontal line
    draw.line([x - 25, y, cx - r, y], fill=(0,0,0), width=4)
    # Text below
    tb = draw.textbbox((0,0), label, font=font)
    tw = tb[2] - tb[0]
    draw.text((x - tw // 2, y + 70), label, fill=(0,0,0), font=font)

def draw_uml_control(draw, x, y, label, font):
    r = 30
    # Circle
    draw.ellipse([x - r, y - r, x + r, y + r], outline=(0,0,0), width=4, fill=(245,245,245))
    # Top-right curved arrow head
    ax, ay = x + 15, y - 28
    draw.polygon([(ax, ay), (ax + 16, ay - 10), (ax + 6, ay + 14)], fill=(0,0,0))
    # Text below
    tb = draw.textbbox((0,0), label, font=font)
    tw = tb[2] - tb[0]
    draw.text((x - tw // 2, y + 70), label, fill=(0,0,0), font=font)

def draw_uml_entity(draw, x, y, label, font):
    r = 30
    # Circle
    draw.ellipse([x - r, y - r, x + r, y + r], outline=(0,0,0), width=4, fill=(245,245,245))
    # Bottom underline base
    draw.line([x - 34, y + 30, x + 34, y + 30], fill=(0,0,0), width=5)
    # Text below
    tb = draw.textbbox((0,0), label, font=font)
    tw = tb[2] - tb[0]
    draw.text((x - tw // 2, y + 70), label, fill=(0,0,0), font=font)

def generate_screenshot_exact_sequence(output_path, caption_title, lifelines_info, messages_info):
    width, height = 3600, 2600
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_header = ImageFont.truetype("arialbd.ttf", 36)
        font_msg = ImageFont.truetype("arial.ttf", 32)
        font_caption = ImageFont.truetype("arial.ttf", 36)
    except:
        font_header = ImageFont.load_default()
        font_msg = font_header
        font_caption = font_header

    # Lifeline spacing
    num_lifelines = len(lifelines_info)
    margin_x = 350
    step_x = (width - 2 * margin_x) // (num_lifelines - 1) if num_lifelines > 1 else 0

    x_coords = []
    top_y = 140

    # Draw Lifeline Icons at Top
    for idx, (label_text, icon_type) in enumerate(lifelines_info):
        cx = margin_x + idx * step_x
        x_coords.append(cx)

        if icon_type == "actor":
            draw_uml_actor(draw, cx, top_y, label_text, font_header)
        elif icon_type == "boundary":
            draw_uml_boundary(draw, cx, top_y, label_text, font_header)
        elif icon_type == "control":
            draw_uml_control(draw, cx, top_y, label_text, font_header)
        elif icon_type == "entity":
            draw_uml_entity(draw, cx, top_y, label_text, font_header)

        # Vertical dashed lifeline
        for y_dash in range(top_y + 130, height - 180, 22):
            draw.line([cx, y_dash, cx, y_dash + 12], fill=(80, 80, 80), width=3)

    # Lifeline Activation Bars (Tall thin rectangular boxes attached to lifelines)
    act_w = 26
    # Compute active ranges for each lifeline
    for idx in range(num_lifelines):
        cx = x_coords[idx]
        # find min and max y for this lifeline in messages
        ys = []
        for src, dst, y_p, text, is_self in messages_info:
            if src == idx or dst == idx:
                ys.append(y_p)
        if ys:
            min_y = min(ys) - 15
            max_y = max(ys) + 35
            draw.rectangle([cx - act_w//2, min_y, cx + act_w//2, max_y], fill=(255, 255, 255), outline=(0, 0, 0), width=3)

    # Render Messages Flow
    for src_idx, dst_idx, y_pos, text, is_self in messages_info:
        x1 = x_coords[src_idx]
        x2 = x_coords[dst_idx]

        if is_self:
            # Self Call Loop Arrow
            draw.line([x1 + act_w//2, y_pos, x1 + 180, y_pos], fill=(0, 0, 0), width=3)
            draw.line([x1 + 180, y_pos, x1 + 180, y_pos + 60], fill=(0, 0, 0), width=3)
            draw.line([x1 + 180, y_pos + 60, x1 + act_w//2, y_pos + 60], fill=(0, 0, 0), width=3)
            # Arrow head
            draw.polygon([(x1 + act_w//2, y_pos + 60), (x1 + act_w//2 + 16, y_pos + 52), (x1 + act_w//2 + 16, y_pos + 68)], fill=(0, 0, 0))
            # Text above self loop
            draw.text((x1 + 25, y_pos - 38), text, fill=(0, 0, 0), font=font_msg)
        else:
            # Horizontal Call Line
            draw.line([x1, y_pos, x2, y_pos], fill=(0, 0, 0), width=3)
            direction = 1 if x2 > x1 else -1
            # Solid Arrow Head
            draw.polygon([(x2, y_pos), (x2 - direction * 20, y_pos - 10), (x2 - direction * 20, y_pos + 10)], fill=(0, 0, 0))
            
            # Text directly above line (Left-aligned or centered above arrow)
            tb = draw.textbbox((0,0), text, font=font_msg)
            tw = tb[2] - tb[0]
            if direction > 0:
                text_x = x1 + 30
            else:
                text_x = x2 + 30
            draw.text((text_x, y_pos - 42), text, fill=(0, 0, 0), font=font_msg)

    # Caption at Bottom (Exact Screenshot format: "Sequence diagram—Title")
    caption_full = f"Sequence diagram—{caption_title}"
    tb_c = draw.textbbox((0,0), caption_full, font=font_caption)
    tw_c = tb_c[2] - tb_c[0]
    draw.text(((width - tw_c) // 2, height - 100), caption_full, fill=(0, 0, 0), font=font_caption)

    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Screenshot exact Sequence Diagram saved to: {output_path}")

# ==================== DEFINE ALL 4 SEQUENCE DIAGRAMS ====================

def generate_seq_auth_exact():
    lifelines = [
        (": User", "actor"),
        (": Login", "boundary"),
        (": Login Checker", "control"),
        (": Login Detail", "entity")
    ]
    messages = [
        (0, 1, 450, "1. Enter userid and Password", False),
        (1, 2, 750, "2. Submit Details", False),
        (2, 3, 1050, "3. Get login details", False),
        (2, 2, 1350, "4. Check login", True),
        (2, 1, 1750, "5. Error or success msg", False)
    ]
    generate_screenshot_exact_sequence("seq_diagram_auth_book_style.png", "Login & User Authentication", lifelines, messages)

def generate_seq_billing_exact():
    lifelines = [
        (": Field Staff", "actor"),
        (": Meter Reading UI", "boundary"),
        (": Billing Calculator", "control"),
        (": Bill Detail", "entity")
    ]
    messages = [
        (0, 1, 450, "1. Enter Meter ID and Reading", False),
        (1, 2, 750, "2. Process Meter Consumption", False),
        (2, 3, 1050, "3. Get Previous Reading & Tariff", False),
        (2, 2, 1350, "4. Calculate Bill Amount", True),
        (2, 3, 1650, "5. Save Invoice Record", False),
        (2, 1, 1950, "6. Display Invoice Generated Success", False)
    ]
    generate_screenshot_exact_sequence("seq_diagram_billing_book_style.png", "Meter Reading & Automated Billing", lifelines, messages)

def generate_seq_payment_exact():
    lifelines = [
        (": Customer", "actor"),
        (": Payment UI", "boundary"),
        (": Payment Processor", "control"),
        (": Payment Detail", "entity")
    ]
    messages = [
        (0, 1, 450, "1. Select Unpaid Bill & Payment Method", False),
        (1, 2, 750, "2. Submit Transaction Details", False),
        (2, 3, 1050, "3. Verify Bill Amount & Txn ID", False),
        (2, 2, 1350, "4. Process Payment Settlement", True),
        (2, 3, 1650, "5. Update Bill Status to Paid", False),
        (2, 1, 1950, "6. Return Digital Payment Receipt", False)
    ]
    generate_screenshot_exact_sequence("seq_diagram_payment_book_style.png", "Online Payment Settlement", lifelines, messages)

def generate_seq_complaint_exact():
    lifelines = [
        (": Customer", "actor"),
        (": Complaint Ticket UI", "boundary"),
        (": Dispatch Manager", "control"),
        (": Support Ticket Detail", "entity")
    ]
    messages = [
        (0, 1, 450, "1. Enter Service Issue & Description", False),
        (1, 2, 750, "2. Submit Complaint Ticket", False),
        (2, 3, 1050, "3. Create New Ticket Record", False),
        (2, 2, 1350, "4. Assign Field Technician", True),
        (2, 3, 1650, "5. Update Status to In Progress / Resolved", False),
        (2, 1, 1950, "6. Notify Customer Resolution Completed", False)
    ]
    generate_screenshot_exact_sequence("seq_diagram_complaint_book_style.png", "Support Ticket & Maintenance Dispatch", lifelines, messages)

if __name__ == "__main__":
    generate_seq_auth_exact()
    generate_seq_billing_exact()
    generate_seq_payment_exact()
    generate_seq_complaint_exact()
