# Nexum Flash Report

Un **flash report de ventas** en un solo archivo HTML. Le arrastras dos extractos en CSV (presupuesto y pipeline) y te monta el dashboard del mes: venta firmada contra presupuesto y contra el año anterior, backlog, pipeline ponderado, negocio nuevo vs existente, top de comerciales y concentración de clientes. Con un botón exporta todo a PowerPoint.

Sin servidor, sin instalación, sin base de datos. Se abre en el navegador y funciona, también sin conexión.

## Probarlo

**Demo en vivo:** _(pendiente: enlace de GitHub Pages)_

Carga sola los datos de ejemplo. Puedes cambiar filtros, mes de corte y moneda (EUR/GBP), y exportar el PowerPoint.

### En local

1. Descarga el repo.
2. Abre `index.html` en el navegador (doble clic).
3. Si no cargan los datos solos, usa los botones **Budget CSV** y **Pipeline CSV** para subir `input_budget.csv` e `input_pipeline.csv`.

## Los datos

`input_budget.csv` e `input_pipeline.csv` son **datos sintéticos de demostración**. No corresponden a ningún cliente real. Los scripts `generate_all.py`, `expand_monthly.py` y `rebuild_inputs.py` muestran cómo se generan.

Cada fila lleva su mes de devengo (`Month`/`Year`): el ingreso se reparte por mes, no se acumula en la fecha de inicio del contrato.

## Cómo está hecho

Un único `index.html` con JavaScript estándar y cuatro librerías por CDN:

- **PapaParse** — leer los CSV en el navegador
- **Chart.js** — los gráficos
- **html2canvas** + **pptxgenjs** — exportar a PowerPoint

## Contexto

Escrito como experimento para *Laboratorio FP&A*. La idea: la IA construye la herramienta una vez; la herramienta hace el trabajo cada mes.
