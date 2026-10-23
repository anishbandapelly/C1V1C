# Blank data templates — NOT observed Bengaluru records

These files contain **column headings only**. Populate from verified sources or explicitly document synthetic/estimated provenance. Do not copy numerical values from `data/synthetic_test/` into curated results without preserving synthetic labels. Schema contracts in `docs/MASTER_PLAN.md` are the source of truth; adapt templates only with a documented change and tests.

Astra should validate all files with Pydantic before running optimisation. Validation must reject missing required source identifiers, negative costs/area, invalid units, impossible roof overlap and unsupported intervention coefficients.
