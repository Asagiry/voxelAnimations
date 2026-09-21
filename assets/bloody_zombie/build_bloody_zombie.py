import bpy
import math
import os
import base64
from mathutils import Vector, Matrix

print("=================================================================")
print(">>> [TROVE VOXEL ARTISAN] Bloody Zombie (Gore / Berserker Undead)")
print(">>> Segmented Floating Limbs | Micro-Voxel Blood & Bone Relief")
print("=================================================================")

# -----------------------------------------------------------------
# 1. Reset Scene & General Configuration
# -----------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 80
scene.render.fps = 30

VOXEL_SIZE = 0.015  # 1.5 cm authentic Trove micro-voxel grid

# -----------------------------------------------------------------
# 2. Shader & Materials Definition (AgX Safe Saturated Palette)
# -----------------------------------------------------------------
def make_shader(name, color, roughness=0.6, metallic=0.0, emission=0.0, emission_color=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new(type='ShaderNodeOutputMaterial')
    out.location = (300, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    
    if emission > 0:
        ec = emission_color if emission_color else color
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = emission
            bsdf.inputs['Emission Color'].default_value = ec
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = ec
            
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

mats = {
    # 1. Rotting Gangrene Flesh (sickly olive gangrene)
    'flesh_green':    make_shader('M_FleshGreen',      (0.065, 0.145, 0.055, 1.0), roughness=0.65, metallic=0.05),
    # 2. Shadowed Gangrenous Flesh
    'flesh_dark':     make_shader('M_FleshDark',       (0.035, 0.075, 0.030, 1.0), roughness=0.70, metallic=0.05),
    # 3. Weathered Ivory Bone (skull, rib structure, heel spur)
    'decayed_bone':   make_shader('M_DecayedBone',     (0.560, 0.520, 0.420, 1.0), roughness=0.45, metallic=0.10),
    # 4. Bone Highlight (tooth pegs, sharp rib tips)
    'bone_highlight': make_shader('M_BoneHighlight',   (0.740, 0.700, 0.600, 1.0), roughness=0.35, metallic=0.10),
    # 5. Blood-Stained Bone (Ivory drenched in deep crimson, zero pink)
    'bone_blood':     make_shader('M_BoneBlood',       (0.420, 0.035, 0.035, 1.0), roughness=0.28, metallic=0.12),
    # 6. Fresh Wet Arterial Blood (Glossy Deep Crimson)
    'blood_fresh':    make_shader('M_BloodFresh',      (0.450, 0.005, 0.010, 1.0), roughness=0.18, metallic=0.10),
    # 7. Coagulated Maroon / Dark Rust Crust
    'blood_dark':     make_shader('M_BloodDark',       (0.100, 0.008, 0.010, 1.0), roughness=0.65, metallic=0.05),
    # 8. Shredded Dark Tattered Tunic
    'cloth_dark':     make_shader('M_ClothDark',       (0.022, 0.028, 0.035, 1.0), roughness=0.85, metallic=0.02),
    # 9. Blood-Soaked Wraps & Straps
    'cloth_bloody':   make_shader('M_ClothBloody',     (0.180, 0.018, 0.020, 1.0), roughness=0.75, metallic=0.05),
    # 10. Corroded Bronze Buckle
    'buckle_bronze':  make_shader('M_BuckleBronze',    (0.350, 0.260, 0.100, 1.0), roughness=0.35, metallic=0.85),
    # 11. Frenzied Bloodlust Eye (Fiery Crimson/Amber Emission)
    'eye_bloodlust':  make_shader('M_EyeBloodlust',    (1.000, 0.050, 0.010, 1.0), roughness=0.05, metallic=0.00, emission=2.4, emission_color=(1.00, 0.06, 0.015, 1.0)),
    # 12. Dark Matted Hair Strands
    'hair_dark':      make_shader('M_HairDark',        (0.014, 0.016, 0.020, 1.0), roughness=0.90, metallic=0.02),
    # 13. Heavy Combat Boot Sole
    'boot_sole':      make_shader('M_BootSole',        (0.012, 0.015, 0.018, 1.0), roughness=0.90, metallic=0.10),
    # 14. Gore Claw Slash Trail (Saturated Ruby / Deep Arterial Crimson - Rich Visceral Red)
    'slash_trail':    make_shader('M_BloodSlashTrail', (0.380, 0.004, 0.008, 1.0), roughness=0.20, metallic=0.00, emission=0.6, emission_color=(0.50, 0.005, 0.01, 1.0)),
    'slash_core':     make_shader('M_BloodSlashCore',  (0.680, 0.008, 0.015, 1.0), roughness=0.15, metallic=0.00, emission=1.2, emission_color=(0.80, 0.010, 0.02, 1.0)),
}

# -----------------------------------------------------------------
# 3. Procedural Micro-Voxel Synthesizer
# -----------------------------------------------------------------
voxels = {}

def set_vox(x, y, z, mat, bone, overwrite=False):
    k = (int(round(x)), int(round(y)), int(round(z)))
    if not overwrite and k in voxels:
        return
    voxels[k] = (mat, bone)

print(">>> [1/5] Synthesizing Bloody Zombie Micro-Voxel Anatomy...")

# --- 3.1 LEFT LEG: Blood-Splattered Boot, Rotting Calf, Tattered Trouser ---
# Foot.L (Z = 0..3) - Chunky Voxel Block (4 wide x 6 long x 4 high)
for x in range(2, 6):
    for y in range(-2, 4):
        set_vox(x, y, 0, 'boot_sole', 'Foot.L', True)
        m1 = 'blood_fresh' if (x == 5 and y in (1, 2)) else 'cloth_dark'
        set_vox(x, y, 1, m1, 'Foot.L', True)
        m2 = 'blood_dark' if (x == 4 and y == 3) else 'cloth_dark'
        set_vox(x, y, 2, m2, 'Foot.L', True)
        m_top = 'blood_fresh' if (x in (2, 3) and y == 2) else ('cloth_bloody' if y in (-2, 3) else 'cloth_dark')
        set_vox(x, y, 3, m_top, 'Foot.L', True)

# ANKLE JOINT GAP: Z = 4 is 1-voxel empty air!

# LowerLeg.L (Z = 5..8) - 2x2 Calf Strut with blood splatter
for z in range(5, 9):
    for x in (3, 4):
        for y in (0, 1):
            if z == 6 and x == 4 and y == 1:
                m = 'blood_fresh'
            elif z == 7:
                m = 'cloth_bloody'
            else:
                m = 'flesh_dark' if y == 0 else 'flesh_green'
            set_vox(x, y, z, m, 'LowerLeg.L', True)

# UpperLeg.L (Z = 9..12) - 2x2 Thigh Strut
for z in range(9, 13):
    for x in (3, 4):
        for y in (0, 1):
            m = 'blood_dark' if (z == 9 and y == 1) else 'cloth_dark'
            set_vox(x, y, z, m, 'UpperLeg.L', True)

# --- 3.2 RIGHT LEG: Bare Bloody Skeletal Leg, Splintered Tibia ---
# Foot.R (Z = 0..3) - Skeletal Claws soaked in blood
for x in range(-5, -1):
    for y in range(-2, 4):
        m = 'bone_blood' if y >= 2 else 'decayed_bone'
        set_vox(x, y, 0, m, 'Foot.R', True)
        m1 = 'blood_fresh' if (x in (-4, -3) and y == 3) else ('blood_dark' if (x == -5 and y == 1) else 'decayed_bone')
        set_vox(x, y, 1, m1, 'Foot.R', True)

for x in (-4, -3):
    for y in (-1, 2):
        set_vox(x, y, 2, 'bone_blood' if y == 1 else 'decayed_bone', 'Foot.R', True)
set_vox(-4, -2, 2, 'bone_highlight', 'Foot.R', True)  # Heel spur

set_vox(-4, 0, 3, 'bone_highlight', 'Foot.R', True)
set_vox(-3, 0, 3, 'bone_blood', 'Foot.R', True)
set_vox(-4, 1, 3, 'decayed_bone', 'Foot.R', True)
set_vox(-3, 1, 3, 'blood_fresh', 'Foot.R', True)

# ANKLE JOINT GAP: Z = 4 is 1-voxel empty air!

# LowerLeg.R (Z = 5..8) - Exposed Tibia with fresh blood drippings
for z in range(5, 9):
    for x in (-4, -3):
        for y in (0, 1):
            if y == 1:
                m = 'blood_fresh' if (z in (6, 8) and x == -3) else 'bone_blood'
                set_vox(x, y, z, m, 'LowerLeg.R', True)
            else:
                set_vox(x, y, z, 'blood_dark' if z % 2 == 0 else 'flesh_dark', 'LowerLeg.R', True)

# UpperLeg.R (Z = 9..12) - Thigh Strut
for z in range(9, 13):
    for x in (-4, -3):
        for y in (0, 1):
            m = 'bone_blood' if (z == 9 and y == 1) else ('cloth_bloody' if (x + z) % 2 == 0 else 'cloth_dark')
            set_vox(x, y, z, m, 'UpperLeg.R', True)

# --- 3.3 PELVIS, WAIST & TORN BELT (Z = 13..16) ---
# Pelvis (Z = 13..15) - 8 wide x 6 deep x 3 high
for z in range(13, 16):
    for x in range(-4, 4):
        for y in range(-3, 3):
            if z == 13 and (y in (-3, 2) or abs(x) in (3, 4)):
                continue
            is_front = (y == 2)
            if is_front and abs(x) <= 2:
                m = 'blood_fresh' if (x in (-1, 1) and z == 15) else 'blood_dark'
            else:
                m = 'cloth_bloody' if (x in (-2, 2) or z == 14) else 'cloth_dark'
            set_vox(x, y, z, m, 'Hips', True)

# Waist & Belt Band (Z = 16) - with blood smears
for x in range(-4, 4):
    for y in range(-3, 3):
        is_front = (y == 2)
        if is_front:
            m = 'buckle_bronze' if abs(x) <= 1 else 'blood_fresh'
        else:
            m = 'cloth_bloody' if abs(x) == 3 else 'cloth_dark'
        set_vox(x, y, 16, m, 'Spine', True)

# Extruded Belt Buckle (+1 voxel forward to Y = 3)
for x in (-1, 0):
    for z in (15, 16):
        set_vox(x, 3, z, 'buckle_bronze', 'Spine', True)

# --- 3.4 CHEST & BLOODY VISCERAL RIB CAGE (Z = 17..24) ---
# Core Chest Body - 8 wide x 6 deep x 8 high
for z in range(17, 25):
    for x in range(-4, 4):
        for y in range(-3, 3):
            # Thoracic cavity opening on the front (Y = 1..2, X in -3..2)
            is_cavity = (y >= 1 and -3 <= x <= 2 and 18 <= z <= 23)
            if is_cavity:
                m = 'blood_fresh' if (z in (19, 21) and x in (-1, 0)) else 'blood_dark'
                set_vox(x, y, z, m, 'Chest', True)
            else:
                is_back = (y == -3)
                if is_back:
                    m = 'blood_dark' if (abs(x) <= 1 and z in (20, 21)) else 'cloth_dark'
                else:
                    m = 'cloth_bloody' if (x in (-4, 3) and z >= 21) else 'cloth_dark'
                set_vox(x, y, z, m, 'Chest', True)

# Broken Protruding Ribs Drenched in Fresh Arterial Blood
# Lower Rib Pair (Z = 19) -> Protrudes forward to Y = 3
set_vox(-3, 1, 19, 'bone_blood', 'Chest', True)
set_vox(-3, 2, 19, 'bone_blood', 'Chest', True)
set_vox(-2, 3, 19, 'blood_fresh', 'Chest', True)
set_vox(-1, 3, 19, 'blood_fresh', 'Chest', True)

set_vox(2, 1, 19, 'bone_blood', 'Chest', True)
set_vox(2, 2, 19, 'bone_blood', 'Chest', True)
set_vox(1, 3, 19, 'bone_blood', 'Chest', True)
set_vox(0, 3, 19, 'blood_fresh', 'Chest', True)

# Middle Rib Pair (Z = 21) -> APEX PROTRUSION to Y = 4 (+2 voxels forward!)
set_vox(-3, 1, 21, 'bone_blood', 'Chest', True)
set_vox(-3, 2, 21, 'bone_blood', 'Chest', True)
set_vox(-2, 3, 21, 'bone_blood', 'Chest', True)
set_vox(-2, 4, 21, 'bone_highlight', 'Chest', True)
set_vox(-1, 4, 21, 'blood_fresh', 'Chest', True)

set_vox(2, 1, 21, 'bone_blood', 'Chest', True)
set_vox(2, 2, 21, 'bone_blood', 'Chest', True)
set_vox(1, 3, 21, 'bone_blood', 'Chest', True)
set_vox(1, 4, 21, 'bone_highlight', 'Chest', True)
set_vox(0, 4, 21, 'blood_fresh', 'Chest', True)

# Upper Rib Pair (Z = 23) -> Protrudes forward to Y = 3
set_vox(-3, 1, 23, 'bone_blood', 'Chest', True)
set_vox(-3, 2, 23, 'bone_blood', 'Chest', True)
set_vox(-2, 3, 23, 'blood_fresh', 'Chest', True)
set_vox(-1, 3, 23, 'blood_fresh', 'Chest', True)

set_vox(2, 1, 23, 'bone_blood', 'Chest', True)
set_vox(2, 2, 23, 'bone_blood', 'Chest', True)
set_vox(1, 3, 23, 'bone_blood', 'Chest', True)
set_vox(0, 3, 23, 'blood_fresh', 'Chest', True)

# Fresh Blood Droplets Dripping Down the Ribs
set_vox(-1, 3, 18, 'blood_fresh', 'Chest', True)
set_vox(0, 3, 18, 'blood_fresh', 'Chest', True)
set_vox(-1, 3, 17, 'blood_fresh', 'Chest', True)

# --- 3.5 PAULDRONS (SHOULDERS): FLOATING WITH 1-VOXEL BREATHING GAP FROM CHEST ---
# Right Pauldron (Shoulder.R) - Floating at X: -9..-6, Y: -3..2, Z: 23..26 (X = -5 is empty gap!)
for z in range(23, 27):
    for x in range(-9, -5):
        for y in range(-3, 3):
            m = 'bone_blood' if (z >= 25 or y == 2) else 'cloth_bloody'
            set_vox(x, y, z, m, 'Shoulder.R', True)

# Bone spikes with blood on right pauldron
set_vox(-8, 0, 27, 'blood_fresh', 'Shoulder.R', True)
set_vox(-7, 0, 27, 'bone_blood', 'Shoulder.R', True)

# Left Pauldron (Shoulder.L) - Floating at X: 5..8, Y: -3..2, Z: 23..26 (X = 4 is empty gap!)
for z in range(23, 27):
    for x in range(5, 9):
        for y in range(-3, 3):
            is_rim = (x in (5, 8) or y in (-3, 2) or z in (23, 26))
            m = 'blood_fresh' if (is_rim and z == 26) else ('flesh_dark' if y == 2 else 'cloth_dark')
            set_vox(x, y, z, m, 'Shoulder.L', True)

# --- 3.6 LEFT ARM: UPPER ARM, FOREARM, WRIST GAP & BLOOD-SOAKED FLOATING CLAW HAND ---
# UpperArm.L (Z = 19..23)
for z in range(19, 24):
    for x in (6, 7):
        for y in (-1, 0):
            m = 'cloth_bloody' if z >= 22 else 'flesh_green'
            set_vox(x, y, z, m, 'UpperArm.L', True)

# Forearm.L (Z = 14..18)
for z in range(14, 19):
    for x in (6, 7):
        for y in (-1, 0):
            m = 'blood_fresh' if (z == 15 and y == 0) else ('cloth_bloody' if z in (16, 17) else 'flesh_dark')
            set_vox(x, y, z, m, 'Forearm.L', True)

# WRIST JOINT GAP: Z = 13 is 1-voxel empty air!

# Hand.L (Z = 8..12) - Floating Chunky Bloody Claw Gauntlet (4x4x4 block: X: 5..8, Y: -2..1)
for z in range(9, 13):
    for x in range(5, 9):
        for y in range(-2, 2):
            is_edge = (x in (5, 8) or y in (-2, 1) or z in (9, 12))
            m = 'blood_fresh' if (is_edge and y == 1) else 'flesh_green'
            set_vox(x, y, z, m, 'Hand.L', True)

# Blood-Tipped Claws on Left Hand (Z = 7..8, Y = 1..2)
for x in (5, 6, 7, 8):
    set_vox(x, 2, 9, 'blood_fresh', 'Hand.L', True)
    set_vox(x, 2, 8, 'blood_fresh', 'Hand.L', True)
    set_vox(x, 2, 7, 'bone_highlight', 'Hand.L', True)

# --- 3.7 RIGHT ARM: BARE BLOODY SKELETAL ARM & CHUNKY TALON CLAW ---
# UpperArm.R (Z = 19..23) - Skeletal Bone drenched in blood
for z in range(19, 24):
    for x in (-8, -7):
        for y in (-1, 0):
            m = 'blood_dark' if z == 21 else 'bone_blood'
            set_vox(x, y, z, m, 'UpperArm.R', True)

# Forearm.R (Z = 14..18) - Exposed Ulna/Radius Bone Strut
for z in range(14, 19):
    for x in (-8, -7):
        for y in (-1, 0):
            m = 'blood_fresh' if (z in (15, 17) and y == 0) else 'bone_blood'
            set_vox(x, y, z, m, 'Forearm.R', True)

# WRIST JOINT GAP: Z = 13 is 1-voxel empty air!

# Hand.R (Z = 8..12) - Skeletal Claw Gauntlet (4x4x4 block: X: -9..-6, Y: -2..1)
for z in range(9, 13):
    for x in range(-9, -5):
        for y in range(-2, 2):
            is_edge = (x in (-9, -6) or y in (-2, 1) or z in (9, 12))
            m = 'blood_fresh' if is_edge else 'bone_blood'
            set_vox(x, y, z, m, 'Hand.R', True)

# Blood-Tipped Skeletal Talons on Right Hand
for x in (-9, -8, -7, -6):
    set_vox(x, 2, 9, 'blood_fresh', 'Hand.R', True)
    set_vox(x, 2, 8, 'blood_fresh', 'Hand.R', True)
    set_vox(x, 2, 7, 'bone_highlight', 'Hand.R', True)

# --- 3.8 NECK & HEAD BASE: 10x10x10 CHIBI HEAD (Z = 24..35) ---
# Neck (Z = 24..25) - 2x2 Strut
for z in (24, 25):
    for x in (-1, 0):
        for y in (-1, 0):
            set_vox(x, y, z, 'blood_fresh' if x == 0 else 'decayed_bone', 'Neck', True)

# Head Base (Z = 26..35, X: -5..4, Y: -5..4) - 10 wide x 10 deep x 10 high
for z in range(26, 36):
    for x in range(-5, 5):
        for y in range(-5, 5):
            # Asymmetrical Anatomy: Right side (x < 0) is exposed skull, Left side (x >= 0) is rotting flesh
            if x < 0:
                m = 'bone_blood' if (z in (27, 28) or (x in (-2, -1) and y >= 2)) else 'decayed_bone'
            else:
                m = 'blood_dark' if (x == 0 and z in (30, 31)) else ('flesh_dark' if (y == -5 or z == 35) else 'flesh_green')
            set_vox(x, y, z, m, 'Head', True)

# --- 3.9 MULTI-LAYERED FACIAL RELIEF & GORE DETAILS ---
# Fresh Blood Streams from Craniotomy Fracture on Right Skull (X: -4..-1, Y: 4, Z: 29..34)
set_vox(-3, 4, 34, 'blood_fresh', 'Head', True)
set_vox(-2, 4, 33, 'blood_fresh', 'Head', True)
set_vox(-3, 4, 32, 'blood_fresh', 'Head', True)
set_vox(-2, 4, 31, 'blood_fresh', 'Head', True)
set_vox(-1, 4, 30, 'blood_fresh', 'Head', True)
set_vox(-1, 4, 29, 'blood_fresh', 'Head', True)

# Bloodlust Glowing Eye on Left Face (X: 1..2, Y: 4, Z: 30..31)
set_vox(1, 4, 30, 'eye_bloodlust', 'Head', True)
set_vox(2, 4, 30, 'eye_bloodlust', 'Head', True)
set_vox(1, 4, 31, 'eye_bloodlust', 'Head', True)
set_vox(2, 4, 31, 'eye_bloodlust', 'Head', True)

# Hollow Gouged Bloody Eye Socket on Right Skull (X: -3..-2, Y: 4, Z: 30..31)
set_vox(-3, 4, 30, 'blood_dark', 'Head', True)
set_vox(-2, 4, 30, 'blood_fresh', 'Head', True)
set_vox(-3, 4, 31, 'blood_dark', 'Head', True)
set_vox(-2, 4, 31, 'blood_dark', 'Head', True)

# Extruded Heavy Brow Ridge (+1 forward to Y = 5, Z = 32)
for x in range(-4, 4):
    m = 'blood_fresh' if x in (-2, -1) else ('decayed_bone' if x < 0 else 'flesh_green')
    set_vox(x, 5, 32, m, 'Head', True)

# Snout Cavity & Dried Blood (Z = 29, Y = 4)
set_vox(0, 4, 29, 'blood_dark', 'Head', True)
set_vox(-1, 4, 29, 'blood_dark', 'Head', True)

# Extruded Open Jaw & Dripping Fangs (+1 forward to Y = 5, Z = 26..28)
for x in range(-4, 4):
    m = 'bone_blood' if x < 0 else 'blood_dark'
    set_vox(x, 5, 26, m, 'Head', True)

# Alternating Tooth Pegs Drenched in Fresh Blood (+1 forward to Y = 5, Z = 27)
for x in range(-4, 4):
    m_tooth = 'blood_fresh' if x in (-3, -1, 1, 3) else 'bone_highlight'
    set_vox(x, 5, 27, m_tooth, 'Head', True)

# Matted Dark Hair Strands on Cranium (+1 up to Z = 36, Y = -4..2)
for x in range(-1, 4):
    for y in range(-4, 3):
        if (x + y) % 2 == 0:
            set_vox(x, y, 36, 'hair_dark', 'Head', True)

# Dripping Blood Clot on Top Cranium
set_vox(-2, -1, 36, 'blood_fresh', 'Head', True)
set_vox(-3, -1, 36, 'blood_dark', 'Head', True)

# --- 3.10 VOLUMETRIC CRIMSON GORE ATTACK TRAILS (SPAWN BEHIND CLAWS) ---
def build_blood_slash_ribbon(x_center, bone_name):
    N_STEPS = 24
    for st in range(N_STEPS):
        u = st / float(N_STEPS - 1)
        ang = -0.45 + u * (math.pi * 0.80)
        rad = 12.5
        cy = 5.0 + math.sin(ang) * rad
        cz = 21.0 - math.cos(ang) * rad * 0.90
        for dx in (-1, 0, 1):
            vx = x_center + dx
            for dy in (0, 1):
                m_trail = 'slash_core' if (dx == 0 and dy == 0) else 'slash_trail'
                set_vox(vx, cy + dy, cz, m_trail, bone_name, True)

build_blood_slash_ribbon(7, 'ClawTrail.L')
build_blood_slash_ribbon(-8, 'ClawTrail.R')

print(f">>> Total Generated Micro-Voxels: {len(voxels)} voxels.")

# -----------------------------------------------------------------
# 4. Watertight Boundary Quad Mesher & Planar Dissolve
# -----------------------------------------------------------------
print(">>> Constructing watertight boundary quad mesh...")

DIRECTIONS = [
    (( 1,  0,  0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
    ((-1,  0,  0), [(0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1)]),
    (( 0,  1,  0), [(1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)]),
    (( 0, -1,  0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
    (( 0,  0,  1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
    (( 0,  0, -1), [(0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)]),
]

verts = []
faces = []
face_mats = []
vert_groups = {}
vert_map = {}

used_mat_names = sorted(list(set(m for m, b in voxels.values())))
mat_to_slot = {name: i for i, name in enumerate(used_mat_names)}

for (vx, vy, vz), (mat_name, bone_name) in voxels.items():
    slot = mat_to_slot[mat_name]
    for (dx, dy, dz), quad_offsets in DIRECTIONS:
        neighbor = (vx + dx, vy + dy, vz + dz)
        if neighbor not in voxels or voxels[neighbor][1] != bone_name:
            quad = []
            for (qx, qy, qz) in quad_offsets:
                p = (
                    round((vx + qx) * VOXEL_SIZE, 6),
                    round((vy + qy) * VOXEL_SIZE, 6),
                    round((vz + qz) * VOXEL_SIZE, 6)
                )
                vkey = (p, bone_name)
                if vkey not in vert_map:
                    vidx = len(verts)
                    vert_map[vkey] = vidx
                    verts.append(p)
                    vert_groups[vidx] = bone_name
                quad.append(vert_map[vkey])
            faces.append(quad)
            face_mats.append(slot)

print(f">>> Raw Quad Mesh: {len(verts)} verts, {len(faces)} faces.")
mesh = bpy.data.meshes.new("Bloody_Zombie_Mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

for m in used_mat_names:
    mesh.materials.append(mats[m])
for poly, slot in zip(mesh.polygons, face_mats):
    poly.material_index = slot

mesh.polygons.foreach_set('use_smooth', [False] * len(mesh.polygons))
mesh.update()

zombie_obj = bpy.data.objects.new("Bloody_Zombie", mesh)
bpy.context.collection.objects.link(zombie_obj)

# -----------------------------------------------------------------
# 5. Skeletal Rigging & Standard Equipment Socket Hierarchy
# -----------------------------------------------------------------
print(">>> Rigging Clean Armature with Rigid Sockets...")
arm_data = bpy.data.armatures.new("Bloody_Zombie_Armature_Data")
arm_obj = bpy.data.objects.new("Bloody_Zombie_Armature", arm_data)
bpy.context.collection.objects.link(arm_obj)

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones

def make_bone(name, head, tail, parent_name=None):
    b = eb.new(name)
    b.head = Vector(head) * VOXEL_SIZE
    b.tail = Vector(tail) * VOXEL_SIZE
    if parent_name and parent_name in eb:
        b.parent = eb[parent_name]
    return b

# Core Spine Chain
b_root = make_bone("Root",      (0, 0, 0),        (0, 0.08 / VOXEL_SIZE, 0),       None)
make_bone("Hips",      (0, 0, 14),       (0, 0, 16),       "Root")
make_bone("Spine",     (0, 0, 16),       (0, 0, 20),       "Hips")
make_bone("Chest",     (0, 0, 20),       (0, 0, 24),       "Spine")
make_bone("Neck",      (0, 0, 24),       (0, 0, 26),       "Chest")
make_bone("Head",      (0, 0, 26),       (0, 0, 36),       "Neck")

# Standard Equipment Sockets
make_bone("Socket_Head", (0, -0.5, 36),     (0, -0.5, 38),       "Head")
make_bone("Socket_Back", (0, -3.5, 22),    (0, -4.5, 22),      "Chest")

# Left Arm Chain & Sockets
make_bone("Shoulder.L", (3.5, 0, 24),    (6.5, 0, 24),       "Chest")
make_bone("UpperArm.L", (6.5, 0, 24),    (6.5, 0, 19),       "Shoulder.L")
make_bone("Forearm.L",  (6.5, 0, 19),    (6.5, 0, 13),       "UpperArm.L")
make_bone("Hand.L",     (6.5, 1.0, 12),  (6.5, 3.0, 9),        "Forearm.L")
make_bone("Socket_Hand_L", (6.5, 1.0, 10.5), (6.5, 2.5, 10.5), "Hand.L")

# Right Arm Chain & Sockets
make_bone("Shoulder.R", (-3.5, 0, 24),   (-6.5, 0, 24),      "Chest")
make_bone("UpperArm.R", (-6.5, 0, 24),   (-6.5, 0, 19),      "Shoulder.R")
make_bone("Forearm.R",  (-6.5, 0, 19),   (-6.5, 0, 13),      "UpperArm.R")
make_bone("Hand.R",     (-6.5, 1.0, 12), (-6.5, 3.0, 9),       "Forearm.R")
make_bone("Socket_Hand_R", (-7.5, 1.0, 10.5), (-7.5, 2.5, 10.5), "Hand.R")

# Claw Slash Trail VFX Bones (Parented to Root for world space sweep plane)
make_bone("ClawTrail.L", (7.0, 7.0, 17.0), (7.0, 11.0, 12.0), "Root")
make_bone("ClawTrail.R", (-7.0, 7.0, 17.0), (-7.0, 11.0, 12.0), "Root")

# Left Leg Chain
make_bone("UpperLeg.L", (3.5, 0, 14),      (3.5, 0, 9),        "Hips")
make_bone("LowerLeg.L", (3.5, 0, 9),       (3.5, 0, 4),        "UpperLeg.L")
make_bone("Foot.L",     (3.5, 0, 4),       (3.5, 3.0, 0),        "LowerLeg.L")

# Right Leg Chain
make_bone("UpperLeg.R", (-3.5, 0, 14),     (-3.5, 0, 9),       "Hips")
make_bone("LowerLeg.R", (-3.5, 0, 9),      (-3.5, 0, 4),       "UpperLeg.R")
make_bone("Foot.R",     (-3.5, 0, 4),      (-3.5, 3.0, 0),       "LowerLeg.R")

bpy.ops.object.mode_set(mode='OBJECT')

# Assign Rigid Vertex Groups
ALL_BONE_NAMES = [b.name for b in arm_obj.data.bones]
for bname in ALL_BONE_NAMES:
    zombie_obj.vertex_groups.new(name=bname)

for vidx, bname in vert_groups.items():
    if bname in zombie_obj.vertex_groups:
        zombie_obj.vertex_groups[bname].add([vidx], 1.0, 'REPLACE')

# Planar Quad Dissolve (optimizes flat voxel faces)
bpy.context.view_layer.objects.active = zombie_obj
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.dissolve_limited(angle_limit=0.0001)
bpy.ops.mesh.tris_convert_to_quads()
bpy.ops.object.mode_set(mode='OBJECT')

print(f">>> Optimized Watertight Mesh: {len(zombie_obj.data.vertices)} verts, {len(zombie_obj.data.polygons)} polys.")

# Bind Armature Modifier
arm_mod = zombie_obj.modifiers.new(name="Armature", type='ARMATURE')
arm_mod.object = arm_obj
arm_mod.use_vertex_groups = True
zombie_obj.parent = arm_obj

# -----------------------------------------------------------------
# 6. Keyframe Animation: Shambling Walk (1-40) & 5-Phase Attack (41-80)
# -----------------------------------------------------------------
print(">>> Keyframing 80-Frame Animation with Game-Feel Juice...")
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')

pb = arm_obj.pose.bones
for name in ALL_BONE_NAMES:
    pb[name].rotation_mode = 'XYZ'

def kf(bone, frame, loc=None, rot=None, scale=None):
    if loc is not None:
        bone.location = loc
        bone.keyframe_insert(data_path="location", frame=frame)
    if rot is not None:
        bone.rotation_euler = (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]))
        bone.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale is not None:
        bone.scale = scale
        bone.keyframe_insert(data_path="scale", frame=frame)

# Animation Choreography (80 frames @ 30fps)
timeline_data = [
    # -------------------------------------------------------------
    # PHASE A: BERSERK SHAMBLING WALK CYCLE (Frames 1–40)
    # -------------------------------------------------------------
    # Frame 1: Limping Stride Contact (Right foot forward, Left leg dragging back)
    (1, {
        "Hips":        ((0, 0, 0), (-4, 3, -2), (1, 1, 1)),
        "Spine":       (None, (-8, 0, -2), None),
        "Chest":       (None, (-6, -2, 2), None),
        "Neck":        (None, (8, 4, -3), None),
        "Head":        (None, (8, 6, -4), None),
        "Shoulder.L":  (None, (0, 0, 0), None),
        "UpperArm.L":  (None, (42, -6, 10), None),
        "Forearm.L":   (None, (20, 0, 5), None),
        "Hand.L":      (None, (-15, 0, -5), None),
        "Shoulder.R":  (None, (0, 0, 0), None),
        "UpperArm.R":  (None, (50, 6, -10), None),
        "Forearm.R":   (None, (15, 0, -5), None),
        "Hand.R":      (None, (-20, 0, 5), None),
        "UpperLeg.L":  (None, (-18, 0, 4), None),
        "LowerLeg.L":  (None, (-15, 0, 0), None),
        "Foot.L":      (None, (12, 0, 0), None),
        "UpperLeg.R":  (None, (22, 0, -4), None),
        "LowerLeg.R":  (None, (-5, 0, 0), None),
        "Foot.R":      (None, (-10, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 10: Vault over right foot, Trove bounce up
    (10, {
        "Hips":        ((0, 0.012, 0.012), (-3, 2, 2), (1, 1, 1)),
        "Spine":       (None, (-10, 0, 2), None),
        "Chest":       (None, (-6, 0, 2), None),
        "Neck":        (None, (6, -2, 1), None),
        "Head":        (None, (6, -4, 3), None),
        "UpperArm.L":  (None, (36, -4, 8), None),
        "UpperArm.R":  (None, (44, 4, -8), None),
        "UpperLeg.L":  (None, (-5, 0, 4), None),
        "LowerLeg.L":  (None, (-18, 0, 0), None),
        "Foot.L":      (None, (15, 0, 0), None),
        "UpperLeg.R":  (None, (6, 0, -3), None),
        "LowerLeg.R":  (None, (-2, 0, 0), None),
        "Foot.R":      (None, (0, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 20: Heavy Limp Drop on Left Foot
    (20, {
        "Hips":        ((-0.008, 0.020, -0.014), (-5, -4, 3), (1, 1, 1)),
        "Spine":       (None, (-12, 0, -2), None),
        "Chest":       (None, (-8, 0, -2), None),
        "Neck":        (None, (10, -4, 4), None),
        "Head":        (None, (10, -8, 6), None),
        "UpperArm.L":  (None, (50, -8, 12), None),
        "UpperArm.R":  (None, (38, 8, -6), None),
        "UpperLeg.L":  (None, (18, 0, 5), None),
        "LowerLeg.L":  (None, (-8, 0, 0), None),
        "Foot.L":      (None, (-8, 0, 0), None),
        "UpperLeg.R":  (None, (-15, 0, -4), None),
        "LowerLeg.R":  (None, (-12, 0, 0), None),
        "Foot.R":      (None, (10, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 30: Recovery step: Right leg swings back forward
    (30, {
        "Hips":        ((0, 0.008, 0.006), (-3, 2, -1), (1, 1, 1)),
        "Spine":       (None, (-9, 0, 0), None),
        "Chest":       (None, (-6, 0, 0), None),
        "Neck":        (None, (6, 2, -1), None),
        "Head":        (None, (6, 4, -2), None),
        "UpperArm.L":  (None, (42, 0, 8), None),
        "UpperArm.R":  (None, (48, 0, -8), None),
        "UpperLeg.L":  (None, (6, 0, 3), None),
        "LowerLeg.L":  (None, (-4, 0, 0), None),
        "Foot.L":      (None, (-2, 0, 0), None),
        "UpperLeg.R":  (None, (10, 0, -3), None),
        "LowerLeg.R":  (None, (-16, 0, 0), None),
        "Foot.R":      (None, (8, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 40: Seamless Walk Loop Reset (Matches Frame 1)
    (40, {
        "Hips":        ((0, 0, 0), (-4, 3, -2), (1, 1, 1)),
        "Spine":       (None, (-8, 0, -2), None),
        "Chest":       (None, (-6, -2, 2), None),
        "Neck":        (None, (8, 4, -3), None),
        "Head":        (None, (8, 6, -4), None),
        "Shoulder.L":  (None, (0, 0, 0), None),
        "UpperArm.L":  (None, (42, -6, 10), None),
        "Forearm.L":   (None, (20, 0, 5), None),
        "Hand.L":      (None, (-15, 0, -5), None),
        "Shoulder.R":  (None, (0, 0, 0), None),
        "UpperArm.R":  (None, (50, 6, -10), None),
        "Forearm.R":   (None, (15, 0, -5), None),
        "Hand.R":      (None, (-20, 0, 5), None),
        "UpperLeg.L":  (None, (-18, 0, 4), None),
        "LowerLeg.L":  (None, (-15, 0, 0), None),
        "Foot.L":      (None, (12, 0, 0), None),
        "UpperLeg.R":  (None, (22, 0, -4), None),
        "LowerLeg.R":  (None, (-5, 0, 0), None),
        "Foot.R":      (None, (-10, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),

    # -------------------------------------------------------------
    # PHASE B: 5-PHASE EXPLOSIVE DOUBLE-CLAW LUNGE ATTACK (Frames 41–80)
    # -------------------------------------------------------------
    # Frame 44 (Phase 1a: Alert Crouch, Claws Tensing)
    (44, {
        "Hips":        ((0, -0.015, -0.022), (-6, 0, 0), (1, 1, 1)),
        "Spine":       (None, (-12, 0, 0), None),
        "Chest":       (None, (-10, 0, 0), None),
        "Neck":        (None, (10, 0, 0), None),
        "Head":        (None, (14, 0, 0), None),
        "UpperArm.L":  (None, (20, 0, 18), None),
        "Forearm.L":   (None, (-20, 0, 0), None),
        "UpperArm.R":  (None, (20, 0, -18), None),
        "Forearm.R":   (None, (-20, 0, 0), None),
        "UpperLeg.L":  (None, (15, 0, 5), None),
        "LowerLeg.L":  (None, (-25, 0, 0), None),
        "UpperLeg.R":  (None, (-10, 0, -5), None),
        "LowerLeg.R":  (None, (-20, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 50 (Phase 1b: Deep Kinetic Coil Back, Arms Raised Overhead, Threat Snarl)
    (50, {
        "Hips":        ((0, -0.045, -0.028), (10, 0, 0), (1, 1, 1)),
        "Spine":       (None, (16, 0, 0), None),
        "Chest":       (None, (14, 0, 0), None),
        "Neck":        (None, (14, 0, 0), None),
        "Head":        (None, (22, 0, 0), None),
        "Shoulder.L":  (None, (0, 0, 15), None),
        "UpperArm.L":  (None, (-60, -14, 28), None),
        "Forearm.L":   (None, (-40, 0, 12), None),
        "Hand.L":      (None, (-25, 0, -8), None),
        "Shoulder.R":  (None, (0, 0, -15), None),
        "UpperArm.R":  (None, (-65, 14, -28), None),
        "Forearm.R":   (None, (-45, 0, -12), None),
        "Hand.R":      (None, (-30, 0, 8), None),
        "UpperLeg.L":  (None, (-22, 0, 6), None),
        "LowerLeg.L":  (None, (-32, 0, 0), None),
        "UpperLeg.R":  (None, (14, 0, -6), None),
        "LowerLeg.R":  (None, (-26, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 53 (Phase 2a: Explosive Lunge Acceleration)
    (53, {
        "Hips":        ((0, 0.028, -0.022), (-4, 0, 0), (1, 1, 1)),
        "Spine":       (None, (-4, 0, 0), None),
        "Chest":       (None, (-4, 0, 0), None),
        "Neck":        (None, (8, 0, 0), None),
        "Head":        (None, (10, 0, 0), None),
        "UpperArm.L":  (None, (25, 0, 12), None),
        "Forearm.L":   (None, (18, 0, 0), None),
        "UpperArm.R":  (None, (28, 0, -12), None),
        "Forearm.R":   (None, (20, 0, 0), None),
        "ClawTrail.L": (None, None, (0.45, 0.45, 0.45)),
        "ClawTrail.R": (None, None, (0.45, 0.45, 0.45)),
    }),
    # Frame 56 (Phase 2b: PEAK IMPACT - EXPLOSIVE DOWNWARD DOUBLE-CLAW SLASH LUNGE!)
    (56, {
        "Hips":        ((0, 0.055, -0.028), (-5, 0, 0), (1, 1, 1)),
        "Spine":       (None, (-7, 0, 0), None),
        "Chest":       (None, (-7, 0, 0), None),
        "Neck":        (None, (12, 0, 0), None),
        "Head":        (None, (15, 0, 0), None),
        "Shoulder.L":  (None, (0, 0, 5), None),
        "UpperArm.L":  (None, (48, -6, 10), None),
        "Forearm.L":   (None, (30, 0, 5), None),
        "Hand.L":      (None, (18, 0, 0), None),
        "Shoulder.R":  (None, (0, 0, -5), None),
        "UpperArm.R":  (None, (54, 6, -10), None),
        "Forearm.R":   (None, (35, 0, -5), None),
        "Hand.R":      (None, (22, 0, 0), None),
        "UpperLeg.L":  (None, (20, 0, 5), None),
        "LowerLeg.L":  (None, (-30, 0, 0), None),
        "Foot.L":      (None, (12, 0, 0), None),
        "UpperLeg.R":  (None, (-18, 0, -5), None),
        "LowerLeg.R":  (None, (-10, 0, 0), None),
        "Foot.R":      (None, (-10, 0, 0), None),
        "ClawTrail.L": (None, None, (1.0, 1.0, 1.0)),
        "ClawTrail.R": (None, None, (1.0, 1.0, 1.0)),
    }),
    # Frame 60 (Phase 3: Overshoot / Momentum Extension)
    (60, {
        "Hips":        ((0, 0.070, -0.032), (-6, 0, 0), (1, 1, 1)),
        "Spine":       (None, (-11, 0, 0), None),
        "Chest":       (None, (-8, 0, 0), None),
        "UpperArm.L":  (None, (58, 0, 8), None),
        "UpperArm.R":  (None, (62, 0, -8), None),
        "ClawTrail.L": (None, None, (0.40, 0.40, 0.40)),
        "ClawTrail.R": (None, None, (0.40, 0.40, 0.40)),
    }),
    # Frame 63 (Trail Dissolves)
    (63, {
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 66 (Phase 4: Zanshin / Hit-Stop Rigid Hold)
    (66, {
        "Hips":        ((0, 0.052, -0.026), (-4, 0, 0), (1, 1, 1)),
        "Spine":       (None, (-8, 0, 0), None),
        "Chest":       (None, (-6, 0, 0), None),
        "Head":        (None, (12, 0, 0), None),
        "UpperArm.L":  (None, (48, 0, 10), None),
        "UpperArm.R":  (None, (52, 0, -10), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 70 (Recoil Breath Shudder - micro-tremor)
    (70, {
        "Chest":       (None, (-8, 2, -1), None),
        "Head":        (None, (10, -2, 2), None),
    }),
    # Frame 75 (Phase 5: Recovery Stumble)
    (75, {
        "Hips":        ((0, 0.022, -0.012), (-4, 2, -1), (1, 1, 1)),
        "Spine":       (None, (-8, 0, 0), None),
        "Chest":       (None, (-6, 0, 0), None),
        "UpperArm.L":  (None, (44, 0, 8), None),
        "UpperArm.R":  (None, (50, 0, -10), None),
        "UpperLeg.L":  (None, (6, 0, 0), None),
        "LowerLeg.L":  (None, (-14, 0, 0), None),
        "UpperLeg.R":  (None, (-6, 0, 0), None),
        "LowerLeg.R":  (None, (-10, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 80: Full Reset back to Walk Stance (Matches Frame 1)
    (80, {
        "Hips":        ((0, 0, 0), (-4, 3, -2), (1, 1, 1)),
        "Spine":       (None, (-8, 0, -2), None),
        "Chest":       (None, (-6, -2, 2), None),
        "Neck":        (None, (8, 4, -3), None),
        "Head":        (None, (8, 6, -4), None),
        "Shoulder.L":  (None, (0, 0, 0), None),
        "UpperArm.L":  (None, (42, -6, 10), None),
        "Forearm.L":   (None, (20, 0, 5), None),
        "Hand.L":      (None, (-15, 0, -5), None),
        "Shoulder.R":  (None, (0, 0, 0), None),
        "UpperArm.R":  (None, (50, 6, -10), None),
        "Forearm.R":   (None, (15, 0, -5), None),
        "Hand.R":      (None, (-20, 0, 5), None),
        "UpperLeg.L":  (None, (-18, 0, 4), None),
        "LowerLeg.L":  (None, (-15, 0, 0), None),
        "Foot.L":      (None, (12, 0, 0), None),
        "UpperLeg.R":  (None, (22, 0, -4), None),
        "LowerLeg.R":  (None, (-5, 0, 0), None),
        "Foot.R":      (None, (-10, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
]

for frame_idx, bone_dict in timeline_data:
    for bname, transforms in bone_dict.items():
        loc, rot, scale = transforms
        if bname in pb:
            kf(pb[bname], frame_idx, loc=loc, rot=rot, scale=scale)

bpy.ops.object.mode_set(mode='OBJECT')

# Set Interpolation to BEZIER with Snappy Ease Out
if arm_obj.animation_data and arm_obj.animation_data.action:
    arm_obj.animation_data.action.name = "Bloody_Zombie_Action"
    for fcurve in arm_obj.animation_data.action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.easing = 'EASE_OUT'

# -----------------------------------------------------------------
# 7. Lighting & Camera Setup with Depsgraph Auto-Framing
# -----------------------------------------------------------------
print(">>> Setting up Studio Lighting & AgX Camera...")

# Dark atmospheric studio background
if scene.world is None:
    scene.world = bpy.data.worlds.new("World")
scene.world.use_nodes = True
bg_node = scene.world.node_tree.nodes.get("Background")
if not bg_node:
    bg_node = scene.world.node_tree.nodes.new(type='ShaderNodeBackground')
    out_node = scene.world.node_tree.nodes.get("World Output") or scene.world.node_tree.nodes.new(type='ShaderNodeOutputWorld')
    scene.world.node_tree.links.new(bg_node.outputs['Background'], out_node.inputs['Surface'])
bg_node.inputs['Color'].default_value = (0.012, 0.016, 0.024, 1.0)
bg_node.inputs['Strength'].default_value = 0.50

# 4-Point High-Fidelity Studio Lighting
# 1) Key Sun Light: Directional glint casting crisp micro-voxel shadows across ribs, skull fracture & teeth
key_sun = bpy.data.objects.new("Key_Sun", bpy.data.lights.new("Key_Sun", type='SUN'))
key_sun.data.energy = 3.2
key_sun.data.color = (1.0, 0.98, 0.95)
key_sun.data.angle = math.radians(4)
key_sun.rotation_euler = (math.radians(-42), math.radians(22), math.radians(135))
bpy.context.collection.objects.link(key_sun)

# 2) Front Specular Fill Light: Illuminates face, glowing eye, wet blood, and claws (balanced to avoid washing out red into pink)
front_fill = bpy.data.objects.new("Front_Fill", bpy.data.lights.new("Front_Fill", type='AREA'))
front_fill.data.energy = 65.0
front_fill.data.color = (0.92, 0.95, 1.00)
front_fill.data.size = 2.4
front_fill.location = (-0.8, 1.6, 0.8)
front_fill.rotation_euler = (math.radians(35), math.radians(-20), math.radians(-40))
bpy.context.collection.objects.link(front_fill)

# 3) Arterial Crimson Rim Backlight: Accentuates gore silhouette & edges in rich deep red
rim_crimson = bpy.data.objects.new("Rim_Crimson", bpy.data.lights.new("Rim_Crimson", type='AREA'))
rim_crimson.data.energy = 360.0
rim_crimson.data.color = (0.98, 0.02, 0.05)
rim_crimson.data.size = 2.2
rim_crimson.location = (1.5, -1.2, 0.9)
rim_crimson.rotation_euler = (math.radians(-40), math.radians(40), math.radians(120))
bpy.context.collection.objects.link(rim_crimson)

# 4) Deep Shadow Fill Light: Soft ambient mood
dark_fill = bpy.data.objects.new("Fill_Shadow", bpy.data.lights.new("Fill_Shadow", type='AREA'))
dark_fill.data.energy = 45.0
dark_fill.data.color = (0.12, 0.06, 0.10)
dark_fill.data.size = 3.0
dark_fill.location = (0.6, 1.5, -0.1)
bpy.context.collection.objects.link(dark_fill)

# Depsgraph Camera Framing at Peak Action Frame 56
ACTION_FRAME = 56
scene.frame_set(ACTION_FRAME)
depsgraph = bpy.context.evaluated_depsgraph_get()

all_corners = []
for obj in scene.objects:
    if obj.type == 'MESH' and not obj.hide_render:
        eval_obj = obj.evaluated_get(depsgraph)
        mat = eval_obj.matrix_world
        all_corners.extend([mat @ Vector(corner) for corner in eval_obj.bound_box])

if all_corners:
    min_co = Vector((min(c.x for c in all_corners), min(c.y for c in all_corners), min(c.z for c in all_corners)))
    max_co = Vector((max(c.x for c in all_corners), max(c.y for c in all_corners), max(c.z for c in all_corners)))
    center = (min_co + max_co) * 0.5
    span = (max_co - min_co).length
else:
    center = Vector((0, 0.08, 0.35))
    span = 0.78

print(f">>> Evaluated Scene Center: {center}, Span: {span:.3f}m")

# Independent Static Camera Target
cam_target = bpy.data.objects.new("CamTarget_BloodyZombie", None)
cam_target.location = Vector((center.x * 0.15, center.y + 0.03, center.z + span * 0.05))
bpy.context.collection.objects.link(cam_target)

# Heroic Front 3/4 Perspective Camera
cam_data = bpy.data.cameras.new("BloodyZombie_HeroCamera")
cam_data.lens = 48
cam_obj = bpy.data.objects.new("BloodyZombie_HeroCamera", object_data=cam_data)

fov_rad = cam_obj.data.angle
dist = (span * 0.5) / math.tan(fov_rad * 0.5) * 0.82

# Camera placed at -X, +Y, +Z to view face, glowing bloodlust eye, skull fissure, 3D ribs, and slashing claws:
cam_obj.location = cam_target.location + Vector((-dist * 0.48, dist * 0.80, dist * 0.42))

track = cam_obj.constraints.new(type='TRACK_TO')
track.target = cam_target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Render Settings (Cycles, AgX High Contrast, 1024x1024)
scene.render.engine = 'CYCLES'
try:
    cpref = bpy.context.preferences.addons['cycles'].preferences
    cpref.compute_device_type = 'CUDA'
    for d in cpref.devices:
        d.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print("GPU compute fallback to CPU:", e)
    scene.cycles.device = 'CPU'

scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.view_settings.view_transform = 'AgX' if hasattr(scene.view_settings, 'view_transform') else 'Filmic'
scene.view_settings.look = 'AgX - High Contrast'

# -----------------------------------------------------------------
# 8. Render & Save Deliverables
# -----------------------------------------------------------------
output_dir = os.path.dirname(os.path.abspath(__file__))
render_filepath = os.path.join(output_dir, "bloody_zombie_render.png")
blend_filepath = os.path.join(output_dir, "bloody_zombie.blend")
glb_filepath = os.path.join(output_dir, "bloody_zombie.glb")
data_js_filepath = os.path.join(output_dir, "bloody_zombie_data.js")

print(f">>> Saving Blender project to: {blend_filepath}")
bpy.ops.wm.save_as_mainfile(filepath=blend_filepath)

# glTF 2.0 Modern Export Contract (Blender 4.2+)
print(f">>> Exporting game-ready GLB to: {glb_filepath}")
scene.frame_set(1)
bpy.ops.export_scene.gltf(
    filepath=glb_filepath,
    export_format='GLB',
    export_animations=True,
    export_skins=True,
    export_all_influences=False,
    export_apply=False,
    export_yup=True
)

print(f">>> Rendering beauty shot (Peak Impact Frame {ACTION_FRAME}) to: {render_filepath}")
scene.frame_set(ACTION_FRAME)
scene.render.filepath = render_filepath
bpy.ops.render.render(write_still=True)

# Generate Base64 Data JS
print(f">>> Baking Zero-CORS Base64 Data JS to: {data_js_filepath}")
with open(glb_filepath, 'rb') as f:
    glb_b64 = base64.b64encode(f.read()).decode('utf-8')

with open(data_js_filepath, 'w', encoding='utf-8') as f:
    f.write(f'window.BLOODY_ZOMBIE_BASE64 = "data:model/gltf-binary;base64,{glb_b64}";\n')

# Mandatory Clean-up: Delete all .blend1 and test_*.png files
blend1_filepath = os.path.join(output_dir, "bloody_zombie.blend1")
if os.path.exists(blend1_filepath):
    try:
        os.remove(blend1_filepath)
    except Exception:
        pass
for fname in os.listdir(output_dir):
    if fname.startswith("test_") and fname.endswith(".png"):
        try:
            os.remove(os.path.join(output_dir, fname))
        except Exception:
            pass

print(">>> [SUCCESS] Bloody Zombie Generation Completed deterministically!")
print("=================================================================")
