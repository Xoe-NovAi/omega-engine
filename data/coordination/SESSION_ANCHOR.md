# Session Anchor — Kali Session End Orchestration Pivot & Roc Integration
**AP Token**: `AP-KALI-SESSION-ANCHOR-20260730-v1.0.0`
**Updated**: 2026-07-30T08:45Z · **Owner**: Kali (Transcendent Oversight)
**Hivemind**: `ses_kali_20260730_001`

---

## Session Objective

Complete the strategic pivot for Session-End Orchestration (fixing the broken soul distillation pipeline) and integrate Roc's Local Worker Pool / Local Models Fix into a unified execution plan. All research complete; implementation ready to begin.

---

## Controlling Documents

| Priority | Path | Role |
|----------|------|------|
| 1 | `docs/strategy/SESSION_END_ORCHESTRATION_PIVOT_20260730.md` | **Strategic pivot SSOT** — Carmack pivot, architecture, execution roadmap |
| 2 | `data/entities/roc_racoon/workspace/KALI_REVIEW_LOCAL_WORKER_POOL_20260730.md` | **Kali review of Roc** — approved with 5 hardening requirements |
| 3 | `data/entities/roc_racoon/workspace/LOCAL_WORKER_POOL_KALI_BRIEFING_20260730.md` | Roc's briefing — 4 pipe fixes, worker pool architecture |
| 4 | `data/entities/roc_racoon/workspace/LOCAL_MODELS_BRIEFING_GAMEPLAN_20260730.md` | Roc's forensics — 4 bugs blocking local inference |
| 5 | `docs/research/R_SESSION_END_WRAPPER_PATTERN_20260730.md` | Wrapper pattern research — community-proven, Carmack-validated |
| 6 | `.opencode/wrapper.sh` + `.opencode/hooks/session_end.py` | **Implementation** — EXIT trap wrapper + distillation hook |
| 7 | `AGENTS.md` | Updated with wrapper usage + automatic distillation |
| 8 | `OMEGA_ENGINE.md` | Updated mandate compliance (23/25 FULL) |

---

## What Was Completed

| Item | Status | Evidence |
|------|--------|----------|
| **Session-End Wrapper** | ✅ COMPLETE | `.opencode/wrapper.sh` (EXIT trap) + `.opencode/hooks/session_end.py` (30s timeout, M22 provenance) |
| **Broken Plugin Deleted** | ✅ COMPLETE | `.opencode/plugins/soul_distiller.js` removed (used `session.compacted` — wrong event) |
| **Wrapper Research Doc** | ✅ COMPLETE | `docs/research/R_SESSION_END_WRAPPER_PATTERN_20260730.md` |
| **11 Research Streams** | ✅ COMPLETE | OpenCode DB, WAL safety, SDK, SoulDistiller quality, MemoryStore, community tools |
| **Strategic Pivot Document** | ✅ COMPLETE | `docs/strategy/SESSION_END_ORCHESTRATION_PIVOT_20260730.md` |
| **Roc Integration Review** | ✅ COMPLETE | `data/entities/roc_racoon/workspace/KALI_REVIEW_LOCAL_WORKER_POOL_20260730.md` |
| **AGENTS.md Updated** | ✅ COMPLETE | Wrapper usage, automatic distillation, updated timestamps |
| **OMEGA_ENGINE.md Updated** | ✅ COMPLETE | 23/25 mandates FULL (M5, M11 fixed via wrapper) |
| **Proposed Lessons** | ✅ COMPLETE | `data/entities/kali/proposed_lessons.yaml` — 6 L3 principles |

---

## The Carmack Pivot (Strategic Summary)

| Old Approach | New Approach |
|--------------|--------------|
| MemoryStore for transcripts (5 layers, batch writer broken) | **OpenCode SQLite DB as Transcript SSOT** — `opencode export` gives perfect JSON |
| Scribe SoulDistiller (regex truncation: "Pattern observed: ...") | **LLM-Driven Distillation** — local LLM via Roc's Worker Pool |
| Plugin hook (`session.compacted`) — fires mid-session | **Shell Wrapper EXIT trap** — catches ALL exits (physics, not API) |
| Multi-entity distillation (fragmented souls) | **Session Ownership Model** — starting entity owns session |
| Third-party CLI tools (`opencode-db`, `opencode-session-toolkit`) | **Native Tooling Only** — `opencode db` + `opencode export` |
| No agent memory of past sessions | **`opencode-sessions-explorer` plugin** — 18 tools for in-session recall |

---

## Roc-Kali Integration Contract

| Roc Delivers | Kali Consumes | Sync Point |
|--------------|---------------|------------|
| LocalWorkerPool + `spawn_local_worker` tool | Semantic distillation pipeline | `data/artifacts/local_worker/{task_id}/task_metadata.json` |
| 4 Pipe Fixes (type_k, logit_bias, cascade_router, context) | Working local inference | `omega talk "hello"` → Qwen3-1.7B via native-gguf |
| File-based queue + artifacts | Distillation input | Crash-safe, inspectable |

**Roc's Immediate Next Steps (Today)**:
1. Fix 0.1: `providers.py:352-353` → `type_k=None, type_v=None`
2. Fix 0.2: `remote_provider.py:223` → add `logit_bias`, `repetition_penalty`, `**kwargs`
3. Fix 0.3: Priority-first routing in `model_gateway.py`
4. Fix 0.4: `providers.py:482` → use `models.yaml` `context_window`
5. `make test` → must pass
6. `omega talk "What model are you?"` → expect Qwen3-1.7B via native-gguf

**Kali's Parallel Start (Today)**:
1. Phase 1: Wrapper DB Integration — `.opencode/wrapper.sh` queries `opencode db` for session metadata
2. Phase 2: Semantic Distillation Pipeline — `session_end.py` calls Oracle SoulDistiller with exported transcript
3. Phase 3: Install `opencode-sessions-explorer` plugin

---

## Key Corrections & Hard Truths

1. **Distillation Theater**: Scribe distiller does mechanical truncation; Oracle distiller has quality gates but never called. `approved_lessons.yaml` empty everywhere.
2. **MemoryStore is Broken**: Batch writer never started; `flush()` is no-op; no atexit handler. ACP JSONL (`updates.jsonl`) is the only crash-safe source.
3. **OpenCode DB is Safe Immediately**: WAL mode with `synchronous=NORMAL` auto-checkpoints on last connection close. Zero wait after exit.
4. **Session Ownership**: Sessions ping-pong 15+ times between agents. Starting entity owns the session; delegated work distills into owner's soul.
5. **Native > Third-Party**: `opencode export` + `opencode db` replaces all community CLI wrappers.

---

## Pending (Next Session)

1. **Execute Roc Phase 0** — 4 pipe fixes → `make test` passes → local inference works
2. **Execute Kali Phase 1** — Wrapper queries `opencode db` for session metadata after exit
3. **Execute Kali Phase 2** — `session_end.py` calls Oracle SoulDistiller with exported transcript
4. **Execute Roc Phase 1-2** — Wire models → Build Worker Pool → `spawn_local_worker` tool
5. **Integration Test** — Session end → distillation via local worker → `proposed_lessons.yaml` populated
6. **Install `opencode-sessions-explorer` plugin** — agent memory expansion

---

## Hydration Commands

```bash
# Strategic pivot
cat docs/strategy/SESSION_END_ORCHESTRATION_PIVOT_20260730.md

# Kali review of Roc
cat data/entities/roc_racoon/workspace/KALI_REVIEW_LOCAL_WORKER_POOL_20260730.md

# Roc's forensics
cat data/entities/roc_racoon/workspace/LOCAL_MODELS_BRIEFING_GAMEPLAN_20260730.md

# Wrapper implementation
cat .opencode/wrapper.sh
cat .opencode/hooks/session_end.py

# Proposed lessons
cat data/entities/kali/proposed_lessons.yaml
```

---

## Gnosis (L1→L2→L3)

- **L1**: 11 parallel research streams + Roc integration review completed. Strategic pivot documented. Wrapper built. All mandates updated. 6 L3 principles extracted.
- **L2**: The distillation pipeline was theater because it relied on a broken MemoryStore and a trivial regex distiller. The fix requires changing the substrate (SQLite SSOT), the intelligence (LLM), and the trigger (EXIT trap). Roc's Local Worker Pool provides the execution substrate for the LLM distillation.
- **L3**: **Substrate Enforces Contract** — Logical mandates (M5, M11) are wishes until the physical layer (wrapper + SQLite + local LLM) enforces them. The 4 pipe fixes are the admission controller for local inference. The file-based queue is the sovereign queue. The wrapper is the sovereign session boundary.

---

*Session complete. Awaiting user direction to begin Phase 1 execution (Roc pipe fixes + Kali wrapper DB integration).*

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ trc_session_anchor ⬡ 2026-07-30*