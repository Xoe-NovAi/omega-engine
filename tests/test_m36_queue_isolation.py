# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""M36 must not be able to reach the LIVE handoff queue.

M30: test from the vantage the defect is reachable at. The previous dispatch's
guards asserted on the process-global `server` singleton and passed standalone
while failing in the full suite, because sibling modules mutate it. So these run
in SUBPROCESSES: the live-queue write is observable only from a separate
interpreter that can count what actually landed in `data/handoff/pending/`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _run(code: str, timeout: int = 240) -> str:
    r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                       text=True, cwd=str(REPO), timeout=timeout)
    return (r.stdout or "") + (r.stderr or "")


# ═══════════════════════════════════════════════════════════════════════════
# 1. STRUCTURAL: the constant does not point at live state
# ═══════════════════════════════════════════════════════════════════════════

def test_m36_queue_root_is_not_the_live_queue():
    """A separate directory is a STRUCTURE. A flag can be omitted; a grep is a
    check. This asserts the isolation exists at all, and points elsewhere."""
    out = _run("import sys; sys.path.insert(0,'src')\n"
               "import omega.oracle.m36_recursive_probe as m\n"
               "print('ROOT', m._M36_TEST_QUEUE_ROOT)\n")
    assert "ROOT" in out, out[-400:]
    root = out.split("ROOT", 1)[1].strip()
    assert "m36-test" in root, f"expected a dedicated test root, got {root!r}"
    assert root.rstrip("/").split("/")[-1] != "pending", \
        "the test root must never BE the live pending dir"


def test_no_hardcoded_live_write_path_remains():
    """Both write paths must be routed. The direct file write at the second
    call site is a SEPARATE path, not a fallback — fixing one leaves the tap on."""
    src = (REPO / "src" / "omega" / "oracle" / "m36_recursive_probe.py").read_text()
    writers = [ln for ln in src.splitlines()
               if 'data/handoff/pending' in ln and not ln.strip().startswith(('"', "#"))]
    assert not writers, f"hardcoded live writes remain: {writers}"
    assert '_test_root / "pending"' in src, "the direct write must use the test root"
    assert "_hub_state.HANDOFF_BASE = _test_root" in src, \
        "the tool-call path must be re-rooted"


# ═══════════════════════════════════════════════════════════════════════════
# 2. BEHAVIOURAL: dispatch lands in the test queue, never in pending/
# ═══════════════════════════════════════════���═══════════════════════════════

def test_m36_dispatch_cannot_land_in_live_pending():
    """M36 must not be able to reach live state. This is the real gate."""
    live = REPO / "data" / "handoff" / "pending"
    before = {p.name for p in live.glob("*.json")} if live.is_dir() else set()

    out = _run(
        "import sys; sys.path.insert(0,'src')\n"
        "from omega.oracle.m33_probe import CompletionEnvelope, CompletionState\n"
        "import omega.oracle.m36_recursive_probe as m\n"
        "env = CompletionEnvelope(state=CompletionState.EXHAUSTED, last_chunk_id=3,"
        " total_chunks=4, queued_findings=['F1'], confidence=0.9)\n"
        "r = m._dispatch_cross_validator_via_hivemind(env, 'data/fixtures/deliverable.md', 'P1', None)\n"
        "print('DISPATCHED', r.get('handoff_dispatched'), r.get('handoff_packet_id'))\n"
    )
    after = {p.name for p in live.glob("*.json")} if live.is_dir() else set()
    leaked = sorted(after - before)

    assert not leaked, (
        f"M36 wrote into the LIVE queue: {leaked}. The faucet is open."
    )


def test_m36_dispatch_lands_in_the_test_queue():
    """Isolation must not mean the packets vanished — they must be somewhere."""
    test_root = REPO / "data" / "handoff" / "m36-test" / "pending"
    _run("import sys; sys.path.insert(0,'src')\n"
         "import omega.oracle.m36_recursive_probe as m\n"
         "m._dispatch_cross_validator_via_hivemind('probe-agent', 'P1',"
         " 'data/fixtures/deliverable.md')\n")
    pkts = list(test_root.glob("*.json")) if test_root.is_dir() else []
    assert pkts, f"M36 produced no packet in the test queue at {test_root}"
    # The guard must be load-bearing: assert a REAL packet, with the marker and
    # a real target. A directory that merely exists is a tautology.
    import json as _json
    pkt = _json.loads(pkts[0].read_text())
    assert pkt.get("packet_id", "").startswith("ho_"), "not a handoff packet"
    assert "CROSS-VALIDATOR" in str(pkt.get("task", "")), \
        "the packet must actually be a cross-validator dispatch"


def test_live_root_is_restored_after_dispatch():
    """Without the restore the isolation LEAKS: the next caller in the same
    process inherits the test root and its packets go where nobody looks."""
    out = _run(
        "import sys; sys.path.insert(0,'src')\n"
        "import omega.oracle.m36_recursive_probe as m\n"
        "from omega.oracle.m33_probe import CompletionEnvelope, CompletionState\n"
        "from mcp_servers.omega_hub import state\n"
        "live = str(state.HANDOFF_BASE)\n"
        "env = CompletionEnvelope(state=CompletionState.EXHAUSTED, last_chunk_id=1,"
        " total_chunks=2, queued_findings=[], confidence=0.8)\n"
        "m._dispatch_cross_validator_via_hivemind(env, 'data/fixtures/deliverable.md', 'P1', None)\n"
        "print('AFTER', str(state.HANDOFF_BASE) == live, str(state.HANDOFF_BASE))\n"
    )
    assert "AFTER True" in out, f"live root not restored: {out[-400:]}"


# ═══════════════════════════════════════════════════════════════════════════
# 3. A REAL submit is unaffected
# ═══════════════════════════════════════════════════════════════════════════

def test_real_handoff_submit_still_works():
    """Isolation must not break the live path. A fix that disables the faucet by
    disabling the tool is the same defect wearing a different hat."""
    out = _run(
        "import sys, json, anyio, tempfile, pathlib\n"
        "sys.path.insert(0,'src')\n"
        "from mcp_servers.omega_hub import state\n"
        "from mcp_servers.omega_hub.hub_tools.tools import hivemind_handoff\n"
        "root = pathlib.Path(tempfile.mkdtemp())\n"
        "for n in ('pending','active','completed','stale','archive'):"
        " (root/n).mkdir(parents=True, exist_ok=True)\n"
        "state.HANDOFF_BASE = root\n"
        "state._init_complete, state._init_error = True, None\n"
        "f = hivemind_handoff.__wrapped__\n"
        "r = json.loads(anyio.run(lambda: f(action='submit',"
        " target_channel='opencode', target_entity='maat',"
        " source_channel='opencode', source_entity='maat', task='real submit')))\n"
        "print('STATUS', r.get('status'))\n"
    )
    assert "STATUS submitted" in out, f"a real submit was broken by the fix: {out[-400:]}"
