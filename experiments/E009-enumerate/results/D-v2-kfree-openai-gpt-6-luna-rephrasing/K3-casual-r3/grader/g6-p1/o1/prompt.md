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

QUESTION ASKED: From 2013 to 2025, how did motorist deaths compare with cyclist deaths in NYC each year?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Annual motorist deaths and annual cyclist deaths
denominator: None; annual totals of people killed in police-reported crashes
grouping: Calendar year and road-user group
chart_type: Two-series line chart
probability: 0.58
WRITTEN ANSWER:
Motorist deaths exceeded cyclist deaths every year, peaking at 139 versus 29 in 2020; in 2025 the counts were 81 versus 23. This framing directly compares the annual number of people recorded killed as motorists or cyclists and shows both groups' changes over time. Raw counts are a defensible answer to how many deaths occurred, but they do not adjust for how much each group traveled or otherwise measure individual risk.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_deaths,cyclist_deaths
2013,110,11
2014,109,20
2015,95,15
2016,72,18
2017,107,27
2018,98,10
2019,82,31
2020,139,29
2021,134,19
2022,116,19
2023,123,31
2024,111,24
2025,81,23

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
git status --short
# bash
python3 -c "import duckdb; con=duckdb.connect(); print(con.execute(\"DESCRIBE SELECT * FROM read_parquet('data/crashes.parquet')\").fetchdf().to_string(index=False)); print(con.execute(\"SELECT COUNT(*) n, MIN(crash_date) min_date, MAX(crash_date) max_date FROM read_parquet('data/crashes.parquet')\").fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); q=\"SELECT EXTRACT(year FROM crash_date)::INT y, COUNT(*) crashes, MIN(crash_date) first_date, MAX(crash_date) last_date, COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL) null_motorist, COUNT(*) FILTER (WHERE number_of_cyclist_killed IS NULL) null_cyclist, SUM(COALESCE(number_of_motorist_killed,0)) motorists, SUM(COALESCE(number_of_cyclist_killed,0)) cyclists FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY y ORDER BY y\"; print(c.execute(q).fetchdf().to_string(index=False))"
# bash
ls
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path
out=Path("out")
df=duckdb.connect().execute("SELECT EXTRACT(year FROM crash_date)::INT AS year, SUM(number_of_motorist_killed)::INT AS motorist_deaths, SUM(number_of_cyclist_killed)::INT AS cyclist_deaths FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= DATE \"2013-01-01\" AND crash_date < DATE \"2026-01-01\" GROUP BY year ORDER BY year").fetchdf()
# Option 1: yearly death counts by road-user category.
df.to_csv(out/"values_1.csv", index=False)
fig, ax=plt.subplots(figsize=(10,5.8))
ax.plot(df.year, df.motorist_deaths, marker="o", linewidth=2.4, color="#d1495b", label="Motorist deaths")
ax.plot(df.year, df.cyclist_deaths, marker="o", linewidth=2.4, color="#00798c", label="Cyclist deaths")
ax.set(title="NYC crash deaths by road-user group, 2013–2025", xlabel="Year", ylabel="Deaths in police-reported crashes")
ax.set_xticks(df.year); ax.grid(axis="y", alpha=.25); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(out/"option_1.png", dpi=180); plt.close(fig)
# Option 2: ratio of annual motorist deaths to annual cyclist deaths.
df["motorist_to_cyclist_ratio"] = df.motorist_deaths / df.cyclist_deaths
df[["year","motorist_to_cyclist_ratio","motorist_deaths","cyclist_deaths"]].to_csv(out/"values_2.csv", index=False)
fig, ax=plt.subplots(figsize=(10,5.8))
ax.plot(df.year, df.motorist_to_cyclist_ratio, marker="o", linewidth=2.4, color="#6a4c93")
ax.axhline(1, color="#777777", linewidth=1, linestyle="--")
ax.set(title="Annual motorist-to-cyclist crash-death ratio in NYC, 2013–2025", xlabel="Year", ylabel="Motorist deaths per cyclist death")
ax.set_xticks(df.year); ax.grid(axis="y", alpha=.25); fig.tight_layout(); fig.savefig(out/"option_2.png", dpi=180); plt.close(fig)
print(df.to_string(index=False))'
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path
out=Path("out")
df=duckdb.connect().execute("SELECT EXTRACT(year FROM crash_date)::INT AS year, SUM(number_of_motorist_killed)::INT AS motorist_deaths, SUM(number_of_cyclist_killed)::INT AS cyclist_deaths FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' GROUP BY year ORDER BY year").fetchdf()
df.to_csv(out/"values_1.csv", index=False)
fig, ax=plt.subplots(figsize=(10,5.8))
ax.plot(df.year, df.motorist_deaths, marker="o", linewidth=2.4, color="#d1495b", label="Motorist deaths")
ax.plot(df.year, df.cyclist_deaths, marker="o", linewidth=2.4, color="#00798c", label="Cyclist deaths")
ax.set(title="NYC crash deaths by road-user group, 2013–2025", xlabel="Year", ylabel="Deaths in police-reported crashes")
ax.set_xticks(df.year); ax.grid(axis="y", alpha=.25); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(out/"option_1.png", dpi=180); plt.close(fig)
df["motorist_to_cyclist_ratio"] = df.motorist_deaths / df.cyclist_deaths
df[["year","motorist_to_cyclist_ratio","motorist_deaths","cyclist_deaths"]].to_csv(out/"values_2.csv", index=False)
fig, ax=plt.subplots(figsize=(10,5.8))
ax.plot(df.year, df.motorist_to_cyclist_ratio, marker="o", linewidth=2.4, color="#6a4c93")
ax.axhline(1, color="#777777", linewidth=1, linestyle="--")
ax.set(title="Annual motorist-to-cyclist crash-death ratio in NYC, 2013–2025", xlabel="Year", ylabel="Motorist deaths per cyclist death")
ax.set_xticks(df.year); ax.grid(axis="y", alpha=.25); fig.tight_layout(); fig.savefig(out/"option_2.png", dpi=180); plt.close(fig)
print(df.to_string(index=False))'
# bash
python3 -c 'import json, pandas as pd; from pathlib import Path
p=Path("out"); options=json.loads((p/"options.json").read_text()); assert len(options["options"])==2; assert abs(sum(x["probability"] for x in options["options"])-1)<1e-9
a=pd.read_csv(p/"values_1.csv"); b=pd.read_csv(p/"values_2.csv"); assert a.year.tolist()==list(range(2013,2026)); assert (a.motorist_deaths>a.cyclist_deaths).all(); assert (b.motorist_to_cyclist_ratio.sub(b.motorist_deaths/b.cyclist_deaths).abs()<1e-12).all(); assert all((p/f).is_file() for f in ["option_1.png","option_2.png","values_1.csv","values_2.csv","options.json"]); print("Validated JSON, probabilities, yearly counts, ratios, and all output files."); print("Count extremes:", a.loc[a.motorist_deaths.idxmax(),["year","motorist_deaths","cyclist_deaths"]].to_dict()); print("Ratios min/max:", b.loc[b.motorist_to_cyclist_ratio.idxmin(),["year","motorist_to_cyclist_ratio"]].to_dict(), b.loc[b.motorist_to_cyclist_ratio.idxmax(),["year","motorist_to_cyclist_ratio"]].to_dict()); print("2025:", a.loc[a.year.eq(2025)].to_dict(orient="records")[0])'

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