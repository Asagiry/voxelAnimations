# Asset Brief Contract

Turn the user's natural-language request into this compact internal brief before generating code. Keep the brief in the agent handover; do not add it to the delivered asset package.

## Required fields

| Field | Character or creature | Weapon or prop |
| --- | --- | --- |
| `name` | concise `snake_case` package name | concise `snake_case` package name |
| `archetype` | class, creature, or undead type | weapon or prop family |
| `silhouette` | three readable masses or asymmetries | shaft/body, focal head/blade, and accent |
| `palette` | four to six material roles | four to six material roles |
| `motion` | walk personality and attack verb | attack verb and expected arc |
| `modularity` | playable empty-hand or natural weapon | socket-grip compatible or self-contained |

## Good request shapes

```text
Create a playable rogue named ember_rogue: compact 34-voxel chibi silhouette,
oversized detached gloves, asymmetrical ember scarf, charcoal/copper/orange palette.
Hands stay empty for Socket_Hand_R. Attack is a low, fast dagger-style cross-slash
performed with a phantom grip.
```

```text
Create a socket-compatible void scythe named void_reaper: 90-voxel obsidian shaft,
wide inward-cutting crescent, three orbiting violet rune rings, black/violet/silver palette.
Its attack is a broad lateral reaping arc, never a propeller spin.
```

## Avoid ambiguous requests

- Do not ask for a "cool detailed model" without a silhouette, material mood, and motion verb.
- Do not ask a playable class to hold a baked-in weapon; request a phantom-grip animation instead.
- Do not combine incompatible actions such as a scythe helicopter spin or a katana ground slam unless deliberately designing a hybrid weapon.
- Do not use exact copyrighted-character reproduction as the design brief; describe original visual traits instead.

## Defaults

If omitted, choose a 4–6 material palette, one prominent asymmetry, one readable focal feature, and a motion that fits the selected archetype. Name the inferred choices in the handover.
