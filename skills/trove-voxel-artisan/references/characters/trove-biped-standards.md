# Trove Modular Biped Standard: Anatomy, Sockets & Micro-Voxel Styling

Use this authoritative reference whenever authoring any Playable Character, Undead, Knight, Monster, or Boss in authentic **Trove / Cube World** style.

---

## 1. Aesthetic Core: Why Trove is NOT Minecraft

| Feature | Minecraft (What to Avoid) | Trove Authentic Style (What to Build) |
| :--- | :--- | :--- |
| **Limbs** | Continuous solid rectangular boxes | **Segmented & Floating Limbs**: Hands, boots, and pauldrons are distinct voxel masses with visible breathing gaps / ball joints. |
| **Silhouette** | Flat untextured 6-sided cuboids | **Multi-layered Micro-Voxel Extrusions**: Hair strands, horns, visors, teeth, ribs, buckles protrude by 1–3 voxel steps. |
| **Proportions** | 1:8 realistic or 1:4 tall box | **Stylized Chibi Biped**: Large expressive head, compact armored torso, oversized gauntlets and sabatons. |
| **Joint Deformations** | Stretched rubbery texture at elbows | **Rigid Segment Rotation**: Individual voxel clusters rotate on their respective bones with zero skin stretching. |

---

## 2. Standard Chibi Dimensions (`VOXEL_SIZE = 0.015m`)

All dimensions are in integer voxel units ($1 \text{ voxel} = 0.015\text{m} = 1.5\text{cm}$):

```
Total Height: 32–36 voxels (~0.48m – 0.54m)

             [ 10 x 10 x 10 Head Base ]  + Layered Hair/Horn steps
                     | (gap: 1v)
[Pauldron L]     [ 8 x 6 x 8 Chest ]     [Pauldron R]
(floating)           | (gap: 1v)         (floating)
                 [ 8 x 6 x 3 Pelvis ]
   [Arm Link]                            [Arm Link]
       | (gap: 1v)                           | (gap: 1v)
[Glove/Hand L]                         [Glove/Hand R]
(floating 4x4x4)                       (floating 4x4x4 + Socket_Hand_R)

   [Leg Link]                            [Leg Link]
       | (gap: 1v)                           | (gap: 1v)
 [Boot/Foot L]                         [Boot/Foot R]
 (floating 4x6x4)                      (floating 4x6x4)
```

### Detailed Component Anatomy:
1. **Head (`Neck` / `Head` bone)**:
   - **Base Cranium**: $10 \times 10 \times 10$ voxels.
   - **Face (front $+Y$)**: Sunken or emissive eyes ($2 \times 2$ or $1 \times 2$), snout/mouth/fangs.
   - **Layered Relief**: Hair tufts, bangs, helmets, crowns, or skull cracks MUST extrude $+1$ or $+2$ voxels beyond the $10 \times 10$ base!
2. **Torso (`Spine` / `Chest` bone)**:
   - $8$ voxels wide ($X$), $6$ voxels deep ($Y$), $8$ voxels high ($Z$).
   - Ribs, vest seams, emblems, belts with buckles extruded by 1 voxel.
3. **Pauldrons (`Shoulder.L` / `Shoulder.R`)**:
   - Detached floating armor blocks ($4 \times 5 \times 3$ to $5 \times 6 \times 4$), floating $1$ voxel away from the chest.
4. **Hands & Gloves (`Hand.L` / `Hand.R`)**:
   - Detached chunky voxel blocks ($4 \times 4 \times 4$ or $4 \times 4 \times 5$) floating slightly below the arm bone.
   - Right hand houses `Socket_Hand_R` at its inner palm center.
5. **Pelvis & Legs (`Hips`, `UpperLeg`, `LowerLeg`, `Foot`)**:
   - Pelvis: $8 \times 6 \times 3$ voxels.
   - Upper/Lower legs: thin leg struts or segmented knee links ($2 \times 2$ voxels).
   - Boots / Sabatons / Skeletal feet: Chunky voxel blocks ($4$ wide $\times 6$ long $\times 4$ high), floating with a $1$ voxel joint clearance from the calf.

---

## 3. Game-Ready Socket Architecture

The armature hierarchy MUST include empty socket bones (or locators) so any weapon or equipment snaps on automatically:

```
Root (0, 0, 0)
 └── Hips (0, 0, Z_hips)
      ├── Spine -> Chest -> Neck -> Head
      │                      │        ├── Socket_Head (top center of head: for hats/helmets)
      │                      └── Socket_Back (upper spine rear: for wings/capes/sheaths)
      ├── Shoulder.L -> UpperArm.L -> Forearm.L -> Hand.L
      │                                              └── Socket_Hand_L (shield/bow grip)
      ├── Shoulder.R -> UpperArm.R -> Forearm.R -> Hand.R
      │                                              └── Socket_Hand_R (weapon handle grip)
      ├── UpperLeg.L -> LowerLeg.L -> Foot.L
      └── UpperLeg.R -> LowerLeg.R -> Foot.R
```

---

## 4. Animation Conventions

- **Locomotion (Frames 1–40)**:
  - Bouncy, toy-like gait.
  - Floating hands sway naturally with slight wrist pitch.
  - Because segments are detached, they never pinch or distort during deep bends!
- **Combat Strike (Frames 41–80)**:
  - Follow the 5-Phase Hitbox Rule (Telegraph $\to$ Hit $\to$ Overshoot $\to$ Zanshin $\to$ Recovery).
  - Claws or held weapons lead the strike with dynamic geometric VFX ribbons.
