# C1V1C — Standalone data folder: hardcoded defaults and remaining blockers

This pack is intentionally **not** a fabricated dataset. It supplies source-grounded *structure* and explicitly illustrative planning defaults.

## Immediately usable as configuration

- Four intervention **types** from the original problem statement.
- Five named priority modes from project development instructions; their actual numerical weights are **not** available here.
- Scenario definitions: Normal, extreme rainfall, drought and budget cut, with planning factors from prior project prompts. Verify against the authoritative master plan before production.
- INR crore display-to-INR conversion (`1 crore = 10,000,000 INR`).
- Default INR 2 crore planning budget, which is **not** a measured Bengaluru budget.

## Must not be treated as real quantified model inputs

- **Unit cost, O&M costs, capacity, lifespan, intervention efficacy, and carbon effects**: not supported by confirmed numerical tables in the available master-plan excerpts or Drive source files. Fields are deliberately blank, rather than invented.
- **Pilot zones**: three ID placeholders only; no invented coordinates or population. Generate from the actual 369-ward GIS source, validate population and document the selection.
- **Processed rainfall**: 51,136 entries were previously all dated 1971-01-01; quarantine until time axis is recovered from original IMD gridded source.
- **Urban heat dataset**: inspected first data points are near 11°N, 76.9°E, outside Bengaluru. Must spatially validate and prohibit joining non-local records to pilot zones.
- **Flood points**: hazard/exposure points, not proven intervention-construction sites.
- **Building footprints**: polygons do not prove structural eligibility for green roofs or construction rights.
- **Drainage**: network lines/maps alone do not provide hydraulic capacity or safe improvement effectiveness.

## Mode behavior

1. Production mode: block a numeric intervention if one of required physical capacity, eligibility, cost or calibrated effectiveness parameters is absent. Display a precise `NOT_ESTIMABLE_FROM_CURRENT_EVIDENCE` status, not zero or success.
2. Development mode: mathematical unit tests can use deliberately synthetic fixtures under `tests/fixtures/`, visually labeled SYNTHETIC_TEST, never mixed with Bengaluru results.
3. Demonstration mode: user-controlled illustrative assumptions may be entered explicitly with units, lower/upper ranges and assumed-source labels. Never show results as measured outcomes or validated recommendations.

## Data maintenance

The file `existing_data_inventory.csv` is an **observed folder inventory summary**, not a substitute for loading and verifying the source files. Re-run the authoritative master-plan review after mounting the repository. Correct stale provenance rows before modelling.
