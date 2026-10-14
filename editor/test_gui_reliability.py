"""Exercise owned pickers and explicit modal parenting without a game save."""
from types import SimpleNamespace
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from gui import EditorApp, SearchChoiceDialog, SearchablePicker


class DialogRoutingTests(unittest.TestCase):
    def test_faction_double_click_selects_the_clicked_row(self):
        app = SimpleNamespace(faction_tree=Mock(), on_edit_standing=Mock())
        app.faction_tree.identify_row.return_value = "3"
        self.assertEqual(EditorApp._on_faction_double_click(app, SimpleNamespace(y=42)), "break")
        app.faction_tree.selection_set.assert_called_once_with("3")
        app.on_edit_standing.assert_called_once()

    def test_faction_dialog_is_owned_by_editor(self):
        faction = SimpleNamespace(name="Test Faction", standing=10)
        app = SimpleNamespace(_guard=lambda: True, faction_tree=Mock(),
                              save=SimpleNamespace(factions=lambda: [faction]))
        app.faction_tree.selection.return_value = ("0",)
        with patch("gui.simpledialog.askinteger", return_value=None) as ask:
            EditorApp.on_edit_standing(app)
        self.assertIs(ask.call_args.kwargs["parent"], app)


class PickerUiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(str(exc))
        self.root.geometry("500x400")
        self.root.update()

    def tearDown(self):
        if hasattr(self, "root"):
            self.root.update_idletasks()
            self.root.destroy()

    def test_browse_filter_accepts_exact_asset_and_releases_grab(self):
        var = tk.StringVar(self.root, "unchanged")
        picker = SearchablePicker(self.root, textvariable=var, width=24, title="Choose trait")
        picker["values"] = ("Laser Specialist -- Laser_PilotTrait", "Missile Specialist -- Missile_PilotTrait")
        picker.pack()
        checked = []

        def choose():
            dialog = next(w for w in self.root.winfo_children() if isinstance(w, SearchChoiceDialog))
            dialog.query.set("laser")
            checked.append(dialog.results.get(0, "end"))
            dialog.ok()

        self.root.after(100, choose)
        picker._browse()
        self.assertEqual(checked, [("Laser Specialist -- Laser_PilotTrait",)])
        self.assertEqual(var.get(), "Laser Specialist -- Laser_PilotTrait")
        self.assertIsNone(self.root.grab_current())

    def test_cancel_retains_typed_value(self):
        var = tk.StringVar(self.root, "CustomAsset")
        picker = SearchablePicker(self.root, textvariable=var, width=24, title="Choose item")
        picker["values"] = ("ItemA", "ItemB")
        picker.pack()
        self.root.after(100, lambda: next(w for w in self.root.winfo_children()
                                        if isinstance(w, SearchChoiceDialog)).cancel())
        picker._browse()
        self.assertEqual(var.get(), "CustomAsset")
        self.assertIsNone(self.root.grab_current())


if __name__ == "__main__":
    unittest.main()
