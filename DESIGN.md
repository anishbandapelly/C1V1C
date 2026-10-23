# C1V1C — brand-led frontend system

## Direction
A calm, capable urban decision workspace for city planners, judges and analysts.
The supplied 24 October brand sheet is authoritative: water, canopy and city form
connect environmental choices without decorative technology imagery.
Archetype: tool/dashboard with an integrated orientation home, explicitly requested
by the user. Evolve the existing Streamlit app; preserve contracts and preview logic.

## Brand source
Original horizontal PNG files copied byte-for-byte to static/brand. Light logo on
Mist/white, white logo on Civic Ink/dark surfaces. Preserve the full 1406:620 aspect
ratio and all supplied transparent margins; no cropping, recoloring or recreated mark.
No separate small icon asset was supplied: the collapsed rail uses a labelled Home
icon, not a fabricated official symbol. Brand sheet is a visual reference, not an
instruction to change engineering scope. The PDF has one page and agrees with PNG.

## Palette and use
| Name | Official value | Role |
|---|---|---|
| Civic Ink | #12302F | Typography, dark identity |
| Canopy | #2E8B57 | Primary action, vegetation |
| Monsoon | #2A6FB5 | Links and water-related context |
| Mist | #F6F8F7 | Main light canvas |

Semantic colors and contrast-safe derivatives live in ui/palette.json, which
supplies both CSS tokens and Plotly colors. Light: Mist canvas, white working
surfaces, soft green-gray navigation. Dark: deep ink canvas, layered teal surfaces,
light green actions and pale blue links; it is not an inverted light palette.
Primary actions use a darker Canopy derivative for normal-size white-text contrast.
Brand accents occupy less than 10% of most workspaces. Status uses text plus color.

## Typography and geometry
Outfit Medium (500) body and Semibold (600) headings as specified in the brand sheet.
Self-hosted variable font from Google Fonts with OFL licence; no runtime font CDN.
14/16/20/28/40/64px scale, 1.15 heading and 1.65 paragraph leading, -.025em heading
tracking, tabular numbers. Main hero uses a responsive 40–64px title.
Spacing: 4/8/12/16/24/32/48/64. Radii: 4/8/12. One-pixel rules.
Navigation rail 260px expanded / 76px collapsed; main offset transitions with it.
Mobile below 800px uses an overlay drawer, backdrop, Escape dismissal and focus trap.
Motion 180ms ease-out for rail/offset only; reduced motion removes it.

## Components and interaction
Native Streamlit form controls retain meanings. Custom shell uses accessible buttons
and Lucide-style line SVGs (24px, 1.8 stroke) consistently. Active navigation has a
small line and restrained tint, hover/pressed/focus states and collapsed tooltips.
Brand button always returns Home. Account footer stays outside the scrollable nav.
Guest profile is explicit; no login, fake name or unsupported sign-out control.
Theme choices: System / Light / Dark; localStorage persists preference and compact
rail state. Browser system theme governs the initial visit; storage failures fall
back to memory. Theme bootstrap occurs before module content; browser tests verify.

## Information architecture
| Screen | Decision / first focus | Secondary disclosure |
|---|---|---|
| Home | Where should I begin? Four connected planning steps | Preview scope |
| City | What differs between zones? Map + selected profile | Sources, candidate capacities, method |
| Investment | What can this budget include? Inputs + cost ledger | Weights, equity floor, review states |
| Shock | What happens if conditions change? Original plan and stress inputs | Parameter record, layout-only examples |
| Decision | What supports this choice? Selection, distribution and export | Full contract, assumptions, alternatives |

Before analysis, show the task, input checklist, existing synthetic catalogue or
comparison structure and a next action. No empty result panel masquerades as a run.
After analysis, retain inputs and give the ledger greater width. Each chart states
its unit, purpose and evidence status. Provenance stays visible, details fold away.

## Voice
Say Explore the pilot, Preview allocation, Compare scenarios, Export review brief.
No claims of actual AI results while the solver is absent. Brief demonstration banner
plus nearby relevant caveats replaces repeated long warning paragraphs.

## Justified deviations
- Two official accents are retained because the user's authoritative brand specifies
  both Canopy and Monsoon; their action and water/link roles are distinct.
- The official logo contains gradients; supplied artwork is preserved, while no
  gradient is added to page backgrounds, text or buttons.
- The logo repeats in navigation and home because consistent official branding is
  explicitly requested; decorative content imagery is not repeated.
- An orientation hero is appropriate because the user requests a home explaining the
  sustainability paradox; it is not a full-screen marketing template.
- Existing Streamlit/Plotly native icons remain framework-owned; custom navigation
  uses one line icon vocabulary. Native chart tools have adjacent accessible inputs.
- The supplied brand typography overrides the earlier Georgia/Trebuchet assumption.

## Approval and constraints
The requested review after implementation overrides intermediate style-guide approval.
Design/tokens/style guide are updated before application changes. Full backend,
modelling, AWS and authentication remain outside this correction stage.
