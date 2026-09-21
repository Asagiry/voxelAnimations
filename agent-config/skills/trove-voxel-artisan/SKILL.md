---
name: trove-voxel-artisan
description: Model and rig a new Trove/Cube World-style micro-voxel character, creature, weapon, or prop in Blender 4.2+. Use during the modeling stage of a new asset; use the combat-animation role for walk, attack, rendering, and GLB export.
argument-hint: "asset brief"
---

# Trove Voxel Artisan

Create a bold, game-ready voxel silhouette with a clean rest pose and modular rig. Preserve artistic freedom while enforcing the contracts below.

## Before modeling

1. Convert the request into the fields in [the asset-brief contract](references/asset-brief.md). Infer a sensible default only when a field is absent; do not invent a named franchise character.
2. Read [Blender and export rules](references/blender-gamedev-practices.md).
3. Read exactly one archetype guide:
   - Characters, monsters, undead: [character standard](references/characters/trove-biped-standards.md); add [undead details](references/characters/humanoid-undead.md) only for undead.
   - Weapons: the matching file in [references/weapons](references/weapons/).
4. For any equipable asset, read [socket and gear standards](references/sockets-and-gear-standards.md).

## Model-stage contract

- Use `VOXEL_SIZE = 0.015` metres. A chibi biped is 32–36 voxels tall (0.48–0.54 m); do not use human-scale metre estimates.
- Generate one efficient mesh from exposed voxel faces. Do not create thousands of individual cube objects.
- Use flat-shaded Principled BSDF materials and a focused 4–6-colour palette.
- The asset object origin is at world `(0, 0, 0)` in rest pose. Vertices retain their normal local coordinates; never collapse every vertex to the origin.
- Characters use detached hands, boots, and pauldrons with one-voxel gaps. Playable classes have empty gripping hands and all four standard sockets.
- A standalone weapon has its grip centre at local `(0, 0, 0)`, length along local `+Z`, and cutting/front direction along local `+Y`.
- Create `model.py`, save `<name>.blend`, render `model_preview.png`, and inspect it with an available image viewer.

## Boundaries

- Do not inspect or copy any existing `assets/` package.
- Do not author walk/attack/export code here; hand the `.blend` to the Combat Animator.
- Do not use procedural particles, smoke, or volume shaders for VFX intended for GLB. Use polygonal ribbons, shards, or rings.
