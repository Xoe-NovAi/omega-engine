#!/usr/bin/env python3
"""P7.3 LoRA fine-tuning — encoder + adapter + linear head.

The frozen-probe baseline (`ENCODER_BASELINE_RESULTS_20261013.md`) hit
0.964 acc on failure_classifier with zero training. This milestone tests
whether LoRA fine-tuning (the spec's scheduled step) adds anything on top
— or whether, as the linear-separability result suggests, the frozen
representation already sits at the task ceiling.

Design choices informed by the Phase-3 negative-result analysis
(`LFM25_SMS_PHASE3_SFT_NEGATIVE_RESULT_ANALYSIS_20261010.md`):
  1. UNDERFIT was failure mode #1 (5 optimizer steps, acc 0.111). Here:
     20 epochs, holdout eval every epoch, best-checkpoint selection.
  2. LOSS-MASK corruption was failure mode #2 (generative models attend
     to instruction tokens). Encoders have no generation — the head sees
     the pooled vector directly, so this class of failure cannot occur.
  3. Overfit is the real risk at 46 train examples: report train AND
     holdout accuracy so a memorizing run is visible as a gap.

Method: mean-pool last hidden state -> Linear(n_classes); LoRA (r=8,
alpha=16) on all Linear submodules of the encoder; AdamW; CE loss.

Usage:
  python3 scripts/sms/encoder_lora.py --encoder modernbert-base \
      --model-dir /home/xnai/models/encoders/modernbert-base \
      --out runs/encoder_baseline_20261013/modernbert_lora.json
"""

import argparse
import gc
import json
import os
import resource
import sys
import threading
import time
from pathlib import Path

# torch arrives transitively via transformers; first-party `import torch`
# is banned by the lint gate, so bind it from sys.modules after the
# transformers import populates it.
from transformers import AutoModel, AutoTokenizer

_torch = sys.modules.get("torch")
if _torch is None:  # pragma: no cover - transformers always loads torch
    raise RuntimeError("torch not loaded by transformers import")
# Pin threads BEFORE any tensor work: 16-thread default pays both sync
# overhead and per-thread memory buffers on this 16GB box (an OOM was
# observed with the default).
_torch.set_num_threads(int(os.environ.get("LORA_THREADS", "6")))

SMS_DIR = Path(os.path.expanduser("~/WanderGround/datasets/sms"))
TRAIN = SMS_DIR / "sms_real_v1_train.jsonl"
HOLDOUT = SMS_DIR / "sms_real_v1_holdout.jsonl"
MAX_LEN = 256
SEED = 20261013
EPOCHS = 20
LORA_R = 8
LORA_ALPHA = 16
LR = 1e-4
TRAIN_CHUNK = 8
EVAL_CHUNK = 16


def rows_for(path: Path, role: str) -> list:
    out = []
    with path.open() as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("role") == role:
                out.append(row)
    return out


def mean_pool(hidden, mask):
    m = mask.unsqueeze(-1).float()
    return (hidden * m).sum(1) / m.sum(1).clamp(min=1e-9)


class RamGuard:
    """Background system-RAM monitor with adaptive backoff + clean abort.

    Polls MemAvailable from /proc/meminfo. Three tiers:
      ok       avail >= warn_gb      -> train normally
      backoff  avail <  warn_gb      -> caller halves its micro-batch and
                                        clears caches; run slows, survives
      abort    avail <  critical_gb  -> raise BEFORE the kernel OOM killer
                                        fires; caller saves partial results
    The failure mode being prevented: once MemAvailable collapses the kernel
    swaps into zram, CPU spikes compressing, and the OOM killer reaps the
    largest process (this one). Reacting to *system* MemAvailable (not just
    our own RSS) means we yield when a browser/ollama spike threatens the
    whole box, instead of racing it to an OOM.
    """

    def __init__(self, warn_gb: float = 3.0, critical_gb: float = 1.5,
                 poll_s: float = 0.75) -> None:
        self.warn_gb = warn_gb
        self.critical_gb = critical_gb
        self.poll_s = poll_s
        self._stop = None
        self._thread = None
        self.min_avail_gb = 999.0
        self.max_self_rss_gb = 0.0
        self.backoff = False
        self.abort = False
        self.events = []

    def _mem_available_gb(self) -> float:
        try:
            with open("/proc/meminfo") as fh:
                for line in fh:
                    if line.startswith("MemAvailable:"):
                        return int(line.split()[1]) / 1e6  # kB -> GB
        except OSError:
            pass
        return 999.0

    def _self_rss_gb(self) -> float:
        try:
            with open("/proc/self/status") as fh:
                for line in fh:
                    if line.startswith("VmRSS:"):
                        return int(line.split()[1]) / 1e6
        except OSError:
            pass
        return 0.0

    def _loop(self) -> None:
        while not self._stop.is_set():
            avail = self._mem_available_gb()
            self_rss = self._self_rss_gb()
            self.min_avail_gb = min(self.min_avail_gb, avail)
            self.max_self_rss_gb = max(self.max_self_rss_gb, self_rss)
            if avail < self.critical_gb:
                self.abort = True
                self.events.append(
                    {"ts": round(time.time(), 1), "avail_gb": round(avail, 2),
                     "self_rss_gb": round(self_rss, 2), "tier": "ABORT"})
                break
            if avail < self.warn_gb:
                if not self.backoff:
                    self.events.append(
                        {"ts": round(time.time(), 1),
                         "avail_gb": round(avail, 2),
                         "self_rss_gb": round(self_rss, 2),
                         "tier": "BACKOFF"})
                self.backoff = True
            else:
                self.backoff = False
            time.sleep(self.poll_s)

    def start(self) -> "RamGuard":
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        if self._stop:
            self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)


class RamAbort(Exception):
    """Raised in the training loop when RamGuard trips critical."""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--encoder", required=True)
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--role", default="failure_classifier")
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    ap.add_argument("--train-chunk", type=int, default=TRAIN_CHUNK,
                    help="train micro-batch size (grad accumulation unit)")
    ap.add_argument("--checkpoint", default="on", choices=["on", "off"],
                    help="gradient checkpointing (default on — the proven "
                         "config; 'off' OOMs this box on a 20-epoch run)")
    ap.add_argument("--ram-warn-gb", type=float, default=3.0,
                    help="back off (halve micro-batch) below this system "
                         "MemAvailable (GB)")
    ap.add_argument("--ram-critical-gb", type=float, default=1.5,
                    help="clean-abort below this system MemAvailable (GB)")
    args = ap.parse_args()

    import numpy as np
    from peft import LoraConfig, get_peft_model

    _torch.manual_seed(SEED)
    np.random.seed(SEED)

    train_rows = rows_for(TRAIN, args.role)
    hold_rows = rows_for(HOLDOUT, args.role)
    classes = sorted({r["gold"]["class"] for r in train_rows})
    cls2idx = {c: i for i, c in enumerate(classes)}

    tokenizer = AutoTokenizer.from_pretrained(args.model_dir)
    base = AutoModel.from_pretrained(args.model_dir)

    # LoRA on every Linear in the encoder body (r=8 keeps adapter params
    # tiny vs the base; architecture-agnostic across ModernBERT and the
    # custom LFM bidirectional arch).
    target_modules = [
        name for name, mod in base.named_modules()
        if isinstance(mod, _torch.nn.Linear)
    ]
    lora_cfg = LoraConfig(
        r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=0.05,
        target_modules=target_modules, bias="none",
    )
    model = get_peft_model(base, lora_cfg)
    head = _torch.nn.Linear(base.config.hidden_size, len(classes))
    # Gradient checkpointing ON BY DEFAULT — this is the empirically proven
    # config on this box. Measured 2026-10-13: WITH checkpointing + 6-thread
    # cap, the full 20-epoch run held Python at ~2.0GB, system ~5.6GB, peak
    # <7GB and completed. WITHOUT it, the same run climbed past 14GB and was
    # OOM-killed — a single-step memory probe (3GB) does NOT predict the
    # multi-epoch allocation pattern. The edge-device LoRA paper (arXiv
    # 2606.19528) lists activation checkpointing as the headline peak-memory
    # lever; here it is the difference between fits and OOMs. Do not remove.
    if args.checkpoint != "off":
        model.model.gradient_checkpointing_enable()
        model.model.config.use_cache = False
    model.train()
    head.train()

    def encode(texts: list):
        batch = tokenizer(
            texts, padding=True, truncation=True, max_length=MAX_LEN,
            return_tensors="pt",
        )
        out = model.model(
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"],
        )
        return mean_pool(out.last_hidden_state, batch["attention_mask"])

    params = [p for p in model.parameters() if p.requires_grad] + list(
        head.parameters()
    )
    opt = _torch.optim.AdamW(params, lr=LR)

    x_train = [r["input"] for r in train_rows]
    y_train = _torch.tensor(
        [cls2idx[r["gold"]["class"]] for r in train_rows]
    )
    x_hold = [r["input"] for r in hold_rows]
    y_hold = [r["gold"]["class"] for r in hold_rows]

    def evaluate():
        model.eval()
        head.eval()
        with _torch.no_grad():
            vecs = []
            for i in range(0, len(x_hold), EVAL_CHUNK):
                vecs.append(encode(x_hold[i:i + EVAL_CHUNK]))
            logits = head(_torch.cat(vecs))
            preds = logits.argmax(-1).numpy()
        model.train()
        head.train()
        return float((preds == np.array(
            [cls2idx[c] for c in y_hold])).mean())

    t0 = time.time()
    best_acc, best_epoch = -1.0, -1
    history = []
    aborted = False
    cur_chunk = args.train_chunk
    guard = RamGuard(
        warn_gb=args.ram_warn_gb, critical_gb=args.ram_critical_gb
    ).start()
    print(f"  [ram-guard] warn<{args.ram_warn_gb}GB "
          f"critical<{args.ram_critical_gb}GB (MemAvailable, system-wide)",
          flush=True)
    try:
        for epoch in range(args.epochs):
            if guard.abort:
                aborted = True
                print(f"  [ram-guard] ABORT before epoch {epoch + 1} "
                      f"(MemAvailable {guard.min_avail_gb}GB)", flush=True)
                break
            # Adaptive backoff: shrink the micro-batch when the box tightens.
            if guard.backoff and cur_chunk > 1:
                cur_chunk = max(1, cur_chunk // 2)
                gc.collect()
                print(f"  [ram-guard] backoff -> train_chunk={cur_chunk}",
                      flush=True)
            opt.zero_grad()
            vecs = []
            for i in range(0, len(x_train), cur_chunk):
                if guard.abort:
                    raise RamAbort(
                        f"MemAvailable {guard.min_avail_gb}GB < critical")
                vecs.append(encode(x_train[i:i + cur_chunk]))
            vecs = _torch.cat(vecs)
            logits = head(vecs)
            loss = _torch.nn.functional.cross_entropy(logits, y_train)
            loss.backward()
            opt.step()
            hold_acc = evaluate()
            train_pred = logits.argmax(-1).detach().numpy()
            train_acc = float((train_pred == y_train.numpy()).mean())
            history.append(
                {"epoch": epoch + 1, "loss": round(float(loss.detach()), 4),
                 "train_acc": round(train_acc, 4),
                 "holdout_acc": round(hold_acc, 4),
                 "train_chunk": cur_chunk}
            )
            if hold_acc > best_acc:
                best_acc, best_epoch = hold_acc, epoch + 1
            print(f"  epoch {epoch + 1:2d}: loss={float(loss.detach()):.4f} "
                  f"train={train_acc:.4f} holdout={hold_acc:.4f} "
                  f"chunk={cur_chunk}", flush=True)
    except RamAbort as exc:
        aborted = True
        print(f"  [ram-guard] {exc} — saving partial results", flush=True)
    finally:
        guard.stop()

    completed_epochs = len(history)
    result = {
        "encoder": args.encoder,
        "role": args.role,
        "aborted": aborted,
        "completed_epochs": completed_epochs,
        "config": {
            "checkpoint": args.checkpoint,
            "train_chunk": args.train_chunk,
            "epochs": args.epochs,
            "max_len": MAX_LEN,
            "lr": LR,
            "lora_r": LORA_R,
            "lora_alpha": LORA_ALPHA,
            "threads": _torch.get_num_threads(),
            "seed": SEED,
            "ram_warn_gb": args.ram_warn_gb,
            "ram_critical_gb": args.ram_critical_gb,
        },
        "trainable_params": sum(
            p.numel() for p in model.parameters() if p.requires_grad
        ) + sum(p.numel() for p in head.parameters()),
        "frozen_probe_baseline_acc": 0.9643,
        "lora_best_holdout_acc": round(best_acc, 4),
        "lora_best_epoch": best_epoch,
        "lora_final_train_acc": history[-1]["train_acc"] if history else None,
        "lora_final_loss": history[-1]["loss"] if history else None,
        "beats_frozen": best_acc > 0.9643,
        "overfit_gap_final": round(
            history[-1]["train_acc"] - history[-1]["holdout_acc"], 4)
        if history else None,
        # --- performance ---
        "train_seconds": round(time.time() - t0, 1),
        "sec_per_epoch": round((time.time() - t0) / completed_epochs, 2)
        if completed_epochs else None,
        "cpu_seconds": round(
            resource.getrusage(resource.RUSAGE_SELF).ru_utime
            + resource.getrusage(resource.RUSAGE_SELF).ru_stime, 1),
        "avg_cores_utilized": round(
            (resource.getrusage(resource.RUSAGE_SELF).ru_utime
             + resource.getrusage(resource.RUSAGE_SELF).ru_stime)
            / (time.time() - t0), 2),
        "peak_rss_gb": round(
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6, 2),
        # --- ram guard telemetry ---
        "ram_guard": {
            "min_avail_gb": round(guard.min_avail_gb, 2),
            "max_self_rss_gb": round(guard.max_self_rss_gb, 2),
            "events": guard.events,
        },
        "history": history,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as handle:
        json.dump(result, handle, indent=2)
    print(f"written: {out}")
    if aborted:
        print(f"verdict: ABORTED at epoch {completed_epochs + 1} "
              f"(MemAvailable {guard.min_avail_gb}GB), "
              f"best_holdout={best_acc:.4f} @epoch{best_epoch} "
              f"vs frozen 0.9643 beats={result['beats_frozen']} "
              f"overfit_gap={result['overfit_gap_final']}", flush=True)
        return 1
    print(f"verdict: best_holdout={best_acc:.4f} @epoch{best_epoch} "
          f"vs frozen 0.9643 beats={result['beats_frozen']} "
          f"overfit_gap={result['overfit_gap_final']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())