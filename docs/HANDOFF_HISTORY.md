# Handoff history (pre-build README sections)

These sections were in the README while the repository was a planning scaffold, before Phases 4–6 were built. They are kept verbatim for traceability. For the current system, see the [README](../README.md) and [IMPLEMENTATION_STATUS](IMPLEMENTATION_STATUS.md).

## Intended architecture (as planned)
Curated source layers / synthetic isolated fixtures → Pydantic schemas and provenance → bounded physical models (flood, water, heat, carbon) and physical site eligibility → PuLP/CBC MILP and alternatives → three shock re-evaluations → immutable run records → interactive dashboard + deterministic explanations; optionally Amazon S3 for storage and Amazon Bedrock for prose.

Preferred initial stack: Python, Pandas/NumPy, PuLP, Pydantic, Streamlit, Plotly, pytest. **Kiro, CKAN, Kubernetes/EKS, SageMaker, Glue/Athena, and full digital twins are not prerequisites.**

## Development handoff
See [`CODEX_START_HERE.md`](CODEX_START_HERE.md). Agree on data contracts, scientific assumptions, solver objective and acceptance tests before dividing tasks across four members.

## Handoff v2 — essential corrections
- Canonical `.env.example` keys now **exactly match** Master Plan §9.5; old `C1V1C_S3_BUCKET` / `C1V1C_S3_PREFIX` have been retired.
- `data/templates/` has blank source-quality-aware contracts and `data/source_registry.csv` lists public **leads**, not downloaded measurements.
- `docs/REQUIREMENTS_TRACEABILITY.md` defines PS-to-test mapping; `docs/DEVELOPMENT_GATES.md` defines build milestones.
- `docs/AWS_ACCESS_AND_FALLBACK.md` has a least-privilege deployment checklist. Cloud service permissions are not assumed.
- The user-supplied AWS/CKAN blueprint is in `docs/reference/`, but **CKAN/EKS is not in the 24-hour stack**.
- `scripts/preflight.py` and `.github/workflows/bootstrap-checks.yml` verify **handoff integrity only**.

### Run before asking Codex to build
```bash
python scripts/preflight.py
python -m pip install 'pytest>=8,<10'
python -m pytest -q
```
Then read `docs/START_PROMPT_FOR_CODEX.md`.

### GitHub (original note)
This package contained local Git history but did not create a GitHub repository. The repository now exists at https://github.com/anishbandapelly/C1V1C.

## Frontend correction round 2
Correction round 2 added the exact budget editor, intervention request rows, streamlined scenario/decision layouts and a source-document compliance matrix. See [round-2 verification](FRONTEND_ROUND2_REVIEW.md) and [frontend requirements audit](FRONTEND_REQUIREMENTS_AUDIT.md).
