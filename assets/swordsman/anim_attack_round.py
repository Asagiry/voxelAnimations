"""
assets/swordsman/anim_attack_round.py
Stand-Alone Minimal Left-Hand 180° Circular Attack:
- Left hand (Hand.L & Socket_Hand_L) performs ONLY the circular rotation from -135° to -315°.
- Trajectory in XY:
  * Start (F8):  theta = -135° (X = -0.198m, Y = -0.198m, Z = 0.28m)
  * Point 1 (F12): theta = -180° (X = -0.280m, Y =  0.000m, Z = 0.28m)
  * Point 2 (F16): theta = -225° (X = -0.198m, Y = +0.198m, Z = 0.28m)
  * Point 3 (F20): theta = -270° (X =  0.000m, Y = +0.280m, Z = 0.28m)
  * End (F24):   theta = -315° (X = +0.198m, Y = +0.198m, Z = 0.28m)
- Strict mathematical tangent blade vector: u_blade = (sin(th), -cos(th), 0.0)
- Outward radial cutting edge: u_edge = (-cos(th), -sin(th), 0.0)
- Arm segments (Shoulder.L, UpperArm.L, Forearm.L) align along the kinetic line of action.
- Action & NLA Track: 'Attack_Round'
- Renders multi-view contact sheet: 'attack_round_filmstrip.png'
"""

import bpy
import os
import math
import base64
import subprocess
from mathutils import Vector, Euler, Matrix

def deg(v):
    return math.radians(v)

def set_bone_world_matrix(pb, target_mat):
    """Accurately computes and sets local location & rotation for pb to achieve target_mat in Armature space."""
    parent = pb.parent
    R_b = pb.bone.matrix_local
    if parent:
        R_p = parent.bone.matrix_local
        M_p = parent.matrix
        L_b = R_b.inverted() @ R_p @ M_p.inverted() @ target_mat
    else:
        L_b = R_b.inverted() @ target_mat
    pb.rotation_mode = 'XYZ'
    pb.location = L_b.to_translation()
    pb.rotation_euler = L_b.to_euler('XYZ')

def solve_socket_hand_matrix(hand_pos, theta_rad):
    """Computes target world matrix for Socket_Hand_L."""
    y_blade = Vector((math.sin(theta_rad), -math.cos(theta_rad), 0.0)).normalized()
    z_edge = Vector((-math.cos(theta_rad), -math.sin(theta_rad), 0.0)).normalized()
    x_cross = y_blade.cross(z_edge).normalized()

    socket_mat = Matrix((
        (x_cross.x, y_blade.x, z_edge.x, hand_pos.x),
        (x_cross.y, y_blade.y, z_edge.y, hand_pos.y),
        (x_cross.z, y_blade.z, z_edge.z, hand_pos.z),
        (0.0,       0.0,       0.0,       1.0)
    ))
    return socket_mat

def solve_hand_matrix_from_socket(pb_hand, pb_socket, socket_mat):
    """Computes target world matrix for Hand.L from Socket_Hand_L target matrix."""
    R_hand = pb_hand.bone.matrix_local
    R_sock = pb_socket.bone.matrix_local
    R_rel = R_hand.inverted() @ R_sock
    hand_mat = socket_mat @ R_rel.inverted()
    return hand_mat

def solve_arm_segments_mat(shoulder_pos, hand_pos):
    """Computes world matrices for UpperArm.L and Forearm.L along line of action."""
    arm_vec = hand_pos - shoulder_pos
    dist = arm_vec.length
    arm_dir = arm_vec.normalized()

    upper_pos = shoulder_pos + arm_dir * (dist * 0.35)
    fore_pos = shoulder_pos + arm_dir * (dist * 0.70)

    y_axis = -arm_dir
    z_axis = Vector((0, 0, 1))
    if abs(y_axis.dot(z_axis)) > 0.9:
        z_axis = Vector((0, 1, 0))
    x_axis = y_axis.cross(z_axis).normalized()
    z_axis = x_axis.cross(y_axis).normalized()

    upper_mat = Matrix((
        (x_axis.x, y_axis.x, z_axis.x, upper_pos.x),
        (x_axis.y, y_axis.y, z_axis.y, upper_pos.y),
        (x_axis.z, y_axis.z, z_axis.z, upper_pos.z),
        (0.0,      0.0,      0.0,      1.0)
    ))
    fore_mat = Matrix((
        (x_axis.x, y_axis.x, z_axis.x, fore_pos.x),
        (x_axis.y, y_axis.y, z_axis.y, fore_pos.y),
        (x_axis.z, y_axis.z, z_axis.z, fore_pos.z),
        (0.0,      0.0,      0.0,      1.0)
    ))
    return upper_mat, fore_mat

def create_temp_sword():
    """Creates a stylized voxel sword mesh for Socket_Hand_L for visual audit."""
    mesh = bpy.data.meshes.new("Temp_Audit_Sword_L")
    obj = bpy.data.objects.new("Temp_Audit_Sword_L", mesh)
    bpy.context.scene.collection.objects.link(obj)

    import bmesh
    bm = bmesh.new()

    # Materials
    mat_blade = bpy.data.materials.new(name="M_Audit_Blade_L")
    mat_blade.use_nodes = True
    bsdf = mat_blade.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.2, 0.75, 1.0, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.9
        bsdf.inputs['Roughness'].default_value = 0.15
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = (0.2, 0.75, 1.0, 1.0)
            bsdf.inputs['Emission Strength'].default_value = 1.0
    obj.data.materials.append(mat_blade)

    mat_gold = bpy.data.materials.new(name="M_Audit_Gold_L")
    mat_gold.use_nodes = True
    bsdf_g = mat_gold.node_tree.nodes.get("Principled BSDF")
    if bsdf_g:
        bsdf_g.inputs['Base Color'].default_value = (1.0, 0.80, 0.15, 1.0)
        bsdf_g.inputs['Metallic'].default_value = 0.9
        bsdf_g.inputs['Roughness'].default_value = 0.25
    obj.data.materials.append(mat_gold)

    # Blade along local +Y of bone
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.035
        v.co.y = v.co.y * 0.21 + 0.24 # y from 0.03 to 0.45
        v.co.z *= 0.015
    for f in bm.faces:
        f.material_index = 0

    bm_guard = bmesh.new()
    bmesh.ops.create_cube(bm_guard, size=1.0)
    for v in bm_guard.verts:
        v.co.x *= 0.11
        v.co.y = v.co.y * 0.02 + 0.02
        v.co.z *= 0.03
    for f in bm_guard.faces:
        f.material_index = 1
    bm_guard.to_mesh(mesh)
    bm_guard.free()

    bm.to_mesh(mesh)
    bm.free()

    # Assign 100% rigid weight to Socket_Hand_L
    vg = obj.vertex_groups.new(name="Socket_Hand_L")
    vg.add(list(range(len(mesh.vertices))), 1.0, 'REPLACE')
    return obj

def build_attack_round():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    blend_path = os.path.join(base_dir, "swordsman.blend")
    if os.path.exists(blend_path):
        bpy.ops.wm.open_mainfile(filepath=blend_path)
    else:
        raise FileNotFoundError(f"Missing base blend file: {blend_path}")

    arm = bpy.data.objects.get("Armature")
    mesh = bpy.data.objects.get("Swordsman_Mesh")
    if not arm or not mesh:
        raise ValueError("Missing Armature or Swordsman_Mesh in scene")

    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')
    pbones = arm.pose.bones

    if not arm.animation_data:
        arm.animation_data_create()

    old_act = bpy.data.actions.get("Attack_Round")
    if old_act:
        bpy.data.actions.remove(old_act)

    act = bpy.data.actions.new("Attack_Round")
    arm.animation_data.action = act

    # Reset all pose bones to rest
    for pb in pbones:
        pb.rotation_mode = 'XYZ'
        pb.location = Vector((0, 0, 0))
        pb.rotation_euler = Euler((0, 0, 0), 'XYZ')

    pb_shoulder_l = pbones['Shoulder.L']
    pb_upperarm_l = pbones['UpperArm.L']
    pb_forearm_l = pbones['Forearm.L']
    pb_hand_l = pbones['Hand.L']
    pb_socket_l = pbones['Socket_Hand_L']

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 36

    # -------------------------------------------------------------------------
    # CIRCULAR TRAJECTORY FROM -135° TO -315°
    # Center = (0, 0, 0.28m), R = 0.28m, Z_const = 0.28m
    # -------------------------------------------------------------------------
    R = 0.28
    Z_const = 0.28
    C = Vector((0.0, 0.0, Z_const))

    def get_circle_pos(deg_val):
        th = math.radians(deg_val)
        return C + Vector((R * math.cos(th), R * math.sin(th), 0.0)), th

    # Keyframe Specs across the rotation
    keyframe_specs = [
        # Frame 1: Hold Start Angle (-135°)
        (1, {'deg': -135}),
        # Frame 6: Ready to Sweep (-135°)
        (6, {'deg': -135}),
        # Frame 10: Sweep (-180°)
        (10, {'deg': -180}),
        # Frame 14: Sweep (-225°)
        (14, {'deg': -225}),
        # Frame 18: Sweep (-270°)
        (18, {'deg': -270}),
        # Frame 22: Reached Target Angle (-315°)
        (22, {'deg': -315}),
        # Frame 26: Hold Target Angle (-315°)
        (26, {'deg': -315}),
        # Frame 36: Return to Start (-135°)
        (36, {'deg': -135}),
    ]

    # Set Neutral Poses for other body parts (Right arm, hips, chest, head, legs)
    for frame, spec in keyframe_specs:
        bpy.context.scene.frame_set(frame)

        # Right hand neutral
        for pb_name in ['Shoulder.R', 'UpperArm.R', 'Forearm.R', 'Hand.R', 'Hips', 'Chest', 'Head', 'UpperLeg.L', 'LowerLeg.L', 'Foot.L', 'UpperLeg.R', 'LowerLeg.R', 'Foot.R']:
            pb = pbones.get(pb_name)
            if pb:
                pb.rotation_mode = 'XYZ'
                pb.location = Vector((0, 0, 0))
                pb.rotation_euler = Euler((0, 0, 0), 'XYZ')
                pb.keyframe_insert(data_path="location", frame=frame)
                pb.keyframe_insert(data_path="rotation_euler", frame=frame)

        # Shoulder.L neutral base
        pb_shoulder_l.rotation_mode = 'XYZ'
        pb_shoulder_l.location = Vector((0, 0, 0))
        pb_shoulder_l.rotation_euler = Euler((0, 0, 0), 'XYZ')
        pb_shoulder_l.keyframe_insert(data_path="location", frame=frame)
        pb_shoulder_l.keyframe_insert(data_path="rotation_euler", frame=frame)

        bpy.context.view_layer.update()
        sh_pos = pb_shoulder_l.matrix.to_translation()

        # Compute trajectory point & angle
        h_pos, th = get_circle_pos(spec['deg'])

        # Align UpperArm.L and Forearm.L along line of action
        upper_mat, fore_mat = solve_arm_segments_mat(sh_pos, h_pos)
        set_bone_world_matrix(pb_upperarm_l, upper_mat)
        pb_upperarm_l.keyframe_insert(data_path="location", frame=frame)
        pb_upperarm_l.keyframe_insert(data_path="rotation_euler", frame=frame)
        bpy.context.view_layer.update()

        set_bone_world_matrix(pb_forearm_l, fore_mat)
        pb_forearm_l.keyframe_insert(data_path="location", frame=frame)
        pb_forearm_l.keyframe_insert(data_path="rotation_euler", frame=frame)
        bpy.context.view_layer.update()

        # Compute exact Hand.L & Socket_Hand_L world matrix
        sock_mat = solve_socket_hand_matrix(h_pos, th)
        hand_mat = solve_hand_matrix_from_socket(pb_hand_l, pb_socket_l, sock_mat)

        set_bone_world_matrix(pb_hand_l, hand_mat)
        pb_hand_l.keyframe_insert(data_path="location", frame=frame)
        pb_hand_l.keyframe_insert(data_path="rotation_euler", frame=frame)

        # Keep Socket_Hand_L keyframed at local identity
        pb_socket_l.location = Vector((0, 0, 0))
        pb_socket_l.rotation_euler = Euler((0, 0, 0), 'XYZ')
        pb_socket_l.keyframe_insert(data_path="location", frame=frame)
        pb_socket_l.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Set Bezier interpolation
    if act.fcurves:
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.easing = 'AUTO'

    print("Keyframed Attack_Round: Left Hand pure rotation from -135° to -315°.")

    # --- TEMPORARY AUDIT SWORD ATTACHMENT VIA ARMATURE SKINNING ---
    audit_sword = create_temp_sword()
    audit_sword.parent = arm
    mod_sword = audit_sword.modifiers.new(name="Armature", type='ARMATURE')
    mod_sword.object = arm
    mod_sword.use_vertex_groups = True

    # --- MULTI-ANGLE 3-ROW FILMSTRIP GENERATION ---
    print("\n--- RENDERING 3-ROW CONTACT SHEET (attack_round_filmstrip.png) ---")
    filmstrip_frames = [1, 6, 10, 14, 18, 22, 26, 36]
    filmstrip_cols = len(filmstrip_frames)

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = False
    scene.render.resolution_x = 256
    scene.render.resolution_y = 256
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - High Contrast'

    for obj in list(scene.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    def add_light(name, ltype, loc, energy, color=(1, 1, 1)):
        ldata = bpy.data.lights.new(name=name, type=ltype)
        ldata.energy = energy
        ldata.color = color
        lobj = bpy.data.objects.new(name=name, object_data=ldata)
        lobj.location = loc
        scene.collection.objects.link(lobj)
        return lobj

    add_light("KeySun", 'SUN', (3.0, 3.0, 5.0), 3.5, (1.0, 0.95, 0.88))
    add_light("FillTop", 'POINT', (0.0, 0.0, 4.0), 40.0, (0.85, 0.92, 1.0))
    add_light("RimLight", 'POINT', (-2.5, -2.5, 2.5), 60.0, (0.4, 0.8, 1.0))

    cam_data = bpy.data.cameras.new("FilmstripCam")
    cam_obj = bpy.data.objects.new("FilmstripCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    views = [
        ('top', Vector((0.0, 0.0, 1.5)), Euler((0.0, 0.0, 0.0), 'XYZ'), 0.95),
        ('front_34', Vector((-0.9, 1.2, 0.7)), Euler((math.radians(65), 0.0, math.radians(-145)), 'XYZ'), 0.70),
        ('side', Vector((-1.4, 0.0, 0.32)), Euler((math.radians(90), 0.0, math.radians(-90)), 'XYZ'), 0.70)
    ]

    rendered_images = []
    for row_idx, (vname, cam_pos, cam_rot, ortho_scale) in enumerate(views):
        cam_obj.location = cam_pos
        cam_obj.rotation_euler = cam_rot
        cam_data.type = 'ORTHO' if vname in ('top', 'side') else 'PERSP'
        if cam_data.type == 'ORTHO':
            cam_data.ortho_scale = ortho_scale
        else:
            cam_data.lens = 50

        for col_idx, f in enumerate(filmstrip_frames):
            scene.frame_set(f)
            bpy.context.view_layer.update()
            temp_img_path = os.path.join(base_dir, f"temp_strip_round_r{row_idx}_c{col_idx}.png")
            scene.render.filepath = temp_img_path
            bpy.ops.render.render(write_still=True)
            rendered_images.append(temp_img_path)

    # Stitch via system python subprocess
    contact_stitch_script = f"""
import os, glob
from PIL import Image, ImageDraw

base_dir = r"{base_dir}"
w, h = 256, 256
filmstrip_cols = {filmstrip_cols}
views = {len(views)}
filmstrip_frames = {filmstrip_frames}
sheet_w = w * filmstrip_cols
sheet_h = h * views
contact_sheet = Image.new('RGBA', (sheet_w, sheet_h), (14, 14, 17, 255))
draw = ImageDraw.Draw(contact_sheet)

for r in range(views):
    for c in range(filmstrip_cols):
        im_path = os.path.join(base_dir, f"temp_strip_round_r{{r}}_c{{c}}.png")
        if os.path.exists(im_path):
            tile = Image.open(im_path)
            contact_sheet.paste(tile, (c * w, r * h))
            tile.close()
            try:
                os.remove(im_path)
            except Exception:
                pass

row_labels = ["TOP-DOWN (Hand.L: -135° to -315°)", "FRONT 3/4 PERSPECTIVE", "SIDE PROFILE (Strict Z=0.28m)"]
for r, label in enumerate(row_labels):
    draw.text((12, r * h + 10), label, fill=(255, 215, 0, 255))

for c, f in enumerate(filmstrip_frames):
    draw.text((c * w + 12, 10), f"F{{f:02d}}", fill=(100, 200, 255, 255))

filmstrip_final_path = os.path.join(base_dir, "attack_round_filmstrip.png")
contact_sheet.save(filmstrip_final_path)
print(f"Saved Contact Sheet to: {{filmstrip_final_path}}")
"""
    try:
        subprocess.run(["python", "-c", contact_stitch_script], check=True)
    except Exception as e:
        print(f"Warning running PIL stitcher subprocess: {e}")

    # Remove temporary objects before saving blend and exporting GLB
    bpy.data.objects.remove(audit_sword, do_unlink=True)
    bpy.data.objects.remove(cam_obj, do_unlink=True)
    for obj in list(scene.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    # Save cleanly to blend
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"Saved updated attack_round animation to: {blend_path}")

    # --- EXPORT GLTF 2.0 (swordsman.glb) WITH ALL ACTIONS AS NLA TRACKS ---
    print("\n--- EXPORTING GLTF 2.0 WITH ALL ANIMATIONS (swordsman.glb) ---")
    if not arm.animation_data:
        arm.animation_data_create()
    arm.animation_data.action = None
    for track in list(arm.animation_data.nla_tracks):
        arm.animation_data.nla_tracks.remove(track)

    for act_name in ['Attack_Round', 'Walk', 'Attack']:
        a = bpy.data.actions.get(act_name)
        if a:
            track = arm.animation_data.nla_tracks.new()
            track.name = act_name
            track.strips.new(act_name, int(a.frame_range[0]), a)

    glb_filepath = os.path.join(base_dir, "swordsman.glb")
    bpy.ops.export_scene.gltf(
        filepath=glb_filepath,
        export_format='GLB',
        export_animations=True,
        export_skins=True,
        export_all_influences=False,
        export_apply=False,
        export_yup=True
    )
    print(f"Saved GLB to: {glb_filepath}")

    # --- EXPORT BASE64 (swordsman_data.js) ---
    with open(glb_filepath, "rb") as f:
        b64_data = base64.b64encode(f.read()).decode('utf-8')

    js_filepath = os.path.join(base_dir, "swordsman_data.js")
    with open(js_filepath, "w", encoding="utf-8") as f:
        f.write(f'window.SWORDSMAN_BASE64 = "data:model/gltf-binary;base64,{b64_data}";\n')
    print(f"Saved Base64 Data URI to: {js_filepath}")

if __name__ == "__main__":
    build_attack_round()
