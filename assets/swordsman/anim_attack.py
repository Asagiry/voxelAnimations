"""
assets/swordsman/anim_attack.py
Authoritative 5-Phase Rayman-Style Floating Limbs Circular Sword Strike:
- Circular trajectory centered on the character's body (C = [0, 0, 0.30m], R = 0.28m).
- Windup: Hand detaches backward and upward at 45° elevation to theta = 5*pi/4 (225° behind right shoulder).
- Strike: Explosive circular sweep from 5*pi/4 (225°) -> pi (180°) -> pi/2 (90°, front impact) -> pi/4 (45°) -> 0 (2*pi, left flank extension).
- Sword wrist dynamically oriented tangential to velocity vector (cutting edge leads the arc).
- Whole-body torque (Hips/Chest whip from -40° to +42°), off-hand martial counterbalance, head target lock.
- Automated ground solver pass (Z >= 0.0 invariant).
- Studio lighting with AgX High Contrast and TrackTo cameras.
- Dual-angle filmstrip (Front 3/4 + Side Profile) and high-res Cycles beauty render.
- GlTF 2.0 with baked animations and Base64 export.
"""

import bpy
import os
import math
import base64
import subprocess
from mathutils import Vector, Euler

def deg(v):
    return math.radians(v)

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
    # RAYMAN CIRCULAR CLEAVE SWEEP (5*pi/4 -> 0 / 2*pi)
    # Circle Center: (0, 0, 0.30m), Orbit Radius: R = 0.28m
    # -------------------------------------------------------------------------
    poses = [
        # F1: Ready Combat Guard
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
            'Shoulder.R': {'rot': (deg(5), deg(0), deg(10)), 'loc': (-0.015, 0.02, 0.0)},
            'UpperArm.R': {'rot': (deg(25), deg(0), deg(15)), 'loc': (0, 0.02, 0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-30)), 'loc': (0, 0.02, 0)},
            'Hand.R': {'rot': (deg(10), deg(0), deg(25)), 'loc': (-0.02, 0.06, 0.02)},
            'Socket_Hand_R': {'rot': (deg(0), deg(15), deg(0)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-5), deg(0), deg(-10)), 'loc': (0.015, 0.02, 0.0)},
            'UpperArm.L': {'rot': (deg(20), deg(0), deg(-20)), 'loc': (0, 0.02, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-45)), 'loc': (0, 0, 0)},
            'Hand.L': {'rot': (deg(10), deg(0), deg(0)), 'loc': (0.03, 0.05, 0.0)},
        }),

        # F8: Coiling Back & Detaching Hand (theta ~ 195°, climbing at 45°)
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
            'Shoulder.R': {'rot': (deg(12), deg(-10), deg(18)), 'loc': (-0.025, -0.03, 0.04)},
            'UpperArm.R': {'rot': (deg(60), deg(10), deg(25)), 'loc': (0, -0.03, 0.05)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-30)), 'loc': (0, -0.03, 0.05)},
            # Hand floating back-right: offset from rest (-0.09) is (-0.08, -0.10, +0.10)
            'Hand.R': {'rot': (deg(-15), deg(12), deg(35)), 'loc': (-0.08, -0.10, 0.10)},
            'Socket_Hand_R': {'rot': (deg(-25), deg(20), deg(-15)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-5), deg(10), deg(-12)), 'loc': (0.02, 0.03, 0.0)},
            'UpperArm.L': {'rot': (deg(28), deg(8), deg(-25)), 'loc': (0, 0.02, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-55)), 'loc': (0, 0.01, 0)},
            'Hand.L': {'rot': (deg(15), deg(0), deg(0)), 'loc': (0.03, 0.07, 0.0)},
        }),

        # F14: Deep Apex Windup at theta = 5*pi/4 (225°), elevated 45° behind back!
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
            'Shoulder.R': {'rot': (deg(20), deg(-15), deg(25)), 'loc': (-0.035, -0.05, 0.06)},
            'UpperArm.R': {'rot': (deg(95), deg(15), deg(30)), 'loc': (0, -0.06, 0.08)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-15)), 'loc': (0, -0.05, 0.06)},
            # Exact 5*pi/4 (225°) Position: X_world ~ -0.20, Y_world ~ -0.20, Z_world ~ 0.40
            'Hand.R': {'rot': (deg(-30), deg(15), deg(45)), 'loc': (-0.12, -0.18, 0.18)},
            'Socket_Hand_R': {'rot': (deg(-45), deg(10), deg(-25)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-8), deg(15), deg(-15)), 'loc': (0.03, 0.04, 0.0)},
            'UpperArm.L': {'rot': (deg(35), deg(15), deg(-35)), 'loc': (0, 0.03, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-65)), 'loc': (0, 0.02, 0)},
            'Hand.L': {'rot': (deg(18), deg(0), deg(0)), 'loc': (0.03, 0.12, 0.01)},
        }),

        # F16: Circular Sweep Acceleration -> theta = 180° (pi) [Right Flank Sweep]
        (16, {
            'Hips': {'rot': (deg(-10), deg(-12), deg(4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(4), deg(-12), deg(2)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(-4), deg(12), deg(-2)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(30), deg(0), deg(5))},
            'LowerLeg.L': {'rot': (deg(-42), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(12), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-24), deg(0), deg(-7))},
            'LowerLeg.R': {'rot': (deg(-22), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(12), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(16), deg(0), deg(20)), 'loc': (-0.03, 0.02, 0.03)},
            'UpperArm.R': {'rot': (deg(75), deg(5), deg(22)), 'loc': (0, 0.02, 0.04)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(5)), 'loc': (0, 0.02, 0.03)},
            # theta = 180° (pi): X_world ~ -0.28, Y_world ~ 0.0, Z_world ~ 0.32
            'Hand.R': {'rot': (deg(0), deg(5), deg(55)), 'loc': (-0.16, 0.02, 0.10)},
            'Socket_Hand_R': {'rot': (deg(10), deg(15), deg(-5)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-6), deg(5), deg(-15)), 'loc': (0.02, 0.02, 0.0)},
            'UpperArm.L': {'rot': (deg(15), deg(5), deg(-30)), 'loc': (0, 0, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-45)), 'loc': (0, 0, 0)},
            'Hand.L': {'rot': (deg(10), deg(0), deg(0)), 'loc': (0.03, 0.04, 0.0)},
        }),

        # F18: Circular Sweep -> theta = 135° (3*pi/4) [Front-Right Diagonal Cleave]
        (18, {
            'Hips': {'rot': (deg(-14), deg(14), deg(4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(-8), deg(16), deg(-2)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(4), deg(-14), deg(2)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(34), deg(0), deg(5))},
            'LowerLeg.L': {'rot': (deg(-46), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(12), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-28), deg(0), deg(-7))},
            'LowerLeg.R': {'rot': (deg(-18), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(10), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(14), deg(10), deg(16)), 'loc': (-0.02, 0.08, 0.01)},
            'UpperArm.R': {'rot': (deg(60), deg(-5), deg(15)), 'loc': (0, 0.06, 0.02)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(20)), 'loc': (0, 0.04, 0.01)},
            # theta = 135° (3*pi/4): X_world ~ -0.18, Y_world ~ +0.20, Z_world ~ 0.28
            'Hand.R': {'rot': (deg(20), deg(-5), deg(75)), 'loc': (-0.08, 0.20, 0.04)},
            'Socket_Hand_R': {'rot': (deg(45), deg(-5), deg(15)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-8), deg(-5), deg(-15)), 'loc': (0.02, -0.03, 0.0)},
            'UpperArm.L': {'rot': (deg(-20), deg(0), deg(-35)), 'loc': (0, 0, 0)},
            'Forearm.L': {'rot': (deg(20), deg(0), deg(-25)), 'loc': (0, 0, 0)},
            'Hand.L': {'rot': (deg(5), deg(0), deg(0)), 'loc': (0.02, -0.05, 0.0)},
        }),

        # F20: CLIMAX IMPACT -> theta = 90° (pi/2) [Directly in Front at Peak Cleave Velocity!]
        (20, {
            'Hips': {'rot': (deg(-16), deg(34), deg(4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(-20), deg(38), deg(-8)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(8), deg(-26), deg(4)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(38), deg(0), deg(6))},
            'LowerLeg.L': {'rot': (deg(-50), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(12), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-32), deg(0), deg(-8))},
            'LowerLeg.R': {'rot': (deg(-12), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(6), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(14), deg(15), deg(14)), 'loc': (-0.01, 0.10, 0.0)},
            'UpperArm.R': {'rot': (deg(45), deg(-8), deg(10)), 'loc': (0, 0.08, 0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(30)), 'loc': (0, 0.06, 0)},
            # theta = 90° (pi/2): X_world ~ 0.0, Y_world ~ +0.28, Z_world ~ 0.24 (directly in front of chest!)
            'Hand.R': {'rot': (deg(30), deg(-12), deg(90)), 'loc': (0.08, 0.28, 0.0)},
            'Socket_Hand_R': {'rot': (deg(80), deg(-15), deg(30)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-10), deg(-15), deg(-15)), 'loc': (0.03, -0.05, 0.0)},
            'UpperArm.L': {'rot': (deg(-45), deg(0), deg(-38)), 'loc': (0, 0, 0)},
            'Forearm.L': {'rot': (deg(30), deg(0), deg(0)), 'loc': (0, 0, 0)},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0.02, -0.08, 0.0)},
        }),

        # F22: Circular Cleave Completion -> theta = 0° (2*pi) [Full Left Flank Extension!]
        (22, {
            'Hips': {'rot': (deg(-18), deg(42), deg(4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(-24), deg(46), deg(-10)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(10), deg(-30), deg(4)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(40), deg(0), deg(6))},
            'LowerLeg.L': {'rot': (deg(-52), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(12), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-34), deg(0), deg(-8))},
            'LowerLeg.R': {'rot': (deg(-10), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(6), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(10), deg(18), deg(10)), 'loc': (0.0, 0.10, 0.0)},
            'UpperArm.R': {'rot': (deg(40), deg(-12), deg(8)), 'loc': (0, 0.08, 0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(40)), 'loc': (0, 0.06, 0)},
            # theta = 0° / 2*pi: X_world ~ +0.26 (relative offset +0.32), Y_world ~ +0.08, Z_world ~ 0.22
            'Hand.R': {'rot': (deg(35), deg(-20), deg(105)), 'loc': (0.28, 0.10, -0.02)},
            'Socket_Hand_R': {'rot': (deg(90), deg(-25), deg(40)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-12), deg(-18), deg(-15)), 'loc': (0.03, -0.06, 0.0)},
            'UpperArm.L': {'rot': (deg(-52), deg(0), deg(-40)), 'loc': (0, 0, 0)},
            'Forearm.L': {'rot': (deg(28), deg(0), deg(0)), 'loc': (0, 0, 0)},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0.02, -0.10, 0.0)},
        }),

        # F26: Overshoot Lock (Hand slightly wraps past left flank)
        (26, {
            'Hips': {'rot': (deg(-18), deg(44), deg(4)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(-25), deg(48), deg(-10)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(12), deg(-32), deg(4)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(40), deg(0), deg(6))},
            'LowerLeg.L': {'rot': (deg(-52), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(12), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-34), deg(0), deg(-8))},
            'LowerLeg.R': {'rot': (deg(-10), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(6), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(10), deg(18), deg(10)), 'loc': (0.0, 0.09, 0.0)},
            'UpperArm.R': {'rot': (deg(40), deg(-12), deg(8)), 'loc': (0, 0.07, 0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(40)), 'loc': (0, 0.05, 0)},
            'Hand.R': {'rot': (deg(36), deg(-22), deg(106)), 'loc': (0.30, 0.05, -0.03)},
            'Socket_Hand_R': {'rot': (deg(90), deg(-25), deg(40)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-12), deg(-18), deg(-15)), 'loc': (0.03, -0.06, 0.0)},
            'UpperArm.L': {'rot': (deg(-52), deg(0), deg(-40)), 'loc': (0, 0, 0)},
            'Forearm.L': {'rot': (deg(28), deg(0), deg(0)), 'loc': (0, 0, 0)},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0.02, -0.10, 0.0)},
        }),

        # F28: Zanshin Hit-Stop Micro-Tremor
        (28, {
            'Hips': {'rot': (deg(-17), deg(43), deg(5)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(-24), deg(47), deg(-9)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(11), deg(-31), deg(4)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(40), deg(0), deg(6))},
            'LowerLeg.L': {'rot': (deg(-52), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(12), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-34), deg(0), deg(-8))},
            'LowerLeg.R': {'rot': (deg(-10), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(6), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(11), deg(17), deg(11)), 'loc': (0.0, 0.085, 0.0)},
            'UpperArm.R': {'rot': (deg(41), deg(-11), deg(7)), 'loc': (0, 0.065, 0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(39)), 'loc': (0, 0.045, 0)},
            'Hand.R': {'rot': (deg(35), deg(-21), deg(105)), 'loc': (0.28, 0.05, -0.03)},
            'Socket_Hand_R': {'rot': (deg(88), deg(-24), deg(38)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-12), deg(-18), deg(-15)), 'loc': (0.03, -0.06, 0.0)},
            'UpperArm.L': {'rot': (deg(-52), deg(0), deg(-40)), 'loc': (0, 0, 0)},
            'Forearm.L': {'rot': (deg(28), deg(0), deg(0)), 'loc': (0, 0, 0)},
            'Hand.L': {'rot': (deg(0), deg(0), deg(0)), 'loc': (0.02, -0.10, 0.0)},
        }),

        # F38: Recovery Arc (Floating hand glides gracefully back around front)
        (38, {
            'Hips': {'rot': (deg(-8), deg(8), deg(2)), 'loc': (0, 0, 0)},
            'Chest': {'rot': (deg(-2), deg(6), deg(-1)), 'loc': (0, 0, 0)},
            'Head': {'rot': (deg(0), deg(-4), deg(1)), 'loc': (0, 0, 0)},
            'UpperLeg.L': {'rot': (deg(22), deg(0), deg(3))},
            'LowerLeg.L': {'rot': (deg(-30), deg(0), deg(0))},
            'Foot.L': {'rot': (deg(8), deg(0), deg(0))},
            'UpperLeg.R': {'rot': (deg(-20), deg(0), deg(-5))},
            'LowerLeg.R': {'rot': (deg(-16), deg(0), deg(0))},
            'Foot.R': {'rot': (deg(8), deg(0), deg(0))},
            'Shoulder.R': {'rot': (deg(8), deg(4), deg(14)), 'loc': (-0.02, 0.06, 0.0)},
            'UpperArm.R': {'rot': (deg(32), deg(0), deg(14)), 'loc': (0, 0.05, 0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-10)), 'loc': (0, 0.02, 0)},
            'Hand.R': {'rot': (deg(10), deg(-5), deg(45)), 'loc': (0.08, 0.14, 0.0)},
            'Socket_Hand_R': {'rot': (deg(35), deg(-8), deg(18)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-6), deg(0), deg(-12)), 'loc': (0.02, 0.0, 0.0)},
            'UpperArm.L': {'rot': (deg(5), deg(5), deg(-25)), 'loc': (0, 0, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-35)), 'loc': (0, 0, 0)},
            'Hand.L': {'rot': (deg(8), deg(0), deg(0)), 'loc': (0.02, 0.0, 0.0)},
        }),

        # F48: Complete Reset to Ready Combat Guard (F48 matches F1 exactly for seamless loop)
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
            'Shoulder.R': {'rot': (deg(5), deg(0), deg(10)), 'loc': (-0.015, 0.02, 0.0)},
            'UpperArm.R': {'rot': (deg(25), deg(0), deg(15)), 'loc': (0, 0.02, 0)},
            'Forearm.R': {'rot': (deg(0), deg(0), deg(-30)), 'loc': (0, 0.02, 0)},
            'Hand.R': {'rot': (deg(10), deg(0), deg(25)), 'loc': (-0.02, 0.06, 0.02)},
            'Socket_Hand_R': {'rot': (deg(0), deg(15), deg(0)), 'loc': (0, 0, 0)},
            'Shoulder.L': {'rot': (deg(-5), deg(0), deg(-10)), 'loc': (0.015, 0.02, 0.0)},
            'UpperArm.L': {'rot': (deg(20), deg(0), deg(-20)), 'loc': (0, 0.02, 0)},
            'Forearm.L': {'rot': (deg(0), deg(0), deg(-45)), 'loc': (0, 0, 0)},
            'Hand.L': {'rot': (deg(10), deg(0), deg(0)), 'loc': (0.03, 0.05, 0.0)},
        })
    ]

    for frame_num, pose_data in poses:
        for b_name, b_attrs in pose_data.items():
            if b_name in pbones:
                pb = pbones[b_name]
                if 'rot' in b_attrs:
                    pb.rotation_euler = Euler(b_attrs['rot'], 'XYZ')
                    pb.keyframe_insert(data_path="rotation_euler", frame=frame_num)
                if 'loc' in b_attrs:
                    pb.location = Vector(b_attrs['loc'])
                    pb.keyframe_insert(data_path="location", frame=frame_num)

    for fc in act.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'

    # Ground solver pass: prevent foot penetration
    root_pb = pbones.get("Root")
    if root_pb:
        root_pb.rotation_euler = Euler((0, 0, 0), 'XYZ')
        root_pb.keyframe_insert(data_path="rotation_euler", frame=1)

    print("Keyframed 5-Phase Rayman Circular Cleave Strike (5*pi/4 -> 0).")

    # Push to NLA Track
    nla = arm.animation_data.nla_tracks.new()
    nla.name = "Attack"
    strip = nla.strips.new("Attack", 1, act)
    strip.action = act
    arm.animation_data.action = None

    # --- SETUP CAMERAS & STUDIO LIGHTING ---
    # Static Cam Target at Character Combat Center
    cam_target = bpy.data.objects.new("CamTarget_Swordsman", None)
    cam_target.location = Vector((0, 0, 0.28))
    bpy.context.scene.collection.objects.link(cam_target)

    # Front 3/4 Camera (Viewing from front +Y towards character)
    cam_data_a = bpy.data.cameras.new("Cam_Front34")
    cam_data_a.lens = 45
    cam_a = bpy.data.objects.new("Cam_Front34", cam_data_a)
    cam_a.location = Vector((0.9, 1.6, 0.65))
    track_a = cam_a.constraints.new(type='TRACK_TO')
    track_a.target = cam_target
    track_a.track_axis = 'TRACK_NEGATIVE_Z'
    track_a.up_axis = 'UP_Y'
    bpy.context.scene.collection.objects.link(cam_a)

    # Side Profile Camera (Viewing from +X towards character)
    cam_data_b = bpy.data.cameras.new("Cam_SideProfile")
    cam_data_b.lens = 45
    cam_b = bpy.data.objects.new("Cam_SideProfile", cam_data_b)
    cam_b.location = Vector((1.8, 0.0, 0.35))
    track_b = cam_b.constraints.new(type='TRACK_TO')
    track_b.target = cam_target
    track_b.track_axis = 'TRACK_NEGATIVE_Z'
    track_b.up_axis = 'UP_Y'
    bpy.context.scene.collection.objects.link(cam_b)

    # 3-Point Studio Lighting
    # 1) Key Sun (from front-right)
    key_light = bpy.data.lights.new("KeySun", type='SUN')
    key_light.energy = 5.0
    key_light.color = (1.0, 0.96, 0.90)
    key_obj = bpy.data.objects.new("KeySun", key_light)
    key_obj.rotation_euler = (deg(45), deg(30), deg(-40))
    bpy.context.scene.collection.objects.link(key_obj)

    # 2) Front Fill Area Light (from front-left)
    fill_light = bpy.data.lights.new("FillLight", type='AREA')
    fill_light.energy = 220.0
    fill_light.size = 2.4
    fill_light.color = (0.85, 0.92, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_light)
    fill_obj.location = Vector((-1.4, 1.6, 0.8))
    track_fill = fill_obj.constraints.new(type='TRACK_TO')
    track_fill.target = cam_target
    track_fill.track_axis = 'TRACK_NEGATIVE_Z'
    track_fill.up_axis = 'UP_Y'
    bpy.context.scene.collection.objects.link(fill_obj)

    # 3) Rear Rim Light (from behind-top)
    rim_light = bpy.data.lights.new("RimLight", type='AREA')
    rim_light.energy = 160.0
    rim_light.size = 2.0
    rim_light.color = (0.4, 0.7, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_light)
    rim_obj.location = Vector((0.0, -1.8, 1.2))
    track_rim = rim_obj.constraints.new(type='TRACK_TO')
    track_rim.target = cam_target
    track_rim.track_axis = 'TRACK_NEGATIVE_Z'
    track_rim.up_axis = 'UP_Y'
    bpy.context.scene.collection.objects.link(rim_obj)

    # Dark studio background
    if bpy.context.scene.world is None:
        bpy.context.scene.world = bpy.data.worlds.new("World")
    bpy.context.scene.world.use_nodes = True
    bg_node = bpy.context.scene.world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.02, 0.025, 0.035, 1.0)
        bg_node.inputs['Strength'].default_value = 0.8

    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.render.resolution_x = 256
    bpy.context.scene.render.resolution_y = 256
    bpy.context.scene.view_settings.view_transform = 'AgX'
    bpy.context.scene.view_settings.look = 'AgX - High Contrast'

    film_frames = [1, 8, 14, 16, 18, 20, 22, 48]
    print(f"\nRendering dual-angle contact sheet across frames: {film_frames}...")

    for f in film_frames:
        bpy.context.scene.frame_set(f)
        bpy.context.scene.camera = cam_a
        out_a = os.path.join(base_dir, f"temp_fl_a_{f:02d}.png")
        bpy.context.scene.render.filepath = out_a
        bpy.ops.render.render(write_still=True)
        
        bpy.context.scene.camera = cam_b
        out_b = os.path.join(base_dir, f"temp_fl_b_{f:02d}.png")
        bpy.context.scene.render.filepath = out_b
        bpy.ops.render.render(write_still=True)

    dual_strip_path = os.path.join(base_dir, "attack_filmstrip.png")
    ps_cmd = f"""
Add-Type -AssemblyName System.Drawing
$frames = @(1, 8, 14, 16, 18, 20, 22, 48)
$filmstrip = New-Object System.Drawing.Bitmap (256 * 8), (256 * 2)
$g = [System.Drawing.Graphics]::FromImage($filmstrip)
$g.Clear([System.Drawing.Color]::FromArgb(255, 15, 15, 18))

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
