"""
assets/swordsman/anim_attack_round.py
Dynamic Martial 180° Slash:
- Katana cutting edge rotated 180° along blade axis to lead cleanly into the cut.
- Shoulder.L displaced outward from torso (+X lateral offset) + widened hand arc (R = 0.35m, C = (0.03, 0.03, 0.28m))
  giving full arm clearance and zero body-clinging.
- Full-body martial torque ("бочком поворачивается"):
  * Wind-up coil (F1–F5): Hips +25°, Chest +35°, lean -5°, Head counter-rotated -22° (target lock).
  * Continuous accelerating power strike (F6–F20, t^1.45): Hips snap from +25° to -35°, Chest whips from +35° to -50°, +15° forward lean.
  * Offhand counter-balance (Right Arm pulls back and flings outward).
  * Impact hold (F21–F24) with subtle micro-tremor at F22.
  * Smooth fluid cubic ease-out recovery (F25–F36): 1 - (1-t)^3 settling seamlessly back to ready coil.
- Ground Plane Invariant (Z >= 0.0m).
- Multi-angle 3-row filmstrip with dynamic look-at camera tracking.
- Action & Primary NLA Track: 'Attack_Round'
"""

import bpy
import os
import math
import base64
import subprocess
from mathutils import Vector, Euler, Matrix, Quaternion

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

def solve_socket_hand_matrix_left(hand_pos, theta_rad):
    """
    Computes target world matrix for Socket_Hand_L on Left-Hand sweep.
    - y_blade: points along weapon shaft / blade length (local +Y)
    - z_edge: cutting edge (local +Z). Flipped 180° around blade axis so the sharp edge faces into the cut.
    """
    y_blade = Vector((-math.sin(theta_rad), -math.cos(theta_rad), 0.0)).normalized()
    # Flipped 180° around y_blade: (cos(th), -sin(th), 0)
    z_edge = Vector((math.cos(theta_rad), -math.sin(theta_rad), 0.0)).normalized()
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
    """Computes world matrices for UpperArm.L and Forearm.L along kinetic line of action."""
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

def point_camera_at(cam_obj, target_loc):
    """Points camera directly at target_loc using Quaternion look-at."""
    direction = target_loc - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler('XYZ')

def create_temp_sword():
    """Creates a stylized voxel katana mesh for Socket_Hand_L for visual audit with red cutting edge."""
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
        bsdf.inputs['Base Color'].default_value = (0.2, 0.8, 1.0, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.95
        bsdf.inputs['Roughness'].default_value = 0.15
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = (0.2, 0.8, 1.0, 1.0)
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

    # Red cutting edge on +Z
    mat_edge = bpy.data.materials.new(name="M_Audit_Edge_L")
    mat_edge.use_nodes = True
    bsdf_e = mat_edge.node_tree.nodes.get("Principled BSDF")
    if bsdf_e:
        bsdf_e.inputs['Base Color'].default_value = (1.0, 0.1, 0.25, 1.0)
        if 'Emission Color' in bsdf_e.inputs:
            bsdf_e.inputs['Emission Color'].default_value = (1.0, 0.1, 0.25, 1.0)
            bsdf_e.inputs['Emission Strength'].default_value = 3.0
    obj.data.materials.append(mat_edge)

    # Katana blade along local +Y
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.026
        v.co.y = v.co.y * 0.26 + 0.28 # y from 0.02 to 0.54
        v.co.z *= 0.016
    for f in bm.faces:
        f.material_index = 0

    # Red cutting edge strip at local +Z
    bm_edge = bmesh.new()
    bmesh.ops.create_cube(bm_edge, size=1.0)
    for v in bm_edge.verts:
        v.co.x *= 0.012
        v.co.y = v.co.y * 0.26 + 0.28
        v.co.z = v.co.z * 0.005 + 0.012 # positive +Z edge
    for f in bm_edge.faces:
        f.material_index = 2
    bm_edge.to_mesh(mesh)
    bm_edge.free()

    # Guard (Tsuba)
    bm_guard = bmesh.new()
    bmesh.ops.create_cube(bm_guard, size=1.0)
    for v in bm_guard.verts:
        v.co.x *= 0.09
        v.co.y = v.co.y * 0.02 + 0.02
        v.co.z *= 0.07
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

    pb_root = pbones.get('Root')
    pb_hips = pbones.get('Hips')
    pb_chest = pbones.get('Chest')
    pb_head = pbones.get('Head')
    pb_shoulder_l = pbones['Shoulder.L']
    pb_upperarm_l = pbones['UpperArm.L']
    pb_forearm_l = pbones['Forearm.L']
    pb_hand_l = pbones['Hand.L']
    pb_socket_l = pbones['Socket_Hand_L']

    pb_shoulder_r = pbones.get('Shoulder.R')
    pb_upperarm_r = pbones.get('UpperArm.R')
    pb_forearm_r = pbones.get('Forearm.R')
    pb_hand_r = pbones.get('Hand.R')
    pb_socket_r = pbones.get('Socket_Hand_R')

    pb_leg_l = pbones.get('UpperLeg.L')
    pb_shin_l = pbones.get('LowerLeg.L')
    pb_foot_l = pbones.get('Foot.L')

    pb_leg_r = pbones.get('UpperLeg.R')
    pb_shin_r = pbones.get('LowerLeg.R')
    pb_foot_r = pbones.get('Foot.R')

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 36

    # -------------------------------------------------------------------------
    # EXPANDED REACH TRAJECTORY:
    # Radius R = 0.35m, Center = (0.02, 0.03, 0.28m)
    # -------------------------------------------------------------------------
    R = 0.35
    Z_strike = 0.28
    C_base = Vector((0.02, 0.03, Z_strike))

    F_start = 6
    F_end = 20

    # Keyframe every frame across [1, 36]
    for frame in range(1, 37):
        bpy.context.scene.frame_set(frame)

        # 1. Trajectory angle and phase factors
        if frame < F_start:
            # Phase 1: Wind-up coil (F1-F5)
            deg_val = -135.0
            body_twist_factor = 0.0 # full coil back
        elif frame <= F_end:
            # Phase 2: Active continuous power strike (F6-F20)
            t_strike_progress = (frame - F_start) / (F_end - F_start)
            # Explosive acceleration curve (t^1.45)
            ease_strike = t_strike_progress ** 1.45
            deg_val = -135.0 + (-315.0 - (-135.0)) * ease_strike
            # Torso torque smoothstep
            body_twist_factor = t_strike_progress
        elif frame <= F_end + 4: # Frames 21-24: Impact hold
            deg_val = -315.0
            body_twist_factor = 1.0
        else:
            # Phase 4: Recovery with smooth cubic ease-out (F25-F36)
            t_rec = (frame - (F_end + 4)) / (36 - (F_end + 4))
            ease_rec = 1.0 - ((1.0 - t_rec) ** 3)
            deg_val = -315.0 + (-135.0 - (-315.0)) * ease_rec
            body_twist_factor = 1.0 - ease_rec

        th = math.radians(deg_val)

        # 2. Dynamic Full Body Martial Torque ("бочком поворачивается")
        # Wind-up coil: Hips +25°, Chest +35°, forward lean -5°
        # Strike peak: Hips -35°, Chest -50°, forward lean +15°
        hips_yaw = math.radians(25.0 + (-35.0 - 25.0) * body_twist_factor)
        chest_yaw = math.radians(35.0 + (-50.0 - 35.0) * body_twist_factor)
        chest_lean = math.radians(-5.0 + (15.0 - (-5.0)) * body_twist_factor)

        # Head target lock: counter-rotates so gaze stays focused forward
        head_yaw = -chest_yaw * 0.65

        # Subtle impact tremor on frame 22
        if frame == 22:
            chest_lean += math.radians(2.0)
            hips_yaw += math.radians(1.5)

        # Apply Spine/Torso
        if pb_hips:
            pb_hips.rotation_mode = 'XYZ'
            pb_hips.location = Vector((0, 0, 0))
            pb_hips.rotation_euler = Euler((0, 0, hips_yaw), 'XYZ')
            pb_hips.keyframe_insert(data_path="location", frame=frame)
            pb_hips.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_chest:
            pb_chest.rotation_mode = 'XYZ'
            pb_chest.location = Vector((0, 0, 0))
            pb_chest.rotation_euler = Euler((chest_lean, 0, chest_yaw), 'XYZ')
            pb_chest.keyframe_insert(data_path="location", frame=frame)
            pb_chest.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_head:
            pb_head.rotation_mode = 'XYZ'
            pb_head.location = Vector((0, 0, 0))
            pb_head.rotation_euler = Euler((0, 0, head_yaw), 'XYZ')
            pb_head.keyframe_insert(data_path="location", frame=frame)
            pb_head.keyframe_insert(data_path="rotation_euler", frame=frame)

        # 3. Shoulder.L: Extended outward from center of character ("отдалить плечо")
        # In Shoulder.L rest pose: head is (4*V, 0, 23.5*V), tail is (8*V, 0, 23.5*V) -> points along +X
        # In bone local space, local +Y is along bone length (+X world).
        # Giving local location.y = +0.035m pushes the shoulder outward away from the chest!
        sh_outward = 0.035
        sh_forward = 0.02 * body_twist_factor
        pb_shoulder_l.rotation_mode = 'XYZ'
        pb_shoulder_l.location = Vector((sh_forward, sh_outward, 0.0))
        pb_shoulder_l.rotation_euler = Euler((
            math.radians(-10.0 + 20.0 * body_twist_factor),
            math.radians(10.0 - 5.0 * body_twist_factor),
            math.radians(15.0 - 30.0 * body_twist_factor)
        ), 'XYZ')
        pb_shoulder_l.keyframe_insert(data_path="location", frame=frame)
        pb_shoulder_l.keyframe_insert(data_path="rotation_euler", frame=frame)

        # 4. Offhand (Right Arm): Martial Counter-balance
        if pb_shoulder_r:
            pb_shoulder_r.rotation_mode = 'XYZ'
            pb_shoulder_r.location = Vector((-0.01 * body_twist_factor, 0.025, 0.0))
            pb_shoulder_r.rotation_euler = Euler((0, 0, math.radians(-10 - 25 * body_twist_factor)), 'XYZ')
            pb_shoulder_r.keyframe_insert(data_path="location", frame=frame)
            pb_shoulder_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_upperarm_r:
            pb_upperarm_r.rotation_mode = 'XYZ'
            pb_upperarm_r.rotation_euler = Euler((
                math.radians(-15.0 - 25.0 * body_twist_factor),
                math.radians(-10.0 - 15.0 * body_twist_factor),
                math.radians(-20.0 - 35.0 * body_twist_factor)
            ), 'XYZ')
            pb_upperarm_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_forearm_r:
            pb_forearm_r.rotation_mode = 'XYZ'
            pb_forearm_r.rotation_euler = Euler((math.radians(20.0 + 30.0 * body_twist_factor), 0, 0), 'XYZ')
            pb_forearm_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_hand_r:
            pb_hand_r.rotation_mode = 'XYZ'
            pb_hand_r.rotation_euler = Euler((0, 0, math.radians(-10.0 * body_twist_factor)), 'XYZ')
            pb_hand_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        # 5. Athletic Martial Footwork & Leg Stance (Ground Z >= 0.0)
        if pb_leg_l:
            pb_leg_l.rotation_euler = Euler((
                math.radians(10.0 - 20.0 * body_twist_factor),
                0,
                math.radians(15.0 - 25.0 * body_twist_factor)
            ), 'XYZ')
            pb_leg_l.keyframe_insert(data_path="rotation_euler", frame=frame)
        if pb_shin_l:
            pb_shin_l.rotation_euler = Euler((math.radians(10.0 * body_twist_factor), 0, 0), 'XYZ')
            pb_shin_l.keyframe_insert(data_path="rotation_euler", frame=frame)
        if pb_foot_l:
            pb_foot_l.rotation_euler = Euler((math.radians(-5.0 * body_twist_factor), 0, 0), 'XYZ')
            pb_foot_l.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_leg_r:
            pb_leg_r.rotation_euler = Euler((
                math.radians(-10.0 + 20.0 * body_twist_factor),
                0,
                math.radians(5.0 - 15.0 * body_twist_factor)
            ), 'XYZ')
            pb_leg_r.keyframe_insert(data_path="rotation_euler", frame=frame)
        if pb_shin_r:
            pb_shin_r.rotation_euler = Euler((math.radians(15.0 - 10.0 * body_twist_factor), 0, 0), 'XYZ')
            pb_shin_r.keyframe_insert(data_path="rotation_euler", frame=frame)
        if pb_foot_r:
            pb_foot_r.rotation_euler = Euler((math.radians(-5.0 + 5.0 * body_twist_factor), 0, 0), 'XYZ')
            pb_foot_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        bpy.context.view_layer.update()

        # 6. Hand.L Position on Expanded Radius (R = 0.35m)
        h_pos = C_base + Vector((-R * math.cos(th), R * math.sin(th), 0.0))

        # Evaluate current shoulder world position in evaluated scene
        sh_pos = pb_shoulder_l.matrix.to_translation()

        # 7. UpperArm.L and Forearm.L along line of action
        upper_mat, fore_mat = solve_arm_segments_mat(sh_pos, h_pos)
        set_bone_world_matrix(pb_upperarm_l, upper_mat)
        pb_upperarm_l.keyframe_insert(data_path="location", frame=frame)
        pb_upperarm_l.keyframe_insert(data_path="rotation_euler", frame=frame)
        bpy.context.view_layer.update()

        set_bone_world_matrix(pb_forearm_l, fore_mat)
        pb_forearm_l.keyframe_insert(data_path="location", frame=frame)
        pb_forearm_l.keyframe_insert(data_path="rotation_euler", frame=frame)
        bpy.context.view_layer.update()

        # 8. Exact Hand.L & Socket_Hand_L world matrix (with 180° rotated blade edge)
        sock_mat = solve_socket_hand_matrix_left(h_pos, th)
        hand_mat = solve_hand_matrix_from_socket(pb_hand_l, pb_socket_l, sock_mat)

        set_bone_world_matrix(pb_hand_l, hand_mat)
        pb_hand_l.keyframe_insert(data_path="location", frame=frame)
        pb_hand_l.keyframe_insert(data_path="rotation_euler", frame=frame)

        pb_socket_l.location = Vector((0, 0, 0))
        pb_socket_l.rotation_euler = Euler((0, 0, 0), 'XYZ')
        pb_socket_l.keyframe_insert(data_path="location", frame=frame)
        pb_socket_l.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Linear interpolation between dense frames for 100% velocity fidelity
    if act.fcurves:
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'

    print("Keyframed Attack_Round: Outward shoulder, martial torque, 180° katana edge, and ease-out recovery.")

    # --- TEMPORARY AUDIT SWORD ATTACHMENT VIA ARMATURE SKINNING ---
    audit_sword = create_temp_sword()
    audit_sword.parent = arm
    mod_sword = audit_sword.modifiers.new(name="Armature", type='ARMATURE')
    mod_sword.object = arm
    mod_sword.use_vertex_groups = True

    # --- MULTI-ANGLE 3-ROW FILMSTRIP GENERATION ---
    print("\n--- RENDERING 3-ROW CONTACT SHEET (attack_round_filmstrip.png) ---")
    filmstrip_frames = [1, 6, 9, 13, 17, 20, 24, 36]
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

    add_light("KeySun", 'SUN', (-2.0, 3.0, 4.0), 4.5, (1.0, 0.98, 0.92))
    add_light("FrontFill", 'POINT', (1.2, 2.2, 1.2), 75.0, (0.9, 0.95, 1.0))
    add_light("TopFill", 'POINT', (0.0, 0.0, 3.0), 45.0, (1.0, 1.0, 1.0))
    add_light("RimLight", 'POINT', (2.0, -2.0, 2.0), 60.0, (0.4, 0.8, 1.0))

    cam_data = bpy.data.cameras.new("FilmstripCam")
    cam_obj = bpy.data.objects.new("FilmstripCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # 3 views with automatic look-at pointing at character center (0, 0, 0.25)
    char_center = Vector((0.0, 0.0, 0.25))
    views = [
        ('top', Vector((0.0, 0.0, 1.6)), 'ORTHO', 1.15),
        ('front_34', Vector((-0.75, 1.15, 0.50)), 'PERSP', 0.85),
        ('front', Vector((0.0, 1.35, 0.28)), 'ORTHO', 0.85)
    ]

    rendered_images = []
    for row_idx, (vname, cam_pos, cam_type, ortho_scale) in enumerate(views):
        cam_obj.location = cam_pos
        point_camera_at(cam_obj, char_center)
        cam_data.type = cam_type
        if cam_type == 'ORTHO':
            cam_data.ortho_scale = ortho_scale
        else:
            cam_data.lens = 45

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

row_labels = ["TOP-DOWN (Expanded Arc R=0.35m & Outward Shoulder)", "FRONT 3/4 (Torso Twist +35° -> -50° & Martial Lean)", "FRONT ELEVATION (Floor Z >= 0.0m & Counter-balance)"]
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

    # --- EXPORT GLTF 2.0 (swordsman.glb) WITH Attack_Round AS PRIMARY NLA TRACK ---
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
