# DLC9 catalog refresh

The v1.18.0 bundle was generated on 2026-10-12 from the installed Steam
MechWarrior 5: Mercenaries game assets after the Ashes & Ascension update.
No mods were included. Asset names, tiers, stats, stock loadouts, and traits
come from the game data rather than inferred naming patterns.

Generator: [Scarab v1.9.8](https://github.com/FiendishDrWu/Scarab/releases/tag/v1.9.8)

Executable SHA-256:
`3e0a53e1e3c2e4ce1394f9a6b53822446745ebe2641592e0b238e840addd99a2`

Reproduction (run in the directory containing Scarab):

```powershell
.\scarab.exe --mw5-dir "<MW5 installation>" --exclude-mods --output dlc9-catalog --build-report
```

Copy the four generated `.json.gz` files into `editor/`. Do not use
`--catalog-input-dir` for this refresh: that option substitutes the previous
catalogs for the base-game scan.

| Catalog | Entries |
| --- | ---: |
| Mech variants | 639 |
| Stock templates | 639 |
| Weapons | 928 |
| Equipment | 49 |
| Ammo | 108 |
| Pilot and mech traits | 241 |

The update adds 79 mech variants without removing any previously addable
variants. Campaign-only display metadata remains in `mech_catalog.py`.
