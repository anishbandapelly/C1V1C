"""Carbon accounting with an explicit boundary (master plan §4.4, §4.5.3).

Only components with a sourced factor are estimated; everything else is reported
as not estimated (None), never as zero.
"""
from __future__ import annotations

C_TO_CO2 = 44.0 / 12.0


def crown_cover_sequestration_tco2e(crown_area_m2: float, rate_tc_per_ha_yr: float, years: int) -> float:
    """IPCC (2006) settlements crown-cover method: area[ha] x rate[tC/ha/yr] x years x 44/12 [tCO2e]."""
    if crown_area_m2 < 0 or rate_tc_per_ha_yr < 0 or years < 0:
        raise ValueError("carbon inputs must be non-negative")
    return crown_area_m2 / 10_000.0 * rate_tc_per_ha_yr * years * C_TO_CO2


def net_co2e(sequestration: float | None, avoided: float | None, embodied: float | None, maintenance: float | None) -> float | None:
    """Net = avoided + sequestration - embodied - maintenance; None if no component is estimated."""
    parts = [sequestration, avoided]
    costs = [embodied, maintenance]
    if all(p is None for p in parts + costs):
        return None
    return sum(p for p in parts if p is not None) - sum(c for c in costs if c is not None)
