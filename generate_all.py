"""
Generate input_pipeline.csv and input_budget.csv for the flash-report mock-up.

Story
-----
- Consulting firm (Nexum) for SMEs. 3 activities x 5 business units, 6 geographies.
- 2025: did EUR 43M against a EUR 44.5M budget (slightly under, mixed months).
- 2026: target EUR 50M = 2025 budget + EUR 3M from opening Portugal + 1-8%
  growth per existing geography.
- January always lands at/above budget (best visibility month of the year).
- Moderate seasonality: August and December dip but business continues.
- Every business unit x geography has revenue in BOTH files every month
  (anchored by annual framework retainers). Portugal exists only from 2026.
- Narrative: France & Italy beat budget, Germany underperforms, UK & Spain
  in line, Portugal launch slightly ahead of plan. Tax Optimization and
  Customer Experience overperform; HR Transformation and Recruitment lag.
- Report cutoff: early June 2026. Until May 2026 everything is Won/Lost;
  June 2026 onwards mixes Won (backlog) and Pending (weighted pipeline).
"""
import random, csv, calendar
from collections import defaultdict
from datetime import date, timedelta

RNG    = random.Random(42)
CUTOFF = date(2026, 6, 1)          # report run date (data as of)
P_END  = date(2026, 12, 31)

# ── Dimensions ────────────────────────────────────────────────────────────────
GEO = {
    "UK":       {"cur": "GBP", "entity": "Nexum UK"},
    "Germany":  {"cur": "EUR", "entity": "Nexum EMEA"},
    "France":   {"cur": "EUR", "entity": "Nexum EMEA"},
    "Italy":    {"cur": "EUR", "entity": "Nexum EMEA"},
    "Spain":    {"cur": "EUR", "entity": "Nexum Iberia"},
    "Portugal": {"cur": "EUR", "entity": "Nexum Iberia"},
}

LEADS = {
    "UK":       ["Emma Clarke", "James Thornton", "Oliver Hayes"],
    "Germany":  ["Tom Becker", "Luisa Meier", "Stefan Krause"],
    "France":   ["Laura Dupont", "Pierre Moreau", "Camille Roussel"],
    "Spain":    ["Sarah Mitchell", "Carlos Vega", "Marta Iglesias"],
    "Portugal": ["Ana Ferreira", "Inês Costa", "Miguel Santos"],
    "Italy":    ["Giulia Romano", "Michael Chen", "Marco Bellini"],
}

CLIENTS_BY_GEO = {
    "UK": ["Brennan & Associates","Juniper Capital","Quorum Staffing","Redbridge Media",
           "Westmore Finance","Hartwell Group","Sterling Dynamics","Pennington & Co",
           "Blackthorn Capital","Oakfield Partners","Cromwell Partners","Ashford Industries",
           "Devlin & Sons","Kingsford Capital","Whitmore Consulting"],
    "Germany": ["Dalton Manufacturing","Ironside Tech","Northfield Construction","Solaris Energy",
           "Xero Dynamics","Bergmann GmbH","Kessler Industries","Rhein Partners",
           "Fischer & Weber","Steinberg Digital","Müller & Partner","Heinz Group",
           "Dortmund Services","Bremen Digital","Hannover Capital"],
    "France": ["Cedar Group","Harbourside Hotels","Meridian Healthcare","Thornton Pharma",
           "Lumière Retail","Dupont Finances","Girard & Associés","Marceau Logistics",
           "Beaumont Digital","Fontaine Capital","Leclerc Associés","Renaud Capital",
           "Chevalier & Fils","Normandie Digital","Bordeaux Finance"],
    "Spain": ["Albatross Foods","Greenvale Retail","Larchwood Services","Uniform Industries",
           "Iberia Ventures","Castillo & Partners","Montserrat Group","Nexo Digital",
           "Solano Industries","Verdana Holdings","Sevilla Capital","Barcelona Ventures",
           "Madrid Consulting","Valencia Group","Bilbao Partners"],
    "Portugal": ["Fairway Logistics","Optica Ventures","Vantage Retail","Atlântico Services",
           "Tejo Capital","Porto Innovations","Lusitano Consulting","Braga Partners",
           "Lisboa Capital","Coimbra Group","Setúbal Industries","Évora Partners"],
    "Italy": ["Ergo Solutions","Kendall & Partners","Pinnacle Exports","Yardarm Shipping",
           "Milano Ventures","Rossi & Figli","Torino Digital","Firenze Consulting",
           "Napoli Ventures","Venezia Digital"],
}

ACTIVITIES = {
    "HR":       ["Recruitment","Training & Development","HR Transformation","Payroll Advisory","HR Compliance"],
    "Finance":  ["CFO Advisory","Financial Planning","Tax Optimization","M&A Support","Accounting Transformation"],
    "Marketing":["Brand Strategy","Digital Marketing","Market Research","Sales Enablement","Customer Experience"],
}
ALL_BUS = [bu for bus in ACTIVITIES.values() for bu in bus]
BU_ACT  = {bu: act for act, bus in ACTIVITIES.items() for bu in bus}

# Revenue mix across BUs (shares of a geography's budget; sums to 1.0)
BU_MIX = {
    "CFO Advisory": 0.14, "M&A Support": 0.11, "Accounting Transformation": 0.09,
    "Financial Planning": 0.08, "Tax Optimization": 0.05,
    "HR Transformation": 0.09, "Recruitment": 0.05, "Payroll Advisory": 0.04,
    "Training & Development": 0.04, "HR Compliance": 0.04,
    "Customer Experience": 0.07, "Digital Marketing": 0.06, "Brand Strategy": 0.05,
    "Sales Enablement": 0.05, "Market Research": 0.04,
}

# Typical project duration in calendar days
BU_DUR = {
    "Recruitment": (21, 42),  "Training & Development": (28, 56),
    "HR Transformation": (84, 150), "Payroll Advisory": (42, 70), "HR Compliance": (21, 42),
    "CFO Advisory": (112, 210), "Financial Planning": (56, 112), "Tax Optimization": (35, 70),
    "M&A Support": (70, 150), "Accounting Transformation": (84, 170),
    "Brand Strategy": (35, 70), "Digital Marketing": (49, 91), "Market Research": (21, 42),
    "Sales Enablement": (42, 84), "Customer Experience": (56, 112),
}

# ── Targets ───────────────────────────────────────────────────────────────────
# Budget per geography. 2025 sums to 44.5M; 2026 to exactly 50.0M:
# +3.0M from opening Portugal, existing geos grow 1.5%-8%.
GEO_BUDGET = {
    "UK":       {2025: 14.00e6, 2026: 15.05e6},   # +7.5%
    "Germany":  {2025: 10.30e6, 2026: 10.45e6},   # +1.5%
    "France":   {2025:  8.90e6, 2026:  9.61e6},   # +8.0%
    "Spain":    {2025:  7.70e6, 2026:  8.16e6},   # +6.0%
    "Italy":    {2025:  3.60e6, 2026:  3.73e6},   # +3.6%
    "Portugal": {2025:  0.00,   2026:  3.00e6},   # new market
}

# Actual performance vs budget per geo-year (2025 actuals land at ~43.0M)
GEO_PERF = {
    ("UK", 2025): 0.96,      ("UK", 2026): 0.99,
    ("Germany", 2025): 0.905,("Germany", 2026): 0.93,   # the problem child
    ("France", 2025): 1.02,  ("France", 2026): 1.05,    # overdelivering
    ("Spain", 2025): 0.955,  ("Spain", 2026): 0.98,
    ("Italy", 2025): 0.97,   ("Italy", 2026): 1.03,     # small but beating
    ("Portugal", 2026): 1.05,                            # launch ahead of plan
}

# Project start-month phasing (mirrors how budget contracts phase the year:
# heavy Feb-May and Sep-Oct, thin around Christmas and high summer).
START_MONTH_W = [0.5, 1.2, 1.3, 1.3, 1.2, 0.9, 0.7, 0.9, 1.3, 1.2, 0.7, 0.3]

# BU narrative vs budget (weighted average ~1.0 so geo stories are preserved)
BU_TARGET = {
    "Tax Optimization": 1.18, "Customer Experience": 1.10, "M&A Support": 1.07,
    "Market Research": 1.05, "Training & Development": 1.04, "HR Compliance": 1.03,
    "Brand Strategy": 1.02, "Payroll Advisory": 1.01,
    "Accounting Transformation": 1.00, "CFO Advisory": 0.99, "Digital Marketing": 0.99,
    "Sales Enablement": 0.97, "Recruitment": 0.93, "Financial Planning": 0.92,
    "HR Transformation": 0.86,
}

# Moderate seasonality — August and Christmas dip, business continues.
SEASONAL = {1: 0.97, 2: 1.00, 3: 1.04, 4: 1.03, 5: 1.03, 6: 1.00,
            7: 0.92, 8: 0.85, 9: 1.02, 10: 1.04, 11: 1.02, 12: 0.90}

# Future months (after cutoff): how much of the target is already secured.
COVERAGE = {6: 1.00, 7: 0.99, 8: 0.98, 9: 0.97, 10: 0.96, 11: 0.95, 12: 0.94}
BACKLOG  = {6: 0.99, 7: 0.92, 8: 0.85, 9: 0.78, 10: 0.70, 11: 0.62, 12: 0.55}

# Per-geo BU mix variation (fixed seed: stable between runs)
MIX_RNG = random.Random(11)
GEO_MIX = {}
for g in GEO:
    raw = {bu: BU_MIX[bu] * MIX_RNG.uniform(0.85, 1.15) for bu in ALL_BUS}
    s = sum(raw.values())
    GEO_MIX[g] = {bu: v / s for bu, v in raw.items()}

# Anchor (recurring) client per geo x BU — powers the framework retainers
ANCHORS = {}
for g, roster in CLIENTS_BY_GEO.items():
    ANCHORS[g] = {bu: roster[i % len(roster)] for i, bu in enumerate(ALL_BUS)}

def geo_years(g):
    return [2026] if g == "Portugal" else [2025, 2026]

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt(d):   return d.strftime("%d/%m/%Y")
def parse(s):
    d, m, y = s.split("/"); return date(int(y), int(m), int(d))

def working_days(s, e):
    n, d = 0, s
    while d <= e:
        if d.weekday() < 5: n += 1
        d += timedelta(days=1)
    return n or 1

def months_in(s, e):
    y, m = s.year, s.month
    while date(y, m, 1) <= e:
        yield y, m
        m += 1
        if m > 12: m, y = 1, y + 1

def overlap(s, e, y, m):
    last = calendar.monthrange(y, m)[1]
    ms = max(s, date(y, m, 1)); me = min(e, date(y, m, last))
    return (ms, me) if ms <= me else (None, None)

def expand(rows):
    """One row per project per month; revenue spread by seasonal working days."""
    out = []
    for r in rows:
        sd, ed = parse(r["Start Date"]), parse(r["End Date"])
        total_rev = float(r["Revenue"])
        raw = r.get("Weighted %", "").strip().replace("%", "")
        wpct = float(raw) / 100 if raw else None
        denom = sum(
            SEASONAL[m] * working_days(*overlap(sd, ed, y, m))
            for y, m in months_in(sd, ed)
            if overlap(sd, ed, y, m)[0] is not None
        ) or 1
        for y, m in months_in(sd, ed):
            ms, me = overlap(sd, ed, y, m)
            if ms is None: continue
            mrev = total_rev * SEASONAL[m] * working_days(ms, me) / denom
            out.append({**r,
                "Month": m, "Year": y, "Revenue": mrev,
                "Weighted %":        f"{int(wpct*100)}%" if wpct else "",
                "Weighted Pipeline": mrev * wpct if wpct else "",
            })
    return out

def assign_new_existing(rows):
    """First chronological deal per client = New Business. TBD always new."""
    rows.sort(key=lambda r: (parse(r["Start Date"]), r["Project ID"]))
    seen = set()
    for r in rows:
        c = r["Client"]
        if c == "TBD" or c not in seen:
            r["New/Existing"] = "New Business"
            if c != "TBD": seen.add(c)
        else:
            r["New/Existing"] = "Existing Business"
    return rows

# ── Budget generation ─────────────────────────────────────────────────────────
def gen_budget():
    rows, bid = [], 1
    for g in GEO:
        for y in geo_years(g):
            B = GEO_BUDGET[g][y]
            if B <= 0: continue
            for bu in ALL_BUS:
                A = B * GEO_MIX[g][bu]
                # Annual framework retainer with the anchor client → guarantees
                # budget revenue for this BU x geo in every month of the year.
                ret_share = RNG.uniform(0.55, 0.70)
                rows.append(dict(pid=f"B{bid:05d}_1", client=ANCHORS[g][bu], bu=bu,
                                 geo=g, sd=f"01/01/{y}", ed=f"31/12/{y}",
                                 rev=round(A * ret_share, -2)))
                bid += 1
                # Remainder: 1-2 planned projects (known clients or TBD)
                R = A * (1 - ret_share)
                n = 1 if R < 150000 else 2
                for j in range(n):
                    rev = R / n
                    sm  = RNG.choice([2, 3, 4, 5]) if j == 0 else RNG.choice([7, 8, 9])
                    sd  = date(y, sm, RNG.randint(1, 14))
                    ed  = sd + timedelta(days=RNG.randint(60, 130))
                    if ed > date(y, 12, 31): ed = date(y, 12, 31)
                    if y == 2026:
                        p_tbd = 0.70 if g == "Portugal" else 0.30
                    else:
                        p_tbd = 0.12
                    client = "TBD" if RNG.random() < p_tbd else RNG.choice(CLIENTS_BY_GEO[g])
                    rows.append(dict(pid=f"B{bid:05d}_1", client=client, bu=bu,
                                     geo=g, sd=fmt(sd), ed=fmt(ed), rev=round(rev, -2)))
                    bid += 1

    out = []
    for r in rows:
        g = r["geo"]
        out.append({
            "Project ID": r["pid"], "Client": r["client"],
            "Business Unit": r["bu"], "Activity": BU_ACT[r["bu"]],
            "Entity": GEO[g]["entity"], "Geography": g,
            "Commercial Lead": LEADS[g][0], "Stage": "Won",
            "Start Date": r["sd"], "End Date": r["ed"],
            "Revenue": r["rev"], "Currency": GEO[g]["cur"],
            "New/Existing": "", "Weighted %": "", "Weighted Pipeline": "",
        })
    return assign_new_existing(out)

# ── Pipeline generation ───────────────────────────────────────────────────────
def pick_stage(sd, ed):
    if ed < CUTOFF:                                   # decided in the past
        return ("Won" if RNG.random() < 0.78 else "Lost"), ""
    if sd < CUTOFF:                                   # signed and running
        return "Won", ""
    months_out = (sd.year - 2026) * 12 + sd.month - 6
    if RNG.random() < max(0.30, 0.88 - 0.10 * months_out):
        return "Won", ""
    if months_out <= 1:   pct = 75
    elif months_out <= 3: pct = RNG.choice([50, 75])
    else:                 pct = RNG.choice([25, 50])
    return "Pending", f"{pct}%"

SOW_PIDS = set()   # framework monthly billing orders (excluded from deal stats)

def gen_pipeline():
    rows, pid = [], 1

    def add(client, bu, g, stage, wpct, sd, ed, rev, split_no=1, base_pid=None):
        nonlocal pid
        if base_pid is None:
            base_pid = pid; pid += 1
        rows.append(dict(pid=f"P{base_pid:05d}_{split_no}", client=client, bu=bu,
                         geo=g, stage=stage, wpct=wpct,
                         sd=fmt(sd), ed=fmt(ed), rev=rev))
        return base_pid

    for g in GEO:
        for y in geo_years(g):
            for bu in ALL_BUS:
                T = (GEO_BUDGET[g][y] * GEO_MIX[g][bu]
                     * GEO_PERF[(g, y)] * BU_TARGET.get(bu, 1.0))
                anchor = ANCHORS[g][bu]

                # Framework retainer billed as monthly SOWs (all Won — the
                # annual frame is signed) → actuals exist for this BU x geo in
                # every month, and every month can flex independently.
                for sm in range(1, 13):
                    sd = date(y, sm, 5 if (g == "Portugal" and sm == 1) else 1)
                    ed = date(y, sm, calendar.monthrange(y, sm)[1])
                    bp = add(anchor, bu, g, "Won", "", sd, ed, T * 0.5 / 12)
                    SOW_PIDS.add(f"P{bp:05d}_1")

                # Project deals on top
                n = 2 + (T > 350000) + (T > 700000) + (T > 1100000)
                for _ in range(n):
                    sm = RNG.choices(range(1, 13), weights=START_MONTH_W)[0]
                    sd = date(y, sm, RNG.randint(1, 25))
                    dur = RNG.randint(*BU_DUR[bu])
                    ed = min(sd + timedelta(days=dur), P_END)
                    stage, wpct = pick_stage(sd, ed)
                    rev = T * 0.5 / n * RNG.uniform(0.5, 1.6)
                    bp = add(RNG.choice(CLIENTS_BY_GEO[g]), bu, g, stage, wpct, sd, ed, rev)
                    # ~20% of deals carry a second split in another BU
                    if RNG.random() < 0.20:
                        bu2 = RNG.choice([b for b in ALL_BUS if b != bu])
                        add(rows[-1]["client"], bu2, g, stage, wpct, sd, ed,
                            rev * RNG.uniform(0.3, 0.7), split_no=2, base_pid=bp)

                # Lost deals (decided, past) — keep a realistic ~20-25% loss rate
                for _ in range(max(1, round(n * 0.30))):
                    latest = min(CUTOFF - timedelta(days=40), date(y, 12, 1))
                    earliest = date(y, 1, 1)
                    if earliest >= latest: continue
                    span = (latest - earliest).days
                    sd = earliest + timedelta(days=RNG.randint(0, span))
                    ed = min(sd + timedelta(days=RNG.randint(*BU_DUR[bu])), P_END)
                    add(RNG.choice(CLIENTS_BY_GEO[g]), bu, g, "Lost", "",
                        sd, ed, T * 0.5 / n * RNG.uniform(0.5, 1.4))

                # Pending deals for the future fan (2026 only)
                if y == 2026:
                    for _ in range(2):
                        sd = date(2026, RNG.randint(7, 11), RNG.randint(1, 25))
                        ed = min(sd + timedelta(days=RNG.randint(*BU_DUR[bu])), P_END)
                        months_out = sd.month - 6
                        pct = 75 if months_out <= 2 else (50 if months_out <= 4 else RNG.choice([25, 50]))
                        add(RNG.choice(CLIENTS_BY_GEO[g]), bu, g, "Pending", f"{pct}%",
                            sd, ed, T * 0.5 / n * RNG.uniform(0.6, 1.4))

    out = []
    for r in rows:
        g = r["geo"]
        out.append({
            "Project ID": r["pid"], "Client": r["client"],
            "Business Unit": r["bu"], "Activity": BU_ACT[r["bu"]],
            "Entity": GEO[g]["entity"], "Geography": g,
            "Commercial Lead": RNG.choice(LEADS[g]), "Stage": r["stage"],
            "Start Date": r["sd"], "End Date": r["ed"],
            "Revenue": r["rev"], "Currency": GEO[g]["cur"],
            "New/Existing": "", "Weighted %": r["wpct"], "Weighted Pipeline": "",
        })
    return assign_new_existing(out)

# ── Calibration ───────────────────────────────────────────────────────────────
def story_calibrate(pipeline_monthly, budget_monthly):
    """
    Scale projects so monthly actuals per (geo, BU) track
    budget_cell x GEO_PERF x BU_TARGET x noise. January is guaranteed at or
    above budget (best-visibility month). Future months split the target into
    secured backlog (Won) and weighted pipeline (Pending).
    """
    CR = random.Random(7)

    bgt_cell = defaultdict(float)
    for r in budget_monthly:
        y, m = int(r["Year"]), int(r["Month"])
        if y > 2026: continue
        bgt_cell[(r["Geography"], r["Business Unit"], y, m)] += float(r["Revenue"])

    # Month mood shared across geos (makes whole months beat or miss) + geo noise
    mood, gnoise = {}, {}
    def noise(g, y, m):
        if (y, m) not in mood:
            mood[(y, m)] = (CR.uniform(1.02, 1.05) if m == 1
                            else min(1.08, max(0.92, CR.gauss(1.0, 0.04))))
        if (g, y, m) not in gnoise:
            gnoise[(g, y, m)] = min(1.06, max(0.94, CR.gauss(1.0, 0.025)))
        return mood[(y, m)] * gnoise[(g, y, m)]

    def targets(g, bu, y, m):
        perf = GEO_PERF.get((g, y), 1.0)
        if m == 1:
            perf = max(perf, 1.0)        # January always lands
        b = bgt_cell.get((g, bu, y, m), 0.0) * perf * BU_TARGET.get(bu, 1.0) * noise(g, y, m)
        if y == 2026 and m >= 6:
            c, s = COVERAGE[m], BACKLOG[m]
            return b * c * s, b * c * (1 - s)
        return b, 0.0

    projects = defaultdict(list)
    for r in pipeline_monthly:
        projects[r["Project ID"]].append(r)

    def cell_sums():
        won, pend = defaultdict(float), defaultdict(float)
        for r in pipeline_monthly:
            y, m = int(r["Year"]), int(r["Month"])
            if y > 2026: continue
            k = (r["Geography"], r["Business Unit"], y, m)
            if r["Stage"] == "Won":
                won[k] += float(r["Revenue"])
            elif r["Stage"] == "Pending":
                pct = float(r["Weighted %"].replace("%", "")) / 100
                pend[k] += float(r["Revenue"]) * pct
        return won, pend

    pre = defaultdict(float)
    for r in pipeline_monthly:
        if r["Stage"] == "Won" and r["Project ID"] not in SOW_PIDS:
            pre[(r["Geography"], int(r["Year"]))] += float(r["Revenue"])

    for _ in range(10):
        won_sum, pend_sum = cell_sums()
        for pid, rows in projects.items():
            stage = rows[0]["Stage"]
            if stage == "Lost": continue
            num = den = 0.0
            for r in rows:
                y, m = int(r["Year"]), int(r["Month"])
                if y > 2026: continue
                k = (r["Geography"], r["Business Unit"], y, m)
                wt, pt = targets(r["Geography"], r["Business Unit"], y, m)
                rev = float(r["Revenue"])
                if stage == "Won":
                    cur, tgt = won_sum.get(k, 0.0), wt
                else:
                    pct = float(r["Weighted %"].replace("%", "")) / 100
                    cur, tgt = pend_sum.get(k, 0.0), pt
                    rev *= pct
                if cur > 0:
                    num += rev * (tgt / cur); den += rev
            if den > 0:
                f = min(6.0, max(0.15, num / den))
                for r in rows:
                    r["Revenue"] = float(r["Revenue"]) * f

    # Lost deals: rescale per geo-year so sizes stay consistent with Won deals
    # (factor computed on real deals only, framework SOWs excluded)
    post = defaultdict(float)
    for r in pipeline_monthly:
        if r["Stage"] == "Won" and r["Project ID"] not in SOW_PIDS:
            post[(r["Geography"], int(r["Year"]))] += float(r["Revenue"])
    for pid, rows in projects.items():
        if rows[0]["Stage"] != "Lost": continue
        g, y = rows[0]["Geography"], int(rows[0]["Year"])
        f = post[(g, y)] / pre[(g, y)] if pre.get((g, y)) else 1.0
        f = min(2.5, max(0.2, f))
        for r in rows:
            r["Revenue"] = float(r["Revenue"]) * f

    for r in pipeline_monthly:
        r["Revenue"] = round(float(r["Revenue"]), 2)
        raw = r.get("Weighted %", "").strip().replace("%", "")
        if r["Stage"] == "Pending" and raw:
            r["Weighted Pipeline"] = round(r["Revenue"] * float(raw) / 100, 2)
        else:
            r["Weighted Pipeline"] = ""
    return pipeline_monthly

# ── Main ──────────────────────────────────────────────────────────────────────
COLS = ["Project ID","Client","Business Unit","Activity","Entity","Geography",
        "Commercial Lead","Stage","Start Date","End Date",
        "Month","Year","Revenue","Currency","New/Existing",
        "Weighted %","Weighted Pipeline"]

b_rows = gen_budget()
p_rows = gen_pipeline()

budget_monthly = expand(b_rows)
for r in budget_monthly:
    r["Revenue"] = round(r["Revenue"], 2)

pipeline_monthly = expand(p_rows)
pipeline_monthly = story_calibrate(pipeline_monthly, budget_monthly)

def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    return len(rows)

pm = write_csv("input_pipeline.csv", pipeline_monthly)
bm = write_csv("input_budget.csv",   budget_monthly)

print(f"Pipeline : {len(p_rows):4d} project-splits → {pm:5d} monthly rows")
print(f"Budget   : {len(b_rows):4d} contracts      → {bm:5d} monthly rows")
