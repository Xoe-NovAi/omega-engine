# 🔱 Account 1 Remaining Deep Dives — Prompt Reference

**AP Token**: `AP-REMAINING-DIVES-v1.0.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_remaining_dives ⬡ PHASE-E

**Account**: Account 1 — Core Architecture (`Arcana.NovAi@gmail.com`)
**Purpose**: Preserve the planned deep dive prompts so Account 1's warm context is fully leveraged before it expires.

---

## Status

| Deep Dive | Status | Completed | Report File |
|-----------|--------|-----------|-------------|
| **DD1**: Missing Files (`entity_workspace.py`, `hierarchy.py`, `gnosis_proxy.py`) | ✅ COMPLETE | 2026-05-22 | `claude-reports/01-deep-dive-1_core-arch.md` |
| **DD2**: Strategic Alignment Audit | 🟡 SENT | 2026-05-22 | *(pending receipt)* |
| **DD3**: Implementation Briefs for Critical Findings | 📋 READY | — | — |
| **DD4**: Threat Modeling — Worst-Case Scenarios | 📋 READY | — | — |
| **DD5**: Architecture Evolution — Next 1000 Lines | 📋 READY | — | — |
| **DD6**: Final Assurance Audit — Post-Remediation Capstone | 🟡 PROMPT READY (do not send before DD2) | — | `deep_dive_06_final_assurance.md` |

---

## Deep Dive 2: Strategic Alignment Audit

**Status**: ✅ ENHANCED PROMPT READY — awaiting Account 1 rate limit reset

The enhanced prompt (v2.0.0) is available at:

📄 **`docs/review/deep_dive_02_strategic_alignment.md`**

Key improvements over the original:
- **Phase 1: Reconnaissance** — forces empirical verification (run `make test`, check grep results) before analysis
- **Document Triangulation** — 4 document pairs (A/B/C/D) cross-referenced for mismatches AND gaps
- **Severity Rubric** — standardized finding format (CRITICAL/HIGH/MEDIUM/LOW/INFO) ready to slot into `FINDINGS_LOG.md`
- **Phase C Readiness Scoring** — 6-dimensional score /60 with supporting evidence
- **Edge Cases Checklist** — 5 concrete failure scenarios to manually exercise
- **Closure Criteria** — explicit exit conditions prevent premature sign-off
- **Zero-Finding Success Condition** — finding nothing is success, not failure; prevents manufactured low-value findings

**To send**: Copy `docs/review/deep_dive_02_strategic_alignment.md` into a new Web Claude conversation on Account 1.

---

## Deep Dive 3: Implementation Briefs for Critical Findings

**Status**: 📋 READY — send after DD2 report is collected

**Prompt to send (copy-paste)**:

```
For your three CRITICAL findings, produce a complete implementation brief for each:

C-ARCH-001 (EntityRegistry._save() atomicity):
- Produce the exact diff (context lines + changed lines) for entity_registry.py
- Write the test cases that verify atomicity (test_entity_registry_save_atomic, test_entity_registry_concurrent_write)
- Is there a migration concern? If entities.yaml was corrupted mid-write, can we detect and recover?

C-ARCH-002 (Double config load in Oracle.__init__):
- Produce the exact lines to delete (oracle.py:123-135)
- What assert/guard should replace them?
- Does removing this affect any caller that depends on default_entity being set before bootstrap()?

C-ARCH-003 (hierarchy.yaml dangling references):
- Produce the corrected hierarchy.yaml (just the key renames)
- What validation tests should exist to prevent regression?
- Are there any other files (not just hierarchy.yaml) that reference these keys?

For each brief, also estimate: implementation time, testing time, and risk level.
```

---

## Deep Dive 4: Threat Modeling — Worst-Case Scenarios

**Status**: 📋 READY — send after DD3 report is collected

**Prompt to send (copy-paste)**:

```
You've now deeply analyzed the core architecture. Think as a red team analyst:

a) SINGLE POINT OF FAILURE: What is the one component whose failure would take down the entire engine? What's the recovery plan?

b) CATASTROPHE SCENARIO: Walk me through exactly what happens if entities.yaml is corrupted at 3am on a Saturday. What data is lost? What can be recovered? How does the operator know?

c) INITIALIZATION ORDERING: What happens if services start in the wrong order? (e.g., Hub starts before Oracle, or Oracle starts before Redis/Qdrant). Map the dependency graph.

d) RESOURCE EXHAUSTION: The engine runs on 14GB RAM with ~12GB available. What happens under memory pressure? Which component OOM-kills first? What's the systemd restart behavior?

e) MALICIOUS WAD: If someone loads a WAD with a manifest.yaml that contains path traversal (../../etc/cronjob), what's the blast radius? Is WAD isolation sufficient?

For each scenario, rate: Likelihood (1-5), Impact (1-5), and Current Mitigation (None / Partial / Full).
```

---

## Deep Dive 5: Architecture Evolution — Next 1000 Lines

**Status**: 📋 READY — send after DD4 report is collected

**Prompt to send (copy-paste)**:

```
You've seen all the core files. If the team asked you "where should we spend the next 1000 lines of code to get the highest ROI on architecture quality," what would you recommend?

Consider:
a) Short-term wins (50-100 lines, high impact) — like the atomic write fix
b) Medium-term investments (200-500 lines) — like a proper entity schema validator
c) Long-term architecture (500-1000 lines) — like multi-backend provider abstraction or WAD dependency resolution

For each recommendation:
- What exactly would you build?
- What existing code does it replace or simplify?
- What future phases does it unblock?
- What would you DELETE as part of this change?

Be specific. "Improve error handling" is not a recommendation. "Replace the 5 hardcoded provider-entry checks in model_gateway.py with a config-driven provider registry" is.
```

---

## Deep Dive 6: Final Assurance Audit — Post-Remediation Capstone

**Status**: 🟡 PROMPT READY — use after DD2 report is collected and reviewed

This is the **capstone review** — Account 1's final word before the engine transitions to Phase C community preparation. Unlike DDs 1-5 which were targeted bug hunts, DD6 asks Account 1 to view the hardened engine through **five strategic lenses** and deliver a final verdict.

### When to Send
- **Wait for**: DD2 report to be received and integrated into context
- **Context strategy**: Send DD6 in a **new conversation** within the same Claude Project, with a brief summarizer linking all prior reports
- **Do not send before DD2**: Account 1's strategic understanding must be fully warmed

### Prompt Location
📄 **`docs/review/deep_dive_06_final_assurance.md`**

### What It Asks
| Lens | Question |
|------|----------|
| **Universal Runtime** | Does the architecture support any user's custom stack, or does it still favor Arcana-NovAi? |
| **AnyIO Architecture** | Are there residual sync-to-async boundary violations? Is the OOM protection sufficient? |
| **Gnosis Pipeline (L1→L2→L3)** | Is the reasoning-model-based distillation sustainable? Does the soul.yaml schema hold up? |
| **Error Boundaries** | What fails gracefully vs catastrophically? Are all entry points hardened? |
| **Phase C Readiness** | Rated 0-10 across 5 dimensions with specific gaps identified |

### Expected Output
1. Executive Summary (one-paragraph verdict)
2. Five Lenses — each with Insight, Suggestion, and Remaining Gap
3. What Surprised You — reflections on the post-hardening system
4. Best Advice for The Architect — strategic direction, not code
5. Final Verdict — PASS / CONDITIONAL PASS / FAIL

---

## Execution Notes

- **Send sequentially**: Each dive builds on the previous one. Don't skip ahead.
- **Save each report**: Save as `claude-reports/01-deep-dive-<N>_core-arch.md`
- **Context is warming**: Account 1's context gets richer with each dive. By DD5, it will have the deepest understanding of the architecture of any agent in the fleet.
- **Usage limit**: If Account 1 hits usage limits, wait for the reset window (typically 5 hours) before continuing.

---

*Draft your prompts. Launch them in order. Collect the gold.*
