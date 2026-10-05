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
# Redis *:6379, deluged <WIFI_IFACE>:51372). None appeared in any policy file. None
# would have been caught by an existing gate.
#
# A LAN bind and a tailnet bind are DIFFERENT classes and are reported
# separately: a LAN bind is reachable by anything on the segment with no policy
# in the path; a tailnet bind is still filtered by tailscaled's packet filter.
#
# POLICY RESOLUTION (D-616) — two files, two jobs:
#   config/lan_exposure_allowlist.yaml            TRACKED. Public template.
#                                               Placeholders only; ships.
#   config/lan_exposure_allowlist.local.yaml     UNTRACKED. Host-local reality.
#                                               Real values; gitignored.
#   effective = local overlay tracked, by top-level key replacement.
# Rationale in `load_allowlist`. Do not "fix" this by writing a real address
# back into the tracked file — that reintroduces the public leak D-612 closed.
#
# Exit codes:  0 = clean   1 = exposure found (gate RED)   2 = audit error
#
# MANDATE NOTE: read-only. This script never stops, disables, or removes
# anything. It reports. A gate that mutated its own subject could not be used
# as evidence that the subject was clean.

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Tracked policy: placeholder-only on purpose. It ships publicly, so it must
# never carry a real address, interface, or MagicDNS name (D-612).
ALLOWLIST = REPO_ROOT / "config" / "lan_exposure_allowlist.yaml"

# Host-local policy overlay: UNTRACKED and gitignored. This is where a node
# records the values that are true on THIS machine and must not ship.
#
# WHY THIS EXISTS (D-616): D-612 replaced the real host values in the tracked
# file with documentation placeholders so the public cut would not leak them.
# That is correct for the public surface and it broke the gate on the host that
# D-612 was run from — `tailnet_interfaces: [<TAILSCALE_IFACE>]` cannot match
# `tailscale0`, so three real tailscaled binds on the tailnet address were
# reclassified as LAN and the gate went RED. The regression was invisible in CI
# because the negative tests were sanitized by the same commit, so both sides
# moved together and the suite agreed with itself.
#
# THE FIX IS A SEPARATION OF CONCERNS, NOT A REVERSAL:
#   tracked file  = the PUBLIC TEMPLATE. Placeholders only. Never a real value.
#   local file    = the HOST-LOCAL REALITY. Real values. Never committed.
# Precedence: local override > tracked. See `load_allowlist`.
LOCAL_OVERRIDE_ENV = "OMEGA_LAN_ALLOWLIST_LOCAL"
LOCAL_OVERRIDE_CANDIDATES = (
    REPO_ROOT / "config" / "lan_exposure_allowlist.local.yaml",
    Path.home() / ".config" / "omega" / "lan_exposure_allowlist.local.yaml",
)

# A value like `<TAILSCALE_IFACE>` is documentation, not policy. If one reaches
# the EFFECTIVE config it means the local override is missing or stale, and the
# gate is blind in exactly the way D-612 blinded it. Surfaced, never silenced.
PLACEHOLDER_RE = re.compile(r"^<.+>$")
SECURITY_RELEVANT_KEYS = (
    "always_exempt_addresses",
    "tailnet_addresses",
    "tailnet_interfaces",
    "allowed_lan_bindings",
    "allowed_tailnet_bindings",
    "suppressed_ports",
)

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


def _load_yaml_file(path: Path) -> dict:
    """Parse one allowlist file. Minimal YAML subset parse — no third-party dep.

    Falls back to PyYAML if present, else uses a small hand parser. The file is
    authored in a deliberately simple block style so the fallback stays correct.
    """
    if not path.exists():
        raise SystemExit(f"[FATAL] allowlist not found: {path}")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text()) or {}
    except ImportError:
        pass
    return _mini_yaml(path.read_text())


def resolve_local_override_path(explicit: Path | None = None) -> Path | None:
    """Find the host-local override file, or None if this host has none.

    Discovery order (first hit wins):
      1. `explicit`            — an argument, used by the tests to point at a
                                synthetic file instead of the real host's.
      2. $OMEGA_LAN_ALLOWLIST_LOCAL — operator override, wins over discovery so
                                a node can relocate the file off the repo.
      3. config/lan_exposure_allowlist.local.yaml  (repo-adjacent, gitignored)
      4. ~/.config/omega/lan_exposure_allowlist.local.yaml

    An explicitly-requested path that does not exist is an ERROR, not a silent
    fall-through to the tracked file: a caller asking for a specific override
    and quietly getting template policy instead is how a gate goes blind while
    reporting PASS.
    """
    if explicit is not None:
        p = Path(explicit)
        if not p.exists():
            raise SystemExit(f"[FATAL] local override not found: {p}")
        return p

    env = os.environ.get(LOCAL_OVERRIDE_ENV)
    if env:
        p = Path(env).expanduser()
        return p if p.exists() else None

    for cand in LOCAL_OVERRIDE_CANDIDATES:
        if cand.exists():
            return cand
    return None


def merge_allowlists(base: dict, overlay: dict) -> dict:
    """Overlay `overlay` onto `base` by TOP-LEVEL KEY REPLACEMENT.

    Replacement, not concatenation, and that choice is load-bearing. The tracked
    values for host-specific keys are documentation placeholders
    (`tailnet_interfaces: [<TAILSCALE_IFACE>]`, `tailnet_addresses: [10.0.0.1]`).
    Concatenating would leave the placeholder sitting in the effective policy as
    a dead entry that reads like coverage while matching nothing — precisely the
    "policy excision is not host excision" shape this gate exists to catch.

    A key present in the overlay replaces the tracked value wholesale. A key
    absent from the overlay is inherited. So a node can tighten policy (redefine
    `allowed_lan_bindings` to be non-empty and refuse the tracked default) as
    well as extend it.
    """
    merged = dict(base)
    for key, value in overlay.items():
        merged[key] = value
    return merged


def load_allowlist(
    path: Path | None = None,
    local_path: Path | None = None,
    *,
    use_local: bool = True,
) -> dict:
    """Load the EFFECTIVE allowlist: tracked template + host-local override.

    Precedence: local override > tracked file. See `merge_allowlists`.

    Args:
        path:      tracked file to read (default: the repo template).
        local_path: explicit override to overlay (default: discovered).
        use_local: set False to load the tracked template ALONE. The negative
                   tests use this to assert that the override is load-bearing —
                   i.e. that the template on its own does NOT clear the gate.
    """
    tracked = _load_yaml_file(path or ALLOWLIST)
    if not use_local:
        return tracked
    local = resolve_local_override_path(local_path)
    if local is None:
        return tracked
    return merge_allowlists(tracked, _load_yaml_file(local))


def effective_sources(
    path: Path | None = None, local_path: Path | None = None, *, use_local: bool = True
) -> tuple[Path, Path | None]:
    """Return (tracked_path, local_path_or_None) for display in the audit."""
    tracked = path or ALLOWLIST
    if not use_local:
        return tracked, None
    try:
        return tracked, resolve_local_override_path(local_path)
    except SystemExit:
        return tracked, None


def find_placeholders(allow: dict) -> list[tuple[str, str]]:
    """Return (key, placeholder) pairs surviving in security-relevant fields.

    A placeholder in the effective policy means the operator forgot to populate
    the local override: the gate will still run, still classify, and will
    silently fail to recognise this host's tailnet. D-612 shipped exactly that
    state and it was invisible for a full commit cycle.
    """
    found: list[tuple[str, str]] = []
    for key in SECURITY_RELEVANT_KEYS:
        for item in _as_list(allow.get(key)):
            if isinstance(item, dict):
                for sub in ("address", "port", "process"):
                    val = item.get(sub)
                    if val is not None and PLACEHOLDER_RE.match(str(val).strip()):
                        found.append((f"{key}.{sub}", str(val)))
            elif item is not None and PLACEHOLDER_RE.match(str(item).strip()):
                found.append((key, str(item)))
    return found


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
        #   "[::]:111"  "[::1]:631"  "[fe80::1%<WIFI_IFACE>]:44348"
        # The bracket test must therefore happen AFTER splitting off %iface —
        # a string like "[fe80::1%<WIFI_IFACE>]" does not end with ']', which is why an
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

    # CI-runner exemption (PR #5 post-merge CI, 2026-10-03): GitHub-hosted
    # runners ship sshd bound to 0.0.0.0:22 and :::22 for their own debug
    # path. The runner is an ephemeral CI VM, not a deployment target, and an
    # unprivileged `ss -ltnp` there cannot attribute the socket
    # (UNKNOWN-PROCESS). Scoped to GITHUB_ACTIONS + wildcard + port 22 ONLY —
    # the gate stays at full strength on Node 0, where a wildcard :22 bind
    # must still go RED. Pinning by env rather than the static allowlist
    # keeps this hole out of the reviewed policy file entirely.
    if (
        os.environ.get("GITHUB_ACTIONS") == "true"
        and l.is_wildcard
        and l.port == 22
    ):
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
    tracked_path, local_path = effective_sources()
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
    print(f"  policy source (tracked)  : {tracked_path}")
    print(f"  policy source (local)    : "
          f"{local_path if local_path else 'NONE — tracked template only'}")
    print()

    # Placeholders reaching the EFFECTIVE policy are the D-612 signature. The
    # tracked template is placeholder-only BY DESIGN; what matters is whether one
    # survived the merge, because that means this host's real tailnet is not
    # being recognised and every tailnet bind will be misfiled as a LAN bind.
    placeholders = find_placeholders(allow)
    if placeholders:
        print(f"{YELLOW}POLICY INTEGRITY WARNING — "
              f"{len(placeholders)} placeholder(s) in the EFFECTIVE policy{NC}")
        print("  The tracked file is a public template and is placeholder-only by")
        print("  design. A placeholder surviving into the effective policy means the")
        print("  host-local override is missing or stale, so this host's real")
        print("  tailnet addresses and interfaces are NOT recognised. Every tailnet")
        print("  bind will then be misreported as a LAN bind — the D-612 failure.")
        print("  Populate the untracked override, e.g.:")
        print(f"    {LOCAL_OVERRIDE_CANDIDATES[0]}")
        for key, val in placeholders:
            print(f"    - {key} = {val}")
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
