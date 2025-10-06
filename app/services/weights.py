from __future__ import annotations
from typing import List, Tuple
def normalize_weights(pairs: List[Tuple[int, float]]) -> list[tuple[int, float]]:
    total = sum(max(0.0, w) for _, w in pairs)
    n = len(pairs) or 1
    if total <= 0.0:
        even = 1.0 / n
        return [(i, even) for i, _ in pairs]
    return [(i, (max(0.0, w) / total)) for i, w in pairs]
