# Frontend correction round 2 — review record

Date: 24 October 2026. Scope: frontend corrections only; no scientific engine,
optimiser, authentication or AWS integration was added.

## Corrections delivered

- Replaced the locale-sensitive number widget with a dot-decimal budget editor.
  It has one stable border, no steppers or embedded framework hint, commits on
  Enter/blur, restores on Escape, blocks allocation when invalid, and converts
  crore to whole INR through `Decimal`.
- Replaced the intervention multiselect with four compact, stateful rows. Each
  row separates requested inclusion from unverified physical suitability and
  states synthetic resource/cost context.
- Moved the rail toggle into the brand header and removed mouse-click brand
  decoration while retaining keyboard `:focus-visible` treatment.
- Reflowed Investment and Shock content sequentially so short controls do not
  force empty equal-height columns. Removed invented environmental result charts.
- Removed raw scenario parameter/model-update and saved-contract JSON panels.
  Reproducibility data remains in typed contracts and exported snapshots.
- Replaced Evidence Lineage with a collapsed Sources & assumptions disclosure,
  and changed Declared priorities to a full-width six-value breakdown.
- Fixed the empty dark Shock box by removing redundant field-help chrome and
  narrowing multiselect CSS to actual combobox buttons.

## Executed verification

- `python -m pytest -q`: 60 passed.
- `scripts/round2_review.cjs`: 117 browser assertions, 50 screenshots, 17
  axe-core 4.14 WCAG A/AA scans, zero violations, zero JavaScript page errors.
- `scripts/round2_interactions.cjs`: 24 explicit interaction assertions and
  112 screenshots covering budget typing/paste/delete/validation/commit/revert,
  intervention selection, five review states, and top/middle/bottom layouts.
- Viewports: 320, 768, 1024, 1440 and 1920 px, in light and dark themes.
- Anti-Slop §9: 30/30 self-assessment checks under the guide's documented-rule-
  exception policy; overall 100/100, no category below 100. This is not an
  independent design review or formal WCAG certification.

## Scientific and integration limits

The UI still uses grade-D synthetic fixtures. Solver status remains `not_run`.
Physical eligibility, environmental outcomes, lifecycle economics, per-zone
benefits, feasible alternatives, shock reoptimisation and deterministic reasons
are blocked by the unimplemented backend or missing validated data. These are
listed requirement by requirement in `FRONTEND_REQUIREMENTS_AUDIT.md`; visible
controls without connected production behaviour are not marked PASS.

Local review URL: `http://127.0.0.1:8505` while the Streamlit process is running.
