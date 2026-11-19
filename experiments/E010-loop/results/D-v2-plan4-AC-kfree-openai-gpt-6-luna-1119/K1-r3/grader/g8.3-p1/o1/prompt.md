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
metric: sum of number_of_pedestrians_killed by crash_date calendar year
denominator: not applicable; this is a count, not a rate or share
grouping: calendar year of crash_date
chart_type: Bar chart
probability: 1
WRITTEN ANSWER:
The recorded pedestrian deaths were 176 in 2013, 133 in 2014, 133 in 2015, 149 in 2016, 127 in 2017, 123 in 2018, 131 in 2019, 101 in 2020, 132 in 2021, 135 in 2022, 107 in 2023, 124 in 2024, and 119 in 2025. Summing number_of_pedestrians_killed across police-reported NYC motor vehicle crashes and grouping by the calendar year of crash_date answers the requested annual-count question; the chart gives the recorded total for each year from 2013 through 2025. This direct count is a defensible measure because it counts pedestrian fatalities recorded in the crashes, with no denominator or rate adjustment. It does not independently verify whether every actual pedestrian death appears in the police-reported crash file. The check covered 2,132,218 in-scope crash rows, found Jan 1 through Dec 31 date endpoints in every year and no NULL crash dates, and found zero missing pedestrian-killed values in every year; all in-scope rows were retained and none were excluded or counted differently for these checks.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrians_killed
2013,176.0
2014,133.0
2015,133.0
2016,149.0
2017,127.0
2018,123.0
2019,131.0
2020,101.0
2021,132.0
2022,135.0
2023,107.0
2024,124.0
2025,119.0

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
ls data
# bash
python -c 'import duckdb,csv; c=duckdb.connect(); p="data/crashes.parquet"; rows=c.execute("SELECT year(crash_date) AS y, count(*) AS n, count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS pedestrian_killed_missing, min(crash_date) AS first_date, max(crash_date) AS last_date FROM read_parquet(?) WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' GROUP BY y ORDER BY y",[p]).fetchall(); null_dates=c.execute("SELECT count(*) FROM read_parquet(?) WHERE crash_date IS NULL",[p]).fetchone()[0]; out=[("rows_in_planned_years",sum(r[1] for r in rows)),("missing_crash_date_rows_unassignable_to_year",null_dates)]; out += [(f"rows_{r[0]}",r[1]) for r in rows]; out += [(f"number_of_pedestrians_killed_missing_{r[0]}",r[2]) for r in rows]; out += [(f"date_coverage_{r[0]}",f"{r[3]} through {r[4]}") for r in rows]; out += [(f"partial_year_{r[0]}", "yes" if (r[3].month,r[3].day)!=(1,1) or (r[4].month,r[4].day)!=(12,31) else "no") for r in rows]; out += [("year_rows_missing_or_impossible_crash_date_within_planned_years",0)]; f=open("out/check_1.csv","w",newline=""); w=csv.writer(f); w.writerow(["fact","value"]); w.writerows(out); f.close(); print(out)'
# bash
python out/analyze_1.py
# bash
python -c 'import json,csv; from pathlib import Path; out=Path("out"); opts=json.loads((out/"options.json").read_text()); plan=json.loads((out/"plan_1.json").read_text()); rows=list(csv.DictReader((out/"values_1.csv").open())); checks={r["fact"]:r["value"] for r in csv.DictReader((out/"check_1.csv").open())}; assert len(opts["options"])==1 and len(rows)==13; assert [int(r["year"]) for r in rows]==list(range(2013,2026)); assert all(float(r["pedestrians_killed"]).is_integer() for r in rows); assert all(checks[f"number_of_pedestrians_killed_missing_{y}"]=="0" for y in range(2013,2026)); assert all(checks[f"partial_year_{y}"]=="no" for y in range(2013,2026)); assert plan["final_plan"]["metric"]==opts["options"][0]["metric"]; assert sum(o["probability"] for o in opts["options"])==1; assert (out/"option_1.png").is_file(); print("Validated JSON, year coverage, chart/data outputs, and plan/check consistency.")'
# bash
python -c 'import json,csv; from pathlib import Path; out=Path("out"); opts=json.loads((out/"options.json").read_text()); plan=json.loads((out/"plan_1.json").read_text()); rows=list(csv.DictReader((out/"values_1.csv").open())); checks={r["fact"]:r["value"] for r in csv.DictReader((out/"check_1.csv").open())}; option=opts["options"][0]; assert len(opts["options"])==1 and len(rows)==13; assert [int(r["year"]) for r in rows]==list(range(2013,2026)); assert all(float(r["pedestrians_killed"]).is_integer() for r in rows); assert all(checks[f"number_of_pedestrians_killed_missing_{y}"]=="0" for y in range(2013,2026)); assert all(checks[f"partial_year_{y}"]=="no" for y in range(2013,2026)); assert option["metric"]==plan["final_plan"]["metric"]; assert option["denominator"]==plan["final_plan"]["denominator"]; assert option["grouping"]==plan["final_plan"]["grouping"]; assert sum(o["probability"] for o in opts["options"])==1; assert (out/"option_1.png").is_file(); print("Validated JSON, year coverage, chart/data outputs, and plan/check consistency.")'

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