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
- NA, not PASS, when the claim or element an item is about is absent from the output (e.g. no claim that deaths changed sharply);
  PASS means the claim is present and handled.

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Annual count of motorist deaths in police-reported crashes
denominator: None (annual total)
grouping: Crash year
chart_type: Line chart
probability: 0.55
WRITTEN ANSWER:
Recorded motorist deaths fell from 110 in 2013 to 81 in 2025 (-26.4%), but this does not establish a decline in deaths per mile driven. This framing answers whether the annual count of recorded motorist deaths changed, and the chart shows a lower total in 2025 than in 2013. It is defensible as a measure of fatality burden in the crash records. It leaves the per-mile risk question unanswered because the data contain no miles driven.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_deaths
2013,110
2014,109
2015,95
2016,72
2017,107
2018,98
2019,82
2020,139
2021,134
2022,116
2023,123
2024,111
2025,81

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c 'import duckdb; print(duckdb.__version__); c=duckdb.connect(); print(c.execute("select min(crash_date), max(crash_date), count(*), count(*) filter(where number_of_motorist_killed > 0), sum(number_of_motorist_killed) from read_parquet(\"data/crashes.parquet\")").fetchall())'
# bash
python -c 'import duckdb; c=duckdb.connect(); q="select year(crash_date) y, min(crash_date), max(crash_date), count(*) crashes, sum(coalesce(number_of_motorist_killed,0)) motorist_deaths, count(*) filter(where coalesce(number_of_motorist_killed,0)>0) fatal_crashes, sum(coalesce(number_of_persons_killed,0)) total_deaths from read_parquet(\"data/crashes.parquet\") where year(crash_date) between 2013 and 2025 group by y order by y"; print(c.execute(q).df().to_string(index=False))'
# bash
ls -la
# bash
python -c '
import json, os
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("out", exist_ok=True)
con = duckdb.connect()
query = """
SELECT year(crash_date) AS year,
       count(*) AS reported_crashes,
       sum(coalesce(number_of_motorist_killed, 0)) AS motorist_deaths,
       count(*) FILTER (WHERE coalesce(number_of_motorist_killed, 0) > 0) AS motorist_fatal_crashes,
       min(crash_date) AS first_date,
       max(crash_date) AS last_date
FROM read_parquet("data/crashes.parquet")
WHERE year(crash_date) BETWEEN 2013 AND 2025
GROUP BY year ORDER BY year
"""
df = con.execute(query).df()
assert len(df) == 13 and all(df.first_date.dt.month == 1) and all(df.first_date.dt.day == 1) and all(df.last_date.dt.month == 12) and all(df.last_date.dt.day == 31)

# Option 1: annual total motorist deaths in reported crashes.
v1 = df[["year", "motorist_deaths"]].copy()
v1.to_csv("out/values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(v1.year, v1.motorist_deaths, marker="o", linewidth=2.2, color="#1769aa")
ax.set(title="Motorist deaths in NYC police-reported crashes, 2013–2025", xlabel="Crash year", ylabel="Motorist deaths (count)")
ax.set_xticks(v1.year)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=.28)
ax.text(.01, -.24, "Crash-data count; no miles-driven denominator, so this is not a per-mile risk measure.", transform=ax.transAxes, fontsize=9)
fig.tight_layout()
fig.savefig("out/option_1.png", dpi=160, bbox_inches="tight")
plt.close(fig)

# Option 2: share of police-reported crashes with at least one motorist death.
v2 = df[["year", "motorist_fatal_crashes", "reported_crashes"]].copy()
v2["motorist_fatal_crashes_per_100000_reported_crashes"] = v2.motorist_fatal_crashes / v2.reported_crashes * 100000
v2.to_csv("out/values_2.csv", index=False, float_format="%.6f")
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(v2.year, v2.motorist_fatal_crashes_per_100000_reported_crashes, marker="o", linewidth=2.2, color="#c45127")
ax.set(title="Crashes involving a motorist death per 100,000 reported crashes", xlabel="Crash year", ylabel="Motorist-fatal crashes per 100,000 reported crashes")
ax.set_xticks(v2.year)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=.28)
ax.text(.01, -.24, "Crash-denominated ratio; it does not measure deaths per mile or per motorist.", transform=ax.transAxes, fontsize=9)
fig.tight_layout()
fig.savefig("out/option_2.png", dpi=160, bbox_inches="tight")
plt.close(fig)

start, end = int(v1.iloc[0].motorist_deaths), int(v1.iloc[-1].motorist_deaths)
death_change = (end / start - 1) * 100
rate_start = float(v2.iloc[0].motorist_fatal_crashes_per_100000_reported_crashes)
rate_end = float(v2.iloc[-1].motorist_fatal_crashes_per_100000_reported_crashes)
rate_change = (rate_end / rate_start - 1) * 100
options = {"options": [
    {"id": 1, "metric": "Annual count of motorist deaths in police-reported crashes", "denominator": "None (annual total)", "grouping": "Crash year", "chart_type": "Line chart", "reason": "Annual deaths directly describe the fatality burden recorded by this crash dataset without implying an exposure-adjusted risk.", "probability": 0.55, "answer": f"Recorded motorist deaths fell from {start} in 2013 to {end} in 2025 ({death_change:.1f}%), but this does not establish a decline in deaths per mile driven.", "interpretation": "This framing answers whether the annual count of recorded motorist deaths changed, and the chart shows a lower total in 2025 than in 2013. It is defensible as a measure of fatality burden in the crash records. It leaves the per-mile risk question unanswered because the data contain no miles driven."},
    {"id": 2, "metric": "Motorist-fatal crash records per 100,000 police-reported crash records", "denominator": "All police-reported crash records in the year", "grouping": "Crash year", "chart_type": "Line chart", "reason": "A crash-denominated rate indicates how often a recorded crash involved a motorist death while making its denominator explicit.", "probability": 0.45, "answer": f"Motorist-fatal crash records increased from {rate_start:.1f} to {rate_end:.1f} per 100,000 reported crashes between 2013 and 2025 ({rate_change:.1f}%), not a per-mile risk estimate.", "interpretation": "This framing answers how the occurrence of motorist-fatal crashes compares with the volume of all reported crashes, and the chart shows this ratio was higher in 2025 than in 2013. It is defensible as a crash-level descriptive ratio, not an individual motorist exposure rate. It leaves deaths per mile driven unanswered because neither miles nor the number of motorists exposed is recorded."}
]}
with open("out/options.json", "w", encoding="utf-8") as f:
    json.dump(options, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("2013 deaths", start, "2025 deaths", end, "change_pct", death_change)
print("2013 rate", rate_start, "2025 rate", rate_end, "change_pct", rate_change)
print(df[["year", "reported_crashes", "motorist_deaths", "motorist_fatal_crashes"]].to_string(index=False))
'
# bash
python -c '
import duckdb
import matplotlib.pyplot as plt
con = duckdb.connect()
df = con.execute("SELECT year(crash_date) AS year, count(*) AS reported_crashes, sum(coalesce(number_of_motorist_killed, 0)) AS motorist_deaths, count(*) FILTER (WHERE coalesce(number_of_motorist_killed, 0) > 0) AS motorist_fatal_crashes FROM read_parquet(\"data/crashes.parquet\") WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY year ORDER BY year").df()
v1 = df[["year", "motorist_deaths"]].copy()
v1["motorist_deaths"] = v1.motorist_deaths.astype(int)
v1.to_csv("out/values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(v1.year, v1.motorist_deaths, marker="o", linewidth=2.2, color="#1769aa")
ax.set(title="Motorist deaths in NYC police-reported crashes, 2013–2025", xlabel="Crash year", ylabel="Motorist deaths (count)", ylim=(0, 150))
ax.set_xticks(v1.year)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=.28)
ax.text(.01, -.24, "Crash-data count; no miles-driven denominator, so this is not a per-mile risk measure.", transform=ax.transAxes, fontsize=9)
fig.tight_layout()
fig.savefig("out/option_1.png", dpi=160, bbox_inches="tight")
plt.close(fig)
v2 = df[["year", "motorist_fatal_crashes", "reported_crashes"]].copy()
v2["motorist_fatal_crashes_per_100000_reported_crashes"] = v2.motorist_fatal_crashes / v2.reported_crashes * 100000
v2.to_csv("out/values_2.csv", index=False, float_format="%.6f")
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(v2.year, v2.motorist_fatal_crashes_per_100000_reported_crashes, marker="o", linewidth=2.2, color="#c45127")
ax.set(title="Crashes involving a motorist death per 100,000 reported crashes", xlabel="Crash year", ylabel="Motorist-fatal crashes per 100,000 reported crashes", ylim=(0, 130))
ax.set_xticks(v2.year)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=.28)
ax.text(.01, -.24, "Crash-denominated ratio; it does not measure deaths per mile or per motorist.", transform=ax.transAxes, fontsize=9)
fig.tight_layout()
fig.savefig("out/option_2.png", dpi=160, bbox_inches="tight")
plt.close(fig)
'
# bash
python -c 'import json; x=json.load(open("out/options.json")); assert abs(sum(o["probability"] for o in x["options"])-1)<0.001; print("valid JSON; probability sum =", sum(o["probability"] for o in x["options"]))'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording (fewer minor crashes reported).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.