# Repository package manifest (handoff v2)

This package deliberately includes **source-of-truth documents and executable bootstrap checks**, not a fictitious finished product. All application modules will be implemented by Codex Astra.

| Path | Purpose | Completion state |
| --- | --- | --- |
| `AGENTS.md` | Agent precedence, science/security guardrails | Complete handoff |
| `docs/Original_Sustainable_Development_PS.docx` | Official non-negotiable problem statement | Exact supplied source |
| `docs/C1V1C_Master_Plan.docx` + `docs/MASTER_PLAN.md` | Approved technical specification | Supplied + converted copy |
| `docs/reference/*` | User-supplied AWS/CKAN supplemental blueprint | Present, lower priority than master |
| `anti-slop-design.md` | **Actual user-supplied UI rulebook** | Exact original at root; included and ready to follow |
| `docs/ANTI_AI_SLOP.md` | Compatibility mirror of original guide | Exact byte-for-byte copy of root guide; test-enforced |
| `docs/research_evidence.md` | Selected paper methodology and limitations | Present (not a full research PDF corpus) |
| `docs/REQUIREMENTS_TRACEABILITY.md` | Official requirements to features/tests | Complete planning, no product evidence yet |
| `docs/INPUT_DATA_AND_PROVENANCE.md`, `data/source_registry.csv` | Source leads, quality rules, provenance | Complete guidance; source data unverified |
| `data/templates/` | Empty CSV/JSON data input contracts | Present, no fake city rows |
| `data/synthetic_test/` | Synthetic reference fixtures and expected outputs | Present, **not local measured data** |
| `.env.example`, `docs/AWS_ACCESS_AND_FALLBACK.md` | Canonical AWS config and safe runbook | Complete instructions; AWS unconfigured |
| `scripts/preflight.py`, `tests/` | Handoff integrity and synthetic reference testing | Present, **not application QA** |
| `.github/workflows/bootstrap-checks.yml` | CI for scaffold health | Present, cannot certify app release |
| `docs/START_PROMPT_FOR_CODEX.md` | Starting message to implementation agent | Present |
| `src/` | App implementation home | Intentional scaffold only |

`AGENTS.md` / `docs/MASTER_PLAN.md` explicitly forbid representing synthetic fixtures or unimplemented modules as completed. Run `python scripts/preflight.py` and `python -m pytest -q` after unpacking. Only print `PASS` for scaffold health. `--strict` intentionally fails while external inputs remain unresolved.

## Handoff v3 — AWS Hyderabad configuration

- `.env.example`: `AWS_REGION=ap-south-2` and owner-specified S3 bucket; **no AWS credential values**.
- `.gitignore`: excludes local environment files and credential artifacts, including nested `.env` files. Secrets must additionally be rotated if disclosed.
- `docs/AWS_HYDERABAD_SETUP.md`: credentials rotation, least-privilege S3, Cloud Codex authentication, host environment settings, checks and fallback.
- `scripts/aws_config_check.py`: tests safe, static settings without AWS calls.
- `scripts/secret_safety_check.py`: best-effort tracked-file credential-safety gate.
- Bedrock access/model remains **unverified**; use the deterministic local explanation until successfully tested.
- This is still a development scaffold, not the finished five-module application.
