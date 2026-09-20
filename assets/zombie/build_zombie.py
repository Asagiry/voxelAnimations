import bpy
import math
import os
import base64
from mathutils import Vector, Matrix

print("=================================================================")
print(">>> [TROVE VOXEL ARTISAN] Authentic Trove Chibi Biped: Undead Zombie")
print(">>> Segmented Floating Limbs | Multi-Layer Micro-Voxel Relief")
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
    # 1. Rotting Olive Flesh
    'flesh_green':    make_shader('M_FleshGreen',    (0.075, 0.160, 0.068, 1.0), roughness=0.65, metallic=0.05),
    # 2. Shadowed Gangrenous Flesh
    'flesh_dark':     make_shader('M_FleshDark',     (0.040, 0.088, 0.038, 1.0), roughness=0.70, metallic=0.05),
    # 3. Decayed Ivory Bone (Skull, Ribs, Talons)
    'decayed_bone':   make_shader('M_DecayedBone',   (0.580, 0.540, 0.440, 1.0), roughness=0.45, metallic=0.10),
    # 4. Bone Highlight (Tooth pegs, rib tips, claw tips)
    'bone_highlight': make_shader('M_BoneHighlight', (0.740, 0.700, 0.600, 1.0), roughness=0.35, metallic=0.10),
    # 5. Shredded Dark Tunic / Trousers
    'cloth_dark':     make_shader('M_ClothDark',     (0.024, 0.032, 0.042, 1.0), roughness=0.85, metallic=0.02),
    # 6. Tattered Leather / Belt / Wraps
    'cloth_tattered': make_shader('M_ClothTattered', (0.068, 0.044, 0.030, 1.0), roughness=0.80, metallic=0.05),
    # 7. Corroded Bronze / Metal Buckle
    'buckle_bronze':  make_shader('M_BuckleBronze',  (0.360, 0.280, 0.120, 1.0), roughness=0.35, metallic=0.85),
    # 8. Dark Wound Cavity / Dried Blood Fissure
    'wound_dark':     make_shader('M_WoundDark',     (0.046, 0.009, 0.009, 1.0), roughness=0.50, metallic=0.15),
    # 9. Eerie Glowing Undead Eyes (Toxic Yellow-Green)
    'eye_glow':       make_shader('M_EyeGlow',       (0.480, 0.850, 0.020, 1.0), roughness=0.10, metallic=0.00, emission=2.2, emission_color=(0.55, 0.95, 0.05, 1.0)),
    # 10. Dark Scalp / Straggly Hair Strands
    'hair_dark':      make_shader('M_HairDark',      (0.015, 0.018, 0.022, 1.0), roughness=0.90, metallic=0.02),
    # 11. Heavy Combat Boot Sole
    'boot_sole':      make_shader('M_BootSole',      (0.012, 0.015, 0.018, 1.0), roughness=0.90, metallic=0.10),
    # 12. Geometric Claw Slash Trail (Toxic Lime Green)
    'slash_trail':    make_shader('M_SlashTrail',    (0.280, 0.820, 0.050, 1.0), roughness=0.15, metallic=0.00, emission=2.2, emission_color=(0.32, 0.90, 0.08, 1.0)),
    'slash_core':     make_shader('M_SlashCore',     (0.750, 0.980, 0.350, 1.0), roughness=0.10, metallic=0.00, emission=2.8, emission_color=(0.80, 1.00, 0.40, 1.0)),
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

print(">>> [1/5] Synthesizing Authentic Trove Chibi Voxel Anatomy...")

# --- 3.1 LEFT LEG: Combat Boot, Rotting Calf, Tattered Trouser ---
# Foot.L (Z = 0..3) - Chunky Distinct Voxel Block (4 wide x 6 long x 4 high)
for x in range(2, 6):
    for y in range(-2, 4):
        set_vox(x, y, 0, 'boot_sole', 'Foot.L', True)
        set_vox(x, y, 1, 'cloth_dark', 'Foot.L', True)
        set_vox(x, y, 2, 'cloth_dark', 'Foot.L', True)
        m_top = 'cloth_tattered' if (y in (-2, 3) or x in (2, 5) or y == 1) else 'cloth_dark'
        set_vox(x, y, 3, m_top, 'Foot.L', True)

# ANKLE JOINT GAP: Z = 4 is 1-voxel empty air!

# LowerLeg.L (Z = 5..8) - 2x2 Calf Strut
for z in range(5, 9):
    for x in (3, 4):
        for y in (0, 1):
            m = 'cloth_tattered' if z == 7 else ('flesh_dark' if y == 0 else 'flesh_green')
            set_vox(x, y, z, m, 'LowerLeg.L', True)

# UpperLeg.L (Z = 9..12) - 2x2 Thigh Strut
for z in range(9, 13):
    for x in (3, 4):
        for y in (0, 1):
            m = 'flesh_dark' if (z == 9 and y == 1) else 'cloth_dark'
            set_vox(x, y, z, m, 'UpperLeg.L', True)

# --- 3.2 RIGHT LEG: Bare Skeletal Foot, Exposed Shin Bone, Torn Knee ---
# Foot.R (Z = 0..3) - Chunky Distinct Skeletal Sabaton (4 wide x 6 long x 4 high)
for x in range(-5, -1):
    for y in range(-2, 4):
        set_vox(x, y, 0, 'decayed_bone', 'Foot.R', True)
        m = 'wound_dark' if ((x == -4 and y == 0) or (x == -3 and y == 1)) else 'decayed_bone'
        set_vox(x, y, 1, m, 'Foot.R', True)

for x in (-4, -3):
    for y in (-1, 2):
        set_vox(x, y, 2, 'decayed_bone', 'Foot.R', True)
set_vox(-4, -2, 2, 'bone_highlight', 'Foot.R', True)  # Heel spur

set_vox(-4, 0, 3, 'bone_highlight', 'Foot.R', True)
set_vox(-3, 0, 3, 'decayed_bone', 'Foot.R', True)
set_vox(-4, 1, 3, 'decayed_bone', 'Foot.R', True)
set_vox(-3, 1, 3, 'decayed_bone', 'Foot.R', True)

# ANKLE JOINT GAP: Z = 4 is 1-voxel empty air!

# LowerLeg.R (Z = 5..8) - 2x2 Strut with EXPOSED TIBIA SHIN BONE
for z in range(5, 9):
    for x in (-4, -3):
        for y in (0, 1):
            if y == 1:
                set_vox(x, y, z, 'bone_highlight' if x == -3 else 'decayed_bone', 'LowerLeg.R', True)
            else:
                set_vox(x, y, z, 'flesh_dark' if z % 2 == 0 else 'wound_dark', 'LowerLeg.R', True)

# UpperLeg.R (Z = 9..12) - 2x2 Thigh Strut
for z in range(9, 13):
    for x in (-4, -3):
        for y in (0, 1):
            m = 'decayed_bone' if (z == 9 and y == 1) else ('cloth_tattered' if (x + z) % 2 == 0 else 'cloth_dark')
            set_vox(x, y, z, m, 'UpperLeg.R', True)

# --- 3.3 PELVIS, WAIST & EXTRUDED BELT BUCKLE (Z = 13..16) ---
# Pelvis (Z = 13..15) - 8 wide x 6 deep x 3 high
for z in range(13, 16):
    for x in range(-4, 4):
        for y in range(-3, 3):
            if z == 13 and (y in (-3, 2) or abs(x) in (3, 4)):
                m = 'cloth_tattered'
            elif x <= -2 and y >= 1 and z == 14:
                m = 'wound_dark'
            else:
                m = 'cloth_dark'
            set_vox(x, y, z, m, 'Hips', True)

# Waist & Belt Perimeter (Z = 16)
for x in range(-4, 4):
    for y in range(-3, 3):
        is_perimeter = (x in (-4, 3) or y in (-3, 2))
        m = 'cloth_tattered' if is_perimeter else 'cloth_dark'
        set_vox(x, y, 16, m, 'Hips', True)

# Belt Buckle Extruded Forward (+1 voxel relief at Y = 3, Z = 16)
set_vox(-1, 3, 16, 'buckle_bronze', 'Hips', True)
set_vox(0, 3, 16, 'buckle_bronze', 'Hips', True)
set_vox(-2, 3, 16, 'cloth_tattered', 'Hips', True)
set_vox(1, 3, 16, 'cloth_tattered', 'Hips', True)

# --- 3.4 TORSO & CHEST: DEEP WOUND CAVITY & 3 PAIRS OF CURVED 3D BONE RIBS (Z = 17..24) ---
# Chest Base (8 wide x 6 deep x 8 high)
for z in range(17, 25):
    for x in range(-4, 4):
        for y in range(-3, 3):
            # Rear vertebral spine ridge (Y = -3)
            if y == -3 and x in (-1, 0):
                set_vox(x, y, z, 'decayed_bone' if z in (18, 20, 22, 24) else 'cloth_tattered', 'Chest', True)
                continue
            
            # Recessed Wound Cavity: X in [-3, 1], Y in [0, 2], Z in [18, 23]
            is_cavity = (-3 <= x <= 1 and 0 <= y <= 2 and 18 <= z <= 23)
            if is_cavity:
                if y <= 1:
                    set_vox(x, y, z, 'wound_dark', 'Chest', True)
            else:
                if x >= 1:
                    m = 'flesh_green' if (z >= 22 or y >= 1) else 'cloth_dark'
                else:
                    m = 'cloth_dark' if (x == -4 or z == 17) else 'flesh_dark'
                set_vox(x, y, z, m, 'Chest', True)

# Rear Vertebral Spikes (Y = -4 at Z = 20, 22, 24)
set_vox(0, -4, 20, 'bone_highlight', 'Chest', True)
set_vox(-1, -4, 22, 'bone_highlight', 'Chest', True)
set_vox(0, -4, 24, 'bone_highlight', 'Chest', True)

# Clavicles / Collar Bones (Z = 24, Y = 2)
for x in (-3, -2, -1, 0, 1, 2):
    set_vox(x, 2, 24, 'decayed_bone', 'Chest', True)

# -----------------------------------------------------------------
# 3 PAIRS OF CURVED 3D BONE RIBS (Protruding +1 to +2 voxels forward!)
# -----------------------------------------------------------------
# Lower Rib Pair (Z = 19) -> Protrudes forward to Y = 3 (+1 voxel forward)
set_vox(-3, 1, 19, 'decayed_bone', 'Chest', True)
set_vox(-3, 2, 19, 'decayed_bone', 'Chest', True)
set_vox(-2, 3, 19, 'decayed_bone', 'Chest', True)
set_vox(-1, 3, 19, 'bone_highlight', 'Chest', True)

set_vox(2, 1, 19, 'decayed_bone', 'Chest', True)
set_vox(2, 2, 19, 'decayed_bone', 'Chest', True)
set_vox(1, 3, 19, 'decayed_bone', 'Chest', True)
set_vox(0, 3, 19, 'bone_highlight', 'Chest', True)

# Middle Rib Pair (Z = 21) -> APEX PROTRUSION to Y = 4 (+2 voxels forward!)
set_vox(-3, 1, 21, 'decayed_bone', 'Chest', True)
set_vox(-3, 2, 21, 'decayed_bone', 'Chest', True)
set_vox(-2, 3, 21, 'decayed_bone', 'Chest', True)
set_vox(-2, 4, 21, 'bone_highlight', 'Chest', True)
set_vox(-1, 4, 21, 'bone_highlight', 'Chest', True)

set_vox(2, 1, 21, 'decayed_bone', 'Chest', True)
set_vox(2, 2, 21, 'decayed_bone', 'Chest', True)
set_vox(1, 3, 21, 'decayed_bone', 'Chest', True)
set_vox(1, 4, 21, 'bone_highlight', 'Chest', True)
set_vox(0, 4, 21, 'bone_highlight', 'Chest', True)

# Upper Rib Pair (Z = 23) -> Protrudes forward to Y = 3 (+1 voxel forward)
set_vox(-3, 1, 23, 'decayed_bone', 'Chest', True)
set_vox(-3, 2, 23, 'decayed_bone', 'Chest', True)
set_vox(-2, 3, 23, 'decayed_bone', 'Chest', True)
set_vox(-1, 3, 23, 'bone_highlight', 'Chest', True)

set_vox(2, 1, 23, 'decayed_bone', 'Chest', True)
set_vox(2, 2, 23, 'decayed_bone', 'Chest', True)
set_vox(1, 3, 23, 'decayed_bone', 'Chest', True)
set_vox(0, 3, 23, 'bone_highlight', 'Chest', True)

# --- 3.5 PAULDRONS (SHOULDERS): FLOATING WITH 1-VOXEL BREATHING GAP FROM CHEST ---
# Right Pauldron (Shoulder.R) - Floating at X: -9..-6, Y: -3..2, Z: 23..26 (X = -5 is empty gap!)
for z in range(23, 27):
    for x in range(-9, -5):
        for y in range(-3, 3):
            m = 'decayed_bone' if (z >= 25 or y == 2) else 'cloth_dark'
            set_vox(x, y, z, m, 'Shoulder.R', True)

# Jagged bone spikes on right pauldron
set_vox(-8, 0, 27, 'bone_highlight', 'Shoulder.R', True)
set_vox(-7, 0, 27, 'decayed_bone', 'Shoulder.R', True)

# Left Pauldron (Shoulder.L) - Floating at X: 5..8, Y: -3..2, Z: 23..26 (X = 4 is empty gap!)
for z in range(23, 27):
    for x in range(5, 9):
        for y in range(-3, 3):
            is_rim = (x in (5, 8) or y in (-3, 2) or z in (23, 26))
            m = 'cloth_tattered' if (is_rim and z >= 25) else ('flesh_dark' if y == 2 else 'cloth_dark')
            set_vox(x, y, z, m, 'Shoulder.L', True)

# --- 3.6 LEFT ARM: UPPER ARM, FOREARM, WRIST GAP & CHUNKY FLOATING HAND ---
# UpperArm.L (Z = 19..23) - 2x2 Strut under pauldron
for z in range(19, 24):
    for x in (6, 7):
        for y in (-1, 0):
            m = 'cloth_dark' if z >= 22 else 'flesh_green'
            set_vox(x, y, z, m, 'UpperArm.L', True)

# Forearm.L (Z = 14..18) - 2x2 Strut with bandage wrap
for z in range(14, 19):
    for x in (6, 7):
        for y in (-1, 0):
            m = 'cloth_tattered' if z in (16, 17) else 'flesh_dark'
            set_vox(x, y, z, m, 'Forearm.L', True)

# WRIST GAP: Z = 13 is 1-voxel empty air!

# Hand.L (Z = 9..12) - Chunky Floating Hand (4 wide x 5 deep x 4 high)
for z in range(9, 13):
    for x in range(5, 9):
        for y in range(-1, 4):
            m = 'flesh_dark' if (y <= 0 or z == 9) else 'flesh_green'
            set_vox(x, y, z, m, 'Hand.L', True)

# Rotting Flesh Claws (protruding forward at Y = 4..5)
set_vox(5, 4, 11, 'flesh_dark', 'Hand.L', True)
set_vox(5, 5, 11, 'bone_highlight', 'Hand.L', True)
set_vox(6, 4, 10, 'flesh_green', 'Hand.L', True)
set_vox(6, 5, 10, 'bone_highlight', 'Hand.L', True)
set_vox(7, 4, 10, 'flesh_green', 'Hand.L', True)
set_vox(7, 5, 10, 'bone_highlight', 'Hand.L', True)
set_vox(8, 4, 11, 'flesh_dark', 'Hand.L', True)
set_vox(8, 5, 11, 'bone_highlight', 'Hand.L', True)

# --- 3.7 RIGHT ARM: UPPER ARM, SKELETAL RADIUS/ULNA, WRIST GAP & CHUNKY FLOATING TALONS ---
# UpperArm.R (Z = 19..23) - 2x2 Strut under pauldron
for z in range(19, 24):
    for x in (-8, -7):
        for y in (-1, 0):
            m = 'cloth_dark' if z >= 22 else 'flesh_dark'
            set_vox(x, y, z, m, 'UpperArm.R', True)

# Forearm.R (Z = 14..18) - TWIN SKELETAL RADIUS & ULNA STRUTS
for z in range(14, 19):
    set_vox(-8, -1, z, 'decayed_bone', 'Forearm.R', True)
    set_vox(-7, 0, z, 'decayed_bone', 'Forearm.R', True)
    if z == 16:
        set_vox(-8, 0, z, 'wound_dark', 'Forearm.R', True)

# WRIST GAP: Z = 13 is 1-voxel empty air!

# Hand.R (Z = 9..12) - Chunky Floating Skeletal Hand (4 wide x 5 deep x 4 high)
for z in range(9, 13):
    for x in range(-9, -5):
        for y in range(-1, 4):
            m = 'decayed_bone' if (y >= 1 or z >= 11) else 'wound_dark'
            set_vox(x, y, z, m, 'Hand.R', True)

# Sharp Skeletal Claws & Talons (protruding forward at Y = 4..5)
set_vox(-6, 4, 11, 'decayed_bone', 'Hand.R', True)
set_vox(-6, 5, 11, 'bone_highlight', 'Hand.R', True)
set_vox(-7, 4, 10, 'decayed_bone', 'Hand.R', True)
set_vox(-7, 5, 10, 'bone_highlight', 'Hand.R', True)
set_vox(-8, 4, 10, 'decayed_bone', 'Hand.R', True)
set_vox(-8, 5, 10, 'bone_highlight', 'Hand.R', True)
set_vox(-9, 4, 11, 'decayed_bone', 'Hand.R', True)
set_vox(-9, 5, 11, 'bone_highlight', 'Hand.R', True)

# --- 3.8 NECK & HEAD WITH MULTI-LAYERED MICRO-VOXEL RELIEF ---
# Neck (Z = 25) - 2x2 Strut
for x in (-1, 0):
    for y in (-1, 0):
        set_vox(x, y, 25, 'flesh_dark' if x == 0 else 'decayed_bone', 'Neck', True)

# Head Base (Z = 26..35) - 10 wide x 10 deep x 10 high base cranium
for z in range(26, 36):
    for x in range(-5, 5):
        for y in range(-5, 5):
            if x <= -1:
                m = 'decayed_bone'
            else:
                m = 'flesh_green' if (z >= 30 and y >= -1) else 'flesh_dark'
            set_vox(x, y, z, m, 'Head', True)

# SKULL CRACK ON RIGHT CRANIUM: Raised exposed ivory plates (+1 voxel step out to X = -6)
for z in range(31, 35):
    for y in (-1, 0, 1):
        set_vox(-6, y, z, 'decayed_bone', 'Head', True)

# Dark fissure cracks zigzagging through bone
set_vox(-5, 1, 34, 'wound_dark', 'Head', True)
set_vox(-5, 0, 33, 'wound_dark', 'Head', True)
set_vox(-5, 1, 32, 'wound_dark', 'Head', True)
set_vox(-5, 0, 31, 'wound_dark', 'Head', True)
set_vox(-4, 2, 33, 'wound_dark', 'Head', True)
set_vox(-4, 1, 34, 'wound_dark', 'Head', True)
set_vox(-6, 0, 32, 'wound_dark', 'Head', True)

# BROW RIDGE (+1 voxel extruded forward to Y = 5)
for x in range(-4, 4):
    m = 'decayed_bone' if x <= -1 else 'flesh_dark'
    set_vox(x, 5, 31, m, 'Head', True)

# RECESSED GLOWING EYES (Under Y = 5 brow ridge, recessed back at Y = 4)
# Left 2x2 Toxic Glowing Eye (X: 1..2, Z: 29..30)
set_vox(1, 4, 30, 'eye_glow', 'Head', True)
set_vox(2, 4, 30, 'eye_glow', 'Head', True)
set_vox(1, 4, 29, 'eye_glow', 'Head', True)
set_vox(2, 4, 29, 'eye_glow', 'Head', True)
# Dark bruised socket framing left eye
set_vox(0, 4, 30, 'flesh_dark', 'Head', True)
set_vox(3, 4, 30, 'flesh_dark', 'Head', True)
set_vox(0, 4, 29, 'flesh_dark', 'Head', True)
set_vox(3, 4, 29, 'flesh_dark', 'Head', True)

# Right Mismatched Asymmetrical Socket
set_vox(-2, 4, 29, 'eye_glow', 'Head', True)    # Pinpoint piercing glow
set_vox(-3, 4, 29, 'wound_dark', 'Head', True)  # Deep hollow fissure socket
set_vox(-3, 4, 30, 'wound_dark', 'Head', True)
set_vox(-2, 4, 30, 'wound_dark', 'Head', True)
set_vox(-4, 4, 30, 'decayed_bone', 'Head', True)
set_vox(-1, 4, 30, 'decayed_bone', 'Head', True)

# Sunken Nose Cavity (Z = 28)
set_vox(-1, 4, 28, 'wound_dark', 'Head', True)
set_vox(0, 4, 28, 'wound_dark', 'Head', True)

# JAW & AGGRESSIVE SNARL WITH PROTRUDING 1x1 VOXEL TOOTH PEGS
# Sunken mouth cavity (Y = 3, Z = 26..27)
for x in range(-3, 4):
    for z in (26, 27):
        set_vox(x, 3, z, 'wound_dark', 'Head', True)

# Jaw rim (Y = 4, Z = 26)
for x in range(-4, 4):
    set_vox(x, 4, 26, 'decayed_bone' if x <= -1 else 'flesh_dark', 'Head', True)

# Individual 1x1 Tooth Pegs protruding forward to Y = 5!
# Upper Teeth:
set_vox(-4, 5, 27, 'decayed_bone', 'Head', True)
set_vox(-3, 5, 27, 'decayed_bone', 'Head', True)
set_vox(-1, 5, 27, 'bone_highlight', 'Head', True)
set_vox(1, 5, 27, 'bone_highlight', 'Head', True)
set_vox(3, 5, 27, 'decayed_bone', 'Head', True)
# Lower Fangs:
set_vox(-4, 5, 26, 'decayed_bone', 'Head', True)
set_vox(-2, 5, 26, 'bone_highlight', 'Head', True)
set_vox(0, 5, 26, 'bone_highlight', 'Head', True)
set_vox(2, 5, 26, 'bone_highlight', 'Head', True)

# HAIR STRANDS & TUFTS (+1 TO +2 VOXELS RELIEF)
# Stepped layer across cranium top (Z = 36: +1 voxel relief)
for x in range(-3, 4):
    for y in range(-4, 2):
        if (x + y) % 2 == 0 or y <= -2:
            set_vox(x, y, 36, 'hair_dark', 'Head', True)

# Spiky Crest Tufts (Z = 37: +2 voxels relief!)
set_vox(-1, 0, 37, 'hair_dark', 'Head', True)
set_vox(0, 0, 37, 'hair_dark', 'Head', True)
set_vox(0, -2, 37, 'hair_dark', 'Head', True)
set_vox(1, -2, 37, 'hair_dark', 'Head', True)
set_vox(-2, -4, 37, 'hair_dark', 'Head', True)
set_vox(-1, -4, 37, 'hair_dark', 'Head', True)

# Back Hair Curtain (Y = -6: +1 voxel relief on rear)
for z in range(28, 35):
    for x in range(-3, 3):
        set_vox(x, -6, z, 'hair_dark', 'Head', True)
set_vox(-2, -6, 27, 'hair_dark', 'Head', True)
set_vox(0, -6, 27, 'hair_dark', 'Head', True)
set_vox(1, -6, 27, 'hair_dark', 'Head', True)

# Left Temple Hair Tuft (X = 5: +1 voxel relief on side)
for z in range(31, 34):
    for y in (-1, 0, 1):
        set_vox(5, y, z, 'hair_dark', 'Head', True)

# --- 3.9 GEOMETRIC TOXIC-GREEN CLAW SLASH TRAILS ---
def build_slash_ribbon(x_center, bone_name):
    N_STEPS = 22
    for st in range(N_STEPS):
        u = st / float(N_STEPS - 1)
        ang = -0.42 + u * (math.pi * 0.78)
        rad = 12.0
        cy = 5.2 + math.sin(ang) * rad
        cz = 22.0 - math.cos(ang) * rad * 0.90
        
        for dx in (-1, 0, 1):
            vx = x_center + dx
            for dy in (0, 1):
                m_trail = 'slash_core' if (dx == 0 and dy == 0) else 'slash_trail'
                set_vox(vx, cy + dy, cz, m_trail, bone_name, True)

build_slash_ribbon(7, 'ClawTrail.L')
build_slash_ribbon(-8, 'ClawTrail.R')

print(f">>> Total Generated Authentic Micro-Voxels: {len(voxels)} voxels.")

# -----------------------------------------------------------------
# 4. Watertight Boundary Quad Mesher & Optimization
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
mesh = bpy.data.meshes.new("Zombie_Mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

for m in used_mat_names:
    mesh.materials.append(mats[m])
for poly, slot in zip(mesh.polygons, face_mats):
    poly.material_index = slot

mesh.polygons.foreach_set('use_smooth', [False] * len(mesh.polygons))
mesh.update()

zombie_obj = bpy.data.objects.new("Zombie", mesh)
bpy.context.collection.objects.link(zombie_obj)

# -----------------------------------------------------------------
# 5. Skeletal Rigging & Standard Socket Architecture
# -----------------------------------------------------------------
print(">>> Rigging Clean Armature with Rigid Sockets...")
arm_data = bpy.data.armatures.new("Zombie_Armature_Data")
arm_obj = bpy.data.objects.new("Zombie_Armature", arm_data)
bpy.context.collection.objects.link(arm_obj)

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones

# 1) Root
b_root = eb.new("Root")
b_root.head = (0, 0, 0)
b_root.tail = (0, 0.08, 0)

# 2) Hips / Pelvis
b_hips = eb.new("Hips")
b_hips.parent = b_root
b_hips.head = (0, 0, 14 * VOXEL_SIZE)
b_hips.tail = (0, 0, 16 * VOXEL_SIZE)

# 3) Spine
b_spine = eb.new("Spine")
b_spine.parent = b_hips
b_spine.head = (0, 0, 16 * VOXEL_SIZE)
b_spine.tail = (0, 0, 20 * VOXEL_SIZE)

# 4) Chest
b_chest = eb.new("Chest")
b_chest.parent = b_spine
b_chest.head = (0, 0, 20 * VOXEL_SIZE)
b_chest.tail = (0, 0, 24 * VOXEL_SIZE)

# 5) Neck
b_neck = eb.new("Neck")
b_neck.parent = b_chest
b_neck.head = (0, 0, 24 * VOXEL_SIZE)
b_neck.tail = (0, 0, 26 * VOXEL_SIZE)

# 6) Head
b_head = eb.new("Head")
b_head.parent = b_neck
b_head.head = (0, 0, 26 * VOXEL_SIZE)
b_head.tail = (0, 0, 36 * VOXEL_SIZE)

# Standard Socket: Socket_Head (top center of head cranium)
b_sock_head = eb.new("Socket_Head")
b_sock_head.parent = b_head
b_sock_head.head = (0.0, -0.5 * VOXEL_SIZE, 36.0 * VOXEL_SIZE)
b_sock_head.tail = (0.0, -0.5 * VOXEL_SIZE, 38.0 * VOXEL_SIZE)

# Standard Socket: Socket_Back (upper rear spine)
b_sock_back = eb.new("Socket_Back")
b_sock_back.parent = b_chest
b_sock_back.head = (0.0, -3.5 * VOXEL_SIZE, 22.0 * VOXEL_SIZE)
b_sock_back.tail = (0.0, -4.5 * VOXEL_SIZE, 22.0 * VOXEL_SIZE)

# Left Arm Bones & Pauldron
b_sh_l = eb.new("Shoulder.L")
b_sh_l.parent = b_chest
b_sh_l.head = (3.5 * VOXEL_SIZE, 0, 24 * VOXEL_SIZE)
b_sh_l.tail = (6.5 * VOXEL_SIZE, 0, 24 * VOXEL_SIZE)

b_arm_l = eb.new("UpperArm.L")
b_arm_l.parent = b_sh_l
b_arm_l.head = (6.5 * VOXEL_SIZE, 0, 24 * VOXEL_SIZE)
b_arm_l.tail = (6.5 * VOXEL_SIZE, 0, 19 * VOXEL_SIZE)

b_fore_l = eb.new("Forearm.L")
b_fore_l.parent = b_arm_l
b_fore_l.head = (6.5 * VOXEL_SIZE, 0, 19 * VOXEL_SIZE)
b_fore_l.tail = (6.5 * VOXEL_SIZE, 0, 13 * VOXEL_SIZE)

b_hand_l = eb.new("Hand.L")
b_hand_l.parent = b_fore_l
b_hand_l.head = (6.5 * VOXEL_SIZE, 1.0 * VOXEL_SIZE, 12 * VOXEL_SIZE)
b_hand_l.tail = (6.5 * VOXEL_SIZE, 3.0 * VOXEL_SIZE, 9 * VOXEL_SIZE)

# Standard Socket: Socket_Hand_L (palm center)
b_sock_hand_l = eb.new("Socket_Hand_L")
b_sock_hand_l.parent = b_hand_l
b_sock_hand_l.head = (6.5 * VOXEL_SIZE, 1.0 * VOXEL_SIZE, 10.5 * VOXEL_SIZE)
b_sock_hand_l.tail = (6.5 * VOXEL_SIZE, 2.5 * VOXEL_SIZE, 10.5 * VOXEL_SIZE)

# Right Arm Bones & Pauldron
b_sh_r = eb.new("Shoulder.R")
b_sh_r.parent = b_chest
b_sh_r.head = (-3.5 * VOXEL_SIZE, 0, 24 * VOXEL_SIZE)
b_sh_r.tail = (-6.5 * VOXEL_SIZE, 0, 24 * VOXEL_SIZE)

b_arm_r = eb.new("UpperArm.R")
b_arm_r.parent = b_sh_r
b_arm_r.head = (-6.5 * VOXEL_SIZE, 0, 24 * VOXEL_SIZE)
b_arm_r.tail = (-6.5 * VOXEL_SIZE, 0, 19 * VOXEL_SIZE)

b_fore_r = eb.new("Forearm.R")
b_fore_r.parent = b_arm_r
b_fore_r.head = (-6.5 * VOXEL_SIZE, 0, 19 * VOXEL_SIZE)
b_fore_r.tail = (-6.5 * VOXEL_SIZE, 0, 13 * VOXEL_SIZE)

b_hand_r = eb.new("Hand.R")
b_hand_r.parent = b_fore_r
b_hand_r.head = (-6.5 * VOXEL_SIZE, 1.0 * VOXEL_SIZE, 12 * VOXEL_SIZE)
b_hand_r.tail = (-6.5 * VOXEL_SIZE, 3.0 * VOXEL_SIZE, 9 * VOXEL_SIZE)

# Standard Socket: Socket_Hand_R (palm center)
b_sock_hand_r = eb.new("Socket_Hand_R")
b_sock_hand_r.parent = b_hand_r
b_sock_hand_r.head = (-7.5 * VOXEL_SIZE, 1.0 * VOXEL_SIZE, 10.5 * VOXEL_SIZE)
b_sock_hand_r.tail = (-7.5 * VOXEL_SIZE, 2.5 * VOXEL_SIZE, 10.5 * VOXEL_SIZE)

# Left Leg Bones
b_uleg_l = eb.new("UpperLeg.L")
b_uleg_l.parent = b_hips
b_uleg_l.head = (3.5 * VOXEL_SIZE, 0, 14 * VOXEL_SIZE)
b_uleg_l.tail = (3.5 * VOXEL_SIZE, 0, 9 * VOXEL_SIZE)

b_lleg_l = eb.new("LowerLeg.L")
b_lleg_l.parent = b_uleg_l
b_lleg_l.head = (3.5 * VOXEL_SIZE, 0, 9 * VOXEL_SIZE)
b_lleg_l.tail = (3.5 * VOXEL_SIZE, 0, 4 * VOXEL_SIZE)

b_foot_l = eb.new("Foot.L")
b_foot_l.parent = b_lleg_l
b_foot_l.head = (3.5 * VOXEL_SIZE, 0, 4 * VOXEL_SIZE)
b_foot_l.tail = (3.5 * VOXEL_SIZE, 3.0 * VOXEL_SIZE, 0)

# Right Leg Bones
b_uleg_r = eb.new("UpperLeg.R")
b_uleg_r.parent = b_hips
b_uleg_r.head = (-3.5 * VOXEL_SIZE, 0, 14 * VOXEL_SIZE)
b_uleg_r.tail = (-3.5 * VOXEL_SIZE, 0, 9 * VOXEL_SIZE)

b_lleg_r = eb.new("LowerLeg.R")
b_lleg_r.parent = b_uleg_r
b_lleg_r.head = (-3.5 * VOXEL_SIZE, 0, 9 * VOXEL_SIZE)
b_lleg_r.tail = (-3.5 * VOXEL_SIZE, 0, 4 * VOXEL_SIZE)

b_foot_r = eb.new("Foot.R")
b_foot_r.parent = b_lleg_r
b_foot_r.head = (-3.5 * VOXEL_SIZE, 0, 4 * VOXEL_SIZE)
b_foot_r.tail = (-3.5 * VOXEL_SIZE, 3.0 * VOXEL_SIZE, 0)

# Claw Slash Trail VFX Bones
b_trail_l = eb.new("ClawTrail.L")
b_trail_l.parent = b_root
b_trail_l.head = (7.0 * VOXEL_SIZE, 7.0 * VOXEL_SIZE, 17.0 * VOXEL_SIZE)
b_trail_l.tail = (7.0 * VOXEL_SIZE, 11.0 * VOXEL_SIZE, 12.0 * VOXEL_SIZE)

b_trail_r = eb.new("ClawTrail.R")
b_trail_r.parent = b_root
b_trail_r.head = (-8.0 * VOXEL_SIZE, 7.0 * VOXEL_SIZE, 17.0 * VOXEL_SIZE)
b_trail_r.tail = (-8.0 * VOXEL_SIZE, 11.0 * VOXEL_SIZE, 12.0 * VOXEL_SIZE)

bpy.ops.object.mode_set(mode='OBJECT')

ALL_BONE_NAMES = [
    "Root", "Hips", "Spine", "Chest", "Neck", "Head",
    "Shoulder.L", "UpperArm.L", "Forearm.L", "Hand.L",
    "Shoulder.R", "UpperArm.R", "Forearm.R", "Hand.R",
    "UpperLeg.L", "LowerLeg.L", "Foot.L",
    "UpperLeg.R", "LowerLeg.R", "Foot.R",
    "ClawTrail.L", "ClawTrail.R",
    "Socket_Hand_R", "Socket_Hand_L", "Socket_Head", "Socket_Back"
]

vgroups = {b: zombie_obj.vertex_groups.new(name=b) for b in ALL_BONE_NAMES}
bone_vert_lists = {b: [] for b in ALL_BONE_NAMES}

for vidx, bname in vert_groups.items():
    if bname in bone_vert_lists:
        bone_vert_lists[bname].append(vidx)

for bname, vlist in bone_vert_lists.items():
    if vlist:
        vgroups[bname].add(vlist, 1.0, 'REPLACE')

# Planar Dissolve Optimization
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
print(">>> Keyframing 80-Frame Animation: Trove Walk (1-40) & Violent Claw Strike (41-80)...")
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

timeline_data = [
    # -------------------------------------------------------------
    # PHASE A: TROVE BOUNCY SHAMBLING WALK CYCLE (Frames 1–40)
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
    # Frame 70 (Recoil Breath Shudder)
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
        kf(pb[bname], frame_idx, loc=loc, rot=rot, scale=scale)

# Smooth Bezier Interpolation with Snappy Ease Out
if arm_obj.animation_data and arm_obj.animation_data.action:
    arm_obj.animation_data.action.name = "Zombie_Action"
    for fcurve in arm_obj.animation_data.action.fcurves:
        for kf_pt in fcurve.keyframe_points:
            kf_pt.interpolation = 'BEZIER'
            kf_pt.easing = 'EASE_OUT'

bpy.ops.object.mode_set(mode='OBJECT')

# -----------------------------------------------------------------
# 7. Cycles AgX Render & Front 3/4 Dynamic Camera Framing
# -----------------------------------------------------------------
print(">>> Configuring Cycles AgX 128-sample Studio Showcase...")
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

# Dark studio background
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

# Dynamic Depsgraph Evaluated Camera Framing at Peak Action Frame 56
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
cam_target = bpy.data.objects.new("CamTarget_Zombie", None)
cam_target.location = Vector((center.x * 0.15, center.y + 0.03, center.z + span * 0.05))
bpy.context.collection.objects.link(cam_target)

# Heroic Front 3/4 Perspective Camera
cam_data = bpy.data.cameras.new("Zombie_HeroCamera")
cam_data.lens = 48
cam_obj = bpy.data.objects.new("Zombie_HeroCamera", object_data=cam_data)

fov_rad = cam_obj.data.angle
dist = (span * 0.5) / math.tan(fov_rad * 0.5) * 0.82

# Camera placed at -X, +Y, +Z to view face, glowing eye, skull fissure, 3D ribs, and slashing claws:
cam_obj.location = cam_target.location + Vector((-dist * 0.48, dist * 0.80, dist * 0.42))

track = cam_obj.constraints.new(type='TRACK_TO')
track.target = cam_target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

# 4-Point High-Fidelity Studio Lighting
# 1) Key Sun Light: Directional glint casting crisp micro-voxel shadows across ribs, skull fracture & teeth
key_sun = bpy.data.objects.new("Key_Sun", bpy.data.lights.new("Key_Sun", type='SUN'))
key_sun.data.energy = 4.5
key_sun.data.color = (1.0, 0.98, 0.94)
key_sun.data.angle = math.radians(4)
key_sun.rotation_euler = (math.radians(-42), math.radians(22), math.radians(135))
bpy.context.collection.objects.link(key_sun)

# 2) Front Specular Fill Light: Illuminates face, glowing eye, and claws
front_fill = bpy.data.objects.new("Front_Fill", bpy.data.lights.new("Front_Fill", type='AREA'))
front_fill.data.energy = 240.0
front_fill.data.color = (0.90, 0.95, 1.00)
front_fill.data.size = 2.4
front_fill.location = (-0.8, 1.6, 0.8)
front_fill.rotation_euler = (math.radians(35), math.radians(-20), math.radians(-40))
bpy.context.collection.objects.link(front_fill)

# 3) Toxic Lime / Green Rim Backlight: Accentuates undead chibi silhouette & edge contours
rim_toxic = bpy.data.objects.new("Rim_ToxicGreen", bpy.data.lights.new("Rim_ToxicGreen", type='AREA'))
rim_toxic.data.energy = 280.0
rim_toxic.data.color = (0.35, 0.95, 0.15)
rim_toxic.data.size = 2.2
rim_toxic.location = (1.5, -1.2, 0.9)
rim_toxic.rotation_euler = (math.radians(-40), math.radians(40), math.radians(120))
bpy.context.collection.objects.link(rim_toxic)

# 4) Deep Shadow Fill Light: Soft ambient mood
dark_fill = bpy.data.objects.new("Fill_Shadow", bpy.data.lights.new("Fill_Shadow", type='AREA'))
dark_fill.data.energy = 120.0
dark_fill.data.color = (0.16, 0.11, 0.24)
dark_fill.data.size = 3.0
dark_fill.location = (0.6, 1.5, -0.1)
bpy.context.collection.objects.link(dark_fill)

# -----------------------------------------------------------------
# 8. Export .blend, .glb, _render.png, and _data.js
# -----------------------------------------------------------------
output_dir = os.path.dirname(os.path.abspath(__file__))
blend_file = os.path.join(output_dir, "zombie.blend")
glb_file = os.path.join(output_dir, "zombie.glb")
render_file = os.path.join(output_dir, "zombie_render.png")
js_file = os.path.join(output_dir, "zombie_data.js")

print(f">>> Saving Blender file: {blend_file}")
bpy.ops.wm.save_as_mainfile(filepath=blend_file)

print(f">>> Exporting game-ready GLB model: {glb_file}")
bpy.ops.object.select_all(action='DESELECT')
zombie_obj.select_set(True)
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj

bpy.ops.export_scene.gltf(
    filepath=glb_file,
    export_format='GLB',
    use_selection=False,
    export_materials='EXPORT',
    export_yup=True,
    export_animations=True,
    export_skins=True,
    export_all_influences=False,
    export_apply=False
)

print(f">>> Rendering Key Impact Frame {ACTION_FRAME} to {render_file}...")
scene.frame_set(ACTION_FRAME)
scene.render.filepath = render_file
bpy.ops.render.render(write_still=True)

# Generate Base64 Data URI in zombie_data.js
print(f">>> Generating Base64 Data URI to {js_file}...")
with open(glb_file, 'rb') as f:
    glb_b64 = base64.b64encode(f.read()).decode('utf-8')

js_content = f'window.ZOMBIE_BASE64 = "data:model/gltf-binary;base64,{glb_b64}";\n'
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_content)

# Mandatory Clean-up: Delete all .blend1 and test_*.png files
blend1_file = os.path.join(output_dir, "zombie.blend1")
if os.path.exists(blend1_file):
    try:
        os.remove(blend1_file)
    except Exception:
        pass
for fname in os.listdir(output_dir):
    if fname.startswith("test_") and fname.endswith(".png"):
        try:
            os.remove(os.path.join(output_dir, fname))
        except Exception:
            pass

print("=================================================================")
print(">>> [SUCCESS] Authentic Trove Chibi Undead Zombie Complete!")
print("=================================================================")
