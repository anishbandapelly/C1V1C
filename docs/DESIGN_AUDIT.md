# Anti-Slop §9 audit — brand redesign, 24 October 2026

Self-assessment against all 30 checks, not an independent design rating or accessibility certification. Justified exceptions count as passes under the supplied rubric.

## Overall: 100/100

| Category | Passes | Score |
|---|---|---|
| Colors | 5/5 | 100 |
| Typography | 5/5 | 100 |
| Layout | 5/5 | 100 |
| Copy | 5/5 | 100 |
| Images & icons | 5/5 | 100 |
| UX | 5/5 | 100 |

## Complete checklist

### Colors

1. PASS — No purple gradient backgrounds; surfaces are flat Civic Ink and Mist derivatives.
2. PASS — Flat action fills; official logo gradient preserved as documented.
3. PASS — Two official brand accents: justified exception in DESIGN.md.
4. PASS — No decorative application shadows; overlay boundaries use borders.
5. PASS — No alternating background section rhythm.

### Typography

6. PASS — Self-hosted official Outfit; no unexamined default font.
7. PASS — Semibold tightly tracked headings differ from medium body text.
8. PASS — Display scale jumps 28/40/64 rather than uniform increments.
9. PASS — Heading leading 1.15; body 1.65, with compact labels intentionally separate.
10. PASS — Display tracking is an explicit token.

### Layout

11. PASS — No repeated three-column card grids.
12. PASS — Home comparison board, city map, allocation ledger and evidence disclosures differ.
13. PASS — Body copy is left aligned.
14. PASS — Token spacing expresses grouping and importance.
15. PASS — Home explains the planning paradox and links into the application; requested hero exception documented.

### Copy

16. PASS — No guide-banned marketing buzzwords in application copy.
17. PASS — Hero states a planning trade-off; supplied official brand tagline retained.
18. PASS — Explore, preview, compare and export actions describe their result.
19. PASS — Page headings ask the decision each screen supports.
20. PASS — Page subtitles are concise single sentences; explanatory body copy is separate.

### Images & icons

21. PASS — Consistent line navigation icons; no emoji.
22. PASS — Official supplied logos and place-specific map match their purpose.
23. PASS — Repeated official logo is an explicit branding exception; no reused decorative imagery.
24. PASS — No generated illustrations.
25. PASS — No blob or gradient image placeholders.

### UX

26. PASS — Home identifies urban sustainability and provides workflow entry points.
27. PASS — Sources, constraints and technical detail use disclosures.
28. PASS — Only navigation transitions; reduced-motion disables them.
29. PASS — 44px controls; native chart toolbar exception has adjacent accessible controls.
30. PASS — At most two actions per content section; navigation and inputs are distinct.

## Priority fixes completed
1. Replaced the rigid native navigation with a responsive, independently scrolling rail, mobile drawer, focus handling and honest Guest profile.
2. Added purposeful pre-analysis guidance and responsive layout proportions instead of empty result panels.
3. Corrected native dark-theme multiselect, slider-value and expanded-disclosure contrast after rendered browser checks.

## Evidence and limits
Brand direction and exceptions: DESIGN.md. Tokens: ui/palette.json and ui/tokens.css. Working specimens: style-guide.html. Browser script: scripts/redesign_review.cjs; machine-readable results and screenshots are supplied with the review. Tests cover both initial and populated states in both themes, 320/375/768/1024/1280/1440px viewports, persistence, keyboard drawer behaviour, exports and reduced motion. Palette contrast assertions are executed in pytest.

Automated accessibility checks cannot evaluate every chart feature. Axe incomplete checks require human review; map profiles and semantic tables provide alternatives to chart interaction. No formal assistive-technology certification is claimed. Official logo artwork is unmodified, including its embedded tagline.

## Final self-critique
The work now reads as a single civic planning application: the home introduces competing priorities, the map explains where to inspect, and pre-analysis pages explain what a preview can and cannot establish. Guest and demonstration labels remain explicit. Long scientific caveats remain a comprehension risk; they are grouped near relevant decisions. Review with actual planners and screen-reader users remains valuable. The scientific engine and production deployment remain pending approval.

## Correction round 2 — audit rerun

The same 30-item checklist above was reviewed against this correction. All six categories remain 5/5 (100/100 self-assessment), with the previously documented official-brand exceptions. New checks: budget uses one border/focus ring and dot-decimal text editing; interventions use selected/excluded text in addition to checkmarks; full-width sequential results replace unequal columns; standalone raw state and static environmental specimens are removed; priorities are a concise table; sources are a disclosure. Headings use h2 below page h1. Native chart controls retain the accessible-control exception.

Priority corrections: (1) exact, locale-independent budget input with no native stepper chrome; (2) remove misleading and developer-facing content while retaining saved metadata/export; (3) reduce wasted columns and keep sidebar toggle inside its header. The budget component sizes to its content so mobile validation text is not clipped. New test evidence and screenshots are recorded in FRONTEND_ROUND2_REVIEW.md. No claim of independent design review or full WCAG certification is made.
