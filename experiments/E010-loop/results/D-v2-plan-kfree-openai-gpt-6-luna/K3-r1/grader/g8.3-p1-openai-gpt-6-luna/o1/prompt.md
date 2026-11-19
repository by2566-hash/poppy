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
metric: Annual number of reported people killed, separately for motorists and cyclists, calculated by summing the corresponding death-count columns across crashes
denominator: None; absolute annual death counts, not a rate
grouping: Calendar year and death group (motorist or cyclist)
chart_type: Line chart
probability: 0.7
WRITTEN ANSWER:
Motorist deaths exceeded cyclist deaths every year, with 72–139 annual motorist deaths versus 10–31 cyclist deaths; motorist deaths peaked at 139 in 2020, while cyclist deaths peaked at 31 in 2019 and 2023. This framing answers the year-by-year comparison in absolute numbers, and its lines show more motorist than cyclist deaths in every year from 2013 to 2025. Absolute counts are a defensible direct measure of the reported number of people killed in each group, although they are not rates adjusted for population or travel exposure. It does not show how each group compares as a share of deaths or account for pedestrian deaths. The check found 2,132,218 in-range crash rows with every year's observed dates spanning January 1 through December 31; the two death fields each had 0 NULLs and 0 negatives, while zero values appeared in 2,130,945 motorist rows and 2,131,942 cyclist rows, so all rows were kept and zeros counted as no-death records.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,death_group,deaths
2013,Motorist,110
2013,Cyclist,11
2014,Motorist,109
2014,Cyclist,20
2015,Motorist,95
2015,Cyclist,15
2016,Motorist,72
2016,Cyclist,18
2017,Motorist,107
2017,Cyclist,27
2018,Motorist,98
2018,Cyclist,10
2019,Motorist,82
2019,Cyclist,31
2020,Motorist,139
2020,Cyclist,29
2021,Motorist,134
2021,Cyclist,19
2022,Motorist,116
2022,Cyclist,19
2023,Motorist,123
2023,Cyclist,31
2024,Motorist,111
2024,Cyclist,24
2025,Motorist,81
2025,Cyclist,23

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c 'import duckdb,csv
from pathlib import Path
p=Path("data/crashes.parquet")
con=duckdb.connect()
years=range(2013,2026)
cols=["number_of_motorist_killed","number_of_cyclist_killed"]
for i in (1,2):
    rows=[]
    result=con.execute("SELECT YEAR(crash_date) AS yr, COUNT(*) AS n, MIN(crash_date), MAX(crash_date) FROM read_parquet(?) WHERE crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2026-01-01\' GROUP BY yr ORDER BY yr",[str(p)]).fetchall()
    by_year={r[0]:r for r in result}
    rows.append(("population_rows_total_2013_2025",sum(r[1] for r in result)))
    for y in years:
        r=by_year.get(y)
        rows.append((f"population_rows_{y}",r[1] if r else 0))
        if r:
            rows.append((f"crash_date_coverage_{y}",f"observed {r[2]} through {r[3]}; {'partial' if str(r[2])[:4]!=str(y) or str(r[3])[:4]!=str(y) or str(r[2])[5:]!='01-01' or str(r[3])[5:]!='12-31' else 'full endpoint coverage'}"))
        else:
            rows.append((f"crash_date_coverage_{y}","no rows"))
    for col in cols:
        q=f"SELECT COUNT(*) FILTER (WHERE {col} IS NULL), COUNT(*) FILTER (WHERE {col} < 0), COUNT(*) FILTER (WHERE {col}=0) FROM read_parquet(?) WHERE crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2026-01-01\'"
        nulls,impossible,zeros=con.execute(q,[str(p)]).fetchone()
        rows.extend([(f"{col}_missing_null_rows",nulls),(f"{col}_impossible_negative_rows",impossible),(f"{col}_zero_value_rows",zeros)])
        for y in years:
            q=f"SELECT COUNT(*) FILTER (WHERE {col} IS NULL), COUNT(*) FILTER (WHERE {col} < 0), COUNT(*) FILTER (WHERE {col}=0) FROM read_parquet(?) WHERE YEAR(crash_date)=?"
            a,b,c=con.execute(q,[str(p),y]).fetchone()
            rows.extend([(f"{col}_missing_null_rows_{y}",a),(f"{col}_impossible_negative_rows_{y}",b),(f"{col}_zero_value_rows_{y}",c)])
    with open(f"out/check_{i}.csv","w",newline="") as f:
        w=csv.writer(f);w.writerow(["fact","value"]);w.writerows(rows)
    print(f"check_{i}: wrote {len(rows)} facts")
'
# bash
python3 out/check_data.py
# bash
python3 out/analyze.py
# bash
python3 -m json.tool out/plan_2.json
# bash
python3 -m json.tool out/options.json
# bash
python3 -m json.tool out/plan_1.json

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