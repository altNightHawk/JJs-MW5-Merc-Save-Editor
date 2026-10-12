"""Verify DLC9 assets can be selected and rebuilt with real stock loadouts."""
import unittest

import item_catalog
import mech_catalog
import stock_templates


class Dlc9CatalogTests(unittest.TestCase):
    def test_new_chassis_have_metadata_and_stock_loadouts(self):
        variants = {
            "ACH-PRIME": 30, "ACW-PRIME": 40, "IFR-PRIME": 45,
            "HMN-PRIME": 50, "HBK-IIC": 50, "NCT-PRIME": 70,
            "SNS-PRIME": 70, "MAD-IIC": 85, "WHM-IIC": 80,
            "BAS-PRIME": 90, "SNV-1": 90, "SR-1": 100,
            "BANE-1": 100, "BJ2-O": 50, "BHKU-OC": 60, "PRS-P1": 75,
        }
        for variant, tons in variants.items():
            with self.subTest(variant=variant):
                self.assertIn(variant, mech_catalog.ALL_VARIANTS)
                self.assertEqual(mech_catalog.chassis_info(variant)[0], tons)
                template = stock_templates.stock_template(variant)
                self.assertIsNotNone(template)
                self.assertTrue(template["structure"])
                self.assertTrue(template["armor"])
                self.assertTrue(template["weapons"])

    def test_new_inner_sphere_weapons_have_all_tiers(self):
        names = {name for name, _ in item_catalog.WEAPONS}
        weapons = (
            "ERSmallLaser", "ERMediumLaser", "LightGaussRifle",
            "UltraAutocannon2_Single", "UltraAutocannon10_Single",
            "UltraAutocannon20_Single", "StreakSRM4", "StreakSRM6",
            "LBXAutocannon2", "LBXAutocannon5", "LBXAutocannon20",
        )
        for weapon in weapons:
            for suffix in ("", "_Lvl0", "_Lvl2", "_Lvl3", "_Lvl4", "_Lvl5"):
                with self.subTest(asset=weapon + suffix):
                    self.assertIn(weapon + suffix, names)


if __name__ == "__main__":
    unittest.main()
