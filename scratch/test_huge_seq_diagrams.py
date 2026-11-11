import os
from PIL import Image, ImageDraw, ImageFont

def draw_uml_actor_large(draw, x, y, label, font):
    # Head
    r = 34
    draw.ellipse([x - r, y - 80 - r, x + r, y - 80 + r], outline=(0,0,0), width=6, fill=(255,255,255))
    # Body
    draw.line([x, y - 46, x, y + 30], fill=(0,0,0), width=6)
    # Arms
    draw.line([x - 45, y - 20, x + 45, y - 20], fill=(0,0,0), width=6)
    # Legs
    draw.line([x, y + 30, x - 32, y + 80], fill=(0,0,0), width=6)
    draw.line([x, y + 30, x + 32, y + 80], fill=(0,0,0), width=6)
    # Text below
    tb = draw.textbbox((0,0), label, font=font)
    tw = tb[2] - tb[0]
    draw.text((x - tw // 2, y + 100), label, fill=(0,0,0), font=font)

def draw_uml_boundary_large(draw, x, y, label, font):
    r = 45
    cx, cy = x + 15, y
    # Circle
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0,0,0), width=6, fill=(245,245,245))
    # Vertical T-bar
    draw.line([x - 40, y - 48, x - 40, y + 48], fill=(0,0,0), width=6)
    # Horizontal line
    draw.line([x - 40, y, cx - r, y], fill=(0,0,0), width=6)
    # Text below
    tb = draw.textbbox((0,0), label, font=font)
    tw = tb[2] - tb[0]
    draw.text((x - tw // 2, y + 100), label, fill=(0,0,0), font=font)

def draw_uml_control_large(draw, x, y, label, font):
    r = 45
    # Circle
    draw.ellipse([x - r, y - r, x + r, y + r], outline=(0,0,0), width=6, fill=(245,245,245))
    # Top-right curved arrow head
    ax, ay = x + 24, y - 42
    draw.polygon([(ax, ay), (ax + 24, ay - 14), (ax + 8, ay + 20)], fill=(0,0,0))
    # Text below
    tb = draw.textbbox((0,0), label, font=font)
    tw = tb[2] - tb[0]
    draw.text((x - tw // 2, y + 100), label, fill=(0,0,0), font=font)

def draw_uml_entity_large(draw, x, y, label, font):
    r = 45
    # Circle
    draw.ellipse([x - r, y - r, x + r, y + r], outline=(0,0,0), width=6, fill=(245,245,245))
    # Bottom underline base
    draw.line([x - 50, y + 45, x + 50, y + 45], fill=(0,0,0), width=7)
    # Text below
    tb = draw.textbbox((0,0), label, font=font)
    tw = tb[2] - tb[0]
    draw.text((x - tw // 2, y + 100), label, fill=(0,0,0), font=font)

def generate_huge_sequence_diagram(output_path, caption_title, lifelines_info, messages_info):
    width, height = 4200, 3200
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_header = ImageFont.truetype("arialbd.ttf", 52)
        font_msg = ImageFont.truetype("arialbd.ttf", 46)
        font_caption = ImageFont.truetype("arialbd.ttf", 52)
    except:
        font_header = ImageFont.load_default()
        font_msg = font_header
        font_caption = font_header

    num_lifelines = len(lifelines_info)
    margin_x = 450
    step_x = (width - 2 * margin_x) // (num_lifelines - 1) if num_lifelines > 1 else 0

    x_coords = []
    top_y = 160

    # Render Header Icons
    for idx, (label_text, icon_type) in enumerate(lifelines_info):
        cx = margin_x + idx * step_x
        x_coords.append(cx)

        if icon_type == "actor":
            draw_uml_actor_large(draw, cx, top_y, label_text, font_header)
        elif icon_type == "boundary":
            draw_uml_boundary_large(draw, cx, top_y, label_text, font_header)
        elif icon_type == "control":
            draw_uml_control_large(draw, cx, top_y, label_text, font_header)
        elif icon_type == "entity":
            draw_uml_entity_large(draw, cx, top_y, label_text, font_header)

        # Dashed Lifeline
        for y_dash in range(top_y + 180, height - 200, 26):
            draw.line([cx, y_dash, cx, y_dash + 14], fill=(60, 60, 60), width=4)

    # Lifeline Activation Bars (Thick rectangular boxes)
    act_w = 38
    for idx in range(num_lifelines):
        cx = x_coords[idx]
        ys = []
        for src, dst, y_p, text, is_self in messages_info:
            if src == idx or dst == idx:
                ys.append(y_p)
        if ys:
            min_y = min(ys) - 20
            max_y = max(ys) + 45
            draw.rectangle([cx - act_w//2, min_y, cx + act_w//2, max_y], fill=(255, 255, 255), outline=(0, 0, 0), width=5)

    # Render Messages Flow
    for src_idx, dst_idx, y_pos, text, is_self in messages_info:
        x1 = x_coords[src_idx]
        x2 = x_coords[dst_idx]

        if is_self:
            # Self Call Loop Arrow
            draw.line([x1 + act_w//2, y_pos, x1 + 220, y_pos], fill=(0, 0, 0), width=5)
            draw.line([x1 + 220, y_pos, x1 + 220, y_pos + 75], fill=(0, 0, 0), width=5)
            draw.line([x1 + 220, y_pos + 75, x1 + act_w//2, y_pos + 75], fill=(0, 0, 0), width=5)
            draw.polygon([(x1 + act_w//2, y_pos + 75), (x1 + act_w//2 + 22, y_pos + 63), (x1 + act_w//2 + 22, y_pos + 87)], fill=(0, 0, 0))
            draw.text((x1 + 30, y_pos - 55), text, fill=(0, 0, 0), font=font_msg)
        else:
            # Horizontal Call Line
            draw.line([x1, y_pos, x2, y_pos], fill=(0, 0, 0), width=5)
            direction = 1 if x2 > x1 else -1
            # Solid Arrow Head
            draw.polygon([(x2, y_pos), (x2 - direction * 28, y_pos - 14), (x2 - direction * 28, y_pos + 14)], fill=(0, 0, 0))
            
            # Text directly above line
            tb = draw.textbbox((0,0), text, font=font_msg)
            tw = tb[2] - tb[0]
            if direction > 0:
                text_x = x1 + 40
            else:
                text_x = x2 + 40
            draw.text((text_x, y_pos - 58), text, fill=(0, 0, 0), font=font_msg)

    # Caption at Bottom
    caption_full = f"Sequence diagram—{caption_title}"
    tb_c = draw.textbbox((0,0), caption_full, font=font_caption)
    tw_c = tb_c[2] - tb_c[0]
    draw.text(((width - tw_c) // 2, height - 120), caption_full, fill=(0, 0, 0), font=font_caption)

    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Huge Ultra-clear Sequence Diagram saved to: {output_path}")

# ==================== 4 SEQUENCE DIAGRAMS ====================

def generate_seq_auth_huge():
    lifelines = [
        (": User", "actor"),
        (": Login", "boundary"),
        (": Login Checker", "control"),
        (": Login Detail", "entity")
    ]
    messages = [
        (0, 1, 550, "1. Enter userid and Password", False),
        (1, 2, 920, "2. Submit Details", False),
        (2, 3, 1290, "3. Get login details", False),
        (2, 2, 1660, "4. Check login", True),
        (2, 1, 2150, "5. Error or success msg", False)
    ]
    generate_huge_sequence_diagram("seq_diagram_auth_book_style.png", "Login & User Authentication", lifelines, messages)

def generate_seq_billing_huge():
    lifelines = [
        (": Field Staff", "actor"),
        (": Meter Reading UI", "boundary"),
        (": Billing Calculator", "control"),
        (": Bill Detail", "entity")
    ]
    messages = [
        (0, 1, 550, "1. Enter Meter ID and Reading", False),
        (1, 2, 920, "2. Process Meter Consumption", False),
        (2, 3, 1290, "3. Get Previous Reading & Tariff", False),
        (2, 2, 1660, "4. Calculate Bill Amount", True),
        (2, 3, 2030, "5. Save Invoice Record", False),
        (2, 1, 2400, "6. Display Invoice Generated Success", False)
    ]
    generate_huge_sequence_diagram("seq_diagram_billing_book_style.png", "Meter Reading & Automated Billing", lifelines, messages)

def generate_seq_payment_huge():
    lifelines = [
        (": Customer", "actor"),
        (": Payment UI", "boundary"),
        (": Payment Processor", "control"),
        (": Payment Detail", "entity")
    ]
    messages = [
        (0, 1, 550, "1. Select Unpaid Bill & Payment Method", False),
        (1, 2, 920, "2. Submit Transaction Details", False),
        (2, 3, 1290, "3. Verify Bill Amount & Txn ID", False),
        (2, 2, 1660, "4. Process Payment Settlement", True),
        (2, 3, 2030, "5. Update Bill Status to Paid", False),
        (2, 1, 2400, "6. Return Digital Payment Receipt", False)
    ]
    generate_huge_sequence_diagram("seq_diagram_payment_book_style.png", "Online Payment Settlement", lifelines, messages)

def generate_seq_complaint_huge():
    lifelines = [
        (": Customer", "actor"),
        (": Complaint Ticket UI", "boundary"),
        (": Dispatch Manager", "control"),
        (": Support Ticket Detail", "entity")
    ]
    messages = [
        (0, 1, 550, "1. Enter Service Issue & Description", False),
        (1, 2, 920, "2. Submit Complaint Ticket", False),
        (2, 3, 1290, "3. Create New Ticket Record", False),
        (2, 2, 1660, "4. Assign Field Technician", True),
        (2, 3, 2030, "5. Update Status to In Progress / Resolved", False),
        (2, 1, 2400, "6. Notify Customer Resolution Completed", False)
    ]
    generate_huge_sequence_diagram("seq_diagram_complaint_book_style.png", "Support Ticket & Maintenance Dispatch", lifelines, messages)

if __name__ == "__main__":
    generate_seq_auth_huge()
    generate_seq_billing_huge()
    generate_seq_payment_huge()
    generate_seq_complaint_huge()
