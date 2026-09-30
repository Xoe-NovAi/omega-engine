# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""The protocol interpreter. Six verbs, and nothing else.

ADR-001: the communication protocol is DATA; this is the mechanism that reads
it. The test of any new feature is "does it add to this surface?" — if it
does, it belongs in the protocol file instead.

    THE SIX VERBS
      1. load_protocol(path)          read a declared protocol
      2. validate(message)            check it against the declared schema
      3. persist(store, message)      write it with a monotonic sequence number
      4. read_inbox(store, ...)       the declared query path
      5. transition(store, ...)       record a state change, refusing illegal ones
      6. receipt(store, ...)          the recorded outcome of an accepted message

Why the surface is capped
-------------------------
id unlocked thirty years of complexity without changing its engine, because
everything variable was data. Every verb added here is a future migration for
every WAD in existence. That is the whole argument for the cap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class ProtocolMalformed(RuntimeError):
    """The protocol file is missing or invalid. Refuse loudly; never default."""


class ProtocolViolation(RuntimeError):
    """A message or transition violates the declared protocol."""


# ── verb 1 ────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Protocol:
    """A parsed, validated protocol declaration."""

    path: Path
    name: str
    version: int
    raw: dict[str, Any] = field(repr=False, default_factory=dict)

    # layout
    @property
    def layout(self) -> dict[str, str]:
        return self.raw.get("layout", {})

    # schema
    @property
    def required(self) -> list[str]:
        return list(self.raw.get("schema", {}).get("required", []))

    @property
    def types(self) -> dict[str, Any]:
        return self.raw.get("schema", {}).get("types", {})

    @property
    def id_re(self) -> re.Pattern[str] | None:
        pat = self.types.get("message_id")
        if isinstance(pat, str) and pat.startswith("pattern "):
            return re.compile(pat.split("pattern ", 1)[1].strip("$ "))
        return None

    # lifecycle
    @property
    def initial_state(self) -> str:
        return self.raw.get("lifecycle", {}).get("initial", "pending")

    @property
    def states(self) -> dict[str, Any]:
        return self.raw.get("lifecycle", {}).get("states", {})

    @property
    def transitions(self) -> dict[str, list[str]]:
        return self.raw.get("lifecycle", {}).get("transitions", {})

    def retention_days(self, state: str) -> int | None:
        return (self.states.get(state) or {}).get("retention_days")

    # naming
    @property
    def naming(self) -> dict[str, Any]:
        return self.raw.get("naming", {})

    def canonicalise(self, name: str) -> str:
        """Canonical form of a target name. NEVER strips a node suffix.

        The suffix fold is deliberately absent. `makali-n0` and `makali` are
        distinct registered agents, and folding them was the deployed
        heuristic that GE-N0 measured and found wrong.
        """
        if not self.naming.get("case_sensitive", False):
            name = name.lower()
        seps = self.naming.get("separators_equivalent", ["_", "-"])
        if len(seps) == 2:
            name = name.replace(seps[0], seps[1])
        return name

    @property
    def suffix_is_significant(self) -> bool:
        return bool(self.naming.get("node_suffix_is_significant", True))

    # delivery
    @property
    def delivery(self) -> dict[str, Any]:
        return self.raw.get("delivery", {})


def load_protocol(path: str | Path) -> Protocol:
    """VERB 1. Read a declared protocol. Malformed input refuses loudly."""
    p = Path(path)
    if not p.is_file():
        raise ProtocolMalformed(
            f"protocol file not found: {p}. Refusing to invent defaults — "
            "a communication protocol with implied behaviour is not a protocol."
        )
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        raise ProtocolMalformed(f"protocol file is not valid YAML: {p}: {exc}") from exc
    if not isinstance(raw, dict) or "protocol" not in raw:
        raise ProtocolMalformed(f"{p}: missing top-level 'protocol' block")

    head = raw["protocol"]
    if not isinstance(head, dict):
        raise ProtocolMalformed(f"{p}: 'protocol' must be a mapping")
    name = head.get("name")
    if not name:
        raise ProtocolMalformed(f"{p}: protocol.name is required")
    version = head.get("version")
    if not isinstance(version, int):
        raise ProtocolMalformed(f"{p}: protocol.version must be an integer")

    proto = Protocol(path=p, name=str(name), version=version, raw=raw)
    # Validate the declarations this module depends on, so a typo in the data
    # surfaces at load time rather than as a mysterious runtime failure later.
    if not proto.required:
        raise ProtocolMalformed(f"{p}: schema.required must not be empty")
    if proto.initial_state not in proto.states:
        raise ProtocolMalformed(
            f"{p}: lifecycle.initial '{proto.initial_state}' is not a declared state"
        )
    for src in proto.transitions:
        if src not in proto.states:
            raise ProtocolMalformed(f"{p}: transition source '{src}' is not a declared state")
        for dst in proto.transitions[src]:
            if dst not in proto.states:
                raise ProtocolMalformed(
                    f"{p}: transition {src}->{dst} targets undeclared state '{dst}'"
                )
    return proto


# ── verb 2 ────────────────────────────────────────────────────────────────────

def validate(proto: Protocol, message: dict[str, Any]) -> list[str]:
    """VERB 2. Check a message against the declared schema.

    Returns the list of problems. An empty list means valid. It never raises for
    an ordinary bad message — the caller decides what an invalid message means —
    but it never silently accepts one either.
    """
    problems: list[str] = []
    for field_name in proto.required:
        if field_name not in message:
            problems.append(f"missing required field: {field_name}")
        elif message.get(field_name) is None and field_name != "resolved_target":
            problems.append(f"required field is null: {field_name}")

    rx = proto.id_re
    mid = message.get("message_id")
    if rx is not None and isinstance(mid, str) and not rx.match(mid):
        problems.append(f"message_id does not match the declared pattern: {mid!r}")

    state = message.get("state", proto.initial_state)
    if state is not None and state not in proto.states:
        problems.append(f"undeclared state: {state!r}")

    # The whole point of ADR-001: requested and resolved are DISTINCT fields, so
    # fold-vs-sender becomes answerable from the record instead of inferred.
    req, res = message.get("requested_target"), message.get("resolved_target")
    if isinstance(req, str) and isinstance(res, str) and proto.naming:
        if proto.naming.get("resolve_and_log", True):
            expected = proto.canonicalise(req)
            if proto.suffix_is_significant and expected != res and res == expected:
                pass  # same name, canonical form recorded — consistent
            elif expected != res and res is not None:
                problems.append(
                    f"resolved_target {res!r} is not the canonical form of "
                    f"requested_target {req!r} (expected {expected!r})"
                )
    return problems


def requires_write(proto: Protocol) -> bool:  # pragma: no cover - convenience
    return bool(proto.delivery.get("ack_required", False))


# ── verb 5 ────────────────────────────────────────────────────────────────────

def check_transition(proto: Protocol, src: str, dst: str) -> None:
    """VERB 5. Refuse an illegal state change.

    The declared transition table IS the ruling. It is never widened at runtime
    and never inferred from a name.
    """
    if src not in proto.states:
        raise ProtocolViolation(f"unknown source state: {src!r}")
    if dst not in proto.states:
        raise ProtocolViolation(f"unknown target state: {dst!r}")
    allowed = proto.transitions.get(src, [])
    if dst not in allowed:
        raise ProtocolViolation(
            f"illegal transition {src} -> {dst}. Declared legal: {allowed or '[] (terminal)'}"
        )


def legal_targets(proto: Protocol, src: str) -> list[str]:
    """What may follow this state, per the declaration."""
    if src not in proto.states:
        raise ProtocolViolation(f"unknown state: {src!r}")
    return list(proto.transitions.get(src, []))


# ── verb 6 ────────────────────────────────────────────────────────────────────

def receipt_fields(proto: Protocol) -> list[str]:
    """VERB 6. What a receipt must carry, per the declaration."""
    return list(proto.delivery.get("receipt_fields", []))


def inbox_dir(proto: Protocol) -> str:
    """The declared inbox directory name. Interface, not just structure."""
    return proto.layout.get("inbox", "pending")


def surface() -> dict[str, list[str]]:
    """The declared interpreter surface. A gate asserts this stays at six.

    If a new verb appears here without a protocol-declared reason, the design
    has leaked back into code — which is the failure ADR-001 exists to stop.
    """
    return {
        "load": ["load_protocol"],
        "validate": ["validate"],
        "persist": ["FederationStore.persist"],
        "read": ["FederationStore.query"],
        "transition": ["check_transition", "legal_targets"],
        "receipt": ["receipt_fields"],
    }
