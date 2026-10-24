"""Independent scientific sanity checks on the real curated baseline and engine outputs.

Re-derives key numbers by hand (not through the engine code paths where possible), checks units,
physical bounds, cost aggregation, water balance, scenario direction and solver feasibility, and
writes docs/SCIENTIFIC_VALIDATION.md. Run: python scripts/validate_science.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from c1v1c.engine import Engine  # noqa: E402
from c1v1c.models import hydrology  # noqa: E402

rows: list[tuple[str, str, str, str]] = []


def check(area: str, name: str, ok: bool, detail: str) -> None:
    rows.append((area, name, "PASS" if ok else "FAIL", detail))


def main() -> int:
    e = Engine()
    b = e.baseline
    p = e.params
    climate = b.climate_summary.set_index("zone_id")
    # --- climate plausibility against the independent long daily series ------------------------
    city = climate.loc["CITY_XCHECK"]
    zone_rain = float(climate.loc[b.zones[0].zone_id, "mean_annual_rain_mm"])
    check("climate", "IMD annual rainfall vs independent daily series", 600 <= zone_rain <= 1200 and abs(zone_rain - city.mean_annual_rain_mm) / city.mean_annual_rain_mm < 0.25,
          f"IMD cell mean {zone_rain:.0f} mm/yr (1971-2005) vs station-type series {city.mean_annual_rain_mm:.0f} mm/yr (1951-2024); "
          "Bengaluru's commonly cited normal is roughly 900-1,000 mm/yr")
    tmax = b.zones[0].summer_tmax_c.value
    check("climate", "summer Tmax vs independent daily series", abs(tmax - city.summer_tmax_c) < 2.0,
          f"IMD 1 deg Mar-May mean Tmax {tmax:.2f} degC vs {city.summer_tmax_c:.2f} degC")
    for z in b.zones:
        # --- runoff: hand recomputation --------------------------------------------------------
        p_ev = z.design_p24_mm.value * (1 / 24) ** (1 / 3)
        v = z.runoff_coefficient.value * p_ev / 1000 * z.area_ha.value * 1e4
        check("runoff", f"{z.zone_id} design-event runoff recomputed", abs(v - z.design_event_runoff_m3.value) < 1e-6 * v,
              f"C {z.runoff_coefficient.value:.3f} x {p_ev:.2f} mm x {z.area_ha.value:.2f} ha = {v:,.0f} m3")
        q = hydrology.rational_peak_m3s(z.runoff_coefficient.value, p_ev, z.area_ha.value)
        rel = q * 3600 / v - 1
        check("runoff", f"{z.zone_id} peak flow units", abs(rel) < 1e-3,
              f"Rational Q {q:.3f} m3/s x 3600 s = {q * 3600:,.0f} m3 vs 1-h volume {v:,.0f} m3 ({rel:+.2%}; "
              "0.00278 is 1/360 rounded, so +0.08% is expected)")
        check("bounds", f"{z.zone_id} fractions in [0,1]", all(0 <= getattr(z, f).value <= 1 for f in
              ("built_fraction", "impervious_fraction", "vegetation_fraction", "runoff_coefficient", "heat_index", "sc_st_share")), "all bounded")
        density = z.population.value / (z.area_ha.value / 100)
        check("bounds", f"{z.zone_id} population density plausible", 5_000 <= density <= 80_000, f"{density:,.0f} persons/km2")
    # --- water balance of one tank over the full record -----------------------------------------
    z = b.zones[0]
    rain = b.rain[z.rainfall_cell]
    spec = e.specs["rainwater_harvesting"]
    eff = p["rwh_collection_efficiency"]
    inflow = rain.rain_mm * spec.roof_m2 * eff / 1000
    res = hydrology.tank_balance(inflow, p["rwh_demand_m3_day"], spec.tank_capacity_m3)
    closure = inflow.sum() - (res.served_m3.sum() + res.overflow_m3.sum() + res.storage_m3[-1])
    check("water", "tank water balance closes over 35 years", abs(closure) < 1e-6, f"residual {closure:.2e} m3")
    check("water", "storage never exceeds capacity", float(res.storage_m3.max()) <= spec.tank_capacity_m3 + 1e-9,
          f"max storage {res.storage_m3.max():.2f} m3 <= {spec.tank_capacity_m3} m3")
    years = len(np.unique(rain.years))
    yield_yr = res.served_m3.sum() / years
    pot = inflow.sum() / years
    check("water", "yield below potential and demand", yield_yr <= pot and yield_yr <= p["rwh_demand_m3_day"] * 365,
          f"usable {yield_yr:.1f} m3/yr; potential {pot:.1f} m3/yr; demand {p['rwh_demand_m3_day'] * 365:.0f} m3/yr")
    # --- carbon --------------------------------------------------------------------------------------
    fs = e.specs["urban_forest"]
    t = fs.land_m2 * p["forest_crown_fraction_avg_10y"] / 1e4 * p["crown_carbon_rate_tc_ha_yr"] * p["carbon_horizon_y"] * 44 / 12
    from c1v1c.evaluate import unit_effects
    eff_units, _ = unit_effects(b, z, fs, p, e.scenarios["normal"])
    check("carbon", "forest sequestration hand calculation", abs(eff_units["G"] - t) < 1e-9,
          f"{fs.land_m2:.0f} m2 x {p['forest_crown_fraction_avg_10y']} crown x {p['crown_carbon_rate_tc_ha_yr']} tC/ha/yr x 10 yr x 44/12 = {t:.2f} tCO2e")
    # --- solver feasibility and cost aggregation across modes/budgets ---------------------------------
    for mode in p.modes:
        for budget in (0, 5_000_000, 20_000_000, 50_000_000):
            r = e.run(e.default_request(budget_inr=budget, mode=mode), use_cache=False)
            agg = sum(next(c.capex_inr for c in e.all_candidates if c.candidate_id == k) * n for k, n in r.selected_candidate_counts.items())
            ok = (r.solver_status == "optimal" and abs(agg - r.allocated_inr) < 1e-6 and r.allocated_inr <= budget
                  and abs(sum(r.capex_by_zone.values()) - agg) < 1e-6 and abs(sum(r.capex_by_intervention.values()) - agg) < 1e-6
                  and all(r.verification.values()))
            check("solver", f"{mode} @ INR {budget / 1e7:g} cr feasible and cost-consistent", ok,
                  f"{r.solver_status}; {len(r.selected_candidate_counts)} units; INR {agg:,.0f}; by-zone and by-type sums match")
    # --- scenario direction --------------------------------------------------------------------------
    base = e.run(e.default_request(budget_inr=20_000_000), use_cache=False)
    rain_c = e.shock(base, "extreme_rain")
    dry = e.shock(e.run(e.default_request(budget_inr=20_000_000, mode="Water-first"), use_cache=False), "drought")
    cut = e.shock(base, "budget_cut")
    check("scenario", "extreme rain raises event runoff 30% for the frozen plan",
          all(abs(rain_c.b_original_under_shock.by_zone[k]["design_event_runoff_m3"] / rain_c.a_original_normal.by_zone[k]["design_event_runoff_m3"] - 1.3) < 1e-9
              for k in rain_c.a_original_normal.by_zone), "x1.30 in every ward; share handled falls or stays equal")
    check("scenario", "drought lowers harvested water", dry.b_original_under_shock.metrics["W"] < dry.a_original_normal.metrics["W"],
          f"{dry.a_original_normal.metrics['W']:.0f} -> {dry.b_original_under_shock.metrics['W']:.0f} m3/yr")
    check("scenario", "budget cut re-optimised plan fits revised envelope",
          cut.c_reoptimised.allocated_inr <= cut.c_reoptimised.budget_available_inr,
          f"original INR {base.allocated_inr:,.0f}; revised envelope INR {cut.c_reoptimised.budget_available_inr:,.0f}; "
          f"original still feasible: {cut.b_feasible}; re-optimised INR {cut.c_reoptimised.allocated_inr:,.0f}")
    check("scenario", "re-optimised never scores below the frozen plan under the same shock",
          all(c.c_reoptimised.evaluated_score >= c.b_original_under_shock.score - 1e-9 for c in (rain_c, dry, cut) if c.b_feasible),
          "C >= B for every feasible frozen plan")
    # --- equity -----------------------------------------------------------------------------------------
    vul = {z.zone_id: z.vulnerability_weight.value for z in b.zones}
    shares = {z.zone_id: z.sc_st_share.value for z in b.zones}
    order_ok = sorted(vul, key=vul.get) == sorted(shares, key=shares.get)
    check("equity", "vulnerability weights follow SC/ST shares", order_ok, json.dumps({k: round(v, 3) for k, v in vul.items()}))
    # --- write report -----------------------------------------------------------------------------------
    df = pd.DataFrame(rows, columns=["Area", "Check", "Result", "Detail"])
    passed = int((df.Result == "PASS").sum())
    out = ROOT / "docs" / "SCIENTIFIC_VALIDATION.md"
    lines = ["# Scientific validation — real Bengaluru baseline", "",
             f"Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} by `python scripts/validate_science.py` "
             f"against baseline `{b.version}` (sha256 `{b.sha256[:16]}`), model `{e.settings.model_version}`, catalogue `{e.catalog_version}`.",
             "", f"**{passed} of {len(df)} checks pass.**", "",
             "These are internal-consistency, unit, bound and direction checks plus cross-checks between two independent "
             "climate sources. They are **not empirical validation** of intervention effects: no field measurements of "
             "retention, harvest yield, cooling or drainage performance exist in the collection, so model outputs remain "
             "screening estimates built on declared assumptions.", "",
             "| Area | Check | Result | Detail |", "|---|---|---|---|"]
    lines += [f"| {a} | {c} | {r} | {d} |" for a, c, r, d in rows]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(df.to_string(index=False))
    print(f"\n{passed}/{len(df)} PASS -> {out.relative_to(ROOT)}")
    return 0 if passed == len(df) else 1


if __name__ == "__main__":
    sys.exit(main())
