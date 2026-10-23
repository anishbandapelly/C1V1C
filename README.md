# C1V1C — Tulabhara AI

**Balancing the Future of Cities.** A research-grounded urban sustainability decision engine for a 24-hour hackathon.

> **Repository status:** Initial *planning and fixture scaffold*. The full application and five MVP modules have **not yet been implemented**. This is prepared for development with Codex.

## Official goal
Choose feasible combinations of **green roofs, urban forests, rainwater harvesting, and drainage improvements** while balancing environmental impact, economic feasibility and social equity under scarce land, limited budgets and climate uncertainties.

### The five required modules
1. Data Engine — urban climate, water, land-use and population information.
2. AI Optimisation — feasible, multi-objective allocation of the four interventions.
3. Interactive Dashboard — environmental risks, costs, resource allocation, neighbourhood benefits.
4. Scenario Simulator — drought, extreme rainfall and budget cuts.
5. Decision Explainer — reasons, trade-offs, uncertainties and unintended consequences.

## Read before implementation
- **Official brief:** [`docs/Original_Sustainable_Development_PS.docx`](docs/Original_Sustainable_Development_PS.docx)
- **Master build specification:** [`docs/C1V1C_Master_Plan.docx`](docs/C1V1C_Master_Plan.docx) (and [`docs/MASTER_PLAN.md`](docs/MASTER_PLAN.md))
- **Agent engineering rules:** [`AGENTS.md`](AGENTS.md)
- **Canonical UI design rulebook:** [`anti-slop-design.md`](anti-slop-design.md) (exact uploaded file; mirrored at [`docs/ANTI_AI_SLOP.md`](docs/ANTI_AI_SLOP.md)).
- **Research application and cautions:** [`docs/research_evidence.md`](docs/research_evidence.md)
- **Current open inputs:** [`docs/DECISIONS_AND_GAPS.md`](docs/DECISIONS_AND_GAPS.md)

## Mandatory design process (user-supplied)

I’ve attached **anti-slop-design.md**, the design rulebook for this project. Read it fully before writing any UI. Follow its workflow: decide the direction and archetype, build the tokens and style guide first, then the pages. Avoid every banned default unless you write down a one-sentence reason, and run the §9 slop check before you show me anything.

**Design gate:** Codex should write the direction statement, archetype and justified deviations in `DESIGN.md`; define semantic tokens and a working `style-guide.html` before building pages; then run §9 after each UI delivery. The guide requires an overall slop-check score of **at least 85/100** and **no category under 60/100**. Never declare that the finished UI passes without showing an actual audit.

## Intended architecture (not yet built)
Curated source layers / synthetic isolated fixtures → Pydantic schemas and provenance → bounded physical models (flood, water, heat, carbon) and physical site eligibility → PuLP/CBC MILP and alternatives → three shock re-evaluations → immutable run records → interactive dashboard + deterministic explanations; optionally Amazon S3 for storage and Amazon Bedrock for prose.

Preferred initial stack: Python, Pandas/NumPy, PuLP, Pydantic, Streamlit, Plotly, pytest. **Kiro, CKAN, Kubernetes/EKS, SageMaker, Glue/Athena, and full digital twins are not prerequisites.**

## Local setup for Codex / developers
After implementation files are added, run:

```bash
python -m venv .venv
# activate .venv using your OS-specific command
pip install -r requirements.txt
pytest -q
# after Codex implements app.py:
streamlit run app.py
```

At present, `pytest` exercises the **reference synthetic fixtures only**. Passing those tests does not mean the application is complete. Codex must implement and test the five official modules, then report the true completion state.

## Data integrity
- `data/raw/`: downloaded original datasets; not committed by default.
- `data/curated/`: derived/versioned municipal or public source subsets; hold back until validated.
- `data/synthetic_test/`: **illustrative development fixtures**, not measured neighbourhood statistics or validated intervention coefficients.
- Research PDFs are not redistributed here; see citation and link register instead. If a licence permits, provide only the specific research you need through the development workspace.

## Development handoff
See [`docs/CODEX_START_HERE.md`](docs/CODEX_START_HERE.md). Agree on data contracts, scientific assumptions, solver objective and acceptance tests before dividing tasks across four members.

## Deployment security
Use IAM roles or secure environment secrets, never put AWS credentials in repository files, and keep a local data/explanation fallback for judging.

## Handoff v2 — essential corrections
- Canonical `.env.example` keys now **exactly match** Master Plan §9.5; old `C1V1C_S3_BUCKET` / `C1V1C_S3_PREFIX` have been retired.
- `data/templates/` has blank source-quality-aware contracts and `data/source_registry.csv` lists public **leads**, not downloaded measurements.
- `docs/REQUIREMENTS_TRACEABILITY.md` defines PS-to-test mapping; `docs/DEVELOPMENT_GATES.md` defines build milestones.
- `docs/AWS_ACCESS_AND_FALLBACK.md` has a least-privilege deployment checklist. Cloud service permissions are not assumed.
- The user-supplied AWS/CKAN blueprint is in `docs/reference/`, but **CKAN/EKS is not in the 24-hour stack**.
- `scripts/preflight.py` and `.github/workflows/bootstrap-checks.yml` verify **handoff integrity only**, not the five unbuilt modules.

### Run before asking Codex to build
```bash
python scripts/preflight.py
python -m pip install 'pytest>=8,<10'
python -m pytest -q
```
Then read `docs/START_PROMPT_FOR_CODEX.md`. The real, user-supplied [`anti-slop-design.md`](anti-slop-design.md) is included: Codex must create `DESIGN.md`, the tokenized `style-guide.html`, and document its §9 review **before** presenting UI. The design guide itself is supplied; UI compliance is **not yet verified**.

### GitHub
This package contains local Git history but **does not create a GitHub repository**. Create a private empty repository under your account, then add its URL as `origin` and push `main`. Avoid committing `.env`, AWS credentials, confidential data or full third-party papers to a public repository.

## AWS / Hyderabad environment (owner-confirmed configuration; access not verified)

- **Region:** `ap-south-2` (Asia Pacific / Hyderabad).
- **S3 bucket:** `amzn-c1v1-bucket-515820372090-ap-south-2-an`.
- **AWS access:** The owner previously shared an access key pair in conversation. **Revoke/rotate the exposed key before use.** No keys are stored in the repository, archives or `.env.example`.
- **Local file:** copy `.env.example` to ignored `.env` for non-secret values. Use AWS CLI login/profile or a role for credentials; if the host needs environment-variable credentials, set a **new** access key/secret in the hosting dashboard's **Environment Variables / Secrets** settings, not in tracked files.
- **Bedrock:** still unverified; leave `BEDROCK_MODEL_ID` blank and `C1V1C_OFFLINE_MODE=true` until a successful invocation.

See [`docs/AWS_HYDERABAD_SETUP.md`](docs/AWS_HYDERABAD_SETUP.md) for rotation, IAM/S3 permissions, Codex-local vs cloud authentication, smoke checks, and deployment steps.
