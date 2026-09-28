# 🔱 SESSION GNOSIS — MaKaLi Fusion
**Entity**: `makali_fusion` · **Node**: 0 / BASTION · **AP**: `AP-MAKALI_FUSION-v2.0.0`
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ opencode/space-bunny-free ⬡ 2026-09-28 ⬡ COMPACT-PREP

> **On resume, read in this order:** this file → `docs/architecture/HIVEMIND_TRANSPORT.md` →
> `docs/architecture/EMBEDDING_SOVEREIGNTY.md` → `data/coordination/ACTIVE_SPRINT.json`.
> If a claim here conflicts with a file, **the file is truth** — this record is a pointer, not an oracle.

---

## §0 — THE ONE-LINE VERSION

The fleet spent 36+ hours blind because a green gate chain never booted the thing it was gating.
Nine EIS sessions were re-grounded, four workstreams repaired the substrate, and the root lesson
is now written into three architecture docs, two CI gates, and a protocol.

---

## §1 — WHAT IS COMMITTED

| Item | Value |
|---|---|
| **Commit** | `de660681` on `release/debut-v1.6.0` |
| **Parents** | `1f531b36` (pre-merge tip) |
| **`origin/main`** | `268528e7` — the squash of PR #4 |
| **Topology** | Local HEAD's parent is **not** an ancestor of main, but the **trees are byte-identical** → cherry-pick applies cleanly |
| **PR #4** | Merged; repo **PUBLIC** |
| **Temple-grade** | **53/53 PASS** |
| **Gates added** | `check-hub-imports` (Tier A in-suite + Tier B release), `check-hub-health` rewritten |
| **Docs added** | `docs/architecture/HIVEMIND_TRANSPORT.md`, `EMBEDDING_SOVEREIGNTY.md`, `NES_EIS_FACET_PROTOCOL.md` |

**Not yet done:** nothing is pushed. `release/debut-v1.6.0` → main requires an Architect decision (push branch, or cherry-pick + PR #5).

---

## §2 — THE ROOT CAUSE, STATED PLAINLY

The Hivemind consolidation deleted `_extended_sessions` from `state.py`. `server.py` still imported it.
`omega-hub.service` crash-looped on boot.

**`make temple-grade` reported 53/53 the entire time.** No gate imported an entry point. Static checks,
doc validation, a compliance meter, tracking validation, and a JSONL renderer suite — 53 green assertions
against an engine that could not start.

**Compounding:** `make check-hub-health` was `systemctl --user is-active`, which returns **true** during
`activating (auto-restart)`. A gate that cannot fail is worse than no gate: it converts an outage into a
false green light.

**And:** `StartLimitIntervalSec` / `StartLimitBurst` were in `[Service]`, where systemd logged
`Unknown key … ignoring` and **silently discarded them**. The unit's comment claimed a breaker that
"STOP trying after 5 crashes in 120s." It never existed. Meanwhile `omega-searxng-mcp` had reached
**NRestarts=6991**.

> **The lesson that generalizes:** a safety mechanism written down but not parsed is worse than none,
> because it manufactures belief. Same for a test that skips: `TestCriticalTools` was 20 skips / 0
> assertions over a truncated tool list, so it could never have caught the tool removal it was
> nominally guarding.

---

## §3 — WHAT WAS REPAIRED (four workstreams)

### Ma'at — gates, shim, contracts
- `tests/test_hub_import_smoke.py` — 6 **explicit** modules, never a glob; asserts `returncode == 0`
  **and** `"Traceback" not in stderr`; 3-state output; structural guards that every passthrough name resolves.
- `make check-hub-imports` wired as the **first** temple-grade prerequisite. Tests `HEAD` + tracked diff,
  so an uncommitted fix is *verified* rather than punished — a gate that punishes a developer for having
  a fix creates pressure to `git commit --no-verify`, the exact failure mode gates exist to prevent.
- `check-hub-health`: ActiveState + SubState + NRestarts bound + port LISTEN + dwell time + `uptime_s`.
  **Four negative tests observed failing**, including a genuinely stopped hub.
- The legacy shim was **half-mapped**: 12 of 28 names bound to deleted symbols and failed at *call* time.
  Now 28/28 with kwarg renames.
- `entity_context` enrichment restored: slot/role/archetype, readiness block, L3 lesson distillation.
- `post` contract ratified: `decisions=[]` is **valid** (empty ≠ omitted); only explicit `None`/omission rejects.
- searxng `stateless` claim was **false** — it is a FastMCP *settings* field, not a method arg, so the
  server ran stateful while `/health` advertised stateless. Now derived from live settings.

### Carmack — stranded imports, embedding sovereignty
- `from omega_hub import …` resolved against a module that **does not exist** — found in
  `hivemind_bridge.py`, `watchdog.py`, `scorecard.py` (a **fifth** site he found himself), `post_to_hivemind.py`.
- `TestCriticalTools`: 20 skips/0 assertions → 26 real assertions incl. 8 retired-name absence checks,
  with a **falsification test** (injected the pre-consolidation surface; watched it fail).
- **Priority-1 nomic fallback removed** as a substitution path. Cross-model substitution now raises.
  MRL ladder preserved.
- **EmbeddingGemma fully removed** — config, provider, adapters, and the 1009-row table.
- **Two self-retractions, both load-bearing:** "39 real vectors" was wrong (it is 1009, proven by
  `1009 × 3072 = 3,099,648` byte arithmetic); "8/10 EmbeddingGemma-300M" was wrong (**0/10** — the rows
  were deterministic feature-hash: 568 all-zero, 4–25 nonzero of 768, L2 exactly 1.0, ratios exactly
  3.0 and 2.0, algorithm reproduced locally).

### Grokster — seals and queue hygiene
- The `n0-to-n1-v2` seal was **broken**: a 3-byte post-seal edit left `MANIFEST.yaml`/`SHA256SUMS` stale
  (40/41, 41/42). Repaired → **41/41 + 42/42 + 43/43** across both trees. Rebuild was provable: 1 entry
  changed, 0 added, 0 removed, only `built_at_utc` advanced.
- Applied Carmack's ruling: package text must not name Node 0 internal paths. That string was the seal-breaker
  and would have broken again on the next rename.
- **Ledger trap for the next sealer:** grepping `^- path:` returns **43** because `subordinate_ledgers:`
  has its own entries at column 0. True `file_count` is **41**. Anyone counting that way mis-seals.
- Classified **759 handoff packets** individually; moved **0** under a false premise and said so.
- Cline dispatch archived (stale, premised on "Repo is PRIVATE", contained `filter-repo --force-push`).

### MaKaLi — governance
- Dispatched via **EIS chat session IDs**, in parallel, with Facet Handshakes.
- Ratified the `post` contract; wrote `NES_EIS_FACET_PROTOCOL.md`.
- **Refused `--no-verify`.** The Code↔Docs Drift Guard blocked the commit; the guard was right, so I wrote
  real documentation instead of bypassing it.

---

## §4 — THE SUBTLE SYSTEM LESSONS (this is the durable value)

1. **EIS sessions also receive the parent's model when paged.** Not just NES children. This is why three
   of nine entities self-reported a model they were not running. Provenance must be *read*, never inherited
   from the brief or from a model ID stamped in a source header.
2. **A stale NES is worse than no NES.** Paging a days-old task session executes competently against a
   world that moved on, and nothing flags it. Prefer the EIS for judgment and anything touching the record.
3. **A page can fail while succeeding.** The tool reported quota errors and cancellations; the DB showed all
   nine sessions had received the brief and responded. **Verify delivery in the store, not from the tool's
   exit status.**
4. **Three agents refused to fabricate a Hivemind post ID** when the tool was absent. That is the single
   best behavior in the entire session. M23 working as designed.
5. **`pyproject.toml` `addopts = "-n auto -x"`** masked 8 real errors as "5 failures" — *which* 5 varied
   with random ordering. **Anything reporting "N failures" from a default `pytest` here reports an artifact.**
6. **A gate run in a shared worktree is a snapshot of a concurrent build**, not of a fixed artifact.
   Ma'at's Tier A caught a transient circular import mid-edit and went green when it settled.
7. **Unescaped quotes in YAML are silent corruption.** Ma'at's `proposed_lessons.yaml` broke on
   `pip install -e ".[cli,dev]"` — three lines from a *prior* day's append. He self-reported before I checked.
8. **`.gitignore:270` blanket-ignores `*.md`**, and `docs/` re-admits files one-by-one via `!`. So the
   drift guard *requires* a staged `docs/` change that `.gitignore` prevents — leaving only two paths:
   edit an unrelated doc (theater) or `--no-verify`. **Fixed by adding the three `!` lines.**
9. **Paged EIS sessions do not receive the `omega-hub` MCP tools.** Config lists it, the hub is healthy, and
   the repo is not the cause — the decisive proof being that `firecrawl` is `enabled: false` yet paged
   sessions still get `firecrawl_*` tools. **A config that does not predict the observed surface is not the
   config in force.** Interim answer: `scripts/hivemind_post.py`.

---

## §5 — FLEET STATE

| Entity | Docs | Hivemind | Note |
|---|---|---|---|
| kali | v4.9.0 | ✅ | 3-verb doctrine ratified; M36 reap authorized |
| researcher | 700-line gnosis | ✅ | 40 lessons; flagged `m36_recursive_probe` re-contamination |
| jem | v6.0.0, 42 lessons | ✅ | 2 self-retractions; decoupling = fault-tolerance |
| roc_racoon | updated | ✅ | SQLite schema banked for federation horizon |
| grokster | v23, 1291 lines, 40 lessons | ✅ | seal doctrine + ledger trap |
| doom_guy | **populated from blank** | ✅ | 5 L3 axioms; 96 lesson entries |
| lilith | gnosis + 11 decisions | ✅ | parity corrected: 54 tools, 4 Hivemind |
| maat | 32 findings, 117 lessons | ✅ | YAML repaired; `hivemind_post.py` shipped |
| carmack | 965 lines, 15 lessons | ✅ | two retractions; Step 19 = rebuild not migration |

---

## §6 — OPEN THREADS (priority order)

1. **Push topology** — `de660681` is on `release/debut-v1.6.0`; main is a squash. Architect decides:
   push branch vs. cherry-pick + PR #5.
2. **`m36_recursive_probe.py:228`** — hardcoded CWD-relative `data/handoff/pending`. Needs
   `OMEGA_HANDOFF_ROOT`, mirroring the existing `OMEGA_M34_REGISTRY` precedent. **Live re-contamination path.**
3. **Sequencing constraint:** do **not** ship a `watchfiles`/inotify watcher on `pending/` before #2 lands,
   or test packets trigger live consensus runs.
4. **Tailscale console edits (Architect-only):** add `tcp:8019` grant N1→N0; drop `tcp:8017`; apply the
   admin `ssh` check-mode section. Also: **Node 1 has three names** (`asus.tailnet`, `kali-n1`, `tag:asus`)
   — the L2 ceremony is 6 phases, not 2, and is blocked on a naming ruling.
5. **`stale/` disposition** — 756 test-spam + **2 REAL work orders** awaiting ruling. Do not bulk-move.
6. **C6/N0-04 OPEN.** Minisign adopted as primitive, but Carmack's ruling stands: a detached signature proves
   *a* key signed *these bytes* — it does not prove *the authorized publisher* did. Items 1/3/4 of
   `OPEN_TRANSFER_GATES.md` remain.
7. **Step 19/20** — a **rebuild**, not a migration. No MRL-truncated canonical data exists anywhere in `data/`.
8. **55 backup files** outside Ma'at's workstream; `MockFastMCP` cross-file mock pollution (26 errors only on
   co-run); Tier B flake (opaque pip output — capture stderr).
9. **9 EIS posts are on disk**; the coordination substrate still needs a durable, tool-independent path
   until the harness attaches `omega-hub` to subagents.

---

## §7 — FACET PROTOCOL (adopted 2026-09-28)

Full text: `docs/architecture/NES_EIS_FACET_PROTOCOL.md`.

- **Opening Handshake** — every NES, first turn, before any action. The pager **must** supply the owning
  EIS ID; the NES never searches for it. Requires `Verified-on-entry:` and `Not verified:` lines.
- **Closing Return** — Executed / Verified / Inferred / Failed-or-skipped / Open threads.
- **Oversoul Pulse** — before approving more work, an EIS enumerates its Facets, reads each live Facet's
  *last decision*, reconciles against the record, absorbs upward, guides downward **before** the next dispatch.
- **Freshness is a gate, not a courtesy.** Dispatching to a known-stale Facet is an M27 violation.

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ GNOSIS-SEALED ⬡ 2026-09-28 ⬡ COMPACT-READY ⬡ NODE-0-BASTION*
