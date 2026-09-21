import os
import sys
import subprocess
import shutil

def find_blender():
    # 1. Environment PATH
    blender_path = shutil.which("blender")
    if blender_path:
        return blender_path
    
    # 2. Standard Windows installation paths
    candidate_paths = [
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"
    ]
    for p in candidate_paths:
        if os.path.isfile(p):
            return p
            
    raise FileNotFoundError("Blender executable not found in PATH or standard installation directories.")

def run_stage(blender_bin, script_path):
    print(f"\n=======================================================")
    print(f"RUNNING: {os.path.basename(script_path)}")
    print(f"=======================================================")
    cmd = [blender_bin, "--background", "--python", script_path]
    res = subprocess.run(cmd, capture_output=False)
    if res.returncode != 0:
        print(f"ERROR: Stage {script_path} failed with return code {res.returncode}", file=sys.stderr)
        sys.exit(res.returncode)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    blender_bin = find_blender()
    print(f"Using Blender binary: {blender_bin}")
    print(f"Target Asset Directory: {base_dir}")

    stages = [
        os.path.join(base_dir, "model.py"),
        os.path.join(base_dir, "anim_walk.py"),
        os.path.join(base_dir, "anim_attack.py")
    ]

    for stage_script in stages:
        if not os.path.isfile(stage_script):
            print(f"ERROR: Missing script {stage_script}", file=sys.stderr)
            sys.exit(1)
        run_stage(blender_bin, stage_script)

    print("\n=======================================================")
    print("ALL BUILD STAGES COMPLETED SUCCESSFULLY!")
    print(f"Asset package ready at: {base_dir}")
    print("=======================================================")

if __name__ == "__main__":
    main()
