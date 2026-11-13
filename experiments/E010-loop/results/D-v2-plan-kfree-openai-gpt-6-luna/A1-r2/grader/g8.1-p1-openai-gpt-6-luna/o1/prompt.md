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

QUESTION ASKED: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Annual count of pedestrians injured and annual count of pedestrians killed, separately summed across Brooklyn crash records
denominator: None; these are annual counts, with each crash row contributing its recorded pedestrian counts
grouping: Calendar year of crash_date
chart_type: Stacked annual bar chart
probability: 0.55
WRITTEN ANSWER:
Recorded pedestrian casualties declined 21.7% from 3,671 in 2013 to 2,874 in 2025, but pedestrian deaths rose from 30 to 39. This framing answers whether recorded pedestrian harm declined: total casualties fell from 3,671 in 2013 to 2,874 in 2025 (21.7%), although deaths rose from 30 to 39 and total casualties increased after their 2020 low. Summing injured and killed people measures the annual burden of recorded harm while keeping deaths distinguishable. It cannot establish risk per walking trip or distance, or explain why the counts changed, because the data has no pedestrian-exposure denominator or causal information. The final plan uses full years 2013-2025 and excludes partial 2026 (the file ends 2026-06-11); it also excludes 659,713 of 2,132,218 dated NYC crash rows (30.9%) with missing/unknown borough because they cannot be assigned to Brooklyn, while retaining valid zeros (no missing or negative pedestrian counts in selected Brooklyn rows).

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrians_injured,pedestrians_killed,pedestrian_casualties
2013,3641,30,3671
2014,3349,42,3391
2015,3029,46,3075
2016,2917,20,2937
2017,2663,20,2683
2018,2785,23,2808
2019,2700,33,2733
2020,1781,17,1798
2021,1905,32,1937
2022,2275,23,2298
2023,2385,22,2407
2024,2645,31,2676
2025,2835,39,2874

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
mkdir out
# bash
python3 out/data_check.py
# bash
python3 out/data_check.py
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT borough, COUNT(*) FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' GROUP BY borough ORDER BY borough\").fetchall())"
# bash
python3 out/data_check.py
# bash
python3 -c "import pandas as pd; d=pd.read_csv('out/check_1.csv').set_index('fact')['value']; years=range(2013,2026); a=sum(int(d[f'all_boroughs_dated_source_rows_{y}']) for y in years); m=sum(int(d[f'all_boroughs_borough_missing_or_unknown_{y}']) for y in years); print({'rows':a,'missing_borough':m,'share':m/a})"
# bash
python3 out/analyze.py
# bash
python3 -c "import json, pathlib, pandas as pd; p=pathlib.Path('out'); opts=json.loads((p/'options.json').read_text()); plans=[json.loads((p/f'plan_{i}.json').read_text()) for i in (1,2)]; assert len(opts['options'])==2 and abs(sum(x['probability'] for x in opts['options'])-1)<1e-9; assert all((p/f'option_{i}.png').is_file() and (p/f'values_{i}.csv').is_file() and (p/f'check_{i}.csv').is_file() for i in (1,2)); a=pd.read_csv(p/'values_1.csv'); b=pd.read_csv(p/'values_2.csv'); assert a.iloc[0].pedestrian_casualties==3671 and a.iloc[-1].pedestrian_casualties==2874 and b.iloc[0,1]==3498 and b.iloc[-1,1]==2766; assert all('final_plan' in x for x in plans); print('JSON, plans, charts, checks, and plotted data verified')"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR05: If a borough filter (borough = 'BROOKLYN') is used, the output discloses that crashes with no borough recorded (19.9–38.1% per year) are excluded.
- tr_TR11: The output does not call Brooklyn 'safer' or 'less safe' from counts alone without saying that there is no pedestrian exposure measure.
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.