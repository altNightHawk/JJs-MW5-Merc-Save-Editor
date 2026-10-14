"""Pilot portrait / voice / bio edits and the pilot catalog helpers."""
import unittest

import pilot_catalog
from savefile import Pilot, read_fstring_payload, write_fstring_payload
from test_pilot_import import PilotHarness, _leaf, _pilot_element, _struct
from ue_property import Reader, Writer, read_property_list, write_property_list


def _asset_ref(field: str, asset_type: str, asset_name: str):
    return _struct(field, [
        _struct("ID", [
            _struct("PrimaryAssetType", [
                _leaf("Name", "NameProperty", write_fstring_payload(asset_type))]),
            _leaf("PrimaryAssetName", "NameProperty", write_fstring_payload(asset_name)),
        ], "PrimaryAssetId"),
    ], "MWPortraitAssetId")


def _pilot(portrait="MalePilot", voice="MaleAlly4", voice_type="MWDialogueVoiceAsset"):
    element = _pilot_element("EXAMPLE", "EMechWarriorPlayerSlot::None", b"p" * 16)
    persona = element.get("PersonaData").decoded
    persona.properties.append(_asset_ref("PortraitAssetId", "MWPortraitAsset", portrait))
    persona.properties.append(_asset_ref("DialogueVoiceAssetId", voice_type, voice))
    return Pilot(element)


def _reload(pilot: Pilot) -> Pilot:
    w = Writer()
    write_property_list(w, pilot.element)
    return Pilot(read_property_list(Reader(w.bytes())))


class PilotAppearanceTests(unittest.TestCase):
    def test_reads_portrait_and_voice(self):
        pilot = _pilot()
        self.assertEqual((pilot.portrait, pilot.voice), ("MalePilot", "MaleAlly4"))

    def test_edits_survive_serialization_even_when_the_name_gets_longer(self):
        pilot = _pilot()
        pilot.portrait = "Female_Rank3_1"
        pilot.voice = "FemaleAlly8"
        again = _reload(pilot)
        self.assertEqual((again.portrait, again.voice), ("Female_Rank3_1", "FemaleAlly8"))

    def test_voice_type_is_fixed_for_a_pilot_without_a_voice(self):
        # The commander's voice is stored as None / None.
        pilot = _pilot(voice="None", voice_type="None")
        pilot.voice = "MaleAlly1"
        kind = pilot.persona.decoded.get("DialogueVoiceAssetId").decoded \
            .get("ID").decoded.get("PrimaryAssetType").decoded.get("Name")
        self.assertEqual(read_fstring_payload(kind.raw_payload), "MWDialogueVoiceAsset")
        self.assertEqual(_reload(pilot).voice, "MaleAlly1")

    def test_empty_values_are_rejected_and_leave_the_pilot_alone(self):
        pilot = _pilot()
        with self.assertRaises(ValueError):
            pilot.portrait = "  "
        self.assertEqual(pilot.portrait, "MalePilot")

    def test_pilot_without_appearance_data_raises(self):
        element = _pilot_element("EXAMPLE", "EMechWarriorPlayerSlot::None", b"p" * 16)
        pilot = Pilot(element)
        self.assertEqual(pilot.portrait, "")
        with self.assertRaises(ValueError):
            pilot.portrait = "MalePilot"

    def test_add_pilot_can_set_portrait_and_voice(self):
        donor = _pilot()
        harness = PilotHarness([donor.element])
        new = harness.add_pilot("NEWBIE", portrait="Female_Rank1_1", voice="FemaleAlly2")
        self.assertEqual((new.portrait, new.voice), ("Female_Rank1_1", "FemaleAlly2"))
        self.assertEqual(donor.portrait, "MalePilot")   # the donor is untouched


class PilotCatalogTests(unittest.TestCase):
    def test_bundled_catalog_has_the_known_assets(self):
        self.assertIn("LeonFreeman", pilot_catalog.PORTRAITS)
        self.assertIn("MaleAlly4", pilot_catalog.VOICES)
        self.assertTrue(pilot_catalog.PERSONAS)

    def test_sex_filter_drops_the_other_sex_but_keeps_unknown(self):
        names = ["Ally_Female_Rank_1", "Male_Rank1_1", "Lyana"]
        female = pilot_catalog.asset_choices(
            [], names, pilot_catalog.portrait_sex, pilot_catalog.FEMALE)
        self.assertIn("Ally_Female_Rank_1", female)
        self.assertNotIn("Male_Rank1_1", female)
        self.assertIn("Lyana", female)      # unknown sex stays selectable

    def test_choices_include_what_the_save_already_uses(self):
        values = pilot_catalog.asset_choices(["ModdedFace", "None"], ["A"], lambda n: None)
        self.assertEqual(values, ["A", "ModdedFace"])

    def test_names_are_derived_from_string_table_keys(self):
        persona = {"asset_name": "Lyana",
                   "full_name": "Persona_Character_LyanaMoore_FullName",
                   "callsign": "Persona_Character_LyanaMoore_Callsign"}
        self.assertEqual(pilot_catalog.persona_name(persona), "Lyana Moore")
        self.assertEqual(pilot_catalog.persona_name({**persona, "full_name": "Lyana Moore"}),
                         "Lyana Moore")
        self.assertEqual(pilot_catalog.persona_callsign({**persona, "callsign": "Raptor"}),
                         "Raptor")

    def test_template_bios_get_the_pilots_name(self):
        persona = {"asset_name": "X", "bio": "{name} hails from Luthien."}
        self.assertEqual(pilot_catalog.persona_bio(persona, "Jo Smith"),
                         "Jo Smith hails from Luthien.")
        self.assertIsNone(pilot_catalog.persona_bio({"asset_name": "X", "bio": "ONEWORD"}, "Jo"))
        self.assertIsNone(pilot_catalog.persona_bio({"asset_name": "X"}, "Jo"))

    def test_persona_picker_round_trips(self):
        persona = pilot_catalog.PERSONAS[0]
        found = pilot_catalog.find_persona(pilot_catalog.persona_display(persona))
        self.assertEqual(found["asset_name"], persona["asset_name"])
        self.assertIsNone(pilot_catalog.find_persona("nope"))


if __name__ == "__main__":
    unittest.main()
