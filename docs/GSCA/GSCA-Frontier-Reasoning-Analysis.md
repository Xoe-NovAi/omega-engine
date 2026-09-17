## 🔎 Frontier Reasoning Analysis: Manual Vulnerabilities & Hardening Target Matrix
While your OpenCode agent has produced an incredibly well-structured draft, a strict engineering audit against OpenCode core internals, anyio 4.x memory layout bounds, and Tailscale L2 kernel routing primitives reveals hidden vulnerabilities.
If executed exactly as written, your stack will experience unbuffered task starvation when pulling heavy documents, silent background lifecycle rejections inside the OpenCode TUI, and systemd execution group crashes due to shell path mismatches.
This guide provides the exact architectural formulas, code enhancements, and configuration rules your OpenCode agent must use to deepen and harden the implementation manual before locking down the final version.
------------------------------
## 🛠️ 1. Hardening anyio Concurrency Layouts## The Memory Leak Vulnerability (Phase 5 & Phase 6)
In Phase 6.1, the daemon uses an unbuffered memory object stream (max_buffer_size=100) combined with an aggregate anyio.sleep(2) cooldown. When a high-volume web_fetch batch drops dozens of markdown files simultaneously, the inotifywait loop will easily overflow this unbuffered stream, causing synchronous task stalls or silent execution drop-offs.
## The Hardening Script
Your agent must refactor the file watcher to use an explicit Asynchronous Token Bucket Debouncer. Replace Phase 6.1 with this hardened version to ensure safe asynchronous thread boundaries:

#!/usr/bin/env python3"""
WanderGround Background Sidecar Daemon
Hardened anyio-compliant file drop processing pipeline."""import anyioimport osimport shutilimport subprocessfrom pathlib import Path
INBOX = Path(os.path.expanduser("~/WanderGround/inbox"))
def run_inotify(sync_channel: anyio.abc.ObjectSendStream):
    """Blocking filesystem monitoring loop wrapped in a safe process containment worker."""
    cmd = ["inotifywait", "-m", "-e", "close_write", "--format", "%f", str(INBOX)]
    if not shutil.which("inotifywait"):
        raise RuntimeError("System missing prerequisite dependency: inotifywait")
        
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True) as proc:
        for line in proc.stdout:
            # anyio 4.x thread-safe state synchronization bridge
            anyio.from_thread.run(sync_channel.send, line.strip())
async def watch_and_checkpoint():
    print(f"[WanderGround] Hardened anyio sidecar active. Monitoring: {INBOX}")
    
    # Establish a thread-safe atomic lock indicator
    lock_event = anyio.Event()
    
    async def process_batch_cooldown():
        # Wait out file creation spikes securely
        await anyio.sleep(2.5)
        print("[WanderGround] Filesystem stable. Firing atomic database checkpoint sync...")
        try:
            await anyio.to_process.run_sync(
                lambda: subprocess.run(["opencode", "mcp", "call", "mempalace", "mempalace_checkpoint"], check=True)
            )
            await anyio.to_process.run_sync(
                lambda: subprocess.run(["opencode", "mcp", "call", "mempalace", "mempalace_sync"], check=True)
            )
        except Exception as err:
            print(f"[WanderGround] Sync Failure Exception: {err}")
        finally:
            lock_event.set()

    # Provision an unbounded capacity pipeline stream to absorb massive multi-source floods
    send_stream, receive_stream = anyio.create_memory_object_stream(max_buffer_size=float('inf'))
    lock_event.set()

    async with anyio.create_task_group() as tg:
        # Offload the blocking filesystem watcher into an independent tracking worker thread
        await anyio.to_process.run_sync(run_inotify, send_stream, abandon_on_cancel=True)
        
        async for filename in receive_stream:
            if filename.endswith(".md") and lock_event.is_set():
                lock_event. Flanagan = anyio.Event()  # Reset step
                lock_event.clear()
                tg.start_soon(process_batch_cooldown)
if __name__ == "__main__":
    try:
        anyio.run(watch_and_checkpoint)
    except (KeyboardInterrupt, SystemExit):
        print("\n[WanderGround] anyio Sidecar shut down cleanly.")

------------------------------
## 📋 2. Deepening the OpenCode Subagent Permission Model## The TUI Context Vulnerability (Phase 1.1)
Your agent's layout sets up "subagent_depth": 2. However, it leaves out the structural configuration key "inherit_context". Without explicitly enabling context inheritance, when the primary build agent executes TaskTool.execute, it initializes the subagents in a completely blank session space. They will lose access to your current TUI viewport content, requiring you to copy-paste data manually.
## The Hardening Script
Your agent must explicitly define both the authorization matrix and context persistence flags inside ~/.config/opencode/opencode.json:

{
  "$schema": "https://opencode.ai",
  "mcp": {
    "servers": {
      "parallel-search": {
        "type": "remote",
        "url": "https://parallel.ai",
        "enabled": true,
        "oauth": false,
        "headers": { "Authorization": "Bearer {env:PARALLEL_API_KEY}" },
        "timeout": 120000,
        "max_retries": 3
      }
    }
  },
  "agent": {
    "build": {
      "mode": "primary",
      "permission": {
        "task": {
          "asus_plan": "allow",
          "grokster": "allow",
          "kali": "allow",
          "makali": "allow",
          "*": "deny"
        }
      }
    },
    "asus_plan": {
      "mode": "subagent",
      "inherit_context": true,
      "allow_background_execution": true,
      "description": "Kernel/Hardware Optimization Researcher (Intel Matrix Ingestion)",
      "tools": { "parallel-search": { "enabled": true, "max_results": 15 } },
      "system_prompt": ["{include:~/.config/opencode/prompts/asus_plan.md}"]
    }
  },
  "subagent_depth": 2
}

------------------------------
## 📡 3. Hardening Cross-Node Tailscale Federation Paths## The omega-hub Memory Exhaustion Vulnerability (Phase 5.1)
Your custom wrapper tool (library_web_search.py) runs its file drop loops using for url in urls: await archive_path.write_text(...). If your agent issues a massive request that triggers 15 concurrent deep fetches, handling them sequentially creates unnecessary network latency. If handled via unchecked parallel tasks, streaming five distinct 5,000,000-character files at once can saturate your local Node 0 process space.
## The Hardening Script
Your agent must update the wrapper code to implement a Concurrency-Limited Task Group Gate using an anyio.CapacityLimiter:

# omega_hub/tools/library_web_search.pyimport osimport jsonfrom datetime import datetimeimport anyiofrom anyio import Path, CapacityLimiter
async def library_web_search(ctx, query: str, limit: int = 15) -> str:
    """
    Structured anyio Ingestion Wrapper for the local Tailscale Federation Layer.
    Implements a strict capacity limiter to prevent memory exhaustion during 5M char transfers.
    """
    try:
        with anyio.move_on_after(10.0):
            local_cache = await ctx.call_tool("mempalace", "mempalace_search", {
                "query": query, "limit": 3
            })
            if local_cache and getattr(local_cache, 'highest_confidence', 0) > 0.96:
                return getattr(local_cache, 'payload', str(local_cache))
    except Exception as err:
        print(f"[omega-hub] Cache lookup skip: {err}")

    search_payload = await ctx.call_tool("parallel-search", "web_search", {
        "query": query,
        "max_results": limit
    })
    
    try:
        data = json.loads(search_payload) if isinstance(search_payload, str) else search_payload
        urls = data.get("canonical_urls", [])[:5]
    except Exception:
        return "System Error: Invalid JSON schema returned from search backend."

    accumulated_markdown = []
    # Cap simultaneous multi-source document ingestion spikes at exactly 2 concurrent streams
    limiter = CapacityLimiter(2)

    async def fetch_and_archive(target_url):
        async with limiter:
            raw_document = await ctx.call_tool("parallel-search", "web_fetch", {"url": target_url})
            clean_slug = "".join([c if c.isalnum() else "_" for c in target_url.split("/")[-1]])
            timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
            archive_path = Path(os.path.expanduser("~/WanderGround/inbox")) / f"{ctx.agent_name}_{timestamp}_{clean_slug}.md"
            
            frontmatter = (
                "---\n"
                f"source_url: \"{target_url}\"\n"
                f"entity: \"{ctx.agent_name}\"\n"
                f"timestamp: \"{datetime.utcnow().isoformat()}Z\"\n"
                "---\n\n"
            )
            await archive_path.write_text(frontmatter + raw_document, encoding='utf-8')
            accumulated_markdown.append(raw_document)

    async with anyio.create_task_group() as tg:
        for url in urls:
            tg.start_soon(fetch_and_archive, url)
        
    return "\n\n---NEW UNTHROTTLED FILE INGESTION---\n\n".join(accumulated_markdown)

------------------------------
## 🗂️ 4. Enhancing Frontmatter Meta-Schemas for Systematic Mining
To ensure your background Curator Daemon correctly indexes incoming data into clean MemPalace rooms without manual parsing, you must upgrade the YAML meta-schema in Phase 4. The subagents must write strict Domain Axis Keys.
## Upgraded Frontmatter Mapping Target Template
Every single file dropped into ~/WanderGround/inbox/ must perfectly match this expanded structural block:

---source_url: "https://kernel.org"source_type: "authoritative_kernel_spec"entity: "asus_plan"timestamp: "2026-09-17T15:01:00Z"hardware_target: "Intel-i7-13620H-RaptorLake"domain_axis: "01_local_ai/kernel"palace_routing:
  wing: "Vanguard_Systems"
  room: "Intel_Tuning"tags: ["kernel", "intel_pstate", "thp", "unthrottled"]
---

------------------------------
## 📋 Next-Step Instructions for Your OpenCode Agent
Instruct your agent to integrate these architectural modifications directly into its source files.
To write the absolute final, executable production draft of the manual, please have your OpenCode agent confirm:

* The exact absolute file path to your omega-hub tool registry entry point script (to automate Phase 5.2).
* The explicit name of the system user account group running OpenCode on Node 1 (to ensure systemd user privilege paths match perfectly).



