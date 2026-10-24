"""MILP correctness: brute-force agreement, hard constraints, infeasibility, alternatives (synthetic baseline)."""
import itertools
import random

import pytest
from pydantic import ValidationError

from c1v1c.catalogue import build_candidates
from c1v1c.evaluate import build_coefficients, surrogate_score
from c1v1c.optimiser import solve
from c1v1c.schemas import INTERVENTIONS, Candidate, RunRequest


def _setup(engine, request):
    cands = engine.candidates_for(request)
    coeffs = build_coefficients(engine.baseline, cands, engine.specs, engine.params, engine.scenario_for(request), engine.scales)
    return cands, coeffs


def _feasible(engine, cands, counts, budget):
    by = {c.candidate_id: c for c in cands}
    if sum(by[k].capex_inr * n for k, n in counts.items()) > budget:
        return False
    for z in engine.baseline.zones:
        if sum(by[k].roof_m2 * n for k, n in counts.items() if by[k].zone_id == z.zone_id) > z.eligible_roof_m2.value:
            return False
        if sum(by[k].land_m2 * n for k, n in counts.items() if by[k].zone_id == z.zone_id) > z.plantable_land_m2.value:
            return False
    return all(n <= by[k].upper_bound for k, n in counts.items())


@pytest.mark.parametrize("mode", ["Balanced", "Flood-first", "Water-first", "Heat-first", "Equity-first"])
@pytest.mark.parametrize("budget", [0, 3_000_000, 9_000_000, 20_000_000])
def test_milp_matches_brute_force(engine, mode, budget):
    req = engine.default_request(budget_inr=budget, mode=mode)
    cands, coeffs = _setup(engine, req)
    sol = solve(engine.baseline, cands, coeffs, engine.scales, req.weights, budget)
    assert sol.status == "optimal"
    ids = [c.candidate_id for c in cands if c.upper_bound > 0]
    best = max(
        (surrogate_score(dict(zip(ids, bits)), coeffs, engine.scales, req.weights)
         for bits in itertools.product((0, 1), repeat=len(ids)) if _feasible(engine, cands, dict(zip(ids, bits)), budget)),
        default=0.0)
    assert surrogate_score(sol.counts, coeffs, engine.scales, req.weights) == pytest.approx(max(best, 0.0), abs=1e-7)


def test_budget_and_hard_constraints_never_violated(engine):
    rnd = random.Random(7)
    for _ in range(25):
        w = [rnd.random() for _ in range(6)]
        weights = dict(zip(("F", "W", "H", "G", "Equity", "LCC"), [x / sum(w) for x in w]))
        budget = rnd.choice([0, 1_000_000, 4_500_000, 12_345_678, 25_000_000, 60_000_000])
        req = engine.default_request(budget_inr=budget).model_copy(update={"weights": weights})
        run = engine.run(req, use_cache=False)
        assert run.solver_status == "optimal"
        assert run.allocated_inr <= run.budget_available_inr + 1e-6
        assert all(run.verification.values())
        assert _feasible(engine, engine.candidates_for(req), run.selected_candidate_counts, run.budget_available_inr)


def test_zero_budget_selects_nothing(engine):
    run = engine.run(engine.default_request(budget_inr=0), use_cache=False)
    assert run.solver_status == "optimal" and run.selected_candidate_counts == {} and run.allocated_inr == 0


def test_insufficient_budget_for_any_unit(engine):
    run = engine.run(engine.default_request(budget_inr=1_000_000), use_cache=False)  # cheapest unit costs 1.2 M
    assert run.selected_candidate_counts == {}
    assert all("only INR" in r or "Not considered" in r or "lowers" in r for r in run.rejected.values())


def test_shared_roof_constraint_binds(tmp_path):
    from synthetic_baseline import build

    from c1v1c.baseline import _load, load_baseline
    from c1v1c.config import Settings
    from c1v1c.engine import Engine

    _load.cache_clear()
    eng = Engine(Settings.load(), baseline=load_baseline(build(tmp_path / "tight", roof_m2=300.0)))
    # 300 m2 of eligible roof fits a 250 m2 green roof OR a 200 m2 tank, never both
    roofs = {c.candidate_id: c.upper_bound for c in eng.all_candidates if c.roof_m2}
    assert all(v == 1 for v in roofs.values())
    run = eng.run(eng.default_request(budget_inr=60_000_000), use_cache=False)
    for z in eng.baseline.zones:
        used = sum(c.roof_m2 * run.selected_candidate_counts.get(c.candidate_id, 0) for c in eng.all_candidates if c.zone_id == z.zone_id)
        assert used <= 300.0
    assert any(b.startswith("roof:") for b in run.binding_constraints)


def test_not_estimable_capacity_blocks_candidate(engine):
    z = engine.baseline.zones[0]
    zones = [z.model_copy(update={"eligible_roof_m2": z.eligible_roof_m2.model_copy(update={"value": None, "evidence": "missing"})}),
             *engine.baseline.zones[1:]]
    cands = build_candidates(zones, engine.specs, engine.params)
    blocked = [c for c in cands if c.zone_id == z.zone_id and c.roof_m2 > 0]
    assert blocked and all(c.eligibility == "not_estimable" and c.upper_bound == 0 for c in blocked)


def test_negative_capacity_and_invalid_inputs_rejected(engine):
    with pytest.raises(ValidationError):
        Candidate(candidate_id="x", zone_id="z", intervention_type="green_roof", capex_inr=1, lcc_inr=1, roof_m2=1, land_m2=0,
                  upper_bound=-1, eligibility="eligible", eligibility_reason="")
    with pytest.raises(ValidationError):
        engine.default_request(budget_inr=-5)
    with pytest.raises(ValidationError):
        RunRequest(baseline_version="b", project_catalog_version="c", model_version="m", budget_inr=1,
                   weights={"F": 0.5, "W": 0.6, "H": 0, "G": 0, "Equity": 0, "LCC": 0}, allowed_interventions=INTERVENTIONS)
    with pytest.raises(ValidationError):
        engine.default_request(equity_floor=2)
    with pytest.raises(ValidationError):
        engine.default_request(overrides={"made_up_factor": 1.0})


def test_equity_floor_infeasible_is_reported_not_relaxed(engine):
    req = engine.default_request(budget_inr=20_000_000, equity_floor=1.0, committed_counts={"ZA:drainage_upgrade": 1})
    run = engine.run(req, use_cache=False)
    assert run.solver_status == "infeasible"
    assert run.outcome is None and run.selected_candidate_counts == {}
    assert run.binding_constraints  # a diagnosed reason, never a fabricated portfolio


def test_equity_floor_shifts_benefit_to_priority_zone(engine):
    priority = max(engine.baseline.zones, key=lambda z: z.vulnerability_weight.value).zone_id
    base = engine.run(engine.default_request(budget_inr=6_000_000), use_cache=False)
    floored = engine.run(engine.default_request(budget_inr=6_000_000, equity_floor=0.9), use_cache=False)
    assert floored.solver_status == "optimal"
    share = lambda r: r.capex_by_zone[priority] / max(r.allocated_inr, 1)  # noqa: E731
    assert share(floored) >= share(base)
    assert floored.allocated_inr == 0 or share(floored) > 0.5


def test_committed_overspend_is_infeasible(engine):
    req = engine.default_request(budget_inr=6_000_000, committed_counts={"ZA:drainage_upgrade": 1, "ZB:drainage_upgrade": 1})
    run = engine.run(req, use_cache=False)
    assert run.solver_status == "infeasible"
    assert any("committed overspend" in r for r in run.binding_constraints)


def test_commitments_are_kept(engine):
    req = engine.default_request(budget_inr=20_000_000, mode="Heat-first", committed_counts={"ZC:drainage_upgrade": 1})
    run = engine.run(req, use_cache=False)
    assert run.selected_candidate_counts.get("ZC:drainage_upgrade") == 1


def test_requires_and_excludes(engine):
    req = engine.default_request(budget_inr=60_000_000)
    cands, coeffs = _setup(engine, req)
    cands = [c.model_copy(update={"requires": ("ZA:drainage_upgrade",)}) if c.candidate_id == "ZA:green_roof" else
             c.model_copy(update={"excludes": ("ZB:green_roof",)}) if c.candidate_id == "ZB:urban_forest" else c for c in cands]
    sol = solve(engine.baseline, cands, coeffs, engine.scales, req.weights, 60_000_000)
    assert sol.counts.get("ZA:green_roof", 0) <= sol.counts.get("ZA:drainage_upgrade", 0)
    assert sol.counts.get("ZB:urban_forest", 0) + sol.counts.get("ZB:green_roof", 0) <= 1
    cands2 = [c.model_copy(update={"upper_bound": 0}) if c.candidate_id == "ZA:drainage_upgrade" else c for c in cands]
    sol2 = solve(engine.baseline, cands2, coeffs, engine.scales, req.weights, 60_000_000)
    assert sol2.counts.get("ZA:green_roof", 0) == 0  # its prerequisite is unavailable


def test_weight_changes_change_the_selection(engine):
    picks = {m: frozenset(engine.run(engine.default_request(budget_inr=6_000_000, mode=m), use_cache=False).selected_candidate_counts)
             for m in ("Flood-first", "Water-first", "Heat-first")}
    assert len(set(picks.values())) == 3
    assert any(k.endswith("drainage_upgrade") for k in picks["Flood-first"])
    assert any(k.endswith("rainwater_harvesting") for k in picks["Water-first"])
    assert any(k.endswith(("urban_forest", "green_roof")) for k in picks["Heat-first"])


def test_alternatives_are_distinct_feasible_and_not_better(engine):
    run = engine.run(engine.default_request(budget_inr=20_000_000), use_cache=False)
    seen = {frozenset(run.selected_candidate_counts.items())}
    for a in run.alternatives:
        assert a.feasible and not a.outcome.violations
        if a.method == "milp_no_good_cut":
            key = frozenset(a.counts.items())
            assert key not in seen
            seen.add(key)
            assert a.outcome.score <= run.evaluated_score + 1e-9
    methods = {a.method for a in run.alternatives}
    assert {"milp_no_good_cut", "baseline"} <= methods
    assert any(a.alternative_id == "baseline-none" for a in run.alternatives)


def test_deselected_interventions_are_never_chosen(engine):
    req = engine.default_request(budget_inr=40_000_000).model_copy(update={"allowed_interventions": ("urban_forest",)})
    run = engine.run(req, use_cache=False)
    assert run.selected_candidate_counts and all(k.endswith("urban_forest") for k in run.selected_candidate_counts)
    assert all("excluded by planner" in v for k, v in run.rejected.items() if not k.endswith("urban_forest"))
