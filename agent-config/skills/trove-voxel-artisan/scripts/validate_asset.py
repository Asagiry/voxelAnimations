"""Run inside Blender: validate a new voxel asset without inspecting other assets."""

import argparse
import json
import os
import struct
import sys

import bpy


CANONICAL_FILES = (
    "model.py",
    "anim_walk.py",
    "anim_attack.py",
    "build.py",
)
CHARACTER_SOCKETS = {
    "Socket_Hand_R",
    "Socket_Hand_L",
    "Socket_Head",
    "Socket_Back",
}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("asset_dir")
    parser.add_argument("--stage", choices=("model", "final"), required=True)
    parser.add_argument("--kind", choices=("character", "weapon", "prop"), required=True)
    return parser.parse_args(argv)


def glb_animation_names(glb_path):
    with open(glb_path, "rb") as glb_file:
        header = glb_file.read(12)
        magic, version, _length = struct.unpack("<4sII", header)
        if magic != b"glTF" or version != 2:
            raise ValueError("not a glTF 2.0 binary")
        chunk_length, chunk_type = struct.unpack("<I4s", glb_file.read(8))
        if chunk_type != b"JSON":
            raise ValueError("GLB has no JSON chunk")
        document = json.loads(glb_file.read(chunk_length).decode("utf-8"))
    return [animation.get("name", "") for animation in document.get("animations", [])]


def mesh_min_z(depsgraph):
    values = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        evaluated = obj.evaluated_get(depsgraph)
        values.extend((evaluated.matrix_world @ vertex.co).z for vertex in evaluated.data.vertices)
    return min(values) if values else None


def action_ground_report(armature):
    report = {}
    animation_data = armature.animation_data_create()
    original_action = animation_data.action
    try:
        for action_name in ("Walk", "Attack"):
            action = bpy.data.actions.get(action_name)
            if not action:
                continue
            animation_data.action = action
            start, end = (round(value) for value in action.frame_range)
            lowest = None
            for frame in range(start, end + 1):
                bpy.context.scene.frame_set(frame)
                minimum = mesh_min_z(bpy.context.evaluated_depsgraph_get())
                lowest = minimum if lowest is None else min(lowest, minimum)
            report[action_name] = lowest
    finally:
        animation_data.action = original_action
    return report


def main():
    args = parse_args()
    asset_dir = os.path.abspath(args.asset_dir)
    asset_name = os.path.basename(asset_dir)
    errors, warnings = [], []
    result = {"asset": asset_name, "stage": args.stage, "kind": args.kind}

    blend_path = os.path.join(asset_dir, f"{asset_name}.blend")
    if not os.path.isfile(blend_path):
        errors.append(f"missing {asset_name}.blend")

    armatures = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    result["armatures"] = [obj.name for obj in armatures]
    if not armatures:
        errors.append("scene has no armature")
    elif args.kind == "character":
        socket_names = {bone.name for bone in armatures[0].pose.bones}
        missing_sockets = sorted(CHARACTER_SOCKETS - socket_names)
        result["missing_sockets"] = missing_sockets
        if missing_sockets:
            errors.append("missing sockets: " + ", ".join(missing_sockets))

    if args.stage == "final":
        required = list(CANONICAL_FILES) + [
            f"{asset_name}.blend",
            f"{asset_name}.glb",
            f"{asset_name}_render.png",
            f"{asset_name}_data.js",
        ]
        missing_files = [name for name in required if not os.path.isfile(os.path.join(asset_dir, name))]
        result["missing_files"] = missing_files
        if missing_files:
            errors.append("missing canonical files: " + ", ".join(missing_files))

        action_names = {action.name for action in bpy.data.actions}
        result["actions"] = sorted(action_names)
        for expected in ("Walk", "Attack"):
            if expected not in action_names:
                errors.append(f"missing Blender action: {expected}")

        if armatures:
            ground = action_ground_report(armatures[0])
            result["minimum_ground_z"] = ground
            for action_name, minimum in ground.items():
                if minimum is None:
                    warnings.append(f"no renderable mesh at {action_name}")
                elif minimum < -0.002:
                    errors.append(f"{action_name} penetrates floor: min_z={minimum:.6f}")

        glb_path = os.path.join(asset_dir, f"{asset_name}.glb")
        if os.path.isfile(glb_path):
            try:
                animation_names = glb_animation_names(glb_path)
                result["glb_animations"] = animation_names
                for expected in ("Walk", "Attack"):
                    if expected not in animation_names:
                        errors.append(f"missing GLB animation: {expected}")
            except (OSError, ValueError, json.JSONDecodeError, struct.error) as error:
                errors.append(f"invalid GLB: {error}")

    result["errors"] = errors
    result["warnings"] = warnings
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
