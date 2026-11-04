"""Validate the portable Tokencat theme bundle."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

if __package__:
    from .export_contract import validate_exports
    from .theme_io import strict_json, strict_yaml
else:
    from export_contract import validate_exports
    from theme_io import strict_json, strict_yaml

CANONICAL_COLOR_KEYS = (
    "background",
    "banner_border",
    "banner_title",
    "banner_accent",
    "banner_dim",
    "banner_text",
    "ui_accent",
    "ui_label",
    "ui_ok",
    "ui_error",
    "ui_warn",
    "ui_tool",
    "ui_thinking",
    "diff_added",
    "diff_removed",
    "diff_added_word",
    "diff_removed_word",
    "syntax_string",
    "syntax_number",
    "syntax_keyword",
    "syntax_comment",
    "prompt",
    "input_rule",
    "response_border",
    "status_bar_bg",
    "status_bar_text",
    "status_bar_strong",
    "status_bar_dim",
    "status_bar_good",
    "status_bar_warn",
    "status_bar_bad",
    "status_bar_critical",
    "session_label",
    "session_border",
    "voice_status_bg",
    "selection_bg",
    "completion_menu_bg",
    "completion_menu_current_bg",
    "completion_menu_meta_bg",
    "completion_menu_meta_current_bg",
    "shell_dollar",
    "ui_primary",
    "ui_text",
    "ui_border",
)

# Pinned semantic roles: the few mappings that define the theme's colour
# grammar. Everything else is checked against palettes/tokencat.json's own mapping, which
# is the single source of truth for the rest of the contract.
SEMANTIC_MAPPINGS = tuple(
    {"skin": skin, "palette": palette}
    for skin, palette in {
        "background": "background",
        "banner_text": "foreground",
        "banner_dim": "muted_accessible",
        "ui_accent": "blue",
        "ui_label": "cyan",
        "ui_tool": "cyan_bright",
        "ui_ok": "green",
        "ui_error": "red",
        "ui_warn": "orange",
        "syntax_string": "green",
        "syntax_keyword": "purple",
        "syntax_comment": "muted_accessible",
        "input_rule": "border",
        "status_bar_bg": "background_alt",
    }.items()
)

# Portable-path check: match ANY local user path (<drive>:\Users\<name>,
# /Users/<name>, /home/<name>) instead of hardcoding one machine's username,
# plus the unsubstituted <USER> placeholder.
USER_PATH_RE = re.compile(
    r"(?:[A-Za-z]:)?[\\/]{1,2}[Uu]sers[\\/]{1,2}[^\\/\s\"']+"
    r"|/(?:home|root)/[^/\s\"']+"
)
PLACEHOLDER_MARKERS = ("<USER>",)
JSON_FILES = (
    "palettes/tokencat.json",
    "vscode/tokencat.vscode-theme.json",
    "vscode/tokencat-color-customizations.json",
    "windows-terminal/tokencat.scheme.json",
    "windows-terminal/theme.json",
    "palette.json",
    "windows-terminal/scheme.json",
    "vscode/carbonfox.vscode-theme.json",
    "vscode/vscode-color-customizations.json",
    "vscode/package.json",
    "zed/tokencat.json",
)


def _parse_skin(text: str, name: str = "tokencat") -> dict[str, Any]:
    data = strict_yaml(text)
    if not isinstance(data, dict):
        raise ValueError("skin must be an object")
    if data.get("name") != name:
        raise ValueError(f"skin name must be {name}")
    colors = data.get("colors")
    if not isinstance(colors, dict) or not colors:
        raise ValueError("missing colors map")
    for key, value in colors.items():
        if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValueError(f"invalid six-digit color: {key}")
    for key in ("banner_logo", "banner_hero"):
        if key in data and not isinstance(data[key], str):
            raise ValueError(f"{key} must be a string")
    return data


def _plain_hero(hero: str) -> list[str]:
    return [re.sub(r"\[[^]]*\]", "", row).rstrip() for row in hero.splitlines()]


def _source_hero(root: Path) -> list[str] | None:
    source_path = root / "ascii-art/lucky-cat-29x11.txt"
    if not source_path.exists():
        return None
    source = source_path.read_text(encoding="utf-8").splitlines()
    return [row.replace("hjw", "$TOKENS").rstrip() for row in source]


def _distributable_files(root: Path) -> list[Path]:
    files = list(root.glob("*.md"))
    files.append(root / "palette.json")
    for directory in (
        "palettes",
        "hermes",
        "ascii-art",
        "fonts",
        "vscode",
        "zed",
        "windows-terminal",
        "wezterm",
        "zellij",
        "licenses",
        "docs",
    ):
        base = root / directory
        if base.is_dir():
            files.extend(p for p in base.rglob("*") if p.is_file())
    return sorted(set(p for p in files if p.is_file()))


def check_palette_shape(data):
    if not isinstance(data, dict):
        raise ValueError("palette must be an object")
    base, mappings = data.get("base"), data.get("mappings")
    if not isinstance(base, dict) or not isinstance(mappings, dict):
        raise ValueError("base and mappings must be objects")
    hermes = mappings.get("hermes")
    if not isinstance(hermes, dict):
        raise ValueError("mappings.hermes must be an object")
    if not all(
        isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?", v)
        for v in base.values()
    ):
        raise ValueError("base tokens must be six- or eight-digit hex strings")
    if not all(isinstance(v, str) for v in hermes.values()):
        raise ValueError("Hermes mappings must reference named tokens")
    return data


REQUIRED_FILES = (
    "palette.json",
    "hermes/skins/carbonfox.yaml",
    "windows-terminal/scheme.json",
    "vscode/carbonfox.vscode-theme.json",
    "vscode/vscode-color-customizations.json",
    "palettes/tokencat.json",
    "hermes/skins/tokencat.yaml",
    "ascii-art/token-cat-29x11.txt",
    "ascii-art/lucky-cat-29x11.txt",
    "ascii-art/token-cat-two-tone.rich.txt",
    "windows-terminal/tokencat.scheme.json",
    "windows-terminal/theme.json",
    "vscode/tokencat.vscode-theme.json",
    "vscode/tokencat-color-customizations.json",
    "hermes/dashboard-themes/tokencat.yaml",
    "wezterm/tokencat.toml",
    "zellij/tokencat.kdl",
    "vscode/package.json",
)


def _validate_vscode_manifest(root: Path) -> list[str]:
    violations = []
    try:
        manifest = strict_json((root / "vscode/package.json").read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or not isinstance(manifest.get("contributes"), dict):
            raise ValueError("manifest contributions must be an object")
        themes = manifest["contributes"].get("themes")
        if not isinstance(themes, list) or not all(isinstance(item, dict) for item in themes):
            raise ValueError("themes must be an array of objects")
        if len(themes) != 1 or themes[0] != {
            "label": "Tokencat",
            "uiTheme": "vs-dark",
            "path": "./tokencat.vscode-theme.json",
        }:
            violations.append("vscode/package.json: Tokencat must be the only selectable theme")
        if (root / "vscode/carbonfox.vscode-theme.json").is_file() is False:
            violations.append("vscode/package.json: legacy Carbonfox payload must be retained")
    except (OSError, ValueError) as exc:
        violations.append(f"vscode/package.json: invalid manifest ({exc})")
    return violations


def validate_repository(root: Path) -> list[str]:
    violations: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            violations.append(f"missing required artifact: {relative}")
    skin_path = root / "hermes/skins/tokencat.yaml"
    palette_path = root / "palettes/tokencat.json"
    try:
        skin_text = skin_path.read_text(encoding="utf-8")
        skin = _parse_skin(skin_text)
    except (OSError, ValueError) as exc:
        violations.append(f"hermes/skins/tokencat.yaml: invalid skin ({exc})")
        skin = {}
    try:
        palette = check_palette_shape(strict_json(palette_path.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        violations.append(f"palettes/tokencat.json: invalid JSON ({exc})")
        palette = {}
    if not isinstance(skin.get("banner_hero"), str) or not skin["banner_hero"].strip():
        violations.append("skin missing required banner_hero")
    colors = skin.get("colors", {}) if isinstance(skin, dict) else {}
    for key in CANONICAL_COLOR_KEYS:
        if key not in colors:
            violations.append(f"skin missing required color: {key}")
    if isinstance(skin, dict) and skin.get("banner_logo") != " ":
        violations.append("banner_logo must be exactly one space")
    if isinstance(skin, dict) and "banner_hero" in skin:
        expected = _source_hero(root)
        if expected is not None and _plain_hero(str(skin["banner_hero"])) != expected:
            violations.append("banner_hero does not match token-cat source")
    palette_base = palette.get("base", {}) if isinstance(palette, dict) else {}
    palette_hermes = (
        palette.get("mappings", {}).get("hermes", {}) if isinstance(palette, dict) else {}
    )
    if set(palette_hermes) != set(CANONICAL_COLOR_KEYS):
        violations.append("palette Hermes mapping must cover every canonical skin color")
    for mapping in SEMANTIC_MAPPINGS:
        if palette_hermes.get(mapping["skin"]) != mapping["palette"]:
            violations.append(f"semantic role changed: {mapping['skin']} -> {mapping['palette']}")
    for key, token in palette_hermes.items():
        if token not in palette_base:
            violations.append(f"palette missing mapped base token: {key} -> {token}")
        elif key in colors and colors[key].lower() != palette_base[token].lower():
            violations.append(
                f"skin/palette drift: {key} {colors[key]} != {token} {palette_base[token]}"
            )
    for name in JSON_FILES:
        path = root / name
        if path.exists():
            try:
                document = strict_json(path.read_text(encoding="utf-8"))
                if not isinstance(document, dict):
                    raise ValueError("JSON artifact must be an object")
            except (OSError, ValueError) as exc:
                violations.append(f"{name}: invalid JSON ({exc})")

    for path in _distributable_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for marker in PLACEHOLDER_MARKERS:
            if marker in text:
                violations.append(
                    f"{path.relative_to(root)}: contains non-portable marker {marker}"
                )
        for match in USER_PATH_RE.finditer(text):
            violations.append(
                f"{path.relative_to(root)}: contains non-portable marker {match.group(0)}"
            )
    violations.extend(validate_exports(root))
    violations.extend(_validate_vscode_manifest(root))
    return violations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    violations = validate_repository(args.root.resolve())
    if violations:
        print("\n".join(f"FAIL: {item}" for item in violations))
        return 1
    print("PASS: hermesfox theme validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
