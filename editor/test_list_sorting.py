"""Display sorting must preserve the save indices used by editing actions."""
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from gui import EditorApp as App


class ListSortingTests(unittest.TestCase):
    def test_mech_sort_retains_indices_selection_and_storage_filter(self):
        active = [SimpleNamespace(chassis="ZEU-9S2"),
                  SimpleNamespace(chassis="ACH-PRIME")]
        cold = [SimpleNamespace(chassis="BAS-PRIME")]
        for order, storage, expected in (
            ("Save order", "all", [0, 1, 2]),
            ("A–Z", "all", [1, 2, 0]),
            ("Z–A", "all", [0, 2, 1]),
            ("A–Z", "cold", [2]),
            ("Z–A", "active", [0, 1]),
        ):
            with self.subTest(order=order, storage=storage):
                app = SimpleNamespace(
                    save=SimpleNamespace(mechs=lambda: active,
                                         cold_storage_mechs=lambda: cold),
                    _sel_mech=0, mech_cards=Mock(),
                    mech_filter=SimpleNamespace(get=lambda: storage),
                    mech_sort_var=SimpleNamespace(get=lambda: order),
                    _make_mech_card=Mock(), _highlight_selected=Mock(),
                    mech_canvas=Mock(), mech_count_var=Mock(),
                )
                app.mech_cards.winfo_children.return_value = []
                App._refresh_mechs(app)
                self.assertEqual([c.args[0] for c in app._make_mech_card.call_args_list],
                                 expected)
                self.assertEqual(app._mech_objs, active + cold)
                self.assertEqual(app._sel_mech, 0 if 0 in expected else 2)

    def test_inventory_sort_dropdown_and_headers_agree(self):
        value = Mock()
        value.get.return_value = "Z–A"
        app = SimpleNamespace(inv_sort_var=value, _inv_sort=("count", False),
                              _render_inventory=Mock())
        App._on_inventory_sort_choice(app)
        self.assertEqual(app._inv_sort, ("item", True))
        App._sort_inventory(app, "item")
        self.assertEqual(app._inv_sort, ("item", False))
        value.set.assert_called_with("A–Z")
        App._sort_inventory(app, "count")
        value.set.assert_called_with("Column order")


if __name__ == "__main__":
    unittest.main()
