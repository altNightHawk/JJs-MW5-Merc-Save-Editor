# Cantina progression investigation — issue #40

Investigation on 2026-10-14 used copies/read-only inspection of local Steam
saves and identifiers in the installed game's executable. No game files or
live saves were modified.

The installed game exposes these career identifiers:

- `CareerPathList`, `OldCareerPathList`, `CareerPathProgressList`
- `CareerPathId`, `CareerPathAssetId`, `CareerPathTag`
- `CareerPoints`, `PreviousCareerPoints`, `CareerLevel`
- `CareerPathLevelProgress`, `CareerPathLevels`, `CareerPathLevelStruct`
- `CareerRewardClaimList`, `CareerRewardClaimStruct`
- `SetCareerPathProgress`, `AddCareerPathProgress`, `ClaimCareerReward`

These identifiers establish that paths, points, levels and reward claims are
separate concepts. They do **not** establish the save schema, types, required
fields, or level thresholds. In particular, a requested tier cannot yet be
translated reliably into points or claimed unlocks.

No inspected local `.sav` initially contained `CareerPathList`,
`CareerPathProgressList`, `CareerRewardClaimList`, or `CareerPoints`.
`ErrandModel` has callbacks and `OfferSaveData` (Cantina job offers), with the
expected four-byte footer. Job offers reference `MWCareerPathAsset` names but
are not the player's progression. Post-mission `CareerProgressRewards` are
reward entries, not demonstrated persistent path progress.

## Advanced-save findings

The publicly supplied save in issue #35 contains the existing structure:

```text
ErrandModel
  CareerPathList : StructProperty<CareerPathProgressList>
    Progress : ArrayProperty<StructProperty<CareerPathProgress>>
      Career.ID.PrimaryAssetName : NameProperty
      Progress : IntProperty
  CareerRewardClaimList : ArrayProperty<StructProperty<CareerRewardClaimStruct>>
```

The five paths are Equipment Collector, Mech Hunter, Mech Collector, Treasure
Hunter and War Dog. Their `Progress` values are 75, 80, 70, 70 and 28. The
reward-claim list separately contains a mech trait, career ID, previous career
points and an icon; offers remain serialized job objects.

The installed unmodified game's `Content/Careers/*CareerPath.uasset/.uexp`
packages each contain ten `CareerPathLevels` elements. Their `CareerPoints`
thresholds are `(5,17,32,50,70,95,124,175,249,349)` except Mech Collector,
whose actual extracted values are `(5,17,50,70,95,95,124,175,249,349)`.
The duplicate 95 is preserved: selecting nominal tier 5 reports effective tier
6 under the threshold calculation. No separate threshold was invented.

`tools/extract_cantina_thresholds.py` reproduces the extraction from separately
extracted package pairs and prints hashes for both source files. The extractor
checks the package/name-table layout, integer tags, array count and tier order.

The experimental editor now changes only those existing `Progress` integers.
It preserves offers, active jobs, campaign arcs and reward claims, and does not
invent missing arrays. Mod-added paths may use point editing but cannot use the
stock tier table or stock max-all action. Max-all never reduces higher points.

Required validation: no-op byte-identical round trip; a single-path change
whose other fields/models stay unchanged; in-game verification of tier display,
upgrade availability, new Cantina jobs and subsequent campaign progression.

## Validation status

The issue #35 save's no-op round-trip is byte-identical. Setting all five paths
to 349 points changes exactly ten bytes, preserves total size and round-trips
successfully; all other models, offers and reward claims remain byte-identical.
The original downloaded save remains untouched. Synthetic regression tests
cover invalid/missing schemas, invalid tiers, shared thresholds and mod paths.

In-game tier display, reward claims, upgrade eligibility and subsequent Cantina
jobs/campaign progression are still unverified. Issue #40 should stay open for
in-game testing; this is an experimental points editor, not a demonstrated
campaign-unlock or automatic reward-claim implementation.
