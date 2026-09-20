import bpy
import math
import os
import base64

print("=================================================================")
print(">>> [TROVE VOXEL ARTISAN] Astral Void Scythe «Gemini3.7» (v2.0)")
print(">>> Enhanced: Majestic Blade Silhouette, Gyro-Rings & Volumetric Vortex")
print("=================================================================")

# -----------------------------------------------------------------
# 1. Reset Scene & General Setup
# -----------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 60
scene.render.fps = 30

VOXEL_SIZE = 0.012  # 1.2 cm micro-voxel scale per specification

# -----------------------------------------------------------------
# 2. Shader & Materials Definition (AgX Safe Palette)
# -----------------------------------------------------------------
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
            bsdf.inputs['Emission'].default_value = ec
            
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

mats = {
    # Shaft & Hardware Materials
    'void_obsidian':       make_shader('M_VoidObsidian',       (0.08, 0.07, 0.11, 1.0), roughness=0.22, metallic=0.88),
    'void_obsidian_dark':  make_shader('M_VoidObsidianDark',   (0.04, 0.03, 0.06, 1.0), roughness=0.30, metallic=0.85),
    'astral_platinum':     make_shader('M_AstralPlatinum',     (0.88, 0.90, 0.98, 1.0), roughness=0.10, metallic=0.96),
    'cosmic_gold':         make_shader('M_CosmicGold',         (0.96, 0.80, 0.24, 1.0), roughness=0.14, metallic=0.94),
    'void_grip':           make_shader('M_VoidGrip',           (0.14, 0.10, 0.20, 1.0), roughness=0.75, metallic=0.15),
    'void_grip_knot':      make_shader('M_VoidGripKnot',      (0.24, 0.16, 0.34, 1.0), roughness=0.65, metallic=0.20),
    
    # Scythe Blade & Socket Materials
    'void_spine':          make_shader('M_VoidSpine',          (0.14, 0.10, 0.22, 1.0), roughness=0.16, metallic=0.92),
    'astral_nebula':       make_shader('M_AstralNebula',       (0.42, 0.14, 0.65, 1.0), roughness=0.18, metallic=0.55),
    'astral_nebula_deep':  make_shader('M_AstralNebulaDeep',   (0.25, 0.08, 0.40, 1.0), roughness=0.22, metallic=0.50),
    'astral_plasma_edge':  make_shader('M_AstralPlasmaEdge',   (0.00, 0.90, 1.00, 1.0), roughness=0.04, metallic=0.10, emission=2.2, emission_color=(0.00, 0.95, 1.00, 1.0)),
    'astral_plasma_violet':make_shader('M_AstralPlasmaViolet', (0.80, 0.18, 1.00, 1.0), roughness=0.05, metallic=0.10, emission=2.2, emission_color=(0.85, 0.22, 1.00, 1.0)),
    
    # Astral Eye Core & Runic Gyro-Rings
    'void_core_eye':       make_shader('M_VoidCoreEye',        (0.90, 0.22, 1.00, 1.0), roughness=0.04, metallic=0.05, emission=2.5, emission_color=(0.95, 0.28, 1.00, 1.0)),
    'void_core_inner':     make_shader('M_VoidCoreInner',      (0.98, 0.96, 1.00, 1.0), roughness=0.02, metallic=0.02, emission=3.5, emission_color=(0.98, 0.96, 1.00, 1.0)),
    'rune_glyph_cyan':     make_shader('M_RuneGlyphCyan',      (0.00, 0.92, 1.00, 1.0), roughness=0.06, metallic=0.10, emission=2.4, emission_color=(0.00, 0.96, 1.00, 1.0)),
    'rune_glyph_purple':   make_shader('M_RuneGlyphPurple',    (0.85, 0.20, 1.00, 1.0), roughness=0.06, metallic=0.10, emission=2.4, emission_color=(0.90, 0.25, 1.00, 1.0)),
    'rune_ring_chassis':   make_shader('M_RuneRingChassis',    (0.95, 0.78, 0.22, 1.0), roughness=0.14, metallic=0.95),
    
    # Volumetric Circular Vortex Whirlwind Materials
    'vortex_core_white':   make_shader('M_VortexCoreWhite',    (0.98, 0.97, 1.00, 1.0), roughness=0.04, metallic=0.02, emission=2.8, emission_color=(0.98, 0.97, 1.00, 1.0)),
    'vortex_void_purple':  make_shader('M_VortexVoidPurple',   (0.78, 0.12, 1.00, 1.0), roughness=0.08, metallic=0.05, emission=2.2, emission_color=(0.82, 0.16, 1.00, 1.0)),
    'vortex_astral_cyan':  make_shader('M_VortexAstralCyan',   (0.00, 0.88, 1.00, 1.0), roughness=0.06, metallic=0.05, emission=2.1, emission_color=(0.00, 0.92, 1.00, 1.0)),
    'vortex_spark':        make_shader('M_VortexSpark',        (0.50, 0.95, 1.00, 1.0), roughness=0.04, metallic=0.05, emission=2.5, emission_color=(0.60, 0.98, 1.00, 1.0)),
}

# -----------------------------------------------------------------
# 3. Micro-Voxel Model Generation
# -----------------------------------------------------------------
voxels = {}

def set_vox(x, y, z, mat, bone, overwrite=False):
    k = (int(round(x)), int(round(y)), int(round(z)))
    if not overwrite and k in voxels:
        return
    voxels[k] = (mat, bone)

print(">>> [1/5] Building Astral Void Shaft & Star Pommel...")

# 3.1 Star-Spiked Pommel (z = -56 to -40)
for z in range(-56, -40):
    t = (z - (-56)) / 16.0
    rad = 1.0 + t * 2.5
    for x in range(-4, 5):
        for y in range(-4, 5):
            d2 = x*x + y*y
            if d2 <= rad*rad:
                if z in (-56, -55, -54):
                    m = 'astral_platinum' if (abs(x) == abs(y)) else 'void_obsidian_dark'
                elif z in (-44, -43):
                    m = 'cosmic_gold' if (abs(x) >= 2 or abs(y) >= 2) else 'void_obsidian'
                else:
                    m = 'astral_plasma_violet' if (x == 0 and y == 0) else 'void_obsidian'
                set_vox(x, y, z, m, 'Shaft_Bone', True)

# 4 Flanged Star Blades on Pommel
for z in range(-52, -43):
    for fl in range(2, 7):
        set_vox( fl, 0, z, 'astral_platinum', 'Shaft_Bone', True)
        set_vox(-fl, 0, z, 'astral_platinum', 'Shaft_Bone', True)
        set_vox(0,  fl, z, 'astral_platinum', 'Shaft_Bone', True)
        set_vox(0, -fl, z, 'astral_platinum', 'Shaft_Bone', True)
        if fl >= 4:
            set_vox( fl, 0, z, 'astral_plasma_edge', 'Shaft_Bone', True)
            set_vox(-fl, 0, z, 'astral_plasma_edge', 'Shaft_Bone', True)
            set_vox(0,  fl, z, 'astral_plasma_edge', 'Shaft_Bone', True)
            set_vox(0, -fl, z, 'astral_plasma_edge', 'Shaft_Bone', True)

# 3.2 Long Void Shaft with Twisted Platinum Ribs & Silk Wrap (z = -40 to +58)
for z in range(-40, 58):
    is_grip_zone = (-20 <= z <= 24)
    twist_angle = (z * 0.35) % (2.0 * math.pi)
    
    for x in range(-2, 3):
        for y in range(-2, 3):
            if abs(x) == 2 and abs(y) == 2:
                continue  # rounded corner
            
            if is_grip_zone:
                wrap_diag = (x + y + z) % 4
                if abs(x) == 2 or abs(y) == 2:
                    m = 'void_grip_knot' if wrap_diag == 0 else 'void_grip'
                else:
                    m = 'void_obsidian_dark'
            else:
                m = 'void_obsidian'
            
            # Gold bands every 16 voxels
            if z in (-40, -22, 26, 42, 54):
                if abs(x) == 2 or abs(y) == 2:
                    m = 'cosmic_gold'
            
            # Platinum fluted spiral ribs on non-grip sections
            if not is_grip_zone:
                rib_x = math.cos(twist_angle) * 1.8
                rib_y = math.sin(twist_angle) * 1.8
                if math.hypot(x - rib_x, y - rib_y) < 0.9 or math.hypot(x + rib_x, y + rib_y) < 0.9:
                    m = 'astral_platinum'
            
            set_vox(x, y, z, m, 'Shaft_Bone', True)

print(">>> [2/5] Building Astral Socket, Void Horns & Astral Eye Core...")

# 3.3 Socket & Junction (z = 55 to 72, y = -2 to 16)
for z in range(55, 73):
    dz = z - 55
    y_center = dz * 0.45
    for x in range(-3, 4):
        for y in range(-3, 16):
            dy = y - y_center
            if (x*x)/10.0 + (dy*dy)/30.0 <= 1.0:
                if abs(x) == 3 or y >= 12 or y <= -2:
                    m = 'astral_platinum' if z % 2 == 0 else 'void_obsidian'
                elif z >= 70 or z == 55:
                    m = 'cosmic_gold'
                else:
                    m = 'void_obsidian'
                set_vox(x, y, z, m, 'Shaft_Bone', True)

# Astral Back-Thorn / Horn (y = 8 to 22, z = 62 to 86)
for t_idx in range(26):
    u = t_idx / 25.0
    hz = 60 + u * 26
    hy = 8 + math.sin(u * 1.8) * 14
    thick = int(round((1.0 - u) * 2.8))
    for x in range(-thick, thick + 1):
        for y in range(int(hy - thick), int(hy + thick + 1)):
            for z in range(int(hz - 1), int(hz + 2)):
                if abs(x) == thick or y == int(hy + thick):
                    m = 'astral_platinum'
                else:
                    m = 'void_spine'
                set_vox(x, y, z, m, 'Shaft_Bone', True)
    if t_idx >= 22:
        set_vox(0, int(hy), int(hz), 'astral_plasma_violet', 'Shaft_Bone', True)

# Astral Eye Core (Diamond Octahedron at x=0, y=5, z=63) rigged to Core_Bone
cx, cy, cz = 0, 5, 63
for dx in range(-5, 6):
    for dy in range(-5, 6):
        for dz in range(-6, 7):
            manhattan = abs(dx) + abs(dy) + abs(dz) * 0.85
            if manhattan <= 4.2:
                if manhattan <= 1.5:
                    m = 'void_core_inner'
                elif manhattan <= 2.8:
                    m = 'void_core_eye'
                elif manhattan <= 3.8:
                    m = 'astral_plasma_violet'
                else:
                    m = 'cosmic_gold' if (dx + dy + dz) % 2 == 0 else 'astral_platinum'
                set_vox(cx + dx, cy + dy, cz + dz, m, 'Core_Bone', True)

print(">>> [3/5] Building Massive Curved Astral Void Scythe Blade...")

# 3.4 Imposing Curved Crescent Scythe Blade
# Starts at socket (0, 7, 65) -> sweeps forward to (0, -32, 52) -> hooks down to (0, -48, 18) -> tip at (0, -44, -2)
blade_points = []
N_BLADE = 95
for i in range(N_BLADE):
    u = i / float(N_BLADE - 1)
    
    # Cubic Bezier curve for spine
    by = (1-u)**3 * 7.0 + 3*(1-u)**2*u * (-16.0) + 3*(1-u)*u**2 * (-56.0) + u**3 * (-44.0)
    bz = (1-u)**3 * 65.0 + 3*(1-u)**2*u * 76.0 + 3*(1-u)*u**2 * 38.0 + u**3 * (-2.0)
    
    # Broad blade width (expanding to 16-18 voxels at belly!)
    b_width = math.sin(u * math.pi) * 16.0 + (1.0 - u) * 4.0 + 1.5
    
    # Volumetric spine thickness: 4-5 voxels at root, tapering to 2 voxels near tip
    spine_thick = max(1, int(round((1.0 - u * 0.65) * 2.4)))
    
    blade_points.append((by, bz, b_width, spine_thick, u))

for bp in blade_points:
    by, bz, b_width, spine_thick, u = bp
    
    # Perpendicular vector pointing inward towards center of crook
    edge_dir_y = math.sin(u * 2.3 + 0.35)
    edge_dir_z = -math.cos(u * 2.3 + 0.35)
    ed_len = math.hypot(edge_dir_y, edge_dir_z)
    if ed_len > 1e-4:
        edge_dir_y /= ed_len
        edge_dir_z /= ed_len
    
    w_steps = int(math.ceil(b_width))
    for w in range(w_steps + 1):
        fw = w / float(max(1, w_steps))  # 0 at spine, 1 at edge
        
        vy = by + edge_dir_y * w
        vz = bz + edge_dir_z * w
        
        curr_thick = max(0, int(round(spine_thick * (1.0 - fw * 0.85))))
        
        for x in range(-curr_thick, curr_thick + 1):
            if w == 0:
                if abs(x) == curr_thick and int(round(bz)) % 4 == 0:
                    m = 'cosmic_gold'
                elif abs(x) == curr_thick:
                    m = 'astral_platinum'
                else:
                    m = 'void_spine'
            elif w == 1 and curr_thick >= 1:
                m = 'astral_nebula_deep'
            elif fw < 0.70:
                if (int(vy) + int(vz)) % 5 == 0 and x == 0:
                    m = 'astral_plasma_violet'
                else:
                    m = 'astral_nebula'
            elif fw < 0.90:
                m = 'astral_plasma_violet'
            else:
                m = 'astral_plasma_edge'
                
            set_vox(x, vy, vz, m, 'Blade_Bone', True)

# Serrated Astral Crystal Spikes along Scythe Spine & Inner Crook
for tooth_idx in range(10):
    tu = 0.20 + (tooth_idx / 9.0) * 0.65
    by, bz, b_width, _, _ = blade_points[int(tu * (N_BLADE - 1))]
    # Spine spikes
    for h in range(1, 4):
        set_vox(0, by - 1.0 * h, bz + 1.2 * h, 'astral_platinum', 'Blade_Bone', True)
        if h == 3:
            set_vox(0, by - 1.0 * h, bz + 1.2 * h, 'cosmic_gold', 'Blade_Bone', True)
    # Inner crook teeth
    for h in range(1, 4):
        set_vox(0, by + 1.4 * h, bz - 1.2 * h, 'astral_plasma_edge', 'Blade_Bone', True)

print(">>> [4/5] Building Rotating Runic Gyro-Rings...")

# 3.5 Rotating Runic Rings
# Ring 1: Inner Gyroscopic Runic Ring (radius = 11 voxels, centered at socket 0, 5, 63)
R1_RAD = 11.0
for deg in range(0, 360, 5):
    rad = math.radians(deg)
    rx = math.cos(rad) * R1_RAD
    ry = math.sin(rad) * R1_RAD
    
    is_rune_node = (deg % 90 == 0)
    is_minor_node = (deg % 45 == 0)
    
    for z_off in (-1, 0, 1):
        for r_off in (-0.7, 0.7):
            px = math.cos(rad) * (R1_RAD + r_off)
            py = math.sin(rad) * (R1_RAD + r_off)
            
            if is_rune_node and z_off == 0:
                m = 'rune_glyph_cyan'
            elif is_minor_node and z_off == 0:
                m = 'rune_glyph_purple'
            elif z_off == 0:
                m = 'rune_ring_chassis'
            else:
                m = 'astral_platinum'
            
            set_vox(px, 5 + py, 63 + z_off, m, 'Rune_Ring_Inner', True)

# Ring 2: Outer Constellation Runic Ring (radius = 18 voxels, centered at upper shaft 0, 0, 48)
R2_RAD = 18.0
for deg in range(0, 360, 4):
    rad = math.radians(deg)
    rz = math.sin(rad * 2.0) * 3.5
    
    is_rune_star = (deg % 60 == 0)
    is_sub_star = (deg % 30 == 0)
    
    for th in (-1, 0, 1):
        for r_off in (-0.6, 0.6):
            px = math.cos(rad) * (R2_RAD + r_off)
            py = math.sin(rad) * (R2_RAD + r_off)
            pz = 48 + rz + th*0.6
            
            if is_rune_star and th == 0:
                m = 'rune_glyph_cyan'
            elif is_sub_star and th == 0:
                m = 'rune_glyph_purple'
            elif th == 0:
                m = 'rune_ring_chassis'
            else:
                m = 'cosmic_gold' if deg % 20 == 0 else 'astral_platinum'
            
            set_vox(px, py, pz, m, 'Rune_Ring_Outer', True)

print(">>> [5/5] Building Volumetric 360° Circular Vortex Whirlwind Effect...")

# 3.6 Dense, Volumetric Multi-Blade Cyclone Disc (Rigged to Vortex_Trail_Bone)
# Built as 4 massive sweeping helical crescent blades forming a continuous cosmic accretion disk!
N_VORTEX_BLADES = 4
N_STEPS = 100

for b_idx in range(N_VORTEX_BLADES):
    blade_angle_offset = (b_idx / float(N_VORTEX_BLADES)) * (2.0 * math.pi)
    
    for st in range(N_STEPS):
        u = st / float(N_STEPS - 1)  # 0 at center, 1 at tip
        
        # Spiral radius: 8 to 46 voxels (~1.15m whirlwind radius, ~2.3m diameter!)
        rad = 8.0 + u * 38.0
        # Angle sweeps 220 degrees along each crescent blade
        ang = blade_angle_offset + u * (math.pi * 1.35)
        
        # Helical dome lift
        vz = 45.0 + math.sin(u * math.pi) * 6.0 - u * 3.0
        
        # Center of ribbon
        cx_v = math.cos(ang) * rad
        cy_v = math.sin(ang) * rad
        
        # Solid volumetric width (thick crescent blade width: up to 7-8 voxels!)
        w_span = math.sin(u * math.pi) * 6.5 + 2.0
        
        perp_ang = ang + math.pi * 0.5
        
        w_count = int(math.ceil(w_span))
        for w in range(-w_count // 2, w_count // 2 + 1):
            fw = (w + w_span * 0.5) / max(1.0, w_span)  # 0 to 1 across width
            
            px = cx_v + math.cos(perp_ang) * w
            py = cy_v + math.sin(perp_ang) * w
            
            # 2 to 3 vertical layers for volumetric mass
            for z_lay in (-1, 0, 1):
                pz = vz + z_lay * 0.85
                
                # Material layering:
                if u < 0.20 and abs(w) <= 1:
                    # White-hot plasma core
                    m = 'vortex_core_white'
                elif fw < 0.35:
                    # Void purple storm
                    m = 'vortex_void_purple'
                elif fw < 0.75:
                    # Translucent astral nebula
                    m = 'astral_nebula'
                else:
                    # Glowing cyan cutting shockwave
                    m = 'vortex_astral_cyan'
                
                set_vox(px, py, pz, m, 'Vortex_Trail_Bone', True)

# Orbiting Cosmic Shockwave Runes & Particle Sparks
for sp_idx in range(60):
    sp_u = sp_idx / 60.0
    sp_rad = 22.0 + sp_u * 26.0
    sp_ang = sp_u * (4.0 * math.pi)
    sx = math.cos(sp_ang) * sp_rad
    sy = math.sin(sp_ang) * sp_rad
    sz = 45.0 + math.sin(sp_u * 8.0) * 5.0
    m_sp = 'vortex_spark' if sp_idx % 2 == 0 else 'rune_glyph_cyan'
    set_vox(sx, sy, sz, m_sp, 'Vortex_Burst_Bone', True)

print(f">>> Total Generated Micro-Voxels: {len(voxels)} voxels.")

# -----------------------------------------------------------------
# 4. Algorithmic Boundary Quad Mesher & Optimization
# -----------------------------------------------------------------
print(">>> Meshing exposed boundary quads with material slots...")

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
        if neighbor not in voxels:
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

print(f">>> Constructing Scythe Mesh: {len(verts)} vertices, {len(faces)} faces...")
mesh = bpy.data.meshes.new("Gemini37_Scythe_Mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

for m in used_mat_names:
    mesh.materials.append(mats[m])
for poly, slot in zip(mesh.polygons, face_mats):
    poly.material_index = slot

# Strict flat shading
mesh.polygons.foreach_set('use_smooth', [False] * len(mesh.polygons))
mesh.update()

scythe_obj = bpy.data.objects.new("Gemini37_Scythe", mesh)
bpy.context.collection.objects.link(scythe_obj)

# Optimize planar faces
bpy.context.view_layer.objects.active = scythe_obj
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.dissolve_limited(angle_limit=0.0001)
bpy.ops.mesh.tris_convert_to_quads()
bpy.ops.object.mode_set(mode='OBJECT')

print(f">>> Mesh Optimized: {len(scythe_obj.data.vertices)} vertices, {len(scythe_obj.data.polygons)} polygons.")

# -----------------------------------------------------------------
# 5. Skeletal Rigging & Armature Setup
# -----------------------------------------------------------------
print(">>> Building Armature & Rigging Hierarchy...")
arm_data = bpy.data.armatures.new("Gemini37_Armature_Data")
arm_obj = bpy.data.objects.new("Gemini37_Armature", arm_data)
bpy.context.collection.objects.link(arm_obj)

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones

# 1) Root Bone
bone_root = eb.new("Root")
bone_root.head = (0, 0, 0)
bone_root.tail = (0, 0.10, 0)

# 2) Shaft Bone
bone_shaft = eb.new("Shaft_Bone")
bone_shaft.parent = bone_root
bone_shaft.head = (0, 0, 0)
bone_shaft.tail = (0, 0, 0.5)

# 3) Core Bone (Astral Eye Socket)
bone_core = eb.new("Core_Bone")
bone_core.parent = bone_shaft
bone_core.head = (0, 5 * VOXEL_SIZE, 63 * VOXEL_SIZE)
bone_core.tail = (0, 5 * VOXEL_SIZE, 70 * VOXEL_SIZE)

# 4) Blade Bone (Massive Scythe Blade)
bone_blade = eb.new("Blade_Bone")
bone_blade.parent = bone_shaft
bone_blade.head = (0, 5 * VOXEL_SIZE, 63 * VOXEL_SIZE)
bone_blade.tail = (0, -25 * VOXEL_SIZE, 30 * VOXEL_SIZE)

# 5) Inner Runic Ring Bone
bone_r1 = eb.new("Rune_Ring_Inner")
bone_r1.parent = bone_core
bone_r1.head = (0, 5 * VOXEL_SIZE, 63 * VOXEL_SIZE)
bone_r1.tail = (0, 5 * VOXEL_SIZE, 72 * VOXEL_SIZE)

# 6) Outer Runic Ring Bone
bone_r2 = eb.new("Rune_Ring_Outer")
bone_r2.parent = bone_shaft
bone_r2.head = (0, 0, 48 * VOXEL_SIZE)
bone_r2.tail = (0, 0, 58 * VOXEL_SIZE)

# 7) Circular Vortex Trail Bone
bone_vortex = eb.new("Vortex_Trail_Bone")
bone_vortex.parent = bone_root
bone_vortex.head = (0, 0, 45 * VOXEL_SIZE)
bone_vortex.tail = (0, 0, 55 * VOXEL_SIZE)

# 8) Vortex Burst Sparks Bone
bone_burst = eb.new("Vortex_Burst_Bone")
bone_burst.parent = bone_root
bone_burst.head = (0, 0, 45 * VOXEL_SIZE)
bone_burst.tail = (0, 0, 55 * VOXEL_SIZE)

bpy.ops.object.mode_set(mode='OBJECT')

BONE_NAMES = [
    "Root", "Shaft_Bone", "Core_Bone", "Blade_Bone",
    "Rune_Ring_Inner", "Rune_Ring_Outer",
    "Vortex_Trail_Bone", "Vortex_Burst_Bone"
]

vgroups = {b: scythe_obj.vertex_groups.new(name=b) for b in BONE_NAMES}
bone_verts = {b: [] for b in BONE_NAMES}
for vidx, bname in vert_groups.items():
    if vidx < len(scythe_obj.data.vertices):
        bone_verts[bname].append(vidx)

for bname, vindices in bone_verts.items():
    if vindices:
        vgroups[bname].add(vindices, 1.0, 'REPLACE')

arm_mod = scythe_obj.modifiers.new(name="Armature", type='ARMATURE')
arm_mod.object = arm_obj
arm_mod.use_vertex_groups = True
scythe_obj.parent = arm_obj

# -----------------------------------------------------------------
# 6. Keyframe Animation (60 Frames @ 30 FPS)
# -----------------------------------------------------------------
print(">>> Keyframing Animation: Gyroscopic Runic Orbit & 720° Void Vortex Cyclone...")
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')

pb_root   = arm_obj.pose.bones["Root"]
pb_shaft  = arm_obj.pose.bones["Shaft_Bone"]
pb_core   = arm_obj.pose.bones["Core_Bone"]
pb_blade  = arm_obj.pose.bones["Blade_Bone"]
pb_r1     = arm_obj.pose.bones["Rune_Ring_Inner"]
pb_r2     = arm_obj.pose.bones["Rune_Ring_Outer"]
pb_vortex = arm_obj.pose.bones["Vortex_Trail_Bone"]
pb_burst  = arm_obj.pose.bones["Vortex_Burst_Bone"]

all_pose_bones = [pb_root, pb_shaft, pb_core, pb_blade, pb_r1, pb_r2, pb_vortex, pb_burst]

for pb in all_pose_bones:
    pb.rotation_mode = 'XYZ'

def keyframe_all(frame):
    for pb in all_pose_bones:
        pb.keyframe_insert(data_path="location", frame=frame)
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)
        pb.keyframe_insert(data_path="scale", frame=frame)

keyframes_data = [
    # F1: Ready Stance (Heroic Floating Idle)
    (1, {
        pb_root:   ((0, 0, 0), (math.radians(10), math.radians(-5), math.radians(15)), (1, 1, 1)),
        pb_shaft:  ((0, 0, 0), (math.radians(5), math.radians(2), math.radians(0)), (1, 1, 1)),
        pb_core:   ((0, 0, 0), (0, 0, 0), (1, 1, 1)),
        pb_blade:  ((0, 0, 0), (0, 0, 0), (1, 1, 1)),
        pb_r1:     ((0, 0, 0), (0, 0, 0), (1, 1, 1)),
        pb_r2:     ((0, 0, 0), (0, 0, 0), (1, 1, 1)),
        pb_vortex: ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
        pb_burst:  ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    }),
    # F7: Idle Gentle Float & Gyroscopic Ring Hum
    (7, {
        pb_root:   ((0, 0, 0.035), (math.radians(7), math.radians(-3), math.radians(12)), (1, 1, 1)),
        pb_shaft:  ((0, 0, 0), (math.radians(3), math.radians(4), math.radians(-2)), (1, 1, 1)),
        pb_core:   ((0, 0, 0), (0, math.radians(60), 0), (1.05, 1.05, 1.05)),
        pb_blade:  ((0, 0, 0), (0, 0, 0), (1, 1, 1)),
        pb_r1:     ((0, 0, 0), (math.radians(45), math.radians(120), math.radians(60)), (1, 1, 1)),
        pb_r2:     ((0, 0, 0), (math.radians(-60), math.radians(40), math.radians(-90)), (1, 1, 1)),
        pb_vortex: ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
        pb_burst:  ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    }),
    # F14: Anticipation Start — The Scythe coils back (Отведение назад перед покосом)
    (14, {
        pb_root:   ((-0.03, 0.04, 0.02), (math.radians(-12), math.radians(12), math.radians(45)), (1, 1, 1)),
        pb_shaft:  ((0, 0.03, 0), (math.radians(-15), math.radians(8), math.radians(10)), (1, 1, 1)),
        pb_core:   ((0, 0, 0), (0, math.radians(180), 0), (1.1, 1.1, 1.1)),
        pb_blade:  ((0, 0, 0), (math.radians(-4), math.radians(6), math.radians(-4)), (1, 1, 1)),
        pb_r1:     ((0, 0, 0), (math.radians(110), math.radians(320), math.radians(160)), (1.15, 1.15, 1.15)),
        pb_r2:     ((0, 0, 0), (math.radians(-160), math.radians(120), math.radians(-240)), (1.15, 1.15, 1.15)),
        pb_vortex: ((0, 0, 0), (0, 0, math.radians(30)), (0.05, 0.05, 0.05)),
        pb_burst:  ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    }),
    # F20: Peak Windup (Глубокий замах назад: коса поднята, лезвие нацелено в горизонт)
    (20, {
        pb_root:   ((-0.06, 0.08, 0.05), (math.radians(-25), math.radians(20), math.radians(65)), (1, 1, 1)),
        pb_shaft:  ((0, 0.06, 0), (math.radians(-25), math.radians(15), math.radians(15)), (1, 1, 1)),
        pb_core:   ((0, 0, 0), (0, math.radians(360), 0), (1.2, 1.2, 1.2)),
        pb_blade:  ((0, 0, 0), (math.radians(-8), math.radians(10), math.radians(-8)), (1, 1, 1)),
        pb_r1:     ((0, 0, 0), (math.radians(220), math.radians(640), math.radians(340)), (1.3, 1.3, 1.3)),
        pb_r2:     ((0, 0, 0), (math.radians(-320), math.radians(240), math.radians(-480)), (1.3, 1.3, 1.3)),
        pb_vortex: ((0, 0, 0), (0, 0, math.radians(50)), (0.25, 0.25, 0.25)),
        pb_burst:  ((0, 0, 0), (0, 0, 0), (0.1, 0.1, 0.1)),
    }),
    # F23: ⚡ INITIATION OF THE REAPING STRIKE (Взрывное начало срезающего покоса!)
    (23, {
        pb_root:   ((0.02, 0.01, 0.01), (math.radians(5), math.radians(-5), math.radians(5)), (1, 1, 1)),
        pb_shaft:  ((0, 0, 0), (math.radians(10), math.radians(-10), math.radians(-10)), (1, 1, 1)),
        pb_core:   ((0, 0, 0), (0, math.radians(520), 0), (1.25, 1.25, 1.25)),
        pb_blade:  ((0, 0, 0), (math.radians(4), math.radians(-4), math.radians(6)), (1, 1, 1)),
        pb_r1:     ((0, 0, 0), (math.radians(340), math.radians(980), math.radians(520)), (1.25, 1.25, 1.25)),
        pb_r2:     ((0, 0, 0), (math.radians(-480), math.radians(360), math.radians(-720)), (1.25, 1.25, 1.25)),
        pb_vortex: ((0, 0, 0), (0, 0, math.radians(-10)), (0.85, 0.85, 0.9)),
        pb_burst:  ((0, 0, 0), (0, 0, math.radians(-5)), (0.7, 0.7, 0.7)),
    }),
    # F26: ⚡ THE HARVEST IMPACT / FULL REAPING CUT (Сокрушительный покос боком: лезвие режет воздух!)
    (26, {
        pb_root:   ((0.08, -0.06, -0.03), (math.radians(22), math.radians(-18), math.radians(-65)), (1, 1, 1)),
        pb_shaft:  ((0, -0.04, 0), (math.radians(20), math.radians(-22), math.radians(-25)), (1, 1, 1)),
        pb_core:   ((0, 0, 0), (0, math.radians(720), 0), (1.3, 1.3, 1.3)),
        pb_blade:  ((0, 0, 0), (math.radians(8), math.radians(-10), math.radians(12)), (1, 1, 1)),
        pb_r1:     ((0, 0, 0), (math.radians(460), math.radians(1300), math.radians(700)), (1.35, 1.35, 1.35)),
        pb_r2:     ((0, 0, 0), (math.radians(-650), math.radians(480), math.radians(-960)), (1.35, 1.35, 1.35)),
        pb_vortex: ((0, 0, 0), (0, 0, math.radians(-65)), (1.35, 1.35, 1.2)),
        pb_burst:  ((0, 0, 0), (0, 0, math.radians(-60)), (1.4, 1.4, 1.4)),
    }),
    # F29: Follow-Through Overshoot & Maximum Swath (Проход дуги до предела: -85° yaw)
    (29, {
        pb_root:   ((0.10, -0.08, -0.04), (math.radians(25), math.radians(-22), math.radians(-85)), (1, 1, 1)),
        pb_shaft:  ((0, -0.05, 0), (math.radians(18), math.radians(-25), math.radians(-30)), (1, 1, 1)),
        pb_core:   ((0, 0, 0), (0, math.radians(840), 0), (1.2, 1.2, 1.2)),
        pb_blade:  ((0, 0, 0), (math.radians(5), math.radians(-6), math.radians(8)), (1, 1, 1)),
        pb_r1:     ((0, 0, 0), (math.radians(550), math.radians(1550), math.radians(840)), (1.2, 1.2, 1.2)),
        pb_r2:     ((0, 0, 0), (math.radians(-780), math.radians(580), math.radians(-1160)), (1.2, 1.2, 1.2)),
        pb_vortex: ((0, 0, 0), (0, 0, math.radians(-85)), (1.4, 1.4, 0.7)),
        pb_burst:  ((0, 0, 0), (0, 0, math.radians(-80)), (1.5, 1.5, 1.5)),
    }),
    # F34: Zanshin Lock & Kinetic Deceleration Snap (Остановка клинка с остаточной отдачей)
    (34, {
        pb_root:   ((0.08, -0.06, -0.03), (math.radians(20), math.radians(-18), math.radians(-80)), (1, 1, 1)),
        pb_shaft:  ((0, -0.04, 0), (math.radians(12), math.radians(-18), math.radians(-22)), (1, 1, 1)),
        pb_core:   ((0, 0, 0), (0, math.radians(940), 0), (1.1, 1.1, 1.1)),
        pb_blade:  ((0, 0, 0), (math.radians(-2), math.radians(3), math.radians(-2)), (1, 1, 1)),
        pb_r1:     ((0, 0, 0), (math.radians(620), math.radians(1750), math.radians(940)), (1.1, 1.1, 1.1)),
        pb_r2:     ((0, 0, 0), (math.radians(-880), math.radians(660), math.radians(-1320)), (1.1, 1.1, 1.1)),
        pb_vortex: ((0, 0, 0), (0, 0, math.radians(-90)), (0.35, 0.35, 0.15)),
        pb_burst:  ((0, 0, 0), (0, 0, math.radians(-85)), (0.5, 0.5, 0.5)),
    }),
    # F44: Graceful Noto Recovery Arc (Плавный дуговой возврат лезвия)
    (44, {
        pb_root:   ((0.03, -0.02, 0), (math.radians(14), math.radians(-10), math.radians(-30)), (1, 1, 1)),
        pb_shaft:  ((0, -0.01, 0), (math.radians(6), math.radians(-8), math.radians(-10)), (1, 1, 1)),
        pb_core:   ((0, 0, 0), (0, math.radians(1020), 0), (1.05, 1.05, 1.05)),
        pb_blade:  ((0, 0, 0), (0, 0, 0), (1, 1, 1)),
        pb_r1:     ((0, 0, 0), (math.radians(680), math.radians(1940), math.radians(1020)), (1.05, 1.05, 1.05)),
        pb_r2:     ((0, 0, 0), (math.radians(-980), math.radians(720), math.radians(-1450)), (1.05, 1.05, 1.05)),
        pb_vortex: ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
        pb_burst:  ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    }),
    # F54: Settling back to Center
    (54, {
        pb_root:   ((0, 0, 0.01), (math.radians(10), math.radians(-5), math.radians(5)), (1, 1, 1)),
        pb_shaft:  ((0, 0, 0), (math.radians(5), math.radians(0), math.radians(0)), (1, 1, 1)),
        pb_core:   ((0, 0, 0), (0, math.radians(1060), 0), (1, 1, 1)),
        pb_blade:  ((0, 0, 0), (0, 0, 0), (1, 1, 1)),
        pb_r1:     ((0, 0, 0), (math.radians(710), math.radians(2100), math.radians(1060)), (1, 1, 1)),
        pb_r2:     ((0, 0, 0), (math.radians(-1040), math.radians(740), math.radians(-1520)), (1, 1, 1)),
        pb_vortex: ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
        pb_burst:  ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    }),
    # F60: Perfect Loop (matches F1)
    (60, {
        pb_root:   ((0, 0, 0), (math.radians(10), math.radians(-5), math.radians(15)), (1, 1, 1)),
        pb_shaft:  ((0, 0, 0), (math.radians(5), math.radians(2), math.radians(0)), (1, 1, 1)),
        pb_core:   ((0, 0, 0), (0, math.radians(1080), 0), (1, 1, 1)),
        pb_blade:  ((0, 0, 0), (0, 0, 0), (1, 1, 1)),
        pb_r1:     ((0, 0, 0), (math.radians(720), math.radians(2160), math.radians(1080)), (1, 1, 1)),
        pb_r2:     ((0, 0, 0), (math.radians(-1080), math.radians(720), math.radians(-1560)), (1, 1, 1)),
        pb_vortex: ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
        pb_burst:  ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
    }),
]

for frame, bone_states in keyframes_data:
    for pb, (loc, rot, scl) in bone_states.items():
        pb.location = loc
        pb.rotation_euler = rot
        pb.scale = scl
    keyframe_all(frame)

bpy.ops.object.mode_set(mode='OBJECT')

# -----------------------------------------------------------------
# 7. Cycles Render Engine & Balanced Studio Lighting Setup
# -----------------------------------------------------------------
print(">>> Setting up Cycles AgX Render & Studio Lighting...")
scene.render.engine = 'CYCLES'
try:
    scene.cycles.device = 'GPU'
    bpy.context.preferences.compute_device_type = 'CUDA'
except Exception as e:
    print("GPU compute unavailable, falling back to CPU:", e)

scene.cycles.samples = 96
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

scene.view_settings.view_transform = 'AgX' if hasattr(scene.view_settings, 'view_transform') else 'Filmic'
scene.view_settings.look = 'AgX - High Contrast'

# Camera Target: Perfectly centered on the scythe's center of mass + vortex disc
cam_target = bpy.data.objects.new("CamTarget_Gemini37", None)
cam_target.location = (-0.12, -0.08, 0.38)
bpy.context.collection.objects.link(cam_target)

cam_data = bpy.data.cameras.new("Gemini37_Camera")
cam_data.lens = 36
cam_obj = bpy.data.objects.new("Gemini37_Camera", object_data=cam_data)
# Heroic isometric framing with comfortable padding around the blade tip and vortex disc
cam_obj.location = (2.35, -2.25, 1.40)

track = cam_obj.constraints.new(type='TRACK_TO')
track.target = cam_target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Studio Lighting Setup:
# 1) Key Sun Light: Cool platinum brilliance for metallic edge highlights
key_light = bpy.data.objects.new("Key_AstralSun", bpy.data.lights.new("Key_AstralSun", type='SUN'))
key_light.data.energy = 5.2
key_light.data.color = (0.96, 0.98, 1.00)
key_light.data.angle = math.radians(4)
key_light.rotation_euler = (math.radians(48), math.radians(18), math.radians(-32))
bpy.context.collection.objects.link(key_light)

# 2) Front Specular Fill Light: Illuminates obsidian shaft, blade body, and gold menuki runes
front_fill = bpy.data.objects.new("Front_Fill", bpy.data.lights.new("Front_Fill", type='AREA'))
front_fill.data.energy = 420.0
front_fill.data.color = (0.92, 0.95, 1.00)
front_fill.data.size = 3.8
front_fill.location = (1.8, -1.8, 1.0)
front_fill.rotation_euler = (math.radians(40), math.radians(-25), math.radians(-35))
bpy.context.collection.objects.link(front_fill)

# 3) Electric Astral Cyan Rim Light: Backlight defining blade curvature and vortex shockwave
rim_cyan = bpy.data.objects.new("Rim_AstralCyan", bpy.data.lights.new("Rim_AstralCyan", type='AREA'))
rim_cyan.data.energy = 360.0
rim_cyan.data.color = (0.00, 0.88, 1.00)
rim_cyan.data.size = 3.2
rim_cyan.location = (-1.6, 1.8, 1.4)
rim_cyan.rotation_euler = (math.radians(-35), math.radians(45), math.radians(120))
bpy.context.collection.objects.link(rim_cyan)

# 4) Deep Void Violet Fill Light: Soft ambient mood
fill_violet = bpy.data.objects.new("Fill_VoidViolet", bpy.data.lights.new("Fill_VoidViolet", type='AREA'))
fill_violet.data.energy = 320.0
fill_violet.data.color = (0.78, 0.18, 1.00)
fill_violet.data.size = 3.8
fill_violet.location = (0.8, 2.0, -0.2)
fill_violet.rotation_euler = (math.radians(-20), math.radians(20), math.radians(150))
bpy.context.collection.objects.link(fill_violet)

# 5) Core Gold Specular Accent: Enhances floating gyro-rings and rune inlays
core_light = bpy.data.objects.new("Core_Specular", bpy.data.lights.new("Core_Specular", type='POINT'))
core_light.data.energy = 250.0
core_light.data.color = (1.00, 0.84, 0.40)
core_light.location = (0.5, -0.1, 0.85)
bpy.context.collection.objects.link(core_light)

# -----------------------------------------------------------------
# 8. Export .blend, .glb, _render.png, and _data.js
# -----------------------------------------------------------------
output_dir = os.path.dirname(os.path.abspath(__file__))
blend_file = os.path.join(output_dir, "gemini3_7.blend")
glb_file = os.path.join(output_dir, "gemini3_7.glb")
render_file = os.path.join(output_dir, "gemini3_7_render.png")
js_file = os.path.join(output_dir, "gemini3_7_data.js")

print(f">>> Saving Blender file: {blend_file}")
bpy.ops.wm.save_as_mainfile(filepath=blend_file)

print(f">>> Exporting GLB model: {glb_file}")
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

print(f">>> Rendering Key Attack Frame 26 (720° Void Vortex Cyclone) to {render_file}...")
scene.frame_set(26)
scene.render.filepath = render_file
bpy.ops.render.render(write_still=True)

# Generate Base64 Data URI for offline zero-CORS browser support
print(f">>> Generating base64 data to {js_file}...")
with open(glb_file, 'rb') as f:
    glb_b64 = base64.b64encode(f.read()).decode('utf-8')

js_content = f'window.GEMINI37_BASE64 = "data:model/gltf-binary;base64,{glb_b64}";\n'
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_content)

print("=================================================================")
print(">>> [SUCCESS] Astral Void Scythe Gemini3.7 v2.0 Created & Exported!")
print("=================================================================")
