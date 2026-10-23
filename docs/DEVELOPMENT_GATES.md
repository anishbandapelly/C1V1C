# 24-hour delivery gates — evidence required, not promises

All work follows the **original PS** and `docs/MASTER_PLAN.md`. H0 means hackathon build start, not the time this repository was created. Do not claim gates pass merely because files exist.

| Time | Gate | Evidence necessary for PASS |
| --- | --- | --- |
| H0–H2 | Inputs and contracts | Pydantic schemas, source/assumption labels, known unit conventions, synthetic fixture loaded, baseline version frozen; design direction/archetype/assumptions recorded in `DESIGN.md` before UI work |
| H2–H5 | Real optimiser | MILP over real decision variables, constraints and verified tiny-instance optimum; visible solver status |
| H5–H8 | Three shocks | Named rainfall, drought and budget shocks recompute physical inputs, evaluate the **unchanged original** plan and separately reoptimise |
| H8–H12 | Complete PS vertical slice | Five modules function end to end, all four interventions considered, four-tab UI and deterministic explanation; `style-guide.html` and tokens precede UI pages, §9 score recorded before showing UI |
| H12–H18 | Impact/strengthening | Same-budget counterfactual, minimum cost/carbon/equity, lifecycle, sensitivity, meaningful S3/Bedrock where accessible |
| H18–H21 | Scientific and system QA | P0 tests, data gaps, solver failures, immutable saved runs, offline demo, evidence integrity, no false local claims |
| H21–H24 | Demo and submission | Freeze; stable demo; screenshots/video backup; traceable limitation statement; submission URL verified |

## P0/P1 ownership
P0: official modules and interventions, constraints, transparent environmental/accounting calculations, equity, three shocks, reproducible runs, deterministic explainer, tests. P1: richer LCC/carbon evidence (the minimum credible accounting remains P0), uncertainty comparisons, AWS services, printable report, advanced maps. P2: CKAN/EKS, full digital twins, machine-trained prediction, multi-agent RAG — **do not implement** without explicit decision.

## Status vocabulary
`NOT STARTED` / `IN PROGRESS` / `PASS` / `PASS WITH DISCLOSED LIMITATION` / `BLOCKED`. A missing source must not become a made-up fact. `PASS WITH DISCLOSED LIMITATION` is permitted only for scientifically bounded screening models; a non-functioning required module is `BLOCKED`.
