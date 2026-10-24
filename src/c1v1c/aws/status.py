"""Live AWS capability probe. Reports PASS/BLOCKED per service without printing identifiers or secrets.

Run: python -m c1v1c.aws.status
"""
from __future__ import annotations

import json
import uuid

from c1v1c.config import Settings


def probe(settings: Settings | None = None) -> dict:
    settings = settings or Settings.load()
    out = {"region": settings.aws_region, "offline_mode": settings.offline_mode}
    import boto3
    from botocore.config import Config
    from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

    cfg = Config(region_name=settings.aws_region, connect_timeout=settings.aws_timeout_s, read_timeout=settings.aws_timeout_s,
                 retries={"max_attempts": 1})
    try:
        boto3.client("sts", config=cfg).get_caller_identity()
        out["credentials"] = "PASS: credentials resolved by the default provider chain"
    except NoCredentialsError:
        return {**out, "credentials": "BLOCKED: no AWS credentials in the default provider chain",
                "s3": "BLOCKED: no credentials", "bedrock": "BLOCKED: no credentials"}
    except (ClientError, BotoCoreError) as exc:
        return {**out, "credentials": f"BLOCKED: {exc.__class__.__name__}", "s3": "BLOCKED", "bedrock": "BLOCKED"}
    if settings.s3_bucket:
        s3 = boto3.client("s3", config=cfg)
        key = f"{settings.s3_runs_prefix}_healthcheck/{uuid.uuid4().hex}.json"
        try:
            s3.head_bucket(Bucket=settings.s3_bucket)
            s3.put_object(Bucket=settings.s3_bucket, Key=key, Body=b'{"ok": true}', ServerSideEncryption="AES256")
            s3.get_object(Bucket=settings.s3_bucket, Key=key)
            s3.delete_object(Bucket=settings.s3_bucket, Key=key)
            out["s3"] = "PASS: head/put/get/delete under the runs prefix"
        except ClientError as exc:
            out["s3"] = f"BLOCKED: {exc.response.get('Error', {}).get('Code', 'ClientError')}"
        except BotoCoreError as exc:
            out["s3"] = f"BLOCKED: {exc.__class__.__name__}"
    else:
        out["s3"] = "BLOCKED: S3_BUCKET not set"
    if settings.bedrock_model_id:
        try:
            r = boto3.client("bedrock-runtime", config=cfg).converse(
                modelId=settings.bedrock_model_id, messages=[{"role": "user", "content": [{"text": "Reply with OK."}]}],
                inferenceConfig={"maxTokens": 5})
            out["bedrock"] = "PASS: Converse invocation succeeded" if r.get("output") else "BLOCKED: empty response"
        except ClientError as exc:
            out["bedrock"] = f"BLOCKED: {exc.response.get('Error', {}).get('Code', 'ClientError')}"
        except BotoCoreError as exc:
            out["bedrock"] = f"BLOCKED: {exc.__class__.__name__}"
    else:
        out["bedrock"] = "BLOCKED: BEDROCK_MODEL_ID not set"
    return out


if __name__ == "__main__":
    print(json.dumps(probe(), indent=1))
