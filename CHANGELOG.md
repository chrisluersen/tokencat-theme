# Changelog

## 2026-11-04 — Lucky with Agency banner

- Tokencat now displays `Lucky` / `with` / `Agency`, centered within each row's available box space. The cat, box outline, 29×11 geometry and existing row colors are preserved.
- Added a separate canonical `ascii-art/lucky-cat-29x11.txt`, renderer/centering/outline regression checks and updated attribution. Original `$TOKENS` artwork, legacy Carbonfox, gated two-tone art and other theme exports remain unchanged.


## 2026-11-02 — SSOT now carries typography; WezTerm drift recorded

- **Fixed: the SSOT silently dropped every font key.** The generator matches colour leaves on a
  hex pattern, so font values never matched and 0 font rows were emitted while VS Code, Zed,
  WezTerm and the Hermes dashboard all declared fonts. Fonts are now collected by a separate
  `rows_fonts()` pass — **13 font rows across 4 surfaces**, plus a `## Typography` section in the
  generated page. `tests/test_ssot_table.py` (7 tests) fails if that coverage disappears again.
- **Added `docs/fonts.json`** — the live editor font settings (VS Code, Zed, WezTerm) that the
  shipped theme files do not carry, so they are visible in the SSOT instead of living only in each
  app's config.
- **Added `docs/ssot-decision.md`** — why the SSOT is a generated CSV *and* a generated page rather
  than one hand-typed table, the per-surface coverage counts, and the surface-parity table.
- **Recorded one open drift, unresolved on purpose.** The installed WezTerm scheme was edited
  2026-11-02 (active tab bar blue → near-black) and does not match the repo. Absorbing it verbatim
  fails 16 tests, because `export_contract.py` requires every shipped colour to resolve to a
  declared palette token and the palette declares the active tab as `blue`. The edit is preserved
  at `backups/2026-11-02-drift/`; the repo file is unchanged from `HEAD`. This needs an owner
  decision — it is a design change, not a backup.
- Zed's per-token `font_style` / `font_weight` attributes are deliberately **not** collected as
  typography; they are syntax rules and belong with the token colours.

## 2026-10-31 — Hermesfox retired

- **Removed the Hermesfox variant from every surface**, by owner decision. The Hermes skin,
  its Windows Terminal scheme, both regression test files and the installed copy are gone;
  the validator no longer requires or checks it. `scripts/validate_theme.py` keeps only the
  VS Code manifest check from that function.
- **Corrected a documentation overclaim found during the removal:** the README asserted
  Hermesfox was *available* on Windows Terminal. It was not — the shipped scheme file was
  never merged into the live settings, which carried only `Carbon Fox` and `tokencat`. The
  claim is removed rather than preserved.
- Carbonfox (Legacy) is untouched and remains the rollback path.

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
