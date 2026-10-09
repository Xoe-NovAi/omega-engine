#!/usr/bin/env python3
"""Phase 3: adversarial, balanced supersession set for supersede_decider/well_curator.

Phase 2 measured the supersession holdout as 47/50 `keep`, so `action_exact` had a
majority-gold floor of 0.94 and could not separate a trained model from a constant
string (docs/research/LFM25_SMS_PHASE2_ECHO_DECOMPOSITION_20261008.md §8.2 item 2).
There are two defects, not one:

  1. **Degenerate balance.** Only 6 of the 74 real Well records carry a successor
     pointer, and the v1 hash split put 3 on each side.
  2. **Confounded chain shape.** The real `supersede` chains present a distractor
     annotated `[other_in_pack]` — always the same older id, `530a5621` — while the
     real `keep` chains present `[newer_in_pack_but_no_pointer]` and no
     `other_in_pack` at all. The classes therefore differ by chain *template*, not
     only by the pointer rule, so a model can classify by shape without reading
     the rule. Phase 2's single non-prior answer picked the `530a5621` distractor,
     which is that shortcut failing.

This builder fixes both. Every case is a matched-shape chain:

    chain records you can see: <other> @ <ts> [<ann>]; <subject> @ <ts>; \
        <other> @ <ts> [<ann>]

The subject always sits between two same-pack neighbours. Both arms carry an
`other_in_pack` member, so "copy the other id" is wrong in BOTH classes. The
label follows one rule, and only the rule:

    supersede  iff  some chain member has ts > subject.ts and annotation == "successor"
    keep       otherwise

`other_in_pack` is always strictly older than the subject (the trap phase 2 fell
into); `newer_in_pack_but_no_pointer` is strictly newer (so a newer id alone is
never sufficient evidence of supersession). Gold is recomputed by `derive_action`
from the rendered chain for every row, including the real ones — a disagreement
with captured gold raises rather than being copied.

Two provenance classes, both labelled per row:

  * `real:*`        the 6 genuine supersession chains, kept on the side of the v1
                    split they already belong to. Real ids, timestamps, text.
  * `constructed:*` synthetic chains borrowing the shape and the kind/domain/tag
                    vocabulary of real Well records, with declared synthetic ids in
                    a declared synthetic pack. Source records are partitioned
                    disjointly between sides, so train and holdout share no text.

Every row passes the unchanged `capture_real_dataset.redact_row` sentinel gate;
anything still tripping is dropped and counted in the manifest. The gate is
imported, never re-implemented — it cannot drift.

Outputs (outside git):
  ~/WanderGround/datasets/sms/p3/{supersede_decider,well_curator}_{holdout,train}.jsonl
  ~/WanderGround/datasets/sms/p3/all_p3_{holdout,train}.jsonl
  ~/WanderGround/datasets/sms/p3/manifest.json

Run: python3 scripts/sms/build_p3_adversarial.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.sms import capture_real_dataset as cap  # noqa: E402

SMS_DIR = Path.home() / "WanderGround" / "datasets" / "sms"
OUT_DIR = SMS_DIR / "p3"
WELL = REPO / "gnosis" / "well" / "well.jsonl"
V1_HOLDOUT = SMS_DIR / "sms_real_v1_holdout.jsonl"
V1_TRAIN = SMS_DIR / "sms_real_v1_train.jsonl"

DATASET_ID = "sms_p3_adversarial_v1"
SCANNER_VERSION = cap.SCANNER_VERSION
ROLES = ("supersede_decider", "well_curator")
CASE_PREFIX = {"supersede_decider": "sdp3", "well_curator": "wcp3"}

#: Namespace for every synthetic id. Fixed forever: a re-run must produce the same
#: ids, or the holdout stops being the holdout.
UUID_NS = uuid.UUID("6f1c9a20-0e5b-5d7a-9c31-7b4e2a8d0f13")
CONSTRUCTED_PACK = "p3-constructed"

#: 12 supersede + 12 keep in the holdout, 6 + 6 in train. These are the exact counts
#: reported in the phase-3 doc; the balance is the whole point of the rebuild.
HOLDOUT_PER_ARM = 12
TRAIN_PER_ARM = 6

CHAIN_HEADER = "chain records you can see: "
NOT_GIVEN = "kind, domain and tags are NOT given. Infer them."
CONSTRUCTED_TAGS = ("p3", "constructed", "adversarial")
RETIRED_LIFECYCLE = "lifecycle: retired. this record is superseded by a newer record in the same chain."
CURRENT_LIFECYCLE = "lifecycle: current. no successor pointer is recorded for this record."

TS_FMT = "%Y-%m-%dT%H:%M:%SZ"


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def syn_id(seed: str) -> str:
    """Stable synthetic uuid for a constructed record. Cannot collide with the Well."""
    return str(uuid.uuid5(UUID_NS, f"{CONSTRUCTED_PACK}:{seed}"))


def parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, TS_FMT).replace(tzinfo=timezone.utc)


# ----------------------------------------------------------------- the rule


def derive_action(subject_ts: str, members: list[tuple[str, str, str]]) -> tuple[str, str | None]:
    """The forward-pointing rule, and the only thing that decides the label.

    `members` is [(record_id, ts, annotation)]. A `[successor]` annotation on a
    strictly newer record is the sole evidence for supersession; everything else
    — an older same-pack record, a newer record with no pointer — is not.
    """
    for rid, ts, ann in members:
        if ann == "successor" and ts > subject_ts:
            return "supersede", rid
    return "keep", None


def render_chain(subject_id: str, subject_ts: str, members: list[tuple[str, str, str]]) -> str:
    """Matched shape: the subject sits between two neighbours, oldest member first.

    Member order is fixed rather than shuffled per row, so presentation order
    carries no signal about the label.
    """
    left, right = members[0], members[1]
    return CHAIN_HEADER + "; ".join([
        f"{left[0]} @ {left[1]} [{left[2]}]",
        f"{subject_id} @ {subject_ts}",
        f"{right[0]} @ {right[1]} [{right[2]}]",
    ])


def normalise_annotation(raw: str) -> str:
    if raw == "successor":
        return "successor"
    return "newer_in_pack_but_no_pointer" if raw.startswith("newer") else "other_in_pack"


def well_by_prefix(prefix: str, well: dict[str, dict]) -> str:
    """v1 case ids are the first 8 hex chars of the Well record id."""
    matches = [rid for rid in well if rid.startswith(prefix)]
    if len(matches) != 1:
        raise KeyError(f"{prefix!r} matches {len(matches)} Well records")
    return matches[0]


# -------------------------------------------------------------- real chains


def real_chains(wc_rows: list[dict], well: dict[str, dict]) -> list[dict]:
    """Recover (subject, members) from genuine well_curator rows.

    The chain line the capture wrote is authoritative for what the model was
    shown; `well.jsonl` supplies the subject's own timestamp.
    """
    chains: list[dict] = []
    for row in wc_rows:
        if row["gold"].get("action") not in ("keep", "supersede"):
            continue
        subject_id = well_by_prefix(str(row["case_id"]).replace("wc_real_", ""), well)
        subject = well[subject_id]
        members: list[tuple[str, str, str]] = []
        for line in row["input"].splitlines():
            if not line.startswith(CHAIN_HEADER):
                continue
            for chunk in line[len(CHAIN_HEADER):].split("; "):
                bits = chunk.strip().split(" @ ")
                if len(bits) != 2 or bits[0] not in well:
                    continue
                head, _, tail = bits[1].partition("[")
                ann = normalise_annotation(tail.rstrip("]"))
                # The chain line lists the subject itself in the middle; that is
                # the subject, not a neighbour. Keeping it here would let it be
                # truncated into the member set and drop the real successor.
                if bits[0] == subject_id:
                    continue
                if any(m[0] == bits[0] for m in members):
                    continue
                members.append((bits[0], head.strip(), ann))
        if members:
            chains.append({
                "subject_id": subject_id,
                "subject": subject,
                "subject_ts": subject["ts"],
                "members": members,
                "provenance": "real",
                "source_file": row.get("source_file"),
                "source_group": row.get("source_group"),
                "captured_action": row["gold"]["action"],
            })
    return chains


def force_older_decoy(chain: dict, well: dict[str, dict], side_records: list[str]) -> dict:
    """Guarantee an `other_in_pack` member that is strictly older than the subject.

    Real `keep` chains carry only a `newer_in_pack_but_no_pointer` neighbour, so
    without this the two arms would still differ by shape.

    The decoy is drawn from `side_records` — the ids belonging to THIS side — not
    from the whole Well. Deciding it globally put two holdout subject ids into
    train-side chain lines, which is a genuine split leak for `supersede_decider`
    (whose input is the chain and nothing else). If a side's own pool holds
    nothing older, a synthetic id at subject_ts - 60min is used and flagged
    `synthetic_decoy` on the row, so the impurity is counted, not hidden.
    """
    subject_ts = chain["subject_ts"]
    members = list(chain["members"])
    if not any(a == "other_in_pack" and ts < subject_ts for _r, ts, a in members):
        candidates = sorted(
            ((rid, well[rid]["ts"]) for rid in side_records
             if rid != chain["subject_id"] and well[rid]["ts"] < subject_ts),
            key=lambda kv: (kv[1], kv[0]),
        )
        if candidates:
            rid, ts = candidates[-1]
        else:
            rid = syn_id(f"predecoy:{chain['subject_id']}")
            ts = (parse_ts(subject_ts) - timedelta(minutes=60)).strftime(TS_FMT)
            chain["synthetic_decoy"] = True
        members.append((rid, ts, "other_in_pack"))

    # Matched shape is exactly two neighbours. Select by rule priority, never by
    # position: dropping the successor to keep an extra decoy would silently flip
    # a `supersede` case to `keep`, so the successor always survives truncation.
    successors = sorted((m for m in members if m[2] == "successor"), key=lambda m: m[1])
    decoys = sorted((m for m in members
                     if m[2] == "other_in_pack" and m[1] < subject_ts and m not in successors),
                    key=lambda m: m[1])
    others = sorted((m for m in members if m not in successors and m not in decoys),
                    key=lambda m: m[1])
    spare = sorted(
        ((rid, well[rid]["ts"]) for rid in side_records if rid != chain["subject_id"]),
        key=lambda kv: (kv[1], kv[0]),
    )
    chosen = [d for d in decoys[:1]]
    if successors:
        chosen.append(successors[0])
    elif others:
        chosen.append(others[0])
    elif spare:
        chosen.append((spare[-1][0], spare[-1][1], "other_in_pack"))
    else:
        chosen.append((syn_id(f"decoy2:{chain['subject_id']}"),
                       (parse_ts(subject_ts) - timedelta(minutes=30)).strftime(TS_FMT),
                       "other_in_pack"))
        chain["synthetic_decoy"] = True
    if not decoys:
        # A supersede chain still needs an older decoy so both arms match shape.
        fallback = sorted(((rid, ts) for rid, ts in spare if ts < subject_ts),
                          key=lambda kv: kv[1])
        if fallback:
            chosen.append((fallback[-1][0], fallback[-1][1], "other_in_pack"))
        else:
            chosen.append((syn_id(f"predecoy2:{chain['subject_id']}"),
                           (parse_ts(subject_ts) - timedelta(minutes=60)).strftime(TS_FMT),
                           "other_in_pack"))
            chain["synthetic_decoy"] = True
    chain = dict(chain)
    chain["members"] = sorted(chosen[:2], key=lambda m: m[1])
    return chain


# ------------------------------------------------------- constructed chains


def constructed_chains(well: dict[str, dict], side_records: list[str]) -> list[dict]:
    """Two extra chains per already-present record, on the side that record is on.

    Every one of the 74 Well records is already a `well_curator` case on one side
    of the v1 split, so a record's prose may only be reused on that same side.
    Reusing it there is what makes this leak-free: each constructed chain reuses
    its own record's id, prose, kind/domain/tags and timestamp, and changes only
    the CHAIN. The label then flips with the chain:

        variant 0  [older other_in_pack] + [synthetic successor, newer, [successor]]
                   -> supersede
        variant 1  [older other_in_pack] + [synthetic newer, [newer_in_pack_but_no_pointer]]
                   -> keep

    The same subject id and the same prose therefore appear with both labels
    inside one split. That is a strictly harder test than a fresh subject would
    be: a model that memorises the subject rather than reading the chain fails,
    and the pair makes the failure visible. No prose crosses the split.
    """
    out: list[dict] = []
    by_id = {rid: rec for rid, rec in well.items()}
    pool = sorted(set(side_records), key=lambda rid: hashlib.sha256(f"p3:{rid}".encode()).hexdigest())
    for idx, rid in enumerate(pool):
        rec = by_id[rid]
        base = parse_ts(rec["ts"])
        seed = f"{rid}:{idx}"
        older_candidates = [x for x in pool
                            if x != rid and by_id[x]["ts"] < rec["ts"]]
        older_candidates.sort(key=lambda x: (by_id[x]["ts"], x))
        synthetic_decoy = False
        if older_candidates:
            # Deterministic spread over the older candidates, clamped so a short
            # pool cannot index out of range.
            older_id = older_candidates[-(1 + idx % min(3, len(older_candidates)))]
            older_ts = by_id[older_id]["ts"]
        else:
            # This side's earliest record: use a synthetic older id so the chain
            # still carries the decoy both arms need. Flagged on the row.
            older_id = syn_id(f"older:{seed}")
            older_ts = (base - timedelta(minutes=7 + idx % 23)).strftime(TS_FMT)
            synthetic_decoy = True
        variants = [
            (syn_id(f"succ:{seed}"), (base + timedelta(minutes=3 + idx % 17)).strftime(TS_FMT), "successor"),
            (syn_id(f"newer:{seed}"), (base + timedelta(minutes=5 + idx % 29)).strftime(TS_FMT),
             "newer_in_pack_but_no_pointer"),
        ]
        for tail_id, tail_ts, tail_ann in variants:
            members = sorted(
                [(older_id, older_ts, "other_in_pack"), (tail_id, tail_ts, tail_ann)],
                key=lambda m: m[1],
            )
            out.append({
                "subject_id": rid,
                "subject": rec,
                "subject_ts": rec["ts"],
                "members": members,
                "provenance": "constructed",
                "source_file": f"{CONSTRUCTED_PACK}:{seed}",
                "source_group": f"p3:{CONSTRUCTED_PACK}",
                "borrowed_record": rid,
                "synthetic_decoy": synthetic_decoy,
            })
    return out


# ---------------------------------------------------------------- row build


def gold_tags(rec: dict) -> list[str]:
    """The Well stores tags as one comma-joined string; v1 gold wraps it in a list.

    `list("a, b")` would explode into characters, so the shape is normalised here
    to match what capture_real_dataset produced — otherwise tags_f1 would be 0 by
    construction and the curator's tag metric would be unscoreable.
    """
    tags = rec.get("tags")
    if isinstance(tags, list):
        return [str(t) for t in tags]
    if isinstance(tags, str) and tags.strip():
        return [tags.strip()]
    return []


def build_row(chain: dict, role: str) -> dict:
    """Render one chain into a dataset row. Gold comes from `derive_action` only."""
    subject_ts = chain["subject_ts"]
    members = chain["members"]
    action, superseded_by = derive_action(subject_ts, members)
    if chain.get("captured_action") is not None:
        assert action == chain["captured_action"], (
            f"rule disagrees with captured gold for {chain['subject_id']}: "
            f"{action} != {chain['captured_action']}"
        )
    chain_text = render_chain(chain["subject_id"], subject_ts, members)
    if role == "supersede_decider":
        inp = chain_text
        gold: dict = {"action": action, "superseded_by": superseded_by}
    else:
        rec = chain["subject"]
        lifecycle = RETIRED_LIFECYCLE if action == "supersede" else CURRENT_LIFECYCLE
        inp = "\n".join([
            "Triage this Well record.",
            f"record: {chain['subject_id']}",
            f"trigger: {rec.get('trigger', '')}",
            f"rule: {rec.get('rule', '')}",
            f"why: {rec.get('rationale', '')}",
            lifecycle,
            chain_text,
            NOT_GIVEN,
        ])
        gold = {
            "kind": rec.get("kind", "insight"),
            "domain": rec.get("domain", "harness"),
            "tags": gold_tags(rec),
            "action": action,
            "superseded_by": superseded_by,
            "rationale": ("retired record; successor points forward in time"
                          if action == "supersede"
                          else "current record; no successor pointer recorded"),
        }
    provenance = chain["provenance"]
    tag_list = (["p3", "adversarial", provenance, action]
                if provenance == "constructed" else ["p3", "adversarial", "real", action])
    prefix = CASE_PREFIX[role]
    # A constructed chain reuses its source record's subject, so the id needs the
    # tail annotation too or the two variants of one subject would collide.
    variant = members[-1][2] if provenance == "constructed" else "chain"
    case_id = f"{prefix}_{provenance[:4]}_{chain['subject_id'][:8]}_{variant[:6]}"
    return {
        "role": role,
        "case_id": case_id,
        "input": inp,
        "gold": gold,
        "tags": tag_list,
        "source_file": chain["source_file"],
        "source_group": chain["source_group"],
        "labeler": f"{provenance}:p3_adversarial_supersession[{action}]",
        "provenance_class": provenance,
        "synthetic_decoy": bool(chain.get("synthetic_decoy", False)),
        "chain_members": [{"record_id": r, "ts": t, "annotation": a} for r, t, a in members],
        "recorded_at": subject_ts,
    }


def sha256_rows(rows: list[dict]) -> str:
    blob = "\n".join(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def verify(rows: list[dict]) -> dict:
    """Check the adversarial properties actually hold on the written rows.

    A manifest that merely asserts balance is worthless; these four counts are the
    properties the dataset exists to provide, so they are computed from the rows
    that were written and any failure is loud.
    """
    n = len(rows)
    rule_mismatch = 0
    older_decoy = 0
    for r in rows:
        members = r.get("chain_members") or []
        has_successor = any(
            m["annotation"] == "successor" and m["ts"] > r["recorded_at"] for m in members)
        if has_successor != (r["gold"]["action"] == "supersede"):
            rule_mismatch += 1
        if any(m["annotation"] == "other_in_pack" and m["ts"] < r["recorded_at"] for m in members):
            older_decoy += 1
    dist = Counter(str(r["gold"]["action"]) for r in rows)
    dup_ids = [cid for cid, c in Counter(str(r["case_id"]) for r in rows).items() if c > 1]
    return {
        "rows": n,
        "gold_action": dict(dist),
        "older_decoy_rows": older_decoy,
        "rule_vs_gold_mismatch": rule_mismatch,
        "duplicate_case_ids": dup_ids,
        "balance_ok": len(dist) == 2 and min(dist.values()) == max(dist.values()),
        "adversarial_ok": older_decoy == n and rule_mismatch == 0 and not dup_ids,
    }


def leak_report(out_dir: Path, well: dict[str, dict]) -> dict:
    """Confirm no record's prose appears on both sides of the split.

    Every Well record is already a case on exactly one side, so a record id
    appearing in both sides' row sets would mean its prose leaked across the
    split. Also reports how many subjects deliberately carry both labels — that
    is a feature (it forces the model to read the chain, not memorise the
    subject), so it is counted rather than treated as a violation.
    """
    def subjects(side: str) -> set[str]:
        ids: set[str] = set()
        for f in sorted(out_dir.glob(f"*_{side}.jsonl")):
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    ids.add(str(json.loads(line)["case_id"]))
        return ids

    def well_subjects(side: str) -> set[str]:
        rows = [json.loads(ln) for fn in sorted(out_dir.glob(f"*_{side}.jsonl"))
                for ln in fn.read_text(encoding="utf-8").splitlines() if ln.strip()]
        found: set[str] = set()
        for r in rows:
            if r.get("provenance_class") == "constructed":
                found.add(str(r["case_id"]))
            for m in r.get("chain_members") or []:
                if m["record_id"] in well:
                    found.add(m["record_id"])
        return found

    train_well = well_subjects("train")
    holdout_well = well_subjects("holdout")
    # Subjects (not case ids) carrying both labels: a constructed chain reuses its
    # source record's subject, so subject -> {keep, supersede} is the count that
    # shows the model must read the chain rather than memorise the record.
    by_subject: dict[str, set[str]] = {}
    for side in ("train", "holdout"):
        for r in (json.loads(ln) for fn in sorted(out_dir.glob(f"*_{side}.jsonl"))
                  for ln in fn.read_text(encoding="utf-8").splitlines() if ln.strip()):
            subject = next((ln.split(": ", 1)[1] for ln in str(r.get("input", "")).splitlines()
                            if ln.startswith("record: ")), None)
            if subject:
                by_subject.setdefault(subject, set()).add(str(r["gold"]["action"]))
    dual = {k: sorted(v) for k, v in by_subject.items() if len(v) > 1}
    return {
        "case_id_overlap": sorted(subjects("train") & subjects("holdout")),
        "well_subject_overlap": sorted(train_well & holdout_well),
        "leak_ok": not (train_well & holdout_well),
        "subjects_with_both_labels": len(dual),
        "example_dual_label_subject": next(iter(sorted(dual.items())), None),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build the phase-3 adversarial balanced supersession set.")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args(argv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    well = {r["record_id"]: r for r in load(WELL)}
    v1_holdout = load(V1_HOLDOUT)
    v1_train = load(V1_TRAIN)
    holdout_wc = [r for r in v1_holdout if r["role"] == "well_curator"]
    train_wc = [r for r in v1_train if r["role"] == "well_curator"]

    manifest: dict = {
        "dataset_id": DATASET_ID,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scanner_version": SCANNER_VERSION,
        "uuid_namespace": str(UUID_NS),
        "constructed_pack": CONSTRUCTED_PACK,
        "rule": "supersede iff a chain member has ts > subject.ts and annotation == 'successor'",
        "matched_shape": "subject id sits between two same-pack neighbours; both arms carry "
                         "an older other_in_pack member",
        "sides": {},
    }

    for side, per_arm, wc_rows in (("holdout", HOLDOUT_PER_ARM, holdout_wc),
                                   ("train", TRAIN_PER_ARM, train_wc)):
        side_records = [well_by_prefix(str(r["case_id"]).replace("wc_real_", ""), well) for r in wc_rows]
        real = [force_older_decoy(c, well, side_records) for c in real_chains(wc_rows, well)]
        con = constructed_chains(well, side_records)
        pools = {"supersede": [], "keep": []}
        for chain in real + con:
            action, _sb = derive_action(chain["subject_ts"], chain["members"])
            pools[action].append(chain)

        stats_side: dict = {"per_arm_target": per_arm, "max_real_per_arm": per_arm // 2}
        union: list[dict] = []
        for role in ROLES:
            arms: dict[str, list[dict]] = {}
            counts: dict[str, dict[str, int]] = {}
            for arm in ("supersede", "keep"):
                by_prov: dict[str, list[dict]] = {"real": [], "constructed": []}
                for chain in sorted(pools[arm], key=lambda c: (c["provenance"] != "real",
                                                                str(c["source_file"]))):
                    by_prov[chain["provenance"]].append(chain)
                # Cap real rows at half the arm so both arms carry the SAME
                # real/constructed mix. Without this the keep arm would be all
                # real (47 real keeps are available) and the supersede arm mostly
                # constructed, reintroducing a provenance confound across arms.
                n_real = min(len(by_prov["real"]), per_arm // 2)
                arms[arm] = by_prov["real"][:n_real] + by_prov["constructed"][: per_arm - n_real]
                counts[arm] = {"real": n_real, "constructed": per_arm - n_real}
                if len(arms[arm]) < per_arm:
                    raise ValueError(
                        f"{side}/{role}/{arm}: only {len(arms[arm])} chains available, need {per_arm}"
                    )
            rows = [build_row(chain, role) for arm in ("supersede", "keep") for chain in arms[arm]]
            # interleave arms so the file order carries no label
            kept: list[dict] = []
            dropped = 0
            redactions: Counter = Counter()
            sup = iter([r for r in rows if r["gold"]["action"] == "supersede"])
            kip = iter([r for r in rows if r["gold"]["action"] == "keep"])
            while True:
                picked = [next(sup, None), next(kip, None)]
                if all(p is None for p in picked):
                    break
                for row in picked:
                    if row is None:
                        continue
                    red, hits, residual = cap.redact_row(row)
                    redactions.update(hits)
                    if residual:
                        dropped += 1
                        continue
                    kept.append(red)
            dest = out_dir / f"{role}_{side}.jsonl"
            with dest.open("w", encoding="utf-8") as f:
                for r in kept:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            dist = Counter(str(r["gold"]["action"]) for r in kept)
            prov = Counter(str(r["provenance_class"]) for r in kept)
            stats_side[role] = {
                "rows": len(kept),
                "gold_action": dict(dist),
                "provenance_class": dict(prov),
                "chain_source_mix": counts,
                "dropped_post_redaction": dropped,
                "synthetic_decoy_rows": sum(1 for r in kept if r.get("synthetic_decoy")),
                "redactions": dict(redactions),
                "file": dest.name,
                "sha256_16": sha256_rows(kept),
                "verify": verify(kept),
            }
            v = verify(kept)
            if not (v["balance_ok"] and v["adversarial_ok"]):
                raise AssertionError(f"{side}/{role} failed its own verification: {v}")
            print(f"[p3] {side:7s} {role:18s} {len(kept):3d} rows  action={dict(dist)}  prov={dict(prov)}")
            union.extend(kept)
        union_dest = out_dir / f"all_p3_{side}.jsonl"
        with union_dest.open("w", encoding="utf-8") as f:
            for r in union:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        stats_side["union"] = {"rows": len(union), "file": union_dest.name,
                               "sha256_16": sha256_rows(union)}
        print(f"[p3] {side:7s} {'ALL':18s} {len(union):3d} rows -> {union_dest.name}")
        manifest["sides"][side] = stats_side

    manifest["leak_check"] = leak_report(out_dir, well)
    print(f"[p3] leak check: well_subject_overlap={len(manifest['leak_check']['well_subject_overlap'])} "
          f"leak_ok={manifest['leak_check']['leak_ok']} "
          f"subjects_with_both_labels={manifest["leak_check"]["subjects_with_both_labels"]}")
    if not manifest["leak_check"]["leak_ok"]:
        raise AssertionError(f"split leak: {manifest['leak_check']['well_subject_overlap']}")

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"[p3] manifest -> {out_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())