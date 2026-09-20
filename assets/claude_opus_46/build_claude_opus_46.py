import bpy
import math
import os

print("=================================================================")
print(">>> [ASTRAL VOXEL FORGE 1.0] Generating ClaudeOpus4.6 — Astral Scythe of the Void")
print("=================================================================")

# =============================================================================
# 1. Reset Scene
# =============================================================================
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 90
scene.render.fps = 30

# =============================================================================
# 2. Materials — Void Cosmic Palette
# =============================================================================
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
    # Core chassis — deep void obsidian
    'void_obsidian':    make_shader('M_VoidObsidian',    (0.03, 0.02, 0.06, 1.0), roughness=0.50, metallic=0.30),
    'void_dark':        make_shader('M_VoidDark',        (0.05, 0.03, 0.10, 1.0), roughness=0.45, metallic=0.25),
    # Metallic accents — astral silver & spectral gold
    'astral_silver':    make_shader('M_AstralSilver',    (0.60, 0.62, 0.68, 1.0), roughness=0.40, metallic=0.70),
    'spectral_gold':    make_shader('M_SpectralGold',    (0.85, 0.65, 0.20, 1.0), roughness=0.20, metallic=0.88),
    # Void energy — deep purple/violet (used heavily, keep low)
    'void_energy':      make_shader('M_VoidEnergy',      (0.50, 0.02, 0.80, 1.0), roughness=0.12, emission=1.2, emission_color=(0.50, 0.02, 0.80, 1.0)),
    'void_core':        make_shader('M_VoidCore',        (0.55, 0.08, 0.85, 1.0), roughness=0.10, emission=1.0, emission_color=(0.55, 0.08, 0.85, 1.0)),
    # Runic cyan glow
    'rune_cyan':        make_shader('M_RuneCyan',        (0.00, 0.55, 0.75, 1.0), roughness=0.12, emission=1.0, emission_color=(0.00, 0.55, 0.75, 1.0)),
    'rune_bright':      make_shader('M_RuneBright',      (0.10, 0.70, 0.88, 1.0), roughness=0.10, emission=1.2, emission_color=(0.10, 0.70, 0.88, 1.0)),
    # Vortex attack trail — restrained spectral
    'vortex_edge':      make_shader('M_VortexEdge',      (0.20, 0.00, 0.60, 1.0), roughness=0.12, emission=0.8, emission_color=(0.20, 0.00, 0.60, 1.0)),
    'vortex_core':      make_shader('M_VortexCore',      (0.55, 0.25, 0.85, 1.0), roughness=0.08, emission=1.0, emission_color=(0.55, 0.25, 0.85, 1.0)),
    'vortex_spark':     make_shader('M_VortexSpark',     (0.90, 0.80, 1.00, 1.0), roughness=0.06, emission=2.5, emission_color=(0.90, 0.80, 1.00, 1.0)),
    # Pedestal / base
    'pedestal':         make_shader('M_Pedestal',        (0.04, 0.03, 0.08, 1.0), roughness=0.30, metallic=0.40),
}

VOXEL_SIZE = 0.012  # 1.2 cm micro-voxel

# =============================================================================
# 3. Voxel Mesher
# =============================================================================
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

# =============================================================================
# 4. SCYTHE BODY — "Astral Scythe of the Void"
# =============================================================================
scythe_voxels = {}

# A. HAFT / SHAFT — Long pole along Z axis, from Z=-45 to Z=+30 (75 voxels ~0.9m)
# Cross-section: 3x3 core with beveled edges and runic channels
HAFT_BOT = -45
HAFT_TOP = 30

for z in range(HAFT_BOT, HAFT_TOP + 1):
    # Core shaft 3x3
    for x in range(-1, 2):
        for y in range(-1, 2):
            m = 'void_obsidian'
            # Gold accent bands every 8 voxels
            if z % 8 == 0:
                m = 'spectral_gold'
            # Silver edge ridges
            elif abs(x) == 1 and abs(y) == 1:
                m = 'astral_silver'
            # Runic glow channel along front face
            elif y == 1 and x == 0 and z % 4 == 0:
                m = 'rune_cyan'
            # Void energy spine along back
            elif y == -1 and x == 0 and z % 6 == 0:
                m = 'void_energy'
            scythe_voxels[(x, y, z)] = m

# B. GRIP WRAP — thicker section at Z=-10 to Z=+5 (player holds here)
for z in range(-10, 6):
    for x in range(-2, 3):
        for y in range(-2, 3):
            if abs(x) == 2 or abs(y) == 2:
                if abs(x) + abs(y) <= 3:  # Beveled corners
                    m = 'void_dark'
                    if z % 3 == 0:
                        m = 'spectral_gold'
                    scythe_voxels[(x, y, z)] = m
    # Grip gems
    if z % 5 == 0:
        scythe_voxels[(0, 2, z)] = 'void_core'
        scythe_voxels[(0, -2, z)] = 'rune_bright'

# C. POMMEL — Bottom cap Z=-45 to Z=-42, ornamental void crystal
for z in range(HAFT_BOT, HAFT_BOT + 4):
    t = (z - HAFT_BOT) / 3.0
    w = int(round(3.5 - t * 1.0))
    for x in range(-w, w + 1):
        for y in range(-w, w + 1):
            if abs(x) + abs(y) <= w + 1:
                m = 'void_dark'
                if abs(x) + abs(y) == w + 1:
                    m = 'spectral_gold'
                elif x == 0 and y == 0:
                    m = 'void_core'
                scythe_voxels[(x, y, z)] = m

# Pommel spike downwards Z=-46 to Z=-50
for z in range(HAFT_BOT - 5, HAFT_BOT):
    w = max(0, (z - (HAFT_BOT - 5)))  # Tapers from 0 to full
    for x in range(-1, 2):
        for y in range(-1, 2):
            if abs(x) <= w // 3 and abs(y) <= w // 3:
                continue  # Already filled
            m = 'void_energy' if (x + y + z) % 3 == 0 else 'astral_silver'
            scythe_voxels[(x, y, z)] = m

# D. NECK — Transition from shaft to blade, Z=+31 to Z=+38
for z in range(HAFT_TOP + 1, HAFT_TOP + 9):
    t = (z - HAFT_TOP - 1) / 7.0
    # Widens in Y (forward direction of blade curve)
    yw = int(round(1.5 + t * 3.5))
    xw = int(round(1.5 + t * 1.0))
    for x in range(-xw, xw + 1):
        for y in range(-1, yw + 1):
            m = 'void_obsidian'
            if abs(x) == xw:
                m = 'astral_silver'
            elif y == yw:
                m = 'spectral_gold'
            elif y == yw - 1 and x == 0:
                m = 'void_energy'
            scythe_voxels[(x, y, z)] = m

# E. BLADE — The massive curved scythe blade
# Curves from Z=+39 upwards and sweeps in +Y direction (forward) then curves down
# Total blade arc: ~50 voxels along the curve
BLADE_START_Z = HAFT_TOP + 9  # Z=39

for step in range(55):
    t = step / 54.0
    # Parametric scythe curve — rises then sweeps forward and down
    # Z rises initially, then curves
    bz = BLADE_START_Z + int(round(math.sin(t * math.pi * 0.7) * 28.0))
    # Y sweeps forward in a crescent
    by = int(round(t * 38.0 - (t ** 2.5) * 18.0))
    
    # Blade thickness — thick at base, thin at tip
    thickness_x = max(1, int(round(3.0 * (1.0 - t * 0.7))))
    # Blade height — the cutting edge extends perpendicular
    blade_height = max(1, int(round(8.0 * math.sin(t * math.pi * 0.85) * (1.0 - t * 0.3))))
    
    for x in range(-thickness_x, thickness_x + 1):
        for dy in range(-1, blade_height + 1):
            actual_y = by + dy
            m = 'void_obsidian'
            # Cutting edge — very tip only, sparse silver accent
            if dy == blade_height:
                m = 'void_dark'
                if step % 6 == 0:
                    m = 'astral_silver'
                if step % 10 == 0:
                    m = 'rune_cyan'  # Very rare runic glow on edge
            elif dy == blade_height - 1:
                m = 'void_obsidian'
            # Spine — back edge, dark with rare gold
            elif dy <= 0:
                m = 'void_dark'
                if step % 8 == 0:
                    m = 'spectral_gold'
            # Interior faces — dark
            elif abs(x) == thickness_x:
                m = 'void_dark'
            # Runic channels inside blade — very rare
            elif x == 0 and dy == blade_height // 2 and step % 10 == 0:
                m = 'void_energy'
            
            scythe_voxels[(x, actual_y, bz)] = m
    
    # Serrated void teeth on outer edge (every 5 steps in mid-blade)
    if 10 <= step <= 45 and step % 5 == 0:
        for tooth in range(1, 4):
            tx = 0
            ty = by + blade_height + tooth
            tz = bz + (1 if step % 10 == 0 else -1)
            m = 'vortex_spark' if tooth == 3 else 'void_energy'
            scythe_voxels[(tx, ty, tz)] = m

# F. BLADE TIP — Sharp curved hook
for tip_i in range(8):
    tt = tip_i / 7.0
    tz = BLADE_START_Z + int(round(math.sin(0.7 * math.pi * (54.0/54.0)) * 28.0)) - tip_i * 2
    ty = int(round(54.0/54.0 * 38.0 - ((54.0/54.0) ** 2.5) * 18.0)) + tip_i
    w = max(0, 2 - tip_i // 2)
    for x in range(-w, w + 1):
        for dy in range(-1, max(1, 3 - tip_i // 2)):
            m = 'vortex_core' if tip_i < 3 else 'void_energy'
            if x == 0 and dy == 0:
                m = 'vortex_spark'
            scythe_voxels[(x, ty + dy, tz)] = m

# G. ASTRAL EYE — Central eye jewel at blade junction
EYE_Z = BLADE_START_Z + 2
EYE_Y = 3
for ex in range(-3, 4):
    for ey in range(-3, 4):
        for ez in range(-3, 4):
            dist = math.sqrt(ex*ex + ey*ey + ez*ez)
            if dist <= 3.5:
                m = 'void_core'
                if dist <= 1.5:
                    m = 'vortex_spark'
                elif dist <= 2.5:
                    m = 'rune_bright'
                scythe_voxels[(ex, EYE_Y + ey, EYE_Z + ez)] = m

scythe_obj = create_voxel_mesh("Astral_Scythe", scythe_voxels)

# =============================================================================
# 5. RUNIC RING A — Inner ring orbiting the blade junction
# =============================================================================
ring_a_voxels = {}
RING_A_RADIUS = 12
RING_A_CX, RING_A_CY, RING_A_CZ = 0, EYE_Y, EYE_Z

for angle_deg in range(0, 360, 4):
    rad = math.radians(angle_deg)
    rx = int(round(math.cos(rad) * RING_A_RADIUS))
    rz = int(round(math.sin(rad) * RING_A_RADIUS))
    
    # Ring cross-section: 2x2 voxel thick
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if abs(dx) + abs(dy) <= 1:
                m = 'void_dark'
                # Runic glyphs — sparse, every 60 degrees
                if angle_deg % 60 == 0:
                    m = 'rune_cyan'
                elif angle_deg % 30 == 0:
                    m = 'astral_silver'
                # Silver structural every 7th segment
                elif (angle_deg // 4) % 7 == 0:
                    m = 'astral_silver'
                ring_a_voxels[(RING_A_CX + rx + dx, RING_A_CY + dy, RING_A_CZ + rz)] = m

ring_a_obj = create_voxel_mesh("Runic_Ring_A", ring_a_voxels)

# =============================================================================
# 6. RUNIC RING B — Outer ring, tilted, larger
# =============================================================================
ring_b_voxels = {}
RING_B_RADIUS = 18

for angle_deg in range(0, 360, 3):
    rad = math.radians(angle_deg)
    # Tilted ring — rotated 45 degrees around X axis
    ry_raw = math.cos(rad) * RING_B_RADIUS
    rz_raw = math.sin(rad) * RING_B_RADIUS
    # Apply 45-degree tilt around X
    tilt = math.radians(35)
    ry = int(round(ry_raw * math.cos(tilt) - rz_raw * math.sin(tilt)))
    rz = int(round(ry_raw * math.sin(tilt) + rz_raw * math.cos(tilt)))
    rx = int(round(math.sin(rad * 2) * 2.5))  # Slight wobble
    
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if abs(dx) + abs(dy) <= 1:
                m = 'void_obsidian'
                if angle_deg % 48 == 0:
                    m = 'rune_bright'
                elif angle_deg % 24 == 0:
                    m = 'astral_silver'
                elif angle_deg % 8 == 0:
                    m = 'spectral_gold'
                ring_b_voxels[(RING_A_CX + rx + dx, RING_A_CY + ry + dy, RING_A_CZ + rz)] = m

ring_b_obj = create_voxel_mesh("Runic_Ring_B", ring_b_voxels)

# =============================================================================
# 7. RUNIC RING C — Third ring, orthogonal plane
# =============================================================================
ring_c_voxels = {}
RING_C_RADIUS = 15

for angle_deg in range(0, 360, 4):
    rad = math.radians(angle_deg)
    # This ring orbits in XY plane (around Z-axis)
    rx = int(round(math.cos(rad) * RING_C_RADIUS))
    ry = int(round(math.sin(rad) * RING_C_RADIUS))
    
    for dz in range(-1, 2):
        for extra in range(-1, 2):
            if abs(dz) + abs(extra) <= 1:
                m = 'void_dark'
                if angle_deg % 72 == 0:
                    m = 'vortex_core'
                elif angle_deg % 36 == 0:
                    m = 'astral_silver'
                elif angle_deg % 9 == 0:
                    m = 'spectral_gold'
                ring_c_voxels[(RING_A_CX + rx + extra, RING_A_CY + ry, RING_A_CZ + dz)] = m

ring_c_obj = create_voxel_mesh("Runic_Ring_C", ring_c_voxels)

# =============================================================================
# 8. VORTEX ATTACK TRAIL — Circular slash wake
# =============================================================================
vortex_voxels = {}
VORTEX_RADIUS = 35
VORTEX_CZ = 10  # Centered near blade middle height

for angle_deg in range(0, 270, 2):  # 3/4 circle sweep
    rad = math.radians(angle_deg)
    vx = int(round(math.cos(rad) * VORTEX_RADIUS))
    vy = int(round(math.sin(rad) * VORTEX_RADIUS))
    
    # Trail gets thinner and more transparent toward the tail
    t = angle_deg / 270.0
    trail_w = max(1, int(round(4.0 * (1.0 - t * 0.6))))
    
    for dz in range(-trail_w, trail_w + 1):
        for dr in range(-2, 3):
            # Radial offset for trail thickness
            rx_off = int(round(math.cos(rad) * dr * 0.5))
            ry_off = int(round(math.sin(rad) * dr * 0.5))
            
            m = 'vortex_edge'
            if abs(dz) <= 1 and abs(dr) <= 1:
                m = 'vortex_core'
            if dz == 0 and dr == 0:
                m = 'vortex_spark' if angle_deg % 20 == 0 else 'vortex_core'
            
            # Only render if within density threshold (fade tail)
            if t > 0.7 and abs(dz) > trail_w // 2:
                continue
            
            vortex_voxels[(vx + rx_off, vy + ry_off, VORTEX_CZ + dz)] = m

# Vortex spark particles scattered along trail
for spark_i in range(30):
    sa = math.radians(spark_i * 9)
    sr = VORTEX_RADIUS + int(round(math.sin(spark_i * 2.3) * 6))
    sx = int(round(math.cos(sa) * sr))
    sy = int(round(math.sin(sa) * sr))
    sz = VORTEX_CZ + int(round(math.sin(spark_i * 1.7) * 5))
    vortex_voxels[(sx, sy, sz)] = 'vortex_spark'

vortex_obj = create_voxel_mesh("Vortex_Trail", vortex_voxels)

# =============================================================================
# 9. COSMIC PEDESTAL
# =============================================================================
base_voxels = {}
for bx in range(-28, 29):
    for by in range(-28, 29):
        dist = math.sqrt(bx*bx + by*by)
        if dist <= 27:
            for bz in (-2, -1, 0):
                m = 'pedestal'
                if bz == 0:
                    if int(dist) in (12, 25):
                        m = 'spectral_gold'
                    elif int(dist) % 6 == 0 and (bx % 4 == 0 or by % 4 == 0):
                        m = 'rune_cyan'
                    elif dist <= 5:
                        m = 'void_energy'
                else:
                    m = 'void_obsidian'
                base_voxels[(bx, by, bz)] = m

base_obj = create_voxel_mesh("Void_Pedestal", base_voxels)
base_obj.location.z = (HAFT_BOT - 8) * VOXEL_SIZE

# =============================================================================
# 10. SKELETON & RIGGING
# =============================================================================
print("Constructing Armature...")

arm_data = bpy.data.armatures.new("Scythe_Rig_Data")
arm_obj = bpy.data.objects.new("Scythe_Rig", arm_data)
bpy.context.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj

bpy.ops.object.mode_set(mode='EDIT')

# Root bone
b_root = arm_data.edit_bones.new("Root")
b_root.head = (0, 0, 0)
b_root.tail = (0, 0, 0.15)

# Scythe body bone — controls the main weapon rotation for vortex attack
b_body = arm_data.edit_bones.new("Scythe_Body")
b_body.head = (0, 0, 0)
b_body.tail = (0, 0, HAFT_TOP * VOXEL_SIZE)
b_body.parent = b_root

# Ring A bone — orbits around blade junction
b_ring_a = arm_data.edit_bones.new("Ring_A")
b_ring_a.head = (RING_A_CX * VOXEL_SIZE, RING_A_CY * VOXEL_SIZE, RING_A_CZ * VOXEL_SIZE)
b_ring_a.tail = (RING_A_CX * VOXEL_SIZE, RING_A_CY * VOXEL_SIZE, (RING_A_CZ + 8) * VOXEL_SIZE)
b_ring_a.parent = b_body

# Ring B bone
b_ring_b = arm_data.edit_bones.new("Ring_B")
b_ring_b.head = (RING_A_CX * VOXEL_SIZE, RING_A_CY * VOXEL_SIZE, RING_A_CZ * VOXEL_SIZE)
b_ring_b.tail = (RING_A_CX * VOXEL_SIZE, (RING_A_CY + 8) * VOXEL_SIZE, RING_A_CZ * VOXEL_SIZE)
b_ring_b.parent = b_body

# Ring C bone
b_ring_c = arm_data.edit_bones.new("Ring_C")
b_ring_c.head = (RING_A_CX * VOXEL_SIZE, RING_A_CY * VOXEL_SIZE, RING_A_CZ * VOXEL_SIZE)
b_ring_c.tail = ((RING_A_CX + 8) * VOXEL_SIZE, RING_A_CY * VOXEL_SIZE, RING_A_CZ * VOXEL_SIZE)
b_ring_c.parent = b_body

# Vortex bone — for the attack trail scaling
b_vortex = arm_data.edit_bones.new("Vortex_Trail")
b_vortex.head = (0, 0, VORTEX_CZ * VOXEL_SIZE)
b_vortex.tail = (0, 0, (VORTEX_CZ + 10) * VOXEL_SIZE)
b_vortex.parent = b_body

bpy.ops.object.mode_set(mode='OBJECT')

# --- Skin scythe body ---
scythe_obj.parent = arm_obj
mod_s = scythe_obj.modifiers.new("Armature", 'ARMATURE')
mod_s.object = arm_obj
vg_body = scythe_obj.vertex_groups.new(name="Scythe_Body")
for v in scythe_obj.data.vertices:
    vg_body.add([v.index], 1.0, 'REPLACE')

# --- Skin Ring A ---
ring_a_obj.parent = arm_obj
mod_ra = ring_a_obj.modifiers.new("Armature", 'ARMATURE')
mod_ra.object = arm_obj
vg_ra = ring_a_obj.vertex_groups.new(name="Ring_A")
for v in ring_a_obj.data.vertices:
    vg_ra.add([v.index], 1.0, 'REPLACE')

# --- Skin Ring B ---
ring_b_obj.parent = arm_obj
mod_rb = ring_b_obj.modifiers.new("Armature", 'ARMATURE')
mod_rb.object = arm_obj
vg_rb = ring_b_obj.vertex_groups.new(name="Ring_B")
for v in ring_b_obj.data.vertices:
    vg_rb.add([v.index], 1.0, 'REPLACE')

# --- Skin Ring C ---
ring_c_obj.parent = arm_obj
mod_rc = ring_c_obj.modifiers.new("Armature", 'ARMATURE')
mod_rc.object = arm_obj
vg_rc = ring_c_obj.vertex_groups.new(name="Ring_C")
for v in ring_c_obj.data.vertices:
    vg_rc.add([v.index], 1.0, 'REPLACE')

# --- Skin Vortex Trail ---
vortex_obj.parent = arm_obj
mod_vt = vortex_obj.modifiers.new("Armature", 'ARMATURE')
mod_vt.object = arm_obj
vg_vt = vortex_obj.vertex_groups.new(name="Vortex_Trail")
for v in vortex_obj.data.vertices:
    vg_vt.add([v.index], 1.0, 'REPLACE')

# =============================================================================
# 11. ANIMATION: IDLE HOVER + RUNIC RING SPIN + VORTEX ATTACK
# =============================================================================
print("Authoring 90-Frame Animation Action...")

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')

pose_body = arm_obj.pose.bones["Scythe_Body"]
pose_ring_a = arm_obj.pose.bones["Ring_A"]
pose_ring_b = arm_obj.pose.bones["Ring_B"]
pose_ring_c = arm_obj.pose.bones["Ring_C"]
pose_vortex = arm_obj.pose.bones["Vortex_Trail"]

# MANDATORY: Set rotation mode to Euler XYZ
for pb in (pose_body, pose_ring_a, pose_ring_b, pose_ring_c, pose_vortex):
    pb.rotation_mode = 'XYZ'

def kf(pb, frame):
    pb.keyframe_insert(data_path="location", frame=frame)
    pb.keyframe_insert(data_path="rotation_euler", frame=frame)
    pb.keyframe_insert(data_path="scale", frame=frame)

# --- Phase 1: IDLE HOVER with continuous ring rotation (Frames 1–30) ---
# Rings spin continuously. Vortex trail is hidden (scale 0).
for f in range(1, 31, 3):
    t = (f - 1) / 29.0
    
    # Scythe body: gentle hover bob
    pose_body.location = (0, 0, math.sin(t * math.pi * 2) * 0.015)
    pose_body.rotation_euler = (0, 0, math.sin(t * math.pi * 2) * math.radians(3))
    pose_body.scale = (1, 1, 1)
    kf(pose_body, f)
    
    # Ring A: continuous Z-axis spin
    pose_ring_a.rotation_euler = (0, 0, t * math.pi * 4)  # 2 full rotations in idle
    pose_ring_a.location = (0, 0, 0)
    pose_ring_a.scale = (1, 1, 1)
    kf(pose_ring_a, f)
    
    # Ring B: continuous X-axis spin (opposite direction)
    pose_ring_b.rotation_euler = (-t * math.pi * 3, 0, 0)  # 1.5 rotations
    pose_ring_b.location = (0, 0, 0)
    pose_ring_b.scale = (1, 1, 1)
    kf(pose_ring_b, f)
    
    # Ring C: continuous Y-axis spin
    pose_ring_c.rotation_euler = (0, t * math.pi * 2.5, 0)
    pose_ring_c.location = (0, 0, 0)
    pose_ring_c.scale = (1, 1, 1)
    kf(pose_ring_c, f)
    
    # Vortex: hidden
    pose_vortex.scale = (0.01, 0.01, 0.01)
    pose_vortex.location = (0, 0, 0)
    pose_vortex.rotation_euler = (0, 0, 0)
    kf(pose_vortex, f)

# --- Phase 2: WIND-UP (Frames 31–44) ---
# Scythe tilts back, rings accelerate, vortex begins to appear
for f in range(31, 45, 2):
    t = (f - 31) / 13.0
    
    # Body winds back
    pose_body.location = (0, 0, 0.02 + t * 0.04)
    pose_body.rotation_euler = (math.radians(-15 * t), 0, math.radians(-20 * t))
    pose_body.scale = (1, 1, 1)
    kf(pose_body, f)
    
    # Rings speed up — base rotation + acceleration
    base_a = math.pi * 4  # Where ring A ended at frame 30
    pose_ring_a.rotation_euler = (0, 0, base_a + t * math.pi * 3)
    pose_ring_a.scale = (1, 1, 1)
    kf(pose_ring_a, f)
    
    base_b = -math.pi * 3
    pose_ring_b.rotation_euler = (base_b - t * math.pi * 2.5, 0, 0)
    pose_ring_b.scale = (1, 1, 1)
    kf(pose_ring_b, f)
    
    base_c = math.pi * 2.5
    pose_ring_c.rotation_euler = (0, base_c + t * math.pi * 2, 0)
    pose_ring_c.scale = (1, 1, 1)
    kf(pose_ring_c, f)
    
    # Vortex starts appearing
    vort_scale = t * 0.3
    pose_vortex.scale = (vort_scale, vort_scale, vort_scale)
    pose_vortex.rotation_euler = (0, 0, t * math.pi * 0.5)
    kf(pose_vortex, f)

# --- Phase 3: VORTEX ATTACK SWING (Frames 45–65) ---
# Full circular slash! Body spins 360°, vortex at full scale, rings blur-speed
for f in range(45, 66, 2):
    t = (f - 45) / 20.0
    
    # Body performs full 360° spin attack!
    spin = math.pi * 2 * t  # Full rotation
    pose_body.location = (0, 0, 0.06 * math.sin(t * math.pi))  # Slight rise at peak
    pose_body.rotation_euler = (math.radians(-15 + 15 * t), 0, -math.radians(20) + spin)
    pose_body.scale = (1, 1, 1)
    kf(pose_body, f)
    
    # Rings at maximum speed
    ra_base = math.pi * 4 + math.pi * 3
    pose_ring_a.rotation_euler = (0, 0, ra_base + t * math.pi * 8)
    pose_ring_a.scale = (1.1, 1.1, 1.1)  # Slight expansion
    kf(pose_ring_a, f)
    
    rb_base = -math.pi * 3 - math.pi * 2.5
    pose_ring_b.rotation_euler = (rb_base - t * math.pi * 6, 0, 0)
    pose_ring_b.scale = (1.1, 1.1, 1.1)
    kf(pose_ring_b, f)
    
    rc_base = math.pi * 2.5 + math.pi * 2
    pose_ring_c.rotation_euler = (0, rc_base + t * math.pi * 7, 0)
    pose_ring_c.scale = (1.1, 1.1, 1.1)
    kf(pose_ring_c, f)
    
    # Vortex at full power
    vort_s = 0.3 + 0.7 * math.sin(t * math.pi)  # Peaks at midswing
    pose_vortex.scale = (vort_s, vort_s, vort_s)
    pose_vortex.rotation_euler = (0, 0, math.pi * 0.5 + t * math.pi * 2)  # Vortex spins with attack
    kf(pose_vortex, f)

# --- Phase 4: RECOVERY (Frames 66–90) ---
# Scythe returns to idle, vortex dissipates, rings decelerate
for f in range(66, 91, 3):
    t = (f - 66) / 24.0
    
    # Body settles back to idle
    pose_body.location = (0, 0, 0.02 * (1.0 - t) + math.sin(t * math.pi * 2) * 0.008 * t)
    pose_body.rotation_euler = (0, 0, math.pi * 2 * (1.0 - t * 0.3) if t < 0.5 else math.sin(t * math.pi * 2) * math.radians(3))
    pose_body.scale = (1, 1, 1)
    kf(pose_body, f)
    
    # Rings decelerate smoothly
    ra_end = math.pi * 4 + math.pi * 3 + math.pi * 8
    pose_ring_a.rotation_euler = (0, 0, ra_end + t * math.pi * 2 * (1.0 - t))
    pose_ring_a.scale = (1.0 + 0.1 * (1.0 - t), 1.0 + 0.1 * (1.0 - t), 1.0 + 0.1 * (1.0 - t))
    kf(pose_ring_a, f)
    
    rb_end = -math.pi * 3 - math.pi * 2.5 - math.pi * 6
    pose_ring_b.rotation_euler = (rb_end - t * math.pi * 1.5 * (1.0 - t), 0, 0)
    pose_ring_b.scale = (1.0 + 0.1 * (1.0 - t), 1.0 + 0.1 * (1.0 - t), 1.0 + 0.1 * (1.0 - t))
    kf(pose_ring_b, f)
    
    rc_end = math.pi * 2.5 + math.pi * 2 + math.pi * 7
    pose_ring_c.rotation_euler = (0, rc_end + t * math.pi * 1.8 * (1.0 - t), 0)
    pose_ring_c.scale = (1.0 + 0.1 * (1.0 - t), 1.0 + 0.1 * (1.0 - t), 1.0 + 0.1 * (1.0 - t))
    kf(pose_ring_c, f)
    
    # Vortex fades out
    vort_fade = max(0.01, (1.0 - t) * 0.3)
    pose_vortex.scale = (vort_fade, vort_fade, vort_fade)
    pose_vortex.rotation_euler = (0, 0, math.pi * 2.5 + t * math.pi * 0.5)
    kf(pose_vortex, f)

bpy.ops.object.mode_set(mode='OBJECT')

# =============================================================================
# 12. CYCLES BEAUTY SHOT — Peak vortex attack frame
# =============================================================================
RENDER_FRAME = 25  # Idle hover with spinning rings — clean beauty shot
scene.frame_set(RENDER_FRAME)
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

# Atmospheric World — deep void space
world = bpy.data.worlds.new("Void_Studio_World")
world.use_nodes = True
bg_node = world.node_tree.nodes['Background']
bg_node.inputs['Color'].default_value = (0.015, 0.01, 0.035, 1.0)
bg_node.inputs['Strength'].default_value = 0.4
scene.world = world

scene.view_settings.view_transform = 'AgX' if hasattr(scene.view_settings, 'view_transform') else 'Filmic'
try:
    scene.view_settings.look = 'AgX - High Contrast'
except:
    pass

# --- Compute automatic camera framing ---
all_voxel_sets = [scythe_voxels, ring_a_voxels, ring_b_voxels, ring_c_voxels, vortex_voxels]
all_xs, all_ys, all_zs = [], [], []
for vset in all_voxel_sets:
    for (vx, vy, vz) in vset.keys():
        all_xs.append(vx * VOXEL_SIZE)
        all_ys.append(vy * VOXEL_SIZE)
        all_zs.append(vz * VOXEL_SIZE)

center = (
    (min(all_xs) + max(all_xs)) / 2.0,
    (min(all_ys) + max(all_ys)) / 2.0,
    (min(all_zs) + max(all_zs)) / 2.0
)
span = max(max(all_xs) - min(all_xs), max(all_ys) - min(all_ys), max(all_zs) - min(all_zs), 0.5)

# Camera
cam_data = bpy.data.cameras.new("Scythe_Camera")
cam_data.lens = 55
cam_obj = bpy.data.objects.new("Scythe_Camera", object_data=cam_data)
cam_obj.location = (center[0] + span * 1.3, center[1] - span * 1.6, center[2] + span * 0.7)
bpy.context.collection.objects.link(cam_obj)

target_emp = bpy.data.objects.new("CamTarget", None)
target_emp.location = center
bpy.context.collection.objects.link(target_emp)

track = cam_obj.constraints.new(type='TRACK_TO')
track.target = target_emp
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

scene.camera = cam_obj

# 3-Point Lighting
key_l = bpy.data.objects.new("Key_Sun", bpy.data.lights.new("Key_Sun", type='SUN'))
key_l.data.energy = 3.5
key_l.data.color = (0.95, 0.90, 1.00)  # Cool white with hint of violet
key_l.data.angle = math.radians(5)
key_l.rotation_euler = (math.radians(48), math.radians(20), math.radians(-35))
bpy.context.collection.objects.link(key_l)

rim_l = bpy.data.objects.new("Rim_Void", bpy.data.lights.new("Rim_Void", type='AREA'))
rim_l.data.energy = 80.0
rim_l.data.color = (0.60, 0.10, 1.0)  # Deep violet rim
rim_l.data.size = 3.0
rim_l.location = (-2.5, 3.5, 1.5)
rim_l.rotation_euler = (math.radians(-50), math.radians(20), math.radians(150))
bpy.context.collection.objects.link(rim_l)

fill_l = bpy.data.objects.new("Fill_Cyan", bpy.data.lights.new("Fill_Cyan", type='AREA'))
fill_l.data.energy = 60.0
fill_l.data.color = (0.0, 0.85, 1.0)  # Cyan fill
fill_l.data.size = 3.5
fill_l.location = (3.0, -3.0, -0.8)
fill_l.rotation_euler = (math.radians(30), math.radians(-30), math.radians(-40))
bpy.context.collection.objects.link(fill_l)

# =============================================================================
# 13. EXPORT
# =============================================================================
workspace_dir = os.path.abspath(os.path.dirname(__file__))
blend_file = os.path.join(workspace_dir, "claude_opus_46.blend")
glb_file = os.path.join(workspace_dir, "claude_opus_46.glb")
render_file = os.path.join(workspace_dir, "claude_opus_46_render.png")

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

print(f"Rendering frame {RENDER_FRAME} to {render_file}...")
scene.render.filepath = render_file
bpy.ops.render.render(write_still=True)

print("=================================================================")
print(">>> [SUCCESS] ClaudeOpus4.6 — Astral Scythe of the Void — Complete!")
print("=================================================================")
