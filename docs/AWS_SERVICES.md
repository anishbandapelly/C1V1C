# AWS services — honest status (24 Oct 2026)

**Live AWS access: credentials PASS, S3 PASS (live), Bedrock BLOCKED by IAM.**

- **Credentials:** profile `c1v1c` (IAM user `c1v1-app`), set up with a rotated key through `scripts/aws_configure.ps1`. It is stored only in `%USERPROFILE%\.aws`. Containers mount it read-only via `docker-compose.aws.yml`.
- **S3:** `python -m c1v1c.aws.status` passes head, put, get and delete on `amzn-c1v1-bucket-515820372090-ap-south-2-an`. The deployed API reports `s3_runs: enabled`. Every run and comparison is mirrored to `runs/runs/` and `runs/comparisons/` with AES256 encryption and object versioning. The smoke test is 15/15, run online.
- **Bedrock:** a real Converse call on `global.anthropic.claude-sonnet-4-5-20250929-v1:0` and `global.anthropic.claude-haiku-4-5-20251001-v1:0` returns **AccessDeniedException: not authorized to perform bedrock:InvokeModel**. `ListFoundationModels` and `ListInferenceProfiles` are also denied. Older apac Claude 3.7 / 4 profiles are end-of-life, and the Nova IDs tried are not offered in ap-south-2. `BEDROCK_MODEL_ID` stays blank and the deterministic explainer is used, labelled as such.

**To unblock Bedrock** (account owner, in IAM): attach this policy to `c1v1-app`. Then make sure Anthropic model access is enabled in the Bedrock console (including the one-time use-case form).

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
     "Resource": ["arn:aws:bedrock:*::foundation-model/anthropic.claude-haiku-4-5-*",
                  "arn:aws:bedrock:*:*:inference-profile/global.anthropic.claude-haiku-4-5-*"]},
    {"Effect": "Allow", "Action": ["bedrock:ListFoundationModels", "bedrock:ListInferenceProfiles", "bedrock:GetInferenceProfile"],
     "Resource": "*"}
  ]
}
```

Then set `BEDROCK_MODEL_ID=global.anthropic.claude-haiku-4-5-20251001-v1:0` in `.env` **only after** `python -m c1v1c.aws.status` reports `bedrock: PASS`.

| Service (PS suggestion) | Status | What exists / why |
|---|---|---|
| **Amazon S3** | **Live — PASS** | `src/c1v1c/aws/s3.py`: SSE-encrypted put/get under `runs/` (immutable run JSON, version id and sha256 recorded); `FailoverS3` keeps local runs when S3 fails and records the error. Tests cover put/get, AccessDenied and a missing bucket. The live probe does head/put/get/delete on a health-check key once credentials exist. |
| **Amazon Bedrock** | **Implemented; live access BLOCKED by IAM (InvokeModel denied)** | `src/c1v1c/aws/bedrock.py`: Converse API over computed facts only, with timeouts and retries. Every number in the response is validated, and the deterministic narrative is the fallback (offline, not configured, AccessDenied, timeout and hallucinated-number cases are tested). No model ID is configured, because none has been verified by a real invocation. |
| AWS Lambda | Replaced by a justified equivalent | Engine exposed as a FastAPI service (`c1v1c.api`) in the same container. Runs take ~0.1–0.5 s, so Lambda is technically feasible later (CBC binary plus a ~250 MB layer). Not provisioned (cost and approval). |
| App Runner / ECS Fargate | Prepared, not provisioned | The Docker image is verified locally; this is the deployment target once approved (see `DEPLOYMENT.md`). |
| AWS Glue / Athena | Deferred, unnecessary | The pipeline is a 25-second deterministic Python job over ~250 MB; a catalogue or SQL engine adds cost without benefit at pilot scale. |
| SageMaker / AWS Batch | Unnecessary | No model training. The MILP solves in under a second. |
| SimSpace Weaver / EventBridge | Unnecessary | Scenarios are parameter overrides re-evaluated synchronously; no agent simulation or event scheduling is needed. |
| OpenSearch | Unnecessary | Explanations are grounded on structured run records, not retrieval. |
| Amazon Location Service | Replaced | Carto/OpenStreetMap basemap via Plotly, with a tile-free offline mode. |
| QuickSight / Managed Grafana | Replaced | The approved Streamlit dashboard is the interactive dashboard. |
