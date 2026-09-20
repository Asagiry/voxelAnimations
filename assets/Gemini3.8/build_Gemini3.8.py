import bpy
import math
import os
import base64

print("=================================================================")
print(">>> [TROVE VOXEL ARTISAN] Astral Void Scythe 'Gemini 3.8' v4.0")
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
    # Deep void metal & obsidian chassis
    'void_steel':         make_shader('M_VoidSteel',         (0.08, 0.09, 0.15, 1.0), roughness=0.22, metallic=0.90),
    'void_black':         make_shader('M_VoidBlack',         (0.02, 0.02, 0.035, 1.0), roughness=0.55, metallic=0.25),
    'starlight_silver':   make_shader('M_StarlightSilver',   (0.82, 0.86, 0.96, 1.0), roughness=0.14, metallic=0.95),
    'celestial_gold':     make_shader('M_CelestialGold',     (0.96, 0.78, 0.22, 1.0), roughness=0.18, metallic=0.95),
    'handle_leather':     make_shader('M_HandleLeather',     (0.12, 0.10, 0.16, 1.0), roughness=0.80, metallic=0.06),
    
    # Controlled AgX luminous energy
    'astral_cyan':        make_shader('M_AstralCyan',        (0.00, 0.76, 1.00, 1.0), roughness=0.08, metallic=0.05, emission=2.2, emission_color=(0.00, 0.82, 1.00, 1.0)),
    'void_purple':        make_shader('M_VoidPurple',        (0.48, 0.06, 0.95, 1.0), roughness=0.10, metallic=0.05, emission=2.0, emission_color=(0.55, 0.10, 1.00, 1.0)),
    'vortex_core':        make_shader('M_VortexCore',        (0.92, 0.98, 1.00, 1.0), roughness=0.04, metallic=0.02, emission=3.2, emission_color=(0.92, 0.98, 1.00, 1.0)),
    'trail_spark':        make_shader('M_TrailSpark',        (0.20, 0.90, 1.00, 1.0), roughness=0.05, metallic=0.05, emission=2.4, emission_color=(0.20, 0.90, 1.00, 1.0)),
}

voxels = {}

def set_vox(x, y, z, mat, bone, overwrite=False):
    k = (int(x), int(y), int(z))
    if not overwrite and k in voxels:
        return
    voxels[k] = (mat, bone)

print("Building Pommel & Counterweight Crescent...")
# Bottom Pommel Crescent Blade (z: -58 to -44)
for z in range(-58, -44):
    progress = (z - (-58)) / 14.0
    y_curve = int(-6 * math.sin(progress * math.pi))
    thickness = 1 if z < -54 else 2
    for x in range(-thickness, thickness + 1):
        for y in range(y_curve - 1, y_curve + 2):
            if abs(x) == thickness and abs(y - y_curve) == 1:
                continue
            if abs(x) == thickness or y == y_curve - 1:
                m = 'void_steel'
            elif y == y_curve:
                m = 'void_purple'
            else:
                m = 'void_black'
            set_vox(x, y, z, m, 'scythe_body', True)

for x in range(-2, 3):
    for y in range(-2, 3):
        if abs(x) == 2 or abs(y) == 2:
            set_vox(x, y, -44, 'celestial_gold', 'scythe_body', True)

print("Building Long Shaft & Wrapped Grips...")
for z in range(-44, 46):
    is_gold_ring = (z in (-32, -18, -4, 10, 24, 38))
    is_silver_accent = (z in (-31, -17, -3, 11, 25, 39))
    
    for x in range(-2, 3):
        for y in range(-2, 3):
            if abs(x) == 2 and abs(y) == 2:
                continue
            is_edge = (abs(x) == 2 or abs(y) == 2)
            
            if is_gold_ring:
                m = 'celestial_gold'
            elif is_silver_accent and is_edge:
                m = 'starlight_silver'
            else:
                spiral_phase = (z * 0.45) % (2 * math.pi)
                spiral_x = math.cos(spiral_phase)
                spiral_y = math.sin(spiral_phase)
                
                dot = (x * spiral_x + y * spiral_y)
                if is_edge and dot > 1.3:
                    m = 'astral_cyan'
                elif is_edge and (z % 4 == 0 or (x + y + z) % 5 == 0):
                    m = 'void_steel'
                elif is_edge:
                    m = 'handle_leather'
                else:
                    m = 'void_black'
                    
            set_vox(x, y, z, m, 'scythe_body', True)

print("Building Cosmic Nexus & Eye of the Void...")
for z in range(46, 58):
    dz = z - 52
    r_bracket = max(2, int(4.5 - abs(dz) * 0.35))
    for x in range(-r_bracket - 1, r_bracket + 2):
        for y in range(-r_bracket - 1, r_bracket + 3):
            d2 = x*x + (y - 0.5)*(y - 0.5)
            if (r_bracket - 0.5)**2 <= d2 <= (r_bracket + 1.2)**2:
                is_claw = (abs(abs(x) - abs(y)) <= 1)
                m = 'celestial_gold' if is_claw else 'void_steel'
                set_vox(x, y, z, m, 'scythe_body', True)

# Floating Void Singularity Eye at nexus center (0, 0, 52)
for x in range(-2, 3):
    for y in range(-2, 3):
        for z in range(50, 55):
            d3 = x*x + y*y + (z - 52)*(z - 52)
            if d3 <= 5.0:
                if d3 <= 1.5:
                    m = 'vortex_core'
                elif d3 <= 3.0:
                    m = 'astral_cyan'
                else:
                    m = 'void_purple'
                set_vox(x, y, z, m, 'scythe_body', True)

# Blade Mount Neck projecting forward along Y
for y in range(3, 11):
    for x in range(-2, 3):
        for z in range(49, 56):
            if abs(x) == 2 and (z == 49 or z == 55):
                continue
            m = 'celestial_gold' if abs(x) == 2 else 'void_steel'
            set_vox(x, y, z, m, 'scythe_body', True)

print("Building Massive Crescent Void Blade...")
# Grand sickle curve wrapping around the vortex
STEPS = 75
for i in range(STEPS):
    t = i / float(STEPS - 1)
    
    if t < 0.36:
        sub_t = t / 0.36
        y_center = 10.0 + 16.0 * math.sin(sub_t * math.pi * 0.5)
        z_center = 52.0 + 26.0 * math.sin(sub_t * math.pi * 0.5)
    else:
        sub_t = (t - 0.36) / 0.64
        y_center = 26.0 + 34.0 * math.sin(sub_t * math.pi * 0.5)
        z_center = 78.0 - 52.0 * (sub_t ** 1.28)
        
    yc = int(round(y_center))
    zc = int(round(z_center))
    
    max_w = max(1, int(round(7.0 * (1.0 - t * 0.70))))
    thickness_x = max(1, int(round(4.0 * (1.0 - t * 0.60))))
    
    for w in range(max_w):
        x_span = max(0, thickness_x - int(w * 0.65))
        vox_z = zc - w
        vox_y = yc - int(w * 0.70)
        
        for vx in range(-x_span, x_span + 1):
            if w == 0:
                m = 'starlight_silver' if (i % 5 == 0) else 'void_steel'
            elif w == 1:
                m = 'void_black'
            elif w == 2:
                m = 'void_purple'
            elif w == max_w - 1:
                m = 'astral_cyan'
            else:
                m = 'astral_cyan' if (i % 3 == 0) else 'void_black'
                
            set_vox(vx, vox_y, vox_z, m, 'scythe_body', True)

# Outer Backward Defensive Thorn
for th in range(15):
    prog = th / 14.0
    th_y = int(round(26.0 - prog * 12.0))
    th_z = int(round(78.0 + prog * 13.0))
    th_w = max(0, 2 - int(prog * 2.5))
    for vx in range(-th_w, th_w + 1):
        for dy in range(-1, 2):
            m = 'celestial_gold' if abs(vx) == th_w else 'void_steel'
            if th >= 13:
                m = 'astral_cyan'
            set_vox(vx, th_y + dy, th_z, m, 'scythe_body', True)

print("Building Rotating Runic Rings...")
R1 = 16
for angle in range(0, 360, 4):
    rad = math.radians(angle)
    rx = R1 * math.cos(rad)
    ry = R1 * math.sin(rad)
    rz = 52.0 + 3.0 * math.sin(rad)
    
    cx, cy, cz = int(round(rx)), int(round(ry)), int(round(rz))
    
    for dx in (0, 1):
        for dz in (0, 1):
            if angle % 90 == 0:
                m = 'celestial_gold'
            elif angle % 20 == 0:
                m = 'astral_cyan'
            else:
                m = 'void_steel'
            set_vox(cx + dx, cy, cz + dz, m, 'runic_ring_1', True)

R2 = 11
for angle in range(0, 360, 5):
    rad = math.radians(angle)
    rx = R2 * math.cos(rad) * math.cos(math.radians(60))
    ry = R2 * math.sin(rad)
    rz = 52.0 + R2 * math.cos(rad) * math.sin(math.radians(60))
    
    cx, cy, cz = int(round(rx)), int(round(ry)), int(round(rz))
    
    for dy in (0, 1):
        for dz in (0, 1):
            if angle % 90 == 0:
                m = 'starlight_silver'
            elif angle % 25 == 0:
                m = 'void_purple'
            else:
                m = 'void_steel'
            set_vox(cx, cy + dy, cz + dz, m, 'runic_ring_2', True)

print("Building Dense Volumetric Circular Vortex Attack Geometry...")
# Center of the vortex disc matches the scythe's sickle hook center (0, 28, 52)
VORTEX_CENTER_Y = 28
VORTEX_CENTER_Z = 52
MAX_R = 36

for r in range(4, MAX_R + 1):
    num_steps = max(18, int(round(3.0 * math.pi * r)))
    for step in range(num_steps):
        angle_deg = (step / float(num_steps)) * 360.0
        rad = math.radians(angle_deg)
        
        # 4 cosmic arms
        arm_phase = (angle_deg - r * 9.0) % 90.0
        dist_to_arm = min(arm_phase, 90.0 - arm_phase)
        
        wave_z = math.sin(math.radians(angle_deg * 2.0 + r * 5.5)) * 1.6
        
        vx = int(round(r * math.cos(rad)))
        vy = int(round(VORTEX_CENTER_Y + r * math.sin(rad)))
        vz = int(round(VORTEX_CENTER_Z + wave_z))
        
        if r <= 11 or dist_to_arm < 16.0 or (r <= 24 and dist_to_arm < 24.0):
            z_thickness = 2 if (r <= 12 or dist_to_arm < 7.0) else 1
            for dz in range(-z_thickness + 1, z_thickness):
                if r <= 8:
                    m = 'vortex_core'
                elif dist_to_arm < 7.0:
                    m = 'astral_cyan'
                elif r <= 24:
                    m = 'void_purple'
                else:
                    m = 'trail_spark' if (step % 2 == 0) else 'void_purple'
                    
                set_vox(vx, vy, vz + dz, m, 'vortex_attack', True)

# Outer crescent cutting slash waves around vortex rim
for sl in range(4):
    base_ang = sl * 90.0 + 15.0
    for arc in range(26):
        arc_ang = math.radians(base_ang + arc * 3.4)
        arc_r = 34.0 + arc * 0.35
        ax = int(round(arc_r * math.cos(arc_ang)))
        ay = int(round(VORTEX_CENTER_Y + arc_r * math.sin(arc_ang)))
        az = int(round(VORTEX_CENTER_Z + math.sin(arc * 0.25) * 1.5))
        for dz in (-1, 0, 1):
            mat_sl = 'astral_cyan' if (dz == 0 and arc > 10) else 'trail_spark'
            set_vox(ax, ay, az + dz, mat_sl, 'vortex_attack', True)

print(f"Total Unique Voxels Generated: {len(voxels)}")

# 4. Optimized Boundary-Only Voxel Mesher
print("Generating Optimized Boundary Quad Mesh...")
DIRECTIONS = [
    (( 1,  0,  0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
    ((-1,  0,  0), [(0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1)]),
    (( 0,  1,  0), [(1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)]),
    (( 0, -1,  0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
    (( 0,  0,  1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
    (( 0,  0, -1), [(0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)]),
]

mat_keys = list(mats.keys())
vgroup_names = ['scythe_body', 'runic_ring_1', 'runic_ring_2', 'vortex_attack']

voxel_keys = set(voxels.keys())

vertices = []
polygons = []
poly_mat_indices = []
vertex_groups_map = {name: [] for name in vgroup_names}

vert_idx = 0
for pos, (mat_name, bone_name) in voxels.items():
    x, y, z = pos
    mat_idx = mat_keys.index(mat_name)
    
    for d, corners in DIRECTIONS:
        neighbor = (x + d[0], y + d[1], z + d[2])
        if neighbor not in voxel_keys:
            quad_vert_indices = []
            for cx, cy, cz in corners:
                vx = (x + cx) * VOXEL_SIZE
                vy = (y + cy) * VOXEL_SIZE
                vz = (z + cz) * VOXEL_SIZE
                vertices.append((vx, vy, vz))
                quad_vert_indices.append(vert_idx)
                vertex_groups_map[bone_name].append(vert_idx)
                vert_idx += 1
                
            polygons.append(quad_vert_indices)
            poly_mat_indices.append(mat_idx)

mesh_data = bpy.data.meshes.new("AstralScythe_Mesh")
mesh_data.from_pydata(vertices, [], polygons)
mesh_data.update()

scythe_obj = bpy.data.objects.new("AstralScythe_Gemini38", mesh_data)
bpy.context.collection.objects.link(scythe_obj)

for m_key in mat_keys:
    scythe_obj.data.materials.append(mats[m_key])

for poly, m_idx in zip(scythe_obj.data.polygons, poly_mat_indices):
    poly.material_index = m_idx

for vg_name in vgroup_names:
    vg = scythe_obj.vertex_groups.new(name=vg_name)
    vert_indices = vertex_groups_map[vg_name]
    if vert_indices:
        vg.add(vert_indices, 1.0, 'ADD')

bpy.context.view_layer.objects.active = scythe_obj
scythe_obj.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.dissolve_limited(angle_limit=0.0001)
bpy.ops.mesh.tris_convert_to_quads()
bpy.ops.object.mode_set(mode='OBJECT')

scythe_obj.data.polygons.foreach_set('use_smooth', [False] * len(scythe_obj.data.polygons))
scythe_obj.data.update()

print("Mesh Optimization Complete!")

# 5. Skeletal Rigging
print("Configuring Skeletal Armature...")
arm_data = bpy.data.armatures.new("Scythe_ArmatureData")
arm_obj = bpy.data.objects.new("Scythe_Armature", arm_data)
bpy.context.collection.objects.link(arm_obj)

bpy.context.view_layer.objects.active = arm_obj
arm_obj.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')

nexus_z = 52 * VOXEL_SIZE
vortex_y = VORTEX_CENTER_Y * VOXEL_SIZE
vortex_z = VORTEX_CENTER_Z * VOXEL_SIZE

def create_bone(name, head, tail, parent_name=None):
    b = arm_data.edit_bones.new(name)
    b.head = head
    b.tail = tail
    if parent_name:
        b.parent = arm_data.edit_bones[parent_name]
    return b

create_bone('root', (0, 0, 0), (0, 0, 0.1))
create_bone('scythe_body', (0, 0, 0), (0, 0, 0.6), 'root')
create_bone('runic_ring_1', (0, 0, nexus_z), (0, 0, nexus_z + 0.1), 'scythe_body')
create_bone('runic_ring_2', (0, 0, nexus_z), (0, 0, nexus_z + 0.1), 'scythe_body')
create_bone('vortex_attack', (0, vortex_y, vortex_z), (0, vortex_y, vortex_z + 0.1), 'scythe_body')

bpy.ops.object.mode_set(mode='OBJECT')

scythe_obj.parent = arm_obj
arm_mod = scythe_obj.modifiers.new(name="Armature", type='ARMATURE')
arm_mod.object = arm_obj

# 6. Keyframe Animation: Heroic Whirlwind Vortex Attack
print("Keyframing 60-Frame Heroic Whirlwind Vortex Attack...")
bpy.context.view_layer.objects.active = arm_obj
arm_obj.select_set(True)
bpy.ops.object.mode_set(mode='POSE')

action = bpy.data.actions.new(name="Attack_Vortex")
arm_obj.animation_data_create()
arm_obj.animation_data.action = action

pb_body = arm_obj.pose.bones['scythe_body']
pb_ring1 = arm_obj.pose.bones['runic_ring_1']
pb_ring2 = arm_obj.pose.bones['runic_ring_2']
pb_vortex = arm_obj.pose.bones['vortex_attack']

for pb in [pb_body, pb_ring1, pb_ring2, pb_vortex]:
    pb.rotation_mode = 'XYZ'

def kf(pb, prop, frame, val):
    if prop == 'location':
        pb.location = val
    elif prop == 'rotation_euler':
        pb.rotation_euler = val
    elif prop == 'scale':
        pb.scale = val
    pb.keyframe_insert(data_path=prop, frame=frame)

# Phase 1: Floating Upright Idle & Gyroscopic Ring Rotation (F1 - F24)
# Note: For a bone along +Z, local Y is along the shaft (yaw spin), local X is forward tilt, local Z is side tilt!
kf(pb_body, 'location', 1, (0, 0, 0.05))
kf(pb_body, 'rotation_euler', 1, (math.radians(-12), 0, math.radians(8)))

kf(pb_body, 'location', 12, (0, 0, 0.08))
kf(pb_body, 'rotation_euler', 12, (math.radians(-9), 0, math.radians(6)))

kf(pb_body, 'location', 24, (0, 0, 0.05))
kf(pb_body, 'rotation_euler', 24, (math.radians(-12), 0, math.radians(8)))

# Continuous Runic Rings Gyroscopic Rotation
kf(pb_ring1, 'rotation_euler', 1, (0, 0, 0))
kf(pb_ring1, 'rotation_euler', 24, (0, 0, math.radians(144)))
kf(pb_ring1, 'rotation_euler', 38, (0, 0, math.radians(400)))
kf(pb_ring1, 'rotation_euler', 60, (0, 0, math.radians(720)))

kf(pb_ring2, 'rotation_euler', 1, (0, 0, 0))
kf(pb_ring2, 'rotation_euler', 24, (math.radians(-144), 0, math.radians(72)))
kf(pb_ring2, 'rotation_euler', 38, (math.radians(-400), 0, math.radians(200)))
kf(pb_ring2, 'rotation_euler', 60, (math.radians(-720), 0, math.radians(360)))

# Vortex hidden during idle
kf(pb_vortex, 'scale', 1, (0.0001, 0.0001, 0.0001))
kf(pb_vortex, 'scale', 24, (0.0001, 0.0001, 0.0001))
kf(pb_vortex, 'rotation_euler', 1, (0, 0, 0))

# Phase 2: Wind-up (F25 - F32)
kf(pb_body, 'location', 28, (-0.08, -0.06, 0.07))
kf(pb_body, 'rotation_euler', 28, (math.radians(-25), math.radians(-35), math.radians(15)))

kf(pb_body, 'location', 32, (-0.14, -0.10, 0.10))
kf(pb_body, 'rotation_euler', 32, (math.radians(-35), math.radians(-70), math.radians(20)))

kf(pb_vortex, 'scale', 32, (0.08, 0.08, 0.08))
kf(pb_vortex, 'rotation_euler', 32, (0, math.radians(60), 0))

# Phase 3: 360° CIRCULAR VORTEX ATTACK (F33 - F44)
# Scythe performs full 360-degree whirlwind rotation around local Y!
kf(pb_body, 'location', 34, (-0.05, 0.0, 0.08))
kf(pb_body, 'rotation_euler', 34, (math.radians(-15), math.radians(0), math.radians(10)))

kf(pb_body, 'location', 36, (0.04, 0.05, 0.06))
kf(pb_body, 'rotation_euler', 36, (math.radians(-12), math.radians(45), math.radians(8)))
kf(pb_vortex, 'scale', 36, (0.70, 0.70, 0.70))
kf(pb_vortex, 'rotation_euler', 36, (0, math.radians(180), 0))

# Frame 38: HERO CLIMAX FRAME (BROADSIDE SWEEP + FULL CIRCULAR VORTEX DISC)
RENDER_FRAME = 38
kf(pb_body, 'location', 38, (0.06, 0.04, 0.05))
kf(pb_body, 'rotation_euler', 38, (math.radians(-12), math.radians(85), math.radians(8)))

kf(pb_vortex, 'scale', 38, (1.15, 1.15, 1.10))
kf(pb_vortex, 'rotation_euler', 38, (0, math.radians(450), 0))

kf(pb_body, 'location', 41, (0.0, -0.05, 0.05))
kf(pb_body, 'rotation_euler', 41, (math.radians(-14), math.radians(190), math.radians(8)))
kf(pb_vortex, 'scale', 41, (0.95, 0.95, 0.5))
kf(pb_vortex, 'rotation_euler', 41, (0, math.radians(650), 0))

kf(pb_body, 'location', 44, (-0.04, -0.02, 0.05))
kf(pb_body, 'rotation_euler', 44, (math.radians(-14), math.radians(290), math.radians(8)))
kf(pb_vortex, 'scale', 44, (0.35, 0.35, 0.15))

# Phase 4: Follow-Through & Vortex Dispersal (F45 - F53)
kf(pb_body, 'location', 48, (-0.02, 0.0, 0.05))
kf(pb_body, 'rotation_euler', 48, (math.radians(-13), math.radians(330), math.radians(8)))
kf(pb_vortex, 'scale', 48, (0.0001, 0.0001, 0.0001))

kf(pb_body, 'location', 53, (0, 0, 0.05))
kf(pb_body, 'rotation_euler', 53, (math.radians(-12), math.radians(355), math.radians(8)))
kf(pb_vortex, 'scale', 53, (0.0001, 0.0001, 0.0001))

# Phase 5: Seamless Loop back to F1 (F54 - F60)
kf(pb_body, 'location', 60, (0, 0, 0.05))
kf(pb_body, 'rotation_euler', 60, (math.radians(-12), math.radians(360), math.radians(8)))
kf(pb_vortex, 'scale', 60, (0.0001, 0.0001, 0.0001))

for fcurve in arm_obj.animation_data.action.fcurves:
    for kp in fcurve.keyframe_points:
        kp.interpolation = 'BEZIER'
        kp.handle_left_type = 'AUTO_CLAMPED'
        kp.handle_right_type = 'AUTO_CLAMPED'

bpy.ops.object.mode_set(mode='OBJECT')

# 7. Cycles AgX Beauty Lighting & Precision Camera Framing
print(f"Configuring Cycles AgX Beauty Shot at Frame {RENDER_FRAME}...")
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

world = bpy.data.worlds.new("Astral_Void_World")
world.use_nodes = True
nodes = world.node_tree.nodes
nodes.clear()

w_out = nodes.new(type='ShaderNodeOutputWorld')
w_bg = nodes.new(type='ShaderNodeBackground')
w_bg.inputs['Color'].default_value = (0.012, 0.016, 0.026, 1.0)
w_bg.inputs['Strength'].default_value = 0.35
world.node_tree.links.new(w_bg.outputs['Background'], w_out.inputs['Surface'])
scene.world = world

scene.view_settings.view_transform = 'AgX' if hasattr(scene.view_settings, 'view_transform') else 'Filmic'
scene.view_settings.look = 'AgX - High Contrast'

# Calculate evaluated world coordinates at RENDER_FRAME
scene.frame_set(RENDER_FRAME)
bpy.context.view_layer.update()

depsgraph = bpy.context.evaluated_depsgraph_get()
eval_obj = scythe_obj.evaluated_get(depsgraph)
eval_mesh = eval_obj.to_mesh()
world_verts = [eval_obj.matrix_world @ v.co for v in eval_mesh.vertices]
eval_obj.to_mesh_clear()

xs = [v.x for v in world_verts]
ys = [v.y for v in world_verts]
zs = [v.z for v in world_verts]

center = ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, (min(zs) + max(zs)) / 2.0)
span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 0.5)

print(f"Evaluated Bounding Box Center: {center}, Span: {span:.3f}m")

target_emp = bpy.data.objects.new("CamTarget_Astral", None)
target_emp.location = center
bpy.context.collection.objects.link(target_emp)

# Camera: Framed with 32° elevation to capture broadside scythe crescent and spiral disc
cam_data = bpy.data.cameras.new("Astral_Camera")
cam_data.lens = 40
cam_obj = bpy.data.objects.new("Astral_Camera", object_data=cam_data)

cam_dist_xy = span * 1.05
cam_z = span * 0.85
cam_obj.location = (center[0] + cam_dist_xy * 0.75, center[1] - cam_dist_xy * 1.05, center[2] + cam_z)

track = cam_obj.constraints.new(type='TRACK_TO')
track.target = target_emp
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

# 4-Point Dramatic Studio Lighting
key_sun = bpy.data.objects.new("Key_Sun", bpy.data.lights.new("Key_Sun", type='SUN'))
key_sun.data.energy = 4.8
key_sun.data.color = (0.98, 0.98, 1.00)
key_sun.data.angle = math.radians(4)
key_sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(-35))
bpy.context.collection.objects.link(key_sun)

rim_cyan = bpy.data.objects.new("Rim_Cyan", bpy.data.lights.new("Rim_Cyan", type='AREA'))
rim_cyan.data.energy = 340.0
rim_cyan.data.color = (0.00, 0.80, 1.00)
rim_cyan.data.size = 2.5
rim_cyan.location = (center[0] - span * 0.9, center[1] + span * 1.1, center[2] + span * 0.6)
bpy.context.collection.objects.link(rim_cyan)
t_rc = rim_cyan.constraints.new(type='TRACK_TO')
t_rc.target = target_emp
t_rc.track_axis = 'TRACK_NEGATIVE_Z'
t_rc.up_axis = 'UP_Y'

fill_purple = bpy.data.objects.new("Fill_Purple", bpy.data.lights.new("Fill_Purple", type='AREA'))
fill_purple.data.energy = 260.0
fill_purple.data.color = (0.65, 0.15, 1.00)
fill_purple.data.size = 2.8
fill_purple.location = (center[0] - span * 0.8, center[1] - span * 0.8, center[2] + span * 0.2)
bpy.context.collection.objects.link(fill_purple)
t_fp = fill_purple.constraints.new(type='TRACK_TO')
t_fp.target = target_emp
t_fp.track_axis = 'TRACK_NEGATIVE_Z'
t_fp.up_axis = 'UP_Y'

spot_gold = bpy.data.objects.new("Spot_Gold", bpy.data.lights.new("Spot_Gold", type='SPOT'))
spot_gold.data.energy = 220.0
spot_gold.data.color = (1.00, 0.82, 0.40)
spot_gold.data.spot_size = math.radians(50)
spot_gold.location = (center[0] + span * 0.4, center[1] + span * 0.4, center[2] + span * 1.2)
bpy.context.collection.objects.link(spot_gold)
t_sg = spot_gold.constraints.new(type='TRACK_TO')
t_sg.target = target_emp
t_sg.track_axis = 'TRACK_NEGATIVE_Z'
t_sg.up_axis = 'UP_Y'

# 8. File Export & Render Output
output_dir = os.path.dirname(os.path.abspath(__file__))
blend_file = os.path.join(output_dir, "Gemini3.8.blend")
glb_file = os.path.join(output_dir, "Gemini3.8.glb")
render_file = os.path.join(output_dir, "Gemini3.8_render.png")
js_file = os.path.join(output_dir, "Gemini3.8_data.js")

print(f"Saving .blend: {blend_file}")
bpy.ops.wm.save_as_mainfile(filepath=blend_file)

print(f"Exporting GLB: {glb_file}")
bpy.ops.object.select_all(action='DESELECT')
scythe_obj.select_set(True)
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

print(f"Rendering Frame {RENDER_FRAME} (Hero 360° Circular Vortex Climax) to {render_file}...")
scene.frame_set(RENDER_FRAME)
scene.render.filepath = render_file
bpy.ops.render.render(write_still=True)

print(f"Generating base64 data to {js_file}...")
with open(glb_file, 'rb') as f:
    glb_b64 = base64.b64encode(f.read()).decode('utf-8')

js_content = f'window.GEMINI3_8_BASE64 = "data:model/gltf-binary;base64,{glb_b64}";\n'
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_content)

print("=================================================================")
print(">>> [SUCCESS] Astral Void Scythe 'Gemini 3.8' Created & Exported!")
print("=================================================================")
