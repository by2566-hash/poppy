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

QUESTION ASKED: Since 2013, has it gotten safer for pedestrians in Brooklyn? Make a chart for a local news story and sum up what you find.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Brooklyn crash reports with at least one pedestrian injured or killed per 1,000 crash reports
denominator: All police-reported Brooklyn motor vehicle crashes in the same calendar year
grouping: Calendar year, 2013–2025
chart_type: Line chart
probability: 0.35
WRITTEN ANSWER:
This dataset cannot show risk per walking trip, but pedestrian-casualty crashes rose from 74.4 to 113.8 per 1,000 reported Brooklyn crashes from 2013 to 2025 (+53.0%). This framing answers how often reported crashes involved pedestrian injury or death relative to the total volume of Brooklyn crash reports: that share was higher in 2025 than in 2013. It accounts for changes in crash-report volume, but its denominator is crashes rather than people walking or walking trips, so it cannot establish pedestrian exposure-adjusted safety.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,total_crash_reports,crashes_with_pedestrian_casualty,pedestrian_casualties_per_1000_crash_reports
2013,47024,3498.000,74.388
2014,47761,3234.000,67.712
2015,50851,2962.000,58.249
2016,47464,2797.000,58.929
2017,44915,2550.000,56.774
2018,47313,2697.000,57.003
2019,44479,2623.000,58.972
2020,25473,1724.000,67.680
2021,25174,1856.000,73.727
2022,23369,2185.000,93.500
2023,22890,2310.000,100.917
2024,22785,2576.000,113.057
2025,24303,2766.000,113.813

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; c=duckdb.connect(); print(c.execute(\"describe select * from read_parquet('data/crashes.parquet')\").fetchall()); print(c.execute(\"select min(crash_date), max(crash_date), count(*) from read_parquet('data/crashes.parquet')\").fetchall())"
# bash
python -c "import duckdb; c=duckdb.connect(); q=\"select year(crash_date) as year, count(*) as crashes, sum(coalesce(number_of_pedestrians_injured,0)) as ped_injured, sum(coalesce(number_of_pedestrians_killed,0)) as ped_killed, sum(coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0)) as ped_casualties, sum(case when coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0)>0 then 1 else 0 end) as crashes_with_ped_casualty from read_parquet('data/crashes.parquet') where borough='BROOKLYN' and crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1 order by 1\"; print(c.execute(q).df().to_string(index=False))"
# bash
ls -la
# bash
ls -la out
# bash
python out/generate_charts.py
# bash
python out/generate_charts.py
# bash
ls -l out
# bash
python -c "import json, pathlib, pandas as pd; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); assert len(o['options']) == 3; assert abs(sum(x['probability'] for x in o['options'])-1)<1e-9; [(lambda d: print(f'option {i}: {len(d)} rows, {d.iloc[0].to_dict()} -> {d.iloc[-1].to_dict()}'))(pd.read_csv(p/f'values_{i}.csv')) for i in range(1,4)]; print('options valid; probabilities sum to', sum(x['probability'] for x in o['options']))"

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
- tr_TR01: If a per-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording.
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.