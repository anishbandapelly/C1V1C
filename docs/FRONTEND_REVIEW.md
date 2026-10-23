# Frontend approval build — 23 October 2026

## Scope and review gate
Phases 1–3 only. The user explicitly requires frontend approval before full backend
implementation. This supersedes the master plan's original engineering build order
and the design guide's intermediate style-guide approval pause.

Python/Streamlit/Plotly retained. No React replacement, external API, optimiser,
physical model or AWS operation has been introduced. Python 3.12.14 was used because
the installed default is experimental 3.15; the dependency lock records the tested
3.12 environment. The master prefers 3.11 but permits other versions after testing.

## Run and inspect
From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
.venv\Scripts\python.exe -m pytest -q
```

1. City Intelligence: select all six layers, pan/zoom the map, switch A/B/C profiles,
   inspect candidates and the source register; turn street tiles off for offline use.
2. Investment Optimiser: set budget and priorities, inspect weights, filter types,
   select a display portfolio, then Preview allocation. Try a budget of 0.1 crore,
   invalid weight totals, a nonzero equity floor and each explicit review state.
3. Climate Shock Lab: after a preview, inspect all three disruptions, adjust factors,
   freeze commitments and submit the comparison. The saved original IDs stay fixed.
4. Decision Intelligence: select a saved preview, inspect included/excluded projects,
   distribution, sources, uncertainties and JSON/Markdown exports.

## Demonstration boundary
- A/B/C profiles and intervention costs originate in master-plan synthetic fixtures.
- Approximate WGS84 display markers provide Yelahanka context, not measured zone
  geometry. Street tiles are CARTO/OpenStreetMap and require network connectivity.
- Benefits in explicitly labelled comparison specimens are invented frontend values.
  They do not react to climate factors and do not represent physical calculations.
- Only arithmetic UI checks (sum of fixture costs, remaining budget, spend per
  synthetic resident, revised budget envelope) are calculated in this phase.
- Portfolio presets are manually selected fixtures, never a ranking or fake solver.
- Changed inputs display stale-result warnings; filters withhold unrelated outcome
  specimens. Nonzero equity floors are blocked because they cannot yet be verified.
- Carbon and lifecycle cost remain not estimated. Unverified eligibility never becomes
  a claim of physical feasibility. No precise temperature or flood-depth claims.
- Preview snapshots are session-only, content-addressed and exportable. They are not
  production immutable RunResults or a durable saved-run service.
- AWS and Bedrock are not connected. No live cloud credentials were inspected.

## Backend handoff
`ui/contracts.py` defines Indicator, CandidateProject, ScenarioRequest, RunResult,
DecisionExplanation and EnginePort. `PreviewSnapshot` is intentionally separate.
After approval, implement the master interfaces behind EnginePort, replace the
fixture adapter and presentation specimens, add validated data/units/provenance,
real PuLP/CBC and independent portfolio evaluation, immutable run storage and
genuine scenario computations. Preserve approved visual structure and controls.

Pending acceptance: every engine/data/scientific/AWS/deployment P0 remains pending.
Frontend test passes must never be reported as proof those modules work.

## Verification
- `python -m pytest -q`: 33 passing tests (16 original handoff/fixture tests and
  17 frontend tests). Includes all pages, zero budget, invalid weights, unsupported
  equity floor, insufficient budget, intervention filter honesty, stale snapshots,
  explicit failure/loading states, profile selection and all shock records.
- `scripts/browser_review.cjs`: real Microsoft Edge/Chromium navigation through
  all sections, preview submission, shock submission and actual JSON download.
  No JavaScript page errors. Measured viewport/body widths 320/320, 375/375,
  768/768. Primary export target height 44px. Screenshots inspected.
- The script uses Playwright from `C1V1C_NODE_MODULES`; set that variable to the
  node_modules directory containing Playwright. Edge must be installed, or change
  the browser channel to an installed Chromium distribution.
- Style guide: 84 rendered token entries across both themes; semantic controls,
  validation, disabled/loading, source disclosure and native dialog specimens.
- Manual audit and contrast measurements: `docs/DESIGN_AUDIT.md`.

## Known frontend limits
Map keyboard users select the same profile through the adjacent labelled selector;
the markers have hover information but do not select a profile. Mobile tables may
scroll within their containers. Native Streamlit/Plotly controls retain framework
behaviour; this is not a formal screen-reader or WCAG certification. A verified
boundary layer and site-level geometry must be added after the data validation gate.

Approval requested for visual direction, navigation and interaction flow only.
