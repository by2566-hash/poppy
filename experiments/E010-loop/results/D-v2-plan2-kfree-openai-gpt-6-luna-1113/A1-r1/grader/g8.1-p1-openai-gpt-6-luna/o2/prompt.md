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

QUESTION ASKED: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Sum of reported pedestrians killed per calendar year, 2013–2025, in Brooklyn-labeled police-reported motor vehicle crashes
denominator: None; annual count, not a rate
grouping: Calendar year of crash_date
chart_type: Annual line chart
probability: 0.35
WRITTEN ANSWER:
Reported pedestrian deaths were 30 in 2013 and 39 in 2025, an increase of 9, with substantial year-to-year fluctuation. This framing answers whether the annual fatal pedestrian burden changed: it sums number_of_pedestrians_killed among police-reported crashes whose borough matches Brooklyn after trimming and case normalization, grouped by calendar year from 2013 through 2025. Deaths increased from 30 in 2013 to 39 in 2025, although the series fluctuates substantially (including 17 in 2020); this is a defensible severity-focused count, with no denominator and therefore no exposure-adjusted rate. It cannot establish whether fatality risk per pedestrian trip improved or describe nonfatal injuries and other dimensions of road safety. The check found zero missing fatality fields in the 2013–2025 Brooklyn rows, so none were dropped for that reason; the plan excludes 9,700 Brooklyn crashes in partial 2026 and cannot assign 668,406 2013-onward crashes with NULL borough to Brooklyn, and year-boundary dates do not prove uninterrupted reporting.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,pedestrians_killed
2013,30
2014,42
2015,46
2016,20
2017,20
2018,23
2019,33
2020,17
2021,32
2022,23
2023,22
2024,31
2025,39

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c 'import duckdb, csv, json; from pathlib import Path; con=duckdb.connect(); source="read_parquet(\"data/crashes.parquet\")"; specs={1:["number_of_pedestrians_injured"],2:["number_of_pedestrians_killed"],3:["number_of_pedestrians_injured","number_of_pedestrians_killed"]}; out=Path("out");
for oid, cols in specs.items():
 facts=[]
 def add(f,v): facts.append((f,str(v)))
 years=con.execute(f"SELECT year(crash_date)::INT AS yr, count(*)::BIGINT AS n, min(crash_date)::VARCHAR AS first_date, max(crash_date)::VARCHAR AS last_date FROM {source} WHERE borough = ? AND crash_date >= DATE '2013-01-01' GROUP BY yr ORDER BY yr",["Brooklyn"]).fetchall()
 total=sum(r[1] for r in years); add("Brooklyn crash rows with crash_date in calendar years 2013 onward (plan population before outcome-field exclusions)",total)
 for y,n,first,last in years:
  add(f"Brooklyn crash rows in {y}",n); add(f"Observed crash_date range in Brooklyn for {y}",f"{first} through {last}"); add(f"Calendar-year coverage note for {y}","observed dates do not span the full calendar year" if first!=f"{y}-01-01" or last!=f"{y}-12-31" else "observed dates reach both calendar-year boundaries; continuous coverage not established")
 add("Rows with borough missing among selected Brooklyn population",0)
 for col in cols:
  q=f"SELECT count(*) FILTER (WHERE {col} IS NULL)::BIGINT FROM {source} WHERE borough = ? AND crash_date >= DATE '2013-01-01'"
  miss=con.execute(q,["Brooklyn"]).fetchone()[0]; add(f"Rows with {col} missing among Brooklyn crash rows in 2013 onward",miss)
 with (out/f"check_{oid}.csv").open("w",newline="") as f:
  w=csv.writer(f); w.writerow(["fact","value"]); w.writerows(facts)
 print(f"check_{oid}: {len(facts)} facts; population rows={total}; year range={years[0][0] if years else None}-{years[-1][0] if years else None}")'
# bash
python3 -c 'import duckdb, csv; from pathlib import Path; con=duckdb.connect(); source="read_parquet(\"data/crashes.parquet\")"; specs={1:["number_of_pedestrians_injured"],2:["number_of_pedestrians_killed"],3:["number_of_pedestrians_injured","number_of_pedestrians_killed"]}; out=Path("out");
for oid, cols in specs.items():
 facts=[]
 def add(f,v): facts.append((f,str(v)))
 years=con.execute(f"SELECT year(crash_date)::INT AS yr, count(*)::BIGINT AS n, min(crash_date)::VARCHAR AS first_date, max(crash_date)::VARCHAR AS last_date FROM {source} WHERE borough = ? AND crash_date >= CAST(? AS DATE) GROUP BY yr ORDER BY yr",["Brooklyn","2013-01-01"]).fetchall()
 total=sum(r[1] for r in years); add("Brooklyn crash rows with crash_date in calendar years 2013 onward (plan population before outcome-field exclusions)",total)
 for y,n,first,last in years:
  add(f"Brooklyn crash rows in {y}",n); add(f"Observed crash_date range in Brooklyn for {y}",f"{first} through {last}"); add(f"Calendar-year coverage note for {y}","observed dates do not span the full calendar year" if first!=f"{y}-01-01" or last!=f"{y}-12-31" else "observed dates reach both calendar-year boundaries; continuous coverage not established")
 add("Rows with borough missing among selected Brooklyn population",0)
 for col in cols:
  q=f"SELECT count(*) FILTER (WHERE {col} IS NULL)::BIGINT FROM {source} WHERE borough = ? AND crash_date >= CAST(? AS DATE)"
  miss=con.execute(q,["Brooklyn","2013-01-01"]).fetchone()[0]; add(f"Rows with {col} missing among Brooklyn crash rows in 2013 onward",miss)
 with (out/f"check_{oid}.csv").open("w",newline="") as f:
  w=csv.writer(f); w.writerow(["fact","value"]); w.writerows(facts)
 print(f"check_{oid}: {len(facts)} facts; population rows={total}; year range={years[0][0] if years else None}-{years[-1][0] if years else None}")'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="read_parquet(\"data/crashes.parquet\")"; print(c.execute(f"SELECT typeof(crash_date), min(crash_date), max(crash_date), count(*) FROM {p}").fetchall()); print(c.execute(f"SELECT borough, count(*) FROM {p} WHERE crash_date >= CAST(? AS DATE) GROUP BY borough ORDER BY borough",["2013-01-01"]).fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="read_parquet(\"data/crashes.parquet\")"; print(c.execute(f"SELECT typeof(crash_date), min(crash_date), max(crash_date), count(*) FROM {p} GROUP BY typeof(crash_date)").fetchall()); print(c.execute(f"SELECT borough, count(*) FROM {p} WHERE crash_date >= CAST(? AS DATE) GROUP BY borough ORDER BY borough",["2013-01-01"]).fetchall())'
# bash
python3 -c 'import duckdb, csv; from pathlib import Path; c=duckdb.connect(); p="read_parquet(\"data/crashes.parquet\")"; specs={1:["number_of_pedestrians_injured"],2:["number_of_pedestrians_killed"],3:["number_of_pedestrians_injured","number_of_pedestrians_killed"]}; out=Path("out");
for oid, cols in specs.items():
 facts=[]
 def add(f,v): facts.append((f,str(v)))
 years=c.execute(f"SELECT year(crash_date)::INT AS yr, count(*)::BIGINT AS n, min(crash_date)::VARCHAR AS first_date, max(crash_date)::VARCHAR AS last_date FROM {p} WHERE upper(trim(borough)) = ? AND crash_date >= CAST(? AS DATE) GROUP BY yr ORDER BY yr",["BROOKLYN","2013-01-01"]).fetchall()
 full=[r for r in years if r[2]==f"{r[0]}-01-01" and r[3]==f"{r[0]}-12-31"]
 add("Brooklyn crash rows with crash_date in 2013 onward (before outcome-field exclusions)",sum(r[1] for r in years))
 add("Brooklyn crash rows in complete observed calendar years 2013 onward",sum(r[1] for r in full))
 add("Year selection based on observed date range","2013 onward screened; years with observed dates not reaching both Jan 1 and Dec 31 flagged as partial and to be excluded")
 for y,n,first,last in years:
  add(f"Brooklyn crash rows in {y}",n); add(f"Observed crash_date range in Brooklyn for {y}",f"{first} through {last}"); add(f"Calendar-year coverage note for {y}","observed dates do not span the full calendar year" if first!=f"{y}-01-01" or last!=f"{y}-12-31" else "observed dates reach both calendar-year boundaries; continuous coverage not established")
 cohort=c.execute(f"SELECT count(*) FILTER (WHERE borough IS NULL)::BIGINT, count(*) FILTER (WHERE borough IS NOT NULL AND trim(borough) = \'\')::BIGINT, count(*) FILTER (WHERE upper(trim(borough)) IN (\'UNKNOWN\',\'UNSPECIFIED\',\'N/A\',\'NULL\'))::BIGINT FROM {p} WHERE crash_date >= CAST(? AS DATE)",["2013-01-01"]).fetchone()
 add("2013-onward crash rows with borough NULL (not assignable to Brooklyn)",cohort[0]); add("2013-onward crash rows with borough blank",cohort[1]); add("2013-onward crash rows with borough labeled as unknown/unspecified",cohort[2]); add("Rows with borough missing within normalized Brooklyn population",0)
 for col in cols:
  q=f"SELECT year(crash_date)::INT, count(*) FILTER (WHERE {col} IS NULL)::BIGINT FROM {p} WHERE upper(trim(borough)) = ? AND crash_date >= CAST(? AS DATE) GROUP BY 1 ORDER BY 1"
  misses=c.execute(q,["BROOKLYN","2013-01-01"]).fetchall()
  add(f"Total rows with {col} missing among Brooklyn crashes in complete observed 2013-onward years",sum(n for y,n in misses if any(z[0]==y for z in full)))
  for y,n in misses: add(f"Rows with {col} missing in Brooklyn crashes in {y}",n)
 with (out/f"check_{oid}.csv").open("w",newline="") as f:
  w=csv.writer(f); w.writerow(["fact","value"]); w.writerows(facts)
 print(f"check_{oid}: Brooklyn rows={sum(r[1] for r in years)}, observed years={years[0][0]}-{years[-1][0]}, complete-observed rows={sum(r[1] for r in full)}; last dates={years[-1][2]}..{years[-1][3]}")'
# bash
python3 out/check_data.py
# bash
python3 out/analyze.py
# bash
python3 out/check_data.py
# bash
python3 out/analyze.py
# bash
python3 -c 'import json; from pathlib import Path; root=Path("out"); opts=json.loads((root/"options.json").read_text()); assert abs(sum(o["probability"] for o in opts["options"])-1)<1e-9; assert len(opts["options"])==3; [json.loads((root/f"plan_{i}.json").read_text()) for i in range(1,4)]; [assertion for assertion in []]; print("JSON valid; probabilities sum to",sum(o["probability"] for o in opts["options"])); print("Outputs:", ", ".join(sorted(p.name for p in root.glob("option_*.png"))))'
# bash
python3 out/check_data.py

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR05: If a borough filter (borough = 'BROOKLYN') is used, the output discloses that crashes with no borough recorded (19.9–38.1% per year) are excluded.
- tr_TR11: The output does not call Brooklyn 'safer' or 'less safe' from counts alone without saying that there is no pedestrian exposure measure.
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.