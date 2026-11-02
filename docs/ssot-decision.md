# Tokencat — SSOT decision and open drift

## The SSOT decision: generated CSV **and** generated page, never hand-typed

**Decision (2026-11-02):** the SSOT is a **generated pair**, not a hand-maintained file.

- `docs/ssot-tokencat.csv` — long-format, one row per key. For filtering, diffing and spreadsheets.
- `docs/ssot-tokencat.md` — the same rows as readable tables, grouped by surface.
- `scripts/ssot_table.py` regenerates both. Neither is edited by hand.

**Why generated rather than typed.** The acceptance test for this card is *"real keys parsed
from the theme files (not hand-typed)"*. A typed table is wrong the moment a theme file changes,
with nothing to detect it. A generated table is wrong only if the generator is wrong, and a
regeneration check catches that.

**Why both formats.** They serve different readers. The CSV answers "what does key X resolve to
on surface Y, across every surface" — that is a filter over 1,358 rows, which a person cannot
scan but a spreadsheet can. The markdown answers "what does the Zed surface contain" — a browsable
inventory. A CSV alone is unreadable; a page alone is un-diffable.

**Why not one page per surface.** That would be ten files to keep in sync with one generator.
The SSOT exists to make cross-surface drift visible; splitting it by surface hides exactly the
comparison it is for.

## Coverage as generated (2026-11-02)

| Surface | File(s) | Keys |
|---|---|---|
| export contract | the six shipped export files | 521 |
| hermes-dashboard | `hermes/dashboard-themes/tokencat.yaml` | 28 |
| hermes-skin | `hermes/skins/{tokencat,carbonfox}.yaml` | 85 |
| palette (SSOT) | `palettes/tokencat.json` | 46 |
| palette (SSOT) > hermes | `palettes/tokencat.json` | 44 |
| vscode | `vscode/{tokencat,carbonfox}.vscode-theme.json` | 245 |
| wezterm | `wezterm/tokencat.toml` | 38 |
| windows-terminal | `windows-terminal/*.scheme.json` | 40 |
| zed | `zed/tokencat.json` | 223 |
| zellij | `zellij/tokencat.kdl` | 88 |
| **total** | | **1,358** |

Font rows included: **13**, across `vscode`, `zed`, `wezterm`, `hermes-dashboard`.

### Defect this fixed

The first generator matched colour leaves on a hex pattern (`HEX.fullmatch`). Font values are
not hex, so **every font row was silently dropped** — the SSOT carried 0 font rows while four
surfaces declared fonts. The original ASK names font explicitly ("keys, labels, colors, **font**").
Fonts are now collected by a separate `rows_fonts()` pass with its own key pattern, and
`tests/test_ssot_table.py` fails if that coverage ever disappears again.

Zed's per-token `font_style` / `font_weight` attributes are deliberately **excluded**: those are
syntax rules attached to a token, not typography settings.

### Font settings that live outside the shipped theme files

VS Code, Zed and WezTerm declare their font in the *application's* config, not in the theme file
they load from this repo. Those values are captured in `docs/fonts.json` so they are visible in the
SSOT. That file is a **snapshot of live app config on 2026-11-02**, not a thing any export writes.

Workstation font family: **Hack Nerd Font Mono**.

## Open drift — WezTerm active tab bar (needs an owner decision)

**Not resolved by this card, deliberately.** It is a design change, not a backup.

The live installed file `~/.config/wezterm/colors/tokencat.toml` was edited on **2026-11-02 08:43**
(local mtime) and differs from the repo in exactly two keys:

| Key | Repo (committed) | Live (installed) |
|---|---|---|
| `colors.tab_bar.active_tab.bg_color` | `#78a9ff` (blue) | `#0d0d0d` (near-black) |
| `colors.tab_bar.active_tab.fg_color` | `#161616` (background) | `#f2f4f8` (foreground) |

**Why the repo did not simply absorb it.** `scripts/export_contract.py` requires every shipped
colour to resolve to a declared palette token (`palette drift` error). The live pair resolves to
`background_alt` / `foreground`, but the palette declares the active tab as
`blue` / `background`. Backing up the live file verbatim therefore fails **16 tests**. Two honest
routes, both needing a decision:

1. **Repo keeps blue (current state).** The live edit is an experiment; the installed file should be
   reverted to the repo version to restore parity.
2. **Live grey wins.** Update `palettes/tokencat.json` to map the active tab to
   `background_alt`/`foreground`, re-export, and reinstall. Note this would make WezTerm's active
   tab the only surface without an accent-coloured active tab — VS Code uses
   `tab.activeBorderTop: #78a9ff` and Zellij's `ribbon_selected` uses blue, so option 2 breaks
   cross-surface consistency on purpose.

**Current state:** the repo file is unchanged from `HEAD`; the live edit is preserved at
`backups/2026-11-02-drift/wezterm-installed.tokencat.toml`. Full test suite passes (97).

## Verification status

Surface parity, checked byte-for-byte against the repo on 2026-11-02:

| Surface | Installed at | Repo parity | Actually selected? |
|---|---|---|---|
| Zed | `AppData/Roaming/Zed/themes/tokencat.json` | **identical** | yes — `settings.json` `theme.dark = "Tokencat"` |
| VS Code | `.vscode/extensions/chrisluersen.tokencat-theme-0.0.1/` | **identical** (theme + color-customizations) | yes — `workbench.colorTheme: "Tokencat"` |
| WezTerm | `~/.config/wezterm/colors/tokencat.toml` | **DIFFERS** — see drift above | yes — `color_scheme = 'Tokencat'` |
| Windows Terminal | `Packages/Microsoft.WindowsTerminal_*/LocalState/settings.json` | **identical** (0 key diffs) | yes — one profile sets `colorScheme: "tokencat"` |
| Zellij | `AppData/Roaming/Zellij/config/themes/tokencat.kdl` | **identical** | **no** — config's active theme is still the custom carbonfox block (line 685) |

Could not verify: nothing on this list is unchecked. Font *rendering* was not inspected visually —
only the font settings were read from config.

The repo is committed and pushed to `master` (`origin` = `github.com/chrisluersen/tokencat-theme`).
