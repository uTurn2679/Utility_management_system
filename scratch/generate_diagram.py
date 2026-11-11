import os
from PIL import Image, ImageDraw, ImageFont

def create_use_case_diagram(output_path="use_case_diagram.png"):
    width, height = 2400, 1700
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Try to load fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_header = ImageFont.truetype("arialbd.ttf", 26)
        font_bold = ImageFont.truetype("arialbd.ttf", 20)
        font_normal = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("ariali.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_header = font_title
        font_bold = font_title
        font_normal = font_title
        font_small = font_title

    # Palette
    COLOR_BG = (255, 255, 255)
    COLOR_BOUNDARY_BG = (248, 250, 252)
    COLOR_BOUNDARY_BORDER = (148, 163, 184)
    COLOR_HEADER_BG = (30, 41, 59)
    COLOR_HEADER_TEXT = (255, 255, 255)
    
    COLOR_ACTOR_HEAD = (30, 41, 59)
    COLOR_ACTOR_LINE = (30, 41, 59)
    
    COLOR_UC_FILL = (239, 246, 255)
    COLOR_UC_BORDER = (37, 99, 235)
    COLOR_UC_TEXT = (30, 41, 59)
    
    COLOR_LINE = (71, 85, 105)
    COLOR_DASH_LINE = (37, 99, 235)

    # 1. System Boundary Box
    sb_left, sb_top, sb_right, sb_bottom = 480, 140, 1920, 1620
    draw.rectangle([sb_left, sb_top, sb_right, sb_bottom], fill=COLOR_BOUNDARY_BG, outline=COLOR_BOUNDARY_BORDER, width=3)
    
    # System Boundary Title Bar
    draw.rectangle([sb_left, sb_top, sb_right, sb_top + 60], fill=COLOR_HEADER_BG)
    draw.text((sb_left + 30, sb_top + 15), "SYSTEM BOUNDARY: UTILITY MANAGEMENT SYSTEM (utilis-app)", fill=COLOR_HEADER_TEXT, font=font_header)

    # Helper: Draw Actor Stick Figure
    def draw_actor(x, y, name, role_type="Primary Actor"):
        # Head
        r = 28
        draw.ellipse([x - r, y - r, x + r, y + r], outline=COLOR_ACTOR_HEAD, width=4, fill=(226, 232, 240))
        # Body
        draw.line([x, y + r, x, y + r + 55], fill=COLOR_ACTOR_LINE, width=4)
        # Arms
        draw.line([x - 40, y + r + 20, x + 40, y + r + 20], fill=COLOR_ACTOR_LINE, width=4)
        # Legs
        draw.line([x, y + r + 55, x - 30, y + r + 110], fill=COLOR_ACTOR_LINE, width=4)
        draw.line([x, y + r + 55, x + 30, y + r + 110], fill=COLOR_ACTOR_LINE, width=4)
        
        # Name Box
        bbox = draw.textbbox((0, 0), name, font=font_bold)
        tw = bbox[2] - bbox[0]
        draw.text((x - tw // 2, y + r + 120), name, fill=COLOR_ACTOR_HEAD, font=font_bold)
        
        bbox_sub = draw.textbbox((0, 0), f"({role_type})", font=font_small)
        tw_sub = bbox_sub[2] - bbox_sub[0]
        draw.text((x - tw_sub // 2, y + r + 148), f"({role_type})", fill=(100, 116, 139), font=font_small)

    # Draw Actors
    # Left Actors
    draw_actor(240, 320, "System Administrator", "Primary Admin")
    draw_actor(240, 950, "Utility Field Staff", "Field Engineer/Staff")
    
    # Right Actors
    draw_actor(2160, 480, "Utility Customer", "Consumer/User")
    draw_actor(2160, 1150, "External Gateway", "Nodemailer / Payment API")

    # Helper: Draw Use Case Ellipse
    def draw_use_case(x, y, uc_id, uc_name, width_uc=340, height_uc=90):
        left = x - width_uc // 2
        top = y - height_uc // 2
        right = x + width_uc // 2
        bottom = y + height_uc // 2
        
        # Outer ellipse shadow / border
        draw.ellipse([left, top, right, bottom], fill=COLOR_UC_FILL, outline=COLOR_UC_BORDER, width=3)
        
        # Text
        full_text = f"{uc_id}: {uc_name}"
        # Word wrap if needed
        words = full_text.split()
        lines = []
        cur_line = ""
        for w in words:
            test = (cur_line + " " + w).strip()
            if draw.textbbox((0,0), test, font=font_normal)[2] > width_uc - 40:
                lines.append(cur_line)
                cur_line = w
            else:
                cur_line = test
        if cur_line:
            lines.append(cur_line)
            
        total_h = len(lines) * 22
        start_y = y - total_h // 2
        for line in lines:
            tb = draw.textbbox((0,0), line, font=font_normal)
            lw = tb[2] - tb[0]
            draw.text((x - lw // 2, start_y), line, fill=COLOR_UC_TEXT, font=font_normal)
            start_y += 22

        return (x, y)

    # Place Use Cases in 3 Columns inside Boundary
    # Column 1 (Left): Admin / Meter / Auth
    uc_positions = {}
    uc_positions["UC01"] = draw_use_case(720, 260, "UC-01", "User Authentication & Profile")
    uc_positions["UC02"] = draw_use_case(720, 460, "UC-02", "Manage Customer Directory")
    uc_positions["UC03"] = draw_use_case(720, 660, "UC-03", "Register Smart Utility Meters")
    uc_positions["UC04"] = draw_use_case(720, 860, "UC-04", "Log Monthly Meter Readings")
    uc_positions["UC05"] = draw_use_case(720, 1060, "UC-05", "Calculate Bills & Apply Tariffs")
    uc_positions["UC06"] = draw_use_case(720, 1260, "UC-06", "Dispatch Automated Reminders")

    # Column 2 (Center/Right): Customer / Billing / Tickets
    uc_positions["UC07"] = draw_use_case(1200, 360, "UC-07", "View Bills & Account Ledger")
    uc_positions["UC08"] = draw_use_case(1200, 600, "UC-08", "Process Online Payments")
    uc_positions["UC09"] = draw_use_case(1200, 840, "UC-09", "Submit & Track Support Tickets")
    uc_positions["UC10"] = draw_use_case(1200, 1080, "UC-10", "Field Maintenance Dispatch")
    
    # Column 3 (Right): GIS & Analytics
    uc_positions["UC11"] = draw_use_case(1650, 480, "UC-11", "View GIS Spatial Map & Outages")
    uc_positions["UC12"] = draw_use_case(1650, 950, "UC-12", "Generate Reports & Analytics")
    uc_positions["UC13"] = draw_use_case(1650, 1350, "UC-13", "Download Digital Receipts")

    # Connect Actors to Use Cases
    def connect(actor_pos, uc_pos):
        draw.line([actor_pos[0], actor_pos[1], uc_pos[0], uc_pos[1]], fill=COLOR_LINE, width=2)

    # Actor positions
    admin_pos = (340, 320)
    staff_pos = (340, 950)
    customer_pos = (2020, 480)
    ext_pos = (2020, 1150)

    # Connections: Admin
    connect(admin_pos, uc_positions["UC01"])
    connect(admin_pos, uc_positions["UC02"])
    connect(admin_pos, uc_positions["UC03"])
    connect(admin_pos, uc_positions["UC05"])
    connect(admin_pos, uc_positions["UC06"])
    connect(admin_pos, uc_positions["UC10"])
    connect(admin_pos, uc_positions["UC12"])

    # Connections: Field Staff
    connect(staff_pos, uc_positions["UC01"])
    connect(staff_pos, uc_positions["UC04"])
    connect(staff_pos, uc_positions["UC09"])
    connect(staff_pos, uc_positions["UC10"])
    connect(staff_pos, uc_positions["UC11"])

    # Connections: Customer
    connect(customer_pos, uc_positions["UC01"])
    connect(customer_pos, uc_positions["UC07"])
    connect(customer_pos, uc_positions["UC08"])
    connect(customer_pos, uc_positions["UC09"])
    connect(customer_pos, uc_positions["UC13"])

    # Connections: External Gateway
    connect(ext_pos, uc_positions["UC06"])
    connect(ext_pos, uc_positions["UC08"])

    # Helper: Dashed Include/Extend Line
    def draw_dashed_relationship(p1, p2, label="<<include>>"):
        x1, y1 = p1
        x2, y2 = p2
        # Simple dashed drawing
        import math
        dist = math.hypot(x2 - x1, y2 - y1)
        dash_len = 12
        gap_len = 8
        step = dash_len + gap_len
        num_steps = int(dist / step)
        
        for i in range(num_steps):
            t1 = (i * step) / dist
            t2 = min(((i * step) + dash_len) / dist, 1.0)
            sx = x1 + (x2 - x1) * t1
            sy = y1 + (y2 - y1) * t1
            ex = x1 + (x2 - x1) * t2
            ey = y1 + (y2 - y1) * t2
            draw.line([sx, sy, ex, ey], fill=COLOR_DASH_LINE, width=2)
            
        # Label in middle
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        tb = draw.textbbox((0,0), label, font=font_small)
        lw = tb[2] - tb[0]
        lh = tb[3] - tb[1]
        draw.rectangle([mx - lw//2 - 4, my - lh//2 - 2, mx + lw//2 + 4, my + lh//2 + 2], fill=(255,255,255), outline=COLOR_DASH_LINE)
        draw.text((mx - lw//2, my - lh//2 - 2), label, fill=COLOR_DASH_LINE, font=font_small)

    # Include / Extend Relationships
    draw_dashed_relationship(uc_positions["UC05"], uc_positions["UC04"], "<<include>>")
    draw_dashed_relationship(uc_positions["UC06"], uc_positions["UC05"], "<<include>>")
    draw_dashed_relationship(uc_positions["UC08"], uc_positions["UC07"], "<<include>>")
    draw_dashed_relationship(uc_positions["UC13"], uc_positions["UC08"], "<<extend>>")
    draw_dashed_relationship(uc_positions["UC10"], uc_positions["UC09"], "<<extend>>")

    # Legend / Key Box
    leg_x, leg_y = 520, 1470
    draw.rectangle([leg_x, leg_y, leg_x + 650, leg_y + 110], fill=(255, 255, 255), outline=COLOR_BOUNDARY_BORDER, width=2)
    draw.text((leg_x + 15, leg_y + 10), "UML Diagram Legend & Notation:", fill=COLOR_HEADER_BG, font=font_bold)
    draw.line([leg_x + 20, leg_y + 50, leg_x + 100, leg_y + 50], fill=COLOR_LINE, width=2)
    draw.text((leg_x + 110, leg_y + 40), "Solid Line: Actor Association", fill=COLOR_UC_TEXT, font=font_small)
    draw_dashed_relationship((leg_x + 20, leg_y + 85), (leg_x + 120, leg_y + 85), "<<include>>")
    draw.text((leg_x + 140, leg_y + 75), "Dashed Arrow: Dependency (<<include>> / <<extend>>)", fill=COLOR_UC_TEXT, font=font_small)

    # Save Image
    img.save(output_path, "PNG")
    print(f"Diagram saved successfully to {output_path}")

if __name__ == "__main__":
    create_use_case_diagram()
