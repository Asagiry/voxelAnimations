# Blender 4.2+ & Gamedev Technical Reference

Technical specification and runtime contracts for authoring, rigging, animating, rendering, and exporting voxel assets in Blender 4.2+.

---

## 1. Blender Runtime Environment & Headless Execution

### The External Python Trap
> [!CAUTION]
> Never attempt to run `python build_asset.py` directly from the OS shell. `bpy` is Blender's internal embedded C/Python API and does not exist in standard system Python. Running `python build_asset.py` will immediately throw `ModuleNotFoundError: No module named 'bpy'`.

### CLI Execution Command
Always execute scripts inside Blender's embedded runtime using headless background mode:
```powershell
& 'C:\Program Files\Blender Foundation\Blender 4.2\blender.exe' --background --python build_asset.py
```

### Dynamic Executable Resolution (Windows Fallback)
If `blender` is not registered in the system environment `PATH`, resolve the binary location using this deterministic hierarchy:
1. `C:\Program Files\Blender Foundation\Blender 4.2\blender.exe`
2. `C:\Program Files\Blender Foundation\Blender 4.1\blender.exe`
3. `C:\Program Files\Blender Foundation\Blender 4.0\blender.exe`
4. Search via PowerShell: `(Get-Command blender.exe -ErrorAction SilentlyContinue).Source`

---

## 2. Blender 4.2+ glTF 2.0 Export Contract

### Deprecation Guard: `export_rest_pose_armature`
> [!WARNING]
> In Blender 4.2+, passing `export_rest_pose_armature` to `bpy.ops.export_scene.gltf()` raises a fatal `TypeError: Calling operator "bpy.ops.export_scene.gltf" error, keyword "export_rest_pose_armature" unrecognized`.
> Never include this flag when writing Blender 4.x export routines.

### Authoritative glTF Export Call
Use this exact parameter contract for game-ready animated `.glb` exports:
```python
bpy.ops.export_scene.gltf(
    filepath=glb_filepath,
    export_format='GLB',
    export_animations=True,
    export_skins=True,
    export_all_influences=False,
    export_apply=False,
    export_yup=True
)
```

### Zero-CORS Browser Embed Generation
Directly following glTF export, read the raw binary file, encode it as Base64, and generate `<asset_name>_data.js` so web viewers can load the 3D model without encountering CORS or local file scheme restrictions:
```python
import base64

with open(glb_filepath, "rb") as f:
    b64_content = base64.b64encode(f.read()).decode("utf-8")

data_js_path = glb_filepath.replace(".glb", "_data.js")
var_name = f"window.{asset_name.upper()}_BASE64"
with open(data_js_path, "w", encoding="utf-8") as f:
    f.write(f'{var_name} = "data:model/gltf-binary;base64,{b64_content}";\n')
```

---

## 3. Principled BSDF & Material API in Blender 4.x

Blender 4.0 redesigned the Principled BSDF shader node socket naming. Scripts using legacy Blender 3.x socket names will fail with `KeyError`.

### Socket Name Migration Table:
| Property | Blender 3.x Socket | Blender 4.x Socket | Safe API Lookup |
|---|---|---|---|
| **Base Color** | `"Base Color"` | `"Base Color"` | `node.inputs["Base Color"]` |
| **Roughness** | `"Roughness"` | `"Roughness"` | `node.inputs["Roughness"]` |
| **Metallic** | `"Metallic"` | `"Metallic"` | `node.inputs["Metallic"]` |
| **Specular** | `"Specular"` | `"Specular IOR Level"` | `node.inputs.get("Specular IOR Level") or node.inputs.get("Specular")` |
| **Emission Color** | `"Emission"` | `"Emission Color"` | `node.inputs.get("Emission Color") or node.inputs.get("Emission")` |
| **Emission Strength** | `"Emission Strength"` | `"Emission Strength"` | `node.inputs["Emission Strength"]` |

### AgX Tonemapping Color Safeguards
Blender 4.x uses **AgX Color Management** by default.
- Emissive colored magic/lasers (purple, cyan, crimson): Keep `Emission Strength` between **1.0 and 2.5**. Higher values cause AgX to desaturate rich colors into washed-out white cores.
- Overdriven pure-white spark cores: Restrict to tiny single-voxel focal points (`Emission Strength = 4.0 – 5.0`, base color pure white `(1, 1, 1, 1)`).

---

## 4. Armature Kinematics & Bone Coordinate Conventions

### The Local +Y Bone Axis Rule
> [!IMPORTANT]
> In Blender armatures, **a bone's local +Y axis ALWAYS points longitudinally along the bone shaft (from head to tail)**.
> - To spin, roll, or drill a weapon along its main shaft: **Rotate strictly on local Y (`rotation_euler.y`)**.
> - **NEVER rotate on local Z or X to achieve an axial spin**. Rotating on Z or X tilts or inverts the weapon 180° upside-down.

### Explicit Euler Rotation Mode
Blender pose bones default to Quaternion rotation (`'QUATERNION'`). Assigning values to `pbone.rotation_euler` without declaring the rotation mode will result in erratic motion or ignored keyframes.
Always declare:
```python
pbone.rotation_mode = 'XYZ'  # Must be set BEFORE keyframing rotation_euler!
pbone.rotation_euler = (rot_x, rot_y, rot_z)
pbone.keyframe_insert(data_path="rotation_euler", frame=current_frame)
```

### F-Curve Interpolation Tuning
Default Blender keyframe interpolation can create sluggish floating motion. To give combat strikes snappy mechanical weight:
```python
if armature.animation_data and armature.animation_data.action:
    for fcurve in armature.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'BEZIER'
            kf.easing = 'EASE_OUT'
```

---

## 5. The Gamedev 5-Phase Hitbox State Machine

Every action game combat animation must follow the authoritative 5-phase combat loop:

```
[Phase 1: Startup / Telegraph] (15–25% of timeline)
    ├── Weapon pulls back into an elevated anticipation posture.
    ├── Kinetic energy gathers; glowing cores hum and particles draw inward.
    └── Clear visual cue signaling incoming attack direction.

[Phase 2: Active Hit Window] (5–10% of timeline)
    ├── Explosive acceleration across the strike plane.
    ├── Maximum linear and angular velocity; cutting edge/impact surface leads the trajectory.
    ├── Combat hitbox active!
    └── Geometric slash ribbon/trail spawns directly behind the cutting edge.

[Phase 3: Overshoot & Follow-Through] (10–15% of timeline)
    ├── Weapon inertia carries past the target zone.
    └── Trail ribbon reaches maximum expansion.

[Phase 4: Zanshin / Hit-Stop / Recoil Hold] (20–30% of timeline)
    ├── Instantaneous deceleration snap or micro-recoil tremor.
    ├── Conveys heavy structural mass and solid physical impact.
    └── Weapon holds execution posture while slash ribbon dissolves.

[Phase 5: Recovery / Sheath / Noto] (25–35% of timeline)
    ├── Smooth, deliberate reset arc returning the weapon back to center.
    └── Secondary orbitals and floating particles settle into ready idle.
```

---

## 6. Depsgraph Evaluated Camera Auto-Framing (The Anti-Crop Rule)

### The Pitch-Black Void Trap
> [!CAUTION]
> **NEVER parent the camera or `cam_target` to an animated bone or armature.**
> Parenting the camera to an animated bone causes the camera to swing into infinity mid-swing, rendering an entirely empty black frame. Cameras and camera tracking targets must always remain independent static world objects.

### Dynamic Evaluated Depsgraph Framing Algorithm
Do not calculate camera bounds from rest-pose vertices or from a single mesh. Evaluate the scene depsgraph at the **key action frame** across ALL scene objects (including animated attack ribbons, floating runes, and expanding vortex discs):

```python
import bpy, math
from mathutils import Vector

def setup_hero_camera(action_frame, resolution=(1024, 1024), margin=1.35):
    scene = bpy.context.scene
    scene.frame_set(action_frame)
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]

    depsgraph = bpy.context.evaluated_depsgraph_get()

    all_corners = []
    for obj in scene.objects:
        if obj.type == 'MESH' and not obj.hide_render:
            eval_obj = obj.evaluated_get(depsgraph)
            mat = eval_obj.matrix_world
            all_corners.extend([mat @ Vector(corner) for corner in eval_obj.bound_box])

    if not all_corners:
        return

    # Calculate center and span in world space
    min_co = Vector((min(c.x for c in all_corners), min(c.y for c in all_corners), min(c.z for c in all_corners)))
    max_co = Vector((max(c.x for c in all_corners), max(c.y for c in all_corners), max(c.z for c in all_corners)))
    center = (min_co + max_co) * 0.5
    span = (max_co - min_co).length

    # Ensure Camera Target Object
    cam_target = bpy.data.objects.get("CamTarget") or bpy.data.objects.new("CamTarget", None)
    if cam_target.name not in scene.collection.objects:
        scene.collection.objects.link(cam_target)
    cam_target.location = center

    # Ensure Camera Object
    cam_obj = bpy.data.objects.get("HeroCamera")
    if not cam_obj:
        cam_data = bpy.data.cameras.new("HeroCamera")
        cam_obj = bpy.data.objects.new("HeroCamera", cam_data)
        scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # 45-degree elevated diagonal isometric perspective
    fov_rad = cam_obj.data.angle
    dist = (span * 0.5) / math.tan(fov_rad * 0.5) * margin
    cam_obj.location = center + Vector((dist * 0.65, -dist * 0.65, dist * 0.70))

    # Track to constraint
    if not any(c.type == 'TRACK_TO' for c in cam_obj.constraints):
        tt = cam_obj.constraints.new('TRACK_TO')
        tt.target = cam_target
        tt.track_axis = 'TRACK_NEGATIVE_Z'
        tt.up_axis = 'UP_Y'
```

---

## 7. High-Performance Voxel Mesh Generation

Creating separate Blender objects for individual voxel cubes causes severe viewport lag, freezes the depsgraph evaluator, and bloats `.glb` export files.

### The Exposed-Face Boundary Rule
When building voxel structures procedurally:
1. Maintain a 3D grid coordinate set of active voxels `(x, y, z)`.
2. For each voxel, test the 6 orthogonal neighbor directions: `(x±1, y, z)`, `(x, y±1, z)`, `(x, y, z±1)`.
3. Only generate quad polygons for faces that border empty space. Internal hidden faces must never be instantiated.

### Planar Quad Dissolve (60–80% Polycount Reduction)
After populating the mesh, execute Blender's BMesh planar dissolve operator to merge coplanar adjacent voxel faces into clean rectangular n-gons/quads:
```python
import bmesh

bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
bmesh.ops.dissolve_limited(bm, faces=bm.faces, angle_limit=0.0001)
bmesh.ops.tris_convert_to_quads(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()
```

---

## 8. glTF-Compatible Combat VFX

> [!IMPORTANT]
> glTF 2.0 does NOT export Blender procedural volume shaders, smoke/fire physics simulations, or point particle systems.
> All VFX in game-ready assets must be constructed from **real polygonal geometry**:

1. **Curved Slash Ribbons**:
   - Extrude a continuous 2D planar strip following the exact arc of the cutting edge.
   - Assign an emissive material with `Alpha Blend` mode or vertex alpha gradient fading from white core to zero opacity at the tail.
2. **Floating Micro-Voxel Shards**:
   - Spawn distinct micro-voxel clusters (1–2 voxels each) orbiting or exploding from impact zones.
   - Parent shards to designated aura/VFX bones within the main armature.
3. **Concentric Runic / Astrological Gyro-Rings**:
   - Stepped circular rings (1–2 voxels thick) with openwork runic teeth.
   - Give each ring its own bone with counter-rotating spin animations for dynamic armillary gyroscopic movement.
