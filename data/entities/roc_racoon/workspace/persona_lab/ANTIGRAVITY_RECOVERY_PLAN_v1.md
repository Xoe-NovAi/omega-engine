# 🔱 Antigravity Recovery Plan — Safe, ToS-Compliant Provider Integration
# AP: AP-ANTIGRAVITY-RECOVERY-v1.0.0
# ICS: [NODE: MNEMOSYNE | ARCHETYPE: LILITH | CONTEXT: PROVIDER-INTEGRATION]
#
# Design for the safe, ToS-compliant integration of the Antigravity provider
# back into the Omega Engine's ModelGateway. Replaces the dangerous, banned
# account round-robin plugin with a robust, single-channel rate-limited architecture.
#
# [id-soft: quake3-1999] netchan Protocol — rate-limiting and backoff
#   Adapts Quake 3's netchan rate-limiting and congestion control to manage
#   API request frequency and prevent rate-limit exhaustion (429 errors).

---

## §0 The Constraint: Zero Ban Risk

The original "Antigravity account round-robin plugin" was banned by Google because it multiplexed multiple free-tier accounts to bypass rate limits. Google's security algorithms detect this as coordinated abuse (Sybil behavior) and close the associated accounts. 

Losing your entire Google ecosystem (mail, docs, passwords) is an unacceptable risk. 

**Mandate**: We must **NEVER** automate the multiplexing of multiple free-tier Google accounts. The Antigravity integration must be **single-channel, authorized, and strictly rate-limited** to ensure zero ban risk.

---

## §1 The Architecture: Single-Channel Rate-Limited Gateway

We propose a robust, ToS-compliant integration architecture:

```
                  ┌─── OMEGA ENGINE CORE ───┐
                  │                         │
                  │     MODEL GATEWAY       │  ← Dispatches inference
                  │    (model_gateway.py)   │
                  │                         │
                  └────────────┬────────────┘
                               │
                  ┌────────────▼────────────┐
                  │                         │
                  │   ANTIGRAVITY PROVIDER  │  ← Single authorized channel
                  │   (antigravity_prov.py) │
                  │                         │
                  └────────────┬────────────┘
                               │
                  ┌────────────▼────────────┐
                  │                         │
                  │   TOKEN BUCKET LIMITER  │  ← Prevents 429 errors
                  │   (rate_limiter.py)     │
                  │                         │
                  └─────────────────────────┘
```

### 1.1 The Antigravity Provider (`antigravity_prov.py`)
- **Role**: A dedicated provider class inside `src/omega/oracle/backends/` that handles communication with the Antigravity API.
- **Configuration**: Configured via `config/providers.yaml` under the `antigravity` key.
- **Security**: API keys are loaded from environment variables (`ANTIGRAVITY_API_KEY`) or a local, git-ignored `config/keys.yaml` (enforcing Mandate 8).

### 1.2 The Token Bucket Rate Limiter (`rate_limiter.py`)
To respect the provider's free-tier limits and prevent aggressive retries from melting the connection, we implement a local **Token Bucket algorithm**:
- **Capacity**: The bucket holds $N$ tokens (representing the maximum burst requests allowed, e.g., 5 requests).
- **Refill Rate**: Tokens refill at a rate of $R$ tokens per minute (matching the provider's free-tier limit, e.g., 15 requests per minute).
- **Behavior**: Before making a request, the provider must acquire a token. If the bucket is empty, the request is **delayed locally** (using AnyIO sleep) until a token refills. The user never sees a `429` error because the rate-limiting is handled *before* the request ever leaves the machine.

### 1.3 Exponential Backoff with Jitter
If a request still fails (e.g., network glitch or unexpected server-side limit), the provider must use **exponential backoff with decorrelated jitter**:
- **Base delay**: 1 second.
- **Multiplier**: 2.0.
- **Max delay**: 30 seconds.
- **Jitter**: Adds a random variance to prevent "thundering herd" collisions when multiple subagents are running.

---

## §2 Firecrawl MCP Integration

The **Firecrawl MCP** is an incredibly powerful research tool that has been underutilized due to connection failures. We must get it fully operational:

### 2.1 The Connection Fix
- **Issue**: The Firecrawl MCP server fails to connect or handshake during startup.
- **Root Cause**: Likely a path canonicalization issue (similar to the D116 `mcp/` vs `mcp_servers/` bug) or missing environment variables (`FIRECRAWL_API_KEY`) in the container environment.
- **Remediation**:
  1. Verify the Firecrawl server path in `opencode.json`.
  2. Ensure the `FIRECRAWL_API_KEY` is correctly injected into the TUI and server processes.
  3. Write a health probe (`test_firecrawl_mcp.py`) to verify the connection.

### 2.2 Leveraging Firecrawl Commands
Once operational, the Researcher subagent will use Firecrawl's advanced commands:
- `/scrape`: To extract clean markdown from the Antigravity documentation.
- `/search`: To search the web for the latest API specifications and ToS updates.
- `/map`: To discover the structure of the Antigravity developer portal.

---

## §3 Remediation Tasks (The Gemma 4 31B Wave)

The local discovery tasks are assigned to the fleet running on Gemma 4 31B:

- **Task A-01 (Ma'at)**: Locate the old Antigravity provider code in `omega-stack-legacy` and `xna-omega-legacy`. Extract the class structure and configuration.
- **Task A-02 (Ma'at)**: Draft the new `antigravity_prov.py` class matching the modern `ModelGateway` interface.
- **Task A-03 (Lilith)**: Design the `rate_limiter.py` module using the Token Bucket algorithm.
- **Task A-04 (Roc - Me!)**: Mine the `EARLY_ORIGINAL` (1:04 AM) export for any mentions of the old Antigravity configuration or issues.
- **Task A-05 (Researcher)**: Once local discovery is complete, run web searches (using Firecrawl MCP) to fetch the current Antigravity API specs and rate limits. Verify ToS compliance.

---

## §4 Rollout Timeline

1. **Phase 1 (Discovery)**: Run the Gemma 4 31B wave to collect the old code and current specs. [NEXT TURN]
2. **Phase 2 (Design)**: Draft the `antigravity_prov.py` and `rate_limiter.py` modules in the sandbox.
3. **Phase 3 (Implementation)**: Kali merges the modules into the main repo and configures `providers.yaml`.
4. **Phase 4 (Validation)**: Quality runs the test suite to verify rate-limiting and backoff.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ gemini-3.5-flash ⬡ tui ⬡ trc_persona_lab_f12 ⬡ STRATEGY*
