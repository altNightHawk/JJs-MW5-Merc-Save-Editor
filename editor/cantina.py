"""Experimental edits to existing Cantina points, preserving jobs/reward claims.

Tier thresholds are factual CareerPoints values extracted from the five
CareerPathLevels arrays in the installed, unmodified DLC9 game assets.
"""
from bisect import bisect_right
from dataclasses import dataclass

from savefile import _path, _set_leaf, read_fstring_payload, read_int, write_int

TIERS = {
    "EquipmentCollectorCareerPath": (5, 17, 32, 50, 70, 95, 124, 175, 249, 349),
    "MechCollectorCareerPath": (5, 17, 50, 70, 95, 95, 124, 175, 249, 349),
    "MechHunterCareerPath": (5, 17, 32, 50, 70, 95, 124, 175, 249, 349),
    "TreasureHunterCareerPath": (5, 17, 32, 50, 70, 95, 124, 175, 249, 349),
    "WarDogCareerPath": (5, 17, 32, 50, 70, 95, 124, 175, 249, 349),
}
LABELS = {
    "EquipmentCollectorCareerPath": "Equipment Collector",
    "MechCollectorCareerPath": "Mech Collector",
    "MechHunterCareerPath": "Mech Hunter",
    "TreasureHunterCareerPath": "Treasure Hunter",
    "WarDogCareerPath": "War Dog",
}


@dataclass
class CantinaPath:
    asset: str
    progress: object

    @property
    def label(self):
        return LABELS.get(self.asset, self.asset)

    @property
    def points(self):
        return read_int(self.progress.raw_payload)

    @property
    def tier(self):
        thresholds = TIERS.get(self.asset)
        return bisect_right(thresholds, self.points) if thresholds else None

    def set_points(self, value):
        if not isinstance(value, int) or not 0 <= value <= 2147483647:
            raise ValueError("Cantina points must be a non-negative 32-bit integer.")
        _set_leaf(self.progress, write_int(value))

    def set_tier(self, tier):
        thresholds = TIERS.get(self.asset)
        if thresholds is None:
            raise ValueError("This path has no verified built-in tier thresholds.")
        if not isinstance(tier, int) or not 0 <= tier <= len(thresholds):
            raise ValueError("Cantina tier must be between 0 and 10.")
        self.set_points(thresholds[tier-1] if tier else 0)


def paths(save):
    """Read only the observed schema; never invent missing campaign records."""
    try:
        model = save.model("ErrandModel").plist
    except KeyError:
        return []
    wrapper = model.get("CareerPathList")
    if wrapper is None:
        return []
    progress = _path(model, "CareerPathList", "Progress")
    array = progress.decoded if progress is not None else None
    if array is None or getattr(array, "element_type", None) != "StructProperty":
        raise ValueError("The save's Cantina progression uses an unsupported layout.")
    result = []
    for element in array.elements:
        name = _path(element, "Career", "ID", "PrimaryAssetName")
        points = element.get("Progress")
        if name is None or points is None or points.type != "IntProperty" or len(points.raw_payload) != 4:
            raise ValueError("A Cantina career record could not be decoded safely.")
        result.append(CantinaPath(read_fstring_payload(name.raw_payload), points))
    return result


def max_paths(records):
    """Advance known existing paths without reducing already higher progress."""
    changes = [(record, max(record.points, TIERS[record.asset][-1]))
               for record in records if record.asset in TIERS]
    for record, points in changes:
        record.set_points(points)
    return len(changes)
