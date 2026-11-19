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
metric: Annual number of motorists killed in reported crashes
denominator: None (annual count)
grouping: Crash year
chart_type: Line chart
probability: 0.45
WRITTEN ANSWER:
The file records 110 motorists killed in 2013 and 81 in 2025 (a 26% decrease), but without miles driven it cannot establish whether deaths per mile declined. This framing addresses whether the observed motorist death count fell between the endpoints, and the chart shows a decline from 110 in 2013 to 81 in 2025. A count is a defensible measure of fatality burden, but it does not adjust for travel exposure and therefore leaves deaths per mile unanswered.

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
ls
# bash
python -c "import duckdb; p='data/crashes.parquet'; con=duckdb.connect(); print(con.execute(\"SELECT MIN(crash_date), MAX(crash_date), COUNT(*), SUM(number_of_motorist_killed), SUM(number_of_persons_killed) FROM read_parquet(?)\", [p]).fetchall()); print(con.execute(\"SELECT EXTRACT(YEAR FROM crash_date) AS yr, COUNT(*) AS crashes, SUM(number_of_motorist_killed) AS motorist_killed, SUM(number_of_persons_killed) AS persons_killed, SUM(number_of_motorist_killed)::DOUBLE/COUNT(*) AS motorist_killed_per_crash FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr\", [p]).df().to_string(index=False))"
# bash
python -c 'import duckdb, matplotlib.pyplot as plt; from pathlib import Path; out=Path("out"); out.mkdir(exist_ok=True); df=duckdb.connect().execute("SELECT EXTRACT(YEAR FROM crash_date)::INT AS year, COUNT(*)::INT AS reported_crashes, SUM(number_of_motorist_killed)::INT AS motorist_deaths, SUM(number_of_motorist_killed)::DOUBLE / COUNT(*) * 100000 AS motorist_deaths_per_100k_crashes FROM read_parquet(?) WHERE crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2026-01-01\' GROUP BY year ORDER BY year", ["data/crashes.parquet"]).df(); df.to_csv(out/"values_1.csv", index=False, columns=["year", "motorist_deaths"]); fig, ax=plt.subplots(figsize=(10,5.5)); ax.plot(df.year, df.motorist_deaths, marker="o", color="#235789", linewidth=2.5); ax.set(title="NYC motorist deaths in reported crashes, 2013–2025", xlabel="Crash year", ylabel="Motorists killed (count)"); ax.set_xticks(df.year); ax.tick_params(axis="x", rotation=45); ax.grid(axis="y", alpha=.25); ax.annotate("110", (2013,110), xytext=(0,9), textcoords="offset points", ha="center"); ax.annotate("81", (2025,81), xytext=(0,9), textcoords="offset points", ha="center"); fig.tight_layout(); fig.savefig(out/"option_1.png", dpi=180); plt.close(fig); df.to_csv(out/"values_2.csv", index=False, columns=["year", "reported_crashes", "motorist_deaths", "motorist_deaths_per_100k_crashes"]); fig, ax=plt.subplots(figsize=(10,5.5)); ax.plot(df.year, df.motorist_deaths_per_100k_crashes, marker="o", color="#c44536", linewidth=2.5); ax.set(title="Motorist deaths per 100,000 reported NYC crashes, 2013–2025", xlabel="Crash year", ylabel="Motorist deaths per 100,000 reported crashes"); ax.set_xticks(df.year); ax.tick_params(axis="x", rotation=45); ax.grid(axis="y", alpha=.25); a=df.iloc[0]; b=df.iloc[-1]; ax.annotate(f"{a.motorist_deaths_per_100k_crashes:.1f}", (a.year,a.motorist_deaths_per_100k_crashes), xytext=(0,9), textcoords="offset points", ha="center"); ax.annotate(f"{b.motorist_deaths_per_100k_crashes:.1f}", (b.year,b.motorist_deaths_per_100k_crashes), xytext=(0,9), textcoords="offset points", ha="center"); fig.tight_layout(); fig.savefig(out/"option_2.png", dpi=180); plt.close(fig); print(df.to_string(index=False)); print("Saved charts and CSVs in out/")'
# bash
python3 -c 'import duckdb, matplotlib.pyplot as plt; from pathlib import Path; out=Path("out"); out.mkdir(exist_ok=True); df=duckdb.connect().execute("SELECT EXTRACT(YEAR FROM crash_date)::INT AS year, COUNT(*)::INT AS reported_crashes, SUM(number_of_motorist_killed)::INT AS motorist_deaths, SUM(number_of_motorist_killed)::DOUBLE / COUNT(*) * 100000 AS motorist_deaths_per_100k_crashes FROM read_parquet(?) WHERE crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2026-01-01\' GROUP BY year ORDER BY year", ["data/crashes.parquet"]).df(); df.to_csv(out/"values_1.csv", index=False, columns=["year", "motorist_deaths"]); fig, ax=plt.subplots(figsize=(10,5.5)); ax.plot(df.year, df.motorist_deaths, marker="o", color="#235789", linewidth=2.5); ax.set(title="NYC motorist deaths in reported crashes, 2013–2025", xlabel="Crash year", ylabel="Motorists killed (count)"); ax.set_xticks(df.year); ax.tick_params(axis="x", rotation=45); ax.grid(axis="y", alpha=.25); ax.annotate("110", (2013,110), xytext=(0,9), textcoords="offset points", ha="center"); ax.annotate("81", (2025,81), xytext=(0,9), textcoords="offset points", ha="center"); fig.tight_layout(); fig.savefig(out/"option_1.png", dpi=180); plt.close(fig); df.to_csv(out/"values_2.csv", index=False, columns=["year", "reported_crashes", "motorist_deaths", "motorist_deaths_per_100k_crashes"]); fig, ax=plt.subplots(figsize=(10,5.5)); ax.plot(df.year, df.motorist_deaths_per_100k_crashes, marker="o", color="#c44536", linewidth=2.5); ax.set(title="Motorist deaths per 100,000 reported NYC crashes, 2013–2025", xlabel="Crash year", ylabel="Motorist deaths per 100,000 reported crashes"); ax.set_xticks(df.year); ax.tick_params(axis="x", rotation=45); ax.grid(axis="y", alpha=.25); a=df.iloc[0]; b=df.iloc[-1]; ax.annotate(f"{a.motorist_deaths_per_100k_crashes:.1f}", (a.year,a.motorist_deaths_per_100k_crashes), xytext=(0,9), textcoords="offset points", ha="center"); ax.annotate(f"{b.motorist_deaths_per_100k_crashes:.1f}", (b.year,b.motorist_deaths_per_100k_crashes), xytext=(0,9), textcoords="offset points", ha="center"); fig.tight_layout(); fig.savefig(out/"option_2.png", dpi=180); plt.close(fig); print(df.to_string(index=False)); print("Saved charts and CSVs in out/")'
# bash
python3 out/generate.py
# bash
python3 -m json.tool out/options.json

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