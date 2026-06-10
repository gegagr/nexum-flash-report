# Research: Nexum Flash Report

## Chart Library

**Decision**: Chart.js 4.x  
**Rationale**: Best CDN story, excellent stacked bar + line support, works with html2canvas, large community. Chart.js 4 has built-in dataset visibility toggle and tooltip formatting.  
**Alternatives considered**: ApexCharts (heavier), D3 (too low-level for this scope), Highcharts (commercial license)

## PowerPoint Export

**Decision**: pptxgenjs 3.x + html2canvas 1.x  
**Rationale**: pptxgenjs is the de-facto browser PPTX library; html2canvas captures DOM nodes as canvas images that pptxgenjs can embed. No server required.  
**Limitation**: html2canvas requires charts to be rendered in DOM at time of capture; hidden elements must be briefly shown or captured off-screen.  
**Alternatives considered**: officegen (Node.js only), docx (Word only)

## CSV Parsing

**Decision**: PapaParse 5.x  
**Rationale**: Handles quoted fields, type coercion, streaming; ~50KB; works entirely in browser.  
**Alternatives considered**: native `split(',')` — too fragile for quoted client names

## Cutoff Logic

**Decision**: Default cutoff = max(Month) where Stage = 'Won' AND Year = 2026 in pipeline file  
**Rationale**: Reflects the latest month of confirmed actuals without user input. Controller can override via dropdown.

## Currency Handling

**Decision**: No FX conversion; nominal amounts displayed as-is  
**Rationale**: Dataset mixes EUR and GBP (e.g. UK entities use GBP). Conversion would require live FX rates. Controller is aware — the dashboard is used internally and the mix is known.  
**Risk**: Totals are cross-currency; label will show "Mixed" currency symbol.

## Stage Mapping

From the pipeline CSV, stages are: **Won**, **Lost**, **Pending**  
- **Signed**: Won, Year = 2026, Month ≤ cutoff  
- **Backlog**: Won, Year = 2026, Month > cutoff (already contracted, not yet delivered)  
- **Pipeline**: Pending, Year = 2026, uses `Weighted Pipeline` column when available, else `Revenue`  
- **Lost**: excluded from all positive metrics  

Budget file: all rows are Stage = Won — treated as budget targets by month.

## Company Name

**Decision**: **Nexum** (derived from entity names in dataset: Nexum EMEA, Nexum UK, Nexum LATAM)  
This is a multi-entity consulting group operating across Europe and LATAM.
