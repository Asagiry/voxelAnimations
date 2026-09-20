"""
ClaudeSonnet4.6 — Astral Void Scythe FINAL
============================================
Architecture fix:
  - All meshes parented to ARMATURE with parent_type='OBJECT' (no bone offset)
  - Rings animated via direct pose bone rotations with ring meshes vertex-group parented
  - Weapon sits upright, camera computed from actual world positions
  - Blade clearly visible as a large crescent sweeping from shaft top
"""

import bpy
import math

VOXEL_SIZE = 0.012
ASSET_NAME = "ClaudeSonnet4.6"

# ── Palette ───────────────────────────────────────────────────────────────────

PALETTE = {
    "shaft_dark":  ((0.025, 0.004, 0.070, 1.0), 0.0),
    "shaft_mid":   ((0.090, 0.020, 0.220, 1.0), 0.0),
    "blade_base":  ((0.012, 0.008, 0.040, 1.0), 0.0),
    "blade_edge":  ((0.260, 0.035, 0.850, 1.0), 2.0),   # was 3.0 — AgX cap 2.5
    "ring_metal":  ((0.520, 0.400, 1.000, 1.0), 0.3),   # was 0.5
    "rune_glow":   ((0.520, 0.060, 1.000, 1.0), 2.0),   # was 2.2
    "void_core":   ((1.000, 1.000, 1.000, 1.0), 3.5),   # was 4.5 — limit tiny cores
    "crystal":     ((0.230, 0.030, 0.800, 1.0), 1.2),   # was 1.4
    "trail":       ((0.350, 0.040, 0.900, 1.0), 1.6),   # was 1.8
}
MATS = {}

def get_mat(name):
    if name in MATS:
        return MATS[name]
    color, emit = PALETTE[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Emission Color"].default_value = color
    bsdf.inputs["Emission Strength"].default_value = emit
    bsdf.inputs["Roughness"].default_value = 0.82
    bsdf.inputs["Metallic"].default_value = 0.15
    MATS[name] = mat
    return mat

# ── Mesh builder ──────────────────────────────────────────────────────────────

def build_mesh(name, voxels_dict, location=(0, 0, 0)):
    DIRS = [
        (( 1, 0, 0), [(1,0,0),(1,1,0),(1,1,1),(1,0,1)]),
        ((-1, 0, 0), [(0,1,0),(0,0,0),(0,0,1),(0,1,1)]),
        (( 0, 1, 0), [(1,1,0),(0,1,0),(0,1,1),(1,1,1)]),
        (( 0,-1, 0), [(0,0,0),(1,0,0),(1,0,1),(0,0,1)]),
        (( 0, 0, 1), [(0,0,1),(1,0,1),(1,1,1),(0,1,1)]),
        (( 0, 0,-1), [(0,1,0),(1,1,0),(1,0,0),(0,0,0)]),
    ]
    vset = set(voxels_dict)
    verts_list, faces_list, mat_idx_list = [], [], []
    mat_map = {}

    def slot(mn):
        if mn not in mat_map:
            mat_map[mn] = len(mat_map)
        return mat_map[mn]

    vi = 0
    for (vx, vy, vz), mn in voxels_dict.items():
        ox, oy, oz = vx*VOXEL_SIZE, vy*VOXEL_SIZE, vz*VOXEL_SIZE
        for (dx,dy,dz), corners in DIRS:
            if (vx+dx, vy+dy, vz+dz) in vset:
                continue
            fv = [(ox+cx*VOXEL_SIZE, oy+cy*VOXEL_SIZE, oz+cz*VOXEL_SIZE)
                  for cx,cy,cz in corners]
            verts_list.extend(fv)
            faces_list.append((vi, vi+1, vi+2, vi+3))
            mat_idx_list.append(slot(mn))
            vi += 4

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts_list, [], faces_list)
    for mn in sorted(mat_map, key=lambda m: mat_map[m]):
        mesh.materials.append(get_mat(mn))
    for fi, poly in enumerate(mesh.polygons):
        poly.material_index = mat_idx_list[fi]
        poly.use_smooth = False
    mesh.validate()
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    return obj

# ── Geometry ──────────────────────────────────────────────────────────────────

def gen_shaft():
    """Vertical shaft z=0..80. 5×5 rounded cross-section."""
    voxels = {}
    for z in range(0, 80):
        mat = "shaft_dark" if (z // 5) % 2 == 0 else "shaft_mid"
        for x in range(-2, 3):
            for y in range(-2, 3):
                if abs(x) + abs(y) <= 3:
                    voxels[(x, y, z)] = mat
    for rz in range(8, 75, 10):
        for x in range(-2, 3):
            for y in range(-2, 3):
                if abs(x) + abs(y) <= 3:
                    voxels[(x, y, rz)] = "rune_glow"
    return voxels

def gen_blade():
    """
    Crescent blade sweeping X+ from shaft top (z=76).
    Large, readable, 90-voxel span with prominent glow edge.
    """
    voxels = {}
    L = 88  # blade length in voxels

    for bx in range(0, L):
        t   = bx / (L - 1)
        arc = int(math.sin(t * math.pi) * 48)  # peak +48 voxels
        cz  = 76 + arc
        thick = max(2, 6 - int(t * 4.5))

        for dz in range(0, thick):
            for dy in range(-3, 4):
                voxels[(bx + 4, dy, cz + dz)] = "blade_base"
        # Glowing outer edge (top)
        for dy in range(-2, 3):
            voxels[(bx + 4, dy, cz + thick)]     = "blade_edge"
            voxels[(bx + 4, dy, cz + thick + 1)] = "blade_edge"
        # Inner belly glow
        if t > 0.05:
            for dy in range(-2, 3):
                voxels[(bx + 4, dy, cz - 1)] = "blade_edge"

    # Back-hook at base
    for hz in range(-12, 1):
        r = max(1, 4 - abs(hz + 6))
        for dy in range(-r, r+1):
            voxels[(4, dy, 76 + hz)] = "blade_base"
        for dy in range(-1, 2):
            voxels[(3, dy, 76 + hz)] = "blade_edge"

    # Void tip at end
    tip_z = 76  # tip end arc falls back to base z
    for dy in range(-1, 2):
        for dz in range(0, 3):
            voxels[(L + 3, dy, tip_z + dz)] = "void_core"
    for dy in range(-2, 3):
        voxels[(L + 2, dy, tip_z + 1)] = "blade_edge"

    return voxels

def gen_guard():
    """Cross-guard z=73–77, 18 voxels wide."""
    voxels = {}
    for gx in range(-9, 10):
        for gy in range(-1, 2):
            for gz in range(73, 77):
                voxels[(gx, gy, gz)] = "ring_metal"
    for gy in range(-1, 2):
        for gz in range(73, 77):
            voxels[(-9, gy, gz)] = "crystal"
            voxels[( 9, gy, gz)] = "crystal"
    return voxels

def gen_runic_ring(radius, ring_width, mat_body, mat_rune, rune_count):
    """Flat XY ring centred at origin — placed at correct Z via object.location."""
    voxels = {}
    for angle_deg in range(0, 360, 3):
        angle = math.radians(angle_deg)
        for r in range(radius - ring_width, radius + ring_width + 1):
            rx = int(round(math.cos(angle) * r))
            ry = int(round(math.sin(angle) * r))
            voxels[(rx, ry, 0)] = mat_body
            voxels[(rx, ry, 1)] = mat_body
    for i in range(rune_count):
        angle = math.radians(i * 360.0 / rune_count)
        rx = int(round(math.cos(angle) * radius))
        ry = int(round(math.sin(angle) * radius))
        for ddx in range(-1, 2):
            for ddy in range(-1, 2):
                if abs(ddx) + abs(ddy) <= 1:
                    voxels[(rx+ddx, ry+ddy, 0)] = mat_rune
                    voxels[(rx+ddx, ry+ddy, 1)] = mat_rune
    return voxels

def gen_void_orb():
    """Crystal orb centred at origin — placed via object.location."""
    voxels = {}
    for oz in range(0, 14):
        r = max(0, 6 - abs(oz - 7))
        for ox in range(-r, r+1):
            for oy in range(-r, r+1):
                if ox*ox + oy*oy <= r*r:
                    inner = (ox*ox + oy*oy < (r-1)*(r-1)) and 6 <= oz <= 8
                    voxels[(ox, oy, oz)] = "void_core" if inner else "crystal"
    return voxels

def gen_vortex_particles():
    """Compact vortex particle rings around weapon midpoint."""
    voxels = {}
    cfgs = [(14, 0, 0.0), (22, 10, 1.1), (30, -10, 2.2)]
    for ring_i, (r_r, dz, phase) in enumerate(cfgs):
        base_z = 40 + dz  # around shaft mid
        for seg in range(0, 360, 6):
            angle = math.radians(seg) + phase
            px = int(round(math.cos(angle) * r_r))
            py = int(round(math.sin(angle) * r_r))
            pz = base_z + int(math.sin(angle * 2 + ring_i) * 5)
            mat = "rune_glow" if seg % 18 == 0 else "trail"
            voxels[(px, py, pz)]     = mat
            voxels[(px, py, pz + 1)] = mat
    return voxels

# ── Scene ─────────────────────────────────────────────────────────────────────

def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for blk in list(bpy.data.meshes):     bpy.data.meshes.remove(blk)
    for blk in list(bpy.data.materials):  bpy.data.materials.remove(blk)
    for blk in list(bpy.data.armatures):  bpy.data.armatures.remove(blk)
    for blk in list(bpy.data.cameras):    bpy.data.cameras.remove(blk)
    for blk in list(bpy.data.lights):     bpy.data.lights.remove(blk)
    for blk in list(bpy.data.objects):
        if blk.type == 'EMPTY': bpy.data.objects.remove(blk)
    MATS.clear()

# Ring Z positions (in meters)
RING_Z = [18 * VOXEL_SIZE, 40 * VOXEL_SIZE, 60 * VOXEL_SIZE]

def build_scene():
    reset_scene()

    shaft_obj  = build_mesh("Shaft",   gen_shaft())
    blade_obj  = build_mesh("Blade",   gen_blade())
    guard_obj  = build_mesh("Guard",   gen_guard())
    orb_obj    = build_mesh("VoidOrb", gen_void_orb(),
                            location=(0, 0, -18 * VOXEL_SIZE))
    vortex_obj = build_mesh("Vortex",  gen_vortex_particles())

    # Rings placed at correct Z world positions
    ring_cfgs = [
        (14, 2, "ring_metal", "rune_glow",  8, RING_Z[0]),
        (20, 2, "ring_metal", "rune_glow", 10, RING_Z[1]),
        (26, 2, "ring_metal", "void_core", 12, RING_Z[2]),
    ]
    ring_objs = []
    for i, (rad, wid, mb, mr, rc, rz) in enumerate(ring_cfgs):
        ro = build_mesh(f"Ring{i+1}", gen_runic_ring(rad, wid, mb, mr, rc),
                        location=(0, 0, rz))
        ring_objs.append(ro)

    weapon_objs = [shaft_obj, blade_obj, guard_obj, orb_obj] + ring_objs
    all_objs    = weapon_objs + [vortex_obj]
    return all_objs, weapon_objs, ring_objs

# ── Armature (rings only, pure rotation) ─────────────────────────────────────

def build_rig_and_animate(ring_objs):
    """
    Simple armature with one bone per ring.
    Rings parented to their bone with OBJECT parent (no offset).
    Static meshes have no armature — they don't need it.
    """
    arm_data = bpy.data.armatures.new("RingArm")
    arm_obj  = bpy.data.objects.new("RingArm", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    bone_names = []
    for i, rz in enumerate(RING_Z):
        b = eb.new(f"ring{i+1}")
        b.head = (0, 0, rz)
        b.tail = (0, 0, rz + 0.05)
        bone_names.append(f"ring{i+1}")

    bpy.ops.object.mode_set(mode='OBJECT')

    # Parent rings to arm (OBJECT parent, NO bone — avoids tail offset)
    for i, ro in enumerate(ring_objs):
        ro.parent      = arm_obj
        ro.parent_type = 'OBJECT'
        # Keep current world position (rings already have correct location)
        ro.matrix_parent_inverse = arm_obj.matrix_world.inverted()

    # ── Keyframe ring spins ──
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')

    scene = bpy.context.scene
    scene.render.fps  = 24
    scene.frame_start = 1
    scene.frame_end   = 72

    action = bpy.data.actions.new("VortexAttack")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = action

    def kf_rot(bn, frame, rx, ry, rz):
        pb = arm_obj.pose.bones[bn]
        pb.rotation_mode  = 'XYZ'
        pb.rotation_euler = (rx, ry, rz)
        pb.keyframe_insert("rotation_euler", frame=frame)

    for frame in range(1, 73):
        t = (frame - 1) / 71.0
        a = t * math.pi * 4

        kf_rot("ring1", frame,  a * 1.0,  a * 0.4,  a * 0.7)
        kf_rot("ring2", frame, -a * 0.7,  a * 1.3,  a * 1.0)
        kf_rot("ring3", frame,  a * 0.9, -a * 1.1,  a * 1.7)

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

# ── Weapon swing via NLA / root empty animation ───────────────────────────────

def animate_weapon_swing(shaft_obj, blade_obj, guard_obj, orb_obj, vortex_obj):
    """Animate the whole weapon group via a root empty rotation."""
    root = bpy.data.objects.new("WeaponRoot", None)
    root.location = (0, 0, 0)
    bpy.context.collection.objects.link(root)

    for obj in [shaft_obj, blade_obj, guard_obj, orb_obj, vortex_obj]:
        obj.parent = root

    root.animation_data_create()
    action = bpy.data.actions.new("WeaponSwing")
    root.animation_data.action = action

    scene = bpy.context.scene
    for frame in range(1, 73):
        t = (frame - 1) / 71.0
        swing = math.sin(t * math.pi) * math.radians(145)
        tilt  = math.sin(t * math.pi * 2) * math.radians(16)
        root.rotation_mode  = 'XYZ'
        root.rotation_euler = (tilt, 0.0, swing)
        root.keyframe_insert("rotation_euler", frame=frame)

    return root

# ── Render ────────────────────────────────────────────────────────────────────

def setup_and_render(weapon_objs):
    scene = bpy.context.scene
    scene.render.engine        = 'CYCLES'
    scene.cycles.samples       = 128
    scene.cycles.use_denoising = True
    try:
        scene.cycles.device = 'GPU'
    except Exception:
        pass
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look           = 'AgX - High Contrast'
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    scene.render.image_settings.file_format = 'PNG'

    scene.frame_set(1)  # rest pose

    # Bounding box from weapon objects only (no vortex particles)
    xs, ys, zs = [], [], []
    for obj in weapon_objs:
        for vert in obj.data.vertices:
            wco = obj.matrix_world @ vert.co
            xs.append(wco.x); ys.append(wco.y); zs.append(wco.z)

    cx   = (min(xs) + max(xs)) / 2.0
    cy   = (min(ys) + max(ys)) / 2.0
    cz   = (min(zs) + max(zs)) / 2.0
    span = max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs), 0.3)
    print(f"[DEBUG] weapon bbox center=({cx:.3f},{cy:.3f},{cz:.3f}) span={span:.3f}")

    cam_d = bpy.data.cameras.new("Cam")
    cam_d.lens = 40          # moderate FOV — balanced framing
    cam   = bpy.data.objects.new("Cam", cam_d)
    bpy.context.collection.objects.link(cam)
    # Shift look-target UP toward blade (weapon is tall: shaft+blade)
    tz = cz + span * 0.22   # aim higher than geometric center
    cam.location = (cx + span*0.5, cy - span*1.1, cz + span*0.55)
    scene.camera = cam

    target = bpy.data.objects.new("CamTarget", None)
    target.location = (cx, cy, tz)   # elevated target
    bpy.context.collection.objects.link(target)
    trk = cam.constraints.new(type='TRACK_TO')
    trk.target     = target
    trk.track_axis = 'TRACK_NEGATIVE_Z'
    trk.up_axis    = 'UP_Y'

    def add_light(ltype, name, energy, color, loc):
        ld = bpy.data.lights.new(name, ltype)
        ld.energy = energy; ld.color = color
        lo = bpy.data.objects.new(name, ld)
        bpy.context.collection.objects.link(lo)
        lo.location = loc
        return lo

    key = add_light('SUN',  'Key',  4.0, (1.00, 0.90, 0.80),
                    (cx+span, cy-span*0.5, cz+span*1.6))
    rim = add_light('SPOT', 'Rim', 60.0, (0.55, 0.15, 1.00),   # was 130
                    (cx-span, cy+span,     cz+span*0.5))
    fll = add_light('AREA', 'Fill', 35.0, (0.70, 0.50, 1.00),  # was 50
                    (cx,      cy+span,     cz+span*0.3))
    rim.constraints.new(type='TRACK_TO').target = target
    fll.constraints.new(type='TRACK_TO').target = target

    import os
    out_dir     = os.path.dirname(os.path.abspath(__file__))
    render_path = os.path.join(out_dir, f"{ASSET_NAME}_render.png")
    scene.render.filepath = render_path
    bpy.ops.render.render(write_still=True)
    print(f"[{ASSET_NAME}] Render → {render_path}")
    return render_path

# ── Export ────────────────────────────────────────────────────────────────────

def export_glb():
    import os
    out_dir  = os.path.dirname(os.path.abspath(__file__))
    glb_path = os.path.join(out_dir, f"{ASSET_NAME}.glb")
    bpy.ops.export_scene.gltf(
        filepath=glb_path, export_format='GLB',
        export_animations=True, export_skins=True,
        export_lights=False, export_apply=True,
    )
    print(f"[{ASSET_NAME}] GLB → {glb_path}")

def save_blend():
    import os
    out_dir    = os.path.dirname(os.path.abspath(__file__))
    blend_path = os.path.join(out_dir, f"{ASSET_NAME}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[{ASSET_NAME}] .blend → {blend_path}")

# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    all_objs, weapon_objs, ring_objs = build_scene()

    shaft_obj  = bpy.data.objects["Shaft"]
    blade_obj  = bpy.data.objects["Blade"]
    guard_obj  = bpy.data.objects["Guard"]
    orb_obj    = bpy.data.objects["VoidOrb"]
    vortex_obj = bpy.data.objects["Vortex"]

    arm_obj  = build_rig_and_animate(ring_objs)
    root_obj = animate_weapon_swing(shaft_obj, blade_obj, guard_obj, orb_obj, vortex_obj)

    render_path = setup_and_render(weapon_objs)
    export_glb()
    save_blend()
    print(f"[{ASSET_NAME}] BUILD COMPLETE ✓")
