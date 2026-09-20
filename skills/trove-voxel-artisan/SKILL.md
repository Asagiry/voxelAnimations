---
name: trove-voxel-artisan
description: Universal abstract skill for authoring, rigging, animating, visually auditing, and exporting any 3D asset (weapons, characters, creatures, props) in authentic Trove / Cube World / Astra 6 micro-voxel style.
---

# Universal Trove Voxel Artisan Skill

Transform any natural-language 3D asset request into production-ready, authentic micro-voxel 3D models with rigging, keyframe animations, and verified visual quality in Blender 4.2+.

---

## 1. Technical Reference & Core Gamedev Practices

Before writing Blender generation scripts, review the comprehensive gamedev and Blender 4.2+ technical specification:
👉 [`references/blender-gamedev-practices.md`](file:///C:/Users/Voimax/.gemini/config/skills/trove-voxel-artisan/references/blender-gamedev-practices.md)

This reference contains the non-negotiable runtime rules:
- **Headless Execution Contract**: How to invoke Blender 4.2 headless CLI (`--background --python`) and resolve binaries without crashing on missing `PATH`. (Never attempt `import bpy` in standard Python!).
- **Modern glTF 2.0 Export Contract**: Blender 4.2+ parameter specifications, avoiding deprecated Blender 3.x flags like `export_rest_pose_armature`.
- **Principled BSDF Socket API**: Safe lookup for `Specular IOR Level`, `Emission Color`, and AgX tonemapping safeguards.
- **Bone Local Axis Kinematics**: Why longitudinal rolls MUST use local +Y (`rotation_euler.y`), and how to avoid gimbal lock/inversion flips.
- **Dynamic Depsgraph Camera Auto-Framing**: Evaluated depsgraph math across all scene meshes at the peak action frame, preventing cropped weapon swings or pitch-black void renders.
- **Voxel Optimization**: Exposed-quad boundary checking and planar quad dissolve (`dissolve_limited` + `tris_convert_to_quads`).

---

## 2. The Archetype Dispatcher (Read Reference First!)

When receiving a user request, **first identify the weapon/asset archetype** and read its specialized kinematic guide using `view_file` before writing code:

| Archetype | Description | Reference Guide |
|---|---|---|
| **Scythes & Reapers** | Lateral reaping cuts, inner crook cutting edge, orbital gyro-rings. (Never propeller spins!) | [`references/weapons/scythe.md`](file:///C:/Users/Voimax/.gemini/config/skills/trove-voxel-artisan/references/weapons/scythe.md) |
| **Katanas & Iaido** | Sori curvature, hamon wave, tsuba, samegawa grip, supersonic drawing cut & zanshin freeze. | [`references/weapons/katana.md`](file:///C:/Users/Voimax/.gemini/config/skills/trove-voxel-artisan/references/weapons/katana.md) |
| **Colossal Greatswords** | Monolithic slabs of raw iron, two-handed hoists, ground-shattering gravitational slams. | [`references/weapons/greatsword.md`](file:///C:/Users/Voimax/.gemini/config/skills/trove-voxel-artisan/references/weapons/greatsword.md) |
| **Bows & Ranged** | Stepped recurve wings, elastic bowstring strain, supersonic release & damped vibration. | [`references/weapons/bow.md`](file:///C:/Users/Voimax/.gemini/config/skills/trove-voxel-artisan/references/weapons/bow.md) |
| **Staves & Catalysts** | Levitation, runic headpieces, hovering core acceleration & pulse spellcasting. | [`references/weapons/staff.md`](file:///C:/Users/Voimax/.gemini/config/skills/trove-voxel-artisan/references/weapons/staff.md) |
| **Daggers & Dual Blades** | Reverse stealth grips, razor-fast cross-slashes, fatal punctures & acrobatic spin resets. | [`references/weapons/dagger.md`](file:///C:/Users/Voimax/.gemini/config/skills/trove-voxel-artisan/references/weapons/dagger.md) |
| **Warhammers & Greathammers** | Top-heavy kinetic mass, strained overhead hoists, seismic shockwaves & earth extraction. | [`references/weapons/hammer.md`](file:///C:/Users/Voimax/.gemini/config/skills/trove-voxel-artisan/references/weapons/hammer.md) |

*(For other categories such as shields, mounts, monsters, or character classes, apply the nearest kinematic principles from these references.)*

---

## 3. Universal Aesthetic & Geometric Specifications

1. **Micro-Voxel Scale (Not Minecraft Blocks)**:
   - Always use a micro-voxel grid: `VOXEL_SIZE = 0.010` to `0.015` meters (1.0 to 1.5 cm per voxel cube).
   - Humanoids: 30 to 45 voxels tall (~1.4m – 1.8m).
   - Medium Weapons (Scythes, Katanas, Bows, Staves, Warhammers): 60 to 95 voxels long (~0.8m – 1.25m).
   - Colossal Heavy Weapons (e.g. Dragon Slayer): 95 to 130 voxels long (~1.2m – 1.6m), thick cross-sections (4 to 10 voxels thick!).
   - **Solid Volumetric Mass**: Never build thin 1-voxel flat cards or wireframes. Every component must have solid structural depth, stepped voxel bevels, and tactile presence.

2. **The Hero Silhouette & Readability Principle**:
   - The core weapon body must always present a bold, readable silhouette.
   - Secondary effects (runic rings, vortex discs, flames, astral spark clusters):
     * Must **frame, accent, and orbit** the subject.
     * Must **never obscure or swallow** the main silhouette into an unreadable noisy blob.

3. **Color Palette & AgX Tonemapping Safeguards**:
   - Palette selection: Choose a cohesive 4-6 tone palette (Base Chassis + Metallic Accent/Gold + Elemental Energy + Shadow/Embers).
   - Flat Shading: Strict flat shading (`use_smooth = False`) on all voxel polygons for authentic retro fidelity.
   - Controlled Emission:
     * Colored magic/fire/energy: Keep emission intensity between **1.0 and 2.5** to avoid clipping saturated hues (purples, reds, cyans) into washed-out white under Blender's AgX color management.
     * Blinding white-hot spark cores: Restrict strictly to tiny focal points (emission 3.5 – 5.0).

---

## 4. The Gamedev 5-Phase Hitbox State Machine

Every attack animation must be choreographed using the authoritative 5-phase gamedev combat state machine:

1. **Phase 1: Startup / Telegraph (15–25%)**:
   - Weapon pulls back into an elevated anticipation posture; kinetic potential energy coils.
   - Clear visual cue signaling the attack path.
2. **Phase 2: Active Hit Window (5–10%)**:
   - Explosive acceleration across the strike plane; cutting edge leads the arc at maximum velocity.
   - Combat hitbox active! Geometric slash ribbon spawns directly behind the cutting edge.
3. **Phase 3: Overshoot & Follow-Through (10–15%)**:
   - Weapon momentum carries past the contact point; energy trail reaches maximum expansion.
4. **Phase 4: Zanshin / Hit-Stop / Recoil Hold (20–30%)**:
   - Deceleration snap or micro-recoil tremor confirming heavy mass and impact.
   - Posture is locked while slash ribbons dissolve.
5. **Phase 5: Recovery / Sheath / Noto (25–35%)**:
   - Smooth reset returning the weapon to combat idle. Seamless 60-frame loop.

---

## 5. Algorithmic Mesher Pipeline

To keep models game-ready and lightweight:
1. **Exposed Quads Only**: Check the 6 orthogonal neighbor directions for each voxel; only generate quads for outer boundary faces that border empty space. Internal hidden faces must never be generated.
2. **Planar Dissolve**: Run Blender's `dissolve_limited(angle_limit=0.0001)` and `tris_convert_to_quads()` on coplanar voxel faces to reduce polycount by 60%–80% without losing a single sharp corner.

---

## 6. Rigging & Animation Standards (Blender 4.x Gamedev Rules)

1. **Unified Armature with Vertex Groups**:
   - Use a single Armature modifier on the mesh with explicit Vertex Groups for all moving sections.
   - Every vertex in the rest pose must share the scene origin $(0, 0, 0)$ to prevent unwanted displacement offsets.

2. **CRITICAL: Blender Bone Local Axis Rules**:
   - In Blender, **a bone's local Y axis ALWAYS points along the bone length (from head to tail)**.
   - For longitudinal spins, rolls, or whirlwinds:
     * Animate rotation **strictly around the bone's local Y axis (`yaw/roll`)**.
     * **NEVER rotate around local Z or X** to spin an upright weapon; doing so tilts or flips the weapon 180° upside-down in world space!

3. **Pivot Placement for Scaling / VFX Bones**:
   - For bones that scale in animation (e.g. expanding vortex discs, stretching energy ribbons, pulsating auras), position the bone head precisely at the **center of attachment/rotation** so it expands outward symmetrically without detaching.

4. **Euler Mode Declaration**:
   - In Blender pose mode, pose bones default to Quaternion rotation. When keyframing Euler angles in Python, you must explicitly declare `pb.rotation_mode = 'XYZ'` before setting `pb.rotation_euler`.

---

## 7. The Mandatory Visual Audit Loop (The "Photo Check")

**Never declare an asset complete without visually inspecting a rendered beauty shot.**

### 1. Fast Cycles Setup & Scene Safety Guards:
- **Render Engine**: Cycles with GPU compute (or CPU fallback) and Denoising enabled.
- **MANDATORY Sample Cap**: Always set `scene.cycles.samples = 128` (or 96). **NEVER leave Blender's default 4096**, which wastes minutes of compute time.
- **MANDATORY 1:1 Square Resolution**:
  Set `resolution_x = 1024` and `resolution_y = 1024`. (Never use wide 16:9 aspect ratios like 1920x1080 for asset showcases, as they severely crop tall weapons).
- **AgX Color Management**:
  Set `view_transform = 'AgX'` and `look = 'AgX - High Contrast'`.
- **CRITICAL ANTI-BLACK RENDER GUARD**:
  > **NEVER parent the camera, camera target (`cam_target`), or scene lights to animated bones or armatures!**
  > They MUST remain independent static objects in global world space. Parenting the camera to an animated bone causes the camera to swing into outer space mid-animation, resulting in a pitch-black render.

- **Dynamic Evaluated Bounding Box (Never Clips Swings or VFX)**:
  Do not calculate camera framing from static rest-pose coordinates of a single mesh. Evaluate the scene's depsgraph at the **key action frame** (`scene.frame_set(ACTION_FRAME)`) across ALL scene meshes (including wide attack ribbons and particle discs). Compute the global center and maximum span with a comfortable **1.35x margin**.
- **Elevated 40°–50° Camera Angle**:
  Position the camera elevated diagonally (`center[2] + span * 1.05`) so horizontal attack discs, vortex rings, and ground impacts are perceived in full 3D volume, never edge-on as a flat 1D line.

### 2. Execute & Inspect:
- Render the key attack frame (peak impact / swing with trail active) to `<asset_name>_render.png`.
- **Execute `view_file` on the rendered PNG image.**
- **Strict Visual Acceptance Criteria**:
  * [ ] **Centering & Scale**: Does the weapon occupy 60%–80% of the canvas diagonally? If it is tiny in the corner or clipped outside the frame, **recalculate camera framing and re-render immediately**.
  * [ ] **Volumetric Presence**: Are attack trails/vortexes rich and volumetric, not thin detached single pixels?
  * [ ] **Correct Upright Orientation**: Is the weapon oriented naturally, not flipped upside-down by a wrong bone axis?
  * [ ] **Color Vibrancy**: Are glowing elements rich and saturated, not bleached into solid white?
  * [ ] **Structural Integrity**: Are moving parts seamlessly joined with no accidental gaps?

### 3. Self-Correction:
- If ANY check fails, modify the procedural generation script, re-run Blender, and re-inspect with `view_file` until the visual evidence confirms perfection.

---

## 8. Output Delivery Structure & Export Standards (Blender 4.2+)

Every asset must be delivered in its own dedicated subfolder under `assets/<asset_name>/`:
- `assets/<asset_name>/<asset_name>.blend` — Full editable Blender 4.2 project.
- `assets/<asset_name>/<asset_name>.glb` — Game-ready glTF 2.0 with embedded skeletal animations.
- `assets/<asset_name>/<asset_name>_render.png` — Visual beauty render.
- `assets/<asset_name>/build_<asset_name>.py` — Deterministic procedural generation script.
- `assets/<asset_name>/<asset_name>_data.js` — Base64 model data for zero-CORS browser preview.

### 1. Modern glTF 2.0 Export Call (Blender 4.2+):
**DO NOT pass deprecated Blender 3.x flags** (such as `export_rest_pose_armature`, which causes a fatal `TypeError`). Use:
```python
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    export_animations=True,
    export_skins=True,
    export_all_influences=False
)
```

### 2. Automatic Embedded `_data.js` Generation:
Immediately after exporting the `.glb`, read its binary bytes, encode them into Base64, and write `<asset_name>_data.js` with the standard window variable prefix:
```javascript
window.ASSET_NAME_BASE64 = "data:model/gltf-binary;base64," + base64_string;
```

### 3. Environment Fallback:
If `blender` is not in the system `PATH` on Windows, invoke `C:\Program Files\Blender Foundation\Blender 4.2\blender.exe` or search `C:\Program Files\Blender Foundation\`.
