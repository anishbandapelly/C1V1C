"""Population-weighted equity (master plan §5.6).

EquityGain = sum_z v_z x RiskReduction_z / max(Population_z, 1) / tau_equity.
Equity is a distribution preference, not additional physical risk reduction.
"""
from __future__ import annotations

from typing import Mapping


def vulnerability_weight(sc_st_share: float, city_mean_share: float, alpha: float = 1.0) -> float:
    """v_z = 1 + alpha x (share_z / city_mean - 1), floored at 0.25: zones with a larger
    Scheduled Caste / Scheduled Tribe population share receive a higher weight."""
    if city_mean_share <= 0:
        raise ValueError("city mean share must be positive")
    return max(0.25, 1.0 + alpha * (sc_st_share / city_mean_share - 1.0))


def per_1000_residents(value: float, population: float) -> float:
    return value / max(population, 1.0) * 1000.0


def gini(values: Mapping[str, float] | list[float]) -> float:
    """Gini coefficient of non-negative benefits (0 = equal, 1 = concentrated)."""
    xs = sorted(max(0.0, float(v)) for v in (values.values() if isinstance(values, Mapping) else values))
    n = len(xs)
    total = sum(xs)
    if n == 0 or total == 0:
        return 0.0
    cum = sum((i + 1) * x for i, x in enumerate(xs))
    return (2 * cum) / (n * total) - (n + 1) / n
