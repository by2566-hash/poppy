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
metric: Police-reported crashes per clock-hour
denominator: Clock-hours in each time band over all observed dates (14 daytime hours or 10 nighttime hours per date)
grouping: Day (6am–7:59pm) vs night (8pm–5:59am)
chart_type: Two-bar comparison of crashes per clock-hour
probability: 0.25
WRITTEN ANSWER:
The file cannot establish whether streets are more dangerous without travel exposure; it records 11.1 crashes per nighttime clock-hour versus 24.2 per daytime clock-hour. This answers how many reported collisions occur in each time band after accounting for its duration: the chart shows 11.1 per nighttime clock-hour versus 24.2 by day. It is a defensible volume comparison because it accounts for the 10 nighttime versus 14 daytime hours in each date. It leaves relative danger unanswered because it is not adjusted for traffic volume, and crash severity is not distinguished. It uses 2013 through 2025 (the 13 complete calendar years in the file); it excludes all 100,545 2012 rows (4.43% of the file; only July–December is present) and all 36,424 2026 rows (1.61%; only January 1–June 11 is present), together 6.04% and no rows for NULL crash time (none in the file); no outcome field is needed.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
period,crashes,observed_calendar_dates,clock_hours_in_period,period_clock_hours,crashes_per_clock_hour
Day (6am–7:59pm),1607499,4748,14,66472,24.183099650980864
Night (8pm–5:59am),524719,4748,10,47480,11.05136899747262

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb, os; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(f\"describe select * from read_parquet('{p}')\").fetchall()); print(c.execute(f\"select count(*), min(crash_date), max(crash_date) from read_parquet('{p}')\").fetchall()); print(os.path.isdir('out'))"
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"select extract(year from crash_date) y, count(*) n from read_parquet('{p}') group by 1 order by 1\").fetchall()); print(c.execute(f\"select count(*) n, count(*) filter(where crash_time is null) null_time, count(*) filter(where number_of_persons_injured is null) null_injured, count(*) filter(where number_of_persons_killed is null) null_killed, count(*) filter(where crash_time is not null and extract(hour from crash_time) >= 20 or crash_time is not null and extract(hour from crash_time) < 6) night from read_parquet('{p}')\").fetchall()); print(c.execute(f\"select extract(hour from crash_time) h,count(*) n, sum(number_of_persons_injured) injured, sum(number_of_persons_killed) killed, count(*) filter(where coalesce(number_of_persons_injured,0)>0 or coalesce(number_of_persons_killed,0)>0) harm_crashes from read_parquet('{p}') where crash_time is not null and extract(year from crash_date) between 2013 and 2025 group by 1 order by 1\").fetchall())"
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=\"\"\"with base as (select *, extract(year from crash_date) as yr, extract(hour from crash_time) as hr from read_parquet(?) ), chosen as (select *, case when hr >= 20 or hr < 6 then 'Night (8pm–5:59am)' else 'Day (6am–7:59pm)' end as period from base where yr between 2013 and 2025 and crash_time is not null) select period, count(*) crashes, count(*) filter(where number_of_persons_injured is not null and number_of_persons_killed is not null) known_harm, count(*) filter(where number_of_persons_injured is null or number_of_persons_killed is null) missing_harm, count(*) filter(where number_of_persons_injured > 0 or number_of_persons_killed > 0) harm_crashes, count(*) filter(where number_of_persons_killed is not null) known_death, count(*) filter(where number_of_persons_killed > 0) fatal_crashes, sum(number_of_persons_killed) killed_people, sum(number_of_persons_injured) injured_people, count(distinct crash_date) dates from chosen group by period order by period\"\"\"; print(c.execute(q,[p]).fetchall()); print(c.execute(\"select count(*), count(*) filter(where extract(year from crash_date) in (2012,2026)), count(*) filter(where extract(year from crash_date) between 2013 and 2025 and (number_of_persons_injured is null or number_of_persons_killed is null)) from read_parquet(?)\",[p]).fetchall()); print(c.execute(\"select count(*), count(*) filter(where number_of_persons_injured is null), count(*) filter(where number_of_persons_killed is null) from read_parquet(?) where extract(year from crash_date) between 2013 and 2025\",[p]).fetchall())"
# bash
python out/build_options.py
# bash
python out/build_options.py
# bash
python -c "import json, pathlib, pandas as pd; o=json.load(open('out/options.json')); print('probability_sum',sum(x['probability'] for x in o['options'])); print('answers'); [print(x['id'], x['answer']) for x in o['options']]; print('artifacts',[(str(p),p.stat().st_size) for i in range(1,4) for p in [pathlib.Path(f'out/option_{i}.png'),pathlib.Path(f'out/values_{i}.csv')]]); print('options_bytes',pathlib.Path('out/options.json').stat().st_size); print('csv_counts',[len(pd.read_csv(f'out/values_{i}.csv')) for i in range(1,4)])"

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