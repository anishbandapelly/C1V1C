# Locked decisions and outstanding external inputs

## Official requirements (non-negotiable)
Five PS modules; green roofs, urban forests, rainwater harvesting, drainage upgrades; rainfall/drought/budget shocks; social equity, environmental impact and economic feasibility; explain uncertainty and side effects.

## Project decisions (master-plan level)
- Project: **C1V1C — Tulabhara AI**.
- Pilot: Bengaluru / Yelahanka catchment context, three coherent test zones when data verified; do **not** claim synthetic A/B/C are measured wards.
- Stack: Python/Pydantic + bounded physical models + PuLP/CBC MILP + Streamlit; optional S3/Bedrock; Codex as implementation agent.
- Source and baseline versioning; immutable result and before-shock frozen-plan evaluation distinct from reoptimisation.
- Green/grey interactions, equity and carbon accounting must be scientifically limited and auditable.

## User-supplied content or access still necessary
1. **UI design execution (Codex task)**. The actual user's `anti-slop-design.md` has now been supplied. Codex must create `DESIGN.md` and `style-guide.html`, justify any §4 rule breaks, and document a §9 audit (overall ≥85; no category below 60) before showing UI.
2. **Authorised GitHub remote**. No remote is included; user creates repository and pushes, or grants repo permissions. Local `.git` history does not mean hosted.
3. **Actual Bengaluru pilot input**, when verified-city claims are desired. Codex can research/download public layers but cannot manufacture local field values. If unavailable, disclose synthetic/mixed mode.
4. **AWS account / IAM / Region and Bedrock access**, if using S3 or Bedrock. Codex can write cloud adapters and configure access once authorised; credentials must never go in repo.
5. **Project visibility and release decision**. Default recommendation: keep repo private while sources, permissions and data licences remain unresolved.

## Astra handles without additional user files
Writing application source code, numerical models, actual MILP, synthetic fixture tests and integration tests, four-tab dashboard, resolver of compatible dependency lock, documented scripts, AWS SDK adapters, deployment instructions, run screenshots and final build-status reporting.

## Conditions for release
All P0 verification evidence in `docs/REQUIREMENTS_TRACEABILITY.md`; no undisclosed synthetic numbers; actual Anti-Slop §9 audit passed; original PS demonstrable; fallback works; no embedded secrets. Check `docs/DEVELOPMENT_GATES.md`.

## Update — AWS Region and S3 configuration (23 Oct 2026)

- Owner selected Hyderabad `ap-south-2` and supplied the bucket name in `.env.example`.
- The IAM key pair shared in chat must be rotated/revoked before any live AWS usage. **No credential values are stored in the repository.**
- AWS API access, S3 bucket existence/permissions, account verification status, and Bedrock inference remain unverified from the local scaffold.
- Codex can implement SDK adapters and safe fallback. The owner must provide a new authorised identity/secret via local profile, role or hosting secret settings; never through repository files.
