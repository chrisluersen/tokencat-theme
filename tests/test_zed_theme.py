"""The Zed theme ships like every other surface, generated from the palette."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_STYLE = {
    "background",
    "editor.background",
    "editor.foreground",
    "editor.line_number",
    "editor.active_line.background",
    "border",
    "error",
    "warning",
    "info",
    "hint",
    "created",
    "modified",
    "deleted",
    "conflict",
    "panel.background",
    "element.background",
    "element.selected",
}


class ZedThemeTests(unittest.TestCase):
    def setUp(self):
        self.path = ROOT / "zed/tokencat.json"
        self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def test_theme_is_shipped_and_well_formed(self):
        self.assertTrue(self.path.is_file(), "zed/tokencat.json must ship")
        self.assertEqual(self.data["name"], "Tokencat")
        self.assertEqual(len(self.data["themes"]), 1)
        theme = self.data["themes"][0]
        self.assertEqual(theme["name"], "Tokencat")
        self.assertEqual(theme["appearance"], "dark")

    def test_required_style_roles_are_present(self):
        style = self.data["themes"][0]["style"]
        missing = REQUIRED_STYLE - set(style)
        self.assertFalse(missing, f"missing Zed style roles: {sorted(missing)}")

    def test_background_matches_the_palette(self):
        palette = json.loads((ROOT / "palettes/tokencat.json").read_text(encoding="utf-8"))
        style = self.data["themes"][0]["style"]
        self.assertEqual(style["background"], palette["base"]["background"])
        self.assertEqual(style["editor.background"], palette["base"]["background"])
        self.assertEqual(style["editor.foreground"], palette["base"]["foreground"])

    def test_syntax_colors_are_all_palette_values(self):
        palette = json.loads((ROOT / "palettes/tokencat.json").read_text(encoding="utf-8"))
        allowed = set(palette["base"].values())
        syntax = self.data["themes"][0]["style"]["syntax"]
        self.assertGreater(len(syntax), 40, "syntax map should be the rich Zed set")
        for role, spec in syntax.items():
            value = spec["color"]
            self.assertTrue(value.startswith("#"), f"{role} must be a hex colour")
            self.assertIn(value, allowed, f"{role} uses {value}, not a palette token")

    def test_boolean_is_distinct_from_number(self):
        syntax = self.data["themes"][0]["style"]["syntax"]
        self.assertNotEqual(
            syntax["boolean"]["color"],
            syntax["number"]["color"],
            "boolean and number must render differently",
        )

    def test_blur_is_declared(self):
        """Window blur is an intentional part of the design, not a default."""
        self.assertEqual(self.data["themes"][0]["style"]["background.appearance"], "blurred")
