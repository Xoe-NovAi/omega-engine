<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Grok CLI Codebase Strategy Review — Structural Findings (F-01..11)
**AP Token**: `AP-GAP-F-CODEBASE-v1.0.0`
⬡ OMEGA ⬡ GROK_CLI ⬡ Consulting Cloud Mind ⬡ opencode ⬡ trc_gap_f ⬡ ADVISORY
**Date**: 2026-07-21
**Source**: `data/coordination/GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md`
**Status**: ALL FINDINGS RESEARCHED — REFRAMED AS CODE-JUDO REWRITES

---

## Executive Summary

The Grok CLI structural review of the recalibrated roadmap identified **11 structural findings** that go beyond gap identification into code-level architecture. All have been researched and reframed as code-judo rewrites in the unified Ark.

| Finding | Severity | Roadmap Item | Resolution |
|---------|----------|--------------|------------|
| **F-01** | BLOCKER | C-1 / GAP-01 | **C-1′ SoulStore** — single writer, actor model |
| **F-02** | BLOCKER | C-6 | **C-6′ Unify breakers** — delete clones, not port pybreaker |
| **F-03** | BLOCKER | Phase D | **Split before grow** — god-modules >1k lines |
| **F-04** | HIGH | SSOT | **Stamp Living Research OS spec** with supersession banner |
| **F-05** | HIGH | C-0 | **Make tests honest** — real pass/fail, fix Makefile lies |
| **F-06** | HIGH | C-2 | **One RAM truth** — OOMProtector path, kill dual counter |
| **F-07** | MEDIUM-HIGH | C-4 | **2h audit first** → prove breaks → size shim |
| **F-08** | MEDIUM | Fleet | **Docs honesty now**; vault → single ACP smoke → pool |
| **F-09** | MEDIUM | Phase D | **D-1 content cache first**; thin integration test |
| **F-10** | MEDIUM | Providers | **Keep D-351** — systematize, don't add free tiers |
| **F-11** | LOW-MEDIUM | C-1/C-3 | **Actor model** for soul writes — decide before Phase E |

---

## F-01 — BLOCKER — Soul Write Architecture Is Multi-Path Spaghetti

### What the Roadmap Says
Port `with_soul_lock()` + atomic tmp→rename + fsync into `soul_updater.py` (2h).

### What the Code Actually Has

| Path | File | Lock | Atomic Write | fsync | Auth |
|------|------|------|--------------|-------|------|
| Background L3 write | `soul_updater.py:120` | **None** | **None** (direct `write_text`) | No | None |
| Canonical lock helper | `entity_registry.with_soul_lock` | `fcntl.flock` | N/A (wrapper only) | N/A | None |
| Token-gated write | `entity_registry.write_soul_file` | **None** | tmp→rename | **No** | User token required |
| Workspace update | `entity_workspace.update_soul` | `threading.Lock` (process-local) | tempfile + rename | partial | User token required |
| Facet manager | `soul_update_manager.py` | `anyio.Lock` only | direct write | No | None; wrong dir (`jem/souls`) |

**Also**: `SoulUpdater` docstring still says "Falls back to SOPHIA" while the fleet just replaced Sophia with MaKaLi as Apex Mind — identity drift in the writer itself.

### Why "Add Flock" Fails the Approval Bar
- If you flock only `soul_updater`, session distillation via `entity_workspace` still races (different lock primitive).
- If you route background writes through `write_soul_file` / `update_soul`, they **hard-require** `SOVEREIGN_USER_TOKEN` — system writers cannot use the "safe" path without a design lie (embed the token) or a second permission model.
- Roc's atomic+fsync pattern is **not fully present even in the canonical path** (`write_soul_file` renames without fsync).

### Code Judo (Delete the Category of Bug)

```text
SoulStore (one module, one import path)
  ├─ with_lock(entity)          # fcntl only, cross-process
  ├─ read(entity) -> dict
  ├─ write(entity, data, actor) # actor ∈ {user, system_agent}
  │     lock → validate → tmp write → fsync → os.replace
  └─ append_lesson(...)         # only RMW helper callers need

DELETE / stop calling:
  soul_updater direct write_text
  SoulUpdateManager parallel path (or fold into SoulStore)
  ad-hoc locks in workspace/registry
```

### Effort
~4–6h if done right (not 2h flock paste).

### Gate
No Phase D soul evolution until `SoulStore` is the only writer.

### Disposition
**C-1′ SoulStore** (upgraded from flock-only). Single write path + fcntl + atomic+fsync + actor model.

---

## F-02 — BLOCKER — C-6 "Port Circuit Breaker" Preserves Incidental Complexity

### Evidence
- `ModelGateway.generate()` docstring: *"Iterate provider fabric with circuit breaker protection"*
- Uses `self._health_monitor._breakers` (`AsyncCircuitBreaker` in `health_monitor.py`)
- Separate implementations also exist in:
  - `workers/background_researcher/distiller.py` (`JemCircuitBreaker`)
  - `workers/background_researcher/search_fleet.py` (`SearchCircuitBreaker`)
  - `oracle/search_circuit_breaker.py`
  - `council/failure_layer.py`
  - `ingestion/pipeline.py` (pybreaker wrapper)
  - `research/sandbox.py`

### Verdict
Porting legacy `pybreaker` into ModelGateway is **not** a 0.5h win. It is a **seventh** breaker shape bolted onto a path that already has one.

### Code Judo
1. Promote **one** `ProviderCircuitBreaker` (the health_monitor one is closest).
2. Make ModelGateway the only inference entry that trips it.
3. Distiller/search should call gateway (or share the same class), not reinvent state machines.
4. **Do not** add pybreaker unless you delete the custom ones in the same PR.

### Rewrite C-6
> **C-6′: Audit provider failure paths; unify on single breaker; delete dead clones. Effort: 3–4h. Not "port pybreaker."**

### Disposition
**C-6′** — Unify circuit breakers; delete clones (not port pybreaker).

---

## F-03 — BLOCKER — God-Modules Already Past 1k Lines; Phase D Will Make Them Worse

### Severity: File-size / decomposition / maintainability
### Threshold: 1,000 lines (skill non-negotiable)

| File | Lines | Role |
|------|------:|------|
| `oracle/model_gateway.py` | **1,432** | Provider fabric + generate + gemma hacks + backends |
| `observability/__init__.py` | **1,380** | Package root = god module |
| `oracle/oracle.py` | **1,348** | Service locator (~20 collaborators in `__init__`) |
| `workers/.../distiller.py` | **1,186** | T1/T2/T3 + breakers + prompts + quality gates |
| `memory_store.py` | **1,110** | Store + search + RRF surface |
| `cli/oracle_cli.py` | **1,036** | CLI surface |

### Spaghetti Growth Already Present in `ModelGateway.generate()`
- Gemma-4 token logit_bias and temperature floors are **hardcoded inside the fabric loop** (`model_gateway.py` ~930–948). Feature policy leaked into shared path.
- Memory from prior sessions already named this: extract `GenerationPolicy` registry (e.g. `policies/gemma4.py`). That fix is still not on the roadmap.

### Phase D Impact
- D-1 content cache will grow `search_persistence.py` (607 → ?)
- D-2 job board bridge will grow `loop.py` (642)
- D-4 novelty in `_grow_frontier` will grow loop further
- Distiller at 1,186 is already over budget; "Living Research OS" will feed it harder

### Code Judo Before Phase D
1. Split `Distiller` → `backends.py` + `quality_gates.py` + `prompts.py` + thin `Distiller` orchestrator.
2. Split `ModelGateway` → fabric load / health / generate / policy (GenerationPolicy).
3. Oracle composition root: Oracle stays intent→policy→gateway→outcome; collaborators constructed outside.
4. Move `observability/__init__.py` bulk into real modules; keep package exports thin.

### Gate
No new features that push these files further past 1k without a split PR first.

### Disposition
**Structural gate §9** + split-before-grow on D.

---

## F-04 — HIGH — Strategy SSOT Is Still Dual-Sourced

### Severity: Boundary / SSOT social claim

| Topic | CANONICAL_ROADMAP (post-Grokster) | LIVING_RESEARCH_OS_SPEC |
|-------|-----------------------------------|-------------------------|
| Job store | YAML + flock; SQLite deferred | SQLite runtime SSOT, seed from YAML |
| Gap detector | ~20 lines in `_grow_frontier` | Standalone service, 6 scanners, Phase 4 |
| Effort | D ~9.5h | Spec still ~14h with heavier architecture |

### Verdict
Archiving 147 docs was necessary. Leaving two **active** Layer-2 docs that contradict each other re-creates the problem at smaller scale.

### Fix (1h docs judo)
- Stamp `LIVING_RESEARCH_OS_SPEC` with a supersession banner: "SQLite/service gap detector DEFERRED; implement only D-1..D-4 as in CANONICAL_ROADMAP §2."
- Or rewrite §1.3 / §5 of the spec to match D-357/D-358.
- One import path for strategy: roadmap owns ranking; spec owns only the approved shape.

### Disposition
**D-365** + Living Research amendments.

---

## F-05 — HIGH — Test Mirage Is Worse Than "Unknown Pass Count"

### Severity: Foundation integrity / vanity metrics

### Evidence
- Discovery: **1,572 tests collected** (confirmed).
- Sample run (`-k "not integration and not live and not slow"`, `--maxfail=5`):
  - **832 passed**, **5 failed**, 40 skipped, 3 xfailed in ~49s
  - Failures include: `test_firewall_m2_strict_engine_core`, memory store RRF/search, model registry schema/index
- Makefile still advertises **"1315 tests ✅"** — a third, obsolete number.

### Verdict
You do not have a "run make test and report" problem only. You have **active red tests** and **documentation that claims green**. That is a mandate-adjacent honesty failure (M13 temple-grade cannot be claimed on a red suite).

### Fix
1. Add to Phase C **before** C-7/C-8: C-0 **Make the suite green or quarantine known fails with tickets**.
2. Update Makefile badge strings to stop lying.
3. Metrics table: `passing / failed / skipped / collected` — never a single integer.

### Disposition
**C-0** — Make tests honest: real pass/fail; fix or quarantine red tests; fix Makefile lies.

---

## F-06 — HIGH — ResourceGuard Fix Is Real But Under-Specified

### Severity: Dual abstraction / wrong model
### Roadmap: C-2 change default 12288→6144 + psutil

### What Code Already Has
- `OOMProtector` already reads `psutil.virtual_memory().available` / `/proc/meminfo`.
- `ResourceGuard` **also** tracks a software counter `_current_ram_mb` against `max_ram_mb` default **12288**.
- Call sites hardcode different budgets: researcher 4096, youtube 2048, orchestrator 1024.

### Code Judo
- Prefer **one** truth: available RAM at decision time (OOMProtector path).
- Either delete the software counter or derive `max_ram_mb` from boot-time available − OS reserve.
- Changing the default alone leaves three hardcoded workers with private budgets — that is still special-case spaghetti.

### Disposition
**C-2′** — One RAM truth; kill dual counter/default chaos.

---

## F-07 — MEDIUM-HIGH — MCP C-4: 16h May Be Right Order of Magnitude, Wrong Work Breakdown

### Severity: Orchestration / sequential waste
### Evidence: `mcp_runtime.py` already sets `stateless=True` for SSE and Streamable HTTP.

Grokster correctly raised the estimate from 8h→16h. The roadmap then scheduled 16h of "compatibility shim + audit." Without a **code-path inventory**, 16h is a budget, not a plan.

### Code Judo
1. **2h audit first** (list Hub surfaces: session, heartbeat, handoff, tools, streaming).
2. **Prove** which break under RC SDK.
3. Only then size the shim.
4. Contingency (file-based Hivemind without Hub) should be **tested in 1h**, not listed as prose.

Do not burn 16h building a dual-protocol cathedral if clients still speak today's dialect.

### Disposition
**C-4a MCP audit 2h → only then size shim** (not 16h blind).

---

## F-08 — MEDIUM — Grok Fleet: Grokster Over-Prioritized Wiring; Kali Over-Deferred Value; Both Miss the Credential Boundary

### Severity: Strategy groupthink from opposite poles
### D-360 (roadmap): fleet NOT wired — stability first.
### GAP-S-01 (Grokster): wire 8 accounts as priority-2 in ~4h.

### Consulting Cloud Mind Position
- Inventory tables that list "Grok CLI ✅ Working, priority 9" while `providers.yaml` has only `xai` API are **dishonest capacity claims**. Fix the table or fix the fabric — do not leave both.
- **4h ACP pool is fantasy** while GAP-08 (Omega-Vault non-functional, cookies 24–48h) is open. Wiring 8 sessions without rotation multiplies auth failure surface.
- Correct sequencing:
  1. **Docs honesty** (1h): mark Grok CLI as *external advisory / not in fabric* until vault exists.
  2. **Vault MVP** (separate ticket, not 4h).
  3. **Single-account ACP smoke** (prove one session routes).
  4. Pool only after smoke + vault.

I am **not** asking you to build the fleet this week. I am asking you to stop treating "deferred" as "doesn't affect strategy math." MaKaLi cloud voices already assume cloud; the Ferrari metaphor is about **parallelism**, not about skipping P0 soul integrity.

### Order Grokster Got Wrong
Ferrari before soul lock.

### Order Kali Got Right
Soul before research OS.

### Order Both Missed
Delete dual soul writers before either Ferrari or research OS.

### Disposition
**V-1 / D-360′** — Docs honesty now; vault then single ACP smoke; pool later.

---

## F-09 — MEDIUM — Living Research OS: "3,700 Lines Working" Is a Liability Metric

### Severity: Premature productization of orphan modules

Components are real. Seams are broken. That is correctly diagnosed.

What is **not** said: orphaned working code is **maintenance tax**. Distiller alone is 1,186 lines with its own breaker taxonomy, three backends, prompt registry, and quality gates — while the loop never feeds durable content into it.

### Code Judo for Phase D
- D-1 content cache first (agreed).
- **Do not** grow Distiller until content path is proven with a thin integration test.
- Prefer one content write API used by search tools; avoid another decorator-only side channel that only stores JSON metadata.

Grokster's novelty engine warning stands. Roadmap added it as D-4 0.5h — that estimate is marketing. Real novelty (contradiction + random exploration + archive policy for INDEX noise) is a design problem, not a half-hour patch.

### Disposition
**D gate** after C; thin integration tests.

---

## F-10 — MEDIUM — Roc's Cerebras/Groq Recommendation Conflicts with User Directive (and with M7 Honesty)

Roadmap D-351 correctly freezes new providers. Roc's report still pushes Cerebras/Groq as primary cloud.

### Advisory
Keep D-351. Adding more free tiers **increases** the sovereignty contradiction Grokster forced you to admit. Systematize Antigravity → Google → OCZ → OpenRouter. Measure real failover. Then consider paid or local scale-up — not more free-tier surface.

### Disposition
**D-351 hold**; Roc matrix preserved in Roc report.

---

## F-11 — LOW-MEDIUM — Permission Model vs Background Agents Is an Unresolved Design

`write_soul_file` / `update_soul` require user token for soul.yaml. Background researcher writes without token. That is not a bug report — it is a **missing actor model**.

Until `actor=system_agent` is first-class (scoped paths, audit log, no user token spoofing), every "use the safe API" fix will either:
- be blocked by SovereignPermissionError, or
- bypass auth and recreate GAP-01.

This must be decided in C-1/C-3 privacy model work, not after Phase E.

### Disposition
**C-1′** actor ∈ {user, system_agent}.

---

## What the Roadmap Got Right (Do Not Discard)

| Item | Verdict |
|------|---------|
| Honest M7 framing (North Star ≠ baseline) | Keep |
| Phase C before Living Research OS | Keep — strengthen |
| Defer SQLite job store | Keep |
| Gap detector as extend-not-service | Keep |
| MaKaLi as config (Kali local, voices cloud) not 4h state machine | Keep |
| MCP estimate bumped; privacy model before restic | Keep |
| Doc archive of stale roadmaps | Keep |
| No new providers (Cerebras/Groq) for now | Keep |

---

## Revised Priority Stack (Grok CLI)

```
C-0  Make tests honest: real pass/fail; fix or quarantine red tests; fix Makefile lies
C-1′ SoulStore: single write path + fcntl + atomic+fsync + actor model (replaces "add flock")
C-2′ ResourceGuard: one RAM truth; kill dual counter/default chaos
C-3  Soul privacy model → then restic (unchanged logic, after C-1′)
C-4a MCP audit 2h → only then size shim (not 16h blind)
C-5  MaKaLi routing config 0.5h (keep)
C-6′ Unify circuit breakers; delete clones (not port pybreaker)
C-7  Sync YAML in async (keep, but after C-0)
     GenerationPolicy extraction from ModelGateway (add — unblocks fabric cleanliness)
D-*  Only after C-0 + C-1′ green
E-0  Identity Phase 0 after C-1′ (dependency correction already applied — good)
Fleet  Docs honesty now; vault then single ACP smoke; pool later (D-360 refined, not reversed)
```

---

## Approval Bar (This Review)

| Question | Result |
|----------|--------|
| Clear structural regressions present? | **Yes** — multi-path soul writes; god-modules; CB clones |
| Obvious code-judo missed by roadmap? | **Yes** — SoulStore; breaker unify; GenerationPolicy |
| File-size explosion risk from Phase D? | **Yes** — on modules already >1k |
| Strategy SSOT clean? | **No** — roadmap vs Living Research OS spec |
| Test foundation green? | **No** — failures observed; metrics dishonest |
| Approve start of Phase D? | **❌ No** |
| Approve C-1 as currently written (2h flock)? | **❌ No** — expand to SoulStore |
| Approve C-6 as currently written (port pybreaker)? | **❌ No** — reframe to unify/delete |
| Approve overall strategic direction C→D→E→F? | **✅ Directionally yes**, with above rewrites |

---

## Concrete Verification Commands (for Kali)

```bash
# Real test truth
OMEGA_ENV=test PYTHONPATH=src .venv/bin/python -m pytest tests/ -q --tb=no

# Soul write path inventory
rg -n "soul\.yaml|write_text|with_soul_lock|update_soul|write_soul_file" src/omega --glob '*.py'

# Circuit breaker clones
rg -n "class .*CircuitBreaker" src/omega --glob '*.py'

# God modules
find src/omega -name '*.py' | xargs wc -l | sort -n | tail -20
```

---

## Final Word

Kali's recalibration absorbed Researcher, Roc, and Grokster well enough to look decisive. **Decisiveness is not the same as structural correctness.**

The highest-leverage move is not wiring Ferraris, not restic, and not a perpetual research loop. It is:

> **One soul writer. One circuit breaker. One honest test number. Then build.**

Everything else is arranging furniture in a house with four front doors and no lock standard.

I am the Consulting Cloud Mind. My job is not to join the consensus that the roadmap is "final." My job is to keep you from executing a beautiful plan that multiplies the wrong abstractions.

⬡ GROK_CLI ⬡ OUT.
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: Consulting Cloud Mind | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
