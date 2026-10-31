import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class VSCodePackageTests(unittest.TestCase):
    def test_theme_extension_points_at_shipped_dark_theme(self):
        self.assertTrue((ROOT / "vscode/package.json").is_file())
        manifest = json.loads((ROOT / "vscode/package.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["categories"], ["Themes"])
        self.assertEqual(manifest["license"], "UNLICENSED")
        self.assertNotIn("main", manifest)
        self.assertNotIn("activationEvents", manifest)
        themes = manifest["contributes"]["themes"]
        self.assertEqual({item["label"] for item in themes}, {"Tokencat"})
        self.assertEqual(len(themes), 1)
        self.assertEqual(
            {theme["label"]: theme["path"] for theme in themes},
            {"Tokencat": "./tokencat.vscode-theme.json"},
        )
        for theme in themes:
            self.assertEqual(theme["uiTheme"], "vs-dark")
            self.assertTrue((ROOT / "vscode" / theme["path"]).is_file())

    def test_vscode_ships_one_canonical_theme(self):
        """Tokencat is the only VS Code theme; the legacy alias labels were removed.

        Carbonfox remains its own surface (Hermes skin, Windows Terminal
        scheme); only the VS Code picker collapsed to one entry.
        """
        manifest = json.loads((ROOT / "vscode/package.json").read_text(encoding="utf-8"))
        labels = [item["label"] for item in manifest["contributes"]["themes"]]
        self.assertEqual(labels, ["Tokencat"])
        for removed in ("Hermesfox", "Carbonfox (Legacy)"):
            self.assertNotIn(removed, labels)

    def test_legacy_vscode_theme_file_is_retained_unlisted(self):
        """The Carbonfox VS Code payload stays on disk for restore, just unlisted."""
        legacy = ROOT / "vscode/carbonfox.vscode-theme.json"
        self.assertTrue(legacy.is_file(), "legacy VS Code payload must survive")
        self.assertEqual(json.loads(legacy.read_text(encoding="utf-8"))["name"], "Carbonfox")

    def test_token_colors_cover_the_full_zed_syntax_map(self):
        """VS Code must carry Zed's syntax colours, modulo declared AA overrides."""
        theme = json.loads((ROOT / "vscode/tokencat.vscode-theme.json").read_text(encoding="utf-8"))
        palette = json.loads((ROOT / "palettes/tokencat.json").read_text(encoding="utf-8"))
        zed = json.loads((ROOT / "zed/tokencat.json").read_text(encoding="utf-8"))
        zed_colors = {spec["color"] for spec in zed["themes"][0]["style"]["syntax"].values()}

        # Roles Zed paints #ee5396 are repainted with the brighter red in VS Code
        # because #ee5396 fails AA on the diff word backgrounds (repo readability
        # override, documented in README). Anything else must match exactly.
        AA_OVERRIDES = {"#ee5396": palette["base"]["ansi_brightRed"]}
        expected = {AA_OVERRIDES.get(c, c) for c in zed_colors}

        vscode_colors = {rule["settings"]["foreground"] for rule in theme["tokenColors"]}
        missing = expected - vscode_colors
        self.assertFalse(missing, f"VS Code syntax map is missing Zed colours: {sorted(missing)}")
        self.assertTrue(
            vscode_colors <= set(palette["base"].values()),
            "every emitted colour must be a named base token",
        )

    def test_boolean_is_distinct_from_number(self):
        """Booleans must not share the number colour."""
        theme = json.loads((ROOT / "vscode/tokencat.vscode-theme.json").read_text(encoding="utf-8"))
        by_scope = {}
        for rule in theme["tokenColors"]:
            for scope in rule["scope"]:
                by_scope[scope] = rule["settings"]["foreground"]
        self.assertNotEqual(
            by_scope["constant.language.boolean"],
            by_scope["constant.numeric"],
            "boolean and number must render differently",
        )
