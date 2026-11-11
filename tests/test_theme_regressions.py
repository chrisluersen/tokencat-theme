import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.validate_theme import CANONICAL_COLOR_KEYS, _parse_skin, validate_repository

ROOT = Path(__file__).resolve().parents[1]


class ThemeRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        shutil.copytree(
            ROOT,
            self.root,
            ignore=shutil.ignore_patterns(
                ".git", ".hermes", ".venv", "venv", "__pycache__", ".ruff_cache"
            ),
        )

    def test_parser_rejects_duplicate_color_keys(self):
        text = 'name: tokencat\ncolors:\n  ui_text: "#ffffff"\n  ui_text: "#000000"\n'
        with self.assertRaises(ValueError):
            _parse_skin(text)

    def test_parser_accepts_real_yaml_and_preserves_hero(self):
        data = _parse_skin(
            "name: tokencat\ncolors: {ui_text: '#ffffff'}\n"
            "banner_logo: ' '\nbanner_hero: |\n  cat\n  box\n"
        )
        self.assertEqual(data["banner_logo"], " ")
        self.assertEqual(data["banner_hero"], "cat\nbox\n")

    def test_parser_rejects_non_string_colors(self):
        with self.assertRaises(ValueError):
            _parse_skin("name: tokencat\ncolors:\n  ui_text: 12\n")

    def test_parser_rejects_list_root(self):
        with self.assertRaises(ValueError):
            _parse_skin("- tokencat\n")

    def test_duplicate_palette_json_is_rejected(self):
        path = self.root / "palettes/tokencat.json"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("{", '{"name":"duplicate",', 1), encoding="utf-8")
        self.assertTrue(
            any("duplicate JSON key: name" in item for item in validate_repository(self.root))
        )

    def test_nonfinite_palette_metadata_is_rejected(self):
        path = self.root / "palettes/tokencat.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["audit_probe"] = float("nan")
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertTrue(
            any("non-finite JSON constant" in item for item in validate_repository(self.root))
        )

    def test_overflow_palette_metadata_is_rejected(self):
        self.assertEqual(validate_repository(self.root), [])
        path = self.root / "palettes/tokencat.json"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("{", '{"audit_probe":1e999,', 1), encoding="utf-8")
        self.assertTrue(
            any("non-finite JSON number" in item for item in validate_repository(self.root))
        )

    def test_palette_wrong_shape_returns_violations(self):
        for value in ([], {"base": [], "mappings": {}}, {"base": {}, "mappings": []}):
            with self.subTest(value=value):
                (self.root / "palettes/tokencat.json").write_text(
                    json.dumps(value), encoding="utf-8"
                )
                self.assertTrue(validate_repository(self.root))

    def test_missing_source_art_is_rejected(self):
        (self.root / "ascii-art/token-cat-29x11.txt").unlink()
        self.assertIn(
            "missing required artifact: ascii-art/token-cat-29x11.txt",
            validate_repository(self.root),
        )

    def test_invalid_utf8_source_art_returns_violation(self):
        self.assertEqual(validate_repository(self.root), [])
        (self.root / "ascii-art/lucky-cat-29x11.txt").write_bytes(b"\xff")
        try:
            violations = validate_repository(self.root)
        except UnicodeDecodeError as exc:
            self.fail(f"unreadable source art escaped validation: {exc}")
        self.assertTrue(
            any("ascii-art/lucky-cat-29x11.txt: invalid source art" in item for item in violations),
            violations,
        )

    def test_missing_json_export_is_rejected(self):
        (self.root / "windows-terminal/tokencat.scheme.json").unlink()
        self.assertIn(
            "missing required artifact: windows-terminal/tokencat.scheme.json",
            validate_repository(self.root),
        )

    def test_missing_hero_is_rejected(self):
        path = self.root / "hermes/skins/tokencat.yaml"
        path.write_text(
            path.read_text(encoding="utf-8").split("banner_hero: |", 1)[0], encoding="utf-8"
        )
        self.assertIn("skin missing required banner_hero", validate_repository(self.root))

    def test_private_plan_is_not_a_distributable(self):
        before = validate_repository(self.root)
        path = self.root / ".hermes/plans/private.md"
        path.parent.mkdir(parents=True)
        path.write_text("/home/example/private", encoding="utf-8")
        self.assertEqual(validate_repository(self.root), before)

    def test_word_diff_guard_rejects_each_old_emitted_background(self):
        for relative, color_key in (
            ("vscode/tokencat.vscode-theme.json", "colors"),
            ("vscode/tokencat-color-customizations.json", "workbench.colorCustomizations"),
        ):
            path = self.root / relative
            original = path.read_text(encoding="utf-8")
            for background, old_color in (
                ("diffEditor.insertedTextBackground", "#21432f"),
                ("diffEditor.removedTextBackground", "#512b3d"),
            ):
                with self.subTest(export=relative, background=background):
                    altered = json.loads(original)
                    altered[color_key][background] = old_color
                    path.write_text(json.dumps(altered), encoding="utf-8")
                    try:
                        with (
                            patch(__name__ + ".ROOT", self.root),
                            self.assertRaisesRegex(AssertionError, "not greater than or equal"),
                        ):
                            case = ContrastTests("test_vscode_syntax_colors_on_word_diffs_clear_aa")
                            case.test_vscode_syntax_colors_on_word_diffs_clear_aa()
                    finally:
                        path.write_text(original, encoding="utf-8")

    def test_all_shared_aliases_are_explicit(self):
        skin = _parse_skin((ROOT / "hermes/skins/tokencat.yaml").read_text(encoding="utf-8"))
        palette = json.loads((ROOT / "palettes/tokencat.json").read_text(encoding="utf-8"))
        for key in ("ui_primary", "ui_text", "ui_border"):
            with self.subTest(key=key):
                self.assertIn(key, CANONICAL_COLOR_KEYS)
                self.assertIn(key, skin["colors"])
                self.assertIn(key, palette["mappings"]["hermes"])

    def test_dashboard_has_explicit_color_and_safe_layout_contract(self):
        from scripts.theme_io import strict_yaml

        self.assertTrue((ROOT / "hermes/dashboard-themes/tokencat.yaml").is_file())
        data = strict_yaml(
            (ROOT / "hermes/dashboard-themes/tokencat.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(data["name"], "tokencat")
        self.assertEqual(data["palette"]["background"]["hex"], "#161616")
        self.assertEqual(data["palette"]["midground"]["hex"], "#f2f4f8")
        self.assertEqual(data["palette"]["background"]["alpha"], 1.0)
        self.assertEqual(data["palette"]["midground"]["alpha"], 1.0)
        self.assertEqual(data["palette"]["foreground"], {"hex": "#78a9ff", "alpha": 0.0})
        self.assertEqual(data["layout"], {"radius": "0.5rem", "density": "comfortable"})
        self.assertEqual(data["layoutVariant"], "standard")
        self.assertEqual(data["palette"]["warmGlow"], "rgba(0, 0, 0, 0)")
        self.assertEqual(data["palette"]["noiseOpacity"], 0.0)
        required = {
            "card",
            "cardForeground",
            "popover",
            "popoverForeground",
            "primary",
            "primaryForeground",
            "secondary",
            "secondaryForeground",
            "muted",
            "mutedForeground",
            "accent",
            "accentForeground",
            "destructive",
            "destructiveForeground",
            "success",
            "warning",
            "border",
            "input",
            "ring",
        }
        self.assertEqual(set(data["colorOverrides"]), required)
        self.assertNotIn("fontUrl", data["typography"])
        self.assertNotIn("customCSS", data)
        self.assertNotIn("assets", data)


def contrast_ratio(first, second):
    def luminance(value):
        channels = [int(value[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in channels]
        return sum(x * weight for x, weight in zip(linear, (0.2126, 0.7152, 0.0722)))

    dark, light = sorted((luminance(first), luminance(second)))
    return (light + 0.05) / (dark + 0.05)


class ContrastTests(unittest.TestCase):
    def test_cli_completion_text_states_clear_aa(self):
        colors = _parse_skin((ROOT / "hermes/skins/tokencat.yaml").read_text(encoding="utf-8"))[
            "colors"
        ]
        # Native styles use ui_label, not banner_title, for selected metadata.
        pairs = (
            ("banner_text", "completion_menu_bg"),
            ("banner_title", "completion_menu_current_bg"),
            ("banner_dim", "completion_menu_meta_bg"),
            ("ui_label", "completion_menu_meta_current_bg"),
        )
        for foreground, background in pairs:
            with self.subTest(foreground=foreground, background=background):
                self.assertGreaterEqual(contrast_ratio(colors[foreground], colors[background]), 4.5)

    def test_vscode_suggestion_text_states_clear_aa(self):
        for relative, color_key in (
            ("vscode/tokencat.vscode-theme.json", "colors"),
            ("vscode/tokencat-color-customizations.json", "workbench.colorCustomizations"),
        ):
            colors = json.loads((ROOT / relative).read_text(encoding="utf-8"))[color_key]
            pairs = (
                ("editorSuggestWidget.foreground", "editorSuggestWidget.background"),
                ("editorSuggestWidget.highlightForeground", "editorSuggestWidget.background"),
                (
                    "editorSuggestWidget.selectedForeground",
                    "editorSuggestWidget.selectedBackground",
                ),
                (
                    "editorSuggestWidget.focusHighlightForeground",
                    "editorSuggestWidget.selectedBackground",
                ),
            )
            for foreground, background in pairs:
                with self.subTest(export=relative, foreground=foreground, background=background):
                    # Focused matches use a distinct VS Code role, not highlightForeground.
                    # Require explicit colors rather than assuming inherited defaults.
                    self.assertIn(foreground, colors)
                    self.assertIn(background, colors)
                    self.assertGreaterEqual(
                        contrast_ratio(colors[foreground], colors[background]), 4.5
                    )

    def test_added_word_border_remains_distinct_on_darker_diff_backgrounds(self):
        for relative, color_key in (
            ("vscode/tokencat.vscode-theme.json", "colors"),
            ("vscode/tokencat-color-customizations.json", "workbench.colorCustomizations"),
        ):
            colors = json.loads((ROOT / relative).read_text(encoding="utf-8"))[color_key]
            border = "diffEditor.insertedTextBorder"
            with self.subTest(export=relative):
                self.assertIn(border, colors)
                self.assertRegex(colors[border], r"^#[0-9a-fA-F]{6}$")
                for background in (
                    "diffEditor.insertedTextBackground",
                    "diffEditor.insertedLineBackground",
                ):
                    self.assertGreaterEqual(contrast_ratio(colors[border], colors[background]), 3.0)

    def test_normal_text_pairs_clear_aa(self):
        base = json.loads((ROOT / "palettes/tokencat.json").read_text(encoding="utf-8"))["base"]
        pairs = (
            ("foreground", "background"),
            ("foreground", "surface"),
            ("foreground", "border"),
            ("muted_accessible", "surface"),
            ("muted_accessible", "surface_selected"),
            ("thinking_accessible", "background"),
            ("thinking_accessible", "surface"),
            ("green", "background"),
            ("orange", "background"),
            ("red", "background"),
            ("foreground", "diff_add_bg"),
            ("foreground", "diff_remove_bg"),
        )
        for foreground, background in pairs:
            with self.subTest(foreground=foreground, background=background):
                self.assertGreaterEqual(contrast_ratio(base[foreground], base[background]), 4.5)

    def test_focus_accent_clears_nontext_contrast(self):
        base = json.loads((ROOT / "palettes/tokencat.json").read_text(encoding="utf-8"))["base"]
        self.assertGreaterEqual(contrast_ratio(base["blue"], base["surface"]), 3.0)

    def test_diff_word_backgrounds_keep_text_readable(self):
        base = json.loads((ROOT / "palettes/tokencat.json").read_text(encoding="utf-8"))["base"]
        for token in ("diff_add_word_bg", "diff_remove_word_bg"):
            with self.subTest(token=token):
                self.assertGreaterEqual(contrast_ratio(base["foreground"], base[token]), 4.5)

    def test_vscode_syntax_colors_on_word_diffs_clear_aa(self):
        for relative, color_key in (
            ("vscode/tokencat.vscode-theme.json", "colors"),
            ("vscode/tokencat-color-customizations.json", "workbench.colorCustomizations"),
        ):
            data = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            colors = data[color_key]
            foregrounds = {"editor.foreground": colors["editor.foreground"]}
            if color_key == "colors":
                comment_rules = []
                for rule in data["tokenColors"]:
                    scope = rule["scope"]
                    scopes = scope if isinstance(scope, list) else [scope]
                    foreground = rule["settings"].get("foreground")
                    if foreground:
                        foregrounds[", ".join(scopes)] = foreground
                        if "comment" in scopes:
                            comment_rules.append(foreground)
                self.assertTrue(comment_rules, "comment foreground must be explicitly tested")
            else:
                token_colors = data["editor.tokenColorCustomizations"]
                self.assertIn("comments", token_colors)
                foregrounds.update(token_colors)
            for role, foreground in foregrounds.items():
                for background in (
                    "diffEditor.insertedTextBackground",
                    "diffEditor.removedTextBackground",
                ):
                    with self.subTest(export=relative, role=role, background=background):
                        self.assertGreaterEqual(contrast_ratio(foreground, colors[background]), 4.5)

    def test_emitted_skin_text_and_diff_pairs_clear_aa(self):
        skin = _parse_skin((ROOT / "hermes/skins/tokencat.yaml").read_text(encoding="utf-8"))
        colors = skin["colors"]
        pairs = (
            ("ui_text", "background"),
            ("ui_primary", "background"),
            ("ui_thinking", "background"),
            ("banner_dim", "background"),
            ("syntax_comment", "background"),
            ("status_bar_text", "status_bar_bg"),
            ("status_bar_dim", "status_bar_bg"),
            ("status_bar_good", "status_bar_bg"),
            ("status_bar_warn", "status_bar_bg"),
            ("status_bar_bad", "status_bar_bg"),
            ("diff_added_word", "diff_added"),
            ("diff_removed_word", "diff_removed"),
        )
        for foreground, background in pairs:
            with self.subTest(foreground=foreground, background=background):
                self.assertGreaterEqual(contrast_ratio(colors[foreground], colors[background]), 4.5)


@unittest.skipUnless(os.environ.get("TOKENCAT_HERMES_SOURCE"), "native Hermes source not supplied")
class NativeCliContrastTests(unittest.TestCase):
    def test_native_selected_completion_metadata_clears_aa(self):
        source = Path(os.environ["TOKENCAT_HERMES_SOURCE"])
        spec = importlib.util.spec_from_file_location(
            "tokencat_native_skin_engine", source / "hermes_cli/skin_engine.py"
        )
        module = importlib.util.module_from_spec(spec)
        # Load the native skin module without agent/server bootstrap or reading
        # the active profile; inject this candidate at the existing boundary.
        with (
            patch.object(sys, "path", [str(source), *sys.path]),
            patch.dict(sys.modules, {module.__name__: module}),
        ):
            spec.loader.exec_module(module)
            skin = _parse_skin((ROOT / "hermes/skins/tokencat.yaml").read_text(encoding="utf-8"))
            candidate = module._build_skin_config(skin)
            with patch.object(module, "get_active_skin", return_value=candidate):
                styles = module.get_prompt_toolkit_style_overrides()
        actual = styles["completion-menu.meta.completion.current"]
        background, foreground = actual.split()
        self.assertEqual(foreground, skin["colors"]["ui_label"])
        self.assertEqual(background, "bg:" + skin["colors"]["completion_menu_meta_current_bg"])
        self.assertGreaterEqual(contrast_ratio(foreground, background.removeprefix("bg:")), 4.5)
