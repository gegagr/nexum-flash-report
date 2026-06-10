# Data Model: Nexum Flash Report

## Source CSVs

### input_pipeline.csv

| Column | Type | Notes |
|--------|------|-------|
| Project ID | string | e.g. `P00001_1`; `_s` suffix = split 1–4 |
| Client | string | client company name |
| Business Unit | string | e.g. Recruitment, CFO Advisory |
| Activity | string | HR / Finance / Marketing |
| Entity | string | Nexum UK / Nexum EMEA / Nexum Iberia |
| Geography | string | UK / Germany / France / Spain / Italy / Portugal |
| Commercial Lead | string | person name |
| Stage | enum | Won / Lost / Pending |
| Start Date | date | dd/mm/yyyy, full project duration (context only) |
| End Date | date | dd/mm/yyyy |
| Month | int | 1–12 — **revenue recognition month; aggregate on this** |
| Year | int | 2025 or 2026 (a few tails in 2027) |
| Revenue | number | this month's slice only (project has 1 row per month) |
| Currency | enum | EUR / GBP (GBP for UK rows) |
| New/Existing | enum | New Business / Existing Business |
| Weighted % | number | nullable; Pending rows only (25/50/75%) |
| Weighted Pipeline | number | nullable; Revenue × Weighted %, Pending only |

**Never bucket revenue by Start Date** — annual contracts start 01/01 and
would land their full-year value in January. Use Month/Year.

### input_budget.csv

Same 17 columns as pipeline CSV. Stage is always `Won`; Weighted % and
Weighted Pipeline are empty. Client may be `TBD` (planned new business,
client unknown at budgeting time).

## Derived Concepts

### RevenueRow (normalised in-memory record)

```js
{
  projectId: string,
  month: number,        // 1–12
  year: number,         // 2025 | 2026
  client: string,
  businessUnit: string,
  activity: string,
  entity: string,
  geography: string,
  lead: string,
  stage: 'Won' | 'Lost' | 'Pending',
  revenue: number,
  currency: 'EUR' | 'GBP',
  weightedRevenue: number,  // = Weighted Pipeline if present, else revenue
  source: 'pipeline' | 'budget'
}
```

### Filter State

```js
{
  activity: string | 'All',
  businessUnit: string | 'All',
  geography: string | 'All',
  cutoffMonth: number   // 1–12, default = max Won month in 2026 pipeline
}
```

Cascade rule:
- When `activity` changes → recompute `businessUnit` options from rows matching that activity; reset `businessUnit` to 'All'
- When `businessUnit` changes → recompute `geography` options; reset `geography` to 'All'

### KPI Aggregates

```js
// For a given year, months 1–cutoff, filtered rows
{
  signedYTD: number,     // sum(revenue) where stage=Won, year, month <= cutoff
  backlog: number,       // sum(revenue) where stage=Won, year, month > cutoff
  pipeline: number,      // sum(weightedRevenue) where stage=Pending, year
  budgetYTD: number,     // sum(revenue) from budget rows, year, month <= cutoff
}
```

### Monthly Series (for charts)

```js
// Array of 12 items, one per month
[{ month: 1, signed: n, backlog: n, pipeline: n, budget: n }, ...]
```

## Entities & Activity → BU Mapping (from data)

| Activity | Business Units |
|----------|---------------|
| HR | Recruitment, HR Compliance, HR Transformation, Payroll Advisory, Training & Development |
| Finance | CFO Advisory, Financial Planning, M&A Support, Tax Optimization, Accounting Transformation |
| Marketing | Brand Strategy, Customer Experience, Digital Marketing, Market Research, Sales Enablement |
