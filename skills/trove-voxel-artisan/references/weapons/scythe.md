# Archetype Reference: Scythes & Reaping Weapons

Use this reference whenever authoring any Scythe, Astral Void Reaper, Death Scythe, War Kama, or Sickle in Trove/Cube World micro-voxel style.

---

## 1. Anatomy & Voxel Proportions

* **Shaft (Haft)**:
  - Length: 70–95 voxels long (~0.85m – 1.15m).
  - Cross-section: 2×2 to 3×3 voxels thick. Obsidian stone, dark Damascus steel, or petrified runic wood.
  - Detail: Segmented metal brackets, leather or silk grip wraps, and an ornate pommel/counterweight.
* **Socket / Nexus (Shaft-to-Blade Joint)**:
  - Reinforced mounting block (4×4 to 6×6 voxels) located at 65–75% height.
  - Ideal focal point for magical cores: a hovering void eye crystal, glowing skull, planetary gem, or armillary gyro-ring sockets.
* **Crescent Blade (The Signature Silhouette)**:
  - Length: 50–75 voxels long; width: 8–18 voxels at the belly curve.
  - Volumetric depth: 3–5 voxels thick at the spine, stepping down to a razor-sharp 1-voxel edge.
  - **CRITICAL ANATOMICAL RULE**: The **inner crook** (the concave inner curve) is the sharp cutting edge; the outer spine is heavy, thick, and protective.
* **Orbitals & Accents**:
  - Floating concentric runic rings, celestial spark orbits, or smoky aura ribbons. Keep them framing the weapon without obscuring the solid voxel geometry.

---

## 2. Combat Physics & Animation Choreography: The Lateral Reaping Slash

> **CRITICAL DIRECTIVE ON SCYTHE MOTION:**
> **A SCYTHE IS NEVER A HELICOPTER ROTOR OR CEILING FAN!**
> Never animate the root bone in a continuous 360° or 720° flat axial spin. It destroys the weapon's identity, looks comical, and ignores physical weight.

A true scythe strike is a **Devastating Lateral Reaping Harvest (Боковой покос)**:

```
[Phase 1: Majestic Hover / Idle] (Frames 1–12)
    └── Weapon floats at a regal, ready angle (slight natural tilt: ~15° yaw, ~10° pitch).
    └── Runic rings and floating crystals orbit smoothly on their own axes, emitting a low astral hum.

[Phase 2: High Wind-up & Energy Coil] (Frames 13–22)
    └── The wielder pulls the scythe back high and to the side (yaw rotates +50° to +65°).
    └── The shaft tilts back; the inner cutting crook of the blade rises high, directly facing the target swath.
    └── Vacuum energy concentrates in the core; particles draw inward.

[Phase 3: Explosive Reaping Slash] (Frames 23–28)
    └── Violent, broad horizontal swath cutting across the front: yaw sweeps from +65° to -85° (a massive 150° arc!).
    └── THE INNER CURVED BLADE LEADS THE MOTION, slicing horizontally through space.
    └── VFX Behavior: The astral crescent trail / vortex ribbon must erupt directly BEHIND the cutting edge, trailing its curved sweep like an astral wake.

[Phase 4: Zanshin Lock & Kinetic Recoil] (Frames 29–36)
    └── Instantaneous deceleration snap at -85° yaw with a subtle micro-recoil tremor, conveying the immense kinetic momentum of the obsidian blade.
    └── The detached crescent energy wave bursts forward and dissipates.

[Phase 5: Noto Recovery] (Frames 37–60)
    └── A deliberate, graceful arc returning the weapon back across center into the initial ready posture.
    └── Orbital rings decelerate back to their serene idle hum. Seamless 60-frame loop.
```

---

## 3. Creative Freedom Guidelines

You have complete artistic license to design:
- The silhouette: slender graceful crescent vs. menacing jagged void scythe with spinal thorns.
- The energy palette: electric cyan plasma, deep astral violet, infernal soul flame, or necrotic green.
- The ring mechanics: single gyro-ring, triple planetary armillary orbits, or floating rune glyphs.
- Just adhere strictly to the combat kinematics: **Idle Hover -> High Wind-up Back -> Violent Horizontal Reaping Slash (Blade Leading) -> Deceleration Lock -> Graceful Return**.
