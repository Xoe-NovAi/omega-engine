# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""Adversarial tests for the protocol interpreter (ADR-001).

The design rests on two claims that must be falsifiable:

  1. The interpreter refuses rather than inventing defaults.
  2. The engine surface stays at six verbs — complexity belongs in data.

Each test below is a sabotage: it constructs a condition a naive implementation
would accept and asserts the interpreter does not.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from mcp_servers.omega_hub.federation_protocol import (  # noqa: E402
    ProtocolMalformed,
    ProtocolViolation,
    check_transition,
    inbox_dir,
    legal_targets,
    load_protocol,
    receipt_fields,
    surface,
    validate,
)

PROTOCOL = REPO_ROOT / "config/wads/_omega_default/protocol/hivemind.yaml"


@pytest.fixture(scope="module")
def proto():
    return load_protocol(PROTOCOL)


def _msg(**over):
    m = {
        "message_id": "ho_abc12345",
        "source_channel": "opencode",
        "source_agent": "ge-n1",
        "source_instance": "ge-n1",
        "source_node": "node1",  # GE-N1 runs on Node 1 — suffix and node must agree
        "target_entity": "ge-n1",
        "requested_target": "ge-n1",
        "resolved_target": "ge-n1",
        "subject": "test",
        "created_at": "2026-09-30T00:00:00+00:00",
    }
    m.update(over)
    return m


# ── verb 1: refuse, never default ────────────────────────────────────────────


def test_missing_protocol_refuses_loudly(tmp_path):
    """A missing protocol is NOT an empty protocol."""
    with pytest.raises(ProtocolMalformed):
        load_protocol(tmp_path / "absent.yaml")


def test_malformed_yaml_refuses_loudly(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("protocol: [unclosed\n", encoding="utf-8")
    with pytest.raises(ProtocolMalformed):
        load_protocol(bad)


@pytest.mark.parametrize(
    "body",
    [
        "name: x\n",                          # no version
        "version: 1\n",                       # no name
        "protocol:\n  name: x\n  version: one\n",  # version not an int
        "something_else: true\n",             # no protocol block
    ],
)
def test_incomplete_declarations_refuse(tmp_path, body):
    f = tmp_path / "p.yaml"
    f.write_text(body, encoding="utf-8")
    with pytest.raises(ProtocolMalformed):
        load_protocol(f)


def test_transition_to_undeclared_state_is_caught_at_load(tmp_path):
    """A typo in the data must surface at load, not as a mystery later."""
    f = tmp_path / "p.yaml"
    f.write_text(
        "protocol:\n  name: t\n  version: 1\n"
        "schema:\n  required: [a]\nlifecycle:\n  initial: pending\n"
        "  states:\n    pending: {}\n    done: {}\n"
        "  transitions:\n    pending: [nowhere]\n",
        encoding="utf-8",
    )
    with pytest.raises(ProtocolMalformed, match="undeclared state"):
        load_protocol(f)


def test_initial_state_must_be_declared(tmp_path):
    f = tmp_path / "p.yaml"
    f.write_text(
        "protocol:\n  name: t\n  version: 1\n"
        "schema:\n  required: [a]\nlifecycle:\n  initial: ghost\n"
        "  states:\n    pending: {}\n  transitions:\n    pending: []\n",
        encoding="utf-8",
    )
    with pytest.raises(ProtocolMalformed):
        load_protocol(f)


# ── verb 2: the request/resolved distinction IS the point ───────────────────


def test_valid_message_has_no_problems(proto):
    assert validate(proto, _msg()) == []


def test_missing_required_field_is_reported(proto):
    m = _msg()
    del m["requested_target"]
    problems = validate(proto, m)
    assert any("requested_target" in p for p in problems)


def test_requested_and_resolved_are_both_required(proto):
    """Removing EITHER must fail. This is the whole ADR-001 premise."""
    for field in ("requested_target", "resolved_target"):
        m = _msg()
        del m[field]
        assert validate(proto, m), f"{field} must be required"


def test_separator_equivalence_is_accepted(proto):
    """ge_n1 and ge-n1 are the SAME name, so the fold is legitimate here."""
    assert validate(proto, _msg(requested_target="ge_n1", resolved_target="ge-n1")) == []


def test_node_suffix_fold_is_REFUSED(proto):
    """makali-n0 and makali are DISTINCT registered agents.

    This is the deployed heuristic GE-N0 measured and found wrong. The schema
    must refuse it rather than accept a silently lossy resolution.
    """
    problems = validate(
        proto, _msg(requested_target="makali-n0", resolved_target="makali")
    )
    assert problems, "the node-suffix fold must be refused"
    assert any("canonical form" in p for p in problems)


def test_case_is_normalised(proto):
    assert validate(proto, _msg(requested_target="GE-N1", resolved_target="ge-n1")) == []


def test_bad_message_id_pattern_is_rejected(proto):
    problems = validate(proto, _msg(message_id="not-an-id"))
    assert any("message_id" in p for p in problems)


def test_undeclared_state_is_rejected(proto):
    problems = validate(proto, _msg(state="teleported"))
    assert any("undeclared state" in p for p in problems)


# ── verb 5: lifecycle is a declared table, never widened at runtime ──────────


@pytest.mark.parametrize(
    "src,dst", [("pending", "active"), ("pending", "rejected"), ("stale", "active")]
)
def test_declared_transitions_are_allowed(proto, src, dst):
    check_transition(proto, src, dst)  # must not raise


@pytest.mark.parametrize(
    "src,dst",
    [
        ("pending", "completed"),   # must go through active
        ("completed", "active"),    # completed is terminal
        ("retired", "pending"),     # nothing leaves retired (M29)
        ("cold", "active"),         # cold is terminal
    ],
)
def test_illegal_transitions_are_refused(proto, src, dst):
    with pytest.raises(ProtocolViolation):
        check_transition(proto, src, dst)


def test_unknown_state_refused_rather_than_defaulted(proto):
    with pytest.raises(ProtocolViolation):
        check_transition(proto, "imaginary", "pending")


def test_retired_is_terminal_per_the_declaration(proto):
    assert legal_targets(proto, "retired") == []


# ── the six-verb cap ─────────────────────────────────────────────────────────


def test_surface_is_six_verbs():
    """A gate elsewhere asserts this too. If a verb is added, BOTH must change —
    which is the point: adding engine surface requires an intentional act."""
    assert len(surface()) == 6


def test_inbox_name_is_human_readable(proto):
    """'pending' tells an operator what the directory is for. 'envelopes' did not."""
    assert inbox_dir(proto) == "pending"


def test_receipt_fields_are_declared(proto):
    fields = receipt_fields(proto)
    assert "resolved_target" in fields
    assert "session_id" in fields


def test_retention_is_never_automatic(proto):
    """M29: retention is a query, never an automatic deletion."""
    assert proto.raw["retention"]["auto_delete"] is False
    assert proto.retention_days("cold") is None
    assert proto.retention_days("retired") is None
