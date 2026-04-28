# CONTEXT.md — Project Bible

## What this is

A personal dashboard hosted on GitHub Pages, used as a launchpad for small browser-based tools. Built and maintained with Claude Code. The homepage is a fixed world clock (New York, London, Dubai) and tools are added as separate pages in their own folders, linked from the homepage. Every tool is a single self-contained HTML file — no frameworks, no build step, no backend.

## Live URL

`https://<github-username>.github.io/<repo-name>/`

_(Update this placeholder once the repo is published.)_

## Repo structure

```
dashboard/
├── index.html                  ← Entry point. World clock + links to tools.
├── CONTEXT.md                  ← This file. Project conventions and design system.
├── CLAUDE.md                   ← Points Claude Code to read CONTEXT.md first.
├── WORLD_CLOCK_README.md       ← Docs for the world clock (deployment, customisation).
├── payroll/
│   └── index.html              ← Payroll discrepancy comparison tool.
├── .streamlit/                 ← Streamlit config (separate local-only dashboard, not on GitHub Pages).
│   └── config.toml
├── Home.py                     ← Streamlit landing page (local only, not part of GitHub Pages).
├── pages/
│   └── 1_📧_Email_Summarizer.py ← Streamlit email triage page (local only).
├── shared/                     ← Shared Python modules for Streamlit dashboard (local only).
│   ├── __init__.py
│   ├── styling.py
│   └── tool_runner.py
├── requirements.txt            ← Python deps for Streamlit dashboard (local only).
├── run.sh                      ← Launcher for Streamlit dashboard (local only).
└── README.md                   ← Docs for the Streamlit dashboard (local only).
```

**GitHub Pages scope:** Only `index.html` and folders containing their own `index.html` (e.g. `payroll/`) are served by GitHub Pages. The Streamlit files (`Home.py`, `pages/`, `shared/`, `run.sh`, etc.) are local-only tools that run via `./run.sh` and are not part of the static site.

## Design system

All values pulled from the actual code in `index.html` and `payroll/index.html`:

| Token | Value |
|---|---|
| Background | `#0a0a0d` |
| Primary text | `#e8e8ea` |
| Muted text (labels, dates) | `rgba(232, 232, 234, 0.4)` |
| Dimmer muted text (secondary) | `rgba(232, 232, 234, 0.3)` |
| Input/control background | `#16161a` |
| Border colour (subtle) | `rgba(232, 232, 234, 0.12)` |
| Border colour (hover/active) | `rgba(232, 232, 234, 0.3)` |
| Status — red (missing/error) | `#ef4444` with bg `rgba(239, 68, 68, 0.15)` |
| Status — amber (mismatch/warning) | `#eab308` with bg `rgba(234, 179, 8, 0.15)` |
| Status — grey (match/neutral) | `#555` / `rgba(107, 114, 128, 0.2)` |
| Success green (e.g. upload confirmed) | `rgba(74, 222, 128, 0.4)` text `rgba(74, 222, 128, 0.7)` |

**Fonts:**

| Purpose | Stack |
|---|---|
| Monospace (numbers, data, times, names) | `"JetBrains Mono", "Roboto Mono", "SF Mono", "Cascadia Code", "Fira Code", ui-monospace, monospace` |
| Sans-serif (UI controls, body text, labels) | `-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif` |

- Use `font-variant-numeric: tabular-nums` on monospace digits so columns don't shift as numbers change.
- The clock homepage uses monospace as the body font. Tool pages use sans-serif as body font with a `.mono` utility class for data cells.

**Borders and dividers:**
- Subtle borders use `1px solid rgba(232,232,234,0.12)`.
- Table row dividers use `1px solid rgba(232,232,234,0.06)`.
- Dashed borders for upload/drop zones: `2px dashed rgba(232,232,234,0.12)`.
- Status indicators use a `4px solid` left border on table rows or cards.
- Border radius: `4px` for inputs/small controls, `6px` for buttons and banners, `8px` for cards and upload zones.

**Spacing:**
- Page padding: `2rem` (desktop), `1rem` (mobile).
- Max content width: `1200px`, centred with `margin: 0 auto`.
- Generous gaps between sections: `1.5rem` to `2rem`.

## Styling principles

- Dark theme, near-black background (`#0a0a0d`). No light mode.
- Minimal and flat — no gradients, no shadows, no decorative effects.
- Monospace for all data (numbers, names, hours, times). Sans-serif for UI (buttons, labels, headings).
- Generous padding and whitespace. Don't cram.
- Responsive — side-by-side on desktop, stacked on mobile (use `flex-wrap` or `@media` breakpoints around `640px`–`700px`).
- Buttons: transparent background, subtle border, text colour inherits. Hover brightens slightly.
- Match the existing aesthetic exactly when adding new tools. Don't introduce new colours or patterns.

## Tools currently built

### World Clock
- **Path:** `/index.html`
- **URL:** `/`
- **Description:** Three live digital clocks showing current time in New York (`America/New_York`), London (`Europe/London`), and Dubai (`Asia/Dubai`). Updates every second. Uses `Intl.DateTimeFormat` with `timeZone` so DST is handled automatically. Also serves as the homepage — links to all other tools are placed below the clocks.
- **External dependencies:** None.
- **localStorage keys:** None.

### Payroll Discrepancy Tool
- **Path:** `/payroll/index.html`
- **URL:** `/payroll/`
- **Description:** Compares hours from a DOM Portal Shift Timesheet export (Source A) against a support worker's submitted sheet (Source B) to find per-staff discrepancies. Source A auto-parses column C (Staff) and H (Hours) from the `Shift_Timesheets` sheet. Source B shows column-mapping dropdowns so any format works. Staff names are normalised (trim + collapse whitespace). Results table shows hours from both sources, difference, £ impact at £13.45/hr, colour-coded status (red = missing, amber = mismatch, grey = exact match), and editable notes. Includes a staff email directory (persisted in localStorage), per-discrepancy `mailto:` buttons with a templated message, and Excel export via SheetJS.
- **External dependencies:** SheetJS via CDN (`https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js`).
- **localStorage keys:** `payroll_emails` — JSON object mapping staff names to email addresses.

## Hard constraints (apply to every tool)

- Single self-contained HTML file per tool (HTML + CSS + JS in one file).
- No frameworks (no React, Vue, Svelte, etc.).
- No build step, no bundler, no `npm install`.
- No backend — must work as pure static files on GitHub Pages.
- All processing client-side. No data leaves the browser.
- External libraries only via CDN, and only when genuinely needed (e.g. SheetJS for Excel parsing).
- Must work in current Safari and Chrome.
- `localStorage` is fine for user preferences and small key-value state.
- No `<form>` tags with default submit behaviour — use button `onClick` handlers or `event.preventDefault()`.

## When adding new tools

- Create a new folder at the repo root: `/<tool-name>/index.html`.
- Add a nav button on the homepage (`index.html`) below the clocks, using the existing `.nav-link` class. Keep it subtle.
- Match the design system above exactly — same background, fonts, colours, spacing.
- Include a `← Dashboard` link top-left on the tool page, linking back to `../index.html`.
- Update the "Tools currently built" section in this file with the new tool's details.
- If the tool uses `localStorage`, document the key name and value format in the tool's entry.
- If the tool loads an external CDN library, document it in the tool's entry.

## How to deploy changes

Edit files locally, commit, and push to the `main` branch. GitHub Pages auto-rebuilds within ~1 minute. Check deployment status at **Settings → Pages** in the GitHub repo.

No build step is needed — GitHub Pages serves the files directly as static assets.

## Notes for future Claude sessions

Read this file **first** before making any changes to this repo. It is the source of truth for project conventions, the design system, and the list of tools.

When you add a new tool, update the "Tools currently built" section immediately — don't leave it for later. When you change any global styling (colours, fonts, spacing), update the "Design system" section to match. If a constraint changes (e.g. a build step is introduced), update "Hard constraints".

This file is read by both humans pasting it into Claude chats and by Claude Code sessions loading it automatically via `CLAUDE.md`. Keep it accurate, keep it current.
