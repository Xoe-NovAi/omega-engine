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
| **DD2**: Strategic Alignment Audit | ✅ SENT | 2026-05-22 | *(pending receipt)* |
| **DD3**: Implementation Briefs for Critical Findings | 📋 READY | — | — |
| **DD4**: Threat Modeling — Worst-Case Scenarios | 📋 READY | — | — |
| **DD5**: Architecture Evolution — Next 1000 Lines | 📋 READY | — | — |

---

## Deep Dive 2: Strategic Alignment Audit

**Status**: ✅ SENT — awaiting report

**Prompt to send (copy-paste)**:

```
Now read the project's strategic documents:

1. https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/docs/MASTER_LEDGER.md
2. https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/docs/decisions/PIVOT_LOG.md (focus on Decisions 44, 50, 51, 52)
3. https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/config/omega.yaml

Then answer:
a) Does the current architecture support the Phase 2-4 roadmap (Multi-Provider, Stack Release, Community)? Where are the architectural blockers?
b) Cross-reference your findings against PIVOT_LOG decisions. Are any of your 17+ issues the result of a deliberate trade-off that was decided and documented? Or are these undocumented gaps?
c) Is there anything in the strategy documents that the current architecture CANNOT support without significant rework?
d) Give me a "Strategic Health Score" (1-10) for the current architecture relative to the stated roadmap. What would it take to get to a 9?
```

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

## Execution Notes

- **Send sequentially**: Each dive builds on the previous one. Don't skip ahead.
- **Save each report**: Save as `claude-reports/01-deep-dive-<N>_core-arch.md`
- **Context is warming**: Account 1's context gets richer with each dive. By DD5, it will have the deepest understanding of the architecture of any agent in the fleet.
- **Usage limit**: If Account 1 hits usage limits, wait for the reset window (typically 5 hours) before continuing.

---

*Draft your prompts. Launch them in order. Collect the gold.*
