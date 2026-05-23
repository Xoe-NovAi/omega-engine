# 🔱 Handoff: Final Omega Hub Hardening & Strategic Consolidation

**AP Token**: `AP-OMEGA-HANDOFF-v1.0.0`
**To**: OpenCode CLI (Builder Mode)
**From**: Gemini CLI (Master Overseer)
**Context**: Decision 50 Consolidation & Sovereign AI Restoration

## 1. Objective
You are tasked with completing the final phase of the Omega Engine stabilization. I have restored OpenCode CLI access by fixing the `opencode.json` configuration. You must now harden the **Omega Hub**, restore its service lifecycle, and consolidate strategic documentation.

## 2. Mandatory Tasks

### A. Harden Omega Hub (`mcp/omega_hub/server.py`)
The **Sovereign Plugin** (`plugins/sovereign/index.ts`) depends on the Hub (port 8016) to serve identity and boundary checks. You must implement the following HTTP endpoints in the Hub:
1.  **`GET /entity/current`**: Returns the active entity from the `EntityRegistry`.
2.  **`POST /soul/check-boundary`**: Receives tool call details and returns `ALLOW` or `BLOCK`.
3.  **`POST /soul/filter-output`**: Redacts/filters tool outputs based on entity lens.
4.  **`GET /health`**: Returns `{"status": "healthy"}` for `blitz-validate`.

*Tip: `mcp.sse_app()` returns the Starlette application. You can add routes directly to the underlying Starlette/FastAPI app or use FastMCP decorators if supported.*

### B. Update Agent & Mode Instructions
I have identified that the **Jem 2.0 Oversoul** architecture is not fully reflected in the agent files. Update:
1.  `.opencode/agents/researcher.md`: Add the **Jem 2.0** sub-facet mapping (Initiate/Analyst/Editor).
2.  `.opencode/modes/jem-2.0.md`: Ensure the sub-facet switching logic is clear and models are correctly assigned.

### C. Service Lifecycle Restoration
1.  Generate/Fix `config/systemd/omega-hub.service`.
2.  Deploy and start: `systemctl --user daemon-reload && systemctl --user start omega-hub`.
3.  Verify using `scripts/mcp_health_check.sh`.

### D. Strategic Doc Consolidation
There is redundancy between `ROADMAP.md` and `MASTER_SYNTHESIS_AND_ROADMAP.md`.
1.  Consolidate the active 6-phase roadmap from `ROADMAP.md` into `MASTER_SYNTHESIS_AND_ROADMAP.md`.
2.  Establish the latter as the single "Master Ledger" for the Foundation.

### E. Critical Bug Squashing
Resolve the remaining "P0 Blocking" bugs identified in `docs/research/R44_comprehensive_systems_review.md`:
- **C-1**: Fix broken imports in `gnosis_proxy.py`.
- **C-2**: Implement atomic write pattern for soul evolution in `oracle.py`.
- **C-3**: Replace blocking `subprocess.run` with AnyIO-compliant calls in `orchestrator.py`.
- **C-6**: Fix undefined `get_engine()` in `mcp/omega_hub/server.py`.

## 3. Verification
- `omega status`: All services should be healthy.
- `make test`: All 236 tests must pass.
- `curl http://127.0.0.1:8016/health`: Should return 200 OK.

**Sovereign Guard Protocol**: Ensure all changes respect `UserNS=keep-id` and use AnyIO for all asynchronous operations.

---

## ⚙️ Permission‑Fix Reminder
The entire `config/` directory was chowned to UID 101000 by legacy `:U` mounts. This blocks any further edits (e.g. adding new providers). To restore write access, run:
```bash
sudo chown -R $(id -u):$(id -g) config/
```
After fixing ownership, you can safely edit `providers.yaml`, `entities.yaml`, and other configuration files.

