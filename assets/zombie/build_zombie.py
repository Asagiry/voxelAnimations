import bpy
import math
import os
import base64
from mathutils import Vector, Matrix

print("=================================================================")
print(">>> [TROVE VOXEL ARTISAN] Micro-Voxel Undead Zombie Character (v2)")
print(">>> Authentic Retro Voxel Style: Trove / Cube World / Astra 6")
print("=================================================================")

# -----------------------------------------------------------------
# 1. Reset Scene & General Configuration
# -----------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 80
scene.render.fps = 30

VOXEL_SIZE = 0.014  # 1.4 cm micro-voxel scale (~44 voxels tall = ~0.62m world units)

# -----------------------------------------------------------------
# 2. Shader & Materials Definition (AgX Safe Palette)
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
    'flesh_green':    make_shader('M_FleshGreen',    (0.068, 0.147, 0.063, 1.0), roughness=0.65, metallic=0.05),
    # 2. Shadowed Gangrenous Flesh
    'flesh_dark':     make_shader('M_FleshDark',     (0.038, 0.082, 0.036, 1.0), roughness=0.70, metallic=0.05),
    # 3. Decayed Bone & Teeth & Exposed Skull
    'decayed_bone':   make_shader('M_DecayedBone',   (0.530, 0.490, 0.390, 1.0), roughness=0.45, metallic=0.10),
    # 4. Shredded Dark Tunic / Trousers
    'cloth_dark':     make_shader('M_ClothDark',     (0.024, 0.032, 0.041, 1.0), roughness=0.85, metallic=0.02),
    # 5. Tattered Leather / Belts / Wraps
    'cloth_tattered': make_shader('M_ClothTattered', (0.055, 0.034, 0.023, 1.0), roughness=0.80, metallic=0.05),
    # 6. Dark Wound / Dried Blood Cavity
    'wound_dark':     make_shader('M_WoundDark',     (0.046, 0.009, 0.009, 1.0), roughness=0.50, metallic=0.15),
    # 7. Eerie Glowing Undead Eyes (Toxic Yellow-Green)
    'eye_glow':       make_shader('M_EyeGlow',       (0.440, 0.790, 0.020, 1.0), roughness=0.10, metallic=0.00, emission=1.8, emission_color=(0.48, 0.85, 0.05, 1.0)),
    # 8. Dark Scalp / Straggly Hair Tufts
    'hair_dark':      make_shader('M_HairDark',      (0.015, 0.018, 0.022, 1.0), roughness=0.90, metallic=0.02),
    # 9. Heavy Combat Boot Sole
    'boot_sole':      make_shader('M_BootSole',      (0.012, 0.015, 0.018, 1.0), roughness=0.90, metallic=0.10),
    # 10. Geometric Claw Slash Trail (Toxic Lime Green)
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

print(">>> [1/5] Synthesizing Micro-Voxel Zombie Anatomy...")

# --- 3.1 LEFT LEG: Combat Boot, Rotting Calf, Tattered Trouser ---
# Foot.L (Z = 0..3)
for x in range(2, 6):
    for y in range(-2, 5):
        set_vox(x, y, 0, 'boot_sole', 'Foot.L', True)
        if y <= 3:
            set_vox(x, y, 1, 'cloth_dark', 'Foot.L', True)
        if -1 <= y <= 2:
            set_vox(x, y, 2, 'cloth_dark', 'Foot.L', True)
            set_vox(x, y, 3, 'cloth_tattered' if (x == 5 or y == 2) else 'cloth_dark', 'Foot.L', True)

# LowerLeg.L (Z = 4..9)
for z in range(4, 10):
    for x in range(2, 6):
        for y in range(-1, 3):
            if z <= 6:
                m = 'flesh_dark' if (y == -1 or x == 5) else 'flesh_green'
            else:
                m = 'cloth_dark' if (z >= 8 or (x + y + z) % 2 == 0) else 'cloth_tattered'
            set_vox(x, y, z, m, 'LowerLeg.L', True)

# UpperLeg.L (Z = 10..17)
for z in range(10, 18):
    for x in range(2, 6):
        for y in range(-1, 3):
            if z == 10 and y == 2:
                m = 'flesh_dark'
            elif z in (13, 14) and x == 2:
                m = 'cloth_tattered'
            else:
                m = 'cloth_dark'
            set_vox(x, y, z, m, 'UpperLeg.L', True)

# --- 3.2 RIGHT LEG: Bare Skeletal Foot, Exposed Shin Bone, Torn Knee ---
# Foot.R (Z = 0..3)
for x in range(-5, -1):
    for y in range(-2, 4):
        set_vox(x, y, 0, 'decayed_bone', 'Foot.R', True)
for toe_x in (-5, -4, -3, -2):
    set_vox(toe_x, 4, 0, 'decayed_bone', 'Foot.R', True)
for z in (1, 2):
    for x in (-4, -3):
        for y in (-1, 1):
            set_vox(x, y, z, 'decayed_bone', 'Foot.R', True)
set_vox(-3, 0, 3, 'decayed_bone', 'Foot.R', True)

# LowerLeg.R (Z = 4..9) - EXPOSED TIBIA SHIN BONE
for z in range(4, 10):
    for x in range(-5, -1):
        for y in range(-1, 3):
            if y == 2 and x in (-4, -3):
                set_vox(x, y, z, 'decayed_bone', 'LowerLeg.R', True)
            elif y == 1 and x in (-4, -3):
                set_vox(x, y, z, 'wound_dark', 'LowerLeg.R', True)
            else:
                m = 'flesh_dark' if (x == -5 or y == -1) else 'flesh_green'
                set_vox(x, y, z, m, 'LowerLeg.R', True)

# UpperLeg.R (Z = 10..17)
for z in range(10, 18):
    for x in range(-5, -1):
        for y in range(-1, 3):
            if z in (10, 11) and y == 2:
                m = 'decayed_bone' if x == -3 else 'wound_dark'
            elif z in (10, 11) and y == 1 and x == -3:
                m = 'wound_dark'
            elif (x + y + z) % 3 == 0:
                m = 'cloth_tattered'
            else:
                m = 'cloth_dark'
            set_vox(x, y, z, m, 'UpperLeg.R', True)

# --- 3.3 PELVIS & HIPS (Z = 17..21) ---
for z in range(17, 22):
    for x in range(-5, 6):
        for y in range(-2, 3):
            m = 'cloth_dark'
            if z == 20:
                if y in (-2, 2) or abs(x) == 5:
                    m = 'cloth_tattered'
            elif z == 17 and (x in (-2, 2) or y == 2):
                m = 'cloth_tattered'
            set_vox(x, y, z, m, 'Hips', True)
set_vox(0, 3, 20, 'cloth_tattered', 'Hips', True)
set_vox(0, 3, 19, 'cloth_tattered', 'Hips', True)

# --- 3.4 SPINE & LOWER TORSO (Z = 21..26) ---
for z in range(21, 27):
    for x in range(-5, 6):
        for y in range(-2, 3):
            if x <= -2 and y >= 0 and z in (22, 23, 24):
                if y == 2:
                    m = 'wound_dark'
                elif y == 1:
                    m = 'wound_dark' if x == -3 else 'flesh_dark'
                else:
                    m = 'flesh_dark'
            elif x == 0 and y == -2:
                m = 'decayed_bone' if z % 2 == 0 else 'cloth_tattered'
            else:
                m = 'cloth_tattered' if (x + y + z) % 4 == 0 else 'cloth_dark'
            set_vox(x, y, z, m, 'Spine', True)

# --- 3.5 CHEST, SHOULDERS & EXPOSED RIBCAGE (Z = 26..33) ---
for z in range(26, 34):
    for x in range(-6, 7):
        for y in range(-3, 4):
            is_back_hump = (y <= -2 and z in (28, 29, 30, 31, 32))
            
            # EXPOSED RIBCAGE on Right Chest (x <= -1, y >= 0, z in 27..32)
            if -5 <= x <= -1 and y >= 1 and 27 <= z <= 32:
                if z in (28, 30, 32) and y == 2:
                    m = 'decayed_bone'
                elif z in (28, 30, 32) and y == 3 and x in (-4, -3, -2):
                    m = 'decayed_bone'
                else:
                    m = 'wound_dark'
            elif is_back_hump:
                if x == 0 and y == -3 and z in (29, 31):
                    m = 'decayed_bone'
                else:
                    m = 'cloth_dark' if abs(x) > 1 else 'cloth_tattered'
            elif z == 33 and y == 2 and x in (-4, -3, -2):
                m = 'decayed_bone'
            elif z >= 32 and abs(x) <= 2 and y >= 1:
                m = 'flesh_dark'
            else:
                m = 'cloth_tattered' if (x == 4 or z == 29) else 'cloth_dark'
            set_vox(x, y, z, m, 'Chest', True)

# --- 3.6 NECK (Z = 33..35) ---
for z in range(33, 36):
    for x in range(-2, 3):
        for y in range(-1, 2):
            if x == 0 and y == -1:
                m = 'decayed_bone'
            else:
                m = 'flesh_dark' if (x == -2 or y == 1) else 'flesh_green'
            set_vox(x, y, z, m, 'Neck', True)

# --- 3.7 HEAD: Asymmetrical Cranium, Glowing Eye, Exposed Jaw & Teeth (Z = 35..45) ---
for z in range(35, 46):
    for x in range(-6, 7):
        for y in range(-3, 5):
            if abs(x) == 6 and (y <= -2 or y >= 4 or z in (35, 45)):
                continue
            if y == -3 and (abs(x) >= 5 or z >= 44):
                continue
            
            if z >= 44:
                if (x >= 0 and y <= 2) or (y == -3 and x >= -2):
                    set_vox(x, y, z, 'hair_dark', 'Head', True)
                    continue
            
            if -5 <= x <= -1 and z >= 40 and y >= 0:
                if (x == -3 and y in (1, 2, 3) and z in (41, 42)) or (x == -2 and y == 3 and z == 43):
                    m = 'wound_dark'
                else:
                    m = 'decayed_bone'
                set_vox(x, y, z, m, 'Head', True)
                continue
            
            m = 'flesh_green' if (x >= 0 and z >= 38) else 'flesh_dark'
            set_vox(x, y, z, m, 'Head', True)

# Facial Details
for x in range(-5, 6):
    m = 'decayed_bone' if x <= -1 else 'flesh_dark'
    set_vox(x, 4, 40, m, 'Head', True)
set_vox(0, 4, 40, 'flesh_dark', 'Head', True)

# Left Glowing Eye
set_vox(2, 4, 39, 'eye_glow', 'Head', True)
set_vox(3, 4, 39, 'eye_glow', 'Head', True)
set_vox(1, 4, 39, 'flesh_dark', 'Head', True)
set_vox(4, 4, 39, 'flesh_dark', 'Head', True)

# Right Eye Socket
set_vox(-3, 4, 39, 'wound_dark', 'Head', True)
set_vox(-2, 4, 39, 'eye_glow', 'Head', True)
set_vox(-4, 4, 39, 'flesh_dark', 'Head', True)
set_vox(-1, 4, 39, 'flesh_dark', 'Head', True)

# Nose Cavity
set_vox(-1, 4, 38, 'wound_dark', 'Head', True)
set_vox(0, 4, 38, 'wound_dark', 'Head', True)

# Mouth & Teeth
for x in range(-3, 4):
    for z in (36, 37):
        set_vox(x, 3, z, 'wound_dark', 'Head', True)
for tx in (-3, -2, -1, 1, 2, 3):
    set_vox(tx, 4, 37, 'decayed_bone', 'Head', True)
for x in range(-4, 5):
    for y in range(2, 5):
        m_jaw = 'decayed_bone' if x <= -2 else ('flesh_dark' if x <= 1 else 'flesh_green')
        set_vox(x, y, 35, m_jaw, 'Head', True)
for tx in (-3, -1, 1, 3):
    set_vox(tx, 4, 36, 'decayed_bone', 'Head', True)

# --- 3.8 LEFT ARM: Fleshy Arm, Bandaged Forearm & Razor Claws ---
for z in range(24, 32):
    for x in range(7, 10):
        for y in range(-1, 3):
            if z >= 29:
                m = 'cloth_dark' if (x == 7 or y == -1) else 'cloth_tattered'
            else:
                m = 'flesh_dark' if (y == -1 or x == 9) else 'flesh_green'
            set_vox(x, y, z, m, 'UpperArm.L', True)

for z in range(17, 24):
    for x in range(7, 10):
        for y in range(0, 3):
            if z in (19, 20):
                m = 'cloth_tattered'
            else:
                m = 'flesh_dark' if y == 0 else 'flesh_green'
            set_vox(x, y, z, m, 'Forearm.L', True)

for z in (15, 16):
    for x in range(7, 10):
        for y in range(2, 5):
            set_vox(x, y, z, 'flesh_dark', 'Hand.L', True)

set_vox(7, 5, 16, 'flesh_dark', 'Hand.L', True)
set_vox(7, 6, 16, 'decayed_bone', 'Hand.L', True)
set_vox(8, 5, 15, 'flesh_dark', 'Hand.L', True)
set_vox(8, 6, 15, 'flesh_dark', 'Hand.L', True)
set_vox(8, 7, 15, 'decayed_bone', 'Hand.L', True)
set_vox(9, 5, 15, 'flesh_dark', 'Hand.L', True)
set_vox(9, 6, 15, 'flesh_dark', 'Hand.L', True)
set_vox(9, 7, 15, 'decayed_bone', 'Hand.L', True)
set_vox(9, 5, 14, 'flesh_dark', 'Hand.L', True)
set_vox(9, 6, 14, 'decayed_bone', 'Hand.L', True)

# --- 3.9 RIGHT ARM: Shredded Sleeve, SKELETAL RADIUS/ULNA FOREARM & TALONS ---
for z in range(24, 32):
    for x in range(-10, -6):
        for y in range(-1, 3):
            if z >= 29:
                m = 'cloth_dark' if (x == -7 or y == -1) else 'cloth_tattered'
            else:
                m = 'wound_dark' if (z in (25, 26) and y == 2) else ('flesh_dark' if x == -10 else 'flesh_green')
            set_vox(x, y, z, m, 'UpperArm.R', True)

for z in range(17, 24):
    for y in (1, 2):
        set_vox(-7, y, z, 'decayed_bone', 'Forearm.R', True)
        set_vox(-9, y, z, 'decayed_bone', 'Forearm.R', True)
    if z == 23:
        set_vox(-8, 1, 23, 'flesh_dark', 'Forearm.R', True)
    elif z == 20:
        set_vox(-8, 1, 20, 'wound_dark', 'Forearm.R', True)
    elif z == 17:
        set_vox(-8, 2, 17, 'decayed_bone', 'Forearm.R', True)

for z in (15, 16):
    for x in (-9, -8, -7):
        for y in (2, 4):
            set_vox(x, y, z, 'decayed_bone', 'Hand.R', True)

set_vox(-7, 5, 16, 'decayed_bone', 'Hand.R', True)
set_vox(-7, 6, 16, 'decayed_bone', 'Hand.R', True)
set_vox(-8, 5, 15, 'decayed_bone', 'Hand.R', True)
set_vox(-8, 6, 15, 'decayed_bone', 'Hand.R', True)
set_vox(-8, 7, 15, 'decayed_bone', 'Hand.R', True)
set_vox(-9, 5, 15, 'decayed_bone', 'Hand.R', True)
set_vox(-9, 6, 15, 'decayed_bone', 'Hand.R', True)
set_vox(-9, 7, 15, 'decayed_bone', 'Hand.R', True)
set_vox(-9, 5, 14, 'decayed_bone', 'Hand.R', True)
set_vox(-9, 6, 14, 'decayed_bone', 'Hand.R', True)

# --- 3.10 GEOMETRIC CLAW SLASH TRAILS (Combat VFX) ---
# Volumetric crescent ribbons sweeping through the downward strike plane
def build_slash_ribbon(x_center, bone_name):
    # Arc sweeps downward through strike zone: Y = 4..18, Z = 32..10
    N_STEPS = 18
    for st in range(N_STEPS):
        u = st / float(N_STEPS - 1)  # 0 at top-back, 1 at bottom-front
        ang = -0.30 + u * (math.pi * 0.70)
        rad = 13.0
        cy = 5.0 + math.sin(ang) * rad
        cz = 24.0 - math.cos(ang) * rad * 0.90
        
        for dx in (-1, 0, 1):
            vx = x_center + dx
            for dy in (0, 1):
                m_trail = 'slash_core' if (dx == 0 and dy == 0) else 'slash_trail'
                set_vox(vx, cy + dy, cz, m_trail, bone_name, True)

build_slash_ribbon(8, 'ClawTrail.L')
build_slash_ribbon(-8, 'ClawTrail.R')

print(f">>> Total Generated Micro-Voxels: {len(voxels)} voxels.")

# -----------------------------------------------------------------
# 4. Watertight Boundary Quad Mesher & Optimization
# -----------------------------------------------------------------
print(">>> Constructing watertight exposed boundary quads...")

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

print(f">>> Constructing Zombie Mesh: {len(verts)} vertices, {len(faces)} faces...")
mesh = bpy.data.meshes.new("Zombie_Mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

for m in used_mat_names:
    mesh.materials.append(mats[m])
for poly, slot in zip(mesh.polygons, face_mats):
    poly.material_index = slot

# Strict flat shading
mesh.polygons.foreach_set('use_smooth', [False] * len(mesh.polygons))
mesh.update()

zombie_obj = bpy.data.objects.new("Zombie", mesh)
bpy.context.collection.objects.link(zombie_obj)

# -----------------------------------------------------------------
# 5. Skeletal Rigging & Armature Hierarchy
# -----------------------------------------------------------------
print(">>> Rigging Clean Humanoid Armature Hierarchy...")
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

# 2) Hips
b_hips = eb.new("Hips")
b_hips.parent = b_root
b_hips.head = (0, 0, 18 * VOXEL_SIZE)
b_hips.tail = (0, 0, 22 * VOXEL_SIZE)

# 3) Spine
b_spine = eb.new("Spine")
b_spine.parent = b_hips
b_spine.head = (0, 0, 22 * VOXEL_SIZE)
b_spine.tail = (0, 0.5 * VOXEL_SIZE, 27 * VOXEL_SIZE)

# 4) Chest
b_chest = eb.new("Chest")
b_chest.parent = b_spine
b_chest.head = (0, 0.5 * VOXEL_SIZE, 27 * VOXEL_SIZE)
b_chest.tail = (0, 1.0 * VOXEL_SIZE, 33 * VOXEL_SIZE)

# 5) Neck
b_neck = eb.new("Neck")
b_neck.parent = b_chest
b_neck.head = (0, 1.0 * VOXEL_SIZE, 33 * VOXEL_SIZE)
b_neck.tail = (0, 1.5 * VOXEL_SIZE, 36 * VOXEL_SIZE)

# 6) Head
b_head = eb.new("Head")
b_head.parent = b_neck
b_head.head = (0, 1.5 * VOXEL_SIZE, 36 * VOXEL_SIZE)
b_head.tail = (0, 2.0 * VOXEL_SIZE, 45 * VOXEL_SIZE)

# Left Arm Bones
b_sh_l = eb.new("Shoulder.L")
b_sh_l.parent = b_chest
b_sh_l.head = (4.0 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 32.0 * VOXEL_SIZE)
b_sh_l.tail = (7.0 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 32.0 * VOXEL_SIZE)

b_arm_l = eb.new("UpperArm.L")
b_arm_l.parent = b_sh_l
b_arm_l.head = (7.0 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 32.0 * VOXEL_SIZE)
b_arm_l.tail = (8.0 * VOXEL_SIZE, 1.0 * VOXEL_SIZE, 24.0 * VOXEL_SIZE)

b_fore_l = eb.new("Forearm.L")
b_fore_l.parent = b_arm_l
b_fore_l.head = (8.0 * VOXEL_SIZE, 1.0 * VOXEL_SIZE, 24.0 * VOXEL_SIZE)
b_fore_l.tail = (8.5 * VOXEL_SIZE, 2.0 * VOXEL_SIZE, 17.0 * VOXEL_SIZE)

b_hand_l = eb.new("Hand.L")
b_hand_l.parent = b_fore_l
b_hand_l.head = (8.5 * VOXEL_SIZE, 2.0 * VOXEL_SIZE, 17.0 * VOXEL_SIZE)
b_hand_l.tail = (8.5 * VOXEL_SIZE, 4.5 * VOXEL_SIZE, 14.0 * VOXEL_SIZE)

# Right Arm Bones (Skeletal)
b_sh_r = eb.new("Shoulder.R")
b_sh_r.parent = b_chest
b_sh_r.head = (-4.0 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 32.0 * VOXEL_SIZE)
b_sh_r.tail = (-7.0 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 32.0 * VOXEL_SIZE)

b_arm_r = eb.new("UpperArm.R")
b_arm_r.parent = b_sh_r
b_arm_r.head = (-7.0 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 32.0 * VOXEL_SIZE)
b_arm_r.tail = (-8.0 * VOXEL_SIZE, 1.0 * VOXEL_SIZE, 24.0 * VOXEL_SIZE)

b_fore_r = eb.new("Forearm.R")
b_fore_r.parent = b_arm_r
b_fore_r.head = (-8.0 * VOXEL_SIZE, 1.0 * VOXEL_SIZE, 24.0 * VOXEL_SIZE)
b_fore_r.tail = (-8.5 * VOXEL_SIZE, 2.0 * VOXEL_SIZE, 17.0 * VOXEL_SIZE)

b_hand_r = eb.new("Hand.R")
b_hand_r.parent = b_fore_r
b_hand_r.head = (-8.5 * VOXEL_SIZE, 2.0 * VOXEL_SIZE, 17.0 * VOXEL_SIZE)
b_hand_r.tail = (-8.5 * VOXEL_SIZE, 4.5 * VOXEL_SIZE, 14.0 * VOXEL_SIZE)

# Left Leg Bones
b_uleg_l = eb.new("UpperLeg.L")
b_uleg_l.parent = b_hips
b_uleg_l.head = (3.5 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 18.0 * VOXEL_SIZE)
b_uleg_l.tail = (3.5 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 10.0 * VOXEL_SIZE)

b_lleg_l = eb.new("LowerLeg.L")
b_lleg_l.parent = b_uleg_l
b_lleg_l.head = (3.5 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 10.0 * VOXEL_SIZE)
b_lleg_l.tail = (3.5 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 3.0 * VOXEL_SIZE)

b_foot_l = eb.new("Foot.L")
b_foot_l.parent = b_lleg_l
b_foot_l.head = (3.5 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 3.0 * VOXEL_SIZE)
b_foot_l.tail = (3.5 * VOXEL_SIZE, 3.5 * VOXEL_SIZE, 0.0)

# Right Leg Bones
b_uleg_r = eb.new("UpperLeg.R")
b_uleg_r.parent = b_hips
b_uleg_r.head = (-3.5 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 18.0 * VOXEL_SIZE)
b_uleg_r.tail = (-3.5 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 10.0 * VOXEL_SIZE)

b_lleg_r = eb.new("LowerLeg.R")
b_lleg_r.parent = b_uleg_r
b_lleg_r.head = (-3.5 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 10.0 * VOXEL_SIZE)
b_lleg_r.tail = (-3.5 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 3.0 * VOXEL_SIZE)

b_foot_r = eb.new("Foot.R")
b_foot_r.parent = b_lleg_r
b_foot_r.head = (-3.5 * VOXEL_SIZE, 0.5 * VOXEL_SIZE, 3.0 * VOXEL_SIZE)
b_foot_r.tail = (-3.5 * VOXEL_SIZE, 3.5 * VOXEL_SIZE, 0.0)

# Claw Slash Trail VFX Bones
b_trail_l = eb.new("ClawTrail.L")
b_trail_l.parent = b_root
b_trail_l.head = (8.0 * VOXEL_SIZE, 8.0 * VOXEL_SIZE, 20.0 * VOXEL_SIZE)
b_trail_l.tail = (8.0 * VOXEL_SIZE, 14.0 * VOXEL_SIZE, 14.0 * VOXEL_SIZE)

b_trail_r = eb.new("ClawTrail.R")
b_trail_r.parent = b_root
b_trail_r.head = (-8.0 * VOXEL_SIZE, 8.0 * VOXEL_SIZE, 20.0 * VOXEL_SIZE)
b_trail_r.tail = (-8.0 * VOXEL_SIZE, 14.0 * VOXEL_SIZE, 14.0 * VOXEL_SIZE)

bpy.ops.object.mode_set(mode='OBJECT')

# Assign Rigid Vertex Groups
ALL_BONE_NAMES = [
    "Root", "Hips", "Spine", "Chest", "Neck", "Head",
    "Shoulder.L", "UpperArm.L", "Forearm.L", "Hand.L",
    "Shoulder.R", "UpperArm.R", "Forearm.R", "Hand.R",
    "UpperLeg.L", "LowerLeg.L", "Foot.L",
    "UpperLeg.R", "LowerLeg.R", "Foot.R",
    "ClawTrail.L", "ClawTrail.R"
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

print(f">>> Mesh Optimized: {len(zombie_obj.data.vertices)} vertices, {len(zombie_obj.data.polygons)} polygons.")

# Bind Armature Modifier
arm_mod = zombie_obj.modifiers.new(name="Armature", type='ARMATURE')
arm_mod.object = arm_obj
arm_mod.use_vertex_groups = True
zombie_obj.parent = arm_obj

# -----------------------------------------------------------------
# 6. Keyframe Animation: Shambling Walk & 5-Phase Claw Strike
# -----------------------------------------------------------------
print(">>> Keyframing 80-Frame Animation: Shambling Walk (1-40) & Violent Claw Strike (41-80)...")
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
    # PHASE A: SHAMBLING ZOMBIE WALK (Frames 1–40, 40-frame loop)
    # -------------------------------------------------------------
    # Frame 1: Limping stance (Right foot forward, Left leg dragging back, arms reaching forward)
    (1, {
        "Hips":        ((0, 0, 0), (-6, 5, -3), (1, 1, 1)),
        "Spine":       (None, (-15, 0, -2), None),
        "Chest":       (None, (-10, -3, 3), None),
        "Neck":        (None, (5, 6, -5), None),
        "Head":        (None, (6, 10, -6), None),
        "UpperArm.L":  (None, (45, -8, 12), None),
        "Forearm.L":   (None, (20, 0, 5), None),
        "Hand.L":      (None, (-15, 0, -5), None),
        "UpperArm.R":  (None, (55, 8, -12), None),
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
    # Frame 10: Vault over right foot, left leg drags forward
    (10, {
        "Hips":        ((0, 0.012, 0.010), (-4, 3, 2), (1, 1, 1)),
        "Spine":       (None, (-16, 0, 2), None),
        "Chest":       (None, (-8, 0, 2), None),
        "Head":        (None, (4, -8, 5), None),
        "UpperArm.L":  (None, (38, -6, 10), None),
        "UpperArm.R":  (None, (48, 6, -10), None),
        "UpperLeg.L":  (None, (-5, 0, 4), None),
        "LowerLeg.L":  (None, (-18, 0, 0), None),
        "Foot.L":      (None, (15, 0, 0), None),
        "UpperLeg.R":  (None, (6, 0, -3), None),
        "LowerLeg.R":  (None, (-2, 0, 0), None),
        "Foot.R":      (None, (0, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 20: The Limp Drop: Left foot scrapes awkwardly, hips drop
    (20, {
        "Hips":        ((-0.008, 0.020, -0.012), (-6, -5, 5), (1, 1, 1)),
        "Spine":       (None, (-18, 0, -3), None),
        "Chest":       (None, (-12, 0, -3), None),
        "Head":        (None, (8, -12, 8), None),
        "UpperArm.L":  (None, (55, -10, 14), None),
        "UpperArm.R":  (None, (40, 10, -8), None),
        "UpperLeg.L":  (None, (18, 0, 5), None),
        "LowerLeg.L":  (None, (-8, 0, 0), None),
        "Foot.L":      (None, (-8, 0, 0), None),
        "UpperLeg.R":  (None, (-15, 0, -4), None),
        "LowerLeg.R":  (None, (-12, 0, 0), None),
        "Foot.R":      (None, (10, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 30: Recovery step: Right leg swings back to front
    (30, {
        "Hips":        ((0, 0.008, 0.005), (-4, 2, -2), (1, 1, 1)),
        "Spine":       (None, (-15, 0, 0), None),
        "Chest":       (None, (-10, 0, 0), None),
        "Head":        (None, (5, 5, -4), None),
        "UpperArm.L":  (None, (46, 0, 10), None),
        "UpperArm.R":  (None, (52, 0, -10), None),
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
        "Hips":        ((0, 0, 0), (-6, 5, -3), (1, 1, 1)),
        "Spine":       (None, (-15, 0, -2), None),
        "Chest":       (None, (-10, -3, 3), None),
        "Neck":        (None, (5, 6, -5), None),
        "Head":        (None, (6, 10, -6), None),
        "UpperArm.L":  (None, (45, -8, 12), None),
        "Forearm.L":   (None, (20, 0, 5), None),
        "Hand.L":      (None, (-15, 0, -5), None),
        "UpperArm.R":  (None, (55, 8, -12), None),
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
    # PHASE B: VIOLENT CLAW STRIKE & LUNGE ATTACK (Frames 41–80)
    # -------------------------------------------------------------
    # Frame 44 (Telegraph 1: Target Spotted, Alert Crouch)
    (44, {
        "Hips":        ((0, -0.015, -0.025), (-12, 0, 0), (1, 1, 1)),
        "Spine":       (None, (-22, 0, 0), None),
        "Chest":       (None, (-16, 0, 0), None),
        "Head":        (None, (-14, 0, 0), None),
        "UpperArm.L":  (None, (25, 0, 18), None),
        "Forearm.L":   (None, (-25, 0, 0), None),
        "UpperArm.R":  (None, (25, 0, -18), None),
        "Forearm.R":   (None, (-25, 0, 0), None),
        "UpperLeg.L":  (None, (15, 0, 5), None),
        "LowerLeg.L":  (None, (-30, 0, 0), None),
        "UpperLeg.R":  (None, (-10, 0, -5), None),
        "LowerLeg.R":  (None, (-25, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 50 (Telegraph 2: Deep Kinetic Coil Back, Arms High Overhead, Shriek)
    (50, {
        "Hips":        ((0, -0.050, -0.040), (12, 0, 0), (1, 1, 1)),
        "Spine":       (None, (22, 0, 0), None),
        "Chest":       (None, (18, 0, 0), None),
        "Neck":        (None, (8, 0, 0), None),
        "Head":        (None, (22, 0, 0), None),
        "UpperArm.L":  (None, (-65, -12, 30), None),
        "Forearm.L":   (None, (-40, 0, 12), None),
        "Hand.L":      (None, (-25, 0, -8), None),
        "UpperArm.R":  (None, (-70, 12, -30), None),
        "Forearm.R":   (None, (-45, 0, -12), None),
        "Hand.R":      (None, (-30, 0, 8), None),
        "UpperLeg.L":  (None, (-22, 0, 6), None),
        "LowerLeg.L":  (None, (-35, 0, 0), None),
        "UpperLeg.R":  (None, (12, 0, -6), None),
        "LowerLeg.R":  (None, (-28, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 53 (Active Hit Window 1: Explosive Lunge Acceleration)
    (53, {
        "Hips":        ((0, 0.040, -0.050), (-10, 0, 0), (1, 1, 1)),
        "Spine":       (None, (-18, 0, 0), None),
        "Chest":       (None, (-14, 0, 0), None),
        "Head":        (None, (-6, 0, 0), None),
        "UpperArm.L":  (None, (15, 0, 15), None),
        "Forearm.L":   (None, (10, 0, 0), None),
        "UpperArm.R":  (None, (15, 0, -15), None),
        "Forearm.R":   (None, (10, 0, 0), None),
        "ClawTrail.L": (None, None, (0.35, 0.35, 0.35)),
        "ClawTrail.R": (None, None, (0.35, 0.35, 0.35)),
    }),
    # Frame 56 (PEAK IMPACT: EXPLOSIVE DOWNWARD DOUBLE-CLAW SLASH LUNGE!)
    (56, {
        "Hips":        ((0, 0.110, -0.065), (-25, 0, 0), (1, 1, 1)),
        "Spine":       (None, (-36, 0, 0), None),
        "Chest":       (None, (-28, 0, 0), None),
        "Neck":        (None, (-8, 0, 0), None),
        "Head":        (None, (-10, 0, 0), None),
        "UpperArm.L":  (None, (50, -8, 8), None),
        "Forearm.L":   (None, (38, 0, 4), None),
        "Hand.L":      (None, (22, 0, 0), None),
        "UpperArm.R":  (None, (55, 8, -8), None),
        "Forearm.R":   (None, (42, 0, -4), None),
        "Hand.R":      (None, (25, 0, 0), None),
        "UpperLeg.L":  (None, (32, 0, 6), None),
        "LowerLeg.L":  (None, (-50, 0, 0), None),
        "Foot.L":      (None, (18, 0, 0), None),
        "UpperLeg.R":  (None, (-30, 0, -6), None),
        "LowerLeg.R":  (None, (-12, 0, 0), None),
        "Foot.R":      (None, (-18, 0, 0), None),
        "ClawTrail.L": (None, None, (1.0, 1.0, 1.0)),
        "ClawTrail.R": (None, None, (1.0, 1.0, 1.0)),
    }),
    # Frame 60 (Phase 3: Overshoot / Ground Reach)
    (60, {
        "Hips":        ((0, 0.125, -0.075), (-28, 0, 0), (1, 1, 1)),
        "Spine":       (None, (-40, 0, 0), None),
        "Chest":       (None, (-30, 0, 0), None),
        "UpperArm.L":  (None, (62, 0, 6), None),
        "UpperArm.R":  (None, (65, 0, -6), None),
        "ClawTrail.L": (None, None, (0.45, 0.45, 0.45)),
        "ClawTrail.R": (None, None, (0.45, 0.45, 0.45)),
    }),
    # Frame 63 (Trail Dissolves)
    (63, {
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 66 (Phase 4: Zanshin / Hit-Stop Rigid Hold)
    (66, {
        "Hips":        ((0, 0.110, -0.065), (-24, 0, 0), (1, 1, 1)),
        "Spine":       (None, (-34, 0, 0), None),
        "Chest":       (None, (-24, 0, 0), None),
        "Head":        (None, (-6, 0, 0), None),
        "UpperArm.L":  (None, (48, 0, 10), None),
        "UpperArm.R":  (None, (52, 0, -10), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 70 (Zanshin Tremor / Breath Shudder)
    (70, {
        "Chest":       (None, (-27, 2, -1), None),
        "Head":        (None, (-10, -2, 2), None),
    }),
    # Frame 75 (Phase 5: Recovery Stumble)
    (75, {
        "Hips":        ((0, 0.040, -0.025), (-10, 3, -2), (1, 1, 1)),
        "Spine":       (None, (-18, 0, 0), None),
        "Chest":       (None, (-14, 0, 0), None),
        "UpperArm.L":  (None, (46, 0, 10), None),
        "UpperArm.R":  (None, (54, 0, -12), None),
        "UpperLeg.L":  (None, (5, 0, 0), None),
        "LowerLeg.L":  (None, (-18, 0, 0), None),
        "UpperLeg.R":  (None, (-8, 0, 0), None),
        "LowerLeg.R":  (None, (-12, 0, 0), None),
        "ClawTrail.L": (None, None, (0, 0, 0)),
        "ClawTrail.R": (None, None, (0, 0, 0)),
    }),
    # Frame 80: Full Reset back to Ready Shambling Stance (Matches Frame 1)
    (80, {
        "Hips":        ((0, 0, 0), (-6, 5, -3), (1, 1, 1)),
        "Spine":       (None, (-15, 0, -2), None),
        "Chest":       (None, (-10, -3, 3), None),
        "Neck":        (None, (5, 6, -5), None),
        "Head":        (None, (6, 10, -6), None),
        "UpperArm.L":  (None, (45, -8, 12), None),
        "Forearm.L":   (None, (20, 0, 5), None),
        "Hand.L":      (None, (-15, 0, -5), None),
        "UpperArm.R":  (None, (55, 8, -12), None),
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
# 7. Cycles Render Engine, Studio Lighting & Dynamic Framing
# -----------------------------------------------------------------
print(">>> Setting up Cycles AgX Render & Dynamic Depsgraph Camera...")
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
bg_node.inputs['Strength'].default_value = 0.60

# Dynamic Depsgraph Evaluated Camera Framing at Peak Attack Frame 56
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
    center = Vector((0, 0.15, 0.35))
    span = 0.75

print(f">>> Evaluated Scene Center: {center}, Span: {span:.3f}m")

# Independent Static Camera Target (Centered on character combat focus)
cam_target = bpy.data.objects.new("CamTarget_Zombie", None)
cam_target.location = center + Vector((0, 0.02, 0.02))
bpy.context.collection.objects.link(cam_target)

# Heroic Perspective Camera
cam_data = bpy.data.cameras.new("Zombie_HeroCamera")
cam_data.lens = 45
cam_obj = bpy.data.objects.new("Zombie_HeroCamera", object_data=cam_data)

# Elevated diagonal isometric framing (margin = 0.88 for 65-75% canvas occupancy)
margin = 0.88
fov_rad = cam_obj.data.angle
dist = (span * 0.5) / math.tan(fov_rad * 0.5) * margin
# View from front-left diagonal showing snarling face, glowing eye, exposed ribcage & slashing claws
cam_obj.location = center + Vector((dist * 0.60, -dist * 0.70, dist * 0.48))

track = cam_obj.constraints.new(type='TRACK_TO')
track.target = cam_target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

# 4-Point Studio Lighting
# 1) Key Sun Light: Warm crisp glint revealing cranium fracture and ribcage bones
key_sun = bpy.data.objects.new("Key_Sun", bpy.data.lights.new("Key_Sun", type='SUN'))
key_sun.data.energy = 4.2
key_sun.data.color = (1.0, 0.98, 0.92)
key_sun.data.angle = math.radians(4)
key_sun.rotation_euler = (math.radians(50), math.radians(20), math.radians(-35))
bpy.context.collection.objects.link(key_sun)

# 2) Front Specular Fill Light: Illuminates snarl, teeth, and grasping claws
front_fill = bpy.data.objects.new("Front_Fill", bpy.data.lights.new("Front_Fill", type='AREA'))
front_fill.data.energy = 200.0
front_fill.data.color = (0.88, 0.94, 1.00)
front_fill.data.size = 2.4
front_fill.location = (1.2, -1.6, 0.9)
front_fill.rotation_euler = (math.radians(35), math.radians(-20), math.radians(-40))
bpy.context.collection.objects.link(front_fill)

# 3) Toxic Lime / Green Rim Backlight: Accentuates undead silhouette and glowing eye
rim_toxic = bpy.data.objects.new("Rim_ToxicGreen", bpy.data.lights.new("Rim_ToxicGreen", type='AREA'))
rim_toxic.data.energy = 260.0
rim_toxic.data.color = (0.35, 0.95, 0.15)
rim_toxic.data.size = 2.2
rim_toxic.location = (-1.5, 1.5, 1.1)
rim_toxic.rotation_euler = (math.radians(-40), math.radians(40), math.radians(120))
bpy.context.collection.objects.link(rim_toxic)

# 4) Deep Shadow Fill Light: Soft ambient mood
dark_fill = bpy.data.objects.new("Fill_Shadow", bpy.data.lights.new("Fill_Shadow", type='AREA'))
dark_fill.data.energy = 130.0
dark_fill.data.color = (0.15, 0.10, 0.22)
dark_fill.data.size = 3.0
dark_fill.location = (0.6, 1.6, -0.2)
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

print(f">>> Rendering Key Impact Frame {ACTION_FRAME} (Double-Claw Strike) to {render_file}...")
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

print("=================================================================")
print(">>> [SUCCESS] Micro-Voxel Undead Zombie Generated & Exported!")
print("=================================================================")
