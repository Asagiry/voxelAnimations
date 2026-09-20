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
   - The grip handle must be modeled with a thickness of **$2 \times 2$ or $3 \times 3$ voxels** ($3.0\text{cm}$ to $4.5\text{cm}$).
2. **Handle Origin & Pivot**:
   - The origin $(0, 0, 0)$ of the weapon mesh in rest pose MUST be placed **at the center of the grip handle** where the character's hand wraps around it.
   - The weapon shaft points along local $+Z$ (or local $+Y$ longitudinal axis).
   - The cutting edge points forward (towards world $+Y$).
3. **Attachment via Socket**:
   - In the character rig, the bone `Socket_Hand_R` is placed inside the cavity of the right gauntlet/hand.
   - When parenting or copying transforms from `Socket_Hand_R`, the weapon snaps with $(0, 0, 0)$ offset and zero rotation discrepancy.

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
