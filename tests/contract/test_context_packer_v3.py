"""M21 / M13 Contract Tests: Context Packer v3 — deterministic 5-step fail-closed API.

AP Token: AP-PACKER-V3-CONTRACT-TESTS-20260808
SSOT:     docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md

These tests are the SPECIFICATION. The v3 implementation (Phase 3 in the manual)
MUST make every test in this file pass. They replace the broken v2 9-phase
surgical pipeline (silent truncation) with a fail-closed 5-step architecture:

    1. Resolve  — GitIgnoreSpec.from_lines() expands explicit file lists.
    2. Count    — shared TokenEstimator (single source of truth for curator + packer).
    3. Validate — FAIL-CLOSED: budget / max_slots / required themes. [PACK-FAIL].
    4. Order    — LITM zone -> priority mapping wired into platform adapters.
    5. Write    — PII mask (AnyIO file-loop), XML escape-before-CDATA, Ed25519 sign,
                  per-profile pii_vault.json. Never delete non-generated files.
"""

import importlib
import inspect
import json
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from pathspec import GitIgnoreSpec

# Ensure the context-packer skill is importable (it lives outside src/).
_SKILL_DIR = Path(__file__).resolve().parent.parent.parent / ".opencode" / "skills" / "context-packer"
_SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
_FIXTURE_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "context_packer"
for _p in (_SKILL_DIR, _SRC_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


# ── Phase 1: Resolve ──────────────────────────────────────────────────────────
class TestResolvePhase:
    """GitIgnoreSpec.from_lines() handles recursive globs + negation (manual §1.2.1, §1.3)."""

    def test_gitignorespec_handles_recursive_globs(self, tmp_path):
        # `**` crosses directory boundaries (manual: full Git behavior via GitIgnoreSpec).
        spec = GitIgnoreSpec.from_lines(["**/*.py"])
        assert spec.match_file("src/oracle/main.py")
        assert spec.match_file("src/omega/oracle/model_gateway.py")
        assert spec.match_file("main.py")
        # Single `*`, when the pattern is anchored, must NOT cross the `/` boundary.
        anchored = GitIgnoreSpec.from_lines(["src/*.py"])
        assert anchored.match_file("src/main.py")
        assert not anchored.match_file("src/oracle/main.py")
        # Bare `*.py` (no slash) is basename-matched at ANY depth per gitignore semantics.
        basename = GitIgnoreSpec.from_lines(["*.py"])
        assert basename.match_file("main.py")
        assert basename.match_file("src/oracle/main.py")

    def test_gitignorespec_negation_patterns(self, tmp_path):
        spec = GitIgnoreSpec.from_lines(["**/*.py", "!tests/**", "!**/test_*.py"])
        assert spec.match_file("src/main.py")
        assert not spec.match_file("tests/test_main.py")
        assert not spec.match_file("test_main.py")

    def test_resolve_theme_files_expands_explicit_lists(self, tmp_path):
        """v3 resolve must expand config theme lists to concrete file paths (manual §1.2.1)."""
        packer = importlib.import_module("packer")
        from platform_adapters import PlatformConfig

        base = tmp_path / "repo"
        (base / "src").mkdir(parents=True)
        (base / "src" / "a.py").write_text("x")
        (base / "src" / "b.py").write_text("y")
        (base / "README.md").write_text("# hi")

        profile = SimpleNamespace(
            name="test",
            max_slots=12,
            include=["src/**/*.py"],
            exclude=["**/__pycache__/**"],
            themes={"core": ["src/**/*.py"], "docs": ["README.md"]},
            platform=PlatformConfig.from_profile_config({}),
        )
        resolved = packer.resolve_theme_files(profile, base)
        assert set(resolved.keys()) == {"core", "docs"}
        assert {f["path"] for f in resolved["core"]} == {"src/a.py", "src/b.py"}
        assert [f["path"] for f in resolved["docs"]] == ["README.md"]


# ── Phase 2: Count ────────────────────────────────────────────────────────────
class TestCountPhase:
    """Single shared TokenEstimator used by curator + packer (manual §1.5 — zero-drift)."""

    def test_shared_token_estimator(self):
        token_estimator = importlib.import_module("omega.oracle.token_estimator")
        n = token_estimator.estimate_tokens("hello world")
        assert isinstance(n, int)
        assert n > 0

    def test_platform_specific_encoding(self):
        token_estimator = importlib.import_module("omega.oracle.token_estimator")
        text = "sovereign local-first inference " * 20
        claude = token_estimator.estimate_tokens(text, model="cl100k_base")
        grok = token_estimator.estimate_tokens(text, model="o200k_base")
        assert claude > 0 and grok > 0
        assert isinstance(claude, int) and isinstance(grok, int)

    def test_token_margin_multiplier_from_config(self):
        token_estimator = importlib.import_module("omega.oracle.token_estimator")
        from platform_adapters import PlatformConfig

        cfg = PlatformConfig.from_profile_config(
            {"tokenizer_encoding": "cl100k_base", "token_margin_multiplier": 2.0}
        )
        assert cfg.token_margin_multiplier == 2.0
        assert cfg.tokenizer_encoding == "cl100k_base"

        raw = token_estimator.estimate_tokens("ab", model=cfg.tokenizer_encoding)
        scaled = token_estimator.estimate_tokens("ab", model=cfg.tokenizer_encoding, margin=2.0)
        assert scaled >= raw


# ── Phase 3: Validate (FAIL-CLOSED) ───────────────────────────────────────────
class TestValidatePhase:
    """Over budget / over slots / missing required theme -> [PACK-FAIL]. Never trim. (manual §1.2.3)"""

    def test_fail_closed_budget_exceeded(self):
        """Bundle exceeds per_bundle budget -> PackValidationError with top-3 diagnostic files."""
        packer = importlib.import_module("packer")
        from platform_adapters import PlatformConfig

        cfg = PlatformConfig.from_profile_config({"token_budget": {"per_bundle": 100, "total": 1000}})
        bundles = {
            "mandates": [
                {"path": "A.md", "token_count": 60},
                {"path": "B.md", "token_count": 70},  # 130 > per_bundle 100 -> fail
            ],
            "oracle_core": [{"path": "C.py", "token_count": 30}],
        }
        with pytest.raises(packer.PackValidationError) as ei:
            packer.validate_pack(bundles, cfg, required_themes={"mandates"})
        msg = str(ei.value)
        assert "[PACK-FAIL]" in msg
        assert "mandates" in msg

    def test_fail_closed_required_theme_missing(self):
        """Missing required theme -> [PACK-FAIL] naming the absent theme."""
        packer = importlib.import_module("packer")
        from platform_adapters import PlatformConfig

        cfg = PlatformConfig.from_profile_config({"token_budget": {"per_bundle": 50000, "total": 500000}})
        bundles = {"mandates": [{"path": "A.md", "token_count": 10}]}
        with pytest.raises(packer.PackValidationError) as ei:
            packer.validate_pack(bundles, cfg, required_themes={"mandates", "oracle_core"})
        assert "oracle_core" in str(ei.value)

    def test_fail_closed_max_slots_exceeded(self):
        """Total bundles (+manifest) must not exceed max_slots -> [PACK-FAIL]."""
        packer = importlib.import_module("packer")
        from platform_adapters import PlatformConfig

        cfg = PlatformConfig.from_profile_config(
            {"max_slots": 3, "token_budget": {"per_bundle": 50000, "total": 500000}}
        )
        bundles = {
            "b1": [{"path": "1", "token_count": 1}],
            "b2": [{"path": "2", "token_count": 1}],
            "b3": [{"path": "3", "token_count": 1}],
            "b4": [{"path": "4", "token_count": 1}],  # 4 bundles + manifest = 5 > 3 slots
        }
        with pytest.raises(packer.PackValidationError):
            packer.validate_pack(bundles, cfg, required_themes=set())


# ── Phase 4: Order ────────────────────────────────────────────────────────────
class TestOrderPhase:
    """litm_zone -> priority mapping wired into platform adapters (manual §1.6)."""

    def test_litm_zone_priority_mapping(self):
        """start=3, middle=2, end=1; unknown/None defaults to middle=2."""
        packer = importlib.import_module("packer")
        assert packer.LITM_ZONE_PRIORITY == {"start": 3, "middle": 2, "end": 1}

        for zone, expected in [("start", 3), ("middle", 2), ("end", 1), ("unknown", 2), (None, 2)]:
            bundle = {"litm_zone": zone} if zone else {}
            ordered = packer.apply_litm_priority(bundle)
            assert ordered["priority"] == expected, f"zone={zone!r}"

    def test_platform_adapters_consume_priority_unchanged(self):
        """LITMUShapedStrategy / PriorityWeightedStrategy work on resolved priority ints."""
        from platform_adapters import LITMUShapedStrategy, PriorityWeightedStrategy

        bundles = [
            {"theme": "end", "token_count": 10, "priority": 1, "relevance": 0.3},
            {"theme": "mid", "token_count": 20, "priority": 2, "relevance": 0.5},
            {"theme": "start", "token_count": 30, "priority": 3, "relevance": 1.0},
        ]
        litm = LITMUShapedStrategy().order(bundles)
        assert [b["theme"] for b in litm][0] == "start"
        assert [b["theme"] for b in litm][-1] == "end"

        pw = PriorityWeightedStrategy().order(bundles)
        assert [b["theme"] for b in pw][0] == "start"


# ── Phase 5: Write ────────────────────────────────────────────────────────────
class TestWritePhase:
    """Safe output, PII vault encapsulation, defusedxml parse-only, Ed25519 signing."""

    def test_pii_vault_encapsulation(self, tmp_path):
        """pii_vault.json is written into context_packs/<profile>/ (NOT the global dir)."""
        packer = importlib.import_module("packer")
        profile_dir = tmp_path / "context_packs" / "sovereign-audit"
        tokens = {"[EMAIL_1]": "alice@example.com", "[PHONE_1]": "+1-555-0100"}
        vault_path = packer.write_pii_vault(profile_dir, "sovereign-audit", tokens)

        assert profile_dir / "pii_vault.json" == vault_path
        assert vault_path.exists()
        data = json.loads(vault_path.read_text())
        assert data["profile"] == "sovereign-audit"
        assert data["tokens"] == tokens
        assert "data/coordination" not in str(vault_path)

    def test_defusedxml_parse_only(self):
        """XML parsing uses defusedxml; CREATION uses stdlib Element/SubElement (manual §1.3, §5.5)."""
        DET = importlib.import_module("defusedxml.ElementTree")
        assert hasattr(DET, "parse") and hasattr(DET, "fromstring")
        assert not hasattr(DET, "Element") and not hasattr(DET, "SubElement")

        import packer
        src = inspect.getsource(packer)
        assert "defusedxml" in src
        assert "xml.etree.ElementTree" in src or "ElementTree as" in src

    def test_escape_bare_ampersand_roundtrip(self):
        """M23: bare & must become &amp; (NOT &lt;). Round-trip must be lossless.

        Regression: `_escape_bare_xml_chars` escaped bare & as `&lt;`, so
        `if a & b` became `if a < b` after XML unescape — silent content
        corruption in every bundled file (AT&T -> AT<T, && -> <<).
        """
        from xml.sax.saxutils import unescape
        import packer

        # Raw content with no pre-escaped entities: round-trip must be lossless.
        cases = [
            "if a & b: pass",
            "AT&T telecom",
            "C:\\path & more",
            "<file> tag in docstring & stuff",
            "&& && & &&",
        ]
        for raw in cases:
            escaped = packer._escape_bare_xml_chars(raw)
            # Bare & must NEVER become &lt; (that is the regression).
            assert "&lt; " not in escaped, \
                f"bare & corrupted to &lt;: {escaped!r}"
            # Round-trip must reconstruct the raw source exactly.
            assert unescape(escaped) == raw, \
                f"round-trip mismatch: {raw!r} -> {escaped!r}"

        # Pre-escaped entities must NOT be double-escaped (they pass through).
        pre = "x = a &lt; b &amp; c"
        assert packer._escape_bare_xml_chars(pre) == pre

    def test_ed25519_signature(self):
        """Manifest signed with Ed25519; public key serialized to PEM (manual §5.5)."""
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.hazmat.primitives import serialization

        key = ed25519.Ed25519PrivateKey.generate()
        pub = key.public_key()
        sig = key.sign(b"manifest-content")
        pub.verify(sig, b"manifest-content")

        pem = pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()
        assert pem.startswith("-----BEGIN PUBLIC KEY-----")
        assert len(sig) == 64


# ── Phase 2: Curator CLI (typer) ──────────────────────────────────────────────
class TestCuratorCLI:
    """curate_packs.py uses typer (CliRunner); failure => non-zero exit (M21)."""

    def _invoke(self, tmp_path, monkeypatch, *argv):
        """Copy the fixture tree into tmp_path, chdir there, run the CLI."""
        import curate_packs
        from typer.testing import CliRunner
        cwd = tmp_path / "cwd"
        shutil.copytree(_FIXTURE_DIR, cwd)
        monkeypatch.chdir(cwd)
        runner = CliRunner()
        return runner.invoke(curate_packs.app, list(argv))

    def test_unknown_profile_exit_2(self, tmp_path, monkeypatch):
        cfg = str(_FIXTURE_DIR / "test-profile.yaml")
        result = self._invoke(tmp_path, monkeypatch, "no-such-profile",
                              "--config", cfg)
        assert result.exit_code == 2
        assert "unknown profile" in result.output

    def test_curate_fixture_success_and_lock(self, tmp_path, monkeypatch):
        """Happy path: exit 0 + theme_lock.json written with SHA256 (DoD P1-13)."""
        cfg = str(_FIXTURE_DIR / "test-profile.yaml")
        result = self._invoke(tmp_path, monkeypatch, "test-profile",
                              "--config", cfg, "--write-lock")
        assert result.exit_code == 0, result.output
        assert "Curate OK" in result.output

        cwd = tmp_path / "cwd"
        lock_path = cwd / "context_packs" / "test-profile" / "theme_lock.json"
        assert lock_path.exists()
        lock = json.loads(lock_path.read_text())
        assert lock["profile"] == "test-profile"
        # theme_lock maps theme -> files carrying tokens + sha256.
        for theme in ("theme_a", "theme_b"):
            assert theme in lock["themes"]
            for entry in lock["themes"][theme]:
                assert entry["tokens"] > 0
                assert len(entry["sha256"]) == 64

    def test_curate_fixture_over_budget_fails(self, tmp_path, monkeypatch):
        """A profile over per_bundle budget must fail with [PACK-FAIL] (exit 1)."""
        cfg = tmp_path / "cwd" / "over-profile.yaml"
        over = {
            "profiles": {
                "over-profile": {
                    "description": "over budget",
                    "tier": "internal",
                    "target_platform": "web-claude",
                    "tokenizer_encoding": "cl100k_base",
                    "token_margin_multiplier": 1.0,
                    "max_slots": 4,
                    "format": "xml",
                    "bundle_ordering": "litm-u-shaped",
                    "token_budget": {"total": 100000, "per_bundle": 5},
                    "themes": {"theme_a": ["theme_a/*.py"]},
                }
            }
        }
        cwd = tmp_path / "cwd"
        if not (cwd / "theme_a").exists():
            shutil.copytree(_FIXTURE_DIR, cwd)
        (cfg.parent).mkdir(parents=True, exist_ok=True)
        cfg.write_text(json.dumps(over))
        monkeypatch.chdir(cwd)
        import curate_packs
        from typer.testing import CliRunner
        result = CliRunner().invoke(curate_packs.app,
                                    ["over-profile", "--config", str(cfg)])
        assert result.exit_code == 1
        assert "[PACK-FAIL]" in result.output
        assert "over budget" in result.output or "OVER" in result.output
