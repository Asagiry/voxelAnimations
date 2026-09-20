import bpy
import math
import os

print("=================================================================")
print(">>> [CELESTIAL VOXEL ENGINE 3.0] Generating Perfect Magic Bow")
print("=================================================================")

# 1. Reset Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 60
scene.render.fps = 30

# 2. Materials
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
    'obsidian':      make_shader('M_Obsidian',      (0.06, 0.07, 0.11, 1.0), roughness=0.45, metallic=0.25),
    'navy_plate':    make_shader('M_NavyPlate',     (0.11, 0.15, 0.25, 1.0), roughness=0.35, metallic=0.35),
    'gold':          make_shader('M_Gold',          (0.96, 0.72, 0.14, 1.0), roughness=0.22, metallic=0.88),
    'gold_bright':   make_shader('M_GoldBright',    (1.00, 0.88, 0.35, 1.0), roughness=0.18, metallic=0.92),
    'crystal_cyan':  make_shader('M_CyanCrystal',   (0.00, 0.85, 1.00, 1.0), roughness=0.08, emission=9.0,  emission_color=(0.0, 0.85, 1.0, 1.0)),
    'crystal_core':  make_shader('M_CoreCyan',      (0.75, 0.98, 1.00, 1.0), roughness=0.04, emission=16.0, emission_color=(0.75, 0.98, 1.0, 1.0)),
    'violet_rune':   make_shader('M_VioletRune',    (0.72, 0.12, 0.95, 1.0), roughness=0.10, emission=8.0,  emission_color=(0.72, 0.12, 0.95, 1.0)),
    'string_energy': make_shader('M_EnergyString',  (0.88, 0.98, 1.00, 1.0), roughness=0.05, emission=14.0, emission_color=(0.8, 0.95, 1.0, 1.0)),
    'arrow_shaft':   make_shader('M_ArrowShaft',    (0.12, 0.10, 0.16, 1.0), roughness=0.35, metallic=0.5),
    'arrow_tip':     make_shader('M_ArrowTip',      (0.00, 0.92, 1.00, 1.0), roughness=0.08, emission=15.0, emission_color=(0.0, 0.92, 1.0, 1.0)),
    'arrow_feather': make_shader('M_ArrowFeather',  (0.85, 0.20, 1.00, 1.0), roughness=0.10, emission=8.0,  emission_color=(0.85, 0.2, 1.0, 1.0)),
    'pedestal':      make_shader('M_Pedestal',      (0.05, 0.07, 0.12, 1.0), roughness=0.30, metallic=0.4),
}

VOXEL_SIZE = 0.012  # 1.2 cm per micro-voxel

# 3. Mesher Helper
def create_voxel_mesh(name, voxels_dict):
    verts = []
    faces = []
    face_mats = []
    
    DIRECTIONS = [
        (( 1,  0,  0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
        ((-1,  0,  0), [(0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1)]),
        (( 0,  1,  0), [(1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)]),
        (( 0, -1,  0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
        (( 0,  0,  1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
        (( 0,  0, -1), [(0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)]),
    ]
    
    used_mat_names = sorted(list(set(voxels_dict.values())))
    mat_to_idx = {m: i for i, m in enumerate(used_mat_names)}
    vert_map = {}
    
    for (vx, vy, vz), mat_name in voxels_dict.items():
        slot = mat_to_idx[mat_name]
        for (dx, dy, dz), qverts in DIRECTIONS:
            neighbor = (vx + dx, vy + dy, vz + dz)
            if neighbor not in voxels_dict:
                quad = []
                for qx, qy, qz in qverts:
                    p = (
                        round((vx + qx) * VOXEL_SIZE, 6),
                        round((vy + qy) * VOXEL_SIZE, 6),
                        round((vz + qz) * VOXEL_SIZE, 6)
                    )
                    if p not in vert_map:
                        vert_map[p] = len(verts)
                        verts.append(p)
                    quad.append(vert_map[p])
                faces.append(quad)
                face_mats.append(slot)
                
    mesh = bpy.data.meshes.new(name=f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    for m in used_mat_names:
        mesh.materials.append(mats[m])
    for poly, slot in zip(mesh.polygons, face_mats):
        poly.material_index = slot
        
    mesh.polygons.foreach_set('use_smooth', [False] * len(mesh.polygons))
    mesh.update()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.dissolve_limited(angle_limit=0.0001)
    bpy.ops.mesh.tris_convert_to_quads()
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)
    
    return obj

print("Building Voxel Models...")

# -----------------------------------------------------------------------------
# 1. Complete Bow Frame (Single solid unified mesh with vertex groups)
# -----------------------------------------------------------------------------
bow_voxels = {}

# A. Central Grip / Riser (Z = -8 to +8)
for z in range(-8, 9):
    w = 2 if abs(z) <= 4 else 3
    d = 2 if abs(z) <= 4 else 3
    for x in range(-w, w + 1):
        for y in range(-d, d + 1):
            m = 'obsidian'
            if abs(x) == w or abs(y) == d:
                m = 'gold' if abs(z) in (0, 1, 7, 8) else 'navy_plate'
            # Astral Eye Gem at front
            if y == d and abs(z) <= 2 and abs(x) <= 1:
                m = 'crystal_core' if (x == 0 and z == 0) else 'crystal_cyan'
            bow_voxels[(x, y, z)] = m

# Astral Sigil Ring around Grip
for angle in range(0, 360, 12):
    rad = math.radians(angle)
    rx = int(round(math.cos(rad) * 7.5))
    ry = int(round(math.sin(rad) * 5.0))
    rz = int(round(math.sin(rad * 2.0) * 3.5))
    bow_voxels[(rx, ry, rz)] = 'crystal_cyan' if angle % 24 == 0 else 'violet_rune'

# B. Upper and Lower Recurve Limbs with Stepped Wings
# Upper limb: Z = 9 to 52. Lower limb: Z = -9 to -52.
# Tips at Z = +-52, Y = -14
TIP_Z = 52
TIP_Y = -14

for sign in (1, -1):
    for step in range(1, 45):
        t = step / 44.0
        # Recurve curve: arches forward slightly, then sweeps back to TIP_Y
        cy = int(round(math.sin(t * math.pi * 0.8) * 6.0 - (t ** 2.0) * 20.0))
        cz = sign * (8 + step)
        
        half_w = max(1, int(round(4.0 - t * 2.0)))
        half_d = max(1, int(round(3.5 - t * 1.8)))
        
        for x in range(-half_w, half_w + 1):
            for y in range(-half_d, half_d + 1):
                m = 'obsidian'
                if abs(x) == half_w:
                    m = 'gold' if step % 3 == 0 else 'navy_plate'
                if y == half_d:
                    m = 'gold'
                if x == 0 and (y == half_d or y == -half_d):
                    m = 'crystal_core' if step % 2 == 0 else 'crystal_cyan'
                bow_voxels[(x, cy + y, cz)] = m
                
        # Solid Stepped Wings / Dragon Fins (steps 10 to 34)
        if 10 <= step <= 34:
            wing_t = (step - 10) / 24.0
            wing_reach = int(round(math.sin(wing_t * math.pi) * 8.5))
            for side in (-1, 1):
                for k in range(1, wing_reach + 1):
                    wx = side * (half_w + k)
                    wy = cy - k // 2
                    wz = cz - sign * (k // 3)
                    for w_depth in (-1, 0):
                        if k == wing_reach:
                            mat_wing = 'gold_bright'
                        elif k >= wing_reach - 2:
                            mat_wing = 'crystal_cyan'
                        elif k >= wing_reach - 4:
                            mat_wing = 'crystal_core'
                        else:
                            mat_wing = 'violet_rune'
                        bow_voxels[(wx, wy + w_depth, wz)] = mat_wing

    # Tip Finials (steps 45 to 52)
    for tip_s in range(0, 8):
        tt = tip_s / 7.0
        tz = sign * (45 + tip_s)
        ty = int(round(-14.0 + tt * 3.0))
        for tx in (-1, 0, 1):
            for ty_off in (-1, 0, 1):
                bow_voxels[(tx, ty + ty_off, tz)] = 'gold'
                
    # String Anchor Gem at Tip
    for ox in (-1, 0, 1):
        for oy in (-1, 0, 1):
            for oz in (-1, 0, 1):
                bow_voxels[(ox, TIP_Y + oy, sign * TIP_Z + oz)] = 'crystal_core'

bow_obj = create_voxel_mesh("Magic_Bow", bow_voxels)

# -----------------------------------------------------------------------------
# 2. Skinned Bowstring
# -----------------------------------------------------------------------------
# Runs from upper tip (0, TIP_Y, TIP_Z) to lower tip (0, TIP_Y, -TIP_Z)
string_voxels = {}
for sz in range(-TIP_Z, TIP_Z + 1):
    string_voxels[(0, TIP_Y, sz)] = 'string_energy'

string_obj = create_voxel_mesh("Bowstring", string_voxels)

# -----------------------------------------------------------------------------
# 3. Prominent Magical Arrow
# -----------------------------------------------------------------------------
# Points along +Y (flight path). Nock sits at (0, TIP_Y, 0) in rest pose!
NOCK_Y = TIP_Y  # -14
arrow_voxels = {}

# Shaft: Y from NOCK_Y to NOCK_Y + 45 (length 45 voxels)
for y in range(NOCK_Y, NOCK_Y + 46):
    for x in (-1, 0):
        for z in (-1, 0):
            m = 'arrow_shaft'
            if (x + y + z) % 5 in (0, 1):
                m = 'crystal_cyan'  # Spiral luminous rune
            elif y % 8 == 0:
                m = 'gold'
            arrow_voxels[(x, y, z)] = m

# Large Diamond Crystal Arrowhead: Y from NOCK_Y + 46 to NOCK_Y + 68 (length 22 voxels)
HEAD_START = NOCK_Y + 46
for i in range(23):
    ay = HEAD_START + i
    t_head = i / 22.0
    if t_head < 0.35:
        w = int(round(t_head / 0.35 * 6.0))
    else:
        w = max(0, int(round(6.0 * (1.0 - (t_head - 0.35) / 0.65))))
        
    for ax in range(-w, w + 1):
        for az in range(-w, w + 1):
            if abs(ax) + abs(az) <= w + 1:
                m = 'arrow_tip'
                if ax == 0 and az == 0:
                    m = 'crystal_core'
                elif abs(ax) + abs(az) == w + 1:
                    m = 'gold' if i < 6 else 'arrow_tip'
                arrow_voxels[(ax, ay, az)] = m

# Tri-vane Crystal Fletchings at nock (Y = NOCK_Y to NOCK_Y + 11)
for fy in range(NOCK_Y, NOCK_Y + 12):
    f_step = fy - NOCK_Y
    span = int(round(math.sin(f_step / 11.0 * math.pi) * 7.5))
    for s in range(1, span + 1):
        m_fletch = 'gold' if s == span else ('arrow_feather' if s >= span - 2 else 'crystal_cyan')
        arrow_voxels[(0, fy, s)] = m_fletch
        arrow_voxels[(-int(round(s * 0.866)), fy, -int(round(s * 0.5)))] = m_fletch
        arrow_voxels[(int(round(s * 0.866)), fy, -int(round(s * 0.5)))] = m_fletch

arrow_obj = create_voxel_mesh("Magic_Arrow", arrow_voxels)

# -----------------------------------------------------------------------------
# 4. Cosmic Pedestal
# -----------------------------------------------------------------------------
base_voxels = {}
for bx in range(-32, 33):
    for by in range(-32, 33):
        dist = math.sqrt(bx*bx + by*by)
        if dist <= 31:
            for bz in (-2, -1, 0):
                m = 'pedestal'
                if bz == 0:
                    if int(dist) in (15, 30):
                        m = 'gold'
                    elif int(dist) % 5 == 0 and (bx % 3 == 0 or by % 3 == 0):
                        m = 'crystal_cyan'
                    elif dist <= 6:
                        m = 'violet_rune'
                else:
                    m = 'obsidian'
                base_voxels[(bx, by, bz)] = m

base_obj = create_voxel_mesh("Voxel_Pedestal", base_voxels)
base_obj.location.z = -62 * VOXEL_SIZE

# =============================================================================
# 5. SKELETON & RIGGING (Single unified Armature)
# =============================================================================
print("Constructing Armature...")

arm_data = bpy.data.armatures.new("Bow_Rig_Data")
arm_obj = bpy.data.objects.new("Bow_Rig", arm_data)
bpy.context.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj

bpy.ops.object.mode_set(mode='EDIT')

b_root = arm_data.edit_bones.new("Root")
b_root.head = (0, 0, 0)
b_root.tail = (0, 0, 0.1)

b_grip = arm_data.edit_bones.new("Grip")
b_grip.head = (0, 0, 0)
b_grip.tail = (0, 0, 0.1)
b_grip.parent = b_root

# Upper limb bone: head at upper grip joint (Z = 8 * VOXEL_SIZE), tail pointing along +Z
b_limb_u = arm_data.edit_bones.new("Limb_Upper")
b_limb_u.head = (0, 0, 8 * VOXEL_SIZE)
b_limb_u.tail = (0, 0, TIP_Z * VOXEL_SIZE)
b_limb_u.parent = b_grip

# Lower limb bone: head at lower grip joint (Z = -8 * VOXEL_SIZE), tail pointing along -Z
b_limb_l = arm_data.edit_bones.new("Limb_Lower")
b_limb_l.head = (0, 0, -8 * VOXEL_SIZE)
b_limb_l.tail = (0, 0, -TIP_Z * VOXEL_SIZE)
b_limb_l.parent = b_grip

# String nock bone: head at nock point (0, NOCK_Y * VOXEL_SIZE, 0), tail pointing along +Y
b_string_nock = arm_data.edit_bones.new("String_Nock")
b_string_nock.head = (0, NOCK_Y * VOXEL_SIZE, 0)
b_string_nock.tail = (0, (NOCK_Y + 10) * VOXEL_SIZE, 0)
b_string_nock.parent = b_root

# Arrow bone: head at nock point, tail pointing along +Y
b_arrow = arm_data.edit_bones.new("Arrow_Bone")
b_arrow.head = (0, NOCK_Y * VOXEL_SIZE, 0)
b_arrow.tail = (0, (NOCK_Y + 40) * VOXEL_SIZE, 0)
b_arrow.parent = b_root

bpy.ops.object.mode_set(mode='OBJECT')

# Skinning Bow Frame
bow_obj.parent = arm_obj
mod_bow = bow_obj.modifiers.new("Armature", 'ARMATURE')
mod_bow.object = arm_obj

vg_grip = bow_obj.vertex_groups.new(name="Grip")
vg_u = bow_obj.vertex_groups.new(name="Limb_Upper")
vg_l = bow_obj.vertex_groups.new(name="Limb_Lower")

for v in bow_obj.data.vertices:
    vz = v.co.z / VOXEL_SIZE
    if vz > 8.5:
        vg_u.add([v.index], 1.0, 'REPLACE')
    elif vz < -8.5:
        vg_l.add([v.index], 1.0, 'REPLACE')
    else:
        vg_grip.add([v.index], 1.0, 'REPLACE')

# Skinning Arrow
arrow_obj.parent = arm_obj
mod_arrow = arrow_obj.modifiers.new("Armature", 'ARMATURE')
mod_arrow.object = arm_obj
vg_arr = arrow_obj.vertex_groups.new(name="Arrow_Bone")
for v in arrow_obj.data.vertices:
    vg_arr.add([v.index], 1.0, 'REPLACE')

# Skinning Bowstring
string_obj.parent = arm_obj
mod_str = string_obj.modifiers.new("Armature", 'ARMATURE')
mod_str.object = arm_obj

vg_str_u = string_obj.vertex_groups.new(name="Limb_Upper")
vg_str_n = string_obj.vertex_groups.new(name="String_Nock")
vg_str_l = string_obj.vertex_groups.new(name="Limb_Lower")

for v in string_obj.data.vertices:
    vz = v.co.z / VOXEL_SIZE
    if vz >= 0:
        # Linear blend from nock (vz=0) to upper tip (vz=TIP_Z)
        weight_u = min(1.0, max(0.0, vz / float(TIP_Z)))
        weight_n = 1.0 - weight_u
        vg_str_u.add([v.index], weight_u, 'REPLACE')
        vg_str_n.add([v.index], weight_n, 'REPLACE')
    else:
        # Linear blend from nock (vz=0) to lower tip (vz=-TIP_Z)
        weight_l = min(1.0, max(0.0, -vz / float(TIP_Z)))
        weight_n = 1.0 - weight_l
        vg_str_l.add([v.index], weight_l, 'REPLACE')
        vg_str_n.add([v.index], weight_n, 'REPLACE')

# =============================================================================
# 6. SKELETAL ANIMATION: DRAW & SHOOT
# =============================================================================
print("Authoring 60-Frame Animation Action...")

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')

pose_nock = arm_obj.pose.bones["String_Nock"]
pose_arrow = arm_obj.pose.bones["Arrow_Bone"]
pose_limb_u = arm_obj.pose.bones["Limb_Upper"]
pose_limb_l = arm_obj.pose.bones["Limb_Lower"]

# Set rotation mode to Euler XYZ for clean predictability
for pb in (pose_nock, pose_arrow, pose_limb_u, pose_limb_l):
    pb.rotation_mode = 'XYZ'

def kf(pb, frame):
    pb.keyframe_insert(data_path="location", frame=frame)
    pb.keyframe_insert(data_path="rotation_euler", frame=frame)
    pb.keyframe_insert(data_path="scale", frame=frame)

DRAW_DIST = -0.32  # Draw string back 32 cm (-Y)

# Frames 1..10: Idle Floating
for f in (1, 10):
    pose_nock.location = (0, 0, 0)
    pose_arrow.location = (0, 0, 0)
    pose_arrow.scale = (1, 1, 1)
    pose_limb_u.rotation_euler = (0, 0, 0)
    pose_limb_l.rotation_euler = (0, 0, 0)
    for pb in (pose_nock, pose_arrow, pose_limb_u, pose_limb_l):
        kf(pb, f)

# Frame 34: PEAK DRAW TENSION
# String drawn back, arrow pulled, limbs flexing back
pose_nock.location = (0, DRAW_DIST, 0)
pose_arrow.location = (0, DRAW_DIST, 0)
pose_arrow.scale = (1, 1, 1)
pose_limb_u.rotation_euler = (math.radians(14), 0, 0)   # +14 deg bends upper tip back (-Y)
pose_limb_l.rotation_euler = (math.radians(-14), 0, 0)  # -14 deg bends lower tip back (-Y)
for pb in (pose_nock, pose_arrow, pose_limb_u, pose_limb_l):
    kf(pb, 34)

# Frame 35: INSTANTANEOUS SNAP RELEASE & RECOIL!
pose_nock.location = (0, 0.04, 0)
pose_limb_u.rotation_euler = (math.radians(-4), 0, 0)
pose_limb_l.rotation_euler = (math.radians(4), 0, 0)
pose_arrow.location = (0, 0.48, 0)
pose_arrow.scale = (1, 1.4, 1)  # High speed stretch
for pb in (pose_nock, pose_arrow, pose_limb_u, pose_limb_l):
    kf(pb, 35)

# Frame 38: STRING VIBRATION
pose_nock.location = (0, -0.02, 0)
pose_limb_u.rotation_euler = (math.radians(1.5), 0, 0)
pose_limb_l.rotation_euler = (math.radians(-1.5), 0, 0)
for pb in (pose_nock, pose_limb_u, pose_limb_l):
    kf(pb, 38)

# Frame 42: STRING SETTLES
pose_nock.location = (0, 0, 0)
pose_limb_u.rotation_euler = (0, 0, 0)
pose_limb_l.rotation_euler = (0, 0, 0)
for pb in (pose_nock, pose_limb_u, pose_limb_l):
    kf(pb, 42)

# Frame 48: ARROW ROCKETS INTO DISTANCE
pose_arrow.location = (0, 10.0, 0)
pose_arrow.scale = (0.01, 0.01, 0.01)
kf(pose_arrow, 48)

# Frame 53: ARROW REFORMS AT REST
pose_arrow.location = (0, 0, 0)
pose_arrow.scale = (0.01, 0.01, 0.01)
kf(pose_arrow, 53)

# Frame 60: COMPLETE LOOP READY FOR NEXT SHOT
pose_arrow.location = (0, 0, 0)
pose_arrow.scale = (1, 1, 1)
pose_nock.location = (0, 0, 0)
pose_limb_u.rotation_euler = (0, 0, 0)
pose_limb_l.rotation_euler = (0, 0, 0)
for pb in (pose_nock, pose_arrow, pose_limb_u, pose_limb_l):
    kf(pb, 60)

bpy.ops.object.mode_set(mode='OBJECT')

# =============================================================================
# 7. CYCLES BEAUTY SHOT (Frame 34 - Peak Draw)
# =============================================================================
scene.frame_set(34)
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

scene.cycles.samples = 96
scene.render.resolution_x = 1280
scene.render.resolution_y = 1280
scene.render.film_transparent = False

# Atmospheric World
world = bpy.data.worlds.new("Voxel_Studio_World")
world.use_nodes = True
bg_node = world.node_tree.nodes['Background']
bg_node.inputs['Color'].default_value = (0.03, 0.04, 0.07, 1.0)
bg_node.inputs['Strength'].default_value = 0.5
scene.world = world

scene.view_settings.view_transform = 'AgX' if hasattr(scene.view_settings, 'view_transform') else 'Filmic'
scene.view_settings.look = 'AgX - High Contrast'

# Lights
key_l = bpy.data.objects.new("Key_Sun", bpy.data.lights.new("Key_Sun", type='SUN'))
key_l.data.energy = 4.8
key_l.data.color = (1.0, 0.96, 0.90)
key_l.data.angle = math.radians(5)
key_l.rotation_euler = (math.radians(45), math.radians(25), math.radians(-30))
bpy.context.collection.objects.link(key_l)

rim_l = bpy.data.objects.new("Rim_Cyan", bpy.data.lights.new("Rim_Cyan", type='AREA'))
rim_l.data.energy = 360.0
rim_l.data.color = (0.0, 0.85, 1.0)
rim_l.data.size = 2.8
rim_l.location = (-2.2, 3.2, 1.2)
rim_l.rotation_euler = (math.radians(-55), math.radians(20), math.radians(145))
bpy.context.collection.objects.link(rim_l)

fill_l = bpy.data.objects.new("Fill_Violet", bpy.data.lights.new("Fill_Violet", type='AREA'))
fill_l.data.energy = 200.0
fill_l.data.color = (0.75, 0.20, 1.0)
fill_l.data.size = 3.2
fill_l.location = (2.8, -2.8, -0.6)
fill_l.rotation_euler = (math.radians(35), math.radians(-25), math.radians(-45))
bpy.context.collection.objects.link(fill_l)

# Camera Framing: Beautiful 3/4 angle showcasing drawn bow, flexed limbs, taut V string, and arrow
cam_data = bpy.data.cameras.new("Bow_Camera")
cam_data.lens = 68
cam_obj = bpy.data.objects.new("Bow_Camera", object_data=cam_data)
cam_obj.location = (2.2, -2.2, 0.5)

target_emp = bpy.data.objects.new("Target_Aim", None)
target_emp.location = (0, -0.05, 0.0)
bpy.context.collection.objects.link(target_emp)

track = cam_obj.constraints.new(type='TRACK_TO')
track.target = target_emp
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Export Paths
workspace_dir = os.path.abspath(os.path.dirname(__file__))
blend_file = os.path.join(workspace_dir, "celestial_magic_bow.blend")
glb_file = os.path.join(workspace_dir, "celestial_magic_bow.glb")
render_file = os.path.join(workspace_dir, "celestial_magic_bow_render.png")

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

print(f"Rendering frame 34 to {render_file}...")
scene.render.filepath = render_file
bpy.ops.render.render(write_still=True)

print("=================================================================")
print(">>> [SUCCESS] Celestial Magic Bow Rigged & Rendered!")
print("=================================================================")
