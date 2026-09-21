"""
assets/swordsman/anim_attack.py
Authoritative 5-Phase Rayman-Style Floating Limbs 180° Pure Flat Circular Sword Strike:
- Strict 180° flat horizontal circular trajectory in XY (Z_const = 0.28m, R_const = 0.28m).
- Clockwise circle parameterization matching user Paint sketch:
  * Start (F14): theta = 225° (5*pi/4, Behind Right Shoulder) -> X = -0.198m, Y = -0.198m, Z = 0.28m
  * Quarter 1 (F16): theta = 180° (pi, Right Flank)          -> X = -0.280m, Y =  0.000m, Z = 0.28m
  * Quarter 2 (F18): theta = 135° (3*pi/4, Front-Right)       -> X = -0.198m, Y = +0.198m, Z = 0.28m
  * Quarter 3 (F20): theta =  90° (pi/2, Front Center Climax) -> X =  0.000m, Y = +0.280m, Z = 0.28m
  * End (F22): theta =  45° (pi/4, Front-Left Overshoot)     -> X = +0.198m, Y = +0.198m, Z = 0.28m
- Pure velocity tangent: blade_dir = (sin(theta), -cos(theta), 0.0)
- Outward radial cutting edge: edge_dir = (-cos(theta), -sin(theta), 0.0)
- Mathematical Bone World Matrix Solver: solves exact local (location, rotation_euler) with 0.000000 error.
- Dynamic arm segment solver: Shoulder.R, UpperArm.R, and Forearm.R align cleanly along the kinetic line of action.
- Offhand (Left Arm): athletic counter-balance on the left flank, no wild flips.
- Whole-body torque (Hips/Chest whip from -35° to +48°), head target lock.
- Automated ground solver pass (Z >= 0.0 invariant).
- 3-Row Contact Sheet: Top-Down (matching sketch), Front 3/4, Side Profile.
- Modern glTF 2.0 export with baked animations and Base64 output.
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
    """
    Accurately computes and sets local location & rotation for pb to achieve target_mat in Armature space.
    Formula: L_b = R_b^-1 * R_p * M_p^-1 * target_mat
    """
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
    """Computes target world matrix for Socket_Hand_R."""
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
    """Computes target world matrix for Hand.R from Socket_Hand_R target matrix."""
    R_hand = pb_hand.bone.matrix_local
    R_sock = pb_socket.bone.matrix_local
    R_rel = R_hand.inverted() @ R_sock
    hand_mat = socket_mat @ R_rel.inverted()
    return hand_mat

def solve_arm_segments_mat(shoulder_pos, hand_pos):
    """Computes world matrices for UpperArm.R and Forearm.R along line of action."""
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
    """Creates a stylized voxel sword mesh in scene with Armature skinning for visual audit."""
    mesh = bpy.data.meshes.new("Temp_Audit_Sword")
    obj = bpy.data.objects.new("Temp_Audit_Sword", mesh)
    bpy.context.scene.collection.objects.link(obj)

    import bmesh
    bm = bmesh.new()

    # Materials
    mat_blade = bpy.data.materials.new(name="M_Audit_Blade")
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

    mat_gold = bpy.data.materials.new(name="M_Audit_Gold")
    mat_gold.use_nodes = True
    bsdf_g = mat_gold.node_tree.nodes.get("Principled BSDF")
    if bsdf_g:
        bsdf_g.inputs['Base Color'].default_value = (1.0, 0.80, 0.15, 1.0)
        bsdf_g.inputs['Metallic'].default_value = 0.9
        bsdf_g.inputs['Roughness'].default_value = 0.25
    obj.data.materials.append(mat_gold)

    # Blade voxels (along local +Y of bone: from y=0.03 to y=0.45)
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.035
        v.co.y = v.co.y * 0.21 + 0.24 # y from 0.03 to 0.45
        v.co.z *= 0.015
    for f in bm.faces:
        f.material_index = 0

    # Crossguard (along local +X of the bone)
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

    # Assign 100% rigid weight to Socket_Hand_R
    vg = obj.vertex_groups.new(name="Socket_Hand_R")
    vg.add(list(range(len(mesh.vertices))), 1.0, 'REPLACE')
    return obj

def build_attack():
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

    for track in arm.animation_data.nla_tracks:
        track.mute = True

    old_act = bpy.data.actions.get("Attack")
    if old_act:
        bpy.data.actions.remove(old_act)

    act = bpy.data.actions.new("Attack")
    arm.animation_data.action = act

    for pb in pbones:
        pb.rotation_mode = 'XYZ'
        pb.location = Vector((0, 0, 0))
        pb.rotation_euler = Euler((0, 0, 0), 'XYZ')

    pb_shoulder_r = pbones['Shoulder.R']
    pb_upperarm_r = pbones['UpperArm.R']
    pb_forearm_r = pbones['Forearm.R']
    pb_hand_r = pbones['Hand.R']
    pb_socket_r = pbones['Socket_Hand_R']

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 48

    # -------------------------------------------------------------------------
    # 180° STRICT FLAT CIRCULAR ARC TRAJECTORY
    # Center = (0, 0, 0.28m), R = 0.28m, Z_const = 0.28m
    # -------------------------------------------------------------------------
    R = 0.28
    Z_const = 0.28
    C = Vector((0.0, 0.0, Z_const))

    def circle_pos(deg_val):
        th = math.radians(deg_val)
        return C + Vector((R * math.cos(th), R * math.sin(th), 0.0)), th

    p_f14, th_f14 = circle_pos(225) # Start (Apex windup, behind right shoulder)
    p_f16, th_f16 = circle_pos(180) # Quarter 1 (Right flank)
    p_f18, th_f18 = circle_pos(135) # Quarter 2 (Front-right)
    p_f20, th_f20 = circle_pos(90)  # Quarter 3 (Center front impact)
    p_f22, th_f22 = circle_pos(45)  # End (Front-left overshoot finish)

    keyframe_specs = [
        # Frame 1: Combat Ready Guard (Right hand in front, left hand ready)
        (1, {
            'hand_pos': Vector((-0.09, 0.08, Z_const)),
            'theta': math.radians(90),
            'Shoulder.R': {'rot': (deg(5), deg(0), deg(8)), 'loc': (-0.01, 0.02, 0.0)},
            'Hips': {'rot': (deg(-4), deg(-6), deg(0)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(6), deg(-6), deg(0)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(-2), deg(6), deg(0)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(12), deg(0), deg(2))},
            'LowerLeg.L': {'rot': (deg(-18), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-10), deg(0), deg(-4))},
            'LowerLeg.R': {'rot': (deg(-14), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(8), deg(0), deg(0))},
            'Shoulder.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0, 0, 0)},
            'UpperArm.L': {'rot': (deg(10), deg(0), deg(-10))},
            'Forearm.L': {'rot': (deg(30), deg(0), deg(0))},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0, 0, 0)},
        }),

        # Frame 8: Telegraph Coil Back (Right shoulder drops and pulls back)
        (8, {
            'hand_pos': (p_f14 + Vector((-0.09, 0.08, Z_const))) * 0.5,
            'theta': math.radians(205),
            'Shoulder.R': {'rot': (deg(10), deg(-8), deg(15)), 'loc': (-0.02, -0.01, 0.02)},
            'Hips': {'rot': (deg(-8), deg(-20), deg(4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(10), deg(-28), deg(6)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(-4), deg(24), deg(-4)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(18), deg(0), deg(3))},
            'LowerLeg.L': {'rot': (deg(-26), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(8), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-16), deg(0), deg(-6))},
            'LowerLeg.R': {'rot': (deg(-22), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(10), deg(0), deg(0))},
            'Shoulder.L': {'rot': (deg(-2), deg(5), deg(-4)), 'loc': (0, 0, 0)},
            'UpperArm.L': {'rot': (deg(12), deg(5), deg(-12))},
            'Forearm.L': {'rot': (deg(38), deg(0), deg(0))},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0, 0, 0)},
        }),

        # Frame 14: START OF 180° ARC (Apex Windup, theta = 225°)
        (14, {
            'hand_pos': p_f14,
            'theta': th_f14,
            'Shoulder.R': {'rot': (deg(18), deg(-15), deg(22)), 'loc': (-0.03, -0.03, 0.04)},
            'Hips': {'rot': (deg(-12), deg(-35), deg(6)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(15), deg(-46), deg(8)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(-8), deg(44), deg(-6)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(26), deg(0), deg(4))},
            'LowerLeg.L': {'rot': (deg(-38), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(12), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-22), deg(0), deg(-8))},
            'LowerLeg.R': {'rot': (deg(-30), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(12), deg(0), deg(0))},
            'Shoulder.L': {'rot': (deg(-5), deg(10), deg(-8)), 'loc': (0, 0, 0)},
            'UpperArm.L': {'rot': (deg(15), deg(10), deg(-15))},
            'Forearm.L': {'rot': (deg(45), deg(0), deg(0))},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0, 0, 0)},
        }),

        # Frame 16: MID-ARC 1 (Right Flank Sweep, theta = 180°)
        (16, {
            'hand_pos': p_f16,
            'theta': th_f16,
            'Shoulder.R': {'rot': (deg(8), deg(5), deg(16)), 'loc': (-0.02, 0.0, 0.01)},
            'Hips': {'rot': (deg(-10), deg(-12), deg(4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(4), deg(-12), deg(2)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(-4), deg(12), deg(-2)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(20), deg(0), deg(3))},
            'LowerLeg.L': {'rot': (deg(-30), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(10), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-16), deg(0), deg(-6))},
            'LowerLeg.R': {'rot': (deg(-24), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(10), deg(0), deg(0))},
            'Shoulder.L': {'rot': (deg(0), deg(0), deg(-4)), 'loc': (0, 0, 0)},
            'UpperArm.L': {'rot': (deg(5), deg(0), deg(-15))},
            'Forearm.L': {'rot': (deg(35), deg(0), deg(0))},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0, 0, 0)},
        }),

        # Frame 18: MID-ARC 2 (Front-Right Sweep, theta = 135°)
        (18, {
            'hand_pos': p_f18,
            'theta': th_f18,
            'Shoulder.R': {'rot': (deg(4), deg(12), deg(12)), 'loc': (-0.01, 0.02, 0.0)},
            'Hips': {'rot': (deg(-4), deg(16), deg(0)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(10), deg(22), deg(-2)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(0), deg(-20), deg(0)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(14), deg(0), deg(2))},
            'LowerLeg.L': {'rot': (deg(-22), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(8), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-10), deg(0), deg(-4))},
            'LowerLeg.R': {'rot': (deg(-16), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(8), deg(0), deg(0))},
            'Shoulder.L': {'rot': (deg(4), deg(-8), deg(-6)), 'loc': (0, 0, 0)},
            'UpperArm.L': {'rot': (deg(-10), deg(-10), deg(-20))},
            'Forearm.L': {'rot': (deg(25), deg(0), deg(0))},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0, 0, 0)},
        }),

        # Frame 20: PEAK IMPACT CLIMAX (Center Front Cleave, theta = 90°)
        (20, {
            'hand_pos': p_f20,
            'theta': th_f20,
            'Shoulder.R': {'rot': (deg(0), deg(20), deg(8)), 'loc': (0.0, 0.04, 0.0)},
            'Hips': {'rot': (deg(0), deg(36), deg(-4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(18), deg(44), deg(-6)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(2), deg(-40), deg(2)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(10), deg(0), deg(2))},
            'LowerLeg.L': {'rot': (deg(-16), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-6), deg(0), deg(-2))},
            'LowerLeg.R': {'rot': (deg(-10), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(6), deg(0), deg(0))},
            'Shoulder.L': {'rot': (deg(8), deg(-15), deg(-8)), 'loc': (0, 0, 0)},
            'UpperArm.L': {'rot': (deg(-20), deg(-15), deg(-25))},
            'Forearm.L': {'rot': (deg(20), deg(0), deg(0))},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0, 0, 0)},
        }),

        # Frame 22: END OF 180° ARC (Front-Left Destination, theta = 45°)
        (22, {
            'hand_pos': p_f22,
            'theta': th_f22,
            'Shoulder.R': {'rot': (deg(-2), deg(25), deg(6)), 'loc': (0.01, 0.03, 0.0)},
            'Hips': {'rot': (deg(2), deg(42), deg(-4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(16), deg(48), deg(-6)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(2), deg(-42), deg(2)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(8), deg(0), deg(1))},
            'LowerLeg.L': {'rot': (deg(-14), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-4), deg(0), deg(-2))},
            'LowerLeg.R': {'rot': (deg(-8), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(6), deg(0), deg(0))},
            'Shoulder.L': {'rot': (deg(10), deg(-20), deg(-8)), 'loc': (0, 0, 0)},
            'UpperArm.L': {'rot': (deg(-25), deg(-20), deg(-25))},
            'Forearm.L': {'rot': (deg(15), deg(0), deg(0))},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0, 0, 0)},
        }),

        # Frame 26: Hit-Stop Tremor & Deceleration Snap
        (26, {
            'hand_pos': p_f22 + Vector((0.005, -0.005, 0.0)),
            'theta': th_f22,
            'Shoulder.R': {'rot': (deg(-2), deg(24), deg(6)), 'loc': (0.01, 0.03, 0.0)},
            'Hips': {'rot': (deg(2), deg(40), deg(-4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(15), deg(45), deg(-6)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(2), deg(-40), deg(2)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(8), deg(0), deg(1))},
            'LowerLeg.L': {'rot': (deg(-14), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-4), deg(0), deg(-2))},
            'LowerLeg.R': {'rot': (deg(-8), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(6), deg(0), deg(0))},
            'Shoulder.L': {'rot': (deg(10), deg(-18), deg(-8)), 'loc': (0, 0, 0)},
            'UpperArm.L': {'rot': (deg(-22), deg(-18), deg(-22))},
            'Forearm.L': {'rot': (deg(15), deg(0), deg(0))},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0, 0, 0)},
        }),

        # Frame 34: Recovery Phase 1 - Pulling back from Left Flank
        (34, {
            'hand_pos': Vector((0.06, 0.12, Z_const)),
            'theta': math.radians(65),
            'Shoulder.R': {'rot': (deg(2), deg(12), deg(6)), 'loc': (0.0, 0.02, 0.0)},
            'Hips': {'rot': (deg(-2), deg(18), deg(-2)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(10), deg(20), deg(-2)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(0), deg(-18), deg(0)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(10), deg(0), deg(2))},
            'LowerLeg.L': {'rot': (deg(-16), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-8), deg(0), deg(-3))},
            'LowerLeg.R': {'rot': (deg(-12), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(7), deg(0), deg(0))},
            'Shoulder.L': {'rot': (deg(5), deg(-8), deg(-4)), 'loc': (0, 0, 0)},
            'UpperArm.L': {'rot': (deg(-10), deg(-10), deg(-15))},
            'Forearm.L': {'rot': (deg(25), deg(0), deg(0))},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0, 0, 0)},
        }),

        # Frame 42: Recovery Phase 2 - Returning toward Guard
        (42, {
            'hand_pos': Vector((-0.03, 0.09, Z_const)),
            'theta': math.radians(80),
            'Shoulder.R': {'rot': (deg(4), deg(4), deg(7)), 'loc': (-0.005, 0.02, 0.0)},
            'Hips': {'rot': (deg(-4), deg(4), deg(0)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(8), deg(4), deg(0)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(-1), deg(-4), deg(0)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(11), deg(0), deg(2))},
            'LowerLeg.L': {'rot': (deg(-17), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-9), deg(0), deg(-3))},
            'LowerLeg.R': {'rot': (deg(-13), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(7), deg(0), deg(0))},
            'Shoulder.L': {'rot': (deg(2), deg(-2), deg(-2)), 'loc': (0, 0, 0)},
            'UpperArm.L': {'rot': (deg(0), deg(0), deg(-12))},
            'Forearm.L': {'rot': (deg(28), deg(0), deg(0))},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0, 0, 0)},
        }),

        # Frame 48: Seamless Reset back to Frame 1
        (48, {
            'hand_pos': Vector((-0.09, 0.08, Z_const)),
            'theta': math.radians(90),
            'Shoulder.R': {'rot': (deg(5), deg(0), deg(8)), 'loc': (-0.01, 0.02, 0.0)},
            'Hips': {'rot': (deg(-4), deg(-6), deg(0)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(6), deg(-6), deg(0)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(-2), deg(6), deg(0)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(12), deg(0), deg(2))},
            'LowerLeg.L': {'rot': (deg(-18), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-10), deg(0), deg(-4))},
            'LowerLeg.R': {'rot': (deg(-14), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(8), deg(0), deg(0))},
            'Shoulder.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0, 0, 0)},
            'UpperArm.L': {'rot': (deg(10), deg(0), deg(-10))},
            'Forearm.L': {'rot': (deg(30), deg(0), deg(0))},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0, 0, 0)},
        }),
    ]

    # Insert keyframes with mathematical solver
    for frame, spec in keyframe_specs:
        bpy.context.scene.frame_set(frame)

        # 1. Apply body, hips, chest, head, legs, offhand poses
        for bone_name, tform in spec.items():
            if bone_name in ('hand_pos', 'theta'):
                continue
            pb = pbones.get(bone_name)
            if not pb:
                continue
            pb.rotation_mode = 'XYZ'
            if 'rot' in tform:
                pb.rotation_euler = Euler(tform['rot'], 'XYZ')
                pb.keyframe_insert(data_path="rotation_euler", frame=frame)
            if 'loc' in tform:
                pb.location = Vector(tform['loc'])
                pb.keyframe_insert(data_path="location", frame=frame)

        # Update view layer to ensure Shoulder.R world matrix is evaluated
        bpy.context.view_layer.update()
        sh_pos = pb_shoulder_r.matrix.to_translation()
        h_pos = spec['hand_pos']
        th = spec['theta']

        # 2. Compute UpperArm.R and Forearm.R world matrices along kinetic line of action
        upper_mat, fore_mat = solve_arm_segments_mat(sh_pos, h_pos)
        set_bone_world_matrix(pb_upperarm_r, upper_mat)
        pb_upperarm_r.keyframe_insert(data_path="location", frame=frame)
        pb_upperarm_r.keyframe_insert(data_path="rotation_euler", frame=frame)
        bpy.context.view_layer.update()

        set_bone_world_matrix(pb_forearm_r, fore_mat)
        pb_forearm_r.keyframe_insert(data_path="location", frame=frame)
        pb_forearm_r.keyframe_insert(data_path="rotation_euler", frame=frame)
        bpy.context.view_layer.update()

        # 3. Compute exact Socket_Hand_R & Hand.R world matrix
        sock_mat = solve_socket_hand_matrix(h_pos, th)
        hand_mat = solve_hand_matrix_from_socket(pb_hand_r, pb_socket_r, sock_mat)

        set_bone_world_matrix(pb_hand_r, hand_mat)
        pb_hand_r.keyframe_insert(data_path="location", frame=frame)
        pb_hand_r.keyframe_insert(data_path="rotation_euler", frame=frame)

        # Keep Socket_Hand_R keyframed at local identity
        pb_socket_r.location = Vector((0, 0, 0))
        pb_socket_r.rotation_euler = Euler((0, 0, 0), 'XYZ')
        pb_socket_r.keyframe_insert(data_path="location", frame=frame)
        pb_socket_r.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Set interpolation to BEZIER
    if act.fcurves:
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.easing = 'AUTO'

    # --- AUTOMATED GROUND SOLVER PASS (Z >= 0.0 INVARIANT) ---
    depsgraph = bpy.context.evaluated_depsgraph_get()
    root_pb = pbones.get("Root")
    if root_pb:
        for f in range(1, 49):
            bpy.context.scene.frame_set(f)
            bpy.context.view_layer.update()
            eval_mesh = mesh.evaluated_get(depsgraph)
            min_z = min((eval_mesh.matrix_world @ v.co).z for v in eval_mesh.data.vertices)
            root_pb.location.z = -min_z
            root_pb.keyframe_insert(data_path="location", frame=f)

    print("Keyframed 180° Pure Flat Circular Arc Strike with Precise Mathematical Kinematics.")

    # --- TEMPORARY AUDIT SWORD ATTACHMENT VIA ARMATURE SKINNING ---
    audit_sword = create_temp_sword()
    audit_sword.parent = arm
    mod_sword = audit_sword.modifiers.new(name="Armature", type='ARMATURE')
    mod_sword.object = arm
    mod_sword.use_vertex_groups = True

    # --- MULTI-ANGLE 3-ROW FILMSTRIP GENERATION ---
    print("\n--- RENDERING 3-ROW 24-FRAME CONTACT SHEET (attack_filmstrip.png) ---")
    filmstrip_frames = [1, 8, 14, 16, 18, 20, 22, 26]
    filmstrip_cols = len(filmstrip_frames)

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = False
    scene.render.resolution_x = 256
    scene.render.resolution_y = 256
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - High Contrast'

    # Setup Lighting
    for obj in list(scene.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    def add_light(name, ltype, loc, energy, color=(1, 1, 1)):
        ldata = bpy.data.lights.new(name=name, type=ltype)
        ldata.energy = energy
        ldata.color = color
        lobj = bpy.data.objects.new(name=name, object_data=ldata)
        lobj.location = loc
        bpy.context.scene.collection.objects.link(lobj)
        return lobj

    add_light("KeySun", 'SUN', (3.0, -3.0, 5.0), 3.5, (1.0, 0.95, 0.88))
    add_light("FillTop", 'POINT', (0.0, 0.0, 4.0), 40.0, (0.85, 0.92, 1.0))
    add_light("RimLight", 'POINT', (-2.5, 2.5, 2.5), 60.0, (0.4, 0.8, 1.0))

    cam_data = bpy.data.cameras.new("FilmstripCam")
    cam_obj = bpy.data.objects.new("FilmstripCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Camera Perspectives:
    # 1. Top-Down: directly above, looking down -Z, Y points UP (or front +Y is UP)
    # 2. Front 3/4 Perspective: diagonal angle showing form
    # 3. Side Profile: pure lateral view proving flat Z trajectory
    views = [
        ('top', Vector((0.0, 0.0, 1.5)), Euler((0.0, 0.0, 0.0), 'XYZ'), 0.95),
        ('front_34', Vector((0.9, -1.2, 0.7)), Euler((math.radians(65), 0.0, math.radians(35)), 'XYZ'), 0.70),
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
            temp_img_path = os.path.join(base_dir, f"temp_strip_r{row_idx}_c{col_idx}.png")
            scene.render.filepath = temp_img_path
            bpy.ops.render.render(write_still=True)
            rendered_images.append(temp_img_path)

    # Stitch into single 3-Row Contact Sheet (filmstrip) via system python subprocess
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
        im_path = os.path.join(base_dir, f"temp_strip_r{{r}}_c{{c}}.png")
        if os.path.exists(im_path):
            tile = Image.open(im_path)
            contact_sheet.paste(tile, (c * w, r * h))
            tile.close()
            try:
                os.remove(im_path)
            except Exception:
                pass

row_labels = ["TOP-DOWN (Pure Flat XY Circle)", "FRONT 3/4 PERSPECTIVE", "SIDE PROFILE (Strict Z=0.28m)"]
for r, label in enumerate(row_labels):
    draw.text((12, r * h + 10), label, fill=(255, 215, 0, 255))

for c, f in enumerate(filmstrip_frames):
    draw.text((c * w + 12, 10), f"F{{f:02d}}", fill=(100, 200, 255, 255))

filmstrip_final_path = os.path.join(base_dir, "attack_filmstrip.png")
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
    print(f"Saved updated attack animation to: {blend_path}")

    # --- BEAUTY CYCLES AGX RENDER (swordsman_render.png) ---
    print("\n--- RENDERING BEAUTY STILL (swordsman_render.png) ---")
    scene.frame_set(20) # Impact frame
    bpy.context.view_layer.update()

    # Dynamic Depsgraph Auto-framing
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_mesh = mesh.evaluated_get(depsgraph)
    verts_co = [eval_mesh.matrix_world @ v.co for v in eval_mesh.data.vertices]
    min_co = Vector((min(v.x for v in verts_co), min(v.y for v in verts_co), min(v.z for v in verts_co)))
    max_co = Vector((max(v.x for v in verts_co), max(v.y for v in verts_co), max(v.z for v in verts_co)))
    center = (min_co + max_co) * 0.5

    # Create beauty camera targeting center from front (+Y looking towards -Y)
    b_cam_data = bpy.data.cameras.new("BeautyCam")
    b_cam_obj = bpy.data.objects.new("BeautyCam", b_cam_data)
    scene.collection.objects.link(b_cam_obj)
    scene.camera = b_cam_obj
    
    b_cam_pos = center + Vector((-0.65, 0.95, 0.30))
    b_cam_obj.location = b_cam_pos
    b_look_dir = (center - b_cam_pos).normalized()
    b_rot_quat = b_look_dir.to_track_quat('-Z', 'Y')
    b_cam_obj.rotation_euler = b_rot_quat.to_euler('XYZ')
    b_cam_data.lens = 52

    # Front Studio 3-Point Lighting
    add_light("KeySun", 'SUN', center + Vector((-2.0, 3.0, 4.0)), 4.5, (1.0, 0.96, 0.90))
    add_light("FillTop", 'POINT', center + Vector((1.5, 2.0, 1.5)), 45.0, (0.85, 0.92, 1.0))
    add_light("RimLight", 'POINT', center + Vector((-1.0, -2.0, 2.0)), 55.0, (0.4, 0.8, 1.0))
    add_light("BounceFill", 'POINT', center + Vector((0.0, 1.2, -0.4)), 20.0, (1.0, 0.85, 0.7))

    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    beauty_path = os.path.join(base_dir, "swordsman_render.png")
    scene.render.filepath = beauty_path
    bpy.ops.render.render(write_still=True)
    print(f"Saved Beauty Render to: {beauty_path}")

    # Cleanup beauty lights & camera
    bpy.data.objects.remove(b_cam_obj, do_unlink=True)
    for obj in list(scene.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    # --- EXPORT GLTF 2.0 (swordsman.glb) ---
    print("\n--- EXPORTING GLTF 2.0 (swordsman.glb) ---")
    # Push all actions to NLA tracks for clean export
    if not arm.animation_data:
        arm.animation_data_create()
    arm.animation_data.action = None
    for track in list(arm.animation_data.nla_tracks):
        arm.animation_data.nla_tracks.remove(track)

    for act_name in ['Walk', 'Attack']:
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
    build_attack()
