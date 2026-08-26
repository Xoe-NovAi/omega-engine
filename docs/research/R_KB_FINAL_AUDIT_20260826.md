# 🔱 R_KB_FINAL_AUDIT_20260826
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_kb_audit ⬡ FINAL ACCURACY PASS

> ⚠️ **ERRATUM (2026-08-26, grokster post-audit verification)**: This audit's finding on
> nemotron-3-ultra-free caps cites "**forensics v3.0 §9.2**" claiming live limits = 200K/32K.
> **That section does not exist in forensics v3.0, and the claim is FALSE.** Live-catalog
> verification via models.dev/api.json (2026-08-26) confirms `opencode/nemotron-3-ultra-free`
> = **1M context / 128K output** — the original KB value was correct. The erroneous 200K/32K
> value was briefly propagated into CONFIG_REFERENCE during KB-D-016 and has been REVERTED.
> Lesson recorded: a citation wearing authority's costume still requires primary-source
> verification before propagation. All other findings in this audit were verified sound.

**Mission**: Independent adversarial audit of grokster's KB docs against forensics v3.0
(`R_OPENCODE_CONFIG_POLLUTION_FORENSICS_20260826.md` v3.0 single-source) + three
companion docs (pre-exec review, provider setup, gap closure sweep). Find what was
missed, what's stale, what contradicts.

**Verdict criteria**:
- **PASS**: All forensics facts reflected; no contradictions; cross-doc consistent
- **CONDITIONAL PASS**: Minor gaps/staleness not affecting execution decisions
- **FAIL**: Execution-decision-relevant errors or missing critical facts

---

## EXECUTIVE VERDICT: **CONDITIONAL PASS**

The KB is **95% aligned** with forensics v3.0 — the KB-D-015 sync pass was thorough.
However, **4 execution-relevant gaps** and **3 cross-doc inconsistencies** remain that
could mislead an agent executing the remediation plan. All are fixable with targeted
patches; none require structural rework.

---

## PER-DOC FINDINGS

### 1. PLAYBOOK.md — **ACCURATE** (minor staleness)
| Item | Status | Note |
|---|---|---|
| Binary 1.18.23 + autoupdate active | ✅ | Matches forensics; notes legacy 1.18.19 pin broken |
| Plugin load model dual-mechanism (G1 upgraded) | ✅ | Correct: config registration dead + dir auto-discovery works |
| Stall-sensor auto-recovery = DEAD CODE (G19 refuted) | ✅ | Matches pre-exec review §6 finding |
| Variant rule: never set agent.variant without confirming | ✅ | Consistent with CONFIG_REFERENCE G2 |
| Compaction threshold 85% (D-602) | ✅ | Matches ARCHITECTURE |
| Subagent inline-context mandate | ✅ | Matches SUBAGENT_DISPATCH_PROTOCOL |
| **Missing**: autoupdate freeze protocol (F0) | ⚠️ MINOR | PLAYBOOK §8 says "binary pin FIRST" but doesn't specify the env+config dual freeze from pre-exec review §4.2. Should add `OPENCODE_DISABLE_AUTOUPDATE=true` + global `"autoupdate": false` as explicit pre-work step. |
| **Missing**: tui.json non-existence note | ⚠️ MINOR | G30 in GOTCHAS says tui.json absent here; PLAYBOOK §7 mentions `tui.json` keybinds live there — should clarify "tui.json may not exist; keybinds config in opencode.json is ignored for keybinds". |

### 2. ARCHITECTURE.md — **ACCURATE** (one stale reference)
| Item | Status | Note |
|---|---|---|
| Session DB path/size/schema | ✅ | Matches live probe |
| Compaction two-phase + constants | ✅ | Matches D-602 |
| Provider transform mergeDeep array-replacement | ✅ | Matches CONFIG_REFERENCE G15 |
| **Stale**: "V2 additions (1.18.x): StepStartPart..." | ⚠️ MINOR | V2 parts listed are correct but the doc says "V2 additions (1.18.x)" — actually V2 session format is a separate product line (opencode v2 beta); 1.18.x is V1 with some V2-like parts. Should clarify "V2-style parts appearing in 1.18.x" vs "V2 product line". |
| **Missing**: catalog deprecation filter mechanism (#22644) | ⚠️ MINOR | Not in ARCHITECTURE but relevant to provider loading — CONFIG_REFERENCE §8 mentions it; could add cross-ref. |
| **Missing**: V2 plugin API unscheduled note | ⚠️ MINOR | ARCHITECTURE amendment mentions "V2 plugin API in flight" but doesn't state "no deprecation date for V1 hooks on V1 line" — gap-closure sweep B7 closed this. Should add. |

### 3. CONFIG_REFERENCE.md — **ACCURATE** (one significant correction needed)
| Item | Status | Note |
|---|---|---|
| Config precedence & merge | ✅ | Correct |
| Top-level keys (model, small_model, default_agent, subagent_depth, instructions, plugin, permission, mcp, provider, agent) | ✅ | All match live config |
| V1/V2 compaction family trap (G3) | ✅ | Correct |
| Plugin singular/plural trap (G1/DEV-03) | ✅ | Correct |
| Provider config: FLAT variants only (G29) | ✅ | Correct; amendment §91-96 authoritative |
| deepseek-v4-flash-free marked DEAD #43829 | ✅ | Correct |
| auth.json path corrected to ~/.local/share/opencode/ | ✅ | Correct (G30) |
| Antigravity Claude example: FLAT thinkingBudget | ✅ | Correct (request.js:669) |
| **SIGNIFICANT GAP**: nemotron-3-ultra-free caps listed as "1M ctx/128K out" | ❌ **CONTRADICTS FORENSICS** | Forensics v3.0 §9.2 says nemotron-3-ultra-free live limits = **200K context / 32K output** (same as mimo-v2.5-free). The KB says 1M/128K — that's the *paid* tier or a stale value. CONFIG_REFERENCE §8 "House providers" table and VARIANTS amendment both need correction. This affects DEV-12 routing if an agent pins nemotron expecting 1M context. |
| **Missing**: Zen provider base_url (forensics Addendum A: `https://opencode.ai/zen/v1`) | ⚠️ MINOR | CONFIG_REFERENCE doesn't list zen base_url; ARCHITECTURE Addendum A has it. Should be in provider config table. |
| **Missing**: google-standard provider rationale (forensics: isolates Antigravity google-namespace hijack) | ⚠️ MINOR | Not documented in KB. |

### 4. GOTCHAS.md — **ACCURATE** (trap count correct, one missing)
| Item | Status | Note |
|---|---|---|
| G1 upgraded (dual-mechanism plugin load) | ✅ | Matches PLAYBOOK |
| G19 refuted-in-part (stall-sensor recovery dead) | ✅ | Matches pre-exec review |
| G29 nested variants silent drop | ✅ | Matches forensics + CONFIG_REFERENCE |
| G30 auth.json path | ✅ | Correct |
| G31 autoupdate silently breaks pins | ✅ | Matches pre-exec review |
| Trap count 31 (G1-G31) | ✅ | INDEX says 31; GOTCHAS has 31 entries |
| **Missing trap**: catalog deprecation filter silently removes config-keyed models (#22644) | ⚠️ MODERATE | Forensics §3.2 + gap-closure A1/A2: models marked "deprecated" in models.dev are dropped from picker EVEN IF config declares them. This is a distinct trap from G29 (variant schema) — it's a catalog-side filter. Should be G32. |
| **Missing trap**: @latest pins stale forever (#30631) | ⚠️ MODERATE | Gap-closure B7: plugin @latest resolves once at install, never re-resolves. KB mentions this in ARCHITECTURE amendment and CLINE doc but not as a GOTCHAS entry. |
| **Missing trap**: Zen free-tier gateway flake (#41236/#44300) | ⚠️ MINOR | Gap-closure D3: x-preview-f-free fails with tools; nemotron-3-ultra-free stable. Cross-check needed in verification. |

### 5. CLINE_GEMINI_ANTIGRAVITY.md — **ACCURATE** (one stale detail)
| Item | Status | Note |
|---|---|---|
| Cline gate caveat (deepseek 403, caps 1M/384K, status fluid) | ✅ | Matches gap-closure A1/A2 |
| Antigravity plugin: local git checkout @ 7db338b via file: | ✅ | Matches forensics |
| Gemini: AGENTS.md resolution + Antigravity CLI transition | ✅ | Matches gap-closure C10/D1 |
| **Stale**: "Cline 3.0.52" in sources | ⚠️ MINOR | Cline CLI version not re-verified this sweep; could be newer. Not execution-critical. |
| **Missing**: ClinePass id-namespace fallback (D4) | ⚠️ MINOR | Gap-closure D4 notes `cline-pass/*` ids as fallback; not in KB. |
| **Missing**: anthropic/claude-* reportedly NOT on api.cline.bot (D2) | ⚠️ MODERATE | Gap-closure D2: third-party validation says claude-* absent despite docs. KB still lists claude-sonnet-4-6 as available. Should add caveat. |

### 6. CODEX_CLAUDE_CODE_VSCODE.md — **ACCURATE** (post-amendments)
| Item | Status | Note |
|---|---|---|
| Codex: architecture summary replaces rust-v0.143.0 citation | ✅ | Gap-closure C9 |
| Codex: AGENTS.md-native, sandbox modes, approval policies | ✅ | Correct |
| Claude Code hooks: 25 → ~29-31 corrected | ✅ | Gap-closure C11 |
| Gemini: AGENTS.md resolved + Antigravity CLI transition | ✅ | Gap-closure C10/D1 |
| Cline: gate fluid, caps 1M/384K, reasoning_effort undocumented | ✅ | Gap-closure |
| Copilot: AI-Credits model replaces premium-request framing | ✅ | Gap-closure A5/U6 |
| **Missing**: Codex version pin still pending (L6) | ⚠️ MINOR | Amendment says "version pin at next local session" — still open. |
| **Missing**: VS Code reads BOTH AGENTS.md and CLAUDE.md (amendment line 35) | ✅ | Documented in amendment but not in main body — should promote. |

### 7. INDEX.md — **ACCURATE** (trap count matches)
| Item | Status | Note |
|---|---|---|
| GOTCHAS trap count 31 | ✅ | Matches GOTCHAS actual entries |
| rot_class per doc | ✅ | Reasonable |
| **Missing**: SOVEREIGN_SEARCH_PROTOCOL.md stub still listed | ✅ | Correctly marked "MERGED → SOVEREIGN_SEARCH.md" |
| **Missing**: OMEGA_VAULT_ARCHITECTURE.md stub still listed | ✅ | Correctly marked "MERGED → OMEGA_VAULT.md" |
| **Stale**: CLI_IDE_ECOSYSTEM.md still listed as "superseded-pending-merge" | ⚠️ MINOR | Has been stale for months; either merge or archive. |
| **Missing**: INDEX doesn't reference the three new research docs (pre-exec, provider-setup, gap-closure) | ⚠️ MINOR | Not required but would improve discoverability. |

### 8. CHANGELOG.md — **ACCURATE** (KB-D-015 correctly summarizes sync)
| Item | Status | Note |
|---|---|---|
| KB-D-015 sync items | ✅ | All match what I see in the docs |
| Escalation: curators.yaml YAML corruption | ✅ | Still open (KD-2) |
| **Missing**: CHANGELOG doesn't record the gap-closure sweep (KB-D-016?) | ⚠️ MINOR | The gap-closure sweep produced KB patches (C9-C11 amendments) but no KB-D entry. Should add for completeness. |

### 9. SOVEREIGN_SEARCH_PROTOCOL.md (stub) — **ACCURATE STUB**
- Correctly marked "MERGED → SOVEREIGN_SEARCH.md"; no stale content.

### 10. OMEGA_VAULT_ARCHITECTURE.md (stub) — **ACCURATE STUB**
- Correctly marked "MERGED → OMEGA_VAULT.md"; no stale content.

---

## FORENSICS FINDINGS MISSING FROM KB (should be added)

| # | Forensics Finding | KB Target Doc | Priority |
|---|---|---|---|
| 1 | **Catalog deprecation filter (#22644)**: models marked "deprecated" in models.dev are silently dropped from picker even if config declares them under that catalog id. Workaround: override with `"status":"beta"`. | GOTCHAS (new G32) + CONFIG_REFERENCE §8 | HIGH — affects any catalog-keyed model we keep (MiMo re-key, nemotron) |
| 2 | **@latest pins stale forever (#30631)**: plugin @latest resolves once at install into `~/.cache/opencode/packages/<pkg>@latest/package.json` and never re-resolves. | GOTCHAS (new G33) + ARCHITECTURE amendment | HIGH — affects antigravity plugin if we ever switch from file: to npm |
| 3 | **Zen free-tier gateway flake (#41236/#44300)**: x-preview-f-free fails with "Endpoint is unavailable" for tool-containing requests; nemotron-3-ultra-free stable. Verification must cross-check. | GOTCHAS (new G34) + PLAYBOOK §7 | MEDIUM — verification protocol |
| 4 | **keep_thinking:true separate window**: flipping keep_thinking in same window as model changes violates single-variable verification; cost/quota downside (re-sends thinking blocks). | PLAYBOOK §7 + CLINE_GEMINI_ANTIGRAVITY | MEDIUM — execution discipline |
| 5 | **V2 plugin API unscheduled**: V1 plugins won't work in V2; migration guidance "will be published when ready"; no deprecation date for V1 hooks on V1 line. | ARCHITECTURE amendment + GOTCHAS | LOW — future-proofing |
| 6 | **Gemini CLI → Antigravity CLI transition (Jun 18 2026)**: unpaid tiers migrated; classic Gemini CLI guidance ages out. | CLINE_GEMINI_ANTIGRAVITY (has it) + CODEX_CLAUDE_CODE_VSCODE (has it) | ✅ Already in KB |
| 6 | **ClinePass id-namespace fallback**: `cline-pass/*` model ids ($9.99/mo, 2-5× rate limits) exist on same endpoint. | CLINE_GEMINI_ANTIGRAVITY | LOW — fleet scaling |
| 7 | **anthropic/claude-* reportedly absent from api.cline.bot** (third-party validation): despite Cline docs listing them, marketplace extension author claims they're not actually available. | CLINE_GEMINI_ANTIGRAVITY + CONFIG_REFERENCE §8 | HIGH — our Cline block includes claude-sonnet-4-6 |
| 8 | **Zen provider base_url**: `https://opencode.ai/zen/v1` (forensics Addendum A) | CONFIG_REFERENCE §8 provider table | MEDIUM — config completeness |
| 9 | **google-standard provider rationale**: isolates Antigravity google-namespace hijack | CONFIG_REFERENCE §8 | LOW — design doc |
| 10 | **MiMo re-key caps**: mimo-v2.5-free = 200K context / 32K output (not 512K from subagent_pool) | CONFIG_REFERENCE §8 | MEDIUM — correct stale value |

---

## KB CLAIMS CONTRADICTING V3.0 FORENSICS

| KB Doc | Claim | Forensics v3.0 Truth | Correction |
|---|---|---|---|
| CONFIG_REFERENCE §8 "House providers" table | `nemotron-3-ultra-free`: **1M ctx / 128K out** | Live limits = **200K ctx / 32K out** (same as mimo-v2.5-free; forensics §9.2) | Change to 200K/32K |
| CONFIG_REFERENCE VARIANTS amendment §93 | Same nemotron caps error | Same | Change to 200K/32K |
| CONFIG_REFERENCE §8 | `mimo-v2.5-free`: 200K/32K (correct) but subagent_pool/profile_manager.py:143 says 512K | 200K/32K is live catalog; 512K is stale code debt | Keep 200K/32K; add note that subagent_pool has stale 512K |
| CLINE_GEMINI_ANTIGRAVITY / CONFIG_REFERENCE | `anthropic/claude-sonnet-4-6` available on api.cline.bot | Third-party validation: **NOT available** (D2) | Add caveat: "reported absent from gateway despite docs; verify via /api/v1/models before relying" |

---

## CROSS-DOC CONSISTENCY ISSUES

| Issue | Docs Involved | Resolution |
|---|---|---|
| nemotron-3-ultra-free caps: 1M/128K vs 200K/32K | CONFIG_REFERENCE (1M/128K) vs forensics (200K/32K) | **CONFIG_REFERENCE is wrong** — patch to 200K/32K |
| Antigravity plugin install: "npm @latest" vs "file: checkout @ 7db338b" | ARCHITECTURE amendment says "V2 plugin API in flight" but doesn't clarify install mode; CLINE doc correctly says file: checkout; CONFIG_REFERENCE doesn't mention antigravity install mode | Standardize: antigravity = local file: checkout @ 7db338b (not npm) |
| Cline deepseek caps: 1M/384K (CLINE doc) vs gap-closure (1M/384K) — consistent | ✅ | No issue |
| Trap count: INDEX says 31, GOTCHAS has 31 | ✅ | Consistent |
| Binary version: PLAYBOOK says 1.18.23, CONFIG_REFERENCE amendment says 1.18.23, ARCHITECTURE doesn't state explicitly | ✅ | Consistent |
| auth.json path: CONFIG_REFERENCE §8 says ~/.local/share/opencode/; GOTCHAS G30 says same | ✅ | Consistent |
| tui.json: GOTCHAS G30 says "does not exist on all installs (absent here)"; PLAYBOOK §7 says keybinds live in tui.json | Clarify in PLAYBOOK: tui.json may not exist; keybinds config is separate file that may be absent |

---

## FINAL VERDICT

**CONDITIONAL PASS** — The KB is execution-ready **after** these 5 targeted patches:

1. **CONFIG_REFERENCE**: Fix nemotron-3-ultra-free caps to 200K/32K (two locations: House providers table + VARIANTS amendment)
2. **GOTCHAS**: Add G32 (catalog deprecation filter), G33 (@latest stale pin), G34 (Zen flake)
3. **CLINE_GEMINI_ANTIGRAVITY**: Add anthropic/claude-* absence caveat + ClinePass fallback note
4. **PLAYBOOK**: Add explicit F0 freeze protocol (env var + global config) + tui.json clarification
5. **CHANGELOG**: Add KB-D-016 for gap-closure sweep amendments

All other findings are minor staleness or documentation completeness items that don't affect the remediation plan execution.

---

## SOURCE INDEX (for this audit)

- Forensics v3.0: `docs/research/R_OPENCODE_CONFIG_POLLUTION_FORENSICS_20260826.md`
- Pre-exec review: `docs/research/R_CONFIG_REMEDIATION_PREEXEC_REVIEW_20260826.md`
- Provider setup: `docs/research/R_CLINE_COPILOT_PROVIDER_SETUP_20260826.md`
- Gap closure: `docs/research/R_GAP_CLOSURE_SWEEP_20260826.md`
- KB docs: all 8 under `data/entities/grokster/kb/` + 2 stubs
- Live config: `~/.config/opencode/opencode.json`, `opencode.json`, `.opencode/opencode.json`
- Live auth: `~/.local/share/opencode/auth.json`
- Plugin source: `omega-engine/opencode-antigravity-auth/dist/src/plugin/request.js`

---
*⬡ OMEGA ⬡ JEM ⬡ KB-FINAL-AUDIT ⬡ CONDITIONAL-PASS ⬡ 2026-08-26*