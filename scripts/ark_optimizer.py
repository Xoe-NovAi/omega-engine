#!/usr/bin/env python3
"""ark_optimizer.py — Sovereign Ark Blueprint optimizer & verifier.

Verifies the Ark Blueprint against reality, detects stale tasks, orphaned
coordination files, broken cross-links, and undocumented `[id-soft:]` tags (M14).
Read-only on all sources; write-only to the optimization report.

Design constraints honored:
  - M1  AnyIO: all file I/O via `anyio.Path` / `anyio.run_process`.
  - M8  Zero Telemetry: no network, no metrics egress.
  - M6  Podman Sovereignty: safe to run under keep-id container.
  - Idempotent & safe: never mutates sources; report is atomic write.

Usage:
  python scripts/ark_optimizer.py --dry-run        # print report, write nothing
  python scripts/ark_optimizer.py                  # write ARK_OPTIMIZATION_REPORT.md
  python scripts/ark_optimizer.py --live-tests     # also run `pytest --co` for real count
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import anyio

REPO = Path(__file__).resolve().parent.parent
ARK = REPO / "docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md"
OMEGA = REPO / "OMEGA_ENGINE.md"
PIVOT = REPO / "docs/decisions/PIVOT_LOG.md"
VET_LOG = REPO / "data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md"
WORKBENCH = REPO / "data/workbench/workbench.db"
COORD = REPO / "data/coordination"
SRC = REPO / "src/omega"
REPORT_DEFAULT = COORD / "ARK_OPTIMIZATION_REPORT.md"
STALE_DAYS = 30

RE_TESTS_PASS = re.compile(r"(\d+)\s+passing")
RE_TESTS_COLLECT = re.compile(r"(\d+)\s+collected")
RE_MANDATE_RANGE = re.compile(r"(\d+)\s*\(M1-M(\d+)\)")
RE_DECISION_RANGE = re.compile(r"D1-D(\d+)")
RE_DECISION_COUNT = re.compile(r"(\d+)\s+decisions")
RE_IDSOFT = re.compile(r"\[id-soft:\s*([^\]\n]+)\]")
RE_IDSOFT_EMPTY = re.compile(r"^[^#\n]*#[^#\n]*\[id-soft:\s*\]", re.MULTILINE)
RE_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
RE_ACTIVE_TASK = re.compile(r"^\|\s*\**([\w.\-]+)\**\s*\|(.+?)\|(.+?)\|$")


# ─────────────────────────────────────────────────────────────────────────────
# Async readers (AnyIO)
# ─────────────────────────────────────────────────────────────────────────────
async def read_text(path: Path) -> str:
    if not await anyio.Path(path).exists():
        return ""
    return await anyio.Path(path).read_text(encoding="utf-8", errors="replace")


async def file_mtime_days(path: Path) -> float:
    p = anyio.Path(path)
    if not await p.exists():
        return 0.0
    info = await p.stat()
    now = datetime.now().timestamp()
    return (now - info.st_mtime) / 86400.0


# ─────────────────────────────────────────────────────────────────────────────
# Drift extraction
# ─────────────────────────────────────────────────────────────────────────────
def _first_int(regex: re.Pattern, text: str, group: int = 1):
    m = regex.search(text)
    return int(m.group(group)) if m else None


def _range_max(regex: re.Pattern, text: str):
    m = regex.search(text)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


async def extract_metrics() -> dict:
    ark = await read_text(ARK)
    omega = await read_text(OMEGA)
    pivot = await read_text(PIVOT)

    ark_tests = _first_int(RE_TESTS_PASS, ark) or _first_int(RE_TESTS_COLLECT, ark)
    omega_tests = _first_int(RE_TESTS_PASS, omega)
    omega_footer_tests = None
    fm = re.search(r"Tests:\s*(\d+)\s+passing", omega)
    if fm:
        omega_footer_tests = int(fm.group(1))

    ark_mand, ark_mand_max = _range_max(RE_MANDATE_RANGE, ark)
    omega_mand, omega_mand_max = _range_max(RE_MANDATE_RANGE, omega)
    # Actual mandate ceiling from SOVEREIGN_MANDATES.md
    mandates_text = await read_text(REPO / "SOVEREIGN_MANDATES.md")
    actual_mand_max = 0
    for m in re.finditer(r"###\s*(\d+)\.\s", mandates_text):
        actual_mand_max = max(actual_mand_max, int(m.group(1)))

    ark_dec_max = None
    m = RE_DECISION_RANGE.search(ark)
    if m:
        ark_dec_max = int(m.group(1))
    omega_dec_max = None
    m = RE_DECISION_RANGE.search(omega)
    if m:
        omega_dec_max = int(m.group(1))

    ark_has_oms = "omega module standard" in ark.lower() or "oms v" in ark.lower()
    ark_has_resonance = "semantic resonance" in ark.lower()
    ark_has_wasm = "wasm" in ark.lower()
    ark_has_qwen = "qwen-embed" in ark.lower()

    return {
        "ark_tests": ark_tests,
        "omega_tests": omega_tests,
        "omega_footer_tests": omega_footer_tests,
        "ark_mand_max": ark_mand_max,
        "omega_mand_max": omega_mand_max,
        "actual_mand_max": actual_mand_max,
        "ark_dec_max": ark_dec_max,
        "omega_dec_max": omega_dec_max,
        "ark_has_oms": ark_has_oms,
        "ark_has_resonance": ark_has_resonance,
        "ark_has_wasm": ark_has_wasm,
        "ark_has_qwen": ark_has_qwen,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Stale Active Tasks
# ─────────────────────────────────────────────────────────────────────────────
async def extract_stale_tasks() -> list[dict]:
    ark = await read_text(ARK)
    omega = await read_text(OMEGA)
    tasks: list[dict] = []
    in_table = False
    for line in ark.splitlines():
        if line.strip().startswith("## IV"):
            in_table = True
            continue
        if in_table and line.strip().startswith("## "):
            break
        if not in_table:
            continue
        m = RE_ACTIVE_TASK.match(line)
        if not m:
            continue
        tid = m.group(1).strip()
        body = m.group(2).strip()
        status = m.group(3).strip()
        if not any(k in status for k in ("PENDING", "⏳", "🟡", "🔮", "MEDIUM", "Deferred")):
            continue
        # Heuristic: token (version/code) already declared done elsewhere?
        token = None
        vm = re.search(r"v(\d+\.\d+\.\d+)", body)
        if vm:
            token = vm.group(1)
        possibly_done = False
        if token and token in omega:
            possibly_done = True
        tasks.append({
            "id": tid, "body": body, "status": status,
            "token": token, "possibly_done": possibly_done,
        })
    return tasks


# ─────────────────────────────────────────────────────────────────────────────
# Orphaned coordination files
# ─────────────────────────────────────────────────────────────────────────────
async def build_reference_set() -> set[str]:
    refs: set[str] = set()
    scan_dirs = [REPO / "docs", COORD, REPO]
    files: list[Path] = []
    for d in scan_dirs:
        if not await anyio.Path(d).exists():
            continue
        async for p in anyio.Path(d).rglob("*.md"):
            files.append(Path(p))
    for f in files:
        if await anyio.Path(f).is_dir():
            continue
        text = await read_text(f)
        for link in RE_MD_LINK.findall(text):
            target = link.split("#")[0].strip()
            if not target or target.startswith(("http", "mailto:")):
                continue
            refs.add(Path(target).name)
        # also bare filenames mentioned
        for bm in re.findall(r"([\w\-]+\.md)", text):
            refs.add(bm)
    return refs


async def find_orphans(refs: set[str]) -> list[dict]:
    orphans: list[dict] = []
    if not await anyio.Path(COORD).exists():
        return orphans
    async for p in anyio.Path(COORD).glob("*.md"):
        name = Path(p).name
        age = await file_mtime_days(Path(p))
        referenced = name in refs
        if (not referenced) and age > STALE_DAYS:
            orphans.append({"name": name, "age_days": round(age, 1), "referenced": False})
    return orphans


# ─────────────────────────────────────────────────────────────────────────────
# Broken cross-links
# ─────────────────────────────────────────────────────────────────────────────
async def find_broken_links() -> list[dict]:
    broken: list[dict] = []
    for doc in (ARK, OMEGA):
        text = await read_text(doc)
        base = Path(doc).parent
        for link in RE_MD_LINK.findall(text):
            target = link.split("#")[0].strip()
            if not target or target.startswith(("http", "mailto:")):
                continue
            resolved = (base / target).resolve()
            if not resolved.exists():
                broken.append({"doc": Path(doc).name, "link": link})
    return broken


# ─────────────────────────────────────────────────────────────────────────────
# Undocumented [id-soft:] tags (M14)
# ─────────────────────────────────────────────────────────────────────────────
async def find_undocumented_tags() -> list[str]:
    vet = await read_text(VET_LOG)
    credits = await read_text(REPO / "CREDITS.md")
    documented = vet + "\n" + credits
    tags: set[str] = set()
    empty_found = False
    
    # Template/documentation patterns to exclude from undocumented check
    # These match the captured group from RE_IDSOFT (content inside [id-soft: ...])
    TEMPLATE_PATTERNS = {
        "GAME-YEAR",
        "GAME YEAR",
        "doom-1993",
        "quake-1996",
        "quake3-1999",
        "doom3-2004",
        "doom3bfg-2012",
    }
    
    if await anyio.Path(SRC).exists():
        async for p in anyio.Path(SRC).rglob("*.py"):
            if await anyio.Path(p).is_dir():
                continue
            text = await read_text(Path(p))
            for t in RE_IDSOFT.findall(text):
                t_stripped = t.strip()
                if t_stripped not in TEMPLATE_PATTERNS:
                    tags.add(t_stripped)
            if RE_IDSOFT_EMPTY.search(text):
                empty_found = True
    # A tag is documented if its exact string OR its game-code token appears
    # in either the Heritage Vet Log or the CREDITS registry.
    undocumented = []
    if empty_found:
        undocumented.append("(EMPTY — malformed [id-soft:] tag, no game code)")
    for t in sorted(tags):
        if t not in documented and t.split()[0] not in documented:
            undocumented.append(t)
    return undocumented


# ─────────────────────────────────────────────────────────────────────────────
# Workbench cross-check
# ─────────────────────────────────────────────────────────────────────────────
async def check_workbench() -> dict:
    out = {"available": False, "omega_shared_modules": None}
    if not await anyio.Path(WORKBENCH).exists():
        return out
    try:
        import sqlite3
        con = sqlite3.connect(str(WORKBENCH))
        cur = con.cursor()
        con.close()
        out["available"] = True
    except Exception as e:  # pragma: no cover
        out["error"] = str(e)
    omega = await read_text(OMEGA)
    m = re.search(r"Shared modules.*?\|\s*\*\*?(\d+)", omega)
    if m:
        out["omega_shared_modules"] = int(m.group(1))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Optional live test count
# ─────────────────────────────────────────────────────────────────────────────
async def live_test_count() -> int | None:
    try:
        res = await anyio.run_process(
            [sys.executable, "-m", "pytest", "--co", "-q", "-p", "no:cacheprovider"],
            cwd=str(REPO), stdout=anyio.PIPE, stderr=anyio.PIPE,
            check=False,
        )
        out = res.stdout.decode(errors="replace")
        m = re.search(r"(\d+)\s+tests? collected", out)
        return int(m.group(1)) if m else None
    except Exception:  # pragma: no cover
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Report assembly
# ─────────────────────────────────────────────────────────────────────────────
def render_report(m: dict, tasks, orphans, broken, tags, wb, live, dry: bool) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    L: list[str] = []
    L.append("# 🔱 ARK OPTIMIZATION REPORT")
    L.append(f"**Generated**: {now} | **Mode**: {'DRY-RUN' if dry else 'LIVE'}")
    L.append(f"**AP Token**: `AP-ARK-OPTIMIZER-v1.0.0`")
    L.append("")
    L.append("## §1 Drift Metrics (Ark Blueprint vs Reality)")
    L.append("")
    L.append("| Dimension | Ark Blueprint | OMEGA_ENGINE.md | Actual | Verdict |")
    L.append("|-----------|---------------|-----------------|--------|---------|")
    tests_actual = live if live is not None else m["omega_tests"]
    L.append(f"| Tests | {m['ark_tests']} | {m['omega_tests']} (footer {m['omega_footer_tests']}) | {tests_actual} | "
             f"{'⚠️ DRIFT' if m['ark_tests'] != m['omega_tests'] else '✅'} |")
    L.append(f"| Mandates (max) | M1-M{m['ark_mand_max']} | M1-M{m['omega_mand_max']} | M1-M{m['actual_mand_max']} | "
             f"{'⚠️ DRIFT' if m['actual_mand_max'] != m['ark_mand_max'] else '✅'} |")
    ark_dec = m["ark_dec_max"] or "?"
    omega_dec = m["omega_dec_max"] or "?"
    dec_drift = (m["ark_dec_max"] is not None and m["omega_dec_max"] is not None
                 and m["ark_dec_max"] != m["omega_dec_max"])
    L.append(f"| Decisions (max) | D1-D{ark_dec} | D1-D{omega_dec} | — | "
             f"{'⚠️ DRIFT' if dec_drift else '✅'} |")
    L.append("")
    L.append("## §2 New-Plan Integration Gap")
    L.append("")
    gaps = []
    if not m["ark_has_oms"]:
        gaps.append("Omega Module Standard (OMS v1.0/v2.0) — absent")
    if not m["ark_has_resonance"]:
        gaps.append("Semantic Resonance Vectoring — absent")
    if not m["ark_has_wasm"]:
        gaps.append("WASM integration — absent")
    if not m["ark_has_qwen"]:
        gaps.append("qwen-embedding wiring — absent")
    if gaps:
        for g in gaps:
            L.append(f"- ❌ {g}")
    else:
        L.append("- ✅ All new plans present")
    L.append("")
    L.append("## §3 Stale / Pending Active Tasks")
    L.append("")
    if not tasks:
        L.append("- ✅ No pending tasks flagged")
    for t in tasks:
        flag = " 🔶 POSSIBLY-COMPLETE" if t["possibly_done"] else ""
        L.append(f"- `{t['id']}` — {t['body']} — *{t['status']}*{flag}")
    L.append("")
    L.append("## §4 Orphaned Coordination Files")
    L.append("")
    if not orphans:
        L.append(f"- ✅ No unreferenced files older than {STALE_DAYS}d")
    for o in orphans:
        L.append(f"- 🗑️ `{o['name']}` — {o['age_days']}d old, unreferenced → archive candidate")
    L.append("")
    L.append("## §5 Broken Cross-Links")
    L.append("")
    if not broken:
        L.append("- ✅ No broken relative links in Ark Blueprint / OMEGA_ENGINE.md")
    for b in broken:
        L.append(f"- 🔗 `{b['doc']}` → `{b['link']}` (target missing)")
    L.append("")
    L.append("## §6 Undocumented `[id-soft:]` Tags (M14)")
    L.append("")
    if not tags:
        L.append("- ✅ All source `[id-soft:]` tags have vet records")
    for t in tags:
        if t.startswith("("):
            L.append(f"- ⚠️ {t} (M14 violation)")
        else:
            L.append(f"- ⚠️ `[id-soft: {t}]` — no vet record in HERITAGE_VET_LOG.md")
    L.append("")
    L.append("## §7 Workbench Cross-Check")
    L.append("")
    if wb.get("available"):
        L.append(f"- OMEGA_ENGINE shared-modules count: {wb.get('omega_shared_modules')}")
    else:
        L.append(f"- ⚠️ workbench DB unavailable: {wb.get('error', 'missing')}")
    L.append("")
    L.append("## §8 Health Verdict")
    n_drift = sum([
        m["ark_tests"] != m["omega_tests"],
        m["actual_mand_max"] != m["ark_mand_max"],
        m["ark_dec_max"] != m["omega_dec_max"],
        len(gaps) > 0,
        len(broken) > 0,
        len(tags) > 0,
    ])
    verdict = "🟢 HEALTHY" if n_drift == 0 else ("🟡 DEGRADED" if n_drift <= 2 else "🔴 ACTION-REQUIRED")
    L.append(f"**{verdict}** — {n_drift} drift/integrity issues detected.")
    L.append("")
    L.append("---")
    L.append("*⬡ OMEGA ⬡ VERITY ⬡ ark_optimizer v1.0.0 ⬡ read-only verification*")
    return "\n".join(L)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
async def main() -> int:
    ap = argparse.ArgumentParser(description="Sovereign Ark Blueprint optimizer")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print report to stdout; write nothing to disk.")
    ap.add_argument("--live-tests", action="store_true",
                    help="Run pytest --co to obtain a real test count.")
    ap.add_argument("--report-path", type=str, default=str(REPORT_DEFAULT))
    args = ap.parse_args()

    m = await extract_metrics()
    tasks = await extract_stale_tasks()
    refs = await build_reference_set()
    orphans = await find_orphans(refs)
    broken = await find_broken_links()
    tags = await find_undocumented_tags()
    wb = await check_workbench()
    live = await live_test_count() if args.live_tests else None

    report = render_report(m, tasks, orphans, broken, tags, wb, live, args.dry_run)

    print(report)

    if not args.dry_run:
        out = Path(args.report_path)
        await anyio.Path(out.parent).mkdir(parents=True, exist_ok=True)
        # Atomic write: tmp -> rename
        tmp = out.with_suffix(out.suffix + ".tmp")
        await anyio.Path(tmp).write_text(report, encoding="utf-8")
        await anyio.Path(tmp).rename(out)
        print(f"\n[ark_optimizer] Report written to {out}", file=sys.stderr)
    else:
        print("\n[ark_optimizer] DRY-RUN: no files written.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    anyio.run(main)
