"""Mixed-integer portfolio optimisation with PuLP/CBC (master plan §5).

max  sum_m w_m * sum_k b[k,m] x_k / tau_m  +  w_E * sum_k e_k x_k / tau_E  -  w_C * sum_k LCC_k x_k / tau_C
s.t. sum_k capex_k x_k                       <= B_available                       (capital)
     sum_{k in z} roof_k x_k                 <= eligible_roof_z                  (shared roof, per zone)
     sum_{k in z} land_k x_k                 <= plantable_land_z                 (land, per zone)
     0 <= x_k <= ub_k  (ub_k = 0 if ineligible / not estimable / deselected)     (eligibility, capacity)
     x_a <= ub_a * x_b  if a requires b;   y_a + y_b <= 1 if a excludes b         (dependencies)
     x_k >= committed_k                                                           (commitments)
     benefit_priority_zone >= floor * benefit_all_zones                          (equity floor)
     x_k integer

Infeasible problems are reported as infeasible with a diagnosed reason; constraints are never relaxed.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import pulp

from c1v1c.baseline import Baseline
from c1v1c.evaluate import Coefficients, Scales
from c1v1c.schemas import METRICS, Candidate

STATUS_MAP = {
    pulp.LpStatusOptimal: "optimal",
    pulp.LpStatusInfeasible: "infeasible",
    pulp.LpStatusUnbounded: "error",
    pulp.LpStatusUndefined: "infeasible",
    pulp.LpStatusNotSolved: "error",
}


@dataclass
class SolveResult:
    status: str
    message: str
    counts: dict[str, int]
    objective: float | None
    runtime_s: float
    slack: dict[str, float] = field(default_factory=dict)
    binding: list[str] = field(default_factory=list)
    diagnosis: list[str] = field(default_factory=list)


def unit_value(k: str, coeffs: Coefficients, scales: Scales, weights: dict[str, float]) -> float:
    """Weighted normalised objective contribution of one unit of candidate k."""
    v = sum(weights[m] * coeffs.per_unit[k][m] / scales.tau[m] for m in METRICS)
    v += weights["Equity"] * coeffs.equity[k] / scales.tau_equity
    v -= weights["LCC"] * coeffs.lcc[k] / scales.tau_cost
    return v


def benefit_value(k: str, coeffs: Coefficients, scales: Scales, weights: dict[str, float]) -> float:
    """Weighted environmental benefit (no cost term), used by the equity-floor share constraint."""
    return sum(weights[m] * coeffs.per_unit[k][m] / scales.tau[m] for m in METRICS)


def solve(baseline: Baseline, candidates: list[Candidate], coeffs: Coefficients, scales: Scales,
          weights: dict[str, float], budget_inr: float, *, equity_floor: float = 0.0,
          committed: dict[str, int] | None = None, exclude_solutions: list[dict[str, int]] | None = None,
          min_distance: int = 2, time_limit_s: float = 20.0) -> SolveResult:
    committed = {k: v for k, v in (committed or {}).items() if v > 0}
    by_id = {c.candidate_id: c for c in candidates}
    start = time.perf_counter()
    if budget_inr < 0:
        return SolveResult("infeasible", "Available budget is negative.", {}, None, 0.0,
                           diagnosis=["capital: available budget below zero"])
    prob = pulp.LpProblem("c1v1c_portfolio", pulp.LpMaximize)
    x = {c.candidate_id: pulp.LpVariable(f"x_{i}", 0, c.upper_bound, cat="Integer") for i, c in enumerate(candidates)}
    prob += pulp.lpSum(unit_value(k, coeffs, scales, weights) * x[k] for k in x), "weighted_score"
    cons: dict[str, pulp.LpConstraint] = {}
    cons["capital"] = pulp.lpSum(by_id[k].capex_inr * x[k] for k in x) <= budget_inr
    for z in baseline.zones:
        zk = [k for k in x if by_id[k].zone_id == z.zone_id]
        if z.eligible_roof_m2.value is not None:
            cons[f"roof:{z.zone_id}"] = pulp.lpSum(by_id[k].roof_m2 * x[k] for k in zk) <= float(z.eligible_roof_m2.value)
        if z.plantable_land_m2.value is not None:
            cons[f"land:{z.zone_id}"] = pulp.lpSum(by_id[k].land_m2 * x[k] for k in zk) <= float(z.plantable_land_m2.value)
    for c in candidates:
        for req in c.requires:
            cons[f"requires:{c.candidate_id}>{req}"] = x[c.candidate_id] <= c.upper_bound * x[req]
    indicator: dict[str, pulp.LpVariable] = {}

    def used(k: str) -> pulp.LpVariable:
        """Binary y_k = 1 if any unit of k is built (x_k <= ub_k * y_k)."""
        if k not in indicator:
            indicator[k] = pulp.LpVariable(f"use_{len(indicator)}", cat="Binary")
            prob.addConstraint(x[k] <= max(1, by_id[k].upper_bound) * indicator[k])
        return indicator[k]

    pairs = {tuple(sorted((c.candidate_id, o))) for c in candidates for o in c.excludes}
    for a, b in sorted(pairs):
        cons[f"excludes:{a}|{b}"] = used(a) + used(b) <= 1
    for k, n in committed.items():
        if k not in x:
            return SolveResult("infeasible", f"Committed project {k} is not in the candidate catalogue.", {}, None, 0.0,
                               diagnosis=[f"commitment: unknown candidate {k}"])
        if n > by_id[k].upper_bound:
            return SolveResult("infeasible", f"Committed {n} units of {k} exceed its eligible maximum {by_id[k].upper_bound}.",
                               {}, None, 0.0, diagnosis=[f"commitment: {k} above capacity"])
        cons[f"commitment:{k}"] = x[k] >= n
    if equity_floor > 0:
        priority = max(baseline.zones, key=lambda z: float(z.vulnerability_weight.value)).zone_id
        bz = pulp.lpSum(benefit_value(k, coeffs, scales, weights) * x[k] for k in x if by_id[k].zone_id == priority)
        ball = pulp.lpSum(benefit_value(k, coeffs, scales, weights) * x[k] for k in x)
        cons[f"equity_floor:{priority}"] = bz >= equity_floor * ball
        # A floor must not be met trivially by investing nothing.
        cons["equity_floor_nontrivial"] = pulp.lpSum(benefit_value(k, coeffs, scales, weights) * x[k]
                                                     for k in x if by_id[k].zone_id == priority) >= 1e-6
    for i, sol in enumerate(exclude_solutions or []):
        dev = []
        for j, k in enumerate(x):
            ub = by_id[k].upper_bound
            if ub == 0:
                continue
            target = sol.get(k, 0)
            # d_k <= |x_k - target_k| via a sign indicator y_k; big-M = 2 ub keeps the inactive branch slack.
            big_m = 2 * max(ub, target)
            d = pulp.LpVariable(f"d_{i}_{j}", 0, max(ub, target))
            y = pulp.LpVariable(f"y_{i}_{j}", cat="Binary")
            prob += d <= x[k] - target + big_m * (1 - y)
            prob += d <= target - x[k] + big_m * y
            dev.append(d)
        cons[f"distinct_from_{i}"] = pulp.lpSum(dev) >= min_distance
    for name, c in cons.items():
        prob += c, name.replace(":", "_").replace(">", "_req_").replace("|", "_x_")
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit_s, gapRel=0.0)
    try:
        code = prob.solve(solver)
    except pulp.PulpSolverError as exc:  # solver binary missing or crashed
        return SolveResult("error", f"CBC solver failed: {exc}", {}, None, time.perf_counter() - start)
    runtime = time.perf_counter() - start
    status = STATUS_MAP.get(code, "error")
    if status == "optimal" and prob.sol_status == pulp.LpSolutionIntegerFeasible:
        status = "feasible_time_limit"
    if status not in ("optimal", "feasible_time_limit"):
        diagnosis = diagnose_infeasibility(baseline, candidates, budget_inr, committed, equity_floor, coeffs, scales, weights)
        return SolveResult(status, "; ".join(diagnosis) or "Solver reported no feasible portfolio.", {}, None, runtime,
                           diagnosis=diagnosis)
    counts = {k: int(round(v.value() or 0)) for k, v in x.items()}
    counts = {k: n for k, n in counts.items() if n > 0}
    slack, binding = {}, []
    for name, c in cons.items():
        if name.startswith("distinct_from") or name == "equity_floor_nontrivial":
            continue
        val = float(c.value() or 0.0)  # PuLP stores each constraint as (expr - rhs) compared with 0
        s = val if c.sense == pulp.LpConstraintGE else -val
        slack[name] = round(float(s), 6)
        if name == "capital":
            cheapest = min((by_id[k].capex_inr for k in x if by_id[k].upper_bound > counts.get(k, 0)), default=None)
            if cheapest is None or s < cheapest:
                binding.append(name)
        elif name.startswith(("roof:", "land:")):
            step = 250.0 if name.startswith("roof") else 300.0
            if s < min(200.0, step):
                binding.append(name)
        elif abs(s) <= 1e-6:
            binding.append(name)
    for k, n in counts.items():
        if n == by_id[k].upper_bound and by_id[k].upper_bound > 0:
            binding.append(f"unit_cap:{k}")
    return SolveResult(status, "Optimal solution found by CBC." if status == "optimal" else "Time limit reached; best feasible solution returned.",
                       counts, float(pulp.value(prob.objective) or 0.0), runtime, slack, binding)


def diagnose_infeasibility(baseline: Baseline, candidates: list[Candidate], budget_inr: float, committed: dict[str, int],
                           equity_floor: float, coeffs: Coefficients, scales: Scales, weights: dict[str, float]) -> list[str]:
    """Identify which hard constraint makes the problem infeasible (each test is exact)."""
    by_id = {c.candidate_id: c for c in candidates}
    reasons = []
    committed_capex = sum(by_id[k].capex_inr * n for k, n in committed.items() if k in by_id)
    if committed_capex > budget_inr + 1e-6:
        reasons.append(f"committed overspend: committed projects cost INR {committed_capex:,.0f} but only INR {budget_inr:,.0f} is available")
    for z in baseline.zones:
        roof = sum(by_id[k].roof_m2 * n for k, n in committed.items() if k in by_id and by_id[k].zone_id == z.zone_id)
        if z.eligible_roof_m2.value is not None and roof > float(z.eligible_roof_m2.value):
            reasons.append(f"commitments in {z.zone_id} need {roof:.0f} m2 roof; only {z.eligible_roof_m2.value:.0f} m2 eligible")
    if equity_floor > 0:
        priority = max(baseline.zones, key=lambda z: float(z.vulnerability_weight.value))
        pk = [c for c in candidates if c.zone_id == priority.zone_id and c.upper_bound > 0
              and benefit_value(c.candidate_id, coeffs, scales, weights) > 0 and c.capex_inr <= budget_inr]
        if not pk:
            reasons.append(f"equity floor {equity_floor:.2f}: no affordable eligible project with positive benefit in priority zone "
                           f"{priority.zone_id} ({priority.name})")
        elif equity_floor >= 1.0:
            reasons.append("equity floor 1.00 requires every unit of benefit to go to the priority zone, which conflicts with commitments elsewhere")
        else:
            reasons.append(f"equity floor {equity_floor:.2f} cannot be met together with the budget and capacity limits; lower the floor")
    if not reasons:
        reasons.append("no combination satisfies all hard constraints simultaneously")
    return reasons
