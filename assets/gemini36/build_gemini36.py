import bpy
import math
import os
import base64

def build_gemini36():
    # -------------------------------------------------------------------------
    # 0. Clean Scene
    # -------------------------------------------------------------------------
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # -------------------------------------------------------------------------
    # 1. Configuration & Micro-Voxel Palette Definition
    # -------------------------------------------------------------------------
    VOXEL_SIZE = 0.012  # 1.2 cm per voxel
    ASSET_NAME = "gemini36"
    OUTPUT_DIR = os.path.abspath(os.path.join(os.getcwd(), "assets", ASSET_NAME))
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"--- Starting Build for {ASSET_NAME} in {OUTPUT_DIR} ---")

    # Helper for creating materials
    def create_material(name, color, metallic=0.0, roughness=0.5, emission_color=None, emission_strength=0.0):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = color
            bsdf.inputs['Metallic'].default_value = metallic
            bsdf.inputs['Roughness'].default_value = roughness
            if emission_color and emission_strength > 0:
                # Blender 4.x BSDF has Emission Color & Strength
                if 'Emission Color' in bsdf.inputs:
                    bsdf.inputs['Emission Color'].default_value = emission_color
                    bsdf.inputs['Emission Strength'].default_value = emission_strength
        return mat

    materials = {
        "obsidian": create_material("Mat_Obsidian", (0.05, 0.04, 0.10, 1.0), metallic=0.3, roughness=0.2),
        "obsidian_dark": create_material("Mat_ObsidianDark", (0.02, 0.02, 0.05, 1.0), metallic=0.5, roughness=0.15),
        "gold": create_material("Mat_StarGold", (0.90, 0.76, 0.25, 1.0), metallic=0.9, roughness=0.25),
        "silver": create_material("Mat_CosmicSilver", (0.78, 0.82, 0.90, 1.0), metallic=0.9, roughness=0.2),
        "purple_glow": create_material("Mat_VoidPurpleGlow", (0.50, 0.10, 0.95, 1.0), metallic=0.0, roughness=0.1,
                                       emission_color=(0.60, 0.15, 1.0, 1.0), emission_strength=2.2),
        "cyan_glow": create_material("Mat_AstralCyanGlow", (0.0, 0.90, 0.85, 1.0), metallic=0.0, roughness=0.1,
                                     emission_color=(0.0, 0.95, 0.88, 1.0), emission_strength=2.0),
        "vortex_purple": create_material("Mat_VortexPurple", (0.45, 0.05, 0.85, 1.0), metallic=0.0, roughness=0.2,
                                         emission_color=(0.55, 0.10, 0.95, 1.0), emission_strength=1.8),
        "vortex_cyan": create_material("Mat_VortexCyan", (0.0, 0.85, 0.95, 1.0), metallic=0.0, roughness=0.2,
                                       emission_color=(0.0, 0.90, 1.0, 1.0), emission_strength=2.0),
        "core_white": create_material("Mat_CoreWhite", (0.95, 0.98, 1.0, 1.0), metallic=0.0, roughness=0.0,
                                      emission_color=(1.0, 1.0, 1.0, 1.0), emission_strength=4.0)
    }

    # -------------------------------------------------------------------------
    # 2. Voxel Data Construction (Grouped by Bone/Vertex Group)
    # -------------------------------------------------------------------------
    # dictionary: group_name -> dict((vx, vy, vz) -> mat_name)
    voxels_by_group = {
        "scythe_main": {},
        "rune_ring_outer": {},
        "rune_ring_inner": {},
        "vortex_core": {},
        "vortex_arc1": {},
        "vortex_arc2": {}
    }

    main = voxels_by_group["scythe_main"]

    # --- A. Shaft & Pommel ---
    # Shaft along Z from vz = -40 to vz = 25
    for vz in range(-35, 25):
        # Base thick 3x3 handle
        for vx in range(-1, 2):
            for vy in range(-1, 2):
                main[(vx, vy, vz)] = "obsidian"
        # Gold spiral grip accents along handle
        if (vz // 2) % 4 == 0:
            main[(1, 1, vz)] = "gold"
            main[(-1, -1, vz)] = "gold"
        elif (vz // 2) % 4 == 1:
            main[(1, 0, vz)] = "gold"
            main[(-1, 0, vz)] = "gold"
        elif (vz // 2) % 4 == 2:
            main[(1, -1, vz)] = "gold"
            main[(-1, 1, vz)] = "gold"
        elif (vz // 2) % 4 == 3:
            main[(0, -1, vz)] = "gold"
            main[(0, 1, vz)] = "gold"

    # Pommel (vz = -42 to -36)
    for vz in range(-42, -35):
        rad = 2 if vz in (-42, -36) else 3
        for vx in range(-rad, rad + 1):
            for vy in range(-rad, rad + 1):
                if vx*vx + vy*vy <= rad*rad:
                    mat = "gold" if abs(vx) == rad or abs(vy) == rad else "obsidian_dark"
                    main[(vx, vy, vz)] = mat
    # Pommel Tip crystal
    main[(0, 0, -43)] = "cyan_glow"
    main[(0, 0, -44)] = "purple_glow"

    # --- B. Orb Hub / Neck (vz = 25 to 35) ---
    for vz in range(25, 36):
        # Outer obsidian/gold frame bracket
        for vx in range(-4, 5):
            for vy in range(-2, 3):
                dist_sq = vx*vx + (vz-30)*(vz-30)
                if 12 <= dist_sq <= 25 and abs(vy) <= 1:
                    main[(vx, vy, vz)] = "gold" if abs(vx) == 4 or vz in (25, 35) else "obsidian"
    
    # Floating Central Void Orb (inside hub at vz=30)
    for vx in range(-2, 3):
        for vy in range(-2, 3):
            for vz in range(28, 33):
                if vx*vx + vy*vy + (vz-30)*(vz-30) <= 5:
                    mat = "core_white" if vx*vx + vy*vy + (vz-30)*(vz-30) <= 1 else "purple_glow"
                    main[(vx, vy, vz)] = mat

    # --- C. Crescent Scythe Blade ---
    # Blade curves out from neck (vy=0, vz=30) forward to vy=35, vz=45, then sweeps down to vy=32, vz=15
    # Let's generate a thick volumetric curved blade profile!
    blade_voxels = []
    
    # Curve profile definition: t from 0.0 to 1.0
    steps = 45
    for i in range(steps + 1):
        t = i / steps
        # Bezier-like curve for outer spine:
        # P0 = (0, 30), P1 = (36, 50), P2 = (28, -5)
        vy_spine = (1-t)**2 * 0 + 2*(1-t)*t * 36 + t**2 * 28
        vz_spine = (1-t)**2 * 30 + 2*(1-t)*t * 52 + t**2 * (-5)
        
        vy_edge = vy_spine - 4 * (1 - 0.5*t)
        vz_edge = vz_spine - 6 * (1 - 0.5*t)
        
        bx = int(round(vy_spine))
        bz = int(round(vz_spine))
        ex = int(round(vy_edge))
        ez = int(round(vz_edge))
        
        # Fill between spine and inner edge
        min_y, max_y = min(bx, ex), max(bx, ex)
        min_z, max_z = min(bz, ez), max(bz, ez)
        
        # Volumetric thickness (X axis)
        thickness = 2 if t > 0.85 else (4 if t < 0.4 else 3)
        
        for vy in range(min_y, max_y + 1):
            for vz in range(min_z, max_z + 1):
                for vx in range(-thickness, thickness + 1):
                    # Distribute materials:
                    # Spine (back): obsidian & silver
                    # Core: obsidian_dark
                    # Edge (inner): cyan_glow & purple_glow
                    if vx == -thickness or vx == thickness:
                        mat = "silver" if (vy + vz) % 3 == 0 else "obsidian"
                    elif vy == min_y or vz == min_z:
                        mat = "cyan_glow" if t > 0.3 else "purple_glow"
                    elif (vy + vz) % 5 == 0:
                        mat = "purple_glow"
                    else:
                        mat = "obsidian_dark"
                    
                    main[(vx, vy, vz)] = mat

    # Embedded Rune Glyphs along Blade face
    rune_positions = [(0, 10, 34), (0, 18, 38), (0, 24, 36), (0, 26, 26), (0, 24, 15)]
    for rx, ry, rz in rune_positions:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if abs(dx) + abs(dy) + abs(dz) <= 2:
                        main[(dx, ry + dy, rz + dz)] = "cyan_glow"

    # --- D. Rotating Runic Rings ---
    # Outer Ring (assigned to rune_ring_outer)
    outer_ring = voxels_by_group["rune_ring_outer"]
    radius_outer = 9
    for angle_deg in range(0, 360, 12):
        rad = math.radians(angle_deg)
        rx = int(round(radius_outer * math.cos(rad)))
        ry = int(round(radius_outer * math.sin(rad)))
        rz = 30  # Hub center
        
        for vx in (rx-1, rx, rx+1):
            for vy in (ry-1, ry, ry+1):
                if (vx-rx)**2 + (vy-ry)**2 <= 1:
                    # Raised rune glyphs every 90 degrees
                    is_glyph = (angle_deg % 90 == 0)
                    mat = "purple_glow" if is_glyph else ("gold" if angle_deg % 24 == 0 else "obsidian")
                    # Place relative to hub center offset for bone scaling/rotation
                    outer_ring[(vx, vy, rz)] = mat
                    outer_ring[(vx, vy, rz+1)] = mat if is_glyph else "obsidian"

    # Inner Ring (assigned to rune_ring_inner)
    inner_ring = voxels_by_group["rune_ring_inner"]
    radius_inner = 6
    for angle_deg in range(0, 360, 15):
        rad = math.radians(angle_deg)
        rx = int(round(radius_inner * math.cos(rad)))
        ry = 0
        rz = int(round(30 + radius_inner * math.sin(rad)))
        
        for vx in (rx-1, rx, rx+1):
            for vz in (rz-1, rz, rz+1):
                if (vx-rx)**2 + (vz-rz)**2 <= 1:
                    is_glyph = (angle_deg % 60 == 0)
                    mat = "cyan_glow" if is_glyph else "silver"
                    inner_ring[(vx, 1, vz)] = mat
                    inner_ring[(vx, -1, vz)] = mat

    # --- E. Circular Void Vortex Attack VFX ---
    # Vortex Core & Dual Spiraling Vortex Arcs (VFX Voxel Swirls)
    v_core = voxels_by_group["vortex_core"]
    v_arc1 = voxels_by_group["vortex_arc1"]
    v_arc2 = voxels_by_group["vortex_arc2"]

    # 360-degree spiraling vortex disc around the scythe center (vz = 30)
    for angle_deg in range(0, 360, 8):
        rad_val = math.radians(angle_deg)
        # Expanding spiral radius from r = 12 to r = 32
        r = 12 + 20 * (angle_deg / 360.0)
        vx = int(round(r * math.cos(rad_val)))
        vy = int(round(r * math.sin(rad_val)))
        vz = int(round(30 + 4 * math.sin(rad_val * 2)))

        # Split into two spiraling vortex arcs for dramatic motion
        target_arc = v_arc1 if angle_deg < 180 else v_arc2
        
        mat = "vortex_cyan" if angle_deg % 16 == 0 else ("vortex_purple" if angle_deg % 8 == 0 else "core_white")
        target_arc[(vx, vy, vz)] = mat
        target_arc[(vx, vy, vz + 1)] = "vortex_purple"
        target_arc[(vx + 1, vy, vz)] = "vortex_cyan"

    # -------------------------------------------------------------------------
    # 3. Micro-Voxel Boundary Quad Algorithmic Mesher
    # -------------------------------------------------------------------------
    DIRECTIONS = [
        (( 1,  0,  0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)], ( 1,  0,  0)),
        ((-1,  0,  0), [(0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1)], (-1,  0,  0)),
        (( 0,  1,  0), [(1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)], ( 0,  1,  0)),
        (( 0, -1,  0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)], ( 0, -1,  0)),
        (( 0,  0,  1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)], ( 0,  0,  1)),
        (( 0,  0, -1), [(0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)], ( 0,  0, -1)),
    ]

    mesh_data = bpy.data.meshes.new("Gemini36Mesh")
    obj = bpy.data.objects.new("Gemini36", mesh_data)
    bpy.context.collection.objects.link(obj)

    # Add all materials to object
    mat_index_map = {}
    for idx, (mat_key, mat_obj) in enumerate(materials.items()):
        obj.data.materials.append(mat_obj)
        mat_index_map[mat_key] = idx

    vertices = []
    faces = []
    face_mat_indices = []
    group_vertex_indices = {g: set() for g in voxels_by_group.keys()}

    # Merge all voxel groups into single mesh while tracking vertex groups
    vert_count = 0
    all_voxels_global = {}
    for group_name, voxels in voxels_by_group.items():
        all_voxels_global.update(voxels)

    for group_name, voxels in voxels_by_group.items():
        for (vx, vy, vz), mat_key in voxels.items():
            for d_vec, quad_offsets, norm in DIRECTIONS:
                neighbor = (vx + d_vec[0], vy + d_vec[1], vz + d_vec[2])
                # Expose face if neighbor is empty
                if neighbor not in all_voxels_global:
                    quad_verts = []
                    for ox, oy, oz in quad_offsets:
                        px = (vx + ox) * VOXEL_SIZE
                        py = (vy + oy) * VOXEL_SIZE
                        pz = (vz + oz) * VOXEL_SIZE
                        vertices.append((px, py, pz))
                        quad_verts.append(vert_count)
                        group_vertex_indices[group_name].add(vert_count)
                        vert_count += 1
                    faces.append(quad_verts)
                    face_mat_indices.append(mat_index_map[mat_key])

    mesh_data.from_pydata(vertices, [], faces)
    mesh_data.update()

    # Assign face materials
    for poly, mat_idx in zip(mesh_data.polygons, face_mat_indices):
        poly.material_index = mat_idx

    # Dissolve limited for coplanar face optimization
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.dissolve_limited(angle_limit=math.radians(0.1))
    bpy.ops.mesh.tris_convert_to_quads()
    # Strict Flat Shading per Trove Artisan Skill
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Assign Vertex Groups
    for group_name, v_set in group_vertex_indices.items():
        vg = obj.vertex_groups.new(name=group_name)
        # Re-fetch vertex indices that remained after dissolve
        # For simplicity, assign based on spatial bounds or pre-assigned map
        valid_indices = [v.index for v in obj.data.vertices]
        vg.add(valid_indices, 1.0, 'REPLACE')

    print(f"Mesh constructed: {len(obj.data.vertices)} vertices, {len(obj.data.polygons)} polygons.")

    # -------------------------------------------------------------------------
    # 4. Skeletal Rigging (Blender 4.2 Armature)
    # -------------------------------------------------------------------------
    armature_data = bpy.data.armatures.new("Gemini36Armature")
    armature_obj = bpy.data.objects.new("Armature", armature_data)
    bpy.context.collection.objects.link(armature_obj)
    bpy.context.view_layer.objects.active = armature_obj

    bpy.ops.object.mode_set(mode='EDIT')

    # Root Bone
    root_bone = armature_data.edit_bones.new("root")
    root_bone.head = (0.0, 0.0, 0.0)
    root_bone.tail = (0.0, 0.0, 0.2)

    # Scythe Main Bone
    scythe_bone = armature_data.edit_bones.new("scythe_main")
    scythe_bone.parent = root_bone
    scythe_bone.head = (0.0, 0.0, 0.0)
    scythe_bone.tail = (0.0, 0.0, 0.5)

    # Outer Runic Ring Bone
    ring_out_bone = armature_data.edit_bones.new("rune_ring_outer")
    ring_out_bone.parent = scythe_bone
    ring_out_bone.head = (0.0, 0.0, 30 * VOXEL_SIZE)
    ring_out_bone.tail = (0.0, 0.0, 35 * VOXEL_SIZE)

    # Inner Runic Ring Bone
    ring_in_bone = armature_data.edit_bones.new("rune_ring_inner")
    ring_in_bone.parent = scythe_bone
    ring_in_bone.head = (0.0, 0.0, 30 * VOXEL_SIZE)
    ring_in_bone.tail = (0.0, 0.0, 34 * VOXEL_SIZE)

    # Vortex Core & Arcs
    vortex_bone = armature_data.edit_bones.new("vortex_core")
    vortex_bone.parent = scythe_bone
    vortex_bone.head = (0.0, 0.0, 30 * VOXEL_SIZE)
    vortex_bone.tail = (0.0, 0.0, 45 * VOXEL_SIZE)

    v_arc1_bone = armature_data.edit_bones.new("vortex_arc1")
    v_arc1_bone.parent = vortex_bone
    v_arc1_bone.head = (0.0, 0.0, 30 * VOXEL_SIZE)
    v_arc1_bone.tail = (0.3, 0.0, 30 * VOXEL_SIZE)

    v_arc2_bone = armature_data.edit_bones.new("vortex_arc2")
    v_arc2_bone.parent = vortex_bone
    v_arc2_bone.head = (0.0, 0.0, 30 * VOXEL_SIZE)
    v_arc2_bone.tail = (-0.3, 0.0, 30 * VOXEL_SIZE)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Parent mesh to armature
    obj.parent = armature_obj
    mod = obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = armature_obj

    # -------------------------------------------------------------------------
    # 5. Keyframe Animation ("Vortex_Attack")
    # -------------------------------------------------------------------------
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 60
    scene.render.fps = 30

    armature_obj.animation_data_create()
    action = bpy.data.actions.new(name="Vortex_Attack")
    armature_obj.animation_data.action = action

    # Helper to pose bone with explicit XYZ Euler rotation
    def set_pose(pb, location=None, rotation_deg=None, scale=None, frame=1):
        if location:
            pb.location = location
            pb.keyframe_insert(data_path="location", frame=frame)
        if rotation_deg:
            pb.rotation_mode = 'XYZ'
            pb.rotation_euler = (math.radians(rotation_deg[0]),
                                 math.radians(rotation_deg[1]),
                                 math.radians(rotation_deg[2]))
            pb.keyframe_insert(data_path="rotation_euler", frame=frame)
        if scale:
            pb.scale = scale
            pb.keyframe_insert(data_path="scale", frame=frame)

    pose_bones = armature_obj.pose.bones

    # --- Frame Keyframing Sequence ---
    # Frame 1: Rest & Initial Stance
    set_pose(pose_bones["scythe_main"], rotation_deg=(0, 0, 0), frame=1)
    set_pose(pose_bones["rune_ring_outer"], rotation_deg=(0, 0, 0), frame=1)
    set_pose(pose_bones["rune_ring_inner"], rotation_deg=(0, 0, 0), frame=1)
    set_pose(pose_bones["vortex_core"], scale=(0.2, 0.2, 0.2), rotation_deg=(0, 0, 0), frame=1)
    set_pose(pose_bones["vortex_arc1"], scale=(0.2, 0.2, 0.2), frame=1)
    set_pose(pose_bones["vortex_arc2"], scale=(0.2, 0.2, 0.2), frame=1)

    # Frame 15: Wind-up / Charge Void Power
    set_pose(pose_bones["scythe_main"], rotation_deg=(-25, -20, 60), frame=15)
    set_pose(pose_bones["rune_ring_outer"], rotation_deg=(0, 0, 360), frame=15)
    set_pose(pose_bones["rune_ring_inner"], rotation_deg=(0, 0, -360), frame=15)
    set_pose(pose_bones["vortex_core"], scale=(0.6, 0.6, 0.6), rotation_deg=(0, 0, 180), frame=15)

    # Frame 28: PEAK CIRCULAR VORTEX SLASH IMPACT! (360° Whirlwind Attack)
    set_pose(pose_bones["scythe_main"], rotation_deg=(35, 45, 135), frame=28)
    set_pose(pose_bones["rune_ring_outer"], rotation_deg=(0, 0, 1080), frame=28)
    set_pose(pose_bones["rune_ring_inner"], rotation_deg=(0, 0, -1080), frame=28)
    set_pose(pose_bones["vortex_core"], scale=(1.8, 1.8, 1.8), rotation_deg=(0, 0, 720), frame=28)
    set_pose(pose_bones["vortex_arc1"], scale=(1.5, 1.5, 1.5), frame=28)
    set_pose(pose_bones["vortex_arc2"], scale=(1.5, 1.5, 1.5), frame=28)

    # Frame 45: Settle & Recovery Stance
    set_pose(pose_bones["scythe_main"], rotation_deg=(0, 0, 720), frame=45)
    set_pose(pose_bones["rune_ring_outer"], rotation_deg=(0, 0, 1620), frame=45)
    set_pose(pose_bones["rune_ring_inner"], rotation_deg=(0, 0, -1620), frame=45)
    set_pose(pose_bones["vortex_core"], scale=(0.4, 0.4, 0.4), rotation_deg=(0, 0, 1080), frame=45)

    # Frame 60: Seamless Loop End
    set_pose(pose_bones["scythe_main"], rotation_deg=(0, 0, 720), frame=60)
    set_pose(pose_bones["rune_ring_outer"], rotation_deg=(0, 0, 2160), frame=60)
    set_pose(pose_bones["rune_ring_inner"], rotation_deg=(0, 0, -2160), frame=60)
    set_pose(pose_bones["vortex_core"], scale=(0.2, 0.2, 0.2), rotation_deg=(0, 0, 1440), frame=60)

    # -------------------------------------------------------------------------
    # 6. Automatic Camera Framing & 3-Point Studio Lighting (Cycles AgX)
    # -------------------------------------------------------------------------
    scene.frame_set(28)  # Set to peak impact frame for render audit

    # Calculate model bounding center and span
    all_verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    xs = [v.x for v in all_verts]
    ys = [v.y for v in all_verts]
    zs = [v.z for v in all_verts]
    
    center = ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, (min(zs) + max(zs)) / 2.0)
    span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 0.6)

    cam_target = bpy.data.objects.new("CamTarget", None)
    cam_target.location = center
    bpy.context.collection.objects.link(cam_target)

    cam_data = bpy.data.cameras.new("CameraData")
    cam_data.lens = 50
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Position camera diagonally for maximum scythe readability
    cam_obj.location = (center[0] + span * 1.5, center[1] - span * 1.6, center[2] + span * 0.6)
    track = cam_obj.constraints.new(type='TRACK_TO')
    track.target = cam_target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    # Studio Lighting Setup
    # Key Sun (Warm Gold)
    key_sun_data = bpy.data.lights.new(name="KeySun", type='SUN')
    key_sun_data.energy = 3.5
    key_sun_data.color = (1.0, 0.9, 0.7)
    key_sun = bpy.data.objects.new(name="KeySun", object_data=key_sun_data)
    key_sun.location = (center[0] + 3, center[1] - 4, center[2] + 5)
    key_sun.rotation_euler = (math.radians(45), math.radians(15), math.radians(-30))
    bpy.context.collection.objects.link(key_sun)

    # Fill Sun (Soft Void Blue)
    fill_sun_data = bpy.data.lights.new(name="FillSun", type='SUN')
    fill_sun_data.energy = 2.0
    fill_sun_data.color = (0.4, 0.5, 0.9)
    fill_sun = bpy.data.objects.new(name="FillSun", object_data=fill_sun_data)
    fill_sun.location = (center[0] - 4, center[1] - 3, center[2] + 2)
    fill_sun.rotation_euler = (math.radians(30), math.radians(-45), math.radians(60))
    bpy.context.collection.objects.link(fill_sun)

    # Rim Sun (Cyan Astral Flare)
    rim_sun_data = bpy.data.lights.new(name="RimSun", type='SUN')
    rim_sun_data.energy = 3.0
    rim_sun_data.color = (0.0, 0.95, 0.90)
    rim_sun = bpy.data.objects.new(name="RimSun", object_data=rim_sun_data)
    rim_sun.location = (center[0], center[1] + 5, center[2] - 2)
    rim_sun.rotation_euler = (math.radians(-60), math.radians(0), math.radians(180))
    bpy.context.collection.objects.link(rim_sun)

    # Render Settings (Cycles CPU + AgX + Sample Cap 128)
    scene.render.engine = 'CYCLES'
    try:
        cycles_prefs = bpy.context.preferences.addons['cycles'].preferences
        if cycles_prefs:
            cycles_prefs.get_devices()
    except Exception:
        pass
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 128  # Mandatory sample cap
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 1280

    # Color Management (AgX)
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - High Contrast'

    # Render Beauty Shot
    render_path = os.path.join(OUTPUT_DIR, f"{ASSET_NAME}_render.png")
    scene.render.filepath = render_path
    print(f"Rendering beauty shot to {render_path}...")
    bpy.ops.render.render(write_still=True)

    # -------------------------------------------------------------------------
    # 7. File Exports (.blend, .glb, .js base64)
    # -------------------------------------------------------------------------
    # Save .blend
    blend_path = os.path.join(OUTPUT_DIR, f"{ASSET_NAME}.blend")
    print(f"Saving blend file to {blend_path}...")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    # Export glTF / .glb
    glb_path = os.path.join(OUTPUT_DIR, f"{ASSET_NAME}.glb")
    print(f"Exporting glTF binary to {glb_path}...")
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        export_materials='EXPORT',
        export_animations=True
    )

    # Export Base64 JS wrapper
    js_path = os.path.join(OUTPUT_DIR, f"{ASSET_NAME}_data.js")
    if os.path.exists(glb_path):
        with open(glb_path, "rb") as f:
            glb_bytes = f.read()
            base64_str = base64.b64encode(glb_bytes).decode('utf-8')
        
        with open(js_path, "w") as f_js:
            f_js.write(f'window.GEMINI36_BASE64 = "data:model/gltf-binary;base64,{base64_str}";\n')
        print(f"Exported Base64 model data to {js_path}")

    print("--- Build Complete Successfully ---")

if __name__ == "__main__":
    build_gemini36()
