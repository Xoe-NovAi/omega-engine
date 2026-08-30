<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Project: omega-vault
## ONE-TURN HYDRATION BRIEF

### ONE-LINER
**Sovereign Credential Operator** — OS keyring + SQLite event log + `vault` CLI + CAP adapters (OpenCode, Omega Engine, generic `.env`) + Policy Engine + Rotation Orchestrator + Provider Registry + Passive watcher + MCP server. Solves 1.5-year credential management hell.

### STATUS (2026-07-19)
- **Architecture**: ✅ Ratified (D-299)
- **Research**: ✅ Grounded (7-domain 2026 research, 40+ sources)
- **Gnosis**: ✅ 12 L3 principles staged to `proposed_lessons.yaml`
- **Phase 0**: ✅ Gitignore fix (credential files) — commit de7406f
- **Phase 1**: 🔄 IN PROGRESS — VaultCore scaffolded (`src/omega/infra/vault/`)
- **Phases 2-6**: ⏳ PENDING

### KEY FILES
| Type | Path |
|------|------|
| Consolidated Plan | `docs/strategy/KEN_WALGER_MINING_CONSOLIDATED_PLAN_20260719.md` |
| Grounding Research | `docs/research/R_KEN_WALGER_MINING_GROUNDING_20260718.md` |
| Knowledge Gaps | `docs/research/R_KEN_MINING_KNOWLEDGE_GAPS_20260719.md` |
| Execution Plan | `docs/strategy/R_KEN_MINING_EXECUTION_PLAN_20260719.md` |
| Unmined Gnosis | `docs/research/R_UNMINED_GNOSIS_KEN_MINING_20260719.md` |
| Scaffold | `src/omega/infra/vault/` (to expand) |

### PHASES (6-Phase Architecture)
| Phase | Deliverable | Status |
|-------|-------------|--------|
| **0** | Gitignore fix (auth.json, credentials.json, .env, .env.*, *.key, *.pem) | ✅ DONE |
| **1** | VaultCore: OS keyring + SQLite event log + `vault` CLI (`init`, `add`, `sync`, `audit`) | 🔄 IN PROGRESS |
| **2** | CAP Adapters: OpenCode, Omega Engine, generic `.env` | ⏳ PENDING |
| **3** | Policy Engine + Rotation Orchestrator + Provider Registry (Google, Anthropic, OpenRouter, OpenAI, xAI, Firecrawl) | ⏳ PENDING |
| **4** | Passive watcher (inotify/fanotify) + MCP server (`omega-vault serve`) | ⏳ PENDING |
| **5** | Context bundle backup/restore + Chaos testing CLI | ⏳ PENDING |
| **6** | `omega-vault` PyPI + Homebrew release | ⏳ PENDING |

### PROVIDER REGISTRY (Antigravity Integration Point)
| Provider | Auth Type | Quota API | Rotation Trigger |
|----------|-----------|-----------|------------------|
| **Google Antigravity** | OAuth PKCE | `cloudcode-pa.googleapis.com/v1internal:fetchAvailableModels` | `remainingFraction < 0.1` OR 429 |
| **Anthropic** | API Key | `/v1/organizations/{id}/usage` | Usage > threshold |
| **OpenRouter** | API Key | `/api/v1/auth/key` | Credits < threshold |
| **OpenAI** | API Key | `/v1/usage` | Rate limit / quota |
| **xAI (Grok)** | API Key | TBD | TBD |
| **Firecrawl** | API Key | `/api/usage` | Credits < threshold |

### GNOSIS STAGED (12 L3 Principles)
- L3-LocalFirstCredentialOperator
- L3-MeditationAsCognitiveCompiler
- L3-StratifiedTruthWithExplicitSync
- L3-PushBasedAdapterProtocol
- L3-ChaosAsDesignConstraint
- L3-MiddlewareForCrossCuttingConcerns
- L3-ContextBundleAsCognitiveContinuity
- L3-ProviderRegistryAsSemanticLayer
- L3-LocalObservabilityNotTelemetry
- L3-RotationAsDistributedTransaction
- L3-GradientAdoptionViaPassiveFirst
- L3-ThreeTierCredentialArchitecture
- L3-StandaloneProductAsForcingFunction
- L3-MCPAsNativeCredentialProtocol
- L3-GitignoreFirst

### DECISIONS LOG
- **D-299**: Omega-Vault Credential Operator ratified
- **D-299a**: Product pattern from omega-sieve (standalone PyPI)
- **D-299b**: Fanotify for passive watching (Linux 5.1+)
- **D-299c**: MCP as native credential protocol
- **D-299c**: Antigravity provider = Phase 1 priority (user has 8 accounts)

### BLOCKERS
- `all2md` not installed (blocks Phase 0 blog ingestion for Ken Walger mining)
- sqlite-vec memory leaks (7 known) — need batch ingestion with LlmMac 500-2000 rows/txn

---

*⬡ OMEGA ⬡ CPR ⬡ omega-vault ⬡ 2026-07-19*