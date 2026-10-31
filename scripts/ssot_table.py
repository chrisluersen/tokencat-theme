"""Emit the Tokencat cross-surface SSOT table (CSV + markdown).

Every colour that ships for every surface, in one long-format table, so drift
between surfaces is visible instead of inferred. Read-only: this script never
writes a theme file.

Usage:
    python scripts/ssot_table.py

Writes:
    docs/ssot-tokencat.csv
    docs/ssot-tokencat.md
"""

from __future__ import annotations

import csv
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

try:
    import yaml
except ImportError:  # pragma: no cover - documented dev dependency
    yaml = None

HEX = re.compile(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?\Z")
FIELDS = ("surface", "file", "category", "key", "value", "base_token")


# ---------------------------------------------------------------- collectors


def _walk(value, prefix=""):
    """Flatten nested dicts/lists into (json-pointer, leaf) pairs."""
    if isinstance(value, dict):
        for k, v in value.items():
            key = str(k).replace("~", "~0").replace("/", "~1")
            yield from _walk(v, f"{prefix}/{key}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _walk(v, f"{prefix}/{i}")
    else:
        yield prefix, value


def _rows_from_mapping(surface, rel, data, skip=()):
    """One row per hex leaf, with its dotted key and pointer."""
    rows = []
    for pointer, leaf in _walk(data):
        if not isinstance(leaf, str) or not HEX.fullmatch(leaf):
            continue
        dotted = pointer.strip("/").replace("/", ".")
        if any(dotted.startswith(s) for s in skip):
            continue
        parts = pointer.strip("/").split("/")
        category = parts[0] if parts else ""
        rows.append(
            {
                "surface": surface,
                "file": rel,
                "category": category,
                "key": dotted,
                "value": leaf,
                "base_token": "",
            }
        )
    return rows


def rows_palette(rel, data):
    rows = []
    for token, leaf in sorted(data.get("base", {}).items()):
        rows.append(
            {
                "surface": "palette (SSOT)",
                "file": rel,
                "category": "base",
                "key": f"base.{token}",
                "value": leaf,
                "base_token": token,
            }
        )
    for app, mapping in sorted(data.get("mappings", {}).items()):
        for role, token in sorted(mapping.items()):
            rows.append(
                {
                    "surface": f"palette (SSOT) > {app}",
                    "file": rel,
                    "category": "mapping",
                    "key": f"mappings.{app}.{role}",
                    "value": data.get("base", {}).get(token, "?"),
                    "base_token": token,
                }
            )
    return rows


def rows_export_pointers(rel, data):
    """Every shipped export pointer, resolved to its base token and hex."""
    rows = []
    base = data.get("base", {})
    for target, mapping in sorted(data.get("exports", {}).items()):
        for pointer, token in sorted(mapping.items()):
            rows.append(
                {
                    "surface": "export contract",
                    "file": target,
                    "category": "pointer",
                    "key": pointer,
                    "value": base.get(token, "?"),
                    "base_token": token,
                }
            )
    return rows


def rows_kdl_theme(surface, rel, text):
    """Parse a zellij theme: nested role blocks holding `key R G B` triplets."""
    rows = []
    theme = re.search(r"themes\s*\{\s*([A-Za-z0-9_-]+)\s*\{(.*)\n\s*\}\s*\}\s*$", text, re.S)
    name, body = (theme.group(1), theme.group(2)) if theme else ("theme", text)
    for role, role_body in re.findall(r"([A-Za-z0-9_-]+)\s*\{([^{}]*)\}", body, re.S):
        for key, r, g, b in re.findall(
            r"([A-Za-z0-9_.-]+)\s+(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})\b", role_body
        ):
            hexv = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            rows.append(
                {
                    "surface": surface,
                    "file": rel,
                    "category": f"zellij:{name}.{role}",
                    "key": f"{role}.{key}",
                    "value": hexv,
                    "base_token": "",
                }
            )
    return rows


# ------------------------------------------------------------------ sources


def collect():
    rows = []

    p = ROOT / "palettes" / "tokencat.json"
    if p.is_file():
        data = json.loads(p.read_text(encoding="utf-8"))
        rows += rows_palette("palettes/tokencat.json", data)
        rows += rows_export_pointers("palettes/tokencat.json", data)

    # VS Code (generated exports + hand-maintained legacy)
    for rel in ("vscode/tokencat.vscode-theme.json", "vscode/carbonfox.vscode-theme.json"):
        p = ROOT / rel
        if p.is_file():
            rows += _rows_from_mapping("vscode", rel, json.loads(p.read_text(encoding="utf-8")))

    # Zed
    p = ROOT / "zed" / "tokencat.json"
    if p.is_file():
        zdata = json.loads(p.read_text(encoding="utf-8"))
        for theme in zdata.get("themes", []):
            rows += _rows_from_mapping("zed", "zed/tokencat.json", theme.get("style", {}))

    # WezTerm
    p = ROOT / "wezterm" / "tokencat.toml"
    if p.is_file():
        rows += _rows_from_mapping(
            "wezterm", "wezterm/tokencat.toml", tomllib.loads(p.read_text(encoding="utf-8"))
        )

    # Windows Terminal
    for rel in (
        "windows-terminal/tokencat.scheme.json",
        "windows-terminal/scheme.json",
        "windows-terminal/hermesfox.scheme.json",
    ):
        p = ROOT / rel
        if p.is_file():
            rows += _rows_from_mapping(
                "windows-terminal", rel, json.loads(p.read_text(encoding="utf-8"))
            )

    # Zellij
    p = ROOT / "zellij" / "tokencat.kdl"
    if p.is_file():
        rows += rows_kdl_theme("zellij", "zellij/tokencat.kdl", p.read_text(encoding="utf-8"))

    # Hermes skins + dashboard
    if yaml is not None:
        for rel in (
            "hermes/skins/tokencat.yaml",
            "hermes/skins/carbonfox.yaml",
            "hermes/skins/hermesfox.yaml",
            "hermes/dashboard-themes/tokencat.yaml",
        ):
            p = ROOT / rel
            if p.is_file():
                surface = "hermes-dashboard" if "dashboard" in rel else "hermes-skin"
                rows += _rows_from_mapping(
                    surface, rel, yaml.safe_load(p.read_text(encoding="utf-8"))
                )

    return rows


# ------------------------------------------------------------------- output


def write_csv(rows, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["surface"], r["file"], r["category"], r["key"])):
            w.writerow(r)


def write_md(rows, dest: Path):
    by_surface: dict[str, list[dict]] = {}
    for r in rows:
        by_surface.setdefault(r["surface"], []).append(r)

    out = ["# Tokencat — cross-surface SSOT", ""]
    out.append(
        "Generated by `scripts/ssot_table.py`. Every colour that ships, per surface. "
        "Regenerate rather than hand-edit."
    )
    out.append("")
    out.append("| Surface | File | Keys |")
    out.append("|---|---|---|")
    for surf in sorted(by_surface):
        files = sorted({r["file"] for r in by_surface[surf]})
        out.append(f"| {surf} | {', '.join(f'`{f}`' for f in files)} | {len(by_surface[surf])} |")
    out.append("")

    # base token table with the surfaces that consume each token
    consumers: dict[str, set[str]] = {}
    for r in rows:
        if r["base_token"]:
            consumers.setdefault(r["base_token"], set()).add(r["surface"])
    base = {}
    for r in rows:
        if r["category"] == "base":
            base[r["base_token"]] = r["value"]
    if base:
        out.append("## Base tokens (the single source of truth)")
        out.append("")
        out.append("| Token | Hex | Consumed by |")
        out.append("|---|---|---|")
        for token in sorted(base):
            used = ", ".join(sorted(consumers.get(token, []))) or "—"
            out.append(f"| `{token}` | `{base[token]}` | {used} |")
        out.append("")

    out.append("## Per-surface key inventory")
    out.append("")
    for surf in sorted(by_surface):
        out.append(f"### {surf}")
        out.append("")
        out.append("| Key | Value | Base token | File |")
        out.append("|---|---|---|---|")
        for r in sorted(by_surface[surf], key=lambda r: (r["file"], r["key"])):
            out.append(
                f"| `{r['key']}` | `{r['value']}` | {r['base_token'] or '—'} | `{r['file']}` |"
            )
        out.append("")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    rows = collect()
    write_csv(rows, ROOT / "docs" / "ssot-tokencat.csv")
    write_md(rows, ROOT / "docs" / "ssot-tokencat.md")
    surfaces = sorted({r["surface"] for r in rows})
    print(f"rows={len(rows)} surfaces={len(surfaces)}")
    for s in surfaces:
        print(f"   {s:34} {sum(1 for r in rows if r['surface'] == s)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
