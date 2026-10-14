"""Portrait / voice / persona buttons on the Pilots tab write to the save."""
import tkinter as tk
import unittest
from unittest.mock import patch

import gui
from test_pilot_appearance import _pilot, _pilot_with_bio
from test_pilot_import import PilotHarness


class PilotLookUiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.app = gui.EditorApp()
        except tk.TclError as exc:
            self.skipTest(str(exc))
        first, second = _pilot_with_bio(), _pilot(portrait="Raptor", voice="MaleAlly9")
        first.persona_id = b"a" * 16
        second.persona_id = b"b" * 16
        self.app.save = PilotHarness([first.element, second.element])
        self.app._refresh_pilots()
        self.app.update()

    def tearDown(self):
        if hasattr(self, "app"):
            self.app.destroy()

    def _select(self, index):
        self.app.pilot_list.selection_clear(0, "end")
        self.app.pilot_list.selection_set(index)
        self.app._load_pilot_form()

    def test_set_buttons_persist_when_switching_pilots(self):
        self._select(0)
        self.app.pilot_portrait_var.set("Female_Rank3_1")
        self.app.pilot_voice_var.set("FemaleAlly1")
        self.app.on_set_pilot_portrait()
        self.app.on_set_pilot_voice()
        self._select(1)
        self.assertEqual(self.app.pilot_portrait_var.get(), "Raptor")
        self._select(0)
        self.assertEqual(self.app.pilot_portrait_var.get(), "Female_Rank3_1")
        self.assertEqual(self.app.pilot_voice_var.get(), "FemaleAlly1")
        pilot = self.app.save.pilots()[0]
        self.assertEqual((pilot.portrait, pilot.voice), ("Female_Rank3_1", "FemaleAlly1"))

    def test_unset_picker_does_not_change_the_pilot(self):
        self._select(0)
        self.app.pilot_portrait_var.set("")
        with patch.object(gui.messagebox, "showinfo") as info:
            self.app.on_set_pilot_portrait()
        info.assert_called_once()
        self.assertEqual(self.app.save.pilots()[0].portrait, "MalePilot")

    def test_apply_persona_sets_portrait_and_voice(self):
        self._select(0)
        persona = next(p for p in gui.pilot_catalog.PERSONAS
                       if p["asset_name"] == "Raptor_Persona")
        self.app.pilot_persona_var.set(gui.pilot_catalog.persona_display(persona))
        self.app.on_apply_persona()
        self.assertEqual(self.app.pilot_portrait_var.get(), "Raptor")
        pilot = self.app.save.pilots()[0]
        self.assertEqual((pilot.portrait, pilot.voice), ("Raptor", "MaleAlly9"))

    def test_bio_box_shows_the_bio_and_set_writes_it(self):
        self._select(0)
        self.assertEqual(self.app.pilot_bio_text.get("1.0", "end").strip(),
                         "Bio one. Bio two. Bio three.")
        self.app.pilot_bio_text.delete("1.0", "end")
        self.app.pilot_bio_text.insert("1.0", "Fresh story.")
        self.app.on_set_pilot_bio()
        self._select(1)
        self._select(0)
        self.assertEqual(self.app.save.pilots()[0].bio_parts(), ["Fresh story.", "", ""])
        self.assertEqual(self.app.pilot_bio_text.get("1.0", "end").strip(), "Fresh story.")

    def test_untouched_bio_box_leaves_the_bio_payloads_alone(self):
        self._select(0)
        before = self.app.save.pilots()[0].bio_parts()
        self.app.on_set_pilot_bio()
        self.assertEqual(self.app.save.pilots()[0].bio_parts(), before)

    def test_template_persona_keeps_the_pilots_name_and_bio(self):
        self._select(0)
        pilot = self.app.save.pilots()[0]
        pilot.callsign = "Angel"
        template = {"asset_name": "Female_Rank3_5", "portrait": "Female_Rank3_5",
                    "voice": "FemaleAlly5"}
        with patch.object(gui.pilot_catalog, "find_persona", return_value=template):
            self.app.pilot_persona_var.set("Female_Rank3_5")
            self.app.pilot_persona_text_var.set(True)
            self.app.on_apply_persona()
        self.assertEqual(pilot.callsign, "Angel")
        self.assertEqual(pilot.bio_parts()[0], "Bio one.")
        self.assertEqual((pilot.portrait, pilot.voice), ("Female_Rank3_5", "FemaleAlly5"))

    def test_persona_with_a_bio_sets_all_three_parts(self):
        self._select(0)
        persona = {"asset_name": "P", "full_name": "Jo Smith", "callsign": "Jo",
                   "bio": "{name} one.", "bio1": "Two.", "portrait": "Raptor"}
        with patch.object(gui.pilot_catalog, "find_persona", return_value=persona):
            self.app.pilot_persona_var.set("P")
            self.app.pilot_persona_text_var.set(True)
            self.app.on_apply_persona()
        pilot = self.app.save.pilots()[0]
        self.assertEqual(pilot.bio_parts(), ["{name} one.", "Two.", ""])
        self.assertEqual(pilot.bio, "Jo one. Two.")   # test pilot has no FullName field


if __name__ == "__main__":
    unittest.main()
