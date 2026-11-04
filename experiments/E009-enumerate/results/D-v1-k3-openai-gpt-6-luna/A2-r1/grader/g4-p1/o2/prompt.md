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

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts fall sharply in 2020 (TR01): a per-reported-crash rate or a pooled count COMPARED ACROSS YEARS spanning 2020 needs a caveat; a comparison between groups within one pooled window (e.g. day vs night) does not (decided 2026-11-04).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Are NYC's streets more dangerous at night? Make a chart and give a conclusion for a news report.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Reported people injured per 100 crashes
denominator: All reported crashes in the corresponding time period
grouping: Night (20:00–05:59) versus day (06:00–19:59)
chart_type: Two-bar comparison
probability: 0.4
WRITTEN ANSWER:
There were 40.45 people reported injured per 100 nighttime crashes, compared with 31.01 per 100 daytime crashes. This indicates greater injury burden per reported crash at night, but not greater risk per trip without traffic-exposure data.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
period,injured_people,crashes,injured_people_per_100_crashes
Day,530247,1710183,31.005278382488893
Night,226106,559004,40.44801110546615

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