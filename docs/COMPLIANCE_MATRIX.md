# Requirements compliance matrix — Phases 4–6 (24 Oct 2026)

Statuses: **PASS** = implemented and verified by the test or evidence cited · **PARTIAL** = works, with a disclosed limitation · **BLOCKED** = needs an external permission or input · **FAIL** = not met.

**Test evidence:**

- `pytest`: **139 passed** (api 4, explainer/AWS 12, frontend 43, handoff 10, models 11, optimiser 34, pipeline 9, reference fixtures 6, scenarios 10).
- `scripts/validate_science.py`: **43/43 PASS** ([SCIENTIFIC_VALIDATION.md](SCIENTIFIC_VALIDATION.md)).
- `scripts/smoke_test.py` against the Docker deployment: **15/15 PASS**.

## Original problem statement (five MVP modules) and master plan P0

| ID | Requirement | Implementation | Data source | API / UI | Test | Result | Status | Limitation / blocker |
|---|---|---|---|---|---|---|---|---|
| PS-01 | Data Engine: climate, water, land-use, population | `pipeline.py`, `baseline.py` | GBA wards, IMD grids, footprints, hazard points, drains, tanks/ponds | City Intelligence; `GET /zones` | `test_pipeline.py` (9) | pass | **PARTIAL** | No ward land-use layer (2017 KML absent), no 2015–25 NetCDF, no LST for Bengaluru, no ward water demand: all reported as gaps |
| PS-02 | Optimise combinations of all 4 interventions | `optimiser.py` (PuLP/CBC MILP) | assumption catalogue + baseline | Investment Optimiser; `POST /runs` | `test_milp_matches_brute_force` (20 cases), constraint tests | pass | **PASS** | Unit costs and effects are master-plan assumptions (grade D), not Bengaluru-validated |
| PS-03 | Interactive dashboard: risks, costs, allocation, neighbourhood benefits | `ui/views.py` on the engine | baseline + runs | 4 pages + map | `test_frontend.py` (43), browser check light/dark | pass | **PASS** | Visual regression at 5 widths × 2 themes not re-captured (spot-checked 800 and 1440 px, both themes) |
| PS-04 | Drought, extreme rain, budget cut; original vs re-optimised | `engine.shock` (A/B/C) | IMD daily series, scenario presets | Climate Shock Lab; `POST /runs/{id}/shocks` | `test_scenarios.py` (10), UI shock tests | pass | **PASS** | Shocks are illustrative presets, not forecasts |
| PS-05 | Explain recommendations, uncertainty, unintended consequences | `explainer.py`, `aws/bedrock.py` | stored run | Decision Intelligence; `GET /runs/{id}/explanation` | explainer tests, number validation | pass | **PASS** (deterministic) / **BLOCKED** (Bedrock live) | No verified Bedrock model or credentials |
| CORE-01 | Multi-objective environment, economy, equity | `evaluate.py` | — | outcome table, score contributions | optimiser + scenario tests | pass | **PASS** | Normalisation scales are declared design choices |
| CORE-02 | Flood, water, heat, carbon models | `models/*` | IMD, footprints | outcomes | `test_models.py`, 43 science checks | pass | **PARTIAL** | Heat is an index (not °C). Carbon covers forest sequestration only. Drain capacity is unmeasured |
| CORE-03 | Budget, roof, land, site, prerequisite, exclusion constraints | `optimiser.solve` | — | constraint review | shared-roof, requires/excludes, property tests | pass | **PASS** | Eligible roof and land are assumed fractions |
| CORE-04 | No unsupported optimality; independent re-evaluation | `evaluate_portfolio` + verification | — | verification table | 25-draw property test | pass | **PASS** | "Optimal" only among the 12 declared units |
| CORE-05 | Commitments respected, overspend reported | `solve(committed=…)`, `diagnose_infeasibility` | — | Shock Lab commitments | `test_committed_overspend…`, `test_commitments_are_kept` | pass | **PASS** | — |
| CORE-06 | Reproducible immutable runs | `run_store.py`, replay verification | — | saved runs, JSON export | `test_saved_run_reproducibility…`, `test_run_store_refuses_overwrites` | pass | **PASS** | — |
| CORE-07 | Offline fallback | offline mode, FailoverS3, deterministic narrator | — | banner + status captions | AWS failure tests, smoke test | pass | **PASS** | — |
| CORE-08 | Equity and evidence honesty; missing ≠ 0 | `evidence.Quantity`, labels in UI | — | evidence column on every indicator | `test_quantity_serialisation…`, data-mode tests | pass | **PASS** | — |
| EXT-01 | Same-budget conventional baselines | `_alternatives` (no investment, equal spend) | — | alternatives table | `test_alternatives…` | pass | **PASS** | — |
| EXT-02 | S3 versioned runs / Bedrock | `aws/`, `run_store.mirror` | — | `GET /aws/status`, `/health` | stubbed tests + live probe | S3 live PASS (runs in bucket); Bedrock AccessDenied | **PARTIAL** | Bedrock needs `bedrock:InvokeModel` ([AWS_SERVICES.md](AWS_SERVICES.md)) |

## Phase 4–6 brief requirements

| Requirement | Status | Evidence / note |
|---|---|---|
| Inventory the dataset folder recursively | **PASS** | 5,765 files listed; 165 downloaded; claims vs bytes in the quality report |
| Fix the `rainfall.csv` 1971-01-01 date bug | **PASS** | Dates rebuilt from the source header; value-for-value match on 4 cells; broken file quarantined |
| Population sum inconsistencies | **PASS** | 125 wards flagged, values preserved, majors excluded from selection |
| Invalid and duplicate flood coordinates | **PASS** | (0,0) excluded; 6 duplicate groups flagged; ward join |
| Do not treat 2017 land use as current / legacy ids / flood points as sites | **PASS** | Land use absent and reported; legacy ids separated; hazard-marker status |
| Inventory claims vs files; CRS/units/licence/provenance | **PASS** | `provenance.csv`, manifest sha256 |
| Personal or unrelated files excluded | **PASS** | Header scan; documents not ingested |
| Three pilot zones from real boundaries | **PASS** | ZA Brundavana Nagara, ZB Dinnur, ZC R.T Nagar (GBA Yelahanka), rule documented |
| Output contracts: `zones.geojson`, `zones.csv`, `sites.csv`, `rainfall.csv`, `interventions.csv`, `scenarios.csv`, `provenance.csv` | **PASS** | In `data/curated/bengaluru_pilot_v1/` (rainfall as `rainfall_daily.csv`) |
| Rainfall/runoff, flood, RWH, heat, carbon, LCC, eligibility, population-weighting, equity, uncertainty | **PARTIAL** | All implemented with documented equations ([MODELS.md](MODELS.md)); several coefficients are grade-D assumptions |
| Priority modes Balanced, Flood-, Water-, Heat-, Equity-first | **PASS** | Presets from config; UI weights editable |
| Optimiser outputs: status, quantities, costs by type and zone, unallocated, outcomes, equity, baseline comparison, binding constraints, rejections, alternatives, versions, provenance | **PASS** | `RunResult` schema; UI ledgers |
| Real infeasibility, never fabricated | **PASS** | Infeasible tests (equity floor, committed overspend) |
| Typed, validated API schemas | **PASS** | Pydantic `RunRequest`/`RunResult`; 422 on invalid input |
| Frontend preserved; mock wiring removed | **PASS** | Same layout and tokens; `ui/fixtures.py` deleted |
| Loading / empty / error / infeasible / missing-baseline states | **PASS** | spinner, preflight, errors; `test_missing_baseline_shows_honest_error` |
| Light and dark mode | **PASS** | Browser checked; contrast test |
| Secure credentials, no secrets in Git | **PASS** | `secret_safety_check.py` PASS; `.env` ignored; smoke test scans responses |
| Deployment with post-deploy checks | **PARTIAL** | Docker deployment healthy, 15/15 smoke; no public cloud deployment (needs approval and credentials) |
| Meaningful AWS integration | **PARTIAL** | S3 live (runs and comparisons mirrored, encrypted, versioned); Bedrock blocked by IAM |
| Anti-slop §9 re-audit after integration | **PARTIAL** | Approved design and tokens unchanged; no new §9 score recorded for the new result tables |

## Known limitations

1. **Mixed-evidence pilot.** Every intervention cost and effect is an illustrative master-plan assumption, so recommendations are screening estimates. The engine labels them as such everywhere.
2. **Coarse climate.** All three wards share one IMD rainfall cell and one temperature cell, and records end in 2005. Climate therefore does not differentiate the wards.
3. **Flood benefit.** Drain upgrades are counted as conveyed volume, assuming the network is at capacity; measured hydraulic capacity is unavailable. Residual unmanaged runoff is shown alongside.
4. **Similar wards.** The three wards are similarly dense (built fraction ≈ 0.49), so allocations differ mainly through hazard markers, SC/ST share and drainage.
5. **Not committed to Git.** The curated baseline (licence review pending) and the raw data are reproducible from the Drive folder plus the pipeline.
