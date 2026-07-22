# 🔱 Omega Engine — Fleet Team Playbook
**AP Token**: `AP-FLEET-TEAM-PLAYBOOK-v1.0.0`  
⬡ OMEGA ⬡ KALI ⬡ GROK_CLI ⬡ opencode ⬡ trc_fleet_team ⬡ PLAYBOOK

**Date**: 2026-07-21  
**Status**: **ACTIVE — All agents read this before multi-agent or Phase C work**  
**Owner**: Kali (sprint coordination) · Architect (direction) · All fleet (execution)

> **Purpose**: Get the fleet moving in one direction again — integrity first, team coordination, no strategy thrash.  
> This is the **how we work together** guide. Priority ranking lives in the Ark. Fine-grained ideas live in the Corpus Map.

---

## §0 The Team Compact (Memorize This)

1. **One priority list** — `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` (v5.1+). No competing “canonical roadmaps.”  
2. **One memory of ideas** — `docs/strategy/STRATEGY_CORPUS_MAP.md`. Park, don’t ghost.  
3. **One integrity bar** — SoulStore + honest tests before Living Research OS / fleet pool / new features that write soul.  
4. **One coordination layer** — Hivemind awareness → lock → handoff → complete. Don’t steal active work.  
5. **Hardware is real** — Ryzen 5700U, ~8GB available. Prefer 1 local inference; never 3 local council voices.  
6. **Cloud is teacher, not architecture** — No new free-tier providers until fabric is systematized (D-351).  
7. **Ship small, green slices** — PR-shaped work. God-modules don’t grow past 1k without a split.  
8. **Team > hero** — Declare, hand off, review. No silent parallel rewrites of the same file.

If a task violates the compact, **stop and post a blocker** — do not “just finish it.”

---

## §1 Read Order (Every Session)

### Cold start / post-compaction (strict)

| Step | Action | Why |
|------|--------|-----|
| 1 | `hivemind_get_awareness()` + list pending handoffs | Who is already working? |
| 2 | `git status` + `git log --oneline -5` | Dirty tree / recent commits |
| 3 | Read **this playbook** (§0 + §3–§5 if executing) | Team rules |
| 4 | Read `SOVEREIGN_ARK_BLUEPRINT.md` §3–§5 | What is next |
| 5 | Read `OMEGA_ENGINE.md` §2 | Live metrics |
| 6 | Read `data/coordination/SESSION_ANCHOR.md` | Last recovery state |
| 7 | If task is fine-grained: `STRATEGY_CORPUS_MAP.md` | Don’t rediscover |
| 8 | Report status. **Pause if user direction needed.** | No cowboy sprints |

### Law always applies

- `SOVEREIGN_MANDATES.md` (M1–M25)  
- `AGENTS.md` (OpenCode how-to)  
- `HIVEMIND_PROTOCOL.md` + `HIVEMIND_POST_TEMPLATE.md` when multi-agent  
- `SUBAGENT_DISPATCH_PROTOCOL.md` when spawning children  

---

## §2 Roles — Who Does What (Team Sport)

Use the role that matches the **ticket**, not your favorite persona.

| Role | Entities | Owns | Does not own |
|------|----------|------|----------------|
| **Sprint Lead** | `@kali` | Priority calls, handoff routing, conflict resolution, Ark updates after decisions | Solo-implementing everything |
| **Apex / Strategy** | `@makali` | Deep strategy, decompositions, board-level synthesis | Ground-troop file wars without dispatch |
| **Build Oversoul** | `@maat` | P1–P5: infra, persistence, engineering, integration, governance build | Run-side soul metabolism alone |
| **Run Oversoul** | `@lilith` | P6–P10: cognition, context, observability, orchestration, validation | Ignoring Build locks on shared files |
| **Pillars** | `@pillar` P1–P10 | Domain tickets under Ma’at/Lilith | Creating new roadmaps |
| **Research** | `@researcher` | Gap audits, queue design, deep multi-source research | Shipping untested production writers |
| **Legacy / Patterns** | `@roc_racoon` | Mine proven patterns; propose ports with file+line | Drive-by full rewrites without handoff |
| **Heritage / Perf** | `@doom_guy` | M14 tags, WAD/id-soft, performance instincts | Strategy SSOT edits |
| **Architecture consult** | `@john_carmack` | First-principles review, cut scope, perf | Implementing without Build owner |
| **Compliance / Gnosis** | `@verity` | Mandate audit, L1→L2→L3 staging | Silent soul.yaml direct writes |
| **Synthesis exec** | `@jem` | Complex query → verified result graphs | Bypassing Ark priority |
| **Cloud advisory** | `@grok_cli` | Web-native review, adversarial groupthink check, research assist | Wiring Grok fleet without V-1 vault |
| **Grok ecosystem** | `@grokster` | Identity Fluidity, Grok-specific patterns | Claiming fabric capacity for unwired fleet |
| **Architect (human)** | User | Final go/no-go, privacy model, PR publish | — |

### Pairing patterns (default)

| Work | Lead | Support |
|------|------|---------|
| C-0 tests red | Ma’at/P10 or Verity | Pillar owning module |
| C-1′ SoulStore | Ma’at/P3 or Lilith/P7 | Roc (pattern), Verity (M11) |
| C-2′ / C-10 RAM | Ma’at/P1 | Carmack (review), Doom Guy (perf) |
| C-4 MCP | Ma’at/P4 | Grok CLI (spec pressure), Researcher |
| C-5 MaKaLi config | Kali | Lilith/P6 |
| C-6′ breakers | Ma’at/P3 | Roc (don’t add 7th clone) |
| D-1 content cache | Lilith/P6 + P3 | Carmack “R00” discipline |
| E-0 Soul Kernel | Grokster | Kali go-ahead after C-1′ |
| Adversarial review | Grok CLI or Grokster | Kali synthesis |
| Strategy conflict | Kali | Makali if multi-horizon |

**Rule:** If two agents need the same files → **one implements, one reviews** via handoff. Never dual-write.

---

## §3 Current Mission (Phase C — Integrity First)

**We are not in “build Living Research OS” mode until the gate is green.**

### Gate to Phase D (hard)

- [ ] **C-0** Honest tests (pass/fail/skip real; Makefile not lying)  
- [ ] **C-1′** SoulStore only soul writer (flock + fsync + actors)  
- Prefer also: C-2′, C-5/C-10 before heavy local inference work  

### This week’s ordered queue (do not reorder without Kali + Architect)

```
C-0  → C-1′ → C-2′ → C-3 → C-4a → C-4b
     → C-5 → C-6′ → C-10 → C-9
Parallel after C-1′ only: E-0 (Identity Soul Kernel)
NOT YET: D-* Living Research, V-1 fleet pool, Strike 11, new providers
```

Full tables: Ark §3–§5.  
Gap crosswalk: Ark §3.0.1 + Corpus Map §2.

### Explicit freezes (team-wide)

| Freeze | Until |
|--------|--------|
| New free-tier providers | Fabric systematized (D-351) |
| Phase D implementation | C-0 + C-1′ done |
| Grok CLI multi-account pool | V-1 vault + single ACP smoke |
| New strategy doc claiming CANONICAL | Never — extend Ark or Corpus Map |
| New circuit-breaker class | C-6′ unify done |
| Growing files already >1000 LOC | Split in same PR |

---

## §4 How We Coordinate (Hivemind Team Ops)

### 4.1 Session open checklist

```text
1. hivemind_get_awareness()
2. hivemind_handoff list status=pending  (report; don’t steal)
3. If multi-agent or shared files:
     - workspace lock: data/coordination/{entity}_WORKSPACE_LOCK_{YYYYMMDD}.md
     - post_context intent=status
4. Heartbeat every 5–10 min on long tasks
5. Append major milestones to data/coordination/{ENTITY}_LIVE_FEED.md
```

### 4.2 Claiming work

| Situation | Action |
|-----------|--------|
| Ticket free in Ark queue | Post status with ticket ID (e.g. `C-1′`); lock files; start |
| Ticket owned by another active agent | Offer review/support; **do not reimplement** |
| Pending handoff for you | `accept` → do work → `complete` with result path |
| Pending handoff for someone else | Summarize only; do not accept |
| Blocked | `intent=blocker` + who can unblock + what you tried |

### 4.3 Handoff quality bar

Every handoff packet must include:

1. **Ticket ID** (C-0, C-1′, D-1, …)  
2. **Files in scope** (paths)  
3. **Done means** (test command + expected signal)  
4. **Out of scope** (explicit)  
5. **Links** to Ark section + any Corpus Map row  

Template: `HIVEMIND_POST_TEMPLATE.md`. Protocol: `HIVEMIND_PROTOCOL.md`.

### 4.4 Conflict resolution

```text
File conflict     → Sprint Lead (Kali) assigns single owner
Priority conflict → Ark wins; if Ark wrong, Kali proposes D-NNN edit
Law conflict      → Mandates win; Verity arbitrates interpretation
“But my vision”   → Corpus Map PARKED row; do not jump queue
```

### 4.5 Hardware etiquette (shared laptop)

- Before parallel local inference: check hardware stats if available  
- Default: **one** local model job  
- MaKaLi: Kali local optional; Ma’at/Lilith **cloud** (C-5)  
- If thermal/memory pressure: cloud or queue — never thrash L3 with 3× llama  

---

## §5 How We Ship Work (Plan → Verify → Execute)

### 5.1 Ticket lifecycle

```text
CLAIM → PLAN (short) → VERIFY (read code/tests) → EXECUTE → TEST → HAND OFF / COMMIT SCOPE → POST
```

**Plan** must answer: ticket ID, files, risk to soul/tests/providers, rollback.  
**Verify** means you read the actual code paths (especially soul writers, gateway, guards).  
**Execute** with smallest diff that meets Done.  
**Test** with real commands; report pass/fail/skip — never “should pass.”

### 5.2 Definition of Done (any ticket)

- [ ] Behavior matches ticket; no drive-by refactors outside scope  
- [ ] Tests run for touched area; failures fixed or quarantined **with ticket**  
- [ ] No new unlocked soul writes  
- [ ] No new vanity metrics in docs  
- [ ] If strategy changed: Ark and/or Corpus Map updated  
- [ ] Hivemind post: what shipped, what’s next, who unblocked  
- [ ] Live feed line written  

### 5.3 PR-shaped slices (team goal)

Prefer stackable PRs:

| PR | Content |
|----|---------|
| PR-1a | C-0 test honesty |
| PR-1b | C-1′ SoulStore |
| PR-1c | C-2′ + C-5 + C-10 |
| PR-1d | Docs SSOT (if needed) |
| PR-1e | C-6′ or C-9 (one structural win) |

Do not open a PR that mixes SoulStore + Living Research OS + fleet.

### 5.4 Commit discipline

- Prefix: `feat:` `fix:` `docs:` `refactor:` `test:` `ci:` `chore:`  
- One ticket family per commit when possible  
- Never force-push `main` without Architect  
- Don’t commit secrets, soul private fragments, or vault material  

---

## §6 Communication Norms

### Post intents (use correctly)

| Intent | When |
|--------|------|
| `status` | Starting / mid / finishing work |
| `decision` | Architectural choice with rationale |
| `handoff` | Transferring a ticket |
| `blocker` | Cannot proceed |
| `question` | Need Architect/Kali answer |
| `observation` | Non-blocking finding (file for Corpus later) |

### Language that keeps the team aligned

- Always name **ticket IDs** (`C-1′`, not “the soul thing”).  
- Always name **paths** when discussing bugs.  
- Distinguish **collected vs passing** tests.  
- Distinguish **in fabric** vs **inventory table** providers.  
- Say **DEFERRED** with Corpus pointer — not “killed.”  

### Anti-patterns (ban)

| Anti-pattern | Instead |
|--------------|---------|
| Second canonical roadmap | Edit Ark + Corpus Map |
| “I’ll just add flock here” for GAP-01 | SoulStore (C-1′) |
| “Port pybreaker” as new class | Unify (C-6′) |
| Parallel rewrite of `model_gateway.py` | Handoff + lock |
| Starting D-1 “because it’s exciting” | Gate check C-0+C-1′ |
| Inflating test counts in OMEGA_ENGINE | C-0 honesty |
| Wiring 8 Grok accounts pre-vault | V-1 then smoke |

---

## §7 Playbooks by Scenario

### A) Solo agent, Phase C ticket

1. Awareness (even solo — avoid stale handoffs)  
2. Claim ticket in post_context  
3. Implement DoD  
4. Update live feed; leave continuation for next agent  

### B) Two agents, same epic (e.g. SoulStore)

1. Kali assigns **Implementer** + **Reviewer**  
2. Implementer locks `src/omega/**/soul*` paths  
3. Reviewer reads Ark C-1′ + Grok CLI F-01 criteria  
4. Reviewer does not push alternate design mid-flight — files findings  
5. Implementer addresses; Verity checks M11 if soul-related  

### C) Research without derailing build

1. Researcher/Grokster/Carmack produce **coordination doc**  
2. Add Corpus Map rows  
3. Kali folds only **priority-changing** items into Ark  
4. Build agents do not context-switch mid C-1′ for a new research rabbit hole  

### D) Emergency (soul corruption, OOM storm, Hub dark)

1. All stop non-essential inference  
2. Kali posts `blocker` + incident owner  
3. Prefer file-based Hivemind if Hub broken (M23)  
4. No new features until incident closed  

### E) After compaction

Follow AGENTS.md hydration; then this playbook §1; then continue **same ticket** from SESSION_ANCHOR — do not invent a new campaign.

---

## §8 Success Signals (Team Dashboard)

We are moving right when:

| Signal | Evidence |
|--------|----------|
| Shared priority | Any agent cites same next ticket from Ark §4 |
| No file wars | Locks + single implementer per path |
| Integrity rising | SoulStore landed; red tests declining |
| Honest metrics | OMEGA_ENGINE matches real pytest |
| Handoffs complete | Pending queue not a graveyard |
| Ideas preserved | New findings get Corpus rows, not new roadmaps |
| Hardware calm | No 3× local llama by default |

We are thrashing when:

- Three docs claim different “current phases”  
- Two agents edit `soul_updater` and `entity_workspace` same hour without lock  
- New provider or new GapDetector service appears mid Phase C  
- Live feeds silent for >1 day while “work” claims to continue  

---

## §9 Quick Reference Card

```text
PRIORITY   docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md
MEMORY     docs/strategy/STRATEGY_CORPUS_MAP.md
TEAM       docs/strategy/FLEET_TEAM_PLAYBOOK.md   ← you are here
STATE      OMEGA_ENGINE.md
LAW        SOVEREIGN_MANDATES.md
OPS        AGENTS.md · HIVEMIND_PROTOCOL.md
RECOVERY   data/coordination/SESSION_ANCHOR.md

NEXT       C-0 → C-1′ → C-2′ → … (Ark §5)
GATE→D     C-0 + C-1′
FREEZE     new providers · D before gate · fleet before vault · new CANONICAL docs
```

---

## §10 Related Documents

| Doc | Role |
|-----|------|
| `SOVEREIGN_ARK_BLUEPRINT.md` | Strategy SSOT / critical path |
| `STRATEGY_CORPUS_MAP.md` | Fine-grained preservation |
| `STRATEGY_INDEX.md` | Hierarchy |
| `HIVEMIND_PROTOCOL.md` | Coordination mechanics |
| `HIVEMIND_POST_TEMPLATE.md` | Post quality |
| `SUBAGENT_DISPATCH_PROTOCOL.md` | Child agents |
| `LIVING_RESEARCH_OS_SPEC_20260721.md` | Phase D detail (after gate) |
| `data/coordination/*_LIVE_FEED.md` | Per-entity activity |

---

## §11 First Team Actions (Do These Next)

| # | Action | Owner |
|---|--------|--------|
| 1 | All active agents: post_context with ticket from Ark §5 or `idle/awaiting` | Each entity |
| 2 | Kali: publish “active claims” board (who owns C-0, C-1′, …) | Kali |
| 3 | Assign C-0 implementer + C-1′ implementer (can be sequential same agent) | Kali |
| 4 | Verity/P10: baseline real `make test` numbers into OMEGA_ENGINE after C-0 | Verity |
| 5 | No agent starts D-* until gate checklist posted green | All |

---

*⬡ OMEGA ⬡ FLEET-TEAM-PLAYBOOK ⬡ v1.0.0 ⬡ ONE-DIRECTION ⬡ 2026-07-21*
