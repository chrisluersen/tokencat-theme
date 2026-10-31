# Validation and local execution

Use Python 3.11 or newer in an existing approved environment containing the versions in `requirements-dev.txt`. The file is a reproducibility manifest, not permission to install software. The implementation used PyYAML 6.0.3, Rich 14.3.3, and an existing Ruff 0.15.10 executable; no package was installed or runtime modified. Ruff is pinned to the version actually available and tested rather than the plan's uninstalled newer version.

Before Python initializes `tempfile`, bind `TMPDIR`, `TEMP`, and `TMP` to the same task-owned directory under the active Hermes home. On Windows all three matter. Bind `TOKENCAT_PYTHON`, `TOKENCAT_RUFF` and `TOKENCAT_SHELLCHECK` to verified existing native executable paths, not guessed PATH aliases. From repository root:

```bash
: "${HERMES_HOME:?Use the actual active Hermes home}"
: "${TOKENCAT_PYTHON:?Bind an approved Python 3.11+ with the declared dependencies}"
: "${TOKENCAT_RUFF:?Bind the existing Ruff 0.15.10 executable}"
: "${TOKENCAT_SHELLCHECK:?Bind an approved existing ShellCheck executable}"
export TMPDIR="$HERMES_HOME/cache/scratch"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"
"$TOKENCAT_PYTHON" -B -c "import tempfile; print(tempfile.gettempdir())"
"$TOKENCAT_RUFF" check scripts tests
"$TOKENCAT_RUFF" format --check scripts tests
"$TOKENCAT_PYTHON" -B -m unittest discover -s tests -v
"$TOKENCAT_PYTHON" -B scripts/validate_theme.py
"$TOKENCAT_PYTHON" -B -m scripts.validate_theme
bash -n fonts/install-hack-nerd-font.sh
"$TOKENCAT_SHELLCHECK" --norc --format=json fonts/install-hack-nerd-font.sh
git diff --check
```

Expected: actual temporary paths under the chosen home; Ruff exits zero; unit tests `OK`; both validator entry points print `PASS: hermesfox theme validation`; syntax/ShellCheck/whitespace commands exit zero. The stable validator message deliberately retains the existing repository name. Missing Ruff/ShellCheck is **blocked**, never a pass, and tool setup must follow the applicable approval policy. CI configuration is not evidence that CI ran; local-only work does not push or dispatch it.

## What the checks prove

- Seven normalized-text hashes preserve the shipped legacy palette, exports and cat sources. Upgrade base values retain every original token.
- Strict JSON/YAML rejects duplicate keys, malformed structures, non-finite JSON values (including exponent overflow) and non-string skin colors. CLI and package import paths share the same parser implementations.
- Missing source art/exports/hero, semantic pin drift, unrecognized palette tokens, missing mappings and changed/extra export colors fail validation. Copied mutation fixtures must validate before mutation.
- Shared skin aliases are explicit. VS Code workbench exports agree and all 16 ANSI colors are present. The manifest points Tokencat to its upgrade file; Carbonfox (Legacy) intentionally shares the original color file. The archived legacy files remain hash-guarded.
- WezTerm TOML has its declared text/cursor/selection/tab fields and ANSI16 parity with Windows Terminal. Zellij has all 14 declared modern-role blocks and ten player colors. Every emitted color is palette-mapped; malformed structure, duplicate nodes, bad RGB and unsupported KDL constructs fail. The KDL reader handles only this repository's emitted subset, not the native Zellij grammar or runtime.
- Named normal-text, word-diff and VS Code suggestion-state pairs satisfy the measured contrast thresholds. Both upgrade VS Code exports require explicit selected text and focused-match roles and at least 4.5:1 text contrast on their corresponding backgrounds. Rich rendering matches the source geometry/escaping; one-span-per-row artwork remains default.
- Word-diff tests measure the default foreground and every emitted syntax foreground, including comments, on both inserted and removed word backgrounds in both VS Code exports. Four independent fixture mutations restoring either former background must fail the actual guard. The added-word border is explicit, opaque, and clears 3:1 against its word and line backgrounds; native diff rendering remains a separate check.
- CLI completion guards include the native selected metadata pair (`ui_label` on `completion_menu_meta_current_bg`), not just the main label. Optional `TOKENCAT_HERMES_SOURCE` selects an approved local Hermes source tree for two native regressions: the TokenCat style generator. Without it, both native integration tests are explicitly skipped; mandatory emitted-role and artifact checks still run. These tests inject candidates at the existing skin boundary and do not bootstrap an agent/server or read the active profile.
- Both standalone validator entry points require the Tokencat skin and scheme and reject original-color, banner, scheme-name or VS Code selector drift. Missing/corrupt scratch-fixture regressions exercise this validator directly; a unit-suite pass is not substituted for the standalone check.
- RGB nodes in the emitted KDL subset require ASCII decimal digits; non-ASCII and mixed decimal tokens fail. WezTerm body/cursor/selection/tab pairs and Zellij base/emphasis role pairs are measured against their declared backgrounds. In-memory foreground mutations demonstrate each checked pair's guard rejects low contrast; this is not native app rendering.
- Font fixtures supply their own archives and fake registry command. Before launching the installer, a Bash guard checks that resolved `reg` is the exact fake fixture file; a shadowed command aborts with exit 97.

## What remains independent

The tests are repository contracts, not complete vendor schemas or rendered acceptance. Effective selection/diff/disabled/hover/focus colors, cold starts, theme-switch cleanup, profile persistence, font rendering, narrow/wide terminal layouts and real dashboard normalization require isolated app/runtime evidence. See [compatibility.md](compatibility.md). Do not invoke model reviewers or alter Hermes to obtain it.

Private commands, RED/GREEN logs, model/budget notes and runtime readiness remain under ignored `.hermes/evidence/`; they are not release payloads. Source/docs scans still reject workstation paths and placeholder markers in shipped material. No tracked validation record should include credentials, private paths or model-provider details.
