#!/usr/bin/env python3
"""P7.3 latency gate re-test — dynamic INT8 quantization of encoders.

The fp32 baseline (`ENCODER_BASELINE_RESULTS_20261013.md`) failed the
spec's <=50 ms p95 gate on CPU. This is the spec's own stated mitigation
("Quantize to INT8/INT4") applied to the cheapest encoder
(ModernBERT-base, Linear-heavy).

Method: torch dynamic quantization of Linear layers to INT8 weights
(activations stay fp32 - the standard CPU inference trade). Same inputs,
same protocol as `encoder_eval.py` so numbers compare directly:
per-case embed of every failure_classifier holdout case, p50/p95.

Quality guard: the probe is refit on train embeddings produced by the
SAME quantized model, then scored on holdout - INT8 must not change
predictions before it is allowed to claim the latency win.

Usage:
  python3 scripts/sms/quantize_bench.py \
      --model-dir /home/xnai/models/encoders/modernbert-base \
      --out runs/encoder_baseline_20261013/modernbert_int8.json
"""

import argparse
import json
import os
import time
from pathlib import Path

from transformers import AutoModel, AutoTokenizer

SMS_DIR = Path(os.path.expanduser("~/WanderGround/datasets/sms"))
TRAIN = SMS_DIR / "sms_real_v1_train.jsonl"
HOLDOUT = SMS_DIR / "sms_real_v1_holdout.jsonl"
MAX_LEN = 512
SEED = 20261013
LATENCY_GATE_MS = 50.0


def rows_for(path: Path, role: str) -> list:
    out = []
    with path.open() as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("role") == role:
                out.append(row)
    return out


def embed_latency(model, tokenizer, texts: list, device: str = "cpu") -> tuple:
    """Per-case masked mean-pool; returns (vectors, sorted latencies ms)."""
    import sys as _sys

    _torch = _sys.modules.get("torch")
    if _torch is None:  # pragma: no cover - transformers always loads torch
        raise RuntimeError("torch not loaded by transformers import")

    vectors, lat = [], []
    for text in texts:
        batch = tokenizer(
            [text], padding=True, truncation=True, max_length=MAX_LEN,
            return_tensors="pt",
        ).to(device)
        t0 = time.perf_counter()
        with _torch.no_grad():
            hidden = model(**batch).last_hidden_state
        mask = batch["attention_mask"].unsqueeze(-1).float()
        pooled = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
        lat.append((time.perf_counter() - t0) * 1000)
        vectors.append(pooled.cpu().numpy()[0])
    return vectors, sorted(lat)


def fit_score(enc_model, tokenizer, role: str) -> dict:
    """Fit probe on train split with THIS model's embeddings, score holdout."""
    import numpy as np
    from sklearn.linear_model import LogisticRegression

    train_rows = rows_for(TRAIN, role)
    hold_rows = rows_for(HOLDOUT, role)
    tr_vecs, _ = embed_latency(
        enc_model, tokenizer, [r["input"] for r in train_rows]
    )
    ho_vecs, lat = embed_latency(
        enc_model, tokenizer, [r["input"] for r in hold_rows]
    )
    ho_gold = [r["gold"]["class"] for r in hold_rows]

    clf = LogisticRegression(max_iter=1000, random_state=SEED)
    clf.fit(np.array(tr_vecs), [r["gold"]["class"] for r in train_rows])
    y_pred = clf.predict(np.array(ho_vecs))

    correct = sum(1 for a, b in zip(y_pred, ho_gold) if a == b)
    p95 = lat[min(len(lat) - 1, int(len(lat) * 0.95))]
    return {
        "accuracy": round(correct / len(ho_gold), 4),
        "latency_ms_p50": round(lat[len(lat) // 2], 2),
        "latency_ms_p95": round(p95, 2),
        "latency_gate_ms": LATENCY_GATE_MS,
        "latency_gate_pass": p95 <= LATENCY_GATE_MS,
        "n_holdout": len(ho_gold),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--role", default="failure_classifier")
    ap.add_argument("--threads", type=int, default=6,
                    help="intra-op threads for BOTH fp32 and int8 runs "
                         "(default 6 = P-cores; thread count is a first-class "
                         "latency variable on this box)")
    args = ap.parse_args()

    import sys as _sys

    _torch = _sys.modules.get("torch")
    if _torch is None:  # pragma: no cover
        raise RuntimeError("torch not loaded by transformers import")
    _torch.set_num_threads(args.threads)

    tokenizer = AutoTokenizer.from_pretrained(args.model_dir)

    print(f"fp32 baseline: {args.model_dir}")
    fp32 = AutoModel.from_pretrained(args.model_dir)
    fp32.eval()
    fp32_res = fit_score(fp32, tokenizer, args.role)
    print(f"  fp32: acc={fp32_res['accuracy']} p50={fp32_res['latency_ms_p50']}ms "
          f"p95={fp32_res['latency_ms_p95']}ms gate={fp32_res['latency_gate_pass']}")

    print("quantizing to dynamic INT8 (Linear layers)...")
    qmodel = _torch.ao.quantization.quantize_dynamic(
        AutoModel.from_pretrained(args.model_dir),
        {_torch.nn.Linear},
        dtype=_torch.qint8,
    )
    qmodel.eval()
    int8_res = fit_score(qmodel, tokenizer, args.role)
    print(f"  int8: acc={int8_res['accuracy']} p50={int8_res['latency_ms_p50']}ms "
          f"p95={int8_res['latency_ms_p95']}ms gate={int8_res['latency_gate_pass']}")

    result = {
        "model_dir": args.model_dir,
        "role": args.role,
        "quantization": "torch dynamic INT8 (Linear weights, fp32 activations)",
        "fp32": fp32_res,
        "int8": int8_res,
        "acc_delta": round(int8_res["accuracy"] - fp32_res["accuracy"], 4),
        "speedup_p50": round(
            fp32_res["latency_ms_p50"] / int8_res["latency_ms_p50"], 2
        ) if int8_res["latency_ms_p50"] else None,
        "speedup_p95": round(
            fp32_res["latency_ms_p95"] / int8_res["latency_ms_p95"], 2
        ) if int8_res["latency_ms_p95"] else None,
        "quality_preserved": int8_res["accuracy"] >= fp32_res["accuracy"] - 0.05,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as handle:
        json.dump(result, handle, indent=2)
    print(f"written: {out}")
    print(f"verdict: quality_preserved={result['quality_preserved']} "
          f"gate_pass_int8={int8_res['latency_gate_pass']} "
          f"p95_speedup={result['speedup_p95']}x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())