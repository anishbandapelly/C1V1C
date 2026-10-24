"""Climate Shock Lab: A/B/C separation, consistency with the evaluator, budget cuts, commitments, replay."""
import pytest

from c1v1c.run_store import RunStore
from c1v1c.schemas import RunResult


@pytest.fixture
def original(engine):
    return engine.run(engine.default_request(budget_inr=12_000_000), use_cache=False)


def test_three_evaluations_are_distinct_and_frozen(engine, original):
    comp = engine.shock(original, "extreme_rain")
    assert comp.b_original_under_shock.counts == original.selected_candidate_counts  # B never redesigns the plan
    assert comp.a_original_normal.counts == original.selected_candidate_counts
    assert comp.c_reoptimised.run_id != original.run_id                                # C is a new solver run
    assert comp.c_reoptimised.comparison_role == "reoptimised_under_shock"
    assert comp.c_reoptimised.parent_run_id == original.run_id
    assert comp.c_reoptimised.scenario.scenario_id == "extreme_rain"
    # A equals the original run's own evaluation under normal conditions
    assert comp.a_original_normal.score == pytest.approx(original.evaluated_score)
    # C is optimal for the shock: its score is at least the frozen plan's score under the same shock
    assert comp.c_reoptimised.evaluated_score >= comp.b_original_under_shock.score - 1e-9


def test_extreme_rain_scales_design_storm_not_water(engine, original):
    comp = engine.shock(original, "extreme_rain", {"design_intensity_multiplier": 1.3})
    a, b = comp.a_original_normal, comp.b_original_under_shock
    for zid in a.by_zone:
        assert b.by_zone[zid]["design_event_runoff_m3"] == pytest.approx(1.3 * a.by_zone[zid]["design_event_runoff_m3"])
        if a.by_zone[zid]["event_runoff_managed_share"]:
            assert b.by_zone[zid]["event_runoff_managed_share"] <= a.by_zone[zid]["event_runoff_managed_share"] + 1e-12
    assert b.metrics["W"] == pytest.approx(a.metrics["W"])
    assert b.metrics["F"] >= a.metrics["F"] - 1e-9  # rain-limited capture can only grow with a stronger storm


def test_drought_reduces_harvest_and_cooling(engine):
    run = engine.run(engine.default_request(budget_inr=20_000_000, mode="Water-first"), use_cache=False)
    heat = engine.run(engine.default_request(budget_inr=20_000_000, mode="Heat-first"), use_cache=False)
    dw = engine.shock(run, "drought")
    dh = engine.shock(heat, "drought")
    assert dw.b_original_under_shock.metrics["W"] < dw.a_original_normal.metrics["W"]
    if any(k.endswith("urban_forest") for k in heat.selected_candidate_counts):
        assert dh.b_original_under_shock.metrics["H"] < dh.a_original_normal.metrics["H"]
    assert dw.b_feasible and dh.b_feasible  # drought changes outcomes, not affordability


def test_budget_cut_makes_original_unaffordable_and_replans(engine, original):
    comp = engine.shock(original, "budget_cut", {"budget_factor": 0.5})
    revised = int(original.request.budget_inr * 0.5)
    assert comp.c_reoptimised.budget_available_inr == revised
    if original.allocated_inr > revised:
        assert not comp.b_feasible
        assert any("no longer affordable" in n for n in comp.b_notes)
    assert comp.c_reoptimised.solver_status == "optimal"
    assert comp.c_reoptimised.allocated_inr <= revised


def test_budget_cut_with_commitments_above_envelope_is_infeasible(engine, original):
    drains = {k: n for k, n in original.selected_candidate_counts.items() if k.endswith("drainage_upgrade")}
    if not drains:
        pytest.skip("original plan has no drainage unit to commit")
    comp = engine.shock(original, "budget_cut", {"budget_factor": 0.05}, drains)
    assert comp.c_reoptimised.solver_status == "infeasible"
    assert any("committed overspend" in r for r in comp.c_reoptimised.binding_constraints)


def test_commitment_must_belong_to_original(engine, original):
    missing = next(c.candidate_id for c in engine.all_candidates if c.candidate_id not in original.selected_candidate_counts)
    with pytest.raises(ValueError):
        engine.shock(original, "budget_cut", {}, {missing: 1})


def test_normal_scenario_reproduces_original(engine, original):
    comp = engine.shock(original, "normal")
    assert comp.b_original_under_shock.score == pytest.approx(comp.a_original_normal.score)
    assert comp.c_reoptimised.selected_candidate_counts == original.selected_candidate_counts


def test_saved_run_reproducibility_and_immutability(engine):
    req = engine.default_request(budget_inr=9_000_000, mode="Water-first")
    first = engine.run(req, use_cache=False)
    replay = engine.run(req, use_cache=False)
    assert replay.run_id == first.run_id and replay.input_hash == first.input_hash
    a, b = first.model_dump(), replay.model_dump()
    for meta in ("created_at_utc", "solver_runtime_s"):
        a.pop(meta), b.pop(meta)
    assert a == b                                            # identical inputs reproduce identical results
    loaded = engine.load_run(first.run_id)
    assert isinstance(loaded, RunResult) and loaded.selected_candidate_counts == first.selected_candidate_counts
    other = engine.run(req.model_copy(update={"scenario_id": "drought"}), use_cache=False)
    assert other.run_id != first.run_id                      # a new scenario is a new run


def test_run_store_refuses_overwrites(engine, tmp_path):
    store = RunStore(engine.settings)
    run = engine.run(engine.default_request(budget_inr=5_000_000), use_cache=False)
    tampered = run.model_copy(update={"allocated_inr": run.allocated_inr + 1})
    with pytest.raises(FileExistsError):
        store.save("runs", run.run_id, tampered)
    with pytest.raises(ValueError):
        store.load("runs", "../../etc/passwd", RunResult)
