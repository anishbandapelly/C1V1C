"""Decision Explainer: deterministic, evidence-grounded explanations of stored runs.

All numbers come from the saved RunResult / ScenarioComparison. An optional Bedrock narrator may
rephrase the deterministic findings, but its output is accepted only if every number it states
matches a computed value; otherwise the deterministic narrative is used and labelled as such.
"""
from __future__ import annotations

import re

from c1v1c.schemas import METRIC_UNITS, METRICS, DecisionExplanation, RunResult, ScenarioComparison

LABEL = {"green_roof": "green roofs", "urban_forest": "urban forests", "rainwater_harvesting": "rainwater harvesting",
         "drainage_upgrade": "drainage improvements"}
METRIC_NAME = {"F": "flood (design-event runoff retained or conveyed)", "W": "usable water", "H": "heat-exposure reduction",
               "G": "carbon sequestration"}


def _fmt_inr(v: float) -> str:
    return f"INR {v / 1e7:.2f} crore"


def _kind(cid: str) -> tuple[str, str]:
    zone, t = cid.split(":", 1)
    return zone, t


def explain(run: RunResult, zone_names: dict[str, str], comparisons: list[ScenarioComparison] | None = None) -> DecisionExplanation:
    comparisons = comparisons or []
    nums: dict[str, float | None] = {}
    o = run.outcome
    if o is None:
        reasons = run.binding_constraints or [run.solver_message]
        return DecisionExplanation(
            run_id=run.run_id, headline=f"No feasible portfolio: {run.solver_message}", why_selected=[],
            why_rejected={}, alternatives_compared=[], improved=[], worsened=[], beneficiaries=[], underserved=[],
            binding_constraints=reasons, shock_findings=[], assumptions=run.assumptions, uncertainties=run.gaps,
            unintended_consequences=[], relevant_computed_numbers={"budget_available_inr": run.budget_available_inr,
                                                                  "committed_capex_inr": run.committed_capex_inr},
            source_ids=run.source_ids, narrative=deterministic_narrative_infeasible(run), explanation_source="deterministic",
            bedrock_status="not requested", validation_passed=True)
    nums.update(capex_inr=o.capex_inr, lcc_inr=o.lcc_inr, budget_available_inr=run.budget_available_inr,
                unallocated_inr=run.unallocated_inr, score=o.score)
    for m in METRICS:
        nums[f"metric_{m}"] = o.metrics[m]
    counts = run.selected_candidate_counts
    by_type: dict[str, int] = {}
    for cid, n in counts.items():
        by_type[_kind(cid)[1]] = by_type.get(_kind(cid)[1], 0) + n
    mix = ", ".join(f"{n} x {LABEL[t]}" for t, n in sorted(by_type.items(), key=lambda kv: -kv[1])) or "no projects"
    headline = (f"{run.request.mode} plan: {mix} for {_fmt_inr(o.capex_inr)} of {_fmt_inr(run.budget_available_inr)} available "
                f"(solver {run.solver_status}, scenario {run.scenario.name}).")
    contrib = sorted(run.score_contributions.items(), key=lambda kv: -abs(kv[1]))
    why = [f"The MILP maximised the weighted score {o.score:.4f} under the {run.request.mode} weights "
           f"({', '.join(f'{k} {v:.0%}' for k, v in run.request.weights.items())})."]
    why += [f"{k}: contributes {v:+.4f} to the score" + (f" ({METRIC_NAME[k]} {o.metrics[k]:,.1f} {METRIC_UNITS[k]})" if k in METRICS else "")
            for k, v in contrib if abs(v) > 1e-9]
    best_alt = None
    alts = []
    for a in run.alternatives:
        if a.outcome is None:
            continue
        diff = o.score - a.outcome.score
        nums[f"alt_{a.alternative_id}_score"] = a.outcome.score
        alts.append({"alternative": a.label, "method": a.method, "feasible": a.feasible, "capex_inr": a.outcome.capex_inr,
                     "score": round(a.outcome.score, 4), "score_gap_vs_selected": round(diff, 4),
                     **{m: round(a.outcome.metrics[m] or 0.0, 2) for m in METRICS},
                     "why_not_chosen": _why_not(a.outcome, o, diff)})
        if a.method != "baseline" and (best_alt is None or a.outcome.score > best_alt.outcome.score):
            best_alt = a
    if best_alt is not None:
        why.append(f"It scores {o.score - best_alt.outcome.score:+.4f} above the best evaluated alternative "
                   f"('{best_alt.label}'); the comparison is among enumerated feasible candidates, not a full Pareto frontier.")
    base = run.baseline_outcome
    improved, worsened = [], []
    for m in METRICS:
        v = o.metrics[m] or 0.0
        if v > 1e-9:
            improved.append(f"{METRIC_NAME[m]}: +{v:,.1f} {METRIC_UNITS[m]} versus no investment")
        elif v < -1e-9:
            worsened.append(f"{METRIC_NAME[m]}: {v:,.1f} {METRIC_UNITS[m]} versus no investment")
    if any(_kind(k)[1] == "urban_forest" for k in counts):
        worsened.append("Urban forests need irrigation (8 m3/month per plot in the assumption set), which is netted out of water.")
    if o.lcc_inr > o.capex_inr:
        worsened.append(f"Lifecycle cost {_fmt_inr(o.lcc_inr)} exceeds capital {_fmt_inr(o.capex_inr)} because of 10-year O&M.")
    beneficiaries, underserved = [], []
    per_capita = []
    for zid, z in run.outcomes_by_zone.items():
        pop = z["population"] or 1
        share = z.get("event_runoff_managed_share")
        per_capita.append((zid, z["capex_inr"] / pop))
        beneficiaries.append({"zone_id": zid, "zone": zone_names.get(zid, zid), "population": pop, "capex_inr": z["capex_inr"],
                              "inr_per_resident": round(z["capex_inr"] / pop, 1),
                              "flood_m3_per_1000": round(z["flood_m3_per_1000_residents"], 2),
                              "water_m3_yr_per_1000": round(z["water_per_1000_residents_m3_yr"], 2),
                              "heat_reduction_per_1000": round(z["heat_reduction_per_1000_residents"], 4),
                              "event_runoff_managed_share": None if share is None else round(share, 4)})
        nums[f"zone_{zid}_capex"] = z["capex_inr"]
        if z["capex_inr"] == 0:
            underserved.append(f"{zone_names.get(zid, zid)} receives no investment in this plan.")
    if per_capita:
        lo = min(per_capita, key=lambda t: t[1])
        hi = max(per_capita, key=lambda t: t[1])
        if hi[1] > 0 and lo[1] < 0.5 * hi[1] and lo[1] > 0:
            underserved.append(f"{zone_names.get(lo[0], lo[0])} receives INR {lo[1]:,.0f} per resident versus "
                               f"INR {hi[1]:,.0f} in {zone_names.get(hi[0], hi[0])}.")
    if o.benefit_gini is not None:
        nums["benefit_gini"] = o.benefit_gini
    binding = [_explain_binding(b, zone_names) for b in run.binding_constraints]
    shock = []
    for c in comparisons:
        b, a = c.b_original_under_shock, c.a_original_normal
        res = c.deltas.get("residual_runoff_m3", {})
        line = f"{c.scenario.name}: unchanged plan score {a.score:.4f} -> {b.score:.4f}"
        if res.get("A") is not None and res.get("B") is not None and abs(res["B"] - res["A"]) > 1e-6:
            line += f"; design-event runoff left unmanaged {res['A']:,.0f} -> {res['B']:,.0f} m3"
        if b.metrics.get("W") is not None and abs((b.metrics["W"] or 0) - (a.metrics["W"] or 0)) > 1e-6:
            line += f"; usable water {a.metrics['W']:,.1f} -> {b.metrics['W']:,.1f} m3/yr"
        if not c.b_feasible:
            line += " and it is no longer feasible (" + "; ".join(c.b_notes[:2]) + ")"
        if c.c_reoptimised.outcome is not None:
            line += f"; re-optimised plan scores {c.c_reoptimised.evaluated_score:.4f}"
            if c.additions or c.removals:
                line += f" (adds {_counts_text(c.additions)}; removes {_counts_text(c.removals)})"
        else:
            line += f"; re-optimisation status {c.c_reoptimised.solver_status}: {c.c_reoptimised.solver_message}"
        shock.append(line)
    unintended = _unintended(counts, run)
    uncert = list(run.gaps) + [
        "Scores depend on declared normalisation scales and weights; changing a weight can change the selected mix.",
        "Rainfall statistics come from 1971-2005 IMD grids; recent climate (2006-2025) is not represented in the zone inputs.",
    ]
    for c in comparisons:
        s = c.sensitivity.get("original")
        if s:
            uncert.append(f"Under {c.scenario.name}, the original plan's score ranges {s['min']:.4f}-{s['max']:.4f} across "
                          f"{s['cases']} disclosed perturbations (sensitivity range, not a confidence interval).")
    exp = DecisionExplanation(
        run_id=run.run_id, headline=headline, why_selected=why, why_rejected=dict(list(run.rejected.items())),
        alternatives_compared=alts, improved=improved, worsened=worsened, beneficiaries=beneficiaries, underserved=underserved,
        binding_constraints=binding, shock_findings=shock, assumptions=run.assumptions, uncertainties=uncert,
        unintended_consequences=unintended, relevant_computed_numbers=nums, source_ids=run.source_ids,
        narrative="", explanation_source="deterministic", bedrock_status="not requested", validation_passed=True)
    return exp.model_copy(update={"narrative": deterministic_narrative(exp)})


def _counts_text(d: dict[str, int]) -> str:
    return ", ".join(f"{n} x {LABEL[_kind(k)[1]]} in {_kind(k)[0]}" for k, n in d.items()) or "nothing"


def _why_not(alt, sel, diff) -> str:
    if alt.violations:
        return "infeasible: " + "; ".join(alt.violations[:2])
    worse = [METRIC_NAME[m] for m in METRICS if (alt.metrics[m] or 0) < (sel.metrics[m] or 0) - 1e-9]
    better = [METRIC_NAME[m] for m in METRICS if (alt.metrics[m] or 0) > (sel.metrics[m] or 0) + 1e-9]
    txt = f"weighted score lower by {diff:.4f}" if diff > 1e-9 else "equal weighted score"
    if better:
        txt += f"; better on {', '.join(better)}"
    if worse:
        txt += f"; worse on {', '.join(worse)}"
    return txt


def _explain_binding(b: str, names: dict[str, str]) -> str:
    if b == "capital":
        return "Capital budget: the remaining budget cannot buy another unit of any eligible project."
    if b.startswith("roof:"):
        return f"Shared eligible roof area in {names.get(b[5:], b[5:])} is fully used (green roofs and rainwater tanks compete for it)."
    if b.startswith("land:"):
        return f"Assumed plantable land in {names.get(b[5:], b[5:])} is fully used."
    if b.startswith("unit_cap:"):
        z, t = _kind(b[9:])
        return f"Programme cap reached for {LABEL[t]} in {names.get(z, z)}."
    if b.startswith("equity_floor"):
        return "The priority-zone benefit floor is binding."
    if b.startswith("commitment"):
        return f"Committed project kept: {b.split(':', 1)[1]}."
    return b


def _unintended(counts: dict[str, int], run: RunResult) -> list[str]:
    types = {_kind(k)[1] for k in counts}
    out = []
    if "drainage_upgrade" in types:
        out.append("Drain upgrades convey water faster; without downstream checks they can move flooding to lower wards.")
    if "urban_forest" in types:
        out.append("Urban forests need watering in drought years and years to mature; early cooling and carbon are lower.")
    if "green_roof" in types:
        out.append("Green roofs need structural checks and maintenance; poorly maintained roofs lose retention.")
    if "rainwater_harvesting" in types:
        out.append("Rainwater tanks yield little in drought; stored water needs quality management (mosquito breeding).")
    if {"green_roof", "rainwater_harvesting"} <= types:
        out.append("Green roofs and rainwater harvesting compete for the same eligible roofs.")
    out.append("Visible greening can raise property values and displace lower-income residents (gentrification risk).")
    return out


def deterministic_narrative(e: DecisionExplanation) -> str:
    parts = [e.headline]
    if len(e.why_selected) > 1:
        parts.append("Main drivers: " + "; ".join(e.why_selected[1:4]) + ".")
    if e.binding_constraints:
        parts.append("Limiting factors: " + " ".join(e.binding_constraints[:3]))
    if e.underserved:
        parts.append("Equity watch: " + " ".join(e.underserved[:2]))
    if e.shock_findings:
        parts.append("Stress tests: " + " ".join(e.shock_findings[:3]))
    parts.append("These are modelled screening estimates built on declared assumptions, not validated engineering forecasts.")
    return " ".join(parts)


def deterministic_narrative_infeasible(run: RunResult) -> str:
    return (f"No feasible portfolio exists for this request ({run.scenario.name}, {_fmt_inr(run.budget_available_inr)} available). "
            + " ".join(run.binding_constraints or [run.solver_message])
            + " No portfolio is shown because presenting one would violate a hard constraint.")


NUMBER = re.compile(r"(?<![A-Za-z_])[-+]?\d[\d,]*(?:\.\d+)?")


def numbers_supported(text: str, e: DecisionExplanation, tolerance: float = 0.02) -> tuple[bool, list[str]]:
    """Every number in generated text must match a number in the deterministic explanation."""
    allowed: list[float] = []
    source = " ".join([e.headline, e.narrative, *e.why_selected, *e.improved, *e.worsened, *e.underserved,
                       *e.binding_constraints, *e.shock_findings, *e.uncertainties, *e.assumptions])
    for m in NUMBER.findall(source):
        try:
            allowed.append(float(m.replace(",", "")))
        except ValueError:
            pass
    allowed += [float(v) for v in e.relevant_computed_numbers.values() if v is not None]
    allowed += [v / 1e7 for v in list(allowed)]
    bad = []
    for m in NUMBER.findall(text):
        try:
            v = float(m.replace(",", ""))
        except ValueError:
            continue
        if v in (0, 1, 2, 3, 4, 5, 10, 100):
            continue
        if not any(abs(v - a) <= tolerance * max(1.0, abs(a)) for a in allowed):
            bad.append(m)
    return not bad, bad
