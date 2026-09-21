# Cross-Asset Equipment & Socket Standards

This document defines the strict kinematic and dimensional contract guaranteeing that **any weapon, helmet, or accessory fits any character** authored in the Trove Voxel ecosystem.

---

## 1. Global Calibration Constants

* **World Scale**: `VOXEL_SIZE = 0.015m` (1 voxel = 1.5 cm).
* **Rest Pose Orientation**: Character faces world $+Y$, up is world $+Z$.
* **Coordinate System for glTF Export**: Export with `export_yup=True` (Blender $+Z \to$ Three.js $+Y$, Blender $+Y \to$ Three.js $+Z$).

---

## 2. Weapon Grip Standard (`Socket_Hand_R` & `Socket_Hand_L`)

To ensure that any weapon (sword, scythe, katana, bow, staff) cleanly sits in a character's hand without clipping or floating:

1. **Grip Cross-Section**:
   - The grip handle must be modeled with a thickness of strictly **$2 \times 2$ voxels** ($3.0\text{cm} \times 3.0\text{cm}$).
2. **Handle Origin & Alignment Standard**:
   - The origin $(0, 0, 0)$ of the weapon mesh in rest pose MUST be placed **strictly at the center of the grip handle** where the character's hand wraps around it.
   - **Strict Orientation**:
     * In Blender: The blade/shaft points strictly along **World $+Z$ (UP)**. Hilt and pommel extend along $-Z$ (DOWN). The cutting edge / blade front faces **World $+Y$ (FORWARD)**. Crossguard/quillons extend along $X$ (LEFT/RIGHT).
     * In glTF export (`export_yup=True`): Blade points along $+Y$ (UP in Three.js/game engines), and cutting edge faces $+Z$ (FORWARD).
   - **Pure Static Mesh**: Zero animations, zero armatures, zero display plinths or pedestals.
3. **Attachment via Socket**:
   - In the character rig, the bone `Socket_Hand_R` is placed inside the cavity of the right gauntlet/hand.
   - When parenting the weapon to `Socket_Hand_R`, it mounts with identity transform `(0, 0, 0)` offset and zero rotation discrepancy. Zero manual sliders needed!

---

## 3. Headgear & Helmet Standard (`Socket_Head`)

1. **Internal Clearance**:
   - All standard Trove character heads have a $10 \times 10 \times 10$ voxel base cranium.
   - Any helmet, hat, crown, or visor must have an **internal hollow cavity of at least $10 \times 10 \times 10$ voxels** so that it fits over the skull without intersecting the face or ears.
2. **Anchor Location**:
   - `Socket_Head` is located at the top-center vertex of the cranium $(0, 0, Z_{\text{head\_top}})$.
   - Hats and helms have their root anchor at their inner crown ceiling $(0, 0, 0)$.

---

## 4. Back Equipment Standard (`Socket_Back`)

1. **Accessories**: Wings, capes, quivers, and sheaths.
2. **Anchor Location**:
   - `Socket_Back` is located on the rear surface of the chest bone at $(0, -Y_{\text{chest\_back}}, Z_{\text{mid\_spine}})$.
   - Accessories mount flush against the rear chest armor.
