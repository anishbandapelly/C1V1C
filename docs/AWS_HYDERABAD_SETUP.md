# AWS Hyderabad deployment setup — C1V1C

**Region:** `ap-south-2` (Asia Pacific / Hyderabad)  
**S3 bucket:** `amzn-c1v1-bucket-515820372090-ap-south-2-an`  
**Status:** values were provided by the project owner; neither S3 access nor Bedrock inference has been independently verified.

## Urgent: rotate the exposed key before any deployment

An AWS access key ID and its secret were shared in the project conversation. **Treat that pair as compromised** even if the key seems unused. In AWS Console, open **IAM → Users → [the owning IAM user] → Security credentials → Access keys**, deactivate the exposed key immediately, then delete it after any required migration. If the key belongs to the root user, follow AWS root access-key removal guidance and use an IAM role/temporary session instead. Audit recent AWS activity, spend and CloudTrail as appropriate. Never place the exposed pair into `.env`, an artifact, screenshots, Git history, tickets or chat again.

Do not rely on `.gitignore` alone: it cannot erase a secret that was already committed. If a secret ever reaches remote Git history, rotate first and treat historical removal separately.

## Safe configuration

The checked-in `.env.example` intentionally contains only the **non-secret** Region, bucket, prefixes and offline defaults. `BEDROCK_MODEL_ID` is left blank until a successful account-authorised invocation confirms the exact identifier/API.

**Preferred local access:** temporary credentials via IAM Identity Center / AWS CLI profile / role. Example checks:

```bash
aws sts get-caller-identity --profile c1v1c --region ap-south-2
aws s3api head-bucket --bucket amzn-c1v1-bucket-515820372090-ap-south-2-an --region ap-south-2 --profile c1v1c
```

AWS profiles are machine-specific. A separate Codex cloud container **does not inherit** credentials configured on your laptop. Configure access only through the workspace's supported secrets mechanism or attach an authorised execution role.

**If environment-variable credentials are truly required:** generate a **new, least-privilege** pair after rotation; set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as **secret settings in the execution/hosting environment** (and `AWS_SESSION_TOKEN` if temporary credentials are used). Set `AWS_REGION=ap-south-2` and `S3_BUCKET=amzn-c1v1-bucket-515820372090-ap-south-2-an` there as non-secret variables. Do not expose or commit credential values.

A `.env` file does **not** automatically become process environment variables for every application. Codex must either configure `python-dotenv`/the Streamlit secrets facility securely or use an already-exported environment/profile. The `boto3` standard credential-provider chain can use inherited environment variables, profiles and roles.

## S3 permissions (scoped to this project's prefixes)

- `s3:ListBucket` on the named bucket, ideally narrowed by prefix.
- `s3:GetObject` for `input/curated/*` and relevant provenance objects.
- `s3:PutObject` for `runs/*` and exported reports, plus `s3:GetObject` if replay is implemented.
- Do not allow public bucket access, embed credentials in UI bundles, or assign blanket `AdministratorAccess` solely for this hackathon.
- Configure default encryption and cost alerts; grant any customer-managed KMS permissions only if actually needed.
- Codex should verify access using `head-bucket` and a deliberately harmless test object under a designated project test prefix (with clean-up), **without** logging the account number, credentials or sensitive data.

## Bedrock remains optional, unverified

Prior tests showed account verification / invocation errors. Do not assume model IDs or entitlement based on their appearance in the model catalogue. Test `get-inference-profile` and a real Playground/API invocation **after** account verification (and Anthropic first-use registration if choosing Claude). Set `BEDROCK_MODEL_ID` only to the confirmed working inference-profile identifier and keep `C1V1C_OFFLINE_MODE=true` until then. The deterministic Decision Explainer must work without Bedrock.

## Local smoke checks before building

```bash
python scripts/preflight.py
python -m pytest -q
python scripts/aws_config_check.py
```

`aws_config_check.py` validates local configuration without making AWS calls. Live `sts` / `s3api` commands above are separate authorisation tests. Never print the process environment or full credentials in build logs.

## Deployment checklist

1. Rotate/revoke the exposed key; choose authorised least-privilege identity/role.
2. Confirm AWS account verification is complete and Hyderabad Region is selected.
3. Confirm S3 bucket exists and that the Codex execution environment can access it.
4. Supply AWS variables through the hosting platform secret/environment settings, never source control.
5. Leave Bedrock model ID blank and offline fallback active until a successful invoke.
6. Test offline operation, live S3 upload/replay, and error handling independently; report each honestly.
