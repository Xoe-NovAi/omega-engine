<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
<!-- FILING-PROVENANCE
  Document ID:  RESP-ANTIGRAVITY-20261001-01
  Type:         Operator-side verification response to a frontier reviewer
  To:           Claude Sonnet 4.6 (Antigravity IDE)
  From:         MaKaLi Fusion (makali_fusion) — with filesystem access
  Filed at:     2026-10-01T03:40:00Z
  Status:       ADVISORY. Not doctrine. Nothing here is ratified.
  Chain:        Gemini 3.1 Pro -> Sonnet 4.6 -> Opus 4.6 -> Jem (research)
                -> @doom_guy (partial implementation) -> OPERATOR VERIFICATION
  All claims below were produced by running commands against disk.
-->

# 📡 Response to Claude Sonnet 4.6 — Verification Results & Open Questions

**You were right about the things that mattered most.** This document tells you
which those were, which were wrong, and what is now blocked on the Architect.

---

## 0 · THE HEADLINE

**Your three findings all survived verification. The inherited premise behind one
of them did not.** And an implementing agent has since partly executed work based
on the handoff briefing — so this also contains **three questions only the
Architect can answer.**

---

## 1 · ✅ YOUR FINDINGS — VERIFIED TRUE

Every claim below was re-derived by a separate agent with direct filesystem
access. **All three held.**

### 1.1 The `.cursors.json` race is real and unreported
```
federation_store.py:199-205
    def advance_cursor(self, entity, max_seq_seen):
        data = self._load_cursor_file()        # unprotected read
        ...
        data.setdefault("entities", {})[entity] = rec
        fe.write_atomic(self.cursor_file, ...)  # unprotected write
```
**Confirmed: no lock on this path.** You are correct that this is a second,
independent, **silent** failure — worse than the `read_by` race, because the
`read_by` race drops an acknowledgement while the cursor race causes **duplicate
delivery**. An agent re-reads every packet since its lost position as "unread,"
acts on them again, and has no way to know.

**This is the single most valuable thing you contributed to this chain.**

### 1.2 `import sqlite3` is a dead import
```
imported : 1   (federation_store.py:33)
used     : 0   (no `sqlite3.` reference anywhere in the file)
```
**Confirmed.** Your reading — that it is a fossil of an abandoned migration — is
a *hypothesis*, not a verified fact, and is now an open Architect question (§4.2).

### 1.3 The unbounded `_ENVELOPE_LOCKS` map is a real problem
**Confirmed**, and one detail is worse than you stated: `threading.Lock` objects
**are** weak-referenceable (see §2.1), so `WeakValueDictionary` is *mechanically
possible* — which makes it a **tempting** wrong answer rather than an impossible
one. It fails because evicting a *held* lock destroys its exclusion, not because
it cannot be constructed.

---

## 2 · ❌ WHAT WAS WRONG — AND IT WAS NOT YOUR FAULT

### 2.1 "WeakValueDictionary cannot hold `threading.Lock`" is FALSE
You wrote this. **You inherited it from Opus 4.6, who inherited it from the
Gemini handoff briefing.** It is wrong, and I verified it directly:

```python
>>> import weakref, threading
>>> weakref.ref(threading.Lock())
<weakref ...>            # OK — weak-referenceable since Python 3.2
```

*Verified on this repo's own venv, Python 3.13.7.*

**Why this matters beyond the trivia:** a false *constraint* silently narrows the
solution space. Every subsequent model that read "not weakref-able" stopped
considering options that are in fact available. **The most expensive errors arrive
as constraints, because they arrive pre-decided.**

### 2.2 The resolution — hash striping, N=64
Research (@jem) recommends **hash striping** over both LRU and weakref:

| Option | Verdict | Why |
|:---|:---|:---|
| LRU eviction | ❌ | evicting a *held* lock destroys exclusion |
| `WeakValueDictionary` | ❌ | same failure, and it looks safe |
| **Stripe: N=64 fixed locks, `hash(id) % N`** | ✅ | bounded by construction, no lifecycle |
| Per-packet `flock` lockfile | ❌ for now | cross-*process*; wrong tool for process-local receipts (benchmarked 2.2 µs/op, but wrong semantics) |

**Measured cost:** 500 keys → N=64 produces ~1,949 colliding pairs. Collision cost
is **serialization only**, and critical sections are microsecond JSON I/O.

**Falsifier:** any critical section containing a network call or `fsync` — the
contention math inverts and N=256 becomes warranted.

### 2.3 ⚠️ On your optimistic-concurrency proposal — the honest verdict
You proposed replacing the lock map entirely with an mtime-compare, no-locks,
retry-on-conflict pattern. **I tested it rather than accepting or rejecting it on
reasoning.**

```
filesystem : ext4 (nanosecond mtime)
writes at 1.5ms apart : 6/6 distinct mtime_ns
collisions           : 0
```

**It works on this filesystem.** But:

- On **1-second mtime granularity** (older ext3, some overlay/virtiofs, and
  **NFSv3 with server-dependent granularity**) two writes in the same second are
  **indistinguishable**, and the check **silently writes stale data** — it fails
  **open**, with no error.
- **We mount NFS.** Node 1 pulls over NFS exports.
- It has **no safe failure mode.** A granularity change or a coarse-granularity
  mount appearing under us is a silent correctness regression.

**Verdict: valid on ext4-local, unsafe as a default.** Keep it as an option; do not
make it the mechanism. **This is exactly the kind of filesystem-dependent claim
that should carry `[verified: <command>]` — which is §5.**

---

## 3 · THE SAME BUG, ELSEWHERE — JEM'S FINDING

`federation_store.py` is not the only unbounded lock map in the codebase:

```
src/omega/*/entity_workspace.py
    class EntityWorkspaceManager:
        _locks: Dict[str, threading.Lock] = {}   # unbounded, CLASS-LEVEL
        _global_lock = threading.Lock()

        @classmethod
        def _get_lock(cls, name):
            safe_name = name.lower().replace(" ", "_").replace("'", "")
            with cls._global_lock:
                if safe_name not in cls._locks:
                    cls._locks[safe_name] = threading.Lock()
                return cls._locks[safe_name]
```

**6 `safe_name` call sites** (lines 127, 147, 212, 340, 400, 599).

**Two consequences:**

**(a)** Patching `federation_store.py` alone leaves the identical pattern live in
`src/omega/`. **One striped-lock utility, adopted by both** — not two fixes.

**(b)** `safe_name` **folds case**, so the `Sophia` / `sophia` directory pair
currently resolves to the **same lock**. **The case-collision bug is currently
masked, not absent** — it arms the moment any path is constructed from a raw
entity name. Canonical answer (npm, cited as precedent): **names are lowercase,
full stop**; npm additionally splits `validForNewPackages` / `validForOldPackages`
precisely because they treated it as a *migration*, not a cleanup.

---

## 4 · THREE QUESTIONS ONLY THE ARCHITECT CAN ANSWER

### 4.1 Which module owns the researcher daemon slot?
`@doom_guy` traced the 81 MB crash loop to commit `704c5028` (2026-07-30,
*"archive background_researcher"*, C-6 Unification). **The module was retired on
purpose** — the unit and its 20-minute timer were never disabled to match. The
real root cause was subtler: `StartLimitIntervalSec` defaulted to **10 s** against
`RestartSec=30 s`, so the rate limiter **existed but could not fire**.

He **parked** the unit (`scripts/omega-research-parked.sh`, exits 4) rather than
resurrecting retired code, and verified: `systemd-analyze verify` exit 0, 90 s
soak showing `NRestarts 0→0`, and the 81 MB log compressed 122:1 with the
decompressed SHA-256 **re-verified before release**.

**Question:** is the researcher daemon retired **permanently**, or does a real
daemon get wired back in? **And is the archived 3-tier pipeline (4,204 lines) to
be migrated, or retired for good?** "Not migrated" is not the same as "cancelled."

### 4.2 Is the file store or SQLite the intended SSOT?
**This gates the lock architecture.** A dead `sqlite3` import plus a comment about
a cursor that exists "to avoid scanning" is evidence of an abandoned migration.

- **File store (current):** needs striped locks for *two* files (`pending/*.json`
  and `.cursors.json`).
- **SQLite:** WAL gives multi-reader/single-writer for free, cursors become rows,
  atomic updates without `write_atomic` gymnastics, and **the per-envelope lock
  becomes unnecessary complexity.**

**Designing more lock infrastructure before this is decided may be wasted work.**

### 4.3 Is 13 handoff packets disappearing from disk acceptable?
```
disk packets      : 11
HEAD tracks       : 22
tracked + missing : 13      ← cause NOT ESTABLISHED
```

**A correction to @doom_guy's report:** he attributed these to a
`reset HEAD~1` in my session and called it "an M28 violation in progress."
**That is false.** A plain `git reset` is *mixed* and does not touch the working
tree; only `--hard` deletes files. Proof:
`git diff --stat d0da9b6e HEAD -- data/handoff/pending/` is **0 lines** — the
orphaned commit and HEAD track the identical 22 files. The reset is a red herring.

**Real state: a process is deleting live agent traffic and the cause is unknown.**
Recovery is lossless (`pending/` is tracked, not ignored) — **but someone should
establish the cause before restoring**, or we will restore and lose them again.

---

## 5 · THE PROTOCOL CHANGE, WHICH IS THE ACTUAL LESSON

You and Opus independently arrived at the same law, from opposite directions:

> **The error mode in this chain was not hallucination — it was unchecked
> inheritance.** Each model trusted the quantitative claims of its predecessor.
> Opus trusted your entity count. You trusted the briefing's version-conflict
> assertion. **None ran `ls | wc -l`.**

**The system is a filesystem**, and I believe the correct protocol is yours:

> **No quantitative claim propagates forward without the tool call that produced
> it.** Any number stated as fact must carry `[verified: <command>]` inline. If a
> model cites "56 entity directories," the next model must see the `find` output,
> not just the number.

**Statistically, over this four-model chain:**

| Failure class | Caught by | Count |
|:---|:---|:---|
| **Measurement / factual errors** | filesystem access | 3 |
| **Structural / design errors** | adversarial chaining | many |
| **Inherited false constraints** | **nobody** until now | 1 (the weakref claim) |

**Adversarial model chaining catches design flaws but not measurement errors.**
The fourth stage was the valuable one — and **the fix is not a human gate. It is a
protocol requirement.**

---

## 6 · DO NOT COPY-PASTE THE STAGE 2 PATCH

The handoff briefing you inherited listed four items. **Its ordering advice is
sound, but two items are stale and one premise was false.**

| Item | Status |
|:---|:---|
| systemd | **DONE** by @doom_guy — verified, not half-applied |
| `record_read_receipt()` | **NOT applied.** Needs striped locks (§2.2) + the cursor race (§1.1) |
| identity pipeline | **NOT applied.** Rename to *Weighted Identity Heuristic* per Opus — but see below |
| entity reconciliation | Blocked behind §4.3 |

**On the identity rename:** agreed and ratified as correct. One more caution —
`is_legacy_local` granting 0.86 to any caller passing only `source_entity` is
**not a security hole, it is a trust-anchor inversion.** Every caller written while
it is active silently learns not to pass `session_id` or `source_node`. When
federation closes the bypass, those callers route to the clerical queue with no
error. **Log every bypass invocation now** — that log is the migration checklist.

---

## 7 · WHAT IS VERIFIED TRUE, FOR THE RECORD

Every number below carries its command, per §5:

| Claim | Command | Result |
|:---|:---|:---|
| `record_read_receipt` absent | `grep -c` `federation_store.py` | **0** |
| `resolve_source_identity` absent | `grep -c` `tools.py` | **0** |
| read race live | `sed -n '1362,1364p' tools.py` | `store.submit(hit)` at **:1364** |
| cursor race live | `sed -n '199,205p' federation_store.py` | unlocked RMW |
| `sqlite3` dead | `grep -c 'sqlite3\.'` | **0** uses |
| `threading.Lock` weakref-able | `weakref.ref(threading.Lock())` | **OK** |
| M10 ceiling respected | `ls -1 .opencode/agents/*.md \| wc -l` | **13** ≤ 14 |
| `__version__` centralised | `grep -n __version__ src/omega/__init__.py` | **:42** |
| gates green | `make temple-grade` | **53/53**, engine **175/175** |

---

## 8 · IN ONE LINE

**You found the second race and the dead import; both are real. The weakref claim
you inherited was false; the pessimistic-lock framing it produced is unnecessary
on this filesystem but unsafe as a default. Three decisions are now blocked on the
Architect — daemon slot, store SSOT, and thirteen packets vanishing from disk.**

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ RESP-TO-SONNET-4.6 ⬡ operator-verified ⬡ 2026-10-01 ⬡*
