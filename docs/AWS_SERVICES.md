# AWS services — honest status (24 Oct 2026)

**Live AWS access: credentials PASS, S3 PASS (live), Bedrock BLOCKED at account level.**

- **Credentials:** profile `c1v1c` (IAM user `c1v1-app`). The key was rotated on 24 Oct 2026; the exposed key is deactivated. The profile is written by `scripts/aws_configure.ps1` and stored only in `%USERPROFILE%\.aws`. Containers mount it read-only via `docker-compose.aws.yml`.
- **S3:** `python -m c1v1c.aws.status` passes head, put, get and delete on `amzn-c1v1-bucket-515820372090-ap-south-2-an`. The deployed API reports `s3_runs: enabled`. Every run and comparison is mirrored to `runs/runs/` and `runs/comparisons/` (SSE-S3 AES256, versioned). The smoke test is 15/15, run online.
- **Bedrock — IAM resolved, account blocked:**
  - **IAM resolved.** The IAM user's policy `c1v1c-policy` now includes the statements from [`config/iam/c1v1-app-bedrock-policy.json`](../config/iam/c1v1-app-bedrock-policy.json): invoke Claude Haiku 5.5 / Sonnet 5.5 (and Haiku 4.5), plus model discovery. Model listing works.
  - **Account blocked.** Every Claude invocation (Haiku 5.5, Sonnet 5.5, Haiku 4.5) returns `ValidationException: Operation not allowed`. The account root user gets the same error for Claude Haiku 5.5 in the Bedrock console playground. This is an account-level restriction that only AWS can lift (billing/verification or a support case for Bedrock in ap-south-2). It is not an app or IAM problem.
  - **Fallback.** `BEDROCK_MODEL_ID` stays blank and Decision Intelligence shows the deterministic explanation, with the status shown to the user.

**When AWS lifts the restriction:** run `python scripts/enable_bedrock.py`. It tries Haiku 5.5 first and writes `BEDROCK_MODEL_ID` to `.env` only after a live Converse call succeeds. Then restart:

```bash
docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d
```

| Service (PS suggestion) | Status | What exists / why |
|---|---|---|
| **Amazon S3** | **Live — PASS** | `src/c1v1c/aws/s3.py`: SSE-encrypted put/get under `runs/` (immutable run JSON, version id and sha256 recorded); `FailoverS3` keeps local runs when S3 fails and records the error. Tests cover put/get, AccessDenied and a missing bucket. The live probe does head/put/get/delete on a health-check key once credentials exist. |
| **Amazon Bedrock** | **Implemented; IAM granted; live use BLOCKED by an account-level restriction** | `src/c1v1c/aws/bedrock.py`: Converse API over computed facts only, with timeouts and retries. Every number in the response is validated, and the deterministic narrative is the fallback (offline, not configured, AccessDenied, timeout and hallucinated-number cases are tested). No model ID is configured, because none has been verified by a real invocation. |
| AWS Lambda | Replaced by a justified equivalent | Engine exposed as a FastAPI service (`c1v1c.api`) in the same container. Runs take ~0.1–0.5 s, so Lambda is technically feasible later (CBC binary plus a ~250 MB layer). Not provisioned (cost and approval). |
| App Runner / ECS Fargate | Prepared, not provisioned | The Docker image is verified locally; this is the deployment target once approved (see `DEPLOYMENT.md`). |
| AWS Glue / Athena | Deferred, unnecessary | The pipeline is a 25-second deterministic Python job over ~250 MB; a catalogue or SQL engine adds cost without benefit at pilot scale. |
| SageMaker / AWS Batch | Unnecessary | No model training. The MILP solves in under a second. |
| SimSpace Weaver / EventBridge | Unnecessary | Scenarios are parameter overrides re-evaluated synchronously; no agent simulation or event scheduling is needed. |
| OpenSearch | Unnecessary | Explanations are grounded on structured run records, not retrieval. |
| Amazon Location Service | Replaced | Carto/OpenStreetMap basemap via Plotly, with a tile-free offline mode. |
| QuickSight / Managed Grafana | Replaced | The approved Streamlit dashboard is the interactive dashboard. |
