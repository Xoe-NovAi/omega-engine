# 🔱 R_OPENCODE_CONFIG_POLLUTION_FORENSICS_20260826 — v3.0 CONSOLIDATED FINAL
⬡ OMEGA ⬡ GROKSTER ⬡ platform-expertise ⬡ **SINGLE-SOURCE EXECUTION DOCUMENT — all amendments merged, no addenda**
**Status**: PLAN FINAL · VERIFIED EXECUTION-READY (§9) · **AWAITING ARCHITECT GO**
**Companion docs**: `R_CONFIG_REMEDIATION_PREEXEC_REVIEW_20260826.md` (Jem adversarial pre-flight) · `R_CLINE_COPILOT_PROVIDER_SETUP_20260826.md` (provider research) · `R_GAP_CLOSURE_SWEEP_20260826.md` (final gap closure)
*v3.0 consolidates v2.0 + §10 gap-closure amendments + §11 final-review verification into one authoritative text. Supersedes all prior versions.*

---

## §0 EXECUTIVE VERDICT

Config pollution root-caused to the 2026-08-10 "Web Gemini-verified config architecture" effort (commit `67fea132` + contemporaneous global-config changes). Remediation direction ratified sound by adversarial pre-flight (two plan defects found and corrected before execution); all web-researchable unknowns closed by final sweep; every plan target disk-verified.

| Verdict item | State |
|---|---|
| Root cause | ✅ Proven (git archaeology + virgin backups + live catalog) |
| Variants schema truth | ✅ Authoritative (official docs + installed plugin source): FLAT keys only |
| Sonnet 4.6 thinking | ✅ Viable via custom SKU; clone template confirmed on disk (.opencode/opencode.json:43–51) |
| MiMo duplicate | ✅ Solved (catalog id restructure mimo-v2.5 → mimo-v2.5-free) |
| deepseek-v4-flash-free | ❌ Officially dead upstream (#43829) → F5 delete/tombstone (Architect decision) |
| Copilot-as-provider | ✅ Already builtin + credentialed (~/.local/share/opencode/auth.json) — zero config (P1a = no-op) |
| Cline-as-provider | ⚠️ Transport OK; deepseek-v4-flash client-gated 403 (Aug-22 probe) — P1b gated on L1/L2 re-probe |
| Freeze safety | ✅ Downgraded risk: 1.18.20→23 changelogs clean re provider-loading/variants/compaction/plugin-API |

---

## §1 ROOT CAUSE TIMELINE

| Date | Event | Evidence |
|---|---|---|
| ≤2026-08-09 | Global config polluted: "(Free)" provider names, npm downgrades on 9 builtins, ~40 hand-listed models | `~/.config/opencode/opencode.json.backup.20260809_114431` |
| 2026-08-10 | Commit `67fea132` pollutes project + subdir configs | `git show 67fea132` |
| 2026-08-22 | Global last touched; `google` → `google-standard` | mtime + diff |
| 2026-08-25 | Binary self-updated to 1.18.23 unattended — autoupdate demonstrably active | `~/.opencode/bin/opencode` mtime |
| ~post-Aug-10 | Zen catalog restructured: `mimo-v2.5` → `mimo-v2.5-free`; `deepseek-v4-flash-free` deprecated → dead (#43829) | live models.dev fetch + house research docs |

---

## §2 FINDINGS (final)

**A — "(Free)" pollution**: Provider display names suffixed "(Free)" (line-counts: 7 global + 5 project) → every picker row contains "Free" → search matches paid models. Model names provider-prefixed violate house rules. Builtin catalogs ship clean names + native `:free` ID marking — manual tags unnecessary by design.

**B — Duplicate MiMo**: Visible pair = orphaned custom `mimo-v2.5` ("OpenCode Zen MiMo v2.5 (Free)", works — old id evidently still accepted server-side) + stock `mimo-v2.5-free` whose override was deleted in `67fea132` (errors against live endpoint). Thinking levels missing because ALL project Zen variant blocks use invalid nested `"reasoning":{"effort":…}` schema — **silently dropped** (KB trap G29). Flat `reasoningEffort` is canonical (official docs use the `opencode` provider as their literal example).

**C — Antigravity Sonnet 4.6 thinking**: Exists upstream ("Claude Sonnet 4.6 (thinking)" in official Antigravity docs); omitted from plugin presets (issue #495). Installed plugin 1.6.0 resolver handles custom ids GENERALLY: strips `antigravity-`, `supportsThinkingTiers()` matches claude+thinking, applies claude budget family. **Schema (pre-exec correction C1)**: FLAT `"thinkingBudget"` variant keys — verified against installed source (`request.js:591` reads `resolved.thinkingBudget`; `:669` reads `variantConfig?.thinkingBudget`). Working sibling proof: `antigravity-claude-opus-4-6-thinking` at `.opencode/opencode.json:43–51` uses exactly `{low: 8192, max: 32768}` flat keys — F6 clones this block. Note: `keep_thinking:false` currently hides thinking output even when enabled.

**D — Manual entries audit**: 9 provider overrides redundant+harmful (downgrade native SDKs, freeze stale limits, cause pollution): openrouter, cerebras, groq, mistral, together, cloudflare, nvidia-nim, sambanova, siliconflow. KEEP: google-standard (real hijack fix), lmstudio/ollama/native-gguf-* (real endpoints), antigravity models. Stale-limit example: our deepseek 163840/8192 vs live 200000/128000 (moot — SKU dead).

---

## §3 HAZARDS ABSORBED INTO THE PLAN (adversarial pre-flight + sweep)

| # | Finding | Resolution |
|---|---|---|
| C1 🔴 | Sonnet-thinking schema was nested (doc-derived); runtime wants flat | F6 uses flat `thinkingBudget` (source-verified) |
| C2 🔴 | Binary premise stale (auto-updated to 1.18.23) | F0 freeze BEFORE all work; freeze safety evidence-backed (changelogs clean) |
| C3 🟡 | Runtime dependents on Zen ids | Ids KEPT under plan → safe. Full inventory: §7 |
| C4 🟡 | Antigravity plugin = local `file:` git checkout in-repo (`omega-engine/opencode-antigravity-auth` @ commit `7db338b`, also installed at `~/.config/opencode/node_modules/`, Jul-21); drifts via git pull, invisible to config backups | F1 pins plugin commit hash; rollback bundle §8 |
| R1 | `@latest` plugin tags pin STALE not float (#30631) | Recorded; both config plugin arrays use `@latest` |
| R2 | Catalog deprecation filter silently hides config-keyed models (#22644) | F2 picker-count verification per retained provider |
| R3 | Zen gateway flake contaminates smoke tests | F7 cross-check vs second model (Nemotron, stable id) |
| R4 | keep_thinking flip must not share window with model changes | F6 optional separate step |
| Sweep | `anthropic/claude-*` NOT actually on api.cline.bot despite Cline's own docs listing them (third-party author validated ids directly) | P1b block ships WITHOUT claude-sonnet-4-6 |
| Sweep | deepseek-v4-flash Cline caps validated: **1M context / 384K output** | P1b limits corrected |
| Sweep | "V1 plugins will not work in V2" confirmed but UNSCHEDULED | Our four V1-family hook files safe on frozen line → monitor item §10, not work item |

---

## §4 THE PLAN — F0–F7 + P1 (fully amended; this section is the operative plan)

```
F0 FREEZE      OPENCODE_DISABLE_AUTOUPDATE=true + global "autoupdate": false;
               record binary hash + plugin commit (7db338b)
F1 BACKUP      timestamped copies: global/project/subdir opencode.json +
               auth.json (~/.local/share/opencode/auth.json — NOT ~/.config) +
               tui.json (ABSENT on this machine — skip) +
               zen_accounts_state.json + antigravity-accounts.json +
               plugin checkout state
F2 DEPOLLUTE   single-pass: strip "(Free)" suffixes + provider prefixes from
               names; DELETE 9 redundant provider overrides (openrouter,
               cerebras, groq, mistral, together, cloudflare, nvidia-nim,
               sambanova, siliconflow) → builtin catalogs return w/ native
               SDKs + working :free filtering. KEEP google-standard + locals.
               VERIFY: picker counts per retained provider (catch silent
               catalog shrinkage #22644-class issues)
F3 ZEN VARIANTS re-schema kept entries to FLAT reasoningEffort
               (likely restores Nemotron thinking levels alone)
F4 MIMO        re-key mimo-v2.5 → mimo-v2.5-free, live limits 200000/32000
               (do LAST within zen work — minimize ghost-id exposure)
F5 DEEPSEEK    DECISION POINT (Architect): delete entry vs tombstone
               (SKU officially dead #43829; variants moot if deleted)
F6 SUBDIR      add antigravity-claude-sonnet-4-6-thinking — clone sibling
               opus-thinking block (.opencode/opencode.json:43–51), change
               id + name, keep limits 200000/64000, FLAT keys:
               "variants": {"low": {"thinkingBudget": 8192},
                            "max": {"thinkingBudget": 32768}}
               Optional SEPARATE step: keep_thinking:true (never same window)
F7 FINAL       opencode --version unchanged; plugin HEAD unchanged;
               session-resume test; smoke calls cross-checked vs Nemotron
               (Zen flake guard)
P1 PROVIDERS   (post-F7 tail; detail in R_CLINE_COPILOT_PROVIDER_SETUP)
   P1a Copilot: NO-OP — builtin github-copilot + existing credential at
       ~/.local/share/opencode/auth.json. Multi-account: only 2 builtin
       isolation slots; 8-account rotation deferred to V-1 vault era.
       Auto-only plans = dead ends (#34644). Economics warning:
       AI-Credits token-metered since Jun 2026 ($0.01/credit);
       agentic loops = documented worst-case burn.
   P1b Cline: config block ready (house-compliant) BUT ship deepseek
       entry ONLY after gate re-probe passes (Aug-22 probe: HTTP 403 —
       free models reserved for Cline product surfaces). Block ships
       WITHOUT anthropic/claude-sonnet-4-6 (not actually available on
       gateway despite docs). deepseek caps: 1M ctx / 384K output.
       Read-only CLINE_API_KEY extraction + 30s curl probe MAY run
       parallel to F0-F7.
```

---

## §5 VERIFICATION EVIDENCE (final review pass — all disk-executed, not trusted)

| Check | Result |
|---|---|
| All 3 configs parse as valid JSON | ✅ VALID ×3 (project 9012B / subdir 2047B / global 15715B) |
| Binary version | ✅ 1.18.23 |
| Plugin checkout commit | ✅ 7db338bbb687f0aad575db3d835b955592bc1d79 |
| Plugin resolver reads FLAT thinkingBudget | ✅ request.js:591 / :669 |
| F2 targets present | ✅ 9 overrides in project config; "(Free)" lines 5 project / 7 global |
| F3 target present | ✅ nested `"reasoning"` ×10 in project config |
| F4/F5 targets present | ✅ mimo-v2.5 ×1; deepseek-v4-flash-free ×1 (project config) |
| F6 target absent + template present | ✅ sonnet-thinking 0 occurrences; opus-thinking sibling at :43–51 |
| error-capture.ts:109 nemotron hardcode | ✅ intact; id KEPT under plan |

---

## §6 RUNTIME DEPENDENTS INVENTORY (for future id changes)

Direct coupling (safe under current plan — ids kept):
- `.opencode/plugins/error-capture.ts:109` hardcodes `opencode/nemotron-3-ultra-free`
- `config/providers.yaml`, `config/entity_model_affinity.yaml`, `configs/token_budgets.yaml` reference Zen model ids

Swept refs requiring NO action (different id space — Cline-namespace / dormant parked code per D-558):
- `src/omega/infra/subagent_pool/account_registry.py:99` (cline_models list), `models.py:373`, `profile_manager.py:143`
- `config/model_registry/providers/cline.yaml:13`, `config/providers.yaml:332`

⚠️ Any FUTURE rename/deletion of Zen ids must clear column 1 first — silent breakage otherwise.

---

## §7 IRREDUCIBLE LOCAL PROBES (web-closable items exhausted: 9 closed / 2 partial)

Pre-P1 gates:
- **L1** curl gate re-probe on `deepseek/deepseek-v4-flash` (30s)
- **L2** authenticated `/api/v1/models` dump → caps + claude-* presence (1 min)

P1-phase:
- **L3** variant smoke call → does gateway honor `reasoningEffort` (2 min)
- **L4** enterprise-slot login attempt with github.com account (5 min)
- **L5** one instrumented agentic session for our AI-Credit burn rate
- **L6** `codex --version` (+ Claude Code version) pins
- **L7** startup-log check — file:-checkout vs @latest wrapper resolution

---

## §8 ROLLBACK BUNDLE (complete checklist)

1. Timestamped config copies (global/project/subdir) — pre-F1
2. `auth.json` (~/.local/share/opencode/), `zen_accounts_state.json`, `antigravity-accounts.json` (`tui.json` absent — skip)
3. Plugin state: commit hash 7db338b recorded; `git -C omega-engine/opencode-antigravity-auth stash list` clean; node_modules rebuild command noted
4. Binary: version + hash at F0 (freeze makes constant)
5. Per-phase revert: project config IS git-tracked (`git checkout -- <file>`); global is NOT — file copies are the only global safety net

---

## §9 EXECUTION ORDER & DECISION POINTS

1. **Pre-exec commit (recommended)**: working tree carries unrelated dirty files (KB/research/session docs). Commit accumulated work FIRST so remediation config diffs stay isolated for clean audit/revert.
2. **Architect GO** → F0 → F1 → … phase-gated, single-variable verification throughout.
3. **F5 mid-run**: Architect decides deepseek delete vs tombstone.
4. L1/L2 may run parallel to F0–F7 (read-only).
5. Context note: classic Gemini CLI replaced by Antigravity CLI for unpaid tiers since Jun 18 2026 (KB banner applied).

## §10 MONITOR ITEMS (not work items)

- **V2 plugin API migration**: V1 hooks deprecated-but-unscheduled; four V1-family hook files safe on frozen line. Revisit when upstream schedules.
- Catalog deprecation filter (#22644): retained-provider picker counts after F2.
- Zen gateway flake: any failed smoke must cross-check vs Nemotron before diagnosis.

## §11 SOURCES

Primary: official docs opencode.ai/docs/{config,models} (Aug 25 2026) · models.dev/api.json live fetch · NoeFabris/opencode-antigravity-auth README/MODEL-VARIANTS.md/issue #495 + INSTALLED SOURCE dist/src/plugin/{request.js,transform/model-resolver.js,config/models.js} · anomalyco/opencode issues #22644/#30631/#34644/#43829/#8030/#8067/#15243 · git: 67fea132 diff+pre-image · ~/.config/opencode backups · official 1.18.20→23 changelogs · House: Web-Gemini-OpenCode-Configuration-Research-Plan.md, R_OPENCODE_V2_RECON_20260719.md, PLATFORM_GROUND_TRUTH_LOG.md, D-557/D-563 rulings.

---
*v3.0 consolidated 2026-08-26 — grokster. Single-source execution document; supersedes v2.0 and all append-only addenda.*
