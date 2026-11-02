# Windows Terminal surface

Two independent pieces go into `settings.json`. They are not the same object and neither implies the other.

| File | What it is | Where it goes in `settings.json` |
|---|---|---|
| `tokencat.scheme.json` | The **colour scheme** (21 keys: background, foreground, 16 ANSI colours) | one entry appended to the top-level `schemes` array; referenced by a profile's `colorScheme` |
| `theme.json` | The **theme** (tab strip, tab row, window chrome) | one entry appended to the top-level `themes` array; activated by the top-level `theme` key |

## Apply

1. Append the contents of `tokencat.scheme.json` to the `schemes` array.
2. Append the contents of `theme.json` to the `themes` array.
3. Set top-level `"theme": "Tokencat"`.
4. Optionally set `"colorScheme": "tokencat"` on individual profiles.

`scheme.json` in this directory is the retired **carbonfox** variant, kept for reference. `tokencat.scheme.json` is the live one.

## Colour format: `#AARRGGBB`, and 6-digit is silently discarded

Windows Terminal's own shipped `defaults.json` uses 8-digit hex throughout — `#00000000`, `#FFFFFFFF`, `#333333FF`. Alpha comes **first**.

A 6-digit value such as `#0d0d0d` is accepted into the file without error but **does not render**. WT discards it and falls back to its built-in default. This is the single easiest way to "fix" a theme and see no change at all: valid JSON, valid-looking config, zero effect.

Use `"unfocusedBackground": "#FF121212"` to make the active tab contrast against the tab row, rather than the two sharing `#0d0d0d` and the active tab reading as invisible.

## `tabRow` accepts only `unfocusedBackground`

Verified against WT's shipped defaults: the `tabRow` object has exactly one key, `unfocusedBackground`. A `tabRow.background` is accepted into the file and ignored. The `tab` object does take `background`.

## Do not put `tabColor` on profiles

`tabColor` overrides the theme's tab colour for that profile, which defeats the theme — a per-profile `tabColor` is what makes a themed terminal show one off-colour tab. If tabs need to differ per profile, that is a deliberate override, not a theming default.

## Verify the change landed — the file is not the render

Editing `settings.json` proves nothing about what WT is showing. Two checks, both cheap:

```bash
# 1. WT's own load signal. Must CHANGE after a restart.
#    An unchanged hash across a restart means WT did not load the file.
python3 -c "import json;print(json.load(open(r'%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\state.json'))['settingsHash'])"

# 2. Sample the actual pixels of the live window.
```

An unchanged `settingsHash` is the fast tell that the config is not being read at all — do not respond by adjusting values, which produces an endless loop of edits with no effect.

## Testing a config change safely

**Back up `settings.json` before any experiment, every time.** Writing a minimal test config over the live file costs the user their theme, their colour scheme and their profile list in one step, and WT's error recovery is silent.

Never reduce `profiles.list` to test something. WT resolves the `defaultProfile` GUID against that list; if the list no longer contains it, WT falls back to its own first default (PowerShell), which reads as the terminal "switching to PowerShell on its own".
