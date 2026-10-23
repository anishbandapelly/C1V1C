# C1V1C — Tulabhara AI: Complete Master Development Plan

> Converted from `docs/C1V1C_Master_Plan.docx`. The DOCX remains the authoritative formatted source. This Markdown retains the original ordered paragraphs and tables; verify equation and layout nuances against the DOCX.

C1V1C

TULABHARA AI

Balancing the Future of Cities.

COMPLETE PROJECT DEVELOPMENT MASTER PLAN

Sustainable Development  |  AI-Driven Urban Sustainability Decision Engine

| PRODUCT THESIS; Recommend where a city should invest, which interventions to combine, how benefits and costs are distributed, and whether the plan remains feasible when rainfall, drought or budgets change. |
| --- |



Version  2.0 — standalone implementation master specification

Prepared  23 October 2026

Build window  24 hours; official event timeline 23–24 October 2026

Pilot geography  Bengaluru / Yelahanka sub-catchment (pending final data validation)

Target team  Four members; Anish as systems and integration lead

Primary workflow  Codex Astra + Python + GitHub; AWS S3 and optional Bedrock

> Planning and demonstration estimates are not municipal engineering advice or validated flood forecasts. All assumptions must be disclosed.


## Document map and decisions

This is a self-contained execution master specification. It translates the supplied Sustainable Development DOCX and research-informed architecture blueprint into exact data contracts, physical-model rules, optimisation mathematics, test fixtures, cloud setup, time-boxed tasks and judging criteria. It does not imply that software or datasets have already been built, acquired or validated.

READ IN THIS ORDER

| Part | What it resolves |
| --- | --- |
| 1–2 | Official requirements, product purpose, scope and success criteria |
| 3–5 | Study area, curated data plan, full physical models and MILP formulation |
| 6–8 | Scenario engine, user experience, explainability and saved runs |
| 9–11 | AWS and technical architecture, repository, development workflow |
| 12–15 | 24-hour execution plan, exact test fixtures, demo, risks and release gates |
| Appendices | Field dictionary, typed contracts, decision gates, research matrix and cited sources |


### Decisions already locked

| Decision | Status / reason |
| --- | --- |
| Name | C1V1C — Tulabhara AI; spoken as “Civic”; balancing competing urban objectives. |
| Official five MVP modules | All are mandatory and must work together; no substitutions. |
| Interventions | Green roofs, urban forests, rainwater harvesting, drainage improvements. |
| Prototype scope | Three zones and ~12–24 candidate project units, after a one-zone vertical slice. |
| Optimiser | Mixed-integer linear optimisation with hard physical constraints and transparent objective weights. |
| Compute and UI | Python domain engine + Streamlit UI; domain logic independent of interface. |
| AWS | S3 for durable provenance/results; Bedrock for grounded narration only if access is ready. |
| Non-goals | Full hydraulic twin, live municipal integration, CKAN/EKS, trained foundation model, misleading precision. |


| INTERPRETATION RULE; The original PS names AWS services but does not expressly require deploying all of them. This plan follows every functional MVP requirement and adopts AWS services only where they provide demonstrable value. If hackathon rules impose a minimum AWS usage requirement, verify that rule separately. |
| --- |


## 1. Official challenge and compliance

### 1.1 Problem in the original brief

Indian cities face interconnected urban heat, flooding, water scarcity and carbon-emissions challenges. Available solutions can conflict, and planners must operate with limited budgets, land availability and uncertain climate conditions. The project must identify intervention combinations while balancing environmental impact, economic feasibility and social equity, adapt to unexpected scenarios, and explain the trade-offs behind its recommendations. [PS]

### 1.2 Exact MVP traceability

| Official MVP module | C1V1C implementation | Acceptance demonstration |
| --- | --- | --- |
| Data Engine | Validated climate, water, land-use and population layers; site capacities, costs, data coverage and provenance. | Select zone; show data values, units, sources and missing-data warnings. |
| AI Optimisation | MILP investment allocation across all four interventions under budget, land, feasibility and equity constraints. | Change budget/weights; recompute feasible portfolio and compare alternatives. |
| Interactive Dashboard | Four-tab risk, cost, investment, impact, equity and comparison interface. | Show map, intervention allocations, costs and benefits by neighbourhood. |
| Scenario Simulator | Separate drought, extreme rainfall and budget-cut stress cases; old-plan test plus reoptimisation. | Run each scenario and compare outputs with the same saved baseline. |
| Decision Explainer | Deterministic numerical reasons, active constraints, uncertainty, rejected options and consequences; optional Bedrock narration. | Explain why a project was selected/rejected, who benefits, and what is uncertain. |


### 1.3 Outcomes and boundaries

- The system should help planners compare interventions, allocate limited resources, anticipate climate disruptions and understand which populations benefit. [PS]

- It is a decision-support proof of concept, not a certified engineering design, city-scale flood prediction, or source of verified avoided-loss estimates.

- No unverified data may be presented as a measured Bengaluru statistic. All model outputs must identify units, study scale, assumptions and evidence grade.

## 2. Product outcomes and minimum success criteria

### 2.1 Target user and workflow

Primary user: urban planner, urban resilience analyst, facilities/municipal infrastructure decision-maker or sustainability programme lead. User journey: choose pilot zone and baseline → inspect risks/suitability → select budget and priorities → optimise → examine who benefits → trigger a shock → compare the old plan and new optimum → read the evidence-backed explanation → save a reproducible decision summary.

### 2.2 Operational success measures

| Measure | Acceptance threshold for prototype |
| --- | --- |
| Requirements coverage | All five official modules demonstrably functional; all four interventions evaluated. |
| Feasibility | 100% of displayed chosen projects pass implemented budget, capacity and eligibility constraints. |
| Traceability | Every material input is linked to a source or explicit assumption with units; every result has a run ID and model version. |
| Scenario validity | Three named shocks recompute model inputs and rerun evaluation; no hard-coded alternative charts. |
| Transparency | Show environment, economic and equity trade-offs; never assert universal superiority on all metrics. |
| Demo reliability | An end-to-end local/offline demonstration works without S3 or Bedrock availability. |
| Speed target | Target ordinary three-zone runs to feel interactive (ideally seconds); measure locally rather than promise fixed latency. |


### 2.3 Impact positioning

The immediate measurable product impact is improved decision quality and auditability in a controlled planning exercise: fewer infeasible options, comparable alternatives, consistent treatment of equity and modelled climate shocks. Real-world flood-loss prevention, emissions reduction and ROI require later calibration, observation and field validation.

## 3. Pilot geography, data and provenance

### 3.1 Study design

Recommended starting geography: Bengaluru, with the ATREE Yelahanka sub-catchment research providing local flood-risk context. Use three internally consistent planning zones in one hydrologically coherent pilot area when comparable layers are available. If formal zone boundaries cannot be obtained quickly, use explicitly illustrative subzones without assigning them unsupported official ward characteristics. [R1]

Maintain 12–24 candidate project units in the initial catalogue, distributed among the three zones. The units represent distinct physical investment opportunities, not thousands of individual assets.

### 3.2 Data input and source plan

| Required category | Key fields / modelling role | Source priority |
| --- | --- | --- |
| Climate / rainfall | Precipitation history, event design intensity, temperature; scenario overrides. | ATREE context, CHIRPS/NASA POWER where spatial resolution is appropriate. |
| Land cover / slope | Impervious fraction, vegetation, eligible land, roof footprint, slope. | ESA WorldCover / terrain layer; Google Open Buildings; local verification. |
| Water / drainage | Catchment area, runoff proxy, reference capacity, water demand and storage. | ATREE/local records if available, otherwise labelled screening assumptions. |
| Population / equity | Population, exposure, density and disclosed vulnerability proxy. | WorldPop or credible official data; no invented measured deprivation index. |
| Cost / maintenance | Capital INR, maintenance INR/year, lifespan, implementation constraint. | Transparent research-informed ranges, vendor/municipal estimates if available. |
| Carbon / heat | Green-cover exposure, sourceable LST/cooling effects, CO2e factors. | Remote sensing plus bounded literature estimates; not direct city-wide forecasts. |


### 3.3 Evidence classification and data quality

For every numerical input record: source title/URL, publication or observation date, spatial resolution, geographic scope, units, type (observed / estimated / literature-derived / synthetic), coverage, transformation and known limitations. Use evidence tiers such as A = measured/local, B = credible external model, C = literature transfer with caveats, D = illustrative assumption. Evidence tiers are metadata, not invented statistical confidence probabilities.

- Never convert a missing environmental indicator into a zero effect. Mark it missing and either block an affected claim or use a disclosed fallback assumption.

- Store frozen, versioned input snapshots before each optimisation run so later updates cannot silently change an earlier result.

- If the data do not support a claim at ward level, use the appropriate catchment/aggregate scale in the interface.

### 3.4 Pilot baseline: what is and is not frozen

The development contract is frozen, but measured numerical Bengaluru zone inputs are NOT yet verified. The following 3-zone figures are a synthetic software fixture only. They must be labelled “illustrative data - not observed Bengaluru conditions” wherever they appear. Before final demo, replace individual fields with verified site-specific inputs where available, preserving source identifiers and provenance. If a replacement is unsupported, retain the synthetic value with an explicit D evidence grade instead of fabricating a measurement.

| Zone fixture | Area / residents | Runoff / drainage | Resources / heat |
| --- | --- | --- | --- |
| A — rain stress | 10 ha; 4,000 people | C=0.85; capacity 0.85 m3/s | Roof 1,500 m2; land 1,000 m2; heat index 0.72 |
| B — heat stress | 8 ha; 6,500 people | C=0.70; capacity 0.90 m3/s | Roof 2,000 m2; land 650 m2; heat index 0.81 |
| C — water stress | 12 ha; 3,500 people | C=0.55; capacity 1.10 m3/s | Roof 1,800 m2; land 1,800 m2; heat index 0.58 |


> ALL numerical rows above are synthetic engineering/unit-test inputs, not official Yelahanka zone observations. They allow development while sourcing proceeds. No city claim may be made from these values.

### 3.5 Data ingestion pipeline and ownership

1. Member 3 selects pilot polygons, ensures all area values use one geographic coordinate reference system for geometry and one time horizon for outcomes, then extracts or constructs a versioned GeoJSON/CSV baseline.

1. Schema validation rejects implausible coordinate bounds, duplicate IDs, negative areas or populations, malformed units, and indicators missing provenance metadata.

1. Convert rainfall units and timestamps before calculating indicators. Do not infer ward-level rainfall from coarse grids without labelling the spatial-resolution limitation.

1. Freeze a read-only baseline snapshot with a SHA-256 checksum, catalogue version, source timestamps, model applicability notes and unresolved gaps.

1. Outputs must carry an explicit mode: observed-data pilot, mixed-evidence pilot, or synthetic demonstration. The mode is displayed in the UI and the decision brief.

## 4. Environmental and economic model specifications

Build separate, documented screening submodels. Each converts input data and a candidate project into an estimated outcome with clear physical limits. The optimiser uses precomputed coefficients for a simplified, auditable portfolio; post-selection evaluation must recheck coupled physical effects. No module should invent outputs through an LLM.

### 4.1 Stormwater / flood screening

Initial peak-flow screening (Rational Method): Q_peak = 0.00278 × C × I × A, where Q is m³/s, C is dimensionless runoff coefficient, I is rainfall intensity in mm/h, and A is area in hectares. Applicability is restricted to appropriate small-catchment assumptions; use consistent time of concentration/design-storm conditions. [R1, R2]

- Runoff control projects (green roofs, retention) change effective runoff characteristics or short-term storage within measured/assumed physical capacity.

- Conventional drainage upgrades increase conveyance or storage capacity; they do not automatically reduce runoff generation.

- Show peak-flow/capacity screening and runoff-retention indicators rather than claiming validated inundation depth or flood damage.

### 4.2 Rainwater capture and usable supply

Potential roof capture: V_potential (m³) = P(mm) × A(m²) × collection efficiency / 1000. Actual usable yield must be capped through a daily or monthly balance using tank capacity, demand, losses and rainfall timing. Water captured cannot exceed rainfall-derived potential; storage at any time cannot exceed tank capacity; total usable supply is demand-limited, but can exceed tank capacity over many refill cycles. [R3]

### 4.3 Urban heat and vegetation

Create an interpretable population-weighted heat-exposure index from selected temperature/LST, vegetation and imperviousness variables; show fixed normalisation bounds. Estimate cooling-related changes conservatively, using evidence-based ranges. Soil moisture and irrigation availability may reduce tree cooling under drought. Do not claim a definite °C cooling result unless separately calibrated. [R4, R5]

### 4.4 Carbon and lifecycle economics

Carbon ledger: net CO2e effect = avoided emissions + sequestration − added lifecycle/maintenance emissions, using consistent time horizons and non-overlapping accounting boundaries. Include only pathways for which coefficients and scope are documented; otherwise report “not estimated”. [R6]

Lifecycle cost: LCC = initial capital + Σ_t (annual maintenance_t / (1 + discount rate)^t). Apply initial capital as a hard constraint; display LCC and modelled physical benefits separately. Call a result ROI only when benefits are credibly monetised; otherwise report cost per unit outcome or transparent cost-effectiveness.

### 4.5 Exact physical-model update rules

#### 4.5.1 Tank storage and usable water balance

Choose one time step (daily preferred; monthly acceptable when only monthly inputs are available), and explicitly state the time-step convention. Let P[t] be precipitation-derived captured water (m3), K be tank capacity (m3), D[t] be demand (m3), S[t-1] be carryover storage (m3). For an inflow-then-overflow-then-demand ordering:

```text
A[t] = S[t-1] + P[t]
overflow[t] = max(0, A[t] - K)
available[t] = min(K, A[t])
served[t] = min(D[t], available[t])
S[t] = available[t] - served[t]
Annual usable water = sum(served[t]); always assert 0 <= S[t] <= K.
```

This conservative discrete balance is a screening model; within-period demand/inflow timing can affect overflow. A tank may refill several times: annual usable yield CAN be greater than K. Run sensitivity checks on time resolution when this changes rankings.

#### 4.5.2 Heat-exposure surrogate

For each zone z, define a transparent, dimensionless heat-exposure indicator H[z] in [0,1] using fixed scaled inputs. An illustrative implementation is H[z] = 0.50*Tnorm[z] + 0.30*Impervious[z] + 0.20*(1 - Vegetation[z]), with Tnorm fixed to disclosed temperature bounds. These weights are development assumptions, not a calibrated thermal-comfort model. For a synthetic coding fixture use Tnorm=clip((LST_C-20)/25,0,1), with illustrative 20–45 °C bounds; if LST is missing, retain the explicitly supplied test H[z] rather than pretending it was calculated from observed temperature.

Exposure load = population[z] * H[z]; the benefit from greening is the decrease in exposure load after applying bounded project effects. Under drought, apply a documented soil-moisture/cooling-retention factor in [0,1] and account separately for irrigation demand. Never relabel exposure-index changes as °C.

#### 4.5.3 Carbon accounting boundary

Freeze reporting as indicative tonnes CO2e over a common 10-year evaluation horizon (illustrative choice). For each project, distinguish year-1 embodied/installation emissions, annual maintenance emissions, annually avoided operational emissions, and time-dependent vegetation sequestration. Use undiscounted physical tCO2e totals for carbon; use discounting only for money.

If a trustworthy emissions factor cannot be sourced for one pathway, mark the pathway “not estimated”; do not silently assign it zero. Track attribution across green roofs, trees and avoided electricity so the same avoided emissions are not booked twice.

#### 4.5.4 Economic reporting boundary

Example development assumption: T=10 years and real discount r=5% per year, subject to explicit revision before presenting as a planning recommendation. For year-indexed O&M cost M[t]: LCC = capex + sum(M[t]/(1+r)^t) for t=1..T. If lifecycle economic benefit is not monetised, report LCC, capex, and per-metric cost-effectiveness, not ROI or a fabricated benefit-cost ratio.

### 4.6 Physical interactions and double-counting controls

| Potential interaction | Required treatment |
| --- | --- |
| Green roof + roof harvesting | Share eligible roof capacity; avoid applying two full-area benefits to one roof without a validated interaction. |
| Tree canopy + drought | Account for irrigation and reduced evaporative cooling when water availability decreases. |
| Drainage + infiltration/retention | Separate generated runoff, retained volume and system conveyance; prevent double-counting reduction. |
| Carbon + cooling electricity savings | Do not count the same avoided emissions twice across indirect pathways. |
| Multiple projects in one zone | Apply project quantity caps and recompute portfolio effect; enforce documented interaction rules. |


## 5. Intervention catalogue and optimiser

### 5.1 Standardised project-unit fields

Each project unit must have project_id, zone_id, intervention_type, eligibility, unit_count_cap, footprint/roof/land need, unit capital cost, annual maintenance, expected life, baseline requirements, climate-dependent benefit vector, source/assumption references, requires/excludes relationships and permitted commitments.

### 5.1a Synthetic intervention catalogue for a first runnable build

The following defaults are deliberately invented SOFTWARE TEST VALUES, not sourced Bengaluru construction quotations or validated effectiveness factors. Generate one eligible candidate of each type in each synthetic zone (12 binary candidates), then apply each zone’s shared capacity limits. These toy values must carry evidence grade D and “illustrative only” in app and exports. Replace with justified prices and benefits before making policy-level claims.

| Intervention unit | Synthetic capex | Unit physical configuration / constraint |
| --- | --- | --- |
| Green roof | INR 3,000,000 | 250 m2 dedicated eligible roof; maximum retained event depth 15 mm over this roof (3.75 m3), subject to climate and antecedent storage. |
| Urban forest | INR 2,000,000 | 300 m2 eligible ground; illustrative irrigation need 8 m3/month; cooling effect requires separately labelled coefficient. |
| Rainwater harvesting | INR 1,200,000 | 200 m2 catchment roof; tank size 20 m3; useful yield computed from rainfall/storage/demand time series. |
| Drainage upgrade | INR 5,000,000 | Upgrade one eligible reference asset; +0.12 m3/s illustrative capacity change; does not change runoff generated. |


For the coding fixture use a displayed default capital budget of INR 20,000,000 (2 crore), with editable range. This is NOT a budget allocated to Yelahanka. Give each type a separate life/maintenance record (source or D-grade assumption) before lifecycle-cost calculations. Do not generate artificial positive carbon/heat benefits when coefficients are not supported.

### 5.2 Decision variables and objective strategy

Let x[z,j,k] denote the nonnegative integer count (often binary 0/1) of candidate option k for intervention j in zone z. Solve for feasible investments that address flood, usable-water, heat-exposure and carbon goals alongside economic cost and equity. Keep each physical outcome in its original unit; convert to normalised benefit dimensions using fixed, published or disclosed bounds solely for optimisation/scoring.

Primary solver: PuLP with CBC (or SciPy MILP if dependency constraints demand). Use a user-visible weighted objective for the Balanced/Flood-first/Water-first/Heat-first/Equity-first modes; enforce budget, eligibility and minimum safeguards as hard constraints. Collect multiple feasible candidates and show non-dominated alternatives from the candidates actually generated. Do not claim a mathematically complete Pareto frontier unless computed.

### 5.3 Hard constraints and fairness

- Capital budget: Σ(project unit capex × chosen units) ≤ available investment capital.

- Physical capacities: eligible roof area, plantable land, drainage upgrade capacity, maximum tanks/project count and site-specific installation requirements.

- Intervention dependencies/exclusions: minimum suitable site requirements; shared roof/land resources; unavailable or unverified projects blocked.

- Equity: an explicit benefit-floor or penalty/weight for exposure-normalised improvements in designated vulnerable zones; show all group outcomes. Infeasible thresholds must be reported and explained.

- Commitment status (advanced): fixed/completed projects remain in a replan; available budget applies only to the remaining uncommitted portfolio.

### 5.4 Optimiser output

Return solver status, applied weights, total capex/LCC, selected project units and zones, constraint utilisation, per-zone benefits and residual risks, physical and normalized objective values, alternative portfolio IDs, model assumptions, runtime and a concise solver diagnostic. A failed or infeasible run must never be shown as successful.

### 5.5 Comparison baseline

Build “no investment” and a feasible equal-spend or transparent conventional-priority baseline. Apply exactly the same budget, candidate eligibility, climate inputs and environmental evaluator to all strategies. The optimised plan may win on its chosen objective while losing on other metrics; report both honestly.

### 5.6 Mathematical formulation: implementable MILP

Indices: k = eligible candidate investment unit (across every site, zone and all four intervention types); z = zone; m in {F, W, H, G} is flood/overflow exposure, usable water, heat-exposure and net CO2e benefit; s = scenario. x[k] is binary for an indivisible unit, or bounded nonnegative integer for approved repeatable units. Only a prevalidated candidate may enter the feasible set.

Required scenario coefficient b[k,m,s] is the estimated PHYSICAL benefit of one unit, evaluated against the same no-investment baseline; negative coefficients for harmful effects must be preserved. All b are generated by source-labelled domain models, never by Bedrock. For the initial MILP, freeze a single linearised coefficient matrix for each scenario. Keep raw benefits in their original units.

Use fixed reference scales tau[m] > 0 (e.g., policy targets or documented, fixed reference maxima) that are unchanged across the competing portfolios and named shock comparisons. Normalised delta[m] = sum(b[k,m,s]*x[k])/tau[m]. Do not dynamically re-normalise each portfolio with its own extrema; do not discard adverse (negative) benefits.

The scalarised initial objective is: MAX sum_m w[m]*delta[m] + wE*EquityGain(x) - wC*(sum(LCC[k]*x[k])/tauCost). Report the original metric vector alongside the score. All displayed weights are nonnegative and normalised to sum to one (including cost/equity if selected). A mode is simply a documented weight preset, not a separate secret scoring rule.

EquityGain(x) = sum_z v[z] * RiskReduction[z,x] / max(Population[z],1) / tauEquity, where v[z] is a publicly visible vulnerability multiplier with a disclosed source or synthetic status. Because environmental effects and equity can share underlying quantities, describe equity as a DISTRIBUTION preference, not additional physical risk reduction.

### 5.7 Hard constraints and edge-state semantics

- Capital: sum(capex[k]*x[k]) <= Bavailable. Treat lifecycle cost as a separate objective/reporting metric unless a lifecycle spending ceiling is explicitly defined.

- Site/land/roof: for each physical resource r at a site, sum(usage[k,r]*x[k]) <= capacity[r]. Only apply shared roof constraints across projects using that same roof polygon or candidate pool.

- Eligibility: x[k] <= unit_cap[k]*eligible[k]. Unknown eligibility is treated as unverified, not automatically available.

- Logical dependencies: x[a] <= x[b] when installation of a requires b; x[a]+x[b] <= 1 for exclusive binary options; validate quantities in the generalized case.

- Equity floor: for each designated priority zone z, BenefitToZone[z,x] >= explicit_floor[z] only where metrics/thresholds have compatible units. An infeasible user-requested floor must return an honest infeasible result and suggested relaxation.

- Committed investments (optional P2): fix x[k]=1 for committed projects; subtract already-obligated capex from the REVISED total envelope before allocating new discretionary capital. If commitments exceed the revised envelope, flag committed overspend rather than claiming feasibility.

- Nonnegative investment counts and bounded unit caps; no negative budgets, undefined normalization targets or unsupported project categories.

### 5.8 Interaction-aware evaluation and solver honesty

MILP optimises a documented LINEARISED SURROGATE, not automatically the exact nonlinear environmental system. After selection, run an independent portfolio-level evaluator with shared-area rules, storage limitations, cross-site drainage interactions and scenario-dependent effects. Store the surrogate score and re-evaluated outcomes separately.

If portfolio re-evaluation violates a hard capacity rule, reject the candidate and add a no-good constraint or refine the catalogue, then resolve. If it changes the relative performance materially, recompute all compared shortlisted portfolios through the same evaluator and report “best among evaluated feasible candidates,” not an unsupported exact nonlinear global optimum.

For four intervention types across 3 zones, first build and verify a small binary catalogue before increasing candidate counts. Use fixed time/memory limits and report the solver status: optimal, feasible_time_limit, infeasible, or error.

### 5.9 Construction of the benefit coefficients

| Metric | Physical effect assigned to each candidate | Reporting unit |
| --- | --- | --- |
| Flood | Change in excess peak-flow/capacity screening and separately retained runoff volume; derived from area/C/I and upgrade capacity. | m3/s exceedance; m3/event retained |
| Water | Additional usable water served by bounded tank and demand balance against same rainfall scenario. | m3/year |
| Heat | Decrease in population-weighted heat-exposure index with water/maintenance corrections. | person-index units |
| Carbon | Net avoided + sequestered − embodied/O&M emissions over stated horizon, with missing pathways excluded and flagged. | tCO2e / horizon |
| Equity | Who receives benefits, per-1000-resident comparisons and priority-zone floor; not independent physical benefit. | group/zone-index |
| Economics | Capex constraint and lifecycle monetary penalty/report; consistent years and price units. | INR; INR LCC |


### 5.10 Default objective settings and transparency

Use the following weights solely as reproducible initial DESIGN DEFAULTS, not proven municipal values: Balanced F=.25, W=.20, H=.20, G=.10, Equity=.15, LCC=.10; Flood-first F=.55 with remaining .45 distributed transparently; Water-first W=.55; Heat-first H=.55; Equity-first Equity=.45. Users can inspect and edit all weights. Record exact weights with each run.

Start with a three-zone reference allocation, and supply at least two feasible alternatives. Non-dominated sets must be labelled “among enumerated/sampled feasible candidates” unless a full frontier was explicitly computed.

## 6. Scenario simulator and climate robustness

| Scenario | What changes | Required output |
| --- | --- | --- |
| Normal baseline | Original environmental inputs and available capital. | Chosen portfolio and modelled outcomes. |
| Extreme rainfall | Transparent storm intensity multiplier / design event; recomputed runoff and capacity consequences. | Old portfolio under shock; feasible reoptimised alternative; risk/cost/equity trade-offs. |
| Drought | Lower water availability, altered rainfall distribution, limits on irrigation/cooling yield. | Changed water yield, tree benefit and selected projects. |
| Sudden budget cut | Reduced uncommitted capital; optional locked/committed investments. | Which candidates remain affordable, which are deferred, and why. |


### 6.1 Scenario logic and scientific honesty

Represent each shock by a saved parameter override, not an opaque AI-generated narrative. Stress assumptions are user-defined test conditions, not predictive statements about when a drought or extreme storm will occur. Compute (a) performance of the original portfolio under the shock and (b) a scenario-specific reoptimised feasible portfolio. Both outputs use the same metric units and environmental model version.

### 6.2 Robustness extension — P1

Sample a small matrix of plausible effectiveness and climate assumptions (for example a disclosed ± range from a documented coefficient, not a statistical confidence interval). For each candidate plan, calculate worst-case outcome, mean, constraint violations and max regret versus each scenario optimum. Label these “sensitivity ranges” until empirically calibrated.

### 6.3 Named default shocks (illustrative, editable)

| Scenario ID | Default stress settings (NOT predictions) | Implementation guard |
| --- | --- | --- |
| normal | Rainfall multiplier 1.00, irrigation factor 1.00, no budget reduction. | Freeze input snapshot and time step. |
| extreme_rain | Design storm intensity multiplier 1.30; original duration/area assumptions retained. | Recompute runoff and conveyance exceedance; no arbitrary flood-depth change. |
| drought | Rainfall availability factor 0.60; tree evaporative-cooling factor 0.70; irrigation need tracked. | Recompute harvest time series, water demand, heat benefits and constraints. |
| budget_cut | Revised total capital envelope = 0.70*baseline; commitments handled separately. | Re-solve feasible portfolio; preserve already obligated projects if toggle enabled. |


The four factors above are user-editable TEST SCENARIOS and not observed 2026 events or climate forecasts. The original portfolio is evaluated with frozen x under each new environment before a second, reoptimised portfolio is calculated. Saved results share a baseline version and a common outcome evaluator.

## 7. User experience and decision explainer

| Tab | Essential view | What the judge changes |
| --- | --- | --- |
| 1. City Intelligence | Pilot zone map, data coverage and risk layers; candidate sites and physical availability. | Select zone/map layer. |
| 2. Investment Optimiser | Budget, priority modes, weights, equity floor, solver status, selected projects and cost/benefit plots. | Budget, priorities and feasibility settings. |
| 3. Climate Shock Lab | Baseline vs old-plan-under-shock vs reoptimised result; project additions/removals. | Choose shock and parameters. |
| 4. Decision Intelligence | Alternatives, score contributions, beneficiary distribution, uncertainties and sources. | Compare saved run IDs; ask for reasons. |


### 7.1 Evidence-grounded explanations

First construct deterministic explanation objects from the solver and physical evaluator: reason selected, reason rejected, binding constraints, objective contributions, equity results, uncertain assumptions and potential unintended consequences. Only then, optionally ask Amazon Bedrock to rewrite that structured evidence into clear planning language. Reject or fall back if the narration contradicts saved numbers. [R7, BP]

### 7.2 Unintended consequences checklist

- Water consumption for tree maintenance or green infrastructure during drought.

- Maintenance liability, runoff overflow migration, drainage bottlenecks and roof-capacity competition.

- Unequal benefits, inaccessible greenspace and possible gentrification concerns, labelled as risks rather than predictions. [R8]

- Uncertain benefits from transferred studies, coarse-resolution rainfall data or missing local evidence.

### 7.3 Shareable planning brief — P1

Generate a one-page decision summary from an immutable run ID: location, date, scenario, budget, objectives, selected projects, total cost, benefits by zone, trade-offs, evidence grade, limitations and responsible review actions. Do not permit the exported report to diverge from the saved run.

## 8. Immutable runs, schemas and reproducibility

### 8.1 Why this is essential

Every user change creates a new, reproducible run snapshot (or reuses an exact cached result with provenance). This is a principal addition from the uploaded AWS/CKAN blueprint, especially its typed contracts, immutable run IDs and visible data gaps. [BP]

### 8.2 Minimal typed data objects

| Object | Must contain |
| --- | --- |
| Indicator | key, value, unit, direction, zone, spatial scale, source, observation date, evidence grade, uncertainty range/flag |
| CandidateProject | project ID/type/zone, resource requirements, eligibility, capex/O&M, unit benefits, interactions, evidence |
| ScenarioRequest | area and baseline version, budget, priority weights, equity settings, shock parameters, committed IDs |
| RunResult | run ID, created time, dataset/model version, solver status, selected projects, metrics, scores, assumptions and citations |


### 8.3 Version and caching rules

- Use a deterministic input hash of zone snapshot, intervention catalogue version, objectives/weights, hard constraints, shock overrides and model version.

- Save a manifest and all outputs as JSON, initially under local /runs and optionally upload to a private S3 prefix. Never overwrite a historical run in place.

- Validate numeric types, non-negative costs, units and categorical choices with Pydantic before invoking the solver.

- Keep raw physical values and normalized scores separate; display both where useful.

### 8.4 Fully specified run object and contract invariants

Use Pydantic v2 schemas (or equivalent validated dataclasses) to implement these exact internal contracts. All arrays/maps are immutable snapshots when saved, and all scalar output fields require units or a corresponding unit definition.

- Indicator: indicator_id, zone_id, numeric_value nullable, unit, better_direction, source_id, observation_period, geometry_scale, evidence_grade, uncertainty_low/high, missing_reason.

- CandidateProject: candidate_id, zone_id, site_id, type enum[green_roof, urban_forest, rainwater_harvesting, drainage_upgrade], capex_inr, opex_inr_y, life_y, resource_demands, upper_bound, prerequisites, exclusions, coefficients_by_scenario, source_ids.

- ScenarioRequest: area_id, baseline_version, project_catalog_version, model_version, budget_inr, weights (F/W/H/G/Equity/LCC), equity_floor, scenario_id, overrides, committed_candidate_ids.

- RunResult: immutable run_id, input_hash, created_at_utc, solver_status, selected_candidate_counts, raw_objectives_with_units, normalised_components, score_contributions, constraint_slack, baseline_and_shock_metrics, outcomes_by_zone, assumptions, gaps, source_ids, warnings.

- DecisionExplanation: selected_and_rejected_reasons, relevant_computed_numbers, counterfactuals, limitations, source_ids, explanation_source (deterministic/Bedrock), validation_passed.

- Every API/function must return a structured error for missing sources, infeasible constraints, invalid normalization bounds or unexpected model arithmetic; never fabricate a populated success object.

### 8.5 Canonical engine interfaces

```text
load_baseline(area_id:str, version:str) -> BaselineSnapshot
validate_catalogue(snapshot, catalogue) -> EligibilityReport
evaluate_portfolio(snapshot, projects, scenario) -> PhysicalOutcomes
build_linear_coefficients(snapshot, catalogue, scenario) -> CoefficientMatrix
optimise(request, snapshot, coefficients) -> SolverResult
run_scenario(request) -> RunResult
explain_deterministically(run:RunResult) -> DecisionExplanation
save_run(run:RunResult) -> RunRef    # do not overwrite
load_run(run_id:str) -> RunResult
```

For a Streamlit single-process MVP these are Python interfaces; FastAPI endpoints are optional and should not be added merely for architectural appearance. All UI computations call these functions rather than duplicating formulas in widgets.

## 9. AWS and application architecture

### 9.1 Default architecture: smallest valuable deployment

| DATA FLOW; Curated source layers and assumptions → Pydantic validation / optional S3 snapshots → Python physical evaluators → MILP allocation → scenario recomputation → immutable run result → Streamlit dashboard and deterministic explanation → optional Amazon Bedrock narration. |
| --- |


| Service / tool | Disposition | Concrete value and timing |
| --- | --- | --- |
| Amazon S3 | Use; P0/P1 | Curated input snapshots, scenario results, manifests and provenance. Local cache must work without AWS. |
| Amazon Bedrock | Conditional P1 | Planner-friendly narration grounded in run JSON/evidence; no numerical decisions. Confirm model/IAM access before use. |
| AWS Lambda | Optional | Introduce only when server-side shared optimisation execution materially helps; avoid deployment work for a local solver. |
| Amazon Location Service | Optional | Basemaps/geocoding if licensing and implementation are straightforward; GeoJSON/Plotly already suffice. |
| Glue / Athena | Defer | No need for crawlers or SQL-over-data-lake for a handful of prepared CSV/GeoJSON datasets. |
| SageMaker / AWS Batch | Defer | No large training task or high-volume batch solver in the 24-hour MVP. |
| SimSpace Weaver / EventBridge | Defer | No distributed spatial simulation or scheduled climate-refresh need. |
| OpenSearch / QuickSight / Grafana | Defer | Compact local evidence register and application charts cover present needs. |
| CKAN / EKS / PostGIS stack | Do not build | Heavy enterprise data catalogue; no direct benefit to the required four-intervention optimiser. |
| Codex Astra / GitHub | Use | Primary implementation agent, source control and repeatable test/debug workflow. |


### 9.2 Hosting and fallback

Use Streamlit on a dependable Python-capable host (Streamlit Community Cloud if available), with the same local application runnable directly. Consider AWS container hosting only if access and deployment experience already exist. Do not rely on App Runner as the default for an unverified new account. The project must remain demonstrable when optional AWS integrations are unavailable.

### 9.3 Security / cloud hygiene

- Use least-privilege IAM for S3 object read/write prefixes and Bedrock invocation. No browser-embedded credentials, committed secrets, public write access or personally identifying demo data.

- Prefer short-lived development access, private buckets, environment-based secrets, explicit service region, cost monitoring and documented setup steps.

- Log errors without exposing credentials; validate user inputs on the application side and never trust LLM text as executable results.

### 9.4 Concrete AWS runbook: smallest valuable integrations

1. Prerequisites: confirm an accessible AWS account, permissions, Region, budgets, and whether a Bedrock model is available in that Region. Verify identity with “aws sts get-caller-identity”; do not record the resulting account ID in public repo artifacts.

1. Create one private S3 bucket (globally unique name chosen during deployment). Use prefixes input/raw/, input/curated/, provenance/, runs/, and exports/. Enable default encryption and block public access. Versioning is recommended if it does not delay core development.

1. Apply least-privilege access: s3:ListBucket on this bucket; s3:GetObject on curated/provenance; s3:PutObject on runs/exports. For Bedrock, allow bedrock:InvokeModel only for an approved model/resource in the selected Region, plus streaming access only if actually used.

1. Use boto3 Python adapters behind clear interfaces. Load a versioned snapshot with a local fallback and persist run JSON with an input hash. Never require S3 for mathematical calculations.

1. For Bedrock, validate permitted model access, quota and IAM. Send only a redacted, structured RunResult subset plus approved evidence text. Validate any numeric strings returned against the original result, rejecting contradictions. Cache deterministic explanation if the API fails.

1. Set AWS budget alerts before testing paid services. Stop unused hosted components after the event. Never introduce EKS, NAT, OpenSearch or large data services just to match a diagram.

1. Deploy Streamlit on a reliable Python-capable host if AWS hosting cannot be verified early; maintain a local offline demo. If cloud deployment is desired and expertise exists, consider a container-based AWS host, but do not block P0.

### 9.5 Environment and security configuration

```text
AWS_REGION=choose_region_after_access_check
S3_BUCKET=private_bucket_name
S3_CURATED_PREFIX=input/curated/
S3_RUNS_PREFIX=runs/
BEDROCK_MODEL_ID=approved_region_specific_model_id
C1V1C_OFFLINE_MODE=true_or_false
C1V1C_BASELINE_VERSION=baseline_v1
C1V1C_MODEL_VERSION=model_v1
```

Use AWS SDK default credential providers for local/cloud execution. Secrets belong in environment secret managers/host secret settings; never store access keys in source control, browser JavaScript or the exported planning report. Keep an example env template without real secrets.

### 9.6 Exact demonstration of AWS value

| AWS component | Live verification | Fallback if blocked |
| --- | --- | --- |
| S3 | Show one curated baseline object loaded, its version/key and a saved JSON run under runs/. | Local identical baseline JSON and local immutable runs/ folder. |
| Bedrock | Ask a judge a “why this allocation?” question; explanation quotes current solver figures and citation IDs. | Deterministic text from recorded score components and constraints. |
| Cloud hosting | Published app opens from submitted URL; no embedded AWS key. | Local app launch and a frozen recorded end-to-end demo. |


## 10. Repository architecture and Codex workflow

### 10.1 Repository structure

```text
c1v1c-tulabhara-ai/
  app.py                    # Streamlit entry point
  requirements.txt          # pinned core dependencies
  AGENTS.md                 # engineering rules for Codex
  docs/                     # PS, plan, model assumptions, source register
  data/                     # pilot zone, site, intervention, source datasets
  engine/
    schemas.py              # Pydantic objects and validation
    baseline.py             # data and risk normalization
    physical_models.py      # runoff, water, heat, carbon, economics
    suitability.py          # eligible sites and interaction constraints
    optimiser.py            # MILP, score breakdown, alternatives
    scenarios.py            # shocks and old/new-plan evaluation
    equity.py               # population benefit and safeguards
    explanations.py         # deterministic reasons and evidence
    run_store.py            # immutable local/S3 snapshots
  services/
    s3_adapter.py           # optional AWS data/results
    bedrock_adapter.py      # optional grounded narration
  pages/                    # four Streamlit tabs
  tests/                    # unit, solver, scenario, app smoke tests
  demo/                     # frozen input, scripts, screenshots and backup video
```

### 10.2 Agent operating rules (put in AGENTS.md)

- Read the original Sustainable Development PS and this plan before coding. All five modules and four interventions are mandatory.

- Build the smallest end-to-end vertical slice before parallel feature expansion; integrate behind shared Pydantic schemas.

- Never fabricate environmental measurements, output numbers, citations, solver success or AWS integration status.

- Use explicit units, applicability notes, assumptions and source IDs for every model parameter.

- Keep deterministic calculations separate from Bedrock narratives. Make optional cloud dependencies fail safely.

- Write tests concurrently with the engine; report a blocked or incomplete requirement openly.

### 10.3 Task boundaries

Issue separate Codex tasks for (a) schemas and data loader, (b) physical evaluators, (c) MILP solver/equity, (d) scenarios and run store, and (e) Streamlit/AWS integration. Merge only after each component passes its contract tests. No agent may change shared schema fields without notifying all module owners.

## 11. Team roles and integration cadence

| Owner | Primary responsibilities | Handoffs / tests |
| --- | --- | --- |
| Anish — Product & Integration Lead | PS compliance, architecture, data contracts, merge decisions, mentor questions, risk register, end-to-end testing and pitch. | Approve schema, preserve five-module checklist, integration and final demo. |
| Member 2 — Optimisation | MILP model, normalisation, constraints, fairness, Pareto shortlist, infeasibility handling. | optimiser.py + solver/constraint tests. |
| Member 3 — Environmental & Data | Study-area input sourcing, runoff/water/heat/carbon models, economics, site suitability, provenance. | Physical parameter matrix + model tests. |
| Member 4 — UI & AWS | Streamlit map/charts, run comparison, S3 and Bedrock adapters, deployment and fallback. | Working interactive app + smoke tests. |


Coordination rule: 15-minute integration check roughly every 2–3 hours; notify the lead immediately on schema changes, external API access failures or estimates that cannot be scientifically supported.

## 12. 24-hour implementation schedule

Event timetable supplied by the team: 23 October 2026, 10:00 build start; 15:00 mentoring; 24 October 2026, 10:00 build concludes/final judgement begins. The schedule below uses hours from build start and should be treated as a time-box rather than a claim that an individual stage is already complete.

| Time / gate | Build tasks | Done means |
| --- | --- | --- |
| H0–H2 \| 10:00–12:00 | Freeze zone scope; data snapshots; Pydantic schemas; project catalogue; objective bounds; assignments; initialize repository. | Validated schemas and one-zone/two-intervention test fixture. |
| H2–H5 \| 12:00–15:00 | Implement core physical coefficients, eligibility, capex, and first MILP; basic CLI/display. | Optimizer produces a feasible allocation with constraints; ready for mentoring. |
| H5–H8 \| 15:00–18:00 | Finish four interventions, three zones; implement rainfall/drought/budget overrides and old/new plan. | All three shocks cause real recomputation with consistent units. |
| H8–H12 \| 18:00–22:00 | Connect four Streamlit tabs, map, costs, benefits, equity and deterministic explanations. | All five official MVP modules work end-to-end. |
| H12–H15 \| 22:00–01:00 | Add same-budget baseline comparison, run-store history, S3 if available and Bedrock after model checks. | Comparable saved runs and meaningful AWS demonstration. |
| H15–H18 \| 01:00–04:00 | Harden carbon/LCC evidence, objective breakdown, uncertainty sensitivity; optional decision brief. | No unsupported impacts; evidence and caveats visible. |
| H18–H21 \| 04:00–07:00 | Test solver, physics, scenarios and deployment; freeze data and model; screenshot backup. | Release candidate passes P0 checks and offline fallback. |
| H21–H24 \| 07:00–10:00 | Rehearse pitch, finalize README, slide evidence, submission; only critical fixes. | Working public/local demo and 3-minute judge narrative. |


| STOP-WORK RULE; If the H5 optimiser is not working, suspend visual polish and AWS extras. If the H12 five-module workflow is incomplete, cut all P1/P2 features. At H21 freeze the model and focus on a stable demonstration. |
| --- |


## 13. Acceptance tests and scientific verification

### 13.1 Automated tests

| Test family | Required cases / assertions |
| --- | --- |
| Input/contract | Reject negative budget and cost; unknown units; invalid weights; unverified site availability; bad or missing source metadata. |
| Physical boundaries | Capture ≤ rainfall-derived potential; usable water ≤ demand/storage; land/roof units consistent; no impossible negative runoff. |
| MILP and eligibility | Respect budget; no over-capacity projects; dependencies/exclusions; fairness floor; valid solver status; zero-budget case. |
| Scenario invariants | All three shocks distinct; same model version; old plan not silently redesigned; new plan reoptimised; results reproducible. |
| Comparison integrity | Baselines share objective normalisation, geography, constraints, evaluation horizon and budget with selected optimum. |
| Explainability | Every quoted metric in generated explanation matches saved run; missing evidence clearly marked; no invented carbon/heat figures. |
| Run persistence | Unique run ID and input hash, immutable saved JSON, source/model version preserved and retrievable. |
| Cloud failure | App usable with local snapshot if S3/Bedrock unavailable; no leaked AWS credentials. |
| Interface smoke | Four tabs load; sliders change decisions; charts reflect current run; data gaps visible; no broken submission links. |


### 13.2 Quantitative validation

- Compare MILP output with brute-force enumeration on a tiny catalogue (one zone, several binary projects) to confirm optimum and feasibility.

- Check model directions on controlled inputs: more rainfall should not mysteriously reduce reference runoff; larger tank should not worsen usable yield solely due to implementation bugs.

- Compare physical and objective metrics independently; plot any trade-off instead of interpreting one weighted number as objective truth.

- Clearly separate sensitivity bands from calibrated probabilistic prediction intervals.

### 13.3 Acceptance status vocabulary

Each capability is marked PASS / PASS WITH DISCLOSED LIMITATION / BLOCKED. No fabricated 100%-complete status. Any blocked P0 item is a release concern and requires a fallback plan.

### 13.4 Numerical unit-test fixtures with expected answers

| Fixture | Input | Expected output / assertion |
| --- | --- | --- |
| Peak runoff | C=0.70; I=50 mm/h; area=10 ha. | Q=0.00278×0.70×50×10 = 0.973 m3/s. |
| Drainage versus generation | Above flow 0.973; capacity initially 0.80 then 1.05 m3/s. | Runoff remains 0.973; exceedance goes from 0.173 to 0 m3/s. |
| Rainwater tank 3 periods | K=10 m3; S0=0; inflows=[8,8,0]; demands=[5,5,5] m3. | Served=[5,5,5]; end storage=[3,5,0]; spill=[0,1,0]; total served=15 m3 > tank K. |
| Tiny binary optimiser | Project A cost4/benefit7; B cost5/benefit9; C cost3/benefit5; budget8. No additional constraints. | Choose B+C, cost8, benefit14. A+C yields12; A+B cost9 infeasible. |
| Equity infeasibility | Priority zone requires 10 units of benefit; all eligible candidates together provide at most 8. | Return infeasible with binding reason; NEVER relax threshold silently. |
| Budget commitments | Revised total budget6; precommitted project costs5; option price2. | Remaining discretionary budget1, so new option cannot be added. |
| Source gaps | Intervention effect has no source or assumption label. | Validation fails or marks coefficient unverified; no silent zero substitution. |
| Shock replay | Recalculate original x under rainfall shock, then optimise separately. | Frozen original project counts unchanged in old-plan test; new run IDs distinct. |


### 13.5 Evidence and scientific integrity gates

- Each physical submodel has at least one known-answer fixture and a conservation/boundary assertion; tests distinguish physical amount from proxy index.

- Each named shock creates a new run with parameter overrides and affected coefficients; identical inputs reproduce identical numeric results (subject to solver tolerances).

- Solver optimum is verified by a brute-force oracle in the tiny fixture; larger runs report solver status, gap (if available), and runtime.

- Decision reports cite sources for input facts and mark synthetic data visibly, including in screenshots and exports.

- One model integration test checks intervention overlap and rejects double counting for a shared roof polygon.

- Carbon claims require documented factor and time horizon; absent sources produce “not estimated,” not a fake zero.

- Production deployment and all AWS service usage remain out of scope until P0 acceptance is verified.

## 14. Presentation and judge-proof demonstration

### 14.1 Three-minute script

| Segment | Action | Proof shown |
| --- | --- | --- |
| 0:00–0:25 \| Problem | Select pilot area; show contrasting flood, heat, water and equity exposure. | Local context + sourced baseline. |
| 0:25–1:05 \| Decide | Enter illustrative budget (e.g., INR 10 crore) and choose Balanced mode; run optimiser. | Chosen projects, feasible costs, constraint status and zone benefits. |
| 1:05–1:45 \| Compare | Compare no-investment and feasible equal-allocation plans. | Computed improvement for chosen objective plus honest trade-offs. |
| 1:45–2:20 \| Shock | Trigger heavy rain or budget cut; test old plan and reoptimise. | Change in feasibility, intervention mix and beneficiaries. |
| 2:20–2:45 \| Explain | Open a selected project; inspect constraint, score component and evidence; optional Bedrock summary. | Traceable explanation and limitations. |
| 2:45–3:00 \| Close | Show one saved run ID, provenance and test status. | Why C1V1C is actionable, reproducible and transparent. |


### 14.2 Questions to rehearse

- Where is the AI? — Constrained decision optimisation plus optional evidence-grounded language explanation; no invented decisions.

- How is it scientifically credible? — Source register, physical limits, explicit assumptions, reproducible outputs and validation tests.

- Why this intervention? — Show objective contributions, constraints, alternative benefit/cost and neighbourhood equity.

- Do the numbers represent real Bengaluru outcomes? — Distinguish observed baseline inputs from illustrative or transferred coefficients.

- Why only selected AWS services? — Each retained service supports a visible need; larger managed data/AI services are unjustified for a small time-boxed prototype.

- Can it work without AWS or internet? — Demonstrate offline mode from a frozen dataset and deterministic explanations.

## 15. Risks, fallback and release decision

| Risk | Trigger | Fallback / owner |
| --- | --- | --- |
| Data unavailable | No reliable ward/site layer by early build. | Use transparent illustrative zones/capacities with retained local research context; Data lead. |
| Solver incomplete | No feasible MILP by H5. | Reduce to one-zone set, brute-force-test portfolio logic, restore multi-zone after solver passes; Optimisation lead. |
| Scientific mismatch | Environmental submodels double-count or yield implausible results. | Disable unsupported metric/claim, expose limitation, reduce interaction cases; Data lead. |
| AWS credentials/model access | IAM, cost or model eligibility blocks access. | Run local curated snapshot and deterministic explainer; UI/AWS lead. |
| Deployment fails | Hosted URL unavailable at H21. | Run on local laptop, include screenshots and prerecorded end-to-end demo; Integration lead. |
| Features proliferate | P1 blocks an unfinished P0. | Freeze bonus work, return to mandatory checklist; Anish. |
| Misleading claims | Demo copy asserts precise flood depth, ROI or proven impact. | Replace with evidence-based wording and show calculations / assumptions; Anish. |


### 15.1 Must-have vs deferrable backlog

| Priority | Includes |
| --- | --- |
| P0: release-critical | Five PS modules, four intervention types, three shocks, feasible MILP, source/assumption register, equity results, deterministic explanation, immutable run and tests. |
| P1: impact | Expanded LCC/carbon evidence, comparative conventional baseline, sensitivity stress test, S3 and Bedrock integration, printable brief; minimum carbon and cost treatment remains P0. |
| P2: post-MVP | Committed construction switch, expanded Pareto analytics, advanced GIS, external policy RAG, more AWS services and polished multi-page export. |
| Out of scope | CKAN/EKS deployment, SimSpace Weaver digital twin, validated flood-depth forecasts, new deep-learning training, actual public-policy deployment. |


### 15.2 Release declaration

| DEFINITION OF DONE; A judge can select a zone, enter budget/priorities, obtain a physically feasible recommendation covering the four intervention choices, view benefits and equity by zone, rerun under all three named shocks, inspect why/why not explanations and retrieve an auditable saved run. Every important number has a source or assumption and an appropriate limitation. |
| --- |


## 16. Locked build decisions, open questions, and evidence gates

| Item | Status now | How it is resolved for implementation |
| --- | --- | --- |
| Five PS modules / four interventions | LOCKED | Never remove or substitute. |
| Three zones in Yelahanka pilot | DESIGN TARGET | Verify polygons/coherent catchment. If not possible, label illustrative zones; no false administrative claims. |
| Source values for rainfall, heat, water and vulnerable groups | DATA GATE | Member 3 records per-field provenance and spatial resolution; unsupported values remain illustrative. |
| Primary optimiser | LOCKED | MILP on precomputed, documented scenario-dependent coefficients. |
| Weights and horizons | DESIGN DEFAULT | Visible weights, T=10 y and r=5% illustration; user can inspect/override. |
| Environmental benefits | MODEL GATE | Separate runoff, storage balance, heat-index and carbon-ledger submodels; verify fixtures. |
| AWS services | CONDITIONAL | Use S3 if access works; Bedrock if approved model and cost allow; no mandatory EKS/CKAN. |
| Public deploy URL | RELEASE GATE | Try reliable hosting, retain fully offline local launch and demo backup. |


### 16.1 Definition of release-ready

Release requires the P0 feature set to be implemented, independently testable, and fully integrated. Every required module must have a testable implementation; any simplified environmental method must show its domain, assumptions and limitations. If a verified dataset cannot be sourced, the final demonstration MUST remain clearly identified as synthetic or mixed-evidence, not quietly upgraded to a real-city evidence claim.

### 16.2 Team handoff matrix by code boundary

| Owner / files | Input contract | Output / acceptance |
| --- | --- | --- |
| Environmental modeller: physical_models.py, baseline.py, data/ | Validated baseline, scenario parameters, project dimensions. | Per-project scenario benefits with physical units and source IDs; numerical fixtures pass. |
| Solver engineer: optimiser.py, equity.py | Feasible projects, coefficients, limits, user priorities. | SolverResult with status, selected x, objective parts, constraint slacks; oracle tests pass. |
| App/cloud engineer: app.py, pages/, services/ | Immutable RunResult and source records. | Four usable tabs, saved history, S3/Bedrock optional, offline smoke test. |
| Anish: schemas.py, integration tests, docs/ | All module outputs and official PS checklist. | Integrated validation, demo acceptance, sign-off and competition submission. |


## 17. Research-to-implementation evidence map

| Reference | Exact contribution to project | Do not overclaim |
| --- | --- | --- |
| [PS] | Mandatory scope, interventions, scenarios, AWS service suggestions and expected decision outcomes. | Does not supply specific data, methods or validated coefficients. |
| [BP] | Typed contracts, data gaps, score breakdown, immutable run IDs, clear service boundaries. | Its toy additive simulator and CKAN/EKS architecture are not required for this MVP. |
| [R1] ATREE Bengaluru | Catchment framing; flood hazard/exposure/vulnerability distinction; local study context. | Its calibrated HEC-HMS/HEC-RAS findings are not automatically reproduced by our screening model. |
| [R2] Leng et al. | Joint green–grey optimisation and explicit uncertain climate conditions. | Its outcomes or model parameters are not transplanted to Bengaluru. |
| [R3] Manivasagam et al. | Building-footprint-based rooftop assessment and water feasibility workflow. | Rooftop footprints do not prove structural eligibility. |
| [R4] Gobatti et al. | Soil moisture and urban form affect tree cooling; drought reduces certainty. | Zurich cooling magnitudes cannot be used as Bengaluru observations. |
| [R5] Nathawat et al. | Suitability logic using land cover, temperature, moisture, slope and rainfall. | Jaipur-specific weights/results are not Bengaluru coefficients. |
| [R6] Pan et al. | Direct and indirect carbon pathways, resource-saving interactions and spatial priorities. | EU carbon reduction percentages are not a local factor. |
| [R7] Kuznetsov et al. | Ground language explanations in numerical climate data and literature. | LLM explanations do not validate physical predictions. |
| [R8] Dorner et al. | Social side-effects must be contextual, not assumed universally. | Greening does not imply demonstrable gentrification in our zones. |
| [R9] Caparros-Midwood | Non-dominated options and trade-offs in spatial planning. | Only sampled solutions are claimed unless a complete Pareto frontier is computed. |
| [R10] Castro | Equity in the allocation objective rather than only downstream displays. | Equity weights and vulnerability data remain policy/data assumptions. |


## Appendix A. Minimum data dictionary

| Dataset | Minimum fields |
| --- | --- |
| zones.csv | zone_id, label, geometry_ref, area_ha, population, vulnerability_band, built_fraction, vegetation_fraction, water_demand_m3, base_heat_index, source_ids |
| sites.csv | site_id, zone_id, site_type, land_area_m2, suitable_roof_m2, slope_class, drainage_asset, eligible_types, evidence_grade |
| interventions.csv | project_id, site_id, intervention_type, capex_inr, opex_inr_yr, horizon_yr, resource_needs, max_units, requires, excludes |
| baseline_climate.csv | scenario_id, rainfall_mm, intensity_mm_h, temperature_proxy, time_period, data_resolution, source_id |
| effect_factors.csv | type, outcome_metric, effect_per_unit, unit, source_id, low_bound, high_bound, applicable_scenario |
| sources.csv | source_id, title, url_or_file, publication_date, observed_at, spatial_scale, evidence_grade, limitations |
| runs/*.json | run_id, input_hash, timestamps, data_version, model_version, request, solver_status, selected_projects, outputs, limitations |


> Field names are the recommended internal schema, not columns supplied by the original problem statement.

## Appendix B. Example run contract

The following JSON is a structural example, not a computed or validated result. Numeric output placeholders are deliberately null until the solver and evaluator return values.

```text
{
  "run_id": "run_example_001",
  "area_id": "pilot_yelahanka_demo",
  "baseline_version": "baseline_v1",
  "catalogue_version": "interventions_v1",
  "model_version": "c1v1c_v1",
  "request": {
    "budget_inr": 100000000,
    "mode": "balanced",
    "equity_floor": null,
    "scenario_id": "extreme_rainfall",
    "shock_parameters": {"rainfall_multiplier": 1.25}
  },
  "solver_status": "not_run",
  "selected_projects": [],
  "capital_cost_inr": null,
  "lifecycle_cost_inr": null,
  "environmental_metrics": {},
  "neighbourhood_benefits": {},
  "score_breakdown": {},
  "constraint_checks": {},
  "evidence_sources": [],
  "assumptions": [],
  "data_gaps": []
}
```

## Appendix C. Citations and source register

The following references explain the scientific and technical rationale. They are evidence sources and architectural guidance, not claims that the project reproduces published results. Source links and specific coefficients used in the build should be recorded in sources.csv.

[PS]  Sustainable_Development(2).docx. “The Sustainability Paradox: Optimising a City That Cannot Afford to Grow Greener.” Original hackathon problem statement and MVP/AWS/expected-outcome tables.

[BP]  Urban Sustainability / Code-Level Blueprint (23 October 2026), 19 pages. Supplied architecture proposal; especially data contracts, immutable runs, evidence gaps, and AWS/CKAN trade-offs.

[R1]  Jamwal, P. et al. (2024). Building Resilience to Urban Floods: Strategy and Action Plan for Bengaluru. ATREE. ISBN 978-81-940887-9-0.

[R2]  Leng, L., Jia, H., Chen, A. S., Zhu, D. Z., Xu, T., & Yu, S. (2021). Multi-objective optimization for green-grey infrastructures in response to external uncertainties. Science of the Total Environment, 775, 145831.

[R3]  Manivasagam, V. S., Saai Shreyaa, G. V., & Ganesh, S. D. (2025). Food-energy-water sustainability in urban spaces: insights from open geospatial datasets in Coimbatore, India. Computational Urban Science, 5:54. DOI: 10.1007/s43762-025-00213-w.

[R4]  Gobatti, L., Bach, P. M., Maurer, M., & Leitão, J. P. (2025). Impact of soil moisture content on urban tree evaporative cooling and human thermal comfort. npj Urban Sustainability, 5:26. DOI: 10.1038/s42949-025-00220-0.

[R5]  Nathawat, R. et al. (2025). Urban Green Infrastructure Planning in Jaipur, India: A GIS-Based Suitability Model for Semi-Arid Cities. Sustainability, 17, 2420. DOI: 10.3390/su17062420.

[R6]  Pan, H. et al. (2023). Contribution of prioritized urban nature-based solutions allocation to carbon neutrality. Nature Climate Change, 13, 862–870. DOI: 10.1038/s41558-023-01737-x.

[R7]  Kuznetsov, I. et al. (2025). Transforming climate services with LLMs and multi-source data integration. npj Climate Action, 4:97. DOI: 10.1038/s44168-025-00300-y.

[R8]  Dorner, J., Scherner, M., Thaler, T., & Friesenecker, M. (2026). Taming the green gentrification cycle? Evidence from street greening in Vienna. Urban Geography. DOI: 10.1080/02723638.2026.2656265.

[R9]  Caparros-Midwood, D., Barr, S., & Dawson, R. (2017). Spatial Optimization of Future Urban Development with Regards to Climate Risk and Sustainability Objectives. Risk Analysis, 37(11). DOI: 10.1111/risa.12777.

[R10]  Castro, C. V. (2022). Optimizing nature-based solutions by combining social equity, hydro-environmental efficiency, and economic costs through a novel Gini coefficient. Earth and Space Science Open Archive preprint. DOI: 10.1002/essoar.10508767.1.

AWS docs  AWS Documentation: https://docs.aws.amazon.com/ ; Amazon S3: https://docs.aws.amazon.com/s3/ ; Amazon Bedrock: https://docs.aws.amazon.com/bedrock/ . Access and IAM/region availability must be verified by the team.

Data portals  ESA WorldCover: https://esa-worldcover.org/ ; WorldPop: https://www.worldpop.org/ ; Google Open Buildings: https://sites.research.google/open-buildings/ ; CHIRPS: https://www.chc.ucsb.edu/data/chirps .

## Appendix D. Final build-room checklist

- Original PS attached and five-module requirements checklist agreed.

- Pilot-zone boundary and data provenance reviewed; synthetic inputs labelled.

- All four intervention types represented in the common catalogue.

- Shared Pydantic schemas frozen and communicated to each member.

- First small MILP run validated against exhaustive enumeration.

- Four environmental objectives plus economic and equity considerations implemented to supported fidelity.

- Three scenario tests return new, auditable computed outputs.

- Selected/rejected project explanations match actual solver diagnostics.

- S3 and optional Bedrock tested with local fallbacks; credentials secure.

- User interface displays metrics, costs, sources, caveats and beneficiaries.

- One saved-run export/replay works and matches the visible dashboard.

- All P0 tests passed; backup demo/pitch/submission assets frozen.

## Appendix E. Codex Astra implementation handoff

Copy the original PS DOCX, this master specification, the selected research sources or evidence matrix, and the frozen data manifest into docs/. Codex can only ground itself in files actually accessible to its workspace.

| INITIAL CODEX INSTRUCTION; Implement C1V1C — Tulabhara AI against this master plan and the attached original Sustainable Development PS. First create validated schemas, unit tests and a 1-zone / 2-intervention vertical slice; then expand to 3 zones, four intervention types and the three shocks. Use a deterministic physical evaluator and PuLP MILP. Preserve immutable runs, equity, source provenance and explicit synthetic-data warnings. Implement S3 and Bedrock only behind optional adapters with working offline fallbacks. Never claim unsupported Bengaluru measurements or validated flood forecasts. Report completed tests, missing sources and blocked functionality after each milestone. |
| --- |


### First three implementation commands

```text
python -m venv .venv
pip install -r requirements.txt
pytest -q && streamlit run app.py
```

These commands are entry points, not evidence of a working build. Pin compatible dependencies; adapt activation for the host OS. Codex must report any failure or missing package rather than declaring completion.

### Required Codex checkpoint reports

- H2: schemas, assumptions and source manifest frozen; synthetic test fixture validates.

- H5: exact small-portfolio optimiser solution plus budget/land constraints verified.

- H8: every named shock recomputes physical coefficients and both old/new plans.

- H12: five PS modules integrated in one accessible app with deterministic explanation.

- H21: numerical acceptance fixtures, scientific caveats and offline fallback pass.

Final deliverables: a working repository, reproducible install commands, test output, frozen input files, model limitations, deployment/backup instructions, sample immutable run JSON and a three-minute judge demonstration. The team should update this plan with actual deployment details, not silently claim unverified readiness.
