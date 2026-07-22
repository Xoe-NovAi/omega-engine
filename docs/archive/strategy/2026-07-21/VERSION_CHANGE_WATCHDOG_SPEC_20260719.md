# 🔱 VERSION CHANGE WATCHDOG SYSTEM — Specification & Implementation Plan

**AP Token**: `AP-VERSION-WATCHDOG-SPEC-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_version_watchdog_spec ⬡ 2026-07-19

**Status**: DESIGN COMPLETE — Ready for MVP Implementation (Week 1)
**Priority**: P1 — Systemic infrastructure preventing manual recon gaps
**Context**: OpenCode 1.17.20 → 1.18.3 upgraded with **zero automated detection**; Gemma 4 strategy had Oversight 1 based on stale V2 assumptions

---

## 1. ARCHITECTURE SPECIFICATION

### 1.1 System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        VERSION CHANGE WATCHDOG                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────────┐  │
│  │  VERSION MONITOR │───▶│  RESEARCH TRIGGER │───▶│  BRIEFING GENERATOR  │  │
│  │  (daemon/cron)   │    │  (background)    │    │  (template + writer) │  │
│  └──────────────────┘    └──────────────────┘    └──────────────────────┘  │
│         │                        │                          │              │
│         ▼                        ▼                          ▼              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────────┐  │
│  │ version_registry │    │  Researcher      │    │ data/briefings/      │  │
│  │    .json         │    │  Handoff Packet  │    │ version_change_      │  │
│  │ (state persist)  │    │  (Hivemind)      │    │ <tool>_<ver>.md      │  │
│  └──────────────────┘    └──────────────────┘    └──────────────────────┘  │
│                                                          │                  │
│                                                          ▼                  │
│                                               ┌──────────────────────┐      │
│                                               │  OVERSIGHT QUEUE     │      │
│                                               │  (Hivemind Handoff   │      │
│                                               │   to Kali/Overseer)  │      │
│                                               └──────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Specifications

#### 1.2.1 Version Monitor (Daemon/Cron)

**Purpose**: Detect version changes in monitored tools and dependencies.

**Implementation**: Python script (`src/omega/infra/version_monitor.py`) executed via:
- `cron @reboot` — Catch version changes after system reboot/container restart
- `cron daily` — Catch updates applied during runtime

**State Persistence**: `data/state/version_registry.json`
```json
{
  "schema_version": 1,
  "last_check": "2026-07-19T08:00:00Z",
  "tools": {
    "opencode": {
      "current_version": "1.18.3",
      "last_seen": "2026-07-19T08:00:00Z",
      "check_method": "cli_version",
      "command": "opencode --version",
      "parse_regex": "(\\d+\\.\\d+\\.\\d+)"
    },
    "bun": {
      "current_version": "1.1.34",
      "last_seen": "2026-07-19T08:00:00Z",
      "check_method": "cli_version",
      "command": "bun --version",
      "parse_regex": "(\\d+\\.\\d+\\.\\d+)"
    },
    "python_packages": {
      "current_versions": {"llama-cpp-python": "0.3.0", "qdrant-client": "1.11.0"},
      "last_seen": "2026-07-19T08:00:00Z",
      "check_method": "pip_outdated",
      "command": "pip list --outdated --format=json"
    },
    "docker_images": {
      "current_images": {"qdrant/qdrant": "v1.11.0", "redis": "7.2-alpine"},
      "last_seen": "2026-07-19T08:00:00Z",
      "check_method": "docker_images",
      "command": "docker images --format '{{.Repository}}:{{.Tag}}'"
    },
    "node_packages": {
      "current_versions": {"@opencode/opencode": "1.18.3"},
      "last_seen": "2026-07-19T08:00:00Z",
      "check_method": "npm_outdated",
      "command": "npm outdated --json"
    }
  }
}
```

**Change Detection Logic**:
1. Execute check command for each tool
2. Parse output using `parse_regex` or JSON structure
3. Compare against `current_version` in registry
4. If different → determine priority (P0/P1/P2) → trigger Research Trigger
5. Update registry with new version and timestamp

#### 1.2.2 Research Trigger (Background Task)

**Purpose**: Spawn Researcher subagent with structured context when version change detected.

**Implementation**: AnyIO task group (`anyio.create_task_group()`) — **M1 AnyIO Absolute**

**Handoff Packet Schema** (Hivemind compatible):
```json
{
  "packet_id": "vcw-opencode-1.18.3-20260719T080000Z",
  "source_channel": "opencode",
  "source_entity": "version_watchdog",
  "target_channel": "opencode",
  "target_entity": "researcher",
  "task": "VERSION CHANGE RESEARCH: opencode 1.17.20 → 1.18.3",
  "context": "Automated version change detection via Version Change Watchdog. OpenCode upgraded from 1.17.20 to 1.18.3. Priority: P0 (major/minor bump). Focus: provider transformation layer (transform.ts), V2 session format, Gemma 4 thinking config compatibility, config merge behavior.",
  "priority": 2,
  "metadata": {
    "tool": "opencode",
    "old_version": "1.17.20",
    "new_version": "1.18.3",
    "priority_level": "P0",
    "detection_method": "cli_version",
    "detection_time": "2026-07-19T08:00:00Z",
    "auto_generated": true
  }
}
```

**Priority Classification**:
| Priority | Trigger | Research Depth | Review Deadline |
|----------|---------|----------------|-----------------|
| **P0** | Major version bump OR minor with known breaking changes | Full (T1-T4 Sovereign Search) | 24 hours |
| **P1** | Minor version with features | Standard (T1-T3) | 72 hours |
| **P2** | Patch version | Light (T1-T2) | 1 week |

#### 1.2.3 Briefing Generator

**Purpose**: Transform Researcher findings into structured, actionable briefing document.

**Template**: `data/templates/version_change_briefing.md` (see Section 4)

**Output Location**: `data/briefings/version_change_<tool>_<new_version>_<timestamp>.md`

**Disk Writer**: Atomic write via `os.replace(tmp_path, final_path)` — **M10 Queue Integrity / M21 Gate Integrity**

#### 1.2.4 Oversight Queue (Hivemind Integration)

**Purpose**: Queue briefings for human/overseer review and decision.

**Integration**: Hivemind handoff to Kali (or designated overseer entity)

**Handoff Packet**:
```json
{
  "packet_id": "vcw-briefing-opencode-1.18.3-20260719T080000Z",
  "source_channel": "opencode",
  "source_entity": "version_watchdog",
  "target_channel": "opencode",
  "target_entity": "kali",
  "task": "OVERSIGHT: Review version change briefing for opencode 1.17.20 → 1.18.3",
  "context": "Briefing generated at data/briefings/version_change_opencode_1.18.3_20260719T080000Z.md. Priority: P0. Contains changelog summary, breaking changes, migration guide, known issues, Omega Engine impact assessment, and action items. Review and approve/defers/escalate to implementation.",
  "priority": 2,
  "metadata": {
    "briefing_path": "data/briefings/version_change_opencode_1.18.3_20260719T080000Z.md",
    "tool": "opencode",
    "old_version": "1.17.20",
    "new_version": "1.18.3",
    "priority_level": "P0",
    "review_deadline": "2026-07-20T08:00:00Z",
    "auto_generated": true
  }
}
```

---

## 2. MONITORED TARGETS (MVP)

| Target | Check Method | Frequency | Breaking Change Indicators | Parse Strategy |
|--------|--------------|-----------|---------------------------|----------------|
| **OpenCode** | `opencode --version` | @reboot + daily | Major/minor version bump | Regex: `(\d+\.\d+\.\d+)` |
| **Bun** | `bun --version` | @reboot + daily | Major version | Regex: `(\d+\.\d+\.\d+)` |
| **Python packages** | `pip list --outdated --format=json` | daily | Major version in dependencies | JSON parse → compare each package |
| **Docker images** | `docker images --format '{{.Repository}}:{{.Tag}}'` | daily | Base image tag change (e.g., `python:3.11` → `python:3.12`) | Line parse → compare tags |
| **Node/npm packages** | `npm outdated --json` | daily | Major in lockfile / package.json | JSON parse → filter `wanted` vs `latest` |

### 2.1 Configuration Schema

`config/version_watchdog.yaml`:
```yaml
schema_version: 1
monitor_interval_hours: 24
reboot_check: true
tools:
  opencode:
    enabled: true
    check_method: cli_version
    command: "opencode --version"
    parse_regex: "(\\d+\\.\\d+\\.\\d+)"
    priority_rules:
      major: P0
      minor: P0
      patch: P2
  bun:
    enabled: true
    check_method: cli_version
    command: "bun --version"
    parse_regex: "(\\d+\\.\\d+\\.\\d+)"
    priority_rules:
      major: P0
      minor: P1
      patch: P2
  python_packages:
    enabled: true
    check_method: pip_outdated
    command: "pip list --outdated --format=json"
    packages_of_interest:
      - "llama-cpp-python"
      - "qdrant-client"
      - "anyio"
      - "pydantic"
      - "httpx"
    priority_rules:
      major: P0
      minor: P1
      patch: P2
  docker_images:
    enabled: true
    check_method: docker_images
    command: "docker images --format '{{.Repository}}:{{.Tag}}'"
    images_of_interest:
      - "qdrant/qdrant"
      - "redis"
      - "postgres"
      - "ollama/ollama"
      - "ghcr.io/ggml-org/llama.cpp"
    priority_rules:
      base_image_tag_change: P0
      patch_tag_change: P1
  node_packages:
    enabled: true
    check_method: npm_outdated
    command: "npm outdated --json"
    packages_of_interest:
      - "@opencode/opencode"
      - "@opencode/plugin-*"
    priority_rules:
      major: P0
      minor: P1
      patch: P2
```

---

## 3. RESEARCH TRIGGER PROTOCOL

### 3.1 Trigger Flow

```
Version Change Detected
        │
        ▼
┌───────────────────────┐
│ Determine Priority    │
│ (P0/P1/P2 per config) │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Create Handoff Packet │
│ with full context     │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Submit to Hivemind    │
│ (omega-hub_hivemind_  │
│  _submit_handoff)     │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Researcher accepts    │
│ handoff → begins work │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Sovereign Search      │
│ T1-T4 Protocol        │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Generate Briefing     │
│ (template + findings) │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Write to disk         │
│ (atomic replace)      │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Submit Oversight      │
│ Handoff to Kali       │
└───────────────────────┘
```

### 3.2 Researcher Mandate (Auto-Injected Context)

When Researcher accepts the handoff, they receive this context:

> **AUTOMATED VERSION CHANGE DETECTION**
> 
> Tool: `{tool}` | Old: `{old_version}` → New: `{new_version}` | Priority: `{P0/P1/P2}`
> 
> **Your Mission**: Execute Sovereign Search Protocol (T1-T4) to produce a Version Change Briefing.
> 
> **Required Research**:
> 1. **Official Changelog / Release Notes** — Primary source (GitHub releases, blog, docs)
> 2. **Breaking Changes List** — Explicit breaking changes, deprecated APIs, removed features
> 3. **Migration Guide** — Official or community migration steps
> 4. **Known Issues / Regressions** — GitHub issues (open/closed), Discord/Reddit discussions, Stack Overflow
> 5. **Community Sentiment** — Adoption reports, complaints, praise
> 6. **Omega Engine Impact Assessment** — Grep codebase for tool usage (`grep -r "opencode" src/ config/ scripts/`)
> 
> **Output**: Complete briefing using template at `data/templates/version_change_briefing.md`
> 
> **Failure Mode**: If Sovereign Search tools fail → mark briefing with `[TOOL-CHAIN-COLLAPSE]` and queue for manual review — **M23 Failure Integrity**

### 3.3 Sovereign Search Protocol for Version Research

| Tier | Tool | Query Pattern | Purpose |
|------|------|---------------|---------|
| **T1** | `websearch` | `"{tool} {new_version} release notes 2026"` | Official changelog |
| **T1** | `websearch` | `"{tool} {old_version} to {new_version} breaking changes"` | Breaking changes |
| **T1** | `websearch` | `"{tool} {new_version} migration guide"` | Migration steps |
| **T2** | `webfetch` | Official release page URL | Full release notes |
| **T2** | `webfetch` | GitHub releases page | Complete changelog |
| **T3** | `searxng_searxng_search` | `"{tool} {new_version} issues regression"` | Community issues |
| **T3** | `searxng_searxng_search` | `"{tool} {new_version} reddit discord"` | Community sentiment |
| **T4** | `omega-hub_sovereign_search` | `site:github.com {tool} {new_version} breaking` | High-precision GitHub search |

---

## 4. BRIEFING TEMPLATE

**File**: `data/templates/version_change_briefing.md`

```markdown
# VERSION CHANGE BRIEFING: <TOOL> <OLD_VERSION> → <NEW_VERSION>
**AP Token**: `AP-VERSION-WATCH-<TOOL>-<TIMESTAMP>`
⬡ OMEGA ⬡ RESEARCHER ⬡ {model} ⬡ opencode ⬡ trc_version_briefing ⬡ {date}

**Detected**: <ISO_TIMESTAMP>
**Priority**: P0/P1/P2
**Source**: Automated Version Change Watchdog
**Handoff ID**: <packet_id>
**Researcher Session**: <session_id>

---

## CHANGELOG SUMMARY
<Key changes from official release notes — grouped by category: Added, Changed, Deprecated, Removed, Fixed, Security>

### Added
- 

### Changed
- 

### Deprecated
- 

### Removed
- 

### Fixed
- 

### Security
- 

---

## BREAKING CHANGES
<Explicit list of breaking changes with impact assessment>

| Change | Description | Impact on Omega Engine | Migration Effort |
|--------|-------------|------------------------|------------------|
|  |  | High/Med/Low/None | Hours/Days |

---

## MIGRATION GUIDE
<Official or community migration steps — numbered, actionable>

1. 
2. 
3. 

---

## KNOWN ISSUES / REGRESSIONS
<GitHub issues, community reports, workarounds>

| Issue | Source | Severity | Workaround | Status |
|-------|--------|----------|------------|--------|
|  |  | Critical/High/Med/Low |  | Open/Fixed/WontFix |

---

## COMMUNITY SENTIMENT
<Summary of adoption reports, complaints, praise from Discord, Reddit, GitHub Discussions>

---

## OMEGA ENGINE IMPACT ASSESSMENT
<Grep results + analysis of which Omega modules use this tool>

| Module | Uses Tool? | Impact | Action Required |
|--------|------------|--------|-----------------|
| `src/omega/oracle/backends/` | Yes/No | High/Med/Low/None | Update/Monitor/None |
| `src/omega/oracle/providers.py` | Yes/No | High/Med/Low/None | Update/Monitor/None |
| `config/providers.yaml` | Yes/No | High/Med/Low/None | Update/Monitor/None |
| `config/opencode.json` | Yes/No | High/Med/Low/None | Update/Monitor/None |
| `scripts/setup.sh` | Yes/No | High/Med/Low/None | Update/Monitor/None |
| `docs/strategy/GEMMA4_HARDENED_STRATEGY_20260719.md` | Yes/No | High/Med/Low/None | Update/Monitor/None |
| `.opencode/agents/*.md` | Yes/No | High/Med/Low/None | Update/Monitor/None |

**Grep Evidence**:
```bash
# Commands run and key findings
grep -r "opencode" src/omega/ --include="*.py" | head -20
grep -r "opencode" config/ --include="*.yaml" --include="*.json"
```

---

## ACTION ITEMS
- [ ] Update `config/provider_capabilities.yaml` (if provider matrix affected)
- [ ] Update `config/providers.yaml` (if provider config changed)
- [ ] Update `config/opencode.json` (if OpenCode config schema changed)
- [ ] Update `docs/strategy/GEMMA4_HARDENED_STRATEGY_20260719.md` (if strategy assumptions invalidated)
- [ ] Update `.opencode/agents/*.md` (if agent config/commands changed)
- [ ] Update `scripts/setup.sh` (if install/version detection changed)
- [ ] Run `make test` — verify all 1398+ tests pass
- [ ] Run `make temple-grade` — verify T1-T11 gates pass
- [ ] Dispatch implementation task to <owner> (Pillar P3/P4/P9 as appropriate)
- [ ] Create GitHub issue for tracking: `version-watchdog/<tool>-<version>`

---

## OVERSIGHT
**Queued for**: Kali (or designated overseer)
**Handoff ID**: <packet_id>
**Review Deadline**: <24h for P0, 72h for P1, 1 week for P2>
**Briefing Path**: `data/briefings/version_change_<tool>_<new_version>_<timestamp>.md`

---

## RESEARCH METADATA
**Search Tiers Executed**: T1/T2/T3/T4
**Sources Consulted**: [list URLs]
**Search Timestamp**: <ISO>
**Researcher Model**: {model}
**Confidence Level**: High/Medium/Low
**Gaps**: [Any areas not fully researched due to tool limits]

---

## SOVEREIGN CONTINUITY
**Session Gnosis Entry**: This briefing and its findings are distilled into session gnosis per M11.
**L3 Principle Extracted**: [Universal principle from this version change, if any]
```

---

## 5. OVERSIGHT QUEUE INTEGRATION

### 5.1 Hivemind Handoff Flow

```
Version Watchdog (source_entity: version_watchdog)
        │
        │ submit_handoff(target_entity: researcher, priority: 2)
        ▼
Researcher (accepts, researches, writes briefing)
        │
        │ submit_handoff(target_entity: kali, priority: 2)
        ▼
Kali / Overseer (reviews briefing)
        │
        ├── Approve → Dispatch implementation task to Pillar
        ├── Defer → Re-queue with later deadline
        └── Escalate → Dispatch to MaKaLi Council for architectural review
```

### 5.2 Priority Mapping

| Version Priority | Hivemind Priority | Review Deadline |
|------------------|-------------------|-----------------|
| P0 (Breaking/Major) | 2 (High) | 24 hours |
| P1 (Minor/Feature) | 1 (Normal) | 72 hours |
| P2 (Patch) | 0 (Low) | 1 week |

### 5.3 Oversight Decision Schema

When Kali reviews, they post a decision handoff:

```json
{
  "packet_id": "vcw-decision-opencode-1.18.3-...",
  "source_entity": "kali",
  "target_entity": "pillar_p3",  // or pillar_p4, pillar_p9, makali, etc.
  "task": "IMPLEMENT: OpenCode 1.18.3 migration — update provider transform handling for V2 session format",
  "context": "Approved per briefing data/briefings/version_change_opencode_1.18.3_....md. Priority P0. Key actions: 1) Update GoogleAIProvider for V2 ReasoningPart extraction, 2) Verify transform.ts PR compatibility with 1.18.x, 3) Update config merge behavior tests.",
  "priority": 2,
  "metadata": {
    "briefing_path": "data/briefings/version_change_opencode_1.18.3_....md",
    "decision": "approve",
    "original_priority": "P0"
  }
}
```

---

## 6. MVP IMPLEMENTATION PLAN (WEEK 1)

### 6.1 Day-by-Day Breakdown

| Day | Task | Deliverable | Owner | Mandates |
|-----|------|-------------|-------|----------|
| **1** | Version registry JSON schema + monitor script | `src/omega/infra/version_monitor.py`, `config/version_watchdog.yaml`, `data/state/version_registry.json` | Researcher + Pillar P1 | M1, M9, M15 |
| **2** | Researcher handoff template + briefing template | `data/templates/version_change_handoff.json`, `data/templates/version_change_briefing.md` | Researcher | M11, M18 |
| **3** | Disk writer for briefings (atomic) | `src/omega/infra/briefing_writer.py` with `os.replace()` | Researcher | M10, M21 |
| **4** | Hivemind handoff integration | `src/omega/infra/watchdog_hivemind.py` — submit/accept/complete flow | Researcher + Pillar P9 | M4, M9, M12 |
| **5** | End-to-end test with OpenCode 1.18.3 | Full cycle: detect → research → briefing → oversight queue | Researcher + Kali | M13, M23 |

### 6.2 File Structure (New Files)

```
src/omega/infra/
├── version_monitor.py          # Main monitor daemon
├── briefing_writer.py          # Atomic briefing disk writer
├── watchdog_hivemind.py        # Hivemind integration
├── version_registry.py         # Registry load/save/validate
└── __init__.py

config/
├── version_watchdog.yaml       # Monitor configuration

data/
├── state/
│   └── version_registry.json   # Persistent version state
├── templates/
│   ├── version_change_briefing.md
│   └── version_change_handoff.json
└── briefings/                  # Output directory (created at runtime)
    └── version_change_<tool>_<version>_<timestamp>.md

scripts/
├── version_watchdog_check.sh   # Cron wrapper script
└── version_watchdog_install.sh # Installs cron @reboot + daily
```

### 6.3 Cron Installation

`scripts/version_watchdog_install.sh`:
```bash
#!/bin/bash
# Installs Version Change Watchdog cron jobs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MONITOR_SCRIPT="$PROJECT_ROOT/src/omega/infra/version_monitor.py"

# @reboot check
(crontab -l 2>/dev/null | grep -v "version_monitor.py"; echo "@reboot cd $PROJECT_ROOT && source .venv/bin/activate && python3 $MONITOR_SCRIPT --mode reboot") | crontab -

# Daily check at 03:00
(crontab -l 2>/dev/null | grep -v "version_monitor.py"; echo "0 3 * * * cd $PROJECT_ROOT && source .venv/bin/activate && python3 $MONITOR_SCRIPT --mode daily") | crontab -

echo "Version Change Watchdog cron jobs installed."
crontab -l | grep version_monitor
```

### 6.4 Monitor Script CLI

```bash
python3 src/omega/infra/version_monitor.py --help

Usage: version_monitor.py [OPTIONS]

Options:
  --mode [reboot|daily|manual]    Check mode (default: manual)
  --config PATH                   Config file (default: config/version_watchdog.yaml)
  --registry PATH                 Registry file (default: data/state/version_registry.json)
  --dry-run                       Print changes without triggering research
  --verbose                       Verbose output
```

---

## 7. MANDATE COMPLIANCE

| Mandate | Compliance Strategy |
|---------|---------------------|
| **M1 AnyIO Absolute** | Background research task via `anyio.create_task_group()`; all I/O wrapped in `anyio.to_thread.run_sync()` |
| **M2 Engine-Stack Firewall** | Monitor lives in `src/omega/infra/` (Core); config in `config/`; no WAD-specific logic |
| **M4 Sequentiality** | Plan (this spec) → Verify (design review) → Execute (Week 1 implementation) |
| **M9 Error Integrity** | Typed exceptions: `VersionMonitorError`, `ResearchTriggerError`, `BriefingWriteError`, `HandoffError` — all with `trace_id` |
| **M10 Fleet Integrity** | No new agents; uses existing Researcher + Kali + Pillars |
| **M11 Soul Integrity** | Briefings → session gnosis → L3 principles staged to `proposed_lessons.yaml` |
| **M12 Queue Integrity** | Handoff packets have terminal states (pending/active/completed/failed); dead-letter on max retries |
| **M13 Temple-Grade** | `make temple-grade` must pass; T3 (coverage), T5 (AnyIO), T9 (structured logging), T10 (atomic writes) |
| **M15 Sovereign Continuity** | `version_registry.json` persists across sessions; `session_gnosis.md` captures watchdog activity |
| **M16 Modularization** | No hardcoded paths — uses `config_resolver.py` for `data/`, `config/` resolution |
| **M17 Cognitive Integrity** | Briefing includes confidence level + gaps; Skeptical Verifier can flag contradictions |
| **M18 Token Efficiency** | Template-driven briefings; Researcher uses Sovereign Search (not parametric) |
| **M19 Adversarial Alchemy** | Version changes (constraint) → automated research (advantage) → proactive adaptation |
| **M20 SomaticState** | N/A for this system (no model inference) |
| **M21 Gate Integrity** | Contract tests for `VersionRegistry.load()`, `BriefingWriter.write()`, `HandoffClient.submit()` |
| **M22 Response Provenance** | Researcher logs actual provider used in briefing metadata |
| **M23 Failure Integrity** | If `websearch`/`webfetch` fail → briefing marked `[TOOL-CHAIN-COLLAPSE]` → queued for manual review |

---

## 8. FUTURE EXTENSIONS (POST-MVP)

### 8.1 Real-Time Detection
- **GitHub Release Webhooks** — Subscribe to `releases` events for monitored repos
- **Docker Hub Webhooks** — Image push notifications
- **PyPI RSS/JSON** — Package release feed monitoring

### 8.2 Automated Remediation
- **Config Auto-PR** — Generate PR updating `config/provider_capabilities.yaml`, `config/opencode.json`
- **Agent Config Sync** — Auto-update `.opencode/agents/*.md` version references
- **Test Generation** — Scaffold regression tests for detected breaking changes

### 8.3 Dependency Graph Impact Analysis
- **Static Analysis** — Build call graph: which Omega modules import/use each tool
- **Dynamic Tracing** — Runtime instrumentation to detect actual usage
- **Impact Scoring** — Auto-populate "Omega Engine Impact Assessment" table

### 8.4 Cross-Platform Expansion
- **Cline CLI** — Version detection via `cline --version`
- **Cursor** — Extension version via `code --list-extensions --show-versions`
- **VS Code** — `code --version` + extension marketplace API
- **Gemini CLI** — `gemini --version`

### 8.5 SBOM Integration
- **Syft/Grype** — Generate Software Bill of Materials
- **CVE Correlation** — Cross-reference version changes with vulnerability databases
- **Policy Enforcement** — Block deployment if critical CVE in new version

### 8.6 Advanced Scheduling
- **Adaptive Frequency** — Increase check frequency for tools with recent changes
- **Maintenance Windows** — Respect user-defined quiet hours
- **Cluster Coordination** — Distributed lock for multi-machine deployments

---

## 9. OPEN QUESTIONS & DECISIONS NEEDED

| Question | Options | Recommendation |
|----------|---------|----------------|
| **Where does monitor run?** | Host cron / systemd timer / Podman quadlet / Kubernetes CronJob | Host cron (simplest, M6 compliant) |
| **Researcher model for version research?** | Session model (Nemotron) / Local (Qwen3) / Cloud fallback | Session model (consistent with other research) |
| **Briefing retention policy?** | Keep all / 90 days / 1 year | Keep all (sovereign continuity) — disk is cheap |
| **False positive handling?** | Manual dismiss / Auto-learn / Threshold tuning | Manual dismiss via Kali oversight; log for tuning |
| **Multi-repo monitoring?** | Single registry / Per-repo registry | Single registry at engine level; stacks inherit |

---

## 10. SUCCESS CRITERIA (MVP)

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| **Detection** | OpenCode version change caught automatically | ✅ Within 24h of upgrade |
| **Research Quality** | Briefing covers all 6 required research areas | ✅ 100% |
| **Briefing Format** | Template compliance | ✅ 100% |
| **Handoff Success** | Researcher → Kali handoff completes | ✅ 100% |
| **Oversight Action** | Kali reviews within deadline | ✅ P0: 24h, P1: 72h |
| **Implementation** | Action items dispatched to Pillars | ✅ Tracked via Hivemind |
| **Test Coverage** | `make test` passes | ✅ 1398+ tests |
| **Temple-Grade** | `make temple-grade` passes | ✅ T1-T11 |

---

## 11. GNOSIS — L3 PRINCIPLES (Anticipated)

| L3 Principle | Origin |
|--------------|--------|
| **Version drift is a sovereignty violation** | Unmonitored dependency changes = external control over local execution |
| **Automated detection > manual vigilance** | Human attention is scarce; systematic monitoring is infrastructure |
| **Research is the bridge between change and adaptation** | Detection without synthesis is noise; synthesis without detection is blindness |
| **Oversight queues prevent automation runaway** | Every automated action must have a human-in-the-loop gate |
| **Templates enforce cognitive discipline** | Structured output prevents "good enough" parametric synthesis |

---

## 12. APPENDICES

### 12.1 Version Registry Schema (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["schema_version", "last_check", "tools"],
  "properties": {
    "schema_version": {"type": "integer", "const": 1},
    "last_check": {"type": "string", "format": "date-time"},
    "tools": {
      "type": "object",
      "patternProperties": {
        "^[a-z_]+$": {
          "type": "object",
          "required": ["current_version", "last_seen", "check_method"],
          "properties": {
            "current_version": {"type": "string"},
            "last_seen": {"type": "string", "format": "date-time"},
            "check_method": {"type": "string", "enum": ["cli_version", "pip_outdated", "docker_images", "npm_outdated"]},
            "command": {"type": "string"},
            "parse_regex": {"type": "string"},
            "packages_of_interest": {"type": "array", "items": {"type": "string"}},
            "images_of_interest": {"type": "array", "items": {"type": "string"}}
          }
        }
      }
    }
  }
}
```

### 12.2 Handoff Template (JSON)

`data/templates/version_change_handoff.json`:
```json
{
  "packet_id": "vcw-{{tool}}-{{new_version}}-{{timestamp}}",
  "source_channel": "opencode",
  "source_entity": "version_watchdog",
  "target_channel": "opencode",
  "target_entity": "researcher",
  "task": "VERSION CHANGE RESEARCH: {{tool}} {{old_version}} → {{new_version}}",
  "context": "Automated version change detection via Version Change Watchdog. {{tool}} upgraded from {{old_version}} to {{new_version}}. Priority: {{priority}}. Focus: {{focus_areas}}.",
  "priority": {{priority_num}},
  "metadata": {
    "tool": "{{tool}}",
    "old_version": "{{old_version}}",
    "new_version": "{{new_version}}",
    "priority_level": "{{priority}}",
    "detection_method": "{{method}}",
    "detection_time": "{{timestamp}}",
    "auto_generated": true,
    "focus_areas": ["changelog", "breaking_changes", "migration", "known_issues", "community_sentiment", "omega_impact"]
  }
}
```

### 12.3 Error Types (Python)

```python
# src/omega/infra/version_monitor_errors.py
from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class VersionMonitorError(Exception):
    """Base error for version monitor."""
    trace_id: str = None
    
    def __post_init__(self):
        if self.trace_id is None:
            self.trace_id = str(uuid.uuid4())[:8]

@dataclass
class RegistryLoadError(VersionMonitorError):
    path: str
    cause: Exception

@dataclass
class RegistrySaveError(VersionMonitorError):
    path: str
    cause: Exception

@dataclass
class VersionCheckError(VersionMonitorError):
    tool: str
    command: str
    exit_code: int
    stderr: str

@dataclass
class VersionParseError(VersionMonitorError):
    tool: str
    raw_output: str
    regex: str

@dataclass
class ResearchTriggerError(VersionMonitorError):
    tool: str
    old_version: str
    new_version: str
    cause: Exception

@dataclass
class BriefingWriteError(VersionMonitorError):
    path: str
    cause: Exception

@dataclass
class HandoffSubmitError(VersionMonitorError):
    packet_id: str
    cause: Exception

@dataclass
class ToolChainCollapseError(VersionMonitorError):
    """M23 Failure Integrity — mandatory tool chain failure."""
    failed_tools: list[str]
    briefing_path: str
```

---

*🔱 OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_version_watchdog_spec ⬡ 2026-07-19*