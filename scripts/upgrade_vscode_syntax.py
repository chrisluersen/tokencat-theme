"""Upgrade vscode/tokencat.vscode-theme.json to the 14-colour Zed syntax map.

Source of truth for every value is palettes/tokencat.json. This script:
  1. adds the base tokens the richer syntax map needs,
  2. rewrites the VS Code tokenColors to the full Zed semantic set,
  3. backfills the Zed chrome keys that have a real VS Code workbench token,
  4. regenerates the export pointers by reverse-mapping hex -> base token,
     so the export contract can never fall out of coverage.

Run once; the palette remains the thing you edit afterwards.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAL = ROOT / "palettes" / "tokencat.json"
VS = ROOT / "vscode" / "tokencat.vscode-theme.json"

# --------------------------------------------------------------- new tokens
NEW_BASE = {
    "syntax_escape": "#5ae0df",
    "syntax_import": "#ff91c1",
    "disabled": "#6e6f70",
    "info_bg": "#252c39",
    "hint_bg": "#1c3433",
    "selection_a": "#2a2a2a8C",
    "border_a": "#525253E3",
    "cyan_bright_a": "#3ddbd957",
    "accent_a": "#78a9ff57",
    "green_a": "#25be6a8C",
    "shadow": "#0000008C",
}

# ------------------------------------------------- chrome additions (VS Code
# workbench tokens that genuinely exist; values are base-token names)
NEW_CHROME = {
    "editorGutter.background": "background",
    "editorWhitespace.foreground": "whitespace",
    "editorOverviewRuler.border": "background_alt",
    "editorGroup.border": "background",
    "editorGroupHeader.border": "surface",
    "editorWidget.shadow": "shadow",
    "editorSuggestWidget.border": "border",
    "sideBar.border": "background",
    "sideBarTitle.foreground": "foreground",
    "activityBar.border": "background",
    "activityBar.inactiveForeground": "muted_accessible",
    "titleBar.border": "background",
    "statusBar.border": "background",
    "statusBarItem.remoteBackground": "background_alt",
    "tab.border": "background_alt",
    "tab.activeBorderTop": "blue",
    "tab.unfocusedActiveBorderTop": "border",
    "tab.hoverBackground": "surface",
    "panelTitle.activeForeground": "foreground",
    "panelTitle.activeBorder": "blue",
    "panelTitle.inactiveForeground": "muted_accessible",
    "scrollbarSlider.background": "selection_a",
    "scrollbarSlider.hoverBackground": "border_a",
    "scrollbarSlider.activeBackground": "cyan_bright_a",
    "minimap.background": "background",
    "minimapSlider.background": "selection_a",
    "minimapSlider.hoverBackground": "border_a",
    "minimapSlider.activeBackground": "cyan_bright_a",
    "badge.background": "blue",
    "badge.foreground": "background",
    "checkbox.background": "surface",
    "checkbox.border": "border",
    "dropdown.background": "surface",
    "dropdown.border": "border",
    "menu.background": "surface",
    "menu.foreground": "foreground",
    "menu.selectionBackground": "surface_selected",
    "menu.selectionForeground": "foreground",
    "menu.border": "border",
    "quickInput.background": "surface",
    "quickInput.foreground": "foreground",
    "peekViewEditor.background": "background",
    "peekViewResult.background": "background_alt",
    "peekView.border": "border",
    "textLink.foreground": "ansi_brightBlue",
    "textLink.activeForeground": "blue",
    "textPreformat.foreground": "green",
    "gitDecoration.untrackedResourceForeground": "green",
    "gitDecoration.ignoredResourceForeground": "disabled",
    "gitDecoration.conflictingResourceForeground": "orange",
    "gitDecoration.submoduleResourceForeground": "teal",
    "editorError.background": "diff_remove_bg",
    "editorWarning.background": "diff_remove_bg",
    "editorInfo.background": "info_bg",
    "editorHint.background": "hint_bg",
    "debugToolBar.background": "surface",
    "editor.stackFrameHighlightBackground": "cyan_bright_a",
    "editor.focusedStackFrameHighlightBackground": "accent_a",
    "terminal.selectionBackground": "selection_a",
    "terminal.findMatchBackground": "accent_a",
    "terminal.border": "border",
    "widget.border": "border",
    "inputValidation.errorBackground": "diff_remove_bg",
    "inputValidation.errorBorder": "red",
    "inputValidation.infoBackground": "info_bg",
    "inputValidation.infoBorder": "blue",
    "notifications.border": "border",
    "notificationCenterHeader.background": "surface",
    "settings.headerForeground": "foreground",
    "settings.modifiedItemIndicator": "blue",
    "list.hoverBackground": "surface",
    "list.highlightForeground": "cyan_bright",
    "list.errorForeground": "red",
    "list.warningForeground": "orange",
    "editorMarkerNavigation.background": "surface",
}

# --------------------------------------------------- tokenColors (Zed parity)
TOKEN_RULES = [
    (["comment", "punctuation.definition.comment"], "muted_accessible"),
    (["string", "constant.other.placeholder"], "green"),
    (["constant.numeric", "constant.language.null", "constant.language"], "cyan_bright"),
    (["constant.language.boolean"], "syntax_escape"),
    (["keyword", "storage", "storage.type"], "purple"),
    (["keyword.import", "keyword.control.import", "meta.preprocessor"], "syntax_import"),
    (["keyword.directive", "keyword.operator.regex"], "ansi_brightBlue"),
    (
        ["keyword.operator", "punctuation", "punctuation.separator", "punctuation.terminator"],
        "muted_accessible",
    ),
    (["entity.name.type", "support.type", "entity.name.namespace"], "blue"),
    (["entity.name.function", "support.function"], "cyan"),
    (["support.function.builtin", "entity.name.function.builtin"], "ansi_brightRed"),
    (["variable", "meta.definition.variable", "variable.other"], "foreground"),
    (["variable.language"], "ansi_brightRed"),
    (["entity.name.tag"], "purple"),
    (["entity.name.tag.doctype"], "syntax_escape"),
    (["entity.other.attribute-name"], "blue"),
    (
        ["meta.decorator", "punctuation.decorator", "entity.name.function.decorator"],
        "syntax_escape",
    ),
    (["string.escape", "constant.character.escape"], "syntax_escape"),
    (["string.regex", "constant.regexp"], "ansi_brightYellow"),
    (["string.special"], "ansi_brightCyan"),
    (["selector", "entity.other.attribute-name.class", "entity.other.attribute-name.id"], "teal"),
    (["markup.italic", "markup.bold", "markup.emphasis", "markup.strong"], "ansi_brightRed"),
    (["markup.underline.link", "string.other.link"], "ansi_brightBlue"),
    (["invalid", "invalid.illegal"], "ansi_brightRed"),
]


def main() -> int:
    pal = json.loads(PAL.read_text(encoding="utf-8"))
    base = pal["base"]
    for k, v in NEW_BASE.items():
        if k in base and base[k] != v:
            raise SystemExit(f"token collision: {k} exists as {base[k]}, wanted {v}")
        base[k] = v

    theme = json.loads(VS.read_text(encoding="utf-8"))
    colors = theme["colors"]
    for key, token in NEW_CHROME.items():
        colors[key] = base[token]

    theme["tokenColors"] = [
        {"scope": scopes, "settings": {"foreground": base[token]}} for scopes, token in TOKEN_RULES
    ]

    # --- regenerate export pointers by reverse-mapping hex -> token
    rev = {}
    for token, hexv in base.items():
        rev.setdefault(hexv.lower(), token)

    def pointers(data, prefix=""):
        out = {}
        if isinstance(data, dict):
            for k, v in data.items():
                out.update(pointers(v, f"{prefix}/{str(k).replace('~', '~0').replace('/', '~1')}"))
        elif isinstance(data, list):
            for i, v in enumerate(data):
                out.update(pointers(v, f"{prefix}/{i}"))
        elif isinstance(data, str) and data.startswith("#"):
            token = rev.get(data.lower())
            if token is None:
                raise SystemExit(f"no base token for {data} at {prefix}")
            out[prefix] = token
        return out

    vs_pointers = pointers(theme)
    pal["exports"]["vscode/tokencat.vscode-theme.json"] = vs_pointers

    # the merge fragment mirrors the colours + the 6 coarse token customisations
    frag = json.loads((ROOT / "vscode" / "tokencat-color-customizations.json").read_text("utf-8"))
    frag["workbench.colorCustomizations"] = dict(colors)
    frag["editor.tokenColorCustomizations"] = {
        "comments": base["muted_accessible"],
        "strings": base["green"],
        "numbers": base["cyan_bright"],
        "keywords": base["purple"],
        "types": base["blue"],
        "functions": base["cyan"],
        "variables": base["foreground"],
    }
    frag_pointers = pointers(frag)
    pal["exports"]["vscode/tokencat-color-customizations.json"] = frag_pointers

    VS.write_text(json.dumps(theme, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "vscode" / "tokencat-color-customizations.json").write_text(
        json.dumps(frag, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    PAL.write_text(json.dumps(pal, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"base tokens      : {len(base)}")
    print(f"chrome keys      : {len(colors)}")
    print(f"tokenColors rules: {len(theme['tokenColors'])}")
    print(f"vs pointers      : {len(vs_pointers)}")
    print(f"fragment pointers: {len(frag_pointers)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
