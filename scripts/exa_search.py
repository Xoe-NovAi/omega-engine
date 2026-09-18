#!/usr/bin/env python3
"""Exa web research wrapper — live search + page fetch without any MCP server.

Reads EXA_API_KEY from the environment (or ~/.config/opencode/.env as fallback).
Never pass keys on the command line; never print them.

Usage:
    python3 scripts/exa_search.py search "query" [--num 5]
    python3 scripts/exa_search.py fetch <url> [--chars 6000]
"""
import json
import os
import sys
import urllib.request
from pathlib import Path


def _key() -> str:
    k = os.environ.get("EXA_API_KEY", "")
    if not k:
        envp = Path.home() / ".config" / "opencode" / ".env"
        if envp.exists():
            for line in envp.read_text().splitlines():
                if line.startswith("EXA_API_KEY="):
                    k = line.split("=", 1)[1].strip().strip('"')
    if not k:
        sys.exit("EXA_API_KEY not set (env or ~/.config/opencode/.env)")
    return k


def _post(path: str, payload: dict, timeout: int = 40) -> dict:
    req = urllib.request.Request(
        f"https://api.exa.ai{path}",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def cmd_search(args: list) -> None:
    if not args:
        sys.exit("usage: exa_search.py search \"query\" [--num 5]")
    num = 5
    if "--num" in args:
        num = int(args[args.index("--num") + 1])
        args = [a for a in args if a != "--num" and a != str(num)]
    body = _post("/search", {"query": " ".join(args), "numResults": num})
    for r in body.get("results", []):
        print(f"- {r.get('title', '')[:90]}")
        print(f"  {r.get('url', '')}")


def cmd_fetch(args: list) -> None:
    if not args:
        sys.exit("usage: exa_search.py fetch <url> [--chars 6000]")
    chars = 6000
    if "--chars" in args:
        chars = int(args[args.index("--chars") + 1])
        args = [a for a in args if a != "--chars" and a != str(chars)]
    body = _post("/contents", {"urls": args, "text": {"maxCharacters": chars}})
    for r in body.get("results", []):
        print(f"### {r.get('title', '')}\n{r.get('url', '')}\n")
        print(r.get("text", ""))
    for s in body.get("statuses", []):
        if s.get("status") == "error":
            print(f"!! {s.get('id')}: {s.get('error')}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    {"search": cmd_search, "fetch": cmd_fetch}[sys.argv[1]](sys.argv[2:])
