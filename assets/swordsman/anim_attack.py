"""
assets/swordsman/anim_attack.py
Authoritative 5-Phase Rayman-Style Floating Limbs 180° Pure Circular Sword Strike:
- Strict 180° flat horizontal circular trajectory in XY (Z_const = 0.28m, R_const = 0.28m).
- Clockwise circle parameterization matching user Paint sketch:
  * Start (F14): theta = 225° (5*pi/4, Bottom-Left) -> X = -0.198m, Y = -0.198m, Z = 0.28m
  * Quarter 1 (F16): theta = 180° (pi, Left Flank) -> X = -0.280m, Y =  0.000m, Z = 0.28m
  * Quarter 2 (F18): theta = 135° (3*pi/4, Top-Left) -> X = -0.198m, Y = +0.198m, Z = 0.28m
  * Quarter 3 (F20): theta =  90° (pi/2, Front Impact) -> X =  0.000m, Y = +0.280m, Z = 0.28m
  * End (F22): theta =  45° (pi/4, Top-Right Finish) -> X = +0.198m, Y = +0.198m, Z = 0.28m
- Tangent vector strictly equals trajectory derivative d/dt [X(t), Y(t)]:
  blade_dir = (sin(theta), -cos(theta), 0.0).
- Pure flat horizontal blade orientation (Z=Const, zero vertical tilt).
- Whole-body torque (Hips/Chest whip from -35° to +48°), offhand counterbalance, head target lock.
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

def solve_hand_matrix(pb_hand, pb_socket, hand_world_pos, blade_dir, edge_dir):
    """
    Computes exact world matrix for Hand.R so that:
    - Socket_Hand_R (and held weapon) sits at hand_world_pos
    - Weapon blade points along blade_dir
    - Weapon cutting edge faces edge_dir
    """
    y_blade = blade_dir.normalized()
    z_edge = edge_dir.normalized()
    z_edge = (z_edge - z_edge.dot(y_blade) * y_blade).normalized()
    x_cross = y_blade.cross(z_edge).normalized()
    z_edge = x_cross.cross(y_blade).normalized()

    socket_mat = Matrix((
        (x_cross.x, y_blade.x, z_edge.x),
        (x_cross.y, y_blade.y, z_edge.y),
        (x_cross.z, y_blade.z, z_edge.z)
    )).to_4x4()
    socket_mat.translation = hand_world_pos

    rest_hand = pb_hand.bone.matrix_local.copy()
    rest_socket = pb_socket.bone.matrix_local.copy()
    rest_rel = rest_hand.inverted() @ rest_socket
    hand_mat = socket_mat @ rest_rel.inverted()
    return hand_mat

def create_temp_sword():
    """Creates a stylized voxel sword mesh in scene for visual audit in renders."""
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
        bsdf.inputs['Base Color'].default_value = (0.90, 0.95, 1.0, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.9
        bsdf.inputs['Roughness'].default_value = 0.15
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = (0.3, 0.6, 1.0, 1.0)
            bsdf.inputs['Emission Strength'].default_value = 0.5
    obj.data.materials.append(mat_blade)
    
    mat_gold = bpy.data.materials.new(name="M_Audit_Gold")
    mat_gold.use_nodes = True
    bsdf_g = mat_gold.node_tree.nodes.get("Principled BSDF")
    if bsdf_g:
        bsdf_g.inputs['Base Color'].default_value = (1.0, 0.80, 0.15, 1.0)
        bsdf_g.inputs['Metallic'].default_value = 0.9
        bsdf_g.inputs['Roughness'].default_value = 0.25
    obj.data.materials.append(mat_gold)

    # Blade voxels (along local +Y of the bone: from y=0.03 to y=0.47)
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.035
        v.co.y *= 0.22
        v.co.y += 0.25
        v.co.z *= 0.015
    for f in bm.faces:
        f.material_index = 0

    # Crossguard (along local +X of the bone)
    bm_guard = bmesh.new()
    bmesh.ops.create_cube(bm_guard, size=1.0)
    for v in bm_guard.verts:
        v.co.x *= 0.11
        v.co.y *= 0.02
        v.co.y += 0.03
        v.co.z *= 0.03
    for f in bm_guard.faces:
        f.material_index = 1
    bm_guard.to_mesh(mesh)
    bm_guard.free()

    bm.to_mesh(mesh)
    bm.free()
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

    pb_hand_r = pbones['Hand.R']
    pb_socket_r = pbones['Socket_Hand_R']
    pb_socket_r.location = Vector((0, 0, 0))
    pb_socket_r.rotation_euler = Euler((0, 0, 0), 'XYZ')

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 48

    # -------------------------------------------------------------------------
    # 180° STRICT FLAT CIRCULAR ARC TRAJECTORY
    # Center = (0, 0, 0.28m), R = 0.28m, Z_const = 0.28m
    # -------------------------------------------------------------------------
    R = 0.28
    Z_const = 0.28
    C = Vector((0.0, 0.0, Z_const))

    def circle_point(deg_val):
        th = math.radians(deg_val)
        pos = C + Vector((R * math.cos(th), R * math.sin(th), 0.0))
        # Tangent vector for clockwise motion (decreasing theta)
        blade_dir = Vector((math.sin(th), -math.cos(th), 0.0)).normalized()
        edge_dir = Vector((0.0, 0.0, -1.0))
        return pos, blade_dir, edge_dir

    p_f14, b_f14, e_f14 = circle_point(225) # Start (Apex windup, bottom-left)
    p_f16, b_f16, e_f16 = circle_point(180) # Quarter 1 (Left flank)
    p_f18, b_f18, e_f18 = circle_point(135) # Quarter 2 (Top-left)
    p_f20, b_f20, e_f20 = circle_point(90)  # Quarter 3 (Center front impact)
    p_f22, b_f22, e_f22 = circle_point(45)  # End (Top-right finish)

    keyframe_specs = [
        # Frame 1: Ready Guard
        (1, {
            'hand_pos': Vector((-0.09, 0.08, Z_const)),
            'blade_dir': Vector((0.0, 1.0, 0.0)),
            'edge_dir': Vector((0.0, 0.0, -1.0)),
            'UpperArm.R': {'rot': (deg(15), deg(0), deg(10)), 'loc': (0, 0.01, 0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-20)), 'loc': (0, 0.01, 0)},
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
            'Shoulder.L': {'rot': (deg(-5), deg(0), deg(-8)), 'loc': (0.01, 0.02, 0.0)},
            'UpperArm.L': {'rot': (deg(15), deg(0), deg(-15)), 'loc': (0, 0.02, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-35)), 'loc': (0, 0.0, 0)},
            'Hand.L': {'rot': (deg(10), deg(0), deg(0)), 'loc': (0.02, 0.04, 0.0)},
        }),

        # Frame 8: Coiling to Start Point
        (8, {
            'hand_pos': (p_f14 + Vector((-0.09, 0.08, Z_const))) * 0.5,
            'blade_dir': b_f14,
            'edge_dir': e_f14,
            'UpperArm.R': {'rot': (deg(45), deg(10), deg(20)), 'loc': (0, -0.01, 0.02)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-15)), 'loc': (0, -0.01, 0.02)},
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
            'Shoulder.L': {'rot': (deg(-5), deg(10), deg(-12)), 'loc': (0.02, 0.03, 0.0)},
            'UpperArm.L': {'rot': (deg(28), deg(8), deg(-25)), 'loc': (0, 0.02, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-55)), 'loc': (0, 0.01, 0)},
            'Hand.L': {'rot': (deg(15), deg(0), deg(0)), 'loc': (0.03, 0.07, 0.0)},
        }),

        # Frame 14: START OF 180° ARC (Apex Windup, "рука" at theta = 225°)
        (14, {
            'hand_pos': p_f14,
            'blade_dir': b_f14,
            'edge_dir': e_f14,
            'UpperArm.R': {'rot': (deg(80), deg(15), deg(28)), 'loc': (0, -0.03, 0.05)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-10)), 'loc': (0, -0.03, 0.04)},
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
            'Shoulder.L': {'rot': (deg(-8), deg(15), deg(-15)), 'loc': (0.03, 0.04, 0.0)},
            'UpperArm.L': {'rot': (deg(35), deg(15), deg(-35)), 'loc': (0, 0.03, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-65)), 'loc': (0, 0.02, 0)},
            'Hand.L': {'rot': (deg(18), deg(0), deg(0)), 'loc': (0.03, 0.12, 0.01)},
        }),

        # Frame 16: MID-ARC 1 (Left Flank Sweep, theta = 180°)
        (16, {
            'hand_pos': p_f16,
            'blade_dir': b_f16,
            'edge_dir': e_f16,
            'UpperArm.R': {'rot': (deg(50), deg(10), deg(18)), 'loc': (0, 0.0, 0.02)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-15)), 'loc': (0, 0.01, 0.01)},
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
            'Shoulder.L': {'rot': (deg(2), deg(5), deg(-10)), 'loc': (0.02, 0.02, 0.0)},
            'UpperArm.L': {'rot': (deg(15), deg(0), deg(-25)), 'loc': (0, 0.0, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-45)), 'loc': (0, -0.02, 0)},
            'Hand.L': {'rot': (deg(10), deg(0), deg(-15)), 'loc': (0.04, 0.04, -0.02)},
        }),

        # Frame 18: MID-ARC 2 (Top-Left Sweep, theta = 135°)
        (18, {
            'hand_pos': p_f18,
            'blade_dir': b_f18,
            'edge_dir': e_f18,
            'UpperArm.R': {'rot': (deg(30), deg(8), deg(12)), 'loc': (0, 0.02, 0.01)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-18)), 'loc': (0, 0.03, 0.0)},
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
            'Shoulder.L': {'rot': (deg(8), deg(-10), deg(-8)), 'loc': (0.01, -0.02, 0.0)},
            'UpperArm.L': {'rot': (deg(-10), deg(-15), deg(-20)), 'loc': (0, -0.04, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-35)), 'loc': (0, -0.05, 0)},
            'Hand.L': {'rot': (deg(5), deg(0), deg(-30)), 'loc': (0.06, -0.06, -0.04)},
        }),

        # Frame 20: PEAK IMPACT CLIMAX (Center Front Cleave, theta = 90°)
        (20, {
            'hand_pos': p_f20,
            'blade_dir': b_f20,
            'edge_dir': e_f20,
            'UpperArm.R': {'rot': (deg(15), deg(5), deg(8)), 'loc': (0.01, 0.04, 0.0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-20)), 'loc': (0.02, 0.05, 0.0)},
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
            'Shoulder.L': {'rot': (deg(12), deg(-20), deg(-6)), 'loc': (0.0, -0.04, 0.0)},
            'UpperArm.L': {'rot': (deg(-25), deg(-25), deg(-15)), 'loc': (0, -0.08, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-25)), 'loc': (0, -0.08, 0)},
            'Hand.L': {'rot': (deg(0), deg(0), deg(-45)), 'loc': (0.08, -0.12, -0.06)},
        }),

        # Frame 22: END OF 180° ARC (Top-Right Destination, theta = 45°)
        (22, {
            'hand_pos': p_f22,
            'blade_dir': b_f22,
            'edge_dir': e_f22,
            'UpperArm.R': {'rot': (deg(5), deg(0), deg(5)), 'loc': (0.02, 0.04, 0.0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-25)), 'loc': (0.03, 0.04, 0.0)},
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
            'Shoulder.L': {'rot': (deg(15), deg(-25), deg(-4)), 'loc': (0.0, -0.05, 0.0)},
            'UpperArm.L': {'rot': (deg(-30), deg(-30), deg(-10)), 'loc': (0, -0.10, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-20)), 'loc': (0, -0.10, 0)},
            'Hand.L': {'rot': (deg(0), deg(0), deg(-50)), 'loc': (0.09, -0.14, -0.06)},
        }),

        # Frame 26: Hit-Stop Tremor & Deceleration Snap
        (26, {
            'hand_pos': p_f22 + Vector((0.01, -0.01, 0.0)),
            'blade_dir': b_f22,
            'edge_dir': e_f22,
            'UpperArm.R': {'rot': (deg(6), deg(0), deg(5)), 'loc': (0.02, 0.04, 0.0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-25)), 'loc': (0.03, 0.04, 0.0)},
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
            'Shoulder.L': {'rot': (deg(14), deg(-22), deg(-4)), 'loc': (0.0, -0.04, 0.0)},
            'UpperArm.L': {'rot': (deg(-28), deg(-25), deg(-10)), 'loc': (0, -0.09, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-20)), 'loc': (0, -0.09, 0)},
            'Hand.L': {'rot': (deg(0), deg(0), deg(-45)), 'loc': (0.08, -0.13, -0.05)},
        }),

        # Frame 34: Recovery Phase 1 - Pulling back from Left Flank
        (34, {
            'hand_pos': Vector((0.06, 0.12, Z_const)),
            'blade_dir': Vector((0.40, 0.90, 0.0)),
            'edge_dir': Vector((0.0, 0.0, -1.0)),
            'UpperArm.R': {'rot': (deg(12), deg(2), deg(8)), 'loc': (0.01, 0.03, 0.0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-22)), 'loc': (0.01, 0.03, 0.0)},
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
            'Shoulder.L': {'rot': (deg(5), deg(-10), deg(-6)), 'loc': (0.01, -0.01, 0.0)},
            'UpperArm.L': {'rot': (deg(-10), deg(-10), deg(-15)), 'loc': (0, -0.04, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-30)), 'loc': (0, -0.04, 0)},
            'Hand.L': {'rot': (deg(5), deg(0), deg(-20)), 'loc': (0.05, -0.05, -0.02)},
        }),

        # Frame 42: Recovery Phase 2 - Returning toward Guard
        (42, {
            'hand_pos': Vector((-0.03, 0.09, Z_const)),
            'blade_dir': Vector((0.20, 0.95, 0.0)),
            'edge_dir': Vector((0.0, 0.0, -1.0)),
            'UpperArm.R': {'rot': (deg(14), deg(1), deg(9)), 'loc': (0.0, 0.02, 0.0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-21)), 'loc': (0.0, 0.02, 0.0)},
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
            'Shoulder.L': {'rot': (deg(-1), deg(-2), deg(-7)), 'loc': (0.01, 0.01, 0.0)},
            'UpperArm.L': {'rot': (deg(5), deg(-2), deg(-15)), 'loc': (0, -0.01, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-32)), 'loc': (0, -0.01, 0)},
            'Hand.L': {'rot': (deg(8), deg(0), deg(-10)), 'loc': (0.03, 0.0, -0.01)},
        }),

        # Frame 48: Seamless Reset back to Frame 1
        (48, {
            'hand_pos': Vector((-0.09, 0.08, Z_const)),
            'blade_dir': Vector((0.0, 1.0, 0.0)),
            'edge_dir': Vector((0.0, 0.0, -1.0)),
            'UpperArm.R': {'rot': (deg(15), deg(0), deg(10)), 'loc': (0, 0.01, 0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-20)), 'loc': (0, 0.01, 0)},
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
            'Shoulder.L': {'rot': (deg(-5), deg(0), deg(-8)), 'loc': (0.01, 0.02, 0.0)},
            'UpperArm.L': {'rot': (deg(15), deg(0), deg(-15)), 'loc': (0, 0.02, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-35)), 'loc': (0, 0.0, 0)},
            'Hand.L': {'rot': (deg(10), deg(0), deg(0)), 'loc': (0.02, 0.04, 0.0)},
        }),
    ]

    # Insert keyframes with mathematical hand solver
    for frame, spec in keyframe_specs:
        bpy.context.scene.frame_set(frame)

        # 1. Apply body & arm joint poses
        for bone_name, tform in spec.items():
            if bone_name in ('hand_pos', 'blade_dir', 'edge_dir'):
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

        # Update view layer so parent bone world matrices are accurate
        bpy.context.view_layer.update()

        # 2. Solve and apply exact Hand.R world matrix
        hand_world_mat = solve_hand_matrix(
            pb_hand_r,
            pb_socket_r,
            spec['hand_pos'],
            spec['blade_dir'],
            spec['edge_dir']
        )
        pb_hand_r.matrix = hand_world_mat
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

    print("Keyframed 180° Pure Flat Circular Arc Strike.")

    # --- TEMPORARY AUDIT SWORD ATTACHMENT ---
    audit_sword = create_temp_sword()
    audit_sword.parent = arm
    audit_sword.parent_type = 'BONE'
    audit_sword.parent_bone = 'Socket_Hand_R'
    audit_sword.matrix_local.identity()

    # --- HIGH VISIBILITY 3-POINT STUDIO LIGHTING ---
    key_light = bpy.data.lights.new(name="Key_Light", type='SUN')
    key_light.energy = 5.0
    key_light.color = (1.0, 0.96, 0.90)
    key_obj = bpy.data.objects.new("Key_Light", key_light)
    bpy.context.scene.collection.objects.link(key_obj)
    key_obj.rotation_euler = (deg(50), deg(-15), deg(35))

    fill_light = bpy.data.lights.new(name="Fill_Light", type='SUN')
    fill_light.energy = 3.5
    fill_light.color = (0.75, 0.88, 1.0)
    fill_obj = bpy.data.objects.new("Fill_Light", fill_light)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (deg(60), deg(25), deg(-65))

    rim_light = bpy.data.lights.new(name="Rim_Light", type='SUN')
    rim_light.energy = 4.5
    rim_light.color = (0.6, 0.9, 1.0)
    rim_obj = bpy.data.objects.new("Rim_Light", rim_light)
    bpy.context.scene.collection.objects.link(rim_obj)
    rim_obj.rotation_euler = (deg(-55), deg(20), deg(160))

    # Top Light (Direct down for top-view illumination)
    top_light = bpy.data.lights.new(name="Top_Light", type='SUN')
    top_light.energy = 3.5
    top_light.color = (1.0, 1.0, 1.0)
    top_obj = bpy.data.objects.new("Top_Light", top_light)
    bpy.context.scene.collection.objects.link(top_obj)
    top_obj.rotation_euler = (0, 0, 0)

    # --- CAMERAS: TOP-DOWN ("Вид сверху"), FRONT 3/4, SIDE PROFILE ---
    cam_target = bpy.data.objects.new("Cam_Target", None)
    cam_target.location = Vector((0.0, 0.0, 0.25))
    bpy.context.scene.collection.objects.link(cam_target)

    # Camera 0: Pure Top-Down Perspective ("Вид сверху")
    cam_top_data = bpy.data.cameras.new("Cam_Top")
    cam_top = bpy.data.objects.new("Cam_Top", cam_top_data)
    bpy.context.scene.collection.objects.link(cam_top)
    cam_top.location = Vector((0.0, 0.0, 1.6))
    cam_top.rotation_euler = (0, 0, deg(180)) # Character faces down in image (matching sketch!)

    # Camera A: Front 3/4 Perspective
    cam_a_data = bpy.data.cameras.new("Cam_Front34")
    cam_a = bpy.data.objects.new("Cam_Front34", cam_a_data)
    bpy.context.scene.collection.objects.link(cam_a)
    cam_a.location = Vector((-0.85, 1.4, 0.45))
    tt_a = cam_a.constraints.new(type='TRACK_TO')
    tt_a.target = cam_target
    tt_a.track_axis = 'TRACK_NEGATIVE_Z'
    tt_a.up_axis = 'UP_Y'

    # Camera B: Pure Side Profile Perspective
    cam_b_data = bpy.data.cameras.new("Cam_Side")
    cam_b = bpy.data.objects.new("Cam_Side", cam_b_data)
    bpy.context.scene.collection.objects.link(cam_b)
    cam_b.location = Vector((-1.5, 0.0, 0.30))
    tt_b = cam_b.constraints.new(type='TRACK_TO')
    tt_b.target = cam_target
    tt_b.track_axis = 'TRACK_NEGATIVE_Z'
    tt_b.up_axis = 'UP_Y'

    # Cycles render configuration
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'CPU'
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.view_settings.view_transform = 'AgX'
    bpy.context.scene.view_settings.look = 'AgX - Medium High Contrast'
    bpy.context.scene.render.film_transparent = False

    # --- 3-ROW FILMSTRIP GENERATION (TOP-DOWN, FRONT 3/4, SIDE) ---
    audit_frames = [1, 8, 14, 16, 18, 20, 22, 48]
    print(f"\nRendering 3-row contact sheet across frames: {audit_frames}...")

    bpy.context.scene.render.resolution_x = 256
    bpy.context.scene.render.resolution_y = 256

    for f in audit_frames:
        bpy.context.scene.frame_set(f)
        
        # Row 1: Top-Down View ("Вид сверху")
        bpy.context.scene.camera = cam_top
        path_top = os.path.join(base_dir, f"temp_fl_top_{f:02d}.png")
        bpy.context.scene.render.filepath = path_top
        bpy.ops.render.render(write_still=True)

        # Row 2: Front 3/4 View
        bpy.context.scene.camera = cam_a
        path_a = os.path.join(base_dir, f"temp_fl_a_{f:02d}.png")
        bpy.context.scene.render.filepath = path_a
        bpy.ops.render.render(write_still=True)

        # Row 3: Side Profile View
        bpy.context.scene.camera = cam_b
        path_b = os.path.join(base_dir, f"temp_fl_b_{f:02d}.png")
        bpy.context.scene.render.filepath = path_b
        bpy.ops.render.render(write_still=True)

    dual_strip_path = os.path.join(base_dir, "attack_filmstrip.png")
    ps_cmd = f"""
Add-Type -AssemblyName System.Drawing
$width = {len(audit_frames)} * 256
$height = 768
$filmstrip = New-Object System.Drawing.Bitmap($width, $height)
$g = [System.Drawing.Graphics]::FromImage($filmstrip)
$g.Clear([System.Drawing.Color]::FromArgb(255, 14, 14, 17))

$frames = @({', '.join(map(str, audit_frames))})

# Draw Row 1: Top-Down View (Вид сверху)
for ($i = 0; $i -lt $frames.Count; $i++) {{
    $f = $frames[$i]
    $fStr = "{{0:D2}}" -f $f
    $path = Join-Path "{base_dir}" "temp_fl_top_$fStr.png"
    if (Test-Path $path) {{
        $img = [System.Drawing.Image]::FromFile((Resolve-Path $path))
        $g.DrawImage($img, ($i * 256), 0, 256, 256)
        $img.Dispose()
        Remove-Item $path -Force
    }}
}}

# Draw Row 2: Front 3/4 View
for ($i = 0; $i -lt $frames.Count; $i++) {{
    $f = $frames[$i]
    $fStr = "{{0:D2}}" -f $f
    $path = Join-Path "{base_dir}" "temp_fl_a_$fStr.png"
    if (Test-Path $path) {{
        $img = [System.Drawing.Image]::FromFile((Resolve-Path $path))
        $g.DrawImage($img, ($i * 256), 256, 256, 256)
        $img.Dispose()
        Remove-Item $path -Force
    }}
}}

# Draw Row 3: Side Profile View
for ($i = 0; $i -lt $frames.Count; $i++) {{
    $f = $frames[$i]
    $fStr = "{{0:D2}}" -f $f
    $path = Join-Path "{base_dir}" "temp_fl_b_$fStr.png"
    if (Test-Path $path) {{
        $img = [System.Drawing.Image]::FromFile((Resolve-Path $path))
        $g.DrawImage($img, ($i * 256), 512, 256, 256)
        $img.Dispose()
        Remove-Item $path -Force
    }}
}}

$g.Dispose()
$filmstrip.Save("{dual_strip_path}", [System.Drawing.Imaging.ImageFormat]::Png)
$filmstrip.Dispose()
"""
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
    print(f"3-row filmstrip saved to {dual_strip_path}")

    # --- BEAUTY RENDER AT PEAK IMPACT CLIMAX FRAME (F20) ---
    print("\nRendering high-res beauty render 'swordsman_render.png'...")
    bpy.context.scene.camera = cam_a
    bpy.context.scene.frame_set(20)
    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1024
    bpy.context.scene.cycles.samples = 96
    render_dest = os.path.join(base_dir, "swordsman_render.png")
    bpy.context.scene.render.filepath = render_dest
    bpy.ops.render.render(write_still=True)
    print(f"Beauty render saved to {render_dest}")

    # Clean up temporary audit sword before GLB export (keep hands empty)
    bpy.data.objects.remove(audit_sword, do_unlink=True)

    for c in [cam_top, cam_a, cam_b, cam_target]:
        if hasattr(c, 'data') and c.data:
            c_data = c.data
            bpy.data.objects.remove(c, do_unlink=True)
            bpy.data.cameras.remove(c_data, do_unlink=True)
        else:
            bpy.data.objects.remove(c, do_unlink=True)

    for l_obj in [key_obj, fill_obj, rim_obj, top_obj]:
        l_data = l_obj.data
        bpy.data.objects.remove(l_obj, do_unlink=True)
        bpy.data.lights.remove(l_data, do_unlink=True)

    for track in arm.animation_data.nla_tracks:
        track.mute = False

    # --- MODERN GLTF 2.0 EXPORT ---
    glb_path = os.path.join(base_dir, "swordsman.glb")
    print(f"\nExporting game-ready GLB '{glb_path}'...")
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        export_animations=True,
        export_bake_animation=True,
        export_skins=True,
        export_all_influences=False,
        export_apply=False,
        export_yup=True
    )
    print("GLB export complete.")

    data_js_path = os.path.join(base_dir, "swordsman_data.js")
    if os.path.exists(glb_path):
        with open(glb_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode('utf-8')
        js_content = f'window.SWORDSMAN_BASE64 = "data:model/gltf-binary;base64,{b64_data}";\n'
        with open(data_js_path, "w", encoding="utf-8") as f:
            f.write(js_content)
        print(f"Exported {data_js_path}")

    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"Saved {blend_path}")
    print("=== SWORDSMAN 180° CIRCULAR COMBAT ANIMATION REBUILD COMPLETE ===")

if __name__ == "__main__":
    build_attack()
