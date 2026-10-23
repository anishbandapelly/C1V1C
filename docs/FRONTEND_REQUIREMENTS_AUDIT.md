# Frontend requirements audit — correction round 2

Scope: existing frontend only, checked against the original DOCX and master DOCX, source code, AppTest and rendered Edge. The supplied filenames correspond to repository files `docs/Original_Sustainable_Development_PS.docx` (PS) and `docs/C1V1C_Master_Plan.docx` (MP); the original titles are retained in those documents. `docs/MASTER_PLAN.md` is the readable section reference. No production-module completion is inferred from a visible control.

PASS means the stated frontend behaviour actually functions. PARTIAL means some of the capability exists. BLOCKED BY BACKEND/DATA identifies required integrated functionality absent at this approval stage. FAIL denotes an outstanding frontend requirement defect. Sources: PS §§1–4; MP section numbers below.

| Requirement | Source document and section | Existing UI location | Status | Evidence | Required correction |
|---|---|---|---|---|---|
| Data Engine: climate, water, land and population analysis | PS §2; MP §§3–4 | City | BLOCKED BY BACKEND/DATA | Synthetic profiles, source leads and missing water/carbon fields only | Validate and ingest real layers; implement analysis after approval |
| AI Optimisation: four interventions and constrained allocation | PS §2; MP §5 | Investment | BLOCKED BY BACKEND/DATA | EnginePort exists; PreviewSnapshot explicitly not_run | PuLP/CBC and independent feasibility evaluator |
| Interactive dashboard: risks, costs, allocation, neighbourhood benefits | PS §2; MP §7 | Four modules | PARTIAL | Map/profile, cost arithmetic and per-zone investment work; benefits unavailable | Bind verified RunResult outputs |
| Scenario Simulator: three shocks | PS §2; MP §6 | Shock | PARTIAL | Controls save factors and frozen IDs; budget arithmetic works | Recompute environmental models and solve new alternatives |
| Decision Explainer: reasons, uncertainty, consequences | PS §2; MP §7.1 | Decision | PARTIAL | Honest selection description and consequences; no calculated reasons | Bind deterministic selected/rejected reasons and objective contributions |
| Meaningful AWS integration | PS §3; MP §9 | No cloud UI | BLOCKED BY BACKEND/DATA | No cloud calls or success claims | S3 and optional grounded Bedrock after approval |
| Urban paradox and limited-resource workflow | PS §§1,4; MP §2.1 | Home | PASS | Home introduces roof, water, land and budget conflicts; four entry actions navigate | None |
| Pilot geography and valid terminology | MP §§3.1,3.4 | City map/caption | PASS | Yelahanka context; A/B/C explicitly illustrative, WGS84 markers not official wards | Verified polygons still a data dependency |
| Geographic layers and profile inspection | MP §7 | City | PASS | Six layers and A/B/C selector update displayed values | Add real layers after validation |
| Climate/flood screening indicators | MP §§3.2,4.1 | City risk table | PARTIAL | Runoff coefficient and drainage capacity shown; rainfall series absent | Source rainfall; compute flow/exceedance |
| Water indicators | MP §§3.2,4.2 | City risk table | BLOCKED BY BACKEND/DATA | Missing demand explicitly reported, never zero | Validated rainfall/demand/storage balance |
| Heat exposure and population | MP §§3.4,4.3 | City profile | PARTIAL | Synthetic heat index and residents, no false Celsius claim | Validate temperature/vegetation/exposure inputs |
| Land, roof and drainage resources | MP §§3.2,5.1 | City candidate disclosure; intervention rows | PARTIAL | Synthetic resources and per-unit needs visible | Site-specific capacity and eligibility validation |
| Source coverage, dates, evidence and missing data | MP §3.3 | City source register; Decision disclosure | PASS | Grade D, no observation date, coverage unverified; downloadable source leads | Replace leads with evidence records as acquired |
| Neighbourhood comparison | MP §§7,5.9 | City map; Decision distribution | PARTIAL | Map compares selected fixture indicator; investment table compares A/B/C | Real risk/benefit/residual comparisons |
| Exact editable capital budget, default INR 20m | MP §5.1a | Investment envelope | PASS | Decimal parser; 2, 2.2, 2.4, 10.5 and bounds tested; INR export checked | None; whole-INR precision bounded at 100 crore |
| Dot editing, Enter/blur/Escape, validation | Round 2 §5 | Budget component | PASS | Text input, no spinners/edit overlay; invalid commit blocked | None |
| All four requested interventions propagate | PS §2; MP §5.1 | Investment selector | PASS | Four checkboxes populate allowed_interventions; filtering tests | No physical-feasibility claim |
| Selection separate from suitability | MP §§5.3,5.7 | Intervention rows | PASS | Requested/excluded state distinct from unverified evidence notice | Eligible/ineligible/system availability must come from trusted adapter |
| Physical eligibility and hard constraints | MP §§5.3,5.7 | Candidate/constraint disclosures | BLOCKED BY BACKEND/DATA | No verified sites; selection is never presented as engineering approval | Enforce roof sharing, land, storage, dependencies, asset limits |
| Balanced/Flood/Water/Heat/Equity presets | MP §5.10 | Priority mode | PASS | All five presets; .55 primary flood/water/heat and .45 equity | None; non-primary shares are disclosed defaults |
| Six weights including LCC; sum validation | MP §§5.6,5.10 | Objective disclosure; Decision priorities | PASS | Editable percentages, sum=100 checked; exact saved weights displayed | Connect weights to real objective later |
| Equity floor | MP §5.7 | Equity safeguard | PARTIAL | Nonzero floor blocked with explanation, never silently relaxed | Population-weighted benefit constraint and vulnerable-zone evidence |
| Solver status, infeasible/error/loading states | MP §§5.4,5.8,8.4 | Allocation ledger | PARTIAL | not_run always; explicit QA specimens distinguish failures | Bind actual engine status, runtime, gap and diagnostics |
| Chosen/rejected project inspection | MP §§5.4,7.1 | Ledger; Decision project selector | PARTIAL | Actual fixture selection/exclusion available | Solver-grounded rejection reasons and counterfactuals |
| Budget utilisation and unallocated capital | MP §5.4 | Allocation metrics | PASS | Sum of fixture costs and remainder from saved budget | Not a feasibility certificate |
| Lifecycle economics and carbon | MP §4.4–4.5 | Notices/weights | BLOCKED BY BACKEND/DATA | Not estimated; no ROI or zero-carbon substitution | Sourced O&M, horizon, emissions and discounting |
| Per-zone benefits and underserved groups | MP §§5.9,7.1 | Decision distribution | BLOCKED BY BACKEND/DATA | Capital per resident shown, expressly not environmental equity | Actual benefit/residual risk and population-weighted equity |
| No-investment/equal-spend baselines | MP §5.5 | Alternative display portfolios | PARTIAL | Cost-only fixture comparison; not evaluated baselines | Same evaluator/budget/eligibility for all strategies |
| Feasible alternative plans and trade-offs | MP §§5.2,5.10 | Alternative display portfolios | BLOCKED BY BACKEND/DATA | No feasible or Pareto claim; invented outcome charts removed | At least two computed feasible alternatives |
| Normal baseline scenario | MP §6.3 | Shock disruption selector | PASS | Normal factors 1.0; frozen selection preserved | Environmental baseline still requires engine |
| Extreme rain 1.30 editable | MP §6.3 | Storm intensity slider | PASS | Default 1.30 saved as test assumption | Recompute physical effects after integration |
| Drought rainfall .60/cooling .70 editable | MP §6.3 | Drought sliders | PASS | Both factors preserved in scenario record | Rainfall timing, irrigation and cooling evaluator |
| Budget cut .70 editable | MP §6.3 | Retained budget slider | PASS | Revised envelope arithmetic; commitments overspend warnings | New constrained optimisation |
| Original normal vs same original under shock vs reoptimised | MP §§6.1,7 | Shock comparison table | PARTIAL | Distinct columns; original IDs frozen; replanned column Not computed | Populate separately computed outputs, distinct run IDs |
| Intervention additions/removals and changed risks | MP §7 | Shock comparison | BLOCKED BY BACKEND/DATA | Static invented chart/change narrative removed | Diff real original/new feasible selections |
| Committed costs cannot disappear | MP §5.7; §6.3 | Commitments control | PARTIAL | Saved committed IDs, deducted cost and overspend warning | Solver must fix project counts |
| Scenario test conditions not forecasts | MP §6.3 | Shock captions | PASS | Explicit user-defined assumptions, no event prediction | None |
| Scenario reproducibility without raw UI dump | MP §8 | Scenario export | PASS | Exports original snapshot plus factors/commitments/IDs; no raw parameter panel | Durable run store remains pending |
| Why selected / why not alternatives | MP §7.1 | Decision explanation | BLOCKED BY BACKEND/DATA | Generic fixture inclusion statement is explicitly not solver explanation | Calculated reasons, constraint slacks, counterfactuals |
| Objectives improved/worsened | MP §§5.5,7.1 | Decision/alternative views | BLOCKED BY BACKEND/DATA | No invented environmental improvement figures retained | Evaluated metric vector and score contributions |
| Declared priorities use available width | MP §5.10; Round 2 §8 | Decision | PASS | Full-width six-value breakdown; preset/custom label | None |
| Uncertainty and unintended consequences | PS §2; MP §7.2 | Decision disclosures | PASS | Irrigation, maintenance, displacement, shared capacity and sensitivity caveats | Add run-specific computed sensitivities later |
| Sources & assumptions, not technical lineage panel | MP §§3.3,7.1 | Decision disclosure | PASS | Source sections, grade and missing observation year; exact metadata in export | None |
| Saved runs and compatible comparison | MP §§7,8 | Saved preview/compare controls | PARTIAL | Session previews selectable; incompatible baseline/catalogue/model versions excluded | Durable immutable computed run store and replay |
| Export agrees with displayed saved selection | MP §7.3 | JSON/Markdown exports | PASS | Generated from same PreviewSnapshot; browser export verifies INR and not_run | Production brief adds real outputs after integration |
| Hero → City → Investment → Shock → Decision | MP §2.1; user home requirement | Shell and next actions | PASS | Active navigation, brand home, mobile drawer and next steps tested | None |
| Zone selection consistency | MP §2.1 | City inspection; Investment scope caption | PARTIAL | City selection is inspection only; allocation explicitly all three fixture zones | Add area/baseline selection when validated areas exist |
| Currency/physical units and honest data | MP §§3.3,4,5.9 | Captions/tables/exports | PASS | INR/crore explicit, index not Celsius, unknowns not zero | Units for future metrics must use contracts |
| No raw developer-facing panels | Round 2 §3; MP §7 | Shock/Decision | PASS | Parameter/model-update and saved-contract JSON views deleted | QA state picker remains explicitly labelled for this review only |
| Header toggle and understated home brand | Round 2 §6 | Sidebar header | PASS | Icon-only toggle in header; mouse background removed, keyboard focus retained | None |
| Themes, responsive layout and reduced motion | anti-slop §6/§9; Round 2 §11 | Entire application | PASS | Browser viewport/theme checks; sequential content removes unequal long columns | Manual assistive-technology review remains advisable |

## Requirement categories and unresolved work

Visual defects corrected: locale-dependent budget chrome, brand click rectangle, toggle in its own list-like row, large uneven result columns, raw metadata panels and redundant static charts. Behaviour corrected: budget commit/revert/validation/conversion, four intervention request flags, normal scenario, comparison version guard. Backend/data dependencies above are intentionally not labelled PASS; all five production MVP modules remain incomplete.

Rendered mobile review identified the empty dark rectangle as native field-help chrome beside Committed projects: the broad multiselect-button styling also coloured its help button. Redundant help widgets are removed; necessary commitment guidance is now a concise caption. The style rule is narrowed to actual combobox buttons, correcting the underlying scope. The large pre-submit guidance block was separately reduced to a short caption. There is no conversational question feature to migrate. Internal scenario records and typed run/provenance contracts are preserved. No authentication, optimiser or AWS implementation was added.

Boundary: this audit certifies inspected frontend behaviour at this commit, not numerical model validity, municipal data quality, solver feasibility or a deployment release. The normal user flow retains only information relevant to a planning decision; explicit review-state specimens remain available in a collapsed frontend-review disclosure until engine integration.
