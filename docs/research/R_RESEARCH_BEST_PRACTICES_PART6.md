<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine Autonomous Agent Research Job Design — Best Practices Guide
**AP Token**: `AP-RESEARCH-BEST-PRACTICES-v2.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp ⬡ 2026-07-24

---

## §6 Quality Gates and Evaluation

### 6.1 Forensic Context — Why Quality Gates Matter

Before quality gates were formalized, Omega Engine research suffered from:

- **Unverified claims**: Research outputs contained claims from low-credibility sources treated as fact
- **Undocumented failures**: Tool timeouts and source errors silently swallowed (M23 violation)
- **Heritage creep**: `[id-soft:]` tags added without vet records (M14 violation)
- **Theater quality**: "Looks good" outputs without measurable acceptance criteria
- **Contract violations**: Typed return values mixed with tuples/strings at call sites (M21 violation)
- **Provenance gaps**: Logs showed "local" but actual inference came from cloud (M22 violation)

**The Turning Point**: The Temple-Grade compliance push identified 12+ critical gaps across the engine. Research outputs were a key source of these gaps — unfounded claims led to incorrect implementation decisions. The quality gate system was designed to ensure research outputs are as reliable as the code they inform.

**Failure Example**: A heritage vet research output claimed "Quake used BSP culling for network optimization" without verification. The claim was later found to be inaccurate — BSP was for rendering, not networking. Without source rigor gates, this would have propagated into engine architecture decisions.

---

### 6.2 The Multi-Layered Quality Gate System

Research outputs must pass **all** applicable quality gates before being considered complete. These gates are non-negotiable and enforced via CI/CD pipelines and manual review.

#### Gate Responsibility Matrix

| Gate | Responsible | Enforced | Failure Consequence |
|------|-------------|----------|---------------------|
| **Temple-Grade (M13)** | Researcher (automated) | CI/CD | Block promotion |
| **Document Standards (M26)** | Researcher (automated) | CI/CD | Block promotion |
| **Heritage Vetting (M14)** | Researcher + Doom_Guy (review) | CI/CD + Manual | Block merge |
| **Contract Tests (M21)** | Ma'at/P3 (implementation) | CI/CD | Block merge |
| **Provenance Tracking (M22)** | Researcher (explicit) | Manual audit | Flag for review |
| **Mandate Alignment** | Researcher (explicit) + Verity (review) | Manual | Flag for review |
| **Source Rigor** | Researcher (explicit) | Manual audit | Flag for review |
| **Contrast Handling** | Researcher (explicit) | Manual review | Flag for review |

---

### 6.3 Gate 1: Temple-Grade Compliance (M13)

- **Standard**: `make temple-grade` must pass (T1-T11 gates)
- **Purpose**: Ensures enterprise-grade quality, security, resilience, observability
- **Implementation**: 
  - All research job code deliverables must include `make temple-grade` in CI
  - Failing T3 (coverage ≥80%), T5 (AnyIO-only), T6 (zero telemetry), T8 (resilience), T9 (structured logging), T10 (atomic writes) blocks promotion
  - T11 (IA2 Agent Security) exempted until specification stabilizes
- **Verification**: CI pipeline runs `make temple-grade` on pull request
- **Omega Example**: A research output recommending a new provider integration must verify the proposed code passes Temple-Grade before final submission

#### 6.3.1 Gate 1 Checklist
- [ ] `make temple-grade` passes
- [ ] T1-T10 all green
- [ ] Any T11 exemptions documented

---

### 6.4 Gate 2: Document Standards (M26)

- **Standard**: `make doc-llm-validate` must pass
- **Purpose**: Ensures LLM-friendly documentation that agents can process reliably
- **Implementation**:
  - All `.md` files in `docs/research/` and `docs/strategy/` must pass validation
  - Checks for proper structure, machine-readability, and agent-processability
  - Enforces Doc Standards: `docs/standards/DOC_STYLE_GUIDE.md` + `docs/standards/LLM_FRIENDLY_DOCS_BP.md`
- **Verification**: CI pipeline runs `make doc-llm-validate` on pull request

#### 6.4.1 Gate 2 Checklist
- [ ] `make doc-llm-validate` passes
- [ ] Document follows R_ template format (AP token, header, sections)
- [ ] File named R_DESCRIPTIVE_NAME_DATE.md
- [ ] All code blocks properly fenced with language tags

---

### 6.5 Gate 3: Heritage Vetting (M14)

- **Standard**: Every `[id-soft:]` tag in output must have corresponding vet record in `HERITAGE_VET_LOG.md` with minimum score 7/10
- **Purpose**: Ensures heritage attribution is properly vetted and justified
- **Implementation**:
  - Research job specs must include heritage tag validation in quality gates
  - CI gate `make heritage-vet` checks all heritage tags in output
  - Vet records must include: exact file:line locations, specific technique, hardware constraint, scope declaration
  - Qualification Gate: If a concept can't be justified without mentioning the original hardware constraint, it fails
- **Verification**: 
  - Automated: `make heritage-vet` CI gate
  - Manual: Verity/Doom_Guy review for complex heritage judgments

#### 6.5.1 Gate 3 Checklist
- [ ] All `[id-soft:]` tags have corresponding vet records
- [ ] Each vet record includes file:line, specific technique, hardware constraint
- [ ] Each vet record has scope declaration ("this tag applies to X, NOT to Y")
- [ ] Minimum confidence score ≥7/10 for all tags
- [ ] No unvetted heritage claims in prose (non-tagged claims still need sources)

---

### 6.6 Gate 4: Contract Tests (M21)

- **Standard**: Every typed result must be validated by at least one test verifying `isinstance(result, ExpectedType)`
- **Purpose**: Prevents runtime crashes from type mismatches; ensures API contracts are enforced
- **Implementation**:
  - For any code deliverable (scripts, modules), write unit tests in `tests/unit/`
  - Tests must use `isinstance(result, ExpectedType)` pattern
  - Mock-based tests that mask type mismatches are prohibited
  - Example: `assert isinstance(result, GenerateResult)` not `assert result == ("value", 200)`
- **Verification**: CI pipeline runs `make test`; coverage must meet T3 threshold (≥80%)

#### 6.6.1 Gate 4 Checklist
- [ ] Code deliverables have unit tests
- [ ] Tests use `isinstance(result, ExpectedType)` pattern
- [ ] No mock-based type masking
- [ ] Coverage ≥80% per T3

---

### 6.7 Gate 5: Provenance Tracking (M22)

- **Standard**: All observability logs must record the actual provider that generated a response, not the configured intent
- **Purpose**: Ensures sovereignty claims are verifiable; prevents "local-first" theater
- **Implementation**:
  - Research job specs must require provenance tracking in execution
  - All LLM calls must log `provider_name` from actual response (not `get_preferred_backend()`)
  - Metrics must include actual provider used for each call
- **Verification**: 
  - Audit research logs for `provider_name` field
  - Check that logs show actual provider (e.g., "native-gguf") not configured intent (e.g., "local_first")
  - M22 compliance verified in CI/log review

#### 6.7.1 Gate 5 Checklist
- [ ] All LLM calls include `provider_name` from actual response
- [ ] Logs show actual provider, not configured intent
- [ ] Claims attributed to verifiable sources (URLs, citations)

---

### 6.8 Gate 6: Mandate Alignment (M5, M11, M14, M17, M21)

- **Standard**: Research output must align with all mandates specified in the job spec
- **Purpose**: Ensures research contributes to mandate compliance, not technical debt
- **Implementation**:
  - Research job specs list mapped mandates in `quality_gates.mandate_cross_check`
  - Manual review verifies alignment with each mandate
  - Examples:
    - M5 (Gnosis Preservation): Does output contribute to L1→L2→L3 pipeline?
    - M11 (Soul Integrity): Does output support soul.yaml enhancement strategy?
    - M14 (Heritage Vetting): Are heritage tags properly vetted?
    - M17 (Cognitive Integrity): Does output include consistency checks and explicit applicability?
    - M21 (Gate Integrity): Are contract tests present for code deliverables?
- **Verification**: Manual review by Verity/Kali as part of quality gate process

#### 6.8.1 Gate 6 Checklist
- [ ] Output maps to specified mandates
- [ ] L3 principles extracted from findings (M5)
- [ ] Soul.yaml relevance stated (M11)
- [ ] Heritage tags properly vetted (M14)
- [ ] Consistency checks performed (M17)
- [ ] Contract tests written for code (M21)

---

### 6.9 Gate 7: Source Rigor (Internal Quality Standard)

- **Standard**: All factual claims must be cited with verifiable URLs; primary vs secondary sources distinguished
- **Purpose**: Ensures research is credible, traceable, and academically rigorous
- **Implementation**:
  - Quality gate `citation_audit`: Every factual claim cited [1], [2] + URLs
  - Quality gate `bias_detection`: Source bias checklist applied (company announcements = medium credibility)
  - Primary sources (academic papers, official docs, government standards) weighted higher than secondary (news, blogs)
  - Unverified claims marked `[UNVERIFIED]` with explanation
  - Confidence tiers enforced:
    - High (10/10): Primary sources, official docs, specifications
    - Medium (6-9/10): Industry reports, expert blogs, reputable news
    - Low (<6/10): Forums, unverified blogs, social media — **DO NOT USE as sole evidence**
- **Verification**: Manual citation audit; spot-check of URLs for verifiability

#### 6.9.1 Gate 7 Checklist
- [ ] Every factual claim cited with URL
- [ ] Primary vs secondary sources distinguished
- [ ] Low-confidence claims marked [UNVERIFIED] or excluded
- [ ] Confidence tiers assigned to all findings
- [ ] Source bias checklist applied
- [ ] Cross-reference minimum: 2 independent sources per claim

---

### 6.10 Gate 8: Contrast and Conflict Handling (Internal Quality Standard)

- **Standard**: Conflicting sources must be surfaced with attribution, not silently merged or ignored
- **Purpose**: Prevents confirmation bias; ensures intellectual honesty
- **Implementation**:
  - Quality gate `contradiction_flag`: Conflicting sources surfaced with attribution
  - Research must note where themes overlap or conflict
  - Evidence pyramid used to rank findings by strength: primary research > industry reports > expert blogs > news > forums
  - Unresolvable contradictions escalate to `escalation_triggers` in the spec
- **Verification**: Manual review for proper conflict handling; check evidence pyramid application

#### 6.10.1 Gate 8 Checklist
- [ ] All conflicting sources surfaced with attribution
- [ ] Evidence pyramid applied and documented
- [ ] Unresolvable contradictions escalated
- [ ] No silent merging of conflicting claims

---

### 6.11 Gate 9: Confidence Scoring Compliance (NEW — v2.0.0)

- **Standard**: All findings must have confidence scores with defined thresholds
- **Purpose**: Ensures output reliability is measurable and actionable
- **Implementation**:
  - Every finding includes confidence score (N/10) with source type
  - Primary source authority = source type + confidence
  - Minimum acceptance threshold defined in spec
  - Findings below threshold marked [LOW CONFIDENCE] and explained
- **Verification**: Manual confidence audit of all findings in the output

#### 6.11.1 Gate 9 Checklist
- [ ] Every finding has confidence score assigned
- [ ] Score matches source type (primary 10/10, secondary 8-9/10, etc.)
- [ ] Below-threshold findings explicitly marked [LOW CONFIDENCE] with rationale
- [ ] Confidence audit documented

---

### 6.12 Gate 10: Temporal Validity (NEW — 2026-07-24 Research)

- **Standard**: All time-sensitive findings must be date-stamped, with information half-life estimated; temporal scope declared in spec
- **Purpose**: Prevents stale information from propagating into engine architecture decisions
- **Why This Matters**:
  > "Your LLM agents are temporally blind. No model achieves >65% alignment with human time perception." (Ma et al., ACL 2026)
  > "Standard evaluation misses temporal decay entirely. DREAM's KIC metric drops from 79.35 (current) to 22.34 (1 year old) — but static benchmarks show no change." (DREAM framework, ACL 2026)
- **Implementation**:
  - All findings date-stamped with retrieval/verification date
  - Information half-life estimated for time-sensitive claims (API versions, pricing, tool availability)
  - Temporal scope declared in spec (e.g., "This research covers 2026-01-01 to 2026-07-24")
  - Re-verification scheduled for claims >7 days old
  - Sources sorted chronologically; stale sources flagged
- **Verification**: Manual audit checks date stamps, half-life estimates, and re-verification schedule

#### 6.12.1 Gate 10 Checklist
- [ ] All findings date-stamped
- [ ] Information half-life estimated for time-sensitive claims
- [ ] Temporal scope declared in research spec
- [ ] Re-verification scheduled for claims >7 days old
- [ ] "As of" dates appended to version-specific findings
- [ ] Sources checked for staleness (publication date < 30 days for fast-decay topics)

---

### 6.13 Gate 11: Meta-Research Quality — Two-Axis Evaluation (NEW — 2026-07-24 Research)

- **Standard**: Research outputs must be scored on two independent axes — **Quality** (readability, structure, depth) and **Grounding** (citation accuracy, source support) — reported as separate scores
- **Purpose**: Prevents "Mirage of Synthesis" where fluent writing masks unsupported claims
- **Why This Matters**:
  > "Current LLM judges remain unreliable — even the best models achieve overall accuracies below 55% across reasoning, tool-use, and report-quality failures." (Reflect benchmark, ACL 2026)
  > "A single overall score hides the case that matters most: a fluent, comprehensive report built on citations that don't hold up." (Dreaming Press 2026)
- **Implementation**:
  - **Quality Score** (0-100): Scored by LLM judge using task-specific rubric per query
    - Dimensions: Comprehensiveness, Insight/Depth, Instruction-Following, Readability
    - Rubric regenerated per task (not a fixed checklist)
  - **Grounding Score** (0-100): Two sub-metrics reported separately
    - Citation Accuracy (precision): % of cited sources that actually support the claim
    - Effective Citations (coverage): count of correctly-supported facts in report
  - **Critical Rule**: NEVER average the two scores into one number
  - Manual spot-check: 10 randomly selected citations verified against sources
- **Verification**: Manual audit of quality score rubric, grounding score calculation, and citation spot-check

#### 6.13.1 Gate 11 Checklist
- [ ] Quality score reported (0-100) against task-specific rubric
- [ ] Grounding score reported — two sub-metrics: citation accuracy % + effective citations count
- [ ] Two scores kept separate (not averaged)
- [ ] LLM judge prompted with task-specific rubric (not fixed checklist)
- [ ] Manual citation spot-check: 10 citations verified against sources
- [ ] Temporal validity considered in evaluation (DREAM-KIC-style checks)
- [ ] Task run ≥2 times to measure consistency (spread reported)

---

### 6.14 Evaluation Framework: Moving Beyond Binary Success

#### 6.14.1 Research Output Quality Scoring

Each research output should be scored on a 0-100 scale across 4 dimensions:

| Dimension | Weight | Scoring Criteria |
|-----------|--------|------------------|
| **Completeness** | 30% | All sub-questions answered? Gaps marked [UNVERIFIED]? All extraction targets checked? |
| **Rigor** | 30% | All claims cited? Sources verifiable? Confidence tiers applied? Conflicts surfaced? |
| **Actionability** | 25% | Consumer specified? Recommendations clear? Implementation path defined? |
| **Omega Integration** | 15% | Mandates referenced? Tools used properly? Heritage vetted? Provenance tracked? |

**Scoring Scale**:
- **90-100**: Exemplary — ready for immediate implementation
- **75-89**: Good — minor gaps, actionable with caveats
- **60-74**: Adequate — needs supplementation before implementation
- **<60**: Insufficient — requires re-execution or significant rework

#### 6.14.2 The Problem with Binary Success
> "The question shouldn't be 'Did this prompt work?,' it should be 'How often does the agent succeed?'" (Infracta 2026)

Binary success/failure hides instability and prevents meaningful improvement.

#### 6.14.3 The Success Rate Paradigm
- **Metric**: Success rate = (Number of successful executions) / (Total executions)
- **Tracking**: Continuous and repetitive evaluations that evolve over time
- **Threshold**: Target success rate defined in research job spec (e.g., ≥80% for automated jobs)
- **Application**:
  - Track success rate over time for each research job type (by quality score ≥75)
  - Use to inform Autonomy Ladder promotions (§5.13)
  - Trigger investigation if success rate drops below threshold

#### 6.14.4 Outcome Grading Over Path Grading (Infracta 2026)
> "The path that the agent takes is important, but there may be multiple paths to arrive at the correct result, so focus on outcome grading."

- **Focus**: Did the agent achieve the required outcome? Not: Did it follow a specific path?
- **Implementation**:
  - Define outcome criteria in acceptance checks (§2.4)
  - Grade based on whether outcome criteria are met
  - Allow multiple valid paths to the same outcome

#### 6.14.5 Combining Multiple Checks (Infracta 2026)
> "Most successful setups leverage a combination of deterministic tests, rubrics, and transcript reviews to cover a variety of behaviors."

- **Deterministic Tests**: Contract tests (M21), spec validation (`make doc-llm-validate`)
- **Rubrics**: Quality gate checklists (completeness, bias, citation, etc.)
- **Transcript Reviews**: Manual review of research process, decision traces, scratchpad evolution
- **Application**: Use all three layers to get comprehensive view of agent performance

#### 6.14.6 Testing Edge Cases and Adversarial Cases (Infracta 2026)
> "Test Edge Cases & Adversarial Cases: Include adversarial coverage from the start, such as jailbreak attempts, conflicts between user and system prompts, etc."

- **Implementation**:
  - Include edge cases in quality gates (e.g., what happens with malformed input?)
  - Test adversarial cases: prompt injection attempts, conflicting instructions, etc.
  - For research jobs: test with contradictory sources, ambiguous queries, incomplete data
  - **Example**: For heritage vetting, test with vague heritage tags, conflicting sources, unclear scope declarations

---

### 6.15 Actionable Reports: Shortening the Prompt-Debug Cycle

> "Actionable reports shorten the prompt-debug cycle because your team doesn't have to guess whether the issue is caused by the prompt, retrieval layer, tool schema, orchestration logic, or surrounding controls." (Infracta 2026)

#### 6.15.1 Report Structure for Debugging
Actionable research job reports should include:

| Section | Purpose | Example Content |
|---------|---------|-----------------|
| **Spec Analysis** | Was the issue in the spec? | "Spec lacked clarity on verification methodology" |
| **Retrieval Analysis** | Was the issue in source gathering? | "Missed key source due to poor query formulation" |
| **Tool Analysis** | Was the issue in tool usage? | "Agent used websearch when webfetch was needed" |
| **Context Engineering Analysis** | Was the issue in context assembly? | "Scratchpad not rewritten → conclusions diluted" |
| **Execution Pattern Analysis** | Was the wrong pattern chosen? | "Simple lookup routed to expensive deep agent" |
| **Quality Gate Analysis** | Which gates flagged issues? | "Source rigor gate: 3 claims missing citations" |
| **Omega Integration Analysis** | Did output connect to systems? | "Consumer not specified → output sits unused" |
| **Recommended Fix** | Specific, actionable improvement | "Update spec to require explicit verification step; add webfetch tool description" |

#### 6.15.2 Report Distribution
- Share actionable reports with research team after each job execution
- Use to iteratively improve research job specs and execution framework
- Track improvement in quality score over time

---

### 6.16 Quality Gate Automation Strategy

#### 6.16.1 CI/CD Pipeline Integration
```
Pull Request
    │
    ▼
{Run make doc-llm-validate}
    ├── Fail → Block PR: Doc Standards (M26)
    └── Pass → {Run make temple-grade}
                 ├── Fail → Block PR: Temple-Grade (M13)
                 └── Pass → {Run make test}
                              ├── Fail → Block PR: Contract Tests (M21)
                              └── Pass → {Run make heritage-vet}
                                           ├── Fail → Block PR: Heritage Vetting (M14)
                                           └── Pass → Manual Review
                                                        ├── Check Mandate Alignment
                                                        ├── Check Source Rigor
                                                        ├── Check Contrast Handling
                                                        ├── Check Confidence Scoring
                                                        └── Check Omega Integration
                                                             ├── Fail → Block PR: Quality Issues
                                                             └── Pass → MERGE
```

#### 6.16.2 Manual Review Focus Areas
Human reviewers focus on gates that are hard to automate:
1. **Mandate Alignment** (M5, M11, M14, M17, M21)
2. **Source Rigor** (primary vs secondary, citation quality, confidence scoring)
3. **Contrast and Conflict Handling** (proper evidence pyramid, attribution)
4. **Living Spec Principle** (was spec updated based on learning?)
5. **Actionability** (is output truly useful for intended purpose?)
6. **Omega Integration Quality** (how well does output connect to Omega systems?)
7. **Quality Score Assignment** (0-100 scoring with justifications)

#### 6.16.3 Quality Gate Thresholds

| Gate | Threshold | Enforcement |
|------|-----------|-------------|
| Temple-Grade (T1-T11) | All must pass | CI block |
| Doc Standards | `make doc-llm-validate` passes | CI block |
| Heritage Vetting | All tags have vet record ≥7/10 | CI block |
| Contract Tests | `isinstance(result, ExpectedType)` tests pass | CI block |
| Provenance Tracking | Logs show actual provider | Manual audit |
| Mandate Alignment | Manual review passes | Manual block |
| Source Rigor | Citations verifiable, primary/secondary distinguished | Manual block |
| Contrast Handling | Conflicts surfaced with attribution | Manual block |
| Confidence Scoring | All findings scored ≥6/10 or marked [LOW CONFIDENCE] | Manual audit |
| Temporal Validity (Gate 10) | All findings date-stamped; half-life estimated; scope declared | Manual audit |
| Meta-Research Quality (Gate 11) | Quality + Grounding scored separately; citations spot-checked | Manual audit |
| Quality Score | Score published with deliverable | Manual audit |

---

### 6.17 Common Quality Gate Failures

| Failure | Root Cause | Fix |
|---------|------------|-----|
| **Uncitable claims** | Agent synthesized from memory, not sources | Mandate source citation for every factual claim |
| **Heritage creep** | `[id-soft:]` tags added without vet records | Run `make heritage-vet` before submission |
| **Provenance gaps** | Logs say "local" but cloud actually used | Track `provider_name` from actual response, not config |
| **Binary success theater** | "Looks good" reported with no measurable criteria | Define acceptance checks in spec before execution |
| **No confidence scoring** | Findings from forums treated as fact | Mandate confidence tier for every finding |
| **Missing contract tests** | Code deliverables merged without isinstance checks | Add contract test requirement to all code PRs |
| **Skipped compression** | Context window overflow → agent performance degradation | Monitor window; trigger compression at 50% threshold |
| **No mandate alignment** | Research output contradicts or ignores mandates | Map mandates in spec; verify alignment in review |
| **Stale information** (NEW) | Time-sensitive findings used without date stamps | Apply Gate 10: date-stamp all findings, estimate half-life, declare temporal scope |
| **Fluent but wrong** (NEW) | Report reads well but citations don't support claims | Apply Gate 11: score Quality and Grounding separately; spot-check 10 citations |
| **Temporal blindness** (NEW) | Agent uses old context without re-verifying | Build temporal awareness into tool design (PART4 §4.10); set re-verify threshold |

---

### 6.18 Cross-Reference: How This Connects to Other Parts

| Part | Connection | How to Use Together |
|------|------------|---------------------|
| **PART1 — Core Principles** | Quality gates enforce the principles (spec-driven, quality-gated) | Read PART1 for the "why", then apply gates here for the "how"; §2.9 Temporal Awareness and §2.10 Meta-Research Quality directly feed Gates 10 and 11 |
| **PART2 — Job Design Framework** | The YAML spec specifies which quality gates apply | Fill in `quality_gates` section of the spec using this part |
| **PART3 — Context Engineering** | Quality gates check context engineering compliance | After execution, verify scratchpad writes, compression, isolation were maintained |
| **PART4 — Tool Design Principles** | Quality gates verify tool usage matches spec | Verify actual tool calls match authorized types and budgets; §4.10 Temporal Blindness Mitigation feeds Gate 10 |
| **PART5 — Execution Patterns** | Different patterns need different quality gates | Deep agents need additional gates for sub-task isolation and aggregation quality; cross-agent patterns (§5.14) need consensus verification gate |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ RESEARCH-BEST-PRACTICES ⬡ v2.0.0 ⬡ 2026-07-24*
*Part 6/6: Quality Gates and Evaluation — Enhanced with Gate 10 (Temporal Validity), Gate 11 (Meta-Research Quality / Two-Axis Evaluation), quality scoring system, gate responsibility matrix, and common failure modes*
*This guide is a living document. Updates must be made via PR with spec-driven changes.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_research_bp | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
