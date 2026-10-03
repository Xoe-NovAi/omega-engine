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

WHY NOT A MAPPING TABLE
-----------------------
A hand-maintained alias map is a registry — the very artefact that just failed
us. So the mapping is COMPUTED from the live entity set at submit time and
nothing is written to disk. Two normalisations only:

  * case / separator folding   `ge_n1` -> `ge-n1`
  * node / site suffixes       `ge-n1-n0` -> `ge-n1`, `makali-n0` -> `makali`

Both are mechanical and reversible. Anything that is NOT a pure spelling
difference of the same name is left alone rather than guessed at.

REFUSE AMBIGUITY
----------------
If a supplied name could reduce to more than one canonical entity, this raises.
Never guess. A wrong target is a silently-forked packet, which is the defect
being fixed.
"""

from __future__ import annotations

import re
from pathlib import Path

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
        defect being fixed. The caller must decide, not the resolver.
      * bare (suffix-free) names keep the legacy fold, but a bare name with
        node-qualified candidates returns them WITHOUT claiming
        ``resolved: true``. ``resolved: true`` with two candidates is the lie;
        the flag is fixed, not just the fold.

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
    # Second derivable source: the dominant spelling already in the live queue.
    queue = _queue_canonical()
    for canon_key, raw in queue.items():
        live.setdefault(canon_key, raw)

    # ── NODE SUFFIX BRANCH (before any folding) ──
    if _NODE_SUFFIX_RE.search(canon):
        if canon in live:
            full = live[canon]
            return {
                "supplied": entity,
                "entity": full,
                "agent_id": f"{channel}/{full}",
                "canonical": canon,
                "resolved": True,
                "rule": "exact",
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
            "candidates": [],
            "note": f"no live entity matches {entity!r}; id left as supplied",
        }

    names = sorted({n for v in matched.values() for n in v})

    # Bare request with node-qualified registrations of the same base: those
    # are DISTINCT destinations, not spelling variants. List them WITHOUT
    # claiming resolved:true — resolved:true with two candidates is the lie.
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

    # Rank: the BASE identity beats a site/node-suffixed spelling of it.
    # `makali-n0` matches both the live entity `makali` and the queued spelling
    # `makali-n0` — and the queued spelling IS the defect we are fixing, so
    # letting it out-vote the real entity would fork the very packets this
    # module exists to unify. Strip suffixes from every candidate and group;
    # only genuinely distinct BASES are ambiguous.
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
