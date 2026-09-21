"""
assets/swordsman/anim_attack.py
Authoritative 5-Phase Rayman-Style Floating Limbs Circular Sword Strike:
- Circular trajectory centered on character body (C = [0, 0, 0.28m], R = 0.28m).
- Windup: Hand detaches backward and upward at 45° elevation to theta = 5*pi/4 (225° behind right shoulder).
- Strike: Explosive circular sweep 5*pi/4 (225°) -> pi (180°) -> pi/2 (90°, front impact) -> 0 (2*pi, left flank extension).
- Sword blade strictly oriented along the arm trajectory / tangent velocity vector (cutting edge leads the arc).
- Whole-body torque (Hips/Chest whip from -35° to +42°), off-hand martial counterbalance, head target lock.
- Automated ground solver pass (Z >= 0.0 invariant).
- High-visibility studio lighting (Key, Fill, Rim) and dual-angle contact sheet.
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
        bsdf.inputs['Base Color'].default_value = (0.90, 0.94, 1.0, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.85
        bsdf.inputs['Roughness'].default_value = 0.15
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = (0.2, 0.5, 0.9, 1.0)
            bsdf.inputs['Emission Strength'].default_value = 0.4
    obj.data.materials.append(mat_blade)
    
    mat_gold = bpy.data.materials.new(name="M_Audit_Gold")
    mat_gold.use_nodes = True
    bsdf_g = mat_gold.node_tree.nodes.get("Principled BSDF")
    if bsdf_g:
        bsdf_g.inputs['Base Color'].default_value = (1.0, 0.80, 0.18, 1.0)
        bsdf_g.inputs['Metallic'].default_value = 0.9
        bsdf_g.inputs['Roughness'].default_value = 0.25
    obj.data.materials.append(mat_gold)

    # Blade voxels (along +Z in standard weapon space: 0.015m scale)
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.035
        v.co.y *= 0.015
        v.co.z *= 0.22
        v.co.z += 0.25  # from z=0.03 to z=0.47
    for f in bm.faces:
        f.material_index = 0

    # Crossguard
    bm_guard = bmesh.new()
    bmesh.ops.create_cube(bm_guard, size=1.0)
    for v in bm_guard.verts:
        v.co.x *= 0.11
        v.co.y *= 0.03
        v.co.z *= 0.02
        v.co.z += 0.03
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

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 48

    # -------------------------------------------------------------------------
    # 5-PHASE COMBAT STRIKE KEYFRAMES (Frames 1 - 48)
    # -------------------------------------------------------------------------
    keyframe_data = [
        # F1: Ready Combat Guard Stance
        (1, {
            'Hips': {'rot': (deg(-4), deg(-6), deg(0)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(6), deg(-6), deg(0)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(-2), deg(6), deg(0)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(12), deg(0), deg(2))},
            'LowerLeg.L': {'rot': (deg(-18), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-10), deg(0), deg(-4))},
            'LowerLeg.R': {'rot': (deg(-14), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(8), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(5), deg(0), deg(8)), 'loc': (-0.01, 0.02, 0.0)},
            'UpperArm.R': {'rot': (deg(20), deg(0), deg(10)), 'loc': (0, 0.02, 0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-20)), 'loc': (0, 0.02, 0)},
            'Hand.R': {'rot': (deg(15), deg(0), deg(20)), 'loc': (-0.02, 0.06, 0.02)},
            'Socket_Hand_R': {'rot': (deg(10), deg(10), deg(0)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-5), deg(0), deg(-8)), 'loc': (0.01, 0.02, 0.0)},
            'UpperArm.L': {'rot': (deg(15), deg(0), deg(-15)), 'loc': (0, 0.02, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-35)), 'loc': (0, 0, 0)},
            'Hand.L': {'rot': (deg(10), deg(0), deg(0)), 'loc': (0.02, 0.04, 0.0)},
        }),

        # F8: Coiling & Detaching Windup Initiation (theta ~ 205°)
        (8, {
            'Hips': {'rot': (deg(-8), deg(-20), deg(4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(10), deg(-28), deg(6)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(-4), deg(24), deg(-4)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(18), deg(0), deg(3))},
            'LowerLeg.L': {'rot': (deg(-26), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(8), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-16), deg(0), deg(-6))},
            'LowerLeg.R': {'rot': (deg(-22), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(10), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(12), deg(-10), deg(18)), 'loc': (-0.02, -0.02, 0.03)},
            'UpperArm.R': {'rot': (deg(55), deg(10), deg(20)), 'loc': (0, -0.02, 0.04)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-20)), 'loc': (0, -0.02, 0.04)},
            'Hand.R': {'rot': (deg(-20), deg(15), deg(35)), 'loc': (-0.06, -0.08, 0.10)},
            'Socket_Hand_R': {'rot': (deg(20), deg(20), deg(-15)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-5), deg(10), deg(-12)), 'loc': (0.02, 0.03, 0.0)},
            'UpperArm.L': {'rot': (deg(28), deg(8), deg(-25)), 'loc': (0, 0.02, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-55)), 'loc': (0, 0.01, 0)},
            'Hand.L': {'rot': (deg(15), deg(0), deg(0)), 'loc': (0.03, 0.07, 0.0)},
        }),

        # F14: Deep Apex Windup at 5*pi/4 (225° behind right shoulder, 45° elevation)
        (14, {
            'Hips': {'rot': (deg(-12), deg(-35), deg(6)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(15), deg(-46), deg(8)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(-8), deg(44), deg(-6)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(26), deg(0), deg(4))},
            'LowerLeg.L': {'rot': (deg(-38), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(12), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-22), deg(0), deg(-8))},
            'LowerLeg.R': {'rot': (deg(-30), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(12), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(20), deg(-15), deg(25)), 'loc': (-0.03, -0.04, 0.05)},
            'UpperArm.R': {'rot': (deg(85), deg(15), deg(30)), 'loc': (0, -0.05, 0.07)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-10)), 'loc': (0, -0.04, 0.06)},
            # Hand.R at theta = 5*pi/4, sword pointing back-up along arm
            'Hand.R': {'rot': (deg(-45), deg(20), deg(50)), 'loc': (-0.10, -0.16, 0.16)},
            'Socket_Hand_R': {'rot': (deg(35), deg(15), deg(-30)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-8), deg(15), deg(-15)), 'loc': (0.03, 0.04, 0.0)},
            'UpperArm.L': {'rot': (deg(35), deg(15), deg(-35)), 'loc': (0, 0.03, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-65)), 'loc': (0, 0.02, 0)},
            'Hand.L': {'rot': (deg(18), deg(0), deg(0)), 'loc': (0.03, 0.12, 0.01)},
        }),

        # F16: Explosive Acceleration -> theta = 180° (pi, right flank cleave)
        (16, {
            'Hips': {'rot': (deg(-10), deg(-12), deg(4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(4), deg(-12), deg(2)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(-4), deg(12), deg(-2)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(20), deg(0), deg(3))},
            'LowerLeg.L': {'rot': (deg(-30), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(10), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-16), deg(0), deg(-6))},
            'LowerLeg.R': {'rot': (deg(-24), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(10), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(10), deg(5), deg(20)), 'loc': (-0.02, 0.0, 0.02)},
            'UpperArm.R': {'rot': (deg(60), deg(10), deg(20)), 'loc': (0, 0.01, 0.03)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-15)), 'loc': (0, 0.02, 0.02)},
            # Hand at right flank, blade slicing forward along trajectory
            'Hand.R': {'rot': (deg(-10), deg(25), deg(75)), 'loc': (-0.14, 0.0, 0.10)},
            'Socket_Hand_R': {'rot': (deg(20), deg(20), deg(-20)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(2), deg(5), deg(-10)), 'loc': (0.02, 0.02, 0.0)},
            'UpperArm.L': {'rot': (deg(15), deg(0), deg(-25)), 'loc': (0, 0.0, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-45)), 'loc': (0, -0.02, 0)},
            'Hand.L': {'rot': (deg(10), deg(0), deg(-15)), 'loc': (0.04, 0.04, -0.02)},
        }),

        # F18: Climax Transition -> theta = 135° (3*pi/4, front-right)
        (18, {
            'Hips': {'rot': (deg(-4), deg(16), deg(0)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(10), deg(22), deg(-2)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(0), deg(-20), deg(0)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(14), deg(0), deg(2))},
            'LowerLeg.L': {'rot': (deg(-22), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(8), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-10), deg(0), deg(-4))},
            'LowerLeg.R': {'rot': (deg(-16), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(8), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(5), deg(15), deg(15)), 'loc': (-0.01, 0.03, 0.01)},
            'UpperArm.R': {'rot': (deg(35), deg(10), deg(15)), 'loc': (0, 0.04, 0.01)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-20)), 'loc': (0, 0.05, 0.0)},
            # Hand leading forward-left, blade slashing diagonally across
            'Hand.R': {'rot': (deg(15), deg(15), deg(105)), 'loc': (-0.06, 0.16, 0.04)},
            'Socket_Hand_R': {'rot': (deg(0), deg(25), deg(-10)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(8), deg(-10), deg(-8)), 'loc': (0.01, -0.02, 0.0)},
            'UpperArm.L': {'rot': (deg(-10), deg(-15), deg(-20)), 'loc': (0, -0.04, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-35)), 'loc': (0, -0.05, 0)},
            'Hand.L': {'rot': (deg(5), deg(0), deg(-30)), 'loc': (0.06, -0.06, -0.04)},
        }),

        # F20: PEAK IMPACT CLIMAX -> theta = 90° (pi/2, DIRECT FRONT HORIZONTAL CLEAVE)
        (20, {
            'Hips': {'rot': (deg(0), deg(36), deg(-4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(18), deg(44), deg(-6)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(2), deg(-40), deg(2)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(10), deg(0), deg(2))},
            'LowerLeg.L': {'rot': (deg(-16), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-6), deg(0), deg(-2))},
            'LowerLeg.R': {'rot': (deg(-10), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(6), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(0), deg(25), deg(10)), 'loc': (0.0, 0.05, 0.0)},
            'UpperArm.R': {'rot': (deg(15), deg(10), deg(10)), 'loc': (0.02, 0.06, 0.0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-25)), 'loc': (0.03, 0.07, -0.01)},
            # Hand extended straight in front of chest, blade cleaving horizontally across (+X)
            'Hand.R': {'rot': (deg(35), deg(0), deg(125)), 'loc': (0.04, 0.22, -0.02)},
            'Socket_Hand_R': {'rot': (deg(-15), deg(25), deg(0)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(12), deg(-20), deg(-6)), 'loc': (0.0, -0.04, 0.0)},
            'UpperArm.L': {'rot': (deg(-25), deg(-25), deg(-15)), 'loc': (0, -0.08, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-25)), 'loc': (0, -0.08, 0)},
            'Hand.L': {'rot': (deg(0), deg(0), deg(-45)), 'loc': (0.08, -0.12, -0.06)},
        }),

        # F22: Follow-Through & Overshoot -> theta = 0° (2*pi, LEFT FLANK COMPLETION)
        (22, {
            'Hips': {'rot': (deg(2), deg(42), deg(-4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(16), deg(48), deg(-6)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(2), deg(-42), deg(2)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(8), deg(0), deg(1))},
            'LowerLeg.L': {'rot': (deg(-14), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-4), deg(0), deg(-2))},
            'LowerLeg.R': {'rot': (deg(-8), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(6), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(-2), deg(28), deg(8)), 'loc': (0.01, 0.04, 0.0)},
            'UpperArm.R': {'rot': (deg(5), deg(5), deg(5)), 'loc': (0.03, 0.05, 0.0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-30)), 'loc': (0.04, 0.05, -0.01)},
            # Hand swept far to the left flank, blade pointed left-back
            'Hand.R': {'rot': (deg(45), deg(-15), deg(145)), 'loc': (0.12, 0.16, -0.04)},
            'Socket_Hand_R': {'rot': (deg(-25), deg(20), deg(10)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(15), deg(-25), deg(-4)), 'loc': (0.0, -0.05, 0.0)},
            'UpperArm.L': {'rot': (deg(-30), deg(-30), deg(-10)), 'loc': (0, -0.10, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-20)), 'loc': (0, -0.10, 0)},
            'Hand.L': {'rot': (deg(0), deg(0), deg(-50)), 'loc': (0.09, -0.14, -0.06)},
        }),

        # F26: Hit-Stop Tremor & Deceleration Hold
        (26, {
            'Hips': {'rot': (deg(2), deg(40), deg(-4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(15), deg(45), deg(-6)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(2), deg(-40), deg(2)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(8), deg(0), deg(1))},
            'LowerLeg.L': {'rot': (deg(-14), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-4), deg(0), deg(-2))},
            'LowerLeg.R': {'rot': (deg(-8), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(6), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(-2), deg(26), deg(8)), 'loc': (0.01, 0.04, 0.0)},
            'UpperArm.R': {'rot': (deg(8), deg(5), deg(5)), 'loc': (0.03, 0.05, 0.0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-30)), 'loc': (0.04, 0.05, -0.01)},
            'Hand.R': {'rot': (deg(42), deg(-12), deg(140)), 'loc': (0.11, 0.15, -0.04)},
            'Socket_Hand_R': {'rot': (deg(-22), deg(20), deg(10)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(14), deg(-22), deg(-4)), 'loc': (0.0, -0.04, 0.0)},
            'UpperArm.L': {'rot': (deg(-28), deg(-25), deg(-10)), 'loc': (0, -0.09, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-20)), 'loc': (0, -0.09, 0)},
            'Hand.L': {'rot': (deg(0), deg(0), deg(-45)), 'loc': (0.08, -0.13, -0.05)},
        }),

        # F34: Recovery Phase 1 - Pulling back from Left Flank
        (34, {
            'Hips': {'rot': (deg(-2), deg(18), deg(-2)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(10), deg(20), deg(-2)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(0), deg(-18), deg(0)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(10), deg(0), deg(2))},
            'LowerLeg.L': {'rot': (deg(-16), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-8), deg(0), deg(-3))},
            'LowerLeg.R': {'rot': (deg(-12), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(7), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(2), deg(15), deg(8)), 'loc': (0.0, 0.03, 0.0)},
            'UpperArm.R': {'rot': (deg(15), deg(5), deg(10)), 'loc': (0.01, 0.04, 0.0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-25)), 'loc': (0.02, 0.04, 0.0)},
            'Hand.R': {'rot': (deg(30), deg(0), deg(95)), 'loc': (0.04, 0.12, -0.01)},
            'Socket_Hand_R': {'rot': (deg(-10), deg(15), deg(0)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(5), deg(-10), deg(-6)), 'loc': (0.01, -0.01, 0.0)},
            'UpperArm.L': {'rot': (deg(-10), deg(-10), deg(-15)), 'loc': (0, -0.04, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-30)), 'loc': (0, -0.04, 0)},
            'Hand.L': {'rot': (deg(5), deg(0), deg(-20)), 'loc': (0.05, -0.05, -0.02)},
        }),

        # F42: Recovery Phase 2 - Returning toward Guard Position
        (42, {
            'Hips': {'rot': (deg(-4), deg(4), deg(0)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(8), deg(4), deg(0)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(-1), deg(-4), deg(0)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(11), deg(0), deg(2))},
            'LowerLeg.L': {'rot': (deg(-17), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-9), deg(0), deg(-3))},
            'LowerLeg.R': {'rot': (deg(-13), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(7), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(4), deg(5), deg(8)), 'loc': (-0.005, 0.025, 0.0)},
            'UpperArm.R': {'rot': (deg(18), deg(2), deg(10)), 'loc': (0.005, 0.03, 0.0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-22)), 'loc': (0.01, 0.03, 0.01)},
            'Hand.R': {'rot': (deg(20), deg(0), deg(50)), 'loc': (-0.005, 0.08, 0.01)},
            'Socket_Hand_R': {'rot': (deg(0), deg(12), deg(0)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-1), deg(-2), deg(-7)), 'loc': (0.01, 0.01, 0.0)},
            'UpperArm.L': {'rot': (deg(5), deg(-2), deg(-15)), 'loc': (0, -0.01, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-32)), 'loc': (0, -0.01, 0)},
            'Hand.L': {'rot': (deg(8), deg(0), deg(-10)), 'loc': (0.03, 0.0, -0.01)},
        }),

        # F48: Seamless Reset back to Frame 1 Ready Guard
        (48, {
            'Hips': {'rot': (deg(-4), deg(-6), deg(0)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(6), deg(-6), deg(0)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(-2), deg(6), deg(0)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(12), deg(0), deg(2))},
            'LowerLeg.L': {'rot': (deg(-18), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(6), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-10), deg(0), deg(-4))},
            'LowerLeg.R': {'rot': (deg(-14), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(8), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(5), deg(0), deg(8)), 'loc': (-0.01, 0.02, 0.0)},
            'UpperArm.R': {'rot': (deg(20), deg(0), deg(10)), 'loc': (0, 0.02, 0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-20)), 'loc': (0, 0.02, 0)},
            'Hand.R': {'rot': (deg(15), deg(0), deg(20)), 'loc': (-0.02, 0.06, 0.02)},
            'Socket_Hand_R': {'rot': (deg(10), deg(10), deg(0)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-5), deg(0), deg(-8)), 'loc': (0.01, 0.02, 0.0)},
            'UpperArm.L': {'rot': (deg(15), deg(0), deg(-15)), 'loc': (0, 0.02, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-35)), 'loc': (0, 0.0, 0)},
            'Hand.L': {'rot': (deg(10), deg(0), deg(0)), 'loc': (0.02, 0.04, 0.0)},
        }),
    ]

    # Insert keyframes
    for frame, pose_dict in keyframe_data:
        bpy.context.scene.frame_set(frame)
        for bone_name, tform in pose_dict.items():
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

    print("Keyframed 5-Phase Rayman Circular Cleave Strike with aligned weapon kinematics.")

    # --- TEMPORARY AUDIT SWORD ATTACHMENT ---
    audit_sword = create_temp_sword()
    audit_sword.parent = arm
    audit_sword.parent_type = 'BONE'
    audit_sword.parent_bone = 'Socket_Hand_R'
    audit_sword.matrix_local.identity()

    # --- HIGH VISIBILITY 3-POINT STUDIO LIGHTING ---
    # Sun Key Light (Warm, high angle from front-left)
    key_light = bpy.data.lights.new(name="Key_Light", type='SUN')
    key_light.energy = 5.0
    key_light.color = (1.0, 0.96, 0.90)
    key_obj = bpy.data.objects.new("Key_Light", key_light)
    bpy.context.scene.collection.objects.link(key_obj)
    key_obj.rotation_euler = (deg(50), deg(-15), deg(35))

    # Sun Fill Light (Cool cyan, from front-right)
    fill_light = bpy.data.lights.new(name="Fill_Light", type='SUN')
    fill_light.energy = 3.2
    fill_light.color = (0.75, 0.88, 1.0)
    fill_obj = bpy.data.objects.new("Fill_Light", fill_light)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (deg(60), deg(25), deg(-65))

    # Sun Rim Light (Crisp edge light from behind-high)
    rim_light = bpy.data.lights.new(name="Rim_Light", type='SUN')
    rim_light.energy = 4.5
    rim_light.color = (0.6, 0.9, 1.0)
    rim_obj = bpy.data.objects.new("Rim_Light", rim_light)
    bpy.context.scene.collection.objects.link(rim_obj)
    rim_obj.rotation_euler = (deg(-55), deg(20), deg(160))

    # --- CAMERAS (FRONT 3/4 & SIDE PROFILE) ---
    cam_target = bpy.data.objects.new("Cam_Target", None)
    cam_target.location = Vector((0.0, 0.0, 0.25))
    bpy.context.scene.collection.objects.link(cam_target)

    # Camera A: Front 3/4 Eye-Level Perspective
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

    # --- DUAL-ANGLE FILMSTRIP GENERATION ---
    audit_frames = [1, 8, 14, 16, 18, 20, 22, 48]
    print(f"\nRendering dual-angle contact sheet across frames: {audit_frames}...")

    bpy.context.scene.render.resolution_x = 256
    bpy.context.scene.render.resolution_y = 256

    for f in audit_frames:
        bpy.context.scene.frame_set(f)
        
        # Angle A (Front 3/4)
        bpy.context.scene.camera = cam_a
        path_a = os.path.join(base_dir, f"temp_fl_a_{f:02d}.png")
        bpy.context.scene.render.filepath = path_a
        bpy.ops.render.render(write_still=True)

        # Angle B (Side Profile)
        bpy.context.scene.camera = cam_b
        path_b = os.path.join(base_dir, f"temp_fl_b_{f:02d}.png")
        bpy.context.scene.render.filepath = path_b
        bpy.ops.render.render(write_still=True)

    dual_strip_path = os.path.join(base_dir, "attack_filmstrip.png")
    ps_cmd = f"""
Add-Type -AssemblyName System.Drawing
$width = {len(audit_frames)} * 256
$height = 512
$filmstrip = New-Object System.Drawing.Bitmap($width, $height)
$g = [System.Drawing.Graphics]::FromImage($filmstrip)
$g.Clear([System.Drawing.Color]::FromArgb(255, 14, 14, 17))

$frames = @({', '.join(map(str, audit_frames))})

# Draw Row 1: Front 3/4 View
for ($i = 0; $i -lt $frames.Count; $i++) {{
    $f = $frames[$i]
    $fStr = "{{0:D2}}" -f $f
    $path = Join-Path "{base_dir}" "temp_fl_a_$fStr.png"
    if (Test-Path $path) {{
        $img = [System.Drawing.Image]::FromFile((Resolve-Path $path))
        $g.DrawImage($img, ($i * 256), 0, 256, 256)
        $img.Dispose()
        Remove-Item $path -Force
    }}
}}

# Draw Row 2: Side Profile View
for ($i = 0; $i -lt $frames.Count; $i++) {{
    $f = $frames[$i]
    $fStr = "{{0:D2}}" -f $f
    $path = Join-Path "{base_dir}" "temp_fl_b_$fStr.png"
    if (Test-Path $path) {{
        $img = [System.Drawing.Image]::FromFile((Resolve-Path $path))
        $g.DrawImage($img, ($i * 256), 256, 256, 256)
        $img.Dispose()
        Remove-Item $path -Force
    }}
}}

$g.Dispose()
$filmstrip.Save("{dual_strip_path}", [System.Drawing.Imaging.ImageFormat]::Png)
$filmstrip.Dispose()
"""
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
    print(f"Dual-angle filmstrip saved to {dual_strip_path}")

    # --- BEAUTY RENDER AT APEX WINDUP FRAME (F14) ---
    print("\nRendering high-res beauty render 'swordsman_render.png'...")
    bpy.context.scene.camera = cam_a
    bpy.context.scene.frame_set(14)
    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1024
    bpy.context.scene.cycles.samples = 96
    render_dest = os.path.join(base_dir, "swordsman_render.png")
    bpy.context.scene.render.filepath = render_dest
    bpy.ops.render.render(write_still=True)
    print(f"Beauty render saved to {render_dest}")

    # Clean up temporary audit sword before GLB export (keep hands empty)
    bpy.data.objects.remove(audit_sword, do_unlink=True)

    for c in [cam_a, cam_b, cam_target]:
        if hasattr(c, 'data') and c.data:
            c_data = c.data
            bpy.data.objects.remove(c, do_unlink=True)
            bpy.data.cameras.remove(c_data, do_unlink=True)
        else:
            bpy.data.objects.remove(c, do_unlink=True)

    for l_obj in [key_obj, fill_obj, rim_obj]:
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
    print("=== SWORDSMAN CIRCULAR COMBAT ANIMATION REBUILD COMPLETE ===")

if __name__ == "__main__":
    build_attack()
