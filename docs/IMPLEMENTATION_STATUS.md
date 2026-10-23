# Implementation status — handoff revision 2

**Only the planning scaffold, synthetic fixtures, preflight and reference tests have been prepared. Core functionality has NOT been built.** Status must be updated by implementers with test commands, actual pass/fail evidence, and commit references.

| Module | Current status | Proven evidence | Next owner task |
| --- | --- | --- | --- |
| Data Engine | NOT IMPLEMENTED | Synthetic fixture files + blank templates + provenance guidance | Typed contracts, source validation, verified/mixed data handling |
| AI Optimisation | NOT IMPLEMENTED | Tiny brute-force reference test only | MILP, site feasibility, objective coefficients, portfolio evaluation |
| Interactive Dashboard | NOT IMPLEMENTED | No application UI | Four tabs with real results; follow `anti-slop-design.md` workflow; audit §9 |
| Scenario Simulator | NOT IMPLEMENTED | Synthetic scenario multipliers only | Three shocks, frozen-plan stress and reoptimised run |
| Decision Explainer | NOT IMPLEMENTED | Research/source register only | Deterministic decision trace and uncertainty; Bedrock optional |
| AWS S3/Bedrock | NOT CONNECTED | Config/runbook only; no auth checked | AWS permissions & tested adapters with fallbacks |
| Real pilot data | NOT VERIFIED | Source leads only; synthetic fixtures | Actual geometry, baseline, costs and traceable coefficients |
| User Anti-Slop design guide | PROVIDED — UI AUDIT PENDING | Exact uploaded `anti-slop-design.md` at root and mirrored in docs | Codex creates `DESIGN.md` + `style-guide.html`, then documents §9 scoring before UI review |
| GitHub remote | NOT VERIFIED | Local Git history only | Create/link repository and push current main |
| Bootstrap tests | PARTIAL — scaffold only | Reference fixture + handoff integrity pytest | Add module/integration/solver tests in actual code |

**Do not advertise this repository as a working urban sustainability application.**
