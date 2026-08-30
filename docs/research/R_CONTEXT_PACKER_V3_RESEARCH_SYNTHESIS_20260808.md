# 🔱 Context Packer v3 — 2026 Research Synthesis Report

**AP Token**: `AP-RESEARCHER-PACKER-V3-SYNTHESIS-20260808-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ laguna-s-2.1-free ⬡ opencode ⬡ trc_synthesis ⬡ COMPLETE

**Date**: 2026-08-08
**Subject**: Comprehensive research synthesis for Context Packer v3 refactor
**Sources**: 8 web searches, 37 research articles, Grok CLI review response

---

## Executive Summary

This report synthesizes 2026 research across 9 domains relevant to the Context Packer v3 refactor. Key findings:

1. **LITM/U-shaped attention is confirmed** — critical information must be at start/end, not middle
2. **Context engineering is now a discipline** — "prompt engineering is dead; context engineering is what replaced it"
3. **Platform-specific formats matter** — Claude prefers XML tags, Gemini uses different caching, Grok has 2M token windows with reasoning modes
4. **PII detection requires multi-tier approach** — regex for patterns + NLP for context-dependent PII
5. **Ed25519 signing is mature** — python-ed25519 library provides 2ms keypair generation
6. **Testing requires golden sets + regression** — Promptfoo is the 2026 standard for CI/CD prompt testing
7. **Profile management needs config-driven discovery** — never edit Python to add a profile
8. **Pack lifecycle should be auto-tracked** — manual PACK_INDEX.md will rot

---

## Domain 1: Context Packing Best Practices (2026)

### Key Findings

**Context Engineering is the new Prompt Engineering** (Thomas Wiegold, Feb 2026):
> "The term 'prompt engineering' trivialises what we actually do. The LLM is a CPU, the context window is RAM, and your job is to be the operating system."

**PACT Framework** (Dev Note, April 2026):
```
[SYSTEM INSTRUCTIONS]        ← Always first (high attention zone)
[TASK DEFINITION]            ← Immediately after system
[SUPPORTING CONTEXT]         ← Middle (lower attention — use sparingly)
[KEY FACTS / CONSTRAINTS]    ← Late middle
[EXAMPLES]                   ← Near end
[FINAL QUERY / INSTRUCTION]  ← Always last (high attention zone)
```

**Production Best Practices** (Thomas Wiegold, Feb 2026):
1. Set explicit context budgets — define max tokens per document type
2. Compress before sending — summarize background context
3. Use context caching aggressively — any repeated system prompt should be cached
4. Monitor "needle recall" in production by injecting synthetic facts
5. Prefer structured over unstructured — JSON, markdown tables, headers improve recall
6. **Position matters** — critical constraints and examples should be near the end

**Context Utilization Testing**:
```python
def test_needle_in_haystack(client, haystack_size_tokens, needle_position):
    """Classic NIAH test: place a specific fact at position X% through context."""
    filler = generate_filler_text(haystack_size_tokens)
    needle = "The secret code is: ALPHA-7734"
    insert_idx = int(len(filler) * needle_position)
    context = filler[:insert_idx] + needle + filler[insert_idx:]
    response = client.complete(f"Context: \n{context}\n\nWhat is the secret code?")
    return "ALPHA-7734" in response.content
```

### Actionable Recommendations for Packer v3

1. **Implement the PACT framework** in `packer.py` — themes are already ordered by `litm_zone` (start/middle/end), which aligns with PACT. Ensure the ordering strategy maps correctly.

2. **Add structured context markers** — each bundle should have explicit headers (e.g., `## THEME: mandates`) to help the model navigate.

3. **Add context utilization testing** — inject a synthetic "needle" fact into a known theme and verify the model can recall it after packing.

4. **Document the PACT framework** in `SKILL.md` so packers understand the positioning rationale.

---

## Domain 2: Token Budgeting & LITM (Lost In The Middle)

### Key Findings

**The U-Shaped Attention Curve** is confirmed across multiple 2026 sources:
- Liu et al. (2023) showed U-shaped performance — accuracy highest at beginning/end, drops in middle
- Zylos Research (Jan 2026): "Even at 4K tokens, accuracy can drop from 75% to 55-60%"
- Atlan (June 2026): "Model accuracy on retrieval and reasoning tasks is highest when relevant information is at the start or end of the context"

**Key Metrics**:
- Retrieval accuracy: 85-95% for first 10% of context, drops to 55-70% in middle, recovers to 80-90% in last 10%
- With 20 retrieved documents (~4K tokens), accuracy drops from 70-75% to 55-60%

**Mitigation Strategies** (QubitTool, April 2026):
1. **Instruction Placement** — Put critical instructions at start/end, never middle
2. **Document Reordering** — Most relevant documents at beginning and end
3. **Chunking and RAG** — Reduce irrelevant evidence
4. **Prompt Compression** — Compress background context
5. **Chain of Thought Extraction** — Extract reasoning chains

**Pause-Tuning** (ArXiv, Feb 2026):
- Insert `<PAUSE>` tokens after each paragraph to segment input
- Redistributes attention more evenly
- 35× speedup for 2M context on H100 GPUs

### Actionable Recommendations for Packer v3

1. **Enforce LITM-aware ordering** — The current `litm_zone` field (start/middle/end) is correct. Ensure `start` themes contain the most critical information (mandates, core engine), `end` themes contain the final query/instructions, and `middle` themes contain supporting context.

2. **Add LITM validation to contract tests** — Test that required themes are in `start` or `end` zones, not buried in `middle`.

3. **Consider token budget allocation** — Allocate more budget to `start` and `end` zones, less to `middle`. Current schema has `per_bundle` which is per-theme, not per-zone.

4. **Document the LITM rationale** in SKILL.md — explain why `litm_zone: start` matters for attention.

5. **Add a `--litm-test` flag** to packer that injects a synthetic fact and verifies retrieval.

---

## Domain 3: Profile/Config Management Patterns

### Key Findings

**The Problem**: Monolithic 15-profile YAML mixes egress ship packs, platform demos, and internal/node packs.

**Grok CLI's Recommendation** (review response):
- **Option A (Minimal)**: Keep one file, add `tier:` field. `pack()` / CLI default lists `tier: ship`. Templates loadable via `--config` or `--tier template`.
- **Option B (Three directories)**: Acceptable if loader merges or accepts `--config` path. **Commit** internal profiles; gitignore only `profiles/local/`.

**Better Method Than Hacking .py**:
1. YAML (or copy-from-template)
2. `curate_packs.py --check`
3. `packer.py <name>`

**Platform Template Dedupe**:
- `web-claude-sonnet5`, `web-grok-4.3`, `web-gemini-3-pro`, `notebooklm-research` share nearly the same include/theme body
- Prefer **one** `context-packer-self-review` template + thin **platform overlay** (format/budget/slots only)

### Actionable Recommendations for Packer v3

1. **Implement `tier:` field** in packer-config.yaml (Option A preferred):
   ```yaml
   profiles:
     sovereign-audit:
       tier: ship
     web-claude-sonnet5:
       tier: template
     engineering-p3:
       tier: internal
   ```

2. **CLI lists profiles dynamically from config** — never hardcoded. Default to `tier: ship`, with `--all` or `--tier` for others.

3. **Add template dedupe** — Create `context-packer-self-review` template, then thin platform overlays for format/budget/slots.

4. **Fix all 16 ghost references** to `enhanced_packer.py` before Phase 3.

5. **Commit internal profiles** — don't gitignore `kali-oversight`, `engineering-p3`, etc.

---

## Domain 4: PII Detection & Masking

### Key Findings

**Four Insertion Points** (TrueFoundry, May 2026):
1. User input (what the user types)
2. RAG-retrieved context (documents pulled into prompt)
3. Tool outputs (results from function calls)
4. System context (system prompts, instructions)

**Detection Approaches**:
1. **Regex-based** (fast, catches known patterns: emails, phones, API keys, credit cards)
2. **NLP-based** (Microsoft Presidio, spaCy — catches PERSON names, addresses)
3. **LLM-based** (most accurate but expensive — use as Tier 4)

**Masking Strategies** (OneUptime, Jan 2026):
- **Redact**: Replace with generic placeholder (for logs)
- **Mask**: Partial hiding (for display)
- **Hash**: One-way transformation (for analytics)
- **Replace**: Entity placeholders (for LLM context) — `<PERSON_1>`, `<PHONE_1>`
- **Encrypt**: Reversible transformation (for recovery)

**Production Pipeline** (DevOpsBoys, July 2026):
```
Input → PII Detection Engine → {Contains PII?} → Mask → LLM API → Check Response → Unmask → Output
```

**pii-guard** (AlphaOfTech, Feb 2026):
- 10MB/sec throughput
- Zero external calls (all local)
- Single dependency (Click)
- Built-in API key detection for 10+ providers

### Actionable Recommendations for Packer v3

1. **Implement multi-tier PII detection**:
   - Tier 1: Regex for known patterns (API keys, emails, phones, credit cards)
   - Tier 2: Presidio/NLP for PERSON names, addresses
   - Tier 3: LLM-based for context-dependent PII (optional, expensive)

2. **Use replace-with-placeholders strategy** for LLM context:
   - `<PERSON_1>`, `<PHONE_1>`, `<EMAIL_1>` — unique, typed placeholders
   - Maintain reverse mapping for unmasking

3. **Scan all four insertion points**:
   - User input (already handled by platform)
   - RAG-retrieved context (packer's file content)
   - Tool outputs (packer's metadata)
   - System context (packer's manifest)

4. **Fail-closed on PII import error** — if PIIMasker import fails, refuse to pack (current behavior is correct).

5. **Add PII audit logging** — log what was masked for compliance.

---

## Domain 5: XML Escaping & Ed25519 Signing

### Key Findings

**XML Special Characters** (Indentio, July 2026):
| Character | Write instead | Must be escaped |
|-----------|---------------|-----------------|
| `&` | `&amp;` | Everywhere (text and attributes) |
| `<` | `&lt;` | Everywhere (text and attributes) |
| `>` | `&gt;` | Only in sequence `]]>` |
| `"` | `&quot;` | Inside double-quoted attributes |
| `'` | `&apos;` | Inside single-quoted attributes |

**CDATA sections** for code samples:
```xml
<description><![CDATA[
  if (a < b && b > 0) { launch(); }
]]></description>
```

**Ed25519** (OpenSSL docs, python-ed25519):
- EdDSA signature scheme using Curve25519
- 2ms keypair creation/verification
- Sign and verify messages with private/public key pairs
- PureEdDSA: requires complete message (not digest)

**python-ed25519** (warner/python-ed25519):
- MIT license
- Quick keypair creation, derive verifying key, sign/verify
- Single dependency

### Actionable Recommendations for Packer v3

1. **Keep existing XML escaping** — `_escape_bare_xml_chars` is correct per XML spec.

2. **Keep Ed25519 signing** — python-ed25519 is mature and fast (2ms).

3. **Add CDATA for code blocks** — if any theme file contains code samples, wrap in CDATA.

4. **Document the signing process** in SKILL.md — explain how to verify pack integrity.

5. **Add signature verification to curate_packs.py** — verify existing pack signatures before allowing regeneration.

---

## Domain 6: Pack Lifecycle Management

### Key Findings

**Context Caching** (Zylos Research, Jan 2026):
- **Anthropic (Claude)**: Requires explicit `cache_control` headers, two cache durations (5-min, 1-hour)
- **Google (Gemini)**: Supports implicit and explicit caching, configurable TTLs up to 1 hour
- **OpenAI**: Automatic caching for prompts >1,024 tokens, static content at beginning
- **Effectiveness**: 90% savings on repeated context

**Pack Lifecycle Tracking** (Grok CLI review):
- Manual `PACK_INDEX.md` will rot like CLI lists
- Packer should **auto-write** `context_packs/PACK_INDEX.json` on each successful pack
- Fields: pack name, generated_at, packer_version, config_hash, source_file_hashes, delivered, platform_target

**Freshness Detection**:
- Compare current source file hashes against last pack's hashes
- If changed → recommend regeneration
- If unchanged → allow cached pack

### Actionable Recommendations for Packer v3

1. **Auto-write PACK_INDEX.json** on each successful `pack()`:
   ```json
   {
     "pack": "sovereign-audit",
     "generated_at": "2026-08-08T14:30:00Z",
     "packer_version": "3.0.0",
     "config_hash": "sha256:...",
     "source_file_hashes": { "SOVEREIGN_MANDATES.md": "sha256:...", ... },
     "delivered": false,
     "platform_target": "web-claude"
   }
   ```

2. **Add `--check-freshness` flag** to packer — compares current source hashes against last pack's hashes.

3. **Add `--list-packs` flag** — shows all packs with status (generated, delivered, stale).

4. **Document the lifecycle** in SKILL.md — generation, delivery, freshness check, regeneration.

---

## Domain 7: Testing Strategies for Context Packers

### Key Findings

**Promptfoo** (QASkills, May 2026; Promptfoo docs, Aug 2026):
- Open-source CLI for LLM prompt testing
- YAML configs, assertions, model comparisons
- CI/CD integration with GitHub Actions, GitLab CI
- JUnit XML output for native CI test-report viewers
- Red teaming for security testing

**Testing Philosophy** (Thomas Wiegold, Feb 2026):
- "Prompts are code — treat them like it"
- Version control your prompts
- Build a golden test set: representative inputs with expected outputs
- Run it on every prompt change (regression testing)

**Testing Anti-Patterns** (PromptQuorum, April 2026):
- ❌ Grading with the same LLM you're testing (self-evaluation inflates scores 10-20%)
- ❌ Ignoring latency and cost in eval
- ❌ No regression testing

**Contract Testing** (from handoff §3.2):
- Every core API boundary must have a "Contract Test" that verifies `isinstance(result, ExpectedType)`
- Mock-based tests can mask runtime crashes

### Actionable Recommendations for Packer v3

1. **Extend contract tests** with semantic assertions (Phase 1):
   - `test_budget_from_platform_config` — enforcement uses profile budget
   - `test_over_total_budget_raises` — no trim; hard fail
   - `test_required_theme_missing_raises` — missing required theme → fail
   - `test_max_slots_includes_manifest` — on-disk file count ≤ max_slots
   - `test_litm_zone_ordering` — start themes before middle before end
   - `test_no_keyword_priority_side_effects` — theme named "mandates" not special-cased

2. **Use fixture configs** (`tests/fixtures/context_packer/test-profile.yaml`) — tiny explicit files, not production config.

3. **Add Promptfoo integration** for LLM-level testing:
   - Test that packed context produces correct LLM responses
   - Golden test set: known inputs → expected outputs
   - CI/CD gate: fail if regression >10%

4. **Add context utilization testing**:
   - Inject synthetic "needle" fact into a theme
   - Pack context
   - Verify LLM can recall the fact
   - This tests both packing correctness and LITM positioning

5. **Use different models for grading** — test with Claude, grade with GPT (or vice versa).

---

## Domain 8: Platform-Specific Constraints

### Key Findings

**Claude (Anthropic)** (Thomas Wiegold, Feb 2026; Claude Code docs, Aug 2026):
- XML tags (`<instructions>`, `<context>`, `<example>`) are the best structuring method
- Aggressive language ("CRITICAL!", "YOU MUST") actively hurts newer Claude models
- Prompt caching: explicit `cache_control` headers, 5-min and 1-hour durations
- 90% cost savings with caching
- CLAUDE.md: persistent context loaded every session
- Context window: ~200K tokens (Sonnet 4.5), ~2M tokens (Opus 4.8)

**Gemini** (Datalakehousehub, March 2026; AI.Google.dev):
- Context window: up to 2M tokens (Gemini 3 Pro)
- Supports implicit and explicit caching, configurable TTLs up to 1 hour
- NotebookLM (now Gemini Notebook): source-grounded research tool
  - PDFs work well for NotebookLM (extracts and indexes content)
  - Markdown/text for clean AI-parseable context
  - Enterprise API: Gemini Notebook Enterprise (REST endpoints)
  - July 2026: Renamed from NotebookLM to Gemini Notebook

**Grok (xAI)** (DataStudios, April 2026; xAI docs, July 2026):
- Grok 4.20: 2,000,000-token context window
- Grok 4: 256,000-token context window (billed at higher rate >128K)
- Grok 4 Fast: 2,000,000 tokens, $0.20/M input, $5/M output
- Reasoning modes: low, medium, high (default high)
- Encrypted reasoning state: can be returned via Responses API
- Interleaved tool calling during thinking
- Rate limits: 2M tokens/minute, 480 requests/minute (Grok 4)
- Stateless memory design — applications must maintain their own memory store

**NotebookLM / Gemini Notebook** (Glasop, Aug 2026):
- Renamed July 2026
- Source-grounded responses (only answers from uploaded sources)
- Audio Overviews: podcast-style discussions of sources
- Enterprise API available (Gemini Notebook Enterprise)
- Community clients exist but can break anytime

### Actionable Recommendations for Packer v3

1. **Platform-specific format adapters** (already in `platform_adapters.py`):
   - Claude: XML tags for structuring, calm language, prompt caching
   - Gemini: Markdown/text preferred, caching support
   - Grok: Large context OK, but cost-aware (2M tokens but metered)
   - NotebookLM: Source-grounded — ensure all sources are included

2. **Add platform-specific budget overrides**:
   - Claude: 150K total, 15K per bundle (current sovereign-audit)
   - Grok 4 Fast: 2M total (but cost-aware)
   - Gemini: 2M total (but cost-aware)

3. **Add platform-specific LITM positioning**:
   - Claude: instructions at start/end, examples near end
   - All platforms: critical info at start/end, not middle

4. **Document platform constraints** in SKILL.md:
   - Claude: XML tags, calm language, caching
   - Grok: 128K threshold for extended pricing
   - NotebookLM: source-grounded only

5. **Add `--platform` flag** to packer that selects platform-specific defaults.

---

## Domain 9: Additional Insights from Grok CLI Review

### Key Corrections to Researcher's Analysis

1. **"Circular dependency" is inaccurate** — it's content self-inclusion / maintenance coupling, not a runtime deadlock.

2. **Phase 0.5 is NOT a hard prerequisite for Phase 1** — fixture tests must not depend on production config cleanliness.

3. **Don't gitignore internal profiles** — commit them; gitignore only `profiles/local/` or `*.local.yaml`.

4. **Ship path = 2 packs** — `sovereign-audit` and `tech-architecture-research`. `provider-fabric-review` is valid but not critical path.

5. **PACK_INDEX should be packer-emitted** — not hand-maintained markdown.

6. **Platform template dedupe** — prefer one `context-packer-self-review` template + thin platform overlays.

7. **Fat globs remain the primary product bug** — `docs/strategy/**` and `oracle/**` in ship profiles.

8. **Effort estimate realism** — full 3-dir split is 2-3h, not 30-60min. Quick hygiene (0.5a) fits in 30-60min.

### Actionable Recommendations

1. **Split Phase 0.5** into 0.5a (hygiene, parallel Phase 1) + 0.5b (taxonomy, optional/late).

2. **DoD split**: P0 (items 1-8) = product; P1 (items 9-13) = hygiene.

3. **Fix ghosts + dynamic CLI** in <30 min without directory churn.

4. **Archive provider-fabric-review output** — move to `context_packs/archive/`.

5. **Don't block v3 core on PACK_INDEX or 3-tier dirs**.

---

## Integrated Recommendations for Packer v3

### Priority 1 (P0 — Must ship)

1. **Delete split/trim/keyword-priority/consolidate pipeline** — no runtime theme drop
2. **Implement fail-closed budgets** — over budget → `[PACK-FAIL]`, no silent success
3. **Wire budgets from config** — `token_budget.total` and `token_budget.per_bundle` must drive packer
4. **Fix max_slots off-by-one** — `len(bundles) + 1(manifest) <= max_slots`
5. **Add `required` + `litm_zone`** — not `priority: 1|2|3`
6. **Fix 16 ghost references** to `enhanced_packer.py`
7. **Fix CLI** — dynamic profile list from config, correct usage string
8. **Regenerate 2 ship packs** — `sovereign-audit` (≤12 files, all required themes), `tech-architecture-research` (protect hand-built md)

### Priority 2 (P1 — Hygiene, not blocking)

1. **Add `tier:` field** to profiles (Option A) OR split to directories (Option B)
2. **Create template dedupe** — one `context-packer-self-review` + platform overlays
3. **Auto-write PACK_INDEX.json** on successful pack
4. **Archive provider-fabric-review output**
5. **Update SKILL.md** with v3 pipeline, tier field, fail-closed policy
6. **Add platform-specific format adapters** in platform_adapters.py

### Priority 3 (Future — Not in this sprint)

1. **Add context utilization testing** — needle-in-haystack with LITM positioning
2. **Add Promptfoo integration** for LLM-level regression testing
3. **Add freshness detection** — compare source hashes against last pack
4. **Add `--platform` flag** with platform-specific defaults
5. **Add PII multi-tier detection** — regex + NLP + LLM

---

## Research Sources

| Source | URL | Date |
|--------|-----|------|
| Context Engineering for Production LLM Agents | appscale.blog | 2026-06-23 |
| Token Budget Planning & Execution | explainx.ai | 2026-06-28 |
| LLM Context Window Management | zylos.ai | 2026-01-19 |
| Lost-in-the-Middle Problem | atlan.com | 2026-06-10 |
| U-shaped Attention Curve | harnez.ai | 2026-05-11 |
| LLM Context Windows Explained | swfte.com | 2026-08-04 |
| PII Detection and Masking | devopsboys.com | 2026-07-02 |
| PII Detection for LLMOps | onestuptime.com | 2026-01-30 |
| pii-guard: Context-Aware PII Detection | alphaoftech.io | 2026-02-11 |
| Ed25519 Signing Walkthrough | ed25519.com | — |
| python-ed25519 | github.com/warner/python-ed25519 | — |
| XML Special Characters | indentio.dev | 2026-07-12 |
| Prompt Engineering Best Practices | thomas-wiegold.com | 2026-02-21 |
| Promptfoo CI/CD Integration | promptfoo.dev | 2026-08-01 |
| Prompt Testing & Evaluation Tools | promptquorum.com | 2026-04-10 |
| Grok Context Window | datastudios.org | 2026-04-19 |
| Grok 4.5 API Docs | docs.x.ai | 2026-07-08 |
| Gemini Notebook | glasp.co | 2026-08-01 |
| Context Management for Gemini/NotebookLM | datalakehousehub.com | 2026-03-07 |
| Claude Code Best Practices | code.claude.com | 2026-08-07 |
| Claude Code Best Practices (rosmur) | rosmur.github.io | — |
| LLM Context Window Exceeded | buzhou.io | 2026-06-28 |
| Found in the Middle (ArXiv) | arxiv.org | 2024-06-23 |
| Pause-Tuning for LITM (ArXiv) | arxiv.org | 2025-09-21 |
| Context Is What You Need (ArXiv) | arxiv.org | 2025-09-21 |
| **Grok CLI Review Response** | data/handoff/GROK_CLI_RESEARCHER_ADDITION_REVIEW_RESPONSE_20260808.md | 2026-08-08 |

---

## Conclusion

The Context Packer v3 refactor is well-supported by 2026 research. The core bug (silent theme deletion) is confirmed as a critical failure. The proposed v3 architecture (config-as-SSOT, fail-closed budgets, curate_packs.py) aligns with industry best practices for context engineering.

The Researcher's additions (§16-17) are validated by Grok CLI's adversarial review, with important corrections:
- Phase 0.5 should be split (not a hard gate)
- Internal profiles should be committed (not gitignored)
- PACK_INDEX should be auto-written
- Platform template dedupe is needed

The integrated recommendations prioritize the P0 product DoD (8 items) over P1 hygiene (5 items), ensuring the packer is fixed before process improvements.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ laguna-s-2.1-free ⬡ opencode ⬡ trc_synthesis ⬡ 2026-08-08 ⬡ Context Packer v3 research synthesis complete*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: laguna-s-2.1-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
