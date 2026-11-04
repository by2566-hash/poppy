You are grading ONE output of a data-analysis agent against a written standard. The chart is attached as an image.
Judge from the materials below only. Do not fix anything, do not redo the analysis. For each item answer PASS or FAIL
(NA if the item does not apply to this output) and quote the sentence, number or chart element that decides it.
Be strict: a limitation that matters but is not stated is a FAIL on the item that asks for it.
If the QUESTION TYPE is "insufficient", the data cannot answer the question as asked; the appropriate output states that
(required_statement) and shows a measure the data does support. Do not FAIL c1 or c2 merely because the measure is not the
one the question named (e.g. not per mile); FAIL them only if the output pretends to answer the unanswerable question.
Rules that follow from the written standard (SCORING.md section 4):
- The DECLARED FRAMING fields are part of the output: a definition given there (e.g. which hours count as night) counts as stated.
- c6 FAILs whenever a disclosure item below (TR.., NIGHTDEF, ...) FAILs: an undisclosed exclusion or an uncaveated denominator is a
  limitation that matters, and an exposure disclaimer does not make up for it. c6 also FAILs when a superlative or comparison in the
  prose (largest, smallest, peak, doubled) is contradicted by the values table.
- Do not invent limitations: rely on DATA FACTS for what is partial, missing or NULL.
- c5: a y-axis that does not start at zero is not a distortion on a line chart when the axis is labelled; on a bar chart it is a FAIL.

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: How are NYC crashes distributed across the days of the week, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Crash-record count
denominator: No normalization; total crash records in 2013–2025
grouping: Day of week, Monday through Sunday
chart_type: Vertical bar chart
probability: 0.55
WRITTEN ANSWER:
Friday had the most recorded crashes (338,800) and Sunday the fewest (257,544) among 2,132,218 crashes. This answers how the total 2013–2025 crash records split among weekdays: Friday leads and Sunday trails. A weekday count chart is a direct descriptive distribution of recorded events; it leaves unanswered the per-date rate and does not adjust for traffic exposure.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crashes
Monday,304518
Tuesday,313488
Wednesday,311111
Thursday,318376
Friday,338800
Saturday,288381
Sunday,257544

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT MIN(crash_date), MAX(crash_date), COUNT(*), COUNT(*) FILTER (WHERE crash_date IS NULL) FROM read_parquet(?)", [p]).fetchall()); print(c.execute("SELECT EXTRACT(year FROM crash_date)::INT AS year, COUNT(*) AS crashes FROM read_parquet(?) GROUP BY 1 ORDER BY 1", [p]).fetchall())'
# bash
ls -ld . data
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("SELECT CASE EXTRACT(dow FROM crash_date)::INT WHEN 0 THEN 7 ELSE EXTRACT(dow FROM crash_date)::INT END AS iso_dow, strftime(crash_date, %s) AS weekday, COUNT(*) AS crashes FROM read_parquet(?) WHERE crash_date >= DATE %s AND crash_date < DATE %s GROUP BY 1,2 ORDER BY 1", ["%A", p, "2013-01-01", "2026-01-01"]).fetchall()); print(c.execute("SELECT COUNT(*), MIN(crash_date), MAX(crash_date) FROM read_parquet(?) WHERE crash_date >= DATE %s AND crash_date < DATE %s", [p, "2013-01-01", "2026-01-01"]).fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("SELECT CASE EXTRACT(dow FROM crash_date)::INT WHEN 0 THEN 7 ELSE EXTRACT(dow FROM crash_date)::INT END AS iso_dow, strftime(crash_date, \u0027%A\u0027) AS weekday, COUNT(*) AS crashes FROM read_parquet(?) WHERE crash_date >= DATE \u00272013-01-01\u0027 AND crash_date < DATE \u00272026-01-01\u0027 GROUP BY 1,2 ORDER BY 1", [p]).fetchall()); print(c.execute("SELECT COUNT(*), MIN(crash_date), MAX(crash_date) FROM read_parquet(?) WHERE crash_date >= DATE \u00272013-01-01\u0027 AND crash_date < DATE \u00272026-01-01\u0027", [p]).fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); print(c.execute("SELECT EXTRACT(dow FROM d)::INT, strftime(d, \u0027%A\u0027), COUNT(*) FROM generate_series(DATE \u00272013-01-01\u0027, DATE \u00272025-12-31\u0027, INTERVAL 1 DAY) t(d) GROUP BY 1,2 ORDER BY CASE EXTRACT(dow FROM d)::INT WHEN 0 THEN 7 ELSE EXTRACT(dow FROM d)::INT END").fetchall())'
# bash
python3 - <<'PY'
import os, json
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("out", exist_ok=True)
con = duckdb.connect()
parquet = "data/crashes.parquet"
counts = con.execute("""
    SELECT CASE EXTRACT(dow FROM crash_date)::INT
             WHEN 0 THEN 7 ELSE EXTRACT(dow FROM crash_date)::INT
           END AS weekday_order,
           strftime(crash_date, '%A') AS weekday,
           COUNT(*)::BIGINT AS crashes
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY 1, 2
    ORDER BY 1
""", [parquet]).df()
days = con.execute("""
    SELECT CASE EXTRACT(dow FROM d)::INT
             WHEN 0 THEN 7 ELSE EXTRACT(dow FROM d)::INT
           END AS weekday_order,
           COUNT(*)::INT AS calendar_days
    FROM generate_series(DATE '2013-01-01', DATE '2025-12-31', INTERVAL 1 DAY) AS t(d)
    GROUP BY 1 ORDER BY 1
""").df()
data = counts.merge(days, on="weekday_order").sort_values("weekday_order")
data["average_crashes_per_calendar_day"] = data["crashes"] / data["calendar_days"]

# Option 1: aggregate crash counts by weekday.
values1 = data[["weekday", "crashes"]].copy()
values1.to_csv("out/values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(9, 5.2))
bars = ax.bar(data["weekday"], data["crashes"], color="#2878B5")
ax.bar_label(bars, labels=[f"{v:,.0f}" for v in data["crashes"]], padding=3, fontsize=9)
ax.set_title("NYC police-reported crashes by weekday, 2013–2025")
ax.set_ylabel("Crash records")
ax.set_xlabel("Day of week")
ax.set_ylim(0, max(data["crashes"]) * 1.12)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("out/option_1.png", dpi=160)
plt.close(fig)

# Option 2: normalize crash counts by the number of calendar dates for each weekday.
values2 = data[["weekday", "calendar_days", "crashes", "average_crashes_per_calendar_day"]].copy()
values2.to_csv("out/values_2.csv", index=False)
fig, ax = plt.subplots(figsize=(9, 5.2))
bars = ax.bar(data["weekday"], data["average_crashes_per_calendar_day"], color="#E07A32")
ax.bar_label(bars, labels=[f"{v:,.1f}" for v in data["average_crashes_per_calendar_day"]], padding=3, fontsize=9)
ax.set_title("Average NYC police-reported crashes per weekday date, 2013–2025")
ax.set_ylabel("Average crash records per calendar date")
ax.set_xlabel("Day of week")
ax.set_ylim(0, max(data["average_crashes_per_calendar_day"]) * 1.12)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("out/option_2.png", dpi=160)
plt.close(fig)

print(data.to_string(index=False))
print("Total crashes:", int(data["crashes"].sum()))
PY
# bash
python3 - <<'PY'
import json, os
import pandas as pd
with open("out/options.json", encoding="utf-8") as f:
    options = json.load(f)["options"]
assert abs(sum(o["probability"] for o in options) - 1.0) < 1e-12
for option in options:
    idx = option["id"]
    assert os.path.getsize(f"out/option_{idx}.png") > 0
    values = pd.read_csv(f"out/values_{idx}.csv")
    assert len(values) == 7
assert int(pd.read_csv("out/values_1.csv")["crashes"].sum()) == 2132218
print("Validated options.json, both charts and CSVs; probabilities sum to 1.0 and totals match.")
PY

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_DAYCOUNT: If per-day averages or 'X% fewer on <day>' comparisons are given, the arithmetic is right (e.g. Sunday has 24% fewer than the mean weekday, Friday 32% more) and unequal day counts (678/679) are handled or noted.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.