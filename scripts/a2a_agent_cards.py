#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""A2A v1.0 Agent Card validator and local discovery-index publisher.

[AP-A2A-AGENT-CARDS-v1.0.0] Ticket P1-2 — knowledge-gap remediation.

WHAT THIS IS
------------
Validates every sovereign seat's Agent Card in ``config/a2a/agent_cards/``
against the **A2A v1.0.0** specification's normative field tables, and
optionally publishes a LOCAL discovery index.

Normative reference: https://a2a-protocol.org/latest/specification
(v1.0.0). Every rule below carries its spec section as a comment. The spec is
authoritative; this file is a linter for it, not a redefinition of it.

MANDATES HONOURED HERE
----------------------
M8  Zero telemetry  — ``--publish`` writes ONE local JSON file. There is no
                      network egress anywhere in this module: no socket, no
                      urllib, no requests, no subprocess fetch. Read the imports.
M23 Failure integrity — ANY schema violation is an explicit, located error
                      (``file: field.path: what is wrong``) and the process
                      exits 1. The validator NEVER coerces a value, NEVER
                      defaults a missing required field, and NEVER repairs a
                      card. It reports; a human or a test decides.
M28 Artifact preservation — cards under ``config/a2a/agent_cards/`` are
                      READ-ONLY to this tool. It will never create, overwrite
                      or delete a card. ``--publish`` touches only the derived
                      index, and ``--diff`` reports index drift without
                      writing anything.
M24 Venv sovereignty — stdlib only; runs under the repo ``.venv``.

USAGE
-----
    scripts/a2a_agent_cards.py                 # validate all cards (default)
    scripts/a2a_agent_cards.py --list          # capability matrix
    scripts/a2a_agent_cards.py --publish       # write local discovery index
    scripts/a2a_agent_cards.py --diff          # index drift vs disk, no write
    scripts/a2a_agent_cards.py --json          # machine-readable report

EXIT CODES
----------
    0  every card validates (warnings may still be printed)
    1  at least one schema violation, or an I/O failure (M23)
    2  bad CLI usage
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = REPO_ROOT / "config" / "a2a" / "agent_cards"
INDEX_PATH = (
    REPO_ROOT / "data" / "coordination" / "a2a" / "agent_index.json"
)

#: Seats that must have a card, one file each. Kept explicit (rather than
#: "whatever is in the directory") so a DELETED card fails validation instead
#: of silently shrinking the fleet's declared surface.
REQUIRED_SEATS: tuple[str, ...] = (
    "kali",
    "maat",
    "lilith",
    "doom_guy",
    "john_carmack",
    "roc_racoon",
    "researcher",
    "verity",
    "antigravity",
    "makali",
)

#: §8.2 Discovery Mechanisms / §14.3 Well-Known URI Registration.
#: URI suffix is "agent-card.json"; the v0.3-era "agent.json" is legacy.
WELL_KNOWN_PATH = "/.well-known/agent-card.json"
LEGACY_WELL_KNOWN_PATH = "/.well-known/agent.json"

#: §5.4.6 / §4.4.6 — the three protocol bindings the A2A spec officially
#: defines. Our cards deliberately declare none of them (see CONFORMANCE_NOTE).
OFFICIAL_BINDINGS = frozenset({"JSONRPC", "GRPC", "HTTP+JSON"})

#: §4.5.1 SecurityScheme is a oneof over exactly these five members. A
#: SecurityScheme MUST contain exactly one.
SECURITY_SCHEME_MEMBERS = (
    "apiKeySecurityScheme",
    "httpAuthSecurityScheme",
    "oauth2SecurityScheme",
    "openIdConnectSecurityScheme",
    "mtlsSecurityScheme",
)

#: v0.3 AgentCard fields that DO NOT EXIST in v1.0. The string
#: "preferredTransport" occurs ZERO times in the v1.0 spec, and the v1.0
#: AgentCard table has no top-level "url". Emitting either is a v0.3-shaped
#: card and is rejected here so the mistake cannot ship quietly.
V03_ABSENT_FIELDS = ("url", "preferredTransport", "additionalInterfaces")

#: Namespaces we are allowed to add that the spec does not define. §5.7
#: ("Unrecognized Fields") says implementations SHOULD ignore unknown fields,
#: which is what makes a namespaced sidecar forward-compatible.
NON_NORMATIVE_NAMESPACES = ("x-omega",)

#: Conformance values that CLAIM compliance. A card may not both claim one of
#: these and still list conformity gaps — that is a self-contradiction, and
#: this validator treats a self-contradiction as an error.
COMPLIANCE_CLAIMING = frozenset({"compliant", "a2a-compliant", "conformant"})
CONFORMANCE_INFORMED = "informed-not-compliant"

CONFORMANCE_NOTE = (
    "These cards are A2A-informed, NOT A2A-compliant. No A2A method set is "
    "implemented and nothing serves the well-known discovery URI. See "
    "docs/architecture/A2A_AGENT_CARDS_20261003.md."
)


# ─────────────────────────────────────────────────────────────────────────────
# Problem reporting
# ─────────────────────────────────────────────────────────────────────────────


class Problem:
    """One located validation finding.

    Renders as ``file: field.path: what is wrong [spec §x.y]`` so the message
    is actionable without opening the file.
    """

    __slots__ = ("source", "path", "message", "severity", "spec")

    def __init__(
        self,
        source: str,
        path: str,
        message: str,
        severity: str = "error",
        spec: str = "",
    ) -> None:
        self.source = source
        self.path = path
        self.message = message
        self.severity = severity
        self.spec = spec

    def __str__(self) -> str:
        tail = f" [A2A v1.0 §{self.spec}]" if self.spec else ""
        return f"{self.source}: {self.path}: {self.message}{tail}"

    def to_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "path": self.path,
            "message": self.message,
            "severity": self.severity,
            "spec": self.spec,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Small typed predicates
# ─────────────────────────────────────────────────────────────────────────────


def _is_str(value: Any) -> bool:
    return isinstance(value, str)


def _is_bool(value: Any) -> bool:
    # bool is a subclass of int; a JSON `1` must not pass as a boolean.
    return isinstance(value, bool)


def _str_array(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(i, str) for i in value)


# ─────────────────────────────────────────────────────────────────────────────
# Field-table validators, one per spec object
# ─────────────────────────────────────────────────────────────────────────────


def validate_agent_card(card: Any, source: str) -> list[Problem]:
    """§4.4.1 AgentCard — required fields, nested objects, v0.3 rejection."""
    problems: list[Problem] = []
    if not isinstance(card, dict):
        return [
            Problem(
                source,
                "<root>",
                f"card must be a JSON object, got {type(card).__name__}",
                spec="4.4.1",
            )
        ]

    # -- v0.3 shape rejection (§4.4.1 has no top-level url/preferredTransport) --
    for stale in V03_ABSENT_FIELDS:
        if stale in card:
            problems.append(
                Problem(
                    source,
                    stale,
                    "field does not exist in A2A v1.0 AgentCard; this is a v0.3-shaped "
                    "field (v1.0 replaced url+preferredTransport with the "
                    "supportedInterfaces array)",
                    spec="4.4.1",
                )
            )

    # -- §4.4.1 required scalar fields --
    for field in ("name", "description", "version"):
        if field not in card:
            problems.append(
                Problem(source, field, "required field is missing", spec="4.4.1")
            )
        elif not _is_str(card[field]):
            problems.append(
                Problem(
                    source,
                    field,
                    f"must be a string, got {type(card[field]).__name__}",
                    spec="4.4.1",
                )
            )
        elif field != "version" and not card[field].strip():
            problems.append(
                Problem(source, field, "required string is empty", spec="4.4.1")
            )

    # -- §4.4.1 required media-type arrays --
    for field in ("defaultInputModes", "defaultOutputModes"):
        if field not in card:
            problems.append(
                Problem(source, field, "required field is missing", spec="4.4.1")
            )
        elif not _str_array(card[field]):
            problems.append(
                Problem(
                    source,
                    field,
                    "must be an array of media-type strings",
                    spec="4.4.1",
                )
            )
        elif not card[field]:
            # §5.7: "Arrays marked as required MUST contain at least one element."
            problems.append(
                Problem(
                    source,
                    field,
                    "required array must contain at least one element",
                    spec="5.7",
                )
            )

    # -- §4.4.1 required arrays of objects/strings --
    for field in ("supportedInterfaces", "skills"):
        if field not in card:
            problems.append(
                Problem(source, field, "required field is missing", spec="4.4.1")
            )
        elif not isinstance(card[field], list):
            problems.append(
                Problem(
                    source,
                    field,
                    f"must be an array, got {type(card[field]).__name__}",
                    spec="4.4.1",
                )
            )
        elif not card[field]:
            problems.append(
                Problem(
                    source,
                    field,
                    "required array must contain at least one element",
                    spec="5.7",
                )
            )

    if "capabilities" not in card:
        problems.append(
            Problem(source, "capabilities", "required field is missing", spec="4.4.1")
        )

    # -- §5.5 JSON field naming convention MUST be camelCase --
    problems.extend(_check_camel_case(card, source, ""))

    # -- nested objects --
    for i, iface in enumerate(card.get("supportedInterfaces") or []):
        if isinstance(iface, dict):
            problems.extend(validate_agent_interface(iface, source, f"supportedInterfaces[{i}]"))
    for i, skill in enumerate(card.get("skills") or []):
        if isinstance(skill, dict):
            problems.extend(validate_agent_skill(skill, source, f"skills[{i}]"))

    caps = card.get("capabilities")
    if isinstance(caps, dict):
        problems.extend(validate_capabilities(caps, source, "capabilities"))
    elif caps is not None and not isinstance(caps, dict):
        problems.append(
            Problem(
                source,
                "capabilities",
                f"must be an AgentCapabilities object, got {type(caps).__name__}",
                spec="4.4.3",
            )
        )

    provider = card.get("provider")
    if isinstance(provider, dict):
        problems.extend(validate_provider(provider, source, "provider"))

    problems.extend(validate_security(card, source))

    for i, sig in enumerate(card.get("signatures") or []):
        if isinstance(sig, dict):
            problems.extend(
                validate_signature(sig, source, f"signatures[{i}]")
            )

    # -- non-normative sidecar --
    problems.extend(_check_non_normative(card, source))
    return problems


def validate_agent_interface(iface: dict, source: str, path: str) -> list[Problem]:
    """§4.4.6 AgentInterface — url, protocolBinding, protocolVersion required."""
    problems: list[Problem] = []
    for field in ("url", "protocolBinding", "protocolVersion"):
        if field not in iface:
            problems.append(
                Problem(
                    source,
                    f"{path}.{field}",
                    "required field is missing",
                    spec="4.4.6",
                )
            )
        elif not _is_str(iface[field]):
            problems.append(
                Problem(
                    source,
                    f"{path}.{field}",
                    f"must be a string, got {type(iface[field]).__name__}",
                    spec="4.4.6",
                )
            )
        elif not iface[field].strip():
            problems.append(
                Problem(
                    source,
                    f"{path}.{field}",
                    "required string is empty",
                    spec="4.4.6",
                )
            )

    url = iface.get("url")
    if _is_str(url) and url:
        # §4.4.6: HTTP transports "must be a valid absolute HTTPS URL in
        # production"; gRPC uses "hostname:port". A bare http:// URL is not
        # production-valid, so we flag it.
        if url.startswith("http://"):
            problems.append(
                Problem(
                    source,
                    f"{path}.url",
                    "HTTP-based interface URLs must be absolute HTTPS in production",
                    severity="warning",
                    spec="4.4.6",
                )
            )
        elif not url.startswith("https://") and ":" in url:
            # gRPC-style hostname:port is explicitly allowed by §4.4.6.
            pass

    binding = iface.get("protocolBinding")
    if _is_str(binding) and binding in OFFICIAL_BINDINGS:
        problems.append(
            Problem(
                source,
                f"{path}.protocolBinding",
                f"declares official binding {binding!r}, but Omega implements no A2A "
                "method set and therefore no official A2A binding; declare a "
                "non-A2A custom binding URI per §5.8 instead of overclaiming",
                spec="5.8",
            )
        )
    return problems


def validate_agent_skill(skill: dict, source: str, path: str) -> list[Problem]:
    """§4.4.5 AgentSkill — id, name, description AND tags are all required."""
    problems: list[Problem] = []
    for field in ("id", "name", "description"):
        if field not in skill:
            problems.append(
                Problem(source, f"{path}.{field}", "required field is missing", spec="4.4.5")
            )
        elif not _is_str(skill[field]):
            problems.append(
                Problem(
                    source,
                    f"{path}.{field}",
                    f"must be a string, got {type(skill[field]).__name__}",
                    spec="4.4.5",
                )
            )
        elif not skill[field].strip():
            problems.append(
                Problem(source, f"{path}.{field}", "required string is empty", spec="4.4.5")
            )

    # tags is REQUIRED and is the field most often forgotten.
    if "tags" not in skill:
        problems.append(
            Problem(source, f"{path}.tags", "required field is missing", spec="4.4.5")
        )
    elif not _str_array(skill["tags"]):
        problems.append(
            Problem(
                source,
                f"{path}.tags",
                "must be an array of strings",
                spec="4.4.5",
            )
        )
    elif not skill["tags"]:
        problems.append(
            Problem(
                source,
                f"{path}.tags",
                "required array must contain at least one element",
                spec="5.7",
            )
        )

    for field in ("examples", "inputModes", "outputModes"):
        if field in skill and not _str_array(skill[field]):
            problems.append(
                Problem(
                    source,
                    f"{path}.{field}",
                    "must be an array of strings",
                    spec="4.4.5",
                )
            )
    return problems


def validate_provider(provider: dict, source: str, path: str) -> list[Problem]:
    """§4.4.2 AgentProvider — BOTH url and organization are required."""
    problems: list[Problem] = []
    for field in ("url", "organization"):
        if field not in provider:
            problems.append(
                Problem(
                    source,
                    f"{path}.{field}",
                    "required field is missing",
                    spec="4.4.2",
                )
            )
        elif not _is_str(provider[field]) or not provider[field].strip():
            problems.append(
                Problem(
                    source,
                    f"{path}.{field}",
                    "required string is missing or empty",
                    spec="4.4.2",
                )
            )
    return problems


def validate_capabilities(caps: dict, source: str, path: str) -> list[Problem]:
    """§4.4.3 AgentCapabilities — all members optional, all booleans."""
    problems: list[Problem] = []
    for field in ("streaming", "pushNotifications", "extendedAgentCard"):
        if field in caps and not _is_bool(caps[field]):
            problems.append(
                Problem(
                    source,
                    f"{path}.{field}",
                    f"must be a boolean, got {type(caps[field]).__name__}",
                    spec="4.4.3",
                )
            )

    exts = caps.get("extensions")
    if exts is not None:
        if not isinstance(exts, list):
            problems.append(
                Problem(
                    source,
                    f"{path}.extensions",
                    "must be an array of AgentExtension",
                    spec="4.4.4",
                )
            )
        else:
            for i, ext in enumerate(exts):
                if not isinstance(ext, dict):
                    problems.append(
                        Problem(
                            source,
                            f"{path}.extensions[{i}]",
                            "must be an object",
                            spec="4.4.4",
                        )
                    )
                    continue
                for field in ("uri", "description", "required", "params"):
                    if field in ext and field == "required" and not _is_bool(ext[field]):
                        problems.append(
                            Problem(
                                source,
                                f"{path}.extensions[{i}].required",
                                "must be a boolean",
                                spec="4.4.4",
                            )
                        )
                if "required" in ext and ext["required"] and "uri" not in ext:
                    problems.append(
                        Problem(
                            source,
                            f"{path}.extensions[{i}].uri",
                            "an extension declared required must carry its identifying uri",
                            spec="4.4.4",
                        )
                    )
    return problems


def validate_security(card: dict, source: str) -> list[Problem]:
    """§4.5 Security objects."""
    problems: list[Problem] = []
    schemes = card.get("securitySchemes")
    if schemes is None:
        return problems
    if not isinstance(schemes, dict):
        return [
            Problem(
                source,
                "securitySchemes",
                "must be a map of string to SecurityScheme",
                spec="4.5.1",
            )
        ]

    for name, scheme in schemes.items():
        base = f"securitySchemes.{name}"
        if not isinstance(scheme, dict):
            problems.append(Problem(source, base, "must be an object", spec="4.5.1"))
            continue
        present = [m for m in SECURITY_SCHEME_MEMBERS if m in scheme]
        # §4.5.1: a SecurityScheme MUST contain EXACTLY ONE of the five members.
        if len(present) == 0:
            problems.append(
                Problem(
                    source,
                    base,
                    "SecurityScheme must contain exactly one of "
                    + ", ".join(SECURITY_SCHEME_MEMBERS),
                    spec="4.5.1",
                )
            )
        elif len(present) > 1:
            problems.append(
                Problem(
                    source,
                    base,
                    "SecurityScheme is a oneof but carries "
                    + str(len(present))
                    + " members ("
                    + ", ".join(present)
                    + ")",
                    spec="4.5.1",
                )
            )
        if "mtlsSecurityScheme" in scheme:
            mtls = scheme["mtlsSecurityScheme"]
            if isinstance(mtls, dict):
                extra = set(mtls) - {"description"}
                # §4.5.6 defines ONLY an optional description.
                if extra:
                    problems.append(
                        Problem(
                            source,
                            f"{base}.mtlsSecurityScheme",
                            "MutualTlsSecurityScheme defines only an optional "
                            f"`description`; unexpected field(s): {sorted(extra)}",
                            spec="4.5.6",
                        )
                    )
        if "apiKeySecurityScheme" in scheme:
            api = scheme["apiKeySecurityScheme"]
            if isinstance(api, dict):
                for field in ("location", "name"):
                    if field not in api:
                        problems.append(
                            Problem(
                                source,
                                f"{base}.apiKeySecurityScheme.{field}",
                                "required field is missing",
                                spec="4.5.2",
                            )
                        )
                loc = api.get("location")
                if loc is not None and loc not in ("query", "header", "cookie"):
                    problems.append(
                        Problem(
                            source,
                            f"{base}.apiKeySecurityScheme.location",
                            f"must be one of query|header|cookie, got {loc!r}",
                            spec="4.5.2",
                        )
                    )

    reqs = card.get("securityRequirements")
    if reqs is not None and not isinstance(reqs, list):
        problems.append(
            Problem(
                source,
                "securityRequirements",
                "must be an array of SecurityRequirement",
                spec="4.4.1",
            )
        )
    return problems


def validate_signature(sig: dict, source: str, path: str) -> list[Problem]:
    """§4.4.7 AgentCardSignature — JWS (RFC 7515): protected + signature."""
    problems: list[Problem] = []
    for field in ("protected", "signature"):
        if field not in sig:
            problems.append(
                Problem(source, f"{path}.{field}", "required field is missing", spec="4.4.7")
            )
        elif not _is_str(sig[field]) or not sig[field].strip():
            problems.append(
                Problem(
                    source,
                    f"{path}.{field}",
                    "required base64url string is missing or empty",
                    spec="4.4.7",
                )
            )
    if "header" in sig and not isinstance(sig["header"], dict):
        problems.append(
            Problem(source, f"{path}.header", "must be an object", spec="4.4.7")
        )
    return problems


# ─────────────────────────────────────────────────────────────────────────────
# Cross-cutting checks
# ─────────────────────────────────────────────────────────────────────────────


#: Keys whose *contents* are outside the A2A protocol data model, so §5.5's
#: camelCase rule does not reach them:
#:   - anything under a non-normative namespace (it is not A2A data at all);
#:   - AgentExtension.params, which §4.4.4 defines as free-form
#:     "extension-specific configuration parameters".
CAMEL_CASE_EXEMPT_CONTAINERS = frozenset({"params"})


def _check_camel_case(
    node: Any, source: str, path: str, exempt: bool = False
) -> list[Problem]:
    """§5.5 — all JSON serialisations MUST use camelCase, not snake_case.

    ``exempt`` suppresses the rule for a subtree that is not part of the A2A
    protocol data model (our ``x-omega`` sidecar, or an extension's free-form
    ``params``). Applying §5.5 there would be a category error, not a
    validation.
    """
    problems: list[Problem] = []
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}" if path else key
            child_exempt = (
                exempt or key in NON_NORMATIVE_NAMESPACES or key in CAMEL_CASE_EXEMPT_CONTAINERS
            )
            if "_" in key and not exempt:
                problems.append(
                    Problem(
                        source,
                        child,
                        "field name uses snake_case; A2A JSON MUST use camelCase (§5.5)",
                        spec="5.5",
                    )
                )
            problems.extend(_check_camel_case(value, source, child, child_exempt))
    elif isinstance(node, list):
        for i, item in enumerate(node):
            problems.extend(_check_camel_case(item, source, f"{path}[{i}]", exempt))
    return problems


def _check_non_normative(card: dict, source: str) -> list[Problem]:
    """Guard the honesty contract on the x-omega sidecar.

    Any top-level key the spec does not define must be inside a declared
    non-normative namespace, and the sidecar must not contradict itself.
    """
    problems: list[Problem] = []

    known = {
        "name", "description", "supportedInterfaces", "provider", "version",
        "documentationUrl", "capabilities", "securitySchemes",
        "securityRequirements", "defaultInputModes", "defaultOutputModes",
        "skills", "signatures", "iconUrl",
    }
    for key in card:
        if key in known or key in NON_NORMATIVE_NAMESPACES:
            continue
        if key in V03_ABSENT_FIELDS:
            # Already reported above with the more specific v0.3 explanation.
            continue
        problems.append(
            Problem(
                source,
                key,
                "undeclared non-normative field; A2A v1.0 §5.7 says implementations "
                "SHOULD ignore unknown fields, so anything we add must live inside a "
                f"namespace ({', '.join(NON_NORMATIVE_NAMESPACES)})",
                spec="5.7",
            )
        )

    ns = card.get("x-omega")
    if not isinstance(ns, dict):
        if "x-omega" in card:
            problems.append(
                Problem(source, "x-omega", "must be an object", spec="5.7")
            )
        return problems

    if ns.get("normative") is not False:
        problems.append(
            Problem(
                source,
                "x-omega.normative",
                "non-normative sidecars must declare normative: false so no reader "
                "mistakes them for spec-defined fields",
                spec="5.7",
            )
        )

    conformance = ns.get("a2a_conformance")
    if conformance is None:
        problems.append(
            Problem(
                source,
                "x-omega.a2a_conformance",
                "missing; every Omega card must state its conformance level "
                f"explicitly (expected {CONFORMANCE_INFORMED!r})",
                spec="5.7",
            )
        )
    elif not _is_str(conformance):
        problems.append(
            Problem(
                source,
                "x-omega.a2a_conformance",
                f"must be a string, got {type(conformance).__name__}",
                spec="5.7",
            )
        )
    else:
        gaps = ns.get("conformity_gaps")
        claims = conformance.strip().lower() in COMPLIANCE_CLAIMING
        if claims and gaps:
            problems.append(
                Problem(
                    source,
                    "x-omega.a2a_conformance",
                    f"card claims {conformance!r} yet lists {len(gaps)} conformity "
                    "gap(s); a card cannot be both compliant and non-compliant",
                    spec="5.7",
                )
            )
        if claims:
            problems.append(
                Problem(
                    source,
                    "x-omega.a2a_conformance",
                    "this fleet implements no A2A method set and serves no "
                    f"{WELL_KNOWN_PATH}; a compliance claim is not supportable "
                    f"(expected {CONFORMANCE_INFORMED!r})",
                    spec="8.2",
                )
            )

    seat = ns.get("seat")
    if not isinstance(seat, dict):
        problems.append(
            Problem(source, "x-omega.seat", "missing or not an object", spec="5.7")
        )
    else:
        if not seat.get("slot"):
            problems.append(
                Problem(
                    source,
                    "x-omega.seat.slot",
                    "missing; report 'unassigned' when no slot is recorded rather "
                    "than omitting or inventing one",
                    spec="5.7",
                )
            )
    return problems


# ─────────────────────────────────────────────────────────────────────────────
# Loading
# ─────────────────────────────────────────────────────────────────────────────


def load_card(path: Path) -> tuple[Any, list[Problem]]:
    """Read one card. JSON errors are reported, never swallowed."""
    source = path.name
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [Problem(source, "<file>", f"cannot read card: {exc}")]
    try:
        return json.loads(raw), []
    except json.JSONDecodeError as exc:
        return None, [
            Problem(
                source,
                f"<line {exc.lineno} col {exc.colno}>",
                f"malformed JSON: {exc.msg}",
            )
        ]


def load_all_cards(cards_dir: Path | None = None) -> tuple[dict[str, Any], list[Problem]]:
    """Load and validate every card, plus check the fleet is complete."""
    cards_dir = cards_dir or CARDS_DIR
    problems: list[Problem] = []
    cards: dict[str, Any] = {}

    if not cards_dir.is_dir():
        return {}, [
            Problem(
                str(cards_dir),
                "<dir>",
                "agent card directory does not exist",
            )
        ]

    for seat in REQUIRED_SEATS:
        path = cards_dir / f"{seat}.json"
        if not path.is_file():
            problems.append(
                Problem(
                    path.name,
                    "<file>",
                    f"required seat card is missing; every sovereign seat in "
                    f"{REQUIRED_SEATS} must have a card",
                )
            )
            continue
        card, load_problems = load_card(path)
        problems.extend(load_problems)
        if load_problems:
            continue
        problems.extend(validate_agent_card(card, path.name))
        cards[seat] = card

    # Unexpected extras are surfaced, never deleted (M28).
    for path in sorted(cards_dir.glob("*.json")):
        seat = path.stem
        if seat not in REQUIRED_SEATS:
            problems.append(
                Problem(
                    path.name,
                    "<file>",
                    "card is not one of the sovereign seats and will be ignored by "
                    "the index (not deleted — M28)",
                    severity="warning",
                )
            )
    return cards, problems


# ─────────────────────────────────────────────────────────────────────────────
# Reporting surfaces
# ─────────────────────────────────────────────────────────────────────────────


def _skill_ids(card: dict) -> list[str]:
    return [
        s.get("id", "?")
        for s in card.get("skills", [])
        if isinstance(s, dict)
    ]


def build_capability_matrix(cards: dict[str, Any]) -> dict[str, list[str]]:
    """skill id -> seats offering it."""
    matrix: dict[str, list[str]] = {}
    for seat, card in sorted(cards.items()):
        for skill in _skill_ids(card):
            matrix.setdefault(skill, []).append(seat)
    return matrix


def render_capability_matrix(cards: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("SOVEREIGN SEAT CAPABILITY MATRIX (A2A v1.0 AgentSkill inventory)")
    lines.append("=" * 78)
    lines.append(
        f"{'seat':16} {'slot':11} {'skills':6} interfaces  conformance"
    )
    lines.append("-" * 78)
    for seat, card in sorted(cards.items()):
        ns = (card.get("x-omega") or {}) if isinstance(card, dict) else {}
        seat_meta = ns.get("seat", {}) if isinstance(ns, dict) else {}
        slot = seat_meta.get("slot", "?")
        skills = _skill_ids(card)
        ifaces = card.get("supportedInterfaces") or []
        binding = ifaces[0].get("protocolBinding", "?") if ifaces else "?"
        binding = binding.rsplit("/", 1)[-1] if _is_str(binding) else "?"
        conformance = ns.get("a2a_conformance", "?") if isinstance(ns, dict) else "?"
        lines.append(
            f"{seat:16} {str(slot):11} {len(skills):<6} "
            f"{binding:10} {conformance}"
        )
        for skill in skills:
            lines.append(f"    · {skill}")
    lines.append("-" * 78)
    lines.append("SKILL -> SEAT INDEX")
    for skill, seats in sorted(build_capability_matrix(cards).items()):
        lines.append(f"  {skill:34} {', '.join(seats)}")
    lines.append("")
    lines.append(f"NOTE: {CONFORMANCE_NOTE}")
    return "\n".join(lines)


def build_index(cards: dict[str, Any]) -> dict[str, Any]:
    """Deterministic (M8, no telemetry): byte-stable across runs.

    Deliberately contains NO wall-clock timestamp by default so the file is
    safe to keep under version control without churn. Use --stamp if you want
    provenance over diff-cleanliness.
    """
    agents = []
    for seat, card in sorted(cards.items()):
        ns = card.get("x-omega") or {}
        seat_meta = ns.get("seat", {})
        agents.append(
            {
                "seat": seat,
                "name": card.get("name"),
                "version": card.get("version"),
                "slot": seat_meta.get("slot"),
                "role": seat_meta.get("role"),
                "domains": seat_meta.get("domains", []),
                "a2a_conformance": ns.get("a2a_conformance"),
                "skills": [
                    {
                        "id": s.get("id"),
                        "name": s.get("name"),
                        "tags": s.get("tags", []),
                    }
                    for s in card.get("skills", [])
                    if isinstance(s, dict)
                ],
                "supportedInterfaces": card.get("supportedInterfaces", []),
                "capabilities": {
                    k: v
                    for k, v in (card.get("capabilities") or {}).items()
                    if k in ("streaming", "pushNotifications", "extendedAgentCard")
                },
                "hub_tools": ns.get("hub_tools", []),
                "card_file": f"config/a2a/agent_cards/{seat}.json",
                "documentation_path": ns.get("documentation_path"),
            }
        )

    return {
        "schema_version": "1.0",
        "artifact": "a2a-agent-discovery-index",
        "generated": True,
        "regenerate_with": "scripts/a2a_agent_cards.py --publish",
        "spec_reference": "https://a2a-protocol.org/latest/specification",
        "spec_version": "1.0.0",
        "registry_scope": "local-only",
        "network_calls": 0,
        "well_known_uri_template": (
            "https://{host}/" + WELL_KNOWN_PATH.strip("/")
        ),
        "well_known_served": False,
        "well_known_note": (
            "Nothing serves " + WELL_KNOWN_PATH + "; these cards are local "
            "artifacts, not a published discovery endpoint."
        ),
        "conformance": CONFORMANCE_INFORMED,
        "conformance_note": CONFORMANCE_NOTE,
        "agent_count": len(agents),
        "agents": agents,
        "capability_matrix": build_capability_matrix(cards),
    }


def render_json(cards: dict[str, Any], problems: list[Problem]) -> str:
    errors = [p for p in problems if p.severity == "error"]
    warnings = [p for p in problems if p.severity != "error"]
    return json.dumps(
        {
            "ok": not errors,
            "spec_version": "1.0.0",
            "seat_count": len(cards),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": [p.to_dict() for p in errors],
            "warnings": [p.to_dict() for p in warnings],
            "capability_matrix": build_capability_matrix(cards),
        },
        indent=2,
        sort_keys=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Publishing (M8 local-only, M28 non-clobbering)
# ─────────────────────────────────────────────────────────────────────────────


def publish(index: dict[str, Any], index_path: Path | None = None) -> Path:
    """Atomically write the discovery index. Local file only."""
    index_path = index_path or INDEX_PATH
    index_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(index, indent=2, sort_keys=True) + "\n"
    # Atomic replace: a reader never observes a half-written index (M23).
    fd, tmp_name = tempfile.mkstemp(
        dir=str(index_path.parent), prefix=".agent_index.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        # mkstemp creates 0600. A published manifest should be world-readable
        # like every other data artifact, so widen it before the atomic swap.
        os.chmod(tmp_name, 0o644)
        os.replace(tmp_name, index_path)
    except BaseException:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise
    return index_path


def _rel(path: Path) -> str:
    """Repo-relative path when possible, else absolute (tests use tmp dirs)."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def diff_index(index: dict[str, Any], index_path: Path | None = None) -> str:
    """Report drift vs the on-disk index WITHOUT writing (M28: report, not clobber)."""
    index_path = index_path or INDEX_PATH
    if not index_path.is_file():
        return f"{_rel(index_path)}: absent; --publish would create it"
    on_disk = json.loads(index_path.read_text(encoding="utf-8"))
    fresh = json.dumps(index, indent=2, sort_keys=True).splitlines()
    disk = json.dumps(on_disk, indent=2, sort_keys=True).splitlines()
    if fresh == disk:
        return f"{_rel(index_path)}: identical to freshly built index"
    import difflib

    diff = list(
        difflib.unified_diff(disk, fresh, "on-disk", "fresh", lineterm="", n=1)
    )
    return "\n".join(diff)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="a2a_agent_cards.py",
        description=(
            "Validate sovereign Agent Cards against A2A v1.0 and publish a "
            "local discovery index. Local-only; no network egress (M8)."
        ),
    )
    parser.add_argument(
        "--list", action="store_true", help="print the seat/skill capability matrix"
    )
    parser.add_argument(
        "--publish", action="store_true", help="write the local discovery index"
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="report index drift without writing (M28)",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    parser.add_argument(
        "--stamp",
        action="store_true",
        help="add a generated_at timestamp (breaks byte-determinism)",
    )
    parser.add_argument(
        "--cards-dir",
        default=None,
        help=f"override card directory (default: {_rel(CARDS_DIR)})",
    )
    parser.add_argument(
        "--index-path",
        default=None,
        help="override index output path (tests)",
    )
    args = parser.parse_args(argv)

    cards_dir = Path(args.cards_dir) if args.cards_dir else CARDS_DIR
    index_path = Path(args.index_path) if args.index_path else INDEX_PATH

    cards, problems = load_all_cards(cards_dir)
    errors = [p for p in problems if p.severity == "error"]
    warnings = [p for p in problems if p.severity != "error"]

    # --report surfaces both the verdict and the matrix.
    if args.list:
        print(render_capability_matrix(cards))
        print("")

    for problem in errors:
        print(f"ERROR  {problem}", file=sys.stderr)
    for problem in warnings:
        print(f"WARN   {problem}", file=sys.stderr)

    if errors:
        # M23: refuse to publish a manifest derived from invalid cards.
        print(
            f"\nFAILED: {len(errors)} schema violation(s) across "
            f"{_rel(cards_dir)}. "
            "No index was written. Fix the cards; this tool will not repair them (M23).",
            file=sys.stderr,
        )
        # A machine-readable surface must be able to go red too. Emitting no
        # JSON on failure would make `--json` indistinguishable from a crash,
        # which is the "reporting surface that cannot go red" defect.
        if args.json:
            print(render_json(cards, problems))
        return 1

    index = build_index(cards)
    if args.stamp:
        import datetime

        index["generated_at"] = datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat()

    if args.diff:
        print(diff_index(index, index_path))

    if args.publish:
        try:
            written = publish(index, index_path)
        except OSError as exc:
            print(f"ERROR  {index_path}: cannot write index: {exc}", file=sys.stderr)
            return 1
        print(
            f"PUBLISHED {_rel(written)} — {index['agent_count']} agents, "
            f"{len(index['capability_matrix'])} distinct skills, "
            "local-only, network_calls=0 (M8)"
        )
    elif not args.list and not args.json and not args.diff:
        print(
            f"OK: {len(cards)}/{len(REQUIRED_SEATS)} seat cards validate against "
            f"A2A v1.0 §4.4.1 ({len(warnings)} warning(s)).\n"
            f"NOTE: {CONFORMANCE_NOTE}"
        )

    if args.json:
        print(render_json(cards, problems))

    return 0


if __name__ == "__main__":
    sys.exit(main())