import bpy
import math
import os

print("=================================================================")
print(">>> [INFERNAL VOXEL ENGINE v4.0] Authentic Trove Flame Greatsword")
print("=================================================================")

# 1. Reset Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 60
scene.render.fps = 30

# 2. Materials Definition with rich saturation & controlled AgX emission
def make_shader(name, color, roughness=0.3, metallic=0.0, emission=0.0, emission_color=(0,0,0,1)):
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
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = emission
            bsdf.inputs['Emission Color'].default_value = emission_color
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = color
            
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

mats = {
    'dragon_gold':     make_shader('M_DragonGold',     (0.96, 0.74, 0.16, 1.0), roughness=0.20, metallic=0.94),
    'gold_bright':     make_shader('M_GoldBright',     (1.00, 0.90, 0.40, 1.0), roughness=0.16, metallic=0.96),
    'obsidian_leather':make_shader('M_ObsidianLeather',(0.06, 0.05, 0.06, 1.0), roughness=0.80, metallic=0.04),
    'star_metal':      make_shader('M_StarMetal',      (0.12, 0.12, 0.18, 1.0), roughness=0.24, metallic=0.85),
    'obsidian_iron':   make_shader('M_ObsidianIron',   (0.04, 0.04, 0.07, 1.0), roughness=0.28, metallic=0.85),
    'molten_ruby':     make_shader('M_MoltenRuby',     (0.96, 0.02, 0.10, 1.0), roughness=0.06, emission=2.5, emission_color=(1.0, 0.02, 0.10, 1.0)),
    'lava_glow':       make_shader('M_LavaGlow',       (1.00, 0.22, 0.00, 1.0), roughness=0.10, emission=2.0, emission_color=(1.0, 0.22, 0.00, 1.0)),
    'white_hot_core':  make_shader('M_WhiteHotCore',   (1.00, 0.92, 0.35, 1.0), roughness=0.06, emission=2.0, emission_color=(1.0, 0.92, 0.35, 1.0)),
    'luminous_yellow': make_shader('M_LuminousYellow', (1.00, 0.65, 0.00, 1.0), roughness=0.08, emission=1.6, emission_color=(1.0, 0.65, 0.00, 1.0)),
    'blazing_orange':  make_shader('M_BlazingOrange',  (1.00, 0.22, 0.00, 1.0), roughness=0.10, emission=1.3, emission_color=(1.0, 0.22, 0.00, 1.0)),
    'magma_crimson':   make_shader('M_MagmaCrimson',   (0.88, 0.03, 0.00, 1.0), roughness=0.14, emission=1.0, emission_color=(0.90, 0.03, 0.00, 1.0)),
    'smoldering_ash':  make_shader('M_SmolderingAsh',  (0.20, 0.05, 0.02, 1.0), roughness=0.85, metallic=0.1, emission=0.6, emission_color=(0.80, 0.08, 0.00, 1.0)),
    'plinth_dark':     make_shader('M_PlinthDark',     (0.04, 0.04, 0.06, 1.0), roughness=0.45, metallic=0.40),
}

VOXEL_SIZE = 0.012  # 1.2 cm micro-voxel scale

# 3. Model Generation
voxels = {}

def set_vox(x, y, z, mat, bone, overwrite=False):
    k = (int(x), int(y), int(z))
    if not overwrite and k in voxels:
        return
    voxels[k] = (mat, bone)

print("Building Pommel (Dragon Talon clutching Molten Ruby)...")
# Molten Ruby core: 3x3x4 faceted gem
for z in range(-19, -15):
    for x in range(-1, 2):
        for y in range(-1, 2):
            if abs(x) == 1 and abs(y) == 1 and (z == -19 or z == -16):
                continue
            mat = 'white_hot_core' if (x == 0 and y == 0 and z in (-18, -17)) else 'molten_ruby'
            set_vox(x, y, z, mat, 'Hilt', True)

# Pommel Base Cap
for x in range(-2, 3):
    for y in range(-2, 3):
        if x*x + y*y <= 5:
            m = 'gold_bright' if (x == 0 and y == 0) else 'dragon_gold'
            set_vox(x, y, -20, m, 'Hilt', True)

# Dragon Talon Claws wrapping the ruby
for z in range(-19, -15):
    # +X Talon
    for y in range(-1, 2):
        set_vox(2, y, z, 'gold_bright' if y == 0 else 'dragon_gold', 'Hilt', True)
    # -X Talon
    for y in range(-1, 2):
        set_vox(-2, y, z, 'gold_bright' if y == 0 else 'dragon_gold', 'Hilt', True)
    # +Y Talon
    for x in range(-1, 2):
        set_vox(x, 2, z, 'gold_bright' if x == 0 else 'dragon_gold', 'Hilt', True)
    # -Y Talon
    for x in range(-1, 2):
        set_vox(x, -2, z, 'gold_bright' if x == 0 else 'dragon_gold', 'Hilt', True)

# Claw Tips hooking inward at z = -16
set_vox(1, 0, -16, 'gold_bright', 'Hilt', True)
set_vox(-1, 0, -16, 'gold_bright', 'Hilt', True)
set_vox(0, 1, -16, 'gold_bright', 'Hilt', True)
set_vox(0, -1, -16, 'gold_bright', 'Hilt', True)

# Pommel Collar Ring
for z in range(-15, -13):
    for x in range(-2, 3):
        for y in range(-2, 3):
            if abs(x) == 2 and abs(y) == 2:
                continue
            if abs(x) == 2 or abs(y) == 2:
                m = 'blazing_orange' if (x == 0 or y == 0) else 'dragon_gold'
                set_vox(x, y, z, m, 'Hilt', True)
            else:
                set_vox(x, y, z, 'star_metal', 'Hilt', True)

print("Building Grip (Wrapped Obsidian Leather with Golden Rings)...")
for z in range(-13, 0):
    is_gold_ring = (z in (-11, -8, -5, -2))
    for x in range(-1, 2):
        for y in range(-1, 2):
            if abs(x) == 1 and abs(y) == 1:
                if is_gold_ring:
                    set_vox(x, y, z, 'dragon_gold', 'Hilt', True)
                continue
            if is_gold_ring:
                m = 'gold_bright' if (x == 0 or y == 0) else 'dragon_gold'
            else:
                m = 'obsidian_leather'
            set_vox(x, y, z, m, 'Hilt', True)

print("Building Crossguard (Dragon Wing Quillons with Molten Lava Channels)...")
# Central guard housing
for z in range(0, 7):
    for x in range(-3, 4):
        for y in range(-3, 4):
            if abs(x) == 3 and abs(y) == 3:
                continue
            if z in (2, 3, 4) and abs(x) <= 1:
                if abs(y) == 3:
                    m = 'white_hot_core' if (x == 0 and z == 3) else 'luminous_yellow'
                    set_vox(x, y, z, m, 'Hilt', True)
                    continue
                elif abs(y) == 2:
                    set_vox(x, y, z, 'blazing_orange', 'Hilt', True)
                    continue
            if abs(x) == 3 or abs(y) == 3 or z in (0, 6):
                set_vox(x, y, z, 'dragon_gold', 'Hilt', True)
            else:
                set_vox(x, y, z, 'star_metal', 'Hilt', True)

# Spreading Dragon Wing Quillons
for side in (-1, 1):
    for dist in range(4, 19):
        x = side * dist
        z_base = 1 + int((dist - 3) * 0.28)
        wing_height = 4 if dist < 14 else (5 if dist < 17 else 3)
        y_max = 2 if dist < 9 else 1
        
        for z in range(z_base, z_base + wing_height):
            for y in range(-y_max, y_max + 1):
                if y == 0 and z == z_base + 1:
                    m = 'white_hot_core' if (dist % 4 == 0) else 'lava_glow'
                elif z == z_base + wing_height - 1 or z == z_base or abs(x) == 18:
                    m = 'gold_bright' if dist in (10, 14, 18) else 'dragon_gold'
                elif abs(y) == y_max:
                    m = 'blazing_orange' if (dist % 3 == 0) else 'star_metal'
                else:
                    m = 'star_metal'
                set_vox(x, y, z, m, 'Hilt', True)
                
        if dist in (10, 14, 18):
            tip_z = z_base + wing_height
            set_vox(x, 0, tip_z, 'gold_bright', 'Hilt', True)
            set_vox(x, 0, tip_z + 1, 'white_hot_core', 'Hilt', True)

print("Building Blade (70 voxels long, Obsidian Fuller, Serrated Flame Gradient)...")
blade_widths = {}
for z in range(8, 79):
    if z <= 13:
        w = 6
    elif z <= 62:
        flame_wave = math.sin((z - 13) * (2.0 * math.pi / 9.5))
        w = 5 + int(max(0.0, flame_wave * 2.2 + 0.3))
    else:
        t = (z - 63) / 15.0
        w = max(0, int(round(5.0 * (1.0 - t))))
    blade_widths[z] = w
        
    for x in range(-w, w + 1):
        ax = abs(x)
        dist_from_edge = w - ax
        
        if ax <= 1:
            y_max = 1 if z < 72 else 0
        elif dist_from_edge <= 1:
            y_max = 0
        else:
            y_max = 1 if z < 50 else 0
            
        for y in range(-y_max, y_max + 1):
            ay = abs(y)
            if ax == 0 and ay == 0:
                if z >= 76:
                    m = 'white_hot_core'
                elif (z % 4) in (0, 1):
                    m = 'lava_glow'
                else:
                    m = 'magma_crimson'
            elif ax <= 2:
                m = 'obsidian_iron'
            elif dist_from_edge == 0:
                m = 'luminous_yellow' if (z % 2 == 0) else 'blazing_orange'
            elif dist_from_edge == 1:
                m = 'blazing_orange'
            elif dist_from_edge == 2:
                m = 'magma_crimson'
            else:
                m = 'obsidian_iron'
                
            set_vox(x, y, z, m, 'Blade_Bone', True)

print("Building Dynamic Fire Aura (Continuous Roaring Fire Wings + Spirals)...")

# A. FLAME CORE (Sharp licking flame tongue extending from sword tip z=79..85)
for z in range(79, 86):
    cw = max(0, int(round((85 - z) * 0.35)))
    for x in range(-cw, cw + 1):
        for y in range(-cw, cw + 1):
            if abs(x) + abs(y) <= cw:
                if z == 85:
                    m = 'magma_crimson'
                elif z >= 83:
                    m = 'blazing_orange'
                elif z >= 81:
                    m = 'luminous_yellow'
                else:
                    m = 'white_hot_core'
                set_vox(x, y, z, m, 'Flame_Core', False)

# B. FLAME OUTER LEFT (Continuous roaring stepped flame sheet along left edge)
for z in range(14, 82):
    bw = blade_widths.get(z, 3)
    reach = max(1, int(round(2.6 + 2.4 * math.sin(z * 0.32) + 1.2 * math.cos(z * 0.65))))
    x_inner = -(bw + 1)
    x_outer = x_inner - reach
    for x in range(x_outer, x_inner + 1):
        df = abs(x - x_outer)
        y_max = 1 if df > 1 and z < 68 else 0
        for y in range(-y_max, y_max + 1):
            if df == 0:
                m = 'magma_crimson'
            elif df == 1:
                m = 'blazing_orange'
            elif df == 2:
                m = 'luminous_yellow'
            else:
                m = 'white_hot_core'
            set_vox(x, y, z, m, 'Flame_Outer_Left', False)
            
    # Floating spark at crest tips
    if reach >= 5:
        set_vox(x_outer - 1, 0, z + 1, 'white_hot_core', 'Flame_Outer_Left', False)

# C. FLAME OUTER RIGHT (Continuous roaring stepped flame sheet along right edge - offset phase)
for z in range(14, 82):
    bw = blade_widths.get(z, 3)
    reach = max(1, int(round(2.6 + 2.4 * math.sin(z * 0.32 + 2.0) + 1.2 * math.cos(z * 0.65 + 1.0))))
    x_inner = bw + 1
    x_outer = x_inner + reach
    for x in range(x_inner, x_outer + 1):
        df = abs(x_outer - x)
        y_max = 1 if df > 1 and z < 68 else 0
        for y in range(-y_max, y_max + 1):
            if df == 0:
                m = 'magma_crimson'
            elif df == 1:
                m = 'blazing_orange'
            elif df == 2:
                m = 'luminous_yellow'
            else:
                m = 'white_hot_core'
            set_vox(x, y, z, m, 'Flame_Outer_Right', False)
            
    if reach >= 5:
        set_vox(x_outer + 1, 0, z + 1, 'white_hot_core', 'Flame_Outer_Right', False)

# D. FLAME SPIRALS (3D helical orbiting embers wrapping the greatsword)
for z in range(14, 78, 2):
    theta = (z - 14) * (6.0 * math.pi / 64.0)
    radius = 7.2 + 1.4 * math.sin(z * 0.22)
    x1 = int(round(radius * math.cos(theta)))
    y1 = int(round(radius * math.sin(theta)))
    x2 = int(round(radius * math.cos(theta + math.pi)))
    y2 = int(round(radius * math.sin(theta + math.pi)))
    
    m1 = 'white_hot_core' if (z % 6 == 0) else ('luminous_yellow' if (z % 4 == 0) else 'blazing_orange')
    m2 = 'blazing_orange' if (z % 6 == 0) else ('white_hot_core' if (z % 4 == 0) else 'luminous_yellow')
    
    set_vox(x1, y1, z, m1, 'Flame_Spirals', False)
    set_vox(x2, y2, z, m2, 'Flame_Spirals', False)
    # Extra spark voxel for volumetric richness
    if z % 4 == 0:
        set_vox(x1, y1, z + 1, 'magma_crimson', 'Flame_Spirals', False)
        set_vox(x2, y2, z + 1, 'magma_crimson', 'Flame_Spirals', False)

print(f"Total Voxels Generated: {len(voxels)}")

# 4. Construct Mesh with Strict Rigid Bone Boundaries
DIRECTIONS = [
    (( 1,  0,  0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
    ((-1,  0,  0), [(0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1)]),
    (( 0,  1,  0), [(1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)]),
    (( 0, -1,  0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
    (( 0,  0,  1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
    (( 0,  0, -1), [(0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)]),
]

used_mat_names = sorted(list(set(m for m, b in voxels.values())))
mat_to_idx = {m: i for i, m in enumerate(used_mat_names)}

verts = []
faces = []
face_mats = []
vert_groups = {}
vert_map = {}

for (vx, vy, vz), (mat_name, bone_name) in voxels.items():
    slot = mat_to_idx[mat_name]
    for (dx, dy, dz), qverts in DIRECTIONS:
        neighbor = (vx + dx, vy + dy, vz + dz)
        if neighbor not in voxels:
            quad = []
            for qx, qy, qz in qverts:
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

print(f"Constructing Mesh: {len(verts)} verts, {len(faces)} faces...")
mesh = bpy.data.meshes.new("Infernal_Flame_Sword_Mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

for m in used_mat_names:
    mesh.materials.append(mats[m])
for poly, slot in zip(mesh.polygons, face_mats):
    poly.material_index = slot
    
mesh.polygons.foreach_set('use_smooth', [False] * len(mesh.polygons))
mesh.update()

sword_obj = bpy.data.objects.new("Infernal_Flame_Sword", mesh)
bpy.context.collection.objects.link(sword_obj)

# Create Armature
print("Building Armature & Rigging...")
arm_data = bpy.data.armatures.new("Infernal_Armature_Data")
arm_obj = bpy.data.objects.new("Infernal_Armature", arm_data)
bpy.context.collection.objects.link(arm_obj)

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones

bone_root = eb.new("Root")
bone_root.head = (0, 0, 0)
bone_root.tail = (0, 0, 0.08)

bone_hilt = eb.new("Hilt")
bone_hilt.parent = bone_root
bone_hilt.head = (0, 0, -0.24)
bone_hilt.tail = (0, 0, 0.096)

bone_blade = eb.new("Blade_Bone")
bone_blade.parent = bone_hilt
bone_blade.head = (0, 0, 0.096)
bone_blade.tail = (0, 0, 0.94)

bone_f_core = eb.new("Flame_Core")
bone_f_core.parent = bone_blade
bone_f_core.head = (0, 0, 78 * VOXEL_SIZE)
bone_f_core.tail = (0, 0, 88 * VOXEL_SIZE)

bone_f_left = eb.new("Flame_Outer_Left")
bone_f_left.parent = bone_blade
bone_f_left.head = (-0.08, 0, 0.20)
bone_f_left.tail = (-0.08, 0, 0.96)

bone_f_right = eb.new("Flame_Outer_Right")
bone_f_right.parent = bone_blade
bone_f_right.head = (0.08, 0, 0.20)
bone_f_right.tail = (0.08, 0, 0.96)

bone_f_spiral = eb.new("Flame_Spirals")
bone_f_spiral.parent = bone_blade
bone_f_spiral.head = (0, 0, 0.16)
bone_f_spiral.tail = (0, 0, 0.95)

bpy.ops.object.mode_set(mode='OBJECT')

# Add Vertex Groups to Mesh
BONE_NAMES = ["Root", "Hilt", "Blade_Bone", "Flame_Core", "Flame_Outer_Left", "Flame_Outer_Right", "Flame_Spirals"]
vgroups = {b: sword_obj.vertex_groups.new(name=b) for b in BONE_NAMES}

bone_verts = {b: [] for b in BONE_NAMES}
for vidx, bname in vert_groups.items():
    bone_verts[bname].append(vidx)

for bname, vindices in bone_verts.items():
    if vindices:
        vgroups[bname].add(vindices, 1.0, 'REPLACE')

arm_mod = sword_obj.modifiers.new(name="Armature", type='ARMATURE')
arm_mod.object = arm_obj
arm_mod.use_vertex_groups = True
sword_obj.parent = arm_obj

# 5. Keyframe Animation (60 frames @ 30fps)
print("Setting up Keyframe Animation...")
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')

pose_root = arm_obj.pose.bones["Root"]
pose_hilt = arm_obj.pose.bones["Hilt"]
pose_blade = arm_obj.pose.bones["Blade_Bone"]
pose_f_core = arm_obj.pose.bones["Flame_Core"]
pose_f_left = arm_obj.pose.bones["Flame_Outer_Left"]
pose_f_right = arm_obj.pose.bones["Flame_Outer_Right"]
pose_f_spiral = arm_obj.pose.bones["Flame_Spirals"]

all_bones = [pose_root, pose_hilt, pose_blade, pose_f_core, pose_f_left, pose_f_right, pose_f_spiral]
for pb in all_bones:
    pb.rotation_mode = 'XYZ'

def kf(pb, frame):
    pb.keyframe_insert(data_path="location", frame=frame)
    pb.keyframe_insert(data_path="rotation_euler", frame=frame)
    pb.keyframe_insert(data_path="scale", frame=frame)

# =============================================================================
# FRAME 1: Rest / Poised Presentation Stance
# =============================================================================
pose_root.location = (0, 0, 0)
pose_root.rotation_euler = (0, 0, 0)

pose_hilt.location = (0, 0, 0.28)
pose_hilt.rotation_euler = (math.radians(-6), math.radians(8), math.radians(-12))

pose_blade.location = (0, 0, 0)
pose_blade.rotation_euler = (0, 0, 0)
pose_blade.scale = (1, 1, 1)

pose_f_core.location = (0, 0, 0)
pose_f_core.rotation_euler = (0, 0, 0)
pose_f_core.scale = (1.0, 1.0, 1.0)

pose_f_left.location = (0, 0, 0)
pose_f_left.rotation_euler = (0, 0, 0)
pose_f_left.scale = (1.0, 1.0, 1.0)

pose_f_right.location = (0, 0, 0)
pose_f_right.rotation_euler = (0, 0, 0)
pose_f_right.scale = (1.0, 1.0, 1.0)

pose_f_spiral.location = (0, 0, 0)
pose_f_spiral.rotation_euler = (0, 0, 0)
pose_f_spiral.scale = (1.0, 1.0, 1.0)

for pb in all_bones:
    kf(pb, 1)

# =============================================================================
# FRAME 10: Idle Flame Surge (Flames expand, pulse and undulate)
# =============================================================================
pose_hilt.location = (0, 0, 0.31)
pose_hilt.rotation_euler = (math.radians(-3), math.radians(10), math.radians(-10))

pose_f_core.scale = (1.15, 1.16, 1.12)
pose_f_core.location = (0, 0.01, 0)

pose_f_left.location = (-0.008, 0, 0.01)
pose_f_left.rotation_euler = (math.radians(-4), math.radians(6), math.radians(4))
pose_f_left.scale = (1.18, 1.12, 1.10)

pose_f_right.location = (0.006, 0, -0.01)
pose_f_right.rotation_euler = (math.radians(4), math.radians(-6), math.radians(-4))
pose_f_right.scale = (0.95, 1.05, 0.95)

# Orbiting swirl around blade length axis (Local Y!)
pose_f_spiral.rotation_euler = (0, math.radians(90), 0)
pose_f_spiral.scale = (1.10, 1.05, 1.10)

for pb in all_bones:
    kf(pb, 10)

# =============================================================================
# FRAME 20: Pre-Windup Tension
# =============================================================================
pose_hilt.location = (0, 0, 0.28)
pose_hilt.rotation_euler = (math.radians(-6), math.radians(8), math.radians(-12))

pose_f_core.scale = (1.0, 1.0, 1.0)
pose_f_core.location = (0, 0, 0)
pose_f_left.scale = (1.0, 1.0, 1.0)
pose_f_left.location = (0, 0, 0)
pose_f_left.rotation_euler = (0, 0, 0)
pose_f_right.scale = (1.0, 1.0, 1.0)
pose_f_right.location = (0, 0, 0)
pose_f_right.rotation_euler = (0, 0, 0)
pose_f_spiral.rotation_euler = (0, math.radians(180), 0)
pose_f_spiral.scale = (1.0, 1.0, 1.0)

for pb in all_bones:
    kf(pb, 20)

# =============================================================================
# FRAME 24: WINDUP / CHARGE (Sword pulled back high, fire sucks inward)
# =============================================================================
pose_hilt.location = (-0.08, -0.10, 0.36)
pose_hilt.rotation_euler = (math.radians(-42), math.radians(22), math.radians(28))

pose_blade.rotation_euler = (math.radians(-3), 0, math.radians(2))

pose_f_core.scale = (0.85, 0.88, 0.88)
pose_f_left.location = (0.008, 0, 0)
pose_f_left.scale = (0.85, 0.88, 0.85)
pose_f_right.location = (-0.008, 0, 0)
pose_f_right.scale = (0.85, 0.88, 0.85)
pose_f_spiral.scale = (0.80, 0.85, 0.80)
pose_f_spiral.rotation_euler = (0, math.radians(240), 0)

for pb in all_bones:
    kf(pb, 24)

# =============================================================================
# FRAME 28: HEAVY FLAMING SLASH CLEAVE & EXPLOSIVE BURST!
# Broad face displays heroically to camera, flames erupting in dynamic wings
# =============================================================================
pose_hilt.location = (0.02, 0.04, 0.22)
pose_hilt.rotation_euler = (math.radians(22), math.radians(-12), math.radians(-40))

pose_blade.rotation_euler = (math.radians(4), 0, math.radians(-3))

# Massive Explosive Fire Eruption!
pose_f_core.location = (0, 0.02, 0)
pose_f_core.rotation_euler = (math.radians(5), 0, 0)
pose_f_core.scale = (1.35, 1.55, 1.30)

pose_f_left.location = (-0.015, 0.01, 0)
pose_f_left.rotation_euler = (math.radians(-6), math.radians(8), math.radians(10))
pose_f_left.scale = (1.35, 1.28, 1.20)

pose_f_right.location = (0.015, 0.01, 0)
pose_f_right.rotation_euler = (math.radians(6), math.radians(-8), math.radians(-10))
pose_f_right.scale = (1.35, 1.28, 1.20)

pose_f_spiral.location = (0, 0.02, 0)
pose_f_spiral.scale = (1.38, 1.18, 1.38)
pose_f_spiral.rotation_euler = (math.radians(4), math.radians(420), 0)

for pb in all_bones:
    kf(pb, 28)

# =============================================================================
# FRAME 32: SLASH OVERSHOOT (Flames stretch along trailing momentum)
# =============================================================================
pose_hilt.location = (0.04, 0.06, 0.18)
pose_hilt.rotation_euler = (math.radians(28), math.radians(-8), math.radians(-46))

pose_blade.rotation_euler = (math.radians(2), 0, math.radians(-1))

pose_f_core.scale = (1.25, 1.40, 1.18)
pose_f_left.scale = (1.25, 1.20, 1.12)
pose_f_right.scale = (1.25, 1.20, 1.12)
pose_f_spiral.rotation_euler = (0, math.radians(500), 0)

for pb in all_bones:
    kf(pb, 32)

# =============================================================================
# FRAME 38: RECOVERY INITIATION (Sword begins ascending smoothly)
# =============================================================================
pose_hilt.location = (0.02, 0.03, 0.22)
pose_hilt.rotation_euler = (math.radians(12), 0, math.radians(-26))

pose_blade.rotation_euler = (0, 0, 0)

pose_f_core.scale = (1.12, 1.18, 1.10)
pose_f_left.scale = (1.15, 1.12, 1.08)
pose_f_right.scale = (1.15, 1.12, 1.08)
pose_f_spiral.rotation_euler = (0, math.radians(570), 0)

for pb in all_bones:
    kf(pb, 38)

# =============================================================================
# FRAME 48: HIGH FLOURISH RETURN
# =============================================================================
pose_hilt.location = (0.01, 0.01, 0.26)
pose_hilt.rotation_euler = (0, math.radians(4), math.radians(-16))

pose_f_core.scale = (1.06, 1.05, 1.06)
pose_f_left.scale = (1.08, 1.06, 1.06)
pose_f_right.scale = (1.08, 1.06, 1.06)
pose_f_spiral.rotation_euler = (0, math.radians(650), 0)

for pb in all_bones:
    kf(pb, 48)

# =============================================================================
# FRAME 60: SEAMLESS LOOP TO FRAME 1
# =============================================================================
pose_hilt.location = (0, 0, 0.28)
pose_hilt.rotation_euler = (math.radians(-6), math.radians(8), math.radians(-12))

pose_blade.location = (0, 0, 0)
pose_blade.rotation_euler = (0, 0, 0)
pose_blade.scale = (1, 1, 1)

pose_f_core.location = (0, 0, 0)
pose_f_core.rotation_euler = (0, 0, 0)
pose_f_core.scale = (1.0, 1.0, 1.0)

pose_f_left.location = (0, 0, 0)
pose_f_left.rotation_euler = (0, 0, 0)
pose_f_left.scale = (1.0, 1.0, 1.0)

pose_f_right.location = (0, 0, 0)
pose_f_right.rotation_euler = (0, 0, 0)
pose_f_right.scale = (1.0, 1.0, 1.0)

pose_f_spiral.location = (0, 0, 0)
pose_f_spiral.rotation_euler = (0, math.radians(720), 0)
pose_f_spiral.scale = (1.0, 1.0, 1.0)

for pb in all_bones:
    kf(pb, 60)

bpy.ops.object.mode_set(mode='OBJECT')

# 6. Display Altar Plinth (Tiered Dark Obsidian Forge Altar with Magma Veins)
plinth_voxels = {}

# Tier 1 (Base): z in [-28, -25], radius 24
for pz in range(-28, -24):
    for px in range(-24, 25):
        for py in range(-24, 25):
            d2 = px*px + py*py
            if d2 <= 520:
                if d2 >= 440 or pz == -28:
                    pm = 'dragon_gold' if (abs(px) == abs(py) or px == 0 or py == 0) else 'plinth_dark'
                else:
                    pm = 'plinth_dark'
                plinth_voxels[(px, py, pz)] = pm

# Tier 2 (Upper Altar): z in [-24, -21], radius 17
for pz in range(-24, -20):
    for px in range(-17, 18):
        for py in range(-17, 18):
            d2 = px*px + py*py
            if d2 <= 280:
                if 160 <= d2 <= 240 and pz == -21:
                    pm = 'lava_glow' if ((px + py) % 3 == 0) else 'blazing_orange'
                elif d2 <= 36 and pz == -21:
                    pm = 'molten_ruby'
                else:
                    pm = 'plinth_dark'
                plinth_voxels[(px, py, pz)] = pm

plinth_verts = []
plinth_faces = []
plinth_mats = []
plinth_used_mats = sorted(list(set(plinth_voxels.values())))
plinth_mat_idx = {m: i for i, m in enumerate(plinth_used_mats)}
plinth_vmap = {}

for (vx, vy, vz), mname in plinth_voxels.items():
    slot = plinth_mat_idx[mname]
    for (dx, dy, dz), qverts in DIRECTIONS:
        nbr = (vx + dx, vy + dy, vz + dz)
        if nbr not in plinth_voxels:
            quad = []
            for qx, qy, qz in qverts:
                p = (
                    round((vx + qx) * VOXEL_SIZE, 6),
                    round((vy + qy) * VOXEL_SIZE, 6),
                    round((vz + qz) * VOXEL_SIZE, 6)
                )
                if p not in plinth_vmap:
                    plinth_vmap[p] = len(plinth_verts)
                    plinth_verts.append(p)
                quad.append(plinth_vmap[p])
            plinth_faces.append(quad)
            plinth_mats.append(slot)

plinth_mesh = bpy.data.meshes.new("Display_Plinth_Mesh")
plinth_mesh.from_pydata(plinth_verts, [], plinth_faces)
for m in plinth_used_mats:
    plinth_mesh.materials.append(mats[m])
for poly, slot in zip(plinth_mesh.polygons, plinth_mats):
    poly.material_index = slot
plinth_mesh.polygons.foreach_set('use_smooth', [False] * len(plinth_mesh.polygons))
plinth_mesh.update()

plinth_obj = bpy.data.objects.new("Display_Plinth", plinth_mesh)
plinth_obj.location = (0, 0, -0.04)
bpy.context.collection.objects.link(plinth_obj)

# 7. Cycles AgX Beauty Lighting & Auto-Framed Camera
scene.frame_set(10)  # Heroic Stance with Living Dancing Flames!
scene.render.engine = 'CYCLES'

try:
    cprefs = bpy.context.preferences.addons['cycles'].preferences
    cprefs.compute_device_type = 'CUDA'
    cprefs.get_devices()
    for d in cprefs.devices:
        d.use = True
    scene.cycles.device = 'GPU'
except Exception:
    scene.cycles.device = 'CPU'

scene.cycles.samples = 128
scene.render.resolution_x = 1280
scene.render.resolution_y = 1280
scene.render.film_transparent = False

# Atmospheric World
world = bpy.data.worlds.new("Voxel_Inferno_World")
world.use_nodes = True
bg_node = world.node_tree.nodes['Background']
bg_node.inputs['Color'].default_value = (0.015, 0.018, 0.028, 1.0)
bg_node.inputs['Strength'].default_value = 0.35
scene.world = world

scene.view_settings.view_transform = 'AgX' if hasattr(scene.view_settings, 'view_transform') else 'Filmic'
scene.view_settings.look = 'AgX - High Contrast'

# Compute Evaluated Sword Bounds at Frame 10 for Perfect Heroic Framing
depsgraph = bpy.context.evaluated_depsgraph_get()
eval_obj = sword_obj.evaluated_get(depsgraph)
eval_mesh = eval_obj.to_mesh()
verts = [eval_obj.matrix_world @ v.co for v in eval_mesh.vertices]
eval_obj.to_mesh_clear()

xs = [v.x for v in verts]
ys = [v.y for v in verts]
zs = [v.z for v in verts]
cx = (min(xs) + max(xs)) / 2.0
cy = (min(ys) + max(ys)) / 2.0
cz = (min(zs) + max(zs)) / 2.0
span_x = max(xs) - min(xs)
span_y = max(ys) - min(ys)
span_z = max(zs) - min(zs)
print(f">>> [EVALUATED FRAME 10] Center: ({cx:.3f}, {cy:.3f}, {cz:.3f}), Span: ({span_x:.3f}, {span_y:.3f}, {span_z:.3f})")

target_emp = bpy.data.objects.new("Target_Aim", None)
target_emp.location = (cx, cy, cz)
bpy.context.collection.objects.link(target_emp)

# Heroic 3/4 Perspective Camera Framing
cam_data = bpy.data.cameras.new("Sword_Camera")
cam_data.lens = 52
cam_obj = bpy.data.objects.new("Sword_Camera", object_data=cam_data)
cam_obj.location = (cx + 1.15, cy - 2.15, cz + 0.25)

track = cam_obj.constraints.new(type='TRACK_TO')
track.target = target_emp
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Dramatic 3-Point Lighting
key_l = bpy.data.objects.new("Key_Warm", bpy.data.lights.new("Key_Warm", type='SUN'))
key_l.data.energy = 3.5
key_l.data.color = (1.0, 0.95, 0.90)
key_l.data.angle = math.radians(8)
key_l.rotation_euler = (math.radians(52), math.radians(24), math.radians(-35))
bpy.context.collection.objects.link(key_l)

rim_l = bpy.data.objects.new("Rim_Inferno", bpy.data.lights.new("Rim_Inferno", type='AREA'))
rim_l.data.energy = 360.0
rim_l.data.color = (1.0, 0.38, 0.04)
rim_l.data.size = 2.5
rim_l.location = (cx - 1.2, cy + 2.0, cz + 0.8)
rim_l.rotation_euler = (math.radians(-50), math.radians(15), math.radians(140))
bpy.context.collection.objects.link(rim_l)

fill_l = bpy.data.objects.new("Fill_Sapphire", bpy.data.lights.new("Fill_Sapphire", type='AREA'))
fill_l.data.energy = 150.0
fill_l.data.color = (0.12, 0.45, 0.95)
fill_l.data.size = 3.2
fill_l.location = (cx + 2.0, cy - 1.8, cz - 0.3)
fill_l.rotation_euler = (math.radians(35), math.radians(-20), math.radians(-45))
bpy.context.collection.objects.link(fill_l)

# Paths
workspace_dir = os.path.abspath(os.path.dirname(__file__))
blend_file = os.path.join(workspace_dir, "infernal_flame_sword.blend")
glb_file = os.path.join(workspace_dir, "infernal_flame_sword.glb")
render_file = os.path.join(workspace_dir, "infernal_flame_sword_render.png")

print(f"Saving .blend: {blend_file}")
bpy.ops.wm.save_as_mainfile(filepath=blend_file)

print(f"Exporting GLB: {glb_file}")
bpy.ops.export_scene.gltf(
    filepath=glb_file,
    export_format='GLB',
    use_selection=False,
    export_materials='EXPORT',
    export_yup=True,
    export_animations=True,
    export_frame_range=True,
    export_frame_step=1,
    export_anim_single_armature=True
)

print(f"Rendering frame 28 to {render_file}...")
scene.render.filepath = render_file
bpy.ops.render.render(write_still=True)

print("=================================================================")
print(">>> [SUCCESS] Infernal Flame Sword Created, Rigged & Rendered!")
print("=================================================================")
