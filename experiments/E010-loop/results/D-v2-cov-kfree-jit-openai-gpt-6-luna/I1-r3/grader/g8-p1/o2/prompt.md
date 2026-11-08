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
metric: Motorist deaths per 1,000 police-reported crash records
denominator: All police-reported crashes in each calendar year
grouping: Crash year (2013–2025)
chart_type: Line chart
probability: 0.45
WRITTEN ANSWER:
This file cannot establish per-mile risk, and deaths per 1,000 crash records rose from 0.540 in 2013 to 0.947 in 2025 (75.4%). This addresses whether motorist deaths became less frequent relative to the number of police-reported crashes, not relative to miles driven. The line rises from 0.540 deaths per 1,000 crash records in 2013 to 0.947 in 2025, with a sharp increase in 2020. This is a defensible crash-normalized fatality measure, but one crash record is not a unit of driving exposure and cannot answer the per-mile question. No rows (0%) are omitted for NULL required values, and all included years are complete.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,crash_count,deaths_per_1000_crashes
2013,110.0,203742,0.5398984990821726
2014,109.0,206046,0.5290080855731244
2015,95.0,217708,0.43636430448123176
2016,72.0,229833,0.31327094020440927
2017,107.0,231007,0.46318942716021594
2018,98.0,231564,0.4232091344077663
2019,82.0,211486,0.3877325213016464
2020,139.0,112918,1.2309817743849518
2021,134.0,110558,1.212033502776823
2022,116.0,103887,1.1165978418858953
2023,123.0,96607,1.273199664620576
2024,111.0,91316,1.2155591572123177
2025,81.0,85546,0.9468589998363454

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"describe select * from read_parquet('{p}')\").fetchall()); print(c.execute(f\"select count(*) n, min(crash_date), max(crash_date) from read_parquet('{p}')\").fetchall()); print(c.execute(f\"select year(crash_date), count(*), sum(number_of_motorist_killed), count(*) filter (where number_of_motorist_killed is null), sum(number_of_persons_killed), count(*) filter (where collision_id is null) from read_parquet('{p}') group by 1 order by 1\").fetchall())"
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"select year(crash_date) y, min(crash_date), max(crash_date), count(*) n, count(*) filter(where crash_date is null) date_null, count(*) filter(where number_of_motorist_killed is null) killed_null, sum(number_of_motorist_killed) killed, sum(number_of_motorist_killed) * 1.0 / count(*) * 1000 per_1000_crashes from read_parquet('{p}') where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1 order by 1\").fetchall()); print(c.execute(f\"select count(*) filter(where crash_date is null) from read_parquet('{p}')\").fetchall())"
# bash
ls
# bash
python -c $'import os, json\nimport duckdb, pandas as pd\nimport matplotlib.pyplot as plt\n\nos.makedirs("out", exist_ok=True)\ncon = duckdb.connect()\np = "data/crashes.parquet"\ndf = con.execute(f"""\n    SELECT year(crash_date) AS year,\n           count(*) AS crash_count,\n           sum(number_of_motorist_killed) AS motorist_deaths,\n           count(*) FILTER (WHERE number_of_motorist_killed > 0) AS fatal_motorist_crashes,\n           count(*) FILTER (WHERE crash_date IS NULL) AS null_date_rows,\n           count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS null_death_rows,\n           min(crash_date) AS first_date, max(crash_date) AS last_date\n    FROM read_parquet(\'{p}\')\n    WHERE crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2026-01-01\'\n    GROUP BY 1 ORDER BY 1\n""").df()\ndf["deaths_per_1000_crashes"] = df.motorist_deaths / df.crash_count * 1000\ndf["fatal_motorist_crash_pct"] = df.fatal_motorist_crashes / df.crash_count * 100\n\n# Option 1: absolute annual burden\nv1 = df[["year", "motorist_deaths"]].copy()\nv1.to_csv("out/values_1.csv", index=False)\nfig, ax = plt.subplots(figsize=(9, 5))\nax.bar(v1.year, v1.motorist_deaths, color="#3973ac")\nax.set(title="Motorists killed in NYC crashes, 2013–2025", xlabel="Crash year", ylabel="Motorists killed (people)")\nax.set_xticks(v1.year); ax.tick_params(axis="x", rotation=45); ax.grid(axis="y", alpha=.25)\nfig.text(.5, .01, "Counts do not adjust for miles driven", ha="center", color="#555")\nfig.tight_layout(rect=(0, .05, 1, 1)); fig.savefig("out/option_1.png", dpi=160); plt.close(fig)\n\n# Option 2: fatalities normalized by reported crash count\nv2 = df[["year", "motorist_deaths", "crash_count", "deaths_per_1000_crashes"]].copy()\nv2.to_csv("out/values_2.csv", index=False)\nfig, ax = plt.subplots(figsize=(9, 5))\nax.plot(v2.year, v2.deaths_per_1000_crashes, marker="o", color="#c04b37")\nax.set(title="Motorist deaths per 1,000 reported crashes, 2013–2025", xlabel="Crash year", ylabel="Motorist deaths per 1,000 crash records")\nax.set_xticks(v2.year); ax.tick_params(axis="x", rotation=45); ax.grid(alpha=.25)\nfig.text(.5, .01, "Crash-normalized measure; not a per-mile risk rate", ha="center", color="#555")\nfig.tight_layout(rect=(0, .05, 1, 1)); fig.savefig("out/option_2.png", dpi=160); plt.close(fig)\n\n# Option 3: incidence of a crash with at least one motorist killed\nv3 = df[["year", "fatal_motorist_crashes", "crash_count", "fatal_motorist_crash_pct"]].copy()\nv3.to_csv("out/values_3.csv", index=False)\nfig, ax = plt.subplots(figsize=(9, 5))\nax.plot(v3.year, v3.fatal_motorist_crash_pct, marker="o", color="#49875a")\nax.set(title="Share of NYC crash records with a motorist killed, 2013–2025", xlabel="Crash year", ylabel="Crashes with ≥1 motorist killed (%)")\nax.set_xticks(v3.year); ax.tick_params(axis="x", rotation=45); ax.grid(alpha=.25)\nfig.text(.5, .01, "Crash-level incidence; not a per-mile risk rate", ha="center", color="#555")\nfig.tight_layout(rect=(0, .05, 1, 1)); fig.savefig("out/option_3.png", dpi=160); plt.close(fig)\n\n# machine-readable coverage/null audit for constructing interpretations\ndf.to_csv("/tmp/crash_yearly_audit.csv", index=False)\nprint(df.to_string(index=False))'
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"select year(crash_date) y, count(*) crashes, sum(number_of_motorist_killed) deaths, count(*) filter(where number_of_motorist_killed>0) fatal_crashes, round(sum(number_of_motorist_killed)*1000.0/count(*),6) deaths_per_1000, round(100.0*count(*) filter(where number_of_motorist_killed>0)/count(*),6) fatal_pct from read_parquet('{p}') where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1 order by 1\").fetchall())"
# bash
python -c "print((81/110-1)*100); print((0.9468589998363454/0.5398984990821726-1)*100); print((0.08767212961447642/0.05006331536943782-1)*100)"
# bash
python -c "import json, duckdb, os; x=json.load(open('out/options.json')); print('options',len(x['options']),'probability_sum',sum(o['probability'] for o in x['options'])); print('files',[(f,os.path.getsize('out/'+f)) for f in sorted(os.listdir('out'))]); c=duckdb.connect(); print('null required rows in selected years',c.execute(\"select count(*) filter(where crash_date is null) as null_date, count(*) filter(where number_of_motorist_killed is null) as null_killed from read_parquet('data/crashes.parquet') where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01'\").fetchall())"

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