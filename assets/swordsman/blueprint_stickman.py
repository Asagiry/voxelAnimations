"""
assets/swordsman/blueprint_stickman.py
Generates the Stick-Figure Sequence Blueprint for Attack_Overhead (Vertical Helm-Splitter / Jodan Giri).
Draws 8 keyframes across 3 views:
- Row 1: SIDE ELEVATION (Sagittal Y-Z plane) - shows Line of Action, spine coil/whip, and vertical blade arc.
- Row 2: FRONT 3/4 PERSPECTIVE - shows athletic power stance and 3D silhouette.
- Row 3: TOP-DOWN (Transverse X-Y plane) - shows centerline discipline and blade tracking.
"""

import math
from PIL import Image, ImageDraw, ImageFont

# 8 Keyframes across the 40-frame action
KEYFRAMES = [
    {"frame": 1,  "phase": "Ready Stance"},
    {"frame": 6,  "phase": "Coil Initiation"},
    {"frame": 12, "phase": "Peak High Windup"},
    {"frame": 16, "phase": "Explosive Launch"},
    {"frame": 18, "phase": "Mid-Chop Velocity"},
    {"frame": 20, "phase": "Impact / Helm Split"},
    {"frame": 24, "phase": "Impact Tremor"},
    {"frame": 38, "phase": "Recovery to Guard"},
]

def get_pose_data(f):
    """
    Returns 3D coordinates for all major joints at frame f.
    Coordinates: X (Left/Right), Y (Forward/Back), Z (Up/Down) in meters.
    Ground is at Z = 0.0.
    """
    # 1. Pelvis / Root
    if f <= 1:
        pelvis = (0.0, 0.0, 0.22)
        spine_pitch = 5.0 # deg forward
    elif f <= 6:
        t = (f - 1) / 5.0
        pelvis = (0.0, -0.02 * t, 0.22 - 0.02 * t)
        spine_pitch = 5.0 - 10.0 * t # starts arching back
    elif f <= 12:
        t = (f - 6) / 6.0
        pelvis = (0.0, -0.02 - 0.03 * t, 0.20 + 0.01 * t)
        spine_pitch = -5.0 - 12.0 * t # -17 deg back at peak
    elif f <= 16:
        t = (f - 12) / 4.0
        t_ease = t * t # accelerate
        pelvis = (0.0, -0.05 + 0.09 * t_ease, 0.21 - 0.03 * t_ease)
        spine_pitch = -17.0 + 22.0 * t_ease # whips from -17 to +5 deg
    elif f <= 18:
        t = (f - 16) / 2.0
        pelvis = (0.0, 0.04 + 0.04 * t, 0.18 - 0.01 * t)
        spine_pitch = 5.0 + 17.0 * t # +22 deg forward
    elif f <= 20:
        t = (f - 18) / 2.0
        pelvis = (0.0, 0.08 + 0.02 * t, 0.17)
        spine_pitch = 22.0 + 6.0 * t # +28 deg deep martial lean
    elif f <= 24:
        # Micro tremor on recoil
        t = (f - 20) / 4.0
        tremor = 2.0 * math.sin(t * math.pi * 3)
        pelvis = (0.0, 0.10, 0.17 + 0.005 * tremor)
        spine_pitch = 28.0 + tremor
    else:
        t = (f - 24) / 14.0
        t_smooth = t * t * (3 - 2 * t)
        pelvis = (0.0, 0.10 * (1 - t_smooth), 0.17 + 0.05 * t_smooth)
        spine_pitch = 28.0 * (1 - t_smooth) + 5.0 * t_smooth

    # 2. Spine & Chest & Head
    pitch_rad = math.radians(spine_pitch)
    spine_len = 0.10
    chest = (
        pelvis[0],
        pelvis[1] + spine_len * math.sin(pitch_rad),
        pelvis[2] + spine_len * math.cos(pitch_rad)
    )
    neck_len = 0.05
    neck = (
        chest[0],
        chest[1] + neck_len * math.sin(pitch_rad),
        chest[2] + neck_len * math.cos(pitch_rad)
    )
    head = (
        neck[0],
        neck[1] + 0.04, # head looks forward at target
        neck[2] + 0.07
    )

    # 3. Feet (Martial stance)
    if f <= 12:
        foot_l = (0.06, 0.08, 0.0)
        foot_r = (-0.06, -0.08, 0.0)
    elif f <= 20:
        t = (f - 12) / 8.0
        # Deep lunge: left foot steps forward, right foot stretches back
        foot_l = (0.07, 0.08 + 0.10 * t, 0.0)
        foot_r = (-0.07, -0.08 - 0.06 * t, 0.0)
    elif f <= 24:
        foot_l = (0.07, 0.18, 0.0)
        foot_r = (-0.07, -0.14, 0.0)
    else:
        t = (f - 24) / 14.0
        t_smooth = t * t * (3 - 2 * t)
        foot_l = (0.07 - 0.01 * t_smooth, 0.18 - 0.10 * t_smooth, 0.0)
        foot_r = (-0.07 + 0.01 * t_smooth, -0.14 + 0.06 * t_smooth, 0.0)

    # 4. Sword Arm (Left hand as lead sword hand, matching Swordsman model standard)
    shoulder_l = (chest[0] + 0.09, chest[1], chest[2])
    shoulder_r = (chest[0] - 0.09, chest[1], chest[2])

    if f <= 1:
        hand_l = (0.04, 0.18, 0.26)
        sword_tip = (0.04, 0.48, 0.38)
    elif f <= 6:
        t = (f - 1) / 5.0
        hand_l = (0.04 + 0.01 * t, 0.18 - 0.10 * t, 0.26 + 0.15 * t)
        sword_tip = (0.04, 0.48 - 0.30 * t, 0.38 + 0.25 * t)
    elif f <= 12:
        t = (f - 6) / 6.0
        # High Jodan Wind-up above & behind head
        hand_l = (0.05 - 0.02 * t, 0.08 - 0.20 * t, 0.41 + 0.25 * t)
        sword_tip = (0.03, -0.12 - 0.25 * t, 0.66 + 0.18 * t) # blade pointed up-back at -45 deg
    elif f <= 16:
        t = (f - 12) / 4.0
        t_ease = t * t
        # Catapulting forward-down
        hand_l = (0.03, -0.12 + 0.26 * t_ease, 0.66 - 0.12 * t_ease)
        sword_tip = (0.03, -0.37 + 0.55 * t_ease, 0.84 - 0.25 * t_ease)
    elif f <= 18:
        t = (f - 16) / 2.0
        hand_l = (0.03, 0.14 + 0.14 * t, 0.54 - 0.22 * t)
        sword_tip = (0.03, 0.18 + 0.28 * t, 0.59 - 0.38 * t)
    elif f <= 20:
        t = (f - 18) / 2.0
        # Slam down to ground level
        hand_l = (0.03, 0.28 + 0.10 * t, 0.32 - 0.16 * t)
        sword_tip = (0.03, 0.46 + 0.22 * t, 0.21 - 0.14 * t) # blade horizontal at Z = 0.07m
    elif f <= 24:
        t = (f - 20) / 4.0
        tremor = 0.015 * math.sin(t * math.pi * 3)
        hand_l = (0.03, 0.38, 0.16 + tremor)
        sword_tip = (0.03, 0.68, 0.07 + tremor * 1.5)
    else:
        t = (f - 24) / 14.0
        t_smooth = t * t * (3 - 2 * t)
        hand_l = (0.03 + 0.01 * t_smooth, 0.38 - 0.20 * t_smooth, 0.16 + 0.10 * t_smooth)
        sword_tip = (0.03 + 0.01 * t_smooth, 0.68 - 0.20 * t_smooth, 0.07 + 0.31 * t_smooth)

    # Off-hand (Right arm - active martial brace)
    if f <= 12:
        hand_r = (shoulder_r[0] - 0.02, shoulder_r[1] + 0.08, shoulder_r[2] - 0.08)
    elif f <= 20:
        t = (f - 12) / 8.0
        # Flings back for athletic counter-balance
        hand_r = (shoulder_r[0] - 0.04, shoulder_r[1] - 0.18 * t, shoulder_r[2] - 0.05)
    elif f <= 24:
        hand_r = (shoulder_r[0] - 0.04, shoulder_r[1] - 0.18, shoulder_r[2] - 0.05)
    else:
        t = (f - 24) / 14.0
        t_smooth = t * t * (3 - 2 * t)
        hand_r = (shoulder_r[0] - 0.04 + 0.02 * t_smooth, shoulder_r[1] - 0.18 + 0.26 * t_smooth, shoulder_r[2] - 0.05 - 0.03 * t_smooth)

    return {
        "pelvis": pelvis,
        "chest": chest,
        "neck": neck,
        "head": head,
        "foot_l": foot_l,
        "foot_r": foot_r,
        "shoulder_l": shoulder_l,
        "shoulder_r": shoulder_r,
        "hand_l": hand_l,
        "hand_r": hand_r,
        "sword_tip": sword_tip,
    }

def project_side(pt, w, h, ox, oy, scale):
    """Side projection (Y forward is right on screen, Z up is up on screen)"""
    x_px = ox + int(pt[1] * scale)
    y_px = oy - int(pt[2] * scale)
    return (x_px, y_px)

def project_top(pt, w, h, ox, oy, scale):
    """Top-down projection (X right is right, Y forward is up)"""
    x_px = ox + int(pt[0] * scale)
    y_px = oy - int(pt[1] * scale)
    return (x_px, y_px)

def project_iso(pt, w, h, ox, oy, scale):
    """3/4 Isometric projection"""
    # 45 deg yaw, 20 deg pitch
    iso_x = pt[0] * 0.707 - pt[1] * 0.707
    iso_y = pt[0] * 0.35 + pt[1] * 0.35 + pt[2] * 0.9
    x_px = ox + int(iso_x * scale)
    y_px = oy - int(iso_y * scale)
    return (x_px, y_px)

def draw_stickman(draw, pose, proj_fn, ox, oy, scale, colors):
    p_pelvis = proj_fn(pose["pelvis"], 0, 0, ox, oy, scale)
    p_chest = proj_fn(pose["chest"], 0, 0, ox, oy, scale)
    p_neck = proj_fn(pose["neck"], 0, 0, ox, oy, scale)
    p_head = proj_fn(pose["head"], 0, 0, ox, oy, scale)
    p_foot_l = proj_fn(pose["foot_l"], 0, 0, ox, oy, scale)
    p_foot_r = proj_fn(pose["foot_r"], 0, 0, ox, oy, scale)
    p_sh_l = proj_fn(pose["shoulder_l"], 0, 0, ox, oy, scale)
    p_sh_r = proj_fn(pose["shoulder_r"], 0, 0, ox, oy, scale)
    p_h_l = proj_fn(pose["hand_l"], 0, 0, ox, oy, scale)
    p_h_r = proj_fn(pose["hand_r"], 0, 0, ox, oy, scale)
    p_tip = proj_fn(pose["sword_tip"], 0, 0, ox, oy, scale)

    # 1. Ground plane line
    g_start = proj_fn((-0.3, -0.4, 0.0), 0, 0, ox, oy, scale)
    g_end = proj_fn((0.3, 0.7, 0.0), 0, 0, ox, oy, scale)
    draw.line([g_start, g_end], fill=colors["ground"], width=1)

    # 2. Spine & Head
    draw.line([p_pelvis, p_chest], fill=colors["spine"], width=4)
    draw.line([p_chest, p_neck], fill=colors["spine"], width=3)
    draw.ellipse([p_head[0]-8, p_head[1]-8, p_head[0]+8, p_head[1]+8], fill=colors["head"], outline=colors["head_border"], width=2)

    # 3. Legs
    draw.line([p_pelvis, p_foot_r], fill=colors["leg_r"], width=3)
    draw.line([p_pelvis, p_foot_l], fill=colors["leg_l"], width=4)
    draw.ellipse([p_foot_r[0]-3, p_foot_r[1]-3, p_foot_r[0]+3, p_foot_r[1]+3], fill=colors["foot"])
    draw.ellipse([p_foot_l[0]-4, p_foot_l[1]-4, p_foot_l[0]+4, p_foot_l[1]+4], fill=colors["foot"])

    # 4. Off-hand arm
    draw.line([p_sh_r, p_h_r], fill=colors["arm_r"], width=2)
    draw.ellipse([p_h_r[0]-3, p_h_r[1]-3, p_h_r[0]+3, p_h_r[1]+3], fill=colors["hand_r"])

    # 5. Lead sword arm & Sword
    draw.line([p_sh_l, p_h_l], fill=colors["arm_l"], width=4)
    draw.ellipse([p_h_l[0]-4, p_h_l[1]-4, p_h_l[0]+4, p_h_l[1]+4], fill=colors["hand_l"])

    # Blade: thick glowing neon laser line
    draw.line([p_h_l, p_tip], fill=colors["blade_glow"], width=5)
    draw.line([p_h_l, p_tip], fill=colors["blade_core"], width=2)
    draw.ellipse([p_tip[0]-3, p_tip[1]-3, p_tip[0]+3, p_tip[1]+3], fill=colors["blade_core"])

def main():
    row_header_h = 32
    cell_w = 260
    cell_h = 240
    cols = len(KEYFRAMES)
    rows = 3
    img_w = cols * cell_w
    img_h = rows * (cell_h + row_header_h) + 50

    img = Image.new("RGB", (img_w, img_h), (12, 14, 18))
    draw = ImageDraw.Draw(img)

    colors = {
        "ground": (50, 60, 75),
        "spine": (220, 220, 230),
        "head": (255, 190, 80),
        "head_border": (255, 230, 160),
        "leg_l": (80, 160, 255),
        "leg_r": (45, 90, 160),
        "foot": (140, 180, 240),
        "arm_l": (255, 110, 110),
        "arm_r": (160, 60, 60),
        "hand_l": (255, 200, 200),
        "hand_r": (180, 140, 140),
        "blade_glow": (255, 60, 120),
        "blade_core": (255, 240, 250),
        "text": (200, 210, 225),
        "title": (255, 200, 80),
        "sub": (120, 140, 160)
    }

    # Top title
    draw.text((20, 14), "STICK-FIGURE BLUEPRINT: ATTACK_OVERHEAD (VERTICAL HELM-SPLITTER)", fill=colors["title"])
    draw.text((700, 16), "Pipeline: 2D Line of Action Blueprint -> 3D Armature Kinematics Solver", fill=colors["sub"])

    row_titles = [
        "ROW 1: SIDE PROFILE (Sagittal Y-Z) — Line of Action, Spine C-Curve & Vertical Arc",
        "ROW 2: FRONT 3/4 PERSPECTIVE — Power Stance & Arm Separation",
        "ROW 3: TOP-DOWN (Transverse X-Y) — Centerline Alignment & Stance Depth"
    ]

    for r_idx, r_title in enumerate(row_titles):
        row_y = 50 + r_idx * (cell_h + row_header_h)
        draw.rectangle([0, row_y, img_w, row_y + row_header_h], fill=(18, 22, 30))
        draw.text((20, row_y + 8), r_title, fill=(100, 180, 255))

        for c_idx, kf in enumerate(KEYFRAMES):
            f = kf["frame"]
            phase = kf["phase"]
            pose = get_pose_data(f)

            col_x = c_idx * cell_w
            cell_top = row_y + row_header_h

            # Column background separator
            draw.line([(col_x, cell_top), (col_x, cell_top + cell_h)], fill=(25, 28, 35), width=1)

            # Frame badge in row 0
            if r_idx == 0:
                draw.text((col_x + 10, cell_top + 8), f"F{f:02d}", fill=colors["title"])
                draw.text((col_x + 50, cell_top + 8), phase, fill=colors["sub"])

            ox = col_x + cell_w // 2
            oy = cell_top + cell_h - 40

            if r_idx == 0:
                # Side view: shift slightly left so blade reaches forward
                draw_stickman(draw, pose, project_side, col_x + 90, oy, scale=170, colors=colors)
            elif r_idx == 1:
                draw_stickman(draw, pose, project_iso, ox, oy, scale=150, colors=colors)
            elif r_idx == 2:
                draw_stickman(draw, pose, project_top, ox, cell_top + cell_h - 90, scale=140, colors=colors)

    out_path = "assets/swordsman/stickman_blueprint.png"
    img.save(out_path)
    print(f"Successfully generated Stick-Figure Blueprint at: {out_path}")

if __name__ == "__main__":
    main()
