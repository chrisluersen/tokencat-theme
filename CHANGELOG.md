# Changelog

## Unreleased

- **Collapsed the VS Code picker to Tokencat alone** (owner decision). The
  `Hermesfox` and `Carbonfox (Legacy)` label aliases both pointed at
  `carbonfox.vscode-theme.json` and shipped identical syntax, so they were three
  menu entries for one appearance. `vscode/carbonfox.vscode-theme.json` is
  retained on disk, unlisted, for restore. Hermesfox keeps its own Hermes skin,
  Windows Terminal scheme and branding — only the VS Code label was removed.
- **Ported Zed's full syntax map into VS Code**: `tokenColors` grew 7 → 24 rules
  covering imports/preprocessor, directives, regex, escapes, decorators, doctype,
  selectors, attributes, tags, markup and invalid, so both editors render the same
  token semantics rather than a coarse superset.
- **Split boolean from number.** `constant.language.boolean` no longer shares
  `cyan_bright` with `constant.numeric`; it uses the new `syntax_escape` token
  (`#5ae0df`), matching the Zed theme.
- **Shipped the Zed surface in-repo** as `zed/tokencat.json` (138 style keys, 57
  syntax roles) with `tests/test_zed_theme.py`. It previously existed only in the
  user's Zed config directory and was unreproducible from the repository.
- Added `scripts/ssot_table.py` and `docs/ssot-tokencat.csv` / `.md`: every colour
  key for every surface in one generated table, so cross-surface drift is visible
  instead of inferred. Regenerate rather than hand-edit.
- Backfilled the Zed chrome roles that have a genuine VS Code workbench token
  (scrollbars, minimap, badge, checkbox, dropdown, menu, peek, git decoration,
  error/info/hint backgrounds, debug toolbar and stack-frame highlights).
- Extended the palette schema to accept 8-digit `#RRGGBBAA` base tokens, since the
  design uses alpha for sliders, selections and multiplayer cursors.
- Added `backups/2026-10-31/` — a hash-manifested snapshot of every **theme
  artefact** on disk for every surface, including the out-of-repo installed
  copies. Personal application config (VS Code / Windows Terminal `settings.json`,
  Zellij `config.kdl`, `wezterm.lua`) is deliberately excluded and `.gitignore`-
  guarded, because this repository is public and settings files are not themes.
- Renamed the repository to `tokencat-theme`; added agent setup instructions,
  default/Carbonfox comparisons and an environment-independent WezTerm example.
- Added Hermesfox: original Carbonfox colors, unchanged current token-cat banner
  and explicit Hermesfox top title. Added its Windows Terminal name and VS Code
  selector, preserving the archived Carbonfox files and backward-compatible label.
- Darkened only Tokencat's VS Code word-diff backgrounds to keep syntax-colored
  comments readable, with emitted-role contrast guards and old-color counterexamples.
- Added an explicit green added-word border so the darker highlight remains
  distinguishable from whole-line shading; preserved comment colors and all legacy exports.
- Added the separately selectable Tokencat upgrade, preserving the Carbonfox
  palette, companion exports and original artwork without changing their bytes.
- Added mapped Hermes/dashboard, Windows Terminal and VS Code upgrade exports,
  strict parsing, provenance and contrast checks, and cross-platform CI.
- Made VS Code selected suggestion text and focused-match colors explicit in
  both upgrade exports; regression tests require AA text contrast in each state.
- Corrected palette documentation and scoped historical runtime evidence;
  cross-surface runtime acceptance remains incomplete.
- Added standalone WezTerm TOML and Zellij modern-role KDL exports, complete
  palette mappings, strict emitted-structure checks and malformed-input coverage.
- Verified changed VS Code suggestion states through switching and cold restart,
  WezTerm native loading/ANSI rendering, and current pure Hermes consumers;
  full app acceptance limits remain explicit in the compatibility matrix.
- Fixed CLI selected completion metadata contrast using the existing darker
  surface token, with emitted-role and optional actual-native style regressions.
- Narrowed VS Code preservation claims to measured files and disclosed that
  existing shared storage was opened without a before-image.
- Restricted emitted KDL RGB digits to ASCII and added WezTerm/Zellij contrast
  coverage with low-contrast foreground counterexamples.

### Retained Carbonfox changes

- Hermes colour roles: blue = chrome, cyan = labels, teal = tool calls, dimmed
  purple = reasoning, gray = passive rules. Syntax and diff colours now follow
  nightfox's own spec (green strings, magenta keywords, tinted diff rows), and
  surfaces follow nvim (statusline bg0, popup sel0/sel1). Added `shell_dollar`.
- Added a two-tone token-cat variant (cat purple→pink, box blue→teal), staged
  until the TUI renders multi-colour banner rows.
- Validation checks Carbonfox against `palette.json` and Tokencat against
  `palettes/tokencat.json`; explicit mappings and pinned roles guard color drift.
- Promoted the active local Carbonfox skin as the canonical distributable skin.
- Documented the active token-cat hero and archived banner-logo artwork.
- Added a validator and unit tests for the shipped theme assets. Current strict
  YAML validation requires PyYAML; Rich is required for artwork-rendering tests.
- Pinned and checksum-verified the optional Nerd Fonts installer.
- Removed generated, duplicate, backup, and stale banner experiments from the release tree.
- Added concise provenance, support boundaries, and non-destructive installation guidance.
