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
metric: Annual sum of number_of_pedestrians_killed (pedestrian fatalities).
denominator: None; count of people, not a rate or share.
grouping: Calendar year of crash_date
chart_type: Bar chart
probability: 0.65
WRITTEN ANSWER:
Annual pedestrian fatalities were highest in 2013 at 176, fell to a low of 101 in 2020, and totaled 119 in 2025. This framing directly answers how many pedestrians were recorded killed in each calendar year: counts peak at 176 in 2013, reach a low of 101 in 2020, and are 119 in 2025. A bar chart is defensible because it makes each annual total and comparisons across years easy to read, while it does not measure per-capita or per-crash risk or fatalities in unreported crashes. The check found no missing or negative pedestrian-fatality values among the 2,132,218 selected crash rows, and every year has observed dates at both calendar-year endpoints, though this does not establish reporting completeness. Zero-valued rows remain as zero contributors (for example, 85,432 of 85,546 crash rows in 2025); crashes without a usable date cannot be assigned to a year and were outside the date-filtered check, so their count is unknown.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrians_killed
2013,176
2014,133
2015,133
2016,149
2017,127
2018,123
2019,131
2020,101
2021,132
2022,135
2023,107
2024,124
2025,119

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c 'import duckdb; print(duckdb.__version__)'
# bash
python -c 'import duckdb, pandas as pd
p="data/crashes.parquet"
q="""WITH selected AS (SELECT crash_date, number_of_pedestrians_killed, EXTRACT(YEAR FROM crash_date)::INT AS yr FROM read_parquet(?) WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'') SELECT yr, COUNT(*) AS rows, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date, COUNT(*) FILTER (WHERE crash_date IS NULL) AS missing_date, COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS missing_pedestrian_fatality_value, COUNT(*) FILTER (WHERE number_of_pedestrians_killed < 0) AS negative_pedestrian_fatality_values, COUNT(*) FILTER (WHERE number_of_pedestrians_killed = 0) AS zero_pedestrian_fatality_values FROM selected GROUP BY yr ORDER BY yr"""
df=duckdb.sql(q, params=[p]).df()
rows=[]
def add(f,v): rows.append({"fact":f,"value":str(v)})
add("Population rows across planned years 2013–2025", int(df.rows.sum()) if len(df) else 0)
for y in range(2013,2026):
 r=df[df.yr==y]
 if len(r)==0:
  add(f"{y}: population rows",0); add(f"{y}: observed date coverage", "no rows"); add(f"{y}: year coverage status", "no observations; cannot establish completeness")
 else:
  x=r.iloc[0]
  add(f"{y}: population rows",int(x["rows"]))
  add(f"{y}: observed date coverage",f"{x.first_date} through {x.last_date}")
  add(f"{y}: year coverage status", "full calendar year by observed first/last date" if str(x.first_date)==f"{y}-01-01" and str(x.last_date)==f"{y}-12-31" else "partial calendar-year coverage by observed first/last date")
  add(f"{y}: rows with missing crash_date",int(x.missing_date))
  add(f"{y}: rows with missing pedestrian fatality value",int(x.missing_pedestrian_fatality_value))
  add(f"{y}: rows with negative (impossible) pedestrian fatality value",int(x.negative_pedestrian_fatality_values))
  add(f"{y}: rows with zero pedestrian fatality value (valid zero, checked for pile-up)",int(x.zero_pedestrian_fatality_values))
add("Across planned population: rows with missing crash_date",int(df.missing_date.sum()) if len(df) else 0)
add("Across planned population: rows with missing pedestrian fatality value",int(df.missing_pedestrian_fatality_value.sum()) if len(df) else 0)
add("Across planned population: rows with negative (impossible) pedestrian fatality value",int(df.negative_pedestrian_fatality_values.sum()) if len(df) else 0)
pd.DataFrame(rows).to_csv("out/check_1.csv",index=False)'
# bash
python -c 'import duckdb, pandas as pd
p="data/crashes.parquet"
q="""WITH selected AS (SELECT crash_date, number_of_pedestrians_killed, EXTRACT(YEAR FROM crash_date)::INT AS yr FROM read_parquet(?) WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'') SELECT yr, COUNT(*) AS rows, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date, COUNT(*) FILTER (WHERE crash_date IS NULL) AS missing_date, COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS missing_value, COUNT(*) FILTER (WHERE number_of_pedestrians_killed < 0) AS negative_value, COUNT(*) FILTER (WHERE number_of_pedestrians_killed = 0) AS zero_value FROM selected GROUP BY yr ORDER BY yr"""
df=duckdb.sql(q,params=[p]).df(); out=[]
def add(f,v): out.append({"fact":f,"value":str(v)})
add("Population rows across planned years 2013–2025",int(df.rows.sum()) if len(df) else 0)
for y in range(2013,2026):
 r=df[df.yr==y]
 if not len(r):
  add(f"{y}: population rows",0); add(f"{y}: observed date coverage","no rows"); add(f"{y}: year coverage status","no observations; completeness unknown")
  continue
 x=r.iloc[0]; first=str(x.first_date)[:10]; last=str(x.last_date)[:10]
 add(f"{y}: population rows",int(x["rows"]))
 add(f"{y}: observed date coverage",f"{first} through {last}")
 add(f"{y}: year coverage status", "observed dates span Jan 1–Dec 31; reporting completeness cannot be established from endpoints alone" if first==f"{y}-01-01" and last==f"{y}-12-31" else "partial year by observed first/last date; reporting completeness not established")
 add(f"{y}: rows with missing crash_date",int(x.missing_date))
 add(f"{y}: rows with missing pedestrian fatality value",int(x.missing_value))
 add(f"{y}: rows with negative (impossible) pedestrian fatality value",int(x.negative_value))
 add(f"{y}: rows with zero pedestrian fatality value (valid zero, checked for pile-up)",int(x.zero_value))
add("Across planned population: rows with missing crash_date",int(df.missing_date.sum()) if len(df) else 0)
add("Across planned population: rows with missing pedestrian fatality value",int(df.missing_value.sum()) if len(df) else 0)
add("Across planned population: rows with negative (impossible) pedestrian fatality value",int(df.negative_value.sum()) if len(df) else 0)
pd.DataFrame(out).to_csv("out/check_1.csv",index=False)'
# bash
python -c 'import duckdb, pandas as pd
p="data/crashes.parquet"
q="""WITH selected AS (SELECT crash_date, number_of_pedestrians_killed, EXTRACT(YEAR FROM crash_date)::INT AS yr FROM read_parquet(?) WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'') SELECT yr, COUNT(*) AS rows, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date, COUNT(*) FILTER (WHERE crash_date IS NULL) AS missing_date, COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS missing_value, COUNT(*) FILTER (WHERE number_of_pedestrians_killed < 0) AS negative_value, COUNT(*) FILTER (WHERE number_of_pedestrians_killed = 0) AS zero_value FROM selected GROUP BY yr ORDER BY yr"""
df=duckdb.sql(q,params=[p]).df(); out=[]
def add(f,v): out.append({"fact":f,"value":str(v)})
add("Population rows across planned years 2013–2025",int(df.rows.sum()) if len(df) else 0)
for y in range(2013,2026):
 r=df[df.yr==y]
 if not len(r):
  add(f"{y}: population rows",0); add(f"{y}: observed date coverage","no rows"); add(f"{y}: year coverage status","no observations; completeness unknown"); continue
 x=r.iloc[0]; first=str(x.first_date)[:10]; last=str(x.last_date)[:10]
 add(f"{y}: population rows",int(x["rows"]))
 add(f"{y}: observed date coverage",f"{first} through {last}")
 add(f"{y}: year coverage status", "observed dates span Jan 1–Dec 31; reporting completeness cannot be established from endpoints alone" if first==f"{y}-01-01" and last==f"{y}-12-31" else "partial year by observed first/last date; reporting completeness not established")
 add(f"{y}: rows with missing crash_date",int(x.missing_date))
 add(f"{y}: rows with missing pedestrian fatality value",int(x.missing_value))
 add(f"{y}: rows with negative (impossible) pedestrian fatality value",int(x.negative_value))
 add(f"{y}: rows with zero pedestrian fatality value (valid zero, checked for pile-up)",int(x.zero_value))
add("Across planned population: rows with missing crash_date",int(df.missing_date.sum()) if len(df) else 0)
add("Across planned population: rows with missing pedestrian fatality value",int(df.missing_value.sum()) if len(df) else 0)
add("Across planned population: rows with negative (impossible) pedestrian fatality value",int(df.negative_value.sum()) if len(df) else 0)
pd.DataFrame(out).to_csv("out/check_2.csv",index=False)'
# bash
python out/analyze.py
# bash
python -c 'import json, pathlib, pandas as pd
root=pathlib.Path("out")
opts=json.loads((root/"options.json").read_text())
assert len(opts["options"])==2
assert abs(sum(x["probability"] for x in opts["options"])-1)<1e-9
for i in (1,2):
 assert (root/f"plan_{i}.json").exists() and (root/f"check_{i}.csv").exists() and (root/f"option_{i}.png").exists()
 assert json.loads((root/f"plan_{i}.json").read_text())["final_plan"]
 v=pd.read_csv(root/f"values_{i}.csv")
 assert v["year"].tolist()==list(range(2013,2026))
 assert len(v)==13 and v["pedestrians_killed"].sum()>0
print("Valid JSON, probabilities sum to 1, and each option has matching 2013–2025 plan/check/chart/value outputs.")'

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