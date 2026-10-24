"""Rainfall, runoff and rainwater-harvesting models (master plan §4.1, §4.2, §4.5.1).

All functions are pure and unit-explicit. They describe screening indicators for a
design event; they do not predict street-level flood depth or inundation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

RATIONAL_K = 0.00278  # converts C x I[mm/h] x A[ha] to m3/s


def rational_peak_m3s(c: float, intensity_mm_h: float, area_ha: float) -> float:
    """Rational Method peak runoff Q = 0.00278 C I A  [m3/s].

    Valid only for small catchments whose time of concentration is close to the
    design-storm duration. ``c`` is a dimensionless runoff coefficient in [0, 1].
    """
    if not 0.0 <= c <= 1.0:
        raise ValueError(f"runoff coefficient must be in [0,1], got {c}")
    if intensity_mm_h < 0 or area_ha < 0:
        raise ValueError("intensity and area must be non-negative")
    return RATIONAL_K * c * intensity_mm_h * area_ha


def exceedance_m3s(peak_m3s: float, capacity_m3s: float) -> float:
    """Peak flow above conveyance capacity [m3/s]; drainage changes capacity, not generation."""
    return max(0.0, peak_m3s - capacity_m3s)


def imd_short_duration_depth_mm(p24_mm: float, duration_h: float) -> float:
    """IMD empirical reduction formula P_t = P_24 (t/24)^(1/3) [mm].

    Converts a 24-hour (daily) depth to a shorter-duration depth when no
    sub-daily record is available. Literature method (C grade), not a local IDF curve.
    """
    if p24_mm < 0 or not 0 < duration_h <= 24:
        raise ValueError("p24 must be >= 0 and duration in (0, 24] h")
    return p24_mm * (duration_h / 24.0) ** (1.0 / 3.0)


def composite_runoff_coefficient(impervious_fraction: float, c_impervious: float, c_pervious: float) -> float:
    """Area-weighted runoff coefficient for a mix of impervious and pervious surfaces."""
    f = min(1.0, max(0.0, impervious_fraction))
    return f * c_impervious + (1.0 - f) * c_pervious


def harvest_potential_m3(rain_mm: float, catchment_m2: float, efficiency: float) -> float:
    """Rainwater potential V = P[mm] x A[m2] x efficiency / 1000 [m3]."""
    if not 0.0 <= efficiency <= 1.0:
        raise ValueError("collection efficiency must be in [0,1]")
    return max(0.0, rain_mm) * catchment_m2 * efficiency / 1000.0


@dataclass(frozen=True)
class TankResult:
    served_m3: np.ndarray
    storage_m3: np.ndarray
    overflow_m3: np.ndarray
    inflow_m3: np.ndarray

    @property
    def total_served(self) -> float:
        return float(self.served_m3.sum())


def tank_balance(inflow_m3: Sequence[float], demand_m3: Sequence[float] | float, capacity_m3: float, initial_m3: float = 0.0) -> TankResult:
    """Daily storage balance, ordered inflow -> overflow -> demand (master plan §4.5.1).

    A[t] = S[t-1] + P[t]; overflow = max(0, A-K); available = min(K, A);
    served = min(D, available); S[t] = available - served.  0 <= S <= K always holds.
    """
    if capacity_m3 < 0:
        raise ValueError("tank capacity must be non-negative")
    inflow = np.asarray(inflow_m3, dtype=float)
    if np.any(inflow < 0):
        raise ValueError("inflow must be non-negative")
    demand = np.broadcast_to(np.asarray(demand_m3, dtype=float), inflow.shape)
    served = np.zeros_like(inflow)
    storage = np.zeros_like(inflow)
    overflow = np.zeros_like(inflow)
    s = min(max(initial_m3, 0.0), capacity_m3)
    for t in range(inflow.size):
        a = s + inflow[t]
        overflow[t] = max(0.0, a - capacity_m3)
        available = min(capacity_m3, a)
        served[t] = min(demand[t], available)
        s = available - served[t]
        storage[t] = s
    assert np.all(storage >= -1e-9) and np.all(storage <= capacity_m3 + 1e-9)
    return TankResult(served, storage, overflow, inflow)


def annual_harvest_m3(daily_rain_mm: np.ndarray, years: np.ndarray, catchment_m2: float, efficiency: float,
                      capacity_m3: float, demand_m3_day: float, rain_factor: float = 1.0) -> dict:
    """Simulate a tank over a daily rainfall record and summarise usable water per year [m3/yr]."""
    rain = np.clip(np.asarray(daily_rain_mm, dtype=float) * rain_factor, 0, None)
    inflow = rain * catchment_m2 * efficiency / 1000.0
    res = tank_balance(inflow, demand_m3_day, capacity_m3)
    yrs = np.asarray(years)
    per_year = {int(y): float(res.served_m3[yrs == y].sum()) for y in np.unique(yrs)}
    values = np.array(list(per_year.values()))
    return {
        "mean_m3_yr": float(values.mean()),
        "p10_m3_yr": float(np.percentile(values, 10)),
        "p90_m3_yr": float(np.percentile(values, 90)),
        "potential_m3_yr": float(inflow.sum() / len(per_year)),
        "overflow_m3_yr": float(res.overflow_m3.sum() / len(per_year)),
        "years": len(per_year),
    }
