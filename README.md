# Voxel Animations & 3D Combat Assets

Interactive 3D Micro-Voxel Weapon & Combat Animation Gallery in authentic Trove / Cube World / Astra 6 aesthetic, generated procedurally with Blender 4.2+ and viewable directly in the browser.

---

## 🎮 Quick Start (Interactive Web Preview)

Start a local HTTP server and open `index.html`:

```powershell
python -m http.server 8080
```

Then navigate to: `http://localhost:8080/index.html`

### Features:
- **Zero-CORS standalone loading**: Models are pre-encoded in Base64 `_data.js` scripts, functioning seamlessly without external CORS restrictions.
- **Interactive 3D Viewport**: Orbit controls (360° rotation, pan, zoom into individual micro-voxels).
- **Animation Controls**: Action trigger, playback speed selector (0.25x, 0.5x, 1.0x, 1.5x), play/pause, auto-rotation toggle, and dynamic lighting.

---

## ⚔️ Included 3D Assets (`assets/`)

| Asset | Archetype | Combat Animation | Source / Model |
|---|---|---|---|
| **Astral Void Scythe** | Scythe / Reaper | 5-Phase Reaping Harvest (*Боковой покос*) | Gemini 3.7 Flash |
| **Astral Void Scythe (3.8)** | Scythe / Reaper | Orbital Gyro-Vortex Spin | Gemini 3.8 Flash High |
| **Astral Void Scythe (Sonnet)** | Scythe / Reaper | Dual Gyro-Ring Harvest | Claude Sonnet 4.6 |
| **Astral Void Scythe (Opus)** | Scythe / Reaper | Concentric Astral Rings | Claude Opus 4.6 |
| **Astral Void Scythe (3.6)** | Scythe / Reaper | Celestial Void Slash | Gemini 3.6 Flash |
| **Astral Void Scythe (Pro)** | Scythe / Reaper | Obsidian Core Slash | Gemini 3.1 Pro |
| **Iaido Crescent Katana** | Katana / Iaido | Supersonic Crescent Slash & Zanshin | Gemini 3.7 Flash |
| **Iaido Razor Katana** | Katana / Iaido | 5-Phase Iaido Draw, Chiburui & Noto | Gemini 3.8 Flash High |
| **Tamahagane Katana** | Katana / Iaido | Classic Stance & Thrust | Gemini 3.1 Pro |
| **Dragon Slayer** | Colossal Greatsword | Ground-Shattering Gravitational Slam | Gemini 3.7 Flash |
| **Infernal Flame Sword** | Greatsword / Elemental | Living Volcanic Plasma Surge | Voxel Artisan |
| **Celestial Magic Bow** | Bow / Ranged | Elastic Draw Tension & Supersonic Release | Voxel Artisan |

Each asset directory contains:
- `<asset>.blend` — Source Blender 4.2 project file.
- `<asset>.glb` — Game-ready glTF 2.0 binary with baked skeletal animation.
- `<asset>_render.png` — Cycles AgX beauty render.
- `build_<asset>.py` — Deterministic procedural generation script.
- `<asset>_data.js` — Embedded Base64 binary for web playback.

---

## 🛠️ The Trove Voxel Artisan Skill (`skills/trove-voxel-artisan/`)

This repository includes the complete autonomous agent skill configuration under [`skills/trove-voxel-artisan/`](skills/trove-voxel-artisan/):

- **Main Dispatcher**: [`SKILL.md`](skills/trove-voxel-artisan/SKILL.md)
- **Technical Specification**: [`references/blender-gamedev-practices.md`](skills/trove-voxel-artisan/references/blender-gamedev-practices.md)
  - Headless Blender 4.2 CLI execution rules.
  - glTF 2.0 export parameters without deprecated Blender 3.x flags.
  - Principled BSDF socket compatibility (Blender 4.x).
  - Armature local +Y bone coordinate rules.
  - Depsgraph evaluated dynamic camera framing math.
  - Voxel mesher optimization (boundary quad checking + BMesh planar dissolve).
- **Archetype References**:
  - [`scythe.md`](skills/trove-voxel-artisan/references/weapons/scythe.md) — Lateral reaping harvest, inner crook leading edge.
  - [`katana.md`](skills/trove-voxel-artisan/references/weapons/katana.md) — Sori curve, hamon, tsuba, samegawa, Iaido supersonic slash.
  - [`greatsword.md`](skills/trove-voxel-artisan/references/weapons/greatsword.md) — Monolithic raw iron slab, two-handed hoist, gravitational slam.
  - [`bow.md`](skills/trove-voxel-artisan/references/weapons/bow.md) — Recurve wings, elastic draw strain, supersonic flight.
  - [`staff.md`](skills/trove-voxel-artisan/references/weapons/staff.md) — Levitating core, channeling spin, spell thrust.
  - [`dagger.md`](skills/trove-voxel-artisan/references/weapons/dagger.md) — Reverse stealth grip, rapid dual cross-slashes, fatal puncture.
  - [`hammer.md`](skills/trove-voxel-artisan/references/weapons/hammer.md) — Top-heavy kinetic mass, seismic shockwave.
