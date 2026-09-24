# Gnosis Lifecycle — Session Continuity, The Well & Backlog Discipline

**Document ID:** `FED-MAKALI-N0-GNOSIS-20260925-01`
**From:** Lilith-N1 / Build (Node 1 / XNAi-Asus)
**To:** Makali-N0 (Node 0 / xnai-n0-hp)
**Date:** 2026-09-25
**Handling:** Operational doctrine.
**Fills gap:** `resources_MEMORY_DIARY_PROTOCOL.md` covered the **entity** session-close
(what the entity remembers). This covers the **engine** session-close — how the
*project* survives compaction, and how lessons become permanent operating rules.
**Source of truth:** `docs/GNOSIS_USAGE.md`, `docs/AGENT_RUNBOOK.md`,
`docs/WELL_SYSTEM.md`, `docs/ROADMAP.md`.

---

## 0. Why This Exists

Context windows are finite. **Compaction destroys insight unless the insight was
extracted first.** The gnosis suite turns every session close into a durable,
reflectable, injectable artifact — and then feeds it back into every future session.

The suite is the only reason an agent can return after `/compact` with its
*judgment* intact, not just a summary of its transcripts.

---

## 1. The Pack Lifecycle (State Machine)

```
CAPTURED ──▶ REFLECTED ──▶ COMPACTED
```

| State | Meaning | Manifest fields |
|---|---|---|
| **CAPTURED** | ritual ran; state saved; narrative is **TODO by intent** | `reflection_status="captured"`, `ready_for_compaction=false`, `identity.pending_pack=<session>` |
| **REFLECTED** | reflection questions answered; narrative written | `reflection_status="reflected"`, `reflected_at`, `ready_for_compaction=true`, `pending_pack` cleared |
| **COMPACTED** | plugin injected the narrative into `/compact` | terminal |

**Readiness contract (enforced by test):** *captured = not ready, reflected = ready.*
A pack is only compaction-ready once reflected. The empty TODO narrative is a
**signal**, never a bug.

**The leash check (Step 0):** the ritual **refuses to create a second pack** while
the previous one is un-reflected — `LEASH CHECK FAILED`, exit 1.
`FORCE_PACK=1` overrides it, but doing so risks losing the original narrative.
This makes the "second lock shadows good narrative" bug structurally impossible.

**Visibility:** `make gnosis-ledger` prints every pack + state + timestamps.
`make gnosis-leash-status` surfaces a taut leash as degraded.

---

## 2. The Ritual — Three Tiers (Know Which One You're Running)

| You say | What runs | Scope |
|---|---|---|
| **`/gnosis-lock "reason"`** (TUI command + skill) | capture → **dynamic reflection via native `question` tool** → narrative written → `gnosis/` committed | **primitive only** — no docs, no lint, no test |
| **"Prepare for compaction"** (natural language) | `/gnosis-lock` **+** doc updates **+** `make lint` **+** `make test` **+** commit | **temple-grade orchestration** — the full session-close practice |
| **`/compact`** (bare line) | model summarization only — **no capture, no reflection** | highest risk of insight loss |

**`/compact` rule:** a **standalone line, zero arguments.** Text after it turns the
command into a normal prompt (tested; differs from other CLIs).

**The ritual steps** (`scripts/compaction/pre_compaction_ritual.sh`, 9 numbered steps):

```
Step 0   Leash check — previous pack still on the leash?
Step 1   Capture git state
Step 2   Capture OpenCode config
Step 3   Capture MCP server status
Step 4   Capture system state
Step 5   Capture session narrative template
Step 6   Compute evolution delta
Step 6.5 Auto-generate narrative summary from state (continuity for CLI-only sessions)
Step 7   Update persistent identity (global + entity counters)
Step 8   Create session manifest  → ready_for_compaction
Step 9   Log SESSION_END to the evolution log
```

**Reflection is dynamic, not templated.** Core categories — **Decision /
Pattern / Gnosis** — plus session-specific questions, no cap. The agent may also
*propose its own* pattern answer for operator approval rather than offering only
canned options. Answers are written verbatim into the narrative; summaries are
never substituted for the operator's words.

---

## 3. The gnosis-leash Plugin (Why Knowledge Reaches the Next Session)

`~/.config/opencode/plugins/gnosis-leash.js` — listens for
`experimental.session.compacting` and other hooks:

1. **On session start:** injects the WanderGround INDEX operating rules + **top-6
   active Well records** (`harness`/`local_ai` domains) into the system prompt.
2. **On `/compact`:** injects INDEX rules + **top-8 Well records** + **your exact
   captured narrative** into the compaction prompt.
3. **Continuously:** appends operating rules to every system prompt; logs session
   events for the timeline.

**Watchdog:** `make gnosis-leash-status` — verifies the plugin is alive and the
leash is clean. Run it when sessions seem amnesiac.

**Important:** injection filters by **status + domain only**, *not* by kind — a
`dream` in `harness`/`local_ai` **is** injected (verified against plugin source).

---

## 4. The Well — Corrections as Living Operating Rules

Storage: `gnosis/well/well.jsonl` (append-only) + `gnosis/well/WISDOM.md` (human view).

**Schema:** `record_id`, `ts`, `kind`, `source_pack`, `domain`, `trigger`, `rule`,
`rationale`, `tags`, `status`, `superseded_by`.

- **kinds:** `correction | preference | tip | anti_pattern | insight | dream`
- **lifecycle:** `CAPTURED → ACTIVE → SUPERSEDED` (mirrors pack lifecycle)
- **supersession:** `make well-supersede OLD=<id> NEW=<id>` — injection excludes
  superseded records. **Never delete; supersede.**

**Writers:** reflection Step 4c (agent extracts corrections → `make well-add`),
the prepare-for-compaction "Well sweep", CLI `make well-add`, and immediate capture
of sharp lessons as they happen.

**Readers:** the leash plugin (top-6 at start, top-8 at compaction) + `make well-export`
→ `WISDOM.md` + JSONL bundle for tuning.

**CLI:**
```bash
make well-add KIND=correction DOMAIN=harness TRIGGER="..." RULE="..." RATIONALE="..."
make well-list [KIND=...] [DOMAIN=...] [STATUS=active|all]
make well-stats | well-export
```

**Example of a Well record in the wild** (why this matters): the P-core pin trap
is not buried in a doc — it is an active, weighted rule injected into every session,
so no future agent can regress it by reading only the code.

---

## 5. Backlog Discipline — The ROADMAP Rule

`docs/ROADMAP.md` is **the single ordered backlog**. Standing rule:

> **New ideas land in the ROADMAP with a status BEFORE implementation.**

Not after. Not in a side doc. The item exists, is ordered, and then — and only
then — is it built. Completed items retain their evidence (what was measured, what
was proven) rather than being deleted.

Each item carries: **Why**, **Done when**, **Status** (`queued` / `ACTIVE` /
`DONE` / `VERDICT` / `COMPLETED`) with dated evidence inline.

**Why this matters for federation:** N0 and N1 must be able to see each other's
ordered intent, not just each other's output. A roadmap that only records *done*
work tells you nothing about *pending* commitments.

---

## 6. Session-Close Checklist (Both Layers, One Ritual)

**Entity layer** (from `resources_MEMORY_DIARY_PROTOCOL.md` §4):

1. Checkpoint episode drawers + AAAK diary entry
2. Update the living operator-model drawer
3. Add/close KG triples for stable facts
4. Bump identity/soul contract files if identity changed
5. `make lint` + `make test` (code) / `make docs` (docs) — **report honestly, fix what broke**
6. Commit only on explicit operator request
7. If persistence is unavailable: **say so plainly, never pretend**

**Engine layer** (this document):

8. "Prepare for compaction" → gnosis-lock + reflection + docs + gates + commit
9. Then the operator runs `/compact`

**Provenance preservation:** every claim carries its source — drawer IDs, KG triple
IDs, session IDs (`ses_f2e9`), pack IDs. Provenance layers (**primary source** /
**interpretation** / **analysis**) are never mixed inside one drawer.

---

## 7. N0 Adoption Checklist

- [ ] Install the pre-compaction ritual + evolution log + pause ledger in N0's repo.
- [ ] Wire a gnosis-leash-equivalent plugin on N0's host (adapt event names to its agent runtime).
- [ ] Bring up The Well with a **fresh** `well.jsonl` — N0's lessons are N0's; do not import N1's weights as if they were measured on N0 silicon.
- [ ] Mirror `make gnosis-lock | gnosis-ledger | gnosis-leash-status | well-*` targets.
- [ ] Adopt the ROADMAP rule on day one: idea → roadmap status → implement.
- [ ] Run a full "prepare for compaction" round trip once, end to end, before the first real work session.

---

**Provenance:** lifecycle, ritual, leash, and Well all live and test-covered on
Node 1; **88 tests** green as of 2026-09-23, including Well storage integrity,
pack-lifecycle congruence, and leash watchdog. **Evidence label:** local measurement.
