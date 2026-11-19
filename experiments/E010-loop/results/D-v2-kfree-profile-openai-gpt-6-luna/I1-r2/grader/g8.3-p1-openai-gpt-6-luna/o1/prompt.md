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
- A disclaimer whose wording can reasonably be read as a conclusion from the data is judged by that reading: "per-trip risk
  is not greater", or a substitute measure offered as the answer ("so this crash-based proxy did not fall" under a per-mile
  question), FAILS unsupported_claim (and PERMILE where it applies); "does not establish" or "this is not per-mile risk" passes.
- Where an item asks for a qualification or disclosure, wording in the WRITTEN ANSWER or the DECLARED FRAMING counts, in any
  phrasing (it need not say "in this dataset" literally); text that appears only inside the chart image (title, footnote, source
  note) does not satisfy it on its own.
- The official-count part of unsupported_claim concerns death counts presented as the official city toll: on a question with a
  TR07 item it FAILs exactly when TR07 FAILs; elsewhere a count or share computed from this data is not an official-count claim.

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Number of motorists killed
denominator: None (annual count)
grouping: Calendar year, 2013–2025
chart_type: Line chart
probability: 0.45
WRITTEN ANSWER:
Reported motorist deaths fell from 110 in 2013 to 81 in 2025 (26.4%), but this count cannot establish whether per-mile risk declined because vehicle-miles traveled are absent. This framing shows whether the annual number of motorists killed in NYC reported crashes changed, and it fell between 2013 and 2025 despite fluctuations in between. A count is a defensible measure of fatality burden, but it leaves the requested exposure-adjusted risk per mile unanswered.

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
ls -ld . data
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.sql(f"SELECT year(crash_date) AS year, count(*) AS crashes, sum(number_of_motorist_killed) AS motorist_deaths, count(*) FILTER (WHERE number_of_motorist_killed > 0) AS crashes_with_motorist_death FROM read_parquet(\"{p}\") WHERE crash_date >= DATE \"2013-01-01\" AND crash_date < DATE \"2026-01-01\" GROUP BY 1 ORDER BY 1").df().to_string(index=False))'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; q=f"SELECT year(crash_date) AS year, count(*) AS crashes, sum(number_of_motorist_killed) AS motorist_deaths, count(*) FILTER (WHERE number_of_motorist_killed > 0) AS crashes_with_motorist_death FROM read_parquet(\"{p}\") WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1"; print(duckdb.sql(q).df().to_string(index=False))'
# bash
python3 -c 'exec("""import duckdb, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path
out = Path(\"out\")
out.mkdir(exist_ok=True)
query = \"\"\"SELECT year(crash_date) AS year, count(*) AS crashes, sum(number_of_motorist_killed)::BIGINT AS motorist_deaths, count(*) FILTER (WHERE number_of_motorist_killed > 0) AS crashes_with_motorist_death FROM read_parquet(\"data/crashes.parquet\") WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1\"\"\"
df = duckdb.sql(query).df()
df[\"motorist_death_crashes_per_100k_crashes\"] = df.crashes_with_motorist_death / df.crashes * 100000
# Option 1: annual death counts
v1 = df[[\"year\", \"motorist_deaths\"]]
v1.to_csv(out / \"values_1.csv\", index=False)
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(v1.year, v1.motorist_deaths, marker=\"o\", color=\"#1f77b4\", linewidth=2)
ax.set(title=\"Motorists killed in NYC reported crashes, 2013–2025\", xlabel=\"Crash year\", ylabel=\"Motorists killed (count)\")
ax.set_xticks(v1.year)
ax.grid(axis=\"y\", alpha=.25)
ax.annotate(f\"2013: {int(v1.motorist_deaths.iloc[0])}\", (v1.year.iloc[0], v1.motorist_deaths.iloc[0]), xytext=(6, 10), textcoords=\"offset points\", fontsize=9)
ax.annotate(f\"2025: {int(v1.motorist_deaths.iloc[-1])}\", (v1.year.iloc[-1], v1.motorist_deaths.iloc[-1]), xytext=(-40, 10), textcoords=\"offset points\", fontsize=9)
fig.text(.5, .01, \"Crash records contain no vehicle-miles-traveled denominator; count is not per-mile risk.\", ha=\"center\", fontsize=9)
fig.tight_layout(rect=(0, .04, 1, 1))
fig.savefig(out / \"option_1.png\", dpi=160, bbox_inches=\"tight\")
plt.close(fig)
# Option 2: crash-level fatal incidence, normalized by all reported crashes
v2 = df[[\"year\", \"crashes_with_motorist_death\", \"crashes\", \"motorist_death_crashes_per_100k_crashes\"]]
v2.to_csv(out / \"values_2.csv\", index=False)
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(v2.year, v2.motorist_death_crashes_per_100k_crashes, marker=\"o\", color=\"#d55e00\", linewidth=2)
ax.set(title=\"Crashes with a motorist death per 100,000 NYC reported crashes\", xlabel=\"Crash year\", ylabel=\"Fatal motorist crash incidence per 100,000 crashes\")
ax.set_xticks(v2.year)
ax.grid(axis=\"y\", alpha=.25)
ax.annotate(f\"2013: {v2.motorist_death_crashes_per_100k_crashes.iloc[0]:.1f}\", (v2.year.iloc[0], v2.motorist_death_crashes_per_100k_crashes.iloc[0]), xytext=(6, 10), textcoords=\"offset points\", fontsize=9)
ax.annotate(f\"2025: {v2.motorist_death_crashes_per_100k_crashes.iloc[-1]:.1f}\", (v2.year.iloc[-1], v2.motorist_death_crashes_per_100k_crashes.iloc[-1]), xytext=(-40, 10), textcoords=\"offset points\", fontsize=9)
fig.text(.5, .01, \"Crash-based incidence, not motorist risk per mile; vehicle-miles traveled are unavailable.\", ha=\"center\", fontsize=9)
fig.tight_layout(rect=(0, .04, 1, 1))
fig.savefig(out / \"option_2.png\", dpi=160, bbox_inches=\"tight\")
plt.close(fig)
print(df[[\"year\", \"crashes\", \"motorist_deaths\", \"crashes_with_motorist_death\", \"motorist_death_crashes_per_100k_crashes\"]].to_string(index=False))
""")'
# bash
python3 -c 'import json, pandas as pd; from pathlib import Path; p=Path("out"); o=json.loads((p/"options.json").read_text()); a=pd.read_csv(p/"values_1.csv").set_index("year"); b=pd.read_csv(p/"values_2.csv").set_index("year"); print("options", len(o["options"]), "probability sum", sum(x["probability"] for x in o["options"])); print("count change %", (a.loc[2025,"motorist_deaths"]/a.loc[2013,"motorist_deaths"]-1)*100); print("crash-rate endpoints", b.loc[2013,"motorist_death_crashes_per_100k_crashes"], b.loc[2025,"motorist_death_crashes_per_100k_crashes"], "change %", (b.loc[2025,"motorist_death_crashes_per_100k_crashes"]/b.loc[2013,"motorist_death_crashes_per_100k_crashes"]-1)*100); print("files", sorted(x.name for x in p.iterdir()))'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.