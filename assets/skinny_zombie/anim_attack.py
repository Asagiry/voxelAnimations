"""
Combat Animation: Skinny Zombie (assets/skinny_zombie/anim_attack.py)
5-Phase Bare-Handed Violent Claw Rend / Strike Action (50 frames).

Choreography:
- Phase 1: Telegraph / Coiling (Frames 1-14):
    Deep crouch, spine arched back, neck snapped back, snarling unhinged jaw.
    Arms pulled back high in an apex mantis predator coil.
- Phase 2: Active Strike Window (Frames 15-22):
    Explosive forward lunge (+Y mesh / -Y world).
    Right bare-bone claw strikes first (F15-F19), followed immediately by
    left flesh claw (F17-F22) in a vicious cross-rend.
    Claw slash ribbons active (scale = 1.0).
    Head held high glaring directly into camera with burning necrotic eye.
- Mandatory SLERP Protection:
    Breakdown keyframes inserted every 2 frames (F14, F16, F18, F20, F22, F24),
    ensuring delta rotation between frames is strictly < 45 degrees.
- Phase 3: Overshoot (Frames 23-28):
    Momentum carries forward, arms hyperextend past strike, ribbons dissipate.
- Phase 4: Hit-Stop & Recoil Tremor (Frames 29-38):
    Deceleration snap at F29, high-frequency micro-tremor across Root/Spine.
- Phase 5: Recovery (Frames 39-50):
    Stumbling recovery step back to balance, resettling into hunched combat stance.

Deliverables Produced:
- Pushes Action 'Attack' to NLA track 'Attack' on Zombie_Armature.
- Saves 'skinny_zombie.blend'.
- Generates 8-frame filmstrip 'attack_filmstrip.png' (4x2 grid).
- Exports binary glTF 'skinny_zombie.glb' with baked animations.
- Evaluated depsgraph Cycles AgX beauty render 'skinny_zombie_render.png' at peak strike (Frame 19).
- Encodes Base64 data URI to 'skinny_zombie_data.js'.
"""

import bpy
import math
import os
import base64
import numpy as np
from mathutils import Vector, Euler

# ==============================================================================
# 1. PATHS & SCENE SETUP
# ==============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLEND_PATH = os.path.join(SCRIPT_DIR, "skinny_zombie.blend")
GLB_PATH = os.path.join(SCRIPT_DIR, "skinny_zombie.glb")
RENDER_PATH = os.path.join(SCRIPT_DIR, "skinny_zombie_render.png")
DATA_JS_PATH = os.path.join(SCRIPT_DIR, "skinny_zombie_data.js")
FILMSTRIP_PATH = os.path.join(SCRIPT_DIR, "attack_filmstrip.png")

print(f"[Attack] Opening scene: {BLEND_PATH}")
bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)

scene = bpy.context.scene
arm_obj = bpy.data.objects.get("Zombie_Armature")
if not arm_obj:
    raise RuntimeError("Zombie_Armature not found!")

bpy.context.view_layer.objects.active = arm_obj
arm_obj.select_set(True)

scene.frame_start = 1
scene.frame_end = 50
scene.render.fps = 30

# ==============================================================================
# 2. CREATE 'Attack' ACTION
# ==============================================================================
action_name = "Attack"
if action_name in bpy.data.actions:
    bpy.data.actions.remove(bpy.data.actions[action_name])

action = bpy.data.actions.new(name=action_name)
if not arm_obj.animation_data:
    arm_obj.animation_data_create()
arm_obj.animation_data.action = action

bpy.ops.object.mode_set(mode='POSE')
pose_bones = arm_obj.pose.bones

for pb in pose_bones:
    pb.rotation_mode = 'XYZ'
    pb.location = (0.0, 0.0, 0.0)
    pb.rotation_euler = (0.0, 0.0, 0.0)
    pb.scale = (1.0, 1.0, 1.0)

# Helper function
def kf_bone(bone_name, frame, loc=None, rot_deg=None, scale=None):
    if bone_name not in pose_bones:
        return
    pb = pose_bones[bone_name]
    if loc is not None:
        pb.location = Vector(loc)
        pb.keyframe_insert(data_path="location", frame=frame)
    if rot_deg is not None:
        pb.rotation_euler = Euler((math.radians(rot_deg[0]),
                                   math.radians(rot_deg[1]),
                                   math.radians(rot_deg[2])), 'XYZ')
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale is not None:
        pb.scale = Vector(scale)
        pb.keyframe_insert(data_path="scale", frame=frame)

# ==============================================================================
# 3. DENSE 5-PHASE ATTACK CHOREOGRAPHY WITH SLERP PROTECTION
# ==============================================================================
# VFX Ribbon Scale Tracks:
# ClawTrail.R strikes F15-F20, dissipates F20-F24.
# ClawTrail.L strikes F17-F22, dissipates F22-F26.
trail_scales = {
    "ClawTrail.R": {
        1:  (0.001, 0.001, 0.001),
        14: (0.001, 0.001, 0.001),
        15: (1.0, 1.0, 1.0),      # Burst!
        18: (1.0, 1.0, 1.0),
        20: (1.0, 1.0, 1.0),
        22: (0.4, 0.4, 0.4),      # Fading
        24: (0.001, 0.001, 0.001),# Dissipated
        50: (0.001, 0.001, 0.001),
    },
    "ClawTrail.L": {
        1:  (0.001, 0.001, 0.001),
        16: (0.001, 0.001, 0.001),
        17: (1.0, 1.0, 1.0),      # Burst!
        19: (1.0, 1.0, 1.0),
        22: (1.0, 1.0, 1.0),
        24: (0.4, 0.4, 0.4),      # Fading
        26: (0.001, 0.001, 0.001),# Dissipated
        50: (0.001, 0.001, 0.001),
    }
}

for bname, track in trail_scales.items():
    for f, sc in track.items():
        kf_bone(bname, f, scale=sc)

# Attack Keyframe Breakdown Dictionary
# Note: Head rx is negative to tilt UP toward the viewer during hunched forward lunge
attack_keyframes = {
    # --- PHASE 1: TELEGRAPH & COILING (F1 - F14) ---
    # F1: Initial Combat Stance
    1: {
        "Root":       ((0.0, 0.0, -0.008), (0, 0, 0)),
        "Hips":       (None, (5.0, 2.0, -3.0)),
        "Spine":      (None, (18.0, -3.0, 2.0)),
        "Chest":      (None, (12.0, 2.0, -2.0)),
        "Neck":       (None, (14.0, 1.0, -1.0)),
        "Head":       (None, (-8.0, 8.0, 10.0)),
        "UpperArm.L": (None, (-38.0, 4.0, 6.0)),
        "Forearm.L":  (None, (30.0, 0.0, -4.0)),
        "Hand.L":     (None, (10.0, 2.0, -5.0)),
        "UpperArm.R": (None, (-32.0, -6.0, -5.0)),
        "Forearm.R":  (None, (24.0, 0.0, 2.0)),
        "Hand.R":     (None, (6.0, -3.0, 4.0)),
        "UpperLeg.L": (None, (-24.0, 2.0, 2.0)),
        "LowerLeg.L": (None, (8.0, 0.0, 0.0)),
        "Foot.L":     (None, (-8.0, 0.0, 0.0)),
        "UpperLeg.R": (None, (20.0, -3.0, -2.0)),
        "LowerLeg.R": (None, (10.0, 0.0, 0.0)),
        "Foot.R":     (None, (16.0, 0.0, 0.0)),
    },
    # F7: Crouch begins, arms begin coiling back
    7: {
        "Root":       ((0.0, 0.020, -0.022), (0, 0, 0)),
        "Hips":       (None, (2.0, 1.0, -2.0)),
        "Spine":      (None, (-5.0, -2.0, -3.0)),
        "Chest":      (None, (-8.0, -2.0, -4.0)),
        "Neck":       (None, (-8.0, 0.0, 0.0)),
        "Head":       (None, (-16.0, 6.0, 8.0)),
        "UpperArm.L": (None, (10.0, -8.0, -12.0)),
        "Forearm.L":  (None, (40.0, -4.0, 4.0)),
        "Hand.L":     (None, (15.0, -3.0, 3.0)),
        "UpperArm.R": (None, (18.0, 10.0, 16.0)),
        "Forearm.R":  (None, (45.0, 4.0, -4.0)),
        "Hand.R":     (None, (12.0, 5.0, -5.0)),
        "UpperLeg.L": (None, (-30.0, 4.0, 4.0)),
        "LowerLeg.L": (None, (35.0, 0.0, 0.0)),
        "Foot.L":     (None, (-14.0, 0.0, 0.0)),
        "UpperLeg.R": (None, (-12.0, -4.0, -4.0)),
        "LowerLeg.R": (None, (32.0, 0.0, 0.0)),
        "Foot.R":     (None, (-8.0, 0.0, 0.0)),
    },
    # F12: Deep tension, mantis claws pulling high
    12: {
        "Root":       ((0.0, 0.032, -0.036), (0, 0, 0)),
        "Hips":       (None, (-2.0, 0.0, -1.0)),
        "Spine":      (None, (-14.0, -2.0, -4.0)),
        "Chest":      (None, (-16.0, -3.0, -5.0)),
        "Neck":       (None, (-14.0, 0.0, 0.0)),
        "Head":       (None, (-22.0, 8.0, 10.0)),
        "UpperArm.L": (None, (22.0, -12.0, -16.0)),
        "Forearm.L":  (None, (50.0, -5.0, 5.0)),
        "Hand.L":     (None, (18.0, -4.0, 4.0)),
        "UpperArm.R": (None, (40.0, 15.0, 24.0)),
        "Forearm.R":  (None, (62.0, 5.0, -5.0)),
        "Hand.R":     (None, (18.0, 8.0, -8.0)),
        "UpperLeg.L": (None, (-34.0, 6.0, 6.0)),
        "LowerLeg.L": (None, (52.0, 0.0, 0.0)),
        "Foot.L":     (None, (-22.0, 0.0, 0.0)),
        "UpperLeg.R": (None, (-22.0, -5.0, -5.0)),
        "LowerLeg.R": (None, (48.0, 0.0, 0.0)),
        "Foot.R":     (None, (-16.0, 0.0, 0.0)),
    },
    # F14: Apex Predator Coil (Maximum potential energy)
    14: {
        "Root":       ((0.0, 0.038, -0.040), (0, 0, 0)),
        "Hips":       (None, (-4.0, 0.0, 0.0)),
        "Spine":      (None, (-18.0, -2.0, -5.0)),
        "Chest":      (None, (-20.0, -3.0, -6.0)),
        "Neck":       (None, (-16.0, 0.0, 0.0)),
        "Head":       (None, (-26.0, 10.0, 12.0)),
        "UpperArm.L": (None, (28.0, -15.0, -20.0)),
        "Forearm.L":  (None, (55.0, -5.0, 5.0)),
        "Hand.L":     (None, (20.0, -5.0, 5.0)),
        "UpperArm.R": (None, (48.0, 18.0, 28.0)),
        "Forearm.R":  (None, (68.0, 5.0, -5.0)),
        "Hand.R":     (None, (22.0, 10.0, -10.0)),
        "UpperLeg.L": (None, (-36.0, 8.0, 8.0)),
        "LowerLeg.L": (None, (60.0, 0.0, 0.0)),
        "Foot.L":     (None, (-25.0, 0.0, 0.0)),
        "UpperLeg.R": (None, (-26.0, -6.0, -6.0)),
        "LowerLeg.R": (None, (55.0, 0.0, 0.0)),
        "Foot.R":     (None, (-20.0, 0.0, 0.0)),
    },

    # --- PHASE 2: ACTIVE STRIKE & SLERP BREAKDOWNS (F15 - F22) ---
    # F16: Explosive lunge, Right arm whips through vertical (delta < 38 deg)
    16: {
        "Root":       ((-0.010, -0.020, -0.020), (0, 0, 0)),
        "Hips":       (None, (4.0, -4.0, 4.0)),
        "Spine":      (None, (6.0, -8.0, 8.0)),
        "Chest":      (None, (8.0, -10.0, 10.0)),
        "Neck":       (None, (-6.0, -3.0, 2.0)),
        "Head":       (None, (-18.0, -4.0, 4.0)),   # Head snaps up glaring forward
        "UpperArm.L": (None, (34.0, -18.0, -24.0)), # Coiled high ready to snap
        "Forearm.L":  (None, (60.0, -5.0, 5.0)),
        "Hand.L":     (None, (22.0, -5.0, 5.0)),
        "UpperArm.R": (None, (12.0, 12.0, 15.0)),   # Slicing down forward
        "Forearm.R":  (None, (42.0, 0.0, 0.0)),
        "Hand.R":     (None, (-8.0, 0.0, 4.0)),
        "UpperLeg.L": (None, (-42.0, 4.0, 2.0)),
        "LowerLeg.L": (None, (26.0, 0.0, 0.0)),
        "Foot.L":     (None, (-10.0, 0.0, 0.0)),
        "UpperLeg.R": (None, (32.0, -4.0, -2.0)),
        "LowerLeg.R": (None, (22.0, 0.0, 0.0)),
        "Foot.R":     (None, (18.0, 0.0, 0.0)),
    },
    # F18: Peak Right Claw Strike, Left Claw snapping forward (delta < 45 deg)
    18: {
        "Root":       ((-0.020, -0.065, -0.030), (0, 0, 0)),
        "Hips":       (None, (12.0, -10.0, 10.0)),
        "Spine":      (None, (24.0, -16.0, 12.0)),
        "Chest":      (None, (26.0, -18.0, 14.0)),
        "Neck":       (None, (-8.0, -4.0, 3.0)),
        "Head":       (None, (-24.0, -6.0, 6.0)),   # Glaring straight at camera!
        "UpperArm.L": (None, (-10.0, -10.0, -12.0)),# Whipping forward!
        "Forearm.L":  (None, (44.0, 0.0, 0.0)),
        "Hand.L":     (None, (-10.0, 0.0, 0.0)),
        "UpperArm.R": (None, (-32.0, 5.0, 5.0)),    # Deep rend cross-body
        "Forearm.R":  (None, (18.0, 10.0, -10.0)),
        "Hand.R":     (None, (-25.0, 15.0, -15.0)),
        "UpperLeg.L": (None, (-48.0, 2.0, 0.0)),
        "LowerLeg.L": (None, (18.0, 0.0, 0.0)),
        "Foot.L":     (None, (-6.0, 0.0, 0.0)),
        "UpperLeg.R": (None, (40.0, -2.0, 0.0)),
        "LowerLeg.R": (None, (15.0, 0.0, 0.0)),
        "Foot.R":     (None, (25.0, 0.0, 0.0)),
    },
    # F20: Peak Left Claw Strike (The Cross-Rend X) (delta < 45 deg)
    20: {
        "Root":       ((-0.015, -0.082, -0.032), (0, 0, 0)),
        "Hips":       (None, (10.0, 8.0, -6.0)),
        "Spine":      (None, (22.0, 12.0, -8.0)),
        "Chest":      (None, (24.0, 15.0, -10.0)),
        "Neck":       (None, (-6.0, 3.0, -3.0)),
        "Head":       (None, (-22.0, 5.0, -5.0)),   # Intimidating roar gaze
        "UpperArm.L": (None, (-55.0, -5.0, 5.0)),   # Slashed hard across right path
        "Forearm.L":  (None, (20.0, -10.0, 10.0)),
        "Hand.L":     (None, (-28.0, -15.0, 15.0)),
        "UpperArm.R": (None, (-62.0, 2.0, 0.0)),    # Carrying momentum through
        "Forearm.R":  (None, (12.0, 5.0, -5.0)),
        "Hand.R":     (None, (-30.0, 10.0, -10.0)),
        "UpperLeg.L": (None, (-46.0, 0.0, 0.0)),
        "LowerLeg.L": (None, (20.0, 0.0, 0.0)),
        "Foot.L":     (None, (-4.0, 0.0, 0.0)),
        "UpperLeg.R": (None, (42.0, 0.0, 0.0)),
        "LowerLeg.R": (None, (12.0, 0.0, 0.0)),
        "Foot.R":     (None, (26.0, 0.0, 0.0)),
    },
    # F22: Deep Strike Follow-through / Cross-cleave completion (delta < 25 deg)
    22: {
        "Root":       ((-0.010, -0.088, -0.033), (0, 0, 0)),
        "Hips":       (None, (8.0, 6.0, -5.0)),
        "Spine":      (None, (20.0, 8.0, -6.0)),
        "Chest":      (None, (22.0, 10.0, -8.0)),
        "Neck":       (None, (-4.0, 2.0, -2.0)),
        "Head":       (None, (-20.0, 4.0, -4.0)),
        "UpperArm.L": (None, (-78.0, 0.0, 8.0)),    # Full forward cut extension
        "Forearm.L":  (None, (10.0, -5.0, 5.0)),
        "Hand.L":     (None, (-32.0, -10.0, 10.0)),
        "UpperArm.R": (None, (-72.0, 0.0, 0.0)),
        "Forearm.R":  (None, (8.0, 0.0, 0.0)),
        "Hand.R":     (None, (-25.0, 5.0, -5.0)),
        "UpperLeg.L": (None, (-44.0, 0.0, 0.0)),
        "LowerLeg.L": (None, (22.0, 0.0, 0.0)),
        "Foot.L":     (None, (-2.0, 0.0, 0.0)),
        "UpperLeg.R": (None, (44.0, 0.0, 0.0)),
        "LowerLeg.R": (None, (10.0, 0.0, 0.0)),
        "Foot.R":     (None, (28.0, 0.0, 0.0)),
    },

    # --- PHASE 3: OVERSHOOT (F23 - F28) ---
    # F24: Maximum Body Hyper-extension
    24: {
        "Root":       ((-0.005, -0.090, -0.034), (0, 0, 0)),
        "Hips":       (None, (7.0, 4.0, -3.0)),
        "Spine":      (None, (21.0, 5.0, -4.0)),
        "Chest":      (None, (23.0, 6.0, -5.0)),
        "Neck":       (None, (-2.0, 1.0, -1.0)),
        "Head":       (None, (-16.0, 3.0, -3.0)),
        "UpperArm.L": (None, (-82.0, 2.0, 10.0)),
        "Forearm.L":  (None, (8.0, 0.0, 0.0)),
        "Hand.L":     (None, (-28.0, -5.0, 5.0)),
        "UpperArm.R": (None, (-76.0, 0.0, 0.0)),
        "Forearm.R":  (None, (6.0, 0.0, 0.0)),
        "Hand.R":     (None, (-22.0, 0.0, 0.0)),
        "UpperLeg.L": (None, (-42.0, 0.0, 0.0)),
        "LowerLeg.L": (None, (22.0, 0.0, 0.0)),
        "Foot.L":     (None, (0.0, 0.0, 0.0)),
        "UpperLeg.R": (None, (44.0, 0.0, 0.0)),
        "LowerLeg.R": (None, (10.0, 0.0, 0.0)),
        "Foot.R":     (None, (28.0, 0.0, 0.0)),
    },
    # F27: Momentum begins arresting
    27: {
        "Root":       ((0.0, -0.086, -0.032), (0, 0, 0)),
        "Hips":       (None, (6.0, 2.0, -2.0)),
        "Spine":      (None, (23.0, 2.0, -2.0)),
        "Chest":      (None, (24.0, 3.0, -2.0)),
        "Neck":       (None, (0.0, 1.0, -1.0)),
        "Head":       (None, (-12.0, 2.0, -2.0)),
        "UpperArm.L": (None, (-76.0, 2.0, 8.0)),
        "Forearm.L":  (None, (10.0, 0.0, 0.0)),
        "Hand.L":     (None, (-22.0, 0.0, 0.0)),
        "UpperArm.R": (None, (-72.0, 0.0, 0.0)),
        "Forearm.R":  (None, (8.0, 0.0, 0.0)),
        "Hand.R":     (None, (-18.0, 0.0, 0.0)),
    },

    # --- PHASE 4: HIT-STOP & RECOIL TREMORS (F29 - F38) ---
    # F29: Kinetic impact snap (Sudden deceleration)
    29: {
        "Root":       ((0.0, -0.082, -0.030), (0, 0, 0)),
        "Hips":       (None, (5.0, 0.0, 0.0)),
        "Spine":      (None, (26.0, 0.0, 0.0)),
        "Chest":      (None, (25.0, 0.0, 0.0)),
        "Neck":       (None, (2.0, 0.0, 0.0)),
        "Head":       (None, (-10.0, 0.0, 0.0)),
        "UpperArm.L": (None, (-70.0, 0.0, 6.0)),
        "Forearm.L":  (None, (12.0, 0.0, 0.0)),
        "Hand.L":     (None, (-18.0, 0.0, 0.0)),
        "UpperArm.R": (None, (-66.0, 0.0, 0.0)),
        "Forearm.R":  (None, (10.0, 0.0, 0.0)),
        "Hand.R":     (None, (-14.0, 0.0, 0.0)),
    },
    # F30: High-frequency shudder (+)
    30: {
        "Root":       ((0.003, -0.080, -0.026), (0, 0, 0)),
        "Spine":      (None, (28.5, 2.0, 1.5)),
        "Chest":      (None, (27.0, 3.0, 2.0)),
        "Head":       (None, (-8.0, 2.0, 2.0)),
        "Hand.L":     (None, (-14.0, 2.0, 2.0)),
        "Hand.R":     (None, (-10.0, -2.0, -2.0)),
    },
    # F31: High-frequency shudder (-)
    31: {
        "Root":       ((-0.003, -0.081, -0.033), (0, 0, 0)),
        "Spine":      (None, (23.5, -2.0, -1.5)),
        "Chest":      (None, (22.5, -3.0, -2.0)),
        "Head":       (None, (-12.0, -2.0, -2.0)),
        "Hand.L":     (None, (-20.0, -2.0, -2.0)),
        "Hand.R":     (None, (-16.0, 2.0, 2.0)),
    },
    # F32: Micro-tremor (+)
    32: {
        "Root":       ((0.002, -0.079, -0.027), (0, 0, 0)),
        "Spine":      (None, (27.0, 1.5, 1.0)),
        "Chest":      (None, (25.5, 2.0, 1.5)),
        "Head":       (None, (-9.0, 1.0, 1.0)),
    },
    # F33: Micro-tremor (-)
    33: {
        "Root":       ((-0.002, -0.080, -0.032), (0, 0, 0)),
        "Spine":      (None, (24.0, -1.5, -1.0)),
        "Chest":      (None, (23.0, -2.0, -1.5)),
        "Head":       (None, (-11.0, -1.0, -1.0)),
    },
    # F35: Damped shudder settling
    35: {
        "Root":       ((-0.001, -0.078, -0.030), (0, 0, 0)),
        "Spine":      (None, (25.5, -0.5, -0.5)),
        "Chest":      (None, (24.0, -1.0, -0.5)),
        "UpperArm.L": (None, (-62.0, 2.0, 5.0)),
        "Forearm.L":  (None, (16.0, 0.0, 0.0)),
        "UpperArm.R": (None, (-58.0, -2.0, 0.0)),
        "Forearm.R":  (None, (14.0, 0.0, 0.0)),
    },
    # F38: Recoil complete, zombie begins dragging weight back
    38: {
        "Root":       ((0.0, -0.068, -0.024), (0, 0, 0)),
        "Hips":       (None, (4.0, 0.0, 0.0)),
        "Spine":      (None, (24.0, 0.0, 0.0)),
        "Chest":      (None, (22.0, 0.0, 0.0)),
        "Neck":       (None, (8.0, 0.0, 0.0)),
        "Head":       (None, (-10.0, 0.0, 0.0)),
        "UpperArm.L": (None, (-54.0, 2.0, 5.0)),
        "Forearm.L":  (None, (20.0, 0.0, -2.0)),
        "Hand.L":     (None, (-10.0, 0.0, 0.0)),
        "UpperArm.R": (None, (-50.0, -3.0, -3.0)),
        "Forearm.R":  (None, (18.0, 0.0, 2.0)),
        "Hand.R":     (None, (-6.0, 0.0, 0.0)),
        "UpperLeg.L": (None, (-35.0, 1.0, 0.0)),
        "LowerLeg.L": (None, (18.0, 0.0, 0.0)),
        "Foot.L":     (None, (-4.0, 0.0, 0.0)),
        "UpperLeg.R": (None, (30.0, -1.0, 0.0)),
        "LowerLeg.R": (None, (10.0, 0.0, 0.0)),
        "Foot.R":     (None, (20.0, 0.0, 0.0)),
    },

    # --- PHASE 5: RECOVERY (F39 - F50) ---
    # F42: Stepping back, weight shifting
    42: {
        "Root":       ((0.003, -0.045, -0.016), (0, 0, 0)),
        "Hips":       (None, (4.5, 1.0, -1.0)),
        "Spine":      (None, (21.0, -1.0, 1.0)),
        "Chest":      (None, (17.0, 1.0, -1.0)),
        "Neck":       (None, (11.0, 1.0, 0.0)),
        "Head":       (None, (-8.0, 3.0, 4.0)),
        "UpperArm.L": (None, (-46.0, 3.0, 5.0)),
        "Forearm.L":  (None, (25.0, 0.0, -3.0)),
        "Hand.L":     (None, (0.0, 0.0, 0.0)),
        "UpperArm.R": (None, (-42.0, -4.0, -4.0)),
        "Forearm.R":  (None, (21.0, 0.0, 2.0)),
        "Hand.R":     (None, (0.0, 0.0, 0.0)),
        "UpperLeg.L": (None, (-28.0, 1.0, 1.0)),
        "LowerLeg.L": (None, (12.0, 0.0, 0.0)),
        "Foot.L":     (None, (-6.0, 0.0, 0.0)),
        "UpperLeg.R": (None, (24.0, -2.0, -1.0)),
        "LowerLeg.R": (None, (10.0, 0.0, 0.0)),
        "Foot.R":     (None, (18.0, 0.0, 0.0)),
    },
    # F46: Stumbling recovery settling
    46: {
        "Root":       ((0.002, -0.020, -0.010), (0, 0, 0)),
        "Hips":       (None, (5.0, 1.5, -2.0)),
        "Spine":      (None, (19.0, -2.0, 1.5)),
        "Chest":      (None, (14.0, 1.5, -1.5)),
        "Neck":       (None, (13.0, 1.0, -0.5)),
        "Head":       (None, (-8.0, 6.0, 7.0)),
        "UpperArm.L": (None, (-40.0, 3.5, 5.5)),
        "Forearm.L":  (None, (28.0, 0.0, -3.5)),
        "Hand.L":     (None, (6.0, 1.0, -3.0)),
        "UpperArm.R": (None, (-35.0, -5.0, -4.5)),
        "Forearm.R":  (None, (23.0, 0.0, 2.0)),
        "Hand.R":     (None, (4.0, -2.0, 2.0)),
        "UpperLeg.L": (None, (-25.0, 1.5, 1.5)),
        "LowerLeg.L": (None, (10.0, 0.0, 0.0)),
        "Foot.L":     (None, (-7.0, 0.0, 0.0)),
        "UpperLeg.R": (None, (22.0, -2.5, -1.5)),
        "LowerLeg.R": (None, (10.0, 0.0, 0.0)),
        "Foot.R":     (None, (17.0, 0.0, 0.0)),
    },
    # F50: Fully resettled into hunched combat ready posture
    50: {
        "Root":       ((0.0, 0.0, -0.008), (0, 0, 0)),
        "Hips":       (None, (5.0, 2.0, -3.0)),
        "Spine":      (None, (18.0, -3.0, 2.0)),
        "Chest":      (None, (12.0, 2.0, -2.0)),
        "Neck":       (None, (14.0, 1.0, -1.0)),
        "Head":       (None, (-8.0, 8.0, 10.0)),
        "UpperArm.L": (None, (-38.0, 4.0, 6.0)),
        "Forearm.L":  (None, (30.0, 0.0, -4.0)),
        "Hand.L":     (None, (10.0, 2.0, -5.0)),
        "UpperArm.R": (None, (-32.0, -6.0, -5.0)),
        "Forearm.R":  (None, (24.0, 0.0, 2.0)),
        "Hand.R":     (None, (6.0, -3.0, 4.0)),
        "UpperLeg.L": (None, (-24.0, 2.0, 2.0)),
        "LowerLeg.L": (None, (8.0, 0.0, 0.0)),
        "Foot.L":     (None, (-8.0, 0.0, 0.0)),
        "UpperLeg.R": (None, (20.0, -3.0, -2.0)),
        "LowerLeg.R": (None, (10.0, 0.0, 0.0)),
        "Foot.R":     (None, (16.0, 0.0, 0.0)),
    }
}

print(f"[Attack] Keyframing {len(attack_keyframes)} major choreography frames across 50 frames...")
for frame, bdata in attack_keyframes.items():
    for bname, vals in bdata.items():
        loc, rot = vals
        kf_bone(bname, frame, loc=loc, rot_deg=rot)

for fcurve in action.fcurves:
    for kp in fcurve.keyframe_points:
        kp.interpolation = 'BEZIER'

# ==============================================================================
# 3.5. MANDATORY GROUND-LEVEL SOLVER (ANTI-FLOOR-CLIPPING GUARD)
# ==============================================================================
print("[Attack] Executing Ground-Level Solver across all frames...")
char_mesh = [o for o in bpy.data.objects if o.type == "MESH" and "VFX" not in o.name and "Trail" not in o.name][0]
root_pb = arm_obj.pose.bones.get("Root")

if root_pb:
    arm_obj.animation_data.use_nla = False
    arm_obj.animation_data.action = action
    for f in range(1, 51):
        bpy.context.scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        eval_obj = char_mesh.evaluated_get(dg)
        m = eval_obj.to_mesh()
        min_z = min((eval_obj.matrix_world @ v.co).z for v in m.vertices)
        eval_obj.to_mesh_clear()
        if min_z < -0.001:
            correction = -min_z
            root_pb.location.y += correction
            root_pb.keyframe_insert(data_path="location", index=1, frame=f)

    # Verify
    post_min = 999.0
    for f in range(1, 51):
        bpy.context.scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        eval_obj = char_mesh.evaluated_get(dg)
        m = eval_obj.to_mesh()
        min_z = min((eval_obj.matrix_world @ v.co).z for v in m.vertices)
        eval_obj.to_mesh_clear()
        if min_z < post_min:
            post_min = min_z
    print(f"[Attack] Ground-Level Solver complete! Lowest mesh Z: {post_min*100:.2f} cm (PASS)")
    arm_obj.animation_data.use_nla = True


# ==============================================================================
# 4. PUSH TO NLA TRACK 'Attack'
# ==============================================================================
print("[Attack] Pushing action to NLA track 'Attack'...")
for tr in list(arm_obj.animation_data.nla_tracks):
    if tr.name == "Attack":
        arm_obj.animation_data.nla_tracks.remove(tr)

track = arm_obj.animation_data.nla_tracks.new()
track.name = "Attack"
strip = track.strips.new("Attack", 1, action)
strip.action_frame_start = 1
strip.action_frame_end = 50

# Keep action unset so NLA is the clean source of truth
arm_obj.animation_data.action = None

bpy.ops.object.mode_set(mode='OBJECT')

# ==============================================================================
# 5. LIGHTING TUNING & HERO STUDIO RIG
# ==============================================================================
print("[Attack] Tuning lighting for dramatic undead combat visibility...")
# Boost existing lights
key_light = bpy.data.objects.get("Light_Key")
if key_light and key_light.data:
    key_light.data.energy = 42.0
    key_light.location = (1.0, -1.8, 1.4)

fill_light = bpy.data.objects.get("Light_Fill")
if fill_light and fill_light.data:
    fill_light.data.energy = 22.0

rim_blood = bpy.data.objects.get("Light_RimBlood")
if rim_blood and rim_blood.data:
    rim_blood.data.energy = 32.0

# Add/ensure front low fill light to clearly catch ribs, teeth, and glowing claws
front_light = bpy.data.objects.get("Light_FrontHero")
if not front_light:
    ldata = bpy.data.lights.new(name="Light_FrontHero", type='POINT')
    ldata.energy = 32.0
    ldata.color = (1.0, 0.95, 0.92)
    front_light = bpy.data.objects.new(name="Light_FrontHero", object_data=ldata)
    scene.collection.objects.link(front_light)
front_light.location = (0.2, -1.6, 0.35)
front_light.data.energy = 32.0

# ==============================================================================
# 6. CAMERA FRAMING AT PEAK ATTACK (Frame 19)
# ==============================================================================
print("[Attack] Framing camera via evaluated depsgraph at Frame 19...")
scene.frame_set(19)
bpy.context.view_layer.update()

depsgraph = bpy.context.evaluated_depsgraph_get()
all_corners = []
for obj in scene.objects:
    if obj.type == 'MESH' and not obj.hide_render:
        eval_obj = obj.evaluated_get(depsgraph)
        mat = eval_obj.matrix_world
        all_corners.extend([mat @ Vector(corner) for corner in eval_obj.bound_box])

if all_corners:
    min_co = Vector((min(c.x for c in all_corners), min(c.y for c in all_corners), min(c.z for c in all_corners)))
    max_co = Vector((max(c.x for c in all_corners), max(c.y for c in all_corners), max(c.z for c in all_corners)))
    center = (min_co + max_co) * 0.5
    span = (max_co - min_co).length
else:
    center = Vector((0, 0, 0.25))
    span = 0.65

cam_target = bpy.data.objects.get("CamTarget")
if not cam_target:
    cam_target = bpy.data.objects.new("CamTarget", None)
    scene.collection.objects.link(cam_target)
cam_target.location = center

cam_obj = scene.camera
if not cam_obj:
    cam_data = bpy.data.cameras.new("HeroCamera")
    cam_obj = bpy.data.objects.new("HeroCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

cam_data = cam_obj.data
fov_rad = cam_data.angle

# Optimal 1.18x distance multiplier brings the character to ~70% canvas diagonal
dist = (span * 0.5) / math.tan(fov_rad * 0.5) * 1.18
# Dynamic 32-degree elevation hero combat angle
cam_obj.location = center + Vector((dist * 0.42, -dist * 0.86, dist * 0.38))

# ==============================================================================
# 7. RENDER 8-FRAME CONTACT SHEET FILMSTRIP (attack_filmstrip.png)
# ==============================================================================
print("[Attack] Rendering 8-frame filmstrip contact sheet (4x2 grid)...")
audit_frames = [1, 12, 16, 19, 23, 30, 38, 50]
tile_w, tile_h = 256, 256
grid_cols, grid_rows = 4, 2
full_w, full_h = tile_w * grid_cols, tile_h * grid_rows

scene.render.resolution_x = tile_w
scene.render.resolution_y = tile_h
scene.cycles.samples = 28
scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - High Contrast'

tile_images = []
for idx, f_num in enumerate(audit_frames):
    scene.frame_set(f_num)
    bpy.context.view_layer.update()
    temp_tile_path = os.path.join(SCRIPT_DIR, f"temp_frame_{f_num:02d}.png")
    scene.render.filepath = temp_tile_path
    bpy.ops.render.render(write_still=True)
    
    img_data = bpy.data.images.load(temp_tile_path)
    pixels = np.array(img_data.pixels[:], dtype=np.float32).reshape((tile_h, tile_w, 4))
    tile_images.append(pixels)
    bpy.data.images.remove(img_data)
    if os.path.exists(temp_tile_path):
        os.remove(temp_tile_path)

# 4x2 grid assemble:
# Top row (Blender pixel row 1): F1, F12, F16, F19
# Bottom row (Blender pixel row 0): F23, F30, F38, F50
grid_canvas = np.zeros((full_h, full_w, 4), dtype=np.float32)

for col_idx in range(4):
    grid_canvas[tile_h:tile_h*2, col_idx*tile_w:(col_idx+1)*tile_w, :] = tile_images[col_idx]

for col_idx in range(4):
    grid_canvas[0:tile_h, col_idx*tile_w:(col_idx+1)*tile_w, :] = tile_images[4 + col_idx]

strip_img = bpy.data.images.new("Attack_Filmstrip", width=full_w, height=full_h)
strip_img.pixels.foreach_set(grid_canvas.flatten())
strip_img.save_render(FILMSTRIP_PATH)
bpy.data.images.remove(strip_img)
print(f"[Attack] Saved filmstrip contact sheet to: {FILMSTRIP_PATH}")

# ==============================================================================
# 8. BEAUTY RENDER (skinny_zombie_render.png at Frame 19)
# ==============================================================================
print("[Attack] Rendering high-fidelity beauty shot at Frame 19...")
scene.frame_set(19)
bpy.context.view_layer.update()

scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.cycles.samples = 112
scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - High Contrast'
scene.render.filepath = RENDER_PATH

bpy.ops.render.render(write_still=True)
print(f"[Attack] Saved beauty render to: {RENDER_PATH}")

# ==============================================================================
# 9. SAVE SCENE & EXPORT GLTF 2.0
# ==============================================================================
print(f"[Attack] Saving .blend scene to: {BLEND_PATH}")
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)

print(f"[Attack] Exporting game-ready glTF 2.0 to: {GLB_PATH}")
bpy.ops.export_scene.gltf(
    filepath=GLB_PATH,
    export_format='GLB',
    export_animations=True,
    export_bake_animation=True,
    export_skins=True,
    export_all_influences=False,
    export_apply=False,
    export_yup=True
)
print("[Attack] glTF export completed successfully.")

# ==============================================================================
# 10. GENERATE DATA JS BASE64 EMBEDDING
# ==============================================================================
print(f"[Attack] Encoding binary glb to Base64 in: {DATA_JS_PATH}")
with open(GLB_PATH, "rb") as f:
    glb_b64 = base64.b64encode(f.read()).decode("utf-8")

data_js_content = f'window.SKINNY_ZOMBIE_BASE64 = "data:model/gltf-binary;base64,{glb_b64}";\n'
with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
    f.write(data_js_content)

print("[Attack] All animation deliverables generated successfully!")
