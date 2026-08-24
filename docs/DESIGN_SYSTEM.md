# Resumind Design System (Phase 11)

Source of truth for all future UI work. Tokens live in
`Frontend/src/styles/tokens.css`; components live in
`Frontend/src/components/design-system/`. A living showcase of every
component is at the `/design-system` route (`Frontend/src/Pages/DesignSystemPage.jsx`).

Do not hard-code colors, font sizes, spacing, radii, or shadows in a
component — reference the tokens below (as a Tailwind utility, e.g.
`bg-surface`, or as `var(--color-surface)` in raw CSS/inline styles).

## 1. Color palette

| Token | Light | Dark | Usage |
|---|---|---|---|
| `--color-primary` | `#4F46E5` | same | Primary actions, active nav, brand accents |
| `--color-secondary` | `#0F172A` | same | Secondary buttons, dark emphasis |
| `--color-accent` | `#0F9D9A` | same | Sparing highlights, distinct from primary |
| `--color-background` | `#F8FAFC` | `#0B1120` | Page background |
| `--color-surface` | `#FFFFFF` | `#111827` | Card/panel background |
| `--color-surface-muted` | `#F1F5F9` | `#1E293B` | Subtle secondary surfaces |
| `--color-border` | `#E2E8F0` | `#263143` | Default border |
| `--color-border-strong` | `#CBD5E1` | `#334155` | Emphasized border |
| `--color-border-subtle` | `#F1F5F9` | `#1E293B` | Divider |
| `--color-text-primary` | `#0F172A` | `#F1F5F9` | Primary text |
| `--color-text-secondary` | `#475569` | `#94A3B8` | Supporting text |
| `--color-text-muted` | `#94A3B8` | `#64748B` | Metadata/placeholder |
| `--color-text-inverse` | `#FFFFFF` | `#0F172A` | Text on colored/dark surfaces |

Semantic: `--color-success` `#16A34A`, `--color-warning` `#D97706`,
`--color-error` `#DC2626`, `--color-info` `#2563EB` — each with a
`-surface` companion (light tint background) for banners/badges.

ATS match-strength scale — a **distinct** token set from the semantic
colors above, since e.g. PARTIAL is not the same concept as WARNING, and
UNKNOWN is deliberately neutral grey (never framed as negative, matching
Phase 10's "MISSING ≠ UNKNOWN" rule):

`--color-match-very-strong` `#16A34A` → `--color-match-strong` `#65A30D`
→ `--color-match-partial` `#D97706` → `--color-match-weak` `#EA580C`
→ `--color-match-missing` `#DC2626`, and `--color-match-unknown` `#64748B`
(neutral, off the red-green spectrum). Each has a `-surface` companion.

Resume Quality reuses this same semantic/match system rather than
inventing a third color language.

## 2. Typography

Font family: **Inter** (Google Fonts, weights 400/500/600/700), with a
system-font fallback stack. Numeric/score values use `tabular-nums` for
alignment rather than a second font family.

| Token | Size | Typical weight |
|---|---|---|
| `text-display` | 48px | 700 |
| `text-h1` | 36px | 700 |
| `text-h2` | 28px | 600 |
| `text-h3` | 22px | 600 |
| `text-h4` | 18px | 600 |
| `text-body-lg` | 16px | 400 |
| `text-body` | 14px | 400 |
| `text-body-sm` | 13px | 400 |
| `text-caption` | 12px | 500 |
| `text-label` | 13px | 600, uppercase, tracked |
| `text-score-lg/md/sm` | 40/28/20px | 700, tabular-nums |

Font weights: `font-normal` (400), `font-medium` (500), `font-semibold`
(600), `font-bold` (700) — Tailwind's built-in utilities, used
intentionally (score numbers are bolder than their captions).

## 3. Spacing

Mirrors Tailwind's default 4px scale exactly — `p-1`(4) `p-2`(8) `p-3`(12)
`p-4`(16) `p-5`(20) `p-6`(24) `p-8`(32) `p-10`(40) `p-12`(48) `p-16`(64).
No arbitrary spacing values in new components.

## 4. Radius

`rounded-sm` 6px · `rounded-md` 10px (default for cards/inputs/buttons)
· `rounded-lg` 16px (larger surfaces) · `rounded-full` pill/circular.

## 5. Shadows

`shadow-none` · `shadow-subtle` (default card elevation) · `shadow-medium`
(hover/focus elevation) · `shadow-elevated` (modals/popovers, used
sparingly). Cards default to `subtle`, never heavy floating-card shadows.

## 6. Borders

`border-border` (default), `border-border-strong` (emphasized, e.g. a
focused input's static border), `border-border-subtle` (dividers).

## 7. Score visualization

`ScoreRing`, `ScoreBar`, `ScoreBadge` (in `components/design-system/score/`)
all read from the same `getScoreState(score)` helper
(`score/scoreStates.js`), so the same numeric score looks identical
everywhere it appears. `ScoreCard` (in `cards/`) pairs a `ScoreRing` with
a title + one-line description, so ATS Alignment ("How well you match
this job"), Resume Quality ("How strong your resume structure and
evidence are"), and Target Fit ("How well your resume fits your selected
career target") stay visually distinct in meaning while sharing identical
visual language.

**Presentation states are separate from scoring logic.** `scoreStates.js`
defines the 90-100/75-89/60-74/40-59/0-39 display buckets from spec §15 —
this is a frontend-only concept. It must never be imported into or
influence `Backend/fastapi_app/app/modules/scoring/config.py` or any
other backend scoring/config module, and vice versa.

Per-requirement match status (`VERY_STRONG`/`STRONG`/`PARTIAL`/`WEAK`/
`MISSING`/`UNKNOWN`, from the backend's `MatchStrength` enum) uses a
separate mapping, `getMatchStrengthDisplay(status)`, since a discrete
status label isn't a percentage to bucket.

## 8. Cards

`BaseCard` is the single foundation (padding, border, radius, shadow,
optional hover elevation) — every other card variant wraps it:
`MetricCard`, `ScoreCard`, `InsightCard`, `RequirementCard`,
`EvidenceCard`, `RecommendationCard`, `SectionCard`. No one-off card
styles elsewhere.

## 9. Buttons

`Button` variants: `primary` / `secondary` / `tertiary` / `destructive`,
sizes `sm`/`md`/`lg`, with `loading` (spinner replaces the leading icon)
and `disabled` states built in. `IconButton` is the icon-only variant and
always requires a `label` (used as both `aria-label` and `title`).

## 10. Forms

`Input`, `Textarea`, `Select`, `Checkbox`, `Radio`, `Toggle`,
`FileUpload`, `SearchInput` — each supports a `label`, `helperText`, and
`error` state (red border + `aria-invalid` + helper text swapped to the
error message). Focus states use a visible 2px ring
(`focus:ring-primary/40`) rather than relying on color-only browser
defaults.

## 11. Badges

`Badge` (generic pill), `ImportanceBadge` (Required/Preferred/Optional/
Critical), `MatchStatusBadge` (the six match-strength states). Status
badges always pair an icon + text + color (spec §32 accessibility rule —
never color alone).

## 12. Evidence / Requirement / Recommendation components

`RequirementCard` (text, category, importance, critical, status, score,
evidence count), `EvidenceCard` (requirement → evidence text → source →
match), `RecommendationCard` (priority, type, message, related
requirement) — all designed to map directly onto the Phase 7/Phase 10
backend schemas (`RequirementScoreResult`, `RankedEvidence`,
`Recommendation`) once a real analysis page consumes them. Priority
visual language (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`) is deliberately
restrained — not every recommendation looks alarming.

## 13. Navigation

`SidebarNav` + `NavItem` establish the visual system for the future
dashboard's primary navigation (Dashboard, My Resumes, Analyses, Target
Profiles, History, Settings) — shell only, no routing/pages wired to it
yet (Phase 12).

## 14. Feedback & data display

`EmptyState`, `Skeleton`, `Spinner`, `ProgressState` (multi-step, e.g.
"Parsing resume... → Calculating ATS score..."), `ErrorState` (clear,
actionable, never a raw stack trace). Table primitives (`Table`,
`TableHead`, `TableRow`, `TableCell`, `TableEmpty`, `TableLoading`,
`TablePagination`) are prepared for future analysis-history/requirement
tables — no complete table is built yet.

## 15. Responsive breakpoints

Uses Tailwind's default breakpoints (`sm` 640px, `md` 768px, `lg` 1024px,
`xl` 1280px, `2xl` 1536px) rather than a custom scale — no reason to
diverge from the framework default.

## 16. Accessibility

- Visible focus rings on every interactive element (`:focus-visible`,
  global 2px primary-colored outline in `index.css`).
- Status is never color-only: badges pair icon + text + color.
- Form errors are announced via `aria-invalid` + `aria-describedby`.
- `prefers-reduced-motion` is respected globally (animations collapse to
  ~0ms).
- Score components carry a full `aria-label`/`role="img"` or
  `role="progressbar"` description (e.g. "ATS Alignment: 84 out of 100,
  Strong").

## 17. Dark mode

Tokens are dark-mode-ready via a `.dark` class (`@custom-variant dark`
in `index.css`) that overrides only the surface/border/text/semantic
tokens — no component duplicates its styles per theme. **Not activated**
anywhere in the app yet (no toggle UI) — this phase only prepares the
token layer per spec §5's "if the existing architecture supports themes
cleanly" condition; the existing app had no theme system before this
phase.

## 18. Motion

`--motion-fast` 120ms (hover/press feedback), `--motion-base` 200ms
(toggles, most transitions), `--motion-slow` 320ms (score reveal
animations — `ScoreRing`'s stroke-dashoffset, `ScoreBar`'s width).
`cubic-bezier(0.4, 0, 0.2, 1)` easing throughout. No bouncing, no
decorative/constant motion.
