"""Exact-match and F1 approximations over extracted field sets."""

from __future__ import annotations

from collections import Counter
from typing import Iterable


def token_f1(a: str, b: str) -> float:
    ta, tb = a.lower().split(), b.lower().split()
    if not ta or not tb:
        return 1.0 if ta == tb else 0.0
    common = Counter(ta) & Counter(tb)
    n = sum(common.values())
    if n == 0:
        return 0.0
    p, r = n / len(ta), n / len(tb)
    return 2 * p * r / (p + r)


def set_f1(pred: Iterable[str], gold: Iterable[str]) -> float:
    c_pred, c_gold = Counter(pred), Counter(gold)
    if not c_pred and not c_gold:
        return 1.0
    common = sum((c_pred & c_gold).values())
    if common == 0:
        return 0.0
    p, r = common / max(1, sum(c_pred.values())), common / max(1, sum(c_gold.values()))
    return 2 * p * r / (p + r)


def exact(a, b) -> float:
    return 1.0 if a == b else 0.0
