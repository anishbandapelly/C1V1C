# AWS setup / security / graceful fallback (developer runbook)

**No AWS account, Region access, bucket, model or permission has been verified for this project.** This is a setup checklist, not proof of connected services. Use AWS only when it improves functionality, and never block the P0 offline demo on IAM configuration.

## Canonical config (matches Master §9.5)
`AWS_REGION`, `S3_BUCKET`, `S3_CURATED_PREFIX`, `S3_RUNS_PREFIX`, `BEDROCK_MODEL_ID`, `C1V1C_OFFLINE_MODE`, `C1V1C_BASELINE_VERSION`, `C1V1C_MODEL_VERSION`.

Copy `.env.example` to `.env` on your own machine; `.env` is gitignored. `C1V1C_OFFLINE_MODE=true` is the safe default. Do not put AWS access keys in `.env` unless there is a genuinely unavoidable, approved local flow; prefer AWS SDK credential-provider chain (SSO/profile/role). Never share credentials in prompts, screenshots or commits.

## S3 — worthwhile for auditability
1. Establish permitted account, Region, billing controls and identity (`aws sts get-caller-identity`; keep account ID private).
2. Create a **private** bucket with blocked public access, default encryption, versioning when practical. Choose a globally unique name, not a hard-coded one from docs.
3. Scope read access to `input/curated/` and `provenance/`; write access to `runs/`/`exports/`; and `ListBucket` to required prefixes. Do **not** grant `s3:*` on `*`. If encryption uses a customer-managed KMS key, scope the necessary KMS grants separately.
4. In boto3, load a versioned baseline from S3 or verified local copy; save immutable `runs/{run_id}.json` and manifest/checksums. Test denied access and temporary outage fallback.
5. A successful local test is not evidence S3 integration is active; show S3 key/version/read and saved object ID in the live app only if verified.

## Bedrock — explanation only, optional
1. Check regional model availability, invocation/inference-profile prerequisites, IAM permissions and service quotas. Set `BEDROCK_MODEL_ID` to the actual permitted model/profile ID, never an invented string.
2. Grant model invocation to the **specific permitted resource(s)**, with streaming only if implemented; check inference-profile dependencies when applicable.
3. Send only sourced, redacted RunResult facts and curated methodology snippets. Do not send raw sensitive records or pass untrusted retrieved documents as system instructions.
4. Validate response numeric mentions against saved values; fall back to deterministic explanations if model access fails/response contradicts calculations.

## Hosting
Default: Python/Streamlit deployable locally, optionally Streamlit Community Cloud. Use AWS container infrastructure only if already provisioned and not distracting from core modelling. A public website is not mandatory evidence of AWS; demonstrate real S3 or Bedrock operation where available.

## Preflight / required demo
- `python scripts/preflight.py` checks local package completeness and shows all remaining blockers.
- When AWS is ready, run an explicit provider check and report only `S3: verified` / `Bedrock: verified`; do not log secrets.
- Force offline mode and verify the **full five-module** workflow. Record the run ID, baseline hash, version and test results.

## Do not deploy
CKAN/EKS, Glue/Athena, SimSpace Weaver, OpenSearch, Batch, multi-agent RAG or SageMaker solely to imitate the PDF's reference architecture.

## Owner's current non-secret configuration (updated)

- AWS Region: **Hyderabad (`ap-south-2`)**, replacing the earlier Mumbai (`ap-south-1`) bootstrap default.
- S3 bucket: **`amzn-c1v1-bucket-515820372090-ap-south-2-an`** (user-provided name, not independently checked).
- Bedrock: **not verified**; leave model/profile ID blank and keep offline fallback active until the AWS account and selected model work.
- **Urgent:** An AWS access key pair was disclosed in conversation; revoke/rotate it before using this deployment. Do **not** copy it into the repository, `.env`, ZIP or CI.

For concrete set-up steps and credential hygiene, follow [`AWS_HYDERABAD_SETUP.md`](AWS_HYDERABAD_SETUP.md). Use the checked-in `.env.example` for non-secret settings and provide secrets via a role/profile or platform environment-variable vault. A `.env` file is gitignored, but ignore rules are not a replacement for rotation or safe key management.
