"""Pilot edits retain game text histories and selection; invalid input is atomic."""
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from gui import EditorApp
from savefile import Pilot, SKILLS, CAPPED_SKILLS, write_int, build_text_property, read_text_property
from test_pilot_import import _pilot_element, _struct, _leaf


class PilotEditingTests(unittest.TestCase):
    def test_unicode_name_is_read_without_losing_characters(self):
        self.assertEqual(read_text_property(build_text_property("Capt. Élodie 李")),
                         "Capt. Élodie 李")

    def test_unchanged_names_preserve_localized_payloads(self):
        # Base/localized FText: flags, history, namespace, key, source string.
        from ue_property import Writer
        w = Writer()
        w.i32(0)
        w.write(b"\x00")
        for value in ("PilotNames", "name_key", "Capt. Example"):
            w.fstring(value)
        payload = w.bytes()
        element = _pilot_element("EXAMPLE", "EMechWarriorPlayerSlot::None", b"p"*16)
        element.get("PersonaData").decoded.properties.append(
            _leaf("FullName", "TextProperty", payload))
        element.get("PersonaData").decoded.get("Callsign").raw_payload = payload
        pilot = Pilot(element)
        pilot.callsign = pilot.callsign
        pilot.full_name = pilot.full_name
        for key in ("Callsign", "FullName"):
            self.assertEqual(pilot.persona.decoded.get(key).raw_payload, payload)
        pilot.full_name = "Custom Name"
        self.assertEqual(pilot.full_name, "Custom Name")

    def test_skill_edits_survive_serialization(self):
        from ue_property import Reader, Writer, read_property_list, write_property_list
        element = _pilot_element("EXAMPLE", "EMechWarriorPlayerSlot::None", b"p"*16)
        nodes = []
        for sk in SKILLS:
            header = Writer()
            header.i64(1)
            header.fstring("None")
            header.write(b"\x00")
            from ue_property import Property
            nodes.append(_struct(sk, [
                Property("SkillCap", "ByteProperty", header.bytes(), b"\x03"),
                _leaf("TotalExp", "IntProperty", write_int(100)),
            ], "PilotSkill"))
        element.properties.append(_struct("Skills", nodes))
        pilot = Pilot(element)
        for sk in SKILLS:
            pilot.set_skill(sk, 54321)
        for sk in CAPPED_SKILLS:
            pilot.set_skill_cap(sk, 10)
        w = Writer()
        write_property_list(w, element)
        reread = Pilot(read_property_list(Reader(w.bytes())))
        for sk in SKILLS:
            self.assertEqual(reread.skill(sk), 54321)
            self.assertEqual(reread.skill_cap(sk), 10 if sk in CAPPED_SKILLS else 3)

    def test_roster_refresh_retains_selected_pilot(self):
        app = SimpleNamespace(
            _selected_pilot_index=lambda: 2,
            pilot_list=Mock(),
            save=SimpleNamespace(pilots=lambda: [SimpleNamespace(callsign=n)
                                               for n in ("ONE", "TWO", "THREE")]),
            _load_pilot_form=Mock(),
        )
        EditorApp._refresh_pilots(app)
        app.pilot_list.selection_set.assert_called_once_with(2)

    def test_invalid_input_does_not_change_name_or_salary(self):
        pilot = Mock()
        values = {"callsign": "Changed", "full_name": "Changed", "salary": "100"}
        values.update({f"skill_{sk}": "100" for sk in SKILLS})
        values.update({f"cap_{sk}": "10" for sk in CAPPED_SKILLS})
        values["cap_HeatManagement"] = "invalid"
        app = SimpleNamespace(
            _guard=lambda: True, _selected_pilot_index=lambda: 0,
            save=SimpleNamespace(pilots=lambda: [pilot]),
            pilot_vars={k: SimpleNamespace(get=lambda v=v: v) for k,v in values.items()},
        )
        with patch("gui.messagebox.showerror") as error:
            EditorApp.on_apply_pilot(app)
        error.assert_called_once()
        self.assertNotIn("callsign", pilot.__dict__)
        self.assertNotIn("salary", pilot.__dict__)
        pilot.set_skill.assert_not_called()


if __name__ == "__main__":
    unittest.main()
