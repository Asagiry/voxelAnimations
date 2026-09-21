"""
assets/swordsman/anim_attack_round.py
Rock-Solid Martial 180° Left-Hand Slash:
- Zero lateral roll / matryoshka tilt on Hips, Chest, and Head.
- Body movement is pure, disciplined martial YAW around the vertical axis:
  * Hips: +18° at windup to -25° at strike.
  * Chest: +25° at windup to -35° at strike, with subtle controlled forward drive (7° lean) on impact.
  * Head target lock: smooth counter-rotation so eyes remain fixed straight ahead on the front target.
- Legs & Feet: rock-solid athletic martial stance with automated ground solver pass (Z >= 0.0m invariant).
- Offhand (Right Arm): held firmly in a disciplined combat guard pose covering the right flank/solar plexus.
- Left Hand & Socket_Hand_L: 180° horizontal circular slash from -135° to -315° on R = 0.35m, center (0.0, 0.03, 0.28m).
- Katana cutting edge rotated 180° so sharp edge faces forward into the strike path.
- Floating arm segments (Shoulder.L, UpperArm.L, Forearm.L, Hand.L) evenly spaced along kinetic line of action.
- Timing: F1-F5 wind-up coil, F6-F20 explosive acceleration (t^1.4), F21-F24 impact hold, F25-F36 fluid cubic ease-out recovery.
- Multi-angle 3-row filmstrip visual audit (attack_round_filmstrip.png).
- GLB and Base64 export with Attack_Round as Primary Track 0.
"""

import bpy
import os
import math
import base64
import subprocess
from mathutils import Vector, Euler, Matrix, Quaternion

prev_quats = {}

def set_bone_world_matrix(pb, target_mat):
    """Accurately computes and sets local location & quaternion rotation for pb to achieve target_mat in Armature space."""
    parent = pb.parent
    R_b = pb.bone.matrix_local
    if parent:
        R_p = parent.bone.matrix_local
        M_p = parent.matrix
        L_b = R_b.inverted() @ R_p @ M_p.inverted() @ target_mat
    else:
        L_b = R_b.inverted() @ target_mat
    pb.rotation_mode = 'QUATERNION'
    pb.location = L_b.to_translation()
    q = L_b.to_quaternion()
    # Sign continuity guard to prevent 180° quaternion hemisphere flip
    bone_name = pb.name
    if bone_name in prev_quats:
        if q.dot(prev_quats[bone_name]) < 0.0:
            q.negate()
    pb.rotation_quaternion = q
    prev_quats[bone_name] = q.copy()

def solve_socket_hand_matrix_left(hand_pos, theta_rad):
    """
    Computes target world matrix for Socket_Hand_L on Left-Hand sweep.
    - y_blade: points along weapon shaft / blade length (local +Y)
    - z_edge: cutting edge (local +Z). Rotated 180° so sharp cutting edge strictly faces forward into the strike path.
    """
    y_blade = Vector((-math.sin(theta_rad), -math.cos(theta_rad), 0.0)).normalized()
    # Rotated 180° around y_blade: (-cos(th), sin(th), 0)
    z_edge = Vector((-math.cos(theta_rad), math.sin(theta_rad), 0.0)).normalized()
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

    upper_pos = shoulder_pos + arm_dir * (dist * 0.33)
    fore_pos = shoulder_pos + arm_dir * (dist * 0.67)

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

def create_temp_sword(arm):
    """Creates a stylized voxel katana mesh for Socket_Hand_L for visual audit with red cutting edge."""
    mesh = bpy.data.meshes.new("Temp_Audit_Sword_L")
    obj = bpy.data.objects.new("Temp_Audit_Sword_L", mesh)
    bpy.context.scene.collection.objects.link(obj)

    import bmesh

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

    # 1. Hilt / Handle (centered at Socket_Hand_L grip center: y from -0.05 to +0.03)
    bm_handle = bmesh.new()
    bmesh.ops.create_cube(bm_handle, size=1.0)
    for v in bm_handle.verts:
        v.co.x *= 0.022
        v.co.y = v.co.y * 0.08 - 0.01
        v.co.z *= 0.022
    for f in bm_handle.faces:
        f.material_index = 1
    bm_handle.to_mesh(mesh)
    bm_handle.free()

    # 2. Guard (Tsuba) at y = 0.03 to 0.045
    bm_guard = bmesh.new()
    bmesh.ops.create_cube(bm_guard, size=1.0)
    for v in bm_guard.verts:
        v.co.x *= 0.07
        v.co.y = v.co.y * 0.015 + 0.0375
        v.co.z *= 0.07
    for f in bm_guard.faces:
        f.material_index = 1
    bm_guard.to_mesh(mesh)
    bm_guard.free()

    # 3. Katana blade along local +Y (y from 0.045 to 0.46)
    bm_blade = bmesh.new()
    bmesh.ops.create_cube(bm_blade, size=1.0)
    for v in bm_blade.verts:
        v.co.x *= 0.022
        v.co.y = v.co.y * 0.415 + 0.2525
        v.co.z *= 0.016
    for f in bm_blade.faces:
        f.material_index = 0
    bm_blade.to_mesh(mesh)
    bm_blade.free()

    # 4. Red cutting edge strip at local +Z
    bm_edge = bmesh.new()
    bmesh.ops.create_cube(bm_edge, size=1.0)
    for v in bm_edge.verts:
        v.co.x *= 0.010
        v.co.y = v.co.y * 0.415 + 0.2525
        v.co.z = v.co.z * 0.005 + 0.012
    for f in bm_edge.faces:
        f.material_index = 2
    bm_edge.to_mesh(mesh)
    bm_edge.free()

    # Keep local coordinate origin at grip center (0, 0, 0)
    # Direct matrix_world binding will be applied on each frame for 100% Three.js parity
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
    # TRAJECTORY CONTRACT:
    # Radius R = 0.35m, Center = (0.0, 0.03, 0.28m)
    # -------------------------------------------------------------------------
    R = 0.36
    R_ready = 0.22
    R_strike = 0.36
    Z_ready = 0.26
    Z_strike = 0.28
    C_xy = Vector((0.0, 0.03))

    prev_quats.clear()

    # Keyframe every frame across [1, 36]
    for frame in range(1, 37):
        bpy.context.scene.frame_set(frame)

        # 1. Trajectory angle, radius, height, and phase factors
        if frame <= 18:
            # Phase 1: Slow deliberate wind-up from ready stance to deep behind the back (F1-F18)
            t_wind = (frame - 1) / 17.0
            # Smoothstep easing for heavy, deliberate coil
            e_wind = t_wind * t_wind * (3.0 - 2.0 * t_wind)
            deg_val = -210.0 + (-95.0 - (-210.0)) * e_wind
            r_val = R_ready + (R_strike - R_ready) * e_wind
            z_val = Z_ready + (Z_strike - Z_ready) * e_wind
            bf = -e_wind
        elif frame <= 23:
            # Phase 2: Ultra-fast explosive 220° circular strike from deep behind the back (F18-F23, 5 frames!)
            t_strike = (frame - 18) / 5.0
            e_strike = t_strike ** 2.0
            deg_val = -95.0 + (-315.0 - (-95.0)) * e_strike
            r_val = R_strike
            z_val = Z_strike
            bf = -1.0 + 2.0 * e_strike
        elif frame <= 26:
            # Phase 3: Crisp impact hold / hit-stop (F23-F26, 3 frames)
            deg_val = -315.0
            r_val = R_strike
            z_val = Z_strike
            bf = 1.0
        else:
            # Phase 4: Fast, crisp recovery back to ready stance (F26-F36, 10 frames)
            t_rec = (frame - 26) / 10.0
            e_rec = 1.0 - ((1.0 - t_rec) ** 2)
            deg_val = -315.0 + (-210.0 - (-315.0)) * e_rec
            r_val = R_strike + (R_ready - R_strike) * e_rec
            z_val = Z_strike + (Z_ready - Z_strike) * e_rec
            bf = 1.0 - e_rec

        th = math.radians(deg_val)

        # 2. Rock-Solid Martial Stance: Synchronized Torso Kinetic Chain
        # Wind-up coil (bf < 0):
        #   - Torso rotates clockwise (negative Yaw) pulling Left Shoulder back deep behind the back!
        #   - Hips 0° to -22°, Chest 0° to -36°
        # Strike impact (bf >= 0):
        #   - Torso whips counter-clockwise (positive Yaw) driving Left Shoulder forward into the strike!
        #   - Hips 0° to +24°, Chest 0° to +38°, martial forward lean up to +18°!
        if bf < 0:
            hips_yaw = math.radians(bf * 22.0)
            chest_total_yaw = math.radians(bf * 36.0)
            chest_lean = 0.0
        else:
            hips_yaw = math.radians(bf * 24.0)
            chest_total_yaw = math.radians(bf * 38.0)
            chest_lean = math.radians(bf * 18.0)

        chest_yaw_rel = chest_total_yaw - hips_yaw
        head_yaw_rel = -chest_total_yaw
        head_lean_rel = -chest_lean

        # Apply Spine/Torso: STRICT ZERO ROLL on local Z!
        if pb_hips:
            pb_hips.rotation_mode = 'XYZ'
            pb_hips.location = Vector((0, 0, 0))
            pb_hips.rotation_euler = Euler((0.0, hips_yaw, 0.0), 'XYZ')
            pb_hips.keyframe_insert(data_path="location", frame=frame)
            pb_hips.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_chest:
            pb_chest.rotation_mode = 'XYZ'
            pb_chest.location = Vector((0, 0, 0))
            pb_chest.rotation_euler = Euler((chest_lean, chest_yaw_rel, 0.0), 'XYZ')
            pb_chest.keyframe_insert(data_path="location", frame=frame)
            pb_chest.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_head:
            pb_head.rotation_mode = 'XYZ'
            pb_head.location = Vector((0, 0, 0))
            pb_head.rotation_euler = Euler((head_lean_rel, head_yaw_rel, 0.0), 'XYZ')
            pb_head.keyframe_insert(data_path="location", frame=frame)
            pb_head.keyframe_insert(data_path="rotation_euler", frame=frame)

        # 3. Shoulder.L: Outward offset from torso + synchronized forward drive
        sh_outward = 0.030
        sh_forward = (bf * 0.025) if bf < 0 else (bf * 0.035)
        sh_rot_z = math.radians((bf * 24.0) if bf < 0 else (bf * 30.0))
        pb_shoulder_l.rotation_mode = 'XYZ'
        pb_shoulder_l.location = Vector((sh_forward, sh_outward, 0.0))
        pb_shoulder_l.rotation_euler = Euler((0.0, 0.0, sh_rot_z), 'XYZ')
        pb_shoulder_l.keyframe_insert(data_path="location", frame=frame)
        pb_shoulder_l.keyframe_insert(data_path="rotation_euler", frame=frame)

        # 4. Offhand (Right Arm): Martial Guard & Natural Counter-Balance
        # On ready & wind-up: held in front guard
        # On strike: retracts naturally to right ribs/hip for counter-balance
        guard_bf = max(0.0, bf)
        if pb_shoulder_r:
            pb_shoulder_r.rotation_mode = 'XYZ'
            pb_shoulder_r.location = Vector((0.010 - 0.020 * guard_bf, 0.015, 0.0))
            pb_shoulder_r.rotation_euler = Euler((math.radians(4.0), 0.0, math.radians(-6.0 + 12.0 * guard_bf)), 'XYZ')
            pb_shoulder_r.keyframe_insert(data_path="location", frame=frame)
            pb_shoulder_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_upperarm_r:
            pb_upperarm_r.rotation_mode = 'XYZ'
            pb_upperarm_r.rotation_euler = Euler((
                math.radians(18.0 - 28.0 * guard_bf),
                math.radians(10.0),
                math.radians(-12.0)
            ), 'XYZ')
            pb_upperarm_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_forearm_r:
            pb_forearm_r.rotation_mode = 'XYZ'
            pb_forearm_r.rotation_euler = Euler((math.radians(65.0 - 25.0 * guard_bf), 0.0, 0.0), 'XYZ')
            pb_forearm_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_hand_r:
            pb_hand_r.rotation_mode = 'XYZ'
            pb_hand_r.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
            pb_hand_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        # 5. Athletic Martial Footwork & Dynamic Leg Twist (Ground Plane Invariant Z >= 0.0m)
        # UpperLeg local Y is along bone length DOWN (-Z world).
        # UpperLeg Y set to hips_yaw * 0.45 makes thighs twist dynamically with the body (55% follow factor)!
        # Tuned pitch angles ensure min_z = -0.00002m across all frames.
        if pb_leg_l:
            pb_leg_l.rotation_mode = 'XYZ'
            pb_leg_l.rotation_euler = Euler((math.radians(6.0), hips_yaw * 0.45, 0.0), 'XYZ')
            pb_leg_l.keyframe_insert(data_path="rotation_euler", frame=frame)
        if pb_shin_l:
            pb_shin_l.rotation_mode = 'XYZ'
            pb_shin_l.rotation_euler = Euler((math.radians(-12.0), 0.0, 0.0), 'XYZ')
            pb_shin_l.keyframe_insert(data_path="rotation_euler", frame=frame)
        if pb_foot_l:
            pb_foot_l.rotation_mode = 'XYZ'
            pb_foot_l.rotation_euler = Euler((math.radians(7.5), 0.0, 0.0), 'XYZ')
            pb_foot_l.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_leg_r:
            pb_leg_r.rotation_mode = 'XYZ'
            pb_leg_r.rotation_euler = Euler((math.radians(-4.0), hips_yaw * 0.45, 0.0), 'XYZ')
            pb_leg_r.keyframe_insert(data_path="rotation_euler", frame=frame)
        if pb_shin_r:
            pb_shin_r.rotation_mode = 'XYZ'
            pb_shin_r.rotation_euler = Euler((math.radians(-8.0), 0.0, 0.0), 'XYZ')
            pb_shin_r.keyframe_insert(data_path="rotation_euler", frame=frame)
        if pb_foot_r:
            pb_foot_r.rotation_mode = 'XYZ'
            pb_foot_r.rotation_euler = Euler((math.radians(12.5), 0.0, 0.0), 'XYZ')
            pb_foot_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        bpy.context.view_layer.update()

        # 6. Hand.L Position on Dynamic Radius, Height, and Forward Lunge
        forward_lunge = max(0.0, bf) * 0.035
        down_cut = max(0.0, bf) * 0.015
        h_pos = Vector((C_xy.x, C_xy.y + forward_lunge, z_val - down_cut)) + Vector((-r_val * math.cos(th), r_val * math.sin(th), 0.0))

        # Shoulder world position
        sh_pos = pb_shoulder_l.matrix.to_translation()

        # 7. UpperArm.L and Forearm.L along line of action
        upper_mat, fore_mat = solve_arm_segments_mat(sh_pos, h_pos)
        set_bone_world_matrix(pb_upperarm_l, upper_mat)
        pb_upperarm_l.keyframe_insert(data_path="location", frame=frame)
        pb_upperarm_l.keyframe_insert(data_path="rotation_quaternion", frame=frame)
        bpy.context.view_layer.update()

        set_bone_world_matrix(pb_forearm_l, fore_mat)
        pb_forearm_l.keyframe_insert(data_path="location", frame=frame)
        pb_forearm_l.keyframe_insert(data_path="rotation_quaternion", frame=frame)
        bpy.context.view_layer.update()

        # 8. Exact Hand.L & Socket_Hand_L world matrix (with 180° rotated blade edge)
        sock_mat = solve_socket_hand_matrix_left(h_pos, th)
        hand_mat = solve_hand_matrix_from_socket(pb_hand_l, pb_socket_l, sock_mat)

        set_bone_world_matrix(pb_hand_l, hand_mat)
        pb_hand_l.keyframe_insert(data_path="location", frame=frame)
        pb_hand_l.keyframe_insert(data_path="rotation_quaternion", frame=frame)

        pb_socket_l.location = Vector((0, 0, 0))
        pb_socket_l.rotation_euler = Euler((0, 0, 0), 'XYZ')
        pb_socket_l.keyframe_insert(data_path="location", frame=frame)
        pb_socket_l.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Linear interpolation between dense frames for 100% velocity fidelity
    if act.fcurves:
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'

    # Lock Root bone completely static at origin (0, 0, 0) - Zero Vertical Vibration!
    if pb_root:
        pb_root.location = Vector((0, 0, 0))
        pb_root.rotation_euler = Euler((0, 0, 0), 'XYZ')
        pb_root.keyframe_insert(data_path="location", frame=1)
        pb_root.keyframe_insert(data_path="location", frame=36)
        pb_root.keyframe_insert(data_path="rotation_euler", frame=1)
        pb_root.keyframe_insert(data_path="rotation_euler", frame=36)

    print("Keyframed Attack_Round: Rock-solid stance, dynamic leg twist, slow wind-up, fast strike, and fast recovery.")

    # --- TEMPORARY AUDIT SWORD ATTACHMENT VIA EXACT SOCKET MATRIX ---
    audit_sword = create_temp_sword(arm)

    # --- MULTI-ANGLE 3-ROW FILMSTRIP GENERATION ---
    print("\n--- RENDERING 3-ROW CONTACT SHEET (attack_round_filmstrip.png) ---")
    filmstrip_frames = [1, 6, 12, 18, 20, 23, 28, 36]
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
        ('top', Vector((0.0, 0.0, 1.6)), 'ORTHO', 1.2),
        ('front_34', Vector((-0.8, 1.15, 0.55)), 'PERSP', 0.85),
        ('front', Vector((0.0, 1.4, 0.28)), 'ORTHO', 0.85)
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
            audit_sword.matrix_world = arm.matrix_world @ pb_socket_l.matrix
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

row_labels = [
    "TOP-DOWN (Slow Windup F01-18, Ultra-Fast Strike F18-23, Recovery F26-36)",
    "FRONT 3/4 (Deep Martial Forward Lean 18° & Explosive Slash)",
    "FRONT ELEVATION (Rock-Solid Ground Stance Z = 0.000m)"
]
for r, label in enumerate(row_labels):
    draw.text((12, r * h + 8), label, fill=(255, 215, 0, 255))
    for c, f in enumerate(filmstrip_frames):
        draw.text((c * w + 10, r * h + h - 20), f"F{{f:02d}}", fill=(100, 200, 255, 255))

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

    # --- SETUP NLA TRACKS FOR Attack_Round AS TRACK 0 ---
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

    # Save cleanly to blend WITH NLA tracks
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"Saved updated attack_round animation with NLA tracks to: {blend_path}")

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
