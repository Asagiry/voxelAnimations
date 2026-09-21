"""
Skinny Zombie Build Entry Point (assets/skinny_zombie/build_skinny_zombie.py)
Delegates directly to build.py for unified execution.
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_PY = os.path.join(SCRIPT_DIR, "build.py")

if __name__ == "__main__":
    with open(BUILD_PY, "r", encoding="utf-8") as f:
        code = f.read()
    globs = {"__file__": BUILD_PY, "__name__": "__main__"}
    exec(compile(code, BUILD_PY, "exec"), globs)
