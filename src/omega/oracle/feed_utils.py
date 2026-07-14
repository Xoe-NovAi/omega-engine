# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Omega Engine — Cross-Pollination Feed Utilities
# ⬡ OMEGA ⬡ P9:LINK ⬡ deepseek-v4-flash ⬡ opencode ⬡ FEED-UTILS
# AP: FEED-UTILS-v1.0.0
#
# Shared utilities for knowledge feed and demand signal operations.
# Used by oracle_cli.py (integrated). link_p9_cli.py has been consolidated.
#
# [id-soft: doom-1993] ZONEID Pattern — knowledge and demand signal validation


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from omega.cvar_table import ZONEID_KNOWLEDGE, ZONEID_DEMAND, cvar_get

logger = logging.getLogger(__name__)

KNOWLEDGE_FEED_DIR = Path("data/coordination/knowledge_feed")
DEMAND_SIGNALS_DIR = Path("data/coordination/demand_signals")
CROSS_REF_DIR = Path("knowledge/cross_references")


# ── Load ─────────────────────────────────────────────────────────────────


def load_knowledge_signals() -> List[Dict[str, Any]]:
    """Load all active KSIG files from knowledge_feed/."""
    if not KNOWLEDGE_FEED_DIR.exists():
        return []
    signals = []
    for path in sorted(KNOWLEDGE_FEED_DIR.glob("KSIG_*.json")):
        try:
            data = json.loads(path.read_text())
            if data.get("zoneid") != ZONEID_KNOWLEDGE:
                logger.warning("SKIP %s: invalid ZONEID (expected 0x%08x)", path.name, ZONEID_KNOWLEDGE)
                continue
            signals.append(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("SKIP %s: corrupt (%s)", path.name, e)
            continue
    return signals


def load_demand_signals() -> List[Dict[str, Any]]:
    """Load all active demand signal files."""
    if not DEMAND_SIGNALS_DIR.exists():
        return []
    signals = []
    for path in sorted(DEMAND_SIGNALS_DIR.glob("dem-*.json")):
        try:
            data = json.loads(path.read_text())
            if data.get("zoneid") != ZONEID_DEMAND:
                logger.warning("SKIP %s: invalid ZONEID", path.name)
                continue
            signals.append(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("SKIP %s: corrupt (%s)", path.name, e)
            continue
    return signals


# ── Discovery ────────────────────────────────────────────────────────────


def find_new_signals(
    agent: str,
    signals: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Find knowledge signals not yet consumed by agent."""
    if signals is None:
        signals = load_knowledge_signals()
    result = []
    for sig in signals:
        consumed_by = sig.get("consumed_by", [])
        if agent not in consumed_by and _agent_matches(agent, sig):
            result.append(sig)
    return result


def find_open_demands(
    domain: Optional[str] = None,
    demands: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Find open demand signals, optionally filtered by domain."""
    if demands is None:
        demands = load_demand_signals()
    result = [d for d in demands if d.get("status", "").upper() == "OPEN"]
    if domain:
        result = [d for d in result if d.get("domain", "").lower() == domain.lower()]
    return result


def summarize_feed(
    signals: Optional[List[Dict[str, Any]]] = None,
    demands: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Get summary counts for knowledge feed and demand signals."""
    if signals is None:
        signals = load_knowledge_signals()
    if demands is None:
        demands = load_demand_signals()

    producers: Dict[str, int] = {}
    for sig in signals:
        p = sig.get("producer", "unknown")
        producers[p] = producers.get(p, 0) + 1

    status_counts: Dict[str, int] = {}
    for d in demands:
        s = d.get("status", "UNKNOWN").upper()
        status_counts[s] = status_counts.get(s, 0) + 1

    return {
        "total_signals": len(signals),
        "total_demands": len(demands),
        "producers": producers,
        "demand_status_counts": status_counts,
        "open_demands": status_counts.get("OPEN", 0),
    }


# ── Consumption ──────────────────────────────────────────────────────────


def consume_signal(signal: Dict[str, Any], agent: str) -> Dict[str, Any]:
    """Mark a signal as consumed by agent. Returns updated signal dict."""
    if agent not in signal.setdefault("consumed_by", []):
        signal["consumed_by"].append(agent)
    signal.setdefault("consumed_at", {})[agent] = datetime.now(timezone.utc).isoformat() + "Z"
    return signal


def write_knowledge_signal(signal: Dict[str, Any]) -> None:
    """Write a KSIG atomically (.tmp → rename)."""
    signal_id = signal["signal_id"]
    path = KNOWLEDGE_FEED_DIR / f"KSIG_{signal_id.upper()}.json"
    if not path.exists():
        path = KNOWLEDGE_FEED_DIR / f"{signal_id}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(signal, indent=2))
    tmp.rename(path)


def write_cross_reference(consumer: str, signal: Dict[str, Any]) -> Path:
    """Write a cross-reference entry when an agent consumes a signal."""
    ref_dir = CROSS_REF_DIR / consumer
    ref_dir.mkdir(parents=True, exist_ok=True)

    producer = signal["producer"]
    signal_id = signal["signal_id"]
    ref_path = ref_dir / f"{producer}_{signal_id}.json"

    ref = {
        "cross_ref_id": f"xref-{consumer}-{signal_id}",
        "consumer": consumer,
        "producer": producer,
        "signal_id": signal_id,
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "zoneid": ZONEID_KNOWLEDGE,
        "domain": signal.get("domain", ""),
        "l2_insight": signal.get("l2_insight", ""),
        "applied_in": "",
        "applied_how": "",
        "soul_updated": False,
        "notes": "",
    }
    tmp = ref_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(ref, indent=2))
    tmp.rename(ref_path)

    _update_cross_ref_index(ref_dir, consumer, ref["cross_ref_id"], producer)
    return ref_path


def _update_cross_ref_index(ref_dir: Path, consumer: str, cross_ref_id: str, producer: str) -> None:
    """Update or create the cross-reference INDEX.json."""
    index_path = ref_dir / "INDEX.json"
    if index_path.exists():
        index = json.loads(index_path.read_text())
    else:
        index = {"agent": consumer, "updated_at": "", "cross_references": [], "total_consumed": 0, "unique_producers": []}

    index["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
    if cross_ref_id not in index["cross_references"]:
        index["cross_references"].append(cross_ref_id)
        index["total_consumed"] = len(index["cross_references"])
        if producer not in index["unique_producers"]:
            index["unique_producers"].append(producer)

    tmp = index_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(index, indent=2))
    tmp.rename(index_path)


# ── Demand Signal Lifecycle ──────────────────────────────────────────────


def transition_demand(
    demand_id: str,
    new_status: str,
    assigned_to: Optional[str] = None,
    fulfilled_signal_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Transition a demand signal to a new state. Returns updated dict or None."""
    path = DEMAND_SIGNALS_DIR / f"{demand_id}.json"
    if not path.exists():
        logger.error("Demand not found: %s", demand_id)
        return None

    data = json.loads(path.read_text())
    if data.get("zoneid") != ZONEID_DEMAND:
        logger.error("Invalid ZONEID in demand: %s", demand_id)
        return None

    if new_status == "ASSIGNED" and assigned_to:
        data["status"] = "ASSIGNED"
        data["assigned_to"] = assigned_to
    elif new_status == "FULFILLED" and fulfilled_signal_id:
        data["status"] = "FULFILLED"
        data["fulfilled_by"] = data.get("assigned_to", "unknown")
        data["fulfilled_signal_id"] = fulfilled_signal_id
        data["fulfilled_at"] = datetime.now(timezone.utc).isoformat() + "Z"
    elif new_status == "FAILED":
        data["status"] = "FAILED"
    elif new_status == "EXPIRED":
        data["status"] = "EXPIRED"

    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.rename(path)
    return data


# ── Internal ─────────────────────────────────────────────────────────────


def _agent_matches(agent: str, signal: Dict[str, Any]) -> bool:
    """Check if an agent matches a signal's relevance tags."""
    if agent == cvar_get("config.entity.default", "default"):
        return True
    tags = [t.lower() for t in signal.get("relevance_tags", [])]
    return agent.lower() in tags
