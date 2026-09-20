import bpy
import math
import os
import base64

print("=================================================================")
print(">>> [KATANA CRESCENT FLASH ENGINE v4.0] Authentic Trove Micro-Voxel")
print("=================================================================")

# 1. Reset Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 60
scene.render.fps = 30

VOXEL_SIZE = 0.012  # 1.2 cm micro-voxel scale per specification

# 2. Materials Definition (Principled BSDF, AgX tone-mapping safe)
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
    # Authentic Folded Tamahagane Steel & High-Contrast Hamon
    'tamahagane_spine': make_shader('M_TamahaganeSpine', (0.12, 0.14, 0.18, 1.0), roughness=0.45, metallic=0.40),
    'tamahagane_flat':  make_shader('M_TamahaganeFlat',  (0.28, 0.32, 0.40, 1.0), roughness=0.35, metallic=0.50),
    'hamon_valley':     make_shader('M_HamonValley',     (0.62, 0.70, 0.78, 1.0), roughness=0.30, metallic=0.40),
    'hamon_crest':      make_shader('M_HamonCrest',      (0.90, 0.95, 0.99, 1.0), roughness=0.18, metallic=0.45),
    'cutting_edge':     make_shader('M_CuttingEdge',     (0.98, 1.00, 1.00, 1.0), roughness=0.10, metallic=0.70),
    
    # Fittings (Habaki collar, Seppa washers, Tsuba guard, Fuchi collar, Kashira pommel)
    'habaki_copper':    make_shader('M_HabakiCopper',    (0.85, 0.52, 0.20, 1.0), roughness=0.25, metallic=0.85),
    'habaki_gold':      make_shader('M_HabakiGold',      (1.00, 0.82, 0.18, 1.0), roughness=0.18, metallic=0.92),
    'seppa_brass':      make_shader('M_SeppaBrass',      (0.90, 0.74, 0.24, 1.0), roughness=0.22, metallic=0.88),
    'tsuba_iron':       make_shader('M_TsubaIron',       (0.07, 0.08, 0.10, 1.0), roughness=0.50, metallic=0.70),
    'tsuba_gold':       make_shader('M_TsubaGold',       (1.00, 0.82, 0.15, 1.0), roughness=0.15, metallic=0.95),
    'fuchi_kashira':    make_shader('M_FuchiKashira',    (0.09, 0.10, 0.12, 1.0), roughness=0.45, metallic=0.75),
    
    # Tsuka Hilt (Samegawa white ray skin, Silk cord tsuka-ito, Gold dragon menuki)
    'samegawa_white':   make_shader('M_SamegawaWhite',   (0.95, 0.93, 0.88, 1.0), roughness=0.85, metallic=0.02),
    'samegawa_grain':   make_shader('M_SamegawaGrain',   (0.78, 0.75, 0.70, 1.0), roughness=0.88, metallic=0.02),
    'tsuka_ito_indigo': make_shader('M_TsukaItoIndigo', (0.04, 0.08, 0.18, 1.0), roughness=0.70, metallic=0.05),
    'tsuka_ito_hi':     make_shader('M_TsukaItoHi',     (0.18, 0.28, 0.55, 1.0), roughness=0.50, metallic=0.10),
    'menuki_gold':      make_shader('M_MenukiGold',      (1.00, 0.80, 0.12, 1.0), roughness=0.15, metallic=0.95),
    
    # Dynamic Attack Slash Ribbon (Luminescent Cyan & Celestial White, AgX safe emission: 0.5 - 1.8)
    'trail_core':        make_shader('M_TrailCore',        (1.00, 1.00, 1.00, 1.0), roughness=0.05, emission=1.8, emission_color=(1.0, 1.0, 1.0, 1.0)),
    'trail_cyan_bright': make_shader('M_TrailCyanBright',  (0.00, 0.88, 1.00, 1.0), roughness=0.08, emission=1.5, emission_color=(0.00, 0.88, 1.00, 1.0)),
    'trail_cyan_deep':   make_shader('M_TrailCyanDeep',    (0.00, 0.50, 1.00, 1.0), roughness=0.12, emission=1.2, emission_color=(0.00, 0.50, 1.00, 1.0)),
    'trail_cyan_plasma': make_shader('M_TrailCyanPlasma',  (0.02, 0.20, 0.85, 1.0), roughness=0.18, emission=0.9, emission_color=(0.02, 0.20, 0.85, 1.0)),
    'trail_cyan_dark':   make_shader('M_TrailCyanDark',    (0.01, 0.08, 0.55, 1.0), roughness=0.22, emission=0.6, emission_color=(0.01, 0.08, 0.55, 1.0)),
}

# 3. Model Generation
voxels = {}

def set_vox(x, y, z, mat, bone, overwrite=False):
    k = (int(x), int(y), int(z))
    if not overwrite and k in voxels:
        return
    voxels[k] = (mat, bone)

print("Building Kashira (Pommel Cap)...")
# Z = -24 to -23
for z in range(-24, -22):
    for x in range(-2, 3):
        for y in range(-2, 3):
            if abs(x) == 2 and abs(y) == 2:
                continue
            is_rim = (abs(x) == 2 or abs(y) == 2)
            if z == -24:
                if x == 0 and y == 0:
                    set_vox(x, y, z, 'tsuba_gold', 'Hilt', True)
                elif is_rim:
                    set_vox(x, y, z, 'tsuba_gold', 'Hilt', True)
                else:
                    set_vox(x, y, z, 'fuchi_kashira', 'Hilt', True)
            else:
                if is_rim:
                    set_vox(x, y, z, 'tsuba_gold', 'Hilt', True)
                else:
                    set_vox(x, y, z, 'fuchi_kashira', 'Hilt', True)

print("Building Tsuka (Hilt with authentic diamond silk wrap & gold menuki)...")
# Tsuka: Z = -22 to -3 (20 voxels tall = 24 cm)
# Ergonomic oval core: x in [-1, 1], y in [-2, 2], rounded corners
for z in range(-22, -2):
    phase = (z + 24) % 4
    for x in range(-1, 2):
        for y in range(-2, 3):
            if abs(x) == 1 and abs(y) == 2:
                continue
            
            # Core inner voxels
            if x == 0 and abs(y) <= 1:
                set_vox(x, y, z, 'samegawa_white', 'Hilt', True)
                continue
            
            # Front and Back (Y = -2 or Y = 2)
            if abs(y) == 2:
                m = 'tsuka_ito_hi' if phase in (0, 2) else 'tsuka_ito_indigo'
                set_vox(x, y, z, m, 'Hilt', True)
                continue
            
            # Sides (X = -1 or X = 1)
            if y == 0 and phase == 0:
                set_vox(x, y, z, 'samegawa_white', 'Hilt', True)
            elif y == 0 and phase == 2:
                set_vox(x, y, z, 'tsuka_ito_hi', 'Hilt', True)
            elif phase in (1, 3) and y == 0:
                set_vox(x, y, z, 'samegawa_grain', 'Hilt', True)
            else:
                set_vox(x, y, z, 'tsuka_ito_indigo', 'Hilt', True)

# Sculpt Golden Dragon Menuki nestled in the diamond windows!
for mz in (-14, -13):
    set_vox(1, 0, mz, 'menuki_gold', 'Hilt', True)
    set_vox(1, 1, mz, 'menuki_gold', 'Hilt', True)
for mz in (-8, -7):
    set_vox(-1, 0, mz, 'menuki_gold', 'Hilt', True)
    set_vox(-1, -1, mz, 'menuki_gold', 'Hilt', True)

print("Building Fuchi (Hilt Collar)...")
# Z = -2 to -1
for z in range(-2, 0):
    for x in range(-2, 3):
        for y in range(-3, 4):
            if abs(x) == 2 and abs(y) == 3:
                continue
            is_outer = (abs(x) == 2 or abs(y) == 3)
            if is_outer:
                if z == -1 and (x == 0 or abs(y) == 1):
                    set_vox(x, y, z, 'tsuba_gold', 'Hilt', True)
                else:
                    set_vox(x, y, z, 'fuchi_kashira', 'Hilt', True)
            else:
                set_vox(x, y, z, 'fuchi_kashira', 'Hilt', True)

print("Building Seppa & Tsuba (Openwork Sukashi Guard)...")
# Radius 6 voxels (diameter 13 voxels = 15.6 cm)
for z in (0, 1):
    for x in range(-6, 7):
        for y in range(-6, 7):
            d = math.sqrt(x*x + y*y)
            if d > 6.2:
                continue
            
            # Center Nakago pass-through
            if abs(x) <= 1 and abs(y) <= 1:
                set_vox(x, y, z, 'seppa_brass', 'Hilt', True)
                continue
            
            # Seppa washer disc (radius <= 2.2)
            if d <= 2.2:
                set_vox(x, y, z, 'seppa_brass', 'Hilt', True)
                continue
            
            # Outer gilded rim
            if d >= 5.0:
                set_vox(x, y, z, 'tsuba_gold', 'Hilt', True)
                continue
            
            # Sukashi Openwork Cutouts:
            # 1. Kozuka-hitsu cutout (+X side): bean-shaped opening at x in (3, 4), y in (-1, 0, 1)
            if x in (3, 4) and y in (-1, 0, 1):
                continue
            # 2. Kogai-hitsu cutout (-X side): trefoil opening at x in (-4, -3), y in (-1, 0, 1)
            if x in (-4, -3) and y in (-1, 0, 1):
                continue
            # 3. Four diagonal petal cutouts
            if abs(x) == 3 and abs(y) == 3:
                continue
            
            # Tsuba blackened iron web with gold highlights
            if x in (2, 5) and y in (-1, 0, 1):
                set_vox(x, y, z, 'tsuba_gold', 'Hilt', True)
            elif x in (-5, -2) and y in (-1, 0, 1):
                set_vox(x, y, z, 'tsuba_gold', 'Hilt', True)
            else:
                set_vox(x, y, z, 'tsuba_iron', 'Hilt', True)

print("Building Habaki (Gilded Copper Blade Collar)...")
# Z = 2 to 4
for z in range(2, 5):
    for x in range(-1, 2):
        for y in range(-2, 3):
            if abs(x) == 1 and abs(y) == 2:
                continue
            if (x + y + z) % 3 == 0:
                set_vox(x, y, z, 'habaki_gold', 'Hilt', True)
            else:
                set_vox(x, y, z, 'habaki_copper', 'Hilt', True)

print("Building Blade (Sori Curvature, Hamon Wave, Tamahagane, Chiseled Kissaki)...")
# Blade: Z = 5 to 68 (64 voxels tall)
# Cutting edge faces +Y, spine faces -Y
for z in range(5, 69):
    t = (z - 5) / 63.0  # 0.0 to 1.0
    y_curve = -int(round(3.8 * (t ** 1.35)))
    
    # Hamon wave undulation formula (Gunome-Midare wave)
    hamon_wave = math.sin(z * 0.42) * 0.8 + math.cos(z * 0.88) * 0.4
    
    is_kissaki = (z >= 60)
    
    if not is_kissaki:
        # Standard Nagasa Blade Body (Shinogi-Zukuri)
        # Spine (Mune) at y_curve - 2 (Deep Charcoal Tamahagane)
        for x in (-1, 0, 1):
            set_vox(x, y_curve - 2, z, 'tamahagane_spine', 'Blade_Bone', True)
            
        # Shinogi-ji Flat at y_curve - 1 (Slate Blue-Grey Folded Steel)
        for x in (-1, 0, 1):
            set_vox(x, y_curve - 1, z, 'tamahagane_flat', 'Blade_Bone', True)
            
        # Shinogi Ridge line at y_curve
        for x in (-1, 0, 1):
            m = 'tamahagane_spine' if abs(x) == 1 else 'tamahagane_flat'
            set_vox(x, y_curve, z, m, 'Blade_Bone', True)
            
        # Hira-ji & Hamon wave line at y_curve + 1 (Crystalline Pearl Wave)
        for x in (-1, 0, 1):
            if hamon_wave > 0.15:
                m = 'hamon_crest'
            elif hamon_wave > -0.25:
                m = 'hamon_valley'
            else:
                m = 'tamahagane_flat'
            set_vox(x, y_curve + 1, z, m, 'Blade_Bone', True)
            
        # Razor Cutting Edge (Ha) at y_curve + 2: single-voxel razor edge (x=0)
        set_vox(0, y_curve + 2, z, 'cutting_edge', 'Blade_Bone', True)
        
    else:
        # Chiseled Kissaki (Tip) - Z = 60 to 68
        kz = z - 60
        if kz <= 2:
            for x in (-1, 0, 1):
                set_vox(x, y_curve - 2, z, 'tamahagane_spine', 'Blade_Bone', True)
                set_vox(x, y_curve - 1, z, 'tamahagane_flat', 'Blade_Bone', True)
                set_vox(x, y_curve, z, 'hamon_crest', 'Blade_Bone', True)
            set_vox(0, y_curve + 1, z, 'cutting_edge', 'Blade_Bone', True)
        elif kz <= 5:
            for x in (-1, 0, 1):
                set_vox(x, y_curve - 1, z, 'tamahagane_spine', 'Blade_Bone', True)
                set_vox(x, y_curve, z, 'hamon_crest', 'Blade_Bone', True)
            set_vox(0, y_curve + 1, z, 'cutting_edge', 'Blade_Bone', True)
        elif kz <= 7:
            set_vox(0, y_curve - 1, z, 'tamahagane_spine', 'Blade_Bone', True)
            for x in (-1, 0, 1):
                set_vox(x, y_curve, z, 'hamon_crest', 'Blade_Bone', True)
            set_vox(0, y_curve + 1, z, 'cutting_edge', 'Blade_Bone', True)
        else:
            set_vox(0, y_curve, z, 'hamon_crest', 'Blade_Bone', True)
            set_vox(0, y_curve + 1, z, 'cutting_edge', 'Blade_Bone', True)

print("Building Dynamic Attack Trail (Flawless C1 Continuous Crescent Wave)...")
# Attached to Trail_Bone!
# Spans from z = 8 (near habaki) up to z = 86 (18 voxels PAST the kissaki tip!)
for z in range(8, 87):
    if z <= 68:
        t_blade = (z - 5) / 63.0
        y_c = -int(round(3.8 * (t_blade ** 1.35)))
        y_edge = y_c + 2
        
        u = (z - 8) / 60.0
        arc_reach = max(1, int(round(22.0 * math.sin(u * math.pi * 0.5))))
        y_start = y_edge + 1
    else:
        t_fin = (z - 68) / 18.0
        arc_reach = max(1, int(round(22.0 * math.cos(t_fin * math.pi * 0.5))))
        y_curl = int(round(math.sin(t_fin * math.pi * 0.5) * 3.0))
        y_start = -2 + 1 + y_curl
        
    for dy in range(arc_reach):
        y = y_start + dy
        pct = dy / float(max(1, arc_reach - 1))
        
        # Saturated cyan/azure gradient with razor white core filament
        if dy == 0:
            m = 'trail_core'          # Pure celestial white laser filament (Emission 1.8)
        elif pct <= 0.35:
            m = 'trail_cyan_bright'   # Electric luminescent cyan (Emission 1.5)
        elif pct <= 0.68:
            m = 'trail_cyan_deep'     # Azure / celestial turquoise (Emission 1.2)
        elif pct <= 0.88:
            m = 'trail_cyan_plasma'   # Outer sapphire plasma (Emission 0.9)
        else:
            m = 'trail_cyan_dark'     # Outer plasma rim (Emission 0.6)
            
        set_vox(0, y, z, m, 'Trail_Bone', True)

# Add dynamic energy trailing spurs peeling off the trailing edge
spur_offsets = [
    (0, 16, 32), (0, 19, 38), (0, 22, 46), (0, 24, 52), (0, 23, 60),
    (0, 21, 68), (0, 18, 76), (0, 12, 82), (0, 6, 86),
    (-1, 18, 42), (1, 21, 50), (-1, 20, 58), (1, 16, 72)
]
for sx, sy_off, sz in spur_offsets:
    t_b = min(1.0, max(0.0, (min(sz, 68) - 5) / 63.0))
    y_c = -int(round(3.8 * (t_b ** 1.35)))
    set_vox(sx, y_c + 2 + sy_off, sz, 'trail_cyan_bright', 'Trail_Bone', True)

print(f">>> Total Katana & Trail Voxels: {len(voxels)}")

# 4. Construct Watertight Boundary-Quad Mesh with Explicit Vertex Groups
print("Generating boundary-quad voxel mesh...")
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

print(f"Mesh Data: {len(verts)} vertices, {len(faces)} boundary quads.")
mesh = bpy.data.meshes.new("Katana_Mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

for m in used_mat_names:
    mesh.materials.append(mats[m])
for poly, slot in zip(mesh.polygons, face_mats):
    poly.material_index = slot
    
mesh.polygons.foreach_set('use_smooth', [False] * len(mesh.polygons))
mesh.update()

katana_obj = bpy.data.objects.new("Katana_Model", mesh)
bpy.context.collection.objects.link(katana_obj)

# 5. Build Armature & Rigging (Aligned to World Coordinates)
print("Building Armature: Root -> Hilt -> Blade_Bone, Hilt -> Trail_Bone...")
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
bone_hilt.head = (0, 0, 0)
bone_hilt.tail = (0, 0.10, 0)

bone_blade = eb.new("Blade_Bone")
bone_blade.parent = bone_hilt
bone_blade.head = (0, 0, 5 * VOXEL_SIZE)
bone_blade.tail = (0, 0.10, 5 * VOXEL_SIZE)

bone_trail = eb.new("Trail_Bone")
bone_trail.parent = bone_hilt
bone_trail.head = (0, 0, 5 * VOXEL_SIZE)
bone_trail.tail = (0, 0.10, 5 * VOXEL_SIZE)

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

# 6. Keyframe Animation (60 frames @ 30fps) - Dynamic Iaido Crescent Slash
print("Keyframing Iaido Crescent Slash Animation (60 frames)...")
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')

pose_root = arm_obj.pose.bones["Root"]
pose_hilt = arm_obj.pose.bones["Hilt"]
pose_blade = arm_obj.pose.bones["Blade_Bone"]
pose_trail = arm_obj.pose.bones["Trail_Bone"]

all_pose_bones = [pose_root, pose_hilt, pose_blade, pose_trail]

# MANDATORY: For all pose bones, set rotation_mode = 'XYZ' before setting rotation_euler
for pb in all_pose_bones:
    pb.rotation_mode = 'XYZ'

def kf_all(frame):
    for pb in all_pose_bones:
        pb.keyframe_insert(data_path="location", frame=frame)
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)
        pb.keyframe_insert(data_path="scale", frame=frame)

# =============================================================================
# FRAME 1: Ready Focus Stance (Coiled Iaido Hip Stance)
# =============================================================================
pose_root.location = (0, 0, 0)
pose_root.rotation_euler = (0, 0, 0)
pose_root.scale = (1, 1, 1)

pose_hilt.location = (-0.15, -0.08, 0.32)
pose_hilt.rotation_euler = (math.radians(-65), math.radians(18), math.radians(-28))
pose_hilt.scale = (1, 1, 1)

pose_blade.location = (0, 0, 0)
pose_blade.rotation_euler = (0, 0, 0)
pose_blade.scale = (1, 1, 1)

pose_trail.location = (0, 0, 0)
pose_trail.rotation_euler = (0, 0, 0)
pose_trail.scale = (0, 0, 0)  # Trail completely hidden!

kf_all(1)

# FRAME 8: Subtle breathing sway
pose_hilt.location = (-0.15, -0.08, 0.33)
pose_hilt.rotation_euler = (math.radians(-64), math.radians(17), math.radians(-27))
kf_all(8)

# FRAME 15: Coiled tension before draw (Trail scale = (0,0,0))
pose_hilt.location = (-0.15, -0.08, 0.32)
pose_hilt.rotation_euler = (math.radians(-66), math.radians(19), math.radians(-29))
pose_trail.scale = (0, 0, 0)
kf_all(15)

# =============================================================================
# FRAME 16-24: Blinding High-Speed Slash Arc!
# =============================================================================
# FRAME 16: Flash Draw Initiation
pose_hilt.location = (-0.08, 0.04, 0.40)
pose_hilt.rotation_euler = (math.radians(-30), math.radians(28), math.radians(-10))
pose_trail.scale = (0.20, 0.20, 0.20)
kf_all(16)

# FRAME 18: Explosive acceleration through diagonal sweep
pose_hilt.location = (0.02, 0.18, 0.50)
pose_hilt.rotation_euler = (math.radians(18), math.radians(32), math.radians(18))
pose_blade.rotation_euler = (math.radians(2.2), 0, 0)
pose_trail.scale = (0.55, 0.55, 0.55)
kf_all(18)

# FRAME 21: Full supersonic sweep
pose_hilt.location = (0.12, 0.30, 0.58)
pose_hilt.rotation_euler = (math.radians(52), math.radians(26), math.radians(40))
pose_blade.rotation_euler = (math.radians(-2.5), 0, 0)
pose_trail.scale = (0.85, 0.85, 0.85)
kf_all(21)

# FRAME 24: PEAK CRESCENT SLASH! Dynamic Heroic Cut & Full Flare!
# Optimized pitch & roll so blade flat faces camera with rich hamon contrast
pose_hilt.location = (0.16, 0.36, 0.62)
pose_hilt.rotation_euler = (math.radians(65), math.radians(24), math.radians(45))
pose_blade.rotation_euler = (math.radians(1.4), 0, 0)
pose_trail.location = (0, 0, 0)
pose_trail.rotation_euler = (0, 0, 0)
pose_trail.scale = (1.0, 1.0, 1.0)  # FULL MAJESTIC CRESCENT FLARE!
kf_all(24)

# =============================================================================
# FRAME 25-36: Climax, Blade Flex & Trail Dissipation (Zanshin)
# =============================================================================
# FRAME 27: Steel vibration deceleration
pose_hilt.location = (0.16, 0.36, 0.62)
pose_hilt.rotation_euler = (math.radians(66), math.radians(23), math.radians(46))
pose_blade.rotation_euler = (math.radians(-1.5), 0, 0)
pose_trail.scale = (0.80, 0.70, 0.80)
kf_all(27)

# FRAME 30: Residual resonance
pose_hilt.location = (0.16, 0.35, 0.62)
pose_hilt.rotation_euler = (math.radians(65), math.radians(24), math.radians(45))
pose_blade.rotation_euler = (math.radians(0.6), 0, 0)
pose_trail.scale = (0.40, 0.30, 0.40)
kf_all(30)

# FRAME 36: Zanshin poise, trail completely dissipated
pose_hilt.location = (0.15, 0.33, 0.61)
pose_hilt.rotation_euler = (math.radians(64), math.radians(24), math.radians(44))
pose_blade.rotation_euler = (0, 0, 0)
pose_trail.scale = (0, 0, 0)
kf_all(36)

# =============================================================================
# FRAME 37-48: Blade Flick (Chiburui - Ritual Cleansing)
# =============================================================================
# FRAME 38: Poised lift
pose_hilt.location = (0.12, 0.28, 0.65)
pose_hilt.rotation_euler = (math.radians(85), math.radians(-2), math.radians(40))
kf_all(38)

# FRAME 42: Downward wrist snap flick!
pose_hilt.location = (0.08, 0.20, 0.46)
pose_hilt.rotation_euler = (math.radians(34), math.radians(-20), math.radians(22))
pose_blade.rotation_euler = (math.radians(-3.5), 0, 0)
kf_all(42)

# FRAME 45: Rebound & poise
pose_hilt.location = (0.05, 0.16, 0.49)
pose_hilt.rotation_euler = (math.radians(40), math.radians(-16), math.radians(18))
pose_blade.rotation_euler = (0, 0, 0)
kf_all(45)

# FRAME 48: Poised before glide return
pose_hilt.location = (0.0, 0.08, 0.46)
pose_hilt.rotation_euler = (math.radians(16), math.radians(-10), math.radians(6))
kf_all(48)

# =============================================================================
# FRAME 49-60: Return to Ready Stance (Noto)
# =============================================================================
# FRAME 53: Gliding back toward hip
pose_hilt.location = (-0.08, 0.0, 0.39)
pose_hilt.rotation_euler = (math.radians(-22), math.radians(2), math.radians(-8))
kf_all(53)

# FRAME 57: Settling at hip scabbard
pose_hilt.location = (-0.12, -0.05, 0.34)
pose_hilt.rotation_euler = (math.radians(-52), math.radians(12), math.radians(-18))
kf_all(57)

# FRAME 60: Seamless loop return to Frame 1
pose_root.location = (0, 0, 0)
pose_root.rotation_euler = (0, 0, 0)
pose_root.scale = (1, 1, 1)

pose_hilt.location = (-0.15, -0.08, 0.32)
pose_hilt.rotation_euler = (math.radians(-65), math.radians(18), math.radians(-28))
pose_hilt.scale = (1, 1, 1)

pose_blade.location = (0, 0, 0)
pose_blade.rotation_euler = (0, 0, 0)
pose_blade.scale = (1, 1, 1)

pose_trail.location = (0, 0, 0)
pose_trail.rotation_euler = (0, 0, 0)
pose_trail.scale = (0, 0, 0)

kf_all(60)

bpy.ops.object.mode_set(mode='OBJECT')

# 7. World Environment & Cycles AgX High Contrast Studio Lighting Setup
print("Setting up Cycles AgX High Contrast Studio Lighting & Celestial World...")
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - High Contrast'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# World ambient background (subtle midnight slate blue)
world = bpy.data.worlds.new("Katana_World")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs['Color'].default_value = (0.010, 0.014, 0.024, 1.0)
    bg_node.inputs['Strength'].default_value = 0.50

# Center target for Frame 24
target_emp = bpy.data.objects.new("Camera_Target", None)
target_emp.location = (0.45, 0.30, 0.70)
bpy.context.collection.objects.link(target_emp)

# Heroic Perspective Camera
cam_data = bpy.data.cameras.new("Katana_Camera")
cam_data.lens = 46
cam_obj = bpy.data.objects.new("Katana_Camera", object_data=cam_data)
cam_obj.location = (0.48, -1.80, 1.25)

track = cam_obj.constraints.new(type='TRACK_TO')
track.target = target_emp
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

# 4-Point Balanced Studio Lighting:
# 1) Key Sun Light (Warm crisp glint revealing crystalline hamon wave)
key_l = bpy.data.objects.new("Key_Sun", bpy.data.lights.new("Key_Sun", type='SUN'))
key_l.data.energy = 2.8
key_l.data.color = (1.00, 0.96, 0.90)
key_l.data.angle = math.radians(4)
key_l.rotation_euler = (math.radians(48), math.radians(22), math.radians(-32))
bpy.context.collection.objects.link(key_l)

# 2) Top Rim Light (Cool azure highlight outlining blade spine & chisel kissaki)
rim_top = bpy.data.objects.new("Rim_Top", bpy.data.lights.new("Rim_Top", type='AREA'))
rim_top.data.energy = 320.0
rim_top.data.color = (0.75, 0.92, 1.00)
rim_top.data.size = 2.6
rim_top.location = (0.2, 1.9, 2.3)
rim_top.rotation_euler = (math.radians(-65), math.radians(10), math.radians(165))
bpy.context.collection.objects.link(rim_top)

# 3) Soft Front Fill Light (Gentle illumination for samegawa ray skin & tsuba openwork)
fill_front = bpy.data.objects.new("Fill_Front", bpy.data.lights.new("Fill_Front", type='AREA'))
fill_front.data.energy = 90.0
fill_front.data.color = (0.85, 0.90, 1.00)
fill_front.data.size = 3.2
fill_front.location = (1.8, -1.2, 0.6)
fill_front.rotation_euler = (math.radians(25), math.radians(-20), math.radians(-40))
bpy.context.collection.objects.link(fill_front)

# 4) Left Rim / Hilt Light (Warm rim on kashira pommel and silk wrap)
rim_hilt = bpy.data.objects.new("Rim_Hilt", bpy.data.lights.new("Rim_Hilt", type='AREA'))
rim_hilt.data.energy = 160.0
rim_hilt.data.color = (0.95, 0.85, 0.70)
rim_hilt.data.size = 1.8
rim_hilt.location = (-1.5, -0.6, 0.9)
rim_hilt.rotation_euler = (math.radians(15), math.radians(50), math.radians(-70))
bpy.context.collection.objects.link(rim_hilt)

# 8. Output Paths & Export
workspace_dir = os.path.abspath(os.path.dirname(__file__))
blend_file = os.path.join(workspace_dir, "katana.blend")
glb_file = os.path.join(workspace_dir, "katana.glb")
render_file = os.path.join(workspace_dir, "katana_render.png")
js_file = os.path.join(workspace_dir, "katana_data.js")

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

print(f"Rendering beauty frame 24 (Peak Crescent Slash) to {render_file}...")
scene.frame_set(24)
scene.render.filepath = render_file
bpy.ops.render.render(write_still=True)

# Generate Base64 Data URI in katana_data.js
print(f"Generating base64 data to {js_file}...")
with open(glb_file, 'rb') as f:
    glb_b64 = base64.b64encode(f.read()).decode('utf-8')

js_content = f'window.KATANA_FLASH_BASE64 = "data:model/gltf-binary;base64,{glb_b64}";\n'
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_content)

print("=================================================================")
print(">>> [SUCCESS] Trove Katana & Attack Trail v4.0 Generated & Exported!")
print("=================================================================")
