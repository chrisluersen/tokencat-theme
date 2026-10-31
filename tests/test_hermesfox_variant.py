"""Hermesfox keeps original colors with explicit branding and selectors."""

import importlib.util
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.theme_io import strict_json, strict_yaml

ROOT = Path(__file__).resolve().parents[1]


class HermesfoxVariantTests(unittest.TestCase):
    def test_skin_preserves_original_colors_and_current_art(self):
        path = ROOT / "hermes/skins/hermesfox.yaml"
        self.assertTrue(path.is_file(), "Hermesfox skin must be shipped")
        fox = strict_yaml(path.read_text(encoding="utf-8"))
        legacy = strict_yaml((ROOT / "hermes/skins/carbonfox.yaml").read_text(encoding="utf-8"))
        current = strict_yaml((ROOT / "hermes/skins/tokencat.yaml").read_text(encoding="utf-8"))
        self.assertEqual(fox["name"], "hermesfox")
        self.assertEqual(fox["colors"], legacy["colors"])
        self.assertEqual(fox["banner_hero"], current["banner_hero"])
        self.assertEqual(fox["banner_logo"], current["banner_logo"])
        self.assertEqual(fox["branding"], {"agent_name": "Hermesfox"})
        self.assertEqual(set(fox), set(legacy))

    def test_windows_terminal_preserves_original_colors(self):
        path = ROOT / "windows-terminal/hermesfox.scheme.json"
        self.assertTrue(path.is_file(), "Hermesfox scheme must be shipped")
        fox = strict_json(path.read_text(encoding="utf-8"))
        legacy = strict_json((ROOT / "windows-terminal/scheme.json").read_text(encoding="utf-8"))
        self.assertEqual(fox.pop("name"), "hermesfox")
        legacy.pop("name")
        self.assertEqual(fox, legacy)

    def test_vscode_ships_only_tokencat_while_hermesfox_keeps_other_surfaces(self):
        """The VS Code picker collapsed to Tokencat; Hermesfox survives elsewhere."""
        manifest = json.loads((ROOT / "vscode/package.json").read_text(encoding="utf-8"))
        labels = [item["label"] for item in manifest["contributes"]["themes"]]
        self.assertEqual(labels, ["Tokencat"])
        self.assertNotIn("Hermesfox", labels)
        # the variant is still shipped on the surfaces that never used the alias
        self.assertTrue((ROOT / "hermes/skins/hermesfox.yaml").is_file())
        self.assertTrue((ROOT / "windows-terminal/hermesfox.scheme.json").is_file())

    @unittest.skipUnless(
        os.environ.get("TOKENCAT_HERMES_SOURCE"), "native Hermes source not supplied"
    )
    def test_native_skin_builder_preserves_title_and_art(self):
        source = Path(os.environ["TOKENCAT_HERMES_SOURCE"])
        spec = importlib.util.spec_from_file_location(
            "hermesfox_native_skin_engine", source / "hermes_cli/skin_engine.py"
        )
        module = importlib.util.module_from_spec(spec)
        data = strict_yaml((ROOT / "hermes/skins/hermesfox.yaml").read_text(encoding="utf-8"))
        with (
            patch.object(sys, "path", [str(source), *sys.path]),
            patch.dict(sys.modules, {module.__name__: module}),
        ):
            spec.loader.exec_module(module)
            candidate = module._build_skin_config(data)
        self.assertEqual(candidate.name, "hermesfox")
        self.assertEqual(candidate.branding["agent_name"], "Hermesfox")
        self.assertEqual(candidate.banner_hero, data["banner_hero"])
        self.assertEqual(candidate.banner_logo, " ")
        for role, color in data["colors"].items():
            self.assertEqual(candidate.colors[role], color)
