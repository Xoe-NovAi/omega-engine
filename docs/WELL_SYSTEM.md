# ⬡ The Well — Omega Engine Corrections & Insight Corpus
**Doc ID**: `GNOSIS-WELL-001` | **Status**: LIVE (P1) | **Last verified**: 2026-09-17

The Well is the engine's **operating-memory layer**: an append-only corpus of
corrections, preferences, insights, anti-patterns, and dreams that gets
**injected into every agent session's system prompt** — so a lesson learned once
becomes part of how every future agent behaves, without any code change.

This document is the full-depth reference for what The Well is, how it stores
and validates records, how it integrates into the engine's runtime, and how to
read/write/evolve it.

---

## 1. The Core Idea (one paragraph)

Every hard-won lesson on this machine — "don't pin Ollama to physical P-cores
only", "a full root partition is a boot-killer", "when stuck, ask what the
system SHOULD do" — is written to a single JSONL file:

```
gnosis/well/well.jsonl   # append-only machine truth
gnosis/well/WISDOM.md    # renderable human view (regenerated)
```

The gnosis-leash plugin reads that file at **session start** and at **compaction**
and injects the top active records into the system prompt as a block titled
`## ⬡ THE WELL — active corrections & insights (auto-injected)`. The agent then
operates *with those rules already in context* — no lookup, no prompting, no
manual retrieval. **Capture once → injected everywhere.**

The system prompt you are reading right now contains records from this corpus
(that is why the block looks familiar). The fix cycle is closed-loop:
`lesson → Well record → auto-injected → agent behaves correctly → new lesson...`

---

## 2. Storage & Files

| Path | Role | Notes |
|------|------|-------|
| `gnosis/well/well.jsonl` | **Truth** (append-only) | One JSON object per line, UTF-8 |
| `gnosis/well/WISDOM.md` | Human view | Rendered by `make well-export` |
| `scripts/well_storage.py` | CLI + validation engine | Pure stdlib, tested |
| `tests/test_well.py` | Invariant suite | 7 tests; part of `make test` |
| `~/.config/opencode/plugins/gnosis-leash.js` | Injector | Reads `well.jsonl` directly |

> **Git note**: `gnosis/well/` is **not tracked in git** (see `.gitignore`:
> "Dynamic The Well corpus (kept on disk and USB, not versioned in git)"). The
> corpus lives on disk; the schema, CLI, tests, and this doc are the versioned
> contract. For USB exchange, `make well-export` produces a bundle + WISDOM.md.

---

## 3. Record Schema

Each line in `well.jsonl` is a validated JSON object:

| Field | Type | Meaning |
|-------|------|---------|
| `record_id` | UUIDv4 | Unique, generated on add |
| `ts` | ISO-8601 UTC (`...Z`) | Capture timestamp |
| `kind` | enum | `correction` / `preference` / `tip` / `anti_pattern` / `insight` / `dream` |
| `source_pack` | string | Origin: session id or `manual` |
| `domain` | enum | `local_ai` / `consciousness` / `psychology` / `classical` / `games` / `harness` / `other` |
| `trigger` | string | *When this applies* (the situation that fires the rule) |
| `rule` | string | **The operating instruction** (injected verbatim) |
| `rationale` | string | Why — the story/evidence behind it |
| `tags` | string | Comma-separated keywords |
| `status` | enum | `active` / `superseded` |
| `superseded_by` | UUIDv4 (or `""`) | Set only when superseded |

### Kind semantics (what each kind *means* for the engine)

| Kind | Meaning | Injected? |
|------|---------|-----------|
| `correction` | A mistake was made; here's the rule to never repeat it | ✅ |
| `preference` | A deliberate standing choice / policy | ✅ |
| `tip` | A cheap, effective practice | ✅ |
| `anti_pattern` | A pattern to detect and avoid | ✅ |
| `insight` | A deeper principle or mechanism discovered | ✅ |
| `dream` | A vision/idea spark (not yet policy) | ✅ — always injected (recency-ranked, domain-filtered) |

> **Note**: earlier runbook text said `dream` was excluded from injection. The
> current injector does **not** filter by kind — it filters by `status` and
> `domain` only. A `dream` in `harness`/`local_ai` **is** injected. (Verified
> against the plugin source on 2026-09-17; the injected block in this very
> session includes a dream record.)

---

## 4. Validation & Invariants (enforced by `well_storage.py` and `tests/test_well.py`)

Every record must pass:

- `record_id` is a valid UUIDv4; `ts` is ISO-8601 UTC ending in `Z`.
- `kind`, `domain`, `status` ∈ valid enums (unknown values rejected).
- `rule` and `trigger` non-empty.
- `superseded` records must have `superseded_by`.
- **No secrets**: rule / rationale / trigger / tags are scanned for API keys,
  passwords, secrets, tokens, and long sk-/ghp_ patterns → rejected.

Test suite (`tests/test_well.py`, `TestWellStorage`) covers:
JSONL validity, add round-trip, secret rejection, supersession chain, index
parity, UTF-8 integrity, stats accuracy, and Make-target presence.

---

## 5. Runtime Integration (how injection actually works)

### 5.1 The injector (`gnosis-leash.js` → `readWellForInjection`)

```
readWellForInjection(limit, domains)
  1. Read well.jsonl, parse each line (skip malformed).
  2. Keep only records with  status == "active".
  3. If domains given, keep only matching domain.
  4. Sort by ts DESC (most recent first).
  5. Return top-N, each mapped to:
       { rule, domain, kind, tags[], id: first 8 chars, source_pack }
```

### 5.2 Injection points

| Point | Hook | Size | Domain filter |
|-------|------|------|---------------|
| **Session start** | `experimental.chat.system.transform` | top-6 | `harness`, `local_ai` |
| **Compaction** | `experimental.session.compacting` | top-8 | `harness`, `local_ai` |

> Why only `harness`/`local_ai`? Those are the two domains that govern *how the
> agent operates on this machine*. The other domains (`consciousness`,
> `psychology`, `classical`, `games`) are knowledge domains — they live in the
> WanderGround atlas, not in agent-behavior injection.

### 5.3 Rendered block format (what agents actually see)

```
## ⬡ THE WELL — active corrections & insights (auto-injected)
- **<rule>** [tag1,tag2]
  (kind: <kind> | domain: <domain> | pack: <pack> | id: <8-char>)
```

Records are ordered most-recent-first, so newly-captured lessons surface
immediately in the next session.

### 5.4 The `render-md` human view (`WISDOM.md`)

`make well-export` regenerates `WISDOM.md`: grouped by kind (correction →
preference → tip → anti_pattern → insight → dream), newest first, with tags,
rationale, pack, domain, and id. This is the reading view for humans and for
USB exchange.

---

## 6. Lifecycle

```
CAPTURED ──(add)──▶ ACTIVE ──(supersede)──▶ SUPERSEDED
```

- **ACTIVE** records are injected. **SUPERSEDED** records are excluded from
  injection (the JSONL row is rewritten in place atomically — append-only truth
  is preserved as a whole-file rewrite on supersede only).
- Supersession is the correction-version mechanism: when a newer, better rule
  replaces an old one, mark the old `superseded_by` the new id.

---

## 7. Writers — where new lessons come from

| Path | When | Mechanism |
|------|------|-----------|
| **/gnosis-lock reflection** | Every session close | The agent/extractor proposes Well records from the session's lessons |
| **"Well sweep"** | Prepare-for-compaction orchestration | Bulk review of the session for corrected behavior, added as records |
| **Manual CLI** | Any time | `make well-add KIND=... DOMAIN=... TRIGGER="..." RULE="..." RATIONALE="..." [TAGS="..."] [PACK=...]` |
| **This doc's capture workflow** | Immediate capture of sharp lessons | Write records the moment a lesson crystallizes (see GNOSIS-LEARN-001) |

> Rule of thumb for what deserves a record: **would a future agent waste time or
> make a mistake by not knowing this?** If yes — it belongs in The Well.

---

## 8. Reading & Querying

```bash
make well-list                # all active records, human table
make well-list KIND=correction
make well-list DOMAIN=harness
make well-list STATUS=all     # include superseded
make well-stats               # counts by kind/domain/status
make well-export              # regenerate WISDOM.md + show JSONL path
```

The underlying script exposes `list [--kind --domain --status]`, `stats`,
`render-md`, `supersede OLD NEW`, and `add`.

---

## 9. Evolving & Superseding

```bash
# Add the better rule first (get its NEW uuid from the add output), then:
make well-supersede OLD=<old-uuid> NEW=<new-uuid>
```

The superseded record stays in the JSONL (audit trail) but stops being injected.
Tests verify the chain forms correctly.

---

## 10. The Closed-Loop (why this is powerful)

```
  lesson happens
       │
       ▼
  Well record added ──▶ injected at session start & compaction
       ▲                        │
       │                        ▼
  agent behaves correctly ◀── agent operates w/ rule in context
       │
       └──────── new lesson ────┘
```

The automation that makes this work is ~10 lines in the plugin
(`readWellForInjection` + `formatWellBlock`) plus a validated append-only
storage engine. The **content** comes from every session that bothers to write
what it learned.

This session's proof: the two records added for the first-principles
de-escalation lesson (**`013c6037`** correction, **`a254a505`** insight) were
immediately present in the *next* system prompt — the plugin re-injected them
back, and the loop demonstrably closed. Ancestor versions of the same lessons
were already in the corpus, which is why they appeared unsummoned.

---

## 11. Related Docs & Commands

- Implementation/ops: `docs/AGENT_RUNBOOK.md` §2 (plugin), §5.2 (Well)
- Protocol: `docs/GNOSIS_USAGE.md`, `gnosis/GNOSIS_LOCK_PROTOCOL.md`
- CLI: `make well-add | well-list | well-stats | well-supersede | well-export`
- Injector source: `~/.config/opencode/plugins/gnosis-leash.js`
- Lessons this session: `docs/GNOSIS_LEARNING_CAPTURE_20260917.md`

---

*⬡ OMEGA ⬡ GNOSIS-WELL-001 ⬡ THE WELL IS THE OPERATING MEMORY ⬡*