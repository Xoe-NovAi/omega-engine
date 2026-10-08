# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""`who_is(entity)` — live peer discovery. Replaces the generated registry.

THE PROBLEM THIS KILLS
----------------------
`data/coordination/EXPERT_SESSION_REGISTRY.md` is a GENERATED view, five weeks
stale, and it is the only artefact labelled "registry". An agent consulted it
to find a peer's session id, found no entry, and had nothing to fall back on.

It is not merely stale. It is STRUCTURALLY INCAPABLE of being right: the live
store holds 285 structural EIS (`parent_id IS NULL`) and multi-EIS per entity
is the norm (kali 68, build 39, roc 35, researcher 26, makali 21). A
one-row-per-agent generated view cannot represent that shape. Regenerating it
would not help; the SHAPE is wrong.

`agent` IS NOT A RELIABLE PEER IDENTITY
---------------------------------------
One entity can run under `makali`, `makali_fusion`, `makali-n0` or
`opencode/kali` depending on the entry path. Measured: 25 distinct structural
agent strings, 53 entity directories, only 12 exact overlaps. A match on
`agent` alone misses and mis-hits.

A mapping TABLE would be a registry — the very thing we are trying not to
need. So the mapping is DERIVED BY QUERY AT POINT OF USE and never written by a
human. Exactly one entity match -> use it. More than one -> `ambiguous`, stop.

REFUSE, NEVER PICK
------------------
Carmack holds two live structural EIS, 2.26h apart:
    ses_fa3f8ae42ffeI6GoJTreBDWb5d  JC-EIS-kq5
    ses_fc8dca39effe3nZJp3QHx81Fy3  JC-EIS
A pure recency rule pages `carmack` -> JC-EIS-kq5 and misses JC-EIS. Picking
one would be a coin toss presented as a lookup, so this tool returns
`ambiguous: true` and refuses to page instead.

THE RULE THAT GENERALISES
-------------------------
*A fact carried forward without a query is not a fact.* Three instances in one
exchange: a truncated tool list read as a total, a five-week-stale generated
registry, and an assertion about an access log that does not exist. Same
failure, three surfaces.

THE DURABLE ANSWER
------------------
Ask once per relationship, then page by explicit id forever. The session id is
the durable artifact; everything else is a cache of it. `who_is` is cheap to
call once and unnecessary thereafter — that is the design, not an accident.
"""

from __future__ import annotations

import re
import sqlite3
import time
from pathlib import Path

DB_PATH = Path.home() / ".local/share/opencode/opencode.db"
# who_is.py lives at <repo>/mcp_servers/omega_hub/who_is.py, so the repo root is
# THREE parents up. Using two silently pointed ENTITIES_DIR at mcp_servers/,
# where no entity directories exist — which made every lookup report
# "no entity match" and would have looked like a peer-not-found rather than a
# path bug.
REPO = Path(__file__).resolve().parent.parent.parent
ENTITIES_DIR = REPO / "data" / "entities"

# Structural EIS updated within this window are all "live". It must EXCEED the
# 2.26h gap between Carmack's two, or the acceptance case would resolve to one
# and pass for the wrong reason.
STALENESS_WINDOW_S = 24 * 3600

_SAFE = re.compile(r"[^a-z0-9]+")


class WhoIsError(RuntimeError):
    """Discovery failed. Never a guessed answer."""


def _norm(s: str) -> str:
    return _SAFE.sub("_", (s or "").strip().lower()).strip("_")


def _connect_readonly(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Open the session store READ-ONLY. Asserted, not assumed.

    A discovery tool that can WRITE to the session store is a new hazard: it
    would sit on the read path with write capability, reachable by any agent
    that can call a tool. `mode=ro` makes that structurally impossible rather
    than merely unlikely.
    """
    if not db_path.is_file():
        raise WhoIsError(f"session DB not found at {db_path}")
    uri = f"file:{db_path}?mode=ro"
    con = sqlite3.connect(uri, uri=True, timeout=5)
    if not _is_readonly(con):
        con.close()
        raise WhoIsError("refusing to use a writable connection to the session DB")
    return con


def _is_readonly(con: sqlite3.Connection) -> bool:
    """Prove the connection cannot write, by attempting a write in a rolled-back txn."""
    try:
        con.execute("CREATE TABLE IF NOT EXISTS _who_is_write_probe (x INT)")
    except sqlite3.OperationalError:
        return True           # refused => read-only, as required
    except sqlite3.Error:
        return False
    # It succeeded, which is itself a failure of the read-only guarantee.
    try:
        con.execute("DROP TABLE IF EXISTS _who_is_write_probe")
    except sqlite3.Error:
        pass
    return False


def _entity_candidates(agent: str, entities: list[str]) -> list[str]:
    """Resolve agent -> entity by SCANNING the live set. No table.

    Matching is deliberately conservative and ordered: exact, then
    token-containment both ways. Containment is what rescues `john_carmack` ->
    `carmack`-style drift and `buildmaster` -> `build`, but it can also match
    two entities at once, and that is precisely the case that must return
    ambiguous rather than pick.
    """
    a = _norm(agent)
    if not a:
        return []
    exact = [e for e in entities if _norm(e) == a]
    contained = [e for e in entities
                 if a in _norm(e).split("_") or _norm(e) in a.split("_")
                 or a in _norm(e) or _norm(e) in a]
    # Union, NOT exact-first. `carmack` matches exactly AND is contained in
    # `john_carmack`, and BOTH are registered entities. Returning only the exact
    # match hid a real ambiguity and sent the lookup down a dead end; both
    # entities can legitimately claim this peer, so both are reported and the
    # caller refuses. Silently preferring the exact match is the "helpful"
    # guess this whole tool exists to eliminate.
    return sorted(set(exact) | set(contained))


def resolve_agent(agent: str) -> dict:
    """agent -> entity, derived by query. Returns the resolution, ambiguity included."""
    entities = sorted(p.name for p in ENTITIES_DIR.iterdir() if p.is_dir()) \
        if ENTITIES_DIR.is_dir() else []
    cands = _entity_candidates(agent, entities)
    if len(cands) == 1:
        return {"entity": cands[0], "ambiguous": False, "candidates": cands,
                "method": "scanned_live_set"}
    if not cands:
        return {"entity": None, "ambiguous": False, "candidates": [],
                "method": "scanned_live_set",
                "note": f"no entity directory matches agent {agent!r}"}
    return {"entity": None, "ambiguous": True, "candidates": cands,
            "method": "scanned_live_set",
            "note": "more than one entity could match; refusing to guess"}


def _structural_eis(agent: str, con: sqlite3.Connection, now_ms: int) -> list[dict]:
    rows = con.execute(
        "SELECT id, title, time_updated FROM session "
        "WHERE parent_id IS NULL AND agent = ? "
        "ORDER BY time_updated DESC",
        (agent,),
    ).fetchall()
    cutoff = now_ms - STALENESS_WINDOW_S * 1000
    return [
        {"id": r[0], "title": r[1], "time_updated_ms": r[2],
         "age_s": int((now_ms - r[2]) / 1000)}
        for r in rows
    ]


def _agents_for_entity(entity: str, con: sqlite3.Connection,
                       entities: list[str]) -> list[str]:
    """Every live agent string that RESOLVES to this entity.

    This is the general answer to `agent` not being a peer identity: we do not
    look up `carmack` and find nothing because the DB keys it as
    `john_carmack`. We enumerate the 25 structural agent strings, resolve each
    one to an entity by scanning, and take those that land on our target.

    Still no hand-maintained table: the mapping is recomputed from the live set
    on every call, and nothing on disk is ever written.
    """
    agents = [r[0] for r in con.execute(
        "SELECT DISTINCT agent FROM session WHERE parent_id IS NULL")]
    out = []
    for a in agents:
        if not a:
            continue
        cands = _entity_candidates(a, entities)
        if len(cands) == 1 and cands[0] == entity:
            out.append(a)
    return sorted(out)


def who_is(peer: str, *, db_path: Path = DB_PATH, now_ms: int | None = None,
           entity: str | None = None) -> dict:
    """Resolve a peer's live structural EIS. Refuses rather than picking.

    Returns `{entity, session_id, ambiguous, candidates, ...}`. On ambiguity
    `session_id` is None — a caller MUST NOT substitute a guess, and the
    `refused` field exists so that is a hard, visible state rather than a null
    to be papered over.
    """
    now_ms = now_ms if now_ms is not None else int(time.time() * 1000)
    # An explicit entity SKIPS peer-name resolution. A caller that already knows
    # the entity (because it is paging an explicit target) still needs the
    # EIS-level ambiguity check below, which is a different and independent
    # refusal: the entity is unambiguous but its SESSIONS are not.
    res = ({"entity": entity, "ambiguous": False, "candidates": [entity],
            "method": "explicit"}
           if entity else resolve_agent(peer))
    out = {
        "peer": peer,
        "entity": res["entity"],
        "entity_ambiguous": res["ambiguous"],
        "entity_candidates": res["candidates"],
        "session_id": None,
        "ambiguous": False,
        "refused": False,
        "candidates": [],
        "staleness_window_s": STALENESS_WINDOW_S,
        "read_only": True,
    }
    if res["ambiguous"]:
        out.update({"ambiguous": True, "refused": True,
                    "error": "entity_ambiguous",
                    "message": f"agent {peer!r} could be {res['candidates']}; "
                               "refusing to guess. Ask the peer for its session id."})
        return out
    if not res["entity"]:
        out.update({"refused": True, "error": "no_entity_match", "message": res["note"]})
        return out

    entities = sorted(p.name for p in ENTITIES_DIR.iterdir() if p.is_dir())
    with _connect_readonly(db_path) as con:
        # Search every agent string that resolves to this entity, not just the
        # peer's own name: the DB may key this entity as `john_carmack` while
        # the peer is called `carmack`.
        agent_keys = [peer, res["entity"]] + _agents_for_entity(res["entity"], con, entities)
        eis = []
        seen_ids = set()
        for a in dict.fromkeys(agent_keys):
            for e in _structural_eis(a, con, now_ms):
                if e["id"] in seen_ids:
                    continue
                seen_ids.add(e["id"])
                e["agent"] = a
                eis.append(e)
        eis.sort(key=lambda e: e["time_updated_ms"], reverse=True)

    if not eis:
        out.update({"refused": True, "error": "no_structural_eis",
                    "message": f"no structural EIS (parent_id IS NULL) for {peer!r}"})
        return out

    live = [e for e in eis if e["age_s"] <= STALENESS_WINDOW_S]
    if not live:
        out.update({"refused": True, "error": "all_stale",
                    "candidates": eis[:5],
                    "message": f"every structural EIS for {peer!r} is older than "
                               f"{STALENESS_WINDOW_S}s; refusing to page a stale id"})
        return out

    if len(live) > 1:
        # THE ACCEPTANCE CASE. Two live structural EIS -> refuse.
        out.update({"ambiguous": True, "refused": True, "error": "ambiguous_eis",
                    "candidates": live[:5],
                    "message": (
                        f"{len(live)} structural EIS for {peer!r} were updated within "
                        f"{STALENESS_WINDOW_S}s. A recency rule would pick one and be "
                        f"wrong about the other. Refusing to page. Candidates: "
                        + ", ".join(c["id"] for c in live[:5])
                    )})
        return out

    only = live[0]
    out.update({"session_id": only["id"], "title": only["title"],
                "age_s": only["age_s"], "candidates": live,
                "pager_echo": (
                    f"PAGE {res['entity']} {only['id']}   # resolved by who_is: "
                    f"{only['title']!r}, updated {only['age_s']}s ago"
                )})
    return out
