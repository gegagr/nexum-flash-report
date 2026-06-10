# Tasks: Nexum Flash Report Dashboard

**Input**: Design documents from `/specs/main/`

**Prerequisites**: plan.md ✓, research.md ✓, data-model.md ✓, contracts/csv-schema.md ✓, quickstart.md ✓

**Organization**: Tasks grouped by deliverable phase. No tests requested — implementation only.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

---

## Phase 1: Setup

**Purpose**: Create the HTML file skeleton with CDN dependencies and layout scaffolding.

- [X] T001 Create `Flash-Report/report.html` with HTML5 boilerplate, CDN `<script>` tags for PapaParse, Chart.js, html2canvas, pptxgenjs
- [X] T002 Add CSS: dark navy theme (`#0D1B2A`), white text, amber accent (`#E8A020`), card styles, responsive grid layout in `report.html` `<style>` block
- [X] T003 Add file-input section with two `<input type="file">` buttons ("Load Budget CSV", "Load Pipeline CSV") and a status line in `report.html`

---

## Phase 2: Foundational — Data Layer

**Purpose**: CSV parsing, `RevenueRow` normalisation, filter state, and cutoff detection. All later phases depend on this.

**⚠️ CRITICAL**: No UI section can be built until this phase is complete.

- [X] T004 Implement `parseCSV(file, source)` in `report.html` `// DATA` block using PapaParse; returns array of `RevenueRow` objects (fields: projectId, month, year, client, businessUnit, activity, entity, geography, lead, stage, revenue, currency, weightedRevenue, source)
- [X] T005 Implement `loadFiles()` wiring: attach change handlers to both file inputs; when both are loaded call `onDataReady(budgetRows, pipelineRows)` in `report.html`
- [X] T006 Implement `detectCutoff(pipelineRows)` — returns max Month where Stage=Won AND Year=2026; store in global `state.cutoff` in `report.html` `// FILTERS` block
- [X] T007 Implement `buildFilterOptions(rows)` — derive distinct Activity list, Activity→BU map, BU→Geography map; populate the three `<select>` dropdowns plus the cutoff month dropdown in `report.html`
- [X] T008 Implement `applyFilters(rows, state)` — returns filtered subset respecting activity, businessUnit, geography selections; used by every downstream computation in `report.html`
- [X] T009 Implement `computeKPIs(filteredBudget, filteredPipeline, year, cutoff)` — returns `{ signedYTD, backlog, pipeline, budgetYTD }` and month-by-month series array `[{ month, signed, backlog, pipeline, budget }]` in `report.html` `// DATA` block

**Checkpoint**: Call `onDataReady` manually with fixture data in browser console to verify KPI output before building UI.

---

## Phase 3: US1 — KPI Flash Cards

**Goal**: YTD and Month snapshot cards visible and correct.

**Independent Test**: Load CSVs, check that 2026 YTD Signed Revenue card shows the sum of all Won 2026 rows up to cutoff month; delta vs budget is green/red/grey correctly.

- [X] T010 [US1] Implement `renderFlashCards(section, kpis2026, kpisYBudget, kpis2025)` in `report.html` `// UI` block — renders three cards (2026 primary, Budget, 2025) with large number + delta badges
- [X] T011 [US1] Implement delta badge logic: green if 2026 > reference, red if lower, grey if equal; apply to both Δ-vs-Budget and Δ-vs-2025 badges inside `renderFlashCards` in `report.html`
- [X] T012 [US1] Add `<section id="ytd-snapshot">` and `<section id="month-snapshot">` containers to `report.html` layout, with "YTD Snapshot" and "Month Snapshot" headings
- [X] T013 [US1] Wire `renderFlashCards` calls into `onDataReady` / filter-change handler for both YTD (months 1→cutoff) and Month (cutoff month only) in `report.html`

**Checkpoint**: Both card rows render with correct numbers and colour coding after loading the CSVs.

---

## Phase 4: US2 — Bar Chart (Pipeline vs Budget)

**Goal**: Stacked bar chart showing Signed+Backlog (black), Pipeline (brown), Gap to Budget (red) per month.

**Independent Test**: January bar height = sum of Jan Won 2026 rows (Signed) — verify against raw CSV sum.

- [X] T014 [US2] Add `<canvas id="barChart">` inside a `<section id="bar-section">` in `report.html`
- [X] T015 [US2] Implement `renderBarChart(monthlySeries, budgetSeries)` in `report.html` `// CHARTS` block using Chart.js stacked bar; datasets: Signed (black `#1a1a1a`), Backlog (dark grey `#444`), Pipeline (brown `#7B4F2E`), Gap (red `#DC3545` — only positive gap)
- [X] T016 [US2] Wire `renderBarChart` into `onDataReady` / filter-change handler; destroy and recreate chart instance on re-render in `report.html`

**Checkpoint**: Bar chart visible with correct stacking; a month with pipeline > budget shows a red gap bar.

---

## Phase 5: US3 — Cumulative Line Chart

**Goal**: Line chart with 2026 actuals, Budget, 2025 actuals, and Gap-to-Budget area.

**Independent Test**: Budget line value at month 3 = sum of budget rows months 1+2+3 (cumulative).

- [X] T017 [US3] Add `<canvas id="lineChart">` inside a `<section id="line-section">` in `report.html`
- [X] T018 [US3] Implement `renderLineChart(monthlySeries26, monthlySeries25, budgetSeries)` in `report.html` `// CHARTS` block; datasets: 2026 blue solid, Budget green solid, 2025 grey solid, Gap red dashed with `fill: 'origin'` and `backgroundColor: 'rgba(220,53,69,0.15)'`
- [X] T019 [US3] Wire `renderLineChart` into `onDataReady` / filter-change handler with chart destroy/recreate pattern in `report.html`

**Checkpoint**: Four lines visible; transparent red area fills between Gap line and zero; budget line is a smooth cumulative curve.

---

## Phase 6: US4 — Top 3 Commercial Performers

**Goal**: Top-3 performers table showing Signed YTD, vs PY, Remaining to Find, % Remaining.

**Independent Test**: First performer's Signed YTD matches manual sum of Won 2026 rows for that lead up to cutoff.

- [X] T020 [US4] Implement `computeTopPerformers(filteredBudget, filteredPipeline, cutoff)` in `report.html` `// DATA` block — groups by Commercial Lead, returns top 3 sorted by Signed YTD desc; each entry: `{ lead, signedYTD, signedPY, budgetYTD, remaining, remainingPct }`
- [X] T021 [US4] Add `<section id="performers-section">` with three performer cards in `report.html`; implement `renderPerformers(top3)` showing rank, name, signed YTD, Δ vs PY (€, colour-coded), remaining €, remaining %

**Checkpoint**: Three cards show correct names and amounts; PY delta is green/red correctly.

---

## Phase 7: US5 — Top 10 Clients Table (Month)

**Goal**: Side-by-side tables of top 10 clients for cutoff month in 2026 and 2025.

**Independent Test**: First row of 2026 table = client with highest Won revenue in cutoff month of 2026.

- [X] T022 [US5] Implement `computeTopClients(filteredPipeline, month, year, n=10)` in `report.html` `// DATA` block — filters Won rows for given month+year, groups by Client, sorts desc, returns top n with `{ rank, client, activity, revenue, currency }`
- [X] T023 [US5] Add `<section id="clients-section">` with two `<table>` elements side by side in `report.html`; implement `renderClientTables(top2026, top2025)` with columns: Rank, Client, Activity, Revenue

**Checkpoint**: Both tables populate with 10 rows each; 2026 and 2025 columns are side-by-side.

---

## Phase 8: US6 — PowerPoint Export

**Goal**: "Export to PowerPoint" button downloads a board-ready .pptx with 7 slides, active filters applied, comment boxes on each data slide.

**Independent Test**: Click export with default filters → .pptx downloads → open in PowerPoint → 7 slides visible → each data slide has a grey "Controller notes:" box at the bottom.

- [X] T024 [US6] Add `<button id="exportBtn">Export to PowerPoint</button>` to the filter bar area in `report.html`
- [X] T025 [US6] Implement `captureSection(sectionId)` helper using `html2canvas` — returns a `dataURL` PNG in `report.html` `// EXPORT` block
- [X] T026 [US6] Implement slide builder helpers in `report.html` `// EXPORT` block: `addCoverSlide(pptx, filterSummary)`, `addDataSlide(pptx, title, imageDataUrl)` — data slides use navy background, white title, amber underline, image occupying ~80% height, grey comment box at bottom labelled "Controller notes:"
- [X] T027 [US6] Implement `exportToPPTX()` async function in `report.html` `// EXPORT` block: instantiate PptxGenJS, call `captureSection` for each of the 6 data sections sequentially, build 7 slides, trigger download as `Nexum_Flash_Report_YYYY-MM.pptx`
- [X] T028 [US6] Wire `exportBtn` click → `exportToPPTX()`; disable button during export and show "Exporting…" text; re-enable on completion in `report.html`

**Checkpoint**: Export produces a valid .pptx; all 7 slides present; comment boxes are editable in PowerPoint; filter state is shown on cover slide.

---

## Phase 9: Polish & Cross-Cutting

**Purpose**: UX polish, edge cases, responsive layout refinements.

- [X] T029 [P] Add loading spinner overlay while CSVs parse and dashboard renders in `report.html`
- [X] T030 [P] Add "Reset Filters" button that restores all dropdowns to 'All' and cutoff to auto-detected in `report.html`
- [X] T031 Handle edge case: if one or both CSV files not yet loaded, show placeholder message instead of blank sections in `report.html`
- [X] T032 [P] Add currency label "EUR/GBP (mixed)" next to KPI totals where amounts span both currencies in `report.html`
- [X] T033 Verify quickstart.md steps work end-to-end: open report.html, load both CSVs, check all sections render, export PPTX, open in PowerPoint

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies
- **Phase 2 (Data Layer)**: Depends on Phase 1
- **Phases 3–8 (User Stories)**: All depend on Phase 2 completion
- **Phase 9 (Polish)**: Depends on all user story phases

### User Story Dependencies

- **US1–US5** are independent of each other once Phase 2 is complete — they each read from the shared computed state
- **US6 (Export)** depends on US1–US5 being rendered (it captures their DOM sections)

### Parallel Opportunities

- US1, US2, US3, US4, US5 can all be built in parallel after Phase 2
- Within each US: markup task [P] can run alongside data-computation task [P]

---

## Parallel Example: US2 + US3

```
// After Phase 2 complete, run simultaneously:
Task T014+T015+T016 (Bar Chart)
Task T017+T018+T019 (Line Chart)
// Both write to different <canvas> elements — no conflict
```

---

## Implementation Strategy

### MVP (US1 + US2 only)

1. Complete Phase 1 + Phase 2
2. Complete Phase 3 (flash cards) → validate
3. Complete Phase 4 (bar chart) → validate
4. **STOP — demo to controller**

### Full Delivery

1. MVP above
2. Add US3 (line chart) → US4 (performers) → US5 (client tables)
3. Add US6 (export) — requires all sections rendered
4. Phase 9 polish

---

## Notes

- All code lives in a single `Flash-Report/report.html` file — no separate JS files
- [P] tasks touch different DOM sections or separate function scopes — safe to parallelize
- Destroy and recreate Chart.js instances on every filter change to avoid stale data
- html2canvas requires elements to be visible in DOM at capture time — do not use `display:none` to hide sections during export
- Cutoff month default auto-detection happens once on data load; user override persists in `state.cutoff`
