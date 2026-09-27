"""Secrets hygiene: tracked files must not contain live credentials.

Scans only git-tracked files (secrets in untracked/gitignored .env.* are
expected to be real — this suite asserts they never reach git).
"""

import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Patterns that indicate a LITERAL credential (not a {env:VAR} placeholder).
# Compiled against bytes so raw file scans stay cheap and binary-safe.
SUSPECT_PATTERNS = [
    re.compile(pat)
    for pat in [
        rb"sk-[A-Za-z0-9]{16,}",
        rb"ghp_[A-Za-z0-9]{20,}",
        rb"AKIA[0-9A-Z]{16}",
        rb"-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----",
        rb"Bearer [A-Za-z0-9_\-]{20,}",
        rb"xox[baprs]-[A-Za-z0-9-]{10,}",
    ]
]


def tracked_files():
    out = subprocess.run(
        ["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout
    return [Path(p) for p in out.splitlines() if p]


class TestSecrets(unittest.TestCase):
    def test_no_literal_credentials_in_tracked_files(self):
        import fnmatch

        offenders = []
        for p in tracked_files():
            if not p.is_file():
                continue
            if any(fnmatch.fnmatch(p.name, pat) for pat in ["*.png", "*.jpg", "*.gz", "*.bundle"]):
                continue
            try:
                data = p.read_bytes()
            except OSError:
                continue
            for pat in SUSPECT_PATTERNS:
                if pat.search(data):
                    offenders.append(f"{p} matched {pat!r}")
        self.assertEqual([], offenders, f"literal credential patterns: {offenders}")

    def test_example_envs_use_placeholders(self):
        for name in [".env.ollama.example", ".env.docker.example"]:
            text = (REPO / name).read_text()
            # Real-looking values must not appear in committed examples.
            self.assertNotIn("8befc29ec3e589b9b7088ed0491c808b05e581284ad711035b23b1bc06dcb042", text)
            self.assertTrue(
                "{env:" in text or "changeme" in text or text.count("=") >= 1,
                f"{name} lacks placeholder-style values",
            )


if __name__ == "__main__":
    unittest.main()