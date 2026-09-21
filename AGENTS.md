# AGENTS.md: Developer & Agent Engineering Manual

> **Authoritative Agent Instructions for `voxelAnimations`**
> This repository is an experimental 3D micro-voxel laboratory and retro combat gallery in the style of **Trove**, **Cube World**, and **Astra 6**.
> All 3D assets are procedurally generated via Python in **Blender 4.2+** and rendered interactively in `index.html`.

---

## 1. Project Mode: Exploratory Sandbox (R&D)

- **Rapid Prototyping & Intuition First**: We are in an active, creative exploration phase. None of the assets are finalized.
- **Principles over Rigid Checklists**: Reference guides in `skills/trove-voxel-artisan/references/` are conceptual archetypes (e.g. "a scythe reaps horizontally with the crook leading; a zombie shambles and lunges"), NOT dogmatic recipes.
- **Creative Freedom**: Experiment with bold silhouettes, stepped micro-voxel relief, saturated color palettes, and expressive combat animations.

---

## 2. Mandatory Runtime & Environment Contracts

### 2.1 Communication & Language
- **User Communication**: Always communicate with the user in **Russian** (clear, concise, structured).
- **Code, Prompts & Documentation**: Procedural Python scripts, internal docstrings, prompt specifications, and technical guides must be authored in **English**.

### 2.2 Headless Blender CLI Execution
- Blender 4.2+ is configured globally in `PATH` (and fallback `C:\Program Files\Blender Foundation\Blender 4.2\blender.exe`). Always execute via:
  ```powershell
  blender --background --python build_asset.py
  ```
  *(or `& 'C:\Program Files\Blender Foundation\Blender 4.2\blender.exe' --background --python build_asset.py`)*

### 2.3 Scope Containment & STRICT ZERO-PEEKING RULE (Absolute Isolation)
- **STRICT ZERO-PEEKING / BLIND ASSET CREATION**: Under NO circumstances should the orchestrator or any subagent inspect, read, grep, or explore existing files in `assets/`!
  * **NEVER call `view_file`, `grep_search`, `find_by_name`, or `list_dir` on existing assets in `assets/`**.
  * Peeking at existing assets causes coordinate copying, stale code carryover, and destroys procedural uniqueness.
  * All anatomical dimensions, voxel algorithms, palettes, and rigging guides are 100% self-contained in `skills/trove-voxel-artisan/`.
  * The `assets/` directory is strictly **WRITE-ONLY** for the new asset folder being generated (`assets/<name>/`).
- **ZERO RESEARCH ON `/createAsset`**: When `/createAsset <prompt>` is invoked, the agent MUST NOT perform research on `assets/`. It must **IMMEDIATELY launch Subagent 1 (Voxel Modeler) on turn 1**!
- **NEVER modify or rewrite `index.html`**: Vite dynamically serves models via `/api/assets`. Touch nothing outside `assets/<name>/`!

### 2.4 glTF 2.0 Modern Export Contract
- **Never use deprecated flags** like `export_rest_pose_armature` (raises fatal `TypeError` in Blender 4.2+).
- Use the authoritative parameter set:
  ```python
  bpy.ops.export_scene.gltf(
      filepath=glb_filepath,
      export_format='GLB',
      export_animations=True,
      export_skins=True,
      export_all_influences=False,
      export_apply=False,   # NEVER apply modifiers on rigged meshes!
      export_yup=True
  )
  ```

### 2.5 Bone Local Axis Kinematics (The Local +Y Rule)
- In Blender armatures, **a bone's local +Y axis always points longitudinally along the bone shaft** (from head to tail).
- Longitudinal spins, rolls, or drilling motions must rotate strictly on **local Y (`rotation_euler.y`)**.
- Always declare `pbone.rotation_mode = 'XYZ'` before setting `pbone.rotation_euler`.

### 2.6 Depsgraph Evaluated Camera Framing (Anti-Black Render Guard)
- **Never parent camera or `cam_target` to an animated bone or armature**. They must remain static world objects.
- Frame the camera using evaluated depsgraph (`eval_obj = obj.evaluated_get(depsgraph)`) across all scene meshes at the peak action frame to prevent clipping.
- Render in **1:1 square aspect ratio** (`1024x1024`) with Cycles samples capped at `96–128` and AgX tonemapping.

### 2.7 The Canonical Modular Deliverables
Each asset package in `assets/<asset_name>/` must contain strictly:
1. `model.py` (geometry, voxel materials, armature, vertex groups, sockets)
2. `anim_walk.py` (locomotion walk loop, NLA track 'Walk')
3. `anim_attack.py` (5-phase combat strike, dense in-betweens, NLA track 'Attack')
4. `build.py` (orchestrator: runs model.py -> anim_walk.py -> anim_attack.py)
5. `<name>.blend` (Blender source scene)
6. `<name>.glb` (game-ready binary glTF with baked animations)
7. `<name>_render.png` (high-fidelity Cycles AgX beauty render)
8. `<name>_data.js` (Base64 data URI for zero-CORS embedding)

---

## 3. Trove Modular Chibi Biped Standards (Characters & Monsters)

When authoring characters, undead monsters, or NPCs:

### 3.1 Anatomical Dimensions
- **Global Voxel Grid**: `VOXEL_SIZE = 0.015m` (1.5 cm per voxel).
- **Total Height**: 32–36 voxels tall (~0.48m – 0.54m).
- **Head Base**: $10 \times 10 \times 10$ voxels.
- **Torso**: $8 \times 6 \times 8$ voxels (Chest) + $8 \times 6 \times 3$ voxels (Pelvis).
- **Pauldrons**: $4 \times 5 \times 3$ to $5 \times 6 \times 4$ voxels (floating detached armor).
- **Hands / Gloves**: $4 \times 4 \times 4$ to $4 \times 4 \times 5$ voxels (chunky floating blocks).
- **Feet / Boots**: $4 \text{ wide} \times 6 \text{ long} \times 4 \text{ high}$ voxels.

### 3.2 Segmented & Floating Limbs
- **Never create solid Minecraft noodle limbs**.
- Hands/gloves, boots, and pauldrons must have a visible $1$-voxel detachment gap from their connecting limb segments.
- This creates the authentic Trove "toy/figurine" look and prevents mesh pinching during extreme animations.

### 3.3 Multi-Layered Micro-Voxel Relief
- Extrude hair strands, horns, skull cracks, teeth, eyebrows, belt buckles, and armor plates $+1$ or $+2$ voxels outward from the base volume.

### 3.4 Equipment Socket Hierarchy
Armatures must include standard empty socket bones for modular equipment:
- `Socket_Hand_R`: inside right palm (weapon grip origin).
- `Socket_Hand_L`: inside left palm (shield / bow hold).
- `Socket_Head`: top center of head (hats, helmets, crowns).
- `Socket_Back`: upper spine rear (capes, wings, sheaths).

### 3.5 Playable Character Classes & Modular Weapon Decoupling
- **Never bake weapons into playable character meshes**: Playable character classes (Knight, Paladin, Rogue, Mage, Archer, etc.) must be authored with **completely empty hands** (clean grasp fist around `Socket_Hand_R`).
- **Grip Cavity Standard**: The palm/fingers form an open grasp channel with `Socket_Hand_R` centered inside, ready to receive any modular weapon handle ($2\times 2$ or $3\times 3$ voxels).
- **Class Archetype Animations with Phantom Grip**: The attack animation is choreographed for the intended class weapon style (e.g. 1-handed sword slash, 2-handed greatsword slam, staff channeling, dagger thrust), animated with a natural weapon-holding hand pose so that any weapon attached to `Socket_Hand_R` follows the strike with 100% fidelity.
- **Universal Cross-Compatibility**: Because weapon models in `assets/` have their grip origin at $(0, 0, 0)$ and characters have `Socket_Hand_R`, any generated weapon can be dynamically snapped into the hand in the 3D engine without modifying the character.

### 3.6 Canonical Modular Weapon Specification (Zero-Animation, Vertical Axis, Zero-Plinth)
When authoring or generating standalone weapons (Swords, Katanas, Greatswords, Bows, Staves, Axes, Daggers):
1. **Pure Static Equipment Item**:
   - A modular weapon is a **static equipment mesh**, NOT an animated diorama or character.
   - **NO armature or skeletal bones** (unless required for flexible bows/whips).
   - **NO embedded animations** (never bake `Walk` or `Attack` into a sword file!).
   - **NO display stands, plinths, pedestals, or scene debris**: The file must contain strictly the weapon itself.
2. **Grip Origin Invariant ($(0, 0, 0)$ Pivot)**:
   - The weapon's local origin $(0, 0, 0)$ is placed **strictly at the center of the grip handle** where the character's fingers wrap around it.
3. **Strict Vertical Axis Orientation Invariant**:
   - In Blender: The blade/shaft points strictly along **World $+Z$ (UP)**. The hilt guard and pommel extend downward along $-Z$. The cutting edge / front faces **World $+Y$ (FORWARD)**. Crossguard/quillons extend along $X$ (LEFT/RIGHT).
   - Upon glTF export (`export_yup=True`): The blade points along $+Y$ (UP in Three.js/game engines), and cutting edge faces $+Z$ (FORWARD).
4. **Standard Handle Dimensions**:
   - Grip cross-section: strictly $2 \times 2$ voxels ($0.03\text{m} \times 0.03\text{m}$).
   - Grip length: $6$–$8$ voxels ($0.09\text{m}$–$0.12\text{m}$) for one-handed/bastard swords; $10$–$14$ voxels for colossal greatswords.
5. **Zero-Manual-Tuning Guarantee**:
   - When any weapon following this standard is attached to a character's `Socket_Hand_R`, it mounts with identity transform `position = (0, 0, 0)` and `rotation = (0, 0, 0)` with zero manual sliders or offsets needed!

---

## 4. Game-Feel & Animation Juice Pipeline

Infuse all combat animations with gamedev "juice" and physical feedback:

### 4.1 5-Phase Hitbox State Machine
1. **Phase 1: Startup / Telegraph (15–25%)** — Wind-up, kinetic energy coiling, contrasting slow build.
2. **Phase 2: Active Hit Window (5–10%)** — Explosive acceleration (`t^3` easing), cutting edge leads the arc, geometric slash ribbons active.
3. **Phase 3: Overshoot (10–15%)** — Momentum carries past the contact point; energy trail reaches maximum expansion.
4. **Phase 4: Hit-Stop & Recoil Tremor (20–30%)** — Deceleration snap, 2–3 frame micro-tremor on the root/spine confirming physical impact.
5. **Phase 5: Recovery / Reset (25–35%)** — Graceful return to combat idle or walk loop.

### 4.2 Locomotion Walk Cycles
- **Asymmetrical Weight Shift**: For monsters/zombies, one foot steps confidently while the damaged/skeletal foot drags behind.
- **Loll & Sway**: Torso rolls $\pm 3^\circ$, head tilts loosely side-to-side, arms reach forward in a predatory search posture.

### 4.3 Quaternion SLERP Guard & In-Between Breakdown Keyframes
- In glTF and Three.js, rotation keyframes are interpolated using spherical linear interpolation (SLERP).
- If keyframes jump $>90^\circ$ (e.g. from wind-up behind the back to ground slam), SLERP takes the shortest arc across the front!
- **Mandatory Rule**: Always insert intermediate breakdown keyframes every 2–4 frames during fast attack arcs so the delta angle is $<45^\circ$.
- Always pass `export_bake_animation=True` in `bpy.ops.export_scene.gltf`.

### 4.4 Mandatory Filmstrip / Contact Sheet Animation Audit
- Never judge animations by a single still image!
- The animator must render an 8-frame filmstrip `attack_filmstrip.png` across key frames (`F0`, `F10`, `F20`, `F24`, `F27`, `F32`, `F40`, `F48`).
- The animator must call `view_file` on `attack_filmstrip.png` to visually audit that the limb/weapon trajectory winds up behind the back and strikes cleanly.

### 4.5 Ground Plane Invariant & Anti-Sinking Contract (Floor $Z \ge 0.0$)
- **Floor Collision Invariant**: The floor is located at $Z = 0.0$. Under NO circumstances may any foot, talon, or body part penetrate below the floor ($Z < -0.002\text{m}$).
- **Prohibition on Blind Root Dropping**: Animators must NEVER manually set `Root.location` to negative Z values (e.g. $-0.04\text{m}$) to fake a crouch or lunge. In FK skeletons, lowering the Root directly buries the feet into the ground.
- **Mandatory Automated Ground-Level Solver**: Every animation script (`anim_walk.py`, `anim_attack.py`) must execute an automated floor pass:
  ```python
  # Iterate all frames, calculate min_z of evaluated character mesh,
  # and offset Root so the lowest contact point rests exactly on Z = 0.0
  ```
- **Height Consistency Across Clips**: When switching clips in the web viewer (`Walk` -> `Attack`), the support foot must remain grounded at $Z = 0.0$. The character must NOT sink into the floor or jump in height.

### 4.6 Martial Arts Kinetic Chain & Dynamic Arc Exaggeration (Anti-Limp Pose Rule)
Never author limp, robotic, arm-only strikes! Combat strikes in Trove / anime biped style must express overwhelming martial power through the entire kinetic chain:
1. **Whole-Body Torque & Power Stance**:
   - **Hips / Pelvis**: Must rotate $\ge 30^\circ$–$45^\circ$ on yaw during wind-up, dropping into a deep athletic coil, then violently whip $\ge 60^\circ$–$80^\circ$ forward on the strike.
   - **Spine / Chest**: Must twist $\ge 35^\circ$–$50^\circ$ during wind-up, coiling the shoulder backward, and snap forward with forward lean $\ge 15^\circ$–$25^\circ$.
   - **Legs**: Left foot lunges forward, right leg drives off the ground from the toes.
2. **Lead Arm Arc & Elevation**:
   - On wind-up, the striking shoulder must elevate $90^\circ$–$125^\circ$ (raising the weapon high above/behind the shoulder or head).
   - On the strike, the arm sweeps a massive, unmistakable $120^\circ$–$160^\circ$ diagonal/horizontal cleave arc across the entire front hemisphere.
3. **Offhand Active Choreography**:
   - The offhand (left arm) must **NEVER dangle limp or float passively**!
   - For two-handed styles: Left hand moves in sync toward the lower hilt.
   - For one-handed styles: Left arm flings backward and outward in an athletic martial counter-balance.
4. **Head Target Lock**:
   - The head must counter-rotate to maintain visual lock on the target in front, instead of blindly rotating with the shoulders.
5. **Filmstrip Visual Gate**:
   - In `attack_filmstrip.png`, the 8 frames must clearly demonstrate high-contrast silhouette shifts. If the limb or torso barely moves or looks like a static figurine twitching, the animator MUST reject it and re-key with greater angular magnitude.

### 4.7 Zero-Clipping & Anatomical Clearance Guard (Anti-Torso-Penetration Contract)
- **Zero Mesh Self-Intersection**: Under NO circumstances may arms, pauldrons, hands, or held weapons penetrate into the torso, pelvis, legs, or head.
- **Forward & Lateral Shoulder Clearance**:
  * When sweeping the main arm across the body (e.g. diagonal cleave or cross-body guard), the animator must elevate and project the arm forward in front of the chest plane ($Y_{\text{arm}} > Y_{\text{chest}}$), preventing the upper arm / pauldron box from embedding into the ribcage or breastplate.
  * When flinging the offhand backward for counter-balance, maintain lateral clearance ($X$ offset outside the hips/ribs) so the forearm and hand do not intersect the flanks or legs.
- **Filmstrip Intersection Audit**: During the mandatory 8-frame filmstrip audit (`attack_filmstrip.png`), the animator MUST visually inspect all poses specifically for torso/arm penetration. Any clipping is an automatic rejection requiring pose refinement.

---

## 5. Zombie & Gore Generation Blueprint

When authoring Zombie and Undead variants:

### 5.1 Color & Shader Architecture
- **Fresh Arterial Blood (`M_BloodFresh`)**: Deep crimson `(0.40, 0.015, 0.02, 1.0)`, glossy `roughness=0.22`, `metallic=0.10`.
- **Coagulated Dark Blood (`M_BloodDark`)**: Maroon/rust-black `(0.12, 0.015, 0.015, 1.0)`, `roughness=0.65`, `metallic=0.05`.
- **Rotting Flesh (`M_FleshGreen`, `M_FleshDark`)**: Olive/gangrene tones with subtle contrast.
- **Exposed Bone (`M_DecayedBone`, `M_BoneHighlight`)**: Weathered ivory and sharp bone tips.
- **Bloodlust Glow (`M_EyeGlow`)**: Intense crimson/amber emission (`emission=2.2`, AgX safe).
- **Gore Slash Trails (`M_BloodSlashTrail`, `M_BloodSlashCore`)**: Ruby/crimson geometric voxel ribbons spawning behind claw tips.

### 5.2 Geometric Detailing
- Asymmetrical cranium: exposed skull on one side, rotting scalp with hair on the other.
- Protruding broken ribs drenched in fresh blood droplets.
- Asymmetrical limbs: one bare skeletal arm with talons, one muscular rotting arm with dripping gore.

---

## 6. Modern React Viewer & Zero-Slop Architecture (`/api/assets`)

- The legacy 1000-line monolithic `index.html` is completely abolished.
- The viewer is powered by **React 18 + TypeScript + Vite** on port 8080.
- **Dynamic Auto-Scanning**: Vite middleware `/api/assets` automatically scans `assets/` on disk. Any new asset placed in `assets/<name>/` appears instantly in the sidebar with stats, thumbnails, and clip switchers (`Walk`, `Attack`).
- **Zero manual edits to `index.html`!** Modifying `index.html` during asset authoring is strictly prohibited.
- **Turntable Auto-Rotation is Permanently Disabled**: `controls.autoRotate = false`.
- **Zero AI Slop**: Dark high-density CAD interface, no glowing purple gradients, no emoji spam, no badge spam.

---

## 7. The `/createAsset` Two-Subagent Production Pipeline

When the user enters `/createAsset <prompt>` (or asks to create a new character, monster, or weapon), the orchestrator agent **must immediately delegate** to the two-subagent pipeline:

1. **Stage 1: Launch Subagent 1 (Voxel Modeler)**:
   - Role: `Voxel Modeler` (`voxel-artisan`).
   - Prompt: Reads `skills/trove-voxel-artisan`, authors `assets/<name>/model.py`, saves `assets/<name>/<name>.blend`, renders `model_preview.png`, and verifies rest-pose silhouette with `view_file`.
2. **Stage 2: Launch Subagent 2 (Combat Animator)**:
   - Role: `Combat Technical Animator`.
   - Prompt: Reads `skills/trove-voxel-artisan` and `blender-motion-state-inspection`, takes `<name>.blend`, authors `anim_walk.py` and `anim_attack.py` with dense keyframes, renders `attack_filmstrip.png`, verifies the trajectory via `view_file`, and exports `<name>.glb`, `<name>_render.png`, and `<name>_data.js`.
3. **Stage 3: Parent Delivery**:
   - Audits `<name>_render.png` with `view_file`.
   - Verifies the model and animations live in `http://localhost:8080/`.
   - Reports to the user in Russian with technical breakdown.

