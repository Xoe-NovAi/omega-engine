<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Gap G1-15: Grok CLI 8-Account Rotation — Part 3: Technical Specifications & Implementation Code

**AP Token**: `AP-GROKSTER-G1-15-SPECS-20260723`
**Date**: 2026-07-23
**Entity**: grokster (Grok Ecosystem Specialist)
**Context**: Detailed technical specifications, code examples, and implementation blueprints for the P3 Engineering Pillar (Ma'at) to construct the `GrokFleetOrchestrator`.

---

## 1. Fleet Directory & Configuration Topology

The orchestrator must isolate each Grok account into its own `GROK_HOME` to prevent session cross-contamination.

### Directory Structure
```text
~/.grok-fleet/
├── acct-1/
│   ├── auth.json          # Captured via `grok login --device-auth`
│   └── config.toml        # Base config (MCP servers, strict sandbox)
├── acct-2/
│   ├── auth.json
│   └── config.toml
...
└── acct-8/
```

### Base `config.toml` Template (Per Account)
```toml
# ~/.grok-fleet/acct-X/config.toml
[cli]
auto_update = false
telemetry = false

[models]
default = "grok-build"

[model.grok-build]
# Force strict sandbox for cloud agents (Security Posture)
sandbox = "strict"

[features]
web_fetch = false
write_file = false
```

---

## 2. ACP Handshake Implementation (Python / AnyIO)

To comply with Mandate 1 (AnyIO) and the strict ACP sequential handshake required by Grok Build, the orchestrator must wrap the subprocess and handle JSON-RPC frames.

```python
import anyio
import json
import os

class GrokACPClient:
    def __init__(self, account_dir: str):
        self.account_dir = account_dir
        self.process = None
        self.session_id = None

    async def start_and_handshake(self):
        # 1. Spawn process with isolated GROK_HOME
        env = os.environ.copy()
        env["GROK_HOME"] = self.account_dir
        
        self.process = await anyio.open_process(
            ["grok", "--no-auto-update", "agent", "stdio"],
            env=env,
            stdin=anyio.subprocess.PIPE,
            stdout=anyio.subprocess.PIPE,
            stderr=anyio.subprocess.STDOUT
        )

        # 2. Initialize
        init_req = {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "1",
                "clientCapabilities": {"fs": {"readTextFile": True}, "terminal": False}
            }
        }
        await self._send(init_req)
        init_res = await self._recv()

        # 3. Authenticate (CRITICAL STEP)
        auth_methods = [m["id"] for m in init_res.get("result", {}).get("authMethods", [])]
        method_id = "xai.api_key" if "xai.api_key" in auth_methods else "cached_token"
        
        auth_req = {
            "jsonrpc": "2.0", "id": 2, "method": "authenticate",
            "params": {"methodId": method_id, "_meta": {"headless": True}}
        }
        await self._send(auth_req)
        await self._recv() # Wait for auth success

        # 4. Create Session
        sess_req = {
            "jsonrpc": "2.0", "id": 3, "method": "session/new",
            "params": {"cwd": os.getcwd(), "mcpServers": []}
        }
        await self._send(sess_req)
        sess_res = await self._recv()
        self.session_id = sess_res["result"]["sessionId"]

    async def _send(self, payload: dict):
        msg = json.dumps(payload) + "\n"
        await self.process.stdin.send(msg.encode())

    async def _recv(self) -> dict:
        line = await self.process.stdout.receive()
        return json.loads(line.decode().strip())
```

---

## 3. Quota Monitoring (gRPC-web)

The orchestrator must proactively poll quota to avoid mid-stream failures where possible.

```python
import httpx
import json
from pathlib import Path

async def get_account_quota(account_dir: str) -> float:
    """Returns usage percentage (0.0 to 100.0)."""
    auth_file = Path(account_dir) / "auth.json"
    
    # Extract Bearer token
    with open(auth_file) as f:
        auth_data = json.load(f)
        token = auth_data.get("https://accounts.x.ai/sign-in", {}).get("key")
        
    if not token:
        raise ValueError("No valid session token found.")

    headers = {
        "Content-Type": "application/grpc-web+proto",
        "Authorization": f"Bearer {token}",
        "X-XAI-Token-Auth": "xai-grok-cli"
    }

    async with httpx.AsyncClient() as client:
        # Empty protobuf body required
        resp = await client.post(
            "https://grok.com/grok_api_v2.GrokBuildBilling/GetGrokCreditsConfig",
            headers=headers,
            content=b""
        )
        
        # Note: In production, use a proper protobuf parser. 
        # For MVP, we can regex/byte-scan the response for the float value 
        # representing `credit_usage_percent`, or use the x.ai/billing ACP extension.
        return parse_grpc_usage(resp.content) 
```

---

## 4. The Rotation State Machine (Mid-Stream Recovery)

When a 402 occurs during a `session/prompt` stream, the orchestrator must catch it and rotate.

```python
async def stream_prompt_with_rotation(fleet_manager, prompt_payload):
    max_retries = 3
    attempts = 0
    
    while attempts < max_retries:
        active_client = fleet_manager.get_best_account()
        
        try:
            # Send prompt
            await active_client._send({
                "jsonrpc": "2.0", "id": 4, 
                "method": "session/prompt",
                "params": {"sessionId": active_client.session_id, "prompt": prompt_payload}
            })
            
            # Read stream
            while True:
                chunk = await active_client._recv()
                
                # Check for mid-stream exhaustion (402)
                if "error" in chunk:
                    err_msg = chunk["error"].get("message", "")
                    if "usage balance exhausted" in err_msg or chunk["error"].get("code") == -32603:
                        raise QuotaExhaustedError(f"Account {active_client.account_dir} exhausted.")
                
                # Yield valid chunks
                if chunk.get("method") == "session/update":
                    yield chunk
                elif "result" in chunk:
                    break # Stream complete
                    
            return # Success, exit loop
            
        except QuotaExhaustedError:
            attempts += 1
            # Mark current account as cooling (300s)
            fleet_manager.mark_cooldown(active_client, duration=300)
            # Loop will fetch the next best account and retry
            
    raise Exception("Fleet exhausted: All accounts in cooldown.")
```

---
*End of Technical Specifications. Ready for implementation by P3 Engineering.*