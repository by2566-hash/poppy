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

QUESTION ASKED: How do motorist and cyclist deaths compare year by year in NYC, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Ratio of motorist deaths to cyclist deaths
denominator: Cyclist deaths in the same calendar year
grouping: Calendar year (2013–2025)
chart_type: Line chart
probability: 0.35
WRITTEN ANSWER:
Motorist deaths were about 2.6 to 10.0 times cyclist deaths per year, with the ratio lowest in 2019 and highest in 2013. This compares the relative yearly scale of motorist and cyclist deaths; the line ranges from about 2.6 motorist deaths per cyclist death in 2019 to 10.0 in 2013. Dividing by cyclist deaths makes the year-to-year size of the disparity easy to compare despite the different absolute scales. It does not show the absolute number of deaths in either group. No rows are omitted for NULL required values (0 of 2269187, 0%); all included years are complete calendar years.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,cyclist_deaths,motorist_to_cyclist_ratio
2013,110,11,10.0000
2014,109,20,5.4500
2015,95,15,6.3333
2016,72,18,4.0000
2017,107,27,3.9630
2018,98,10,9.8000
2019,82,31,2.6452
2020,139,29,4.7931
2021,134,19,7.0526
2022,116,19,6.1053
2023,123,31,3.9677
2024,111,24,4.6250
2025,81,23,3.5217

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("describe select * from read_parquet(?)",[p]).fetchdf().to_string(index=False)); print(c.execute("select min(crash_date), max(crash_date), count(*), count(number_of_cyclist_killed), count(number_of_motorist_killed) from read_parquet(?)",[p]).fetchall())' && ls out
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("select year(crash_date) y, min(crash_date) start, max(crash_date) end, count(*) crashes, sum(number_of_motorist_killed) motorist, sum(number_of_cyclist_killed) cyclist, sum(number_of_motorist_killed) filter (where number_of_motorist_killed is null) null_motorist, sum(number_of_cyclist_killed) filter (where number_of_cyclist_killed is null) null_cyclist, count(*) filter (where crash_date is null) null_date from read_parquet(?) where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by y order by y",[p]).fetchdf().to_string(index=False))'
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"select year(crash_date) as yr, min(crash_date) as first_date, max(crash_date) as last_date, count(*) as crashes, sum(number_of_motorist_killed) as motorist, sum(number_of_cyclist_killed) as cyclist, count(*) filter (where number_of_motorist_killed is null) as null_motorist, count(*) filter (where number_of_cyclist_killed is null) as null_cyclist from read_parquet(?) where crash_date >= make_date(2013,1,1) and crash_date < make_date(2026,1,1) group by yr order by yr\", [p]).fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"select count(*) as total, count(*) filter (where crash_date is null) as null_date, count(*) filter (where crash_date between make_date(2013,1,1) and make_date(2025,12,31) and (number_of_motorist_killed is null or number_of_cyclist_killed is null)) as null_death_in_period from read_parquet('data/crashes.parquet')\").fetchall())"
# bash
python3 -c 'import json
from pathlib import Path
import duckdb
import matplotlib.pyplot as plt
import pandas as pd

out = Path("out")
out.mkdir(exist_ok=True)
con = duckdb.connect()
source = "data/crashes.parquet"
query = """select year(crash_date) as year, cast(sum(number_of_motorist_killed) as integer) as motorist_deaths, cast(sum(number_of_cyclist_killed) as integer) as cyclist_deaths from read_parquet(?) where crash_date >= ? and crash_date < ? group by year order by year"""
df = con.execute(query, [source, "2013-01-01", "2026-01-01"]).fetchdf()
nulls = con.execute("select count(*) as total, count(*) filter (where crash_date is null) as null_date, count(*) filter (where crash_date between date \'2013-01-01\' and date \'2025-12-31\' and (number_of_motorist_killed is null or number_of_cyclist_killed is null)) as null_deaths from read_parquet(?)", [source]).fetchone()
assert df["year"].tolist() == list(range(2013, 2026))
assert int(nulls[1]) == 0 and int(nulls[2]) == 0

# Option 1: annual absolute deaths, shown as paired time-series lines.
values1 = df.copy()
values1.to_csv(out / "values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.7))
ax.plot(df["year"], df["motorist_deaths"], marker="o", linewidth=2.4, label="Motorist deaths", color="#1f77b4")
ax.plot(df["year"], df["cyclist_deaths"], marker="o", linewidth=2.4, label="Cyclist deaths", color="#e87524")
ax.set(title="Motorist and cyclist deaths by year, NYC (2013–2025)", xlabel="Year", ylabel="Deaths")
ax.set_xticks(df["year"])
ax.tick_params(axis="x", rotation=45)
ax.set_ylim(bottom=0)
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(out / "option_1.png", dpi=160)
plt.close(fig)

# Option 2: relative comparison as motorist deaths per cyclist death.
values2 = df.copy()
values2["motorist_to_cyclist_ratio"] = values2["motorist_deaths"] / values2["cyclist_deaths"]
values2.to_csv(out / "values_2.csv", index=False, float_format="%.4f")
fig, ax = plt.subplots(figsize=(10, 5.7))
ax.plot(values2["year"], values2["motorist_to_cyclist_ratio"], marker="o", linewidth=2.4, color="#6a4c93")
ax.set(title="Motorist deaths per cyclist death, NYC (2013–2025)", xlabel="Year", ylabel="Motorist deaths per cyclist death")
ax.set_xticks(values2["year"])
ax.tick_params(axis="x", rotation=45)
ax.set_ylim(bottom=0)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(out / "option_2.png", dpi=160)
plt.close(fig)

minimum = values2.loc[values2["motorist_to_cyclist_ratio"].idxmin()]
maximum = values2.loc[values2["motorist_to_cyclist_ratio"].idxmax()]
options = {"options": [
 {"id": 1, "metric": "Annual motorist and cyclist deaths", "denominator": "None; sum of reported deaths for each road-user group", "grouping": "Calendar year (2013–2025)", "chart_type": "Two-series line chart", "reason": "Annual counts preserve the units in the question and make changes in each group directly comparable over time.", "probability": 0.65, "answer": f"Motorist deaths exceeded cyclist deaths in every year, ranging from {int(df.motorist_deaths.min())} to {int(df.motorist_deaths.max())} versus {int(df.cyclist_deaths.min())} to {int(df.cyclist_deaths.max())}; motorist deaths peaked in 2020, while cyclist deaths peaked at 31 in both 2019 and 2023.", "interpretation": "This compares absolute motorist and cyclist fatality counts year by year; the lines show more motorist deaths in every year, with motorist deaths highest in 2020 and cyclist deaths highest (tied) in 2019 and 2023. Absolute annual totals directly answer which group had more deaths and how the counts changed over time. It does not express the gap relative to the cyclist count. No rows are omitted for NULL required values (0 of {int(nulls[0])}, 0%); all included years are complete calendar years."},
 {"id": 2, "metric": "Ratio of motorist deaths to cyclist deaths", "denominator": "Cyclist deaths in the same calendar year", "grouping": "Calendar year (2013–2025)", "chart_type": "Line chart", "reason": "A within-year ratio shows how large the motorist death count was relative to the cyclist count, independent of the different count scales.", "probability": 0.35, "answer": f"Motorist deaths were about {minimum.motorist_to_cyclist_ratio:.1f} to {maximum.motorist_to_cyclist_ratio:.1f} times cyclist deaths per year, with the ratio lowest in {int(minimum.year)} and highest in {int(maximum.year)}.", "interpretation": "This compares the relative yearly scale of motorist and cyclist deaths; the line ranges from about {minimum.motorist_to_cyclist_ratio:.1f} motorist deaths per cyclist death in {int(minimum.year)} to {maximum.motorist_to_cyclist_ratio:.1f} in {int(maximum.year)}. Dividing by cyclist deaths makes the year-to-year size of the disparity easy to compare despite the different absolute scales. It does not show the absolute number of deaths in either group. No rows are omitted for NULL required values (0 of {int(nulls[0])}, 0%); all included years are complete calendar years."}
]}
(out / "options.json").write_text(json.dumps(options, indent=2) + "\n")
print(df.to_string(index=False))
print("Ratio range:", round(float(minimum.motorist_to_cyclist_ratio), 4), "in", int(minimum.year), "to", round(float(maximum.motorist_to_cyclist_ratio), 4), "in", int(maximum.year))
print("Null-row audit total/date/death:", nulls)'
# bash
python3 out/build_analysis.py
# bash
python3 -c "import json, pathlib, pandas as pd; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); assert len(o['options']) == 2 and abs(sum(x['probability'] for x in o['options'])-1)<1e-9; assert all((p/f'option_{i}.png').is_file() and (p/f'values_{i}.csv').is_file() for i in (1,2)); d1=pd.read_csv(p/'values_1.csv'); d2=pd.read_csv(p/'values_2.csv'); assert len(d1)==len(d2)==13 and d1['year'].tolist()==list(range(2013,2026)); assert d1['motorist_deaths'].gt(d1['cyclist_deaths']).all(); assert d2.loc[d2.motorist_to_cyclist_ratio.idxmin(),'year']==2019 and d2.loc[d2.motorist_to_cyclist_ratio.idxmax(),'year']==2013; print('Validated both charts, CSVs, JSON structure, and stated extrema.')"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR15: Claims about cyclist deaths changing sharply (e.g. 'tripled') are qualified by the small counts (10 → 31).
- tr_TR03: The output does not claim that motorist + cyclist deaths are all deaths (pedestrians and unclassified deaths exist).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.