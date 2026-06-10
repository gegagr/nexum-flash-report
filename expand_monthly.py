from datetime import date, timedelta
import calendar
import csv

COLS = [
    "Project ID", "Client", "Business Unit", "Activity", "Entity", "Geography",
    "Commercial Lead", "Stage", "Start Date", "End Date",
    "Month", "Year", "Revenue", "Currency", "New/Existing",
    "Weighted %", "Weighted Pipeline",
]

def parse_date(s):
    d, m, y = s.split("/")
    return date(int(y), int(m), int(d))

def fmt(d):
    return d.strftime("%d/%m/%Y")

def working_days(start, end):
    """Count Mon–Fri days in [start, end] inclusive."""
    count = 0
    d = start
    while d <= end:
        if d.weekday() < 5:
            count += 1
        d += timedelta(days=1)
    return count

def months_in_range(start, end):
    y, m = start.year, start.month
    while date(y, m, 1) <= end:
        yield y, m
        m += 1
        if m > 12:
            m = 1; y += 1

def month_overlap(start, end, year, month):
    last = calendar.monthrange(year, month)[1]
    ms = max(start, date(year, month, 1))
    me = min(end, date(year, month, last))
    return (ms, me) if ms <= me else (None, None)

def expand(input_path, output_path):
    with open(input_path) as f:
        rows = list(csv.DictReader(f))

    out = []
    for r in rows:
        sd = parse_date(r["Start Date"])
        ed = parse_date(r["End Date"])
        total_rev = float(r["Revenue"])
        total_wd = working_days(sd, ed) or 1

        raw_wp = r.get("Weighted %", "").strip().replace("%", "")
        weighted_pct = float(raw_wp) / 100 if raw_wp else None

        for y, m in months_in_range(sd, ed):
            ms, me = month_overlap(sd, ed, y, m)
            if ms is None:
                continue
            wd = working_days(ms, me)
            monthly_rev = round(total_rev * wd / total_wd, 2)

            if weighted_pct is not None:
                monthly_wp = round(monthly_rev * weighted_pct, 2)
                wp_str = f"{int(weighted_pct*100)}%"
            else:
                monthly_wp = ""
                wp_str = ""

            out.append({
                "Project ID":       r["Project ID"],
                "Client":           r["Client"],
                "Business Unit":    r["Business Unit"],
                "Activity":         r["Activity"],
                "Entity":           r["Entity"],
                "Geography":        r["Geography"],
                "Commercial Lead":  r["Commercial Lead"],
                "Stage":            r["Stage"],
                "Start Date":       r["Start Date"],
                "End Date":         r["End Date"],
                "Month":            m,
                "Year":             y,
                "Revenue":          monthly_rev,
                "Currency":         r["Currency"],
                "New/Existing":     r["New/Existing"],
                "Weighted %":       wp_str,
                "Weighted Pipeline": monthly_wp,
            })

    with open(output_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(out)

    print(f"{output_path}: {len(rows)} projects → {len(out)} monthly rows")

expand("input_pipeline.csv", "input_pipeline.csv")
expand("input_budget.csv",   "input_budget.csv")
