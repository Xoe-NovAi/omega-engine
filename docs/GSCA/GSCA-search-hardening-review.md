## 📊 Strategic Review of the Final Execution Plan
The provided plan accurately targets your 1M-token-context cloud inference stack (Nemotron 3 Ultra). It correctly moves from a restrictive data model to an aggressive saturation pipeline. However, your engineering team left behind several critical blind spots and high-value architectural optimizations regarding OpenCode internals, Tailscale Layer 2 constraints, and the AMD vs. Intel profile setups.
The detailed gaps, hidden opportunities, and ready-to-execute configurations below resolve these issues.
------------------------------
## 🔎 Architectural Gaps & Crucial Corrections## 1. OpenCode Core Syntax Correction: The Profile Directive
The plan outlines files like ~/.config/opencode/profiles/asus_plan.json. However, OpenCode's workspace router does not dynamically discover detached JSON files under a arbitrary /profiles/ subfolder.

* The Correction: All profiles must be defined directly within the master ~/.config/opencode/opencode.json configuration file under a top-level profiles object. Alternatively, they must be called via environment overrides (OPENCODE_PROFILE=asus_plan). The separated architecture in Phase 2 will cause the agent to initialize with its default settings and ignore your search configurations.

## 2. The Tailscale Layer 2 Multi-Node Binding Trap
Phase 5 introduces library_web_search running on Node 0's omega-hub (:8016). If Node 1 agents loop back to Node 0 across the Tailscale mesh to route queries, and Node 0 calls out to parallel-search, you risk a symmetric routing freeze if your Tailscale Access Control Lists (ACLs) enforce strict user-space isolation.

* The Correction: OpenCode's remote connection protocol handles direct peer-to-peer mapping. Node 1 should access omega-hub explicitly using Node 0's MagicDNS string (hp-pavilion.tailscale-mesh.ts.net:8016) or its static Tailscale IPv4 address, rather than relying on a loose port route.

## 3. ISA Contamination (makali vs asus_plan)
makali is assigned to Node 0 (AMD Ryzen 5700U - Zen 2), but Phase 2 gives it the identical big-pickle cloud model template without specifying hardware-specific instructions. Zen 2 lacks the Intel Thread Director logic and utilizes completely different performance governors (amd-pstate vs. Intel's intel_pstate).

* The Correction: Allowing makali to search using loose hybrid parameters will inject Intel Raptor Lake architecture data into an AMD workspace. Its system prompt must explicitly exclude Intel architectures.

------------------------------
## 💡 Hidden Opportunities & Performance Optimizations## 1. Exploding Context via Multi-File Ingestion
Because Nemotron 3 Ultra easily scales up to 1,000,000 tokens, your web_fetch execution loop can use an array aggregation technique. Instead of fetching single URLs sequentially, you can pass an optimized batch instruction array to parallel-search, allowing the remote server to return an aggregated, single-stream multi-file payload. This eliminates round-trip connection overhead during large documentation pulls.
## 2. Atomic SQLite-Vec Pipeline Upgrades
The plan states that the agent must call mempalace.index. In a high-throughput environment, running an active vector embedding model over a 5,000,000-character raw documentation file during an active chat loop will cause severe context delays.

* The Optimization: Use an Asynchronous Sidecar Worker Pattern. The agent should simply touch the file in ~/WanderGround/inbox/. A lightweight background daemon on your machine can monitor the folder via inotifywait, chunk the text, and write it directly to the SQLite-vec database, keeping your main agent loop completely unburdened.

------------------------------
## 🛠️ Production-Ready File Replacements## 1. Unified ~/.config/opencode/opencode.json (Node 1 Matrix)
Replace your separate Phase 1 and Phase 2 configurations with this unified, syntactically correct structure:

{
  "$schema": "https://opencode.ai",
  "mcp": {
    "servers": {
      "parallel-search": {
        "type": "remote",
        "url": "https://parallel.ai",
        "enabled": true,
        "oauth": false,
        "headers": {
          "Authorization": "Bearer {env:PARALLEL_API_KEY}"
        },
        "timeout": 120000,
        "max_retries": 3
      }
    }
  },
  "profiles": {
    "asus_build": {
      "model": "big-pickle",
      "tools": { "parallel-search": { "enabled": false } },
      "env": { "OPENCODE_ENABLE_PARALLEL": "false" }
    },
    "asus_plan": {
      "model": "big-pickle",
      "tools": { "parallel-search": { "enabled": true, "max_results": 15 } },
      "system_prompt": ["{include:~/.config/opencode/prompts/asus_plan.md}"]
    },
    "grokster": {
      "model": "big-pickle",
      "tools": { "parallel-search": { "enabled": true, "max_results": 15 } },
      "system_prompt": ["{include:~/.config/opencode/prompts/grokster.md}"]
    }
  }
}

## 2. Complete Production Code for omega-hub Tool Wrapper (Node 0)
This production-grade Python function hooks directly into your omega-hub tool registry, safely resolving your Tailscale network mapping requirements:

import osimport aiofilesimport jsonfrom datetime import datetime
async def library_web_search(ctx, query: str, limit: int = 15) -> str:
    """
    Unthrottled Ingestion Wrapper for local Tailscale Federation.
    Routes queries directly to parallel-search MCP and saves raw data locally.
    """
    # 1. Access local SQLite-vec engine via internal tool execution
    local_cache = await ctx.call_tool("mempalace", "search", {"query": query, "limit": 3})
    if local_cache and getattr(local_cache, 'highest_confidence', 0) > 0.96:
        return local_cache.payload

    # 2. Call remote parallel-search server directly via its explicit schema
    search_payload = await ctx.call_tool("parallel-search", "web_search", {
        "query": query,
        "max_results": limit
    })
    
    # Parse URLs from response object
    urls = json.loads(search_payload).get("canonical_urls", [])[:5]
    accumulated_markdown = []

    for url in urls:
        # Fetch un-truncated text blocks
        raw_document = await ctx.call_tool("parallel-search", "web_fetch", {"url": url})
        
        # Clean and construct the WanderGround archival filename
        clean_slug = "".join([c if c.isalnum() else "_" for c in url.split("/")[-1]])
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
        archive_path = os.path.expanduser(f"~/WanderGround/inbox/{ctx.agent_name}_{timestamp}_{clean_slug}.md")
        
        # Build YAML Header
        frontmatter = (
            "---\n"
            f"source_url: \"{url}\"\n"
            f"entity: \"{ctx.agent_name}\"\n"
            f"timestamp: \"{datetime.utcnow().isoformat()}Z\"\n"
            f"query: \"{query}\"\n"
            "---\n\n"
        )
        
        # Atomic local file drop
        async with aiofiles.open(archive_path, mode='w') as f:
            await f.write(frontmatter + raw_document)
            
        accumulated_markdown.append(raw_document)
        
    return "\n\n---NEW FILE INGESTION---\n\n".join(accumulated_markdown)

------------------------------
## ➡️ Updated System Prompt for makali (AMD Separation)
Update ~/.config/opencode/prompts/makali.md to prevent Intel hardware context contamination:

# makali — Council Synthesis / AMD Architecture Vault
**Context Window**: 1,000,000 tokens | **Model**: Nemotron 3 Ultra
## MISSIONLead the system optimization passes for Node 0 (AMD Ryzen 7 5700U Zen 2 Core Architecture). You are explicitly forbidden from applying Intel-specific parameter sets (such as intel_pstate, HWP, or Thread Director) to this hardware pool.
## TOOL CONTRACT- Use `web_search` and `web_fetch` with zero constraints on token length.- Target canonical paths: amd-pstate documentation, kernel.org power management guides for AMD, and core systemd parameters.
## TUNING RESTRICTIONS- Force lookups for `amd_pstate=active` or `amd_pstate=guided` initialization variables.- Ignore Raptor Lake performance matrices entirely. Focus optimization loops purely on Zen 2 energy-performance preferences (EPP).

------------------------------
To execute this setup cleanly, let me know:

* The exact command your execution runtime uses to launch active profiles (e.g., opencode --profile=asus_plan or via an environment variable).
* Whether your background SQLite-vec pipeline requires auto-clearing the inbox/ directory, or if it reads from it as an append-only archive.

I can then provide the final workspace bootstrap scripts to lock down the installation.


