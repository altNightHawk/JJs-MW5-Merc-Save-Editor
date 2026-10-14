"""Portrait / voice / persona buttons on the Pilots tab write to the save."""
import tkinter as tk
import unittest
from unittest.mock import patch

import gui
from test_pilot_appearance import _pilot
from test_pilot_import import PilotHarness


class PilotLookUiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.app = gui.EditorApp()
        except tk.TclError as exc:
            self.skipTest(str(exc))
        first, second = _pilot(), _pilot(portrait="Raptor", voice="MaleAlly9")
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


if __name__ == "__main__":
    unittest.main()
