# Quickstart: Nexum Flash Report

## Prerequisites

- Modern browser (Chrome 90+, Edge 90+, Firefox 88+, Safari 14+)
- `input_budget.csv` and `input_pipeline.csv` in the same folder as `report.html`
- Internet connection on first load (CDN libraries); or bundle libraries offline

## Running the Report

1. Open `Flash-Report/report.html` in your browser (double-click or `File → Open`)
2. Click **Load Budget CSV** and select `input_budget.csv`
3. Click **Load Pipeline CSV** and select `input_pipeline.csv`
4. The dashboard renders automatically

## Using Filters

- **Activity** dropdown → selecting an activity narrows the **Business Unit** list
- **Business Unit** dropdown → further narrows **Geography** list
- **Cutoff Month** → changes which month is treated as the latest actual (default: auto-detected)
- All filters apply simultaneously; any change re-renders everything

## Exporting to PowerPoint

1. Set your desired filters and cutoff
2. Click **Export to PowerPoint**
3. Wait ~3 seconds while html2canvas captures each section
4. A `.pptx` file downloads automatically (filename: `Nexum_Flash_Report_YYYY-MM.pptx`)
5. Open in PowerPoint; fill in the "Controller notes:" box on each slide

## Development

No build step. Edit `report.html` directly. All logic is in the single file:
- `<style>` block: layout and card styles
- `<script>` block sections: `// DATA`, `// FILTERS`, `// CHARTS`, `// EXPORT`

## Library Versions (CDN)

```html
<script src="https://cdn.jsdelivr.net/npm/papaparse@5/papaparse.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/pptxgenjs@3/dist/pptxgen.bundle.js"></script>
```
