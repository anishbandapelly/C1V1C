# Implementation status — Phases 4–6 (24 Oct 2026)

| Area | Status | Evidence |
|---|---|---|
| Frontend (Phases 1–3) | Approved design preserved, now wired to the engine | `ui/views.py`, `ui/backend.py`; fixtures removed |
| Data engine / curated Bengaluru baseline | Implemented (mixed-evidence pilot) | [DATA_PIPELINE.md](DATA_PIPELINE.md); `python -m c1v1c.pipeline` |
| Physical, economic and equity models | Implemented with documented equations | [MODELS.md](MODELS.md); [SCIENTIFIC_VALIDATION.md](SCIENTIFIC_VALIDATION.md) 43/43 |
| PuLP/CBC MILP, alternatives, infeasibility | Implemented, brute-force verified | `src/c1v1c/optimiser.py`; `tests/test_optimiser.py` |
| Scenario simulator (A/B/C) | Implemented | `engine.shock`; `tests/test_scenarios.py` |
| Decision explainer | Deterministic implemented; Bedrock adapter ready, live access blocked | `explainer.py`, `aws/bedrock.py` |
| Run store | Immutable, replay-verified; S3 adapter ready | `run_store.py`, `aws/s3.py` |
| HTTP API | Implemented | `src/c1v1c/api.py`; `tests/test_api.py` |
| AWS live services | S3 **live**; Bedrock **BLOCKED** (IAM denies InvokeModel) | [AWS_SERVICES.md](AWS_SERVICES.md) |
| Deployment | Docker on the owner's machine, healthy, 15/15 smoke checks; no public cloud | [DEPLOYMENT.md](DEPLOYMENT.md) |
| Tests | 139 passed | `pytest -q` |

Full requirement mapping: [COMPLIANCE_MATRIX.md](COMPLIANCE_MATRIX.md).
