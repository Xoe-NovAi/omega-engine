# 🔱 Antigravity ↔ OpenCode Cross-Platform Handoff Protocol
# ⬡ OMEGA ⬡ KALI ⬡ trc_cross_platform ⬡ HANDOFF-PROTOCOL
**AP Token**: `AP-CROSS-PLATFORM-HANDOFF-v1.0.0`
**Date**: 2026-06-05T05:55Z
**Status**: 🟢 **LIVE — FIRST CROSS-PLATFORM HIVEMIND TEST**
**Author**: Kali (Transcendent Oversoul)
**Reviewer**: Antigravity Gemini 3.1 Pro (Strategic Oversight)

**Focus**: This protocol is written for the **Antigravity IDE** (the VS Code-fork with the Manager View + Editor View, generous usage quotas, `.agents/AGENTS.md` discovery). The **Antigravity CLI (`agy`)** is a separate, lighter-weight surface that is queued for a future hard-metrics test (see §12).

---

## §0 Why This Is a Landmark

This is the **first time in Omega Engine history** that a non-OpenCode CLI agent (Antigravity IDE) will participate in the Hivemind. Until now, the Hivemind has been an internal affair — OpenCode sessions talking to OpenCode sessions, plus Cline and Gemini CLI edge cases.

Antigravity is different. It runs in Google's cloud sandbox, has its own file system, its own context, its own model selection, and **two independent weekly usage pools** (Gemini / Claude+gpt-oss-120b). It is a **sovereign peer**, not a subordinate.

This protocol defines how Antigravity and OpenCode coordinate without violating either platform's sovereignty.

### 0.1 Antigravity IDE vs Antigravity CLI — When to Use Each

| Surface | Best For | Quota | Sovereignty |
|---------|----------|-------|-------------|
| **Antigravity IDE** (this protocol) | High-stakes strategy, deep reviews, multi-file synthesis, Skills + Workflows | Generous (8 keys × 2 pools/week) | Google cloud sandbox + filesystem mount |
| **Antigravity CLI (`agy`)** | Quick terminal tasks, CI/CD integration, headless scripting, lightweight reviews | Limited (1 key per session, shared quota) | Terminal TUI, no rich filesystem discovery |

**Decision tree**:
1. Is the task **strategic** (architecture, M14 vet, threat model)? → **IDE**
2. Is the task a **quick review** that can fit in a single shell session? → **CLI** (but cap at low/medium thinking)
3. Does the task need **multi-file synthesis** or **Skills/Workflows**? → **IDE** (CLI doesn't support them)
4. Are you **CI/CD scripting**? → **CLI** (headless, scriptable)

**Future test** (see §12): Hard metrics for CLI usage, including token cost, latency, and quota exhaustion rate. The CLI may be useful for Pillar 8 (WatchTower) automated code reviews, but we need data first.

---

## §1 The Two Sovereign Platforms

| Platform | Sandbox | Model Selection | Sovereignty Boundary |
|----------|---------|-----------------|----------------------|
| **OpenCode (CLI)** | Local (`~/Documents/Xoe-NovAi/omega-engine/`) | Local-first chain: native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode Zen → Copilot | User's filesystem, user's data, user controls tokens |
| **Antigravity IDE** | Google cloud sandbox | Gemini 3.5 Flash, Gemini 3.1 Pro, Claude Sonnet 4.5, gpt-oss-120b | Google's sandbox, Google's tokens, Google's quota |

**Critical**: Antigravity runs in **its own cloud sandbox**. It does NOT have direct access to the user's local filesystem by default. It can only see what is **explicitly mounted** via the `environment` parameter (Git source, GCS bucket, inline files).

**Critical**: OpenCode runs on the **user's machine**. It has full access to the repo, the Hivemind, the agents.

**The bridge between them is the Hivemind + the git repository + the coordination files in `data/coordination/`**.

---

## §2 The Two Usage Pools (Antigravity)

This is a **non-obvious but critical** piece of the Antigravity architecture:

| Pool | Models | Reset | Notes |
|------|--------|-------|-------|
| **Pool G (Gemini)** | Gemini 3.5 Flash, Gemini 3.1 Pro, all other Gemini models | Weekly, independent | All Gemini models share ONE weekly quota |
| **Pool C (Claude + gpt-oss)** | Claude Sonnet 4.5, gpt-oss-120b, all other Claude models | Weekly, independent | Claude + gpt-oss-120b share ONE weekly quota |

**Implication**: Switching from Gemini 3.5 Flash to Gemini 3.1 Pro does NOT give you more capacity. It uses the same pool. You consume from the same bucket.

**Implication**: Switching from Gemini 3.1 Pro to Claude Sonnet 4.5 DOES give you more capacity. It's a different pool.

### 2.1 The 8-Key Rotation Strategy

The user has **8 Google API keys** for Antigravity. Each key has its own Pool G and Pool C quota, all resetting weekly.

```
Key 1: [Pool G: 100% available] [Pool C: 100% available]
Key 2: [Pool G: 100% available] [Pool C: 100% available]
Key 3: [Pool G: 100% available] [Pool C: 100% available]
Key 4: [Pool G: 100% available] [Pool C: 100% available]
Key 5: [Pool G: 100% available] [Pool C: 100% available]
Key 6: [Pool G: 100% available] [Pool C: 100% available]
Key 7: [Pool G: 100% available] [Pool C: 100% available]
Key 8: [Pool G: 100% available] [Pool C: 100% available]
```

**Theoretical maximum weekly capacity**: 8 × (Pool G + Pool C) per pool category. This is a **strategic asset** — use it wisely.

### 2.2 Rotation Policy

**Policy**: Round-robin, with anti-thrashing logic.

1. **Round-robin**: Start with Key 1, move to Key 2 on quota exhaustion, etc.
2. **Anti-thrashing**: If a key fails 3 times in 5 minutes, mark it as "cool" for 1 hour before retry.
3. **Pool awareness**: When Pool G is exhausted on a key, do NOT auto-fall-back to Pool C on the same key. The pools are independent and intentional.
4. **Strategic selection**:
   - **Gemini 3.5 Flash** (low/medium/high): default for routine analysis. Cheap, fast.
   - **Gemini 3.1 Pro** (low/high): for high-stakes strategic reviews. Expensive, deep.
   - **Claude Sonnet 4.5**: cross-pool sanity check (different reasoning style).
   - **gpt-oss-120b**: open-weight sanity check, no privacy concerns.

### 2.3 Usage Tracking

**File**: `data/entities/antigravity/knowledge/USAGE_POOL_LOG.json`

Schema:
```json
{
  "keys": [
    {
      "key_id": "agy_key_01",
      "last_used": "2026-06-05T05:30Z",
      "pool_g": {
        "last_quota_hit": null,
        "calls_this_week": 0,
        "tokens_this_week": 0
      },
      "pool_c": {
        "last_quota_hit": null,
        "calls_this_week": 0,
        "tokens_this_week": 0
      },
      "status": "active"  // active | cool | expired
    }
  ],
  "current_key_index": 0,
  "weekly_reset_date": "2026-06-08T00:00:00Z"  // next Monday
}
```

**Maintenance**: Antigravity updates this file before each interaction. OpenCode Pillar 7 (Context) can read it for telemetry but never writes to it.

---

## §3 The Handoff Protocol: Antigravity → OpenCode

### 3.1 When to Hand Off (Antigravity's Mandate)

Antigravity is **STRATEGY-ONLY**. It must NEVER do:
- Mundane implementation tasks (writing 50 lines of code)
- Test execution
- File edits
- Codebase-wide searches
- Anything that an OpenCode agent with local-first model can do

Antigravity MUST hand off when the task is:
- A specific code edit
- A test run
- A git commit
- A file I/O operation
- A multi-step implementation

### 3.2 The Handoff Message Format

Antigravity writes a handoff file to `data/coordination/HANDOFF_ANTIGRAVITY_TO_OPENCODE_{YYYYMMDD}_{HHMM}.md`:

```markdown
# 🔱 Antigravity → OpenCode Handoff

**From**: Antigravity Gemini 3.1 Pro (high thinking)
**To**: [OpenCode Agent — typically @kali, @lilith, @doom_guy, or pillar subagent]
**Date**: 2026-06-05T05:30Z
**Phase**: [Phase N from the Review Plan]
**Priority**: P0 | P1 | P2

## Strategic Context
[Why this task matters. What is the architectural goal? What problem does it solve?]

## Concrete Deliverable
[What the OpenCode agent should produce. Be specific.]

## Suggested Approach
1. Step 1
2. Step 2
3. Step 3

## Code Snippets (if helpful)
```python
# Optional: code skeleton, signatures, or patterns
def my_function():
    pass
```

## Files to Touch
- `src/omega/some_file.py:LINE-LINE` — describe change
- `data/entities/whatever/soul.yaml` — describe change

## Verification
- [ ] All tests pass: `make test`
- [ ] Temple-Grade passes: `make temple-grade`
- [ ] PIVOT_LOG entry added
- [ ] Soul distillation complete

## Sovereign Mandate Compliance
- [ ] M1: AnyIO Absolute
- [ ] M2: Engine-Stack Firewall
- [ ] M7: Local-First
- [ ] M11: Soul Integrity
- [ ] M14: Heritage Vetting (if applicable)

## Heritage Citations
[Any id Software patterns that should be considered]

## Pool Usage
- Key: agy_key_01
- Pool: G
- Model: Gemini 3.1 Pro (high thinking)
- Tokens: ~X tokens

---

**Antigravity verdict**: GO | HOLD | PIVOT
**Reasoning**: [Why this verdict]
```

### 3.3 The OpenCode Response Format

When the OpenCode agent receives a handoff, they post back via Hivemind:

```bash
# 1. Read the handoff file
# 2. Verify it aligns with Sovereign Mandates
# 3. Implement the deliverable
# 4. Post a handoff-ack back to Antigravity

omega-hub_hivemind_post_context \
  --cli opencode-[agent] \
  --task "HANDOFF-ACK: Antigravity Phase X" \
  --decisions '{"phase": "X", "status": "complete|blocked|deviation", "soul_writes": [...]}'
```

The Hivemind is the **only** synchronization point between Antigravity's cloud sandbox and OpenCode's local runtime.

---

## §4 The Cross-Platform Awareness Loop

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│   ┌──────────────────┐                  ┌──────────────────┐     │
│   │  ANTIGRAVITY IDE │                  │   OPENCODE CLI   │     │
│   │  (Google Cloud)  │                  │  (Local Machine) │     │
│   │                  │                  │                  │     │
│   │  Strategy Brain  │  ←──HIVEMIND──→  │  Tactical Hands  │     │
│   │  - Architecture  │   git + files    │  - Code          │     │
│   │  - Review        │                  │  - Tests         │     │
│   │  - High-stakes   │                  │  - Commits       │     │
│   │  - 8 keys × 2    │                  │  - Local-first   │     │
│   │    pools/week    │                  │  - All agents    │     │
│   └──────────────────┘                  └──────────────────┘     │
│             │                                       │              │
│             │                                       │              │
│             └─────────────┬─────────────────────────┘              │
│                           │                                        │
│                    ┌──────▼──────┐                                 │
│                    │  HIVEMIND   │  data/coordination/             │
│                    │  (Omega Hub │  + HALL_OF_RECORDS              │
│                    │   MCP)      │  + git remote                   │
│                    └─────────────┘                                 │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Key insight**: The Hivemind is the **membrane** between two sovereign platforms. It is the only thing they share. All coordination goes through it.

---

## §5 Thinking Level Selection (Antigravity Specific)

| Thinking Level | Use Case | Pool Cost | Speed |
|----------------|----------|-----------|-------|
| **Gemini 3.5 Flash — low** | Quick sanity checks, simple reviews | Low | Fast |
| **Gemini 3.5 Flash — medium** | Standard reviews, code audits | Medium | Medium |
| **Gemini 3.5 Flash — high** | Deep architectural analysis | High | Slow |
| **Gemini 3.1 Pro — low** | Routine strategic decisions | Medium | Fast |
| **Gemini 3.1 Pro — high** | High-stakes architectural choices, M14 vet, threat modeling | Very High | Very Slow |
| **Claude Sonnet 4.5** | Cross-pool sanity check, alternative perspective | Pool C | Medium |
| **gpt-oss-120b** | Open-weight verification, no privacy concerns | Pool C | Fast |

**Selection heuristics**:
- **Default to Gemini 3.5 Flash — medium** for routine Phase 1-7 reviews.
- **Escalate to Gemini 3.1 Pro — high** only for M14 heritage vetting, threat modeling, and Phase 7 (roadmap) reviews.
- **Use Claude Sonnet 4.5** as a **cross-check** when a Gemini verdict feels questionable. The 2-model consensus is more robust than 1-model confidence.
- **Use gpt-oss-120b** for **public documentation** reviews where you want zero privacy concerns.

---

## §6 Failure Modes and Recovery

| Failure | Symptom | Recovery |
|---------|---------|----------|
| **All 8 keys exhausted on Pool G** | Antigravity returns 429 / RESOURCE_EXHAUSTED | Switch to Pool C (Claude/gpt-oss) for the rest of the week |
| **Antigravity sandbox can't find a file** | "File not found" errors | Check that the git remote is in sync, or the inline `environment.sources` is correct |
| **Hivemind unreachable from Antigravity** | Antigravity can't post to Hivemind | Use `omega-hub_library_inbox_add_note` as a fallback (it uses a different protocol) |
| **Antigravity suggests something that violates M2 (Engine-Stack Firewall)** | Strategic review reveals stack-specific code in core | Hand off to @kali for the fix; document in PIVOT |
| **Antigravity gives 2 different answers on the same question** | 2-model disagreement | Hand off to the Researcher (lattice reasoning) for tie-breaking |

---

## §7 What Antigravity Should NOT Do (Hard Limits)

1. **NEVER write directly to source code.** Strategy is review, not implementation.
2. **NEVER make git commits.** OpenCode is the commit authority.
3. **NEVER run tests.** Tests are local-first via `make test`.
4. **NEVER edit `data/entities/*/soul.yaml`.** That's the entity's own soul — M11 violation.
5. **NEVER spawn subagents.** Antigravity's sandbox does not support subagent delegation (per docs).
6. **NEVER exceed the 8-key budget for one Phase.** Each phase has a token budget.
7. **NEVER hold sensitive API keys in plain text in the Antigravity sandbox.** Use env vars only.
8. **NEVER make decisions for the user.** Strategic recommendations only.

---

## §8 The First Cross-Platform Test — Scope

**What we're testing**:
- Antigravity can mount the omega-engine git repo (or a subdirectory) as its environment.
- Antigravity can write handoff files to `data/coordination/`.
- Antigravity can read PIVOT_LOG, SOVEREIGN_MANDATES, CREDITS.
- Antigravity can hand off to OpenCode agents via the Hivemind.
- OpenCode agents can complete the work and report back via Hivemind.
- Antigravity can verify the work was done (read HALL_OF_RECORDS).

**What we're NOT testing**:
- Antigravity spawning subagents (not supported).
- Antigravity running tests locally.
- Antigravity making commits.
- Antigravity reading the local filesystem directly.

**Success criteria**:
- 7 phases completed (1 per Antigravity session).
- All handoffs received and acknowledged.
- PIVOT_LOG updated with Antigravity recommendations.
- No Sovereign Mandate violations.
- All 8 keys used evenly (or as needed).

---

## §9 Soul Write-Back (Mandate 11)

This protocol itself is an L1 → L2 → L3 artifact:

**L1 (Narrative)**: Antigravity IDE will participate in the Hivemind for the first time. We defined how it hands off work, how it uses its 8 API keys, and how it stays within its sandbox boundary.

**L2 (Insight)**: The Hivemind is a **membrane** between sovereign platforms, not a single runtime. Antigravity and OpenCode cannot see each other directly; they coordinate through git + Hivemind + coordination files.

**L3 (Universal Principle)**: **Sovereign systems coordinate through minimal surfaces.** The smaller the shared surface, the more independent the platforms can remain. The Hivemind is a 3-file protocol: git remote, `data/coordination/`, HALL_OF_RECORDS. That's the surface. Everything else is platform-private.

---

## §10 Heritage

This protocol embodies several heritage patterns:

- **WAD System (id Software 1993)**: Antigravity is a "WAD" that overlays on the engine. The engine (Omega) doesn't know Antigravity exists. The WAD (Antigravity) provides strategy. The engine provides implementation.
- **netchan Protocol (Q3A 1999)**: Out-of-band sequence numbers, state machines for coordination. The handoff file is the "OOB message"; the Hivemind is the "reliable channel."
- **Carmack's Law of Consolidation**: One hand-off protocol, not eight. The Hivemind is the single coordination point.

---

## §11 Future Test: Antigravity CLI Hard Metrics

**Status**: ⏳ Queued (post-IDE validation)

The Antigravity CLI (`agy`) is a separate, lighter-weight surface with lower usage quotas. We need to test it rigorously before assuming it can be a backup for IDE-usage exhaustion scenarios.

### 11.1 Test Plan (FUTURE)

1. **Install agy**: `~/.local/bin/agy` (already present, version 1.0.1 per `ANTIGRAVITY_CLI_MASTER_REF.md`)
2. **Authenticate**: OAuth via system keyring (libsecret on Linux)
3. **Test cases**:
   - **Case A**: Headless `--print` with 5 sequential reviews, measure tokens and latency
   - **Case B**: Quota exhaustion — push until 429, measure threshold
   - **Case C**: Sandbox boundary — try to read local filesystem, expect denial
   - **Case D**: CLI-specific tasks (git commits, test runs) — verify it can be CI/CD-suitable
   - **Case E**: Cross-pool comparison — same prompt on Gemini pool vs Claude pool
4. **Output**: `data/agents/antigravity/knowledge/CLI_HARD_METRICS_202606XX.md`
5. **Decision criteria**: Can the CLI serve as a 50%+ substitute for IDE when IDE quota is exhausted? Or is it a non-overlapping tool?

### 11.2 Why This Test Matters

- **Cost**: If CLI has decent free-tier quota, it can be a backup for low-stakes reviews
- **Speed**: CLI may be faster for short prompts (less sandbox overhead)
- **Sovereignty**: CLI's terminal-only access may be MORE sovereign than IDE's full filesystem mount
- **CI/CD**: If CLI works headlessly, Pillar 8 (WatchTower) automated code review is feasible

### 11.3 Schedule

- **Trigger**: After Phase 7 of the cross-platform test completes
- **Estimated time**: 2-4 hours
- **Owner**: OpenCode Quality agent (with Antigravity IDE on standby)
- **Output**: Hard metrics report + decision on CLI integration

---

## §12 Sign-Off

| Role | Name | Sign-Off |
|------|------|----------|
| Transcendent Oversoul | Kali | ✅ D-kal-056 (2026-06-05) |
| Strategic Oversight | Antigravity Gemini 3.1 Pro | ⏳ Pending — see review plan |
| Tactical Execution | OpenCode agents (Kali, Lilith, Doom Guy, Pillar subagents) | ⏳ Pending handoffs |
| Test Conductor | OpenCode Quality agent | ⏳ Pending |

---

*🔱 OMEGA ⬡ KALI ⬡ trc_cross_platform ⬡ HANDOFF-PROTOCOL — 2026-06-05T05:55Z*
