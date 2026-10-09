"""Flat single-purpose contracts that decompose the four complex v1 roles.

Hypothesis under test (docs/research/LFM25_SMS_PHASE2_ECHO_DECOMPOSITION_20261008.md):
for a ≤350M model a chain of flat contracts beats one nested contract, even though
it costs more inference calls. Each role here emits a single JSON object with at
most two short scalar keys and `additionalProperties: false` — no arrays, no
nesting, no provenance object.

  place_classifier   <- mempalace_extractor's wing/room placement
  quote_extractor    <- mempalace_extractor's first item (content + grounding)
  pii_action         <- privacy_sentinel's decision (detection already done)
  supersede_decider  <- well_curator's forward-pointing supersession reasoning

Gold for these is derived, never hand-labelled: `build_derived.py` projects the
existing sms_real_v1 holdout gold onto each flat contract.
"""

from __future__ import annotations

from scripts.sms.scoring import provenance, span_f1

DECOMPOSITION_ROLES = ("place_classifier", "quote_extractor", "pii_action", "supersede_decider")

EXACT_MATCH_KEYS = {
    "place_classifier": ["wing", "room"],
    "quote_extractor": ["content", "source_quote"],
    "pii_action": ["action"],
    "supersede_decider": ["action", "superseded_by"],
}

SYSTEM = {
    "place_classifier": (
        "You place a transcript window into a memory palace. Respond with ONLY the JSON object; "
        "do not echo or repeat the input. Keys: wing (string) and room (string) — the single best "
        "wing and the single best room for the window's subject. Exactly two keys."
    ),
    "quote_extractor": (
        "You quote one durable fact from a transcript window. Respond with ONLY the JSON object; "
        "do not echo or repeat the input. Keys: content (short string stating the fact) and "
        "source_quote (string copied character-for-character out of the window). The "
        "source_quote must appear verbatim in the input. Exactly two keys."
    ),
    "pii_action": (
        "You decide what to do with text that has already been scanned. The spans are given. "
        "Respond with ONLY the JSON object; do not echo or repeat the input. Keys: action, one of "
        "allow|redact|drop. allow when no spans were found, redact when spans were found and the "
        "text can be masked with typed placeholders, drop when the text cannot be made safe. "
        "Exactly one key."
    ),
    "supersede_decider": (
        "You decide whether a Well record has been superseded. Respond with ONLY the JSON object; "
        "do not echo or repeat the input. Keys: action (keep|supersede) and superseded_by (the id "
        "of the NEWER record, or null). Set action=supersede only when a strictly newer record in "
        "the chain carries the successor pointer; otherwise keep with null. Exactly two keys."
    ),
}


def build_user(role: str, case: dict) -> str:
    """Render the user turn.

    The parent contracts wrap the raw window in a JSON envelope for the
    extractor and the router. The flat roles read the window (or the prepared
    fields) directly — one less shape for a 350M model to hold in mind.

    pii_action and supersede_decider take prepared fields in `context_fields`;
    those are the outputs of the upstream contract, which is the whole point of
    a chain: the decider never sees the PII spans or the chain ids as free text.
    """
    fields = case.get("context_fields")
    if isinstance(fields, dict) and fields:
        parts = [str(fields[k]) for k in sorted(fields)]
        return "\n".join(parts) if len(parts) > 1 else parts[0]
    return str(case.get("input", ""))


def score_case(role: str, pred: object, gold: dict, case: dict) -> dict:
    """Score one flat-contract output. Exact match is over all emitted keys."""
    if not isinstance(pred, dict):
        return {"exact_match": 0.0, "field_f1": 0.0}
    metrics: dict[str, float] = {}
    if role == "place_classifier":
        for k in EXACT_MATCH_KEYS[role]:
            metrics[f"{k}_exact"] = span_f1.exact(str(pred.get(k, "")), str(gold.get(k, "")))
        metrics["exact_match"] = sum(metrics.values()) / 2
        metrics["field_f1"] = metrics["exact_match"]
        return metrics
    if role == "quote_extractor":
        metrics["content_f1"] = span_f1.token_f1(str(pred.get("content", "")), str(gold.get("content", "")))
        grounded, _ = _grounding(pred, gold, case)
        metrics["source_quote_exact"] = span_f1.exact(pred.get("source_quote"), gold.get("source_quote"))
        metrics["quote_grounded"] = grounded
        metrics["exact_match"] = (metrics["source_quote_exact"] + metrics["content_f1"]) / 2
        metrics["field_f1"] = metrics["content_f1"]
        return metrics
    if role == "pii_action":
        metrics["action_exact"] = span_f1.exact(pred.get("action"), gold.get("action"))
        metrics["exact_match"] = metrics["action_exact"]
        metrics["field_f1"] = metrics["action_exact"]
        return metrics
    if role == "supersede_decider":
        metrics["action_exact"] = span_f1.exact(pred.get("action"), gold.get("action"))
        sb_pred, sb_gold = pred.get("superseded_by"), gold.get("superseded_by")
        metrics["superseded_by_exact"] = span_f1.exact(
            sb_pred if isinstance(sb_pred, str) else None,
            sb_gold if isinstance(sb_gold, str) else None,
        )
        metrics["supersession_shape_ok"] = 1.0 if (
            (pred.get("action") == "supersede" and isinstance(sb_pred, str) and sb_pred)
            or (pred.get("action") != "supersede" and sb_pred in (None, ""))
        ) else 0.0
        metrics["exact_match"] = (metrics["action_exact"] + metrics["superseded_by_exact"]) / 2
        metrics["field_f1"] = metrics["exact_match"]
        return metrics
    return metrics


def _grounding(pred: dict, gold: dict, case: dict) -> tuple[float, str]:
    """Same grounding rule as mempalace_extractor, via the shared scorer.

    The flat contract has no items[] array, so the single quote is re-wrapped
    into the parent's shape and handed to `source_quote_grounded`. That keeps
    one definition of "grounded" — the decomposition must not weaken the gate.
    """
    window = case.get("input", "")
    if not isinstance(window, str):
        window = ""
    q = pred.get("source_quote")
    if not isinstance(q, str) or not q:
        return 0.0, "empty source_quote"
    shim = {"items": [{"source_quote": q}]}
    ok = provenance.source_quote_grounded(shim, window)
    return (1.0, "grounded") if ok else (0.0, f"not a substring of window: {q[:80]!r}")


__all__ = ["DECOMPOSITION_ROLES", "SYSTEM", "build_user", "score_case", "EXACT_MATCH_KEYS"]