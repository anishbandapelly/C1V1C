# Short prompt for Codex Astra

> Build C1V1C — Tulabhara AI end-to-end using this repository. Read `AGENTS.md`, the official problem statement, and `docs/MASTER_PLAN.md` first, then implement and test all five required modules. **Before writing any UI**, read `anti-slop-design.md` fully: define the direction and archetype in `DESIGN.md`, build tokens and `style-guide.html` first, justify any banned defaults, and pass its §9 slop audit before showing UI. Use AWS only where it adds functional value. Never fabricate datasets or results. Run tests, update implementation status, and demonstrate the working application.

`docs/CODEX_START_HERE.md` retains the longer engineering handoff and test gates. The uploaded design guide is present at repository root.

**AWS configuration note:** Use Hyderabad `ap-south-2` and the S3 bucket in `.env.example`. An AWS access key pair was exposed; do not reuse or ask to paste it. Read `docs/AWS_HYDERABAD_SETUP.md`. Leave Bedrock offline until a real invocation succeeds.
