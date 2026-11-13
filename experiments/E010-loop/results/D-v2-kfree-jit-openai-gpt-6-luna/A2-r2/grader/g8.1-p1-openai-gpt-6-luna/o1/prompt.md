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
metric: Reported crashes per calendar-day clock-hour
denominator: crashes / calendar-day clock-hour
grouping: Night (8pm–5:59am) versus day (6am–7:59pm), over all crash dates in the file
chart_type: bar chart
probability: 0.25
WRITTEN ANSWER:
The file records 11.0 reported crashes per night clock-hour per calendar day versus 24.0 per daytime clock-hour, so recorded crash volume is lower at night. This chart answers whether more police-reported crashes occur during nighttime hours after accounting for the unequal lengths of the day and night periods. It shows lower nighttime crash frequency per clock-hour, a defensible measure of recorded crash burden; it leaves unanswered the risk per trip or per vehicle because traffic exposure is not in the file.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
period,crashes,calendar_days,clock_hours_per_day,denominator_clock_hours,value
Day,1710183,5094,14,71316,23.980355039542317
Night,559004,5094,10,50940,10.973773066352571

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"select count(*) n, min(crash_date) min_date, max(crash_date) max_date, count(*) filter(where crash_time is null) null_time from read_parquet('{p}')\").fetchdf().to_string(index=False)); print(c.execute(f\"select strftime(crash_time, '%H') hr, count(*) n, sum(number_of_persons_injured) injured, sum(number_of_persons_killed) killed from read_parquet('{p}') group by hr order by hr\").fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=f\"with x as (select *, extract(hour from crash_time) h from read_parquet('{p}')), g as (select case when h>=20 or h<6 then 'Night (8pm–5:59am)' else 'Day (6am–7:59pm)' end period, count(*) crashes, sum(coalesce(number_of_persons_injured,0)) injured, sum(coalesce(number_of_persons_killed,0)) killed, count(*) filter(where coalesce(number_of_persons_injured,0)>0 or coalesce(number_of_persons_killed,0)>0) harm_crashes, count(*) filter(where coalesce(number_of_persons_killed,0)>0) fatal_crashes, count(distinct h) hours from x group by period) select *, crashes::double/hours crashes_per_clock_hour, injured::double/crashes injured_per_crash, killed::double/crashes killed_per_crash, harm_crashes::double/crashes pct_harm_crashes, fatal_crashes::double/crashes pct_fatal_crashes from g order by period\"; print(c.execute(q).fetchdf().to_string(index=False)); print(c.execute(f\"select count(distinct crash_date) dates, min(crash_date), max(crash_date), count(*) filter(where number_of_persons_killed is null) null_killed from read_parquet('{p}')\").fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=f\"with x as (select *, extract(hour from crash_time) h from read_parquet('{p}')), g as (select case when h>=20 or h<6 then 'Night (8pm–5:59am)' else 'Day (6am–7:59pm)' end period, count(*) crashes, sum(coalesce(number_of_persons_injured,0)) injured, sum(coalesce(number_of_persons_killed,0)) killed, count(*) filter(where coalesce(number_of_persons_injured,0)>0 or coalesce(number_of_persons_killed,0)>0) harm_crashes, count(*) filter(where coalesce(number_of_persons_killed,0)>0) fatal_crashes, count(distinct h) as n_hours from x group by period) select *, crashes::double/n_hours crashes_per_clock_hour, injured::double/crashes injured_per_crash, killed::double/crashes killed_per_crash, harm_crashes::double/crashes pct_harm_crashes, fatal_crashes::double/crashes pct_fatal_crashes from g order by period\"; print(c.execute(q).fetchdf().to_string(index=False)); print(c.execute(f\"select count(distinct crash_date) dates, min(crash_date), max(crash_date), count(*) filter(where number_of_persons_killed is null) null_killed from read_parquet('{p}')\").fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"select date_diff('day', min(crash_date), max(crash_date))+1 span_days, count(distinct crash_date) observed_days, sum(number_of_persons_injured) injuries from read_parquet('{p}')\").fetchdf().to_string(index=False)); print(c.execute(f\"select case when extract(hour from crash_time)>=20 or extract(hour from crash_time)<6 then 'Night' else 'Day' end period, count(*) crashes, count(*) filter(where number_of_persons_injured>0) injury_crashes, sum(number_of_persons_injured) injuries, count(*) filter(where number_of_persons_killed is not null) known_death_crashes, count(*) filter(where number_of_persons_killed>0) fatal_crashes, sum(number_of_persons_killed) deaths from read_parquet('{p}') group by period order by period\").fetchdf().to_string(index=False))"
# bash
ls
# bash
python3 generate_analysis.py
# bash
python3 generate_analysis.py
# bash
python3 -c "import json, pathlib; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); print('options=',len(o['options']),'probability_sum=',sum(x['probability'] for x in o['options'])); print('outputs=',sorted(x.name for x in p.iterdir()))"

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