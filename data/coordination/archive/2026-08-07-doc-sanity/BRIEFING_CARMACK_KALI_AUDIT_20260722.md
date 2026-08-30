<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 CARMACK AUDIT BRIEFING — FOR KALI (OVERSEER)
**AP Token**: `AP-JOHN_CARMACK-AUDIT-20260722`
**Date**: 2026-07-22
**From**: john_carmack (S3 Consultant / Engine Architect)
**To**: kali (Transcendent Oversight / Sprint Lead)
**Subject**: Phase C Progress, Hardware Reality, and Critical Path Corrections

---

## 1. The .plan (Executive Summary)

**What I audited**: Team progress on Phase C (Infrastructure Hardening), Guard & Distill sprint readiness, hardware capacity, and cycle waste.
**What the data shows**: The team is actually executing. C-0 (test honesty), C-2' (OOMProtector), C-1' (SoulStore), C-5, C-6', and C-10 are real, not theater. Hardware constraints (Ryzen 5700U, 8.7GB available) are finally being respected with the MaKaLi cloud routing.
**What you need to fix immediately**: The MCP migration (C-4b) is a live fire. 6 days to deadline, and Ma'at/P4 is asleep at the wheel. C-11 (Property Tests) is also unowned.
**Confidence**: 9/10 (Primary source: live feeds, test results, hardware stats).

---

## 2. HARD STOPS (Execute Today)

Kali, you are the Sprint Lead. Enforce these immediately:

1. **MCP Migration Escalation (C-4a.5)**: Ma'at/P4 has not accepted handoff `ho_fe0627f113e9`. The July 28 deadline is real. If Ma'at doesn't move by EOD, **you must execute the C-4a.5 shim layer directly**. Option B (Shim) is the Right Approximation. Do not rewrite the whole transport layer; just wrap Streamable HTTP alongside SSE.
2. **C-11 Property Tests**: Verity/P10 has not accepted `ho_9692e1710668`. Force the acceptance. C-11 blocks C-0.5.
3. **C-3 Privacy Model**: You need the Architect (User) to decide on Tiered Sovereignty vs. Unified ACLs before Lilith wastes cycles on C-3.

---

## 3. RIGHT APPROXIMATION (Scope Creep Warnings)

I am seeing scope creep risks in the Guard & Distill sprint. Trim them down:

*   **C-11 (Test Infrastructure)**: The plan mentions Hypothesis async FSM, chaos testing, and benchmarks. **TRIM THIS**. Start strictly with OOMProtector and SoulStore invariants. Do not build a massive chaos testing suite until the core invariants are proven.
*   **C-0.5 (Scribe Agent)**: The plan calls for a full L1→L2→L3 pipeline + crash recovery. **PHASE THIS**. Build L1→L2 first using JSON Schema and LLM-as-Judge. Push L3 extraction to Phase D if it threatens the sprint timeline.
*   **V-1 (VaultCore)**: Grokster's R35 16-account schema is thorough. Extending the existing KeyVault is the correct, pragmatic move. Keep it.

---

## 4. WASTED CYCLES (Enforce the Freezes)

Ensure the fleet does not regress into these anti-patterns:

*   **NO Phase D (Living Research OS)**: Do not let anyone touch Phase D until C-0 and C-1' are 100% locked and verified.
*   **NO Grok CLI Fleet Wiring**: Keep this blocked until V-1 Vault + ACP smoke test is done.
*   **NO New Providers**: Cerebras/Groq are deferred. Keep the fabric frozen until systematized.
*   **NO Parallel Local Inference**: The hardware stats confirm 8.7GB available and an 8MB victim L3 cache. 3x local llama.cpp will thrash the cache to 2-3 t/s. Enforce the rule: ONE local inference at a time. MaKaLi MUST use cloud voices for Ma'at/Lilith.

---

## 5. ARCHITECTURAL VERDICT

The foundation is solidifying. The atomic writer (C-1') and OOMProtector (C-2') are exactly the kind of first-principles engineering this engine needed. 

Your immediate job is to clear the unowned handoffs (MCP and C-11) and prevent the Scribe agent (C-0.5) from becoming a bloated science project. Keep the team focused on the Right Approximation.

*End of Audit.*