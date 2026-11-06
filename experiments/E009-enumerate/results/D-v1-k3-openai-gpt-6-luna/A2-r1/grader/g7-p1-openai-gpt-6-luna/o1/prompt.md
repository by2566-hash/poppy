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

QUESTION ASKED: Are NYC's streets more dangerous at night? Make a chart and give a conclusion for a news report.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Average reported crash count per clock-hour per observed calendar date
denominator: Observed calendar dates multiplied by the number of hours in each period (10 night hours; 14 day hours)
grouping: Hour of day, highlighting night (20:00–05:59) versus day (06:00–19:59)
chart_type: 24-hour line chart
probability: 0.3
WRITTEN ANSWER:
Across the observed dates, the average was 10.97 reported crashes per nighttime clock-hour, versus 23.98 per daytime clock-hour. This measures crash frequency, not risk per trip, because traffic exposure is not in the data.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
hour,crashes,observed_dates,crashes_per_observed_date,period
0,75806,5094,14.881429132312524,Night
1,40498,5094,7.950137416568512,Night
2,31269,5094,6.138398115429918,Night
3,27571,5094,5.412446014919513,Night
4,31321,5094,6.148606203376521,Night
5,33878,5094,6.650569297212407,Night
6,51553,5094,10.120337652139773,Day
7,70581,5094,13.855712603062427,Day
8,124228,5094,24.387122104436592,Day
9,118950,5094,23.3510011778563,Day
10,111160,5094,21.82175107970161,Day
11,115977,5094,22.767373380447584,Day
12,123461,5094,24.236552807224186,Day
13,129341,5094,25.390851982724776,Day
14,149385,5094,29.32567726737338,Day
15,141172,5094,27.713388299960737,Day
16,161385,5094,31.681389870435808,Day
17,158232,5094,31.062426383981155,Day
18,139496,5094,27.384373773066354,Day
19,115262,5094,22.627012171181782,Day
20,96751,5094,18.993129171574402,Night
21,82841,5094,16.262465645857873,Night
22,75404,5094,14.802512760109932,Night
23,63665,5094,12.498036906164115,Night

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__); print('pandas', pandas.__version__); print('matplotlib', matplotlib.__version__)"
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(f\"DESCRIBE SELECT * FROM read_parquet('{p}')\").fetchdf().to_string(index=False)); print(c.execute(f\"SELECT COUNT(*) rows, MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE crash_time IS NULL) null_time FROM read_parquet('{p}')\").fetchall()); print(c.execute(f\"SELECT EXTRACT(hour FROM crash_time) hr, COUNT(*) n, SUM(number_of_persons_injured) injured, SUM(number_of_persons_killed) killed FROM read_parquet('{p}') GROUP BY hr ORDER BY hr\").fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(f\"SELECT COUNT(*) AS total, MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE crash_time IS NULL) AS null_time FROM read_parquet('{p}')\").fetchall()); print(c.execute(f\"SELECT CASE WHEN EXTRACT(hour FROM crash_time) >= 20 OR EXTRACT(hour FROM crash_time) < 6 THEN 'Night (20:00–05:59)' ELSE 'Day (06:00–19:59)' END AS period, COUNT(*) AS crashes, SUM(COALESCE(number_of_persons_injured,0)) AS injured, SUM(COALESCE(number_of_persons_killed,0)) AS killed, COUNT(*) FILTER (WHERE COALESCE(number_of_persons_killed,0)>0) AS fatal_crashes, COUNT(*) FILTER (WHERE COALESCE(number_of_persons_injured,0)+COALESCE(number_of_persons_killed,0)>0) AS injury_or_fatal_crashes FROM read_parquet('{p}') WHERE crash_time IS NOT NULL GROUP BY 1 ORDER BY 1\").fetchdf().to_string(index=False)); print(c.execute(f\"SELECT COUNT(*) FILTER (WHERE crash_time IS NULL) FROM read_parquet('{p}')\").fetchall())"
# bash
python3 out/generate_analysis.py
# bash
python3 -c "import json, pathlib, pandas as pd; out=pathlib.Path('out'); o=json.loads((out/'options.json').read_text()); assert [x['id'] for x in o['options']]==[1,2,3]; assert abs(sum(x['probability'] for x in o['options'])-1)<1e-9; assert all((out/f'option_{i}.png').is_file() and (out/f'values_{i}.csv').is_file() for i in (1,2,3)); h=pd.read_csv(out/'values_1.csv'); v2=pd.read_csv(out/'values_2.csv').set_index('period'); v3=pd.read_csv(out/'values_3.csv').set_index('period'); n_dates=int(h.observed_dates.iloc[0]); night=h[h.period=='Night'].crashes.sum()/(n_dates*10); day=h[h.period=='Day'].crashes.sum()/(n_dates*14); assert f'{night:.2f}' in o['options'][0]['answer'] and f'{day:.2f}' in o['options'][0]['answer']; assert f\"{v2.loc['Night','injured_people_per_100_crashes']:.2f}\" in o['options'][1]['answer']; assert f\"{v3.loc['Night','fatal_crashes_per_1000_crashes']:.2f}\" in o['options'][2]['answer']; print('JSON, artifacts, probabilities, and answer-value checks passed')"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR11: Severity per crash (deaths or injuries per crash) is described as such, not as the risk of being on the street at night (no traffic volume by hour exists).
- tr_TR08: NA if the option uses no killed or injured counts. Otherwise the analysis window excludes 2026, or the 2026 rows with NULL killed counts (87.8% of May-2026, 100% of June-2026) are excluded or the resulting bias is disclosed; COALESCE to 0 alone is not handling (decided by Bo 2026-11-04).
- tr_NIGHTDEF: The definition of 'night' (hours) is stated.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.