"""Per-role prompt builders and scorers for the SMS gauntlet.

Each role module contract:
  SYSTEM: system-prompt template for the role
  build_user(case) -> str
  score(pred, gold, case) -> dict of metric name -> value
"""

from __future__ import annotations

from typing import Any

from scripts.sms.scoring import provenance, span_f1

EXACT_MATCH_KEYS = {
    "well_curator": ["kind", "domain", "action"],
    "tool_router": ["tool", "fallback"],
    "privacy_sentinel": ["action"],
    "failure_classifier": ["class"],
}

SYSTEM = {
    "mempalace_extractor": (
        "You extract structured memory items from a transcript window. Respond with ONLY the JSON object; do not echo or repeat the input. "
        "Keys: wing (string), room (string), items (array of {kind, content, source_quote, "
        "confidence}), provenance ({source_file, recorded_at, window_id}). kind is one of "
        "corrections|decisions|measurements|patterns|narrative|questions. source_quote must be an "
        "exact substring of the input window. If nothing is extractable, return items: []."
    ),
    "well_curator": (
        "You triage a Well record. Respond with ONLY the JSON object; do not echo or repeat the input. Keys: kind "
        "(correction|anti_pattern|insight|preference|dream|measurement|rule), domain (local_ai|gaming|harness|"
        "research|consciousness|general), tags (array of strings), action (keep|supersede|merge|drop), "
        "superseded_by (well id string or null), rationale (<=200 chars). superseded_by must point "
        "to the NEWER record; only set action=supersede when superseding with a newer record."
    ),
    "tool_router": (
        "You route a request to a tool. Respond with ONLY the JSON object; do not echo or repeat the input. Keys: tool (one of "
        "mempalace_search|mempalace_kg_query|well_add|web_search|ochist_grep|ocdb_ro|none), args "
        "(object), fallback (none|ask_human|deterministic_regex). Choose none when no tool fits."
    ),
    "privacy_sentinel": (
        "You scan text for PII and decide an action. Respond with ONLY the JSON object; do not echo or repeat the input. Keys: "
        "pii_found (array of {type, span} where type is email|ip|api_key|user_path|ssn|phone), "
        "action (allow|redact|drop), redacted_text (string with typed placeholders or null)."
    ),
    "failure_classifier": (
        "You classify a runner failure trace. Respond with ONLY the JSON object; do not echo or repeat the input. Keys: class (one of "
        "parse_failure|schema_violation|truncation|hallucinated_entity|latency_spike|wrong_tool|"
        "abstained|ok), confidence (0-1), evidence (short string)."
    ),
}


def build_user(role: str, case: dict) -> str:
    inp = case.get("input", "")
    if role == "mempalace_extractor":
        return json_dump({"window": inp, "source_file": case.get("source_file", "synthetic"), "window_id": case.get("case_id", "w0")})
    if role == "tool_router":
        return json_dump({"request": inp, "allowlist": ["mempalace_search", "mempalace_kg_query", "well_add", "web_search", "ochist_grep", "ocdb_ro", "none"]})
    return inp if isinstance(inp, str) else json_dump(inp)


def json_dump(obj: Any) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)


def _tags_f1(pred: Any, gold: Any) -> float:
    p = [str(t).lower() for t in pred] if isinstance(pred, list) else []
    g = [str(t).lower() for t in gold] if isinstance(gold, list) else []
    return span_f1.set_f1(p, g)


def _item_content_f1(pred: Any, gold: Any) -> float:
    def contents(items):
        if not isinstance(items, list):
            return []
        return [str(it.get("content", "")).lower() for it in items if isinstance(it, dict)]

    pred_items = contents(pred.get("items")) if isinstance(pred, dict) else []
    gold_items = contents(gold.get("items")) if isinstance(gold, dict) else []
    if not pred_items and not gold_items:
        return 1.0
    # match each pred content to best gold content (token F1), greedy
    used = [False] * len(gold_items)
    scores = []
    for pc in pred_items:
        best, best_i = 0.0, -1
        for i, gc in enumerate(gold_items):
            if used[i]:
                continue
            s = span_f1.token_f1(pc, gc)
            if s > best:
                best, best_i = s, i
        if best_i >= 0:
            used[best_i] = True
        scores.append(best)
    matched = sum(scores)
    denom = max(1, len(pred_items) + len(gold_items) - len(scores))
    # approximation: average of matched precision/recall style score
    if not pred_items and not gold_items:
        return 1.0
    return matched / denom if denom else 0.0


def _span_pairs(items: Any) -> list[str]:
    if not isinstance(items, list):
        return []
    out = []
    for it in items:
        if isinstance(it, dict):
            out.append(f"{it.get('type')}:{str(it.get('span', '')).lower()}")
    return out


def _args_f1(pred: Any, gold: Any) -> float:
    if not isinstance(pred, dict) or not isinstance(gold, dict):
        return 0.0
    keys = list(set(pred.keys()) | set(gold.keys()))
    if not keys:
        return 1.0
    hits = 0
    for k in keys:
        if k in pred and k in gold and str(pred[k]).lower() == str(gold[k]).lower():
            hits += 1
    p = hits / max(1, len(pred))
    r = hits / max(1, len(gold))
    return 2 * p * r / (p + r) if (p + r) else 0.0


def score_case(role: str, pred: Any, gold: dict, case: dict) -> dict:
    metrics: dict[str, float] = {}
    if not isinstance(pred, dict):
        return {"exact_match": 0.0, "field_f1": 0.0}
    if role == "mempalace_extractor":
        metrics["wing_exact"] = span_f1.exact(str(pred.get("wing", "")), str(gold.get("wing", "")))
        metrics["room_exact"] = span_f1.exact(str(pred.get("room", "")), str(gold.get("room", "")))
        metrics["items_f1"] = _item_content_f1(pred, gold)
        metrics["provenance_preserved"] = provenance.provenance_preserved(pred, gold, case.get("input", "") if isinstance(case.get("input"), str) else "")
        metrics["exact_match"] = (metrics["wing_exact"] + metrics["room_exact"]) / 2
        metrics["field_f1"] = metrics["items_f1"]
    elif role == "well_curator":
        for k in EXACT_MATCH_KEYS[role]:
            metrics[f"{k}_exact"] = span_f1.exact(pred.get(k), gold.get(k))
        metrics["tags_f1"] = _tags_f1(pred.get("tags"), gold.get("tags"))
        sb = pred.get("superseded_by")
        metrics["supersession_shape_ok"] = 1.0 if (
            (pred.get("action") == "supersede" and isinstance(sb, str) and sb)
            or (pred.get("action") != "supersede" and sb in (None, ""))
        ) else 0.0
        metrics["exact_match"] = sum(metrics[f"{k}_exact"] for k in EXACT_MATCH_KEYS[role]) / 3
        metrics["field_f1"] = (metrics["tags_f1"] + sum(metrics[f"{k}_exact"] for k in EXACT_MATCH_KEYS[role]) / 3) / 2
    elif role == "tool_router":
        metrics["tool_exact"] = span_f1.exact(pred.get("tool"), gold.get("tool"))
        metrics["fallback_exact"] = span_f1.exact(pred.get("fallback"), gold.get("fallback"))
        metrics["args_f1"] = _args_f1(pred.get("args"), gold.get("args"))
        metrics["abstention_ok"] = 1.0 if (gold.get("tool") == "none") == (pred.get("tool") == "none") else 0.0
        metrics["exact_match"] = metrics["tool_exact"]
        metrics["field_f1"] = metrics["args_f1"]
    elif role == "privacy_sentinel":
        metrics["action_exact"] = span_f1.exact(pred.get("action"), gold.get("action"))
        metrics["span_f1"] = span_f1.set_f1(_span_pairs(pred.get("pii_found")), _span_pairs(gold.get("pii_found")))
        metrics["abstention_ok"] = 1.0 if (gold.get("action") == "allow") == (pred.get("action") == "allow") else 0.0
        metrics["exact_match"] = metrics["action_exact"]
        metrics["field_f1"] = metrics["span_f1"]
    elif role == "failure_classifier":
        metrics["class_exact"] = span_f1.exact(pred.get("class"), gold.get("class"))
        metrics["exact_match"] = metrics["class_exact"]
        metrics["field_f1"] = metrics["class_exact"]
    return metrics
