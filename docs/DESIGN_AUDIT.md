# Anti-Slop §9 audit — frontend approval candidate

Self-review against the supplied 30-item rubric; not an independent design score.
Evidence: DESIGN.md, ui/tokens.css, style-guide.html, ui/views.py, browser screenshots
of all four sections, 320/375/768px viewport checks and measured contrast below.

## Overall score: 100/100

| Category | Passes | Score | Evidence |
|---|---|---|---|
| Colors | 5/5 | 100 | Canopy/ledger palette, flat controls; semantic data colors documented |
| Typography | 5/5 | 100 | Georgia headings, humanist body, 42/26 scale, 1.15/1.65 leading |
| Layout | 5/5 | 100 | Map/profile split, allocation ledger, scenario comparison, evidence disclosures |
| Copy | 5/5 | 100 | Specific controls, short introductions, visible demonstration status |
| Images & icons | 5/5 | 100 | Place-specific street map, no decorative imagery; native material controls |
| UX | 5/5 | 100 | Four-section navigation, folded detail, touch/focus rules, no entrance motion |

## Thirty checks
1. PASS — no purple gradient background; no gradients used for page decoration.
2. PASS — buttons and actions use flat fills.
3. PASS — neutral base plus green accent; brown is a semantic warning/data color.
4. PASS — no application box-shadow; only native overlay behaviour.
5. PASS — no alternating section background rhythm.
6. PASS — Trebuchet chosen for humanist legibility; no unexamined Inter/Roboto/Open Sans.
7. PASS — Georgia display differs from body family and weight.
8. PASS — 26 to 42px display jump, rather than uniform steps.
9. PASS — heading leading 1.15, body 1.65 in shared CSS.
10. PASS — heading tracking -0.025em.
11. PASS — no repeated three-column card grids.
12. PASS — maps, ledger, controls, bars and disclosures have different structures.
13. PASS — left-aligned body throughout.
14. PASS — token spacing distinguishes controls, evidence and major sections.
15. PASS — task-oriented first viewport; no marketing hero.
16. PASS — no guide-banned buzzwords in product copy.
17. PASS — no generic slogan template.
18. PASS — Preview allocation / Inspect / Export actions name their function.
19. PASS — headings identify investment, evidence, constraints or comparison.
20. PASS — section introductions are one sentence.
21. PASS — no emoji icons; material/native controls only.
22. PASS — street map actually depicts Yelahanka context; markers are labelled illustrative.
23. PASS — no reused decorative imagery across pages.
24. PASS — no AI-generated illustrations.
25. PASS — no blob/gradient image placeholders.
26. PASS — first viewport names urban sustainability, pilot context and review mode.
27. PASS — long sources, candidates, weights and uncertainty use disclosures/selectors.
28. PASS — no hidden entrance content; reduced-motion CSS disables animation.
29. PASS — primary controls and buttons use 44px minima; radio/checkbox full labels
    are targets. Chart internals retain the justified native exception in DESIGN.md;
    adjacent native controls provide an accessible alternative to marker inspection.
30. PASS — max two primary/secondary actions per content section; navigation,
    field inputs and explicit review-state controls are not competing CTAs.

## Accessibility and browser evidence
Contrast ratios computed with WCAG sRGB relative luminance:

| Pair | Ratio |
|---|---|
| Light text/background | 12.55:1 |
| Light muted/background | 5.79:1 |
| White/accent | 8.47:1 |
| Warning/background | 6.15:1 |
| Light boundary/background | 3.42:1 |
| Dark text/background | 15.35:1 |
| Dark muted/background | 10.09:1 |
| Dark accent foreground/background | 10.76:1 |
| Dark boundary/background | 5.44:1 |

Browser computed caption color: rgb(82,97,89). Export button height: 44px.
At 320, 375 and 768px, document body did not exceed viewport width. Data grids
retain internal scrolling. Focus outlines use a 3px canopy ring and 3px offset.
Map data can also be inspected by labelled profile/layer selectors and tables.

## Priority fixes completed
1. Caption styling was overridden by Streamlit: target caption paragraphs explicitly
   to restore 5.79:1 contrast; verified the browser computed color.
2. Fixed toolbar clipped the demonstration banner: added 80px toolbar-clearance
   token at desktop and mobile sizes; inspected final screenshots.
3. Compact native buttons: enforced 44px minimum size, with nonshrinking button
   layout; kept primary map controls outside Plotly's compact toolbar.

## Final self-critique
The map, evidence grades, INR budgeting, explicit unsupported metrics and shared
roof/water constraints make this recognisably an urban planning tool. No marketing
testimonials, invented adoption claims, ornamental imagery or empty feature cards.
The greatest remaining design risk is lengthy scientific caveats; disclosures keep
them close to decisions without making every section a warning wall. Backend
integration must retain the evidence hierarchy and replace fixtures, not hide it.
