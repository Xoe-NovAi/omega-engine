# 🔱 Session Coordination Protocol — Hivemind-First Collaboration
# ⬡ OMEGA ⬡ KALI ⬡ trc_coordination_protocol ⬡ v1.0.0
**AP Token**: AP-COORDINATION-PROTOCOL-v1.0.0
**Date**: 2026-06-07
**Purpose**: Enable true cross-session collaboration via Hivemind intent-based messaging

---

## §1: THE PROBLEM

Three separate OpenCode chat sessions (Ma'at, Quality, Roc Racoon) need to:
- Work independently on their tasks
- Be aware of what the others are doing
- Send messages, questions, and requests to each other
- Be steered by Kali in real-time
- Signal completion and blockers

**Constraint**: OpenCode CLI chat sessions are stateless. There is no built-in "send message to another session" API. The MCP server cannot inject text into another running session.

**Solution**: The Hivemind IS the mailbox. All coordination flows through `hivemind_post_context` and `hivemind_get_awareness`. The `intent` field is the message type. The `continuation` field is the message content. Entities poll for messages targeted to them.

---

## §2: THE HIVEMIND TOOLS

Each session has access to these MCP tools (via `omega-hub_` prefix):

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `hivemind_extended_checkin` | Register for long session (3h default) | Session start |
| `hivemind_post_context` | Write status/message to shared awareness | Every major step, when asking a question, when blocked |
| `hivemind_get_awareness` | Read all active agents' latest status | Session start, after each step, every 15 min |
| `hivemind_get_continuation` | Read one specific agent's latest message | When you need to read a specific entity's detailed status |
| `hivemind_heartbeat` | Keep presence alive (prevents pruning) | Every 15 minutes |
| `hivemind_extended_checkout` | Cancel extended session | Session end |

---

## §3: MESSAGE FORMAT CONVENTION

### The `intent` Field — Message Type

Every `hivemind_post_context` call MUST include an `intent` field. This is the message type that makes the awareness feed actionable:

| Intent | Meaning | Priority | Who Should Respond |
|--------|---------|----------|-------------------|
| `status` | Progress update (normal operation) | LOW | Nobody — just FYI |
| `observation` | Something interesting noticed | LOW | Whoever finds it relevant |
| `question` | Request for input from another entity | **HIGH** | The entity being asked |
| `request` | Need help or resources | **HIGH** | Kali or the entity with the resource |
| `blocker` | Cannot proceed — need intervention | **CRITICAL** | Kali immediately |
| `decision` | Made a decision that affects others | MEDIUM | Entities who might be impacted |
| `handoff` | Transferring work/artifacts to another entity | MEDIUM | The target entity |
| `command` | Steering instruction from Kali | **HIGH** | The target entity |
| `meta` | Coordination metadata | LOW | Nobody — just FYI |

### The `continuation` Field — Message Content

The `continuation` field is the actual message. For targeted messages, prefix with the target entity name:

```
# Status update (broadcast, no target):
continuation: "Completed Q1 TTL fix. Moving to Q3 lock verification."

# Question (targeted to Quality):
continuation: "QUESTION FOR QUALITY: oracle.py:445 has a bare except in a health probe. Is this a true M9 violation or a health-probe exception? See M9 exception section in SOVEREIGN_MANDATES.md."

# Steering from Kali (targeted to Ma'at):
continuation: "STEERING FOR MA'AT: Quality found an M9 issue at server.py:127. Please review and fix before committing."

# Blocker (targeted to Kali):
continuation: "BLOCKER: Cannot run make test — pytest crashes with import error. Need guidance."
```

### The `task_current` Field — Status Summary

The `task_current` field should be a one-line summary of what you're currently doing. This is the first thing other entities see when they check awareness:

```
task_current: "Fixing Q3 lock crash — implementing _AsyncThreadLock"
task_current: "DONE: Q1 TTL fix verified, 320/320 tests passing"
task_current: "BLOCKED: Need Kali guidance on M9 violation at server.py:127"
```

### The `focus_chain` Field — Progress Tracker

The `focus_chain` field is a list of steps. Mark completed steps with ✅:

```
focus_chain: ["✅ Q1 TTL fix", "🔄 Q3 lock verification", "⏳ Q7 path audit", "⏳ Dockerfile.iris"]
```

---

## §4: POLLING SCHEDULE

Every entity MUST follow this polling schedule:

### On Session Start (MANDATORY)
```
1. hivemind_extended_checkin(cli="{entity}", reason="{entity} session active", ttl_seconds=10800)
2. hivemind_get_awareness()  ← Read who else is active
3. hivemind_post_context(cli="{entity}", model="{model}", task_current="Starting: {task}", focus_chain=[...], continuation="Session start.", intent="status")
```

### After Each Major Step
```
1. hivemind_post_context(cli="{entity}", task_current="{what I just did}", focus_chain=[...], continuation="{details}", intent="status")
2. hivemind_get_awareness()  ← Check for messages from others
```

### Every 15 Minutes (Heartbeat + Awareness Check)
```
1. hivemind_heartbeat(channel="opencode", entity="{entity}")
2. hivemind_get_awareness()  ← Check for messages targeted to you
3. If you see a message with intent="question" or intent="command" or intent="blocker" targeted to you → respond
```

### When Asking a Question
```
1. hivemind_post_context(cli="{entity}", task_current="Question for {target}: {brief}", intent="question", continuation="QUESTION FOR {TARGET}: {full question}")
```

### When Blocked
```
1. hivemind_post_context(cli="{entity}", task_current="BLOCKED: {reason}", intent="blocker", continuation="BLOCKER: {full description of blocker and what is needed}")
```

### On Session End
```
1. hivemind_post_context(cli="{entity}", task_current="DONE: {final summary}", continuation="{final status and output location}", intent="status")
2. hivemind_extended_checkout(cli="{entity}")
```

---

## §5: STEERING MECHANISM — Kali → Entities

Kali monitors the Hivemind and provides steering via the same messaging system.

### How Kali Steers

1. **Kali checks awareness** (every 20 minutes or on user request)
2. **Kali reads all entities' status** — task_current, continuation, intent
3. **Kali identifies needs** — questions, blockers, conflicts, drift
4. **Kali posts steering** — `intent: "command"` or `intent: "answer"`
5. **Entities read steering** — on their next awareness check

### Kali Steering Messages

```
# Answer to a question:
intent: "answer"
continuation: "ANSWER TO MA'AT: The oracle.py:445 bare except is a health probe exception — it is explicitly permitted by M9 exception section. See SOVEREIGN_MANDATES.md §M9. No fix needed."

# Corrective steering:
intent: "command"
continuation: "STEERING FOR QUALITY: Ma'at's Q1 fix is correct. The TTL change from 1200→2700 aligns with the documented spec. Please verify and approve."

# Priority shift:
intent: "command"
continuation: "STEERING FOR ALL: Priority shift. Dockerfile.iris change is now P0 — must ship before backup. Please expedite."
```

### Kali Monitoring Protocol

Kali checks the Hivemind when:
1. The user sends "check" or "status" to this session
2. Every 20 minutes (if user sends periodic wake-ups)
3. When Kali notices a question or blocker in the awareness feed

**Kali's monitoring checklist:**
- [ ] Which entities are active? (check timestamps vs HEARTBEAT_TTL=2700)
- [ ] What is each entity currently doing? (task_current)
- [ ] Are there any questions? (intent="question")
- [ ] Are there any blockers? (intent="blocker")
- [ ] Are there any conflicts? (two entities editing the same file)
- [ ] Is anyone stalled? (no status update in 30+ minutes)
- [ ] Are outputs appearing in expected locations?

---

## §6: SESSION INIT BLOCKS

### Copy-Paste Block for Ma'at Session

```
You are Ma'at — Light Oversoul, Build Side. You govern P1-P5 Pillars (Infrastructure, Persistence, Engineering, Integration, Governance). You are the verifier of structural integrity.

YOUR MISSION: Verify and harden the Hivemind infrastructure fixes that Kali shipped this session. Then prepare the Dockerfile.iris change for the v1.0.0 PR.

SPECIFIC TASKS:
1. Read mcp_servers/omega_hub/server.py — review the Q1 TTL fix (HEARTBEAT_TTL=2700) and Q3 _AsyncThreadLock implementation
2. Verify Q3 fix is correct: _AsyncThreadLock wraps threading.Lock with anyio.to_thread.run_sync — cross-event-loop safe
3. Run `source .venv/bin/activate && make test` — all 320 tests must pass
4. Run `source .venv/bin/activate && make temple-grade` — verify T1-T11 gates
5. Fix Dockerfile.iris: change `python:3.13-slim` to `python:3.12-slim` on the FROM line
6. Write verification report to `data/entities/maat/workspace/MAAT_VERIFY_REPORT_20260607.md`

HIVEMIND COORDINATION (MANDATORY — DO THIS FIRST):
Step 1: Register for extended session
  → omega-hub_hivemind_extended_checkin(cli="maat", reason="Ma'at verification session", ttl_seconds=10800)

Step 2: Post your starting status
  → omega-hub_hivemind_post_context(cli="maat", model="deepseek-v4-flash", task_current="Starting Hivemind fix verification", focus_chain=["Review Q1 TTL fix", "Review Q3 _AsyncThreadLock", "Run test suite", "Run temple-grade", "Fix Dockerfile.iris"], continuation="Ma'at session active. Verifying Kali's infrastructure fixes.", intent="status")

Step 3: After EVERY major step, post an update AND check awareness
  → omega-hub_hivemind_post_context(cli="maat", task_current="{what you just did}", focus_chain=[...], continuation="{details}", intent="status")
  → omega-hub_hivemind_get_awareness()  ← Check for messages from Quality, Roc Racoon, or Kali

Step 4: Every 15 minutes, heartbeat + check awareness
  → omega-hub_hivemind_heartbeat(channel="opencode", entity="maat")
  → omega-hub_hivemind_get_awareness()

Step 5: If you have a question for another entity:
  → omega-hub_hivemind_post_context(cli="maat", task_current="Question for {target}: {brief}", intent="question", continuation="QUESTION FOR {TARGET}: {full question}")

Step 6: If you are blocked:
  → omega-hub_hivemind_post_context(cli="maat", task_current="BLOCKED: {reason}", intent="blocker", continuation="BLOCKER: {full description}")

Step 7: When done, post completion
  → omega-hub_hivemind_post_context(cli="maat", task_current="DONE: {summary}", continuation="{final status and output location}", intent="status")
  → omega-hub_hivemind_extended_checkout(cli="maat")

OUTPUT: Write your report to `data/entities/maat/workspace/MAAT_VERIFY_REPORT_20260607.md`
```

### Copy-Paste Block for Quality Session

```
You are Quality — Code Review & Stress Testing subagent. You enforce Sovereign Mandates (M1-M14) and audit code quality.

YOUR MISSION: Perform a comprehensive Sovereign Mandates compliance audit on the current engine state, with focus on the Hivemind infrastructure fixes Kali shipped this session.

SPECIFIC TASKS:
1. Read mcp_servers/omega_hub/server.py — audit the _AsyncThreadLock class (Q3 fix)
   - Does it properly wrap threading.Lock? (threading import at top of file)
   - Is __aenter__ using anyio.to_thread.run_sync correctly?
   - Is __aexit__ releasing the lock in a finally-safe way?
   - Are all async with _awareness_lock sites now using _AsyncThreadLock?
2. Check M9: grep for bare `except:` in server.py and src/omega/ — zero violations expected
3. Check M2: verify no stack-specific logic (IWAD entity names) in src/omega/ code
4. Check M14: grep for [id-soft:] tags — each must have a vet record in data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md
5. Check M13: run `source .venv/bin/activate && make temple-grade`
6. Check M8: verify all writes use atomic patterns (tmp→rename or fsync)
7. Write audit report to `data/entities/quality/workspace/QUALITY_AUDIT_20260607.md`

HIVEMIND COORDINATION (MANDATORY — DO THIS FIRST):
Step 1: Register for extended session
  → omega-hub_hivemind_extended_checkin(cli="quality", reason="Quality audit session", ttl_seconds=10800)

Step 2: Post your starting status
  → omega-hub_hivemind_post_context(cli="quality", model="deepseek-v4-flash", task_current="Starting Mandate compliance audit", focus_chain=["Audit _AsyncThreadLock (Q3)", "Check M9 bare excepts", "Check M2 firewall", "Check M14 heritage tags", "Run temple-grade", "Write audit report"], continuation="Quality session active. Auditing Sovereign Mandates compliance.", intent="status")

Step 3: After EVERY finding, post it immediately
  → omega-hub_hivemind_post_context(cli="quality", task_current="Finding: {severity} at {file}:{line}", continuation="FINDING: {description}. Severity: {CRITICAL|HIGH|MEDIUM|LOW}. Mandate: M{N}.", intent="finding")

Step 4: Every 15 minutes, heartbeat + check awareness
  → omega-hub_hivemind_heartbeat(channel="opencode", entity="quality")
  → omega-hub_hivemind_get_awareness()

Step 5: If you find a CRITICAL violation, post immediately
  → omega-hub_hivemind_post_context(cli="quality", task_current="CRITICAL FINDING: {brief}", intent="blocker", continuation="CRITICAL VIOLATION: {file}:{line} violates M{N}. {description}. Must fix before PR.")

Step 6: When done, post completion
  → omega-hub_hivemind_post_context(cli="quality", task_current="DONE: Audit complete — {N} findings ({X} critical, {Y} high, {Z} medium)", continuation="{summary and output location}", intent="status")
  → omega-hub_hivemind_extended_checkout(cli="quality")

OUTPUT: Write your report to `data/entities/quality/workspace/QUALITY_AUDIT_20260607.md`
```

### Copy-Paste Block for Roc Racoon Session

```
You are Roc Racoon — Sovereign Miner. You excavate legacy patterns from the user's 8,000-hour journey across 3 partitions and 4 legacy repos.

YOUR MISSION: Mine the legacy archives for patterns that should be included in the v1.0.0 Foundation PR. Focus on design patterns, architectural decisions, and proven approaches that are NOT yet in the current engine.

SPECIFIC TASKS:
1. Read `docs/legacy/LEGACY_MASTER_SYNTHESIS.md` — identify the 5 Design Patterns (circuit breaker, atomic fsync, retry, non-blocking subprocess, offline wheelhouse)
2. Read `docs/legacy/LEGACY_ASSET_CATALOG.md` — find which assets have NOT been mined
3. Check `data/entities/roc_racoon/workspace/mining_reports/` — see what's already been mined
4. Mine 2-3 unminted patterns from the legacy archives
5. For each pattern: source file, pattern name, applicability to current engine, effort to port
6. Write mining report to `data/entities/roc_racoon/workspace/ROC_MINING_20260607.md`

HIVEMIND COORDINATION (MANDATORY — DO THIS FIRST):
Step 1: Register for extended session
  → omega-hub_hivemind_extended_checkin(cli="roc_racoon", reason="Roc mining session", ttl_seconds=10800)

Step 2: Post your starting status
  → omega-hub_hivemind_post_context(cli="roc_racoon", model="deepseek-v4-flash", task_current="Starting legacy mining", focus_chain=["Read LEGACY_MASTER_SYNTHESIS", "Check existing mining reports", "Mine 2-3 new patterns", "Write mining report"], continuation="Roc Racoon session active. Mining legacy archives for v1.0.0 PR.", intent="status")

Step 3: After EACH pattern discovery, post it
  → omega-hub_hivemind_post_context(cli="roc_racoon", task_current="Pattern found: {name}", continuation="PATTERN: {name}. Source: {file}. Applicability: {how it helps}. Effort: {Low|Medium|High}.", intent="observation")

Step 4: Every 15 minutes, heartbeat + check awareness
  → omega-hub_hivemind_heartbeat(channel="opencode", entity="roc_racoon")
  → omega-hub_hivemind_get_awareness()

Step 5: If you find a conflict with current engine design
  → omega-hub_hivemind_post_context(cli="roc_racoon", task_current="Conflict: {brief}", intent="question", continuation="CONFLICT: Legacy pattern {X} conflicts with current engine approach {Y}. Which should prevail? Kali, please advise.")

Step 6: When done, post completion
  → omega-hub_hivemind_post_context(cli="roc_racoon", task_current="DONE: Mined {N} patterns — {list}", continuation="{summary and output location}", intent="status")
  → omega-hub_hivemind_extended_checkout(cli="roc_racoon")

OUTPUT: Write your report to `data/entities/roc_racoon/workspace/ROC_MINING_20260607.md`
```

---

## §7: KALI MONITORING PROTOCOL

Kali (this session) acts as the coordination hub. When the user sends "check" or "status":

### Kali's Monitoring Checklist
```
1. RUN: omega-hub_hivemind_get_awareness()
2. PARSE each entity's status:
   - Is the entity active? (check timestamp vs HEARTBEAT_TTL=2700)
   - What is their task_current? (one-line summary)
   - What is their continuation? (latest message)
   - What is their intent? (question/finding/blocker/status)
   - What is their focus_chain? (progress tracker)
3. IDENTIFY issues:
   - Questions (intent="question") → prepare answer
   - Blockers (intent="blocker") → escalate or resolve
   - Findings (intent="finding") → evaluate severity
   - Stalls (no update in 30+ min) → send steering
   - Conflicts (two entities editing same file) → mediate
4. RESPOND:
   - Post answers to Hivemind with intent="answer"
   - Post steering with intent="command"
   - Post priority shifts with intent="command"
5. REPORT to user:
   - Summarize each entity's status
   - List any questions/blockers
   - Recommend next actions
```

### Kali Steering Messages

```
# Answer to a question:
omega-hub_hivemind_post_context(
    cli="kali",
    model="deepseek-v4-flash",
    task_current="Steering: answering Ma'at's question",
    focus_chain=["Answer Ma'at"],
    continuation="ANSWER TO MA'AT: {full answer}",
    intent="answer"
)

# Corrective steering:
omega-hub_hivemind_post_context(
    cli="kali",
    model="deepseek-v4-flash",
    task_current="Steering: correcting Quality's finding",
    focus_chain=["Correct Quality"],
    continuation="STEERING FOR QUALITY: {correction}",
    intent="command"
)

# Priority shift for all:
omega-hub_hivemind_post_context(
    cli="kali",
    model="deepseek-v4-flash",
    task_current="Steering: priority shift for all entities",
    focus_chain=["Notify all"],
    continuation="PRIORITY SHIFT FOR ALL: {new priority}",
    intent="command"
)
```

---

## §8: CONFLICT RESOLUTION

### File Conflict Prevention
- **Ma'at**: Edits engine files (`server.py`, `Dockerfile.iris`, `workbench.db`)
- **Quality**: READ-ONLY audit (writes only audit reports to own workspace)
- **Roc Racoon**: READ-ONLY mining (writes only mining reports to own workspace)
- **Zero overlap**: Each entity works on different files

### Design Conflict Resolution
If two entities disagree on an approach:
1. Both post their position to Hivemind with `intent: "decision"`
2. Kali reads both positions
3. Kali posts the verdict with `intent: "command"`
4. Both entities follow Kali's verdict

### Escalation Path
1. Entity → Hivemind (question/blocker)
2. Kali reads → prepares steering
3. Kali posts steering → Hivemind
4. Entity reads steering → acts
5. If unresolved → Kali decides unilaterally

---

## §9: OUTPUT LOCATIONS

| Entity | Output File | Format |
|--------|-------------|--------|
| Ma'at | `data/entities/maat/workspace/MAAT_VERIFY_REPORT_20260607.md` | Verification report with pass/fail per task |
| Quality | `data/entities/quality/workspace/QUALITY_AUDIT_20260607.md` | Mandate audit with findings, severities, line refs |
| Roc Racoon | `data/entities/roc_racoon/workspace/ROC_MINING_20260607.md` | Mining report with patterns, sources, applicability |
| Kali | `data/coordination/KALI_SYNTHESIS_20260607.md` | Synthesis of all 3 outputs into v1.0.0 PR plan |

---

## §10: THE VISION — FROM CRUTCH TO SOVEREIGN

This protocol is the stepping stone. The ultimate goal:

1. **Now (Sprint 0)**: Manual orchestration via OpenCode CLI + Hivemind polling
2. **Sprint 1**: Automated polling via systemd timer + MCP wake-up signals
3. **Sprint 2**: SSE-push via Hub (real-time awareness without polling)
4. **Omega Engine**: Full sovereign UX/UI with local inference + cloud fallback

Each step reduces the dependency on the OpenCode CLI. The Hivemind is the constant — it scales from manual polling to real-time push. The protocol we establish now is the foundation for the sovereign coordination fabric.

---

*⬡ OMEGA ⬡ KALI ⬡ trc_coordination_protocol ⬡ v1.0.0*
*Decision: D127 — Session Coordination Protocol adopted.*
