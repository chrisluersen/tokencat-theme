# Backups

Snapshots of the theme artefacts **as actually installed on disk**, captured so a
bad build can be diffed against what the applications were really reading.

## What belongs here

Theme artefacts only:

- the installed VS Code extension payload
- the installed Zed theme
- WezTerm / Zellij theme files
- Hermes skin and dashboard theme files

## What must never be committed here

This repository is **public**. Personal application configuration is deliberately
excluded and kept outside the repository:

- `settings.json` (VS Code, Windows Terminal)
- `config.kdl` (Zellij user config)
- `wezterm.lua` (WezTerm user config)

`.gitignore` blocks these paths as a backstop. An installed application's settings
file routinely contains machine paths, extension state and personal preferences —
it is not a theme artefact and has no place in a public history, which is
irreversible once pushed.

`MANIFEST.json` lists only repository-relative paths and content hashes; absolute
paths from the collecting machine are intentionally omitted.

## Regenerating

Snapshots are point-in-time by design. Take a new dated directory rather than
overwriting an old one — the value of a before-image is that it does not move.
