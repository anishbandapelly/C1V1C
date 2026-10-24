"""Per-unit benefit coefficients (MILP surrogate) and independent portfolio evaluation.

Metrics (master plan §5.2): F flood, W water, H heat, G carbon; plus equity and lifecycle cost.
The surrogate is linear per unit; the evaluator re-computes the portfolio with physical caps
(e.g. retained + conveyed volume cannot exceed the runoff the zone generates), so the two
can differ and both are reported (requirement CORE-04).
"""
from __future__ import annotations

from dataclasses import dataclass


from c1v1c.baseline import Baseline
from c1v1c.catalogue import ModelParameters
from c1v1c.models import carbon, equity, heat, hydrology
from c1v1c.schemas import (
    INTERVENTIONS, METRICS, Candidate, InterventionSpec, PortfolioOutcome, ScenarioParams, ZoneBaseline,
)

REFERENCE_BUDGET_INR = 20_000_000  # default 2 crore; fixes tau scales (frozen across portfolios and shocks)


@dataclass(frozen=True)
class Coefficients:
    """Per-unit physical effects b[k, m] for one scenario, plus equity and cost."""

    scenario_id: str
    per_unit: dict[str, dict[str, float]]          # candidate_id -> metric -> value per unit
    components: dict[str, dict[str, float]]        # candidate_id -> component -> value per unit
    equity: dict[str, float]                       # candidate_id -> equity units per unit
    lcc: dict[str, float]
    capex: dict[str, float]


@dataclass(frozen=True)
class Scales:
    tau: dict[str, float]          # F, W, H, G
    tau_equity: float
    tau_cost: float
    reference_budget_inr: float


def _zone_area_m2(z: ZoneBaseline) -> float:
    return float(z.area_ha.value) * 10_000.0


_RWH_CACHE: dict[tuple, dict] = {}


def rwh_yield(baseline: Baseline, zone: ZoneBaseline, spec: InterventionSpec, params: ModelParameters, factor: float) -> dict:
    """Daily tank simulation over the zone's full rainfall record (one tank). Cached because it is
    a pure function of the baseline, the tank specification and the rainfall factor."""
    eff, demand = float(params["rwh_collection_efficiency"]), float(params["rwh_demand_m3_day"])
    key = (baseline.sha256, zone.rainfall_cell, spec.roof_m2, eff, spec.tank_capacity_m3, demand, round(factor, 9))
    if key not in _RWH_CACHE:
        series = baseline.rain[zone.rainfall_cell]
        _RWH_CACHE[key] = hydrology.annual_harvest_m3(series.rain_mm, series.years, spec.roof_m2, eff,
                                                      spec.tank_capacity_m3, demand, factor)
    return _RWH_CACHE[key]


def unit_effects(baseline: Baseline, zone: ZoneBaseline, spec: InterventionSpec, params: ModelParameters,
                 scenario: ScenarioParams) -> tuple[dict[str, float], dict[str, float]]:
    """Physical effect of ONE unit of ``spec`` in ``zone`` under ``scenario``."""
    p_event = float(zone.design_event_mm.value) * scenario.design_intensity_multiplier
    t = spec.intervention_type
    comp: dict[str, float] = {}
    f = w = h = g = 0.0
    if t == "green_roof":
        retained_mm = min(spec.retention_depth_mm, float(params["c_impervious"]) * p_event)
        f = comp["retained_m3_event"] = retained_mm * spec.roof_m2 / 1000.0
        h = comp["exposure_reduction"] = heat.exposure_reduction(
            float(zone.population.value), _zone_area_m2(zone), spec.roof_m2, 1.0, float(zone.vegetation_fraction.value))
    elif t == "urban_forest":
        dc = max(0.0, float(params["c_pervious"]) - float(params["c_vegetated_plot"]))
        f = comp["runoff_reduction_m3_event"] = dc * p_event * spec.land_m2 / 1000.0
        irrigation = spec.irrigation_m3_month * 12.0
        comp["irrigation_m3_yr"] = irrigation
        w = -irrigation
        h = comp["exposure_reduction"] = heat.exposure_reduction(
            float(zone.population.value), _zone_area_m2(zone), spec.land_m2, scenario.tree_cooling_factor,
            float(zone.vegetation_fraction.value))
        crown = spec.land_m2 * float(params["forest_crown_fraction_avg_10y"])
        g = comp["sequestration_tco2e_10y"] = carbon.crown_cover_sequestration_tco2e(
            crown, float(params["crown_carbon_rate_tc_ha_yr"]), int(params["carbon_horizon_y"]))
    elif t == "rainwater_harvesting":
        y = rwh_yield(baseline, zone, spec, params, scenario.rainfall_availability_factor)
        w = comp["usable_water_m3_yr"] = y["mean_m3_yr"]
        comp["usable_water_p10_m3_yr"] = y["p10_m3_yr"]
        comp["usable_water_p90_m3_yr"] = y["p90_m3_yr"]
        comp["overflow_m3_yr"] = y["overflow_m3_yr"]
        captured = hydrology.harvest_potential_m3(p_event, spec.roof_m2, float(params["rwh_collection_efficiency"]))
        f = comp["captured_m3_event"] = min(spec.tank_capacity_m3, captured)
    elif t == "drainage_upgrade":
        f = comp["conveyed_m3_event"] = spec.drainage_capacity_delta_m3_s * float(params["design_storm_duration_h"]) * 3600.0
    return {"F": f, "W": w, "H": h, "G": g}, comp


def build_coefficients(baseline: Baseline, candidates: list[Candidate], specs: dict[str, InterventionSpec],
                       params: ModelParameters, scenario: ScenarioParams, scales: Scales | None = None) -> Coefficients:
    per_unit, comps, eq = {}, {}, {}
    pops = [float(z.population.value) for z in baseline.zones]
    mean_pop = sum(pops) / len(pops)
    for c in candidates:
        z = baseline.zone(c.zone_id)
        effects, comp = unit_effects(baseline, z, specs[c.intervention_type], params, scenario)
        per_unit[c.candidate_id] = effects
        comps[c.candidate_id] = comp
        if scales is not None:
            risk = sum(effects[m] / scales.tau[m] for m in ("F", "W", "H")) / 3.0
            eq[c.candidate_id] = float(z.vulnerability_weight.value) * risk * mean_pop / float(z.population.value)
        else:
            eq[c.candidate_id] = 0.0
    return Coefficients(scenario.scenario_id, per_unit, comps, eq,
                        {c.candidate_id: c.lcc_inr for c in candidates}, {c.candidate_id: c.capex_inr for c in candidates})


def reference_scales(baseline: Baseline, candidates: list[Candidate], specs: dict[str, InterventionSpec],
                     params: ModelParameters, normal: ScenarioParams) -> Scales:
    """tau_m = best single-type benefit per INR x reference budget, in the normal scenario.
    Computed on ALL intervention types regardless of planner selection so scales stay fixed."""
    coeffs = build_coefficients(baseline, candidates, specs, params, normal)
    tau = {}
    for m in METRICS:
        best = max((coeffs.per_unit[k][m] / coeffs.capex[k] for k in coeffs.per_unit if coeffs.capex[k] > 0), default=0.0)
        tau[m] = best * REFERENCE_BUDGET_INR if best > 0 else 1.0
    tau_cost = max(c.lcc_inr / c.capex_inr for c in candidates if c.capex_inr > 0) * REFERENCE_BUDGET_INR
    provisional = Scales(tau, 1.0, tau_cost, REFERENCE_BUDGET_INR)
    eq = build_coefficients(baseline, candidates, specs, params, normal, provisional).equity
    best_eq = max((eq[k] / coeffs.capex[k] for k in eq if coeffs.capex[k] > 0), default=0.0)
    return Scales(tau, best_eq * REFERENCE_BUDGET_INR if best_eq > 0 else 1.0, tau_cost, REFERENCE_BUDGET_INR)


def surrogate_score(counts: dict[str, int], coeffs: Coefficients, scales: Scales, weights: dict[str, float]) -> float:
    s = 0.0
    for k, n in counts.items():
        if not n:
            continue
        for m in METRICS:
            s += weights[m] * coeffs.per_unit[k][m] * n / scales.tau[m]
        s += weights["Equity"] * coeffs.equity[k] * n / scales.tau_equity
        s -= weights["LCC"] * coeffs.lcc[k] * n / scales.tau_cost
    return s


def evaluate_portfolio(baseline: Baseline, candidates: list[Candidate], counts: dict[str, int],
                       specs: dict[str, InterventionSpec], params: ModelParameters, scenario: ScenarioParams,
                       scales: Scales, weights: dict[str, float], budget_inr: float,
                       committed: dict[str, int] | None = None) -> PortfolioOutcome:
    """Independent evaluation with physical caps and hard-constraint checks."""
    by_id = {c.candidate_id: c for c in candidates}
    coeffs = build_coefficients(baseline, candidates, specs, params, scenario, scales)
    counts = {k: int(v) for k, v in counts.items() if int(v) > 0}
    violations: list[str] = []
    capex = sum(by_id[k].capex_inr * n for k, n in counts.items())
    lcc = sum(by_id[k].lcc_inr * n for k, n in counts.items())
    checks = {"budget": capex <= budget_inr + 1e-6}
    if not checks["budget"]:
        violations.append(f"capital {capex:,.0f} INR exceeds available {budget_inr:,.0f} INR")
    by_zone: dict[str, dict[str, float | None]] = {}
    totals = {m: 0.0 for m in METRICS}
    comp_tot: dict[str, dict[str, float | None]] = {t: {} for t in INTERVENTIONS}
    roof_ok = land_ok = cap_ok = elig_ok = True
    for z in baseline.zones:
        zc = {k: n for k, n in counts.items() if by_id[k].zone_id == z.zone_id}
        roof = sum(by_id[k].roof_m2 * n for k, n in zc.items())
        land = sum(by_id[k].land_m2 * n for k, n in zc.items())
        if z.eligible_roof_m2.value is not None and roof > float(z.eligible_roof_m2.value) + 1e-6:
            roof_ok = False
            violations.append(f"{z.zone_id}: roof use {roof:.0f} m2 exceeds eligible {z.eligible_roof_m2.value:.0f} m2")
        if z.plantable_land_m2.value is not None and land > float(z.plantable_land_m2.value) + 1e-6:
            land_ok = False
            violations.append(f"{z.zone_id}: land use {land:.0f} m2 exceeds plantable {z.plantable_land_m2.value:.0f} m2")
        for k, n in zc.items():
            if n > by_id[k].upper_bound:
                if by_id[k].eligibility != "eligible":
                    elig_ok = False
                    violations.append(f"{k}: {n} units selected but candidate is {by_id[k].eligibility} ({by_id[k].eligibility_reason})")
                else:
                    cap_ok = False
                    violations.append(f"{k}: {n} units exceed the maximum of {by_id[k].upper_bound}")
        f_raw = sum(coeffs.per_unit[k]["F"] * n for k, n in zc.items())
        event_runoff = float(z.design_event_runoff_m3.value) * scenario.design_intensity_multiplier
        f = min(f_raw, event_runoff)
        w = sum(coeffs.per_unit[k]["W"] * n for k, n in zc.items())
        greened = sum(specs[by_id[k].intervention_type].roof_m2 * n for k, n in zc.items() if by_id[k].intervention_type == "green_roof")
        planted = sum(specs[by_id[k].intervention_type].land_m2 * n for k, n in zc.items() if by_id[k].intervention_type == "urban_forest")
        area = _zone_area_m2(z)
        pop = float(z.population.value)
        veg0 = float(z.vegetation_fraction.value)
        h_roof = heat.exposure_reduction(pop, area, greened, 1.0, veg0)
        h_forest = heat.exposure_reduction(pop, area, planted, scenario.tree_cooling_factor, min(1.0, veg0 + greened / area))
        h = h_roof + h_forest
        g = sum(coeffs.per_unit[k]["G"] * n for k, n in zc.items())
        h0 = float(z.heat_index.value) * pop
        by_zone[z.zone_id] = {
            "F": f, "W": w, "H": h, "G": g,
            "capex_inr": sum(by_id[k].capex_inr * n for k, n in zc.items()),
            "design_event_runoff_m3": event_runoff,
            "event_runoff_managed_share": f / event_runoff if event_runoff > 0 else None,
            "residual_runoff_m3": event_runoff - f,
            "heat_exposure_baseline": h0,
            "heat_exposure_after": h0 - h,
            "population": pop,
            "water_per_1000_residents_m3_yr": equity.per_1000_residents(w, pop),
            "heat_reduction_per_1000_residents": equity.per_1000_residents(h, pop),
            "flood_m3_per_1000_residents": equity.per_1000_residents(f, pop),
            "roof_used_m2": roof, "land_used_m2": land,
        }
        for m, v in (("F", f), ("W", w), ("H", h), ("G", g)):
            totals[m] += v
        for k, n in zc.items():
            t = by_id[k].intervention_type
            for name, val in coeffs.components[k].items():
                comp_tot[t][name] = (comp_tot[t].get(name) or 0.0) + val * n
    checks.update(roof=roof_ok, land=land_ok, unit_caps=cap_ok, eligibility=elig_ok)
    committed = committed or {}
    commit_ok = all(counts.get(k, 0) >= n for k, n in committed.items())
    checks["commitments"] = commit_ok
    if not commit_ok:
        violations.append("committed projects were removed from the portfolio")
    norm = {m: totals[m] / scales.tau[m] for m in METRICS}
    mean_pop = sum(float(z.population.value) for z in baseline.zones) / len(baseline.zones)
    eq_gain = sum(
        float(z.vulnerability_weight.value) * (sum(by_zone[z.zone_id][m] / scales.tau[m] for m in ("F", "W", "H")) / 3.0)
        * mean_pop / float(z.population.value) for z in baseline.zones) / scales.tau_equity
    norm["Equity"] = eq_gain
    norm["LCC"] = lcc / scales.tau_cost
    score = sum(weights[m] * norm[m] for m in METRICS) + weights["Equity"] * eq_gain - weights["LCC"] * norm["LCC"]
    per_capita = {z.zone_id: max(0.0, sum(by_zone[z.zone_id][m] / scales.tau[m] for m in ("F", "W", "H")))
                  / max(float(z.population.value), 1) for z in baseline.zones}
    gini = equity.gini(per_capita) if any(per_capita.values()) else None
    metrics: dict[str, float | None] = dict(totals)
    if not any(by_id[k].intervention_type == "urban_forest" for k in counts):
        metrics["G"] = 0.0
    return PortfolioOutcome(
        scenario_id=scenario.scenario_id, counts=counts, capex_inr=capex, lcc_inr=lcc, metrics=metrics,
        metric_components={t: v for t, v in comp_tot.items() if v}, by_zone=by_zone, normalised=norm, score=score,
        equity_gain=eq_gain, benefit_gini=gini, constraint_checks=checks, violations=violations,
    )


def zero_outcome_metrics() -> dict[str, float]:
    return {m: 0.0 for m in METRICS}


__all__ = ["Coefficients", "Scales", "build_coefficients", "reference_scales", "evaluate_portfolio",
           "surrogate_score", "unit_effects", "REFERENCE_BUDGET_INR"]
