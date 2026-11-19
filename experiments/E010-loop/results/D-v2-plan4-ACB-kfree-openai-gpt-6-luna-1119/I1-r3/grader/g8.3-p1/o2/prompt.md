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
metric: Annual count of crash rows where number_of_motorist_killed is greater than zero; each qualifying crash row counts once
denominator: None; annual count of qualifying crash rows
grouping: Calendar year of crash_date, complete years 2013–2025 inclusive
chart_type: Line chart
probability: 0.42
WRITTEN ANSWER:
This crash file cannot determine whether per-mile motorist-death risk declined; crashes with at least one recorded motorist death numbered 102 in 2013, peaked at 126 in both 2020 and 2021, and numbered 75 in 2025. The crash file cannot answer whether risk per mile declined, but the chart shows annual counts of crash rows involving a motorist death. For police-reported NYC crashes with a known nonnegative motorist-death count in complete calendar years 2013–2025, it counts a row once when number_of_motorist_killed is greater than zero, regardless of how many motorists died in that crash; the count was 102 in 2013, 126 in both 2020 and 2021, and 75 in 2025. This is a defensible measure of fatal crash-event frequency, but it leaves per-mile risk unanswered because miles driven are not recorded. Checks found 2,132,218 rows in the planned years, 0 missing crash dates, and 0 missing or negative motorist-death values, so no rows were excluded for missing or invalid values; zero-death crashes do not qualify by definition, all planned years are full calendar years, and partial 2026 coverage is outside the selected period.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,crashes_with_motorist_death
2013,102
2014,99
2015,89
2016,63
2017,100
2018,97
2019,77
2020,126
2021,126
2022,107
2023,114
2024,98
2025,75

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c 'import duckdb, pandas, matplotlib; print("duckdb", duckdb.__version__, "pandas", pandas.__version__, "matplotlib", matplotlib.__version__)'
# bash
python3 -c 'import duckdb,csv,json,datetime; con=duckdb.connect(); p="data/crashes.parquet"; years=range(2013,2026); rows=con.execute("SELECT crash_date, number_of_motorist_killed FROM read_parquet(?)",[p]).fetchall(); yearly={y:{"rows":0,"min":None,"max":None,"missing_killed":0,"negative_killed":0} for y in years}; null_dates=0; all_dates=[]
for d,k in rows:
    if d is None:
        null_dates+=1
    else:
        all_dates.append(d)
        y=d.year
        if y in yearly:
            x=yearly[y]; x["rows"]+=1; x["min"]=d if x["min"] is None or d<x["min"] else x["min"]; x["max"]=d if x["max"] is None or d>x["max"] else x["max"]
            if k is None: x["missing_killed"]+=1
            elif k<0: x["negative_killed"]+=1
first=min(all_dates) if all_dates else None; last=max(all_dates) if all_dates else None
for i in (1,2):
    facts=[("planned_year_range","2013-01-01 through 2025-12-31 inclusive"),("rows_in_planned_years",sum(x["rows"] for x in yearly.values())),("rows_with_missing_crash_date_all_file_rows",null_dates),("file_earliest_nonmissing_crash_date",str(first)),("file_latest_nonmissing_crash_date",str(last))]
    for y,x in yearly.items():
        facts.extend([(f"rows_{y}",x["rows"]),(f"first_observed_date_{y}",str(x["min"])),(f"last_observed_date_{y}",str(x["max"]))])
    facts.append(("motorist_killed_missing_rows_in_planned_years",sum(x["missing_killed"] for x in yearly.values())))
    facts.append(("motorist_killed_negative_rows_in_planned_years",sum(x["negative_killed"] for x in yearly.values())))
    with open(f"out/check_{i}.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["fact","value"]); w.writerows(facts)
print(json.dumps({"null_crash_date":null_dates,"file_date_min":str(first),"file_date_max":str(last),"by_year":{y:{k:(str(v) if isinstance(v,datetime.date) else v) for k,v in x.items()} for y,x in yearly.items()}},indent=2))'
# bash
python3 out/analyze.py
# bash
python3 out/analyze.py
# bash
python3 out/analyze.py && python3 -c 'import json; [json.load(open(p)) for p in ["out/plan_1.json","out/plan_2.json","out/options.json"]]; print("JSON valid")'

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