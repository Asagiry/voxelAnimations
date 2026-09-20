# Project Guidelines: Voxel Animations & Combat Assets

> **Context for AI Agents**: This file is automatically loaded into your context. Read it thoroughly before authoring, modifying, or auditing any assets in this repository.

---

## 1. Project Overview & Current Mode: Exploratory Sandbox (R&D)

> [!IMPORTANT]
> **CURRENT PROJECT STATE: EXPERIMENTAL R&D & RAPID PROTOTYPING**
> - **We are in an exploratory, creative phase.** None of the weapons, models, or animations have been finalized or approved yet.
> - **DO NOT over-constrain models with overly rigid, bureaucratic, step-by-step instructions.** Over-prescriptive dogmatic rules stifle creativity and cause models to overthink instead of designing expressive art.
> - **Principles & Intuition over Rigid Checklists**: Reference guides (`references/weapons/`, `references/characters/`) are meant as **inspirational archetypes and physical intuition** (e.g. "a scythe reaps horizontally with the crook leading, a zombie shambles and lunges"), NOT strict immutable recipes.
> - **Creative Freedom First**: Give models room to invent unique silhouettes, unexpected voxel details, distinct palettes, and dynamic motion.
> - **Production Pipeline Comes Later**: Strict assembly-line conveyor rules and rigorous production locks will be introduced later when actual game development begins. For now: rapid prototyping, visual exploration, and fun experimentation in the 3D gallery (`index.html`)!

This repository (**`voxelAnimations`**) is an interactive 3D micro-voxel laboratory and combat gallery in the retro-voxel style of **Trove**, **Cube World**, and **Astra 6**. Everything is procedurally generated via Python in **Blender 4.2+** and viewable directly in `index.html`.

---

## 2. Repository Architecture

```
noble-fermi/ (voxelAnimations)
├── index.html                               # Interactive Three.js 3D web gallery (port 8080)
├── README.md                                # Repository overview & quickstart
├── PROJECT_ONBOARDING.md                    # Deep-dive architecture & onboarding manual
├── GEMINI.md                                # Agent instructions (this file)
├── .gitignore                               # Excludes *.blend1, Python cache; tracks skills/
├── skills/
│   └── trove-voxel-artisan/                 # Core procedural voxel generation skill
│       ├── SKILL.md                         # English archetype dispatcher & visual audit rules
│       └── references/
│           ├── blender-gamedev-practices.md # Technical Blender 4.2+ & gamedev contracts
│           └── weapons/                     # Kinematic & anatomical archetype guides
│               ├── scythe.md                # Lateral reaping harvest (no helicopter spins!)
│               ├── katana.md                # Iaido supersonic crescent, zanshin, chiburui
│               ├── greatsword.md            # Monolithic slab, gravitational earth-cleave
│               ├── bow.md                   # Recurve wings, elastic draw, damped vibration
│               ├── staff.md                 # Hovering mana core, channeling acceleration
│               ├── dagger.md                # Reverse assassin grip, twin cross-slashes
│               └── hammer.md                # Top-heavy kinetic mass, seismic shockwave
└── assets/                                  # 12+ standalone asset packages
    ├── Gemini3.7/                           # Astral Void Scythe (lateral reaping slash)
    ├── Gemini3.8/                           # Astral Void Scythe (gyro-ring orbital)
    ├── ClaudeSonnet4.6/                     # Astral Void Scythe (dual orbit rings)
    ├── claude_opus_46/                      # Astral Void Scythe (concentric celestial)
    ├── gemini36/                            # Astral Void Scythe (void blade)
    ├── GeminiPro/                           # Astral Void Scythe (obsidian core)
    ├── katana_flash/                        # Iaido Crescent Katana (continuous ribbon)
    ├── katana_38_flash/                     # Iaido Razor Katana (5-phase iaido)
    ├── katana_pro/                          # Tamahagane Katana (classic stance)
    ├── guts_sword_flash/                    # Dragon Slayer (colossal greatsword)
    ├── flame_sword/                         # Infernal Flame Sword (living fire surge)
    └── magic_bow/                           # Celestial Magic Bow (starlight draw)
```

---

## 3. Mandatory Non-Negotiable Engineering Rules

### Rule 1: Communication vs Code Language
- **User Communication**: Always communicate with the user in **Russian** (clear, concise, structured).
- **Code & Prompts**: Always write procedural Python scripts, internal docstrings, prompt specifications, and technical references in **English**. (LLMs reason, compute 3D vectors, and generate Blender code with far higher fidelity in English).

### Rule 2: Blender Headless CLI Execution
- Never execute `python script.py` outside Blender. `bpy` is embedded inside Blender's C/Python environment.
- Always execute scripts via Blender CLI:
  ```powershell
  & 'C:\Program Files\Blender Foundation\Blender 4.2\blender.exe' --background --python build_asset.py
  ```

### Rule 3: Blender 4.2+ glTF Export Contract
- **Never pass deprecated flags** such as `export_rest_pose_armature` (raises fatal `TypeError` in Blender 4.2+).
- Use the authoritative parameter set:
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

### Rule 4: Bone Local Axis Kinematics (The Local +Y Rule)
- In Blender armatures, **a bone's local +Y axis always points longitudinally along the bone shaft**.
- Longitudinal spins, rolls, or drilling motions must rotate strictly on **local Y (`rotation_euler.y`)**.
- Never rotate on local Z or X to spin an upright weapon; doing so flips the weapon 180° upside-down.
- Always declare `pbone.rotation_mode = 'XYZ'` before setting `pbone.rotation_euler`.

### Rule 5: Gamedev 5-Phase Combat State Machine
Never animate an attack as a meaningless 360°/720° helicopter spin. Melee attacks must follow:
1. **Phase 1: Startup / Telegraph (15–25%)** — Wind-up, kinetic energy coiling.
2. **Phase 2: Active Hit Window (5–10%)** — Explosive acceleration, cutting edge leads the arc, hitbox active.
3. **Phase 3: Overshoot / Follow-Through (10–15%)** — Momentum carries past impact.
4. **Phase 4: Zanshin / Hit-Stop / Recoil (20–30%)** — Deceleration snap, physical mass confirmation.
5. **Phase 5: Recovery / Sheath / Noto (25–35%)** — Graceful return to combat idle.

### Rule 6: Depsgraph Evaluated Camera Framing (Anti-Black Render Guard)
- **Never parent camera or `cam_target` to an animated bone**. They must remain static world objects.
- Frame the camera using evaluated depsgraph (`eval_obj = obj.evaluated_get(depsgraph)`) across **all scene objects** at the peak action frame to prevent clipping wide slashes or VFX ribbons.
- Render in **1:1 square aspect ratio** (`1024x1024`) with Cycles samples capped at `96–128` and AgX tonemapping.

### Rule 7: Mandatory Visual Audit Loop
Never declare an asset complete without running `view_file` on `<asset_name>_render.png`. Verify:
- [ ] Weapon or Character occupies 60%–80% of canvas diagonally.
- [ ] Proper upright orientation (not flipped).
- [ ] Saturated, rich emission without washed-out white clipping in AgX.
- [ ] Attack ribbons spawn behind the cutting edge.

### Rule 8: Mandatory Clean-up & Zero-Clutter Contract
Every script and agent execution must keep the repository pristine:
- Delete all temporary debug renders (`test_*.png`), Blender auto-save backups (`*.blend1`), temporary obj/ply files, and one-off test scripts before finishing.
- Each asset package in `assets/<asset_name>/` must contain strictly the 5 canonical deliverables:
  1. `build_<name>.py` (reproducible procedural generator)
  2. `<name>.blend` (Blender source scene)
  3. `<name>.glb` (game-ready binary glTF)
  4. `<name>_render.png` (high-fidelity Cycles AgX beauty render)
  5. `<name>_data.js` (Base64 data URI for zero-CORS embedding)

### Rule 9: Trove Modular Biped & Standard Sockets Contract
When authoring characters, monsters, weapons, or equipment:
- **Never make characters flat Minecraft blocks**: Trove characters are stylized Chibi Bipeds with:
  - **Segmented / Floating Limbs**: Hands/gloves, feet/boots, and pauldrons have visible breathing room / detachment gaps from torso and limbs. No continuous stretchy tubes of flesh!
  - **Multi-Layered Micro-Voxel Relief**: Heads are $10 \times 10 \times 10$ bases, but hair, horns, crowns, masks, teeth, and armor must be extruded in multiple stepped micro-voxel layers for rich silhouette and self-shadowing.
- **Rigid Dimensions & Socket Standard**:
  - Global Voxel Unit: `VOXEL_SIZE = 0.015m` across all characters, weapons, and gear.
  - Standard Biped Height: 32–36 voxels tall (~0.48m – 0.54m).
  - Standard Sockets in Character Armature:
    * `Socket_Hand_R`: inside right hand palm (origin for weapon grip).
    * `Socket_Hand_L`: inside left hand palm (shield / off-hand / bow hold).
    * `Socket_Head`: at top center of head (for hats, helmets, crowns).
    * `Socket_Back`: on upper spine (for capes, wings, sheaths).
  - Standard Weapon Grip: Handle thickness is exactly $2 \times 2$ or $3 \times 3$ voxels with handle grip center positioned at $(0, 0, 0)$ in rest pose so any weapon seamlessly snaps into `Socket_Hand_R`.
  - Standard Equipment Fit: Helmets/hats have an internal clearance cavity of $10 \times 10 \times 10$ voxels to fit any standard head.

---

## 4. Web Gallery Integration Contract

Every new asset must be wired into `index.html`:
1. Read the exported `.glb` binary, convert to Base64, and save as `<asset_name>_data.js`:
   ```javascript
   window.ASSET_NAME_BASE64 = "data:model/gltf-binary;base64,...";
   ```
2. In `index.html`:
   - Add `<script src="assets/<folder>/<asset_name>_data.js"></script>`.
   - Add a tab button in `<div class="asset-tabs">`.
   - Add the asset configuration to `const ASSETS = { ... }` with name, base64 key, ideal camera position, and animation state details.
3. Test in browser: start `python -m http.server 8080` and verify at `http://localhost:8080/index.html`.
