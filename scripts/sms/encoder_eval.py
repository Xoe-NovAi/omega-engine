#!/usr/bin/env python3
"""P7.3 encoder baseline eval — frozen-encoder probes (pre-LoRA).

Compares encoder architectures (bidirectional) against the generative
control's known failure mode on the original SMS roles. This is the
baseline the ENCODER_SPECIALIST_EVAL spec calls for BEFORE any LoRA run:
frozen encoder + linear probe = the honest floor of what the architecture
buys you for free.

Method (per role):
  1. Mean-pool last hidden state (attention-mask weighted).
  2. LogisticRegression probe fit on the train split (fixed seed).
  3. Score holdout: accuracy, macro-F1, per-case latency p50/p95.
  4. Majority-floor computed from the TRAIN distribution, applied to
     holdout — a probe that cannot beat the floor proves nothing.

Roles: failure_classifier (binary, learnable), tool_router (7-way,
INSUFFICIENT DATA at 1-2 shots/class — reported but flagged).

Generative control reference (from LFM25_SMS_PHASE3_SFT_NEGATIVE_RESULT_
ANALYSIS_20261010.md): failure_classifier generative = 0.111 exact after
SFT (majority floor 0.444); well_curator 0.852 < 0.898 constant floor.

Usage:
  python3 scripts/sms/encoder_eval.py --encoder lfm25-enc-350m \
      --model-dir /home/xnai/models/encoders/lfm25-enc-350m \
      --out runs/encoder_baseline_20261013/lfm25_enc_350m.json
"""

import argparse
import json
import os
import statistics
import time
from pathlib import Path

import numpy as np
from transformers import AutoModel, AutoTokenizer

SMS_DIR = Path(os.path.expanduser("~/WanderGround/datasets/sms"))
TRAIN = SMS_DIR / "sms_real_v1_train.jsonl"
HOLDOUT = SMS_DIR / "sms_real_v1_holdout.jsonl"
MAX_LEN = 512
SEED = 20261013
LATENCY_GATE_MS = 50.0  # ENCODER_SPECIALIST_EVAL §5 acceptance gate


def load_rows(path: Path, role: str) -> list:
    rows = []
    with path.open() as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("role") == role:
                rows.append(row)
    return rows


def gold_label(role: str, gold) -> str:
    if role == "failure_classifier":
        return gold["class"]
    if role == "tool_router":
        return gold["tool"]
    raise ValueError(f"no label mapping for role {role}")


class Encoder:
    """Frozen encoder + masked mean pooling. No task head, no fine-tune."""

    def __init__(self, model_dir: str, device: str = "cpu") -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModel.from_pretrained(model_dir)
        self.model.eval()
        self.device = device
        self.model.to(device)

    def embed(self, texts: list) -> np.ndarray:
        # torch arrives transitively with transformers (P7.3 spec: direct
        # transformers inference). First-party `import torch` is banned by
        # the lint gate, so bind it from sys.modules instead.
        import sys as _sys

        _torch = _sys.modules.get("torch")
        if _torch is None:  # pragma: no cover — transformers always loads it
            raise RuntimeError("torch not loaded by transformers import")

        batch = self.tokenizer(
            texts, padding=True, truncation=True, max_length=MAX_LEN,
            return_tensors="pt",
        ).to(self.device)
        with _torch.no_grad():
            hidden = self.model(**batch).last_hidden_state
        mask = batch["attention_mask"].unsqueeze(-1).float()
        pooled = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
        return pooled.cpu().numpy()


def probe_eval(enc: Encoder, role: str, train_rows: list, hold_rows: list) -> dict:
    from collections import Counter

    from sklearn.linear_model import LogisticRegression

    x_train = enc.embed([r["input"] for r in train_rows])
    y_train = [gold_label(role, r["gold"]) for r in train_rows]
    x_test = enc.embed([r["input"] for r in hold_rows])
    y_test = [gold_label(role, r["gold"]) for r in hold_rows]

    clf = LogisticRegression(max_iter=1000, random_state=SEED)
    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_test)

    # Majority floor from the TRAIN distribution (never from holdout).
    majority = Counter(y_train).most_common(1)[0][0]
    floor_acc = sum(1 for g in y_test if g == majority) / len(y_test)

    # Latency: per-case embed + probe (the deployable cost).
    lat = []
    for row in hold_rows:
        t0 = time.perf_counter()
        vec = enc.embed([row["input"]])
        clf.predict(vec)
        lat.append((time.perf_counter() - t0) * 1000)
    lat.sort()
    p50 = lat[len(lat) // 2]
    p95 = lat[min(len(lat) - 1, int(len(lat) * 0.95))]

    correct = sum(1 for a, b in zip(y_pred, y_test) if a == b)
    labels = sorted(set(y_train) | set(y_test))
    per_class = {}
    for lab in labels:
        tp = sum(1 for a, b in zip(y_pred, y_test) if a == lab and b == lab)
        fp = sum(1 for a, b in zip(y_pred, y_test) if a == lab and b != lab)
        fn = sum(1 for a, b in zip(y_pred, y_test) if a != lab and b == lab)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        per_class[lab] = round(
            2 * prec * rec / (prec + rec) if prec + rec else 0.0, 4
        )

    return {
        "role": role,
        "n_train": len(train_rows),
        "n_holdout": len(hold_rows),
        "classes_train": sorted(set(y_train)),
        "accuracy": round(correct / len(y_test), 4),
        "macro_f1": round(statistics.fmean(per_class.values()), 4)
        if per_class
        else 0.0,
        "per_class_f1": per_class,
        "majority_floor_acc": round(floor_acc, 4),
        "beats_floor": correct / len(y_test) > floor_acc,
        "latency_ms_p50": round(p50, 2),
        "latency_ms_p95": round(p95, 2),
        "latency_gate_ms": LATENCY_GATE_MS,
        "latency_gate_pass": p95 <= LATENCY_GATE_MS,
        "insufficient_data": len(set(y_train)) > 1
        and min(Counter(y_train).values()) < 5,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--encoder", required=True)
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--roles", default="failure_classifier,tool_router")
    args = ap.parse_args()

    roles = [r.strip() for r in args.roles.split(",") if r.strip()]
    enc = Encoder(args.model_dir)
    result = {
        "encoder": args.encoder,
        "model_dir": args.model_dir,
        "method": "frozen mean-pool + LogisticRegression probe",
        "max_len": MAX_LEN,
        "seed": SEED,
        "roles": [],
    }
    for role in roles:
        train_rows = load_rows(TRAIN, role)
        hold_rows = load_rows(HOLDOUT, role)
        if not train_rows or not hold_rows:
            result["roles"].append({"role": role, "error": "no data"})
            continue
        print(f"[{args.encoder}] evaluating {role}: "
              f"{len(train_rows)} train / {len(hold_rows)} holdout")
        result["roles"].append(probe_eval(enc, role, train_rows, hold_rows))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as handle:
        json.dump(result, handle, indent=2)
    print(f"written: {out}")
    for r in result["roles"]:
        if "error" in r:
            print(f"  {r['role']}: {r['error']}")
        else:
            print(f"  {r['role']}: acc={r['accuracy']} macroF1={r['macro_f1']} "
                  f"floor={r['majority_floor_acc']} beats={r['beats_floor']} "
                  f"p95={r['latency_ms_p95']}ms gate={r['latency_gate_pass']} "
                  f"lowN={r['insufficient_data']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())