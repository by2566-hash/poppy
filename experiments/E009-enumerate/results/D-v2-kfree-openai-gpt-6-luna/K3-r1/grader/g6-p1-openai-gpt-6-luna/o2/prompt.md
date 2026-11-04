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

QUESTION ASKED: How do motorist and cyclist deaths compare year by year in NYC, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Annual count of people killed while motorist or cyclist
denominator: None; raw death counts
grouping: Calendar year and road-user type
chart_type: Grouped bar chart
probability: 0.3
WRITTEN ANSWER:
The motorist-cyclist death gap was smallest in 2019 at 51 (82 motorist deaths versus 31 cyclist deaths) and largest in 2021 at 115 (134 versus 19). This framing answers how the two annual counts compare within each year, with paired bars making their absolute gaps visually accessible. Comparing raw counts is appropriate for describing the recorded fatality totals, but this chart does not normalize the difference or indicate risk by travel exposure.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
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
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT min(crash_date), max(crash_date), count(*), count_if(number_of_motorist_killed IS NULL), count_if(number_of_cyclist_killed IS NULL) FROM read_parquet('data/crashes.parquet')\").fetchall()); print(c.execute(\"SELECT year(crash_date) y, count(*) crashes, sum(number_of_motorist_killed) motorist_deaths, sum(number_of_cyclist_killed) cyclist_deaths, count_if(number_of_motorist_killed IS NULL) motorist_null, count_if(number_of_cyclist_killed IS NULL) cyclist_null FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY y ORDER BY y\").df().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT year(crash_date) y, min(crash_date), max(crash_date), count(*) FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY y ORDER BY y\").fetchall())"
# bash
ls
# bash
python3 out/generate_outputs.py
# bash
python3 -c "import json, pandas as pd; p=json.load(open('out/options.json')); assert len(p['options']) == 3; assert abs(sum(o['probability'] for o in p['options']) - 1) < 1e-9; d=pd.read_csv('out/values_1.csv'); assert d.year.tolist() == list(range(2013, 2026)); assert (d.motorist_deaths > d.cyclist_deaths).all(); assert int((d.motorist_deaths-d.cyclist_deaths).min()) == 51 and int((d.motorist_deaths-d.cyclist_deaths).max()) == 115; r=pd.read_csv('out/values_3.csv'); assert r.loc[r.cyclist_deaths_per_100_motorist_deaths.idxmax(), 'year'] == 2019; assert r.loc[r.cyclist_deaths_per_100_motorist_deaths.idxmin(), 'year'] == 2013; print('JSON and numeric claims validated; probabilities sum to', sum(o['probability'] for o in p['options']))"

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