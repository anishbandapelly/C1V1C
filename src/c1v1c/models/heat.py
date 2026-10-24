"""Heat-exposure screening index (master plan §4.5.2).

H = 0.50 Tnorm + 0.30 Impervious + 0.20 (1 - Vegetation), bounded [0, 1].
Exposure load = population x H  [person-index units]. Not a temperature in degC.
"""
from __future__ import annotations

W_TEMP, W_IMPERV, W_VEG = 0.50, 0.30, 0.20


def normalise_temperature(t_c: float, lo: float = 20.0, hi: float = 45.0) -> float:
    """Tnorm = clip((T - 20) / 25, 0, 1) with illustrative 20-45 degC bounds."""
    return min(1.0, max(0.0, (t_c - lo) / (hi - lo)))


def heat_index(t_norm: float, impervious: float, vegetation: float) -> float:
    for name, v in (("t_norm", t_norm), ("impervious", impervious), ("vegetation", vegetation)):
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"{name} must be in [0,1], got {v}")
    return W_TEMP * t_norm + W_IMPERV * impervious + W_VEG * (1.0 - vegetation)


def exposure_load(population: float, h: float) -> float:
    return max(0.0, population) * h


def exposure_reduction(population: float, zone_area_m2: float, greened_m2: float, cooling_factor: float = 1.0,
                       current_vegetation: float = 0.0) -> float:
    """Reduction in exposure load from adding vegetated area [person-index units].

    Added vegetation fraction dV = greened_m2 / zone_area, capped so V <= 1.
    dH = W_VEG x dV x cooling_factor (drought lowers evaporative cooling).
    """
    if zone_area_m2 <= 0:
        raise ValueError("zone area must be positive")
    if not 0.0 <= cooling_factor <= 1.0:
        raise ValueError("cooling factor must be in [0,1]")
    dv = min(max(greened_m2, 0.0) / zone_area_m2, max(0.0, 1.0 - current_vegetation))
    return max(0.0, population) * W_VEG * dv * cooling_factor
