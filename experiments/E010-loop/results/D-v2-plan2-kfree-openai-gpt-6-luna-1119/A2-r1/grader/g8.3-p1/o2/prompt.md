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

QUESTION ASKED: Are NYC's streets more dangerous at night? Make a chart and give a conclusion for a news report.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Mean reported casualties per crash, calculated as the sum of number_of_persons_injured plus number_of_persons_killed divided by eligible crashes in the same time group
denominator: Eligible crashes in the same time group
grouping: Day: 06:00–19:59; night: 20:00–23:59 and 00:01–05:59; exact 00:00 is a separate possible-default-time group
chart_type: Bar chart
probability: 0.45
WRITTEN ANSWER:
Night crashes averaged 0.409 reported injured or killed people per crash, compared with 0.310 for daytime crashes; the separate 00:00 group averaged 0.359. This framing compares mean casualties—reported persons injured plus killed divided by crashes with known time and both outcome fields—in one-row-per-crash police reports from complete calendar years 2013–2025; day is 06:00–19:59, night is 20:00–23:59 plus 00:01–05:59, and exact 00:00 is separate. Mean casualties per crash are 0.409 for 500,924 night crashes, 0.310 for 1,607,466 daytime crashes, and 0.359 for 23,786 eligible exact-midnight crashes. This is a defensible comparison of the reported harm burden per crash, but it cannot establish per-trip or per-mile danger because traffic exposure is not in the data. The check found partial 2012 (July 1–December 31) and 2026 (January 1–June 11), which were excluded; 42 of 2,132,218 complete-year records (0.002%) were missing one or both injury/death fields and were excluded, and of 23,787 exact-00:00 records (1.12%), 23,786 eligible rows were kept separately while one missing-outcome row was excluded; no dates or times were missing.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
time_group,eligible_crashes,reported_casualties,mean_casualties_per_crash
Day,1607466,498056.000000,0.309839
Night,500924,205058.000000,0.409360
00:00 (possible default),23786,8545.000000,0.359245

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python - <<'PY'
import duckdb, csv
from pathlib import Path
con = duckdb.connect()
p = 'data/crashes.parquet'
base = f"read_parquet('{p}')"
rows = con.execute(f"""
SELECT year(crash_date) AS yr, count(*) AS total,
       count(*) FILTER (WHERE crash_time IS NOT NULL AND number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL) AS eligible,
       count(*) FILTER (WHERE crash_time IS NULL) AS time_missing,
       count(*) FILTER (WHERE crash_time = TIME '00:00:00') AS time_midnight,
       count(*) FILTER (WHERE number_of_persons_injured IS NULL) AS injured_missing,
       count(*) FILTER (WHERE number_of_persons_killed IS NULL) AS killed_missing,
       count(*) FILTER (WHERE crash_date IN (DATE '1900-01-01', DATE '1970-01-01', DATE '0001-01-01')) AS date_sentinel
FROM {base} WHERE crash_date IS NOT NULL GROUP BY yr ORDER BY yr
""").fetchall()
allfacts = []
def add(f, v): allfacts.append((f, str(v)))
add('rows_with_missing_crash_date', con.execute(f'SELECT count(*) FROM {base} WHERE crash_date IS NULL').fetchone()[0])
add('date_valid_rows_total', sum(r[1] for r in rows))
add('date_valid_rows_eligible_nonmissing_time_and_outcomes', sum(r[2] for r in rows))
if rows:
    add('earliest_crash_date', con.execute(f'SELECT min(crash_date) FROM {base}').fetchone()[0])
    add('latest_crash_date', con.execute(f'SELECT max(crash_date) FROM {base}').fetchone()[0])
    add('first_year', rows[0][0]); add('last_year', rows[-1][0])
    add('first_year_is_partial', rows[0][0] != con.execute(f'SELECT min(year(crash_date)) FROM {base}').fetchone()[0] or str(con.execute(f'SELECT min(crash_date) FROM {base}').fetchone()[0]) != f"{rows[0][0]}-01-01")
    add('last_year_is_partial', str(con.execute(f'SELECT max(crash_date) FROM {base}').fetchone()[0]) != f"{rows[-1][0]}-12-31")
for yr,total,eligible,tmiss,midnight,imiss,kmiss,sentinel in rows:
    add(f'year_{yr}_rows', total)
    add(f'year_{yr}_eligible_nonmissing_time_and_outcomes', eligible)
    add(f'year_{yr}_missing_crash_time', tmiss)
    add(f'year_{yr}_crash_time_midnight_default_candidate', midnight)
    add(f'year_{yr}_missing_number_of_persons_injured', imiss)
    add(f'year_{yr}_missing_number_of_persons_killed', kmiss)
    add(f'year_{yr}_crash_date_sentinel_candidates', sentinel)
add('date_sentinel_candidates_total', sum(r[7] for r in rows))
add('crash_time_midnight_default_candidate_total', sum(r[4] for r in rows))
for output in ('out/check_1.csv','out/check_2.csv'):
    with open(output, 'w', newline='') as f:
        writer=csv.writer(f); writer.writerow(['fact','value']); writer.writerows(allfacts)
print('Wrote plan-scoped checks:', len(allfacts), 'facts per file')
PY
# bash
python - <<'PY'
import duckdb, csv
from pathlib import Path
con=duckdb.connect()
p='data/crashes.parquet'
base=f"read_parquet('{p}')"
extra=[
 ('analysis_full_years','2013–2025'),
 ('full_year_rows_2013_2025',con.execute(f"SELECT count(*) FROM {base} WHERE year(crash_date) BETWEEN 2013 AND 2025").fetchone()[0]),
 ('full_year_rows_with_nonmissing_time_and_outcomes_2013_2025',con.execute(f"SELECT count(*) FROM {base} WHERE year(crash_date) BETWEEN 2013 AND 2025 AND crash_time IS NOT NULL AND number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL").fetchone()[0]),
 ('full_year_missing_crash_time_2013_2025',con.execute(f"SELECT count(*) FROM {base} WHERE year(crash_date) BETWEEN 2013 AND 2025 AND crash_time IS NULL").fetchone()[0]),
 ('full_year_midnight_time_candidates_2013_2025',con.execute(f"SELECT count(*) FROM {base} WHERE year(crash_date) BETWEEN 2013 AND 2025 AND crash_time = TIME '00:00:00'").fetchone()[0]),
 ('full_year_missing_number_of_persons_injured_2013_2025',con.execute(f"SELECT count(*) FROM {base} WHERE year(crash_date) BETWEEN 2013 AND 2025 AND number_of_persons_injured IS NULL").fetchone()[0]),
 ('full_year_missing_number_of_persons_killed_2013_2025',con.execute(f"SELECT count(*) FROM {base} WHERE year(crash_date) BETWEEN 2013 AND 2025 AND number_of_persons_killed IS NULL").fetchone()[0]),
 ('full_year_rows_missing_either_outcome_2013_2025',con.execute(f"SELECT count(*) FROM {base} WHERE year(crash_date) BETWEEN 2013 AND 2025 AND (number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL)").fetchone()[0]),
 ('nonmissing_crash_time_values_outside_clock_range',0),
]
for name in ('out/check_1.csv','out/check_2.csv'):
    with open(name,newline='') as f: existing=list(csv.reader(f))
    known={r[0] for r in existing[1:]}
    with open(name,'w',newline='') as f:
        w=csv.writer(f); w.writerows(existing)
        for fact,value in extra:
            if fact not in known: w.writerow([fact,value])
print('Added full-year and time-validity check facts to both check files.')
PY
# bash
python out/analyze.py
# bash
python - <<'PY'
import duckdb, csv
con=duckdb.connect(); p='data/crashes.parquet'; base=f"read_parquet('{p}')"
extra=[]
for yr in (2012,2026):
    lo,hi=con.execute(f"SELECT min(crash_date),max(crash_date) FROM {base} WHERE year(crash_date)={yr}").fetchone()
    extra.extend([(f'year_{yr}_first_crash_date',lo),(f'year_{yr}_last_crash_date',hi)])
for name in ('out/check_1.csv','out/check_2.csv'):
    with open(name,newline='') as f: existing=list(csv.reader(f))
    known={r[0] for r in existing[1:]}
    with open(name,'w',newline='') as f:
        w=csv.writer(f); w.writerows(existing)
        for fact,value in extra:
            if fact not in known: w.writerow([fact,value])
print(extra)
PY
# bash
python - <<'PY'
import duckdb,csv
con=duckdb.connect(); p='data/crashes.parquet'; base=f"read_parquet('{p}')"
value=con.execute(f"SELECT count(*) FROM {base} WHERE year(crash_date) BETWEEN 2013 AND 2025 AND crash_time=TIME '00:00:00' AND (number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL)").fetchone()[0]
for name in ('out/check_1.csv','out/check_2.csv'):
    with open(name,newline='') as f: existing=list(csv.reader(f))
    known={r[0] for r in existing[1:]}
    with open(name,'w',newline='') as f:
        w=csv.writer(f); w.writerows(existing)
        if 'full_year_midnight_rows_missing_either_outcome_2013_2025' not in known:
            w.writerow(['full_year_midnight_rows_missing_either_outcome_2013_2025',value])
print('full_year_midnight_rows_missing_either_outcome_2013_2025',value)
PY
# bash
python - <<'PY'
import csv, json
from pathlib import Path
out=Path('out')
for name in ('plan_1.json','plan_2.json','options.json'):
    json.loads((out/name).read_text())
options=json.loads((out/'options.json').read_text())['options']
assert len(options)==2
assert abs(sum(o['probability'] for o in options)-1)<1e-12
v1=list(csv.DictReader((out/'values_1.csv').open()))
v2=list(csv.DictReader((out/'values_2.csv').open()))
assert [r['time_group'] for r in v1]==['Day','Night','00:00 (possible default)']
assert sum(int(r['eligible_crashes']) for r in v1)==2132176
assert [r['eligible_crashes'] for r in v1]==[r['eligible_crashes'] for r in v2]
assert all((out/f'option_{i}.png').is_file() for i in (1,2))
print('JSON valid; probabilities sum to 1; 2,132,176 eligible crashes reconcile across options; both charts and value files present.')
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
- tr_TR11: Severity per crash (deaths or injuries per crash) is described as such, not as the risk of being on the street at night (no traffic volume by hour exists).
- tr_TR08: NA if the option uses no killed or injured counts. Otherwise the analysis window excludes 2026, or the 2026 rows with NULL killed counts (87.8% of May-2026, 100% of June-2026) are excluded or the resulting bias is disclosed; COALESCE to 0 alone is not handling (decided by Bo 2026-11-04).
- tr_NIGHTDEF: The definition of 'night' (hours) is stated.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.