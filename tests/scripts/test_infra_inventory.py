"""Contract tests for scripts/infra_inventory.py (M21 Gate Integrity).

All tests use tmp fixtures — no dependence on live repo state.
Load strategy: importlib from file path (tests/scripts is not a package).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "infra_inventory.py"
_spec = importlib.util.spec_from_file_location("infra_inventory", SCRIPT)
assert _spec is not None and _spec.loader is not None
ii = importlib.util.module_from_spec(_spec)
sys.modules["infra_inventory"] = ii
_spec.loader.exec_module(ii)


# --------------------------------------------------------------------------
# Fixtures: synthetic repo trees
# --------------------------------------------------------------------------

def make_repo(tmp_path: Path) -> Path:
    """Minimal repo shape exercising every probe dimension."""
    root = tmp_path / "repo"
    (root / "src" / "omega").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "scripts").mkdir()
    # implemented + wired + documented -> KEEP
    (root / "src" / "omega" / "widget.py").write_text(
        "class Widget:\n    pass\n")
    (root / "src" / "omega" / "app.py").write_text(
        "from omega.widget import Widget\n")
    (root / "docs" / "guide.md").write_text("The Widget is documented here.\n")
    # documented but nonexistent -> GHOST
    (root / "docs" / "ghost_doc.md").write_text("soul_promote does magic.\n")
    # implemented but unwired, no traces -> CEREMONY
    (root / "src" / "omega" / "ceremony.py").write_text(
        "def dead_ritual():\n    return 1\n")
    # exists but entry symbol missing -> FIX
    (root / "src" / "omega" / "hollow.py").write_text("# nothing here\n")
    # unwired but runtime traces present -> FIX (not CEREMONY)
    (root / "src" / "omega" / "traced.py").write_text(
        "def traced_fn():\n    return 2\n")
    (root / "data" / "logs").mkdir(parents=True)
    (root / "data" / "logs" / "traced_fn.run.log").write_text("ran\n")
    return root


def base_registry() -> list:
    return [
        ii.ComponentSpec(
            name="Widget", subsystem="context",
            paths=["src/omega/widget.py"], entry_symbol="Widget",
            wire_class="import", wire_patterns=[r"widget\s+import"],
            doc_refs=[ii.DocRef("docs/guide.md", "Widget")]),
        ii.ComponentSpec(
            name="GhostThing", subsystem="context",
            paths=["scripts/soul_promote_impl.py"],
            wire_class="cli", wire_patterns=[r"soul_promote"],
            doc_refs=[ii.DocRef("docs/ghost_doc.md", "soul_promote")]),
        ii.ComponentSpec(
            name="Ceremony", subsystem="continuation",
            paths=["src/omega/ceremony.py"], entry_symbol="dead_ritual",
            wire_class="import", wire_patterns=[r"ceremony\s+import"]),
        ii.ComponentSpec(
            name="Hollow", subsystem="instructions",
            paths=["src/omega/hollow.py"], entry_symbol="MissingClass",
            wire_class="none"),
        ii.ComponentSpec(
            name="TracedButUnwired", subsystem="continuation",
            paths=["src/omega/traced.py"], entry_symbol="traced_fn",
            wire_class="import", wire_patterns=[r"traced\s+import"],
            trace_globs=["data/logs/traced_fn*"]),
    ]


# --------------------------------------------------------------------------
# Registry contract
# --------------------------------------------------------------------------

class TestRegistry:
    def test_embedded_registry_loads(self):
        assert len(ii.REGISTRY) >= 20, "seed must cover the full audit inventory"

    def test_embedded_registry_fields_valid(self):
        for spec in ii.REGISTRY:
            assert spec.name and spec.subsystem in ("context", "instructions", "continuation")
            assert spec.wire_class in ii.WIRE_CLASSES
            assert spec.expected in ii.VERDICTS, spec.name
            assert spec.paths, spec.name

    def test_yaml_registry_override(self, tmp_path):
        yaml_file = tmp_path / "reg.yaml"
        yaml_file.write_text(
            "components:\n"
            "  - name: YamlComp\n"
            "    subsystem: context\n"
            "    paths: ['some/path.md']\n"
            "    wire_class: none\n"
            "    expected: KEEP\n")
        specs = ii.load_registry(yaml_file)
        assert len(specs) == 1
        assert isinstance(specs[0], ii.ComponentSpec)
        assert specs[0].name == "YamlComp"


# --------------------------------------------------------------------------
# Probe contract (typed results)
# --------------------------------------------------------------------------

class TestProbes:
    def test_probe_returns_typed_result(self, tmp_path):
        root = make_repo(tmp_path)
        res = ii.probe_component(base_registry()[0], root)
        assert isinstance(res, ii.ProbeResult)
        assert res.exists is True
        assert res.implemented is True
        assert res.wired is True
        assert res.documented is True
        assert isinstance(res.evidence, dict)

    def test_symbol_absent_means_not_implemented(self, tmp_path):
        root = make_repo(tmp_path)
        res = ii.probe_component(base_registry()[3], root)  # Hollow / MissingClass
        assert res.exists is True
        assert res.implemented is False

    def test_wiring_ignores_test_dirs(self, tmp_path):
        """Wire evidence inside tests/ must NOT count."""
        root = make_repo(tmp_path)
        (root / "src" / "omega" / "app.py").unlink()  # remove the real wire evidence
        (root / "tests").mkdir()
        (root / "tests" / "test_widget.py").write_text(
            "from omega.widget import Widget\n")
        spec = ii.ComponentSpec(
            name="Widget2", subsystem="context",
            paths=["src/omega/widget.py"], entry_symbol="Widget",
            wire_class="import", wire_patterns=[r"widget\s+import"])
        res = ii.probe_component(spec, root)
        assert res.wired is False  # only evidence lives under tests/

    def test_extra_probe_opencode_json(self, tmp_path):
        root = tmp_path / "cfg"
        root.mkdir()
        (root / "opencode.json").write_text(json.dumps({
            "agent": {"a": {"instructions": ["x"]},
                      "b": {"prompt": {"file": ".opencode/a.md"}}}}))
        ok, ev = ii._probe_opencode_json_agent_prompts(root)
        assert ok is True
        assert ev["with_instructions_array"] == 1
        assert ev["with_prompt_file"] == 1

    def test_negated_doc_ref_detects_defect(self, tmp_path):
        """negate=True: documented requires the keyword ABSENT (defect detector)."""
        root = tmp_path / "neg"
        (root / "docs").mkdir(parents=True)
        spec = ii.ComponentSpec(
            name="Tutorial", subsystem="continuation",
            paths=["docs/tutorial.md"], wire_class="none",
            doc_refs=[ii.DocRef("docs/tutorial.md", "ghost_api", negate=True)])
        # defect present -> documented False
        (root / "docs" / "tutorial.md").write_text("requires explicit ghost_api.\n")
        res = ii.probe_component(spec, root)
        assert res.documented is False
        assert res.verdict == "FIX"
        # de-documented -> documented True
        (root / "docs" / "tutorial.md").write_text("clean now.\n")
        res = ii.probe_component(spec, root)
        assert res.documented is True
        assert res.verdict == "KEEP"

    def test_freshness_gate_flags_stale_mechanism(self, tmp_path):
        """freshness_path older than freshness_hours => implemented False => FIX."""
        import os
        root = tmp_path / "fresh"
        (root / "hooks").mkdir(parents=True)
        (root / "hooks" / "hook.py").write_text("def run():\n    pass\n")
        (root / "OUTPUT.md").write_text("stale\n")
        old = time.time() - 100 * 3600  # 100h old
        os.utime(root / "OUTPUT.md", (old, old))
        spec = ii.ComponentSpec(
            name="Refresher", subsystem="instructions",
            paths=["hooks/hook.py"], entry_symbol="run", wire_class="none",
            freshness_path="OUTPUT.md", freshness_hours=24)
        res = ii.probe_component(spec, root)
        assert res.implemented is False
        assert res.verdict == "FIX"
        assert "100" in res.evidence["freshness"]
        # fresh mtime -> implemented True
        os.utime(root / "OUTPUT.md", (time.time(), time.time()))
        res = ii.probe_component(spec, root)
        assert res.implemented is True
        assert res.verdict == "KEEP"


# --------------------------------------------------------------------------
# Verdict engine (pure function — exhaustive class coverage)
# --------------------------------------------------------------------------

class TestVerdictEngine:
    def test_keep(self):
        assert ii.derive_verdict(True, True, True, True, False) == "KEEP"

    def test_ghost_documented_nonexistent(self):
        assert ii.derive_verdict(False, None, None, True, False) == "GHOST"

    def test_cut_undocumented_nonexistent(self):
        assert ii.derive_verdict(False, None, None, False, False) == "CUT"

    def test_fix_unimplemented(self):
        assert ii.derive_verdict(True, False, None, None, False) == "FIX"

    def test_ceremony_unwired_no_traces(self):
        assert ii.derive_verdict(True, True, False, True, False) == "CEREMONY"

    def test_unwired_with_traces_is_fix_not_ceremony(self):
        assert ii.derive_verdict(True, True, False, True, True) == "FIX"

    def test_fix_undocumented(self):
        assert ii.derive_verdict(True, True, True, False, False) == "FIX"


# --------------------------------------------------------------------------
# End-to-end verdict assignment on fixture repo
# --------------------------------------------------------------------------

class TestInventoryRun:
    def test_full_run_assigns_expected_classes(self, tmp_path):
        root = make_repo(tmp_path)
        report = ii.run_inventory(root, base_registry())
        comps = report["components"]
        assert comps["Widget"]["verdict"] == "KEEP"
        assert comps["GhostThing"]["verdict"] == "GHOST"
        assert comps["Ceremony"]["verdict"] == "CEREMONY"
        assert comps["Hollow"]["verdict"] == "FIX"
        assert comps["TracedButUnwired"]["verdict"] == "FIX"

    def test_report_shape(self, tmp_path):
        root = make_repo(tmp_path)
        report = ii.run_inventory(root, base_registry())
        assert set(report) >= {"generated", "root", "components"}
        c = report["components"]["Widget"]
        assert set(c) >= {"subsystem", "E", "I", "W", "D", "verdict", "expected"}


# --------------------------------------------------------------------------
# CI regression contract
# --------------------------------------------------------------------------

class TestCI:
    def _baseline(self, tmp_path, root):
        report = ii.run_inventory(root, base_registry())
        bp = tmp_path / "baseline.json"
        bp.write_text(json.dumps(report))
        return bp

    def test_no_regression_exits_zero(self, tmp_path, capsys):
        root = make_repo(tmp_path)
        bp = self._baseline(tmp_path, root)
        rc = ii.main(["--root", str(root), "--ci", "--baseline", str(bp)], registry=base_registry())
        assert rc == 0
        assert "OK" in capsys.readouterr().out

    def test_wire_loss_is_regression_exit_one(self, tmp_path, capsys):
        root = make_repo(tmp_path)
        bp = self._baseline(tmp_path, root)
        # sever the wiring evidence
        (root / "src" / "omega" / "app.py").unlink()
        rc = ii.main(["--root", str(root), "--ci", "--baseline", str(bp)], registry=base_registry())
        assert rc == 1
        err = capsys.readouterr().err
        assert "REGRESSIONS" in err

    def test_missing_baseline_exits_two(self, tmp_path):
        root = make_repo(tmp_path)
        rc = ii.main(["--root", str(root), "--ci",
                      "--baseline", str(tmp_path / "nope.json")],
                     registry=base_registry())
        assert rc == 2

    def test_ghost_to_cut_is_remediation_not_regression(self, tmp_path):
        root = make_repo(tmp_path)
        before = ii.run_inventory(root, base_registry())
        # excise the ghost's documentation -> GHOST degrades to CUT (intended fix)
        (root / "docs" / "ghost_doc.md").unlink()
        after = ii.run_inventory(root, base_registry())
        assert before["components"]["GhostThing"]["verdict"] == "GHOST"
        assert after["components"]["GhostThing"]["verdict"] == "CUT"
        assert ii.diff_baseline(after, before) == []

    def test_new_component_is_not_regression(self, tmp_path):
        root = make_repo(tmp_path)
        bp = self._baseline(tmp_path, root)
        reg = base_registry() + [ii.ComponentSpec(
            name="BrandNew", subsystem="context", paths=["src/omega/widget.py"],
            wire_class="none")]
        report = ii.run_inventory(root, reg)
        assert ii.diff_baseline(report, json.loads(bp.read_text())) == []


# --------------------------------------------------------------------------
# CLI output contract
# --------------------------------------------------------------------------

class TestOutput:
    def test_json_flag_emits_valid_json(self, tmp_path, capsys):
        root = make_repo(tmp_path)
        rc = ii.main(["--root", str(root), "--json"], registry=base_registry())
        assert rc == 0
        payload = json.loads(capsys.readouterr().out)
        assert "components" in payload

    def test_update_baseline_writes_atomic_snapshot(self, tmp_path, capsys):
        root = make_repo(tmp_path)
        bp = tmp_path / "nested" / "baseline.json"
        rc = ii.main(["--root", str(root), "--update-baseline",
                      "--baseline", str(bp)], registry=base_registry())
        assert rc == 0
        assert bp.is_file()
        data = json.loads(bp.read_text())
        assert "Widget" in data["components"]

    def test_human_table_renders(self, tmp_path, capsys):
        root = make_repo(tmp_path)
        rc = ii.main(["--root", str(root)], registry=base_registry())
        assert rc == 0
        out = capsys.readouterr().out
        assert "INFRASTRUCTURE INVENTORY" in out
        assert "VERDICT SUMMARY" in out
