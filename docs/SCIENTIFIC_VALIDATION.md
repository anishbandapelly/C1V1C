# Scientific validation — real Bengaluru baseline

Generated 2026-10-24T03:12:08+00:00 by `python scripts/validate_science.py` against baseline `bengaluru_pilot_v1` (sha256 `33b6dd75e6083b3f`), model `c1v1c-model-1.0.0`, catalogue `catalog-ce9252fea3b2`.

**43 of 43 checks pass.**

These are internal-consistency, unit, bound and direction checks plus cross-checks between two independent climate sources. They are **not empirical validation** of intervention effects: no field measurements of retention, harvest yield, cooling or drainage performance exist in the collection, so model outputs remain screening estimates built on declared assumptions.

| Area | Check | Result | Detail |
|---|---|---|---|
| climate | IMD annual rainfall vs independent daily series | PASS | IMD cell mean 902 mm/yr (1971-2005) vs station-type series 796 mm/yr (1951-2024); Bengaluru's commonly cited normal is roughly 900-1,000 mm/yr |
| climate | summer Tmax vs independent daily series | PASS | IMD 1 deg Mar-May mean Tmax 34.37 degC vs 34.10 degC |
| runoff | ZA design-event runoff recomputed | PASS | C 0.653 x 24.95 mm x 67.12 ha = 10,943 m3 |
| runoff | ZA peak flow units | PASS | Rational Q 3.042 m3/s x 3600 s = 10,952 m3 vs 1-h volume 10,943 m3 (+0.08%; 0.00278 is 1/360 rounded, so +0.08% is expected) |
| bounds | ZA fractions in [0,1] | PASS | all bounded |
| bounds | ZA population density plausible | PASS | 42,832 persons/km2 |
| runoff | ZB design-event runoff recomputed | PASS | C 0.656 x 24.95 mm x 50.89 ha = 8,328 m3 |
| runoff | ZB peak flow units | PASS | Rational Q 2.315 m3/s x 3600 s = 8,335 m3 vs 1-h volume 8,328 m3 (+0.08%; 0.00278 is 1/360 rounded, so +0.08% is expected) |
| bounds | ZB fractions in [0,1] | PASS | all bounded |
| bounds | ZB population density plausible | PASS | 53,832 persons/km2 |
| runoff | ZC design-event runoff recomputed | PASS | C 0.653 x 24.95 mm x 62.84 ha = 10,233 m3 |
| runoff | ZC peak flow units | PASS | Rational Q 2.845 m3/s x 3600 s = 10,241 m3 vs 1-h volume 10,233 m3 (+0.08%; 0.00278 is 1/360 rounded, so +0.08% is expected) |
| bounds | ZC fractions in [0,1] | PASS | all bounded |
| bounds | ZC population density plausible | PASS | 47,589 persons/km2 |
| water | tank water balance closes over 35 years | PASS | residual 0.00e+00 m3 |
| water | storage never exceeds capacity | PASS | max storage 19.50 m3 <= 20.0 m3 |
| water | yield below potential and demand | PASS | usable 106.8 m3/yr; potential 144.3 m3/yr; demand 182 m3/yr |
| carbon | forest sequestration hand calculation | PASS | 300 m2 x 0.5 crown x 2.9 tC/ha/yr x 10 yr x 44/12 = 1.59 tCO2e |
| solver | Balanced @ INR 0 cr feasible and cost-consistent | PASS | optimal; 0 units; INR 0; by-zone and by-type sums match |
| solver | Balanced @ INR 0.5 cr feasible and cost-consistent | PASS | optimal; 1 units; INR 5,000,000; by-zone and by-type sums match |
| solver | Balanced @ INR 2 cr feasible and cost-consistent | PASS | optimal; 6 units; INR 19,400,000; by-zone and by-type sums match |
| solver | Balanced @ INR 5 cr feasible and cost-consistent | PASS | optimal; 12 units; INR 33,600,000; by-zone and by-type sums match |
| solver | Flood-first @ INR 0 cr feasible and cost-consistent | PASS | optimal; 0 units; INR 0; by-zone and by-type sums match |
| solver | Flood-first @ INR 0.5 cr feasible and cost-consistent | PASS | optimal; 1 units; INR 5,000,000; by-zone and by-type sums match |
| solver | Flood-first @ INR 2 cr feasible and cost-consistent | PASS | optimal; 6 units; INR 18,600,000; by-zone and by-type sums match |
| solver | Flood-first @ INR 5 cr feasible and cost-consistent | PASS | optimal; 11 units; INR 30,600,000; by-zone and by-type sums match |
| solver | Water-first @ INR 0 cr feasible and cost-consistent | PASS | optimal; 0 units; INR 0; by-zone and by-type sums match |
| solver | Water-first @ INR 0.5 cr feasible and cost-consistent | PASS | optimal; 3 units; INR 3,600,000; by-zone and by-type sums match |
| solver | Water-first @ INR 2 cr feasible and cost-consistent | PASS | optimal; 6 units; INR 18,600,000; by-zone and by-type sums match |
| solver | Water-first @ INR 5 cr feasible and cost-consistent | PASS | optimal; 8 units; INR 24,600,000; by-zone and by-type sums match |
| solver | Heat-first @ INR 0 cr feasible and cost-consistent | PASS | optimal; 0 units; INR 0; by-zone and by-type sums match |
| solver | Heat-first @ INR 0.5 cr feasible and cost-consistent | PASS | optimal; 2 units; INR 5,000,000; by-zone and by-type sums match |
| solver | Heat-first @ INR 2 cr feasible and cost-consistent | PASS | optimal; 7 units; INR 20,000,000; by-zone and by-type sums match |
| solver | Heat-first @ INR 5 cr feasible and cost-consistent | PASS | optimal; 12 units; INR 33,600,000; by-zone and by-type sums match |
| solver | Equity-first @ INR 0 cr feasible and cost-consistent | PASS | optimal; 0 units; INR 0; by-zone and by-type sums match |
| solver | Equity-first @ INR 0.5 cr feasible and cost-consistent | PASS | optimal; 1 units; INR 5,000,000; by-zone and by-type sums match |
| solver | Equity-first @ INR 2 cr feasible and cost-consistent | PASS | optimal; 6 units; INR 19,400,000; by-zone and by-type sums match |
| solver | Equity-first @ INR 5 cr feasible and cost-consistent | PASS | optimal; 12 units; INR 33,600,000; by-zone and by-type sums match |
| scenario | extreme rain raises event runoff 30% for the frozen plan | PASS | x1.30 in every ward; share handled falls or stays equal |
| scenario | drought lowers harvested water | PASS | 320 -> 235 m3/yr |
| scenario | budget cut re-optimised plan fits revised envelope | PASS | original INR 19,400,000; revised envelope INR 14,000,000; original still feasible: False; re-optimised INR 13,600,000 |
| scenario | re-optimised never scores below the frozen plan under the same shock | PASS | C >= B for every feasible frozen plan |
| equity | vulnerability weights follow SC/ST shares | PASS | {"ZA": 0.551, "ZB": 0.565, "ZC": 0.268} |
