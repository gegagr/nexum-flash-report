# Implementation Plan: Nexum Flash Report Dashboard

**Branch**: `main` | **Date**: 2026-06-09 | **Spec**: inline (from /speckit-plan prompt)

## Summary

Build a single-file HTML dashboard fed by two CSV files (`input_budget.csv`, `input_pipeline.csv`) for Nexum consulting group. The dashboard shows YTD and monthly KPI flash cards, stacked bar and cumulative line charts, top-3 commercial performers, and top-10 client tables — all filterable by Activity, Business Unit, Geography, and cutoff month. A one-click PowerPoint export (html2canvas + pptxgenjs) produces a board-ready deck with per-slide comment boxes.

## Technical Context

**Language/Version**: HTML5 + vanilla JavaScript (ES2020)  
**Primary Dependencies**: Chart.js 4.x (charts), html2canvas 1.x (screenshot), pptxgenjs 3.x (PPTX export), PapaParse 5.x (CSV parsing) — all loaded from CDN, no build step  
**Storage**: client-side only; CSV files loaded via `<input type="file">` drag-drop  
**Testing**: manual browser testing  
**Target Platform**: modern desktop browser (Chrome/Edge/Safari/Firefox)  
**Project Type**: single-file web application  
**Performance Goals**: render < 1 second for ~200 rows  
**Constraints**: zero server dependency; entirely offline-capable once opened  
**Scale/Scope**: 1 HTML file, 2 CSV inputs, ~100 rows total

## Constitution Check

No constitution file found — no gates to evaluate. Proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/main/
├── plan.md              ← this file
├── research.md          ← Phase 0
├── data-model.md        ← Phase 1
├── quickstart.md        ← Phase 1
└── contracts/
    └── csv-schema.md
```

### Source Code

```text
Flash-Report/
├── input_budget.csv       (existing)
├── input_pipeline.csv     (existing)
└── report.html            (to be created — the entire app)
```

## Implementation Phases

### Phase 1 — Data Layer & Filters

- Load + parse both CSVs via PapaParse (triggered by file-input buttons)
- Normalise rows to `RevenueRow` schema (see data-model.md)
- Currency note: dataset mixes EUR and GBP; amounts are treated as nominal (no FX conversion) — controller decides at usage time
- Derive `cutoff`: default = highest month with Won Pipeline data in 2026 (overridable via filter)
- Build cascading filter state: Activity → filters Business Unit list → filters Geography list
- Any filter change re-runs all computations and re-renders synchronously

### Phase 2 — KPI Flash Cards

**YTD Snapshot** (months 1 → cutoff, 2026 vs Budget vs 2025):

| Card | Content |
|------|---------|
| 2026 (primary) | Large total; bottom-right: Δ vs Budget (€, %); below that: Δ vs 2025 (€, %) |
| Budget | YTD budget total for same period |
| 2025 | YTD Won actuals for same months |

Color logic: green if 2026 > reference, red if lower, grey if equal.

**Month Snapshot**: identical 3-card row, filtered to cutoff month only.

KPI metrics tracked: Signed Revenue (Won ≤ cutoff), Pipeline (Pending weighted), Backlog (Won > cutoff — already contracted future months).

### Phase 3 — Charts

**Stacked Bar Chart** (monthly, 2026, Jan–Dec):
- Stack A (black): Signed (Won, ≤ cutoff month) + Backlog (Won, > cutoff)
- Stack B (brown): Pipeline (Pending, weighted)
- Stack C (red): Gap to Budget = Budget − (Signed + Backlog + Pipeline), shown only when positive; negative gap hidden or shown differently

**Cumulative Line Chart** (Jan–Dec):
- Blue solid: 2026 cumulative Won
- Green solid: 2026 Budget cumulative
- Grey solid: 2025 cumulative Won
- Red dashed: cumulative gap = Budget − 2026 Won (fills transparent red area between this line and the budget line)

### Phase 4 — Performers & Client Tables

**Top 3 Performers** (YTD, by Commercial Lead):
- Signed YTD | vs PY YTD (€ delta) | Remaining to find (Budget YTD − Signed YTD) | % remaining

**Top 10 Clients — Cutoff Month** (side-by-side):
- Left table: 2026 | Right table: 2025 (same cutoff month number)
- Columns: Rank, Client, Activity, Revenue

### Phase 5 — PowerPoint Export

Trigger: "Export to PowerPoint" button — respects active filters and cutoff.

Slides (7):
1. Cover — company name, date, filters applied
2. YTD Flash Cards + comment box
3. Month Flash Cards + comment box
4. Pipeline Bar Chart + comment box
5. Cumulative Line Chart + comment box
6. Top 3 Performers + comment box
7. Top 10 Clients + comment box

Styling: navy background (`#0D1B2A`), white text, amber accent (`#E8A020`), comment box = grey-bordered rectangle labelled "Controller notes:".

html2canvas captures each dashboard section as an image; pptxgenjs places image + comment placeholder on each slide.
