import bpy
import math
import os
import base64

print("=================================================================")
print(">>> [GUTS DRAGON SLAYER ENGINE v4.0] Authentic Trove Micro-Voxel")
print("=================================================================")

# 1. Reset Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 60
scene.render.fps = 30

VOXEL_SIZE = 0.012  # 1.2 cm micro-voxel scale

# 2. Materials Definition
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
    # Raw battle-hardened steel (Metallic 0.85, Roughness 0.35 per specification)
    'raw_steel':       make_shader('M_RawSteel',       (0.32, 0.35, 0.40, 1.0), roughness=0.35, metallic=0.85),
    'raw_steel_dark':  make_shader('M_RawSteelDark',   (0.22, 0.24, 0.28, 1.0), roughness=0.38, metallic=0.82),
    'steel_bevel':     make_shader('M_SteelBevel',      (0.55, 0.60, 0.68, 1.0), roughness=0.25, metallic=0.88),
    'cutting_edge':    make_shader('M_CuttingEdge',     (0.88, 0.92, 0.98, 1.0), roughness=0.15, metallic=0.92),
    'fuller_dark':     make_shader('M_FullerDark',      (0.14, 0.15, 0.18, 1.0), roughness=0.55, metallic=0.75),
    'blood_stain':     make_shader('M_BloodStain',      (0.50, 0.04, 0.08, 1.0), roughness=0.35, metallic=0.45, emission=1.5, emission_color=(0.55, 0.04, 0.08, 1.0)),
    'battle_notch':    make_shader('M_BattleNotch',     (0.18, 0.15, 0.15, 1.0), roughness=0.70, metallic=0.50),
    
    # Cast-iron fittings
    'cast_iron':       make_shader('M_CastIron',        (0.18, 0.20, 0.23, 1.0), roughness=0.40, metallic=0.80),
    'iron_highlight':  make_shader('M_IronHighlight',   (0.44, 0.48, 0.55, 1.0), roughness=0.28, metallic=0.85),
    'steel_rivet':     make_shader('M_SteelRivet',      (0.88, 0.90, 0.96, 1.0), roughness=0.15, metallic=0.95),
    
    # Grip wraps
    'bandage_white':   make_shader('M_BandageWhite',    (0.88, 0.85, 0.78, 1.0), roughness=0.88, metallic=0.00),
    'bandage_tan':     make_shader('M_BandageTan',      (0.72, 0.66, 0.56, 1.0), roughness=0.85, metallic=0.00),
    'bandage_dark':    make_shader('M_BandageDark',     (0.48, 0.42, 0.34, 1.0), roughness=0.92, metallic=0.00),
    'under_leather':   make_shader('M_UnderLeather',    (0.12, 0.09, 0.07, 1.0), roughness=0.80, metallic=0.05),
    'leather_strap':   make_shader('M_LeatherStrap',    (0.25, 0.18, 0.13, 1.0), roughness=0.75, metallic=0.05),
    
    # Impact Shards & Embers
    'rock_dark':       make_shader('M_RockDark',        (0.16, 0.17, 0.20, 1.0), roughness=0.85, metallic=0.10),
    'rock_light':      make_shader('M_RockLight',       (0.42, 0.45, 0.52, 1.0), roughness=0.75, metallic=0.10),
    'impact_ember':    make_shader('M_ImpactEmber',     (1.00, 0.42, 0.04, 1.0), roughness=0.06, emission=22.0, emission_color=(1.0, 0.46, 0.06, 1.0)),
    
    # Display Plinth (Dark fractured battlefield stone)
    'plinth_stone':    make_shader('M_PlinthStone',     (0.11, 0.12, 0.15, 1.0), roughness=0.85, metallic=0.15),
    'plinth_crack':    make_shader('M_PlinthCrack',     (0.04, 0.04, 0.06, 1.0), roughness=0.95, metallic=0.05),
    'plinth_rim':      make_shader('M_PlinthRim',       (0.24, 0.26, 0.30, 1.0), roughness=0.60, metallic=0.40),
}

# 3. Model Generation
voxels = {}

def set_vox(x, y, z, mat, bone, overwrite=False):
    k = (int(x), int(y), int(z))
    if not overwrite and k in voxels:
        return
    voxels[k] = (mat, bone)

print("Building Pommel (Heavy circular forged iron counterweight)...")
# Pommel Base & Counterweight Disc: z = -26 to -22
for z in range(-26, -21):
    r_max = 4.0 if z in (-25, -24) else 3.5
    for x in range(-4, 5):
        for y in range(-4, 5):
            d2 = x*x + y*y
            if d2 <= r_max * r_max:
                if z == -26 and d2 <= 2.0:
                    m = 'steel_rivet'
                elif d2 >= (r_max - 1.0) * (r_max - 1.0):
                    m = 'iron_highlight'
                else:
                    m = 'cast_iron'
                set_vox(x, y, z, m, 'Hilt', True)

# Iron Collar connecting Pommel to Grip: z = -21 to -19
for z in range(-21, -19):
    for x in range(-3, 4):
        for y in range(-3, 4):
            d2 = x*x + y*y
            if d2 <= 7:
                if (abs(x) == 2 and y == 0) or (abs(y) == 2 and x == 0):
                    m = 'steel_rivet'
                elif d2 >= 5:
                    m = 'iron_highlight'
                else:
                    m = 'cast_iron'
                set_vox(x, y, z, m, 'Hilt', True)

print("Building Grip (Two-handed bastard grip with weathered cloth bandages & strapping)...")
# Grip: z = -19 to 0 (20 voxels tall = 24 cm)
for z in range(-19, 0):
    for x in range(-1, 2):
        for y in range(-1, 2):
            is_corner = (abs(x) == 1 and abs(y) == 1)
            is_center = (x == 0 and y == 0)
            
            if is_center:
                m = 'under_leather'
            else:
                # Procedural spiral bandage wrap with criss-cross leather strapping
                wrap_diag1 = (z + x + 2*y + 40) % 5
                wrap_diag2 = (z - 2*x + y + 40) % 5
                
                if wrap_diag2 == 0:
                    m = 'leather_strap'
                elif wrap_diag1 in (0, 1):
                    m = 'bandage_white'
                elif wrap_diag1 == 2:
                    m = 'bandage_tan'
                elif wrap_diag1 == 3:
                    m = 'bandage_dark'
                else:
                    m = 'under_leather'
                    
                if is_corner and m == 'bandage_white':
                    m = 'bandage_tan'
                    
            set_vox(x, y, z, m, 'Hilt', True)

print("Building Crossguard (Heavy blocky cast-iron rectangular crossbar with rivets & bevels)...")
# Crossguard: z = 0 to 5 (6 voxels tall)
# Span X in [-13, 13] (27 voxels wide = 32.4 cm)
for x in range(-13, 14):
    y_max = 2 if abs(x) >= 6 else 3
    z_max = 4 if abs(x) >= 6 else 5
    
    for y in range(-y_max, y_max + 1):
        for z in range(0, z_max + 1):
            # Outer bevels on ends
            if abs(x) == 13:
                if abs(y) == y_max or z in (0, z_max):
                    continue
            
            # Central reinforced housing & steel rivets
            if abs(x) <= 5:
                if abs(y) == 3 and abs(x) in (0, 3) and z in (1, 4):
                    m = 'steel_rivet'
                elif abs(y) == 3 or z in (0, 5) or abs(x) == 5:
                    m = 'iron_highlight'
                else:
                    m = 'cast_iron'
            else:
                if abs(y) == y_max or z in (0, z_max) or abs(x) in (12, 13):
                    m = 'iron_highlight'
                else:
                    m = 'cast_iron'
                    
            set_vox(x, y, z, m, 'Hilt', True)

print("Building Blade Base Collar / Ricasso Clamp...")
# Blade Collar: z = 6 to 9
for z in range(6, 10):
    y_lim = 2 if z in (6, 7) else 1
    for x in range(-6, 7):
        for y in range(-y_lim, y_lim + 1):
            if abs(x) == 6 and abs(y) == y_lim:
                continue
            if z in (6, 7) and abs(x) == 4 and abs(y) == y_lim:
                m = 'steel_rivet'
            elif abs(x) == 6 or abs(y) == y_lim or z == 6:
                m = 'iron_highlight'
            else:
                m = 'cast_iron'
            set_vox(x, y, z, m, 'Hilt', True)

print("Building Colossal Blade Slab (Raw battle-hardened steel, fuller spine, worn bevels, battle notches)...")
battle_notches = {
    24: 8,
    41: -8,
    58: 8,
    73: -8,
    82: 7
}

for z in range(10, 96):
    # Silhouette width taper
    if z <= 84:
        half_w = 8
    elif z <= 86:
        half_w = 7
    elif z <= 88:
        half_w = 6
    elif z <= 90:
        half_w = 5
    elif z <= 92:
        half_w = 4
    elif z <= 93:
        half_w = 3
    elif z <= 94:
        half_w = 2
    elif z == 95:
        half_w = 1

    for x in range(-half_w, half_w + 1):
        if z in battle_notches and x == battle_notches[z]:
            continue  # Exposed chipped battle notch!
            
        dist_from_edge = half_w - abs(x)
        
        # Cross-sectional thickness profile
        if z >= 93:
            y_thick = 0 if dist_from_edge <= 1 else 1
        elif z >= 88:
            y_thick = 0 if dist_from_edge == 0 else 1
        else:
            if dist_from_edge == 0:
                y_thick = 0  # Cutting edge
            elif dist_from_edge == 1:
                y_thick = 0  # Sharp bevel
            elif dist_from_edge == 2:
                y_thick = 1  # Outer transition
            elif abs(x) == 2:
                y_thick = 2  # Raised spine ridge
            elif abs(x) <= 1:
                y_thick = 1  # Recessed dark fuller channel
            else:
                y_thick = 1  # Main colossal steel flat
                
        for y in range(-y_thick, y_thick + 1):
            if dist_from_edge == 0:
                m = 'cutting_edge'
            elif dist_from_edge == 1:
                if z in battle_notches and abs(x - battle_notches[z]) == 1:
                    m = 'battle_notch'
                else:
                    m = 'steel_bevel'
            elif abs(x) <= 1 and y in (-y_thick, y_thick) and z <= 84:
                if (z % 13) in (3, 7):
                    m = 'blood_stain'  # Dark apostle blood patina
                else:
                    m = 'fuller_dark'
            elif abs(x) == 2 and abs(y) == 2:
                m = 'steel_bevel'
            else:
                m = 'raw_steel' if ((x + z) % 7 != 0) else 'raw_steel_dark'
                
            set_vox(x, y, z, m, 'Blade_Bone', True)

# Apex sharp tip voxel
set_vox(0, 0, 96, 'cutting_edge', 'Blade_Bone', True)

print("Building Animated Impact Shards (Rock debris & glowing kinetic embers)...")
# Shard voxels modeled radiating from impact point (0, 0, 0)
shard_clusters = [
    # Chunk A (Left-front sharp block)
    [(-5, 4, 3), (-4, 4, 3), (-5, 5, 3), (-4, 5, 3), (-5, 4, 4), (-4, 4, 4), (-6, 5, 3)],
    # Chunk B (Right-front flying boulder)
    [(5, 4, 4), (6, 4, 4), (5, 5, 4), (6, 5, 4), (5, 4, 5), (6, 4, 5), (7, 4, 4)],
    # Chunk C (High flying shard)
    [(3, -4, 5), (4, -4, 5), (3, -5, 5), (3, -4, 6), (4, -4, 6), (4, -5, 6)],
    # Chunk D (Left-rear chunk)
    [(-4, -4, 4), (-5, -4, 4), (-4, -5, 4), (-4, -4, 5), (-5, -5, 4)],
    # Chunk E (Front wedge)
    [(0, 6, 3), (1, 6, 3), (0, 7, 3), (0, 6, 4), (1, 7, 3)],
    # Chunk F (Right side secondary)
    [(7, 1, 3), (7, 2, 3), (8, 2, 3), (8, 1, 4)],
    # Chunk G (Left side secondary)
    [(-7, 1, 3), (-7, 2, 3), (-8, 2, 3), (-8, 1, 4)],
    # Chunk H (Rear ejecta)
    [(0, -6, 4), (1, -6, 4), (0, -7, 4)]
]

for idx, cluster in enumerate(shard_clusters):
    for px, py, pz in cluster:
        sm = 'rock_light' if (px + py + pz) % 2 == 0 else 'rock_dark'
        set_vox(px, py, pz, sm, 'Debris_Bone', True)

# Flying Kinetic Impact Embers (high-intensity sparks)
impact_embers = [
    (-3, 3, 6), (4, 4, 7), (1, -4, 8), (5, -2, 6),
    (-4, -3, 7), (2, 5, 5), (0, 3, 9), (-2, -2, 8),
    (3, 2, 8), (-1, 5, 6), (4, -1, 9), (0, -2, 10),
    (-5, 2, 7), (6, 2, 8), (2, -6, 7), (-3, 6, 6)
]
for px, py, pz in impact_embers:
    set_vox(px, py, pz, 'impact_ember', 'Debris_Bone', True)

print(f">>> Total Sword Voxels: {len(voxels)}")

# 4. Construct Mesh with Rigid Bone Boundaries
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

print(f"Constructing Sword Mesh: {len(verts)} vertices, {len(faces)} faces...")
mesh = bpy.data.meshes.new("Guts_Dragon_Slayer_Mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

for m in used_mat_names:
    mesh.materials.append(mats[m])
for poly, slot in zip(mesh.polygons, face_mats):
    poly.material_index = slot
    
mesh.polygons.foreach_set('use_smooth', [False] * len(mesh.polygons))
mesh.update()

sword_obj = bpy.data.objects.new("Guts_Dragon_Slayer", mesh)
bpy.context.collection.objects.link(sword_obj)

# 5. Build Armature & Rigging (Aligned to World Axes for Intuitive Kinematics)
print("Building Armature with Root, Hilt, Blade_Bone, Debris_Bone...")
arm_data = bpy.data.armatures.new("DragonSlayer_Armature_Data")
arm_obj = bpy.data.objects.new("DragonSlayer_Armature", arm_data)
bpy.context.collection.objects.link(arm_obj)

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones

# All bones aligned along +Y so bone local axes exactly equal world XYZ!
bone_root = eb.new("Root")
bone_root.head = (0, 0, 0)
bone_root.tail = (0, 0.10, 0)

# Hilt pivot is at crossguard center (0, 0, 0)
bone_hilt = eb.new("Hilt")
bone_hilt.parent = bone_root
bone_hilt.head = (0, 0, 0)
bone_hilt.tail = (0, 0.10, 0)

# Blade pivot is at crossguard/blade junction (0, 0, 0.072)
bone_blade = eb.new("Blade_Bone")
bone_blade.parent = bone_hilt
bone_blade.head = (0, 0, 0.072)
bone_blade.tail = (0, 0.172, 0.072)

# Debris pivot is at ground impact center (0, 0, 0)
bone_debris = eb.new("Debris_Bone")
bone_debris.parent = bone_root
bone_debris.head = (0, 0, 0)
bone_debris.tail = (0, 0.10, 0)

bpy.ops.object.mode_set(mode='OBJECT')

# Add Vertex Groups to Mesh
BONE_NAMES = ["Root", "Hilt", "Blade_Bone", "Debris_Bone"]
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

# 6. Keyframe Animation (60 frames @ 30fps)
print("Keyframing Berserk Overhead Ground-Slam Animation...")
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')

pose_root = arm_obj.pose.bones["Root"]
pose_hilt = arm_obj.pose.bones["Hilt"]
pose_blade = arm_obj.pose.bones["Blade_Bone"]
pose_debris = arm_obj.pose.bones["Debris_Bone"]

all_bones = [pose_root, pose_hilt, pose_blade, pose_debris]
for pb in all_bones:
    pb.rotation_mode = 'XYZ'

def kf_all(frame):
    for pb in all_bones:
        pb.keyframe_insert(data_path="location", frame=frame)
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)
        pb.keyframe_insert(data_path="scale", frame=frame)

# =============================================================================
# FRAME 1: Heroic Shoulder Rest Stance
# =============================================================================
pose_root.location = (0, 0, 0)
pose_root.rotation_euler = (0, 0, 0)
pose_root.scale = (1, 1, 1)

pose_hilt.location = (0.22, 0.0, 0.75)
pose_hilt.rotation_euler = (math.radians(-60), math.radians(20), math.radians(-30))
pose_hilt.scale = (1, 1, 1)

pose_blade.location = (0, 0, 0)
pose_blade.rotation_euler = (0, 0, 0)
pose_blade.scale = (1, 1, 1)

pose_debris.location = (0, 0, -5.0)
pose_debris.rotation_euler = (0, 0, 0)
pose_debris.scale = (0.001, 0.001, 0.001)

kf_all(1)

# FRAME 8: Subtle breathing sway
pose_hilt.location = (0.22, 0.01, 0.77)
pose_hilt.rotation_euler = (math.radians(-58), math.radians(21), math.radians(-29))
kf_all(8)

# FRAME 15: Poised Shoulder Rest ready to draw
pose_hilt.location = (0.22, 0.0, 0.75)
pose_hilt.rotation_euler = (math.radians(-60), math.radians(20), math.radians(-30))
kf_all(15)

# FRAME 18: Anticipation stance dip to hoist mass
pose_hilt.location = (0.16, -0.08, 0.58)
pose_hilt.rotation_euler = (math.radians(-45), math.radians(12), math.radians(-15))
kf_all(18)

# FRAME 22: Upward surge of colossal mass
pose_hilt.location = (0.06, 0.05, 0.95)
pose_hilt.rotation_euler = (math.radians(20), math.radians(-5), math.radians(5))
pose_blade.rotation_euler = (math.radians(-3), 0, 0)
kf_all(22)

# FRAME 26: High overhead windup
pose_hilt.location = (0.00, 0.12, 1.35)
pose_hilt.rotation_euler = (math.radians(135), 0, 0)
pose_blade.rotation_euler = (math.radians(-5), 0, 0)
kf_all(26)

# FRAME 28: Peak coiled tension overhead before the strike
pose_hilt.location = (0.00, 0.15, 1.45)
pose_hilt.rotation_euler = (math.radians(155), 0, 0)
pose_blade.rotation_euler = (math.radians(-2), 0, 0)
kf_all(28)

# =============================================================================
# FRAME 29: CATACLYSMIC VERTICAL SLAM INTO GROUND!
# =============================================================================
# Crossguard at z = 1.102m, blade rotated 180 deg, tip enters plinth crater at z = -0.05m!
pose_hilt.location = (0.0, 0.0, 1.102)
pose_hilt.rotation_euler = (math.radians(180), 0, 0)

# Steel compression flex upon impact with granite
pose_blade.rotation_euler = (math.radians(4.0), 0, 0)

# Ground shockwave tremor
pose_root.location = (0.015, -0.02, -0.02)
pose_root.rotation_euler = (math.radians(1.5), math.radians(-1.0), math.radians(0.8))

# Flying rock debris & sparks burst right from the crater surface!
pose_debris.location = (0, 0, 0.04)
pose_debris.rotation_euler = (math.radians(20), math.radians(-15), math.radians(25))
pose_debris.scale = (1.35, 1.35, 1.35)

kf_all(29)

# FRAME 31: Recoil shudder
pose_hilt.location = (0.0, 0.0, 1.110)
pose_blade.rotation_euler = (math.radians(-2.8), 0, 0)
pose_root.location = (-0.01, 0.015, 0.01)
pose_root.rotation_euler = (math.radians(-1.0), math.radians(0.8), math.radians(-0.5))
pose_debris.location = (0, 0.03, 0.14)
pose_debris.rotation_euler = (math.radians(40), math.radians(-30), math.radians(50))
pose_debris.scale = (1.25, 1.25, 1.25)
kf_all(31)

# FRAME 34: Tremor dampening
pose_hilt.location = (0.0, 0.0, 1.102)
pose_blade.rotation_euler = (math.radians(1.2), 0, 0)
pose_root.location = (0.004, -0.005, -0.004)
pose_root.rotation_euler = (math.radians(0.3), math.radians(-0.2), math.radians(0.1))
pose_debris.location = (0, 0.06, 0.20)
pose_debris.rotation_euler = (math.radians(60), math.radians(-45), math.radians(80))
pose_debris.scale = (1.10, 1.10, 1.10)
kf_all(34)

# FRAME 40: Tremor settle, debris arc landing
pose_blade.rotation_euler = (0, 0, 0)
pose_root.location = (0, 0, 0)
pose_root.rotation_euler = (0, 0, 0)
pose_debris.location = (0, 0.08, 0.06)
pose_debris.rotation_euler = (math.radians(85), math.radians(-60), math.radians(110))
pose_debris.scale = (0.50, 0.50, 0.50)
kf_all(40)

# FRAME 43: Bracing down on hilt before pulling
pose_hilt.location = (0.0, 0.0, 1.08)
kf_all(43)

# FRAME 47: Wrenching sword upward out of stone fissure
pose_hilt.location = (0.02, -0.02, 1.28)
pose_hilt.rotation_euler = (math.radians(172), math.radians(4), math.radians(3))
pose_debris.location = (0, 0, -5.0)
pose_debris.scale = (0.001, 0.001, 0.001)
kf_all(47)

# FRAME 52: Tip clears stone and swings around
pose_hilt.location = (0.10, -0.05, 1.25)
pose_hilt.rotation_euler = (math.radians(110), math.radians(-10), math.radians(15))
kf_all(52)

# FRAME 56: Settling back across shoulder
pose_hilt.location = (0.18, -0.02, 0.88)
pose_hilt.rotation_euler = (math.radians(-30), math.radians(18), math.radians(-25))
kf_all(56)

# FRAME 60: Seamless loop back to Frame 1
pose_root.location = (0, 0, 0)
pose_root.rotation_euler = (0, 0, 0)
pose_root.scale = (1, 1, 1)

pose_hilt.location = (0.22, 0.0, 0.75)
pose_hilt.rotation_euler = (math.radians(-60), math.radians(20), math.radians(-30))
pose_hilt.scale = (1, 1, 1)

pose_blade.location = (0, 0, 0)
pose_blade.rotation_euler = (0, 0, 0)
pose_blade.scale = (1, 1, 1)

pose_debris.location = (0, 0, -5.0)
pose_debris.rotation_euler = (0, 0, 0)
pose_debris.scale = (0.001, 0.001, 0.001)

kf_all(60)

bpy.ops.object.mode_set(mode='OBJECT')

# 7. Display Plinth (2-Tier Fractured Battlefield Stone Altar)
print("Building 2-Tier Fractured Granite Display Plinth at ground level...")
plinth_voxels = {}

# Tier 1 (Lower Base): Z = -16 to -8, radius 25
for pz in range(-16, -8):
    for px in range(-25, 26):
        for py in range(-25, 26):
            d2 = px*px + py*py
            if d2 <= 580:
                if d2 >= 480 or pz == -16:
                    pm = 'plinth_rim'
                elif abs(px) == abs(py) or (px % 8 == 0 and py % 8 == 0):
                    pm = 'plinth_crack'
                else:
                    pm = 'plinth_stone'
                plinth_voxels[(px, py, pz)] = pm

# Tier 2 (Upper Crag): Z = -8 to 0, radius 20
for pz in range(-8, 1):
    for px in range(-20, 21):
        for py in range(-20, 21):
            d2 = px*px + py*py
            if d2 <= 380:
                # Fissure crater at (0, 0)
                crater_x = abs(px)
                crater_y = abs(py)
                
                # Impact crater indentation
                if crater_x <= 9 and crater_y <= 3 and pz >= -5:
                    continue
                elif crater_x <= 12 and crater_y <= 5 and pz >= -2:
                    pm = 'plinth_crack'
                elif abs(px) == abs(py) or (px % 7 == 0 and py % 7 == 0):
                    pm = 'plinth_crack'
                elif d2 >= 320 or pz == -8:
                    pm = 'plinth_rim'
                else:
                    pm = 'plinth_stone'
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
plinth_obj.location = (0, 0, 0.0)
bpy.context.collection.objects.link(plinth_obj)

# 8. Cycles AgX Beauty Lighting & Camera Framing
print("Configuring Cycles AgX High Contrast Beauty Render...")
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

# Atmospheric World with Rich Ambient Reflection Dome
world = bpy.data.worlds.new("Voxel_Berserk_World")
world.use_nodes = True
nodes = world.node_tree.nodes
nodes.clear()

w_out = nodes.new(type='ShaderNodeOutputWorld')
w_bg = nodes.new(type='ShaderNodeBackground')
w_bg.inputs['Color'].default_value = (0.04, 0.05, 0.07, 1.0)
w_bg.inputs['Strength'].default_value = 0.80
world.node_tree.links.new(w_bg.outputs['Background'], w_out.inputs['Surface'])
scene.world = world

scene.view_settings.view_transform = 'AgX' if hasattr(scene.view_settings, 'view_transform') else 'Filmic'
scene.view_settings.look = 'AgX - High Contrast'

# Heroic Framing Target: Center of the sword slab
target_emp = bpy.data.objects.new("Target_Aim", None)
target_emp.location = (0.0, 0.0, 0.58)
bpy.context.collection.objects.link(target_emp)

# Heroic Perspective Camera: slightly low angle for towering presence
cam_data = bpy.data.cameras.new("Sword_Camera")
cam_data.lens = 52
cam_obj = bpy.data.objects.new("Sword_Camera", object_data=cam_data)
cam_obj.location = (1.65, -2.15, 0.82)

track = cam_obj.constraints.new(type='TRACK_TO')
track.target = target_emp
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

# 5-Point Dramatic Studio Lighting
# 1) Key Sun Light (Warm crisp battle steel illumination)
key_l = bpy.data.objects.new("Key_Steel", bpy.data.lights.new("Key_Steel", type='SUN'))
key_l.data.energy = 5.8
key_l.data.color = (1.00, 0.96, 0.90)
key_l.data.angle = math.radians(6)
key_l.rotation_euler = (math.radians(45), math.radians(25), math.radians(-35))
bpy.context.collection.objects.link(key_l)

# 2) Top Rim Light (Silvery blue edge highlight catching blade bevels & hilt rivets)
rim_top = bpy.data.objects.new("Rim_Top", bpy.data.lights.new("Rim_Top", type='AREA'))
rim_top.data.energy = 650.0
rim_top.data.color = (0.85, 0.94, 1.00)
rim_top.data.size = 2.2
rim_top.location = (0.0, 0.2, 2.3)
rim_top.rotation_euler = (math.radians(-75), 0, 0)
bpy.context.collection.objects.link(rim_top)

# 3) Berserk Crimson Accent Light (Vivid apostle blood reflection)
rim_crimson = bpy.data.objects.new("Rim_Crimson", bpy.data.lights.new("Rim_Crimson", type='AREA'))
rim_crimson.data.energy = 480.0
rim_crimson.data.color = (1.00, 0.22, 0.04)
rim_crimson.data.size = 2.5
rim_crimson.location = (-1.8, 1.6, 0.7)
rim_crimson.rotation_euler = (math.radians(-40), math.radians(25), math.radians(135))
bpy.context.collection.objects.link(rim_crimson)

# 4) Cold Moonlight Fill Light (Reflecting metallic sheen on blade flat)
fill_moon = bpy.data.objects.new("Fill_Moonlight", bpy.data.lights.new("Fill_Moonlight", type='AREA'))
fill_moon.data.energy = 250.0
fill_moon.data.color = (0.45, 0.70, 1.00)
fill_moon.data.size = 3.2
fill_moon.location = (2.2, -1.5, 0.4)
fill_moon.rotation_euler = (math.radians(30), math.radians(-25), math.radians(-40))
bpy.context.collection.objects.link(fill_moon)

# 5) Crater Friction Glow (Upward warm point light from impact zone)
crater_glow = bpy.data.objects.new("Crater_Glow", bpy.data.lights.new("Crater_Glow", type='POINT'))
crater_glow.data.energy = 90.0
crater_glow.data.color = (1.00, 0.45, 0.06)
crater_glow.location = (0.0, 0.0, 0.12)
bpy.context.collection.objects.link(crater_glow)

# Output Paths
workspace_dir = os.path.abspath(os.path.dirname(__file__))
blend_file = os.path.join(workspace_dir, "guts_sword.blend")
glb_file = os.path.join(workspace_dir, "guts_sword.glb")
render_file = os.path.join(workspace_dir, "guts_sword_render.png")
render_f15 = os.path.join(workspace_dir, "guts_sword_shoulder.png")
js_file = os.path.join(workspace_dir, "guts_sword_data.js")

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

print(f"Rendering beauty frame 29 (Impact Slam) to {render_file}...")
scene.frame_set(29)
scene.render.filepath = render_file
bpy.ops.render.render(write_still=True)

print(f"Rendering frame 15 (Shoulder Rest) to {render_f15}...")
scene.frame_set(15)
scene.render.filepath = render_f15
bpy.ops.render.render(write_still=True)

# Generate Base64 Data URI in guts_sword_data.js
print(f"Generating base64 data to {js_file}...")
with open(glb_file, 'rb') as f:
    glb_b64 = base64.b64encode(f.read()).decode('utf-8')

js_content = f'window.GUTS_SWORD_FLASH_BASE64 = "data:model/gltf-binary;base64,{glb_b64}";\n'
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_content)

print("=================================================================")
print(">>> [SUCCESS] Guts Dragon Slayer Created, Rigged, Rendered & Exported!")
print("=================================================================")
