# START HERE — Codex / GPT-6 Astra handoff

You are implementing **C1V1C — Tulabhara AI**, a 24-hour hackathon solution. This ZIP is a **planning scaffold, not the application**.

## Source-of-truth order
1. `docs/Original_Sustainable_Development_PS.docx` — mandatory five modules, four interventions and three shocks.
2. `docs/C1V1C_Master_Plan.docx` / `docs/MASTER_PLAN.md` — final technical spec; DOCX wins conversion disputes.
3. `AGENTS.md` — repo engineering protocol and scientific safety.
4. `anti-slop-design.md` — the exact user-supplied design rulebook (mirrored at `docs/ANTI_AI_SLOP.md`). Read it **before any UI**; create `DESIGN.md` and `style-guide.html` before application pages, then perform the §9 audit.
5. `docs/research_evidence.md` and `docs/reference/` — rationale/references only; do not substitute their toy architecture for the master.

## First operations
1. Run `python scripts/preflight.py` and `python -m pytest -q`. These verify only scaffold/fixtures.
2. Read `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/DEVELOPMENT_GATES.md`, `docs/INPUT_DATA_AND_PROVENANCE.md`, `docs/AWS_ACCESS_AND_FALLBACK.md`, and `docs/DECISIONS_AND_GAPS.md`.
3. Freeze Pydantic schemas + immutable run contract. Agree physical units, sources and scenario semantics first.
4. Build/test one-zone/two-intervention vertical slice, then grow to all four interventions and three zones, then all three shocks.
5. Implement physical models, real MILP, independent portfolio re-evaluation, before/after scenarios, reproducible results, deterministic explanation and four-tab UI.
6. Populate `docs/IMPLEMENTATION_STATUS.md` and traceability rows with test evidence. No test evidence = not complete.
7. Add useful S3, then optional Bedrock, only after offline five-module path works. Do not invent actual AWS connectivity.

## Rules on supplied inputs
- `data/synthetic_test/` contains numerical *synthetic fixtures* transcribed from the plan; no local empirical claim may be made from them.
- `data/templates/` is blank schemas, `data/source_registry.csv` is an **unverified source lead list**, and `data/raw` and `data/curated` contain no verified city data yet.
- The actual Anti-Slop guide **is present** at repository root. Compliance still requires implementing its design workflow and passing the documented §9 audit.
- Do not treat a fabricated coefficient, synthetic zone, or successful unit test as a validated environmental prediction or a deployed application.

## Outputs expected from implementation
A tested Python/Streamlit application, validated input contracts, reproducible fixture-based demo, bounded flood/water/heat/carbon models, site-aware MILP, scenarios + equity, immutable RunResult, deterministic explanation, fallback, an implementer-written dependency lock, deployment commands, documented limitations, and a three-minute judge demo.
