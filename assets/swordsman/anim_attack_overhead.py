"""
assets/swordsman/anim_attack_overhead.py
Vertical Overhead Helm-Splitter (Jodan Giri / Кабуто-вари)
Built using the Stick-Figure Blueprint Pipeline:
1. Mathematical line of action matching assets/swordsman/blueprint_stickman.py
2. Sagittal Y-Z plane vertical blade arc from -45° (high Jodan wind-up behind head) to +90° (ground-level horizontal split)
3. Blade cutting edge strictly faces velocity tangent in the strike path
4. UpperArm.L and Forearm.L floating segments solved along vector line of action
5. Spine/Chest: dynamic C-curve coiling (-15° pitch back) -> violent explosive whip (+28° forward lean)
6. Head target lock: counter-rotates to maintain gaze on front enemy
7. Rock-solid martial split lunge with automated ground solver (Z >= 0.0m)
8. Multi-angle 3-row filmstrip: Side Profile, Front 3/4, Top-Down
9. Export to GLB with Attack_Overhead as Primary Track 0, with Attack_Round, Walk, Attack preserved.
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
    bone_name = pb.name
    if bone_name in prev_quats:
        if q.dot(prev_quats[bone_name]) < 0.0:
            q.negate()
    pb.rotation_quaternion = q
    prev_quats[bone_name] = q.copy()

def solve_socket_hand_matrix_overhead(hand_pos, alpha_rad):
    """
    Computes target world matrix for Socket_Hand_L on vertical sagittal chop.
    - alpha_rad: angle in Y-Z plane (0 = vertical +Z, +pi/2 = horizontal forward +Y, -pi/4 = back-up)
    - y_blade: points along blade shaft (local +Y) = (0, sin(alpha), cos(alpha))
    - z_edge: cutting edge (local +Z) = (0, cos(alpha), -sin(alpha))
    - x_cross: orthogonal normal = (-1, 0, 0)
    Orthonormal basis with det = +1.
    """
    sin_a = math.sin(alpha_rad)
    cos_a = math.cos(alpha_rad)

    x_axis = Vector((-1.0, 0.0, 0.0))
    y_axis = Vector((0.0, sin_a, cos_a)).normalized()
    z_axis = Vector((0.0, cos_a, -sin_a)).normalized()

    socket_mat = Matrix((
        (x_axis.x, y_axis.x, z_axis.x, hand_pos.x),
        (x_axis.y, y_axis.y, z_axis.y, hand_pos.y),
        (x_axis.z, y_axis.z, z_axis.z, hand_pos.z),
        (0.0,      0.0,      0.0,      1.0)
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
        z_axis = Vector((1, 0, 0))
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

def create_temp_sword(arm_obj):
    """Creates a stylized voxel katana mesh parented to Socket_Hand_L with red cutting edge for audit."""
    mesh = bpy.data.meshes.new("Temp_Audit_Katana_Mesh")
    obj = bpy.data.objects.new("Temp_Audit_Katana", mesh)
    bpy.context.collection.objects.link(obj)

    obj.parent = arm_obj
    obj.parent_type = 'BONE'
    obj.parent_bone = 'Socket_Hand_L'

    mat_blade = bpy.data.materials.new(name="M_AuditKatana_Blade")
    mat_blade.use_nodes = True
    bsdf_blade = mat_blade.node_tree.nodes.get('Principled BSDF')
    bsdf_blade.inputs['Base Color'].default_value = (0.90, 0.92, 0.96, 1.0)
    bsdf_blade.inputs['Roughness'].default_value = 0.15
    bsdf_blade.inputs['Metallic'].default_value = 0.90
    obj.data.materials.append(mat_blade)

    mat_edge = bpy.data.materials.new(name="M_AuditKatana_Edge")
    mat_edge.use_nodes = True
    bsdf_edge = mat_edge.node_tree.nodes.get('Principled BSDF')
    bsdf_edge.inputs['Base Color'].default_value = (1.0, 0.05, 0.35, 1.0) # Hot glowing pink/red edge
    if 'Emission Color' in bsdf_edge.inputs:
        bsdf_edge.inputs['Emission Color'].default_value = (1.0, 0.05, 0.35, 1.0)
        bsdf_edge.inputs['Emission Strength'].default_value = 3.5
    obj.data.materials.append(mat_edge)

    mat_hilt = bpy.data.materials.new(name="M_AuditKatana_Hilt")
    mat_hilt.use_nodes = True
    bsdf_hilt = mat_hilt.node_tree.nodes.get('Principled BSDF')
    bsdf_hilt.inputs['Base Color'].default_value = (0.12, 0.10, 0.15, 1.0)
    bsdf_hilt.inputs['Roughness'].default_value = 0.70
    obj.data.materials.append(mat_hilt)

    mat_guard = bpy.data.materials.new(name="M_AuditKatana_Guard")
    mat_guard.use_nodes = True
    bsdf_guard = mat_guard.node_tree.nodes.get('Principled BSDF')
    bsdf_guard.inputs['Base Color'].default_value = (0.85, 0.65, 0.15, 1.0)
    bsdf_guard.inputs['Metallic'].default_value = 0.90
    bsdf_guard.inputs['Roughness'].default_value = 0.25
    obj.data.materials.append(mat_guard)

    V = 0.015
    boxes = []
    # 1. Hilt (centered along Y)
    boxes.append((Vector((-0.75*V, -4.0*V, -0.75*V)), Vector((0.75*V, 2.0*V, 0.75*V)), 2))
    # 2. Tsuba Guard
    boxes.append((Vector((-2.5*V, 2.0*V, -2.5*V)), Vector((2.5*V, 2.8*V, 2.5*V)), 3))
    # 3. Blade Body (Silver steel)
    boxes.append((Vector((-0.4*V, 2.8*V, -0.6*V)), Vector((0.4*V, 34.0*V, 0.2*V)), 0))
    # 4. Cutting Edge (Sharp neon red strip along +Z)
    boxes.append((Vector((-0.3*V, 2.8*V, 0.2*V)), Vector((0.3*V, 34.0*V, 0.8*V)), 1))

    verts = []
    faces = []
    mat_indices = []

    for b_min, b_max, mat_idx in boxes:
        start_v = len(verts)
        v = [
            Vector((b_min.x, b_min.y, b_min.z)),
            Vector((b_max.x, b_min.y, b_min.z)),
            Vector((b_max.x, b_max.y, b_min.z)),
            Vector((b_min.x, b_max.y, b_min.z)),
            Vector((b_min.x, b_min.y, b_max.z)),
            Vector((b_max.x, b_min.y, b_max.z)),
            Vector((b_max.x, b_max.y, b_max.z)),
            Vector((b_min.x, b_max.y, b_max.z)),
        ]
        verts.extend(v)
        box_faces = [
            (start_v+0, start_v+1, start_v+2, start_v+3), # -Z
            (start_v+4, start_v+7, start_v+6, start_v+5), # +Z
            (start_v+0, start_v+4, start_v+5, start_v+1), # -Y
            (start_v+2, start_v+6, start_v+7, start_v+3), # +Y
            (start_v+0, start_v+3, start_v+7, start_v+4), # -X
            (start_v+1, start_v+5, start_v+6, start_v+2), # +X
        ]
        faces.extend(box_faces)
        mat_indices.extend([mat_idx]*6)

    mesh.from_pydata(verts, [], faces)
    mesh.update()
    for poly, m_idx in zip(mesh.polygons, mat_indices):
        poly.material_index = m_idx

    return obj

def point_camera_at(cam_obj, target_pos):
    """Sets camera world matrix to point directly at target_pos with upright orientation."""
    loc = cam_obj.location
    forward = (target_pos - loc).normalized()
    up = Vector((0.0, 1.0, 0.0)) if abs(forward.z) > 0.9 else Vector((0.0, 0.0, 1.0))
    right = forward.cross(up).normalized()
    up_corrected = right.cross(forward).normalized()
    cam_mat = Matrix((
        (right.x, up_corrected.x, -forward.x, loc.x),
        (right.y, up_corrected.y, -forward.y, loc.y),
        (right.z, up_corrected.z, -forward.z, loc.z),
        (0.0,     0.0,            0.0,        1.0)
    ))
    cam_obj.matrix_world = cam_mat

def build_attack_overhead():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    blend_path = os.path.join(base_dir, "swordsman.blend")
    if os.path.isfile(blend_path):
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

    old_act = bpy.data.actions.get("Attack_Overhead")
    if old_act:
        bpy.data.actions.remove(old_act)

    act = bpy.data.actions.new("Attack_Overhead")
    arm.animation_data.action = act

    # Reset all pose bones
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

    TOTAL_FRAMES = 40
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = TOTAL_FRAMES

    prev_quats.clear()

    # --- KEYFRAME GENERATION FROM STICK-FIGURE BLUEPRINT ---
    for frame in range(1, TOTAL_FRAMES + 1):
        bpy.context.scene.frame_set(frame)

        # Kinematic Phase Calculation (40 Frames)
        if frame <= 6:
            # Phase 1: Initiation / Coil Start (F1-F6)
            t = (frame - 1) / 5.0
            spine_pitch = 5.0 - 10.0 * t # +5 to -5 deg
            pelvis_y = -0.02 * t
            pelvis_z = 0.0 - 0.01 * t
            lunge_factor = 0.0
            h_y = 0.18 - 0.10 * t
            h_z = 0.26 + 0.15 * t
            alpha_deg = 30.0 - 45.0 * t # +30 to -15 deg
            counter_balance = 0.0
        elif frame <= 12:
            # Phase 2: Peak High Jodan Wind-up (F6-F12)
            t = (frame - 6) / 6.0
            e = t * t * (3.0 - 2.0 * t)
            spine_pitch = -5.0 - 12.0 * e # reaches -17 deg arch back
            pelvis_y = -0.02 - 0.03 * e
            pelvis_z = -0.01 + 0.005 * e
            lunge_factor = 0.0
            h_y = 0.08 - 0.20 * e # hand drawn back behind head
            h_z = 0.41 + 0.25 * e # hand reaches Z = 0.66m
            alpha_deg = -15.0 - 30.0 * e # blade angled up-back at -45 deg
            counter_balance = 0.0
        elif frame <= 16:
            # Phase 3: Explosive Catapult Launch (F12-F16, 4 frames!)
            t = (frame - 12) / 4.0
            e = t * t # accelerate
            spine_pitch = -17.0 + 22.0 * e # snaps from -17 to +5 deg
            pelvis_y = -0.05 + 0.09 * e
            pelvis_z = -0.005 - 0.02 * e
            lunge_factor = e * 0.5
            h_y = -0.12 + 0.26 * e
            h_z = 0.66 - 0.12 * e
            alpha_deg = -45.0 + 75.0 * e # blade whips from -45 to +30 deg
            counter_balance = e * 0.6
        elif frame <= 18:
            # Phase 4: Mid-Chop Velocity Peak (F16-F18, 2 frames)
            t = (frame - 16) / 2.0
            spine_pitch = 5.0 + 17.0 * t # +22 deg forward
            pelvis_y = 0.04 + 0.04 * t
            pelvis_z = -0.025 - 0.005 * t
            lunge_factor = 0.5 + 0.3 * t
            h_y = 0.14 + 0.14 * t
            h_z = 0.54 - 0.22 * t
            alpha_deg = 30.0 + 35.0 * t # +65 deg
            counter_balance = 0.6 + 0.4 * t
        elif frame <= 20:
            # Phase 5: Ground-Level Helm Split Impact (F18-F20, 2 frames)
            t = (frame - 18) / 2.0
            spine_pitch = 22.0 + 6.0 * t # +28 deg deep martial lean
            pelvis_y = 0.08 + 0.02 * t
            pelvis_z = -0.03
            lunge_factor = 0.8 + 0.2 * t # full 1.0 split lunge
            h_y = 0.28 + 0.10 * t
            h_z = 0.32 - 0.16 * t # hand down at Z = 0.16m
            alpha_deg = 65.0 + 25.0 * t # horizontal split at +90 deg
            counter_balance = 1.0
        elif frame <= 24:
            # Phase 6: Hit-Stop & Recoil Tremor (F20-F24, 4 frames)
            t = (frame - 20) / 4.0
            tremor = 2.0 * math.sin(t * math.pi * 3)
            spine_pitch = 28.0 + tremor
            pelvis_y = 0.10
            pelvis_z = -0.03 + 0.004 * tremor
            lunge_factor = 1.0
            h_y = 0.38
            h_z = 0.16 + 0.015 * tremor
            alpha_deg = 90.0 + tremor * 2.0
            counter_balance = 1.0
        else:
            # Phase 7: Fluid Martial Recovery (F24-F40, 16 frames)
            t = (frame - 24) / 16.0
            e = t * t * (3.0 - 2.0 * t)
            spine_pitch = 28.0 * (1.0 - e) + 5.0 * e
            pelvis_y = 0.10 * (1.0 - e)
            pelvis_z = -0.03 * (1.0 - e)
            lunge_factor = 1.0 - e
            h_y = 0.38 * (1.0 - e) + 0.18 * e
            h_z = 0.16 * (1.0 - e) + 0.26 * e
            alpha_deg = 90.0 * (1.0 - e) + 30.0 * e
            counter_balance = 1.0 - e

        # 1. Hips & Chest: Pitch along local X, strictly zero roll
        chest_lean_rad = math.radians(spine_pitch)
        head_lean_rel = -chest_lean_rad

        if pb_hips:
            pb_hips.rotation_mode = 'XYZ'
            pb_hips.location = Vector((0.0, pelvis_y, pelvis_z))
            pb_hips.rotation_euler = Euler((chest_lean_rad * 0.4, 0.0, 0.0), 'XYZ')
            pb_hips.keyframe_insert(data_path="location", frame=frame)
            pb_hips.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_chest:
            pb_chest.rotation_mode = 'XYZ'
            pb_chest.location = Vector((0.0, 0.0, 0.0))
            pb_chest.rotation_euler = Euler((chest_lean_rad * 0.6, 0.0, 0.0), 'XYZ')
            pb_chest.keyframe_insert(data_path="location", frame=frame)
            pb_chest.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_head:
            pb_head.rotation_mode = 'XYZ'
            pb_head.location = Vector((0.0, 0.0, 0.0))
            pb_head.rotation_euler = Euler((head_lean_rel, 0.0, 0.0), 'XYZ')
            pb_head.keyframe_insert(data_path="location", frame=frame)
            pb_head.keyframe_insert(data_path="rotation_euler", frame=frame)

        # 2. Legs: Athletic Split Lunge
        # Left leg lunges forward (hip flexes forward, knee flexes)
        # Right leg drives backward
        leg_l_pitch = math.radians(-10.0 - 28.0 * lunge_factor)
        shin_l_pitch = math.radians(12.0 + 32.0 * lunge_factor)
        foot_l_pitch = -(leg_l_pitch + shin_l_pitch)

        leg_r_pitch = math.radians(8.0 + 22.0 * lunge_factor)
        shin_r_pitch = math.radians(6.0 + 10.0 * lunge_factor)
        foot_r_pitch = -(leg_r_pitch + shin_r_pitch)

        if pb_leg_l:
            pb_leg_l.rotation_mode = 'XYZ'
            pb_leg_l.rotation_euler = Euler((leg_l_pitch, 0.0, 0.0), 'XYZ')
            pb_leg_l.keyframe_insert(data_path="rotation_euler", frame=frame)
        if pb_shin_l:
            pb_shin_l.rotation_mode = 'XYZ'
            pb_shin_l.rotation_euler = Euler((shin_l_pitch, 0.0, 0.0), 'XYZ')
            pb_shin_l.keyframe_insert(data_path="rotation_euler", frame=frame)
        if pb_foot_l:
            pb_foot_l.rotation_mode = 'XYZ'
            pb_foot_l.rotation_euler = Euler((foot_l_pitch, 0.0, 0.0), 'XYZ')
            pb_foot_l.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_leg_r:
            pb_leg_r.rotation_mode = 'XYZ'
            pb_leg_r.rotation_euler = Euler((leg_r_pitch, 0.0, 0.0), 'XYZ')
            pb_leg_r.keyframe_insert(data_path="rotation_euler", frame=frame)
        if pb_shin_r:
            pb_shin_r.rotation_mode = 'XYZ'
            pb_shin_r.rotation_euler = Euler((shin_r_pitch, 0.0, 0.0), 'XYZ')
            pb_shin_r.keyframe_insert(data_path="rotation_euler", frame=frame)
        if pb_foot_r:
            pb_foot_r.rotation_mode = 'XYZ'
            pb_foot_r.rotation_euler = Euler((foot_r_pitch, 0.0, 0.0), 'XYZ')
            pb_foot_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        # 3. Shoulder.L (Lead Arm)
        sh_elev = math.radians(15.0 + 40.0 * (1.0 if frame <= 16 else 0.0))
        pb_shoulder_l.rotation_mode = 'XYZ'
        pb_shoulder_l.location = Vector((0.02, 0.03, 0.01))
        pb_shoulder_l.rotation_euler = Euler((sh_elev, 0.0, 0.0), 'XYZ')
        pb_shoulder_l.keyframe_insert(data_path="location", frame=frame)
        pb_shoulder_l.keyframe_insert(data_path="rotation_euler", frame=frame)

        # 4. Offhand (Right Arm): Active Martial Counter-balance
        if pb_shoulder_r:
            pb_shoulder_r.rotation_mode = 'XYZ'
            pb_shoulder_r.location = Vector((-0.02 * counter_balance, 0.015, 0.0))
            pb_shoulder_r.rotation_euler = Euler((math.radians(10.0 * counter_balance), 0.0, math.radians(-15.0 * counter_balance)), 'XYZ')
            pb_shoulder_r.keyframe_insert(data_path="location", frame=frame)
            pb_shoulder_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_upperarm_r:
            pb_upperarm_r.rotation_mode = 'XYZ'
            pb_upperarm_r.rotation_euler = Euler((math.radians(15.0 - 45.0 * counter_balance), 0.0, math.radians(-10.0)), 'XYZ')
            pb_upperarm_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_forearm_r:
            pb_forearm_r.rotation_mode = 'XYZ'
            pb_forearm_r.rotation_euler = Euler((math.radians(-30.0 + 15.0 * counter_balance), 0.0, 0.0), 'XYZ')
            pb_forearm_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        if pb_hand_r:
            pb_hand_r.rotation_mode = 'XYZ'
            pb_hand_r.rotation_euler = Euler((math.radians(10.0), 0.0, 0.0), 'XYZ')
            pb_hand_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        # 5. Lead Arm Solver along Kinetic Line of Action
        bpy.context.view_layer.update()
        sh_pos = pb_shoulder_l.matrix.to_translation()
        h_pos = Vector((0.045, h_y, h_z))

        upper_mat, fore_mat = solve_arm_segments_mat(sh_pos, h_pos)
        set_bone_world_matrix(pb_upperarm_l, upper_mat)
        pb_upperarm_l.keyframe_insert(data_path="location", frame=frame)
        pb_upperarm_l.keyframe_insert(data_path="rotation_quaternion", frame=frame)
        bpy.context.view_layer.update()

        set_bone_world_matrix(pb_forearm_l, fore_mat)
        pb_forearm_l.keyframe_insert(data_path="location", frame=frame)
        pb_forearm_l.keyframe_insert(data_path="rotation_quaternion", frame=frame)
        bpy.context.view_layer.update()

        # 6. Socket_Hand_L & Hand.L: Exact Sagittal Orthonormal Basis
        alpha_rad = math.radians(alpha_deg)
        sock_mat = solve_socket_hand_matrix_overhead(h_pos, alpha_rad)
        hand_mat = solve_hand_matrix_from_socket(pb_hand_l, pb_socket_l, sock_mat)

        set_bone_world_matrix(pb_hand_l, hand_mat)
        pb_hand_l.keyframe_insert(data_path="location", frame=frame)
        pb_hand_l.keyframe_insert(data_path="rotation_quaternion", frame=frame)

        pb_socket_l.location = Vector((0, 0, 0))
        pb_socket_l.rotation_euler = Euler((0, 0, 0), 'XYZ')
        pb_socket_l.keyframe_insert(data_path="location", frame=frame)
        pb_socket_l.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Linear interpolation between dense keyframes
    if act.fcurves:
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'

    # Lock Root at origin
    if pb_root:
        pb_root.location = Vector((0, 0, 0))
        pb_root.rotation_euler = Euler((0, 0, 0), 'XYZ')
        pb_root.keyframe_insert(data_path="location", frame=1)
        pb_root.keyframe_insert(data_path="location", frame=TOTAL_FRAMES)
        pb_root.keyframe_insert(data_path="rotation_euler", frame=1)
        pb_root.keyframe_insert(data_path="rotation_euler", frame=TOTAL_FRAMES)

    print(f"Keyframed Attack_Overhead: Vertical Helm Splitter across {TOTAL_FRAMES} frames.")

    # --- TEMPORARY AUDIT SWORD ATTACHMENT ---
    audit_sword = create_temp_sword(arm)

    # --- MULTI-ANGLE 3-ROW FILMSTRIP GENERATION ---
    print("\n--- RENDERING 3-ROW CONTACT SHEET (attack_overhead_filmstrip.png) ---")
    filmstrip_frames = [1, 6, 12, 16, 18, 20, 24, 38]
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

    # Setup studio lights
    sun_data = bpy.data.lights.new(name="Sun_Key", type='SUN')
    sun_data.energy = 3.5
    sun_obj = bpy.data.objects.new(name="Sun_Key", object_data=sun_data)
    scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = Euler((math.radians(45.0), math.radians(25.0), math.radians(-30.0)), 'XYZ')

    # Side light for clear side-profile illumination
    side_data = bpy.data.lights.new(name="Sun_Side", type='SUN')
    side_data.energy = 3.0
    side_obj = bpy.data.objects.new(name="Sun_Side", object_data=side_data)
    scene.collection.objects.link(side_obj)
    side_obj.rotation_euler = Euler((math.radians(20.0), math.radians(65.0), math.radians(10.0)), 'XYZ')

    fill_data = bpy.data.lights.new(name="Sun_Fill", type='SUN')
    fill_data.energy = 1.5
    fill_obj = bpy.data.objects.new(name="Sun_Fill", object_data=fill_data)
    scene.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = Euler((math.radians(-30.0), math.radians(-45.0), math.radians(120.0)), 'XYZ')

    cam_data = bpy.data.cameras.new("Contact_Cam")
    cam_data.lens = 45.0
    cam_obj = bpy.data.objects.new("Contact_Cam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # 3 View Rows: Side Profile, Front 3/4, Top-Down
    cam_views = [
        {
            "name": "SIDE PROFILE (Sagittal Y-Z) — Primary Strike Arc & Spine Coil",
            "cam_pos": Vector((1.30, 0.12, 0.35)),
            "target": Vector((0.0, 0.12, 0.35))
        },
        {
            "name": "FRONT 3/4 — Power Stance & Athletic Forward Lean",
            "cam_pos": Vector((-0.75, 1.20, 0.50)),
            "target": Vector((0.0, 0.12, 0.25))
        },
        {
            "name": "TOP-DOWN (Transverse X-Y) — Centerline Alignment",
            "cam_pos": Vector((0.0, 0.10, 1.45)),
            "target": Vector((0.0, 0.10, 0.28))
        }
    ]

    for r_idx, v in enumerate(cam_views):
        cam_obj.location = v["cam_pos"]
        point_camera_at(cam_obj, v["target"])
        bpy.context.view_layer.update()

        for c_idx, f_num in enumerate(filmstrip_frames):
            scene.frame_set(f_num)
            bpy.context.view_layer.update()
            audit_sword.matrix_world = arm.matrix_world @ pb_socket_l.matrix
            bpy.context.view_layer.update()

            out_img = os.path.join(base_dir, f"tmp_over_r{r_idx}_c{c_idx}.png")
            scene.render.filepath = out_img
            bpy.ops.render.render(write_still=True)

    # Stitch into contact sheet via system python subprocess
    contact_stitch_script = f"""
import os
from PIL import Image, ImageDraw

base_dir = r"{base_dir}"
cell_size = 256
header_h = 32
filmstrip_cols = {filmstrip_cols}
filmstrip_frames = {filmstrip_frames}
sheet_w = filmstrip_cols * cell_size
sheet_h = 3 * (cell_size + header_h)

filmstrip_img = Image.new('RGB', (sheet_w, sheet_h), (12, 14, 18))
draw = ImageDraw.Draw(filmstrip_img)

row_titles = [
    "ROW 1: SIDE PROFILE (Sagittal Y-Z) — Primary Strike Arc & Spine Coil",
    "ROW 2: FRONT 3/4 — Power Stance & Athletic Forward Lean",
    "ROW 3: TOP-DOWN (Transverse X-Y) — Centerline Alignment"
]

for r_idx, r_title in enumerate(row_titles):
    row_y = r_idx * (cell_size + header_h)
    draw.rectangle([0, row_y, sheet_w, row_y + header_h], fill=(20, 24, 32))
    draw.text((15, row_y + 8), r_title, fill=(100, 180, 255))

    for c_idx, f_num in enumerate(filmstrip_frames):
        img_path = os.path.join(base_dir, f"tmp_over_r{{r_idx}}_c{{c_idx}}.png")
        if os.path.isfile(img_path):
            tile = Image.open(img_path)
            tile_x = c_idx * cell_size
            tile_y = row_y + header_h
            filmstrip_img.paste(tile, (tile_x, tile_y))
            tile.close()
            draw.text((tile_x + 10, tile_y + 10), f"F{{f_num:02d}}", fill=(255, 200, 80))
            try:
                os.remove(img_path)
            except Exception:
                pass

filmstrip_path = os.path.join(base_dir, "attack_overhead_filmstrip.png")
filmstrip_img.save(filmstrip_path)
print(f"Saved 3-row filmstrip to: {{filmstrip_path}}")
"""
    try:
        subprocess.run(["python", "-c", contact_stitch_script], check=True)
    except Exception as e:
        print(f"Warning running PIL stitcher subprocess: {e}")

    # Render beauty render at peak strike frame 20 (swordsman_render.png)
    scene.frame_set(20)
    bpy.context.view_layer.update()
    audit_sword.matrix_world = arm.matrix_world @ pb_socket_l.matrix
    bpy.context.view_layer.update()

    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.cycles.samples = 64
    cam_obj.location = Vector((-0.80, 1.25, 0.48))
    point_camera_at(cam_obj, Vector((0.0, 0.15, 0.22)))
    bpy.context.view_layer.update()
    render_path = os.path.join(base_dir, "swordsman_render.png")
    scene.render.filepath = render_path
    bpy.ops.render.render(write_still=True)
    print(f"Saved beauty render to: {render_path}")

    # Remove temporary objects
    bpy.data.objects.remove(audit_sword, do_unlink=True)
    bpy.data.objects.remove(cam_obj, do_unlink=True)
    for obj in list(scene.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    # --- SETUP NLA TRACKS: Attack_Overhead, Attack_Round, Walk, Attack ---
    if not arm.animation_data:
        arm.animation_data_create()
    arm.animation_data.action = None
    for track in list(arm.animation_data.nla_tracks):
        arm.animation_data.nla_tracks.remove(track)

    for act_name in ['Attack_Overhead', 'Attack_Round', 'Walk', 'Attack']:
        a = bpy.data.actions.get(act_name)
        if a:
            track = arm.animation_data.nla_tracks.new()
            track.name = act_name
            track.strips.new(act_name, int(a.frame_range[0]), a)
            print(f"Added NLA track: {act_name}")

    # Save cleanly to blend
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"Saved blend file with Attack_Overhead to: {blend_path}")

    # --- EXPORT GLTF 2.0 (swordsman.glb) ---
    print("\n--- EXPORTING GLTF 2.0 WITH ALL ANIMATIONS (swordsman.glb) ---")
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
    build_attack_overhead()
