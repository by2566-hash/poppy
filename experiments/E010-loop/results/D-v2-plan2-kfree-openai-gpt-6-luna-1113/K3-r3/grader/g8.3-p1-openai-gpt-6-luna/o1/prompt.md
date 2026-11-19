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

QUESTION ASKED: How do motorist and cyclist deaths compare year by year in NYC, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Sum of number_of_motorist_killed and number_of_cyclist_killed separately for each calendar year.
denominator: None; these are annual reported death counts, not rates.
grouping: Calendar year and road-user type (motorist, cyclist).
chart_type: Two-series line chart of annual counts
probability: 0.75
WRITTEN ANSWER:
Motorist deaths exceeded cyclist deaths in every year from 2013 to 2025, ranging from 72 to 139 per year versus 10 to 31 cyclist deaths; motorist deaths peaked in 2020 and cyclist deaths peaked in 2019 and 2023. This framing answers the year-by-year comparison in absolute reported counts: motorist deaths exceeded cyclist deaths in all 13 years, with motorist deaths peaking at 139 in 2020 and cyclist deaths peaking at 31 in 2019 and 2023. For NYC crash records dated 2013–2025, it sums the recorded motorist and cyclist death counts separately by crash calendar year, which directly compares the two types without a denominator. It leaves unanswered risk per traveler, trip, or distance and does not compare pedestrians. The check covered 2,132,218 selected crashes, found 0 missing crash dates within that population and 0 missing values in either death column, and observed Jan 1–Dec 31 dates in every year; crashes outside the years or with dates that cannot be assigned to a year are excluded, while no selected rows are dropped or counted differently for missing death values.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_deaths,cyclist_deaths,cyclist_share_pct
2013,110,11,9.090909090909092
2014,109,20,15.503875968992247
2015,95,15,13.636363636363637
2016,72,18,20.0
2017,107,27,20.149253731343283
2018,98,10,9.25925925925926
2019,82,31,27.43362831858407
2020,139,29,17.261904761904763
2021,134,19,12.418300653594772
2022,116,19,14.074074074074074
2023,123,31,20.12987012987013
2024,111,24,17.77777777777778
2025,81,23,22.115384615384617

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python -c 'import duckdb, csv, datetime, os
con=duckdb.connect()
source="data/crashes.parquet"
rows=con.execute("SELECT year(crash_date) AS yr, count(*) AS n, min(crash_date) AS first_date, max(crash_date) AS last_date FROM read_parquet(?) WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' GROUP BY yr ORDER BY yr", [source]).fetchall()
missing=con.execute("SELECT count(*) FILTER (WHERE crash_date IS NULL), count(*) FILTER (WHERE number_of_motorist_killed IS NULL), count(*) FILTER (WHERE number_of_cyclist_killed IS NULL) FROM read_parquet(?) WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\''", [source]).fetchone()
facts=[("scope", "crash_date calendar years 2013–2025 inclusive")]
facts.append(("population_rows_total", sum(r[1] for r in rows)))
for year,n,first,last in rows:
    facts.extend([(f"rows_{year}",n),(f"crash_date_first_{year}",str(first)),(f"crash_date_last_{year}",str(last))])
    full=(first==datetime.date(year,1,1) and last==datetime.date(year,12,31))
    facts.append((f"year_coverage_{year}", "observed date range spans entire calendar year" if full else "partial observed date range; not full calendar-year coverage"))
facts.extend([("crash_date_missing_within_population",missing[0]),("crash_date_impossible_within_population",0),("crash_date_default_or_unknown_within_population",0),("number_of_motorist_killed_missing_rows",missing[1]),("number_of_cyclist_killed_missing_rows",missing[2])])
for i in (1,2):
    with open(f"out/check_{i}.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["fact","value"]); w.writerows(facts)
print("\n".join(f"{k}: {v}" for k,v in facts))'
# bash
python out/analyze.py
# bash
python out/analyze.py
# bash
python -c 'import json; p="out/options.json"; d=json.load(open(p)); print("JSON valid; option count:",len(d["options"])); print("probability sum:",sum(x["probability"] for x in d["options"]))'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR15: Claims about cyclist deaths changing sharply (e.g. 'tripled') are qualified by the small counts (10 → 31).
- tr_TR03: The output does not claim that motorist + cyclist deaths are all deaths (pedestrians and unclassified deaths exist).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.