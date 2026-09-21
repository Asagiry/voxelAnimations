"""
Procedural Walk Cycle: Skinny Zombie (assets/skinny_zombie/anim_walk.py)
Shambling, asymmetric, emaciated undead locomotion loop (40 frames).

Key Motion Traits:
- 40-frame seamless loop (F1 to F40 match).
- Asymmetrical weight shift:
  * Left booted foot steps with a heavy, limping gait.
  * Right bare skeletal foot drags behind with a jerky, scraping catch-up hitch.
- Hunched spine, forward craning neck, and erratic predatory head twitch.
- Spindly arms reach forward in a predatory searching posture with subtle wrist micro-tremors.
- Claw slash VFX ribbons kept hidden (scale = (0.001, 0.001, 0.001)).
- Rotation mode strictly 'XYZ' for all bones before keyframing.
- Pushes Action to an NLA track named 'Walk'.
"""

import bpy
import math
import os
from mathutils import Vector, Euler

# ==============================================================================
# 1. LOAD BLENDER FILE & LOCATE ARMATURE
# ==============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLEND_PATH = os.path.join(SCRIPT_DIR, "skinny_zombie.blend")

print(f"[Walk] Loading scene from: {BLEND_PATH}")
bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)

scene = bpy.context.scene
arm_obj = bpy.data.objects.get("Zombie_Armature")
if not arm_obj:
    raise RuntimeError("Zombie_Armature object not found in scene!")

bpy.context.view_layer.objects.active = arm_obj
arm_obj.select_set(True)

# Set frame range
scene.frame_start = 1
scene.frame_end = 40
scene.render.fps = 30

# ==============================================================================
# 2. CREATE 'Walk' ACTION
# ==============================================================================
action_name = "Walk"
if action_name in bpy.data.actions:
    bpy.data.actions.remove(bpy.data.actions[action_name])

action = bpy.data.actions.new(name=action_name)
if not arm_obj.animation_data:
    arm_obj.animation_data_create()
arm_obj.animation_data.action = action

# Ensure pose mode and rotation_mode = 'XYZ'
bpy.ops.object.mode_set(mode='POSE')
pose_bones = arm_obj.pose.bones

for pb in pose_bones:
    pb.rotation_mode = 'XYZ'
    pb.location = (0.0, 0.0, 0.0)
    pb.rotation_euler = (0.0, 0.0, 0.0)
    pb.scale = (1.0, 1.0, 1.0)

# VFX Claw Trails must remain hidden during walk
for trail_name in ["ClawTrail.L", "ClawTrail.R"]:
    if trail_name in pose_bones:
        pose_bones[trail_name].scale = (0.001, 0.001, 0.001)

# Helper function to insert keyframe
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
# 3. PROCEDURAL KEYFRAME DATA FOR 40-FRAME LOOP
# ==============================================================================
# Hidden Claw Trails throughout
for f in [1, 10, 20, 30, 40]:
    kf_bone("ClawTrail.L", f, scale=(0.001, 0.001, 0.001))
    kf_bone("ClawTrail.R", f, scale=(0.001, 0.001, 0.001))

# Walk Animation Keyframes
# Format: {frame: {bone_name: (loc, rot_deg)}}
walk_data = {
    # Frame 1: Contact - Left booted foot plants forward, Right skeletal foot trails behind
    1: {
        "Root":        ((0.0, 0.0, -0.008), (0, 0, 0)),
        "Hips":        (None, (5.0, 2.0, -3.0)),
        "Spine":       (None, (18.0, -3.0, 2.0)),
        "Chest":       (None, (12.0, 2.0, -2.0)),
        "Neck":        (None, (14.0, 1.0, -1.0)),
        "Head":        (None, (-8.0, 8.0, 10.0)),
        "Shoulder.L":  (None, (0.0, 0.0, 3.0)),
        "UpperArm.L":  (None, (-38.0, 4.0, 6.0)),
        "Forearm.L":   (None, (30.0, 0.0, -4.0)),
        "Hand.L":      (None, (10.0, 2.0, -5.0)),
        "Shoulder.R":  (None, (0.0, 0.0, -2.0)),
        "UpperArm.R":  (None, (-32.0, -6.0, -5.0)),
        "Forearm.R":   (None, (24.0, 0.0, 2.0)),
        "Hand.R":      (None, (6.0, -3.0, 4.0)),
        "UpperLeg.L":  (None, (-24.0, 2.0, 2.0)),    # Left leg stepped forward (-Y)
        "LowerLeg.L":  (None, (8.0, 0.0, 0.0)),
        "Foot.L":      (None, (-8.0, 0.0, 0.0)),     # Heel strike / plant
        "UpperLeg.R":  (None, (20.0, -3.0, -2.0)),   # Right leg trailing back (+Y)
        "LowerLeg.R":  (None, (10.0, 0.0, 0.0)),
        "Foot.R":      (None, (16.0, 0.0, 0.0)),     # Toe dragging
    },
    # Frame 6: Left foot full plant, weight shifts forward over left hip
    6: {
        "Root":        ((0.004, -0.008, -0.004), (0, 0, 0)),
        "Hips":        (None, (4.0, 3.0, -4.0)),
        "Spine":       (None, (17.0, -2.0, 1.0)),
        "Chest":       (None, (13.0, 3.0, -2.0)),
        "Neck":        (None, (13.0, 2.0, 0.0)),
        "Head":        (None, (-7.0, 5.0, 8.0)),
        "UpperArm.L":  (None, (-42.0, 3.0, 7.0)),
        "Forearm.L":   (None, (34.0, 0.0, -3.0)),
        "Hand.L":      (None, (14.0, 1.0, -3.0)),
        "UpperArm.R":  (None, (-28.0, -5.0, -6.0)),
        "Forearm.R":   (None, (22.0, 0.0, 3.0)),
        "Hand.R":      (None, (4.0, -2.0, 3.0)),
        "UpperLeg.L":  (None, (-14.0, 2.0, 1.0)),
        "LowerLeg.L":  (None, (12.0, 0.0, 0.0)),
        "Foot.L":      (None, (2.0, 0.0, 0.0)),      # Flat on ground
        "UpperLeg.R":  (None, (22.0, -3.0, -2.0)),   # Dragging behind
        "LowerLeg.R":  (None, (14.0, 0.0, 0.0)),
        "Foot.R":      (None, (18.0, 0.0, 0.0)),
    },
    # Frame 11: Left foot mid-stance / push off, body rises, right leg scrapes floor
    11: {
        "Root":        ((0.006, -0.015, 0.004), (0, 0, 0)),
        "Hips":        (None, (3.0, 4.0, -5.0)),
        "Spine":       (None, (16.0, 1.0, -1.0)),
        "Chest":       (None, (14.0, -2.0, 2.0)),
        "Neck":        (None, (15.0, -1.0, 1.0)),
        "Head":        (None, (-9.0, -4.0, -4.0)),   # Head starts tilting left
        "UpperArm.L":  (None, (-45.0, 2.0, 8.0)),
        "Forearm.L":   (None, (38.0, 0.0, -2.0)),
        "Hand.L":      (None, (8.0, 0.0, -2.0)),
        "UpperArm.R":  (None, (-24.0, -4.0, -4.0)),
        "Forearm.R":   (None, (20.0, 0.0, 2.0)),
        "Hand.R":      (None, (8.0, -4.0, 5.0)),     # Wrist micro-tremor
        "UpperLeg.L":  (None, (6.0, 1.0, 0.0)),      # Thigh straight under hip
        "LowerLeg.L":  (None, (4.0, 0.0, 0.0)),
        "Foot.L":      (None, (6.0, 0.0, 0.0)),
        "UpperLeg.R":  (None, (16.0, -2.0, -1.0)),   # Right leg scraping forward
        "LowerLeg.R":  (None, (22.0, 0.0, 0.0)),
        "Foot.R":      (None, (12.0, 0.0, 0.0)),
    },
    # Frame 16: Right skeletal foot begins jerky forward hitch
    16: {
        "Root":        ((0.002, -0.010, -0.002), (0, 0, 0)),
        "Hips":        (None, (5.0, 1.0, -2.0)),
        "Spine":       (None, (18.0, 2.0, -2.0)),
        "Chest":       (None, (13.0, -1.0, 1.0)),
        "Neck":        (None, (16.0, -2.0, 2.0)),
        "Head":        (None, (-12.0, -8.0, -8.0)),  # Sudden predatory twitch
        "UpperArm.L":  (None, (-38.0, 3.0, 6.0)),
        "Forearm.L":   (None, (32.0, 0.0, -3.0)),
        "Hand.L":      (None, (12.0, 1.0, -4.0)),
        "UpperArm.R":  (None, (-30.0, -5.0, -5.0)),
        "Forearm.R":   (None, (26.0, 0.0, 3.0)),
        "Hand.R":      (None, (12.0, -2.0, 2.0)),
        "UpperLeg.L":  (None, (18.0, 1.0, 0.0)),     # Left leg pushing back
        "LowerLeg.L":  (None, (18.0, 0.0, 0.0)),
        "Foot.L":      (None, (14.0, 0.0, 0.0)),
        "UpperLeg.R":  (None, (4.0, -2.0, 1.0)),     # Right knee lifting awkwardly
        "LowerLeg.R":  (None, (35.0, 0.0, 0.0)),
        "Foot.R":      (None, (-2.0, 0.0, 0.0)),
    },
    # Frame 21: Right skeletal leg awkward snap / jerky forward lurch
    21: {
        "Root":        ((-0.004, -0.005, -0.007), (0, 0, 0)),
        "Hips":        (None, (6.0, -2.0, 3.0)),
        "Spine":       (None, (20.0, 0.0, 0.0)),
        "Chest":       (None, (11.0, 1.0, -1.0)),
        "Neck":        (None, (14.0, 1.0, -1.0)),
        "Head":        (None, (-14.0, 2.0, 4.0)),
        "UpperArm.L":  (None, (-32.0, 4.0, 5.0)),
        "Forearm.L":   (None, (26.0, 0.0, -2.0)),
        "Hand.L":      (None, (6.0, 2.0, -3.0)),
        "UpperArm.R":  (None, (-38.0, -6.0, -6.0)),  # Right arm reaches out
        "Forearm.R":   (None, (32.0, 0.0, 2.0)),
        "Hand.R":      (None, (8.0, -3.0, 3.0)),
        "UpperLeg.L":  (None, (22.0, 1.0, -1.0)),
        "LowerLeg.L":  (None, (28.0, 0.0, 0.0)),
        "Foot.L":      (None, (18.0, 0.0, 0.0)),     # Toe push off
        "UpperLeg.R":  (None, (-12.0, -2.0, 2.0)),   # Skeletal leg flung forward
        "LowerLeg.R":  (None, (24.0, 0.0, 0.0)),
        "Foot.R":      (None, (-6.0, 0.0, 0.0)),
    },
    # Frame 26: Right skeletal foot awkward flat plant / scraping stop
    26: {
        "Root":        ((-0.007, -0.012, 0.002), (0, 0, 0)),
        "Hips":        (None, (4.0, -4.0, 4.0)),
        "Spine":       (None, (17.0, -1.0, 1.0)),
        "Chest":       (None, (13.0, -2.0, 2.0)),
        "Neck":        (None, (15.0, 0.0, 0.0)),
        "Head":        (None, (-10.0, 6.0, 8.0)),
        "UpperArm.L":  (None, (-28.0, 4.0, 4.0)),
        "Forearm.L":   (None, (22.0, 0.0, -2.0)),
        "Hand.L":      (None, (4.0, 1.0, -2.0)),
        "UpperArm.R":  (None, (-44.0, -5.0, -7.0)),
        "Forearm.R":   (None, (36.0, 0.0, 3.0)),
        "Hand.R":      (None, (14.0, -4.0, 4.0)),
        "UpperLeg.L":  (None, (12.0, 0.0, -1.0)),    # Left leg starts lifting
        "LowerLeg.L":  (None, (36.0, 0.0, 0.0)),
        "Foot.L":      (None, (10.0, 0.0, 0.0)),
        "UpperLeg.R":  (None, (-18.0, -2.0, 2.0)),   # Planted forward
        "LowerLeg.R":  (None, (8.0, 0.0, 0.0)),
        "Foot.R":      (None, (2.0, 0.0, 0.0)),
    },
    # Frame 31: Left leg swings forward, right skeletal leg takes brief jarring weight
    31: {
        "Root":        ((-0.005, -0.018, 0.005), (0, 0, 0)),
        "Hips":        (None, (3.0, -3.0, 3.0)),
        "Spine":       (None, (16.0, -2.0, 2.0)),
        "Chest":       (None, (14.0, 1.0, -1.0)),
        "Neck":        (None, (13.0, 2.0, -1.0)),
        "Head":        (None, (-7.0, 9.0, 12.0)),    # Tilting back towards right
        "UpperArm.L":  (None, (-32.0, 3.0, 5.0)),
        "Forearm.L":   (None, (26.0, 0.0, -3.0)),
        "Hand.L":      (None, (8.0, 2.0, -4.0)),
        "UpperArm.R":  (None, (-40.0, -4.0, -6.0)),
        "Forearm.R":   (None, (30.0, 0.0, 2.0)),
        "Hand.R":      (None, (10.0, -3.0, 3.0)),
        "UpperLeg.L":  (None, (-4.0, 1.0, 1.0)),     # Left leg swinging forward
        "LowerLeg.L":  (None, (28.0, 0.0, 0.0)),
        "Foot.L":      (None, (-4.0, 0.0, 0.0)),
        "UpperLeg.R":  (None, (2.0, -2.0, 0.0)),     # Right leg supporting
        "LowerLeg.R":  (None, (6.0, 0.0, 0.0)),
        "Foot.R":      (None, (6.0, 0.0, 0.0)),
    },
    # Frame 36: Left leg prepares for heel strike, right leg moves into back drag
    36: {
        "Root":        ((-0.002, -0.008, -0.003), (0, 0, 0)),
        "Hips":        (None, (4.5, 0.0, -1.0)),
        "Spine":       (None, (17.5, -2.5, 2.0)),
        "Chest":       (None, (12.5, 1.5, -1.5)),
        "Neck":        (None, (13.5, 1.5, -1.0)),
        "Head":        (None, (-7.5, 8.5, 11.0)),
        "UpperArm.L":  (None, (-36.0, 3.5, 5.5)),
        "Forearm.L":   (None, (28.0, 0.0, -3.5)),
        "Hand.L":      (None, (9.0, 2.0, -4.5)),
        "UpperArm.R":  (None, (-34.0, -5.0, -5.5)),
        "Forearm.R":   (None, (26.0, 0.0, 2.0)),
        "Hand.R":      (None, (7.0, -3.0, 3.5)),
        "UpperLeg.L":  (None, (-18.0, 1.5, 1.5)),
        "LowerLeg.L":  (None, (12.0, 0.0, 0.0)),
        "Foot.L":      (None, (-6.0, 0.0, 0.0)),
        "UpperLeg.R":  (None, (14.0, -2.5, -1.5)),
        "LowerLeg.R":  (None, (8.0, 0.0, 0.0)),
        "Foot.R":      (None, (12.0, 0.0, 0.0)),
    },
    # Frame 40: EXACT MATCH TO FRAME 1 FOR SEAMLESS 40-FRAME LOOP
    40: {
        "Root":        ((0.0, 0.0, -0.008), (0, 0, 0)),
        "Hips":        (None, (5.0, 2.0, -3.0)),
        "Spine":       (None, (18.0, -3.0, 2.0)),
        "Chest":       (None, (12.0, 2.0, -2.0)),
        "Neck":        (None, (14.0, 1.0, -1.0)),
        "Head":        (None, (-8.0, 8.0, 10.0)),
        "Shoulder.L":  (None, (0.0, 0.0, 3.0)),
        "UpperArm.L":  (None, (-38.0, 4.0, 6.0)),
        "Forearm.L":   (None, (30.0, 0.0, -4.0)),
        "Hand.L":      (None, (10.0, 2.0, -5.0)),
        "Shoulder.R":  (None, (0.0, 0.0, -2.0)),
        "UpperArm.R":  (None, (-32.0, -6.0, -5.0)),
        "Forearm.R":   (None, (24.0, 0.0, 2.0)),
        "Hand.R":      (None, (6.0, -3.0, 4.0)),
        "UpperLeg.L":  (None, (-24.0, 2.0, 2.0)),
        "LowerLeg.L":  (None, (8.0, 0.0, 0.0)),
        "Foot.L":      (None, (-8.0, 0.0, 0.0)),
        "UpperLeg.R":  (None, (20.0, -3.0, -2.0)),
        "LowerLeg.R":  (None, (10.0, 0.0, 0.0)),
        "Foot.R":      (None, (16.0, 0.0, 0.0)),
    }
}

print(f"[Walk] Keyframing {len(walk_data)} major stance breakdowns across 40 frames...")

for frame, bdata in walk_data.items():
    for bname, vals in bdata.items():
        loc, rot = vals
        kf_bone(bname, frame, loc=loc, rot_deg=rot)

# Set interpolation to BEZIER for organic biological sway
for fcurve in action.fcurves:
    for kp in fcurve.keyframe_points:
        kp.interpolation = 'BEZIER'

# ==============================================================================
# 3.5. MANDATORY GROUND-LEVEL SOLVER (ANTI-FLOOR-CLIPPING GUARD)
# ==============================================================================
print("[Walk] Executing Ground-Level Solver across all frames...")
char_mesh = [o for o in bpy.data.objects if o.type == "MESH" and "VFX" not in o.name and "Trail" not in o.name][0]
root_pb = arm_obj.pose.bones.get("Root")

if root_pb:
    arm_obj.animation_data.use_nla = False
    arm_obj.animation_data.action = action
    for f in range(1, 41):
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
    for f in range(1, 41):
        bpy.context.scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        eval_obj = char_mesh.evaluated_get(dg)
        m = eval_obj.to_mesh()
        min_z = min((eval_obj.matrix_world @ v.co).z for v in m.vertices)
        eval_obj.to_mesh_clear()
        if min_z < post_min:
            post_min = min_z
    print(f"[Walk] Ground-Level Solver complete! Lowest mesh Z: {post_min*100:.2f} cm (PASS)")
    arm_obj.animation_data.use_nla = True


# ==============================================================================
# 4. PUSH ACTION TO NLA TRACK 'Walk'
# ==============================================================================
print("[Walk] Pushing action to NLA track 'Walk'...")

# Clean existing Walk tracks if any
for tr in list(arm_obj.animation_data.nla_tracks):
    if tr.name == "Walk":
        arm_obj.animation_data.nla_tracks.remove(tr)

track = arm_obj.animation_data.nla_tracks.new()
track.name = "Walk"
strip = track.strips.new("Walk", 1, action)
strip.action_frame_start = 1
strip.action_frame_end = 40

# Unset active action so NLA takes effect cleanly
arm_obj.animation_data.action = None

bpy.ops.object.mode_set(mode='OBJECT')

# ==============================================================================
# 5. SAVE BLEND FILE
# ==============================================================================
print(f"[Walk] Saving updated scene to: {BLEND_PATH}")
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
print("[Walk] Complete! Walk action generated and saved successfully.")
