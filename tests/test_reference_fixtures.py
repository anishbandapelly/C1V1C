"""Reference math / synthetic-fixture integrity ONLY — not full application tests."""
import csv
from itertools import combinations
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic_test"

def load(name):
    with (DATA / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def test_zone_fixtures_are_explicitly_synthetic():
    rows=load("zone_fixture.csv")
    assert len(rows)==3
    assert all(x["evidence_class"]=="synthetic" for x in rows)
    assert all(float(x["area_ha"])>0 for x in rows)

def test_four_required_intervention_fixtures():
    rows=load("intervention_unit_fixture.csv")
    assert {r["intervention_type"] for r in rows} == {"green_roof", "urban_forest", "rainwater_harvesting", "drainage_upgrade"}
    assert all(float(x["capex_inr"])>=0 and x["evidence_class"]=="synthetic" for x in rows)

def test_all_required_shocks_in_fixture():
    rows=load("scenario_fixture.csv")
    assert {r["scenario_id"] for r in rows} == {"normal", "extreme_rain", "drought", "budget_cut"}

def test_rational_method_numeric_reference():
    q=0.00278 * 0.70 * 50 * 10
    assert abs(q-0.973)<1e-12
    initial_exceedance=max(0,q-0.8)
    upgraded_exceedance=max(0,q-1.05)
    assert abs(initial_exceedance-0.173)<1e-12
    assert upgraded_exceedance==0

def test_tank_turnover_numeric_reference():
    capacity=10.0; stored=0.0
    inflow=[8.,8.,0.]; demand=[5.,5.,5.]
    served=[];end=[];spill=[]
    for v,d in zip(inflow,demand):
        pre=min(capacity,stored+v)
        spill.append(max(0,stored+v-capacity))
        use=min(pre,d);served.append(use)
        stored=pre-use;end.append(stored)
    assert served==[5.,5.,5.]
    assert end==[3.,5.,0.]
    assert spill==[0.,1.,0.]
    assert sum(served)>capacity

def test_tiny_optimizer_reference_by_exhaustion():
    candidates=load("optimization_fixture.csv")
    feasible=[]
    for size in range(len(candidates)+1):
        for chosen in combinations(candidates,size):
            cost=sum(int(p["cost_units"]) for p in chosen)
            benefit=sum(int(p["benefit_units"]) for p in chosen)
            if cost<=8:feasible.append((benefit,cost,tuple(p["project_id"] for p in chosen)))
    optimum=max(feasible,key=lambda t:t[0])
    assert optimum == (14,8,("B","C"))
