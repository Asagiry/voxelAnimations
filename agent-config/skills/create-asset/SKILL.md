---
name: create-asset
description: Create a new procedural Trove-style voxel character, creature, prop, or weapon as a modular Blender and glTF package. Use for new assets, not for inspecting or repairing an existing asset.
argument-hint: "<asset description>"
---

# Create Voxel Asset

Use the project workflow in [`../../workflows/create-asset.md`](../../workflows/create-asset.md). It is the only orchestration contract for this skill.

## Scope

- Create a new package only in `assets/<asset_name>/`.
- Do not inspect existing folders in `assets/` and do not edit `index.html`.
- Keep geometry, animation, and export in `model.py`, `anim_walk.py`, and `anim_attack.py`; do not combine them into one script.
- Treat `model_preview.png` and `attack_filmstrip.png` as temporary QA evidence. Inspect them with an available image viewer, then remove them before delivery.

## Handover

1. The Voxel Modeler follows `trove-voxel-artisan` and delivers a rest-pose `.blend`.
2. The Combat Animator starts only after the model-stage validator passes.
3. The QA role runs the final validator and visually checks the beauty render and filmstrip.

Stop after two failed repair attempts for the same validation error and report the evidence instead of masking it.

## Definition of done

The final package contains exactly `model.py`, `anim_walk.py`, `anim_attack.py`, `build.py`, `<name>.blend`, `<name>.glb`, `<name>_render.png`, and `<name>_data.js`; the GLB exposes `Walk` and `Attack`.
