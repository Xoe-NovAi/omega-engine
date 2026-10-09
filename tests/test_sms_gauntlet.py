"""Unit tests for the SMS gauntlet instrumentation added in phase 2.

Read-only and offline: no Ollama, no network, no dataset access. They pin the
behaviour the phase-2 report depends on — echo metrics, the failure-probe
injections, flat-contract scoring and the paraphrase rewriter's label guard.

Run:  .venv/bin/python3 -m unittest discover -s tests
"""

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.sms import gauntlet  # noqa: E402
from scripts.sms.decomposition import build_derived, roles as droles  # noqa: E402
from scripts.sms.paraphrase_probe import build_variants, split_fields  # noqa: E402
from scripts.sms.scoring import echo, provenance  # noqa: E402

SCHEMA = {
    "type": "object",
    "required": ["action", "superseded_by"],
    "additionalProperties": False,
    "properties": {"action": {"enum": ["keep", "supersede"]}, "superseded_by": {"type": ["string", "null"]}},
}


class TestEchoMetrics(unittest.TestCase):
    def test_empty_group_is_not_suspect(self):
        m = echo.echo_metrics([])
        self.assertEqual(m["n"], 0)
        self.assertFalse(m["copy_suspect"])

    def test_uniform_outputs_trip_the_alarm(self):
        rows = ['{"action": "keep"}'] * 10
        m = echo.echo_metrics(rows)
        self.assertEqual(m["distinct_output_ratio"], 0.1)
        self.assertEqual(m["modal_output_share"], 1.0)
        self.assertEqual(m["copy_suspect_n"], 10)
        self.assertTrue(m["copy_suspect"])

    def test_all_distinct_never_trips(self):
        m = echo.echo_metrics([f'{{"n": {i}}}' for i in range(12)])
        self.assertEqual(m["distinct_output_ratio"], 1.0)
        self.assertFalse(m["copy_suspect"])

    def test_small_n_is_not_flagged(self):
        """n < 8 is too noisy to accuse; the ratio still reports."""
        m = echo.echo_metrics(['{"a": 1}'] * 4)
        self.assertEqual(m["modal_output_share"], 1.0)
        self.assertFalse(m["copy_suspect"])

    def test_normalization_collapses_surface_form_only(self):
        same = ['{"a": 1, "b": 2}', '{"b":2,"a":1}', '  {"a":1,"b":2}  ']
        m = echo.echo_metrics(same)
        self.assertEqual(m["distinct_outputs"], 1)
        different = echo.echo_metrics(['{"a": 1}', '{"a": 2}'])
        self.assertEqual(different["distinct_outputs"], 2)

    def test_non_string_output_does_not_raise(self):
        m = echo.echo_metrics([None, "", "\u0000"])
        self.assertEqual(m["n"], 3)


class TestFailureInjection(unittest.TestCase):
    def test_auto_cycle_covers_every_mode(self):
        cycle = {gauntlet.injection_for("auto", i) for i in range(len(gauntlet.AUTO_INJECTION_CYCLE) * 3)}
        self.assertEqual(cycle, set(gauntlet.INJECTION_MODES))

    def test_truncate_breaks_json(self):
        raw = '{"action": "keep", "superseded_by": null}'
        out, note = gauntlet.apply_injection("truncate", raw, SCHEMA, 0)
        self.assertNotEqual(out, raw)
        self.assertTrue(note)
        self.assertFalse(gauntlet.json_schema.parse_json(out)[1])

    def test_malformed_json_is_rejected_by_the_parser(self):
        for i in range(len(gauntlet.MALFORMED_SAMPLES)):
            out, _ = gauntlet.apply_injection("malformed_json", '{"action":"keep"}', SCHEMA, i)
            self.assertFalse(gauntlet.json_schema.parse_json(out)[1], out)

    def test_schema_violation_drops_a_required_key(self):
        out, note = gauntlet.apply_injection(
            "schema_violation", '{"action": "keep", "superseded_by": null}', SCHEMA, 0)
        obj, valid = gauntlet.json_schema.parse_json(out)
        self.assertTrue(valid)
        self.assertFalse(gauntlet.json_schema.validate_schema(obj, SCHEMA)[0])
        self.assertIn("action", note)

    def test_none_injection_is_a_passthrough(self):
        raw = '{"action": "keep", "superseded_by": null}'
        out, note = gauntlet.apply_injection("none", raw, SCHEMA, 3)
        self.assertEqual(out, raw)
        self.assertEqual(note, "")

    def test_timeout_injection_never_touches_the_output(self):
        raw = '{"action": "keep", "superseded_by": null}'
        out, note = gauntlet.apply_injection("timeout", raw, SCHEMA, 0)
        self.assertEqual(out, raw)
        self.assertEqual(note, "")


class TestFailureClassFor(unittest.TestCase):
    def test_precedence(self):
        self.assertEqual(gauntlet.failure_class_for(True, True, True), "latency_spike")
        self.assertEqual(gauntlet.failure_class_for(False, True, False), "parse_failure")
        self.assertEqual(gauntlet.failure_class_for(True, False, False), "schema_violation")
        self.assertEqual(gauntlet.failure_class_for(True, True, False), "ok")

    def test_timeout_message_is_recognised(self):
        err = "request timed out after 0.05s"
        self.assertIn("timed out", err.lower())


class TestDecompositionSchemas(unittest.TestCase):
    def test_every_flat_role_has_a_flat_closed_schema(self):
        schema_dir = REPO / "scripts" / "sms" / "decomposition" / "schemas"
        for role in droles.DECOMPOSITION_ROLES:
            path = schema_dir / f"{role}.schema.json"
            self.assertTrue(path.exists(), role)
            schema = json.loads(path.read_text())
            self.assertIs(schema["additionalProperties"], False, role)
            self.assertNotIn("items", schema["properties"], role)
            self.assertNotIn("provenance", schema["properties"], role)
            self.assertNotIn("pii_found", schema["properties"], role)
            self.assertLessEqual(len(schema["properties"]), 2, role)

    def test_place_classifier_rejects_nesting_and_extras(self):
        schema = json.loads((REPO / "scripts/sms/decomposition/schemas/place_classifier.schema.json").read_text())
        self.assertFalse(gauntlet.json_schema.validate_schema({"wing": "w", "room": "r", "items": []}, schema)[0])
        self.assertTrue(gauntlet.json_schema.validate_schema({"wing": "w", "room": "r"}, schema)[0])

    def test_every_flat_role_has_a_prompt(self):
        for role in droles.DECOMPOSITION_ROLES:
            self.assertIn(role, droles.SYSTEM)
            self.assertTrue(droles.SYSTEM[role].strip())


class TestDecompositionScoring(unittest.TestCase):
    def test_place_classifier_exact_is_mean_of_two_fields(self):
        gold = {"wing": "w", "room": "r"}
        self.assertEqual(droles.score_case("place_classifier", {"wing": "w", "room": "r"}, gold, {})["exact_match"], 1.0)
        self.assertEqual(droles.score_case("place_classifier", {"wing": "w", "room": "x"}, gold, {})["exact_match"], 0.5)

    def test_pii_action_scoring(self):
        self.assertEqual(droles.score_case("pii_action", {"action": "redact"}, {"action": "redact"}, {})["exact_match"], 1.0)
        self.assertEqual(droles.score_case("pii_action", {"action": "drop"}, {"action": "allow"}, {})["exact_match"], 0.0)

    def test_supersede_shape_rule_is_not_softened(self):
        case = {"input": "x"}
        good = droles.score_case("supersede_decider",
                                 {"action": "supersede", "superseded_by": "abc"},
                                 {"action": "supersede", "superseded_by": "abc"}, case)
        self.assertEqual(good["supersession_shape_ok"], 1.0)
        bad = droles.score_case("supersede_decider",
                                {"action": "supersede", "superseded_by": None},
                                {"action": "supersede", "superseded_by": "abc"}, case)
        self.assertEqual(bad["supersession_shape_ok"], 0.0)
        leaked = droles.score_case("supersede_decider",
                                   {"action": "keep", "superseded_by": "abc"},
                                   {"action": "keep", "superseded_by": None}, case)
        self.assertEqual(leaked["supersession_shape_ok"], 0.0)

    def test_quote_grounding_uses_the_shared_extractor_rule(self):
        case = {"input": "alpha beta gamma"}
        grounded = droles.score_case("quote_extractor", {"content": "b", "source_quote": "beta gamma"}, {}, case)
        self.assertEqual(grounded["quote_grounded"], 1.0)
        invented = droles.score_case("quote_extractor", {"content": "b", "source_quote": "delta"}, {}, case)
        self.assertEqual(invented["quote_grounded"], 0.0)
        self.assertEqual(
            provenance.source_quote_grounded({"items": [{"source_quote": "beta"}]}, "alpha beta"), True)


class TestDerivedProjection(unittest.TestCase):
    def test_place_projection_keeps_only_wing_and_room(self):
        row = {"role": "mempalace_extractor", "case_id": "ex_real_x", "input": "w", "tags": [],
               "source_file": "s", "source_group": "g", "recorded_at": "t",
               "gold": {"wing": "W", "room": "R", "items": [{"content": "c", "source_quote": "w"}],
                        "provenance": {"source_file": "s"}}}
        out = build_derived.derive_place(row)
        self.assertEqual(out["gold"], {"wing": "W", "room": "R"})
        self.assertEqual(out["role"], "place_classifier")

    def test_quote_projection_drops_ungroundable_labels(self):
        row = {"role": "mempalace_extractor", "case_id": "ex_real_x", "input": "window text", "tags": [],
               "source_file": "s", "source_group": "g", "recorded_at": "t",
               "gold": {"wing": "W", "room": "R",
                        "items": [{"content": "c", "source_quote": "NOT IN WINDOW"}]}}
        self.assertIsNone(build_derived.derive_quote(row))

    def test_quote_projection_keeps_grounded_labels(self):
        row = {"role": "mempalace_extractor", "case_id": "ex_real_x", "input": "window text", "tags": [],
               "source_file": "s", "source_group": "g", "recorded_at": "t",
               "gold": {"wing": "W", "room": "R", "items": [{"content": "c", "source_quote": "window"}]}}
        self.assertEqual(build_derived.derive_quote(row)["gold"],
                         {"content": "c", "source_quote": "window"})

    def test_supersede_projection_excludes_merge_and_drop(self):
        base = {"role": "well_curator", "case_id": "wc_real_x", "input": "chain records you can see: a",
                "tags": [], "source_file": "s", "source_group": "g", "recorded_at": "t"}
        for action in ("merge", "drop"):
            row = dict(base, gold={"action": action, "superseded_by": None})
            self.assertIsNone(build_derived.derive_supersede(row))
        keep = dict(base, gold={"action": "keep", "superseded_by": "stale"})
        self.assertEqual(build_derived.derive_supersede(keep)["gold"]["superseded_by"], None)
        sup = dict(base, gold={"action": "supersede", "superseded_by": None})
        self.assertIsNone(build_derived.derive_supersede(sup))

    def test_pii_projection_hands_the_spans_in(self):
        row = {"role": "privacy_sentinel", "case_id": "ps_real_x", "input": "text", "tags": [],
               "source_file": "s", "source_group": "g", "recorded_at": "t",
               "gold": {"pii_found": [{"type": "api_key", "span": "sk-X"}], "action": "redact",
                        "redacted_text": None}}
        out = build_derived.derive_pii(row)
        self.assertEqual(out["gold"], {"action": "redact"})
        self.assertIn("api_key=sk-X", out["context_fields"]["spans_found"])


class TestParaphraseProbe(unittest.TestCase):
    CASE = {
        "case_id": "wc_real_1",
        "input": (
            "Triage this Well record.\n"
            "record: aaaaaaaa-1111-2222-3333-444444444444\n"
            "trigger: the operator asks about the thing\n"
            "rule: always use the mask\n"
            "why: because it is faster\n"
            "lifecycle: retired. this record is superseded by a newer record in the same chain.\n"
            "chain records you can see: bbbbbbbb-1111-2222-3333-444444444444 @ 2026-01-02T00:00:00Z "
            "[successor]; aaaaaaaa-1111-2222-3333-444444444444 @ 2026-01-01T00:00:00Z\n"
            "kind, domain and tags are NOT given. Infer them."
        ),
        "gold": {"kind": "correction", "domain": "harness", "tags": ["x"], "action": "supersede",
                 "superseded_by": "bbbbbbbb-1111-2222-3333-444444444444", "rationale": "r"},
    }

    def test_fields_split_excludes_chain_and_closing_lines(self):
        fields = split_fields(self.CASE["input"])
        self.assertEqual(set(fields), {"trigger", "rule", "why", "lifecycle"})
        # The chain evidence must not be swallowed into the lifecycle value —
        # that duplication is what produced a doubled chain line in an early draft.
        self.assertNotIn("bbbbbbbb-1111-2222-3333-444444444444", fields["lifecycle"])
        self.assertNotIn("2026-01-02T00:00:00Z", fields["lifecycle"])
        self.assertNotIn("kind, domain and tags", fields["lifecycle"])

    def test_gold_is_identical_across_arms(self):
        verbatim, para, reason = build_variants(self.CASE, 0)
        self.assertEqual(reason, "")
        self.assertIsNotNone(para)
        self.assertEqual(verbatim["gold"], para["gold"])
        self.assertNotEqual(verbatim["input"], para["input"])

    def test_decision_bearing_tokens_survive(self):
        _v, para, _r = build_variants(self.CASE, 0)
        self.assertIn("aaaaaaaa-1111-2222-3333-444444444444", para["input"])
        self.assertIn("bbbbbbbb-1111-2222-3333-444444444444", para["input"])
        self.assertIn("2026-01-02T00:00:00Z", para["input"])

    def test_paraphrase_is_deterministic(self):
        _v1, p1, _r1 = build_variants(self.CASE, 3)
        _v2, p2, _r2 = build_variants(self.CASE, 3)
        self.assertEqual(p1["input"], p2["input"])

    def test_case_without_chain_is_dropped(self):
        broken = dict(self.CASE, input="Triage this Well record.\nrecord: aaaa")
        verbatim, para, reason = build_variants(broken, 0)
        self.assertIsNone(para)
        self.assertIn("chain", reason)
        self.assertIsNotNone(verbatim)


class TestGauntletConfig(unittest.TestCase):
    def test_num_predict_default_is_sweepable(self):
        """512 is the historical default and stays a default, not a hardcode."""
        self.assertEqual(gauntlet.DEFAULT_NUM_PREDICT, 512)

    def test_schema_dispatch_sends_flat_roles_to_the_decomposition_dir(self):
        path = gauntlet.schema_path("place_classifier")
        self.assertEqual(path.parent.name, "schemas")
        self.assertIn("decomposition", str(path))
        self.assertIn("decomposition", str(gauntlet.schema_path("quote_extractor")))
        self.assertNotIn("decomposition", str(gauntlet.schema_path("tool_router")))

    def test_flat_schemas_load(self):
        for role in droles.DECOMPOSITION_ROLES:
            self.assertIn("properties", gauntlet.load_schema(role))


if __name__ == "__main__":
    unittest.main()