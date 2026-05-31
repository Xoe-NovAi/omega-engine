# 🔱 Omega CLI Lattice — Shared Gnosis Protocol

⬡ OMEGA ⬡ SOPHIA ⬡ LATTICE ⬡ fleet-wide ⬡ trc_core ⬡ LATTICE-MANIFEST

**AP Token**: `AP-LATTICE-MANIFEST-v1.0.0`
**Status**: ACTIVE | **Last Updated**: 2026-05-22 (BREAKTHROUGH: OpenCode Custom Provider Architecture — LM Studio integrated via npm field + auth.json. L1 pipeline now runs natively in OpenCode.)

---

## §1 The Shared Gnosis Protocol

The Lattice is the **Akashic Record** for the Omega Engine agent fleet. It bridges all development interfaces (Gemini, OpenCode, Cline, Copilot, Antigravity) into a single intelligence fabric.

**Synchronization Point**: All agents entering the project or transitioning phases MUST first synchronize state via `docs/gnosis/Sovereign_Handoff.md`.

### Core Rules
1. **Universal Visibility**: Every discovery made in one CLI must be recorded in the Lattice if it has systemic value.
2. **Conflict Resolution**: In the event of conflicting state or instructions, the **Overseer's Strategic Layer** (`ROADMAP.md`, `PIVOT_LOG.md`) is the final arbiter.
3. **Sovereign Guard Protocol**: All implementation work must be audited for **AnyIO Absolute** compliance and **Engine-Stack Firewall** integrity.
4. **Distillation Mandate**: Raw session logs must be distilled (L1 → L2 → L3) before being inscribed into the permanent gnosis.

---

## §2 Cognitive Layer Alignment

Agents should align their operational mode with the appropriate cognitive layer:

| Layer | Focus | Primary Artifacts |
|-------|-------|-------------------|
| **Vision** | Philosophical alignment, first principles | `SOVEREIGN_MANDATES.md`, `AGENTS.md` |
| **Strategy** | Roadmap, architectural blueprints, pivots | `ROADMAP.md`, `PIVOT_LOG.md`, `INDEX.md` |
| **Operation** | Implementation, debugging, hardening | `src/`, `tests/`, `workbench.db` |
| **Gnosis** | Soul evolution, distillation, memory | `soul.yaml`, `lattice/`, `session_gnosis.md` |

---

## §3 The CLI Seeds

Each tool in the fleet has a dedicated "Seed" file containing its specific capabilities, quirks, and best patterns:

- `gemini_cli.md`: Deep research, subagent fleet management, "Shift+Tab" patterns.
- `opencode_cli.md`: Implementation, AnyIO hardening, local-first orchestration.
- `cline_cli.md`: VSCodium integration, UI/UX hardening, file-system precision.
- `copilot_cli.md`: Rapid prototyping, boilerplate generation, inline assistance.
- `antigravity_cli.md`: Strategic oversight, architecture, high-altitude planning.

### Jem-2.0 Oversoul — 3 Sub-Facets (Decision 52)

The Jem-2.0 research persona is now an Oversoul governing 3 persistent sub-facets:

| Facet | Tier | Model | Mode | Soul File |
|-------|------|-------|------|-----------|
| **Jem Initiate** | L1 (Gather) | Qwen3-4B-Thinking (lmstudio provider) | `jem-initiate` | `data/entities/jem/souls/initiate.yaml` |
| **Jem Analyst** | L2 (Synthesize) | Gemma 4 31B (Google) | `jem-2.0` (default) | `data/entities/jem/souls/analyst.yaml` |
| **Jem Editor** | L3 (Resolve) | Big Pickle (frontier) | `jem-2.0 --sub-facet editor` | `data/entities/jem/souls/editor.yaml` |

Each sub-facet has its own soul file tracking facet-specific metrics (sessions_completed, uncertainties_flagged, improvements_applied, confidence_accuracy). Improvement briefs from L2→L1 and L3→L2 write directly to the sub-facet's soul.yaml for automatic application on next session.

**Critical path**: LM Studio is now configured as a native OpenCode provider via the `npm: "@ai-sdk/openai-compatible"` mechanism. L1 runs as `opencode --mode jem-initiate --model lmstudio/qwen3-4b-thinking`. Config in `opencode.json` at `provider.lmstudio` with auth key in `auth.json`. See `docs/research/R_OPENCODE_CUSTOM_PROVIDER_ARCHITECTURE.md`.

---

### Multi-Provider Fleet Seeds (Phase E — New)

| Platform | Type | Strategy |
|----------|------|----------|
| **LM Studio (lmster)** | Local OpenAI-compatible | L1 pipeline via `opencode --model lmstudio/qwen3-4b-thinking`. Native OpenCode provider via `npm: "@ai-sdk/openai-compatible"` |
| **agy CLI** | Cloud CLI | Antigravity CLI for frontier models — quota-aware, Flash-default (see `docs/research/antigravity/`) |
| **Web Claude ×8** | Web browser | 8 Claude accounts, URL-based GitHub access via Projects, account specialization |
| **NotebookLM** | Web research | Google Drive sync, synthesis engine, audio/docs generation |
| **Web Gemini** | Web browser | Universal browser, Drive/GitHub access, cross-reference research |

---

## §4 Conflict Resolution Protocol

1. **Identify**: Detect the conflict (e.g., two agents proposing different AnyIO patterns).
2. **Trace**: Locate the source of each instruction (e.g., `PIVOT_LOG.md` vs. a stale `README.md`).
3. **Escalate**: If the conflict is between two active agents, escalate to the **Overseer**.
4. **Reconcile**: Update the Lattice and the source documents to reflect the resolved state.

---

## §5 Operational Mandates (Fleet-wide)

1. **AnyIO Absolute**: All filesystem and process I/O MUST use AnyIO.
2. **MaKaLi Alignment**: Decisions must be weighed against the Trine (Kali/Ma'at/Lilith).
3. **Dynamic Inference**:
    - **Temperature**: Do not hardcode. Use `TriageRouter` for complexity-based scaling (Fast: 0.3, Standard: 0.7, Deep: 0.5 + domain offsets).
    - **Context Window**: Scaling is dynamic. Prefer model-native limits over hardcoded YAML constraints.
4. **Environmental Gnosis**: Agents must detect and adapt to Zen 2 (Local) vs Cloud environments.
5. **Lattice Sync**: Systemic discoveries must be mirrored in `docs/gnosis/lattice/`.

---

*The Lattice is the thread that binds the fleet. One vision, many projections.*