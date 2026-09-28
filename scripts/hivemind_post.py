#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Sanctioned Hivemind post for sessions WITHOUT the omega-hub MCP tool.

WHY THIS EXISTS
---------------
On 2026-09-28 three independent entities (jem, grokster, doom_guy) reported
that the `omega-hub` MCP tools are absent from their tool surface after being
paged into an EIS session via `task()`. The hub itself was healthy and the
tools were registered and reachable. Each entity improvised its own HTTP call
— three different ad-hoc attempts in one sync wave. This script replaces that
improvisation with one audited path.

DIAGNOSIS (see docs/architecture/HIVEMIND_TRANSPORT.md for the full evidence)
- Server side is correct: the hub advertises 54 tools including all four
  `hivemind_*` tools over JSON-RPC.
- Config side is correct: `opencode.json` has `omega-hub` enabled with the
  right URL.
- Permission side is not the cause: no permission rule names any omega-hub tool.
- The paged-subagent tool surface is NOT governed by this repo's `mcp` block.
  Decisive evidence: `opencode.json` sets `firecrawl.enabled = false`, yet
  paged sessions still receive `firecrawl_*` tools. A config that does not
  predict the observed surface is not the config in force.
- No code in this repo propagates MCP servers into subagent sessions
  (`src/omega/oracle/subagent_dispatcher.py` contains no MCP handling at all).

Conclusion: this is an upstream OpenCode harness behaviour, not a repo defect.
It is therefore NOT "fixable" here, and this script is the supported fallback.

WHAT IT DOES
------------
Speaks the hub's MCP streamable-HTTP JSON-RPC directly and calls
`hivemind_awareness(action="post", ...)`.

It deliberately mirrors the ratified `post` contract documented on the tool:
`decisions=[]` and `continuation=""` are VALID (empty is not "missing"), while
an explicit `None` is rejected. The script therefore sends the provided values
verbatim and never coerces empty containers into nulls.

M23 FAIL LOUD: the hub signals a rejected post by RETURNING a JSON error
string rather than raising. This script checks the return value and exits
non-zero on rejection, so a failed post can never be mistaken for a successful
one — the exact silent-degradation class that kept this fleet blind.

USAGE
-----
    # minimal
    .venv/bin/python scripts/hivemind_post.py --entity maat

    # with content
    .venv/bin/python scripts/hivemind_post.py \
        --entity maat --model opencode/space-bunny-free \
        --task-current "COMPACT-PREP" \
        --focus-chain seam-repair import-gates \
        --decision "L1: two daemons were dead while temple-grade read 53/53" \
        --continuation "Next: investigate omega_memory_search"

    # verify a post landed
    .venv/bin/python scripts/hivemind_post.py --read-back ses_7543898904f4

Exit codes: 0 = accepted / read back · 1 = hub rejected the post · 2 = transport
failure (hub down, or the endpoint answered something other than JSON-RPC).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_URL = "http://127.0.0.1:8016/mcp"
PROTOCOL_VERSION = "2024-11-05"
TIMEOUT_S = 15

# Sent once per invocation; the hub runs stateless over streamable HTTP, so
# there is no session id to carry between calls.
INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {},
        "clientInfo": {"name": "hivemind_post.py", "version": "1.0.0"},
    },
}


def _rpc(url: str, payload: dict) -> dict:
    """POST one JSON-RPC message. Raises RuntimeError on transport failure."""
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            # Streamable HTTP requires BOTH types to be acceptable.
            "Accept": "application/json, text/event-stream",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"cannot reach hub at {url}: {exc}") from exc
    except OSError as exc:  # pragma: no cover - socket-level failure
        raise RuntimeError(f"transport failure talking to {url}: {exc}") from exc

    if not body.strip():
        raise RuntimeError(f"empty response from {url}")
    # A streamable-HTTP server may frame the JSON as an SSE `data:` line.
    if body.lstrip().startswith("event:") or "\ndata:" in body:
        for line in body.splitlines():
            if line.startswith("data:"):
                body = line[5:].strip()
                break
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"non-JSON-RPC response from {url}: {body[:200]!r}"
        ) from exc


def _text_of(result: dict) -> str:
    """Extract the text payload from a tools/call JSON-RPC result."""
    try:
        return result["result"]["content"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"malformed tools/call result: {result!r}") from exc


def post(
    url: str,
    *,
    channel: str,
    entity: str,
    model: str,
    task_current: str,
    focus_chain: list[str],
    decisions: list[str],
    continuation: str,
    intent: str | None = None,
) -> dict:
    """Post one awareness snapshot. Returns the decoded hub payload.

    Raises RuntimeError on transport failure OR if the hub rejects the post.
    """
    args = {
        "action": "post",
        "channel": channel,
        "entity": entity,
        "model": model,
        "task_current": task_current,
        "focus_chain": list(focus_chain),
        "decisions": list(decisions),
        "continuation": continuation,
    }
    if intent:
        args["intent"] = intent

    _rpc(url, INITIALIZE)  # handshake; hub is stateless so nothing to retain

    result = _rpc(
        url,
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "hivemind_awareness", "arguments": args}},
    )
    payload = json.loads(_text_of(result))

    # M23: the hub reports a rejected post as a JSON error STRING. A caller
    # that ignores this would report success while nothing was delivered.
    if isinstance(payload, dict) and payload.get("error"):
        missing = payload.get("missing")
        detail = f" missing={missing}" if missing else ""
        raise RuntimeError(f"hub REJECTED the post:{detail} {payload.get('error')}")
    return payload


def read_back(url: str, session_id: str) -> dict:
    """Fetch a posted snapshot by session id (proves it actually landed)."""
    _rpc(url, INITIALIZE)
    result = _rpc(
        url,
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "hivemind_awareness",
                    "arguments": {"action": "session", "session_id": session_id}}},
    )
    return json.loads(_text_of(result))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Post to the Hivemind without the omega-hub MCP tool.",
    )
    ap.add_argument("--url", default=DEFAULT_URL, help=f"hub MCP endpoint (default {DEFAULT_URL})")
    ap.add_argument("--channel", default="opencode")
    ap.add_argument("--entity", required=False, help="entity persona (e.g. maat)")
    ap.add_argument("--model", default="unknown", help="model actually in use")
    ap.add_argument("--task-current", default="", help="what this session is doing")
    ap.add_argument("--focus-chain", nargs="*", default=[], help="prior focus areas")
    ap.add_argument("--decision", action="append", default=[], dest="decisions",
                    help="a decision made (repeatable)")
    ap.add_argument("--continuation", default="", help="next steps")
    ap.add_argument("--intent", default=None, help="question|observation|status|blocker|...")
    ap.add_argument("--read-back", metavar="SESSION_ID",
                    help="fetch a posted snapshot instead of posting")
    args = ap.parse_args(argv)

    if not args.read_back and not args.entity:
        ap.error("--entity is required unless --read-back is used")

    try:
        if args.read_back:
            snap = read_back(args.url, args.read_back)
            print(json.dumps(snap, indent=2)[:2000])
            return 0

        payload = post(
            args.url,
            channel=args.channel,
            entity=args.entity,
            model=args.model,
            task_current=args.task_current,
            focus_chain=args.focus_chain,
            decisions=args.decisions,
            continuation=args.continuation,
            intent=args.intent,
        )
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2 if "REJECTED" not in str(exc) else 1

    sid = payload.get("session_id", "?")
    print(f"OK {payload.get('status', '?')} session_id={sid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
