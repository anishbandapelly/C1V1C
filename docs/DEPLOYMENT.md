# Deployment

## Verified deployment (24 Oct 2026): Docker on the owner's workstation

| Item | Result |
|---|---|
| Image | `c1v1c-tulabhara:latest` (python:3.11-slim, non-root uid 10001, ~1.06 GB) |
| Services | `app` = Streamlit UI on :8501 · `api` = FastAPI on :8000 (`docker compose up -d`) |
| Health | both containers report `healthy` (UI `/_stcore/health`, API `/health`) |
| Solver in container | CBC (PuLP 3.3.2 bundled binary, x86_64) solves and returns the same ₹1.94 crore Balanced plan as the Windows dev build |
| Post-deploy smoke test | `python scripts/smoke_test.py` → **15/15 PASS** (UI, API, real zones, solver, budget, saved-run replay, all three shocks, explanation, 422 on bad input, honest infeasibility, AWS probe, no credential material) |
| AWS in container | `offline_mode=true`; the probe reports `BLOCKED: no AWS credentials` (no credentials are supplied) |

This is a local production-like deployment. **No public cloud deployment has been made**: that needs authorised AWS credentials, approval for chargeable services, or the owner's GitHub/Streamlit Cloud login.

## Build and run

```bash
pip install -r requirements-pipeline.txt
python -I scripts/data/fetch_drive_dataset.py   # raw data (not in Git)
python -m c1v1c.pipeline                        # curated baseline -> data/curated/bengaluru_pilot_v1
docker compose build
docker compose up -d
python scripts/smoke_test.py                    # post-deploy verification
```

The curated baseline is copied into the image at build time and is never committed (see the licence note in `DATA_PIPELINE.md`).

Without Docker:

```bash
pip install -r requirements.txt
streamlit run app.py
uvicorn c1v1c.api:app --port 8000
```

## Online mode (live AWS)

```bash
powershell -ExecutionPolicy Bypass -File scripts/aws_configure.ps1                 # once: you type a rotated key into %USERPROFILE%\.aws
docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d --build      # mounts ~/.aws read-only, C1V1C_OFFLINE_MODE=false
python scripts/smoke_test.py
```

Verified 24 Oct 2026: credentials PASS, S3 PASS, runs mirrored to S3, smoke test 15/15. Bedrock is blocked by IAM (see AWS_SERVICES.md).

## Configuration

Non-secret settings come from `.env.example`. Copy it to an ignored `.env` for local use; the variable names follow master plan §9.5.

| Variable | Default | Purpose |
|---|---|---|
| `AWS_REGION` | `ap-south-2` | Hyderabad |
| `S3_BUCKET`, `S3_RUNS_PREFIX`, `S3_CURATED_PREFIX` | owner bucket, `runs/`, `input/curated/` | run and baseline storage when online |
| `BEDROCK_MODEL_ID` | blank | set only after a successful invocation |
| `C1V1C_OFFLINE_MODE` | `true` | `false` enables S3 and Bedrock |
| `C1V1C_BASELINE_VERSION` | `bengaluru_pilot_v1` | curated baseline folder |
| `C1V1C_ROOT`, `C1V1C_RUNS_DIR`, `C1V1C_CURATED_DIR` | repo paths | path overrides (set in the image) |

**Credentials** are never read from these files. Use the default boto3 chain: an SSO or profile mount, an ECS/App Runner task role, or the host's secret store. Rotate the previously exposed key before any live use.

## Cloud deployment path (prepared, not executed — needs approval)

The same image runs on AWS App Runner or ECS Fargate in ap-south-2, with a task role limited to:

- `s3:GetObject`, `s3:PutObject` and `s3:ListBucket` on the project prefixes;
- `bedrock:InvokeModel` on the one approved model.

Health check path: `/_stcore/health`. These are chargeable services, so obtain cost approval first, then re-run `scripts/smoke_test.py --ui <url> --api <url>` against the deployed URLs.
