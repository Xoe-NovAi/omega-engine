<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# SECURITY_SEG3_delta.md — Researcher Paging Return Report
**AP Token**: `AP-RESEARCHER-v1.0.0`
**Paged from**: kali (ses_fdef2be4effe4pAaLXCTUx62GO) — Architect-direct mission
**Date**: 2026-08-21
**Original scope**: Security Segments 7-10 (logging sanitization, process isolation, community standards, key rotation)
**Hydration**: ACTIVE_SPRINT.json header only (571 lines; grep for "blocker" = 0 hits — no such key). Blocker state taken from paging packet: P0-1 scrubbed+rotated; gitleaks/trufflehog wired; full-history filter-repo executing; `model_gateway.py:316-335` env-dump prevention gap OPEN; SecretRegistry + 4 egress hooks + ProviderIdentity RBAC designed, never implemented.

## 1A. Forgotten Findings — Sanitization & Isolation (Segs 7-8)

**Sanitizer choice (never surfaced into implementation):**
- `flashtext` (pure-Python, MIT, O(N) in line length regardless of keyword count) was the
  recommended primary for ~40 secret keys: 20K keywords → 0.13s vs regex-alternation 6.99s.
- `pyahocorasick` C-ext risk CONFIRMED: GCC 15 C23 `bool` keyword broke builds (issue #199,
  fixed v2.2.0 2025-06), but wheel coverage gaps persist on rolling/minimal platforms →
  violates zero-friction `pip install` for debut users. Do NOT add as hard dep.
- Zero-dep fallback benchmarked: plain `str.replace` loop over 40 keys ≈ <0.1ms/log-line.
  Acceptable debut-grade; no new dependency at all.

**Process isolation verdict (pre-debut decision that still stands):**
- In-process sanitizer = 0ms overhead → correct for debut.
- If isolation later mandated: Unix Domain Socket + msgspec ≈ 0.3ms (1% of a 30ms LLM call)
  — within budget. gRPC 1.5ms acceptable; HTTP/JSON 4ms tolerable.
- REJECT subprocess-stdio JSON-RPC (MCP-style): measured ~27ms/call — unacceptable streaming.
- SECURITY: `multiprocessing.Connection.recv()` unpickles → RCE vector if any untrusted
  writer reaches the pipe. If IPC ever added: `recv_bytes()` + msgspec/JSON, never pickle.
- systemd socket activation (FD 3, `socket.fromfd`, zero-downtime restarts) is viable but
  complexity unjustified pre-debut; revisit only if gateway process split happens.

Sources retained: vgi-rpc benchmarks; infergo transport.md; MCP-vs-direct bench (~16x
subprocess overhead); vllm PR #6883 (zmq+pickle TPOT win); pyahocorasick #199/v2.3.1;
flashtext gist vi3k6i5 + arXiv:1711.00046.

## 1B/2. Forgotten Findings — Community Standards & Rotation (Segs 9-10)

**Community patterns (surveyed 9 tools; pattern held):**
- CLI tools → `.env` + env vars universally (Aider, Continue.dev, OpenCode, LM Studio).
  GUI/Electron apps → OS Keychain via `safeStorage`. Omega CLI should follow `.env`+env.
- OpenCode precedent directly relevant to our debut: `auth.json` stored PLAINTEXT at
  `~/.local/share/opencode/auth.json`; keyring support remains opt-in feature request
  (#4318, Bun.secrets / @napi-rs/keyring). We are not behind the ecosystem standard.
- **Claude Code split-brain (#78020)**: rotation written to Keychain while `/login` writes
  `.credentials.json` → single-use refresh tokens presented stale → whole token family
  revoked → forced re-login loops. LESSON: ONE canonical credential store per secret;
  every writer must target it atomically.
- **Silverfort finding**: Claude Code macOS Keychain item ACL trusts `/usr/bin/security`
  itself → ANY same-user process reads creds silently (`find-generic-password -w`), no
  prompt (CWE-732/CWE-522). LESSON: if Omega ever uses OS keystore, bind items via native
  API to app identity — never shell out to `security`.
- Electron `safeStorage` Linux `basic_text` fallback = PBKDF2(1 iter) + hardcoded salt
  "saltysalt" ≈ plaintext. Any keystore integration MUST check backend and refuse
  `basic_text` (pattern from chenguangliang teardown; zero popular apps do this check).
- Aider #3475: `--api-key` CLI args leak into shell history AND are readable via
  `/proc/*/cmdline`; env vars do NOT appear in cmdline. Never accept secrets as argv.

**Key-rotation practices worth adopting (never adopted):**
- Rotation capability matrix: OpenRouter Management API = FULL auto (create/delete,
  `expires_at`, per-key hash + usage counters); Google SA keys = FULL auto (+ org-policy
  auto-disable of leaked keys since 2024-06); OpenAI = automatable; **Anthropic Admin API
  CANNOT create keys** — status/name updates only; expiration fixed at creation
  (3h/1d/7d/30d/custom/Never), unchangeable afterward. → `omega secrets rotate --all`
  feasible for 3/4 majors; Anthropic path must be "manual console step + import".
- Zero-downtime pattern: create → deploy staging → verify → dual-key grace (10-15 min)
  → monitor usage migration → revoke old. Google explicitly warns AGAINST expiring keys
  in production (outage risk) — prefer rotation lifecycle over expiry.
- Adopt OpenRouter-style metadata in any Omega secret store: stable hash ID (never the
  secret), `expires_at`, usage counters → enables audit + safe delete-by-hash.

Sources: openrouter.ai/docs/cookbook/administration/api-key-rotation; cloud.google.com/iam/
docs/key-rotation; platform.claude.com/docs/en/manage-claude/authentication#key-expiration.

## 3. Flagged Important — Never Executed

| # | Item | Status | Debut relevance |
|---|------|--------|-----------------|
| 1 | **SecretRegistry + 4 egress hooks + ProviderIdentity RBAC** (sibling runtime-security design) | DESIGNED, never implemented; root cause `model_gateway.py:316-335` still dumps ALL keys to `os.environ` at init | **HIGHEST** — prevention gap open while scrub/rotation (P0-1) only treats symptoms. Without egress hooks, next leak path (logs, errors, subprocess env, telemetry-free traces) re-exposes rotated keys |
| 2 | flashtext / str.replace log sanitizer wired into logging path | Researched + benchmarked, never built | HIGH — cheap (<0.1ms), zero-dep option exists; complements gitleaks (repo) with runtime (logs) coverage |
| 3 | `omega secrets rotate --all` CLI | Feasibility proven (3/4 providers automatable; Anthropic manual+import), never implemented | MEDIUM — rotation now proved necessary by P0-1 incident itself |
| 4 | Single-canonical-store rule for credentials | Lesson extracted (Claude Code #78020), never codified in Omega secrets design | MEDIUM — must be a constraint on SecretRegistry impl, not folklore |
| 5 | Keystore-backend refusal check (`basic_text` pattern) | Never ported | LOW pre-debut (no keystore yet); mandatory gate IF keyring support lands |
| 6 | Secrets-never-as-argv rule (Aider #3475 lesson) | Never codified | LOW-MED — applies to any future `omega secrets set` CLI surface |

**Recommended sequencing for the security thread**: (1) implement SecretRegistry + egress
hooks FIRST (closes the os.environ dump = prevention), (2) wire sanitizer into logging
(runtime defense-in-depth), (3) rotate CLI after registry exists (it becomes a Registry
operation, not ad-hoc API calls). Items 4-6 are design constraints to embed in (1)-(3),
not separate tickets.

---
**FILE COMPLETE** — Researcher paging report closed 2026-08-21. No other files written.
Hydration cost: ACTIVE_SPRINT.json lines 1-60 + grep (0 hits). Retained research reused;
no new web searches performed (resource discipline).

