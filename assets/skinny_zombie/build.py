"""
Master Pipeline Orchestrator: Skinny Zombie (assets/skinny_zombie/build.py)

Runs the complete 3-stage modular pipeline:
1. model.py       -> Procedural micro-voxel modeling, materials, armature, sockets
2. anim_walk.py   -> 40-frame shambling asymmetrical undead walk loop
3. anim_attack.py -> 50-frame 5-phase cross-rend claw attack, SLERP guard, filmstrip, beauty render, glTF export, Base64 data URI

Can be executed either inside Blender:
  blender --background --python build.py
or via Python directly:
  python build.py
"""

import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PY = os.path.join(SCRIPT_DIR, "model.py")
ANIM_WALK_PY = os.path.join(SCRIPT_DIR, "anim_walk.py")
ANIM_ATTACK_PY = os.path.join(SCRIPT_DIR, "anim_attack.py")

BLENDER_EXE = os.environ.get("BLENDER_EXE", r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe")
if not os.path.exists(BLENDER_EXE):
    BLENDER_EXE = "blender"

def run_step_subprocess(script_path, step_name):
    print(f"\n==================================================")
    print(f"  RUNNING STAGE: {step_name}")
    print(f"  Script: {script_path}")
    print(f"==================================================")
    cmd = [BLENDER_EXE, "--background", "--python", script_path]
    res = subprocess.run(cmd, cwd=SCRIPT_DIR)
    if res.returncode != 0:
        raise RuntimeError(f"Stage '{step_name}' failed with exit code {res.returncode}")

def run_step_in_blender(script_path, step_name):
    print(f"\n==================================================")
    print(f"  RUNNING STAGE (IN-PROCESS): {step_name}")
    print(f"  Script: {script_path}")
    print(f"==================================================")
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()
    globs = {"__file__": script_path, "__name__": "__main__"}
    exec(compile(code, script_path, "exec"), globs)

def cleanup_backups():
    print("\n[Cleanup] Removing .blend1 backup files and temporary scratch items...")
    for fname in os.listdir(SCRIPT_DIR):
        if fname.endswith(".blend1") or fname.startswith("temp_frame_"):
            p = os.path.join(SCRIPT_DIR, fname)
            try:
                os.remove(p)
                print(f"  Removed: {fname}")
            except Exception as e:
                print(f"  Failed to remove {fname}: {e}")

def main():
    in_blender = "bpy" in sys.modules
    
    stages = [
        ("Voxel Modeling & Rigging", MODEL_PY),
        ("Shambling Walk Cycle", ANIM_WALK_PY),
        ("5-Phase Combat Attack & glTF Export", ANIM_ATTACK_PY)
    ]
    
    for step_name, script_path in stages:
        if in_blender:
            run_step_in_blender(script_path, step_name)
        else:
            run_step_subprocess(script_path, step_name)
            
    cleanup_backups()
    print("\n[SUCCESS] Entire Skinny Zombie asset production finished cleanly!")

if __name__ == "__main__":
    main()
