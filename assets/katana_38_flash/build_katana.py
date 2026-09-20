import bpy
import math
import os
import base64

print("=================================================================")
print(">>> [TROVE VOXEL KATANA ENGINE v4.0] Authentic Katana & Slash")
print("=================================================================")

# 1. Reset Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 60
scene.render.fps = 30

VOXEL_SIZE = 0.012  # 1.2 cm micro-voxel scale

# 2. Materials Definition
def make_shader(name, color, roughness=0.3, metallic=0.0, emission=0.0, emission_color=None):
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
            bsdf.inputs['Emission'].default_value = color
            
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

mats = {
    # Folded Tamahagane Steel & Blade
    'tamahagane_spine':       make_shader('M_TamahaganeSpine',      (0.36, 0.40, 0.48, 1.0), roughness=0.20, metallic=0.92),
    'tamahagane_dark':        make_shader('M_TamahaganeDark',       (0.20, 0.22, 0.26, 1.0), roughness=0.28, metallic=0.90),
    'tamahagane_light':       make_shader('M_TamahaganeLight',      (0.74, 0.80, 0.88, 1.0), roughness=0.12, metallic=0.96),
    'hamon_mist':             make_shader('M_HamonMist',            (0.85, 0.90, 0.98, 1.0), roughness=0.15, metallic=0.85),
    'hamon_crystalline':      make_shader('M_HamonCrystalline',     (0.98, 0.99, 1.00, 1.0), roughness=0.08, metallic=0.75, emission=0.8, emission_color=(0.92, 0.97, 1.0, 1.0)),
    'cutting_edge':           make_shader('M_CuttingEdge',          (0.96, 0.98, 1.00, 1.0), roughness=0.04, metallic=0.98),
    
    # Habaki & Seppa (Gilded Copper Collar & Spacers)
    'habaki_gold':            make_shader('M_HabakiGold',           (0.96, 0.78, 0.24, 1.0), roughness=0.16, metallic=0.94),
    'habaki_groove':          make_shader('M_HabakiGroove',         (0.68, 0.48, 0.14, 1.0), roughness=0.35, metallic=0.85),
    'seppa_copper':           make_shader('M_SeppaCopper',          (0.85, 0.48, 0.22, 1.0), roughness=0.25, metallic=0.90),
    
    # Tsuba (Guard: Blackened Iron & Gilded Gold Sukashi)
    'tsuba_iron':             make_shader('M_TsubaIron',            (0.10, 0.11, 0.13, 1.0), roughness=0.45, metallic=0.82),
    'tsuba_gold':             make_shader('M_TsubaGold',            (0.96, 0.78, 0.22, 1.0), roughness=0.18, metallic=0.95),
    
    # Tsuka (Grip: Samegawa, Tsuka-ito Silk Wrap, Menuki Dragons, Kashira Pommel)
    'fuchi_kashira':          make_shader('M_FuchiKashira',         (0.12, 0.13, 0.16, 1.0), roughness=0.35, metallic=0.85),
    'kashira_gold':           make_shader('M_KashiraGold',          (0.95, 0.76, 0.24, 1.0), roughness=0.18, metallic=0.92),
    'samegawa_white':         make_shader('M_SamegawaWhite',        (0.95, 0.93, 0.90, 1.0), roughness=0.80, metallic=0.02),
    'tsuka_ito_black':        make_shader('M_TsukaItoBlack',        (0.06, 0.06, 0.08, 1.0), roughness=0.82, metallic=0.10),
    'tsuka_ito_knot':         make_shader('M_TsukaItoKnot',         (0.16, 0.18, 0.24, 1.0), roughness=0.72, metallic=0.16),
    'menuki_gold':            make_shader('M_MenukiGold',           (0.98, 0.82, 0.24, 1.0), roughness=0.15, metallic=0.96),
    
    # Dynamic Attack Trail (AgX Safe Emission = 2.0 per Specification)
    'trail_core_white':       make_shader('M_TrailCoreWhite',       (0.95, 0.99, 1.00, 1.0), roughness=0.05, metallic=0.02, emission=2.0, emission_color=(0.95, 0.99, 1.00, 1.0)),
    'trail_luminescent_cyan': make_shader('M_TrailCyan',            (0.00, 0.72, 1.00, 1.0), roughness=0.08, metallic=0.05, emission=2.0, emission_color=(0.00, 0.78, 1.00, 1.0)),
    'trail_energy_edge':      make_shader('M_TrailEnergyEdge',      (0.00, 0.38, 0.92, 1.0), roughness=0.10, metallic=0.05, emission=2.0, emission_color=(0.00, 0.42, 0.96, 1.0)),
    'trail_spark':            make_shader('M_TrailSpark',           (0.10, 0.88, 1.00, 1.0), roughness=0.05, metallic=0.05, emission=2.2, emission_color=(0.15, 0.92, 1.00, 1.0)),
}

# 3. Model Generation (Micro-Voxel Data)
voxels = {}

def set_vox(x, y, z, mat, bone, overwrite=False):
    k = (int(x), int(y), int(z))
    if not overwrite and k in voxels:
        return
    voxels[k] = (mat, bone)

print("Building Kashira (Pommel Cap & Shitodome Eyelets)...")
for z in range(-26, -24):
    for x in range(-2, 3):
        for y in range(-3, 4):
            if (x*x)/4.0 + (y*y)/9.0 <= 1.0:
                if z == -26:
                    if x == 0 and abs(y) == 1:
                        m = 'kashira_gold'
                    elif abs(x) == 1 and y == 0:
                        m = 'kashira_gold'
                    else:
                        m = 'fuchi_kashira'
                else:
                    if abs(x) == 2 or abs(y) == 3:
                        m = 'kashira_gold'
                    else:
                        m = 'fuchi_kashira'
                set_vox(x, y, z, m, 'Hilt', True)

print("Building Tsuka (Grip: Samegawa Ray Skin, Tsuka-ito Silk Wrap, Golden Menuki)...")
for z in range(-24, -1):
    cycle = (z + 24) % 6
    is_menuki_z = (z in (-17, -16, -15) or z in (-9, -8, -7))
    
    for x in range(-1, 2):
        for y in range(-2, 3):
            if abs(x) == 1 and abs(y) == 2:
                continue
            
            is_center = (x == 0 and abs(y) <= 1)
            if is_center:
                set_vox(x, y, z, 'tsuka_ito_black', 'Hilt', True)
                continue
            
            if abs(x) == 1 and abs(y) <= 1:
                if cycle in (2, 3):
                    if is_menuki_z and ((x == 1 and z in (-16, -15)) or (x == -1 and z in (-9, -8))):
                        m = 'menuki_gold'
                    else:
                        m = 'samegawa_white'
                elif cycle in (1, 4):
                    m = 'tsuka_ito_knot'
                else:
                    m = 'tsuka_ito_black'
            else:
                if cycle in (0, 3):
                    m = 'tsuka_ito_knot'
                elif (z + y) % 2 == 0:
                    m = 'tsuka_ito_black'
                else:
                    m = 'tsuka_ito_knot'
            
            set_vox(x, y, z, m, 'Hilt', True)

print("Building Fuchi (Hilt Metal Collar & Gold Rim)...")
for z in range(-1, 1):
    for x in range(-2, 3):
        for y in range(-3, 4):
            if (x*x)/4.5 + (y*y)/9.5 <= 1.0:
                if z == 0:
                    m = 'tsuba_gold'
                else:
                    m = 'fuchi_kashira'
                set_vox(x, y, z, m, 'Hilt', True)

print("Building Tsuba (Octagonal/Circular Openwork Sukashi Guard)...")
for z in range(1, 3):
    for x in range(-7, 8):
        for y in range(-7, 8):
            d2 = x*x + y*y
            if d2 > 42:
                continue
            if abs(x) <= 1 and abs(y) <= 2:
                continue
            if (x in (-5, -4, -3)) and abs(y) <= 1:
                continue
            if (x in (3, 4, 5)) and abs(y) <= 1:
                continue
            if (abs(x) == 3 and abs(y) == 3) or (abs(x) == 2 and abs(y) == 4):
                continue
            
            if d2 >= 32:
                m = 'tsuba_gold'
            elif d2 in (10, 11, 12):
                m = 'tsuba_gold'
            else:
                m = 'tsuba_iron'
                
            set_vox(x, y, z, m, 'Hilt', True)

print("Building Seppa & Habaki (Copper Spacers & Gilded Copper Collar)...")
for x in range(-2, 3):
    for y in range(-3, 4):
        if (x*x)/4.0 + (y*y)/8.0 <= 1.0:
            if not (abs(x) <= 1 and abs(y) <= 1):
                set_vox(x, y, 3, 'seppa_copper', 'Hilt', True)

for z in range(4, 7):
    for x in range(-1, 2):
        for y in range(-2, 4):
            if x == 0 and y in (-1, 0, 1):
                continue
            if (z + y) % 2 == 0:
                m = 'habaki_groove'
            else:
                m = 'habaki_gold'
            set_vox(x, y, z, m, 'Hilt', True)

print("Building Blade (Nagasa) with Sori Curvature, Hamon Wave, and Chiseled Kissaki...")
def get_sori_y(z_val):
    if z_val < 6:
        return 0
    u = (z_val - 6.0) / (70.0 - 6.0)
    return -int(round(4.2 * (u ** 1.32)))

for z in range(4, 71):
    sy = get_sori_y(z)
    
    if z < 65:
        set_vox(0, sy - 2, z, 'tamahagane_spine', 'Blade_Bone', True)
        set_vox(-1, sy - 1, z, 'tamahagane_light', 'Blade_Bone', True)
        set_vox( 0, sy - 1, z, 'tamahagane_dark',  'Blade_Bone', True)
        set_vox( 1, sy - 1, z, 'tamahagane_light', 'Blade_Bone', True)
        
        hw = math.sin(z * 0.46) * 0.72 + math.cos(z * 0.98) * 0.38
        
        if hw > 0.15:
            set_vox(-1, sy, z, 'hamon_crystalline', 'Blade_Bone', True)
            set_vox( 0, sy, z, 'hamon_mist',        'Blade_Bone', True)
            set_vox( 1, sy, z, 'hamon_crystalline', 'Blade_Bone', True)
        else:
            set_vox(-1, sy, z, 'hamon_mist',        'Blade_Bone', True)
            set_vox( 0, sy, z, 'tamahagane_dark',   'Blade_Bone', True)
            set_vox( 1, sy, z, 'hamon_mist',        'Blade_Bone', True)
            
        if hw > -0.25:
            set_vox(-1, sy + 1, z, 'hamon_crystalline', 'Blade_Bone', True)
            set_vox( 0, sy + 1, z, 'hamon_crystalline', 'Blade_Bone', True)
            set_vox( 1, sy + 1, z, 'hamon_crystalline', 'Blade_Bone', True)
        else:
            set_vox(-1, sy + 1, z, 'hamon_mist',        'Blade_Bone', True)
            set_vox( 0, sy + 1, z, 'tamahagane_light',  'Blade_Bone', True)
            set_vox( 1, sy + 1, z, 'hamon_mist',        'Blade_Bone', True)
            
        set_vox(0, sy + 2, z, 'cutting_edge', 'Blade_Bone', True)
        
    else:
        if z == 65:
            set_vox( 0, sy - 2, z, 'tamahagane_spine',   'Blade_Bone', True)
            set_vox(-1, sy - 1, z, 'tamahagane_light',   'Blade_Bone', True)
            set_vox( 0, sy - 1, z, 'tamahagane_dark',    'Blade_Bone', True)
            set_vox( 1, sy - 1, z, 'tamahagane_light',   'Blade_Bone', True)
            set_vox(-1, sy,     z, 'hamon_crystalline',  'Blade_Bone', True)
            set_vox( 0, sy,     z, 'hamon_crystalline',  'Blade_Bone', True)
            set_vox( 1, sy,     z, 'hamon_crystalline',  'Blade_Bone', True)
            set_vox( 0, sy + 1, z, 'cutting_edge',       'Blade_Bone', True)
            set_vox( 0, sy + 2, z, 'cutting_edge',       'Blade_Bone', True)
        elif z == 66:
            set_vox( 0, sy - 1, z, 'tamahagane_spine',   'Blade_Bone', True)
            set_vox(-1, sy,     z, 'hamon_crystalline',  'Blade_Bone', True)
            set_vox( 0, sy,     z, 'tamahagane_light',   'Blade_Bone', True)
            set_vox( 1, sy,     z, 'hamon_crystalline',  'Blade_Bone', True)
            set_vox( 0, sy + 1, z, 'cutting_edge',       'Blade_Bone', True)
            set_vox( 0, sy + 2, z, 'cutting_edge',       'Blade_Bone', True)
        elif z == 67:
            set_vox( 0, sy - 1, z, 'tamahagane_spine',   'Blade_Bone', True)
            set_vox(-1, sy,     z, 'hamon_crystalline',  'Blade_Bone', True)
            set_vox( 0, sy,     z, 'hamon_crystalline',  'Blade_Bone', True)
            set_vox( 1, sy,     z, 'hamon_crystalline',  'Blade_Bone', True)
            set_vox( 0, sy + 1, z, 'cutting_edge',       'Blade_Bone', True)
        elif z == 68:
            set_vox( 0, sy,     z, 'tamahagane_light',   'Blade_Bone', True)
            set_vox(-1, sy + 1, z, 'hamon_crystalline',  'Blade_Bone', True)
            set_vox( 0, sy + 1, z, 'cutting_edge',       'Blade_Bone', True)
            set_vox( 1, sy + 1, z, 'hamon_crystalline',  'Blade_Bone', True)
        elif z == 69:
            set_vox( 0, sy,     z, 'hamon_crystalline',  'Blade_Bone', True)
            set_vox( 0, sy + 1, z, 'cutting_edge',       'Blade_Bone', True)
        elif z == 70:
            set_vox( 0, sy,     z, 'cutting_edge',       'Blade_Bone', True)

print("Building Dynamic Attack Trail (Crescent Slash Ribbon & Energy Motes)...")
trail_z_min = 20
trail_z_max = 76

for z in range(trail_z_min, trail_z_max + 1):
    sy = get_sori_y(min(z, 70))
    edge_y = sy + 2 if z < 68 else (sy + 1 if z < 70 else sy)
    u = (z - trail_z_min) / float(trail_z_max - trail_z_min)
    
    crescent_depth = int(round(14.0 * math.sin(u * math.pi)))
    if crescent_depth < 1:
        crescent_depth = 1
        
    for dy in range(1, crescent_depth + 1):
        vy = edge_y + dy
        
        # Subtle aerodynamic crescent sweep lag behind the cut arc
        vz = z - int(round(0.20 * (dy - 1)))
        
        if dy == 1:
            # Celestial White Hot Core directly hugging cutting edge
            set_vox( 0, vy, vz, 'trail_core_white',       'Trail_Bone', True)
            set_vox(-1, vy, vz, 'trail_luminescent_cyan', 'Trail_Bone', True)
            set_vox( 1, vy, vz, 'trail_luminescent_cyan', 'Trail_Bone', True)
        elif dy <= 6:
            # Rich Radiant Cyan Energy Ribbon
            set_vox( 0, vy, vz, 'trail_luminescent_cyan', 'Trail_Bone', True)
            set_vox(-1, vy, vz, 'trail_luminescent_cyan', 'Trail_Bone', True)
            set_vox( 1, vy, vz, 'trail_luminescent_cyan', 'Trail_Bone', True)
        elif dy <= crescent_depth - 2:
            # Deep Celestial Blue Outer Flare
            set_vox( 0, vy, vz, 'trail_energy_edge',      'Trail_Bone', True)
            set_vox(-1, vy, vz, 'trail_energy_edge',      'Trail_Bone', True)
            set_vox( 1, vy, vz, 'trail_energy_edge',      'Trail_Bone', True)
        else:
            # Crescent Feathered Tips
            set_vox( 0, vy, vz, 'trail_energy_edge',      'Trail_Bone', True)

spark_offsets = [
    ( 0, 16, 52), ( 1, 15, 56), (-1, 14, 48), ( 0, 17, 58),
    ( 2, 12, 44), (-2, 13, 62), ( 0, 15, 64), ( 1, 11, 38),
    (-1, 10, 66), ( 0,  9, 72), ( 1,  8, 75), ( 0, 10, 32),
    ( 2, 14, 54), (-2, 15, 50), ( 0, 18, 55), ( 1, 16, 60),
    (-1, 16, 42), ( 0, 13, 36), ( 1, 12, 68), ( 0, 11, 70),
    ( 2,  9, 28), (-2,  8, 26), ( 0, 12, 24), ( 1, 10, 73)
]
for sx, sy_off, sz in spark_offsets:
    base_sy = get_sori_y(min(sz, 70)) + 2
    set_vox(sx, base_sy + sy_off, sz, 'trail_spark', 'Trail_Bone', True)

print(f">>> Total Katana & Trail Voxels: {len(voxels)}")

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
        if neighbor not in voxels or voxels[neighbor][1] != bone_name:
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

print(f"Constructing Katana Mesh: {len(verts)} vertices, {len(faces)} faces...")
mesh = bpy.data.meshes.new("Katana_Mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

for m in used_mat_names:
    mesh.materials.append(mats[m])
for poly, slot in zip(mesh.polygons, face_mats):
    poly.material_index = slot

mesh.polygons.foreach_set('use_smooth', [False] * len(mesh.polygons))
mesh.update()

katana_obj = bpy.data.objects.new("Katana", mesh)
bpy.context.collection.objects.link(katana_obj)

# 5. Build Armature & Rigging
print("Building Armature with Root, Hilt, Blade_Bone, Trail_Bone...")
arm_data = bpy.data.armatures.new("Katana_Armature_Data")
arm_obj = bpy.data.objects.new("Katana_Armature", arm_data)
bpy.context.collection.objects.link(arm_obj)

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones

bone_root = eb.new("Root")
bone_root.head = (0, 0, 0)
bone_root.tail = (0, 0.10, 0)

bone_hilt = eb.new("Hilt")
bone_hilt.parent = bone_root
bone_hilt.head = (0, 0, 0.012)
bone_hilt.tail = (0, 0.10, 0.012)

bone_blade = eb.new("Blade_Bone")
bone_blade.parent = bone_hilt
bone_blade.head = (0, 0, 0.048)
bone_blade.tail = (0, 0.10, 0.048)

bone_trail = eb.new("Trail_Bone")
bone_trail.parent = bone_blade
bone_trail.head = (0, 0.03, 0.55)
bone_trail.tail = (0, 0.13, 0.55)

bpy.ops.object.mode_set(mode='OBJECT')

BONE_NAMES = ["Root", "Hilt", "Blade_Bone", "Trail_Bone"]
vgroups = {b: katana_obj.vertex_groups.new(name=b) for b in BONE_NAMES}

bone_verts = {b: [] for b in BONE_NAMES}
for vidx, bname in vert_groups.items():
    bone_verts[bname].append(vidx)

for bname, vindices in bone_verts.items():
    if vindices:
        vgroups[bname].add(vindices, 1.0, 'REPLACE')

arm_mod = katana_obj.modifiers.new(name="Armature", type='ARMATURE')
arm_mod.object = arm_obj
arm_mod.use_vertex_groups = True
katana_obj.parent = arm_obj

# 6. Keyframe Animation (Iaido Crescent Slash: 60 frames @ 30fps)
print("Keyframing Iaido Crescent Slash Animation (60 frames @ 30fps)...")
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')

pose_root  = arm_obj.pose.bones["Root"]
pose_hilt  = arm_obj.pose.bones["Hilt"]
pose_blade = arm_obj.pose.bones["Blade_Bone"]
pose_trail = arm_obj.pose.bones["Trail_Bone"]

all_bones = [pose_root, pose_hilt, pose_blade, pose_trail]

# MANDATORY: For all pose bones, set pb.rotation_mode = 'XYZ' before setting pb.rotation_euler
for pb in all_bones:
    pb.rotation_mode = 'XYZ'

def kf_all(frame):
    for pb in all_bones:
        pb.keyframe_insert(data_path="location", frame=frame)
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)
        pb.keyframe_insert(data_path="scale", frame=frame)

# F1: Ready Stance
pose_root.location = (0, 0, 0)
pose_root.rotation_euler = (0, 0, 0)
pose_root.scale = (1, 1, 1)

pose_hilt.location = (-0.18, -0.05, 0.38)
pose_hilt.rotation_euler = (math.radians(12), math.radians(-20), math.radians(-42))
pose_hilt.scale = (1, 1, 1)

pose_blade.location = (0, 0, 0)
pose_blade.rotation_euler = (0, 0, 0)
pose_blade.scale = (1, 1, 1)

pose_trail.location = (0, 0, 0)
pose_trail.rotation_euler = (0, 0, 0)
pose_trail.scale = (0, 0, 0)
kf_all(1)

# F8: Breathing Inhale
pose_hilt.location = (-0.17, -0.04, 0.39)
pose_hilt.rotation_euler = (math.radians(14), math.radians(-18), math.radians(-40))
pose_trail.scale = (0, 0, 0)
kf_all(8)

# F14: Anticipation Draw
pose_hilt.location = (-0.24, -0.12, 0.34)
pose_hilt.rotation_euler = (math.radians(22), math.radians(-32), math.radians(-55))
pose_blade.rotation_euler = (math.radians(-2), math.radians(0), math.radians(-3))
pose_trail.scale = (0, 0, 0)
kf_all(14)

# F15: Maximum Coiled Tension
pose_hilt.location = (-0.26, -0.14, 0.33)
pose_hilt.rotation_euler = (math.radians(25), math.radians(-35), math.radians(-58))
pose_blade.rotation_euler = (math.radians(-3), math.radians(0), math.radians(-4))
pose_trail.scale = (0, 0, 0)
kf_all(15)

# F16: Explosive Ignition
pose_hilt.location = (-0.14, 0.06, 0.36)
pose_hilt.rotation_euler = (math.radians(10), math.radians(-8), math.radians(-28))
pose_blade.rotation_euler = (math.radians(1), math.radians(0), math.radians(2))
pose_trail.scale = (0.35, 0.35, 0.35)
kf_all(16)

# F18: Supersonic Arc Across Centerline
pose_hilt.location = (0.04, 0.22, 0.44)
pose_hilt.rotation_euler = (math.radians(-6), math.radians(26), math.radians(18))
pose_blade.rotation_euler = (math.radians(3), math.radians(0), math.radians(5))
pose_trail.scale = (0.80, 0.88, 0.80)
kf_all(18)

# F21: High-Power Forward Cut
pose_hilt.location = (0.18, 0.26, 0.49)
pose_hilt.rotation_euler = (math.radians(-12), math.radians(52), math.radians(52))
pose_blade.rotation_euler = (math.radians(1), math.radians(0), math.radians(2))
pose_trail.scale = (0.95, 1.02, 0.95)
kf_all(21)

# F24: PEAK SLASH CLIMAX (BEAUTY RENDER FRAME)
pose_hilt.location = (0.28, 0.16, 0.50)
pose_hilt.rotation_euler = (math.radians(-15), math.radians(72), math.radians(75))
pose_blade.rotation_euler = (0, 0, 0)
pose_trail.scale = (1.0, 1.0, 1.0)
kf_all(24)

# F26: Follow-Through
pose_hilt.location = (0.33, 0.08, 0.49)
pose_hilt.rotation_euler = (math.radians(-16), math.radians(78), math.radians(82))
pose_trail.scale = (0.65, 0.70, 0.65)
kf_all(26)

# F29: Trail Dissipating
pose_hilt.location = (0.36, 0.04, 0.48)
pose_hilt.rotation_euler = (math.radians(-16), math.radians(80), math.radians(85))
pose_trail.scale = (0.20, 0.20, 0.20)
kf_all(29)

# F32: Trail Extinguished
pose_hilt.location = (0.36, 0.02, 0.47)
pose_hilt.rotation_euler = (math.radians(-15), math.radians(80), math.radians(85))
pose_trail.scale = (0, 0, 0)
kf_all(32)

# F36: Zanshin Stillness
pose_hilt.location = (0.35, 0.0, 0.46)
pose_hilt.rotation_euler = (math.radians(-14), math.radians(78), math.radians(83))
pose_trail.scale = (0, 0, 0)
kf_all(36)

# F37: Chiburui Initiation
pose_hilt.location = (0.33, -0.02, 0.45)
pose_hilt.rotation_euler = (math.radians(-10), math.radians(65), math.radians(70))
pose_trail.scale = (0, 0, 0)
kf_all(37)

# F40: Wind-up
pose_hilt.location = (0.30, -0.05, 0.48)
pose_hilt.rotation_euler = (math.radians(-5), math.radians(45), math.radians(40))
pose_trail.scale = (0, 0, 0)
kf_all(40)

# F43: CHIBURUI SNAP DOWN
pose_hilt.location = (0.24, -0.08, 0.36)
pose_hilt.rotation_euler = (math.radians(-42), math.radians(15), math.radians(-15))
pose_blade.rotation_euler = (math.radians(-5), math.radians(0), math.radians(0))
pose_trail.scale = (0, 0, 0)
kf_all(43)

# F45: Rebound Vibration
pose_hilt.location = (0.22, -0.07, 0.38)
pose_hilt.rotation_euler = (math.radians(-35), math.radians(18), math.radians(-12))
pose_blade.rotation_euler = (math.radians(2), math.radians(0), math.radians(0))
pose_trail.scale = (0, 0, 0)
kf_all(45)

# F48: Settled Flick
pose_hilt.location = (0.20, -0.06, 0.37)
pose_hilt.rotation_euler = (math.radians(-32), math.radians(15), math.radians(-15))
pose_blade.rotation_euler = (0, 0, 0)
pose_trail.scale = (0, 0, 0)
kf_all(48)

# F52: Returning Arc
pose_hilt.location = (0.05, -0.05, 0.36)
pose_hilt.rotation_euler = (math.radians(-15), math.radians(0), math.radians(-25))
pose_trail.scale = (0, 0, 0)
kf_all(52)

# F56: Aligning Back to Hip
pose_hilt.location = (-0.10, -0.05, 0.37)
pose_hilt.rotation_euler = (math.radians(2), math.radians(-12), math.radians(-35))
pose_trail.scale = (0, 0, 0)
kf_all(56)

# F60: Exact Loop to F1
pose_hilt.location = (-0.18, -0.05, 0.38)
pose_hilt.rotation_euler = (math.radians(12), math.radians(-20), math.radians(-42))
pose_blade.rotation_euler = (0, 0, 0)
pose_trail.scale = (0, 0, 0)
kf_all(60)

if arm_obj.animation_data and arm_obj.animation_data.action:
    for fcurve in arm_obj.animation_data.action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'

bpy.ops.object.mode_set(mode='OBJECT')

# 7. Cycles AgX Beauty Lighting & Cinematic Camera Framing
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

# Atmospheric World
world = bpy.data.worlds.new("Katana_Dojo_World")
world.use_nodes = True
nodes = world.node_tree.nodes
nodes.clear()

w_out = nodes.new(type='ShaderNodeOutputWorld')
w_bg = nodes.new(type='ShaderNodeBackground')
w_bg.inputs['Color'].default_value = (0.018, 0.024, 0.035, 1.0)
w_bg.inputs['Strength'].default_value = 0.40
world.node_tree.links.new(w_bg.outputs['Background'], w_out.inputs['Surface'])
scene.world = world

# AgX Tone Mapping with High Contrast
scene.view_settings.view_transform = 'AgX' if hasattr(scene.view_settings, 'view_transform') else 'Filmic'
scene.view_settings.look = 'AgX - High Contrast'

# Heroic Framing Target: Center of Katana + Crescent Trail at F24
target_emp = bpy.data.objects.new("Target_Aim", None)
target_emp.location = (0.24, 0.44, 0.58)
bpy.context.collection.objects.link(target_emp)

# Perspective Camera: 36mm lens framed perfectly for diagonal Katana slash
cam_data = bpy.data.cameras.new("Katana_Camera")
cam_data.lens = 36
cam_obj = bpy.data.objects.new("Katana_Camera", object_data=cam_data)
cam_obj.location = (1.30, -0.06, 1.00)

track = cam_obj.constraints.new(type='TRACK_TO')
track.target = target_emp
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

# 4-Point Dramatic Studio Lighting Setup
# 1) Key Sun Light: Crisp steel illumination
key_l = bpy.data.objects.new("Key_Steel", bpy.data.lights.new("Key_Steel", type='SUN'))
key_l.data.energy = 4.8
key_l.data.color = (1.00, 0.98, 0.94)
key_l.data.angle = math.radians(4)
key_l.rotation_euler = (math.radians(45), math.radians(20), math.radians(-30))
bpy.context.collection.objects.link(key_l)

# 2) Celestial Cyan Rim Light: Backlight for electric edge definition
rim_cyan = bpy.data.objects.new("Rim_Cyan", bpy.data.lights.new("Rim_Cyan", type='AREA'))
rim_cyan.data.energy = 220.0
rim_cyan.data.color = (0.00, 0.75, 1.00)
rim_cyan.data.size = 2.4
rim_cyan.location = (-0.8, 1.4, 0.9)
rim_cyan.rotation_euler = (math.radians(-35), math.radians(45), math.radians(110))
bpy.context.collection.objects.link(rim_cyan)

# 3) Warm Golden Accent Light: Accents tsuba, gold menuki dragon, and samegawa ray skin
fill_gold = bpy.data.objects.new("Fill_Gold", bpy.data.lights.new("Fill_Gold", type='AREA'))
fill_gold.data.energy = 320.0
fill_gold.data.color = (1.00, 0.82, 0.45)
fill_gold.data.size = 2.5
fill_gold.location = (0.8, -0.8, 0.2)
fill_gold.rotation_euler = (math.radians(35), math.radians(-15), math.radians(-30))
bpy.context.collection.objects.link(fill_gold)

# 4) Blade Specular Fill Light: Specifically brings out crystalline Hamon and steel reflection
blade_fill = bpy.data.objects.new("Blade_Fill", bpy.data.lights.new("Blade_Fill", type='AREA'))
blade_fill.data.energy = 160.0
blade_fill.data.color = (0.85, 0.95, 1.00)
blade_fill.data.size = 2.0
blade_fill.location = (0.9, 0.6, 1.1)
blade_fill.rotation_euler = (math.radians(40), math.radians(-25), math.radians(-20))
bpy.context.collection.objects.link(blade_fill)

# Output Paths
output_dir = os.path.dirname(os.path.abspath(__file__))
blend_file = os.path.join(output_dir, "katana.blend")
glb_file = os.path.join(output_dir, "katana.glb")
render_file = os.path.join(output_dir, "katana_render.png")
js_file = os.path.join(output_dir, "katana_data.js")

print(f"Saving .blend: {blend_file}")
bpy.ops.wm.save_as_mainfile(filepath=blend_file)

print(f"Exporting GLB: {glb_file}")
bpy.ops.object.select_all(action='DESELECT')
katana_obj.select_set(True)
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj

bpy.ops.export_scene.gltf(
    filepath=glb_file,
    export_format='GLB',
    use_selection=True,
    export_materials='EXPORT',
    export_yup=True,
    export_animations=True,
    export_frame_range=True,
    export_frame_step=1,
    export_anim_single_armature=True
)

print(f"Rendering Frame 24 (Peak Slash with Crescent Trail) to {render_file}...")
scene.frame_set(24)
scene.render.filepath = render_file
bpy.ops.render.render(write_still=True)

# Generate Base64 Data URI in katana_data.js
print(f"Generating base64 data to {js_file}...")
with open(glb_file, 'rb') as f:
    glb_b64 = base64.b64encode(f.read()).decode('utf-8')

js_content = f'window.KATANA_38_BASE64 = "data:model/gltf-binary;base64,{glb_b64}";\n'
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_content)

print("=================================================================")
print(">>> [SUCCESS] Trove Katana Created, Rigged, Rendered & Exported!")
print("=================================================================")
