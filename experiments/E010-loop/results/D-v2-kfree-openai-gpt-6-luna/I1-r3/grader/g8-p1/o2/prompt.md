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
metric: Motorist deaths per 1,000 reported crashes
denominator: All police-reported crashes in the same calendar year
grouping: Calendar year
chart_type: Line chart
probability: 0.45
WRITTEN ANSWER:
This data cannot determine deaths per mile; deaths per 1,000 reported crashes rose from 0.54 in 2013 to 0.95 in 2025. This framing answers whether motorist deaths changed relative to the volume of reported crashes, and the chart shows this crash-based rate increased between 2013 and 2025. It is defensible for comparing fatality burden per reported crash, but does not measure travel exposure or deaths per mile driven.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,"motorist_deaths_per_1,000_reported_crashes",motorist_deaths,reported_crashes
2013,0.539898,110,203742
2014,0.529008,109,206046
2015,0.436364,95,217708
2016,0.313271,72,229833
2017,0.463189,107,231007
2018,0.423209,98,231564
2019,0.387733,82,211486
2020,1.230982,139,112918
2021,1.212034,134,110558
2022,1.116598,116,103887
2023,1.273200,123,96607
2024,1.215559,111,91316
2025,0.946859,81,85546

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"DESCRIBE SELECT * FROM read_parquet('{p}')\").fetchdf().to_string(index=False)); print(c.execute(f\"SELECT year(crash_date) year, count(*) crashes, sum(coalesce(number_of_motorist_killed,0)) motorist_deaths, count(*) FILTER (WHERE coalesce(number_of_motorist_killed,0)>0) fatal_motorist_crashes FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").fetchdf().to_string(index=False))"
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=f\"SELECT year(crash_date) AS crash_year, count(*) AS crashes, sum(coalesce(number_of_motorist_killed,0)) AS motorist_deaths, count(*) FILTER (WHERE coalesce(number_of_motorist_killed,0)>0) AS fatal_motorist_crashes FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\"; print(c.execute(q).fetchdf().to_string(index=False))"
# bash
python -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT min(crash_date) AS first_date, max(crash_date) AS last_date, count(*) FILTER (WHERE crash_date >= DATE '2025-01-01') AS crashes_2025 FROM read_parquet('data/crashes.parquet')\").fetchdf().to_string(index=False))"
# bash
python -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT EXTRACT(YEAR FROM crash_date) AS yr, count(*) AS n, min(crash_date), max(crash_date) FROM read_parquet('data/crashes.parquet') GROUP BY 1 ORDER BY 1\").fetchdf().to_string(index=False)); print(c.execute(\"SELECT count(*) FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2025-01-01' AND crash_date < DATE '2026-01-01'\").fetchall())"
# bash
ls
# bash
python build_analysis.py
# bash
python build_analysis.py
# bash
python -c "import json, pathlib; p=pathlib.Path('out/options.json'); x=json.loads(p.read_text()); print('valid JSON; option count:', len(x['options']), 'probability sum:', sum(o['probability'] for o in x['options'])); print('artifacts:', sorted(f.name for f in pathlib.Path('out').iterdir()))"

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