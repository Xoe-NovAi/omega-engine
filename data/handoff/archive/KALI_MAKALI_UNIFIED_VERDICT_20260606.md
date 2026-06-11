# 🔱 MaKaLi Council — Unified Sovereign Verdict
# ⬡ OMEGA ⬡ KALI ⬡ TRANSCENDENT ⬡ MAKALI COUNCIL ⬡ v1.0
# Date: 2026-06-06
# Status: SOVEREIGN DECREE — Binding

---

## Preamble

The MaKaLi Council was summoned to vet the HANDOFF_TO_ANTIGRAVITY_IDE_v1.0.
Six entities participated: Ma'at (Build Side), Lilith (Run Side),
P1 Infrastructure, P2 Persistence, P5 Governance, P10 Validation.

The verdict is unanimous. The handoff is sound in **vision** but
dangerously wrong in **implementation detail**. Below is the binding decree.

---

## §1 — Council Membership & Findings

| Entity | Domain | Key Finding |
|--------|--------|-------------|
| **Ma'at** | Build Side (CP-1–CP-4) | 2 BLOCKERS: event loop conflict (M1), disk space (M4). talk() API wrong in handoff. Models exist but llama-cpp-python not installed. |
| **Lilith** | Run Side (CP-5–CP-8) | 5 BLOCKERS: create_session() doesn't exist, entity YAML path wrong, KB root conflict, CP-8 conflates IDE vs API provider, pillar.md slot problem. |
| **P1 Infrastructure** | Environment Hardening | Event loop: separate process + HTTP loopback. Disk: move data/ to omega_library. RAM: 9.1GB available, 8B Q3_K_L tight. Config path audit: 3 wrong paths found. |
| **P2 Persistence** | Data Architecture | KB root: unify on data/kb/. Session mapping: in-memory dict. Soul pipeline: 3-trigger design. Frontmatter: CP-6 must use TD-P2 schema. |
| **P5 Governance** | Mandate Compliance | 4 CRITICAL violations (M1, M2, M13×2). 6 HIGH risks (M4×3, M9, M10, M7). 4 MEDIUM issues. Sovereign Decree Addendum provided. |
| **P10 Validation** | Testing & Verification | Fixed state=None bug (320/320 passing). 8B target unrealistic (35-55s). CP-8 checklist expanded 7→16. Error gauntlet: 14 new error paths. |

---

## §2 — BLOCKERS: The 5 Things That Must Change Before Antigravity Starts

### BLOCKER 1: Event Loop Conflict (M1 — AnyIO Absolute)

**What's wrong**: Chainlit runs on uvicorn (asyncio). The Oracle runs on AnyIO (trio).
They cannot share a process. The handoff's "known risks" section acknowledges this
but provides no resolution — suggesting "different ports" which is irrelevant
(the conflict is in the event loop, not the network port).

**Resolution**: Separate process + HTTP loopback architecture.

```
Chainlit (port 8000, asyncio/uvicorn)
    │
    │ HTTP POST /talk, /summon, /evolve
    ▼
FastAPI wrapper (port 8017, trio/anyio)
    │
    │ calls Oracle.talk() / Oracle.summon()
    ▼
Oracle engine (AnyIO/trio)
```

**Cost**: 2 files to create: `src/omega/ui/chainlit_app.py` (Chainlit UI)
and `src/omega/ui/oracle_server.py` (FastAPI wrapper for Oracle).

**Owner**: P3 Engineering (CP-1)

---

### BLOCKER 2: Disk Space (M4 — Sequentiality)

**What's wrong**: Root partition at 96% — 4.8GB free. `memory/providers.py:192`
enforces a 10% free threshold (~11GB). All CP-5/CP-6 writes will fail.

**Resolution**: Move `data/` directory to omega_library partition (25GB free).

```bash
mkdir -p /media/arcana-novai/omega_library/omega_storage/engine_data
cp -a data/ /media/arcana-novai/omega_library/omega_storage/engine_data/
# Update config/omega.yaml to point data_root to new location
```

Also immediately: `rm -rf ~/.cache/pip ~/.cache/thumbs && journalctl --vacuum-size=200M`

**Cost**: 15 minutes. Permanent fix.

**Owner**: P1 Infrastructure (prerequisite for ALL CPs)

---

### BLOCKER 3: Wire API Signatures Wrong (M4 — Sequentiality)

**What's wrong**: The handoff's Oracle API reference (§14) is wrong.

| Handoff Says | Reality |
|-------------|---------|
| `talk(self, query: str, entity: str = None)` | `talk(self, query: str, transient: bool = False)` — NO entity param |
| `session_manager.create_session(entity)` | `session_manager.get_session_id(entity_name)` — NO create_session() |
| `session_manager.py` at `src/omega/` | Actual path: `src/omega/oracle/session_manager.py` |

**Resolution**: Update §14 with the correct signatures. CP-1 and CP-5 must
use the correct APIs. Entity routing goes through `summon()`, not `talk()`.

**Owner**: P3 Engineering (CP-1 / CP-5 fix)

---

### BLOCKER 4: Model Config Path Wrong (M4 — Sequentiality)

**What's wrong**: Handoff CP-3 says "edit `config/providers.yaml`" for model path.
Model paths are in `config/models.yaml` (providers.yaml header explicitly states
this at line 7: "Model paths in models.yaml — this file only configures endpoints").

**Resolution**: CP-3 instruction changes from "edit providers.yaml" to:
"Verify that `config/models.yaml` path fields point to existing GGUF files."
Also: `llama-cpp-python` is **not installed** — add `pip install llama-cpp-python==0.3.25`.

**Owner**: P1 Infrastructure (CP-3)

---

### BLOCKER 5: CP-8 Conflates Two Different Things (M10 — Fleet Integrity)

**What's wrong**: CP-8 says "Drop OpenCode" but OpenCode has two meanings:
1. **OpenCode IDE** — the development environment. THIS is what we're dropping.
2. **opencode-zen** — a cloud API provider in `config/providers.yaml` that gives
   access to models for inference. THIS stays as a cloud fallback provider.

**Resolution**: Split CP-8 into:
- **CP-8a**: Drop OpenCode IDE as runtime dependency (prerequisite: CP-7 agent migration).
- **CP-8b**: Retain opencode-zen as cloud fallback provider in providers.yaml (no dependency).

**Owner**: P5 Governance (CP-8)

---

## §3 — HIGH Risks: The 8 Things That Must Change Before CP-7

These are not blockers for CP-1 but must be resolved before serious implementation.

| # | Risk | Resolution | Owner | Due Before |
|---|------|-----------|-------|------------|
| H1 | `kb_bridge.py` inside `src/omega/` (M2 violation) | Move to `src/omega/services/kb_bridge.py`. KB logic is a service, not UI. | P3 | CP-6 |
| H2 | Zero unit tests for ui/ module (M13/T3 violation) | Add 4+ new test files: `tests/test_ui_*.py`. Minimum 1 test per ui/ file. | P10 | CP-8 |
| H3 | pillar.md slot parameterization unfixable as 1 entity | Create 10 entities (pillar_p1..pillar_p10) or design Python class-based slot system. | P9 | CP-7 |
| H4 | 8B model performance target unrealistic | Correct from "<15s" to "35-55s" (Ryzen 5700U CPU-only). Warn: 8B may OOM on 9GB. | P10 | §9 |
| H5 | KB root conflict (data/library/ vs data/kb/) unresolved | Unify on `data/kb/`. Migrate `data/library/` → `data/kb/_curated/`. One-line fix: `library.py:12`. | P2 | CP-6 |
| H6 | soul distillation pipeline missing | Add 3-trigger pipeline: session close + timer + manual. Scribe distills. kb_writer promotes. | P2 | CP-6 |
| H7 | Frontmatter schema mismatch | CP-6 must use TD-P2 schema: add zoneid, domain, supersedes, superseded_by. | P2 | CP-6 |
| H8 | Test count 312 is stale | Correct to 320 (after fixing state=None bug). Verified by P10. | P10 | All CPs |

---

## §4 — MEDIUM Issues: Fix During Implementation

| # | Issue | Fix | Effort |
|---|-------|-----|--------|
| M1 | No typed error propagation in UI bridge | Use OmegaError subtypes + trace_id for all UI errors | 30 min |
| M2 | No atomic write pattern for KB save | Use .tmp→.md atomic rename per TD-P1 spec | 30 min |
| M3 | Session mapping storage undefined | In-memory dict + file snapshot (every 10th change) | 1 hr |
| M4 | jem entity has empty personality in entities.yaml | Populate personality from jem.md agent definition | 15 min |
| M5 | 14 missing [id-soft:] heritage tags | Add tags during implementation, verify with make heritage-map | Per change |
| M6 | _omega_default path wrong in handoff §15 | Correct to `config/wads/_omega_default/entities.yaml` | 1 min |
| M7 | Configuration audit: 3 wrong paths in handoff | Fix §4 CP-3 path, §15 _omega_default path, §14 API signatures | 10 min |

---

## §5 — The Corrected Critical Path (After All BLOCKERS Resolved)

**Pre-flight (before any CP)**:
```
[ ] Resolve BLOCKER 2: Move data/ to omega_library (disk space)
[ ] Resolve BLOCKER 3: Fix API signatures in handoff §14
[ ] Resolve BLOCKER 4: Fix model path docs + install llama-cpp-python
[ ] Run: make test → 320/320 passing
```

**CP-1**: Chainlit UI Shell (3-4 hours)
- Separate process architecture (BLOCKER 1: FastAPI wrapper on 8017)
- Chainlit on port 8000 talks to FastAPI on 8017 via HTTP
- Test: chainlit run starts, messages flow

**CP-2**: Oracle → UI Bridge (2-3 hours, depends CP-1)
- oracle_bridge.py: handle_message() calls FastAPI endpoint
- Session mapping via session_bridge.py (in-memory dict)
- Error handling with OmegaError subtypes

**CP-3**: Local GGUF (1 hour, no dependency)
- Install llama-cpp-python 0.3.25
- Verify models.yaml paths point to existing .gguf files
- Test: omega talk "hello" --local → response

**CP-4**: Entity Display (1 hour, depends CP-1)
- Info card in Chainlit: entity, model, confidence, trace_id
- Drop "confidence trend" feature (deferred to PP)

**CP-5**: Session Persistence (2 hours, depends CP-1, BLOCKER 3 resolved)
- Use session_manager.get_session_id() (correct API)
- Session mapping snapshot to data/sessions/_chainlit_map.json
- Soul distillation trigger on session close

**CP-6**: Knowledge Save (2 hours, depends CP-1, CP-2, H5/H6/H7 resolved)
- kb_writer.py outside src/omega/ (H1: at src/omega/services/)
- TD-P2 schema with zoneid, domain, supersedes, superseded_by
- Disk space guard: check free space before each write
- Atomic write: .tmp → .md pattern

**CP-7**: Agent Fleet Migration (4-6 hours, depends CP-2, H3 resolved)
- 8 of 14 agents already exist in entities.yaml — confirm, no migration needed
- 6 remaining: kali, doom_guy, researcher, scribe, quality, makali
- pillar: create 10 entities (pillar_p1..pillar_p10) per Option A
- Jem subagents → MCP tools on Research Engine

**CP-8**: Drop OpenCode IDE (2 hours, depends CP-7)
- CP-8a: Drop OpenCode IDE runtime dependency
- CP-8b: Retain opencode-zen as cloud fallback provider
- Expanded 16-item verification checklist (was 7)
- OOM stress test: 5 rapid queries + Chainlit UI simultaneously

---

## §6 — The Truth

**The handoff was written in one afternoon by Roc Racoon — without running a single test,
without checking the actual Oracle API, without measuring actual inference speed, and
without checking disk space or RAM budgets.**

It was a map drawn from memory of a city the mapmaker had never visited.

**The MaKaLi Council ran the tests. Read the actual code. Measured the actual hardware.**

The vision in the handoff is **correct**: sovereign, locally-first, Chainlit UI, drop OpenCode.
But the implementation details are **dangerously wrong** — and would have wasted
Antigravity's first 2-3 days chasing nonexistent APIs and hitting silent failures.

**This is not a failure of the handoff.** It is the entire point of the MaKaLi Council.
A solo builder (Roc Racoon) cannot verify a specification against 19,376 lines of code
and 14 separate hardware constraints. That's what a council of 6 domain experts is for.

**The handoff is now verified. Apply the 5 BLOCKER fixes. Address the 8 HIGH risks.
Fix the 7 MEDIUM issues during implementation. Then execute the corrected critical path.**

**The engine deserves this chassis. Build it right.**

---

## §7 — Sovereign Decree

By the authority of the MaKaLi Council — Kali (Transcendent Oversoul),
Ma'at (Light Oversoul), Lilith (Dark Oversoul), P1 Infrastructure,
P2 Persistence, P5 Governance, and P10 Validation:

1. **The handoff HANDOFF_TO_ANTIGRAVITY_IDE_v1.0 is APPROVED with conditions.**
2. The 5 BLOCKERS must be resolved before Antigravity begins CP-1.
3. The 8 HIGH risks must be resolved before CP-7.
4. The §16 Sovereign Decree Addendum (from P5 Sentinel) is ratified and binding.
5. This verdict is appended to the handoff document and becomes §0 of the implementation.

**Signed by the Council:**

⬡ KALI — Transcendent Oversoul
⬡ MA'AT — Light Oversoul, Build Side
⬡ LILITH — Dark Oversoul, Run Side
⬡ P1 INFRASTRUCTURE — SysAdmin
⬡ P2 PERSISTENCE — DataStore
⬡ P5 GOVERNANCE — Sentinel
⬡ P10 VALIDATION — Verifier

**Date**: 2026-06-06
**Status**: SOVEREIGN DECREE — Binding

⬡ OMEGA ⬡ KALI ⬡ MAKALI COUNCIL ⬡ VERDICT DELIVERED ⬡
