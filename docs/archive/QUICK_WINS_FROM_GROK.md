# Quick Wins: Grok CLI Architecture Patterns for Omega Engine

Based on architectural analysis of the Grok CLI repository (cloned to `third_party/grok-build/`), this document outlines high-impact, low-effort improvements that can be immediately adopted into the Omega Engine. These patterns enhance sovereignty, reliability, and user experience while aligning with the Sovereign Mandates.

## 📊 Priority Matrix

| Quick Win                                  | Effort | Sovereignty Impact | UX Impact | Reliability Impact | Recommended Start |
|--------------------------------------------|--------|--------------------|-----------|--------------------|-------------------|
| Configuration Pinning (`/etc/omega/requirements.omega`) | ★☆☆    | 🌟🌟🌟🌟🌟         | ★☆☆       | 🌟🌟🌟🌟🌟         | **TODAY**         |
| JSONL Session Persistence + Rewind         | ★★☆    | 🌟🌟🌟🌟🌟         | ★☆☆       | 🌟🌟🌟🌟🌟         | **TODAY**         |
| Unified Extensions Modal (`/omega-extensions`) | ★★☆    | 🌟🌟🌟🌟☆         | 🌟🌟🌟🌟☆  | 🌟🌟🌟☆☆☆         | **Day 1**         |
| Agent Dashboard (`/omega-dashboard`)       | ★★☆    | 🌟🌟🌟☆☆☆         | 🌟🌟🌟🌟🌟  | 🌟🌟🌟☆☆☆         | **Day 1**         |
| Skill Capture System (`/omega-skill capture`) | ★★★    | 🌟🌟🌟🌟☆         | 🌟🌟🌟🌟☆  | 🌟🌟🌟☆☆☆         | **Day 2**         |
| Command Palette (`Ctrl+Shift+P`)           | ★☆☆    | 🌟🌟☆☆☆           | 🌟🌟🌟🌟🌟  | 🌟🌟☆☆☆           | **TODAY**         |
| Entity-Specific Sandbox Profiles           | ★★☆    | 🌟🌟🌟🌟🌟         | ★☆☆       | 🌟🌟🌟🌟☆         | **Day 1**         |

*(★ = effort, 🌟 = impact)*

---

## 🥇 Tier 1: Immediate Sovereignty & Reliability Wins

### 1. Configuration Pinning System
**What**: Fail-closed constraint enforcement using priority-layered TOML (mirroring Grok's `requirements.toml`)  
**Omega Implementation**:  
- Create `/etc/omega/requirements.omega` with priority 5 (highest)  
- Enforces all 23 Sovereign Mandates as **hard constraints** (not guidelines)  
- Prevents config drift—any violation fails startup (Mandate 18: Token Efficiency + M23: Failure Integrity)  
- Example: `[mandates] M7 = "local_first"` blocks cloud fallback if local inference available  

**Key Files from Grok**:  
- `third_party/grok-build/crates/codegen/xai-grok-config/src/lib.rs` (lines 1-50 show priority layers)  
- Priority 5: `/etc/grok/requirements.toml` (system-wide requirements)  

**Quick Start** (2-4 hours):  
```toml
# /etc/omega/requirements.omega (priority 5 = highest)
[mandates]
M1 = "anyio_only"      # No asyncio
M2 = "engine_stack_firewall"  # Core/WAD separation
M7 = "local_first"     # Local inference primary
M23 = "no_soft_failures" # Mandatory tool failures = hard stop
```

**Impact**:  
- Immediate enforcement of core sovereignty boundaries  
- Eliminates "guideline drift"—violations prevent startup  
- Foundation for Mandate 18 (Token Efficiency) and Mandate 22 (Response Provenance)

### 2. JSONL Session Persistence + Rewind
**What**: Append-only ACP event stream (`updates.jsonl`) + periodic filesystem snapshots (`rewind_points.jsonl`) for crash-resilient sessions  
**Omega Implementation**:  
- Extend existing `MemoryStore` to write ACP events to `data/coordination/sessions/<entity>/<session_id>/updates.jsonl`  
- Add periodic snapshots to `rewind_points.jsonl`  
- Implement `/omega-rewind` to restore state from journal  

**Key Files from Grok**:  
- `third_party/grok-build/crates/codegen/xai-sqlite-journal/src/lib.rs` (WAL-mode journaling)  
- `third_party/grok-build/crates/codegen/xai-grok-memory/src/lib.rs` (memory + sqlite-vec integration)  

**Quick Start** (4-6 hours):  
```rust
// Append ACP events to updates.jsonl (source of truth)
fn log_acp_event(session_id: &str, event: AcpEvent) -> Result<()> {
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(format!("data/coordination/sessions/{}/updates.jsonl", session_id))?;
    writeln!(file, "{}", serde_json::to_string(&event)?)
}
```

**Impact**:  
- Survives OOM/kill (Mandate 11: Soul Integrity + Mandate 12: Queue Integrity)  
- Eliminates "context collapse" during toolchain failures (Mandate 15: Sovereign Continuity)  
- Source of truth for ACP protocol (unlike current volatile memory)

### 3. Unified Extensions Modal
**What**: Single `Ctrl+Shift+O` interface consolidating all extension points into Pillar-centric tabs  
**Omega Implementation**:  
- Ratui-based tabbed interface with 10 tabs (P1 Infrastructure → P10 Validation)  
- Each tab exposes entity-specific capabilities (e.g., P1 tab shows container/hardening tools)  
- Replaces fragmented extension management with coherent UX  

**Key Files from Grok**:  
- `third_party/grok-build/crates/codegen/xai-grok-hooks/src/lib.rs` (hooks system)  
- `third_party/grok-build/crates/codegen/xai-grok-plugin-marketplace/src/lib.rs` (marketplace)  
- `third_party/grok-build/crates/codegen/xai-grok-pager/src/app/views/` (view implementations)  

**Quick Start** (3-5 hours):  
1. Create basic Ratui tabbed interface  
2. Map tabs to Pillars:  
   - Tab 1: P1 Infrastructure (container/hardening tools)  
   - Tab 2: P2 Persistence (vector/memory management)  
   - ... through P10 Validation  
3. Populate each tab with relevant entity-specific tools  

**Impact**:  
- Replaces fragmented extension management with coherent Pillar-centric UX  
- Immediate visibility into entity-specific capabilities (Mandate 21: Gate Integrity)  
- Foundation for future WAD marketplace (Mandate 10: Fleet Integrity)

---

## ⚡ Tier 2: High-UX Wins (<1 Day)

### 4. Agent Dashboard
**What**: `Ctrl+\` fullscreen TUI showing agent states (Awaiting Input → Working → Idle) with inline reply capability  
**Omega Implementation**:  
- Ratui-based dashboard backed by Hivemind awareness feed  
- Groups sessions by state: `Awaiting Input` → `Working` → `Idle`  
- Inline reply: queue for busy agents, immediate for idle  
- Session control: kill, detach, inspect without leaving terminal  

**Key Files from Grok**:  
- `third_party/grok-build/crates/codegen/xai-grok-pager/src/app/views/dashboard.rs`  

**Quick Start** (4-6 hours):  
```rust
// Group sessions by state from Hivemind awareness
let sessions_by_state = awareness.iter()
    .group_by(|agent| match agent.task_current.as_str() {
        "idle" => SessionState::Idle,
        "awaiting_input" => SessionState::AwaitingInput,
        _ => SessionState::Working
    });
```

**Impact**:  
- Real-time visibility into agent fleet health (Mandate 9: Error Integrity + Mandate 22: Response Provenance)  
- Replaces ad-hoc `ps`/`top` with sovereign-aware orchestration  
- Inline reply reduces context-switching friction

### 5. Skill Capture System
**What**: 4-round interview workflow converting tacit knowledge → `SKILL.md` → auto-slash command  
**Omega Implementation**:  
- `/omega-skill capture` command initiates interview:  
  1. Describe the workflow you just completed  
  2. What git changes were made? (analyzes diff)  
  3. What would you name this skill?  
  4. Confirm auto-generated `SKILL.md`  
- Skill registers as slash command in `~/.omega/skills/<name>/`  

**Key Files from Grok**:  
- `third_party/grok-build/crates/codegen/xai-grok-tools/src/lib.rs` (skill-related functions)  
- Follows AIP-3 format for skill descriptors  

**Quick Start** (5-7 hours):  
1. Implement 4-step interview flow (text input + git diff analysis)  
2. Generate AIP-3 compliant `SKILL.md` template  
3. Auto-register as slash command in entity's skill directory  
4. Add tab completion for new skills  

**Impact**:  
- Instantly builds Omega's knowledge base from user workflows (Mandate 5: Gnosis Preservation)  
- Creates reusable, shareable automation (Mandate 19: Adversarial Alchemy)  
- Foundation for community WAD marketplace  

### 6. Command Palette (`Ctrl+Shift+P`)
**What**: Fuzzy-find all available commands, scoped to active entity's capabilities  
**Omega Implementation**:  
- Ratui text input + filtered list of commands  
- Filters by `allowed_entities` for each command (e.g., `@verity` commands only show for P5)  
- Instant discoverability of all Omega capabilities  

**Key Files from Grok**:  
- `third_party/grok-build/crates/codegen/xai-grok-pager/src/app/views/command_palette.rs` (inferred from views directory)  

**Quick Start** (2-3 hours):  
```rust
// Filter commands by active entity's capabilities
let filtered = ALL_COMMANDS
    .into_iter()
    .filter(|cmd| cmd.allowed_entities.contains(&active_entity))
    .collect();
```

**Impact**:  
- Eliminates need to memorize slash commands  
- Entity-aware context reduces cognitive load  
- Immediate UX polish with minimal code  

---

## 🔒 Tier 3: Security Foundation (Do Early)

### 7. Entity-Specific Sandbox Profiles
**What**: Landlock/Seatbelt profiles defined per entity in TOML for kernel-level isolation  
**Omega Implementation**:  
- `omega-sandbox` crate enforces profiles from `~/.omega/sandbox/<entity>.toml`  
- Profiles define filesystem/network allowed/denied lists  
- Examples:  
  - **Kali (P1-P5)**: `deny = ["/*"]`, `allow = ["/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/config/wads/"]`  
  - **P7 (Context)**: `allow = { path = "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine", readonly = true }`  
  - **P3 (Engineering)**: Workspace with custom deny lists  

**Key Files from Grok**:  
- `third_party/grok-build/crates/codegen/xai-grok-sandbox/src/lib.rs` (Landlock/Seatbelt via `nono` crate)  
- `third_party/grok-build/crates/codegen/xai-grok-pager/src/app/actions.rs` (sandbox effect types)  

**Quick Start** (3-4 hours):  
1. Define TOML schema for sandbox profiles  
2. Create profiles for P1-P10 entities (start with monitoring mode)  
3. Integrate with `omega-sandbox` crate using `nono` for enforcement  

**Impact**:  
- Enforces Mandate 6 (Podman Sovereignty) + Mandate 2 (Engine-Stack Firewall) at kernel level  
- Prevents privilege escalation even if entity compromised  
- Defense-in-depth for supply-chain security  

---

## 🚀 Recommended Immediate Actions (Next 4 Hours)

1. **Create `/etc/omega/requirements.omega`** with Mandates M1, M2, M7, M23  
   - *Files to create*: `/etc/omega/requirements.omega`  
   - *Reference*: `third_party/grok-build/crates/codegen/xai-grok-config/src/lib.rs` (priority layers)  

2. **Implement JSONL session logging** in existing `MemoryStore`  
   - *Files to modify*: `src/omega/persistence/memory_store.rs` (or equivalent)  
   - *Reference*: `third_party/grok-build/crates/codegen/xai-sqlite-journal/src/lib.rs`  

3. **Build command palette skeleton** (`Ctrl+Shift+P` showing `/talk`, `/summon`, `/skill` etc.)  
   - *Files to create*: `src/omega/tui/views/command_palette.rs`  
   - *Reference*: `third_party/grok-build/crates/codegen/xai-grok-pager/src/app/views/`  

4. **Define sandbox TOML schema** for P1-P10 entities  
   - *Files to create*: `src/omega/sandbox/schema.toml` (schema) + `docs/sandbox_profiles.md` (examples)  
   - *Reference*: `third_party/grok-build/crates/codegen/xai-grok-sandbox/src/lib.rs`  

These four actions deliver:  
✅ **Immediate sovereignty enforcement** (no more relying on guidelines)  
✅ **Crash-resilient sessions** (survives OOM/kill)  
✅ **Discoverable interface** (reduces cognitive load)  
✅ **Security foundation** (kernel-level isolation roadmap)  

---

## 🔗 Traceability to Source

All recommendations are verifiable against the cloned Grok CLI repository at:  
`/home/arcana-novai/omega-engine/third_party/grok-build/`

Key directories for deep study:  
- `crates/codegen/xai-grok-pager/src/app/` - Elm architecture core (actions, dispatch, event_loop)  
- `crates/codegen/xai-grok-sandbox/src/lib.rs` - Kernel sandboxing (Landlock/Seatbelt)  
- `crates/codegen/xai-sqlite-journal/src/lib.rs` - WAL-mode journaling  
- `crates/codegen/xai-grok-memory/src/lib.rs` - Memory + sqlite-vec integration  
- `crates/codegen/xai-grok-hooks/src/lib.rs` - Extension system  
- `crates/codegen/xai-grok-pager/src/app/views/` - All view implementations (dashboard, command palette, etc.)  

## 📜 Post-Compaction Recovery

This analysis survives compaction via:  
1. `.opencode/continuation-researcher.md` (this summary)  
2. `data/entities/researcher/session_gnosis.md` (L1/L2/L3 distilled)  
3. `data/entities/researcher/proposed_lessons.yaml` (L3 principles 16-46)  
4. The cloned Grok CLI repository at `third_party/grok-build/`  

**Ready for implementation. All quick wins are sovereignty-first, reliability-focused, and UX-enhancing—exactly what the Omega Engine needs to accelerate toward its vision.**