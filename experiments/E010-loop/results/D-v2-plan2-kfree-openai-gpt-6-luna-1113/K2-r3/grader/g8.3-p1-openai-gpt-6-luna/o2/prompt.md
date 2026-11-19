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

QUESTION ASKED: How are NYC crashes distributed across the days of the week, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: mean number of police-reported crash records per calendar occurrence of each weekday
denominator: number of calendar dates of each weekday from 2013-01-01 through 2025-12-31 inclusive
grouping: weekday of crash_date in Monday-to-Sunday order
chart_type: bar chart
probability: 0.45
WRITTEN ANSWER:
On an average calendar date, Friday had the most recorded crashes (499.7) and Sunday the fewest (379.9) from 2013 through 2025. For the same NYC police-reported crash records dated 2013-01-01 through 2025-12-31, this divides each weekday's count by the calendar dates of that weekday in the inclusive period (678 or 679 dates) and groups Monday through Sunday; Friday averages 499.7 records per date and Sunday 379.9. This is a defensible comparison of average recorded crash volume per occurrence of a weekday and adjusts for unequal counts of weekday dates. It does not adjust for traffic exposure or year-specific changes, so it cannot show risk per trip/distance or how the weekday pattern changed over time. The scoped check found 2,132,218 selected records, 0 with missing or impossible dates and 0 at the checked sentinel dates, and full Jan 1–Dec 31 bounds in every year; all selected rows were kept, while missing/out-of-period dates cannot be assigned and were not counted in that scoped check.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
weekday,crashes,calendar_dates,avg_crashes_per_calendar_date
Monday,304518,678,449.141593
Tuesday,313488,679,461.690722
Wednesday,311111,679,458.189985
Thursday,318376,678,469.581121
Friday,338800,678,499.705015
Saturday,288381,678,425.340708
Sunday,257544,678,379.858407

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c 'import duckdb; con=duckdb.connect(); print(con.execute("SELECT COUNT(*) AS n, MIN(crash_date) AS min_date, MAX(crash_date) AS max_date FROM read_parquet('') WHERE crash_date >= DATE ''2013-01-01'' AND crash_date < DATE ''2026-01-01''".replace("\u0001", "data/crashes.parquet")).fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); q="SELECT COUNT(*), MIN(crash_date), MAX(crash_date) FROM read_parquet(?) WHERE crash_date >= make_date(2013,1,1) AND crash_date < make_date(2026,1,1)"; print(c.execute(q,["data/crashes.parquet"]).fetchall())'
# bash
python3 out/check_data.py
# bash
python3 out/analyze.py
# bash
python3 -c 'import json; from pathlib import Path; p=Path("out"); options=json.loads((p/"options.json").read_text()); assert len(options["options"]) == 2; assert abs(sum(o["probability"] for o in options["options"])-1) < 1e-9; assert all((p/f"option_{i}.png").is_file() and (p/f"values_{i}.csv").is_file() and (p/f"plan_{i}.json").is_file() and (p/f"check_{i}.csv").is_file() for i in (1,2)); print("JSON valid; probabilities sum to 1; all plan, check, chart, and values files exist.")'

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