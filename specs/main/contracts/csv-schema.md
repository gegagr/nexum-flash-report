# CSV Input Contract

## Shared structure (both files)

`input_pipeline.csv` and `input_budget.csv` have the **same 17 columns**
(header row, comma-separated):

```
Project ID, Client, Business Unit, Activity, Entity, Geography,
Commercial Lead, Stage, Start Date, End Date, Month, Year, Revenue,
Currency, New/Existing, Weighted %, Weighted Pipeline
```

## Monthly revenue recognition (IMPORTANT)

Revenue is recognised **by month**: a project spanning N calendar months has
**N rows** — same `Project ID`, `Start Date`, `End Date`; different
`Month`/`Year`; `Revenue` carries that month's slice only (allocated by
seasonal working days).

> **Always aggregate by the `Month` and `Year` columns — never by
> `Start Date`.** Annual contracts start 01/01: grouping by Start Date dumps
> their full-year value into January (e.g. Jan 2026 shows ~€31M instead of
> ~€2.6M) and leaves months with no contract starts empty. That is an
> aggregation error, not a data property.

## Column rules

- `Project ID`: `P#####_s` (pipeline) / `B#####_s` (budget); `_s` = split
  number 1–4. Splits of one deal can differ in Business Unit and Entity.
- `Stage`: `Won`, `Lost`, `Pending`. Budget is always `Won`.
  Pipeline: until May 2026 only Won/Lost; June 2026 onwards (report cutoff)
  Won = backlog, Pending = weighted pipeline.
- `Start Date` / `End Date`: `dd/mm/yyyy`, full project duration (context
  only — not for monthly bucketing).
- `Month` 1–12, `Year` 2025–2026 (a few project tails reach 2027).
- `Revenue`: positive number, monthly slice in the row's currency.
- `Currency`: `EUR`, or `GBP` for UK rows.
- `New/Existing`: `New Business` (first deal for the client, and all TBD
  budget rows) or `Existing Business`.
- `Weighted %` / `Weighted Pipeline`: only on Pending rows
  (25/50/75%; `Weighted Pipeline = Revenue × Weighted %`). Empty otherwise.
- Budget `Client` may be `TBD` (new business planned but client unknown at
  budgeting time).

## Dataset invariants (for sanity checks)

- 2025: actuals ≈ €43M vs budget €44.5M (slightly under, mixed months).
- 2026: budget = exactly €50M (= 2025 base + €3M Portugal launch + 1–8%
  growth per existing geography).
- Every Business Unit × Geography has revenue in **both** files **every
  month** (Portugal from Jan 2026 only).
- January actuals are always at/above budget (highest-visibility month).

## File Loading Contract

`report.html` loads both files via `<input type="file">`. Once both are
loaded the dashboard initialises automatically; files can be re-loaded at any
time to refresh data. The dashboard buckets every row by `Month`/`Year`
(falling back to `Start Date` only if those columns are absent).
