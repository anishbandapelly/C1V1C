# Claude Code handoff: integrate C1V1C seed configuration

The approved frontend and entire repository are authoritative for style and API contracts. The original problem statement and the master development plan are authoritative for functionality.

1. Read `AGENTS.md`, the master plan, the original problem statement and the existing code. Reconcile all numeric assumptions in this seed pack against the original master plan. Log any discrepancy instead of silently changing it.
2. Use `planning_defaults.json`, `scenarios.csv`, `intervention_catalog.csv` and `model_parameters.csv` as a **transparent versioned fallback configuration**. Do not overwrite validated real data with these presets.
3. Keep and process original GBA 369-ward KML, footprints, SRTM, stormwater, IMD, soil, water supply and heat datasets. Resolve provenance, coverage, units, dates and geospatial identifiers. In particular, **fix the curated IMD rainfall date bug** and reject non-Bengaluru UHI rows.
4. Derive the 3 pilot-zone polygons from real GIS, not `zones_selection_template.csv` IDs. Populate zone statistics with validated aggregation; do not manufacture ward population, area or environmental values.
5. Implement all four intervention types in PuLP/CBC, but treat real-life portfolios as NOT_ESTIMABLE if required cost/capacity/effect data remains missing. A synthetic solver test is not real-world validation.
6. Scenario engine must distinguish: original normal portfolio, original portfolio evaluated under a shock, and freshly reoptimised under the same shock. Present budget-cut infeasibility honestly.
7. Keep the approved frontend unchanged except for minimal API integration/bug fixes. Expose observed/modelled/assumed/missing labels, uncertainties and provenance. Bedrock may narrate verified outputs but cannot invent metrics.
8. Produce real unit/integration tests and a requirements pass/partial/blocked matrix. Report any missing AWS permissions or model access truthfully.
9. Never commit credentials or dotenv secrets. Ask permission before chargeable cloud provisioning. Avoid uploading bulk source datasets to the public repository without licensing review.

**Critical:** This pack does **not** claim complete calibrated Bengaluru inputs. It hardcodes only project requirements, scenario assumptions and placeholders with honest validation states.
