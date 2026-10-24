"""Known-answer, physical-bound and unit tests for the environmental and economic models."""
import numpy as np
import pytest

from c1v1c.models import carbon, cost, equity, heat, hydrology


def test_rational_method_matches_master_plan_fixture():
    q = hydrology.rational_peak_m3s(0.70, 50, 10)
    assert q == pytest.approx(0.973, abs=1e-12)
    assert hydrology.exceedance_m3s(q, 0.80) == pytest.approx(0.173, abs=1e-12)
    assert hydrology.exceedance_m3s(q, 1.05) == 0.0  # drainage changes capacity, never runoff generation


def test_rational_method_rejects_invalid_inputs_and_is_monotonic():
    with pytest.raises(ValueError):
        hydrology.rational_peak_m3s(1.2, 50, 10)
    with pytest.raises(ValueError):
        hydrology.rational_peak_m3s(0.5, -1, 10)
    assert hydrology.rational_peak_m3s(0.7, 60, 10) > hydrology.rational_peak_m3s(0.7, 50, 10)  # more rain never less runoff


def test_imd_reduction_formula_and_units():
    assert hydrology.imd_short_duration_depth_mm(72.0, 24) == pytest.approx(72.0)
    assert hydrology.imd_short_duration_depth_mm(72.0, 1) == pytest.approx(72.0 * (1 / 24) ** (1 / 3))
    with pytest.raises(ValueError):
        hydrology.imd_short_duration_depth_mm(72.0, 30)


def test_tank_balance_fixture_and_capacity_invariant():
    r = hydrology.tank_balance([8, 8, 0], [5, 5, 5], 10)
    assert r.served_m3.tolist() == [5, 5, 5]
    assert r.storage_m3.tolist() == [3, 5, 0]
    assert r.overflow_m3.tolist() == [0, 1, 0]
    assert r.total_served > 10  # annual yield can exceed capacity through turnover
    rng = np.random.default_rng(0)
    inflow = rng.gamma(0.5, 10, 2000)
    r = hydrology.tank_balance(inflow, 3.0, 20.0)
    assert (r.storage_m3 >= 0).all() and (r.storage_m3 <= 20.0 + 1e-9).all()
    # water balance closes: inflow = served + overflow + final storage
    assert inflow.sum() == pytest.approx(r.served_m3.sum() + r.overflow_m3.sum() + r.storage_m3[-1])


def test_tank_rejects_negative_inputs():
    with pytest.raises(ValueError):
        hydrology.tank_balance([-1.0], 1.0, 5)
    with pytest.raises(ValueError):
        hydrology.tank_balance([1.0], 1.0, -5)


def test_harvest_direction_checks():
    rng = np.random.default_rng(1)
    rain = rng.gamma(0.4, 12, 365 * 4)
    years = np.repeat(np.arange(4), 365)
    small = hydrology.annual_harvest_m3(rain, years, 200, 0.8, 10, 0.5)
    big = hydrology.annual_harvest_m3(rain, years, 200, 0.8, 30, 0.5)
    dry = hydrology.annual_harvest_m3(rain, years, 200, 0.8, 30, 0.5, rain_factor=0.6)
    assert big["mean_m3_yr"] >= small["mean_m3_yr"]          # bigger tank never worse
    assert dry["mean_m3_yr"] <= big["mean_m3_yr"]            # less rain never more water
    assert big["mean_m3_yr"] <= big["potential_m3_yr"] + 1e-9  # capture never exceeds potential
    assert big["mean_m3_yr"] <= 0.5 * 365 + 1e-9               # served never exceeds demand


def test_harvest_potential_units():
    assert hydrology.harvest_potential_m3(100, 200, 0.8) == pytest.approx(16.0)  # 100 mm x 200 m2 x 0.8 / 1000
    with pytest.raises(ValueError):
        hydrology.harvest_potential_m3(10, 10, 1.5)


def test_heat_index_bounds_and_exposure():
    assert heat.normalise_temperature(20) == 0 and heat.normalise_temperature(45) == 1 and heat.normalise_temperature(50) == 1
    h = heat.heat_index(0.6, 0.6, 0.4)
    assert h == pytest.approx(0.5 * 0.6 + 0.3 * 0.6 + 0.2 * 0.6)
    assert 0 <= h <= 1
    with pytest.raises(ValueError):
        heat.heat_index(1.2, 0.5, 0.5)
    r = heat.exposure_reduction(10_000, 1_000_000, 300, 1.0)
    assert r == pytest.approx(10_000 * 0.2 * 300 / 1_000_000)
    assert heat.exposure_reduction(10_000, 1_000_000, 300, 0.7) == pytest.approx(0.7 * r)  # drought weakens cooling
    assert heat.exposure_reduction(10_000, 1_000, 5_000, 1.0, current_vegetation=0.9) == pytest.approx(10_000 * 0.2 * 0.1)


def test_carbon_boundary_and_not_estimated():
    t = carbon.crown_cover_sequestration_tco2e(300, 2.9, 10)
    assert t == pytest.approx(0.03 * 2.9 * 10 * 44 / 12)
    assert carbon.net_co2e(None, None, None, None) is None  # not estimated is not zero
    assert carbon.net_co2e(5.0, None, 1.0, None) == pytest.approx(4.0)
    with pytest.raises(ValueError):
        carbon.crown_cover_sequestration_tco2e(-1, 2.9, 10)


def test_lifecycle_cost_and_crore_conversion():
    pv = cost.present_value_factor(0.05, 10)
    assert pv == pytest.approx(7.721734929, rel=1e-9)
    assert cost.lifecycle_cost_inr(1_000_000, 20_000, 0.05, 10) == pytest.approx(1_000_000 + 20_000 * pv)
    assert cost.crore_to_inr(2.2) == 22_000_000
    with pytest.raises(ValueError):
        cost.lifecycle_cost_inr(-1, 0)


def test_equity_helpers():
    assert equity.vulnerability_weight(0.2, 0.1) == pytest.approx(2.0)
    assert equity.vulnerability_weight(0.0, 0.1) == pytest.approx(0.25)  # floored
    assert equity.per_1000_residents(50, 25_000) == pytest.approx(2.0)
    assert equity.gini([1, 1, 1]) == pytest.approx(0.0)
    assert equity.gini([0, 0, 3]) == pytest.approx(2 / 3)
