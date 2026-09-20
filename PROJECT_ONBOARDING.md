# Project Onboarding: Voxel Animations & 3D Combat Laboratory

Welcome to **`voxelAnimations`**! This document provides a complete onboarding walkthrough for any developer or AI agent joining this codebase.

---

## 1. What We Are Building & Why

This project is an experimental laboratory and production pipeline for **retro micro-voxel 3D game assets** inspired by *Trove*, *Cube World*, and *Astra 6*.

### What Makes This Project Unique:
1. **Micro-Voxel Scale (Not Minecraft)**:
   We use tiny voxel dimensions ($VOXEL\_SIZE = 0.010 - 0.015$m). A sword or scythe is 60 to 120 voxels long, allowing detailed curvature, stepped bevels, intricate hilt wraps (*ito*), temper lines (*hamon*), and faceted gemstones.
2. **100% Procedural & Deterministic**:
   Every asset is generated via standalone Python scripts inside **Blender 4.2+**. No manual box-modeling required. You run the script, and in seconds it generates the voxel mesh, bakes materials, rigs the armature, bakes skeletal animation, renders a beauty audit image, and exports a game-ready `.glb`.
3. **Zero-CORS Web Gallery**:
   All `.glb` models are automatically encoded into Base64 JavaScript strings (`<asset>_data.js`). Anyone can open `index.html` locally via a simple HTTP server (`python -m http.server 8080`) and view all 12+ weapons in full interactive 3D with animation playback without hitting CORS security errors.
4. **Autonomous AI Skill System**:
   The project ships with [`skills/trove-voxel-artisan/`](skills/trove-voxel-artisan/), enabling autonomous AI agents to design, rig, and audit new weapons with zero human hand-holding.

### Current Mindset: Creative Exploration (R&D Mode)
> [!IMPORTANT]
> **We are in an exploratory, creative phase.** None of the weapons, models, or animations have been finalized or approved yet.
> - Avoid rigid dogmatic instructions: models need creative freedom to invent striking silhouettes and unique shapes.
> - Reference guides are conceptual inspiration, not rigid recipes.
> - Once the actual game production starts, we will establish an assembly-line conveyor pipeline. Until then, rapid prototyping and visual experimentation rule!

---

## 2. Directory Structure & File Map

```
noble-fermi/ (voxelAnimations)
│
├── index.html                               # Three.js browser viewer with orbit controls & animation playback
├── README.md                                # Quickstart & model summary
├── GEMINI.md                                # Auto-loaded AI agent rules & execution constraints
├── PROJECT_ONBOARDING.md                    # This comprehensive onboarding manual
├── .gitignore                               # Git rules (excludes *.blend1, Python cache, tracks skills/)
│
├── skills/
│   └── trove-voxel-artisan/                 # The universal 3D voxel authoring skill
│       ├── SKILL.md                         # Main dispatcher & visual audit checklist
│       └── references/
│           ├── blender-gamedev-practices.md # Technical Blender 4.2+ API & gamedev contracts
│           └── weapons/                     # 7 specialized weapon archetype references
│               ├── scythe.md                # Scythes: Lateral reaping cuts, crook-leading arcs
│               ├── katana.md                # Katanas: Iaido supersonic drawing, zanshin freeze
│               ├── greatsword.md            # Greatswords: Colossal slabs, gravitational slams
│               ├── bow.md                   # Bows: Recurve wings, elastic draw, damped vibration
│               ├── staff.md                 # Staves: Hovering cores, channeling spin, spell thrust
│               ├── dagger.md                # Daggers: Reverse stealth grip, twin cross-slashes
│               └── hammer.md                # Hammers: Top-heavy kinetic mass, seismic shockwave
│
└── assets/                                  # All completed weapon asset packages
    ├── Gemini3.7/                           # Astral Void Scythe (Gemini 3.7 Flash - lateral reaping)
    ├── Gemini3.8/                           # Astral Void Scythe (Gemini 3.8 Flash High - gyro orbital)
    ├── ClaudeSonnet4.6/                     # Astral Void Scythe (Claude Sonnet 4.6 - dual rings)
    ├── claude_opus_46/                      # Astral Void Scythe (Claude Opus 4.6 - concentric glyphs)
    ├── gemini36/                            # Astral Void Scythe (Gemini 3.6 Flash)
    ├── GeminiPro/                           # Astral Void Scythe (Gemini 3.1 Pro)
    ├── katana_flash/                        # Iaido Crescent Katana (continuous ribbon arc)
    ├── katana_38_flash/                     # Iaido Razor Katana (5-phase iaido choreography)
    ├── katana_pro/                          # Tamahagane Katana (classic stance)
    ├── guts_sword_flash/                    # Dragon Slayer (Guts colossal raw iron slab)
    ├── flame_sword/                         # Infernal Flame Sword (living elemental fire)
    └── magic_bow/                           # Celestial Magic Bow (starlight draw & release)
```

---

## 3. Anatomy of an Asset Package

Every subfolder inside `assets/<name>/` is completely self-contained:

1. **`build_<name>.py`**:
   The procedural generation script. Cleans the scene, generates voxel coordinates, assigns vertex groups & materials, creates an Armature with named bones, keyframes the 5-phase combat animation, sets up the camera & lighting, renders `<name>_render.png`, exports `<name>.glb`, and generates `<name>_data.js`.
2. **`<name>.blend`**:
   The native Blender 4.2 project file. Can be opened in Blender GUI at any time to inspect bones, materials, or timelines.
3. **`<name>.glb`**:
   Game-ready glTF 2.0 binary with embedded skeletal animation. Compatible with Three.js, Godot 4, Unity, and Unreal Engine.
4. **`<name>_render.png`**:
   Cycles beauty render (1024x1024 square, AgX High Contrast) used for visual verification.
5. **`<name>_data.js`**:
   Base64 representation of `<name>.glb` formatted as `window.<NAME>_BASE64 = "data:model/gltf-binary;base64,..."`.

---

## 4. How to Create a New Weapon (Step-by-Step Tutorial)

When tasked with adding a new weapon (e.g. an *Infernal Warhammer* or *Cursed Dagger*):

### Step 1: Consult the Archetype Reference
Read the corresponding reference guide in [`skills/trove-voxel-artisan/references/weapons/`](skills/trove-voxel-artisan/references/weapons/).
Understand the:
- Anatomical proportions (length, thickness, cross-sections).
- 5-Phase combat choreography (Telegraph $\to$ Strike $\to$ Overshoot $\to$ Zanshin $\to$ Recovery).
- Critical dos and don'ts (e.g., never spin a scythe like a helicopter; rotate on local +Y).

### Step 2: Write the Procedural Generator (`assets/<name>/build_<name>.py`)
- Follow the API contracts in [`references/blender-gamedev-practices.md`](skills/trove-voxel-artisan/references/blender-gamedev-practices.md).
- Use `VOXEL_SIZE = 0.012`.
- Emit only boundary outer quads (check 6 orthogonal neighbors).
- Run BMesh `dissolve_limited(angle_limit=0.0001)` to optimize polycount.
- Parent mesh to Armature via Vertex Groups.
- Set bone rotation mode: `pbone.rotation_mode = 'XYZ'`.
- Dynamic camera framing: evaluate depsgraph across all scene meshes at the peak swing frame.
- Cycles samples capped at `96–128` (never 4096).

### Step 3: Execute in Headless Blender
```powershell
& 'C:\Program Files\Blender Foundation\Blender 4.2\blender.exe' --background --python assets/<name>/build_<name>.py
```

### Step 4: Perform the Visual Audit Loop
Open and inspect `assets/<name>/<name>_render.png` using `view_file`:
- Is the weapon centered and occupying 60%–80% of the canvas?
- Is it upright and correctly oriented?
- Are glowing materials rich in color (not washed-out white)?
- Does the slash ribbon align cleanly with the cutting edge?
*If anything is off, tune the script and re-render.*

### Step 5: Wire into `index.html`
1. Add script tag to `index.html`:
   ```html
   <script src="assets/<name>/<name>_data.js"></script>
   ```
2. Add a tab button in `<div class="model-tabs">`:
   ```html
   <button class="model-tab" data-model="<name_id>">🔨 Name</button>
   ```
3. Add entry to `MODELS` dictionary in the Three.js setup script.
4. Verify in browser at `http://localhost:8080/index.html`.

---

## 5. Running the Local Web Server

```powershell
python -m http.server 8080
```
Open your browser to: **`http://localhost:8080/index.html`**

Controls:
- **Left click + drag**: Orbit camera (360° rotation)
- **Right click + drag**: Pan camera
- **Scroll wheel**: Zoom into individual micro-voxels
- **⚡ Действие! Button**: Trigger the combat animation
- **Speed Selector**: 0.25x, 0.5x, 1.0x, 1.5x slow-motion playback

---

## 6. Git Workflow

- **Remote**: `https://github.com/Asagiry/voxelAnimations.git`
- **Main Branch**: `main`
- Keep `.gitignore` intact: it ensures skills are tracked while excluding temporary Blender `.blend1` backup files.

---

## 7. Specialized Subagent Architecture & Socket Standards

To scale asset generation without style fragmentation, the pipeline is divided into 3 specialized subagents, all sharing the **Trove Voxel & Socket Standard**:

| Subagent | Role | Key Constraints & Sockets |
| :--- | :--- | :--- |
| `weapon_artisan` | Melee, ranged & magical weapons | Handle grip thickness: $2 \times 2$ or $3 \times 3$ voxels. Pivot at `(0, 0, 0)` matching `Socket_Hand_R`. 5-phase attack animation. |
| `character_artisan` | Trove Chibi Bipeds & Monsters | Height 32–36 voxels. Segmented/floating limbs (hands, boots, pauldrons detached with joint gaps). Armature includes `Socket_Hand_R`, `Socket_Hand_L`, `Socket_Head`, `Socket_Back`. |
| `equipment_artisan` | Hats, helms, wings, shields, pauldrons | Helmets have internal hollow $10 \times 10 \times 10$ cavity to fit any standard head. Anchor points match standard sockets. |

### Clean-up Contract
Every subagent must clean up all temporary `test_*.png` images and `*.blend1` files before finishing. Only 5 canonical files per asset: `build_*.py`, `*.blend`, `*.glb`, `*_render.png`, `*_data.js`.
