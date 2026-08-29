# Report design contract

Create a polished offline audit report from the canonical Markdown. This file defines the visual outcome and the design rules, not an HTML template. Design the composition for the actual repository, language, and finding count on every run.

## Product job

The reader must understand the audit state in the first viewport, find the highest-value evidence quickly, filter noise, and copy an exact source location. Evidence is the main content. Decoration stays quiet.

The report is an instrument, not a marketing page:

- The audit state is clear in the first viewport: repository, scope, profile, complete or partial, active and dismissed counts.
- Findings and their evidence are visually dominant.
- Exact values such as counts, thresholds, line numbers, and rule keys are easy to scan and compare.
- Controls sit next to the content they filter.
- Color communicates state; it does not decorate the page.
- The page stays calm during a long reading session.

## Required information

The index shows repository, commit, date, completion state, scope, profile, active and dismissed counts, rule summary, synthesis, source-area pages, and environment details.

Each Markdown finding entry keeps these values together:

- id, status, title, and rule key
- all source locations and one copy action
- evidence rank and evidence text
- the verbatim snippet
- consequence for an active finding, or removal reason for a dismissed finding

Use one self-contained HTML index, one Markdown summary, and source-area Markdown shards. A shard contains at most 100 findings. The index links the summary and every shard and remains the only HTML file. Give large audits clear navigation. Give an empty audit a clear result instead of empty panels.

## Composition

Start with the audit, not the identity. Keep the title compact. Give the most space to findings and evidence.

Reading order of the index:

1. Audit state: repository, commit, date, scope, profile with its basis, complete or partial, active and dismissed counts.
2. Rule summary: one row per rule with active count, dismissed count, and evidence rank.
3. Synthesis: at most three hypotheses, each marked as inference.
4. Source areas: one entry per shard with its status, area, and count, linking the Markdown file.
5. Environment.

Layout rules:

- Fluid content width up to 1440px. Wide screens may place the filters in a sticky rail beside the content; narrow screens use one column with the filters above the content.
- Hierarchy comes from position, scale, spacing, alignment, and density before color or containers.
- Each region answers one reader question. Merge duplicates. Keep one home for each claim.
- Do not use centered heroes, equal metric tiles, bento grids, or a card around every group. Counts must be easy to compare without identical tiles.
- Do not copy a prior report's DOM or layout. Choose the structure after reading the data.

## Visual direction

A precise editorial instrument: near-monochrome warm surfaces, thin structural lines, and one accent for readings and state.

- Hairlines, spacing, and alignment define sections instead of heavy containers.
- Code and evidence are the strongest surfaces.
- Tabular monospace for ids, rule keys, paths, measurements, and code.
- Corner radius is small: 6px; smaller controls derive from it.
- Use a faint top highlight or a subtle inset shadow for depth. No heavy shadows, neon glow, gradient text, or glass.
- No gradients, stock art, emoji, decorative charts, or external fonts.

## Themes

Ship two themes in every report: **Daylight paper** and **Night amber**. Daylight is the default and the print theme. On first load follow `prefers-color-scheme`, offer a theme control, and remember the choice in `localStorage` by setting `data-theme` on the root element. Without JavaScript the page renders Daylight.

Tokens use space-separated HSL channels and are consumed as `hsl(var(--token))`. The names are roles, not a required CSS API. Keep the roles and the contrast relationships; adjust a value only when the content or the contrast rules need it.

### Daylight paper

```css
:root,
[data-theme='daylight'] {
  --page: 32 68% 95%;
  --surface: 30 100% 98%;
  --elevated: 0 0% 100%;
  --inset: 33 45% 91%;
  --hairline: 33 25% 81%;
  --edgeline: 33 17% 68%;
  --control: 34 10% 50%;

  --accent: 10 76% 43%;
  --accent-bright: 10 66% 36%;
  --accent-dim: 11 73% 80%;

  --text: 33 16% 11%;
  --text-muted: 30 11% 33%;
  --on-accent: 30 100% 98%;
  --destructive: 358 65% 42%;
  --on-destructive: 0 0% 98%;

  --inset-shadow: inset 0 1px 3px hsl(33 20% 20% / .09);
  --ease-fluid: cubic-bezier(.22, 1, .36, 1);
  --radius: 6px;
  color-scheme: light;
}
```

Reference swatches: `#FBF3EA`, `#FFF9F3`, `#C1361A`. The accent is vermilion on paper.

### Night amber

```css
[data-theme='amber'] {
  --page: 30 14% 5%;
  --surface: 30 12% 12%;
  --elevated: 28 11% 17%;
  --inset: 32 14% 8%;
  --hairline: 28 10% 22%;
  --edgeline: 27 10% 31%;
  --control: 28 10% 47%;

  --accent: 34 78% 55%;
  --accent-bright: 38 88% 70%;
  --accent-dim: 34 45% 30%;

  --text: 36 20% 93%;
  --text-muted: 32 12% 68%;
  --on-accent: 30 60% 8%;
  --destructive: 8 75% 62%;
  --on-destructive: 0 0% 98%;

  --inset-shadow: inset 0 2px 7px rgba(0, 0, 0, .42),
    inset 0 1px 2px rgba(0, 0, 0, .5);
  color-scheme: dark;
}
```

Reference swatches: `#100D0B`, `#1F1A15`, `#E29C2F`. Warm black surfaces keep the amber readings distinct.

### Token roles

| Token | Role |
|---|---|
| `--page` | Page background |
| `--surface` | Main content surface |
| `--elevated` | Sticky rail, popovers, theme control |
| `--inset` | Code blocks, search field, recessed fields |
| `--hairline` | Structural divider |
| `--edgeline` | Stronger structural emphasis |
| `--control` | Control border and scrollbar thumb |
| `--accent` | Links, focus ring, active filter, selected state, active-finding marker |
| `--accent-bright` | Headline readings: the active count, a measured value over its threshold |
| `--accent-dim` | Quiet accent: tag backgrounds, selected-row tint |
| `--text`, `--text-muted` | Body text; secondary text and dismissed findings |
| `--destructive` | Reset and clear controls, the partial-run notice |

Do not use the accent as a panel outline or as a large background fill. Do not use `--hairline` for a control boundary when `--control` is required. Status (`active`, `dismissed`) and evidence rank (`mechanical`, `semantic`, `estimate`) always appear as text; color may reinforce them but never replaces them.

## Typography

System fonts only. The report loads no font files.

| Role | Family | Use |
|---|---|---|
| Interface | `system-ui`, then the host sans stack | Headings, prose, labels, controls, localized text |
| Readings | `ui-monospace`, then the host mono stack | ids, rule keys, paths, line numbers, measurements, code |

Rules:

- Body text starts at 16px. Functional text never goes below 12px. Code is 13px or larger.
- Use type size for hierarchy and the accent for state. Do not enlarge a value only because it is important.
- Numeric readings use tabular numbers and stable widths, so changing digits do not move nearby content.
- CJK and other localized prose use the interface font, not the mono font.
- Prose keeps a narrow reading line of about 70 characters. Tables and code may use the full width and scroll horizontally.
- Do not add a third font role for one component.

## Spacing and grouping

- Label to control: close. Controls in one group: tight and regular. Group to group: more space or one hairline. Region to region: clear separation.
- Each gap has one owner. The stack, grid, or panel sets it; children add no competing margins.
- Density comes from removing needless containers and travel, not from shrinking text or hit targets.
- Do not wrap every group in a card. An empty rectangle usually means the grouping is wrong.

## Interaction

Keep the page static unless interaction materially helps the current audit. When the finding count justifies it, add local JavaScript for search, exact filters on rule, evidence rank, status, and source area, a reset control, and the theme control. Filters combine with AND and show visible versus total counts. Keep the page readable when JavaScript is unavailable: all content is in the DOM, and native `details` elements and anchors carry the navigation.

Controls and state:

- Every control has a visible label or accessible name. Prefer native `input type="search"`, `select`, `button`, and `details`.
- One primary control per context. Reset and clear controls use the destructive color and keep their position and size.
- Pair color with text, position, line, shape, or icon.
- Keep important readings stable in width.
- Never leave an empty result without a next step: show "0 of N findings match" and the reset control.
- Prefer `aria-disabled` over `disabled` when focus must stay stable; intercept the action in code.
- Copying a location gives quiet inline confirmation beside the control. No toast.

## Evidence

Treat snippets, measurements, and locations as evidence.

- Render snippets as text inside `pre` and `code`. Escape all subject text before insertion; never interpret subject text as markup, style, or script.
- Keep snippets verbatim, at most 10 lines; longer spans show the head plus `…`.
- Keep the measured value, its threshold, and the unit together.
- Show every location as a repo-relative `path:line` with one copy action.
- Reserve space for content before it renders. No layout shift.
- Do not use fake data, invented metrics, decorative charts, or screenshots.

## Copy and localization

Write plain report language. Do not put the visual metaphor into headings, labels, or status text.

- Write titles and prose in the user's conversation language, as the summary and the shards do.
- Keep rule keys, paths, commands, code, finding ids, and the tokens `mechanical`, `semantic`, `estimate`, `active`, `dismissed`, and `partial` unchanged, wrapped in `translate="no"`.
- Describe only states the audit proves. Preserve units, thresholds, and qualifiers.
- Use one stable label for each concept across the index and the shards.

## Motion

Default to stillness. Motion explains state, continuity, or direct manipulation.

- Feedback takes 100 to 300 ms with `--ease-fluid`. Leaving is slightly faster than entering.
- Animate `transform` and `opacity` only. Make motion interruptible by new input.
- Never use `transition: all`.
- No scroll reveal, parallax, idle pulse, bounce, or decorative loops.
- Respect `prefers-reduced-motion` without removing essential state feedback.

## Responsive behavior

The report is a document. It reflows; it never shows a minimum-width notice.

- Recompose around the task: audit state and findings first, then navigation, then environment.
- The filter rail moves above the content on narrow screens. The page keeps a clear way to reach the filters.
- Keep source order equal to reading order. Tables and code blocks scroll horizontally inside their own container; the page never scrolls horizontally.
- Prefer intrinsic CSS layout over JavaScript measurement.

## Access and safety

Meet WCAG AA in both themes.

- Semantic HTML: one `h1`, logical heading order, a skip link, landmark regions, visible labels.
- Every flow works by keyboard. `:focus-visible` is visible and stays above the sticky rail.
- Keep browser zoom enabled; test at 200%.
- Never rely on color alone. Test text and non-text contrast in both themes, and test controls over the brightest and darkest content behind them.
- Announce filter results through one polite live region. Do not announce rapidly changing values.
- Inline all CSS and JavaScript. Embed a necessary image as a data URL. Load no network or local resource files.
- Escape all subject data before it enters HTML.

## Print

Print uses the Daylight tokens: white paper, black text, no controls, no sticky rail, hairline table rules, and no page break inside a finding where supported. Print shows all findings regardless of active filters.

## Work in passes

1. **Understand.** Read the summary, every shard, and this contract. Note the finding count, the source areas, the longest path, and whether the run is partial.
2. **Compose.** Privately compare two meaningfully different layouts for this audit. Change structure and evidence placement, not only color. Choose the one that makes the audit clearest.
3. **Implement.** One HTML file, inline CSS and JavaScript, both themes, system fonts.
4. **Verify.** Open the generated index and inspect at least one populated Markdown shard. Check the first viewport, a long path, a long snippet, and the empty-result state; keyboard focus, focus above the sticky rail, and accessible names; both themes, 200% zoom, reduced motion, and narrow width; print; and that the Markdown preserves long code lines and every required finding field. Fix the highest-impact defect and check again.

## Reject these defaults

Do not ship:

- Purple-black AI styling, neon glow, gradient text, or abstract blobs.
- A card around every group, or equal dashboard tiles without an information reason.
- Several competing accent colors, or large accent borders and fills.
- Decorative motion, scroll reveal, or `transition: all`.
- External fonts, stylesheets, scripts, or images.
- Tiny functional text.
- Fake data, fake progress, invented metrics, or unsupported promises.
- A copy of a previous report's DOM.

Restraint is not emptiness. It is exact hierarchy, scarce color, readable state, and evidence that stays central.
