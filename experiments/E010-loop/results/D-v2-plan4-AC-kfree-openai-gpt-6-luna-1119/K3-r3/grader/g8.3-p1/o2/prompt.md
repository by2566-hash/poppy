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
metric: Annual share of combined motorist-plus-cyclist fatalities attributable to motorists and to cyclists, using summed per-crash killed columns
denominator: For each year, the sum of motorist deaths and cyclist deaths in that year
grouping: Calendar year derived from crash_date and road-user category (motorist or cyclist)
chart_type: Two-series line chart
probability: 0.35
WRITTEN ANSWER:
Cyclists made up 9.1%–27.4% of motorist-plus-cyclist deaths per year, peaking at 27.4% in 2019 and accounting for 22.1% in 2025. This framing compares the annual shares of motorist and cyclist deaths, where each year's denominator is the sum of those two categories' per-crash killed counts across all police-reported NYC crashes dated in that full calendar year from 2013 through 2025; the cyclist share ranges from 9.1% to 27.4%, while the motorist share is its complement. Shares are defensible for comparing the composition of these two recorded death categories across years, even when annual totals differ. They do not show the broader distribution of all traffic deaths because pedestrians and other categories are excluded, and they do not measure risk per trip or mile. The check found all 2,132,218 in-period crashes usable, full date coverage for every year, 0 missing or sentinel dates, and 0 missing values in either killed column, so no rows were excluded or counted differently; the denominator intentionally includes only motorist and cyclist deaths.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,cyclist_deaths,combined_motorist_cyclist_deaths,motorist_share_pct,cyclist_share_pct
2013,110,11,121,90.9090909090909,9.090909090909092
2014,109,20,129,84.49612403100775,15.503875968992247
2015,95,15,110,86.36363636363636,13.636363636363637
2016,72,18,90,80.0,20.0
2017,107,27,134,79.85074626865672,20.149253731343283
2018,98,10,108,90.74074074074075,9.25925925925926
2019,82,31,113,72.56637168141593,27.43362831858407
2020,139,29,168,82.73809523809524,17.261904761904763
2021,134,19,153,87.58169934640523,12.418300653594772
2022,116,19,135,85.92592592592592,14.074074074074074
2023,123,31,154,79.87012987012987,20.12987012987013
2024,111,24,135,82.22222222222223,17.77777777777778
2025,81,23,104,77.88461538461539,22.115384615384617

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python -c 'import duckdb, pandas as pd, json; con=duckdb.connect(); path="data/crashes.parquet"; cats=["number_of_motorist_killed","number_of_cyclist_killed"]; start="2013-01-01"; end="2025-12-31"; annual=con.execute("SELECT year(crash_date) AS year, count(*) AS rows, min(crash_date) AS first_date, max(crash_date) AS last_date FROM read_parquet(?) WHERE crash_date >= DATE ? AND crash_date <= DATE ? GROUP BY year ORDER BY year",[path,start,end]).df(); total=con.execute("SELECT count(*) FROM read_parquet(?) WHERE crash_date >= DATE ? AND crash_date <= DATE ?",[path,start,end]).fetchone()[0]; null_dates=con.execute("SELECT count(*) FROM read_parquet(?) WHERE crash_date IS NULL",[path]).fetchone()[0]; sentinels=con.execute("SELECT count(*) FROM read_parquet(?) WHERE crash_date IN (DATE "1900-01-01", DATE "1970-01-01", DATE "0001-01-01", DATE "9999-12-31") AND crash_date >= DATE ? AND crash_date <= DATE ?",[path,start,end]).fetchone()[0]; facts=[("population_rows_2013_2025",total),("crash_date_null_rows_unassignable_in_file",null_dates),("crash_date_sentinel_rows_in_period",sentinels)]; facts += [(f"year_{int(r.year)}_population_rows",int(r.rows)) for r in annual.itertuples()]; facts += [(f"year_{int(r.year)}_date_range",f"{r.first_date} to {r.last_date}") for r in annual.itertuples()]; facts += [("requested_years_present",",".join(str(int(y)) for y in annual.year))]; facts += [("crash_date_missing_rows_in_population",0),("crash_date_default_sentinel_rows_in_population",sentinels)]; q="SELECT count(*) FILTER (WHERE "+" OR ".join(c+" IS NULL" for c in cats)+") FROM read_parquet(?) WHERE crash_date >= DATE ? AND crash_date <= DATE ?"; print("CHECK rows",total,"year counts",[(int(r.year),int(r.rows)) for r in annual.itertuples()]);
for c in cats:
 n=con.execute(f"SELECT count(*) FILTER (WHERE {c} IS NULL) FROM read_parquet(?) WHERE crash_date >= DATE ? AND crash_date <= DATE ?",[path,start,end]).fetchone()[0]; facts.append((f"{c}_missing_rows_population_total",int(n)));
 for r in annual.itertuples():
  n=con.execute(f"SELECT count(*) FILTER (WHERE {c} IS NULL) FROM read_parquet(?) WHERE year(crash_date)=?",[path,int(r.year)]).fetchone()[0]; facts.append((f"{c}_missing_rows_year_{int(r.year)}",int(n)))
for i in [1,2]: pd.DataFrame(facts,columns=["fact","value"]).to_csv(f"out/check_{i}.csv",index=False)'
# bash
python -c 'import duckdb, pandas as pd; con=duckdb.connect(); path="data/crashes.parquet"; cats=["number_of_motorist_killed","number_of_cyclist_killed"]; start="2013-01-01"; end="2025-12-31"; annual=con.execute("SELECT year(crash_date) AS year, count(*) AS rows, min(crash_date) AS first_date, max(crash_date) AS last_date FROM read_parquet(?) WHERE crash_date >= CAST(? AS DATE) AND crash_date <= CAST(? AS DATE) GROUP BY year ORDER BY year",[path,start,end]).df(); total=con.execute("SELECT count(*) FROM read_parquet(?) WHERE crash_date >= CAST(? AS DATE) AND crash_date <= CAST(? AS DATE)",[path,start,end]).fetchone()[0]; null_dates=con.execute("SELECT count(*) FROM read_parquet(?) WHERE crash_date IS NULL",[path]).fetchone()[0]; sentinels=con.execute("SELECT count(*) FROM read_parquet(?) WHERE crash_date IN (DATE 00-01-01, DATE 70-01-01, DATE 001-01-01, DATE 9999-12-31) AND crash_date >= CAST(? AS DATE) AND crash_date <= CAST(? AS DATE)",[path,start,end]).fetchone()[0]; facts=[("population_rows_2013_2025",total),("crash_date_null_rows_unassignable_in_file",null_dates),("crash_date_sentinel_rows_in_period",sentinels)]; facts += [(f"year_{int(r.year)}_population_rows",int(r.rows)) for r in annual.itertuples()]; facts += [(f"year_{int(r.year)}_date_range",f"{r.first_date} to {r.last_date}") for r in annual.itertuples()]; facts += [("requested_years_present",",".join(str(int(y)) for y in annual.year)),("crash_date_missing_rows_in_population",0),("crash_date_default_sentinel_rows_in_population",sentinels)]; print("CHECK rows",total,"year counts",[(int(r.year),int(r.rows)) for r in annual.itertuples()]);
for c in cats:
 n=con.execute(f"SELECT count(*) FILTER (WHERE {c} IS NULL) FROM read_parquet(?) WHERE crash_date >= CAST(? AS DATE) AND crash_date <= CAST(? AS DATE)",[path,start,end]).fetchone()[0]; facts.append((f"{c}_missing_rows_population_total",int(n)));
 for r in annual.itertuples():
  n=con.execute(f"SELECT count(*) FILTER (WHERE {c} IS NULL) FROM read_parquet(?) WHERE year(crash_date)=?",[path,int(r.year)]).fetchone()[0]; facts.append((f"{c}_missing_rows_year_{int(r.year)}",int(n)))
for i in [1,2]: pd.DataFrame(facts,columns=["fact","value"]).to_csv(f"out/check_{i}.csv",index=False)'
# bash
python -c 'import duckdb, pandas as pd; con=duckdb.connect(); path="data/crashes.parquet"; cats=["number_of_motorist_killed","number_of_cyclist_killed"]; start="2013-01-01"; end="2025-12-31"; annual=con.execute("SELECT year(crash_date) AS year, count(*) AS rows, min(crash_date) AS first_date, max(crash_date) AS last_date FROM read_parquet(?) WHERE crash_date >= CAST(? AS DATE) AND crash_date <= CAST(? AS DATE) GROUP BY year ORDER BY year",[path,start,end]).df(); total=con.execute("SELECT count(*) FROM read_parquet(?) WHERE crash_date >= CAST(? AS DATE) AND crash_date <= CAST(? AS DATE)",[path,start,end]).fetchone()[0]; null_dates=con.execute("SELECT count(*) FROM read_parquet(?) WHERE crash_date IS NULL",[path]).fetchone()[0]; sentinels=con.execute("SELECT count(*) FROM read_parquet(?) WHERE crash_date IN (CAST(? AS DATE), CAST(? AS DATE), CAST(? AS DATE), CAST(? AS DATE)) AND crash_date >= CAST(? AS DATE) AND crash_date <= CAST(? AS DATE)",[path,"1900-01-01","1970-01-01","0001-01-01","9999-12-31",start,end]).fetchone()[0]; facts=[("population_rows_2013_2025",total),("crash_date_null_rows_unassignable_in_file",null_dates),("crash_date_sentinel_rows_in_period",sentinels)]; facts += [(f"year_{int(r.year)}_population_rows",int(r.rows)) for r in annual.itertuples()]; facts += [(f"year_{int(r.year)}_date_range",f"{r.first_date} to {r.last_date}") for r in annual.itertuples()]; facts += [("requested_years_present",",".join(str(int(y)) for y in annual.year)),("crash_date_missing_rows_in_population",0),("crash_date_default_sentinel_rows_in_population",sentinels)]; print("CHECK rows",total,"year counts",[(int(r.year),int(r.rows)) for r in annual.itertuples()]);
for c in cats:
 n=con.execute(f"SELECT count(*) FILTER (WHERE {c} IS NULL) FROM read_parquet(?) WHERE crash_date >= CAST(? AS DATE) AND crash_date <= CAST(? AS DATE)",[path,start,end]).fetchone()[0]; facts.append((f"{c}_missing_rows_population_total",int(n)));
 for r in annual.itertuples():
  n=con.execute(f"SELECT count(*) FILTER (WHERE {c} IS NULL) FROM read_parquet(?) WHERE year(crash_date)=?",[path,int(r.year)]).fetchone()[0]; facts.append((f"{c}_missing_rows_year_{int(r.year)}",int(n)))
for i in [1,2]: pd.DataFrame(facts,columns=["fact","value"]).to_csv(f"out/check_{i}.csv",index=False)'
# bash
python out/analyze.py
# bash
python -c 'import json, pathlib; p=pathlib.Path("out"); options=json.loads((p/"options.json").read_text()); plans=[json.loads((p/f"plan_{i}.json").read_text()) for i in (1,2)]; assert len(options["options"])==2; assert abs(sum(x["probability"] for x in options["options"])-1)<1e-9; assert all(x["status"]=="final" for x in plans); assert all((p/f"check_{i}.csv").exists() and (p/f"values_{i}.csv").exists() and (p/f"option_{i}.png").exists() for i in (1,2)); print("JSON valid; probabilities sum to 1; both final plans, checks, values, and charts are present.")'

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