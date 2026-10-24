# Models, optimisation, scenarios and explanations

All numbers below are computed by deterministic code. Parameters and their evidence classes live in [`config/model_parameters.json`](../config/model_parameters.json) and [`config/intervention_assumptions.csv`](../config/intervention_assumptions.csv). The catalogue version shown in every run is a content hash of these files.

## 1. Environmental and economic models

| Model | Equation | Inputs (units, evidence) | Validity / limitations | Code · tests |
|---|---|---|---|---|
| Peak runoff (Rational Method) | `Q = 0.00278 · C · I · A` [m³/s] | C [-]: derived from footprints plus an assumed paved share. I [mm/h]: design storm. A [ha]: observed. | Small catchments with time of concentration ≈ storm duration. A screening indicator, **not** flood depth. | `models/hydrology.py` · `test_models.py` |
| Composite runoff coefficient | `C = f_imp·0.90 + (1−f_imp)·0.25` | f_imp: footprints (derived) + 25% of non-building area (assumed). Coefficients: estimated, ranges 0.75–0.95 / 0.10–0.35. | No ward land-cover layer; roads are approximated. | `pipeline.py` |
| Design storm | `P_1h = P24 · (1/24)^(1/3)` (IMD reduction formula) | P24 = mean annual-maximum daily rainfall, IMD 0.5° cell, 1971–2005 (derived). | Literature method, not a local IDF curve. Coarse cell shared by all three wards. | `hydrology.imd_short_duration_depth_mm` |
| Design-event runoff | `V = C · P_1h · A` [m³/event] | as above | Volume over the 1-h event | `pipeline.py`, `validate_science.py` |
| **Flood objective F** | Sum per zone of retained + captured + newly conveyed volume, capped at V [m³/event]. Green roof `min(15 mm, 0.9·P)·250 m²`; tank `min(20 m³, 0.8·P·200 m²)`; forest `(0.25−0.15)·P·300 m²`; drain `+0.12 m³/s × 3,600 s`. | Unit effects assumed (master plan Table 9) | Existing drain capacity is **not measured**. Conveyance is counted 1:1 on the stated assumption that the network is at capacity in the design event. Drains move water downstream. Residual unmanaged runoff `V − F` is reported separately. | `evaluate.unit_effects` |
| Rainwater harvesting **W** | Daily tank balance, inflow → overflow → demand: `A=S+P; overflow=max(0,A−K); served=min(D,min(K,A)); S=min(K,A)−served` | 35-year daily IMD record (observed), roof 200 m², efficiency 0.80 (estimated), K = 20 m³, D = 0.5 m³/day (assumed) | `0 ≤ S ≤ K` is asserted every day. Annual yield can exceed K through turnover. Mean, P10 and P90 are reported. Urban forests subtract 96 m³/yr irrigation. | `hydrology.tank_balance` · water-balance closure test |
| Heat index | `H = 0.5·Tnorm + 0.3·Impervious + 0.2·(1−Veg)`, `Tnorm = clip((T−20)/25)` | T = Mar–May mean Tmax, IMD 1° (observed). Imperviousness and vegetation as above. | A screening index in [0,1], **not °C**. Urban LST data absent (the heat CSV was outside Bengaluru). | `models/heat.py` |
| **Heat objective H** | `ΔExposure = Pop · 0.2 · ΔVeg · cooling_factor` [person-index units] | Greened area / ward area. Drought lowers the tree cooling factor. | Linear in added vegetation; vegetation capped at 1. | `heat.exposure_reduction` |
| **Carbon G** | `tCO₂e = area·crown_fraction/10⁴ · 2.9 tC/ha/yr · 10 yr · 44/12` | IPCC 2006 Vol.4 Ch.8 crown-cover default (estimated, 1.8–3.4). Average crown cover 0.5 (assumed). | Forest sequestration only. Embodied, maintenance and avoided-energy emissions are **not estimated** (null, never 0). | `models/carbon.py` |
| Lifecycle cost | `LCC = capex + Σ_{t=1}^{10} O&M/(1.05)^t` | Capex and O&M share assumed. 5% real rate, 10-year horizon (master plan). | Capex is the hard constraint; LCC is an objective term only. No ROI claimed. | `models/cost.py` |
| Equity | `v_z = 1 + (SCST_z/SCST_city − 1)` (floored at 0.25). `EquityGain = Σ_z v_z · mean(F,W,H normalised) · P̄/P_z / τ_E` | SC/ST shares from the ward KML (derived) | A distribution preference, not extra physical benefit. Per-1,000-resident outcomes and a Gini of per-capita benefit are reported. | `models/equity.py`, `evaluate.py` |

## 2. Mixed-integer optimisation (PuLP/CBC)

There are 12 decision variables, `x[k]` for zone × intervention. Per master plan §5.2 the first build allows one unit per type per ward, so the variables are binary through `max_units_per_zone = 1`; integer units are supported by configuration.

```
max  Σ_m w_m Σ_k b[k,m] x_k / τ_m  +  w_E Σ_k e_k x_k / τ_E  −  w_C Σ_k LCC_k x_k / τ_C
s.t. Σ capex_k x_k ≤ B·budget_factor                    capital (hard)
     Σ_{k∈z} roof_k x_k ≤ eligible_roof_z               green roofs and tanks share roofs
     Σ_{k∈z} land_k x_k ≤ plantable_land_z
     0 ≤ x_k ≤ ub_k   (ub = 0 if not eligible, not estimable or deselected)
     x_a ≤ ub_a·x_b (requires),  y_a + y_b ≤ 1 (excludes)
     x_k ≥ committed_k
     benefit(priority ward) ≥ floor · benefit(all wards)   (equity floor; priority = highest SC/ST weight)
```

- **Normalisation:** each `τ_m` is the benefit of spending the reference ₹2 crore on the single best intervention for metric m in the normal scenario. These scales are frozen per baseline and identical across portfolios and shocks (shown in every run's assumptions).
- **Weights:** Balanced follows the master plan. For the four "-first" modes the master plan fixes only the primary weight; the remaining split is the approved frontend's preset. Users can edit weights, and they must sum to 100%.
- **Independent verification:** after CBC solves, `evaluate_portfolio` re-computes budget, roof, land, caps, eligibility and commitments from scratch, with physical caps applied. A violation turns the run into an error; it is never displayed as a feasible plan. The surrogate and evaluated scores are both stored.
- **Infeasibility:** CBC infeasible gives `solver_status = infeasible` with a diagnosed reason (committed overspend, unreachable equity floor, …). No portfolio is fabricated and no constraint is relaxed.
- **Alternatives:**
  - Up to three next-best plans, each forced by an exact no-good constraint to differ by at least 2 units.
  - The optimum of every other priority mode.
  - Two baselines: no investment, and an equal-spend conventional plan.
  - All are scored with the same weights, scales, budget and evaluator, and labelled "best among evaluated feasible plans".
- **Tests:** CBC matches brute-force enumeration of all 4,096 combinations for 5 modes × 4 budgets. 25 random weight/budget draws never exceed the budget. There are also tests for shared-roof binding, requires/excludes, commitments, equity floor and infeasibility.

## 3. Scenario simulator

These presets come from master plan §6.3. They are editable stress tests, **not forecasts**.

| Scenario | Changes |
|---|---|
| Extreme rainfall | design-storm intensity ×1.30 (event depth and runoff) |
| Drought | daily rainfall ×0.60 in the tank simulation; tree cooling ×0.70 |
| Budget cut | capital envelope ×0.70 |

- **A** — the original plan evaluated under normal conditions.
- **B** — the **same frozen counts** evaluated under the shock. B is flagged infeasible if it no longer fits the revised envelope or commitments.
- **C** — a **new MILP run** under the shock, with the same weights and the committed units fixed. It gets a new run ID linked to the original.

Reports show per-metric A/B/C values, residual unmanaged runoff, additions and removals, and score ranges across four disclosed perturbations. These perturbations are design storm ±10%, rainfall availability −20% and tree cooling −30%, together with the original plan's maximum regret. They are *sensitivity ranges, not confidence intervals*.

## 4. Decision explainer

`explainer.explain(run)` builds the explanation deterministically from the stored run:

- why the plan was selected (score contributions, weights, gap to the best alternative);
- why each other project was rejected (eligibility, budget remaining, lower score per crore, shared roof);
- improved and worsened metrics;
- beneficiaries per ward (INR per resident, outcomes per 1,000 residents) and underserved wards;
- binding constraints, shock findings, assumptions, uncertainties and unintended consequences (overflow migration, irrigation, roof competition, maintenance, gentrification).

**Bedrock** (optional) receives only these computed facts. Its text is accepted only if every number in it matches a computed value within 2%. Otherwise the deterministic narrative is shown, labelled with the reason (offline, not configured, access denied, timeout, or rejected numbers).

## 5. Reproducibility

`run_id = hash(request, baseline sha256, catalogue version, parameter version, model version)`.

- Runs are stored once as JSON; overwriting with different content is refused.
- Re-running identical inputs recomputes the result and verifies it equals the stored record (ignoring timestamp and solver wall time); a mismatch raises an error.
- Any model change bumps `MODEL_VERSION`; the current version is `c1v1c-model-1.1.0`.
