# Requirements-to-implementation traceability

**Baseline status:** This repository is only a handoff scaffold. All executable application requirements are `NOT IMPLEMENTED` until verified by running actual code. The official PS controls scope; Master Plan v2.0 supplies detailed acceptance criteria.

| ID | Source | Required behaviour | Planned implementation | Verification / acceptance | Baseline state |
| --- | --- | --- | --- | --- | --- |
| PS-01 | PS MVP | Climate, water, land-use and population data | Pydantic data engine, sourced zone/site indicators, provenance + flags | Reject missing essential input/units; show source & missingness | NOT IMPLEMENTED |
| PS-02 | PS MVP | Four interventions considered in combination | Site eligibility, interaction-aware coefficients, MILP | Consider green roofs, urban forests, rainwater harvesting, drainage improvements; hard constraints | NOT IMPLEMENTED |
| PS-03 | PS MVP | Interactive map/results | Four-tab Streamlit, zone costs, allocations, risks and beneficiaries | Real UI controls change actual solver run; visible data mode | NOT IMPLEMENTED |
| PS-04 | PS MVP | Drought, rainfall and budget cuts | Original portfolio under shock + distinct reoptimised portfolio | Three scenario recomputation tests; immutable run comparison | NOT IMPLEMENTED |
| PS-05 | PS MVP | Explain recommendations and negative impacts | Deterministic source-grounded explanation; Bedrock optional | Numbers match saved RunResult; uncertainty and unintended effects shown | NOT IMPLEMENTED |
| CORE-01 | PS problem | Multi-objective environmental/economic/equity outcomes | Physical benefits, LCC, equity weights/floor | Show separate raw metrics, normalisation and trade-offs | NOT IMPLEMENTED |
| CORE-02 | PS problem | Heat/flood/water/carbon challenges | Bounded flood, tank balance, heat index, carbon accounting | Conservation, time horizon and unsupported-effect tests | NOT IMPLEMENTED |
| CORE-03 | Master §5 | Feasible allocation | MILP with budget/land/roof/site/prerequisites/exclusions | Verify tiny optimum, infeasibility, slack and solver status | NOT IMPLEMENTED |
| CORE-04 | Master §5.8 | No unsupported optimality claim | Surrogate solver + independent portfolio re-evaluation | Record both scores; flag material re-evaluation differences | NOT IMPLEMENTED |
| CORE-05 | Master §6 | Committed investment treatment | Freeze previous projects when evaluating post-commitment cut | Cannot delete obligated spend; infeasible reason displayed | NOT IMPLEMENTED |
| CORE-06 | Master §8 | Reproducible runs | Saved immutable RunResult JSON, input hash, version and evidence | Replay same input; new scenario -> new run_id | NOT IMPLEMENTED |
| CORE-07 | Master §13 | End-to-end offline fallback | Local data + deterministic explainer; S3/Bedrock optional | Disable cloud; pass complete five-module demo | NOT IMPLEMENTED |
| CORE-08 | Master §13 | Equity and evidence honesty | Beneficiaries per zone, residual risk, quality/uncertainty | Synthetic visibly synthetic; missing not silently zero | NOT IMPLEMENTED |
| EXT-01 | Master P1 | Same-budget conventional baseline | Equal-feasible vs optimised vs no investment | Fair same constraints/horizon; real trade-offs | NOT IMPLEMENTED |
| EXT-02 | Master P1 | Sourceable AWS features | boto3 S3 versioned input/saved run, optional Bedrock | AWS connection evidence and reliable local fallback | NOT IMPLEMENTED |
| DESIGN-01 | User | Use actual Anti-Slop design rulebook | `anti-slop-design.md` (mirror: `docs/ANTI_AI_SLOP.md`) | Original file included; check exact bytes against mirror | SUPPLIED — not yet applied to UI |
| DESIGN-02 | User §1–3, §7 | Direction and tokens before pages | Codex creates `DESIGN.md` and `style-guide.html` | Direction statement/archetype/assumptions, semantic tokens, light+dark states, usable components before UI | NOT IMPLEMENTED |
| DESIGN-03 | User §4, §6, §9 | No unreasoned banned defaults; accessible, audited UI | Codex documents justified exceptions and 30-point §9 audit | Overall score ≥85, no category <60, record fixes and check mobile/focus/reduced-motion | NOT IMPLEMENTED |

Update statuses with direct test commands or screenshots and Git commit IDs. Do not bulk-mark complete. Minimum functional P0 requirements are PS-01..05 plus CORE-01..08.
