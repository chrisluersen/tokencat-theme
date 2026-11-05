import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class CIContractTests(unittest.TestCase):
    def test_whitespace_check_has_parent_history_and_is_not_filtered(self):
        workflow = yaml.load(
            (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8"),
            Loader=yaml.BaseLoader,
        )
        steps = workflow["jobs"]["validate"]["steps"]
        checkout = next(
            step for step in steps if step.get("uses", "").startswith("actions/checkout@")
        )
        depth = int(checkout.get("with", {}).get("fetch-depth", "1"))
        self.assertTrue(depth == 0 or depth >= 2, "git show --check needs HEAD's parent")
        whitespace = next(step for step in steps if step.get("name") == "Check whitespace")
        self.assertEqual(
            whitespace["run"].splitlines(),
            ["git diff --check", "git show --check --oneline HEAD"],
        )

    def test_cross_platform_lint_and_validation_are_explicit(self):
        # BaseLoader keeps the YAML 1.1 word `on` a string without altering global loaders.
        workflow = yaml.load(
            (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8"),
            Loader=yaml.BaseLoader,
        )
        self.assertEqual(set(workflow["on"]), {"push", "pull_request"})
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        job = workflow["jobs"]["validate"]
        self.assertEqual(
            job["strategy"]["matrix"].get("include"),
            [
                {"os": "ubuntu-latest", "python": "3.11"},
                {"os": "windows-latest", "python": "3.14"},
            ],
        )
        commands = [step["run"] for step in job["steps"] if "run" in step]
        for required in (
            "python -m ruff check scripts tests",
            "python -m ruff format --check scripts tests",
            "python -B -m unittest discover -s tests -v",
            "python -B scripts/validate_theme.py",
            "bash -n fonts/install-hack-nerd-font.sh",
            "shellcheck fonts/install-hack-nerd-font.sh",
        ):
            self.assertIn(required, commands)
        for step in job["steps"]:
            if "uses" in step:
                self.assertRegex(step["uses"], r"^[^@]+@[0-9a-f]{40}$")
