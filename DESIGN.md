# C1V1C — design direction

## Direction
An urban planning desk for Bengaluru resilience analysts: precise, grounded, calm.
Archetype: tool/dashboard. A large editorial serif title and a ruled evidence ledger
deviate from the neutral dashboard to give civic decisions appropriate weight.
Anchor: survey drawings, municipal ledger paper and the deep green of Bengaluru's
tree canopy. Geography, units and source quality provide the visual identity.
Assumptions: no existing logo or font must be preserved; English is the initial
interface; analysts use desktop workstations but reviews must work on phones.

## Workflow and scope
Read AGENTS, the complete Anti-Slop guide, original PS DOCX, master Markdown and
checked its long text against the authoritative DOCX; supporting handoff, evidence,
data, AWS and acceptance documents were reviewed before code.
User's frontend-first request supersedes the repository's backend-first sequence.
User explicitly requests one approval gate after frontend testing, so the style
guide precedes pages in Git but is reviewed with them at Phase 3.
No backend, solver, scientific model or live cloud work belongs to this phase.

## Colors
| Human name | Token | Light | Dark | Role |
|---|---|---|---|---|
| Ledger paper | bg | #f4f1e9 | #151c19 | Main canvas, ~70% |
| Drawing sheet | surface | #fffdf7 | #202b25 | Controls and evidence |
| Survey ink | text | #202e28 | #f4f1e9 | Text |
| Pencil | muted | #526159 | #bbc9c0 | Secondary text |
| Rule | border | #78857b | #81958a | Boundaries |
| Canopy | accent | #245640 | #acd6b5 | Actions, <10% |
| Caution ink | warning | #79520b | #f0c477 | Evidence caveats |
| Correction ink | danger | #a13327 | #ffb4a6 | Errors |

## Typography
Georgia display: familiar printed-report authority, bundled system serif.
Trebuchet MS body: open humanist forms, intentionally chosen for dense planning
work; Arial fallback. Consolas for IDs and units. No network font dependency.
Scale: 12, 14, 16, 20, 26, 42px. Heading leading 1.15, tracking -0.025em;
body 1.65. Tabular numerals. Mobile body remains 16px.

## Geometry and motion
Spacing 4,8,12,16,24,32,48,64px. Radius 2/4/6px. One-pixel rules.
No shadows. Controls 44px minimum height. Motion only on focus/active state,
120ms; disabled with reduced motion. Split map/profile and ledger layouts,
not repeated feature-card grids. Mobile stacks controls and chart regions.

## Components
Primary/secondary/ghost buttons: default, hover, focus, active, disabled, loading.
Inputs: labelled, focus, invalid, disabled. Navigation: active text + border.
Evidence tags always include words. Flat metric strips, ruled tables, details
disclosures, status alerts, empty states and confirmation dialogs.
`ui/tokens.css` is the common source for the guide and Streamlit styling.

## Voice
Use: Inspect evidence, Preview allocation, Compare plans, Export decision brief.
Always say demonstration for fixtures; never call previews solver results.
Do not imply forecasts, ROI, measured wards or calibrated confidence intervals.

## Justified rule breaks
- Streamlit uses its native accessible widget typography where internal widget
  rendering cannot inherit the selected font; the shared theme selects the
  humanist face wherever the framework supports it.
- Data visualizations may use semantic warning/danger shades for ordered exposure
  and grayscale alternatives; these encode data, not competing brand accents.
- Standard Streamlit widget layout uses framework spacing internally; application
  CSS and guide use shared tokens rather than brittle overrides of private classes.
- Plotly's built-in chart tools use their standard compact targets; primary map
  selection has a separate 44px labelled selector and map navigation supports touch.

## Review boundary
All frontend workflows may exercise demonstration fixtures, never disguised
mathematical optimisation. Model-derived production outputs remain pending approval.
