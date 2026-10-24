"""Lifecycle cost (master plan §4.5.4): LCC = capex + sum_t M_t / (1 + r)^t."""
from __future__ import annotations


def present_value_factor(rate: float, years: int) -> float:
    if rate <= -1 or years < 0:
        raise ValueError("invalid discount rate or horizon")
    return sum(1.0 / (1.0 + rate) ** t for t in range(1, years + 1))


def lifecycle_cost_inr(capex_inr: float, annual_om_inr: float, rate: float = 0.05, years: int = 10) -> float:
    if capex_inr < 0 or annual_om_inr < 0:
        raise ValueError("costs must be non-negative")
    return capex_inr + annual_om_inr * present_value_factor(rate, years)


CRORE = 10_000_000


def crore_to_inr(crore: float) -> int:
    return int(round(crore * CRORE))
