"""The cross-surface SSOT must carry typography, not just colour.

Regression guard for a real defect: `_rows_from_mapping` matches hex values only,
so every font row was silently dropped from the SSOT — the table had 0 font rows
while four surfaces declared fonts. The owner's ASK names font explicitly.
"""

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "docs" / "ssot-tokencat.csv"
FONTS = ROOT / "docs" / "fonts.json"


def _rows():
    with CSV.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class SsotTypographyTests(unittest.TestCase):
    def test_csv_exists_and_has_the_expected_header(self):
        self.assertTrue(CSV.is_file(), "run scripts/ssot_table.py")
        with CSV.open(encoding="utf-8", newline="") as fh:
            header = next(csv.reader(fh))
        self.assertEqual(header, ["surface", "file", "category", "key", "value", "base_token"])

    def test_ssot_carries_font_rows(self):
        font = [r for r in _rows() if r["category"] == "font"]
        self.assertGreater(
            len(font), 0, "font rows vanished from the SSOT — check rows_fonts() wiring"
        )

    def test_every_font_declaring_surface_is_represented(self):
        surfaces = {r["surface"] for r in _rows() if r["category"] == "font"}
        for expected in ("vscode", "zed", "wezterm", "hermes-dashboard"):
            self.assertIn(expected, surfaces, f"{expected} font settings missing from SSOT")

    def test_no_duplicate_font_rows(self):
        keys = [(r["surface"], r["file"], r["key"]) for r in _rows() if r["category"] == "font"]
        self.assertEqual(len(keys), len(set(keys)), "duplicate font rows in SSOT")

    def test_zed_syntax_attributes_are_not_mistaken_for_typography(self):
        """`font_style`/`font_weight` are per-token syntax rules, not typography."""
        font_keys = [r["key"] for r in _rows() if r["category"] == "font"]
        offenders = [k for k in font_keys if ".syntax." in k or k.endswith("_style")]
        self.assertEqual(offenders, [], f"syntax attributes leaked into typography: {offenders}")

    def test_fonts_json_is_valid_and_names_only_real_surfaces(self):
        data = json.loads(FONTS.read_text(encoding="utf-8"))
        self.assertIn("surfaces", data)
        self.assertGreater(len(data["surfaces"]), 0)
        for surface in data["surfaces"]:
            self.assertTrue(surface, "empty surface name in docs/fonts.json")

    def test_csv_generator_uses_lf_line_endings(self):
        import tempfile

        from scripts.ssot_table import write_csv

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ssot.csv"
            write_csv([], path)
            self.assertEqual(path.read_bytes(), b"surface,file,category,key,value,base_token\n")
        self.assertIn("*.csv text eol=lf", (ROOT / ".gitattributes").read_text())

    def test_markdown_generator_uses_lf_and_one_final_newline(self):
        import tempfile

        from scripts.ssot_table import write_md

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ssot.md"
            write_md([], path)
            data = path.read_bytes()
            self.assertNotIn(b"\r", data)
            self.assertTrue(data.endswith(b"\n"))
            self.assertFalse(data.endswith(b"\n\n"))

    def test_regenerator_is_deterministic(self):
        """Re-running the generator must preserve both generated files byte for byte."""
        import subprocess
        import sys

        paths = (CSV, ROOT / "docs" / "ssot-tokencat.md")
        before = {path: path.read_bytes() for path in paths}
        subprocess.run(
            [sys.executable, "scripts/ssot_table.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        for path in paths:
            self.assertEqual(
                before[path], path.read_bytes(), f"{path.name} drifted on regeneration"
            )


if __name__ == "__main__":
    unittest.main()
