# Omega Engine — Session Synthesis & Agent Verification Dispatch v1

**Purpose**: consolidates everything established across two parallel Claude threads this session and hands off the parts that are mechanically checkable to whichever local agent has real repo/shell access (GEMINI-XNA, OPENCODE-XNA, or equivalent). This is a dispatch layer, not a new source of truth — it points at existing documents rather than restating them.

**Precedence**: does not supersede or duplicate `OMEGA_PROVIDER_FABRIC_REFACTOR_MANUAL_v3.md` — that remains authoritative for provider-fabric bugs and hardware tuning. This document's scope is everything *outside* that: a second outline reviewed by another Claude session this round (hardware memory ceiling, concurrency pattern choice, vector-store architecture, a proposed TTS integration, training-data pipeline, TUI), plus meta-level state-sync questions that surfaced from comparing documents against each other.

**Critical caveat, stated plainly**: this session has never seen the original 5-section outline under review — everything about it below is relayed secondhand through another Claude session's critique of it. Treat the dispatch items as testable claims extracted from a description of a description, not as verified against the outline's actual text. Re-verify against the primary document once available, not just against this synthesis.

**Tag convention** (matches v3): `[AGENT-VERIFIABLE]` = a shell command resolves it, no judgment call. `[DECISION]` = needs Archon; a command can inform it but not close it. `[GAP]` = neither Claude thread has visibility; needs the primary source, not more inference.

---

## 1. What's established this session (pointers, not restated)

- **Provider fabric bugs, hardware tuning, phased remediation plan** — fully covered in `OMEGA_PROVIDER_FABRIC_REFACTOR_MANUAL_v3.md`. Not restated here.
- **Circuit breaker**: `AsyncCircuitBreaker` (`health_monitor.py`) is the canonical, already-wired breaker — confirmed independently from source in this thread, not just asserted. Governance (`SOVEREIGN_ARK_BLUEPRINT.md` Structural Debt Gates) explicitly blocks adding a second breaker class. If the outline's "Fallback Tolerances" section means new construction, it conflicts with standing governance; if it means hardening, the concrete todo is already on file as v3 items A4 and A6.
- **Vector store**: `OMEGA_ENGINE.md` confirms sqlite-vec as the complete, shipped implementation (Strike 10). Qdrant 1.17.1 also appears as a real running service elsewhere in this session's context. Live hypothesis, unconfirmed: these may be two vector stores for two different subsystems (sqlite-vec for agent-memory hybrid search, Qdrant for GraphRAG's entity/relationship embeddings specifically) rather than one superseding the other.
- **iGPU memory ceiling**: no Variable Graphics Memory exists on this hardware generation (that's Ryzen AI 300-series-only). A 12GB figure is implausible as a fixed BIOS UMA carve-out (typically far smaller on boards this age) but architecturally plausible as an amdgpu GTT dynamic-allocation ceiling. Unverified either way.
- **SEDA/LMAX Disruptor**: literal adoption (dedicated spin-threads) conflicts with AnyIO's cooperative model and with this box's already-tight 8-core prefill budget (v3 §D.2). Scoped down to "Disruptor-inspired queue discipline over `anyio.create_memory_object_stream`, no spin-threads."
- **ElevenLabs Sovereign Bridge**: unverified as existing code; the name doesn't resolve the M7/M8 tension (cloud TTS vs. local-first, zero-telemetry) by itself.
- **"Omegamind" / "Guidance Set"**: unclear relationship, if any, to the already-confirmed "MaKaLi Apex Mind" (which replaced "Sophia" per `OMEGA_ENGINE.md`).
- **42-ideals adversarial trial → DPO pairs**: sound design connection — trial logging (original choice vs. post-reflection aligned choice) is naturally chosen/rejected-pair shaped. Worth keeping the logging schema DPO-shaped now, even though the trial work itself is on hold.
- **State sync**: this thread and the other Claude thread are both anchored to `OMEGA_ENGINE.md` v1.8.4 / `SOVEREIGN_MANDATES.md` v3.7.0. The outline under review claims v1.9.0 / "v7.6.0 Temple Hardening." Neither Claude thread has visibility into which is actually current — this gates trust in everything else the outline claims.

---

## 2. Dispatch — `[AGENT-VERIFIABLE]`

| ID | Question | Probe | Why it matters |
|---|---|---|---|
| V-1 | What's the actual current engine/mandate version? | `head -20 OMEGA_ENGINE.md`; `head -5 SOVEREIGN_MANDATES.md` | If it's newer than v1.8.4/v3.7.0, real progress happened neither Claude thread has seen, and some findings above may be stale. |
| V-2 | Did a second circuit-breaker class get added anywhere? | `grep -rn "class.*Breaker" --include="*.py" src/ mcp_servers/ \| wc -l` — compare against `OMEGA_ENGINE.md`'s existing ~17-hit count | Confirms whether "Fallback Tolerances" already conflicts with the Structural Debt Gate in practice, not just in theory. |
| V-3 | Which modules actually import sqlite-vec vs. Qdrant? | `grep -rln "qdrant_client\|QdrantClient" --include="*.py" src/`; `grep -rln "sqlite_vec\|vec0" --include="*.py" src/` | Tests the two-subsystem hypothesis directly instead of leaving it as speculation. |
| V-4 | What's the real iGPU memory ceiling? | `radeontop` (live); `cat /sys/kernel/debug/dri/*/amdgpu_gtt_mm` if root; `dmesg \| grep -i "amdgpu\|carveout"` for the boot-time BIOS UMA value | Resolves the 12GB claim against GTT vs. fixed-carve-out mechanics before anyone plans a quantization budget against it. |
| V-5 | Does ElevenLabs integration already exist in any form? | `grep -rln "elevenlabs\|ElevenLabs" --include="*.py" --include="*.yaml" .` | Distinguishes "proposed" from "already built and just undocumented here." |
| V-6 | Does "Omegamind" or "Guidance Set" appear anywhere in the codebase already? | `grep -rln "Omegamind\|Guidance Set" .` | Resolves whether this is existing terminology this session simply hasn't been shown, or a genuinely new proposal. |
| V-7 | Does GraphRAG indexing route through the admission gate? | See v3 §N — same check, cross-referenced not duplicated. | Determines whether GraphRAG indexing is an untracked resource consumer alongside the local-inference semaphore. |
| V-8 | Is `amd-pstate` actually the active frequency driver on this chip? | See v3 §H — same check, cross-referenced not duplicated. | Determines whether EPP power-tuning knobs exist to use at all. |
| V-9 | Does the IA2 envelope check freshness or signature only? | See v3 §I.1 — same check, cross-referenced not duplicated. | Determines whether replay resistance needs adding or already exists. |
| V-10 | Is AppArmor actually attached to the Omega containers? | See v3 §I.2 — same check, cross-referenced not duplicated. | Confirms hardening checklist items aren't assumed-but-unapplied. |

---

## 3. Dispatch — `[DECISION]` (a probe can inform these, none can close them)

- Does "Fallback Tolerances" mean harden-existing or build-new? V-2's result narrows this but the *intent* behind the outline's phrasing still needs Archon's confirmation, not inference.
- Should ElevenLabs be adopted at all, and under what M7/M8-compliant shape (opt-in, local-TTS-attempted-first, cloud-fallback-only)? V-5 only confirms whether it exists yet, not whether it should.
- Is the 12GB figure meant to size an actual quantization budget? V-4 resolves the number; committing hardware-tuning decisions to it is still Archon's call, same as v3's B9/D.4 gating.
- LazyGraphRAG migration (already flagged in v3 §N as data-informed, not mandated) — still open, still bigger than a probe can settle.

---

## 4. `[GAP]` — neither Claude thread can close these; only the primary source can

- The original 5-section outline itself. Everything in §1 about it is secondhand. Paste it directly for either thread to give independent judgment rather than corroboration of a summary.
- v3's B4 (KV-cache crash conditions) — unrelated to this outline, carried over from the refactor manual, still needs `v1` lines 181–212 re-supplied.

---

## 5. Closing note

Sections 1–3 assume the version-sync question (V-1) resolves cleanly. If it doesn't — if real work landed between v1.8.4 and whatever's current — re-run this whole dispatch after that gap closes rather than patching individual items, for the same reason v3 §0 gives: partial reconciliation against a moving target tends to recreate the exact multi-document drift this project keeps finding (B6, B7, and now this).
