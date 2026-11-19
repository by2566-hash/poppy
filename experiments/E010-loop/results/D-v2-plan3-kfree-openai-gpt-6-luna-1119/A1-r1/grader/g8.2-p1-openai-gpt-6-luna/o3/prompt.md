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
metric: For each calendar year, count each Brooklyn crash record once if it reports at least one pedestrian injury or death, divide by all Brooklyn crash records that year, and express the result as a percentage.
denominator: All police-reported Brooklyn crash rows in that calendar year; a crash record is the denominator unit, not a pedestrian or travel-exposure unit.
grouping: Calendar year of crash_date, 2013-2025 inclusive.
chart_type: Line chart
probability: 0.2
WRITTEN ANSWER:
This file cannot establish whether pedestrian safety improved; the share of Brooklyn crash reports with a reported pedestrian injury or death is 7.4% in 2013 and 11.4% in 2025. This answers the crash-record-composition part: for each calendar year from 2013 through 2025, the numerator counts each Brooklyn crash record once when its pedestrian-injured or pedestrian-killed count is positive, and the denominator is all Brooklyn police-reported crash rows that year. The plotted share is 7.4% in 2013, reaches a low of 5.7% in 2017, and is 11.4% in 2025. This is a defensible way to compare the fraction of crash reports involving a pedestrian casualty, but it leaves unanswered risk per pedestrian, trip, or distance walked and is not an exposure-based safety rate. The check found 0 of 483,501 Brooklyn rows from 2013-2026 missing/unknown borough or crash_date and 0 missing/impossible values in either classification field, so the complete 2013-2025 rows are kept and the 9,700 partial 2026 rows are excluded (coverage ends June 11); annual denominators range from 50,851 rows in 2015 to 22,785 in 2024 and 24,303 in 2025, so the percentages describe a changing crash-record pool rather than a constant exposure base.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,brooklyn_crash_rows,crashes_with_pedestrian_casualty,share_pct
2013,47024,3498,7.438754678462062
2014,47761,3234,6.77121500806097
2015,50851,2962,5.824860868026194
2016,47464,2797,5.892887240856228
2017,44915,2550,5.677390626739396
2018,47313,2697,5.700336059856699
2019,44479,2623,5.897164954248072
2020,25473,1724,6.76795037883249
2021,25174,1856,7.37268610471121
2022,23369,2185,9.349993581240104
2023,22890,2310,10.091743119266056
2024,22785,2576,11.30568356374808
2025,24303,2766,11.381310949265522

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
ls
# bash
python3 - <<'PY'
import csv, json
from pathlib import Path
import duckdb

root = Path('.')
out = root / 'out'
plans = [json.loads((out / f'plan_{i}.json').read_text())['initial_plan'] for i in (1, 2, 3)]
con = duckdb.connect()
path = str(root / 'data' / 'crashes.parquet')
# The check is deliberately limited to Brooklyn rows dated from 2013 onward,
# and reports no outcome values or outcome sums.
base = f"read_parquet('{path}')"
where = "borough = 'Brooklyn' AND crash_date >= DATE '2013-01-01'"
per_year = con.execute(f"""
    SELECT year(crash_date) AS year, count(*) AS rows,
           min(crash_date) AS first_date, max(crash_date) AS last_date,
           count(*) FILTER (WHERE borough IS NULL OR trim(borough) = '' OR lower(trim(borough)) IN ('unknown','unspecified','null','n/a','na')) AS borough_missing_or_unknown,
           count(*) FILTER (WHERE crash_date IS NULL) AS crash_date_missing,
           count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL OR number_of_pedestrians_injured < 0) AS pedestrian_injured_missing_or_impossible,
           count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL OR number_of_pedestrians_killed < 0) AS pedestrian_killed_missing_or_impossible
    FROM {base}
    WHERE {where}
    GROUP BY year ORDER BY year
""").fetchall()
total = con.execute(f"SELECT count(*) FROM {base} WHERE {where}").fetchone()[0]
first_year = per_year[0][0] if per_year else None
last_year = per_year[-1][0] if per_year else None
for i in (1, 2, 3):
    facts = [
        ('population_rows_2013_onward', total),
        ('included_calendar_years', f'{first_year}-{last_year}' if per_year else 'none'),
        ('borough_missing_or_unknown_in_population', sum(r[5] for r in per_year)),
        ('crash_date_missing_in_population', sum(r[6] for r in per_year)),
    ]
    for row in per_year:
        year, count, first, last, bmiss, dmiss, imiss, kmiss = row
        # A date-range boundary short of Jan 1/Dec 31 means only part of year in file.
        partial = first.month != 1 or first.day != 1 or last.month != 12 or last.day != 31
        facts.extend([
            (f'rows_{year}', count),
            (f'coverage_{year}', f'{first} through {last}; ' + ('partial year' if partial else 'full calendar year by date range')),
            (f'borough_missing_or_unknown_{year}', bmiss),
            (f'crash_date_missing_{year}', dmiss),
            (f'pedestrian_injured_missing_or_impossible_{year}', imiss),
            (f'pedestrian_killed_missing_or_impossible_{year}', kmiss),
        ])
    for col, index in [('pedestrian_injured_missing_or_impossible', 6), ('pedestrian_killed_missing_or_impossible', 7)]:
        facts.append((f'{col}_total', sum(r[index] for r in per_year)))
    with (out / f'check_{i}.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['fact', 'value'])
        writer.writerows(facts)
PY
# bash
python3 - <<'PY'
import csv
from pathlib import Path
import duckdb
out = Path('out')
con = duckdb.connect()
base = "read_parquet('data/crashes.parquet')"
where = "lower(trim(borough)) = 'brooklyn' AND crash_date >= DATE '2013-01-01'"
per_year = con.execute(f"""
    SELECT year(crash_date) AS year, count(*) AS rows,
           min(crash_date) AS first_date, max(crash_date) AS last_date,
           count(*) FILTER (WHERE borough IS NULL OR trim(borough) = '' OR lower(trim(borough)) IN ('unknown','unspecified','null','n/a','na')) AS borough_missing_or_unknown,
           count(*) FILTER (WHERE crash_date IS NULL) AS crash_date_missing,
           count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL OR number_of_pedestrians_injured < 0) AS pedestrian_injured_missing_or_impossible,
           count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL OR number_of_pedestrians_killed < 0) AS pedestrian_killed_missing_or_impossible
    FROM {base}
    WHERE {where}
    GROUP BY year ORDER BY year
""").fetchall()
total = sum(r[1] for r in per_year)
first_year = per_year[0][0] if per_year else None
last_year = per_year[-1][0] if per_year else None
for i in (1, 2, 3):
    facts = [
        ('population_rows_2013_onward', total),
        ('included_calendar_years', f'{first_year}-{last_year}' if per_year else 'none'),
        ('borough_filter', "lower(trim(borough)) = 'brooklyn' (case/space normalized)"),
        ('borough_missing_or_unknown_in_population', sum(r[4] for r in per_year)),
        ('crash_date_missing_in_population', sum(r[5] for r in per_year)),
        ('pedestrian_injured_missing_or_impossible_total', sum(r[6] for r in per_year)),
        ('pedestrian_killed_missing_or_impossible_total', sum(r[7] for r in per_year)),
    ]
    for year, count, first, last, bmiss, dmiss, imiss, kmiss in per_year:
        partial = first.month != 1 or first.day != 1 or last.month != 12 or last.day != 31
        facts.extend([
            (f'rows_{year}', count),
            (f'coverage_{year}', f'{first} through {last}; ' + ('partial year' if partial else 'full calendar year by date range')),
            (f'borough_missing_or_unknown_{year}', bmiss),
            (f'crash_date_missing_{year}', dmiss),
            (f'pedestrian_injured_missing_or_impossible_{year}', imiss),
            (f'pedestrian_killed_missing_or_impossible_{year}', kmiss),
        ])
    with (out / f'check_{i}.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['fact', 'value'])
        writer.writerows(facts)
PY
# bash
python3 out/analyze.py
# bash
python3 out/analyze.py
# bash
python3 -c "import json; from pathlib import Path; p=Path('out'); opts=json.loads((p/'options.json').read_text()); plans=[json.loads((p/f'plan_{i}.json').read_text()) for i in (1,2,3)]; assert len(opts['options'])==3; assert abs(sum(x['probability'] for x in opts['options'])-1)<1e-9; assert all('final_plan' in x for x in plans); assert all((p/f'option_{i}.png').exists() and (p/f'values_{i}.csv').exists() and (p/f'check_{i}.csv').exists() for i in (1,2,3)); print('JSON valid; probabilities sum to 1; all plans and chart/value/check artifacts present.')"

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