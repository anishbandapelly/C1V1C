#!/usr/bin/env python3
"""Validate non-secret AWS handoff configuration without making network calls."""
from pathlib import Path
import os
import re

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REGION = 'ap-south-2'
EXPECTED_BUCKET = 'amzn-c1v1-bucket-515820372090-ap-south-2-an'


def read_example():
    settings = {}
    for line in (ROOT / '.env.example').read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            name, value = line.split('=', 1)
            settings[name.strip()] = value.strip()
    return settings


def main():
    vals=read_example()
    assert vals.get('AWS_REGION') == EXPECTED_REGION, 'Unexpected AWS Region'
    assert vals.get('S3_BUCKET') == EXPECTED_BUCKET, 'S3 bucket configuration mismatch'
    for name in ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN'):
        assert name not in vals, 'Credentials must never be committed in .env.example'
    assert vals.get('C1V1C_OFFLINE_MODE','').lower()=='true', 'Offline fallback must remain enabled until verified'
    assert not vals.get('BEDROCK_MODEL_ID'), 'Bedrock model has not yet been verified'
    print('PASS: Hyderabad region, named S3 bucket, no saved credentials, offline Bedrock fallback.')
    print('NOTE: Configuration-only check. Does not verify real AWS permissions or bucket existence.')


if __name__=='__main__':
    main()
