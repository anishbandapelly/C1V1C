# AWS services — honest status (24 Oct 2026)

**Live AWS access: BLOCKED.** No AWS CLI, profile or credentials exist on the development machine. `python -m c1v1c.aws.status` reports `credentials: BLOCKED: no AWS credentials in the default provider chain`. The previously exposed key must be rotated and must not be reused. None of the services below has been called against a real account.

| Service (PS suggestion) | Status | What exists / why |
|---|---|---|
| **Amazon S3** | **Implemented, tested with stubs; live access BLOCKED** | `src/c1v1c/aws/s3.py`: SSE-encrypted put/get under `runs/` (immutable run JSON, version id and sha256 recorded); `FailoverS3` keeps local runs when S3 fails and records the error. Tests cover put/get, AccessDenied and a missing bucket. The live probe does head/put/get/delete on a health-check key once credentials exist. |
| **Amazon Bedrock** | **Implemented, tested with stubs; live access BLOCKED** | `src/c1v1c/aws/bedrock.py`: Converse API over computed facts only, with timeouts and retries. Every number in the response is validated, and the deterministic narrative is the fallback (offline, not configured, AccessDenied, timeout and hallucinated-number cases are tested). No model ID is configured, because none has been verified by a real invocation. |
| AWS Lambda | Replaced by a justified equivalent | Engine exposed as a FastAPI service (`c1v1c.api`) in the same container. Runs take ~0.1–0.5 s, so Lambda is technically feasible later (CBC binary plus a ~250 MB layer). Not provisioned (cost and approval). |
| App Runner / ECS Fargate | Prepared, not provisioned | The Docker image is verified locally; this is the deployment target once approved (see `DEPLOYMENT.md`). |
| AWS Glue / Athena | Deferred, unnecessary | The pipeline is a 25-second deterministic Python job over ~250 MB; a catalogue or SQL engine adds cost without benefit at pilot scale. |
| SageMaker / AWS Batch | Unnecessary | No model training. The MILP solves in under a second. |
| SimSpace Weaver / EventBridge | Unnecessary | Scenarios are parameter overrides re-evaluated synchronously; no agent simulation or event scheduling is needed. |
| OpenSearch | Unnecessary | Explanations are grounded on structured run records, not retrieval. |
| Amazon Location Service | Replaced | Carto/OpenStreetMap basemap via Plotly, with a tile-free offline mode. |
| QuickSight / Managed Grafana | Replaced | The approved Streamlit dashboard is the interactive dashboard. |

**To enable live S3 and Bedrock:**

1. Rotate the exposed key.
2. Configure SSO or a profile: `aws configure sso --profile c1v1c`, then `AWS_PROFILE=c1v1c`.
3. In Bedrock, enable access to a model available in ap-south-2 (or a cross-region inference profile).
4. Set `C1V1C_OFFLINE_MODE=false`, `BEDROCK_MODEL_ID=<verified id>`.
5. Run `python -m c1v1c.aws.status`. Mark S3 or Bedrock as live only when it shows `PASS`.
