# GitHub Copilot — Research Targets (Open Probes & Re-verification Cadence)

**KB Entry**: grokster/platforms/copilot/RESEARCH_TARGETS
**last_verified**: 2026-08-26 · **rot_class**: fast (probe list changes every session)
**Scope**: Unresolved items from the 2026-08-26 deep mine, ordered by value/effort. Evidence base: `docs/research/R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md` §I.
**Sources**: R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md; house inline context (grokster EXPERT_SESSIONS charter).

---

## §1 Local Probes (L4 — cheap, high value)

| ID | Target | Method | Unblock value | Status |
|---|---|---|---|---|
| **L4-a** | Enterprise slot ← plain github.com account — **REDESIGNED 2026-08-26** (binary shows NO separate enterprise provider; see CONFIG_REFERENCE §2). Runbook below | ~5 min by Architect | Resolves whether a second individual Copilot credential is possible without proxies | OPEN (GOTCHAS G-COP-08) |

#### L4-a RUNBOOK (prepared 2026-08-26 — NOT executed; Architect-executable, <5 min)

**Premise change**: original design (write credential into `github-copilot-enterprise` auth.json key) is likely DEAD — the binary contains no such provider ID and no auth loader for it. This runbook tests that premise first, then falls back to the real enterprise mechanism (`enterpriseUrl` field on the single `github-copilot` credential).

```bash
# ── STEP 0: Does github-copilot-enterprise exist at runtime? (30 sec, no writes)
opencode models 2>/dev/null | grep -i "copilot" || opencode run --model github-copilot-enterprise/gpt-5.4-mini "Say SUCCESS" 2>&1 | head -5
# IF provider resolves AND a model lists → original probe viable: proceed to STEP 1.
# IF "provider not found"/empty → premise CONFIRMED dead: skip to STEP 3 (record verdict, stop).

# ── STEP 1: Backup credentials (mandatory)
cp ~/.local/share/opencode/auth.json ~/.local/share/opencode/auth.json.bak-l4a-$(date +%Y%m%d-%H%M%S)
chmod 600 ~/.local/share/opencode/auth.json.bak-l4a-*

# ── STEP 2: Inject test credential into the enterprise key (python, JSON-safe)
python3 - <<'EOF'
import json
p = "/home/arcana-novai/.local/share/opencode/auth.json"
auth = json.load(open(p))
# clone the working github-copilot credential into the enterprise key
auth["github-copilot-enterprise"] = dict(auth["github-copilot"])
json.dump(auth, open(p, "w"), indent=2)
print("injected:", list(auth.keys()))
EOF

# ── STEP 2b: Smoke test
opencode run --model github-copilot-enterprise/gpt-5.4-mini "Say SUCCESS" 2>&1 | tail -3

# ── STEP 3: Rollback (ALWAYS run, pass or fail — restores exact prior state)
LATEST_BAK=$(ls -t ~/.local/share/opencode/auth.json.bak-l4a-* | head -1)
cp "$LATEST_BAK" ~/.local/share/opencode/auth.json && chmod 600 ~/.local/share/opencode/auth.json
echo "rolled back from $LATEST_BAK"
```

**Success criteria**: smoke output contains `SUCCESS` with model banner naming `github-copilot-enterprise/...` → second individual slot EXISTS at runtime; update PLAYBOOK §4 + CONFIG_REFERENCE §2 to CONFIRMED.
**Failure criteria**: `provider not found`, auth-loader miss (no apiKey), or HTTP 401/404 → premise dead; record in GOTCHAS as G-COP-13 ("no second copilot auth loader in binary"); multi-account planning shifts entirely to rotation-plugin / proxy patterns.
**Safety**: no token values modified or exposed (credential object cloned verbatim); rollback restores byte-exact prior file; freeze means no binary drift during test.
| **L4-b** | Live `/models` catalog dump | Exchange token → authenticated GET /models; record SKUs + picker-policy flags | Ground-truth model ids vs docs drift | OPEN |
| **L4-c** | Token anatomy decode | Decode real bearer fields (`sku`, `proxy-ep`, `exp`, unknown fields) | Programmatic plan health-check implementation | OPEN |
| **L4-d** | Copilot CLI current version + full flag dump | Install; `copilot --version`; `copilot -p "hi" --max-ai-credits=5` | §A freshness; verify session-limit flag live behavior | OPEN |
| **L4-e** | Native `/v1/messages` Claude passthrough | Direct curl, tiny prompt, Claude SKU | Validates cheapest Claude integration path for any future proxy | OPEN |

## §2 Instrumented Studies (L5)

| ID | Target | Design | Answers |
|---|---|---|---|
| **L5-a** | Burn-rate A/B | Identical task through (a) OpenCode+github-copilot vs (b) Copilot CLI, same model; log usage checkpoints + billing-page deltas | THE outstanding house question: agentic-loop credits per task type. Hypothesis: OpenCode ≤ CLI burn (context handling) |
| **L5-b** | Cache-hit ratio | Repeat-context workload; measure cached-input share of billed tokens | Quantifies biggest burn lever (>93% claimed by Microsoft) |
| **L5-c** | Proxy stability soak | messense/copilot-api-proxy under light load, 1 week | Empirical ban-risk signal for the N>2 fan-out pattern (currently zero observed incidents [UNVERIFIED absence]) |

## §3 Re-verification Cadence

| Item | Cadence | Trigger dates |
|---|---|---|
| Pricing table vs docs.github.com models-and-pricing | Monthly + before any cost decision | **2026-09-03** (GPT-5.6 Sol promo ends) · **2026-09-01** (Biz/Ent boosted pools end) · 2026-12-31 (Gemini Flash promo ends) |
| Model catalog drift | Quarterly or on "model not supported" error | — |
| Copilot CLI version/flags | Before each CLI probe session | — |
| Ban-risk landscape scan (proxy projects' issues, GitHub enforcement reports) | Quarterly | — |
| OpenCode builtin provider changes (transform.ts copilot handling, slot semantics) | On each MANUAL upgrade event (autoupdate DISABLED 2026-08-26, binary pinned 1.18.23 — see opencode KB GOTCHAS G31/F0 freeze). Side-effect: probe results are now version-stable and reproducible | — |

## §4 Unresolved Questions (no probe assigned yet)

1. Does the server-side model allowlist differ between `gho_` (OpenCode app) and `ghu_` (VS Code app) tokens **in practice on paid individual plans**, or only on Business? (#20759 asserts difference; unquantified.) → fold into L4-b.
2. Exact credit accounting for OpenCode-harness sessions: does GitHub meter identically regardless of harness, or does client identity affect accounting paths? → L5-a secondary output.
3. Whether `endpoints.api` in exchange response is always populated for individual plans (pi code treats it as Business-only signal). → L4-c. **NOTE 2026-08-26**: moot for the builtin path — binary never exchanges (ARCHITECTURE §5a); still relevant for direct-API work.
4. Copilot SDK as sanctioned integration substrate for a first-party-style house proxy (replaces impersonation concern) — feasibility spike unscoped. → propose when N>2 fan-out becomes real.

## §5 Fabric Inventory Drift — FOR FABRIC-OWNER REVIEW (drafted 2026-08-26, jem does NOT edit fabric docs)

**Observation**: `~/.local/share/opencode/auth.json` holds credentials for **7 providers**: google, openrouter, github-copilot, siliconflow, aihubmix, cerebras, nebius.

**Ark §7 fabric list** (SOVEREIGN_ARK_BLUEPRINT.md) recognizes: native-gguf, lmster, Ollama (local); antigravity, google/google-compat, openrouter, opencode-zen, cline, anthropic, xai (cloud). Cerebras appears only under "EXPLICITLY NOT DOING NOW / new free-tier providers."

**Credentialed-but-unfabricated** (present in auth.json, absent from fabric ordering):
| Provider | M7 classification (pessimistic default per ProviderRegistry.is_cloud()) | Note |
|---|---|---|
| siliconflow | cloud | also had a deleted config override in today's remediation |
| aihubmix | cloud | aggregator; unknown upstream routing |
| nebius | cloud | — |
| cerebras | cloud | explicitly parked by Ark "NOT DOING NOW" yet credentialed |

**Ask for fabric owner**: reconcile under M7 — either (a) add these to the fabric ordering with explicit priorities, or (b) document them as deliberately-unranked credentials. Until then they are invisible to M7 local-first enforcement, which is a classification-integrity gap: unknown/unmapped names classify as cloud by default, so sovereignty ratios are safe, but the fabric picture is incomplete.

**Copilot-domain relevance**: none of the four affects Copilot posture; recorded here because the inventory surfaced during Copilot credential forensics (M2 finding #7).

---
*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*
