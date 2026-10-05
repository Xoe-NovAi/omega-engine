# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Alias resolution for handoff targets — DERIVED, never curated.

THE DEFECT
----------
`target_agent_id` was built as literal ``f"{channel}/{entity}"``. No alias
registry, no validation, no existence check. Measured consequence on the live
queue: 9 distinct spellings for the same agents across 32 pending packets —
`ge-n1`x7 and `ge_n1`x1, `makali`x5 and `makali-n0`x1, `john_carmack`x1 and
`john-carmack-n1`x1. The `ge_n1` packet was forked by a `ge-n1` agent that
will never meet the six it forked from.

SPELLING IS DERIVED; IDENTITY IS DECLARED
-----------------------------------------
Two different questions were being answered by one function, which is how it
ended up holding two opposite policies at once.

  * "is this the SAME NAME spelled differently?" — a mechanical question.
    DERIVED at call time, nothing on disk: case / separator folding
    (`ge_n1` -> `ge-n1`). Reversible, testable, cannot be wrong about itself.

  * "is this the SAME SEAT under a different name?" — not mechanical at all.
    DECLARED in `config/entity_canonicalization.yaml` [D-614].

The defect this module was born to fix was asking the SECOND question with the
FIRST question's tool. Deriving identity from the live queue means the fork
elects its own winner by majority, so the louder fork gets canonised and the
quieter one gets declared defective — and then, holding a derived majority and
a registered identity as peers, the function refused to decide which was which.
That refusal is what forked `ho_98ae17535622` (-> `makali`) from
`ho_7db7cfdb09ac` (-> `makali-n0`), byte-identical, 6 seconds apart.

A heuristic cannot arbitrate identity, so it must not try. Identity is declared
in ONE authoritative place, reviewed, and tested. Spelling noise is still folded
mechanically. A table ABSENT entry is not a merge.

THE ONE POLICY (this supersedes the two contradictory comments it replaces)
-------------------------------------------------------------------------
  1. A node suffix on INPUT (`-n\\d+$`) is a ROUTING assertion by the caller.
     It is answered by the node-suffix branch ALONE: exact match, or refuse.
     A declared alias NEVER redirects a node-qualified name. This is kept
     because the evidence for it is a real misdelivery (`lilith-n1` folded to
     `lilith` while reporting success), not a hypothetical.
  2. A BARE name is answered by the DECLARED identity table FIRST. A declared
     canonical outranks every derived signal, including a queue majority. A
     bare name with MULTIPLE node candidates is still refused UNLESS the table
     says which of them is canonical — that is the case the old code got wrong
     by refusing to ask.
  3. Only then does the derived path run, for everything undeclared.

REFUSE AMBIGUITY
----------------
Still the default for anything the table does not settle. If a supplied name
could reduce to more than one canonical entity, this raises. Never guess. A
wrong target is a silently-forked packet, which is the defect being fixed.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
ENTITIES_DIR = REPO / "data" / "entities"

# `ge-n1-n0` -> base `ge-n1`. Node/site suffixes, not part of the identity.
_SUFFIXES = {"n0", "n1", "n2", "n3", "n4", "n5"}

# NODE SUFFIX IS LOAD-BEARING (routing, not spelling). A trailing node
# qualifier matching this regex is a DISTINGUISHING token: `lilith-n1` and
# `lilith` are different machines. Folding one to the other delivers a reply
# to the wrong node while reporting success (observed live: `lilith-n1`
# stored as `lilith`, rule `spelling_or_suffix_folded`, resolved:true).
_NODE_SUFFIX_RE = re.compile(r"-n\d+$")


def _strip_node_suffixes(canon: str) -> str:
    """Strip ALL trailing node qualifiers. `ge-n1-n0` -> `ge-n1` -> `ge`."""
    cur = canon
    while True:
        nxt = _NODE_SUFFIX_RE.sub("", cur)
        if nxt == cur:
            return cur
        cur = nxt


class AliasResolutionError(ValueError):
    """The target name cannot be resolved to exactly one entity."""


def canonical_form(name: str) -> str:
    """Fold separators and case. `ge_n1` -> `ge-n1`, `John_Carmack` -> `john-carmack`."""
    s = (name or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


# ── DECLARED IDENTITY (the one authoritative surface, D-614) ────────────────
CANONICALIZATION_PATH = REPO / "config" / "entity_canonicalization.yaml"

# What a malformed / unreadable declaration can raise. Named, not blind: a
# bare `except Exception` here would swallow a typo in the table exactly as
# happily as it swallows a missing file, and the second is not worth alerting
# anyone about.
_TABLE_ERRORS = (OSError, ValueError, TypeError, AttributeError, yaml.YAMLError)

# M23: degradation must be visible. Appended to whenever the declared table
# fails to load and the resolver falls back to the derived path.
CANONICALIZATION_ERRORS: list[str] = []

_alias_cache: dict[str, object] = {"mtime": None, "table": {}}


def _declared_alias_table() -> dict[str, str]:
    """alias (canonical_form) -> canonical name, from the declared table.

    A DECLARED table in reviewed, tested config — not a mapping dict in this
    file. `tests/test_handoff_contract.py::test_no_hand_maintained_mapping_table`
    guards against an unversioned registry hiding in code; ADR-001 §"Canonical
    naming" already ruled that suffix heuristics in this module are to be
    replaced by "declared canonicalisation rules in data". That ruling is why
    the table is data. The defect was never CURATION — it was letting a
    self-referential majority arbitrate identity.

    A missing or unreadable file yields an EMPTY table, never an exception: an
    absent declaration must degrade to the pre-existing derived behaviour, not
    take the federation's addressing down with it.
    """
    try:
        mtime = CANONICALIZATION_PATH.stat().st_mtime
    except OSError:
        _alias_cache["mtime"] = None
        _alias_cache["table"] = {}
        return {}

    if _alias_cache["mtime"] != mtime:
        table: dict[str, str] = {}
        try:
            doc = yaml.safe_load(CANONICALIZATION_PATH.read_text()) or {}
            for canonical, spec in (doc.get("canonical") or {}).items():
                canon_key = canonical_form(canonical)
                if not canon_key:
                    continue
                # The canonical name is its own alias (identity), so
                # canonicalising it twice is a no-op by construction.
                table[canon_key] = canonical
                for alias in ((spec or {}).get("aliases") or []):
                    akey = canonical_form(alias)
                    if akey and akey not in table:
                        table[akey] = canonical
        except _TABLE_ERRORS as exc:
            # A malformed table must not break addressing — but it must not
            # fail SILENTLY either (M23). Fall back to the derived path and
            # record the reason where the next reader will find it.
            table = {}
            CANONICALIZATION_ERRORS.append(f"{type(exc).__name__}: {exc}")
        _alias_cache["mtime"] = mtime
        _alias_cache["table"] = table
    return _alias_cache["table"]  # type: ignore[return-value]


def canonical_entity_name(name: str) -> str:
    """Map any declared alias to its canonical entity name [D-614].

      makali         -> makali-n0
      makali_fusion  -> makali-n0
      makali-fusion  -> makali-n0
      makali-n0      -> makali-n0      (identity — idempotent)

    UNDECLARED names are returned unchanged (after mechanical folding), so this
    is safe to call on anything. Node-qualified names are deliberately NOT
    redirected here — see policy 1 in the module docstring; routing is answered
    by `resolve_target_entity`, not by a name map.
    """
    canon = canonical_form(name)
    if not canon or _NODE_SUFFIX_RE.search(canon):
        return canon
    return _declared_alias_table().get(canon, canon)


def _live_entities() -> list[str]:
    if not ENTITIES_DIR.is_dir():
        return []
    return sorted(p.name for p in ENTITIES_DIR.iterdir() if p.is_dir())


def _queue_canonical() -> dict[str, str]:
    """The dominant spelling of each canonical name, derived from the LIVE queue.

    Entity directories cannot canonicalize everything: GE-N1 has no entity
    directory at all, yet it is one of the most active peers (7 pending
    packets). So the second source is the queue itself — scan every packet's
    `target_agent_id`/`source_agent_id`, group by canonical form, and take the
    most frequent raw spelling as canonical for that group.

    Still derived, never curated: nothing is written to disk, and the answer
    changes as the traffic changes. Ties are NOT broken arbitrarily — a tie is
    reported as ambiguous so a human decides.
    """
    import collections
    import json

    counts: dict[str, collections.Counter] = {}
    handoff = REPO / "data" / "handoff"
    if handoff.is_dir():
        for queue in handoff.iterdir():
            if not queue.is_dir():
                continue
            for f in queue.glob("*.json"):
                try:
                    pkt = json.loads(f.read_text())
                except (OSError, ValueError):
                    continue
                for key in ("target_agent_id", "source_agent_id"):
                    raw = pkt.get(key)
                    if not isinstance(raw, str) or "/" not in raw:
                        continue
                    ent = raw.split("/", 1)[1]
                    counts.setdefault(canonical_form(ent), collections.Counter())[ent] += 1

    out: dict[str, str] = {}
    for canon, counter in counts.items():
        top = counter.most_common()
        if len(top) > 1 and top[0][1] == top[1][1]:
            continue  # tie -> leave unresolved rather than pick
        out[canon] = top[0][0]
    return out


def _base_variants(canon: str) -> list[str]:
    """Strip node suffixes, repeatedly, from both ends. `a-n0` -> `a`."""
    out = [canon]
    cur = canon
    while True:
        tail = cur.rsplit("-", 1)
        if len(tail) == 2 and tail[1] in _SUFFIXES:
            cur = tail[0]
            out.append(cur)
            continue
        return out


def resolve_target_entity(entity: str, channel: str) -> dict:
    """Resolve a caller-supplied entity to a canonical agent id.

    NODE SUFFIX IS LOAD-BEARING (routing, not spelling). A trailing node
    qualifier matching the regex ``-n\\d+$`` (``_NODE_SUFFIX_RE``) is a
    DISTINGUISHING token, never a spelling variant:

      * suffixed name matches a known name exactly -> deliver it, rule
        ``"exact"``, no fold, no note. ``lilith-n1`` -> ``lilith-n1``. Done.
      * suffixed name matches NOTHING -> resolved False, rule
        ``"node_suffix_unmatched"``. NEVER folded to the base name: folding
        delivers to the wrong machine while reporting success, which is the
        defect being fixed. The caller must decide, not the resolver. A
        DECLARED alias never overrides this branch either — an explicit node
        qualifier is a routing assertion, not a spelling.
      * bare names are answered by the DECLARED identity table
        (``config/entity_canonicalization.yaml``) FIRST. A declared alias
        resolves with ``resolved: true`` and rule ``"declared_alias"`` (or
        ``"exact"`` when the supplied spelling is already canonical) — even
        when a node-qualified spelling of the same seat is also registered.
        That combination used to return ``resolved: false`` and fork the
        packet; see the module docstring, D-614.
      * bare names the table does NOT cover keep the legacy fold, and a bare
        name with node-qualified candidates returns them WITHOUT claiming
        ``resolved: true``. Undeclared means undeclared: ``resolved: true``
        with two candidates is the lie; the flag is fixed, not just the fold.

    Do NOT "simplify" the suffix branch back into the fold. That simplification
    IS the bug (live evidence: ``lilith-n1`` stored as ``lilith``).

    Returns `{entity, agent_id, resolved_from, rule, candidates}`. Raises
    AliasResolutionError when resolution is ambiguous across genuinely
    distinct bases or empty — a wrong target is a silently forked packet,
    which is the defect being fixed.
    """
    canon = canonical_form(entity)
    if not canon:
        raise AliasResolutionError("target_entity is empty after normalisation")

    live = {canonical_form(e): e for e in _live_entities()}
    # Declared identity (policy 2). Read once here so BOTH the routing branch
    # and the bare branch below can see it; the routing branch only uses it to
    # LABEL the answer, never to redirect it.
    declared = _declared_alias_table().get(canon)
    # Second derivable source: the dominant spelling already in the live queue.
    queue = _queue_canonical()
    for canon_key, raw in queue.items():
        live.setdefault(canon_key, raw)

    # ── NODE SUFFIX BRANCH (before any folding) ──
    if _NODE_SUFFIX_RE.search(canon):
        if canon in live:
            full = live[canon]
            exact_hit = canonical_form(full) == canon
            # `resolved_exactly` / `declared_canonical` are emitted by EVERY
            # branch so the response shape does not depend on which rule fired.
            # A caller must not have to know whether a name was answered by the
            # routing branch or the declared-identity branch to read the answer.
            return {
                "supplied": entity,
                "entity": full,
                "agent_id": f"{channel}/{full}",
                "canonical": canon,
                "resolved": True,
                "rule": "exact",
                "resolved_exactly": exact_hit,
                "declared_canonical": declared if declared else None,
                "candidates": [full],
                "queue_canonical": queue.get(canon),
            }
        # The full suffixed name matches no known name. DO NOT fold to the
        # base: silent delivery to the wrong node is a false success (M23:
        # a refused delivery returns an error shape here, never a guess).
        base = _NODE_SUFFIX_RE.sub("", canon)
        base_hit = live.get(base)
        return {
            "supplied": entity,
            "entity": entity,
            "agent_id": f"{channel}/{entity}",
            "canonical": canon,
            "resolved": False,
            "rule": "node_suffix_unmatched",
            "resolved_exactly": False,
            "declared_canonical": None,
            "requested": entity,
            "candidates": [base_hit] if base_hit else [],
            "delivered": False,
            "delivered_to": None,
            "note": (
                f"{entity!r} carries an explicit node suffix "
                f"({_NODE_SUFFIX_RE.pattern}) and matches no registered "
                f"entity; NOT folded to base {base_hit!r}. Delivering to the "
                "base node would be a false success — the caller must decide."
            ),
            "queue_canonical": queue.get(canon),
        }

    # ── DECLARED IDENTITY (policy 2: the table answers this first) ──────────
    # This branch is what the old code was missing. It held a registered
    # identity (`makali`) and a queued node spelling (`makali-n0`) as peers and
    # refused to pick, so one packet became two. A declared canonical is not a
    # peer of a derived majority — it outranks it, and saying so out loud is
    # the whole fix.
    if declared:
        dc_canon = canonical_form(declared)
        dc_hit = live.get(dc_canon)
        if dc_hit:
            is_identity = dc_canon == canon
            return {
                "supplied": entity,
                "entity": dc_hit,
                "agent_id": f"{channel}/{dc_hit}",
                "canonical": canon,
                "resolved": True,
                # `exact` when the supplied spelling IS the canonical name;
                # `declared_alias` when the table collapsed a different
                # spelling onto it. Reporting a fold as `exact` would put a
                # lie back into the one field that callers read to decide
                # whether a target was matched or rewritten.
                "rule": "exact" if is_identity else "declared_alias",
                "resolved_exactly": is_identity,
                "declared_canonical": dc_hit,
                "candidates": sorted({live[canon], dc_hit} if canon in live else {dc_hit}),
                "queue_canonical": queue.get(canon),
            }
        # Declared canonical is not a known destination (no entity dir, no
        # queue traffic). Do NOT claim a resolution we cannot deliver: fall
        # through to the derived path, which refuses rather than guesses.

    matched: dict[str, list[str]] = {}
    for variant in _base_variants(canon):
        if variant in live:
            matched.setdefault(variant, []).append(live[variant])

    if not matched:
        # Not a known entity. Do NOT invent one: echo back the caller's spelling
        # so the packet is still deliverable, but mark it unresolved so the
        # submit response says so loudly.
        return {
            "supplied": entity,
            "entity": entity,
            "agent_id": f"{channel}/{entity}",
            "canonical": canon,
            "resolved": False,
            "rule": "unknown_entity_passed_through",
            "resolved_exactly": False,
            "declared_canonical": None,
            "candidates": [],
            "note": f"no live entity matches {entity!r}; id left as supplied",
        }

    names = sorted({n for v in matched.values() for n in v})

    # Bare request with node-qualified registrations of the same base, and NO
    # declaration saying which is canonical: refuse.
    #
    # This branch used to carry the claim "those are DISTINCT destinations, not
    # spelling variants" as a general policy. It is not one — it is only true
    # when nothing DECLARES otherwise, and it was stated as if it settled the
    # question. It did not: it made `makali` unresolvable because a *different
    # spelling of the same seat* happened to be sitting in the queue, and that
    # refusal is what produced the double-submit.
    #
    # Policy 2 applies: if the table had an entry for `makali`, we would never
    # reach here. Reaching here means "undeclared" — and undeclared is exactly
    # the case where refusing is correct, because nothing else can tell
    # `lilith` from `lilith-n1`.
    extensions = sorted(
        {
            spelling
            for key, spelling in live.items()
            if key != canon
            and _NODE_SUFFIX_RE.search(key)
            and _strip_node_suffixes(key) == canon
        }
    )
    if extensions:
        cands = sorted(set(names) | set(extensions))
        return {
            "supplied": entity,
            "entity": entity,
            "agent_id": f"{channel}/{entity}",
            "canonical": canon,
            "resolved": False,
            "rule": "ambiguous_node_candidates",
            "resolved_exactly": False,
            "declared_canonical": None,
            "requested": entity,
            "candidates": cands,
            "delivered": False,
            "delivered_to": None,
            "note": (
                f"{entity!r} is a bare name with {len(cands)} node candidates "
                f"{cands}; NOT resolved to one of them. Pass the exact "
                "node-qualified entity name."
            ),
            "queue_canonical": queue.get(canon),
        }

    # Rank the surviving spellings of ONE base. The node-suffix branch above has
    # already removed anything node-qualified, so what remains are pure
    # separator/case variants of a single name.
    #
    # The comment this replaced claimed the queued spelling `makali-n0` "IS the
    # defect we are fixing" and that the base must out-vote it. Both halves were
    # wrong, and it was unreachable while wrong, which is worse: the
    # `extensions` branch returned first, so this "policy" had never once run.
    # It also inverted the ruling — `makali-n0` is the AUTHORITATIVE name
    # [D-614], not the defect. Preferring a registered spelling over a derived
    # one remains correct and is kept below; preferring it because it is
    # "shorter and less decorated" is not a reason, so a declaration is
    # consulted first and this ranking only breaks ties among equals.
    bases: dict[str, list[str]] = {}
    for n in names:
        bases.setdefault(_base_variants(canonical_form(n))[-1], []).append(n)
    if len(bases) > 1:
        raise AliasResolutionError(
            f"target_entity {entity!r} is AMBIGUOUS: it could mean {sorted(bases)}. "
            "Refusing to guess — a wrong target silently forks the packet. "
            "Pass the exact entity name, or page by explicit agent_id."
        )
    # Among the spellings of the single base, prefer the one that is itself a
    # live entity directory, then the shortest (least decoration).
    base = next(iter(bases))
    spelling_choices = bases[base]
    live_dirs = {e for e in _live_entities()}
    canonical_name = sorted(
        spelling_choices,
        key=lambda s: (s not in live_dirs, len(s), s),
    )[0]
    rule = "exact" if canonical_name == canon else "spelling_or_suffix_folded"
    return {
        "supplied": entity,
        "entity": canonical_name,
        "agent_id": f"{channel}/{canonical_name}",
        "canonical": canon,
        "resolved": True,
        "rule": rule,
        "candidates": names,
        "queue_canonical": queue.get(canon),
    }
