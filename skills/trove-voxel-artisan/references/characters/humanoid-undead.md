# Archetype Reference: Humanoids, Undead & Monster Characters

Use this authoritative reference whenever authoring any Humanoid Character, Undead Zombie, Skeleton Warrior, Armored Knight, or Monster in Trove/Cube World micro-voxel style.

---

## 1. Anatomy & Voxel Proportions (Trove Chibi Biped Standard)

* **Global Grid**: `VOXEL_SIZE = 0.015m` (1.5 cm per voxel).
* **Total Height**: 32–36 voxels tall (~0.48m – 0.54m).
* **Component Proportions**:
  - **Head**: $10 \times 10 \times 10$ voxels base. Stylized chibi ratio (large expressive head).
  - **Torso**: $8$ wide $\times 6$ deep $\times 8$ high (Chest) + $8 \times 6 \times 3$ (Pelvis).
  - **Arms**: Upper arm (2×2, 5 voxels high) + Forearm (2×2, 5 voxels high) + Hand/Claw (4×4×4 detached block).
  - **Legs**: Thigh (2×2, 4 voxels high) + Calf/Shin (2×2, 4 voxels high) + Boot/Foot (4 wide $\times 6$ long $\times 4$ high).
* **Segmented & Floating Limbs**:
  - **Never create solid noodle limbs**.
  - Hands/claws, boots, and pauldrons must have a visible **1-voxel breathing detachment gap** from connecting limbs to avoid mesh pinching during deep bends and preserve the authentic toy-like retro look.
* **Asymmetrical Decay & Characterization**:
  - Never generate a symmetrically boring monster:
    * One arm skeletal bone with exposed joints; the other rotting muscle/flesh with blood-stained wraps.
    * Exposed ribcage on one side protruding $+1$ or $+2$ voxels forward; torn tunic on the other.
    * Glowing mismatched eyes (one gouged or dried socket, one burning with necromantic or bloodlust glow).
    * Combat boot on one leg; bare skeletal clawed foot on the other.

---

## 2. Archetypal Variations & Shader Palettes

### 2.1 Necrotic / Toxic Zombie (`assets/zombie/`)
- **Flesh**: Rotting olive gangrene `M_FleshGreen` `(0.075, 0.160, 0.068)`, dark shadow `M_FleshDark` `(0.040, 0.088, 0.038)`.
- **Bone**: Weathered ivory `M_DecayedBone` `(0.58, 0.54, 0.44)`, tooth highlights `M_BoneHighlight` `(0.74, 0.70, 0.60)`.
- **Emission**: Sickly toxic yellow-green eye glow `M_EyeGlow` `(0.48, 0.85, 0.02, 1.0)`, `emission=2.2`.
- **Attack Trails**: Toxic lime-green curved geometric ribbons `M_SlashTrail` & `M_SlashCore` (`emission=2.2 - 2.8`).
- **Rim Lighting**: Sickly lime-green point light (`0x84cc16`).

### 2.2 Gore / Berserker Zombie (`assets/bloody_zombie/`)
- **Fresh Arterial Blood**: Wet glossy crimson `M_BloodFresh` `(0.42, 0.012, 0.02, 1.0)`, `roughness=0.18 - 0.22`, `metallic=0.10`.
- **Coagulated Dark Blood**: Maroon/rust crust `M_BloodDark` `(0.10, 0.008, 0.012, 1.0)`, `roughness=0.65`.
- **Blood-Stained Bone**: Saturated red-tinged ivory `M_BoneBlood` `(0.45, 0.035, 0.035, 1.0)`.
- **Emission**: Bloodlust glowing eye `M_EyeBloodlust` `(0.95, 0.08, 0.02, 1.0)`, `emission=2.4` (AgX safe).
- **Attack Trails**: Volumetric ruby/crimson geometric blood ribbons `M_BloodSlashTrail` & `M_BloodSlashCore` (`emission=2.2 - 2.8`).
- **Rim Lighting**: Deep crimson red point light (`0xef4444` / `0x991b1b`).

---

## 3. Rigging & Bone Hierarchy (Humanoid Armature)

Rooted at the origin $(0, 0, 0)$ in rest pose with standard equipment sockets:

```
Root (0, 0, 0)
 └── Hips (0, 0, 14v)
      ├── Spine (0, 0, 16v) -> Chest (0, 0, 20v) -> Neck (0, 0, 24v) -> Head (0, 0, 26v)
      │                                             ├── Socket_Head (0, 0, 36v)
      │                                             └── Socket_Back (0, -4v, 23v)
      ├── Shoulder.L -> UpperArm.L -> Forearm.L -> Hand.L
      │                                              ├── Socket_Hand_L (palm)
      │                                              └── ClawTrail.L (VFX ribbon bone)
      ├── Shoulder.R -> UpperArm.R -> Forearm.R -> Hand.R
      │                                              ├── Socket_Hand_R (palm)
      │                                              └── ClawTrail.R (VFX ribbon bone)
      ├── UpperLeg.L -> LowerLeg.L -> Foot.L
      └── UpperLeg.R -> LowerLeg.R -> Foot.R
```

### Bone Rotation Conventions:
- **Down-pointing limbs (arms/legs)**: Local $+Y$ points downward (head to tail). Local $+X$ swings forward; local $-X$ swings backward.
- **Up-pointing spine & neck**: Local $+Y$ points upward. Local $-X$ hunches forward; local $+X$ arches backward.
- **Always declare** `pbone.rotation_mode = 'XYZ'` before setting keyframes.

---

## 4. Combat & Locomotion Choreography with Game-Feel Juice (80 frames @ 30fps)

Every character animation combines authentic locomotion and punchy 5-phase combat:

### Phase A: Shambling Walk Loop (Frames 1–40)
- **Asymmetrical Weight Shift**: Booted foot steps firmly; damaged/skeletal foot drags behind with delayed pickup.
- **Sway & Loll**: Pelvis rolls $\pm 3^\circ$, spine sways side-to-side, head spasms and tilts loosely in a predatory search posture.
- **Claws Search**: Arms reach forward with high-frequency micro-tremors on wrists.
- **Seamless Loop**: Frame 40 transforms smoothly into Frame 1.

### Phase B: 5-Phase Predatory Strike (Frames 41–80)
1. **Telegraph / Coiling Wind-up (Frames 41–52)**:
   - Deep crouch into `Root`, torso arched back, jaw unhinged, claws raised high in an apex threat posture.
2. **Active Hit Window (Frames 53–58)**:
   - Explosive acceleration ($t^3$ ease-in) lunging forward $+0.22$m into the strike plane.
   - Twin claws slash downward across the target zone; curved geometric slash ribbons expand behind the claws.
3. **Overshoot & Trail Dissolve (Frames 59–64)**:
   - Momentum carries the body past the contact point; slash ribbons dissolve (`scale -> 0`).
4. **Hit-Stop & Recoil Trauma (Frames 65–72)**:
   - 2–3 frame impact freeze at maximum extension.
   - High-frequency micro-tremor on `Root` and `Chest` simulating physical kinetic deceleration.
5. **Recovery / Settle (Frames 73–80)**:
   - Stumbling recovery step returning posture back into Frame 1.

---

## 5. Visual Verification & Camera Framing

- **Scale**: Character occupies **65%–75%** of the canvas vertically in 1024x1024 square render.
- **Camera Elevation**: Elevated at **35°–45°** diagonally in front (`+Y` world space) to show 3D depth of face, stepping feet, and forward claw arcs.
- **Depsgraph Bounding Box**: Evaluated at peak impact frame (Frame 56) to ensure no attack ribbons or extended limbs are cropped.
