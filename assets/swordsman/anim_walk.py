import bpy
import math
import os
from mathutils import Vector, Euler

def setup_walk_animation():
    arm_obj = bpy.data.objects.get("Armature")
    mesh_obj = bpy.data.objects.get("Swordsman_Mesh")
    if not arm_obj or not mesh_obj:
        raise RuntimeError("Armature or Swordsman_Mesh not found in scene!")

    # Switch to pose mode
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')

    # Ensure animation data
    if not arm_obj.animation_data:
        arm_obj.animation_data_create()
    else:
        # Clear existing action and NLA tracks to start completely fresh
        arm_obj.animation_data.action = None
        for track in list(arm_obj.animation_data.nla_tracks):
            arm_obj.animation_data.nla_tracks.remove(track)

    action = bpy.data.actions.new(name="Walk")
    arm_obj.animation_data.action = action

    # Configure pose bone rotation modes to 'XYZ'
    pbones = arm_obj.pose.bones
    for pb in pbones:
        pb.rotation_mode = 'XYZ'
        pb.location = Vector((0, 0, 0))
        pb.rotation_euler = Euler((0, 0, 0), 'XYZ')

    # Keyframe poses definitions across 36-frame walk cycle (F1 to F37 for seamless loop)
    def deg(val):
        return math.radians(val)

    # Keyframe dictionary: frame -> {bone_name: (rot_x, rot_y, rot_z)}
    # Remember coordinate systems:
    # Root: local Y = World +Z.
    # Hips, Spine, Chest, Head: local X < 0 = lean forward, local Y = yaw, local Z = roll
    # Arms: local X > 0 = swing forward, local Y = shaft spin, local Z > 0 = swing outward
    # Legs: UpperLeg X > 0 = forward swing, LowerLeg X < 0 = knee flexion backwards, Foot X = tilt
    keyframes_data = {
        1: { # Left Contact / Right Push-off
            'Hips': (deg(-2), deg(4), deg(0)),
            'Chest': (deg(-3), deg(-6), deg(0)),
            'Head': (deg(1), deg(2), deg(0)),
            # Left Leg (Forward Heel Contact)
            'UpperLeg.L': (deg(24), deg(0), deg(2)),
            'LowerLeg.L': (deg(-4), deg(0), deg(0)),
            'Foot.L': (deg(12), deg(0), deg(0)),
            # Right Leg (Trailing Push-off)
            'UpperLeg.R': (deg(-20), deg(0), deg(-2)),
            'LowerLeg.R': (deg(-34), deg(0), deg(0)),
            'Foot.R': (deg(-10), deg(0), deg(0)),
            # Arms (Right Arm forward with sword grip, Left Arm back)
            'UpperArm.R': (deg(20), deg(-10), deg(10)),
            'Forearm.R': (deg(42), deg(0), deg(0)),
            'Hand.R': (deg(-12), deg(-5), deg(10)),
            'UpperArm.L': (deg(-16), deg(0), deg(-8)),
            'Forearm.L': (deg(22), deg(0), deg(0)),
            'Hand.L': (deg(6), deg(0), deg(0)),
            'Shoulder.R': (deg(0), deg(2), deg(0)),
            'Shoulder.L': (deg(0), deg(-2), deg(0)),
        },
        5: { # Left Down / Weight Cushion
            'Hips': (deg(-2), deg(2), deg(2)),
            'Chest': (deg(-3), deg(-3), deg(-1)),
            'Head': (deg(1), deg(1), deg(0)),
            # Left Leg absorbs weight
            'UpperLeg.L': (deg(14), deg(0), deg(2)),
            'LowerLeg.L': (deg(-18), deg(0), deg(0)),
            'Foot.L': (deg(0), deg(0), deg(0)),
            # Right Leg toe push
            'UpperLeg.R': (deg(-12), deg(0), deg(-2)),
            'LowerLeg.R': (deg(-42), deg(0), deg(0)),
            'Foot.R': (deg(-16), deg(0), deg(0)),
            # Arms passing
            'UpperArm.R': (deg(12), deg(-10), deg(10)),
            'Forearm.R': (deg(38), deg(0), deg(0)),
            'Hand.R': (deg(-12), deg(-5), deg(10)),
            'UpperArm.L': (deg(-8), deg(0), deg(-8)),
            'Forearm.L': (deg(25), deg(0), deg(0)),
            'Hand.L': (deg(3), deg(0), deg(0)),
            'Shoulder.R': (deg(0), deg(1), deg(0)),
            'Shoulder.L': (deg(0), deg(-1), deg(0)),
        },
        10: { # Left Passing / Mid-Stance (Right leg swings forward)
            'Hips': (deg(-1), deg(0), deg(1)),
            'Chest': (deg(-3), deg(0), deg(-1)),
            'Head': (deg(1), deg(0), deg(0)),
            # Left Leg straight carrying body
            'UpperLeg.L': (deg(-2), deg(0), deg(2)),
            'LowerLeg.L': (deg(-3), deg(0), deg(0)),
            'Foot.L': (deg(0), deg(0), deg(0)),
            # Right Leg knee lifts forward
            'UpperLeg.R': (deg(12), deg(0), deg(-2)),
            'LowerLeg.R': (deg(-48), deg(0), deg(0)),
            'Foot.R': (deg(10), deg(0), deg(0)),
            # Arms at neutral mid-swing
            'UpperArm.R': (deg(0), deg(-8), deg(8)),
            'Forearm.R': (deg(35), deg(0), deg(0)),
            'Hand.R': (deg(-12), deg(-5), deg(10)),
            'UpperArm.L': (deg(4), deg(0), deg(-6)),
            'Forearm.L': (deg(30), deg(0), deg(0)),
            'Hand.L': (deg(0), deg(0), deg(0)),
            'Shoulder.R': (deg(0), deg(0), deg(0)),
            'Shoulder.L': (deg(0), deg(0), deg(0)),
        },
        14: { # Left Push-Off / Peak Height (Right leg extending forward)
            'Hips': (deg(-2), deg(-2), deg(0)),
            'Chest': (deg(-3), deg(3), deg(0)),
            'Head': (deg(1), deg(-1), deg(0)),
            # Left Leg extending back on toe
            'UpperLeg.L': (deg(-16), deg(0), deg(2)),
            'LowerLeg.L': (deg(-5), deg(0), deg(0)),
            'Foot.L': (deg(-14), deg(0), deg(0)),
            # Right Leg reaching forward
            'UpperLeg.R': (deg(20), deg(0), deg(-2)),
            'LowerLeg.R': (deg(-16), deg(0), deg(0)),
            'Foot.R': (deg(12), deg(0), deg(0)),
            # Arms moving to opposite stride
            'UpperArm.R': (deg(-8), deg(-5), deg(7)),
            'Forearm.R': (deg(32), deg(0), deg(0)),
            'Hand.R': (deg(-12), deg(-5), deg(10)),
            'UpperArm.L': (deg(16), deg(0), deg(-6)),
            'Forearm.L': (deg(36), deg(0), deg(0)),
            'Hand.L': (deg(-4), deg(0), deg(0)),
            'Shoulder.R': (deg(0), deg(-1), deg(0)),
            'Shoulder.L': (deg(0), deg(1), deg(0)),
        },
        19: { # Right Contact / Left Push-Off (Mirror of F1)
            'Hips': (deg(-2), deg(-4), deg(0)),
            'Chest': (deg(-3), deg(6), deg(0)),
            'Head': (deg(1), deg(-2), deg(0)),
            # Right Leg (Forward Heel Contact)
            'UpperLeg.R': (deg(24), deg(0), deg(-2)),
            'LowerLeg.R': (deg(-4), deg(0), deg(0)),
            'Foot.R': (deg(12), deg(0), deg(0)),
            # Left Leg (Trailing Push-off)
            'UpperLeg.L': (deg(-20), deg(0), deg(2)),
            'LowerLeg.L': (deg(-34), deg(0), deg(0)),
            'Foot.L': (deg(-10), deg(0), deg(0)),
            # Arms (Left Arm forward, Right Arm back)
            'UpperArm.R': (deg(-14), deg(-5), deg(6)),
            'Forearm.R': (deg(30), deg(0), deg(0)),
            'Hand.R': (deg(-12), deg(-5), deg(10)),
            'UpperArm.L': (deg(22), deg(0), deg(-8)),
            'Forearm.L': (deg(38), deg(0), deg(0)),
            'Hand.L': (deg(-6), deg(0), deg(0)),
            'Shoulder.R': (deg(0), deg(-2), deg(0)),
            'Shoulder.L': (deg(0), deg(2), deg(0)),
        },
        23: { # Right Down / Weight Cushion (Mirror of F5)
            'Hips': (deg(-2), deg(-2), deg(-2)),
            'Chest': (deg(-3), deg(3), deg(1)),
            'Head': (deg(1), deg(-1), deg(0)),
            # Right Leg absorbs weight
            'UpperLeg.R': (deg(14), deg(0), deg(-2)),
            'LowerLeg.R': (deg(-18), deg(0), deg(0)),
            'Foot.R': (deg(0), deg(0), deg(0)),
            # Left Leg toe push
            'UpperLeg.L': (deg(-12), deg(0), deg(2)),
            'LowerLeg.L': (deg(-42), deg(0), deg(0)),
            'Foot.L': (deg(-16), deg(0), deg(0)),
            # Arms passing
            'UpperArm.R': (deg(-6), deg(-6), deg(7)),
            'Forearm.R': (deg(33), deg(0), deg(0)),
            'Hand.R': (deg(-12), deg(-5), deg(10)),
            'UpperArm.L': (deg(12), deg(0), deg(-7)),
            'Forearm.L': (deg(32), deg(0), deg(0)),
            'Hand.L': (deg(-3), deg(0), deg(0)),
            'Shoulder.R': (deg(0), deg(-1), deg(0)),
            'Shoulder.L': (deg(0), deg(1), deg(0)),
        },
        28: { # Right Passing / Mid-Stance (Mirror of F10)
            'Hips': (deg(-1), deg(0), deg(-1)),
            'Chest': (deg(-3), deg(0), deg(1)),
            'Head': (deg(1), deg(0), deg(0)),
            # Right Leg straight carrying body
            'UpperLeg.R': (deg(-2), deg(0), deg(-2)),
            'LowerLeg.R': (deg(-3), deg(0), deg(0)),
            'Foot.R': (deg(0), deg(0), deg(0)),
            # Left Leg knee lifts forward
            'UpperLeg.L': (deg(12), deg(0), deg(2)),
            'LowerLeg.L': (deg(-48), deg(0), deg(0)),
            'Foot.L': (deg(10), deg(0), deg(0)),
            # Arms neutral
            'UpperArm.R': (deg(4), deg(-8), deg(8)),
            'Forearm.R': (deg(36), deg(0), deg(0)),
            'Hand.R': (deg(-12), deg(-5), deg(10)),
            'UpperArm.L': (deg(0), deg(0), deg(-6)),
            'Forearm.L': (deg(28), deg(0), deg(0)),
            'Hand.L': (deg(0), deg(0), deg(0)),
            'Shoulder.R': (deg(0), deg(0), deg(0)),
            'Shoulder.L': (deg(0), deg(0), deg(0)),
        },
        32: { # Right Push-Off / Peak Height (Mirror of F14)
            'Hips': (deg(-2), deg(2), deg(0)),
            'Chest': (deg(-3), deg(-3), deg(0)),
            'Head': (deg(1), deg(1), deg(0)),
            # Right Leg extending back on toe
            'UpperLeg.R': (deg(-16), deg(0), deg(-2)),
            'LowerLeg.R': (deg(-5), deg(0), deg(0)),
            'Foot.R': (deg(-14), deg(0), deg(0)),
            # Left Leg reaching forward
            'UpperLeg.L': (deg(20), deg(0), deg(2)),
            'LowerLeg.L': (deg(-16), deg(0), deg(0)),
            'Foot.L': (deg(12), deg(0), deg(0)),
            # Arms
            'UpperArm.R': (deg(14), deg(-10), deg(9)),
            'Forearm.R': (deg(40), deg(0), deg(0)),
            'Hand.R': (deg(-12), deg(-5), deg(10)),
            'UpperArm.L': (deg(-10), deg(0), deg(-7)),
            'Forearm.L': (deg(24), deg(0), deg(0)),
            'Hand.L': (deg(3), deg(0), deg(0)),
            'Shoulder.R': (deg(0), deg(1), deg(0)),
            'Shoulder.L': (deg(0), deg(-1), deg(0)),
        },
        37: { # Loop back to F1 exactly
            'Hips': (deg(-2), deg(4), deg(0)),
            'Chest': (deg(-3), deg(-6), deg(0)),
            'Head': (deg(1), deg(2), deg(0)),
            'UpperLeg.L': (deg(24), deg(0), deg(2)),
            'LowerLeg.L': (deg(-4), deg(0), deg(0)),
            'Foot.L': (deg(12), deg(0), deg(0)),
            'UpperLeg.R': (deg(-20), deg(0), deg(-2)),
            'LowerLeg.R': (deg(-34), deg(0), deg(0)),
            'Foot.R': (deg(-10), deg(0), deg(0)),
            'UpperArm.R': (deg(20), deg(-10), deg(10)),
            'Forearm.R': (deg(42), deg(0), deg(0)),
            'Hand.R': (deg(-12), deg(-5), deg(10)),
            'UpperArm.L': (deg(-16), deg(0), deg(-8)),
            'Forearm.L': (deg(22), deg(0), deg(0)),
            'Hand.L': (deg(6), deg(0), deg(0)),
            'Shoulder.R': (deg(0), deg(2), deg(0)),
            'Shoulder.L': (deg(0), deg(-2), deg(0)),
        }
    }

    # Insert rotation keyframes
    for f, bones_dict in keyframes_data.items():
        for b_name, rot_tuple in bones_dict.items():
            if b_name in pbones:
                pb = pbones[b_name]
                pb.rotation_euler = Euler(rot_tuple, 'XYZ')
                pb.keyframe_insert(data_path="rotation_euler", frame=f)

    # Initial interpolation smoothing
    for fc in action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.easing = 'AUTO'

    # ---------------------------------------------------------------
    # MANDATORY AUTOMATED GROUND-LEVEL SOLVER (Floor Z >= 0.0)
    # ---------------------------------------------------------------
    pb_root = pbones['Root']
    pb_root.location = Vector((0, 0, 0))

    # Initialize Root location keyframes
    for f in range(1, 38):
        pb_root.keyframe_insert(data_path="location", frame=f)

    scene = bpy.context.scene
    print("--- Executing Walk Ground-Level Solver Pass ---")
    min_z_samples = []

    for f in range(1, 38):
        scene.frame_set(f)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_mesh = mesh_obj.evaluated_get(depsgraph)
        mat = eval_mesh.matrix_world
        curr_min_z = min((mat @ v.co).z for v in eval_mesh.data.vertices)

        # Ground plane correction:
        # In Blender armatures, Root's local +Y axis corresponds directly to World +Z!
        # If curr_min_z != 0.0, offset Root.location.y by (0.0 - curr_min_z)
        correction = 0.0 - curr_min_z
        pb_root.location.y += correction
        pb_root.keyframe_insert(data_path="location", frame=f)

    # Post-solver validation
    print("--- Verifying Walk Ground Contact Across All Frames ---")
    min_z_after = []
    for f in range(1, 38):
        scene.frame_set(f)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_mesh = mesh_obj.evaluated_get(depsgraph)
        mat = eval_mesh.matrix_world
        mz = min((mat @ v.co).z for v in eval_mesh.data.vertices)
        min_z_after.append(mz)

    worst_z = min(min_z_after)
    max_z = max(min_z_after)
    print(f"Ground Solver Result: min_z={worst_z:.6f}m, max_contact_z={max_z:.6f}m")
    if worst_z < -0.002:
        raise RuntimeError(f"Ground Plane Invariant violated! min_z = {worst_z:.6f} < -0.002m")

    # Finalize Walk Action and NLA Track
    action.use_frame_range = True
    action.frame_start = 1
    action.frame_end = 36

    # Push to NLA Track 'Walk'
    arm_obj.animation_data.action = None
    walk_track = arm_obj.animation_data.nla_tracks.new()
    walk_track.name = "Walk"
    strip = walk_track.strips.new("Walk", 1, action)
    strip.action_frame_start = 1
    strip.action_frame_end = 37
    strip.blend_type = 'REPLACE'

    bpy.ops.object.mode_set(mode='OBJECT')
    print("Successfully built Walk action and pushed to NLA track 'Walk'.")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    blend_path = os.path.join(base_dir, "swordsman.blend")
    print(f"Loading {blend_path} for Walk animation authoring...")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    setup_walk_animation()

    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Successfully saved Walk animation to {blend_path}")

if __name__ == "__main__":
    main()
