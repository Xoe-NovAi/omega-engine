# PARALLEL AGENT FLEET ARCHITECTURE — doctrine for the Omega Engine

**Date**: 2026-09-26
**Origin**: Architect directive (`/home/xnai/omega-exchange/n1-to-n0/git-and-parallel-links-to-research.md`)
**Method**: Parallel multi-query search + official-docs fetch; provenance tagged [O] official, [P] practitioner, [M] measured on Node 1.

---

## 0. Why this matters *now* — the pain is measured, not hypothetical

Node 1 already runs **multiple concurrent Lilith/Humboldt/build sessions against one
working tree**. Symptoms observed tonight, unprompted:

- `git checkout fa9c4edc` **aborted** because a sibling session's uncommitted changes would be overwritten.
- ROADMAP required **surgical hunk staging** to avoid committing another session's `P4.5a` edit.
- Two stashes in flight; branch-switch thrash to complete a WAD alignment.
- A `lint`/`test` red that was **another session's** untracked instrument.

Every one of these is the textbook failure the worktree pattern exists to eliminate. This is not
adoption for its own sake — it is a fix for a live, recurring, self-inflicted wound.

---

## 1. Git worktrees — the filesystem isolation boundary

**Core mechanism** [O/P]: one `.git` object store, N working directories, each on its own branch.
O(1) disk for the history; no duplicate clones; fetches propagate everywhere.

**Worktree-per-task** — the dominant pattern [P]:
```bash
git worktree add ../feature-auth -b feature/auth
git worktree add ../add-tests    -b test/coverage
git worktree add ../pr-review    pr/456
```

**The three-phase sweep** [P] — *this is the highest-value pattern for us, and it is what I
already did tonight with read-only research subagents*:
1. **Discovery** — run several **read-only** subagents in parallel, one per concern. They only
   read, so they may all point at the main tree with zero risk.
2. **Apply** — fold findings into one plan, execute in an isolated worktree. **One writer, one
   branch, one contained blast radius.**
3. **Review** — diff the branch in isolation before merging. The worktree makes this free.

**Ephemeral discipline** [P]: remove on merge (`git worktree remove` + `git branch -d`), `git
worktree prune` periodically. Treat worktrees as create-use-destroy.

**Gotchas** [P]:
- `git worktree add` **refuses** a branch already checked out elsewhere — deliberate, prevents two
  trees fighting over one HEAD. Give every worktree its own branch.
- Lockfile conflicts are real (shared `package.json`, per-worktree `node_modules`).
- **Pre-warmed pool** [P]: fixed worktree slots with deps pre-installed, rotate branches through
  them. Cuts activation from ~10 min to ~5 s. Directly relevant: our `.venv` is expensive.

**The prerequisite nobody skips** [P]: *spec-driven task decomposition*. Worktrees stop **file-level**
collisions only. Two agents both told "improve the checkout flow" still collide semantically.
Decomposition quality decides whether parallelism is real or merely deferred merge pain.

**Context delivery** [P, ICSE 2026]: architectural documentation in agent context produces
*measurable* gains in functional correctness, architectural conformance, and modularity — this is
the delivery mechanism for our `AGENTS.md`. Treat it as infrastructure, not boilerplate.

**Ceiling** [P]: **5–7 concurrent agents** on a modern laptop; disk math ~5 GB/worktree on a 2 GB
codebase; then rate limits and review overhead eat the gain. **Start with 2–3, measure, scale on
evidence.** Node 1 has 76 GB free — real but finite.

**Drift control** [P]: agents over-refactor. Use per-file diff navigation, and treat **any change
touching files outside the declared task scope as an automatic review escalation.**

---

## 2. Runtime isolation — what worktrees do NOT solve

> "The isolation boundary is exactly as wide as the filesystem checkout, and no wider." [P]

| Shared resource | Mitigation |
|---|---|
| **Ports** | per-worktree port offsets / dynamic allocation; per-worktree env file |
| **Databases** | separate database *names* per worktree, or a schema factory |
| **.env / secrets** | per-worktree `.env.local`, gitignored; committed `.env` is a cross-agent leak |
| **Docker daemon** | shared; problematic when agents edit Dockerfiles in parallel |
| **Package caches** | shared read cache is fine; `node_modules` isolated by default |
| **Build cache** | absolute-path caches collide — namespace or share deliberately |

Tooling: `worktree-env` auto-allocates unique ports + emits per-worktree vars to `.envrc` for
direnv integration [P].

### SQLite specifics (our substrate) [O: sqlite.org/isolation.html]
- Transactions are **SERIALIZABLE** — writes are actually serialized; **one writer at a time**.
- **WAL mode** gives readers *snapshot* isolation; readers never see uncommitted writes.
- **Separate database FILES = complete isolation.** This is the load-bearing fact for us.
- `PRAGMA read_uncommitted` is the *only* way one connection sees another's uncommitted changes —
  never enable it in a fleet.
- **No isolation between operations on the same connection** — undefined behaviour if you assume
  otherwise inside a single connection.

**Recommended Omega pattern** [P, corroborated by Hive and HelperX architectures]: **one database
file per agent/worktree, living inside that worktree's own directory.** Do *not* share one
MemPalace/coordination DB across concurrent agents. Multi-tenant guidance for SQLite is explicit
that **one file per tenant beats row-level isolation** — isolation you can point at is worth more
than a clever `tenant_id` column.

---

## 3. Multi-node orchestration (N0 ↔ N1 and beyond)

**GitOps is the sober pattern** [P]: a central Git repo declares authoritative state; a small
sync daemon on each host reconciles. For two personal machines this is lighter and more auditable
than Kubernetes anything.

**Configuration hierarchy** [P]:
```
global defaults  →  fleet/node defaults  →  instance overrides
```
The hard constraint: **instance overrides must live in version control.** An untracked override is
indistinguishable from drift — that sentence is the whole config-management discipline in one line.

**Emerging standards** [P]: **MCP** (Anthropic) for tool interop; **A2A** (Google, now under Linux
Foundation governance) for agent discovery/communication; **OpenTelemetry GenAI semantic
conventions** for observability. Patterns adopted now map cleanly as these mature.

**Identity is the unsolved part** [P]: machine identities outnumber humans; each agent needs its
own keys and scopes. The named failure mode is **secret sprawl** — hardcoded credentials that
cannot be rotated, giving any single compromise a fleet-wide blast radius. Direction of travel is
**workload identity attestation** / zero static secrets. *We are not there yet; treat per-agent
credentials as a known open risk, not a solved problem.*

**Session continuity pattern worth stealing** [P]: an *initializer* agent establishes environment
state, a *coding* agent makes incremental progress per session, and a persistent per-agent
`memory` directory survives conversation boundaries so **any instance can resume another's work**.
This maps directly onto our gnosis/soul-continuity doctrine.

---

## 4. Paperclip — what it is, and an honest Omega fit

**What it is** [O]: `github.com/paperclipai/paperclip` — appeared March 2026, **74,000+ stars in
five months**, 100+ contributors, **MIT licensed**, self-hosted, no account required. Node 20+/24.11+,
pnpm, embedded PostgreSQL (or your own), API on `:3100`. Explicitly **not** a chatbot, **not** an
agent framework, **not** a workflow builder, **not** a prompt manager, **not** a single-agent tool.
It is a **management layer above agents that already exist**.

**Its model** [O]:
- **Org chart** — hierarchies, roles, reporting lines; agents have a boss, title, job description.
- **Tickets** — every conversation traced; **immutable audit log**; full tool-call tracing.
- **Budgets** — monthly per agent with a hard stop. "Runaway loops waste hundreds of dollars before
  you know what happened."
- **Heartbeats** — agents wake on schedule or on events (assignment, @-mention); delegation flows
  up and down the chart.
- **Governance** — approve hires, override strategy, reassign, pause or terminate any agent.
- **Multi-company** — one deployment, many orgs, complete data isolation.
- **Tailscale-friendly** — solo-operator access over a tailnet is an explicit use case.

**Its design stance, which is the important part** [O]: *"Paperclip's design assumes agents must be
governed, not trusted."* Scope permissions, cap budgets, gate consequential actions behind
approval. And — critically — **a Paperclip company always has a human at the top: you act as the
board.** It is not a self-running company; in 2026 it works best as a **supervised team**.

**Telemetry** [O]: anonymous usage telemetry only; explicitly **no** personal information, issue
content, prompts, file paths, or secrets. Private repo references are hashed with a per-install
salt. *M8 Zero Telemetry is absolute for us — this passes the letter, but the safe reading is to
disable it at the source rather than trust a policy page.*

**Comparables** [P]: CrewAI Enterprise (strongest OSS-rooted coordination; fleet visibility is
crew-level not fleet-level; audit trail lacks structured governance metadata), Dify, n8n, Langflow,
Agent Zero. None matches Paperclip's org-chart-plus-budget-plus-audit combination.

### Fit for the Omega Engine — the honest read

**What genuinely aligns:** we have *already hand-built* the thing Paperclip productizes. Our
`hierarchy.yaml` is an org chart (Sophia = containing field → Kali = unification → Ma'at = light
oversoul / Lilith = dark oversoul → 10 pillar keepers). Our mandates already encode budgets
(M10 fleet ceiling ≤14 agents without architectural review), governance (C6/N0-04, the Architect
veto pattern), and audit (gnosis packs, evolution log, immutable SHA ledgers). Paperclip's
"governed, not trusted" is our M23 restated.

**What does NOT align:**
1. **It is multi-tenant SaaS-shaped.** Embedded Postgres, org/budget/goal model, and a UI built for
   a company with headcount. Our Engine is a *sovereignty substrate* with one operator.
2. **Node 24.11+ / pnpm / Postgres** is a real operational footprint on a 16 GB CPU-only box that
   already runs Ollama, MemPalace, and a 66-tool MCP hub.
3. **Duplicate governance surface.** Adopting it would create a second source of truth for org
   structure against our `hierarchy.yaml` and mandates — precisely the "two spaces" hazard we
   recorded in the palace work.
4. **Telemetry exists at all.** M8 is absolute for us.

**Verdict**: **do not adopt. Do mine.** The valuable, portable ideas are four and they are free:
(1) *budgets with hard stops* per agent; (2) *immutable audit log of every tool call*;
(3) *heartbeats as the trigger mechanism* rather than manual invocation; (4) *goal alignment — every
task traces to a mission*, so an agent always knows **what and why**. Items 1–2 we largely have;
items 3–4 are genuine gaps worth closing in our own substrate.

---

## 5. Recommended sequence for Node 1 (proposal, not yet authorized)

1. **Worktree-per-task for this repo**, branches named `agent/<entity>-<task>`, ephemeral, pruned.
   Start at **2 concurrent** — measure before scaling.
2. **Per-worktree `.env.local`** carrying: unique port, **its own SQLite paths** (MemPalace
   instance, coordination DB, test DBs), its own cache dir. Never share a DB file across agents.
3. **TASKS.md at repo root**, agent-readable, declaring scope and **off-limits files**; any diff
   outside declared scope = automatic escalation.
4. **Three-phase discipline** for every sweep: parallel read-only discovery → single-writer apply
   in a worktree → isolated review before merge.
5. **Adopt Paperclip's four ideas natively** — hard budgets, immutable tool-call audit, heartbeat
   triggers, goal-traced tasks — inside our own substrate, not as a dependency.
6. **Multi-node**: Git repo as declared state + a small per-host sync daemon. Keep the physical
   exchange pipe and MCP as the coordination transport; do not reintroduce SSH/NFS (policy-removed).

---

## 6. Sources

- Tailscale Serve reference + examples + feature docs (official) — file/directory vs proxy targets, port rules, localhost-binding guidance
- pypa/pip#11067 — editable installs and console scripts
- sqlite.org/isolation.html — serializable transactions, WAL snapshot isolation, per-file isolation
- github.com/paperclipai/paperclip + paperclip.ing + paperclip.inc blog — model, features, telemetry, 2026 supervised-team caveat
- codeongrass, mindstudio, htek.dev, konadu.dev, appxlab — worktree patterns, runtime isolation, pre-warm pool, 5–7 ceiling, three-phase sweep
- zylos.ai fleet management 2026, knowlee.ai fleet guide — GitOps, config drift, secret sprawl, A2A/MCP/OpenTelemetry
- Neon branching guide, DanWahlin/ai-agent-board, iurimadeira/worktree-env — DB/port isolation tooling
