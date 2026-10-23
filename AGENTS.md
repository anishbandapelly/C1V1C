# AGENTS.md — C1V1C / Tulabhara AI

This repository is the **development handoff**, not a completed application. Do not claim modules are implemented until actual code and tests prove it.

## Source-of-truth hierarchy
1. `docs/Original_Sustainable_Development_PS.docx`: non-negotiable official scope and five MVP modules.
2. `docs/C1V1C_Master_Plan.docx` and `docs/MASTER_PLAN.md`: detailed model, architecture, fixtures, development gates, test criteria, and research boundaries. In case of a conversion discrepancy, prefer the DOCX.
3. `anti-slop-design.md`: the **actual, user-supplied design rulebook**, preserved verbatim at repository root (with an exact mirror at `docs/ANTI_AI_SLOP.md`). This guide governs UI work; don't substitute generic design conventions.
4. `docs/research_evidence.md`: traceable research rationale, not locally validated numerical coefficients.

## Hard requirements
- Implement the original PS's five modules: Data Engine, AI Optimisation, Interactive Dashboard, Scenario Simulator, Decision Explainer.
- Evaluate all four interventions: green roofs, urban forests, rainwater harvesting, drainage improvements.
- Support three disruptions: extreme rainfall, drought, sudden budget cuts. Compare original-plan under shock and re-optimised alternative.
- Use source-labelled/assumption-labelled environmental inputs. Synthetic fixtures are never measured Bengaluru data.
- Real constrained MILP/verified numerical calculations must determine allocations; LLMs only explain saved outputs.
- Respect budget, physical suitability, roof/land sharing, storage timing, commitments, equity, and feasibility. Never silently relax constraints.
- Keep source, date, unit, geography, evidence grade, scenario/run ID, data/catalog/model version, and missing-data flags with results.
- Prevent double-counting intervention benefits. Keep generated runoff distinct from drainage conveyance/storage changes.
- Annual harvested water can exceed tank capacity due to turnover; **instantaneous stored water must never exceed capacity**.
- Present heat and carbon as appropriately bounded modelling outputs; do not imply validated city-wide forecasts.
- S3 is valuable for reproducible datasets/runs; Bedrock is optional for evidence-grounded explanation. Use reliable local fallbacks.
- No AWS keys, personally sensitive records, fabricated external statistics, placeholder feature success states, or fake controls in commits.

## Non-negotiable UI design gate
- Read **all of** `anti-slop-design.md` before writing any UI code or modifying UI components.
- Follow §§1–3 and §7 in order: choose a design direction and dashboard archetype; record assumptions, brand inspiration, and deliberate deviations in `DESIGN.md`; define semantic tokens and component states; produce `style-guide.html` in light and dark; only then build application pages. Streamlit CSS, if used, must also follow the chosen tokens.
- Treat the exact uploaded guide as source-of-truth. Avoid all §4 banned defaults unless `DESIGN.md` records a one-sentence justification for each exception.
- Before **showing or shipping any UI**, run the guide's §9 six-category slop check (30 items), record the pass/fail scores and fixes, and achieve overall ≥85/100 with every category ≥60/100. Document the report; a claimed score without evidence does not count.
- Apply §6 accessibility: contrast, focus, semantic controls, reduced motion, touch targets, and mobile width.
- User has provided the real guide; **design rules are no longer blocked due to file absence**. Actual UI design, style guide and audit remain to be done by the implementation agent.

## Supporting executable handoff artefacts
- `docs/REQUIREMENTS_TRACEABILITY.md`: official five-module mapping and P0 verification gates.
- `docs/INPUT_DATA_AND_PROVENANCE.md` and `data/source_registry.csv`: source leads, quality labels and input schema constraints; leads are NOT verified downloaded datasets.
- `docs/AWS_ACCESS_AND_FALLBACK.md` and `.env.example`: exactly match Master §9.5 variable names; no account access is presumed.
- `docs/DEVELOPMENT_GATES.md`: milestone checkpoints with evidence required.
- `scripts/preflight.py`: scaffold audit only; **not** application certification.
- `docs/reference/`: supplemental reference PDF, lower-priority than PS/master; do not deploy CKAN/EKS on its recommendation.

## Build order and verification
1. Inspect original PS, master plan and fixture provenance; list unresolved inputs and assumptions.
2. Freeze typed schemas for zones, sites, interventions, scenarios, physical effects and immutable run results.
3. Implement/test flood, storage, heat and carbon model rules and site suitability.
4. Implement/test MILP, fair alternatives, equity guardrail and infeasibility reporting.
5. Implement/test all shocks, committed-project behavior, sensitivity and saved-run replay.
6. Build four-tab dashboard from the same stored run result and deterministic explanation first.
7. Integrate AWS only after end-to-end flow works; deploy and test fallbacks.
8. Verify every P0 item in master plan; show actual test output and known limitations.

`data/synthetic_test/` contains **illustrative fixtures transcribed from the master DOCX**. `tests/test_reference_fixtures.py` checks only those fixtures and does not establish application correctness. Add comprehensive module and integration tests during development.

If an important source input or AWS permission is unavailable, record the blocker and use the specified transparent fallback; never silently manufacture field observations.

## AWS owner configuration / secret handling

- `AWS_REGION=ap-south-2` and the configured S3 bucket are in `.env.example`; see `docs/AWS_HYDERABAD_SETUP.md`.
- An AWS key pair was exposed in conversation. **Never reuse, reproduce, upload or commit it.** Request confirmation that it has been revoked/rotated before performing any live cloud actions. Do not print credentials during diagnostics.
- `.env`, nested `.env.*` files and local AWS credentials are excluded by `.gitignore` (except the non-secret `.env.example`). Never turn the repository's examples into real credential files in commits or ZIPs.
- Codex may implement S3 connectivity using the standard boto3 credential-provider chain; prefer temporary roles/SSO. Cloud Codex must have separately configured permissions and must not infer them from a browser login.
- Do not invent a Bedrock model ID, claim model access, or disable the deterministic fallback until a live authorized invocation succeeds.
