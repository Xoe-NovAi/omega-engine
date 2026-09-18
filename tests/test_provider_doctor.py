"""Provider doctor regressions (hermetic fixtures, no quota, no secrets).

Runs scripts/opencode_provider_doctor.sh against a fake HOME so no live
config is touched. Network-dependent assertions (registry drift) accept
either outcome; everything else is deterministic.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOC = REPO / "scripts" / "opencode_provider_doctor.sh"

TOXIC = {
    "provider": {
        "opencode": {
            "options": {},
            "models": {
                "big-pickle": {
                    "name": "BP",
                    "limit": {"context": 1000000, "input": 950000, "output": 64000},
                }
            },
        },
        "custom": {
            "npm": "@ai-sdk/openai-compatible",
            "options": {"baseURL": "https://api.openrouter.ai/v1"},
            "models": {},
        },
    }
}


def make_home(toxic=True):
    tmp = Path(tempfile.mkdtemp(prefix="doctor-test-"))
    conf = tmp / ".config" / "opencode"
    conf.mkdir(parents=True)
    if toxic:
        (conf / "opencode.json").write_text(json.dumps(TOXIC))
    (tmp / ".local" / "share" / "opencode").mkdir(parents=True)
    if not toxic:
        (conf / "opencode.json").write_text(json.dumps({"mcp": {}}))
    return tmp


def run(*args):
    return subprocess.run(
        ["bash", str(DOC), *args],
        capture_output=True, text=True, timeout=120,
    )


class TestProviderDoctor(unittest.TestCase):
    def test_syntax(self):
        r = subprocess.run(["bash", "-n", str(DOC)], capture_output=True, timeout=15)
        self.assertEqual(0, r.returncode, "doctor has syntax errors")

    def test_toxic_fixture_fails_with_expected_findings(self):
        home = make_home()
        r = run("--home", str(home), "--project", str(home))
        self.assertEqual(2, r.returncode, f"expected exit 2:\n{r.stdout[-1500:]}")
        self.assertIn("empty object", r.stdout)
        self.assertIn("api.openrouter.ai", r.stdout)

    def test_apply_strips_options_keeps_models_with_backup(self):
        home = make_home()
        cfg = home / ".config" / "opencode" / "opencode.json"
        r = run("--home", str(home), "--project", str(home), "--apply")
        self.assertEqual(2, r.returncode)  # dead baseURL FAIL remains (report-only)
        live = json.loads(cfg.read_text())
        self.assertNotIn("options", live["provider"]["opencode"])
        self.assertIn("big-pickle", live["provider"]["opencode"]["models"])
        self.assertTrue(list(cfg.parent.glob("opencode.json.bak.*")), "no backup written")

    def test_apply_is_idempotent(self):
        home = make_home()
        run("--home", str(home), "--project", str(home), "--apply")
        before = sorted(p.name for p in (home / ".config" / "opencode").glob("*.bak.*"))
        run("--home", str(home), "--project", str(home), "--apply")
        after = sorted(p.name for p in (home / ".config" / "opencode").glob("*.bak.*"))
        # options already gone: global-file backup must not multiply (project file
        # absent so only the one global backup exists from run 1)... simpler:
        # second run must not create additional backups for already-clean files.
        self.assertEqual(before, after, "second --apply created new backups (not idempotent)")

    def test_embedded_secret_flagged_value_never_shown(self):
        home = make_home()
        cfg_path = home / ".config" / "opencode" / "opencode.json"
        cfg = json.loads(cfg_path.read_text())
        cfg["provider"]["custom"]["options"]["apiKey"] = "sk-or-v1-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
        cfg_path.write_text(json.dumps(cfg))
        r = run("--home", str(home), "--project", str(home))
        self.assertIn("embeds a full-length secret", r.stdout)
        self.assertNotIn("ABCDEFGHIJKLMNOPQRSTUVWXYZ123456", r.stdout, "secret value leaked to output")

    def test_clean_tree_reports_no_provider_blocks(self):
        home = make_home(toxic=False)
        r = run("--home", str(home), "--project", str(home))
        self.assertIn("no provider blocks", r.stdout)


if __name__ == "__main__":
    unittest.main()
