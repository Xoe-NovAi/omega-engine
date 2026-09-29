#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
#
# lan_exposure_audit.py — M-new / E1 systemic fix.
#
# Enumerates every `ss -ltn` listener bound to a non-loopback address and
# compares it against config/lan_exposure_allowlist.yaml.
#
# WHY (2026-09-28, E1 dispatch): three services were found LAN-bound while the
# tailnet policy was believed to describe total exposure (NFS 2049/20048/32803,
# Redis *:6379, deluged wlo1:51372). None appeared in any policy file. None
# would have been caught by an existing gate.
#
# A LAN bind and a tailnet bind are DIFFERENT classes and are reported
# separately: a LAN bind is reachable by anything on the segment with no policy
# in the path; a tailnet bind is still filtered by tailscaled's packet filter.
#
# Exit codes:  0 = clean   1 = exposure found (gate RED)   2 = audit error
#
# MANDATE NOTE: read-only. This script never stops, disables, or removes
# anything. It reports. A gate that mutated its own subject could not be used
# as evidence that the subject was clean.

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST = REPO_ROOT / "config" / "lan_exposure_allowlist.yaml"

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
NC = "\033[0m"

# Addresses that are loopback or kernel-internal regardless of allowlist.
HARDCODED_LOOPBACK = {"127.0.0.1", "::1", "127.0.0.53", "127.0.0.54", "localhost"}


@dataclass
class Listener:
    """One parsed row of `ss -ltn`."""

    bind_addr: str
    port: int
    ifname: str | None
    process: str | None

    @property
    def is_loopback(self) -> bool:
        a = self.bind_addr.split("%")[0]
        return a in HARDCODED_LOOPBACK

    @property
    def is_link_local(self) -> bool:
        # fe80::/10 — every fe80: address is link-local and unroutable off-link.
        a = self.bind_addr.split("%")[0].lower()
        return a.startswith("fe80:") or a.startswith("fe8") or a.startswith("fe9") \
            or a.startswith("fea") or a.startswith("feb")

    @property
    def is_wildcard(self) -> bool:
        return self.bind_addr in ("0.0.0.0", "*", "::", "[::]")


@dataclass
class Finding:
    """A listener that is non-loopback and not on the allowlist."""

    listener: Listener
    kind: str  # "LAN" or "TAILNET"
    reason: str

    def render(self) -> str:
        l = self.listener
        iface = f" (iface {l.ifname})" if l.ifname else ""
        proc = l.process or "UNKNOWN-PROCESS"
        return (
            f"  {self.kind:<8} {l.bind_addr}:{l.port}{iface}\n"
            f"           process: {proc}\n"
            f"           reason:  {self.reason}"
        )


def load_allowlist() -> dict:
    """Parse the allowlist. Minimal YAML subset parse — no third-party dep.

    Falls back to PyYAML if present, else uses a small hand parser. The file is
    authored in a deliberately simple block style so the fallback stays correct.
    """
    if not ALLOWLIST.exists():
        raise SystemExit(f"[FATAL] allowlist not found: {ALLOWLIST}")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(ALLOWLIST.read_text()) or {}
    except ImportError:
        pass
    return _mini_yaml(ALLOWLIST.read_text())


def _mini_yaml(text: str) -> dict:
    """Parse the restricted YAML subset used by the allowlist.

    Supports: scalar `key: value`, block `key:` followed by `- item` lists, and
    `- key: value` mappings inside those lists. That is exactly what the
    allowlist uses and nothing more. Anything else is ignored deliberately
    rather than guessed at.
    """
    root: dict = {}
    stack: list[tuple[int, object]] = [(-1, root)]
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        body = line.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            stack = [(-1, root)]
        container = stack[-1][1]
        if body.startswith("- "):
            item = body[2:].strip()
            if isinstance(container, list):
                if ":" in item:
                    k, _, v = item.partition(":")
                    mapping: dict = {}
                    mapping[k.strip()] = v.strip().strip('"').strip("'")
                    container.append(mapping)
                    stack.append((indent, mapping))
                else:
                    container.append(item.strip('"').strip("'"))
            continue
        if ":" not in body:
            continue
        key, _, val = body.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            # Possible nested block (list or mapping); decide lazily.
            probe: object = []
            parent = stack[-1][1]
            if isinstance(parent, dict):
                parent[key] = probe
            stack.append((indent, probe))
        else:
            val = val.split("  #")[0].strip().strip('"').strip("'")
            if isinstance(container, dict):
                container[key] = val
    return root


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def parse_ss() -> list[Listener]:
    """Run `ss -ltnp` and parse it. Returns [] if ss is unavailable."""
    if not shutil.which("ss"):
        raise SystemExit("[FATAL] 'ss' not found — cannot audit without iproute2")
    out = subprocess.run(
        ["ss", "-ltnp"], capture_output=True, text=True, check=False
    ).stdout

    listeners: list[Listener] = []
    for line in out.splitlines()[1:]:  # skip header
        parts = line.split()
        if len(parts) < 4:
            continue
        local = parts[3]
        if ":" not in local:
            continue
        addr, _, port_s = local.rpartition(":")
        try:
            port = int(port_s)
        except ValueError:
            continue
        # ss emits bracketed IPv6 with the %iface suffix INSIDE the brackets:
        #   "[::]:111"  "[::1]:631"  "[fe80::1%wlo1]:44348"
        # The bracket test must therefore happen AFTER splitting off %iface —
        # a string like "[fe80::1%wlo1]" does not end with ']', which is why an
        # endswith-based strip silently misses every link-local bind.
        ifname = None
        if "%" in addr:
            addr, _, ifname = addr.partition("%")
        addr = addr.strip("[]")
        if ifname:
            ifname = ifname.strip("[]")
        proc = None
        for token in parts:
            if token.startswith("users:("):
                m = token.split('"')[1] if '"' in token else None
                if m:
                    proc = m
                    break
        listeners.append(Listener(addr, port, ifname, proc))
    return listeners


def classify(l: Listener, allow: dict) -> tuple[str, str] | None:
    """Return (kind, reason) if this listener is an exposure. None if clean."""
    if l.is_loopback or l.is_link_local:
        return None
    if l.port in {int(p) for p in _as_list(allow.get("suppressed_ports"))}:
        return None
    if l.bind_addr in HARDCODED_LOOPBACK:
        return None

    exempt = set(_as_list(allow.get("always_exempt_addresses")))
    if l.bind_addr in exempt:
        return None

    tailnet_addrs = {
        str(a).split("%")[0].strip("[]").lower()
        for a in _as_list(allow.get("tailnet_addresses"))
    }
    tailnet_ifaces = set(_as_list(allow.get("tailnet_interfaces")))

    l_norm = l.bind_addr.strip("[]").lower()
    is_tailnet = l_norm in tailnet_addrs or (
        l.ifname is not None and l.ifname in tailnet_ifaces
    )
    kind = "TAILNET" if is_tailnet else "LAN"

    allowed = _as_list(
        allow.get("allowed_tailnet_bindings" if is_tailnet else "allowed_lan_bindings")
    )
    for entry in allowed:
        if not isinstance(entry, dict):
            continue
        e_addr = str(entry.get("address", "")).split("%")[0].strip("[]").lower()
        e_port = entry.get("port")
        e_proc = str(entry.get("process", ""))
        if e_addr != l_norm or e_port is None or int(e_port) != l.port:
            continue
        # Address+port is the identity of a bind. The process field narrows the
        # entry, but `ss -ltnp` frequently cannot attribute a socket (kernel
        # threads, tailscaled's netstack listeners, and anything in a foreign
        # netns show no `users:(...)` token). An unattributable listener must
        # therefore still match on address+port alone, otherwise the allowlist
        # would be unsatisfiable for exactly the services it exists to permit.
        if not e_proc:
            return None
        if l.process is None:
            return None
        if e_proc in l.process:
            return None
        # Address+port matched but a different process owns it — that is a
        # takeover, not a match. Fall through to reporting it.

    if is_tailnet:
        reason = (
            "bound to the tailnet interface; tailscaled's packet filter still "
            "gates this, but it is not on the approved tailnet allowlist"
        )
    elif l.is_wildcard:
        reason = (
            "wildcard bind — reachable from EVERY interface including the LAN "
            "with no policy in the path"
        )
    else:
        reason = "bound to a routable non-loopback address with no policy in the path"
    return kind, reason


def main() -> int:
    allow = load_allowlist()
    listeners = parse_ss()

    findings: list[Finding] = []
    for l in listeners:
        verdict = classify(l, allow)
        if verdict:
            kind, reason = verdict
            findings.append(Finding(l, kind, reason))

    lan = [f for f in findings if f.kind == "LAN"]
    tailnet = [f for f in findings if f.kind == "TAILNET"]

    total = len(listeners)
    non_loopback = sum(
        1 for l in listeners if not (l.is_loopback or l.is_link_local)
    )

    print(f"{CYAN}LAN EXPOSURE AUDIT{NC}")
    print(f"  listeners scanned        : {total}")
    print(f"  non-loopback listeners   : {non_loopback}")
    print(f"  allowlist version        : {allow.get('version', '?')} "
          f"(updated {allow.get('updated', '?')})")
    print()

    if lan:
        print(f"{RED}{len(lan)} LAN EXPOSURE(S) — gate RED{NC}")
        print("  (a LAN bind has NO policy in the path; anything on the segment can reach it)")
        for f in lan:
            print(f.render())
        print()

    if tailnet:
        print(f"{YELLOW}{len(tailnet)} TAILNET BIND(S) not on allowlist — gate RED{NC}")
        print("  (tailnet binds are packet-filter-gated, lower risk, but must be explicit)")
        for f in tailnet:
            print(f.render())
        print()

    if findings:
        print(f"{RED}RESULT: FAIL{NC} — {len(findings)} unapproved non-loopback bind(s).")
        print()
        print("  Do NOT silence this by adding entries to the allowlist without")
        print("  recording the justification in the PR. That is the failure mode")
        print("  this gate exists to catch.")
        print()
        print("  Fix by one of:")
        print("    - rebind the service to 127.0.0.1 (preferred; smallest change)")
        print("    - stop + disable the unit AND remove the socket (survives reboot)")
        print("    - if it is genuinely required, add a reviewed entry with a reason")
        return 1

    print(f"{GREEN}RESULT: PASS{NC} — no unapproved non-loopback binds.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"{RED}[FATAL] audit error: {type(exc).__name__}: {exc}{NC}")
        sys.exit(2)
