"""Find a Bedrock model that really answers for the configured profile, then enable it in .env.

Run after the IAM policy in config/iam/c1v1-app-bedrock-policy.json is attached:
    python scripts/enable_bedrock.py
Writes BEDROCK_MODEL_ID to the git-ignored .env ONLY if a live Converse call succeeds.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [
    "global.anthropic.claude-haiku-5-5",                 # current, cheapest adequate narrator first
    "global.anthropic.claude-sonnet-5-5",
    "in.anthropic.claude-haiku-4-5-20251001-v1:0",       # in-country (India) profile fallback
    "global.anthropic.claude-haiku-4-5-20251001-v1:0",
]


def env_value(name: str, default: str) -> str:
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip() or default
    return default


def main() -> int:
    profile = env_value("AWS_PROFILE", "c1v1c")
    region = env_value("AWS_REGION", "ap-south-2")
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client("bedrock-runtime", config=Config(read_timeout=30, retries={"max_attempts": 1}))
    try:  # discovery is optional; the invocation below is the real test
        listed = [p["inferenceProfileId"] for p in session.client("bedrock").list_inference_profiles()["inferenceProfileSummaries"]
                  if "anthropic" in p["inferenceProfileId"]]
        candidates = CANDIDATES + [m for m in listed if m not in CANDIDATES]
    except ClientError:
        candidates = CANDIDATES
    for model in candidates:
        try:
            r = client.converse(modelId=model, messages=[{"role": "user", "content": [{"text": "Reply with OK."}]}],
                                inferenceConfig={"maxTokens": 5})
            text = r["output"]["message"]["content"][0].get("text", "")
        except ClientError as e:
            print(f"fail {model}: {e.response['Error']['Code']}")
            continue
        except BotoCoreError as e:
            print(f"fail {model}: {type(e).__name__}")
            continue
        print(f"PASS {model}: replied {text!r}")
        env = ROOT / ".env"
        body = env.read_text(encoding="utf-8") if env.exists() else ""
        line = f"BEDROCK_MODEL_ID={model}"
        body = re.sub(r"(?m)^BEDROCK_MODEL_ID=.*$", line, body) if "BEDROCK_MODEL_ID=" in body else body.rstrip() + "\n" + line + "\n"
        env.write_text(body, encoding="utf-8")
        print(f"Enabled {model} in .env. Restart: docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d")
        return 0
    print("No Bedrock model answered. Attach config/iam/c1v1-app-bedrock-policy.json to the IAM user and enable "
          "Anthropic model access in the Bedrock console (ap-south-2), then re-run.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
