from types import SimpleNamespace
import unittest

from cantina import CantinaPath, paths, max_paths
from savefile import write_int, read_int, write_fstring_payload
from test_pilot_import import _leaf, _struct
from ue_property import ArrayValue, Property, PropertyList


def record(asset, points):
    return PropertyList([
        _struct('Career', [_struct('ID', [
            _leaf('PrimaryAssetName', 'NameProperty', write_fstring_payload(asset))])]),
        _leaf('Progress', 'IntProperty', write_int(points)),
    ])


class CantinaTests(unittest.TestCase):
    def test_read_and_edit_only_observed_progress_field(self):
        element = record('MechHunterCareerPath', 80)
        array = ArrayValue('StructProperty', 1, [element])
        progression = Property('Progress', 'ArrayProperty', b'', b'', array)
        reward_claims = _leaf('CareerRewardClaimList', 'UnknownProperty', b'claims untouched')
        offers = _leaf('OfferSaveData', 'UnknownProperty', b'jobs untouched')
        plist = PropertyList([_struct('CareerPathList', [progression]), reward_claims, offers])
        save = SimpleNamespace(model=lambda name: SimpleNamespace(plist=plist))
        result = paths(save)
        self.assertEqual(result[0].tier, 5)
        result[0].set_tier(10)
        self.assertEqual(read_int(element.get('Progress').raw_payload), 349)
        self.assertEqual(reward_claims.raw_payload, b'claims untouched')
        self.assertEqual(offers.raw_payload, b'jobs untouched')

    def test_missing_records_are_not_created(self):
        plist = PropertyList([])
        save = SimpleNamespace(model=lambda name: SimpleNamespace(plist=plist))
        self.assertEqual(paths(save), [])
        self.assertEqual(plist.properties, [])

    def test_unrecognized_structure_is_rejected(self):
        plist = PropertyList([_struct('CareerPathList', [
            _leaf('Progress', 'IntProperty', write_int(3))])])
        save = SimpleNamespace(model=lambda name: SimpleNamespace(plist=plist))
        with self.assertRaises(ValueError):
            paths(save)

    def test_invalid_tier_does_not_change_points(self):
        item = CantinaPath('MechHunterCareerPath', _leaf('Progress','IntProperty',write_int(80)))
        for tier in (-1, 11):
            with self.assertRaises(ValueError):
                item.set_tier(tier)
        self.assertEqual(item.points, 80)

    def test_max_preserves_mod_path_and_higher_existing_points(self):
        items = [CantinaPath(name, _leaf('Progress', 'IntProperty', write_int(points)))
                 for name, points in [('MechHunterCareerPath', 80),
                                      ('WarDogCareerPath', 400), ('ModCareerPath', 27)]]
        self.assertEqual(max_paths(items), 2)
        self.assertEqual([p.points for p in items], [349, 400, 27])

    def test_duplicate_game_threshold_reports_effective_tier(self):
        item = CantinaPath('MechCollectorCareerPath', _leaf('Progress','IntProperty',write_int(0)))
        item.set_tier(5)
        self.assertEqual((item.points, item.tier), (95, 6))


if __name__ == '__main__':
    unittest.main()
