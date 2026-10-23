# Synthetic reference fixtures — NOT measured Bengaluru data

The zones, intervention unit configurations, stress factors, and tiny optimisation test below are taken from **Tables 7, 9, 12 and 22** of `docs/C1V1C_Master_Plan.docx`. Their purpose is to catch implementation/contract errors and give Codex a deterministic starting point.

- `zone_fixture.csv`: labels A/B/C are illustrative risk profiles, not real neighbourhood names, boundaries or actual census counts.
- `intervention_unit_fixture.csv`: illustrative unit costs and capacities are **not** verified local price/benefit estimates.
- `scenario_fixture.csv`: example multipliers are user-defined stress tests **not climate predictions**.
- `optimization_fixture.csv`: toy A/B/C project data to verify a solver/enum result.
- `fixture_manifest.json`: lineage and units.

Do not show these figures in a public demo as real measurements; if used, label prominently `ILLUSTRATIVE DATA` and show missing evidence. The final environmental coefficient matrix and real geospatial boundaries have not been provided.
