# Archetype Reference: Humanoids, Undead & Monster Characters

Use this reference whenever authoring any Humanoid Character, Undead Zombie, Skeleton Warrior, Armored Knight, or Monster in Trove/Cube World micro-voxel style.

---

## 1. Anatomy & Voxel Proportions

* **Voxel Scale**:
  - `VOXEL_SIZE = 0.012` to `0.015` meters.
  - Standard Humanoid Height: 36–48 voxels tall (~1.4m – 1.8m).
* **Body Component Proportions**:
  - **Head**: 8×8×8 to 10×10×10 voxels. Stylized retro proportions (slightly larger head-to-body ratio: 1:4 to 1:5).
  - **Torso / Spine**: 8–12 voxels wide, 4–6 voxels deep, 12–16 voxels high.
  - **Arms**: Upper arm (8–10 voxels) + Forearm (8–10 voxels) + Hand/Claws (4–6 voxels). Cross section: 2×2 to 3×3 voxels.
  - **Legs**: Thigh (8–12 voxels) + Calf/Shin (8–10 voxels) + Boot/Foot (3–5 voxels high, 6–8 voxels long forward).
* **Asymmetrical Decay & Characterization**:
  - Avoid perfect bilateral symmetry on monsters/zombies:
    * One arm skeletal bone (`#c2bba8`), the other rotting muscle/flesh (`#4a6b48`).
    * Exposed ribcage on one side; torn tattered tunic on the other.
    * Glowing mismatched eyes (sunken yellow-green, emissive intensity 1.8).
    * Combat boot on one leg; bare skeletal tarsals on the other.

---

## 2. Rigging & Bone Hierarchy (Humanoid Armature)

Rooted at the origin $(0, 0, 0)$ in rest pose:

```
Root (0, 0, 0)
 └── Hips / Pelvis
      ├── Spine -> Chest -> Neck -> Head
      ├── Shoulder.L -> UpperArm.L -> Forearm.L -> Hand.L
      ├── Shoulder.R -> UpperArm.R -> Forearm.R -> Hand.R
      ├── UpperLeg.L -> LowerLeg.L -> Foot.L
      └── UpperLeg.R -> LowerLeg.R -> Foot.R
```

### Blender Bone Rotation Conventions:
- **Limbs pointing downward (Head at top, Tail at bottom)**:
  - Bone local $+Y$ points downward (from head to tail).
  - Positive local $X$ rotation (`rot_x > 0`) swings limbs **forward** ($+Y$ in world coordinates).
  - Negative local $X$ rotation (`rot_x < 0`) swings limbs **backward** ($-Y$ in world coordinates).
- **Spine & Neck pointing upward**:
  - Negative local $X$ rotation (`rot_x < 0`) hunches the character **forward**.
  - Positive local $X$ rotation (`rot_x > 0`) arches the character **backward**.
- **Always declare** `pbone.rotation_mode = 'XYZ'` before keyframing Euler angles.

---

## 3. Combat & Locomotion Animation Choreography

### Phase A: Locomotion / Shambling Walk Cycle (Frames 1–40)
- **Asymmetrical Weight Shift**:
  - A limping creature drags one leg behind: the healthy/booted foot steps with confidence; the skeletal foot drags along the ground with delayed recovery.
  - Pelvis sways slightly left-to-right ($\pm 3^\circ$ roll).
  - Spine hunches forward, with head tilting loosely side-to-side in a zombie loll.
  - Arms reach forward in a predatory search posture, swaying with subtle high-frequency wrist tremors.
  - Loop seamless: Frame 40 matches Frame 1.

### Phase B: Predatory Attack Strike (Frames 41–80)
Follows the Gamedev 5-Phase Hitbox Rule:
```
[Telegraph / Wind-up] (Frames 41–52)
    └── Spine coils low into a crouch; jaw unhinges; claws raise overhead into an apex threat posture.
[Active Hit Window] (Frames 53–58)
    └── Explosive forward lunge! Torso snaps forward; claws slash downward across the target zone at maximum velocity.
    └── Geometric slash ribbons spawn behind the claws along the cutting arc.
[Overshoot] (Frames 59–64)
    └── Inertia carries the lunging mass low past the impact plane; slash ribbons reach apex expansion.
[Zanshin / Impact Hold] (Frames 65–72)
    └── Rigid impact lock; subtle body shudder absorbing kinetic rebound while claw ribbons fade.
[Recovery / Reset] (Frames 73–80)
    └── Stumbling, uncoordinated recovery step resetting posture back into the shambling walk ready state.
```

---

## 4. Visual Verification & Camera Framing for Characters

- **Character Scale**: Adjust camera distance so the humanoid figure occupies **60%–80%** of the canvas vertically.
- **Camera Elevation**: Elevate the camera at a **35°–45° diagonal angle** to clearly reveal the 3D depth of the hunched back, stepping feet, and forward-reaching claw strikes.
- **Dynamic Depsgraph Target**: Center the camera target on the character's animated chest/spine at the peak impact frame.
