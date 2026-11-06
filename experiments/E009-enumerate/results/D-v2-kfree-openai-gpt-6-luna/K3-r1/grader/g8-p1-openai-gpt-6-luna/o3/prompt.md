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
metric: Cyclist deaths per 100 motorist deaths
denominator: Motorist deaths in the same calendar year
grouping: Calendar year
chart_type: Line chart of annual ratio
probability: 0.2
WRITTEN ANSWER:
Cyclist deaths ranged from 10.0 per 100 motorist deaths in 2013 to a peak of 37.8 per 100 in 2019. This answers the relative-count part of the question: cyclist deaths were between 10.0 and 37.8 per 100 motorist deaths across the years shown. The ratio is a defensible way to compare the groups' recorded counts proportionally, but it does not show their absolute totals by itself or estimate risk per person or trip.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,motorist_deaths,cyclist_deaths,cyclist_deaths_per_100_motorist_deaths
2013,110,11,10.0
2014,109,20,18.3
2015,95,15,15.8
2016,72,18,25.0
2017,107,27,25.2
2018,98,10,10.2
2019,82,31,37.8
2020,139,29,20.9
2021,134,19,14.2
2022,116,19,16.4
2023,123,31,25.2
2024,111,24,21.6
2025,81,23,28.4

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