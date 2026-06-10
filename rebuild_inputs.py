from datetime import date, timedelta
import csv

# Base duration in calendar days per BU
BU_DAYS = {
    "Recruitment": 30,
    "Training & Development": 45,
    "HR Transformation": 105,
    "Payroll Advisory": 55,
    "HR Compliance": 28,
    "CFO Advisory": 140,
    "Financial Planning": 70,
    "Tax Optimization": 49,
    "M&A Support": 84,
    "Accounting Transformation": 112,
    "Brand Strategy": 49,
    "Digital Marketing": 63,
    "Market Research": 35,
    "Sales Enablement": 56,
    "Customer Experience": 70,
}

def proj_num(proj_id):
    return int(proj_id.split("_")[0][1:])

def start_date(month, year, pid):
    n = proj_num(pid)
    day = (n * 3 % 13) + 1  # 1–13
    return date(year, month, day)

def end_date(sd, bu, pid):
    n = proj_num(pid)
    base = BU_DAYS[bu]
    delta = (n % 5 - 2) * 7   # -14 to +14 days variation
    return sd + timedelta(days=max(base + delta, 14))

def fmt(d):
    return d.strftime("%d/%m/%Y")

COLS = ["Project ID", "Client", "Business Unit", "Activity", "Entity", "Geography",
        "Commercial Lead", "Stage", "Start Date", "End Date", "Revenue", "Currency",
        "New/Existing", "Weighted %", "Weighted Pipeline"]

# ── PIPELINE ──────────────────────────────────────────────────────────────────
# Read existing pipeline (has Month, Year columns still)
with open("input_pipeline.csv") as f:
    raw = list(csv.DictReader(f))

rows = []
for r in raw:
    m, y = int(r["Month"]), int(r["Year"])
    pid = r["Project ID"]
    sd = start_date(m, y, pid)
    ed = end_date(sd, r["Business Unit"], pid)
    rows.append({
        "Project ID": pid,
        "Client": r["Client"],
        "Business Unit": r["Business Unit"],
        "Activity": r["Activity"],
        "Entity": r["Entity"],
        "Geography": r["Geography"],
        "Commercial Lead": r["Commercial Lead"],
        "Stage": r["Stage"],
        "Start Date": fmt(sd),
        "End Date": fmt(ed),
        "Revenue": r["Revenue"],
        "Currency": r["Currency"],
        "New/Existing": "",          # filled below
        "Weighted %": r.get("Weighted %", ""),
        "Weighted Pipeline": r.get("Weighted Pipeline", ""),
    })

# New future Won deals (backlog — Jun 2026 onwards)
FUTURE_WON = [
    ("P00092_1", "Brennan & Associates", "HR Transformation",      "HR",      "Nexum EMEA",  "UK",       "Sarah Mitchell",  "Won", "06/07/2026", 180000, "GBP"),
    ("P00093_1", "Solaris Energy",        "Accounting Transformation","Finance","Nexum EMEA",  "Germany",  "James Thornton",  "Won", "13/07/2026", 240000, "EUR"),
    ("P00094_1", "Vantage Retail",        "Sales Enablement",       "Marketing","Nexum UK",   "Portugal", "Michael Chen",    "Won", "03/08/2026",  95000, "EUR"),
    ("P00095_1", "Meridian Healthcare",   "Financial Planning",     "Finance", "Nexum EMEA",  "France",   "James Thornton",  "Won", "10/08/2026", 165000, "EUR"),
    ("P00096_1", "Cedar Group",           "Brand Strategy",         "Marketing","Nexum EMEA", "France",   "Laura Dupont",    "Won", "01/09/2026", 120000, "EUR"),
    ("P00096_2", "Cedar Group",           "Digital Marketing",      "Marketing","Nexum UK",   "France",   "Laura Dupont",    "Won", "01/09/2026",  85000, "EUR"),
    ("P00097_1", "Ironside Tech",         "M&A Support",            "Finance", "Nexum UK",    "Germany",  "James Thornton",  "Won", "07/09/2026", 310000, "EUR"),
    ("P00098_1", "Quorum Staffing",       "Payroll Advisory",       "HR",      "Nexum UK",    "UK",       "Ana Ferreira",    "Won", "05/10/2026",  75000, "GBP"),
    ("P00099_1", "Greenvale Retail",      "Customer Experience",    "Marketing","Nexum EMEA", "Spain",    "Laura Dupont",    "Won", "12/10/2026", 140000, "EUR"),
    ("P00100_1", "Dalton Manufacturing",  "Training & Development", "HR",      "Nexum EMEA",  "Germany",  "Sarah Mitchell",  "Won", "02/11/2026",  90000, "EUR"),
    ("P00101_1", "Larchwood Services",    "CFO Advisory",           "Finance", "Nexum EMEA",  "Spain",    "James Thornton",  "Won", "09/11/2026", 280000, "EUR"),
    ("P00102_1", "Thornton Pharma",       "Recruitment",            "HR",      "Nexum UK",    "France",   "Sarah Mitchell",  "Won", "01/12/2026",  55000, "EUR"),
    ("P00103_1", "Optica Ventures",       "Market Research",        "Marketing","Nexum EMEA", "Portugal", "Michael Chen",    "Won", "08/12/2026",  70000, "EUR"),
]

for fw in FUTURE_WON:
    pid, client, bu, act, entity, geo, lead, stage, sd_str, rev, cur = fw
    sd = date(int(sd_str[6:]), int(sd_str[3:5]), int(sd_str[:2]))
    ed = end_date(sd, bu, pid)
    rows.append({
        "Project ID": pid, "Client": client, "Business Unit": bu, "Activity": act,
        "Entity": entity, "Geography": geo, "Commercial Lead": lead, "Stage": stage,
        "Start Date": sd_str, "End Date": fmt(ed), "Revenue": rev, "Currency": cur,
        "New/Existing": "", "Weighted %": "", "Weighted Pipeline": "",
    })

# Compute New/Existing (first deal per client chronologically = New Business)
rows.sort(key=lambda r: r["Start Date"][-4:] + r["Start Date"][3:5] + r["Start Date"][:2])
seen_clients = set()
for r in rows:
    c = r["Client"]
    if c not in seen_clients:
        r["New/Existing"] = "New Business"
        seen_clients.add(c)
    else:
        r["New/Existing"] = "Existing Business"

with open("input_pipeline.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for r in rows:
        w.writerow(r)

print(f"Pipeline: {len(rows)} rows written")

# ── BUDGET ────────────────────────────────────────────────────────────────────
# Rebuild as annual/project-based contracts — same columns as pipeline
# Retainers → one row per annual contract period
# Weighted % and Weighted Pipeline are blank (Won only in budget)

BUDGET = [
    # (proj_id, client, bu, activity, entity, geo, lead, start, end, revenue, currency)
    # Albatross Foods — HR Compliance retainer, 2-year contract
    ("B00001_1","Albatross Foods","HR Compliance","HR","Nexum EMEA","Spain","Ana Ferreira",
     "01/01/2025","31/12/2026", 600000, "EUR"),

    # Ironside Tech — CFO Advisory, annual retainers
    ("B00002_1","Ironside Tech","CFO Advisory","Finance","Nexum UK","Germany","James Thornton",
     "06/01/2025","19/12/2025", 192000, "EUR"),
    ("B00002_1","Ironside Tech","CFO Advisory","Finance","Nexum UK","Germany","James Thornton",
     "05/01/2026","18/12/2026", 200000, "EUR"),

    # Juniper Capital — M&A Support, annual retainers (split: M&A + Financial Planning)
    ("B00003_1","Juniper Capital","M&A Support","Finance","Nexum EMEA","UK","James Thornton",
     "03/01/2025","19/12/2025", 280000, "GBP"),
    ("B00003_2","Juniper Capital","Financial Planning","Finance","Nexum UK","UK","James Thornton",
     "03/01/2025","19/12/2025", 112000, "GBP"),
    ("B00003_1","Juniper Capital","M&A Support","Finance","Nexum EMEA","UK","James Thornton",
     "05/01/2026","18/12/2026", 300000, "GBP"),
    ("B00003_2","Juniper Capital","Financial Planning","Finance","Nexum UK","UK","James Thornton",
     "05/01/2026","18/12/2026", 120000, "GBP"),

    # Westmore Finance — Tax Optimization, annual
    ("B00004_1","Westmore Finance","Tax Optimization","Finance","Nexum UK","UK","James Thornton",
     "10/02/2025","28/11/2025", 152000, "GBP"),
    ("B00004_1","Westmore Finance","Tax Optimization","Finance","Nexum UK","UK","James Thornton",
     "09/02/2026","27/11/2026", 160000, "GBP"),

    # Solaris Energy — Financial Planning, annual
    ("B00005_1","Solaris Energy","Financial Planning","Finance","Nexum EMEA","Germany","James Thornton",
     "03/03/2025","12/12/2025", 208000, "EUR"),
    ("B00005_1","Solaris Energy","Financial Planning","Finance","Nexum EMEA","Germany","James Thornton",
     "02/03/2026","11/12/2026", 220000, "EUR"),

    # Meridian Healthcare — Customer Experience, bi-annual project (Mar & Sep each year)
    ("B00006_1","Meridian Healthcare","Customer Experience","Marketing","Nexum EMEA","France","Laura Dupont",
     "03/03/2025","08/08/2025",  58000, "EUR"),
    ("B00006_1","Meridian Healthcare","Customer Experience","Marketing","Nexum EMEA","France","Laura Dupont",
     "01/09/2025","05/12/2025",  58000, "EUR"),
    ("B00006_1","Meridian Healthcare","Customer Experience","Marketing","Nexum EMEA","France","Laura Dupont",
     "02/03/2026","07/08/2026",  62000, "EUR"),
    ("B00006_1","Meridian Healthcare","Customer Experience","Marketing","Nexum EMEA","France","Laura Dupont",
     "01/09/2026","04/12/2026",  62000, "EUR"),

    # Fairway Logistics — HR Transformation, bi-annual (Jun & Dec)
    ("B00007_1","Fairway Logistics","HR Transformation","HR","Nexum EMEA","Portugal","Sarah Mitchell",
     "02/06/2025","14/11/2025",  62000, "EUR"),
    ("B00007_1","Fairway Logistics","HR Transformation","HR","Nexum EMEA","Portugal","Sarah Mitchell",
     "01/12/2025","27/03/2026",  62000, "EUR"),
    ("B00007_1","Fairway Logistics","HR Transformation","HR","Nexum EMEA","Portugal","Sarah Mitchell",
     "01/06/2026","13/11/2026",  65000, "EUR"),
    ("B00007_1","Fairway Logistics","HR Transformation","HR","Nexum EMEA","Portugal","Sarah Mitchell",
     "01/12/2026","31/12/2026",  65000, "EUR"),  # starts Dec, continues into 2027

    # Redbridge Media — Digital Marketing (contracted Jan 2025 – Jan 2026)
    ("B00008_1","Redbridge Media","Digital Marketing","Marketing","Nexum UK","UK","Laura Dupont",
     "07/01/2025","04/07/2025",  42000, "GBP"),
    ("B00008_1","Redbridge Media","Digital Marketing","Marketing","Nexum UK","UK","Laura Dupont",
     "07/07/2025","09/01/2026",  42000, "GBP"),
    ("B00008_1","Redbridge Media","Digital Marketing","Marketing","Nexum UK","UK","Laura Dupont",
     "12/01/2026","26/06/2026",  45000, "GBP"),

    # TBD new expected wins
    ("B00009_1","TBD","Recruitment","HR","Nexum EMEA","Spain","Sarah Mitchell",
     "05/01/2026","06/02/2026",  80000, "EUR"),
    ("B00010_1","TBD","Brand Strategy","Marketing","Nexum UK","Italy","Laura Dupont",
     "02/03/2026","20/04/2026",  95000, "EUR"),
    ("B00011_1","TBD","Accounting Transformation","Finance","Nexum UK","France","James Thornton",
     "04/05/2026","11/09/2026", 150000, "EUR"),
    ("B00011_2","TBD","HR Transformation","HR","Nexum EMEA","France","Ana Ferreira",
     "04/05/2026","28/08/2026",  70000, "EUR"),
    ("B00012_1","TBD","Digital Marketing","Marketing","Nexum EMEA","Germany","Michael Chen",
     "03/08/2026","30/10/2026", 110000, "EUR"),
    ("B00013_1","TBD","CFO Advisory","Finance","Nexum LATAM","Portugal","James Thornton",
     "05/10/2026","26/03/2027", 180000, "EUR"),
]

budget_rows = []
for b in BUDGET:
    pid, client, bu, act, entity, geo, lead, sd, ed, rev, cur = b
    budget_rows.append({
        "Project ID": pid, "Client": client, "Business Unit": bu, "Activity": act,
        "Entity": entity, "Geography": geo, "Commercial Lead": lead, "Stage": "Won",
        "Start Date": sd, "End Date": ed, "Revenue": rev, "Currency": cur,
        "New/Existing": "", "Weighted %": "", "Weighted Pipeline": "",
    })

# Sort and compute New/Existing for budget
budget_rows.sort(key=lambda r: r["Start Date"][-4:] + r["Start Date"][3:5] + r["Start Date"][:2])
seen_budget = set()
for r in budget_rows:
    c = r["Client"]
    if c == "TBD":
        r["New/Existing"] = "New Business"
        continue
    if c not in seen_budget:
        r["New/Existing"] = "New Business"
        seen_budget.add(c)
    else:
        r["New/Existing"] = "Existing Business"

with open("input_budget.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for r in budget_rows:
        w.writerow(r)

print(f"Budget: {len(budget_rows)} rows written")
