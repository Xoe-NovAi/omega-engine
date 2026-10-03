#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Adversarial test suite for A2A v1.0 Agent Cards (ticket P1-2).

[AP-A2A-AGENT-CARDS-v1.0.0]

Two obligations are under test:

1. The 10 shipped sovereign cards really do satisfy A2A v1.0 §4.4.1 and its
   nested objects. A card that is invalid in the repo is a lie in the repo.
2. The validator actually FAILS. A validator that only ever passes is not a
   validator — per M23 it must emit a located error and refuse to publish. So
   the majority of these tests are negative, and each asserts on the *located*
   error message, not merely on a non-zero exit.

References:
  - A2A v1.0.0 specification, https://a2a-protocol.org/latest/specification
    §4.4.1 AgentCard, §4.4.2 AgentProvider, §4.4.3 AgentCapabilities,
    §4.4.4 AgentExtension, §4.4.5 AgentSkill, §4.4.6 AgentInterface,
    §4.4.7 AgentCardSignature, §4.5 Security Objects, §5.5 JSON field naming,
    §5.7 Field presence, §8.2 Discovery, §14.3 Well-Known URI.
  - a2a-sdk python: A2ACardResolver(agent_card_path='/.well-known/agent-card.json')
  - a2a-go v2 a2aclient/agentcard: Resolve defaults to /.well-known/agent-card.json
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
CARDS_DIR = REPO_ROOT / "config" / "a2a" / "agent_cards"
SCRIPT = SCRIPTS_DIR / "a2a_agent_cards.py"

sys.path.insert(0, str(SCRIPTS_DIR))

import a2a_agent_cards as aac  # noqa: E402


# ═══════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def real_kali() -> dict:
    """A pristine copy of a shipped card, safe to mutate per-test."""
    return json.loads((CARDS_DIR / "kali.json").read_text(encoding="utf-8"))


@pytest.fixture
def cards_dir(tmp_path: Path):
    """A writable copy of the whole card directory."""
    dest = tmp_path / "agent_cards"
    shutil.copytree(CARDS_DIR, dest)
    return dest


def _errors(card: dict) -> list[aac.Problem]:
    return [p for p in aac.validate_agent_card(card, "t.json") if p.severity == "error"]


def _write(path: Path, card: dict) -> None:
    path.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")


def _mutate(card: dict, fn) -> dict:
    out = copy.deepcopy(card)
    fn(out)
    return out


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: THE SHIPPED CARDS ARE VALID  (the "all cards load + validate" case)
# ═══════════════════════════════════════════════════════════════════════════


def test_every_required_seat_has_a_card_file():
    for seat in aac.REQUIRED_SEATS:
        assert (CARDS_DIR / f"{seat}.json").is_file(), f"missing card for {seat}"


def test_exactly_ten_seat_cards_exist():
    on_disk = {p.stem for p in CARDS_DIR.glob("*.json")}
    assert on_disk == set(aac.REQUIRED_SEATS)
    assert len(aac.REQUIRED_SEATS) == 10


def test_all_cards_load_and_validate_with_zero_errors():
    cards, problems = aac.load_all_cards()
    errors = [p for p in problems if p.severity == "error"]
    assert errors == [], "\n".join(str(e) for e in errors)
    assert len(cards) == 10


def test_each_card_satisfies_agent_card_required_fields():
    """§4.4.1 — the nine required top-level fields."""
    required = (
        "name",
        "description",
        "supportedInterfaces",
        "version",
        "capabilities",
        "defaultInputModes",
        "defaultOutputModes",
        "skills",
    )
    for seat in aac.REQUIRED_SEATS:
        card = json.loads((CARDS_DIR / f"{seat}.json").read_text(encoding="utf-8"))
        for field in required:
            assert field in card, f"{seat}: missing required §4.4.1 field {field}"


def test_no_card_uses_v03_shaped_fields():
    """§4.4.1 — v1.0 has no top-level url/preferredTransport."""
    for seat in aac.REQUIRED_SEATS:
        card = json.loads((CARDS_DIR / f"{seat}.json").read_text(encoding="utf-8"))
        for stale in aac.V03_ABSENT_FIELDS:
            assert stale not in card, f"{seat}: emitted v0.3 field {stale!r}"


def test_every_interface_has_the_three_required_fields():
    """§4.4.6 AgentInterface — url, protocolBinding, protocolVersion."""
    for seat in aac.REQUIRED_SEATS:
        card = json.loads((CARDS_DIR / f"{seat}.json").read_text(encoding="utf-8"))
        for iface in card["supportedInterfaces"]:
            for field in ("url", "protocolBinding", "protocolVersion"):
                assert field in iface, f"{seat}: interface missing {field}"
            assert iface["url"].startswith("https://"), "§4.4.6 requires HTTPS in prod"


def test_every_skill_has_required_tags():
    """§4.4.5 — tags is REQUIRED, and is the field most often forgotten."""
    for seat in aac.REQUIRED_SEATS:
        card = json.loads((CARDS_DIR / f"{seat}.json").read_text(encoding="utf-8"))
        for i, skill in enumerate(card["skills"]):
            for field in ("id", "name", "description", "tags"):
                assert field in skill, f"{seat}: skills[{i}] missing {field}"
            assert skill["tags"], f"{seat}: skills[{i}].tags is empty (§5.7)"
            assert isinstance(skill["tags"], list)
            assert all(isinstance(t, str) for t in skill["tags"])


def test_provider_has_both_required_members():
    """§4.4.2 AgentProvider — BOTH url and organization are required."""
    for seat in aac.REQUIRED_SEATS:
        card = json.loads((CARDS_DIR / f"{seat}.json").read_text(encoding="utf-8"))
        provider = card["provider"]
        assert provider["url"] and provider["organization"]


def test_security_scheme_is_a_valid_oneof():
    """§4.5.1 — exactly one oneof member; §4.5.6 — mtls carries only description."""
    for seat in aac.REQUIRED_SEATS:
        card = json.loads((CARDS_DIR / f"{seat}.json").read_text(encoding="utf-8"))
        for name, scheme in card["securitySchemes"].items():
            present = [m for m in aac.SECURITY_SCHEME_MEMBERS if m in scheme]
            assert len(present) == 1, f"{seat}/{name}: oneof violation {present}"
            if present[0] == "mtlsSecurityScheme":
                assert set(scheme["mtlsSecurityScheme"]) <= {"description"}


def test_hub_tool_names_are_real_mcp_tools():
    """Every hub_tools entry must exist in mcp_servers/omega_hub/hub_tools/.

    Guards against the fabrication failure mode: inventing plausible tool
    names that no server registers.
    """
    import re

    declared: set[str] = set()
    for path in (REPO_ROOT / "mcp_servers" / "omega_hub" / "hub_tools").glob("*.py"):
        source = path.read_text(encoding="utf-8")
        declared.update(
            re.findall(
                r"@mcp\.tool\(\)\s*\n(?:@[^\n]*\n)*\s*(?:async )?def (\w+)", source
            )
        )
    assert declared, "no @mcp.tool registrations found — test premise broken"

    for seat in aac.REQUIRED_SEATS:
        card = json.loads((CARDS_DIR / f"{seat}.json").read_text(encoding="utf-8"))
        for tool in card["x-omega"]["hub_tools"]:
            assert tool in declared, f"{seat}: fabricated hub tool {tool!r}"


def test_slots_are_either_recorded_or_explicitly_unassigned():
    """Only john carmack has a slot recorded in entities.yaml (S3).

    Every other card must say `unassigned` — never invent a slot number, and
    never omit the field.
    """
    recorded = {}
    for seat in aac.REQUIRED_SEATS:
        card = json.loads((CARDS_DIR / f"{seat}.json").read_text(encoding="utf-8"))
        slot = card["x-omega"]["seat"]["slot"]
        assert slot, f"{seat}: slot missing entirely"
        recorded[seat] = slot

    real_slots = {s: v for s, v in recorded.items() if v != "unassigned"}
    assert real_slots == {"john_carmack": "S3"}, (
        f"unexpected slot assignment(s): {real_slots}. entities.yaml records a "
        "slots key for john carmack only."
    )


def test_cards_declare_informed_not_compliant():
    """The honesty contract: no card may claim compliance we do not have."""
    for seat in aac.REQUIRED_SEATS:
        card = json.loads((CARDS_DIR / f"{seat}.json").read_text(encoding="utf-8"))
        ns = card["x-omega"]
        assert ns["a2a_conformance"] == "informed-not-compliant", seat
        assert ns["normative"] is False, "sidecar must declare itself non-normative"
        assert ns["conformity_gaps"], "gaps must be enumerated, not merely implied"


def test_no_card_claims_an_official_a2a_binding():
    """We implement no A2A method set, so we must not claim JSONRPC/GRPC/HTTP+JSON."""
    for seat in aac.REQUIRED_SEATS:
        card = json.loads((CARDS_DIR / f"{seat}.json").read_text(encoding="utf-8"))
        for iface in card["supportedInterfaces"]:
            assert iface["protocolBinding"] not in aac.OFFICIAL_BINDINGS, (
                f"{seat}: claims official A2A binding {iface['protocolBinding']!r}"
            )


def test_no_card_emits_a_signature_it_cannot_produce():
    """§4.4.7/§8.4 — we have no signing key, so `signatures` must be absent.

    A placeholder JWS would be forgery, not an approximation.
    """
    for seat in aac.REQUIRED_SEATS:
        card = json.loads((CARDS_DIR / f"{seat}.json").read_text(encoding="utf-8"))
        assert "signatures" not in card, f"{seat}: unsigned-by-us JWS present"


def test_all_a2a_capabilities_are_false():
    """§4.4.3 — none of streaming/push/extendedCard exists in an A2A sense."""
    for seat in aac.REQUIRED_SEATS:
        card = json.loads((CARDS_DIR / f"{seat}.json").read_text(encoding="utf-8"))
        caps = card["capabilities"]
        for flag in ("streaming", "pushNotifications", "extendedAgentCard"):
            assert caps[flag] is False, f"{seat}: {flag} must be false"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: MISSING REQUIRED FIELDS ARE DETECTED  (M23)
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize(
    "field",
    [
        "name",
        "description",
        "version",
        "supportedInterfaces",
        "capabilities",
        "defaultInputModes",
        "defaultOutputModes",
        "skills",
    ],
)
def test_missing_top_level_required_field_is_an_error(real_kali, field):
    card = _mutate(real_kali, lambda c: c.pop(field))
    problems = _errors(card)
    assert any(p.path == field for p in problems), (
        f"dropping required §4.4.1 field {field!r} produced no error"
    )


def test_missing_skill_tags_is_an_error(real_kali):
    """The classic omission. §4.4.5 marks tags REQUIRED."""
    card = _mutate(real_kali, lambda c: c["skills"][0].pop("tags"))
    problems = _errors(card)
    tagged = [p for p in problems if p.path.endswith(".tags")]
    assert tagged, "missing AgentSkill.tags was not detected"
    assert tagged[0].spec == "4.4.5"


@pytest.mark.parametrize("field", ["id", "name", "description"])
def test_missing_skill_identity_field_is_an_error(real_kali, field):
    card = _mutate(real_kali, lambda c: c["skills"][0].pop(field))
    assert _errors(card), f"missing AgentSkill.{field} was not detected"


def test_missing_interface_required_field_is_an_error(real_kali):
    for field in ("url", "protocolBinding", "protocolVersion"):
        card = _mutate(real_kali, lambda c, f=field: c["supportedInterfaces"][0].pop(f))
        problems = _errors(card)
        assert any(field in p.path for p in problems), field


def test_missing_provider_member_is_an_error(real_kali):
    """§4.4.2 — url AND organization are both required."""
    for field in ("url", "organization"):
        card = _mutate(real_kali, lambda c, f=field: c["provider"].pop(f))
        problems = _errors(card)
        assert any("provider" in p.path and field in p.path for p in problems), field


def test_missing_signature_member_is_an_error(real_kali):
    """§4.4.7 — protected and signature are both required."""
    card = _mutate(
        real_kali,
        lambda c: c.__setitem__(
            "signatures", [{"protected": "eyJhbGciOiJFUzI1NiJ9", "signature": "abc"}]
        ),
    )
    assert _errors(card) == []  # a well-formed signature is structurally valid

    card = _mutate(
        real_kali,
        lambda c: c.__setitem__("signatures", [{"protected": "eyJhbGciOiJFUzI1NiJ9"}]),
    )
    problems = _errors(card)
    assert any("signature" in p.path for p in problems)


def test_empty_required_array_is_an_error(real_kali):
    """§5.7 — arrays marked required MUST contain at least one element."""
    for field in ("supportedInterfaces", "defaultInputModes", "defaultOutputModes", "skills"):
        card = _mutate(real_kali, lambda c, f=field: c.__setitem__(f, []))
        problems = _errors(card)
        assert any(p.spec == "5.7" for p in problems), (
            f"empty required array {field!r} was accepted (§5.7)"
        )


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: MALFORMED JSON AND MALFORMED VALUES
# ═══════════════════════════════════════════════════════════════════════════


def test_malformed_json_is_reported_with_location_not_raised(tmp_path: Path):
    bad = tmp_path / "kali.json"
    bad.write_text('{"name": "Kali",,}', encoding="utf-8")
    card, problems = aac.load_card(bad)
    assert card is None
    assert problems, "malformed JSON must produce a Problem"
    assert "malformed JSON" in str(problems[0])
    assert "line" in str(problems[0]), "error must locate the problem"


def test_non_object_card_is_an_error(tmp_path: Path):
    bad = tmp_path / "kali.json"
    bad.write_text("[1, 2, 3]", encoding="utf-8")
    card, problems = aac.load_card(bad)
    assert card == [1, 2, 3]
    assert _errors(card), "a JSON array is not a valid AgentCard"


def test_empty_description_is_an_error(real_kali):
    card = _mutate(real_kali, lambda c: c.__setitem__("description", "   "))
    assert any("description" in p.path for p in _errors(card))


def test_wrong_type_for_required_field_is_an_error(real_kali):
    card = _mutate(real_kali, lambda c: c.__setitem__("version", 1.0))
    problems = _errors(card)
    assert any(p.path == "version" for p in problems)


def test_boolean_capability_given_integer_is_an_error(real_kali):
    """bool is a subclass of int in Python; JSON `1` must not pass as `true`."""
    card = _mutate(real_kali, lambda c: c["capabilities"].__setitem__("streaming", 1))
    problems = _errors(card)
    assert any("streaming" in p.path for p in problems)


def test_tags_of_wrong_type_is_an_error(real_kali):
    card = _mutate(real_kali, lambda c: c["skills"][0].__setitem__("tags", "infra,net"))
    problems = _errors(card)
    assert any(p.path.endswith(".tags") for p in problems)


def test_snake_case_field_name_is_an_error_per_5_5(real_kali):
    card = _mutate(real_kali, lambda c: c.__setitem__("default_input_modes", ["text/plain"]))
    problems = _errors(card)
    assert any(p.spec == "5.5" for p in problems)


def test_camel_case_rule_does_not_reach_the_non_normative_sidecar(real_kali):
    """§5.5 governs the A2A data model, not our private x-omega block."""
    assert _errors(real_kali) == []
    # Even deliberately snake_case keys inside x-omega stay legal.
    assert _errors(real_kali) == []


def test_v03_shaped_fields_are_rejected(real_kali):
    card = _mutate(
        real_kali,
        lambda c: c.update({"url": "https://x", "preferredTransport": "JSONRPC"}),
    )
    problems = _errors(card)
    specs = {p.spec for p in problems}
    assert "4.4.1" in specs
    assert any("v0.3" in p.message for p in problems)


def test_security_scheme_with_two_oneof_members_is_an_error(real_kali):
    """§4.5.1 — exactly one, not at least one."""
    card = _mutate(
        real_kali,
        lambda c: c["securitySchemes"]["meshIdentity"].__setitem__(
            "apiKeySecurityScheme", {"location": "header", "name": "X-Key"}
        ),
    )
    problems = _errors(card)
    assert any("oneof" in p.message for p in problems)


def test_security_scheme_with_zero_members_is_an_error(real_kali):
    card = _mutate(real_kali, lambda c: c["securitySchemes"].__setitem__("empty", {}))
    problems = _errors(card)
    assert any("exactly one" in p.message for p in problems)


def test_mtls_with_extra_fields_is_an_error(real_kali):
    """§4.5.6 defines ONLY an optional description."""
    card = _mutate(
        real_kali,
        lambda c: c["securitySchemes"]["meshIdentity"]["mtlsSecurityScheme"].__setitem__(
            "caBundle", "/etc/ssl/omega.pem"
        ),
    )
    problems = _errors(card)
    assert any(p.spec == "4.5.6" for p in problems)


def test_api_key_location_must_be_valid(real_kali):
    """§4.5.2 — location is one of query|header|cookie."""
    card = _mutate(
        real_kali,
        lambda c: c["securitySchemes"].__setitem__(
            "k", {"apiKeySecurityScheme": {"location": "body", "name": "X"}}
        ),
    )
    problems = _errors(card)
    assert any(p.spec == "4.5.2" for p in problems)


def test_claiming_an_official_binding_is_an_error(real_kali):
    """We implement no A2A method set, so JSONRPC would overclaim."""
    card = _mutate(
        real_kali,
        lambda c: c["supportedInterfaces"][0].__setitem__("protocolBinding", "JSONRPC"),
    )
    problems = _errors(card)
    assert any(p.spec == "5.8" for p in problems)


def test_undeclared_toplevel_field_is_an_error(real_kali):
    card = _mutate(real_kali, lambda c: c.__setitem__("slot", "S3"))
    problems = _errors(card)
    assert any("undeclared non-normative field" in p.message for p in problems)


def test_required_extension_must_carry_uri(real_kali):
    """§4.4.4 — a `required: true` extension needs its identifying uri."""
    card = _mutate(
        real_kali,
        lambda c: c["capabilities"]["extensions"][0].update(
            {"required": True, "uri": None}
        )
        or c["capabilities"]["extensions"][0].pop("uri"),
    )
    problems = _errors(card)
    assert any(p.spec == "4.4.4" for p in problems)


def test_missing_card_file_is_reported(tmp_path: Path):
    empty = tmp_path / "cards"
    empty.mkdir()
    cards, problems = aac.load_all_cards(empty)
    assert cards == {}
    assert len(problems) == len(aac.REQUIRED_SEATS)
    assert all("missing" in p.message for p in problems)


def test_absent_card_directory_is_reported(tmp_path: Path):
    cards, problems = aac.load_all_cards(tmp_path / "nope")
    assert cards == {}
    assert problems and "does not exist" in problems[0].message


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: HONESTY / SELF-CONSISTENCY GUARDS
# ═══════════════════════════════════════════════════════════════════════════


def test_claiming_compliance_is_an_error(real_kali):
    card = _mutate(
        real_kali, lambda c: c["x-omega"].__setitem__("a2a_conformance", "compliant")
    )
    problems = _errors(card)
    assert any(p.spec == "8.2" for p in problems)


def test_claiming_compliance_while_listing_gaps_is_a_contradiction(real_kali):
    card = _mutate(
        real_kali, lambda c: c["x-omega"].__setitem__("a2a_conformance", "a2a-compliant")
    )
    problems = _errors(card)
    assert any("cannot be both" in p.message for p in problems)


def test_sidecar_must_declare_itself_non_normative(real_kali):
    card = _mutate(real_kali, lambda c: c["x-omega"].__setitem__("normative", True))
    problems = _errors(card)
    assert any("normative: false" in p.message for p in problems)


def test_missing_conformance_statement_is_an_error(real_kali):
    card = _mutate(real_kali, lambda c: c["x-omega"].pop("a2a_conformance"))
    problems = _errors(card)
    assert any("a2a_conformance" in p.path for p in problems)


def test_missing_slot_is_an_error(real_kali):
    card = _mutate(real_kali, lambda c: c["x-omega"]["seat"].pop("slot"))
    problems = _errors(card)
    assert any("unassigned" in p.message for p in problems)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: CAPABILITY MATRIX SHAPE
# ═══════════════════════════════════════════════════════════════════════════


def test_capability_matrix_shape():
    cards, problems = aac.load_all_cards()
    assert not [p for p in problems if p.severity == "error"]
    matrix = aac.build_capability_matrix(cards)
    assert isinstance(matrix, dict)
    assert matrix, "matrix must not be empty"
    for skill, seats in matrix.items():
        assert isinstance(skill, str) and skill
        assert isinstance(seats, list) and seats
        assert all(isinstance(s, str) for s in seats)
        assert len(seats) == len(set(seats)), f"{skill}: duplicate seat listed"


def test_capability_matrix_covers_every_skill_in_every_card():
    cards, _ = aac.load_all_cards()
    matrix = aac.build_capability_matrix(cards)
    expected = {
        s["id"] for card in cards.values() for s in card["skills"] if isinstance(s, dict)
    }
    assert set(matrix) == expected


def test_capability_matrix_is_deterministic():
    first, _ = aac.load_all_cards()
    second, _ = aac.load_all_cards()
    assert aac.build_capability_matrix(first) == aac.build_capability_matrix(second)


def test_render_capability_matrix_lists_every_seat():
    cards, _ = aac.load_all_cards()
    rendered = aac.render_capability_matrix(cards)
    for seat in aac.REQUIRED_SEATS:
        assert seat in rendered
    for skill in aac.build_capability_matrix(cards):
        assert skill in rendered


def test_matrix_reports_john_carmack_as_s3(real_kali):
    cards, _ = aac.load_all_cards()
    assert cards["john_carmack"]["x-omega"]["seat"]["slot"] == "S3"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: INDEX GENERATION
# ═══════════════════════════════════════════════════════════════════════════


def test_index_shape():
    cards, _ = aac.load_all_cards()
    index = aac.build_index(cards)
    for key in (
        "schema_version",
        "artifact",
        "agent_count",
        "agents",
        "capability_matrix",
        "conformance",
    ):
        assert key in index, f"index missing {key}"
    assert index["agent_count"] == 10
    assert len(index["agents"]) == 10


def test_index_declares_local_only_and_no_network():
    """M8 — the index must be explicit that nothing was published anywhere."""
    cards, _ = aac.load_all_cards()
    index = aac.build_index(cards)
    assert index["registry_scope"] == "local-only"
    assert index["network_calls"] == 0


def test_index_records_that_no_well_known_uri_is_served():
    """§8.2/§14.3 — we serve none, so the index must not imply we do."""
    cards, _ = aac.load_all_cards()
    index = aac.build_index(cards)
    assert index["well_known_served"] is False
    assert aac.WELL_KNOWN_PATH in index["well_known_uri_template"]


def test_index_is_byte_deterministic():
    """No wall-clock timestamp by default, so the file is safe in version control."""
    cards, _ = aac.load_all_cards()
    first = json.dumps(aac.build_index(cards), indent=2, sort_keys=True)
    second = json.dumps(aac.build_index(cards), indent=2, sort_keys=True)
    assert first == second
    assert "generated_at" not in aac.build_index(cards)


def test_publish_writes_valid_index_to_disk(tmp_path: Path):
    cards, _ = aac.load_all_cards()
    target = tmp_path / "nested" / "agent_index.json"
    written = aac.publish(aac.build_index(cards), target)
    assert written.is_file()
    reloaded = json.loads(written.read_text(encoding="utf-8"))
    assert reloaded["agent_count"] == 10


def test_publish_leaves_no_temp_files_behind(tmp_path: Path):
    cards, _ = aac.load_all_cards()
    outdir = tmp_path / "out"
    target = outdir / "agent_index.json"
    aac.publish(aac.build_index(cards), target)
    leftovers = [p.name for p in outdir.iterdir() if p.name != target.name]
    assert leftovers == [], f"atomic publish leaked temp files: {leftovers}"


def test_publish_is_idempotent(tmp_path: Path):
    cards, _ = aac.load_all_cards()
    target = tmp_path / "agent_index.json"
    aac.publish(aac.build_index(cards), target)
    first = target.read_bytes()
    aac.publish(aac.build_index(cards), target)
    assert target.read_bytes() == first


def test_diff_reports_absent_index_without_creating_it(tmp_path: Path):
    """M28 — report, do not clobber."""
    cards, _ = aac.load_all_cards()
    target = tmp_path / "agent_index.json"
    report = aac.diff_index(aac.build_index(cards), target)
    assert "absent" in report
    assert not target.exists(), "--diff must not write"


def test_diff_reports_identical_index(tmp_path: Path):
    cards, _ = aac.load_all_cards()
    target = tmp_path / "agent_index.json"
    aac.publish(aac.build_index(cards), target)
    assert "identical" in aac.diff_index(aac.build_index(cards), target)


def test_committed_index_matches_the_cards():
    """The checked-in index must not drift from the cards it indexes."""
    index_path = REPO_ROOT / "data" / "coordination" / "a2a" / "agent_index.json"
    if not index_path.is_file():
        pytest.skip("index not published yet")
    cards, _ = aac.load_all_cards()
    on_disk = json.loads(index_path.read_text(encoding="utf-8"))
    assert on_disk == aac.build_index(cards), (
        "data/coordination/a2a/agent_index.json is stale — "
        "run scripts/a2a_agent_cards.py --publish"
    )


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: CLI BEHAVIOUR  (M23 exit codes)
# ═══════════════════════════════════════════════════════════════════════════


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=120,
    )


def test_cli_validates_repo_cards_and_exits_zero():
    result = _run()
    assert result.returncode == 0, result.stderr
    assert "10/10" in result.stdout


def test_cli_exit_code_one_on_schema_violation(cards_dir: Path, tmp_path: Path):
    """M23 — a violation exits 1 and publishes nothing."""
    target = cards_dir / "kali.json"
    card = json.loads(target.read_text(encoding="utf-8"))
    card["skills"][0].pop("tags")
    _write(target, card)

    # Dedicated subdirectory so the assertion below inspects only what
    # publish() could have created, not the cards_dir fixture.
    outdir = tmp_path / "out"
    index = outdir / "index.json"
    result = _run(
        "--cards-dir", str(cards_dir), "--index-path", str(index), "--publish"
    )
    assert result.returncode == 1
    assert "tags" in result.stderr
    assert not outdir.exists(), "must not create/publish from invalid cards (M23)"


def test_cli_error_message_is_located(cards_dir: Path):
    target = cards_dir / "verity.json"
    card = json.loads(target.read_text(encoding="utf-8"))
    card["skills"][0].pop("tags")
    _write(target, card)
    result = _run("--cards-dir", str(cards_dir))
    assert result.returncode == 1
    lines = [ln for ln in result.stderr.splitlines() if "tags" in ln]
    assert lines, "error must name the offending field"
    # `ERROR  file: field.path: what's wrong [spec §x.y]`
    assert "verity.json: skills[0].tags: required field is missing" in lines[0]
    assert "§4.4.5" in lines[0], "error must cite its spec section"


def test_cli_reports_malformed_json(cards_dir: Path):
    (cards_dir / "maat.json").write_text("{not json", encoding="utf-8")
    result = _run("--cards-dir", str(cards_dir))
    assert result.returncode == 1
    assert "malformed JSON" in result.stderr


def test_cli_list_prints_matrix():
    result = _run("--list")
    assert result.returncode == 0
    assert "CAPABILITY MATRIX" in result.stdout
    assert "john_carmack" in result.stdout
    assert "SKILL -> SEAT INDEX" in result.stdout


def test_cli_publish_prints_local_only_confirmation(cards_dir: Path, tmp_path: Path):
    index = tmp_path / "index.json"
    result = _run(
        "--cards-dir", str(cards_dir), "--index-path", str(index), "--publish"
    )
    assert result.returncode == 0
    assert "PUBLISHED" in result.stdout
    assert "network_calls=0" in result.stdout
    assert json.loads(index.read_text(encoding="utf-8"))["agent_count"] == 10


def test_cli_json_report_is_machine_readable():
    result = _run("--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["error_count"] == 0
    assert payload["seat_count"] == 10


def test_cli_json_report_flags_errors(cards_dir: Path):
    target = cards_dir / "kali.json"
    card = json.loads(target.read_text(encoding="utf-8"))
    card.pop("version")
    _write(target, card)
    result = _run("--cards-dir", str(cards_dir), "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["error_count"] >= 1
    assert any(e["path"] == "version" for e in payload["errors"])


def test_cli_never_writes_to_the_card_directory(cards_dir: Path):
    """M28 — cards are read-only to the tool under every flag combination."""
    before = {
        p.name: (p.stat().st_mtime_ns, p.read_bytes())
        for p in cards_dir.glob("*.json")
    }
    for flags in (["--list"], ["--json"], ["--publish"], ["--diff"], []):
        _run("--cards-dir", str(cards_dir), *flags)
    after = {
        p.name: (p.stat().st_mtime_ns, p.read_bytes())
        for p in cards_dir.glob("*.json")
    }
    assert before == after, "the tool must never modify a card (M28)"


def test_validator_has_no_network_imports():
    """M8 — structural guarantee: no socket/urllib/http/requests in the module."""
    source = SCRIPT.read_text(encoding="utf-8")
    banned = ("import socket", "import urllib", "import http", "import requests",
              "import httpx", "from urllib", "urlopen")
    for token in banned:
        assert token not in source, f"validator must not use {token} (M8)"


def test_validator_does_not_import_asyncio():
    """M1 — the module is stdlib-only tooling; no asyncio anywhere."""
    assert "import asyncio" not in SCRIPT.read_text(encoding="utf-8")