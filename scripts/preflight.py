#!/usr/bin/env python3
"""Local handoff readiness audit: NOT an application functional test."""
from __future__ import annotations
from pathlib import Path
import argparse
import csv
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'AGENTS.md','README.md','anti-slop-design.md','docs/Original_Sustainable_Development_PS.docx',
    'docs/C1V1C_Master_Plan.docx','docs/MASTER_PLAN.md','docs/ANTI_AI_SLOP.md',
    'docs/REQUIREMENTS_TRACEABILITY.md','docs/INPUT_DATA_AND_PROVENANCE.md',
    'docs/AWS_ACCESS_AND_FALLBACK.md','docs/research_evidence.md',
    'data/synthetic_test/fixture_manifest.json', 'data/source_registry.csv',
    'tests/test_reference_fixtures.py', '.env.example', 'docs/AWS_HYDERABAD_SETUP.md', 'scripts/aws_config_check.py'
]
CONFIG = {
    'AWS_REGION','S3_BUCKET','S3_CURATED_PREFIX','S3_RUNS_PREFIX',
    'BEDROCK_MODEL_ID','C1V1C_OFFLINE_MODE','C1V1C_BASELINE_VERSION',
    'C1V1C_MODEL_VERSION'
}

def scan() -> tuple[list[str], list[str]]:
    failures=[]; warnings=[]
    for p in REQUIRED:
        if not (ROOT/p).is_file():failures.append('Missing required handoff file: '+p)
    source=ROOT/'docs/MASTER_PLAN.md'
    template=ROOT/'.env.example'
    if source.is_file() and template.is_file():
        md=source.read_text('utf-8')
        cfg=set(re.findall(r'^([A-Z][A-Z0-9_]+)=',template.read_text('utf-8'),re.M))
        missing=CONFIG-cfg
        if missing:failures.append('Missing canonical env variable(s): '+', '.join(sorted(missing)))
        if 'S3_BUCKET=' not in md or 'S3_RUNS_PREFIX=' not in md:
            failures.append('Master Plan environment contract not readable/matching')
    guide=ROOT/'anti-slop-design.md'
    mirror=ROOT/'docs/ANTI_AI_SLOP.md'
    if guide.is_file() and mirror.is_file():
        contents=guide.read_text('utf-8')
        if guide.read_bytes()!=mirror.read_bytes():
            failures.append('docs/ANTI_AI_SLOP.md mirror differs from canonical root anti-slop-design.md')
        if '# Anti-Slop Design Guide' not in contents or '## 9. Slop check' not in contents or '## 7. Workflow summary' not in contents:
            failures.append('User design guide appears incomplete or invalid')
        if 'anti-slop-design.md' not in (ROOT/'README.md').read_text('utf-8'):
            failures.append('README does not link to actual design guide')
    try:
        manifest=json.loads((ROOT/'data/synthetic_test/fixture_manifest.json').read_text('utf-8'))
        if manifest.get('status')!='synthetic_only_not_city_data':
            failures.append('Synthetic fixture manifest does not clearly identify synthetic-only data')
    except Exception as e: failures.append('Fixture manifest invalid: '+str(e))
    if template.is_file():
        settings={a.strip():b.strip() for a,b in (line.split('=',1) for line in template.read_text('utf-8').splitlines() if '=' in line and not line.lstrip().startswith('#'))}
        if settings.get('AWS_REGION') != 'ap-south-2':
            failures.append('AWS_REGION must reflect owner-selected Hyderabad (ap-south-2)')
        if settings.get('S3_BUCKET') != 'amzn-c1v1-bucket-515820372090-ap-south-2-an':
            failures.append('S3_BUCKET must reflect user-supplied project bucket')
        for key in ('AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN'):
            if key in settings:
                failures.append('Credential variable must not appear in checked-in .env.example')
    ignore=(ROOT/'.gitignore')
    if not ignore.exists() or '.env' not in ignore.read_text('utf-8'):
        failures.append('Missing .env ignore rule')
    if (ROOT/'.git').is_dir():
        import subprocess
        p=subprocess.run(['git','-C',str(ROOT),'ls-files','--error-unmatch','.env'],capture_output=True)
        if p.returncode==0: failures.append('DANGER: .env is tracked by Git')
    if not any((ROOT/'data/curated').glob('*.csv')):
        warnings.append('No verified curated local pilot datasets supplied (not an error for scaffold)')
    if not (ROOT/'app.py').exists():
        warnings.append('Application NOT IMPLEMENTED; this check does not validate product functions')
    if not (ROOT/'.git/config').exists():
        warnings.append('No embedded local Git configuration; create/push repo if required')
    else:
        git=(ROOT/'.git/config').read_text('utf-8')
        if '[remote "origin"]' not in git:
            warnings.append('No GitHub remote configured; local repository is not published')
    return failures,warnings

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--strict',action='store_true',help='Treat unresolved external/user blockers as errors')
    a=ap.parse_args()
    failures,warnings=scan()
    for x in failures: print('FAIL:',x)
    for x in warnings: print('PENDING:',x)
    if not failures: print('PASS: Bootstrap handoff integrity only. P0 application NOT verified.')
    if failures or (a.strict and warnings):sys.exit(1)
