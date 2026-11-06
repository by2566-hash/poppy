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
metric: Annual number of deaths among motorists and cyclists
denominator: None; absolute death counts, not population-adjusted rates
grouping: Crash year, with side-by-side bars for road-user group
chart_type: Grouped bar chart
probability: 0.3
WRITTEN ANSWER:
The side-by-side annual counts show more motorist than cyclist deaths in all 13 years; motorist deaths peaked at 139 in 2020 while cyclist deaths peaked at 31 in both 2019 and 2023. This framing answers the question as a direct year-by-year comparison of the two death counts. Paired bars make the absolute difference for each year visible, and the peaks identify when each group had its highest count. It does not show risk per traveler or explain why counts differ.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,road_user,deaths
2013,Motorists,110
2014,Motorists,109
2015,Motorists,95
2016,Motorists,72
2017,Motorists,107
2018,Motorists,98
2019,Motorists,82
2020,Motorists,139
2021,Motorists,134
2022,Motorists,116
2023,Motorists,123
2024,Motorists,111
2025,Motorists,81
2013,Cyclists,11
2014,Cyclists,20
2015,Cyclists,15
2016,Cyclists,18
2017,Cyclists,27
2018,Cyclists,10
2019,Cyclists,31
2020,Cyclists,29
2021,Cyclists,19
2022,Cyclists,19
2023,Cyclists,31
2024,Cyclists,24
2025,Cyclists,23

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb,pandas,matplotlib; print('duckdb',duckdb.__version__); print('pandas',pandas.__version__)"
# bash
python -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(f\"DESCRIBE SELECT * FROM read_parquet('{p}')\").fetchdf().to_string(index=False)); print(c.execute(f\"SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet('{p}')\").fetchall()); print(c.execute(f\"SELECT EXTRACT(year FROM crash_date) year, sum(number_of_motorist_killed) motorist_deaths, sum(number_of_cyclist_killed) cyclist_deaths, count(*) crashes FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").fetchdf().to_string(index=False))"
# bash
python -c "import duckdb; c=duckdb.connect(); q=\"SELECT year(crash_date) AS crash_year, sum(coalesce(number_of_motorist_killed,0)) AS motorist_deaths, sum(coalesce(number_of_cyclist_killed,0)) AS cyclist_deaths, sum(coalesce(number_of_persons_killed,0)) AS all_deaths, count(*) AS crashes FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY crash_year ORDER BY crash_year\"; print(c.execute(q).fetchdf().to_string(index=False))"
# bash
python out/_build_options.py
# bash
python -c "import json,pathlib,pandas as pd; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); assert len(o['options'])==3 and abs(sum(x['probability'] for x in o['options'])-1)<1e-9; a=pd.read_csv(p/'values_1.csv'); b=pd.read_csv(p/'values_2.csv'); g=pd.read_csv(p/'values_3.csv'); assert a.equals(b); assert len(a)==26 and set(a.year)==set(range(2013,2026)); assert (g.motorist_minus_cyclist_deaths==g.motorist_deaths-g.cyclist_deaths).all(); assert all((p/f'option_{i}.png').is_file() for i in (1,2,3)); assert all((p/f'values_{i}.csv').is_file() for i in (1,2,3)); print('Validated JSON, probabilities, annual plotted data, gap calculations, and chart/CSV files.')"

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