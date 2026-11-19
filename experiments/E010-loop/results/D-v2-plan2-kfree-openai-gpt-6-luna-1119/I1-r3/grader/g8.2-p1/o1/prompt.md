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
metric: Annual count of reported motorist deaths, calculated as the sum of number_of_motorist_killed
denominator: None
grouping: crash_date calendar year, 2013-2025 inclusive
chart_type: bar chart
probability: 0.65
WRITTEN ANSWER:
Reported motorist deaths fell from 110 in 2013 to 81 in 2025 (26.4% lower), but this crash data cannot show whether risk per mile declined. The question asks about risk per mile, which this option cannot measure because the crash file has no miles-driven exposure; instead, it plots the yearly sum of persons classified as motorists killed on police-reported NYC crash records with nonmissing number_of_motorist_killed, grouped by crash_date calendar year from 2013 through 2025, with no denominator. This is a defensible direct count of the fatal outcome, and the values show 110 deaths in 2013 versus 81 in 2025, a 26.4% lower count. The count does not establish a decline in risk per mile, because neither miles driven nor another exposure denominator is available. In the 2,132,218 dated crash rows in the selected years, none has a missing motorist-death field and no crash_date is missing in the file, so no such rows were excluded; all years, including 2025, have Jan 1-Dec 31 date endpoints, but daily reporting completeness is not established.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_deaths
2013,110.0
2014,109.0
2015,95.0
2016,72.0
2017,107.0
2018,98.0
2019,82.0
2020,139.0
2021,134.0
2022,116.0
2023,123.0
2024,111.0
2025,81.0

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python - <<'PY'
import csv
import duckdb
from pathlib import Path

src = 'data/crashes.parquet'
out = Path('out')
con = duckdb.connect()
for option, fields in [(1, ['number_of_motorist_killed']), (2, ['number_of_motorist_killed', 'number_of_persons_killed'])]:
    cols = ', '.join(f'count(*) FILTER (WHERE {c} IS NULL) AS missing_{i}' for i, c in enumerate(fields))
    completeness = ' AND '.join(f'{c} IS NOT NULL' for c in fields)
    query = f"""
        SELECT year(crash_date) AS yr, count(*) AS candidate_rows,
               count(*) FILTER (WHERE {completeness}) AS complete_rows,
               min(crash_date) AS first_date, max(crash_date) AS last_date,
               {cols}
        FROM read_parquet('{src}')
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        GROUP BY yr ORDER BY yr
    """
    rows = con.execute(query).fetchall()
    facts = []
    total_candidates = sum(r[1] for r in rows)
    total_complete = sum(r[2] for r in rows)
    facts.extend([
        ('years_checked', '2013-2025 inclusive; restricted to non-NULL crash_date in this interval'),
        ('candidate_rows_in_years', total_candidates),
        ('final_population_rows_with_required_fields', total_complete),
        ('rows_removed_for_missing_required_death_field', total_candidates-total_complete),
        ('crash_date_missing_in_checked_rows', 0),
        ('crash_date_impossible_or_default_in_checked_rows', 'none observed; crash_date is a typed DATE and all selected dates fall within 2013-2025'),
    ])
    for r in rows:
        year, candidate, complete, first, last, *missing = r
        facts.extend([
            (f'{year}_candidate_rows', candidate),
            (f'{year}_final_population_rows_with_required_fields', complete),
            (f'{year}_first_crash_date', str(first)),
            (f'{year}_last_crash_date', str(last)),
            (f'{year}_year_coverage', 'partial' if (str(first)[:4] != str(year) or str(first)[5:] != '01-01' or str(last)[:4] != str(year) or str(last)[5:] != '12-31') else 'date endpoints span full calendar year; daily completeness is not established'),
        ])
        for i, field in enumerate(fields):
            facts.append((f'{year}_{field}_missing_rows', missing[i]))
    with (out / f'check_{option}.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['fact', 'value'])
        writer.writerows(facts)
con.close()
PY
# bash
python - <<'PY'
import csv
import duckdb
from pathlib import Path

con = duckdb.connect()
missing_dates = con.execute("SELECT count(*) FROM read_parquet('data/crashes.parquet') WHERE crash_date IS NULL").fetchone()[0]
for option in (1, 2):
    path = Path(f'out/check_{option}.csv')
    with path.open(newline='') as f:
        rows = list(csv.reader(f))
    rows.append(['crash_date_missing_rows_unassignable_to_any_year', missing_dates])
    with path.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
con.close()
PY
# bash
python out/analyze.py
# bash
python out/analyze.py && python - <<'PY'
import json
from pathlib import Path
import pandas as pd

out = Path('out')
for name in ['plan_1.json', 'plan_2.json', 'options.json']:
    json.loads((out / name).read_text())
options = json.loads((out / 'options.json').read_text())['options']
assert abs(sum(option['probability'] for option in options) - 1) < 1e-12
v1 = pd.read_csv(out / 'values_1.csv')
v2 = pd.read_csv(out / 'values_2.csv')
assert list(v1['year']) == list(range(2013, 2026))
assert list(v2['year']) == list(range(2013, 2026))
assert int(v1.loc[v1.year.eq(2013), 'motorist_deaths'].iloc[0]) == 110
assert int(v1.loc[v1.year.eq(2025), 'motorist_deaths'].iloc[0]) == 81
assert round(v2.loc[v2.year.eq(2013), 'motorist_death_share'].iloc[0] * 100, 1) == 37.0
assert round(v2.loc[v2.year.eq(2025), 'motorist_death_share'].iloc[0] * 100, 1) == 35.4
assert all((out / f'option_{i}.png').is_file() for i in (1, 2))
print('JSON valid; option values and charts verified.')
PY

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.