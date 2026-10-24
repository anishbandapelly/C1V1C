# C1V1C — Tulabhara AI | Seed Inputs + Claude Code Implementation Handoff

**What this ZIP is:** A small, transparent set of **provisional planning/configuration inputs** and a **complete handoff prompt** for finishing backend, dataset processing, integration, testing, and deployment. It is **not** the Bengaluru dataset collection, a replacement for real measurements, or a production-ready calibrated model.

**Prepared:** 24 October 2026  
**Existing repository:** https://github.com/anishbandapelly/C1V1C  
**Standalone dataset folder:** https://drive.google.com/drive/folders/1couEReZl1kt9KqVtcH09a5O2JUz4BbE6?usp=sharing

## 1. Exactly what to give Claude Code

1. **The existing GitHub repository**, cloned into Claude Code's working directory. Confirm that it contains the **latest approved frontend** and `AGENTS.md`, original problem statement, master development plan, `anti-slop-design.md`, and the actual approved design assets. If the frontend or any key document is newer on your computer, give Claude Code that newer version too. Do not overwrite newer work with an old clone.
2. **The entire standalone Drive dataset folder** (downloaded or mounted *as real files* and accessible in Claude Code's execution environment), with its nested `raw/`, `curated/`, reference archives, large files and provenance. A Drive URL by itself is not guaranteed to make the file bytes accessible to Claude Code.
3. **This ZIP**, extracted alongside the repo or in `config/provisional_seed/` in it. It supplies fallback defaults and the instructions below. Do not overwrite existing raw source files or blindly replace repo configuration. This pack is **supplemental**; prefer any newer, verified master-plan configuration already present in the repo.
4. **AWS credentials only through a secure login or environment/role connection**, never in the Claude Code chat, the ZIP, Git, README, logs, or `.env` committed to Git. Rotate any previously exposed AWS access keys before use. Require approval for chargeable deployment/provisioning.

### Example local layout

```text
workspace/
├── C1V1C/                         # existing cloned repository (approved frontend + project docs)
│   └── config/provisional_seed/   # optionally copy extracted seed files here
└── C1V1C-Datasets/                # complete downloaded standalone Drive folder, not a partial CSV export
    ├── raw/
    └── curated/
```

In your application configuration, provide the **actual absolute or relative location** of `C1V1C-Datasets` to Claude Code. Do not assume it can read Google Drive merely from the shared link.

## 2. Contents of this ZIP

| File | Purpose / trust level |
|---|---|
| `planning_defaults.json` | Default budget, three-zone requirement, scenario multipliers, solver family, and safety restrictions; **verify against master plan** |
| `scenarios.csv` | **Illustrative** normal, rain, drought, and budget-cut input presets, not forecasts |
| `intervention_catalog.csv` | Four required intervention definitions; numerical prices, physical capacities and measured effects deliberately left blank |
| `model_parameters.csv` | Source/status-labelled configuration constants |
| `zones_selection_template.csv` | Three unassigned zone slots; **not genuine zone geometry or population** |
| `existing_data_inventory.csv` | Summary of previously observed sources, **not evidence that every catalogued file is present** |
| `DATA_READINESS.md` | Known failures, limitations and rules for safe use |
| `CLAUDE_CODE_HANDOFF.md` | Short form of the handoff instructions |
| `README.md` | **This file, including the full Claude Code implementation prompt** |

**Don't merge this seed-pack `intervention_catalog.csv` by blindly replacing the standalone Drive's `curated/interventions.csv`.** The latter is a policy-recommendation extract, not a quantified cost/effect model.

## 3. Copy-and-paste prompt for Claude Code (Phases 4–6)

> **Give Claude Code access to the actual repo, complete dataset directory and this extracted pack before sending this prompt.**

---

# CLAUDE CODE TASK — FINISH C1V1C / TULABHARA AI

Continue the existing project at **https://github.com/anishbandapelly/C1V1C**. The frontend design and interaction work (Phases 1–3) is already approved. **Your responsibility is Phases 4–6: real data processing, environmental modelling, genuine optimisation, backend services, AWS integration, end-to-end testing, and deployment.** Do not regenerate or redesign the approved frontend.

## A. Read the authoritative materials first

Inspect the actual repo and read `AGENTS.md`, the original Sustainable Development problem statement, complete master development plan, `anti-slop-design.md`, `DESIGN.md`, the current frontend/API contracts, existing tests and deployment configuration. **The source documents define mandatory functionality; the approved frontend defines the user experience.** Before making edits, make a concrete inventory of what is implemented, what is hardcoded, and what is missing. If documents or frontend files are absent or outdated, report the exact missing path and use the copies provided by the user instead of guessing.

**Also recursively inventory the complete local dataset folder** supplied alongside this ZIP. Compare actual present bytes against `existing_data_inventory.csv` and `provenance.csv`. Treat entries in a manifest as *catalogue claims*, not as uploaded data. Reconcile this seed pack's hardcoded values with the **actual** master plan and working frontend; record conflicts, don't silently choose one.

## B. Data ingestion and validation (Phase 4)

Build a reproducible, source-preserving geospatial and temporal data pipeline that can process the actually present GBA 369-ward KML, land-use and soil archives, Microsoft-derived building-footprint GeoJSONL, available IMD rain sources, long-run station weather CSV, SRTM elevation tiles, stormwater KML/PDF reference material, water supply and groundwater documents, flood-location KMLs, and other inspectable records.

**Known errors and limitations to address explicitly:**

- The current curated rainfall CSV has **51,136 rows whose dates are all `1971-01-01`**. Rebuild time from verified source metadata or quarantine the file; **never invent sequential dates**.
- The GBA KML population totals conflict with male/female subtotals in numerous wards. Preserve source values, validate the applicable census/reference year, and flag discrepancies; do not silently correct by assumption.
- Flood/low-lying points include invalid/duplicated coordinates and are **hazard markers, not eligible intervention construction sites**. Clean and geospatially validate them.
- Historical 2017 land use must not be presented as verified current use.
- The first inspected records of the uploaded urban-heat CSV were outside Bengaluru. Validate its entire geographic coverage and exclude observations outside actual pilot polygons.
- Microsoft building-footprint polygons are useful potential footprint estimates, **not proof of usable rooftop area, structural capacity, ownership, access or permission**.
- Drainage geometry is not measured hydraulic capacity; source water-demand tables are not automatically validated current ward-level demand.
- Raw sources must retain provenance, observation date, units, CRS, licence, resolution, missing-data flags and any spatial/temporal uncertainty.

Establish **three real, geographically coherent Bengaluru pilot zones**, derived from actual validated boundary geometries, with traceable ward IDs and population references. Generate checked `zones.geojson`, `zones.csv`, zone-level environmental inputs, usable site features and a versioned provenance registry. Do not turn the empty `zones_selection_template.csv` into fabricated polygons or demographic numbers.

Implement deterministic environmental models with documented equations and units for runoff, rainwater harvesting, heat/cooling, carbon, lifecycle costs, site constraints and population-weighted equity, with uncertainty where supported. **If the available inputs cannot support a numeric result, report `NOT_ESTIMABLE_FROM_CURRENT_EVIDENCE` instead of presenting invented Bengaluru measurements.** Clearly separate observed data, derived data, literature estimates, user-entered assumptions, and synthetic test fixtures.

## C. Mathematical optimisation and scenarios (Phase 4)

Implement a real **PuLP/CBC MILP** covering all four mandatory intervention types: green roofs, urban forests, rainwater harvesting, and drainage improvements. Follow the master plan for objectives and constraints: capex budget, land/roof availability, intervention eligibility/capacity, material dependencies, environmental outcomes, lifecycle costs, equity and user priority modes (Balanced, Flood-first, Water-first, Heat-first, Equity-first). Use declared, appropriately normalised weights, not invented weights or arbitrary rankings.

Produce solver status, feasible portfolio quantities, costs, available budget, baseline-vs-solution impacts, binding constraints, meaningful alternative portfolios, zone-wise impacts, declared uncertainty, provenance and explanations for infeasibility. Independently verify the hard constraints after solve. **No silent mock solver outputs in production paths.** Synthetic solver fixtures are acceptable only for tests and clearly-labelled demo mode.

Implement four scenarios: normal, drought, extreme rainfall and sudden budget cut. The attached seed presets currently use **1.30 extreme-rain rainfall, 0.60 drought rainfall, 0.70 drought tree-cooling and 0.70 budget-cut capital**, with an illustrative default capital budget of **₹2 crore** (₹20,000,000). **Recheck every value against the authoritative master plan. These are not observed hazard forecasts or real city budget estimates.** Distinguish: (1) original portfolio in normal conditions, (2) unchanged original portfolio under the shock, and (3) a newly reoptimised portfolio under the same shock. Never call (2) a new optimisation.

## D. Complete the backend and connect the approved frontend (Phases 4–5)

Preserve the existing frontend design system, hero, sidebar, theme states and page hierarchy. Connect its actual controls through validated typed APIs and persistent run records:

1. **City Intelligence:** true pilot geography and environmental layers, source dates and missing-data indicators.
2. **Investment Optimiser:** correct INR/crore decimal conversions, intervention selection, priority weights, solver run/feasibility, per-zone results, alternative plans and costs.
3. **Climate Shock Lab:** genuine selected-shock evaluation and reoptimisation with baseline comparison.
4. **Decision Intelligence:** computed trade-offs, who benefits, rejected alternatives, uncertainty and unintended consequences, saved runs and a readable “Sources & assumptions” disclosure.

Replace frontend demonstration data **only when** genuine backend responses are working. Where evidence is missing, display a meaningful blocked/estimated/not-available state rather than pretending a real optimisation was completed.

## E. AWS integration (Phase 5)

Use authorised AWS credentials through the provider chain / secure role, **Region `ap-south-2` (Hyderabad)** and the actual configured S3 bucket when accessible. Prioritise meaningful integrations: **S3** for versioned data/run artefacts, **Bedrock** for strictly grounded narrative explanations of deterministic results, and appropriate **Lambda / Batch / other compute** based on workload suitability. Check the status of account verification, model identifier, inference profile, IAM and Region before claiming any Bedrock call works. Implement local deterministic explanatory fallback when Bedrock cannot be called. Document any original-problem-statement AWS services not genuinely integrated and justify substitutions or blockers. Do not spend money provisioning services without explicit approval.

Never hardcode or print access keys, publish private source data without checking licence, or commit `.env`/AWS credentials.

## F. Verification and deployment (Phase 6)

Implement and **run** meaningful unit, scientific, data-quality, solver, API contract, integration and browser/end-to-end tests. Test corrupt input data, invalid dates/coordinates, insufficient budget, infeasible constraints, priority changes, all shock scenarios, AWS auth and Bedrock failures, and saved-run reproducibility. Test a complete flow from choosing a real zone to comparing a solver-produced portfolio and shock run with a grounded explanation. Verify light/dark and responsive layouts are preserved.

Prepare a reproducible local start and authorised deployment, including environment setup, health checks, API connectivity, solver execution, S3 and Bedrock checks where enabled, and post-deployment smoke tests. **Do not report deployment as successful unless it actually ran and was verified.** Do not silently proceed with chargeable cloud changes.

Deliver the functioning integrated system in the **same GitHub repository**, tests and actual test output, versioned curated files, data dictionary, modelling-methods/provenance docs, real deployment instructions, a PASS / PARTIAL / FAIL / BLOCKED requirement matrix linked to the original specification, and clear unresolved blockers. Make reviewable Git commits.

**Start Phase 4 now and continue through Phases 5 and 6. Do not stop at investigation, scaffolding or placeholder APIs. Preserve the approved frontend and scientific truthfulness. Only request human action for genuine access, cost-approval, missing-source or deployment blockers.**

---

## 4. Data-use rules / red flags

- **Project configuration and mathematical unit definitions may be seeded. Actual measured Bengaluru environment metrics may not be invented.**
- **Synthetic mathematical solver fixtures must not masquerade as validated real-city recommendations.**
- `zones_selection_template.csv` and `scenarios.csv` are *definitions/templates*, not measured inputs or finished outputs.
- The **standalone** dataset Drive is expected to be separately supplied in full. This seed ZIP is an optional supplemental input, not a dataset replacement.
- Revalidate the seed configuration against newer code and the complete master plan instead of overriding it automatically.
- Preserve current frontend work, and report actual tests/deployments only when executed.

## 5. Quick start for the human operator

1. Give Claude Code access to the latest GitHub repo and entire standalone dataset folder.
2. Extract this ZIP under `config/provisional_seed/` or alongside the repo.
3. Ask Claude Code to **read `README.md` in full, then implement the Phase 4–6 instructions in section 3**.
4. Keep AWS authorisation in the runtime environment only and review cloud-cost approval requests separately.
