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
- Qualifications (reported, recorded in this dataset) count when they are in the WRITTEN ANSWER or the DECLARED FRAMING; text
  that appears only inside the chart image (title, footnote, source note) does not satisfy an item on its own. The official-count
  part of unsupported_claim follows the same test as TR07.

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: From 2013 to 2025, did the risk of a motorist being killed for each mile driven in NYC go down? Use this crash data to make a chart and answer the question.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Motorist deaths per 100,000 reported crashes
denominator: All police-reported crash records in the same year
grouping: Crash year, 2013–2025
chart_type: Line chart
probability: 0.7
WRITTEN ANSWER:
The data cannot establish per-mile risk; motorist deaths per 100,000 reported crashes increased from 54.0 in 2013 to 94.7 in 2025, so this crash-based proxy did not fall. This addresses whether fatalities declined relative to recorded crash volume: deaths per 100,000 police-reported crash records rose from 54.0 in 2013 to 94.7 in 2025. It is a defensible normalized proxy using an available denominator, but it does not measure risk per mile because the crash data contain no miles-driven measure.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,reported_crashes,motorist_deaths,motorist_deaths_per_100000_crashes
2013,203742,110,53.989850
2014,206046,109,52.900809
2015,217708,95,43.636430
2016,229833,72,31.327094
2017,231007,107,46.318943
2018,231564,98,42.320913
2019,211486,82,38.773252
2020,112918,139,123.098177
2021,110558,134,121.203350
2022,103887,116,111.659784
2023,96607,123,127.319966
2024,91316,111,121.555916
2025,85546,81,94.685900

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c 'import duckdb; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet(\"data/crashes.parquet\")").fetchall()); print(c.execute("SELECT min(crash_date), max(crash_date), count(*), sum(number_of_motorist_killed) FROM read_parquet(\"data/crashes.parquet\")").fetchall())'
# bash
python -c 'import duckdb; c=duckdb.connect(); q="SELECT year(crash_date) y, count(*) crashes, sum(coalesce(number_of_motorist_killed,0)) deaths, count(*) FILTER (WHERE coalesce(number_of_motorist_killed,0)>0) fatal_crashes FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= DATE \"2013-01-01\" AND crash_date < DATE \"2026-01-01\" GROUP BY y ORDER BY y"; print(c.execute(q).df().to_string(index=False))'
# bash
python -c 'import duckdb; c=duckdb.connect(); q="SELECT year(crash_date) y, count(*) crashes, sum(coalesce(number_of_motorist_killed,0)) deaths, count(*) FILTER (WHERE coalesce(number_of_motorist_killed,0)>0) fatal_crashes FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' GROUP BY y ORDER BY y"; print(c.execute(q).df().to_string(index=False))'
# bash
python -c 'import duckdb; c=duckdb.connect(); q="SELECT year(crash_date) y, month(crash_date) m, count(*) n FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= DATE '\''2019-01-01'\'' AND crash_date < DATE '\''2027-01-01'\'' GROUP BY y,m ORDER BY y,m"; print(c.execute(q).df().to_string(index=False))'
# bash
ls -ld .
# bash
python - <<'PY'
from pathlib import Path
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = Path("out")
out.mkdir(exist_ok=True)
con = duckdb.connect()
query = """
SELECT year(crash_date) AS year,
       count(*) AS reported_crashes,
       sum(coalesce(number_of_motorist_killed, 0))::BIGINT AS motorist_deaths,
       count(*) FILTER (WHERE coalesce(number_of_motorist_killed, 0) > 0) AS crashes_with_motorist_death
FROM read_parquet('data/crashes.parquet')
WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
GROUP BY year
ORDER BY year
"""
df = con.execute(query).df()
df["motorist_deaths_per_100000_crashes"] = df["motorist_deaths"] / df["reported_crashes"] * 100000

# Option 1: annual count of motorists killed.
values1 = df[["year", "motorist_deaths"]]
values1.to_csv(out / "values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(values1["year"], values1["motorist_deaths"], marker="o", color="#276FBF", linewidth=2.5)
ax.set_title("Motorists killed in NYC crashes, 2013–2025", fontsize=15, pad=14)
ax.set_xlabel("Crash year")
ax.set_ylabel("Motorists killed (people)")
ax.set_xticks(values1["year"])
ax.grid(axis="y", alpha=0.28)
ax.spines[["top", "right"]].set_visible(False)
ax.text(0.01, -0.20, "Annual deaths in police-reported crashes; this is a count, not risk per mile.", transform=ax.transAxes, fontsize=9, color="#555555")
fig.tight_layout()
fig.savefig(out / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 2: deaths per 100,000 police-reported crashes (not per mile driven).
values2 = df[["year", "reported_crashes", "motorist_deaths", "motorist_deaths_per_100000_crashes"]]
values2.to_csv(out / "values_2.csv", index=False, float_format="%.6f")
fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(values2["year"], values2["motorist_deaths_per_100000_crashes"], marker="o", color="#D95F02", linewidth=2.5)
ax.set_title("Motorist deaths per 100,000 reported crashes, 2013–2025", fontsize=15, pad=14)
ax.set_xlabel("Crash year")
ax.set_ylabel("Motorist deaths per 100,000 crash records")
ax.set_xticks(values2["year"])
ax.grid(axis="y", alpha=0.28)
ax.spines[["top", "right"]].set_visible(False)
ax.text(0.01, -0.20, "Deaths divided by all police-reported crashes; denominator is crash records, not miles driven.", transform=ax.transAxes, fontsize=9, color="#555555")
fig.tight_layout()
fig.savefig(out / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
print(df.to_string(index=False))
print("\nSaved:", *(str(p) for p in sorted(out.iterdir())), sep="\n")
PY
# bash
python -c 'import json; p=json.load(open("out/options.json")); assert abs(sum(o["probability"] for o in p["options"])-1)<1e-9; print("valid JSON; probabilities sum to", sum(o["probability"] for o in p["options"])); print("output files:", __import__("os").listdir("out"))'

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