#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""infra_inventory.py — the anti-blindspot organ (Carmack audit remediation #5).

Institutional memory is an EVENT ledger; this script is the INVENTORY ledger.
It walks a declared component registry and mechanically derives, per component:
    E  exists        — declared paths/globs resolve on disk
    I  implemented   — entry symbol present (AST scan / structural probe)
    W  wired         — wire-target-class evidence found OUTSIDE tests
                       (imports, CLI registration, hook wiring, MCP registration,
                       or live-doc reference for doc-only components)
    D  documented    — all declared doc-refs resolve (file exists + keyword hit)

Verdict engine (ordered rules):
    not exists + documented            -> GHOST     (documented-but-nonexistent)
    not exists + not documented        -> CUT       (absent / already excised)
    exists + implemented == False      -> FIX
    exists + wired == False:
        runtime traces absent          -> CEREMONY  (delete-probe heuristic:
                                                       implemented, unwired, never ran)
        runtime traces present         -> FIX
    exists + documented == False       -> FIX
    otherwise                          -> KEEP

CI mode (--ci) diffs against a baseline snapshot and exits non-zero when any
component regresses (severity increases, or any E/I/W/D dimension flips True->False).
GHOST/CEREMONY -> CUT is treated as remediation (improvement), not regression.

Usage:
    python3 scripts/infra_inventory.py                 # human table
    python3 scripts/infra_inventory.py --json          # machine JSON to stdout
    python3 scripts/infra_inventory.py --update-baseline
    python3 scripts/infra_inventory.py --ci            # exit 1 on regression

Registry: embedded below (single-file deliverable; schema co-evolves with probes).
Override with --registry <yaml> for future external registries (PyYAML).

Constraints honored: stdlib + PyYAML only; sync (AnyIO n/a for offline script);
idempotent; targets <10s on repo scale; reads nothing outside the repo root.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

DEFAULT_BASELINE = Path("data/coordination/infra_inventory_baseline.json")

VERDICTS = ("KEEP", "FIX", "CUT", "GHOST", "CEREMONY")
SEVERITY = {"KEEP": 0, "FIX": 1, "CEREMONY": 2, "GHOST": 3, "CUT": 3}
WIRE_CLASSES = ("import", "cli", "hook", "mcp", "doc-only", "none")

# Directories never counted as wiring evidence (tests prove nothing runs).
WIRE_EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "node_modules",
                     "archive", "tests", "data", ".pytest_cache"}
# Never scanned at all (any probe).
SCAN_SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", ".pytest_cache"}
MAX_SCAN_BYTES = 1_000_000


# --------------------------------------------------------------------------
# Registry (seeded from CARMACK_CONTEXT_INFRA_AUDIT.md §1, 2026-08-25)
# --------------------------------------------------------------------------

@dataclass
class DocRef:
    path: str
    keyword: str
    negate: bool = False  # when True, documented requires keyword ABSENT (defect detector)


@dataclass
class ComponentSpec:
    name: str
    subsystem: str                      # context | instructions | continuation
    paths: list[str]                    # globs relative to repo root
    entry_symbol: Optional[str] = None  # class/function probed for implementation
    entry_file: Optional[str] = None    # file scanned for symbol (default: first concrete path)
    wire_class: str = "import"          # one of WIRE_CLASSES
    wire_patterns: list[str] = field(default_factory=list)   # regexes = wiring evidence
    wire_roots: list[str] = field(default_factory=list)      # override default search roots
    doc_refs: list[DocRef] = field(default_factory=list)
    trace_globs: list[str] = field(default_factory=list)     # runtime-trace evidence (anti-ceremony)
    extra_probe: Optional[str] = None   # named structural probe (see EXTRA_PROBES)
    freshness_path: Optional[str] = None  # file whose mtime proves the mechanism RAN recently
    freshness_hours: Optional[int] = None  # max age for freshness_path
    expected: str = "KEEP"
    notes: str = ""


def _imp(mod_fragment: str) -> list[str]:
    """Standard import-evidence patterns for a module fragment."""
    return [rf"(from\s+[\w.]*{mod_fragment}[\w.]*\s+import)|(import\s+[\w.]*{mod_fragment})"]


REGISTRY: list[ComponentSpec] = [
    # ---------------- A. CONTEXT SYSTEMS ----------------
    ComponentSpec(
        name="MemoryStore", subsystem="context",
        paths=["src/omega/memory_store.py"],
        entry_symbol="MemoryStore", wire_class="import",
        wire_patterns=_imp("memory_store"),
        doc_refs=[DocRef("docs/user/ONBOARDING_GUIDE.md", "MemoryStore")],
        expected="KEEP"),
    ComponentSpec(
        name="Memory module (spatial/blocks/recall)", subsystem="context",
        paths=["src/omega/memory/__init__.py"],
        wire_class="import",
        wire_patterns=[r"omega\.memory\.(providers|spatial|recall|blocks|compaction|vector_adapters)"],
        doc_refs=[DocRef("docs/user/ONBOARDING_GUIDE.md", "memory")],
        expected="KEEP"),
    ComponentSpec(
        name="ContextBuilder", subsystem="context",
        paths=["src/omega/oracle/context_builder.py"],
        entry_symbol="ContextBuilder", wire_class="import",
        wire_patterns=_imp("context_builder"),
        doc_refs=[DocRef("docs/user/ONBOARDING_GUIDE.md", "ContextBuilder")],
        expected="KEEP"),
    ComponentSpec(
        name="Headroom semantic compression", subsystem="context",
        paths=["src/omega/oracle/middleware/headroom.py"],
        entry_symbol="get_headroom_middleware", wire_class="import",
        wire_patterns=[r"middleware\.headroom|get_headroom_middleware"],
        doc_refs=[DocRef("docs/decisions/PIVOT_LOG_CANONICAL.md", "headroom")],
        notes="MCP headroom_retrieve served by external omega-hub; in-repo wiring = middleware chain.",
        expected="KEEP"),
    ComponentSpec(
        name="CompactionHarvester", subsystem="context",
        paths=["src/omega/oracle/compaction_harvester.py"],
        entry_symbol="CompactionHarvester", wire_class="import",
        wire_patterns=[r"compaction_harvester\s+import|get_harvester"],
        doc_refs=[DocRef("docs/research/R_HYDRATION_RECEIPT_COMPACTION_DETECTION_20260716.md", "[Cc]ompaction")],
        notes="Audit orphan: implemented-but-undocumented (D=part).",
        expected="KEEP"),
    ComponentSpec(
        name="anchored-summary.md (Tier-2 lifeboat)", subsystem="context",
        paths=[".opencode/anchored-summary.md"],
        wire_class="doc-only",
        wire_patterns=[r"anchored-summary"],
        wire_roots=["OMEGA_CODEX.md", ".opencode/hooks"],
        doc_refs=[DocRef("OMEGA_CODEX.md", "anchored-summary")],
        expected="KEEP"),
    ComponentSpec(
        name="SESSION_ANCHOR.md", subsystem="context",
        paths=["data/coordination/SESSION_ANCHOR.md"],
        freshness_path="data/coordination/SESSION_ANCHOR.md", freshness_hours=48,
        wire_class="doc-only",
        wire_patterns=[r"SESSION_ANCHOR"],
        wire_roots=["OMEGA_CODEX.md"],
        doc_refs=[DocRef("OMEGA_CODEX.md", "SESSION_ANCHOR")],
        notes="Audit FIX (2026-08-25): ~14h stale through the entire FLE campaign. "
              "Freshness gate added so that failure class can never recur silently.",
        expected="KEEP"),
    ComponentSpec(
        name="session_gnosis files", subsystem="context",
        paths=["data/entities/*/workspace/session_gnosis*.md"],
        wire_class="doc-only",
        wire_patterns=[r"session_gnosis"],
        wire_roots=["OMEGA_CODEX.md"],
        doc_refs=[DocRef("OMEGA_CODEX.md", "session_gnosis")],
        expected="KEEP"),
    ComponentSpec(
        name="Hivemind continuation store", subsystem="context",
        paths=["data/knowledge/HALL_OF_RECORDS"],
        wire_class="mcp",
        wire_patterns=[r"post_context|get_continuation"],
        doc_refs=[DocRef("OMEGA_CODEX.md", "continuation")],
        notes="MCP tools served by omega-hub (external); in-repo evidence = cold-store dir + references.",
        expected="KEEP"),
    ComponentSpec(
        name="HMC Collaboration Hub", subsystem="context",
        paths=["data/coordination/HMC_COLLABORATION_HUB.md"],
        wire_class="doc-only",
        wire_patterns=[r"HMC_COLLABORATION_HUB|HMC Hub"],
        doc_refs=[],
        notes="FIRST-RUN CORRECTION: Carmack audit §0 verdict 'CUT (already done)' was based on the "
              "archived v1.5.1 July-outage forum — but a live v2.0 rewrite (2026-08-22, pre-debut, "
              "kali-owned) is ACTIVE. The audit itself carried a stale claim; inventory caught it.",
        expected="KEEP"),
    ComponentSpec(
        name="HMC Watcher (Quad-Forge)", subsystem="context",
        paths=["src/omega/orchestrator/hmc_watcher.py"],
        entry_symbol="HMCWatcher", wire_class="import",
        wire_patterns=_imp("hmc_watcher"),
        doc_refs=[DocRef("OMEGA_ENGINE.md", "Quad-Forge")],
        notes="Impossible API (anyio.Path.watch), unwired, start() untested. Remediation #1: delete + strike medal.",
        expected="CUT"),

    # ---------------- B. INSTRUCTIONS SYSTEMS ----------------
    ComponentSpec(
        name="Root AGENTS.md", subsystem="instructions",
        paths=["AGENTS.md"],
        wire_class="doc-only",
        wire_patterns=[r"AGENTS\.md"],
        wire_roots=["OMEGA_CODEX.md", "SOVEREIGN_MANDATES.md"],
        doc_refs=[DocRef("OMEGA_CODEX.md", "AGENTS")],
        notes="Absent from entire git history; ~462 citers. WP-E owns reconstruction.",
        expected="GHOST"),
    ComponentSpec(
        name="OMEGA_CODEX.md (hydration law)", subsystem="instructions",
        paths=["OMEGA_CODEX.md"],
        wire_class="hook",
        wire_patterns=[r"OMEGA_CODEX|codex_cat|CODEX_CAT"],
        wire_roots=[".opencode/hooks", "Makefile"],
        doc_refs=[DocRef("docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md", "OMEGA_CODEX")],
        expected="KEEP"),
    ComponentSpec(
        name="Codex freshness automation", subsystem="instructions",
        paths=[".opencode/hooks/session_end.py"],
        entry_symbol="_regenerate_codex", wire_class="hook",
        wire_patterns=[r"check-codex-stale|codex"],
        wire_roots=["Makefile", ".opencode/wrapper.sh"],
        freshness_path="OMEGA_CODEX.md", freshness_hours=24,
        doc_refs=[DocRef("OMEGA_CODEX.md", "hydration")],
        notes="Audit FIX (2026-08-25): refresh silently did NOT fire across a dozen session ends. "
              "Freshness gate = OMEGA_CODEX.md mtime < 24h; regression now detectable by --ci.",
        expected="KEEP"),
    ComponentSpec(
        name="Agent markdown defs (.opencode/agents/*.md)", subsystem="instructions",
        paths=[".opencode/agents/*.md"],
        wire_class="cli",
        wire_patterns=[r'"agent"|"agents"'],
        wire_roots=["opencode.json"],
        doc_refs=[DocRef("OMEGA_CODEX.md", "agent")],
        notes="Loader is OpenCode-native directory scan; opencode.json agent key = config surface.",
        expected="KEEP"),
    ComponentSpec(
        name="Agent-level instructions[] (opencode.json)", subsystem="instructions",
        paths=["opencode.json"],
        extra_probe="opencode_json_agent_prompts", wire_class="cli",
        wire_patterns=[r'"instructions"'],
        wire_roots=["opencode.json"],
        doc_refs=[DocRef("OMEGA_CODEX.md", "instruction")],
        notes="Audit FIX (WP-B2): agents carry instructions[], zero prompt:{file:} — GAP-4 exposure class.",
        expected="FIX"),
    ComponentSpec(
        name="Root instructions[] chain (opencode.json)", subsystem="instructions",
        paths=["opencode.json"],
        extra_probe="opencode_json_root_instructions", wire_class="cli",
        wire_patterns=[r'"instructions"'],
        wire_roots=["opencode.json"],
        doc_refs=[],
        notes="Live injection verified by audit; still carries archive entry (G5 pending).",
        expected="KEEP"),
    ComponentSpec(
        name="Scribe agent def", subsystem="instructions",
        paths=[".opencode/agents/scribe.md"],
        wire_class="doc-only",
        wire_patterns=[r"Scribe agent"],
        wire_roots=["SOVEREIGN_MANDATES.md"],
        doc_refs=[DocRef("SOVEREIGN_MANDATES.md", "Scribe agent")],
        notes="Remediation #2 executed (def cut). Residual GHOST: M11 still cites 'Scribe agent' as "
              "canonical executor of a pipeline that was scrapped — de-document or re-document.",
        expected="GHOST"),

    # ---------------- C. CONTINUATION SYSTEMS ----------------
    ComponentSpec(
        name="OpenCode native compaction", subsystem="continuation",
        paths=["opencode.json"],
        wire_class="doc-only",
        wire_patterns=[r"compaction"],
        wire_roots=["OMEGA_CODEX.md"],
        doc_refs=[DocRef("OMEGA_CODEX.md", "compaction")],
        expected="KEEP"),
    ComponentSpec(
        name="session_end.py hook", subsystem="continuation",
        paths=[".opencode/hooks/session_end.py"],
        entry_symbol="_write_timestamp", wire_class="hook",
        wire_patterns=[r"session_end\.py"],
        wire_roots=[".opencode/wrapper.sh"],
        doc_refs=[DocRef("data/coordination/CONSULTANT_TUTORIAL_PRE_COMPACTION.md", "session_end")],
        expected="KEEP"),
    ComponentSpec(
        name="Manual lesson staging (proposed_lessons.yaml)", subsystem="continuation",
        paths=["data/entities/*/proposed_lessons.yaml"],
        wire_class="hook",
        wire_patterns=[r"proposed_lessons|proposed"],
        wire_roots=[".opencode/hooks"],
        doc_refs=[DocRef("SOVEREIGN_MANDATES.md", "proposed_lessons")],
        expected="KEEP"),
    ComponentSpec(
        name="soul_promote", subsystem="continuation",
        paths=["scripts/soul_promote.py"],
        entry_symbol="main", wire_class="cli",
        wire_patterns=[r"soul_promote"],
        doc_refs=[DocRef("data/coordination/CONSULTANT_TUTORIAL_PRE_COMPACTION.md", "soul_promote")],
        notes="IMPLEMENTED 2026-08-25 20:16 (review-gated, atomic, dry-run default) — audit's "
              "'one-way door' closed same-day. Verify --ci keeps it wired.",
        expected="KEEP"),
    ComponentSpec(
        name="WAKE_STATE decision queue", subsystem="continuation",
        paths=["data/coordination/WAKE_STATE.json"],
        wire_class="cli",
        wire_patterns=[r"WAKE_STATE"],
        doc_refs=[DocRef("data/coordination/CONSULTANT_TUTORIAL_PRE_COMPACTION.md", "WAKE_STATE")],
        expected="KEEP"),
    ComponentSpec(
        name="Handoff packets (active queue)", subsystem="continuation",
        paths=["data/handoff/**/*.json"],
        wire_class="import",
        wire_patterns=[r"data/handoff\b|data[/\\]handoff"],
        doc_refs=[DocRef("docs/strategy/FLEET_TEAM_PLAYBOOK.md", "handoff")],
        expected="KEEP"),
    ComponentSpec(
        name="Legacy synonym dir (data/handoffs/)", subsystem="continuation",
        paths=["data/handoffs"],
        wire_class="none",
        doc_refs=[],
        notes="Art. XII synonym-dir recurrence #2. Remediation #6: consolidate into data/handoff/archive/.",
        expected="CUT"),
    ComponentSpec(
        name="CONSULTANT_TUTORIAL_PRE_COMPACTION.md", subsystem="continuation",
        paths=["data/coordination/CONSULTANT_TUTORIAL_PRE_COMPACTION.md"],
        wire_class="doc-only",
        wire_patterns=[r"CONSULTANT_TUTORIAL"],
        wire_roots=["data/coordination/fle_study_20260825/CARMACK_CONTEXT_INFRA_AUDIT.md"],
        doc_refs=[
            DocRef("data/coordination/fle_study_20260825/CARMACK_CONTEXT_INFRA_AUDIT.md",
                   "TUTORIAL"),
            # Negated ref = defect detector: tutorial must NOT cite nonexistent mechanisms.
            DocRef("data/coordination/CONSULTANT_TUTORIAL_PRE_COMPACTION.md",
                   "soul_promote\\s*\\.?\\s*$|requires explicit soul_promote", negate=True),
        ],
        notes="Audit FIX(minor) EXECUTED 2026-08-25 20:19: tutorial now cites the real "
              "scripts/soul_promote.py implementation. Negated doc-ref remains as a guard against "
              "any future citation of nonexistent mechanisms.",
        expected="KEEP"),
]


# --------------------------------------------------------------------------
# Probe machinery
# --------------------------------------------------------------------------

@dataclass
class ProbeResult:
    """Typed per-component probe outcome. Dimensions are True/False/None(n/a)."""
    exists: Optional[bool]
    implemented: Optional[bool]
    wired: Optional[bool]
    documented: Optional[bool]
    verdict: str
    evidence: dict = field(default_factory=dict)

    def dimensions(self) -> dict:
        return {"E": self.exists, "I": self.implemented,
                "W": self.wired, "D": self.documented}


def _resolve_globs(root: Path, patterns: list[str]) -> list[Path]:
    out: list[Path] = []
    for pat in patterns:
        out.extend(sorted(p for p in root.glob(pat) if p.is_file() or p.is_dir()))
    return out


def _iter_text_files(root: Path, rel_roots: list[str]) -> list[Path]:
    files: list[Path] = []
    for r in rel_roots:
        base = root / r
        if base.is_file():
            files.append(base)
            continue
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if any(part in SCAN_SKIP_DIRS or part in WIRE_EXCLUDE_DIRS
                   for part in p.relative_to(root).parts):
                continue
            try:
                if p.stat().st_size > MAX_SCAN_BYTES:
                    continue
                files.append(p)
            except OSError:
                continue
    return files


_WIRE_CACHE: dict[tuple, str] = {}


def _corpus_text(root: Path, rel_roots: list[str]) -> str:
    key = (str(root), tuple(rel_roots))
    if key not in _WIRE_CACHE:
        chunks = []
        for p in _iter_text_files(root, rel_roots):
            try:
                chunks.append(p.read_text(errors="replace"))
            except OSError:
                continue
        _WIRE_CACHE[key] = "\n".join(chunks)
    return _WIRE_CACHE[key]


def _symbol_present(path: Path, symbol: str) -> bool:
    try:
        tree = ast.parse(path.read_text(errors="replace"))
    except (SyntaxError, OSError):
        return bool(re.search(rf"\b(def|class)\s+{re.escape(symbol)}\b",
                              path.read_text(errors="replace")))
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) \
                and node.name == symbol:
            return True
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == symbol:
                    return True
    return False


def _probe_opencode_json_agent_prompts(root: Path) -> tuple[bool, dict]:
    """Implemented = at least one agent migrated to prompt:{file:} refs."""
    try:
        data = json.loads((root / "opencode.json").read_text())
    except (OSError, json.JSONDecodeError) as e:
        return False, {"error": str(e)}
    agents = data.get("agent", {})
    with_instr = sorted(a for a, v in agents.items()
                        if isinstance(v, dict) and v.get("instructions"))
    with_file = sorted(a for a, v in agents.items()
                       if isinstance(v, dict) and v.get("prompt"))
    return bool(with_file), {
        "agents_total": len(agents),
        "with_instructions_array": len(with_instr),
        "with_prompt_file": len(with_file),
    }


def _probe_opencode_json_root_instructions(root: Path) -> tuple[bool, dict]:
    try:
        data = json.loads((root / "opencode.json").read_text())
    except (OSError, json.JSONDecodeError) as e:
        return False, {"error": str(e)}
    instr = data.get("instructions", [])
    return len(instr) > 0, {"root_instruction_count": len(instr)}


EXTRA_PROBES = {
    "opencode_json_agent_prompts": _probe_opencode_json_agent_prompts,
    "opencode_json_root_instructions": _probe_opencode_json_root_instructions,
}


def derive_verdict(exists: Optional[bool], implemented: Optional[bool],
                   wired: Optional[bool], documented: Optional[bool],
                   has_traces: bool) -> str:
    """Pure verdict engine — ordered rules, no I/O. Unit-testable in isolation."""
    if exists is False:
        return "GHOST" if documented else "CUT"
    if implemented is False:
        return "FIX"
    if wired is False:
        return "FIX" if has_traces else "CEREMONY"
    if documented is False:
        return "FIX"
    return "KEEP"


def probe_component(spec: ComponentSpec, root: Path) -> ProbeResult:
    ev: dict = {}

    hits = _resolve_globs(root, spec.paths)
    exists = len(hits) > 0
    ev["resolved_paths"] = [str(p.relative_to(root)) for p in hits[:10]]

    # --- implemented ---
    implemented: Optional[bool] = None
    if spec.extra_probe:
        fn = EXTRA_PROBES.get(spec.extra_probe)
        if fn is None:
            raise ValueError(f"unknown extra_probe: {spec.extra_probe}")
        implemented, extra_ev = fn(root)
        ev["extra_probe"] = extra_ev
    elif spec.entry_symbol:
        target = root / spec.entry_file if spec.entry_file else (
            hits[0] if hits and hits[0].is_file() else None)
        if target is None or not target.is_file():
            pkg_init = hits[0] / "__init__.py" if hits and hits[0].is_dir() else None
            target = pkg_init
        implemented = bool(target and _symbol_present(target, spec.entry_symbol))
        ev["entry_symbol"] = spec.entry_symbol
        ev["entry_file"] = str(target.relative_to(root)) if target else None

    # --- freshness (mechanism ran recently — the codex-refresh lesson) ---
    if spec.freshness_path and spec.freshness_hours:
        fp = root / spec.freshness_path
        if not fp.is_file():
            fresh = False
            ev["freshness"] = f"missing: {spec.freshness_path}"
        else:
            age_h = (time.time() - fp.stat().st_mtime) / 3600.0
            fresh = age_h <= spec.freshness_hours
            ev["freshness"] = f"{age_h:.1f}h old (limit {spec.freshness_hours}h)"
        implemented = True if implemented is None else implemented
        implemented = implemented and fresh

    # --- wired ---
    wired: Optional[bool] = None
    if spec.wire_class != "none":
        roots = spec.wire_roots or ["src", "scripts", ".opencode", "config",
                                    "Makefile", "opencode.json"]
        corpus = _corpus_text(root, roots)
        wired = any(re.search(pat, corpus) for pat in spec.wire_patterns)
        ev["wire_class"] = spec.wire_class
        ev["wire_hits"] = [p for p in spec.wire_patterns if re.search(p, corpus)]

    # --- documented ---
    documented: Optional[bool] = None
    if spec.doc_refs:
        results = []
        for ref in spec.doc_refs:
            f = root / ref.path
            present = False
            if f.is_file():
                try:
                    present = re.search(ref.keyword, f.read_text(errors="replace"),
                                        re.IGNORECASE) is not None
                except OSError:
                    present = False
            ok = (not present) if ref.negate else present
            results.append(ok)
        documented = all(results)
        ev["doc_refs"] = {f"{r.path}::{r.keyword}{' [negate]' if r.negate else ''}": ok
                          for r, ok in zip(spec.doc_refs, results)}

    # --- runtime traces (anti-ceremony evidence) ---
    has_traces = bool(_resolve_globs(root, spec.trace_globs)) if spec.trace_globs else False

    verdict = derive_verdict(exists, implemented, wired, documented, has_traces)
    return ProbeResult(exists=exists, implemented=implemented,
                       wired=wired, documented=documented,
                       verdict=verdict, evidence=ev)


# --------------------------------------------------------------------------
# Reporting / CI
# --------------------------------------------------------------------------

def run_inventory(root: Path, registry: list[ComponentSpec]) -> dict:
    _WIRE_CACHE.clear()  # per-run cache only: never reuse corpus across runs
    components = {}
    rows = []
    for spec in registry:
        res = probe_component(spec, root)
        d = res.dimensions()
        components[spec.name] = {
            "subsystem": spec.subsystem,
            "E": d["E"], "I": d["I"], "W": d["W"], "D": d["D"],
            "verdict": res.verdict,
            "expected": spec.expected,
            "notes": spec.notes,
            "evidence": res.evidence,
        }
        rows.append((spec.subsystem, spec.name, d, res.verdict, spec.expected))
    return {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "root": str(root), "components": components}


def render_table(report: dict) -> str:
    lines = []
    lines.append("=" * 96)
    lines.append(f"INFRASTRUCTURE INVENTORY — generated {report['generated']}  "
                 f"(E=exists I=implemented W=wired D=documented; '-'=n/a)")
    lines.append("=" * 96)
    last_sub = None
    for sub in ("context", "instructions", "continuation"):
        for name, c in report["components"].items():
            if c["subsystem"] != sub:
                continue
            if sub != last_sub:
                lines.append(f"\n--- {sub.upper()} SYSTEMS " + "-" * 60)
                last_sub = sub
            fmt = lambda v: {True: "Y", False: "N", None: "-"}[v]
            flag = "" if c["verdict"] == c["expected"] else f"  [expected {c['expected']}]"
            lines.append(f"{name:<44} E={fmt(c['E'])} I={fmt(c['I'])} "
                         f"W={fmt(c['W'])} D={fmt(c['D'])}  -> {c['verdict']}{flag}")
    counts: dict[str, int] = {}
    for c in report["components"].values():
        counts[c["verdict"]] = counts.get(c["verdict"], 0) + 1
    lines.append("\n" + "-" * 96)
    lines.append("VERDICT SUMMARY: " + "  ".join(
        f"{v}={counts[v]}" for v in VERDICTS if v in counts))
    drift = [n for n, c in report["components"].items() if c["verdict"] != c["expected"]]
    if drift:
        lines.append(f"DRIFT vs EXPECTED ({len(drift)}): " + "; ".join(drift))
    return "\n".join(lines)


def diff_baseline(current: dict, baseline: dict) -> list[str]:
    regressions = []
    old = baseline.get("components", {})
    for name, c in current["components"].items():
        prev = old.get(name)
        if prev is None:
            continue  # new component — not a regression
        sev_old, sev_new = SEVERITY[prev["verdict"]], SEVERITY[c["verdict"]]
        excised = prev["verdict"] in ("GHOST", "CEREMONY") and c["verdict"] == "CUT"
        improved = excised or sev_new < sev_old
        if sev_new > sev_old and not excised:
            regressions.append(
                f"{name}: verdict {prev['verdict']} -> {c['verdict']}")
        # Dimension flips count as regressions unless the component's overall
        # state improved (e.g., de-documenting a GHOST into CUT is remediation).
        if not improved:
            for dim in ("E", "I", "W", "D"):
                if prev[dim] is True and c[dim] is False:
                    regressions.append(f"{name}: {dim} True -> False")
    return regressions


def load_registry(path: Optional[Path]) -> list[ComponentSpec]:
    if path is None:
        return REGISTRY
    import yaml  # local import: PyYAML only needed for external registries
    raw = yaml.safe_load(path.read_text())
    specs = []
    for item in raw["components"]:
        refs = [DocRef(**d) for d in item.pop("doc_refs", [])]
        specs.append(ComponentSpec(doc_refs=refs, **item))
    return specs


def main(argv: Optional[list[str]] = None,
         registry: Optional[list[ComponentSpec]] = None) -> int:
    ap = argparse.ArgumentParser(description="Anti-blindspot infrastructure inventory")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--registry", default=None, help="Optional YAML registry override")
    ap.add_argument("--json", action="store_true", help="Machine JSON to stdout")
    ap.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    ap.add_argument("--update-baseline", action="store_true")
    ap.add_argument("--ci", action="store_true",
                    help="Exit non-zero on regression vs baseline")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    if registry is None:
        registry = load_registry(Path(args.registry) if args.registry else None)
    report = run_inventory(root, registry)

    if args.update_baseline:
        bp = Path(args.baseline)
        bp.parent.mkdir(parents=True, exist_ok=True)
        tmp = bp.with_suffix(".tmp")
        tmp.write_text(json.dumps(report, indent=2))
        tmp.replace(bp)  # atomic write (T10 pattern)
        print(f"baseline written: {bp}")

    regressions: list[str] = []
    if args.ci:
        bpath = Path(args.baseline)
        if not bpath.is_file():
            print(f"[CI] FAIL: baseline missing: {bpath}", file=sys.stderr)
            return 2
        baseline = json.loads(bpath.read_text())
        regressions = diff_baseline(report, baseline)
        if regressions:
            print("[CI] REGRESSIONS DETECTED:", file=sys.stderr)
            for r in regressions:
                print(f"  - {r}", file=sys.stderr)
            return 1
        if not args.json:
            print("[CI] OK: no inventory regressions vs baseline")

    if args.json:
        payload = dict(report)
        payload["regressions_vs_baseline"] = regressions
        print(json.dumps(payload, indent=2))
    elif not args.ci or not regressions:
        print(render_table(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
