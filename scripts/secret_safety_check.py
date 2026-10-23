#!/usr/bin/env python3
"""Fail if tracked files appear to contain AWS long-lived keys or .env files.

This is a guardrail, not a substitute for secret scanning and key rotation.
Never prints matched credential content.
"""
from __future__ import annotations
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
IDENT=re.compile(rb'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b')
VALUE=re.compile(rb'(?m)^\s*(?:export\s+)?(?:AWS_SECRET_ACCESS_KEY|AWS_ACCESS_KEY_ID|AWS_SESSION_TOKEN)\s*=\s*[\"\']?[^\s#\"\']+')

def scan():
    files=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).split(b'\0')
    flagged=[]
    for raw in files:
        if not raw: continue
        relative=raw.decode('utf-8','surrogateescape')
        if relative == '.env' or relative.endswith('/.env') or relative.startswith('.env.') and relative!='.env.example':
            flagged.append(relative)
            continue
        blob=(ROOT/relative).read_bytes()
        if b'\0' in blob[:4096]: continue
        # Exclude commented rules and code snippets that merely name variables.
        real_lines=b'\n'.join(line for line in blob.splitlines() if not line.lstrip().startswith((b'#',b'//',b'-',b'*',b'>',b'"',b"'")))
        if IDENT.search(blob) or VALUE.search(real_lines):
            flagged.append(relative)
    return sorted(set(flagged))

if __name__=='__main__':
    bad=scan()
    if bad:
        print('FAIL: Suspected secret or tracked environment file at: '+', '.join(bad))
        sys.exit(1)
    print('PASS: No obvious access keys or tracked environment secrets in current tracked files.')
    print('NOTE: Automated scanning cannot guarantee the absence of every type of secret; rotate disclosed keys.')
