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

QUESTION ASKED: How many pedestrians were killed in NYC motor vehicle crashes each year from 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: sum of number_of_pedestrians_killed by calendar year of crash_date; counts pedestrian deaths, not crashes
denominator: not applicable; annual count, not a rate or share
grouping: calendar year of crash_date
chart_type: bar chart
probability: 0.55
WRITTEN ANSWER:
The recorded annual pedestrian death counts were 176 (2013), 133 (2014), 133 (2015), 149 (2016), 127 (2017), 123 (2018), 131 (2019), 101 (2020), 132 (2021), 135 (2022), 107 (2023), 124 (2024), and 119 (2025). This framing answers the requested annual counts by summing number_of_pedestrians_killed across all police-reported NYC motor vehicle crash rows dated in each calendar year from 2013 through 2025; each bar represents pedestrian deaths, not crashes. The bars show the exact annual totals listed in the answer and support direct comparison of one calendar year with another. A bar chart is defensible for these discrete yearly counts because bar heights emphasize the size of each separate annual total; it cannot count deaths outside police-reported crashes or independently verify recorded deaths. The check covered 2,132,218 in-range crash rows and found 0 missing crash dates, 0 missing pedestrian-killed values, 0 candidate default dates, and observed date endpoints spanning January 1 to December 31 in every year; all in-range rows were kept, none were dropped or counted differently, and endpoint coverage does not establish complete reporting.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,pedestrians_killed
2013,176
2014,133
2015,133
2016,149
2017,127
2018,123
2019,131
2020,101
2021,132
2022,135
2023,107
2024,124
2025,119

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python - <<'PY'
import duckdb
import pandas as pd
from pathlib import Path

con = duckdb.connect()
path = 'data/crashes.parquet'
query = """
WITH scoped AS (
  SELECT crash_date, number_of_pedestrians_killed
  FROM read_parquet(?)
  WHERE crash_date >= DATE '2013-01-01'
    AND crash_date <= DATE '2025-12-31'
)
SELECT
  year(crash_date) AS year,
  count(*) AS rows,
  min(crash_date) AS first_crash_date,
  max(crash_date) AS last_crash_date,
  count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS pedestrian_killed_missing_rows,
  count(*) FILTER (WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01')) AS candidate_default_dates
FROM scoped
GROUP BY year
ORDER BY year
"""
years = con.execute(query, [path]).df()
total = con.execute("""
SELECT count(*) AS rows,
       count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS pedestrian_killed_missing_rows,
       count(*) FILTER (WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01')) AS candidate_default_dates
FROM read_parquet(?)
WHERE crash_date >= DATE '2013-01-01' AND crash_date <= DATE '2025-12-31'
""", [path]).fetchone()
null_dates = con.execute("SELECT count(*) FROM read_parquet(?) WHERE crash_date IS NULL", [path]).fetchone()[0]

facts = []
def add(fact, value):
    facts.append({'fact': fact, 'value': str(value)})
add('population_rows_2013_2025', total[0])
add('rows_with_missing_number_of_pedestrians_killed_2013_2025', total[1])
add('rows_with_candidate_default_crash_date_0001-01-01_1900-01-01_or_1970-01-01_in_population', total[2])
add('rows_with_missing_crash_date_in_entire_file_excluded_from_year_filter', null_dates)
for row in years.itertuples(index=False):
    y = int(row.year)
    add(f'rows_{y}', int(row.rows))
    add(f'first_observed_crash_date_{y}', row.first_crash_date)
    add(f'last_observed_crash_date_{y}', row.last_crash_date)
    add(f'rows_with_missing_number_of_pedestrians_killed_{y}', int(row.pedestrian_killed_missing_rows))
    add(f'candidate_default_crash_date_rows_{y}', int(row.candidate_default_dates))
    partial = row.first_crash_date > pd.Timestamp(year=y, month=1, day=1).date() or row.last_crash_date < pd.Timestamp(year=y, month=12, day=31).date()
    add(f'coverage_status_{y}', 'partial by observed min/max date' if partial else 'spans Jan 1 through Dec 31 by observed min/max date')
pd.DataFrame(facts, columns=['fact', 'value']).to_csv('out/check_1.csv', index=False)
print(pd.DataFrame(facts, columns=['fact', 'value']).to_string(index=False))
PY
# bash
python - <<'PY'
import duckdb
import pandas as pd
from datetime import date

con = duckdb.connect()
path = 'data/crashes.parquet'
query = """
WITH scoped AS (
  SELECT crash_date, number_of_pedestrians_killed
  FROM read_parquet(?)
  WHERE crash_date >= DATE '2013-01-01'
    AND crash_date <= DATE '2025-12-31'
)
SELECT year(crash_date) AS year, count(*) AS rows,
       min(crash_date) AS first_crash_date, max(crash_date) AS last_crash_date,
       count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS pedestrian_killed_missing_rows,
       count(*) FILTER (WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01')) AS candidate_default_dates
FROM scoped GROUP BY year ORDER BY year
"""
years = con.execute(query, [path]).df()
total = con.execute("""
SELECT count(*) AS rows,
       count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS pedestrian_killed_missing_rows,
       count(*) FILTER (WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01')) AS candidate_default_dates
FROM read_parquet(?)
WHERE crash_date >= DATE '2013-01-01' AND crash_date <= DATE '2025-12-31'
""", [path]).fetchone()
null_dates = con.execute("SELECT count(*) FROM read_parquet(?) WHERE crash_date IS NULL", [path]).fetchone()[0]
facts = []
def add(fact, value): facts.append({'fact': fact, 'value': str(value)})
add('population_rows_2013_2025', total[0])
add('rows_with_missing_number_of_pedestrians_killed_2013_2025', total[1])
add('rows_with_candidate_default_crash_date_0001-01-01_1900-01-01_or_1970-01-01_in_population', total[2])
add('rows_with_missing_crash_date_in_entire_file_excluded_from_year_filter', null_dates)
for row in years.itertuples(index=False):
    y = int(row.year)
    first = pd.Timestamp(row.first_crash_date).date()
    last = pd.Timestamp(row.last_crash_date).date()
    add(f'rows_{y}', int(row.rows))
    add(f'first_observed_crash_date_{y}', first)
    add(f'last_observed_crash_date_{y}', last)
    add(f'rows_with_missing_number_of_pedestrians_killed_{y}', int(row.pedestrian_killed_missing_rows))
    add(f'candidate_default_crash_date_rows_{y}', int(row.candidate_default_dates))
    partial = first > date(y, 1, 1) or last < date(y, 12, 31)
    add(f'coverage_status_{y}', 'partial by observed min/max date' if partial else 'spans Jan 1 through Dec 31 by observed min/max date')
check = pd.DataFrame(facts, columns=['fact', 'value'])
check.to_csv('out/check_1.csv', index=False)
print(check.to_string(index=False))
PY
# bash
python out/analyze_1.py
# bash
python - <<'PY'
import duckdb
import pandas as pd
from datetime import date

con = duckdb.connect()
path = 'data/crashes.parquet'
years = con.execute("""
SELECT year(crash_date) AS year, count(*) AS rows,
       min(crash_date) AS first_crash_date, max(crash_date) AS last_crash_date,
       count(*) FILTER (WHERE crash_date IS NULL) AS missing_crash_date_rows,
       count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS missing_pedestrian_killed_rows,
       count(*) FILTER (WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01')) AS candidate_default_dates
FROM read_parquet(?)
WHERE crash_date >= DATE '2013-01-01' AND crash_date <= DATE '2025-12-31'
GROUP BY year(crash_date) ORDER BY year
""", [path]).df()
total = con.execute("""
SELECT count(*) AS rows,
       count(*) FILTER (WHERE crash_date IS NULL) AS missing_crash_date_rows,
       count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS missing_pedestrian_killed_rows,
       count(*) FILTER (WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01')) AS candidate_default_dates
FROM read_parquet(?)
WHERE crash_date >= DATE '2013-01-01' AND crash_date <= DATE '2025-12-31'
""", [path]).fetchone()
facts = []
def add(fact, value): facts.append({'fact': fact, 'value': str(value)})
add('population_rows_2013_2025', total[0])
add('rows_with_missing_crash_date_2013_2025', total[1])
add('rows_with_missing_number_of_pedestrians_killed_2013_2025', total[2])
add('rows_with_candidate_default_crash_date_0001-01-01_1900-01-01_or_1970-01-01_in_population', total[3])
for row in years.itertuples(index=False):
    y = int(row.year)
    first = pd.Timestamp(row.first_crash_date).date()
    last = pd.Timestamp(row.last_crash_date).date()
    add(f'rows_{y}', int(row.rows))
    add(f'first_observed_crash_date_{y}', first)
    add(f'last_observed_crash_date_{y}', last)
    add(f'rows_with_missing_crash_date_{y}', int(row.missing_crash_date_rows))
    add(f'rows_with_missing_number_of_pedestrians_killed_{y}', int(row.missing_pedestrian_killed_rows))
    add(f'candidate_default_crash_date_rows_{y}', int(row.candidate_default_dates))
    partial = first > date(y, 1, 1) or last < date(y, 12, 31)
    add(f'coverage_status_{y}', 'partial by observed min/max date' if partial else 'spans Jan 1 through Dec 31 by observed min/max date')
check = pd.DataFrame(facts, columns=['fact', 'value'])
check.to_csv('out/check_1.csv', index=False)
print(check.to_string(index=False))
PY
# bash
python out/analyze_1.py
# bash
python - <<'PY'
import duckdb
import pandas as pd
from datetime import date

con = duckdb.connect()
path = 'data/crashes.parquet'
years = con.execute("""
SELECT year(crash_date) AS year, count(*) AS rows,
       min(crash_date) AS first_crash_date, max(crash_date) AS last_crash_date,
       count(*) FILTER (WHERE crash_date IS NULL) AS missing_crash_date_rows,
       count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS missing_pedestrian_killed_rows,
       count(*) FILTER (WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01')) AS candidate_default_dates
FROM read_parquet(?)
WHERE crash_date >= DATE '2013-01-01' AND crash_date <= DATE '2025-12-31'
GROUP BY year(crash_date) ORDER BY year
""", [path]).df()
total = con.execute("""
SELECT count(*) AS rows,
       count(*) FILTER (WHERE crash_date IS NULL) AS missing_crash_date_rows,
       count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS missing_pedestrian_killed_rows,
       count(*) FILTER (WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01')) AS candidate_default_dates
FROM read_parquet(?)
WHERE crash_date >= DATE '2013-01-01' AND crash_date <= DATE '2025-12-31'
""", [path]).fetchone()
facts = []
def add(fact, value): facts.append({'fact': fact, 'value': str(value)})
add('population_rows_2013_2025', total[0])
add('rows_with_missing_crash_date_2013_2025', total[1])
add('rows_with_missing_number_of_pedestrians_killed_2013_2025', total[2])
add('rows_with_candidate_default_crash_date_0001-01-01_1900-01-01_or_1970-01-01_in_population', total[3])
for row in years.itertuples(index=False):
    y = int(row.year)
    first = pd.Timestamp(row.first_crash_date).date()
    last = pd.Timestamp(row.last_crash_date).date()
    add(f'rows_{y}', int(row.rows))
    add(f'first_observed_crash_date_{y}', first)
    add(f'last_observed_crash_date_{y}', last)
    add(f'rows_with_missing_crash_date_{y}', int(row.missing_crash_date_rows))
    add(f'rows_with_missing_number_of_pedestrians_killed_{y}', int(row.missing_pedestrian_killed_rows))
    add(f'candidate_default_crash_date_rows_{y}', int(row.candidate_default_dates))
    partial = first > date(y, 1, 1) or last < date(y, 12, 31)
    add(f'coverage_status_{y}', 'partial by observed min/max date' if partial else 'spans Jan 1 through Dec 31 by observed min/max date')
check = pd.DataFrame(facts, columns=['fact', 'value'])
check.to_csv('out/check_2.csv', index=False)
print(check.to_string(index=False))
PY
# bash
python out/analyze_2.py
# bash
python out/analyze_1.py && python - <<'PY'
import json
from pathlib import Path
import pandas as pd

out = Path('out')
options = json.loads((out / 'options.json').read_text())['options']
assert len(options) == 2
assert abs(sum(option['probability'] for option in options) - 1) < 1e-9
expected = [(2013,176),(2014,133),(2015,133),(2016,149),(2017,127),(2018,123),(2019,131),(2020,101),(2021,132),(2022,135),(2023,107),(2024,124),(2025,119)]
for option_id in (1, 2):
    rows = pd.read_csv(out / f'values_{option_id}.csv')
    assert list(rows.itertuples(index=False, name=None)) == expected
    assert (out / f'option_{option_id}.png').is_file()
print('JSON valid; probabilities sum to 1; both plotted value files and charts verified.')
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
- tr_TR07: The output does not present the open-data death counts as the official NYC toll. The counts are qualified when the written output (answer, interpretation or declared framing fields) ties them to this data in any wording: reported, recorded, police-reported crashes, in this dataset (e.g. 'pedestrians killed in reported motor vehicle crashes' qualifies). A qualification or source note that appears only inside the chart image does not count, and a chart title without one is fine when the written output has it. FAIL only when no such qualification appears in the written output (Bo 2026-11-04, refined 2026-11-06).
- tr_CAUSAL: The output makes no causal attribution (e.g. 'because of the pandemic') that the data cannot support.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.