# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Regression guard for MCP protocol-version drift (P0-1 knowledge-gap).

The Hub's protocol identity is declared exactly once, in
``mcp_servers/omega_hub/protocol_version.py``. Before this guard,
``mcp_client.py`` documented 2026-07-28 while the federation probe still
POSTed ``"protocolVersion":"2024-11-05"`` — and the probe reported PASS
because the endpoint answered HTTP 200, not because the version was right.

These tests walk the AST of every module in ``mcp_servers/omega_hub/`` and
fail on any protocol-version *string literal* outside the canonical module.
AST rather than grep, deliberately:

* comments are not in the AST, so the many ``# SEP-2575 (MCP 2026-07-28)``
  provenance notes that must stay for M14 heritage do not trip the guard;
* docstrings are excluded explicitly, so narrative documentation of the spec
  date remains legal while an executable literal does not;
* a version smuggled into a dict, a call arg, or a default is still caught.

M1 AnyIO: pure AST + filesystem work, no async runtime, no ``asyncio``.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

HUB_DIR = Path(__file__).resolve().parents[2] / "mcp_servers" / "omega_hub"
CANONICAL = HUB_DIR / "protocol_version.py"

# An MCP protocol version is a bare ISO-like date: 2024-11-05, 2025-11-25.
PROTOCOL_VERSION_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# A protocol version EMBEDDED in a serialized payload. The original drift was
# not a bare literal at all — it sat inside a concatenated JSON fragment:
#     '"params":{"protocolVersion":"2024-11-05","capabilities":{},'
# so an anchored whole-string regex reports nothing and the guard silently
# passes the exact bug it was written to catch. Any string constant that
# mentions a protocolVersion key AND contains a date is a violation.
EMBEDDED_PROTOCOL_VERSION_RE = re.compile(
    r"protocolversion", re.IGNORECASE)
DATE_ANYWHERE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

# The MCP protocol revision lineage. A date-shaped literal matching one of
# these is a protocol version wherever it appears.
#
# This list alone would be insufficient — it cannot anticipate the next
# revision — so it is combined with the context rules in
# _ProtocolLiteralVisitor: a date literal also counts when bound to a
# PROTOCOL-named symbol, used as the value of a ``protocolVersion`` mapping
# key, or equal to the canonical version. A date literal that is none of
# these (e.g. ``SCOPE_ALL_REMOVAL_DATE = "2026-12-31"``) is not a protocol
# version and must not fail the build.
KNOWN_PROTOCOL_VERSIONS = frozenset({
    "2024-11-05",  # superseded — the value this guard was written to catch
    "2025-03-26",
    "2025-06-18",
    "2025-11-25",
    "2026-07-28",
})

CANONICAL_VERSION = "2026-07-28"


class _ProtocolLiteralVisitor(ast.NodeVisitor):
    """Collect date-shaped strings that are used AS protocol versions.

    Tracks enclosing assignment target and dict keys so a bare ISO date bound
    to an unrelated name (``SCOPE_ALL_REMOVAL_DATE``) is not misread as a
    protocol version, while a future ``PROTOCOL_VERSION = "2027-01-01"`` is
    still caught even though it is not in KNOWN_PROTOCOL_VERSIONS.
    """

    def __init__(self, docstrings: set[int] | None = None) -> None:
        self.found: list[tuple[int, str]] = []
        self._docstrings: set[int] = docstrings or set()
        self._assign_target: str = ""
        self._dict_keys: set[str] = set()

    # -- context tracking ---------------------------------------------------
    def visit_Assign(self, node: ast.Assign) -> None:
        target = next((t.id for t in node.targets if isinstance(t, ast.Name)), "")
        previous, self._assign_target = self._assign_target, target
        self.visit(node.value)
        self._assign_target = previous

    def visit_Dict(self, node: ast.Dict) -> None:
        keys = {k.value for k in node.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)}
        previous, self._dict_keys = self._dict_keys, keys
        for value in node.values:
            self.visit(value)
        self._dict_keys = previous

    def visit_Constant(self, node: ast.Constant) -> None:
        if not isinstance(node.value, str):
            return
        # Documentation is not a protocol assertion. Comments never reach the
        # AST at all; docstrings do, and are excluded here by identity.
        if id(node) in self._docstrings:
            return
        text = node.value

        # Rule A — version embedded in a serialized payload. Unconditional:
        # naming a protocolVersion key and a date in one string is a protocol
        # assertion regardless of where it sits.
        if EMBEDDED_PROTOCOL_VERSION_RE.search(text):
            for date in DATE_ANYWHERE_RE.findall(text):
                self.found.append((node.lineno, date))
            return

        if not PROTOCOL_VERSION_RE.match(text):
            return

        # Rules B–E: bare date literal in protocol context.
        in_protocol_context = (
            text in KNOWN_PROTOCOL_VERSIONS          # known MCP revision
            or text == CANONICAL_VERSION             # our own version, verbatim
            or "PROTOCOL" in self._assign_target.upper()
            or "protocolversion" in {k.lower() for k in self._dict_keys}
        )
        if in_protocol_context:
            self.found.append((node.lineno, text))


def _docstring_nodes(tree: ast.AST) -> set[int]:
    """Return id() of every node that is a docstring Constant.

    Covers module, class and function docstrings — the only bare-Constant
    strings that are documentation rather than data.
    """
    ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef,
                             ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and \
                    isinstance(body[0].value, ast.Constant) and \
                    isinstance(body[0].value.value, str):
                ids.add(id(body[0].value))
    return ids


def _protocol_literals(path: Path) -> list[tuple[int, str]]:
    """Return (lineno, value) for each protocol-version literal in ``path``."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    visitor = _ProtocolLiteralVisitor(_docstring_nodes(tree))
    visitor.visit(tree)
    return visitor.found


def _hub_modules() -> list[Path]:
    assert HUB_DIR.is_dir(), f"hub package not found at {HUB_DIR}"
    return sorted(p for p in HUB_DIR.rglob("*.py") if "__pycache__" not in p.parts)


# ── the guard ────────────────────────────────────────────────────────────────

def test_no_protocol_version_literal_outside_canonical_module() -> None:
    """No hub module may inline a protocol version; import the constant."""
    assert CANONICAL.is_file(), (
        f"canonical protocol constant missing: {CANONICAL}. The Hub's MCP "
        "protocol identity must be declared in exactly one place."
    )
    offenders: list[str] = []
    for module in _hub_modules():
        if module == CANONICAL:
            continue
        for lineno, value in _protocol_literals(module):
            offenders.append(f"{module.relative_to(HUB_DIR.parent.parent)}:{lineno}: {value!r}")
    assert not offenders, (
        "MCP protocol version hardcoded outside "
        f"{CANONICAL.relative_to(HUB_DIR.parent.parent)}:\n  "
        + "\n  ".join(offenders)
        + "\nImport PROTOCOL_VERSION from mcp_servers.omega_hub.protocol_version."
    )


def test_canonical_module_is_the_only_definer() -> None:
    """The canonical module still declares the version we expect."""
    tree = ast.parse(CANONICAL.read_text(encoding="utf-8"), filename=str(CANONICAL))
    assigned = {
        t.id: node.value.value
        for node in tree.body if isinstance(node, ast.Assign)
        for t in node.targets if isinstance(t, ast.Name)
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
    }
    assert assigned.get("PROTOCOL_VERSION") == CANONICAL_VERSION, (
        "PROTOCOL_VERSION changed without updating this guard — a protocol "
        "revision is a deliberate act, not a side effect of a refactor. "
        f"Expected {CANONICAL_VERSION}, found {assigned.get('PROTOCOL_VERSION')!r}."
    )


def test_client_and_probe_import_the_shared_constant() -> None:
    """Both the client and the federation probe read the one constant.

    Guards the actual P0-1 regression: two call sites that each believed they
    knew the protocol version. An import can be aliased, so match the module
    path rather than the symbol name.
    """
    consumers = [
        HUB_DIR / "mcp_client.py",
        HUB_DIR / "hub_tools" / "federation.py",
    ]
    for module in consumers:
        assert module.is_file(), f"expected consumer missing: {module}"
        tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
        imported = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and \
                    (node.module or "").endswith("protocol_version"):
                imported = True
        assert imported, (
            f"{module.name} must import from "
            "mcp_servers.omega_hub.protocol_version rather than naming a "
            "version of its own."
        )


def test_probe_is_stateless_and_carries_identity_in_meta() -> None:
    """The federation probe uses tools/list, not the removed initialize.

    SEP-2575 removed initialize/initialized in MCP 2026-07-28; a live probe
    still calling it reports on a method the spec no longer defines.
    """
    source = (HUB_DIR / "hub_tools" / "federation.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    probe_methods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if isinstance(key, ast.Constant) and key.value == "method" and \
                        isinstance(key.value, str):
                    sibling = [k.value for k in node.keys
                               if isinstance(k, ast.Constant)]
                    for v in node.values:
                        if isinstance(v, ast.Constant) and isinstance(v.value, str):
                            probe_methods.add(v.value)
    assert "initialize" not in probe_methods, (
        "federation probe still sends the removed `initialize` method; "
        "SEP-2575 replaced it with stateless calls."
    )
    assert "tools/list" in probe_methods, (
        "federation probe should use the stateless tools/list call"
    )
    # Identity travels in the SEP-2575 _meta envelope, never a bare literal.
    assert '"protocolVersion": "2024-11-05"' not in source
    assert "_meta" in source, "probe must carry identity in the _meta envelope"


@pytest.mark.parametrize("version", ["2024-11-05", "2025-03-26", "2025-06-18"])
def test_known_stale_versions_are_absent(version: str) -> None:
    """No executable literal may reintroduce a superseded version."""
    for module in _hub_modules():
        if module == CANONICAL:
            continue
        assert version not in [v for _, v in _protocol_literals(module)], (
            f"{module.name} reintroduces superseded protocol version {version}"
        )