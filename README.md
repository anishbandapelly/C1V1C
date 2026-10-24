# C1V1C — Tulabhara AI

**Balancing the Future of Cities.** A research-grounded urban sustainability decision engine. It helps planners choose feasible combinations of **green roofs, urban forests, rainwater harvesting and drainage improvements**. It balances environmental impact, cost and social equity under scarce land, limited budgets and climate shocks, and explains every trade-off.

> **Status:** working system, Bengaluru pilot.
>
> - **141 tests** pass and **43/43** scientific checks pass.
> - The Docker deployment passes **15/15** post-deploy smoke checks.
> - **Amazon S3 is live:** every run is mirrored, encrypted and versioned.
> - **Amazon Bedrock is ready but blocked** by an AWS account-level restriction. Explanations fall back to the deterministic explainer, labelled as such.
>
> Full requirement-by-requirement status: [docs/COMPLIANCE_MATRIX.md](docs/COMPLIANCE_MATRIX.md).

## What it does

| Module (official brief) | What you get | Where |
|---|---|---|
| **Data Engine** | Real Bengaluru data for 3 pilot wards: GBA 369-ward boundaries and population, Microsoft building footprints, validated flood/low-lying markers, storm-water drains, tanks and ponds, and IMD rainfall/temperature grids. Every value carries its unit, source and evidence class. | City Intelligence · `src/c1v1c/pipeline.py` |
| **AI Optimisation** | A PuLP/CBC mixed-integer optimiser over all four interventions. Hard constraints: budget, shared roof, land, eligibility, commitments and an equity floor. It reports solver status, binding constraints, rejected projects and evaluated alternatives, and never fabricates a plan when the problem is infeasible. | Investment Optimiser · `src/c1v1c/optimiser.py` |
| **Interactive Dashboard** | A four-page Streamlit workspace with a real ward map, risk indicators, allocations and benefits per ward, in light and dark themes. | `app.py`, `ui/` |
| **Scenario Simulator** | Extreme rainfall, drought and budget cut. Each compares **A** (the plan under normal conditions), **B** (the same frozen plan under the shock) and **C** (a fresh re-optimisation), with sensitivity ranges. | Climate Shock Lab · `engine.shock` |
| **Decision Explainer** | Why this plan, why not the others, who benefits, what got worse, uncertainty and unintended consequences, all computed from the stored run. Bedrock narration is accepted only if every number in it matches. | Decision Intelligence · `explainer.py` |

**Pilot wards** (GBA Yelahanka zone, chosen by a data-driven rule):

- **ZA** Brundavana Nagara: most flood markers
- **ZB** Dinnur: most built-up
- **ZC** R.T Nagar: no surface water storage

**Evidence labels:** Observed · Derived · Estimated · Assumed · Missing. This is a **mixed-evidence pilot**. Ward geography, population, footprints, hazards and climate are real. Intervention costs and effects are declared master-plan assumptions, so results are **modelled screening estimates, not engineering forecasts**.

## Quick start

```bash
python -m venv .venv
# activate .venv for your shell, then:
pip install -r requirements-dev.txt
python -I scripts/data/fetch_drive_dataset.py   # downloads the 165 Bengaluru files the pilot needs
python -m c1v1c.pipeline                        # builds data/curated/bengaluru_pilot_v1 (~25 s)
streamlit run app.py                            # http://localhost:8501
```

Optional HTTP API: `uvicorn c1v1c.api:app --port 8000`. It provides `/health`, `/zones`, `/runs`, `/runs/{id}/shocks`, `/runs/{id}/explanation` and `/aws/status`.

**Docker (offline):**
```bash
docker compose up -d --build && python scripts/smoke_test.py
```

**Docker (online, with S3 and Bedrock when enabled):**
```bash
powershell -ExecutionPolicy Bypass -File scripts/aws_configure.ps1    # once; you type a rotated key, stored only in ~/.aws
docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d --build
python scripts/smoke_test.py
```

**Tests and checks:**
```bash
pytest -q                            # 141 tests
python scripts/validate_science.py   # 43 independent scientific checks
python -m c1v1c.aws.status           # live AWS probe (PASS/BLOCKED per service; no secrets printed)
```

## Documentation

| Topic | Document |
|---|---|
| Requirement status (PASS / PARTIAL / BLOCKED) | [docs/COMPLIANCE_MATRIX.md](docs/COMPLIANCE_MATRIX.md) |
| Implementation status by module | [docs/IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md) |
| Data inventory, quality fixes, pilot zones, data dictionary | [docs/DATA_PIPELINE.md](docs/DATA_PIPELINE.md) |
| Model equations, MILP formulation, scenarios, explainer | [docs/MODELS.md](docs/MODELS.md) |
| Scientific validation results | [docs/SCIENTIFIC_VALIDATION.md](docs/SCIENTIFIC_VALIDATION.md) |
| Deployment, configuration, smoke tests | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) |
| AWS service status, IAM policy, Bedrock unblocking | [docs/AWS_SERVICES.md](docs/AWS_SERVICES.md) |
| Official brief and master plan | [docs/Original_Sustainable_Development_PS.docx](docs/Original_Sustainable_Development_PS.docx), [docs/C1V1C_Master_Plan.docx](docs/C1V1C_Master_Plan.docx) ([MD](docs/MASTER_PLAN.md)) |
| Engineering rules | [AGENTS.md](AGENTS.md) |
| Pre-build handoff notes (historical) | [docs/HANDOFF_HISTORY.md](docs/HANDOFF_HISTORY.md) |

## Repository layout

```text
app.py                  Streamlit entry point
ui/                     approved frontend (views, shell, theme, tokens) + engine adapter
src/c1v1c/              engine: pipeline, baseline, models/, evaluate, optimiser, engine, explainer, run_store, api, aws/
config/                 declared assumptions (interventions, parameters, scenarios), IAM policy, provisional seed pack
scripts/                data fetch, science validation, smoke test, AWS setup, Bedrock enablement
tests/                  unit, solver, scenario, AWS-failure, API and UI integration tests
data/synthetic_test/    master-plan fixtures (tests only; never shown as Bengaluru data)
data/raw, data/curated  downloaded and processed data — git-ignored, rebuilt by the pipeline
```

## Design process (user-supplied)

I’ve attached **anti-slop-design.md**, the design rulebook for this project. Read it fully before writing any UI. Follow its workflow: decide the direction and archetype, build the tokens and style guide first, then the pages. Avoid every banned default unless you write down a one-sentence reason, and run the §9 slop check before you show me anything.

The rulebook is [`anti-slop-design.md`](anti-slop-design.md), mirrored at [`docs/ANTI_AI_SLOP.md`](docs/ANTI_AI_SLOP.md). Design decisions are recorded in [`DESIGN.md`](DESIGN.md), with the tokenised [`style-guide.html`](style-guide.html) and the [design audit](docs/DESIGN_AUDIT.md). Any UI change must keep the §9 audit at an overall score of **≥85/100**, with **no category below 60**.

## Data integrity

- `data/raw/` and `data/curated/` are **not committed**. Source licences for the ward, hazard and IMD layers are not stated, so they are rebuilt locally by the pipeline and copied into the Docker image at build time.
- `data/synthetic_test/` holds illustrative fixtures for tests only.
- Missing values are `null` with a reason, never zero. Known source defects are fixed only where the source itself supports the fix, otherwise quarantined (see `data_quality_report.json`).

## AWS / Hyderabad environment and security

- **Region:** `ap-south-2` (Asia Pacific / Hyderabad). **S3 bucket:** `amzn-c1v1-bucket-515820372090-ap-south-2-an`.
- **Credentials** come only from the AWS default provider chain: the `c1v1c` profile in `~/.aws`, a role, or a host secret store. They are never stored in the repository, `.env`, images or logs. `.env` holds non-secret settings only and is git-ignored.
- **S3:** live. Runs and comparisons are mirrored to `runs/runs/` and `runs/comparisons/` (SSE-S3, versioned). If S3 fails, the app keeps working locally and records the error.
- **Bedrock:** IAM is in place ([config/iam/c1v1-app-bedrock-policy.json](config/iam/c1v1-app-bedrock-policy.json)). The account itself currently gets `ValidationException: Operation not allowed` for every Claude model, even in the console playground, which only AWS Support can lift. After that, `python scripts/enable_bedrock.py` switches it on only once a live call succeeds.
- Any previously exposed access key must stay deactivated. Rotate keys with `scripts/aws_configure.ps1`; it refuses to re-save the key being replaced.

See [docs/AWS_HYDERABAD_SETUP.md](docs/AWS_HYDERABAD_SETUP.md) and [docs/AWS_SERVICES.md](docs/AWS_SERVICES.md).
