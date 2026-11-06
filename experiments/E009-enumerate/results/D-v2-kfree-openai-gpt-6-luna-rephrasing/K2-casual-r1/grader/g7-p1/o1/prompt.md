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

QUESTION ASKED: From 2013 to 2025, how were NYC crashes spread across the days of the week?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Total police-reported crash count
denominator: None; absolute count of crash records
grouping: Day of week
chart_type: Vertical bar chart
probability: 0.55
WRITTEN ANSWER:
From 2013 through 2025, Friday had the most crashes (338,800; 15.9% of the total) and Sunday the fewest (257,544; 12.1%). This framing answers how the total number of crashes was distributed across weekdays, with Fridays the largest share and Sundays the smallest. Counts and each weekday's share of all crash records are a defensible summary of the overall distribution. It does not show whether the number of dates for each weekday differs or whether crash risk per trip differs.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,weekday_num,crash_count,calendar_days,share_of_crashes_pct
Monday,1,304518,678,14.281748
Tuesday,2,313488,679,14.702437
Wednesday,3,311111,679,14.590956
Thursday,4,318376,678,14.931681
Friday,5,338800,678,15.889557
Saturday,6,288381,678,13.524930
Sunday,7,257544,678,12.078690

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
ls out
# bash
python -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(\"select count(*) rows, min(crash_date), max(crash_date), count(*) filter (where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01') in_range from read_parquet(?)\", [p]).fetchall()); print(c.execute(\"select count(*) filter (where crash_date is null) null_dates from read_parquet(?)\", [p]).fetchall())"
# bash
python -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(\"select count(*) as n_rows, min(crash_date), max(crash_date), count(*) filter (where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01') as in_range from read_parquet(?)\", [p]).fetchall()); print(c.execute(\"select count(*) filter (where crash_date is null) as null_dates from read_parquet(?)\", [p]).fetchall())"
# bash
python out/generate_weekdays.py
# bash
ls out
# bash
python -c "import json, pathlib; p=pathlib.Path('out/options.json'); data=json.loads(p.read_text()); print('valid JSON; options:', len(data['options']), '; probability sum:', sum(o['probability'] for o in data['options']))"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_DAYCOUNT: If per-day averages or 'X% fewer on <day>' comparisons are given, the arithmetic is right (e.g. Sunday has 24% fewer than the mean weekday, Friday 32% more) and unequal day counts (678/679) are handled or noted.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.