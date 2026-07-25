# 🔱 OMEGA ENGINE — PHASE C HARDENING GAME PLAN
**AP Token**: `AP Token**: `AP-GAME-PLAN-v1.0.0`  
**Date**: 2026-07-21  
**Entity**: kali (Sprint Coordinator)  
**Status**: Research Complete — Ready for Execution  

---

## PART 4B: WEEK 3 CONTINUATION & SUMMARY

### 📋 **WEEK 3 SUMMARY (CONTINUED)**
| Day | Ticket | Owner | Status |
|-----|--------|-------|--------|
| Mon | C-3    | Kali + Architect | **DEPENDS ON ARCHITECT DECISION** |
| Tue | V-1    | Researcher + P3 | **READY AFTER C-0** |
| Wed | E-0    | Kali | **READY AFTER C-1′** |
| Thu | D-1    | Verity/P10 | **READY AFTER C-11** |
| Fri | D-2/D-3| Verity/P10 | **READY AFTER C-11** |

### 🎯 **PHASE C COMPLETION CRITERIA**
**Phase C is complete when ALL of the following are true**:
1. ✅ **C-0**: `make test` output matches `C0_TEST_RESULTS_*.json` (no more "276/276" lies)
2. ✅ **C-1′**: Only one thread/process can write `soul.yaml` (verified via `lsof` + audit logs)
3. ✅ **C-2′**: `OOMProtector::can_allocate()` returns `false` at ~8GB available (not 12GB)
4. ✅ **C-11**: Test infrastructure passes:
   - Fixtures: `tests/fixtures/` populated with realistic data
   - Chaos: `pytest -xvs tests/chaos/` runs without killing essential services
   - Benchmarks: `tests/benchmarks/` show performance baselines
   - MCP matrix: `tests/mcp_compatibility/` validates all 60+ tools
5. ✅ **Gate to Phase D**: All four above are GREEN

### 📊 **METRICS TO TRACK**
| Metric | Target | Measurement Tool |
|--------|--------|------------------|
| Test Honesty | 0 "276/276" lies | `make test` output vs JSON |
| Soul Write Safety | 0 concurrent writes | `lsof | grep soul.yaml` |
| RAM Truth Accuracy | ±5% vs `/proc/meminfo` | OOMProtector readings |
| Test Infrastructure Coverage | ≥80% line coverage | `pytest --cov=src/omega` |
| MCP Tool Compatibility | 100% of 60+ tools work | `tests/mcp_compatibility/` |
| False Positives (C-2′) | <1% | Benign allocations blocked |
| False Negatives (C-2′) | 0% | OOM situations caught |

### 🚨 **KNOWN RISKS & MITIGATIONS**
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-------------------|
| Architect delays C-3/mcp_compatibility/` |
| False Positives (C-2′) | <1% | Benign allocations blocked |
| False Negatives (C-2′) | 0% | OOM situations caught |

### 🚨 **KNOWN RISKS & MITIGATIONS**
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Architect delays C-3 decision | Medium | High | Proceed with default Tiered Sovereignty; revise if needed |
| C-2′ OOMProtector false negatives | Low | Critical | Add double-check: `if available() < 0: emergency_halt()` |
| C-1′ actor model deadlock | Low | High | Use timeout on mailbox; fallback to queue |
| C-11 test infrastructure scope creep | Medium | Medium | Strict definition: fixtures + chaos + benchmarks + MCP matrix |
| MCP audit takes >7 days | Low | High | File-based Hivemind contingency verified as fallback |
| Week 3 tasks exceed estimate | Medium | Medium | Descope D-2/D-3 to MVP if needed |

### 📁 **ARTIFACTS TO PRODUCE**
By end of Phase C, these artifacts must exist:
```
/docs/strategy/
├── SOVEREIGN_ARK_BLUEPRINT.md          # Updated v5.2
├── IMPLEMENTATION_MANUAL_C0_C2.md      # Updated with all tickets
├── GAME_PLAN_PART1.md                  # This file (PART 1)
├── GAME_PLAN_PART2.md                  # Week 1 execution
├── GAME_PLAN_PART3.md                  # Week 2 execution  
├── GAME_PLAN_PART4A.md                 # Week 3A execution
└── GAME_PLAN_PART4B.md                 # Week 3B execution (this file)

/docs/research/
├── R_RESEARCH_GAPS_REPORT_PART1.md
├── R_RESEARCH_GAPS_REPORT_PART2.md
├── R_RESEARCH_GAPS_REPORT_PART3.md
├── R_RESEARCH_GAPS_REPORT_PART4A.md
└── R_RESEARCH_GAPS_REPORT_PART4B.md

/data/coordination/
├── C0_TEST_RESULTS_*.json
├── C0_C2_C11_COMPLETION_TIMESTAMPS.md
└── PHASE_C_COMPLETION_SIGNATURES.md

/src/omega/
├── resource/oom_protector.rs             # C-2′
├── soul/actor.rs                         # C-1′
├── admission/local_admission.rs          # C-10
├── soul/privacy_gate.py                  # C-3 (if approved)
├── generation/policy.py                  # C-9
├── search/content_cache.py               # D-1
├── workers/background_researcher/job_store.py  # D-2
└── workers/background_researcher/index_builder.py  # D-3
```

### ✅ **DEFINITION OF DONE FOR EACH TICKET**
| Ticket | Done When |
|--------|-----------|
| **C-0** | `make test` output matches JSON fixture; no hardcoded counts in Makefile |
| **C-1′** | Only one writer to soul.yaml verified via `lsof` + no race conditions in stress test |
| **C-2′** | OOMProtector returns false at 8.0GB ±0.5GB; true at 7.5GB |
| **C-5** | config/makali.yaml reflects Kali-local/Ma'at+Lilith-cloud routing |
| **C-6′** | ≥6 breaker duplicates removed; single implementation used everywhere |
| **C-7** | 0 synchronous `yaml.safe_load` calls in async context (grep -r verified) |
| **C-8** | Every `[id-soft:]` tag has corresponding vet record in HERITAGE_VET_LOG.md |
| **C-9** | No hardcoded generation parameters in oracles/model_gateway/etc. |
| **C-10** | System rejects 3rd concurrent 7B model; queues excess requests |
| **C-11** | Tests/fixtures/ populated; tests/chaos/ passes; tests/benchmarks/ has baselines; tests/mcp_compatibility/ passes |
| **E-0** | Agent config reflects soul kernel values after soul update |
| **V-1** | Design document signed off by Researcher + P3 |

### 📅 **FINAL TIMELINE SUMMARY**
```
WEEK 1 (JUL 21-25): FOUNDATION
  MON: C-0 (Test Honesty) → Establish honest baseline
  TUE: C-2′ (OOMProtector) → RAM truth enables safe memory ops
  WED: C-1′ (SoulStore Actor) → Safe writes with truthful RAM
  THU: C-10 (Admission Control) → Prevent overload (1 large + 1 small model)
  FRI: C-5 (MaKaLi Config) + C-4a MCP Audit Start

WEEK 2 (JUL 28-AUG 1): HARDENING
  MON: C-11 (Test Infrastructure) → New P0 for Phase D gate
  TUE: C-6′ (Breaker Unify) → Eliminate duplicates
  WED: C-7 (YAML Audit) → Fix 57 sync calls in async context
  THU: C-8 (Heritage Vet) → Clear 100+ unvetted tags
  FRI: C-9 (GenerationPolicy) → Extract from god classes

WEEK 3 (AUG 4-8): PREP FOR PHASE D
  MON: C-3 (Privacy Model) → Tiered Sovereignty (if approved)
  TUE: V-1 (Vault Design) → Credential/session automation MVP
  WED: E-0 (Identity Fluidity) → Soul kernel → agent config
  THU: D-1 (Content Persistence) → .firecrawl/ cache with TTL
  FRI: D-2/D-3 (Job Board + Indexing) → SQLite queue + initial index
```

### 🚦 **NEXT IMMEDIATE ACTIONS**
1. **Post Hivemind claims** for C-0, C-2′, C-11
2. **Request Architect decisions** on C-3/V-1/MCP by EOD
3. **Start C-2′ OOMProtector implementation** (blocks everything else)
3. **Begin C-4a MCP audit** (7-day clock started)

### ❓ **Questions for User Direction**
1. Shall I proceed with posting the Hivemind claims for C-0, C-2′, C-11 now?
2. Should I start the C-2′ OOMProtector implementation immediately?
3. Do you want me to begin the C-4a MCP audit code inventory in parallel?
4. Do you want me to create the V-1 design document outline now?

**Ready for your direction on final steps.** 🚀