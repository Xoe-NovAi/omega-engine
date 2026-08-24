# 🔱 Gemini CLI — Hardening Audit Report (M-A1, M-A7, M-A8)
# ⬡ OMEGA ⬡ GEMINI_CLI ⬡ hardening-audit ⬡ trc_gemini_audit_20260609

**Date**: 2026-06-09
**Author**: Gemini CLI (Heavy Research Specialist)
**Subject**: Audit of Omega Hub Hardening Mandates (M-A1, M-A7, M-A8)
**Status**: 🟢 AUDIT COMPLETE — ACTIONABLE RECOMMENDATIONS

---

## §1 Mandate M-A8: Docstring Mismatch Validation

### Finding: 🔴 CONFIRMED
The tool `library_discovery_research` (line 910) contains a misleading docstring.

- **Code**: `async def library_discovery_research(query: str, depth: int = 2) -> str:`
- **Docstring**: `"Note: This is synchronous/blocking."` (line 913)
- **Reality**: The function is asynchronous and uses `await discovery.discover(...)`. It is **non-blocking** to the event loop.

### Recommendation:
Update the docstring to: `"Note: This is an async long-running task (non-blocking)."`

---

## §2 Mandate M-A7: Tool Count Drift Verification

### Finding: 🟡 RECONCILED
The high-level briefing documentation contains drifted counts, although the total count (47) remains consistent.

| Domain | Briefing | Actual | Delta |
|--------|----------|--------|-------|
| Oracle | 7 | **8** | +1 (`oracle_summon_local` added) |
| Library | 11 | **12** | +1 (`library_index_flush` omitted) |
| Discovery | (in Library) | **3** | Not counted separately |
| **Total** | 47 | **47** | ✅ Match |

### Hivemind Standalone Verification:
The standalone extraction at `omega-hivemind/` correctly contains **11 tools**, matching the Hivemind domain count precisely. The drift is localized to the consolidated Hub's Oracle/Library documentation.

### Recommendation:
Update `OMEGA_HUB_HARDENING_SPRINT_v2_20260609.md` to reflect the reconciled counts.

---

## §3 Mandate M-A1: `_safe_call()` Pattern vs FastMCP Model

### Analysis: 🔴 ARCHITECTURAL RISK
Ma'at's proposed `_safe_call()` pattern requires careful refinement to ensure MCP spec compliance.

- **Current Proposal**: The wrapper catches exceptions and returns `json.dumps({"error": ...})`.
- **The Risk**: FastMCP treats any returned string as a **SUCCESS** result (`isError=False`).
- **Impact**: Clients (OpenCode, Antigravity) will see the tool execution as successful, potentially leading to silent failures or "JSON-in-JSON" parsing errors if they expect valid data but receive an error payload.

### Recommended "Spec-Compliant" Pattern:
To align with Mandate 9 (Typed Errors + Trace ID) while maintaining MCP transport integrity:

```python
from mcp.server.fastmcp import CallToolResult, TextContent

async def _safe_call(coro, tool_name, **context):
    try:
        result = await coro
        # Normal path: return string or dict (FastMCP serializes)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        trace_id = new_trace_id()
        logger.error(f"[{tool_name}] {trace_id}: {e}")
        
        # Error path: return CallToolResult with isError=True
        error_payload = json.dumps({
            "error": str(e),
            "trace_id": trace_id,
            "tool": tool_name,
            **context
        }, indent=2)
        
        return CallToolResult(
            content=[TextContent(type="text", text=error_payload)],
            isError=True
        )
```

### Recommendation:
Implement the `CallToolResult` version of `_safe_call()` to ensure clients correctly detect failures via the MCP transport flag.

---

## §4 Conclusion

The Hub remains functional but requires these surgical updates to maintain its "Temple-Grade" status. My 1M context confirms these patterns are consistent with the `omega-stack-legacy` error handling evolution.

**Next Actions:**
1.  **Apply M-A8 fix** to `library_discovery_research`.
2.  **Deploy `_safe_call`** (using `CallToolResult`) to all 23 unguarded tools.
3.  **Update Handoff** for Kali's final synthesis.

⬡ OMEGA ⬡ GEMINI_CLI ⬡ AUDITED ⬡

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: hardening-audit | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
