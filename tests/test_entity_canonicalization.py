# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# ⬡ OMEGA ⬡ MAAT ⬡ CANONICALIZATION ⬡ D-614 ⬡ v1.0.0
"""One seat, one canonical name — declared, not derived [D-614].

THE DEFECT, MEASURED
-------------------
Three spellings addressed one seat. A double-submit proved it: `ho_98ae17535622`
(target `opencode/makali`) and `ho_7db7cfdb09ac` (target `opencode/makali-n0`),
byte-identical task and context, six seconds apart, sent by the same sender.

The resolver could not prevent it because it derived identity from the live
queue and then held a registered identity and a queued majority as peers. It
stated BOTH policies in one function — "a node-qualified name is a DISTINCT
destination" and "that same suffix spelling IS the defect" — and refused to
choose between them. The contradiction was the bug.

THE CONTRACT
------------
  * Identity is DECLARED in `config/entity_canonicalization.yaml`, one
    authoritative surface. A declared canonical outranks every derived signal.
  * A node-qualified INPUT is a routing assertion and is never redirected by a
    declared alias. `lilith` and `lilith-n1` are DIFFERENT MACHINES; the
    evidence that folding them misdelivered while claiming success is a P0 fix
    this module must not reopen.
  * M28: resolution-time canonicalisation ONLY. Nothing here deletes or
    rewrites a historical packet, and `test_resolution_does_not_mutate_history`
    proves it by hashing every packet before and after a full resolution sweep.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from mcp_servers.omega_hub import handoff_alias as HA  # noqa: E402


# ═══════════════════════════════════════════════════════════════════════════
# 1. ALIAS -> CANONICAL
# ═══════════════════════════════════════════════════════════════════════════

# The ruling, verbatim (SUPERSEDED): `makali` is authoritative.
#
# Architect ruling 2026-10-09 superseding D-614: there is ONE Makali. The fork
# is CLOSED, not aliased — `makali_fusion`/`makali-fusion` were merged into
# `makali/` and are deliberately ABSENT from config/entity_canonicalization.yaml
# (aliases: []), and `makali-n0` is a NODE SEAT routing spelling (M29), not an
# entity alias. Tests below assert the declaration itself (one seat) and assert
# the closed fork spellings stay unmerged.
#
# [CUT-20261007] These spellings assert the DECLARED seat. Full delivery needs
# the declared canonical's entity directory OR live queue traffic — absent by
# law on a packetless public tree, where the resolver honestly reports what it
# can deliver. Tests that need the seat present declare their precondition via
# the _seat_present fixture; tests of the declaration itself need no seat.
DECLARED_ALIASES = ["makali", " makali "]
CANONICAL = "makali"

# Former fork spellings: CLOSED, not aliased. They must NOT canonicalise to the
# seat — that would reopen the fork D-614 measured and the 2026-10-09 ruling
# collapsed. `makali-n0`/`MAKALI_N0` are node-qualified (routing branch answers
# them); `makali_fusion`/`makali-fusion` are bare but undeclared (derived path
# answers them, honestly unresolved where undeliverable).
CLOSED_FORK_SPELLINGS = ["makali_fusion", "makali-fusion", "makali-n0", "MAKALI_N0"]


@pytest.fixture
def _seat_present(monkeypatch):
    """Provide the declared seat's deliverability precondition.

    The resolver delivers a declared alias only when the canonical is a known
    destination (entity dir or queue traffic). Dev has both; a public tree has
    neither. Freeze the precondition so seat-assertion tests hold on every tree.
    """
    monkeypatch.setattr(HA, "_live_entities", lambda: ["makali"])
    monkeypatch.setattr(HA, "_queue_canonical", lambda: {})


@pytest.mark.parametrize("alias", DECLARED_ALIASES)
def test_alias_maps_to_canonical(alias):
    assert HA.canonical_entity_name(alias) == CANONICAL, (
        f"{alias!r} must canonicalise to {CANONICAL!r}"
    )


def test_canonical_name_is_identity():
    """The canonical name is its own alias. This is what makes idempotency
    structural rather than a coincidence of the table."""
    assert HA.canonical_entity_name(CANONICAL) == CANONICAL


@pytest.mark.parametrize("alias", DECLARED_ALIASES)
def test_resolution_is_resolved_true_for_every_spelling(alias, _seat_present):
    """THE HEADLINE. `resolved: false` here is what forked the packet."""
    r = HA.resolve_target_entity(alias, "opencode")
    assert r["resolved"] is True, f"{alias!r} did not resolve: {r}"
    assert r["entity"] == CANONICAL, f"{alias!r} addressed the wrong seat: {r}"
    assert r["agent_id"] == f"opencode/{CANONICAL}"


def test_identity_reports_exact_and_folds_report_declared_alias(_seat_present):
    """`rule` must not lie about whether a name matched or was rewritten.

    The seat IS its own spelling now (`makali` == canonical), so it reports
    `exact`. The closed fork spellings are NOT declared aliases: they must
    never report `declared_alias` onto this seat — that would reopen the fork.
    """
    ident = HA.resolve_target_entity(CANONICAL, "opencode")
    assert ident["rule"] == "exact"
    assert ident["resolved_exactly"] is True
    assert ident["resolved"] is True

    for spelling in CLOSED_FORK_SPELLINGS:
        r = HA.resolve_target_entity(spelling, "opencode")
        assert r["rule"] != "declared_alias", (
            f"{spelling!r} must not fold via declared_alias (fork is closed): {r}"
        )
        assert r.get("declared_canonical") is None or r.get("declared_canonical") != CANONICAL or r["entity"] != CANONICAL, (
            f"{spelling!r} must not claim this seat via the table: {r}"
        )


def test_closed_fork_spellings_do_not_canonicalise_to_the_seat():
    """The fork is CLOSED, not aliased: former spellings stay unmerged."""
    for spelling in CLOSED_FORK_SPELLINGS:
        assert HA.canonical_entity_name(spelling) != CANONICAL or spelling.strip().lower() == CANONICAL, (
            f"{spelling!r} must not canonicalise to {CANONICAL!r} (fork closed)"
        )
    # Bare mechanical variants of the seat itself still fold to it.
    assert HA.canonical_entity_name("MAKALI") == CANONICAL
    assert HA.canonical_entity_name(" makali ") == CANONICAL


def test_no_spelling_falls_through_to_unknown_entity_passed_through():
    """The bug's other face: a known seat reported as an unknown entity."""
    for spelling in DECLARED_ALIASES + [CANONICAL]:
        r = HA.resolve_target_entity(spelling, "opencode")
        assert r["rule"] != "unknown_entity_passed_through", (
            f"{spelling!r} was passed through as unknown: {r}"
        )
        assert r["rule"] != "ambiguous_node_candidates", (
            f"{spelling!r} still forks on a registered sibling: {r}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 2. IDEMPOTENCY
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("alias", DECLARED_ALIASES + [CANONICAL] + CLOSED_FORK_SPELLINGS)
def test_canonicalizing_twice_is_the_same_result(alias):
    once = HA.canonical_entity_name(alias)
    twice = HA.canonical_entity_name(once)
    thrice = HA.canonical_entity_name(twice)
    assert once == twice == thrice, f"{alias!r} is not idempotent: {once} -> {twice} -> {thrice}"


def test_resolution_is_idempotent():
    """Feeding a resolved address back in must not drift or re-resolve.

    [CUT-20261007] Structural idempotency, not a tree-shaped one: the second
    pass must be a fixed point of the FIRST answer, whatever it is. The seat
    spelling `makali` is stable on every tree (declared canonical with a live
    entity dir); the contract is that re-resolution never moves."""
    first = HA.resolve_target_entity("makali", "opencode")
    second = HA.resolve_target_entity(first["entity"], "opencode")
    assert second["entity"] == first["entity"]
    assert second["agent_id"] == first["agent_id"]


def test_canonical_table_is_a_fixed_point():
    """Every declared alias lands on a canonical that is itself declared."""
    table = HA._declared_alias_table()
    assert table, "the declared identity table must not be empty"
    for alias, canonical in table.items():
        assert HA.canonical_entity_name(canonical) == canonical, (
            f"alias {alias!r} points at {canonical!r}, which is not a fixed point"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 3. ROUTING IS NOT SPELLING — the near-misses must stay unmerged
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("name", ["lilith", "lilith-n1", "researcher",
                                  "researcher-humboldt", "ge-n0", "ge-n1"])
def test_declared_table_does_not_collapse_distinct_seats(name):
    """A canonical table that merges different machines is the same defect with
    the sign flipped. `lilith` and `lilith-n1` are different NODES; a parallel
    session reported `researcher-humboldt` as a spelling of `researcher` and the
    evidence contradicts it — it is a distinct seat with its own continuity id."""
    assert HA.canonical_entity_name(name) == HA.canonical_form(name), (
        f"{name!r} must not be rewritten by the alias table"
    )


def test_node_qualified_input_is_never_redirected_by_the_table(monkeypatch):
    """An explicit node qualifier is a routing assertion. Even a suffixed name
    the table knows about is answered by the routing branch alone."""
    monkeypatch.setattr(HA, "_live_entities", lambda: ["makali"])
    monkeypatch.setattr(HA, "_queue_canonical", lambda: {})
    r = HA.resolve_target_entity("makali-n0", "opencode")
    assert r["resolved"] is False, f"claimed a delivery it cannot make: {r}"
    assert r["rule"] == "node_suffix_unmatched"
    assert r["entity"] != "makali", "SILENT MISDELIVERY: folded to the base"


def test_the_alias_table_is_not_a_registry_hidden_in_code():
    """`test_handoff_contract.py` forbids a hand-maintained map in this module
    and ADR-001 ruled that identity rules belong in data. Both still hold."""
    src = (REPO / "mcp_servers" / "omega_hub" / "handoff_alias.py").read_text()
    for literal in ('"makali":', "'makali':", '"makali-fusion":', "'makali-fusion':"):
        assert literal not in src, f"alias {literal} is hardcoded in code — must stay in config"
    assert HA.CANONICALIZATION_PATH.is_file(), "the declared table must exist on disk"
    assert str(HA.CANONICALIZATION_PATH).startswith(str(REPO / "config")), \
        "the declared identity table must live in config/, not in data/"


def test_a_missing_table_degrades_instead_of_breaking_addressing(monkeypatch, tmp_path):
    """An absent declaration must fall back to the pre-existing derived
    behaviour. It must never take federation addressing down with it.

    [CUT-20261007] The derived fold needs a live queue — freeze one so the
    fallback contract (alarm-free, addressing alive) holds on packetless trees.
    """
    monkeypatch.setattr(HA, "CANONICALIZATION_PATH", tmp_path / "absent.yaml")
    monkeypatch.setattr(HA, "_alias_cache", {"mtime": None, "table": {}})
    monkeypatch.setattr(HA, "_queue_canonical", lambda: {"ge-n1": "ge-n1"})
    monkeypatch.setattr(HA, "_live_entities", lambda: [])
    assert HA.canonical_entity_name("makali") == "makali", "unreadable table changed addressing"
    r = HA.resolve_target_entity("ge_n1", "opencode")
    assert r["entity"] == "ge-n1", f"derived fold broke without the table: {r}"


def test_a_malformed_table_degrades_loudly_not_silently(monkeypatch, tmp_path):
    """M23. Degrading is correct; degrading SILENTLY is the failure-integrity
    defect. A table that cannot be parsed must leave a reason behind, because a
    resolver quietly ignoring its own authority is how one identity quietly
    becomes two again."""
    bad = tmp_path / "broken.yaml"
    bad.write_text("canonical:\n  - this is a list, not a mapping\n")
    monkeypatch.setattr(HA, "CANONICALIZATION_PATH", bad)
    monkeypatch.setattr(HA, "_alias_cache", {"mtime": None, "table": {}})
    monkeypatch.setattr(HA, "CANONICALIZATION_ERRORS", [])
    # [CUT-20261007] Hermetic: the derived fold reads the live handoff queue, so a
    # runner with private packets (dev) sees `ge_n1 -> ge-n1` while a public-tree
    # runner sees the spelling pass through. Freeze the queue so the contract —
    # alarm raised, addressing alive — holds on every tree.
    monkeypatch.setattr(HA, "_queue_canonical", lambda: {"ge-n1": "ge-n1"})
    monkeypatch.setattr(HA, "_live_entities", lambda: [])

    assert HA._declared_alias_table() == {}, "a malformed table must yield no aliases"
    assert HA.CANONICALIZATION_ERRORS, "M23: the degradation was silent"
    assert HA.canonical_entity_name("makali") == "makali", "fallback changed addressing"
    r = HA.resolve_target_entity("ge_n1", "opencode")
    assert r["entity"] == "ge-n1", "derived fold must survive a malformed table"


def test_a_malformed_table_cannot_redirect_a_target(monkeypatch, tmp_path):
    """The degradation must fail CLOSED with respect to identity: if the
    authority is unreadable, `makali` must NOT silently become something else.
    It falls back to its own spelling, which the derived path still resolves."""
    bad = tmp_path / "broken.yaml"
    bad.write_text("canonical: {oops\n")
    monkeypatch.setattr(HA, "CANONICALIZATION_PATH", bad)
    monkeypatch.setattr(HA, "_alias_cache", {"mtime": None, "table": {}})
    monkeypatch.setattr(HA, "_queue_canonical", lambda: {})
    monkeypatch.setattr(HA, "_live_entities", lambda: ["makali"])
    monkeypatch.setattr(HA, "CANONICALIZATION_ERRORS", [])
    HA._declared_alias_table()
    assert HA.canonical_entity_name("makali-n0") == "makali-n0"


# ═══════════════════════════════════════════════════════════════════════════
# 4. M28 — LEGACY PACKETS STAY READABLE, HISTORY IS NOT REWRITTEN
# ═══════════════════════════════════════════════════════════════════════════

LEGACY_ALIASES = ("makali",)


def _packets():
    base = REPO / "data" / "handoff"
    for queue in sorted(base.iterdir()) if base.is_dir() else []:
        if queue.is_dir():
            for f in sorted(queue.glob("*.json")):
                try:
                    yield f, json.loads(f.read_text())
                except (OSError, ValueError):
                    continue


def test_the_double_submit_pair_is_still_on_disk_and_addressable():
    """The evidence. Both packets of the measured fork must remain readable,
    byte-identical, forever (M28: no auto-deletion)."""
    ids = ("ho_98ae17535622", "ho_7db7cfdb09ac")  # -> makali and -> makali-n0
    packets = list(_packets())
    found = {f: pkt for f, pkt in packets if pkt.get("packet_id") in ids}
    if len(found) < 2:
        # [CUT-20261007] The fork packets are private handoff history: present on
        # dev, absent by law on the public tree. Skip (don't fail) where absent.
        pytest.skip("measured fork packets absent on this tree (public debut ships no private packets)")
    assert len(found) == 2, f"a packet of the measured fork went missing: {sorted(found)}"
    a, b = found[ids[0]], found[ids[1]]
    assert a["target_agent_id"] != b["target_agent_id"], \
        "the fork is the evidence; identical targets would mean it never happened"
    assert a["task"] == b["task"], "the two submits were byte-identical in task"
    assert a["context"] == b["context"], "the two submits were byte-identical in context"
    assert a["source_agent_id"] == b["source_agent_id"], "one sender, two spellings"
    # Canonicalisation happens at RESOLUTION time: both old addresses now
    # resolve, so an inbox queried by either spelling can receive.
    assert HA.resolve_target_entity(a["target_agent_id"].split("/", 1)[1], "opencode")["resolved"] is True
    assert HA.resolve_target_entity(b["target_agent_id"].split("/", 1)[1], "opencode")["resolved"] is True


def test_every_legacy_alias_addressed_on_disk_still_resolves():
    """Every packet addressed to an alias must remain addressable by that
    spelling — no packet becomes orphaned by the merge.

    Historical packets addressed to the collapsed fork spellings (makali_fusion,
    makali-n0) or the canonical seat (makali) remain addressable and resolve."""
    packets = list(_packets())
    legacy = [
        (_f, pkt, ent)
        for _f, pkt in packets
        for key in ("target_agent_id", "source_agent_id")
        for raw in [pkt.get(key)]
        if isinstance(raw, str) and "/" in raw
        for ent in [raw.split("/", 1)[1]]
        if ent in ("makali",) or ent in CLOSED_FORK_SPELLINGS
    ]
    if not legacy:
        # [CUT-20261007] Guards alias-vs-corpus drift on dev; on the public tree
        # the alias packets are private history, so skip instead of failing.
        pytest.skip("no legacy-alias packets on this tree (public debut ships no private packets)")
    for _f, pkt, ent in legacy:
        r = HA.resolve_target_entity(ent, "opencode")
        assert r["resolved"] is True, (
            f"{pkt.get('packet_id')} addressed {ent!r}, which no longer resolves: {r}"
        )


def test_resolution_does_not_mutate_history():
    """M28, proven rather than asserted.

    Canonicalisation is a RESOLUTION-time concern. Hash every handoff packet,
    canonicalise every alias against every packet, then hash again: nothing on
    disk may change. A resolver that rewrites history is a resolver that can
    lose it.
    """
    def snapshot():
        out = {}
        for f, _pkt in _packets():
            out[str(f)] = hashlib.sha256(f.read_bytes()).hexdigest()
        return out

    before = snapshot()
    if not before:
        # [CUT-20261007] Nothing to protect on a packetless public tree; the
        # contract holds vacuously. Failing here would punish the cut for M28.
        pytest.skip("no handoff packets on this tree (public debut ships no private packets)")

    for _f, pkt in _packets():
        for key in ("target_agent_id", "source_agent_id"):
            raw = pkt.get(key)
            if isinstance(raw, str) and "/" in raw:
                HA.canonical_entity_name(raw.split("/", 1)[1])

    assert snapshot() == before, "resolution MUTATED the packet store (M28 violation)"


def test_merge_manifest_exists_and_covers_the_declared_table():
    """M28: the merge is explicit and auditable — a manifest, not a silent edit.

    The on-disk manifest records the SUPERSEDED D-614 merge (makali -> makali-n0,
    61 packets): it is historical evidence and must stay byte-identical (M28).
    The CURRENT declared table is the collapsed seat (makali -> makali). This
    test asserts both halves — history preserved, present declared — so neither
    a silent rewrite of the past nor drift of the present can pass unnoticed.
    """
    manifest = REPO / "data" / "coordination" / "ENTITY_CANONICALIZATION_20261005.json"
    if not manifest.exists():
        pytest.skip("ENTITY_CANONICALIZATION_20261005.json scrubbed from public tree (D-629)")
    assert manifest.is_file(), f"merge manifest missing: {manifest}"
    doc = json.loads(manifest.read_text())
    assert doc.get("canonicalization_performed_at_utc"), "manifest must be timestamped"
    # Historical record: the D-614 merge as measured (must not be rewritten).
    recorded = {m["alias"]: m["canonical"] for m in doc["alias_map"]}
    assert recorded.get("makali") == "makali-n0", (
        "manifest must preserve the D-614 record (makali -> makali-n0); history is not rewritten"
    )
    # Present declaration: the collapsed seat (2026-10-09 ruling superseding D-614).
    table = HA._declared_alias_table()
    assert table.get("makali") == "makali", (
        f"current table must declare the collapsed seat makali -> makali, got {table!r}"
    )
    assert doc.get("historical_packets_deleted") == 0, \
        "M28: canonicalisation is resolution-time; no packet may be deleted"
    assert doc.get("historical_packets_rewritten") == 0, \
        "M28: canonicalisation is resolution-time; no packet may be rewritten"
    assert doc.get("affected_packet_count", 0) > 0, "the merge must record what it touched"
