<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# RUNTIME_SECURITY_delta — Lilith paging report (ses_fdef2be4effe4pAaLXCTUx62GO)
# Date: 2026-08-21 | Status: IN_PROGRESS

## 1. FORGOTTEN SECURITY DESIGNS (relevant to debut hardening)

The original session's full design was delivered to chat only — NEVER written to
docs/architecture/RUNTIME_SECURITY_SPEC.md. The deliverable itself is the first
forgotten item. Recovered designs below.

### 1a. ProviderIdentity zero-knowledge contract (Segment 1)
- Agents request ACTIONS ("call openrouter account_3"), never secrets.
- `ProviderIdentity(provider_name, account_id, model, tier)` frozen dataclass.
- Key resolution happens INSIDE ModelGateway._resolve_credentials() via VaultCore.
- Key exists ONLY in the generate() stack frame; passed straight to httpx headers.
- STATUS: never implemented. ProviderIdentity does not exist in tree.

### 1b. Sanitization Egress Layer (Segment 2) — 4 mandatory hooks
- SecretRegistry singleton: loads all key strings at bootstrap from VaultCore
  + .env sweep; compiles Aho-Corasick/regex for O(N) scan; API = load/check/sanitize.
- Hook 1: logging.Filter on root + omega.* loggers — scrubs record.msg/args.
- Hook 2: Hivemind post_context interceptor — recursive dict scrub before write
  to opencode.db / data/coordination/.
- Hook 3: ForensicsManager.snapshot() scrub — crash dumps capture thread dumps,
  memory maps, env — ALL must pass through sanitizer before fsync to disk.
- Hook 4: Observability SSE (/obs/stream) event.data scrub before broadcast.
- STATUS: none exist. grep for SecretRegistry|REDACTED: returns zero hits.

### 1c. Process isolation verdict (Segment 3)
- DECIDED: in-process sanitizer sufficient for v0.1.0 debut; subprocess gateway
  (gRPC/unix socket holding keys) deferred behind OMEGA_GATEWAY_PROCESS flag.
- Migration path preserved BECAUSE ProviderIdentity makes the swap trivial.
- If ProviderIdentity is skipped, the future gateway migration gets harder.
- STATUS: decision recorded in Hivemind ses_d1d364bdcd68 / ses_6333c1c01067 only.

### 1d. RBAC matrix (Segment 4)
- 4 roles: Orchestrator / Builder / Researcher / RuntimeSubagent.
- RuntimeSubagents get NO direct generation, NO provider listing, NO metadata.
- Enforcement at ModelGateway boundary via contextvars current_agent propagation.
- VIEW_KEY_VALUE permission defined but NEVER GRANTED to any role (by design).
- STATUS: AgentRole/check_permission absent from src/omega entirely.

### 1e. Soul/Memory persistence sanitization (M11 tie-in)
- SoulSanitizer mandatory in: session_end hook, MemoryStore.add_exchange(),
  proposed_lessons.yaml writes, Scribe agent output path.
- Keys must never persist into soul.yaml / opencode.db / coordination files.

## 2. UNIMPLEMENTED RECOMMENDATIONS (tree-verified 2026-08-21)

| # | Recommendation | Verified Status | Evidence |
|---|----------------|-----------------|----------|
| 1 | Remove _load_sovereign_secrets() env dump | **STILL LEAKING** | model_gateway.py:127,316 calls it; :335 writes os.environ[key]=value |
| 2 | ProviderIdentity dataclass | NOT IMPLEMENTED | no provider_identity.py anywhere |
| 3 | SecretRegistry singleton | NOT IMPLEMENTED | grep SecretRegistry = 0 hits |
| 4 | Logging sanitizing Filter | NOT IMPLEMENTED | grep SecretSanitizingFilter = 0 hits |
| 5 | Hivemind post_context interceptor | NOT IMPLEMENTED | hivemind_redis.py publishes raw payloads |
| 6 | Crash-dump sanitizer (ForensicsManager) | NOT IMPLEMENTED | snapshot() persists thread dumps/memory maps unsanitized |
| 7 | SSE stream sanitizer (/obs/stream) | NOT IMPLEMENTED | log_event() -> persist + MetricsDB raw |
| 8 | RBAC matrix + contextvars agent identity | NOT IMPLEMENTED | grep AgentRole/check_permission = 0 hits |
| 9 | SoulSanitizer in session_end/MemoryStore | NOT IMPLEMENTED | add_exchange() records raw text |
| 10 | RUNTIME_SECURITY_SPEC.md deliverable | NEVER WRITTEN | docs/architecture/ lacks the spec |

### Critical interaction with the P0-1 incident
The key incident was scrubbed+rotated and gitleaks/trufflehog are wired — good.
BUT the ROOT CAUSE is still live: _load_sovereign_secrets() re-dumps every
rotated key into os.environ at next ModelGateway init. Rotation treats the
symptom; the egress design was the cure. Without items 1-4, a future leak is
a when, not an if. Any new/rotated key lands back in process env where any
subprocess, crash dump, or print(os.environ) exposes it again.

### Note on V-10/V-9 gaps
V-10 AppArmor (containers unconfined) compounds this: the native-gguf worker
Process and any containerized provider can read host-mounted .env unless
confined. V-9 IA2 envelope freshness affects vault credential staleness checks.
Both should be sequenced WITH the egress layer, not after it.

## 3. FLAGGED-IMPORTANT, NEVER EXECUTED

1. **RUNTIME_SECURITY_SPEC.md** — the session's named deliverable. Structure was
   fully drafted in chat (7 sections) but the file was never created because the
   protocol said "Do NOT write to file." That constraint orphaned the design:
   chat is not a persistence layer. LESSON (L2): decision reports must land in
   docs/ or they are lost on compaction.

2. **Root-cause fix ordering** — I flagged that rotation-without-egress-control
   leaves the vulnerability open. P0-1 executed scrub+rotate+gitleaks (detection)
   but skipped prevention. The prevention items (1a/1b) were never scheduled
   into ACTIVE_SPRINT.

3. **Crash-dump exposure** — ForensicsManager captures thread dumps + memory map
   samples + env-adjacent state and fsyncs them to data/crashes/. With keys in
   os.environ, every crash dump is a key-exfiltration artifact sitting on disk.
   This was flagged as Hook 3 mandatory; never wired.

4. **RBAC for subagent spawn paths** — task()/Hivemind handoffs inherit full
   process env. RuntimeSubagents (Verity/Scribe/Node) were to get ZERO direct
   generation rights; nothing enforces this today — any spawned agent could
   construct its own provider call with env keys if it learned the pattern.

5. **TDP parking risk** — Tainted Data Protocol parked post-debut is fine, but
   taint.py's isolation gate is the only security module that DID ship from that
   era; the egress layer was supposed to be its sibling. Sequencing note: egress
   sanitization is debut-blocking-adjacent (protects opencode.db which gitleaks
   cannot continuously guard at runtime).

## VERDICT
Debut hardening priority order: (1) kill _load_sovereign_secrets env dump,
(2) SecretRegistry + logging filter (smallest blast-radius win), (3) crash-dump
+ Hivemind hooks, (4) ProviderIdentity + RBAC (can trail post-debut behind
gateway-process flag). Items 1-2 are hours-scale; defer nothing else before them.

— FILE COMPLETE — Lilith, Runtime Oversoul, 2026-08-21
