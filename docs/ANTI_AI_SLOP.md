---
name: anti-slop-design
description: Design guardrails for any web build (site, app, dashboard, store, docs). Use before writing UI code, when redesigning, and as a final audit. Forces a deliberate direction and a token system first, bans on-distribution AI defaults, and ends with a scored 30-point slop check.
---

# Anti-Slop Design Guide

> Drop this file in your project root (or in your agent's skills/rules folder) and tell the agent: **"Follow anti-slop-design.md for all UI work."**
>
> This file does not dictate a look. It dictates a **process** and a set of **banned defaults**. The agent picks the aesthetic based on what's being built, then has to justify it, lock it into tokens, and pass an audit before shipping.

---

## 0. The core idea

AI-generated UI looks generic for one reason: when nothing is decided, the model fills every blank with the most statistically common choice. Inter. Purple gradient. Three cards. "Unlock your potential."

So the rule is: **nothing gets left blank.** Every visual decision is made on purpose, written down once, and reused everywhere.

Three laws:

1. **Direction before code.** No component is written until a design direction exists.
2. **Tokens before pages.** Every color, size, radius, and spacing value comes from a token. No one-off values in page code.
3. **Audit before ship.** Every output passes the slop check in §9. If it fails, fix it before showing it.

Any rule below can be broken **if the agent states the reason in one sentence** (e.g. "Using Inter because the client's existing brand mandates it"). Breaking a rule silently is the actual failure.

---

## 1. Phase 1 — Direction (ask, don't assume)

Before building, the agent gathers or infers answers to these. If the user is present and the answer isn't obvious from context, **ask** (max 4–5 questions, batched). If working unattended, infer the most reasonable answer and **write the assumption down** at the top of `DESIGN.md`.

| Question | Why it matters |
|---|---|
| What is this, and who uses it? (product type, audience) | Decides archetype (§2) |
| What should it *feel* like to that person? Pick 2–3 adjectives (e.g. "calm, premium, exact" / "loud, playful, scrappy") | Drives type, color, density |
| What already exists and must stay? (logo, brand colors, fonts, copy, existing site) | Prevents reinventing what's decided |
| How far to move from what exists? Evolve / reinvent / evolve + one bold alternative | Sets risk level |
| Any references they like (URLs, screenshots, a physical object, a material)? | Real taste input beats model defaults |

**Find a source of truth outside the screen.** The best brands get their palette and texture from something real: the product's materials, the founder's workshop, a place, a printed artifact, an industry's visual history. If nothing like that is given, the agent proposes one concrete anchor ("Palette pulled from aged ledger paper and stamp ink, because this is an accounting tool for small shops") instead of choosing colors from nowhere.

Output of Phase 1: a short **Direction Statement** (3–5 lines) at the top of `DESIGN.md`.

---

## 2. Pick an archetype, then deviate deliberately

Different things need different defaults. Identify the archetype first; it sets the *starting* posture, not the final look.

| Archetype | Density | Type posture | Color posture | Layout posture |
|---|---|---|---|---|
| **Tool / dashboard / app** | High, scannable | Quiet, highly legible UI sans; tabular numbers; mono for data/IDs | Mostly neutral; accent reserved for state and primary action | Sidebar/top-bar shells, tables, split panes; no hero |
| **Marketing / product site** | Medium, rhythmic | Distinct display face for headings + readable body | One brand color with confidence; neutrals carry the page | Varied section structures; one real hero tied to the product |
| **Editorial / blog / docs** | Low, long-form | Serif or strong text face for reading; 60–75ch measure | Restrained, near-monochrome | Single column, generous margins, strong typographic hierarchy |
| **Commerce / store** | Medium–high | Brand display + clean body; prices legible | Brand colors from the product itself | Product imagery leads; grids are fine here, but vary card states |
| **Portfolio / studio / brand** | Low–medium | Expressive; type can *be* the visual | Can be bold or austere, but intentional | Asymmetry, large type, whitespace, work-first |
| **Internal / admin / form-heavy** | High | System-like, clear | Neutral + semantic colors (success/warn/error) | Function over flair; fast, obvious, accessible |

The agent writes in `DESIGN.md`: *"Archetype: X. Deviating from its defaults in these ways: … because …"*

---

## 3. Phase 2 — Tokens (the style guide comes first)

Build the design system **before** any page. All page code references tokens; if a needed value doesn't exist, add it to the tokens, never inline it.

### Minimum token set

```css
:root {
  /* Color: name them by meaning, not by hue */
  --color-bg:        ;
  --color-surface:   ;   /* only if genuinely different from bg */
  --color-text:      ;
  --color-text-muted:;
  --color-border:    ;
  --color-accent:    ;   /* ONE accent */
  --color-accent-fg: ;   /* text on accent, contrast-checked */
  --color-success:   ;   /* semantic colors only if the product needs them */
  --color-warning:   ;
  --color-danger:    ;

  /* Type */
  --font-display: ;      /* headings */
  --font-body:    ;
  --font-mono:    ;      /* only if there's code/data */
  --text-xs … --text-display ;   /* a scale with a real jump at the top */
  --leading-tight: 1.1;   /* headings 1.1–1.3 */
  --leading-body:  1.65;  /* body 1.6–1.8 */
  --tracking-display: -0.02em;

  /* Space: a scale, not arbitrary numbers */
  --space-1 … --space-10 ;

  /* Shape */
  --radius-sm: ; --radius-md: ; --radius-lg: ;   /* or all 0 — decide */
  --border-width: 1px;

  /* Elevation: decide if the system uses shadows at all */
  --shadow-overlay: ;    /* menus/modals only, if any */

  /* Motion */
  --ease-out: ;
  --duration-fast: 120ms;
  --duration-base: 200ms;
}

/* Dark mode is a token remap, not a redesign */
@media (prefers-color-scheme: dark) { :root { /* remap color tokens */ } }
```

Give brand colors **human names** in `DESIGN.md` (e.g. "Canola Yellow", "Hockey Puck Black") with a note on where each came from and how much of it to use. Named colors with a story get used deliberately; `#6366f1` gets used everywhere.

### Components to define before pages
Buttons (primary / secondary / ghost, all states incl. disabled + loading), inputs (default / focus / error / disabled), cards (if used at all), nav, links, badges/tags, tables (if data), empty states, error states, toasts/alerts, modals. Document each in the style guide page with its tokens.

### Deliverable
A single `style-guide.html` that renders every token and component in light and dark, plus one sample section using **real copy**. The user approves this before pages are built. Changing the look later = edit tokens, not pages.

---

## 4. Banned defaults (the AI tells)

These are banned **unless justified in one sentence in `DESIGN.md`**.

### Color
- ❌ Purple→blue (or any purple/indigo/violet) gradient backgrounds — the #1 tell
- ❌ Gradient buttons, gradient text on headlines
- ❌ Indigo/violet (`#6366f1`, `#8b5cf6` family) as the accent "because it looks modern"
- ❌ Box-shadow on everything; soft glow shadows on cards
- ❌ Alternating section backgrounds (`#f5f5f5` / white / `#f5f5f5`) as a rhythm device
- ❌ More than one accent; 5+ colors competing
- ❌ Glassmorphism / blurred blobs / mesh-gradient hero backgrounds as decoration

**Do instead:** One base, neutrals, one accent. Flat buttons with a clear hover/active state. Borders (1px, low-contrast) before shadows. Change section background only when the content genuinely changes.

### Typography
- ❌ Inter, Roboto, Open Sans, or system default as the *unexamined* choice
- ❌ One family at one weight for everything
- ❌ Uniform size steps (16 → 24 → 32 → 40) with no drama at the top
- ❌ `line-height: 1.5` on everything
- ❌ Default letter-spacing on large headings
- ❌ ALL-CAPS tiny eyebrow label above every section heading

**Do instead:**
- Choose type by the adjectives from Phase 1, not from a favorites list. **Do not treat any recommended font as the new default** — DM Sans, Plus Jakarta Sans, Geist, Sora etc. are already becoming the next generation of AI defaults. Consider the whole range: serifs (editorial trust), grotesks (neutral precision), humanist sans (warmth), monos (technical), display faces (personality).
- Pair a heading face and a body face, or one family with deliberately different weights/width/tracking.
- Make the display size dramatically larger than h2 — a jump, not a step.
- Headings: leading 1.1–1.3, tracking around −0.01 to −0.03em. Body: leading 1.6–1.8, measure 60–75 characters.
- Use `font-variant-numeric: tabular-nums` for numbers in tables, prices, and stats.
- For non-Latin scripts, choose a proper family for that script (e.g. Noto Sans JP / BIZ UDGothic for Japanese, Noto Sans Devanagari / Mukta for Hindi) and set its line-height separately.

### Layout
- ❌ Hero → 3 feature cards → 3 testimonial cards → 3 pricing cards → CTA (the SaaS template)
- ❌ Three-column icon-card grid repeated in 3+ sections
- ❌ Every section built as heading → subtitle → cards
- ❌ Everything centered
- ❌ Identical padding on every section
- ❌ Full-screen hero + huge headline + two CTA buttons, regardless of content
- ❌ Cards nested in cards

**Do instead:** Mix single-column, split (text + visual), lists, tables, timelines, and full-bleed media. Left-align body text; center only short hero lines or single statements. Vary spacing to show relationships: tight within a group, loose between groups, extra-loose before the most important section. Size the hero to what you actually have to say — a tool may need no hero at all.

### Copy & microcopy
- ❌ Buzzwords: unlock, empower, seamless, leverage, streamline, robust, cutting-edge, elevate, harness, delve, revolutionize, supercharge, next-level, game-changing, effortless, "in today's fast-paced world"
- ❌ Japanese tell: 「〜を、もっと〜に」 and similar slogan templates in any language
- ❌ "Learn more", "Get started", "Click here" as the only CTAs
- ❌ Section headings like "Features", "Solutions", "Benefits", "Why choose us"
- ❌ Multi-sentence subtitles under every heading
- ❌ Fake testimonials, fake logos ("Trusted by 10,000+ teams"), invented stats

**Do instead:** Concrete verbs (calculate, compare, track, find, book, export). Specific CTAs ("Compare 3 plans", "Estimate your trip cost"). Headings that say what's there ("What you can track", "How refunds work"). Subtitle: one sentence max. Use the user's real copy; if none exists, write plain specific placeholder copy and mark it `[DRAFT]` — never fabricated proof.

### Images & icons
- ❌ Emoji as icons (🚀 💡 ✨ ⚡)
- ❌ Stock photos chosen by keyword rather than meaning
- ❌ The same image reused across sections/pages
- ❌ AI illustrations with visible artifacts (hands, text, melted details)
- ❌ Gradient/blob placeholder boxes standing in for missing images
- ❌ Generic "3D isometric illustration of people at laptops"

**Do instead:** One consistent SVG icon set (Lucide, Phosphor, Heroicons, Tabler — pick one, one stroke weight). Every image must show *this* product/place/thing. No real image? Design the layout without one — let type, color, and real data carry it. Real product screenshots, real photos, or a simple diagram beat decoration every time.

### UX & interaction
- ❌ Fade-in/slide-up scroll animation on every element
- ❌ Content invisible until JS runs (opacity: 0 by default)
- ❌ 50+ items dumped at once
- ❌ 3+ CTA buttons in one section
- ❌ Hover effects that lift/scale every card
- ❌ Tiny tap targets

**Do instead:** Motion only where it explains something (state change, spatial relationship, feedback); respect `prefers-reduced-motion`; content visible without JS. Show 6–9 items, then "Show more" / pagination / filters. Max 2 CTAs per section (one primary, one secondary). Touch targets ≥ 44×44px. The first viewport must say what this is and what you can do here.

---

## 5. Things that make work look *human-directed*

Slop avoidance is half the job. These add the other half — choose a few that fit, not all:

- **A point of view.** One unexpected but justified decision (an oversized serif, a strict monochrome palette with one hot color, a dense data-first homepage, a hand-drawn rule, a grid borrowed from a physical object).
- **Real content in the design.** Actual product UI, actual numbers, actual names. Designing around real content forces non-generic layouts.
- **Asymmetry with intent.** Uneven columns, offset images, a strong left edge.
- **Typographic hierarchy doing the work** instead of boxes and shadows.
- **Consistent small details:** one radius system, one border weight, one icon stroke, aligned baselines, consistent focus rings.
- **Designed edge states:** empty, loading, error, sold-out, zero-results, long names, missing images. AI skips these; humans ship them.
- **Restraint.** Removing an element is often the best fix.

---

## 6. Accessibility floor (non-negotiable)

- Text contrast ≥ 4.5:1 (≥ 3:1 for large text and UI boundaries). Check accent-on-bg and text-on-accent.
- Visible `:focus-visible` style on every interactive element.
- Semantic HTML: real `<button>`, `<a>`, `<nav>`, `<main>`, headings in order, labels on inputs.
- Color is never the only signal for state.
- `alt` text that describes meaning; empty `alt=""` for decorative images.
- `prefers-reduced-motion` respected.
- Works at 320px wide with no horizontal scroll; 16px+ base text on mobile.

---

## 7. Workflow summary

```
1. Direction  → ask/infer, write Direction Statement + archetype in DESIGN.md
2. Tokens     → define tokens + components, render style-guide.html, get approval
3. Build      → pages use tokens only; no new raw values
4. Self-critique → before showing output, run §9 and fix every FAIL
5. Iterate    → change the look by editing tokens, never by patching pages
```

When the user asks to "make it look less AI", don't patch the page. Go back to step 1 or 2.

---

## 8. Project `DESIGN.md` template

The agent creates/maintains this file for each project. It is the single source of truth.

```markdown
# DESIGN.md — [Project name]

## Direction
- What: [product + audience]
- Feel: [2–3 adjectives]
- Archetype: [from §2] — deviations: [what + why]
- Anchor: [the real-world source of palette/texture]
- Assumptions made without asking: [list, or "none"]

## Colors
| Name | Token | Value | Use | Share of page |
|---|---|---|---|---|
| [Human name] | --color-bg | #… | page background | ~70% |
| … | --color-accent | #… | primary actions, key highlights only | <10% |

## Typography
- Display: [font] — why: …
- Body: [font] — why: …
- Scale: [list], leading, tracking

## Spacing, radius, borders, elevation
[values + rules, e.g. "No shadows except overlays"]

## Components
[list with states]

## Voice
- Say: [examples of real CTAs/headings]
- Don't say: [banned phrases for this brand]

## Do / Don't
- Do: …
- Don't: …

## Justified rule breaks
- [Rule] — [one-sentence reason]
```

---

## 9. Slop check (run before every delivery)

Score each item PASS / FAIL. Category score = passed ÷ 5 × 100. Overall = average of the 6.
**Ship threshold: overall ≥ 85 and no category below 60.** Otherwise fix and re-run.
A justified rule break (recorded in `DESIGN.md`) counts as PASS.

### 1. Colors
- [ ] No purple-to-blue (or purple/violet) gradient backgrounds
- [ ] No gradient buttons or CTAs
- [ ] Max 3 colors: base + grayscale + 1 accent (semantic state colors excepted)
- [ ] Box-shadow on no more than 2 element types
- [ ] No alternating section background pattern

### 2. Typography
- [ ] Primary font is not Inter / Roboto / Open Sans (unexamined)
- [ ] Headings and body differ (family, weight, width or tracking)
- [ ] Clear size jump at the top of the scale, not uniform increments
- [ ] Heading leading 1.1–1.3, body leading 1.6–1.8
- [ ] Intentional tracking on large headings

### 3. Layout
- [ ] No 3+ sections with identical 3-column card grids
- [ ] Sections use visibly different structures
- [ ] Body text left-aligned; centering used sparingly
- [ ] Spacing varies to show grouping and importance
- [ ] Hero fits the content (not the default full-screen + headline + 2 CTAs)

### 4. Copy
- [ ] No buzzwords from §4
- [ ] No slogan templates (incl. 「〜を、もっと〜に」)
- [ ] CTAs are specific actions
- [ ] Section headings are concrete
- [ ] Subtitles ≤ 1 sentence

### 5. Images & icons
- [ ] No emoji as icons
- [ ] Every image matches its content
- [ ] No image reused across sections/pages
- [ ] No AI illustrations with artifacts
- [ ] No gradient/blob placeholders for missing images

### 6. UX
- [ ] First viewport states what this is and what to do
- [ ] Long content folded (show more / tabs / accordion / pagination)
- [ ] Animations never hide content; reduced-motion respected
- [ ] Touch targets ≥ 44px
- [ ] Max 2 CTAs per section

### Report format

```markdown
### Overall Score: X/100

| Category | Score | Issues |
|---|---|---|
| Colors | X/100 | … |
| Typography | X/100 | … |
| Layout | X/100 | … |
| Copy | X/100 | … |
| Images & Icons | X/100 | … |
| UX | X/100 | … |

### Top 3 priority fixes
1. [fix + exact instruction, e.g. "Replace --color-accent #7c3aed with the brand's terracotta #C2562F; remove gradient on .btn-primary"]
2. …
3. …

### What's already good
- …
```

### Final self-critique (one pass, after the checklist)
Ask honestly:
1. If I removed the logo, could this be any company's site? If yes, what one decision would make it unmistakably *this* one?
2. Is there anything here only because "sites usually have it"? Remove it.
3. Does every color, font, and image trace back to the Direction Statement?
4. Would a designer screenshot this as an example of AI slop? Which element would they circle first? Fix that element.
