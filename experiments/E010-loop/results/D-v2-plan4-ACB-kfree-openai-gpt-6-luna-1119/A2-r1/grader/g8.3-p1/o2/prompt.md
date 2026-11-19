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
metric: Annual mean number of persons injured plus killed per eligible reported crash
denominator: Count of eligible police-reported crash rows in each calendar year and time-of-day group; rows have nonmissing crash_date, crash_time, number_of_persons_injured, and number_of_persons_killed
grouping: Calendar year 2013–2025 and time of day: night 20:00–05:59; day 06:00–19:59
chart_type: line chart
probability: 0.45
WRITTEN ANSWER:
This answers only part of whether NYC streets are more dangerous at night: in 2025, the mean was 0.600 injured-or-killed persons per eligible night crash and 0.576 per eligible day crash, but the data cannot determine travel-level danger. This answers only part of the question: for each year from 2013–2025, the chart shows the sum of persons injured and killed divided by police-reported crash rows with nonmissing date, time and both person counts; night is 20:00–05:59 and day is 06:00–19:59, with 2025 means of 0.600 and 0.576 persons per crash, respectively. This mean-harm-per-crash framing is defensible because it includes the number of people injured or killed, including multiple people in one crash, rather than counting each crash as only harmed or not harmed. It leaves unanswered whether an individual trip or street user faces more danger at night because traffic and other exposure denominators are absent. The check found 2012 (100,545 dated rows) and 2026 (36,424) partial by observed dates and excluded them; of 2,132,218 rows in candidate full years, 18 lacked injury counts and 36 lacked death counts (42 distinct rows excluded), no crash times were missing, and 23,787 00:00 records were retained in night though they may be defaults; date bounds cannot prove source completeness, and annual dated rows fell by 98,568 from 211,486 in 2019 to 112,918 in 2020, so any change in this row-denominator mean across those years could come from the denominator shift rather than outcome counts.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
metric,year,time_period,numerator,denominator,metric_value
Mean number of persons injured plus killed per reported crash,2013,Day,40119.00000000,158695,0.25280570
Mean number of persons injured plus killed per reported crash,2013,Night,15306.00000000,45047,0.33977845
Mean number of persons injured plus killed per reported crash,2014,Day,36840.00000000,160471,0.22957419
Mean number of persons injured plus killed per reported crash,2014,Night,14652.00000000,45575,0.32149205
Mean number of persons injured plus killed per reported crash,2015,Day,37176.00000000,169298,0.21958913
Mean number of persons injured plus killed per reported crash,2015,Night,14436.00000000,48410,0.29820285
Mean number of persons injured plus killed per reported crash,2016,Day,42924.00000000,176645,0.24299584
Mean number of persons injured plus killed per reported crash,2016,Night,17639.00000000,53186,0.33164743
Mean number of persons injured plus killed per reported crash,2017,Day,43187.00000000,177547,0.24324263
Mean number of persons injured plus killed per reported crash,2017,Night,17706.00000000,53441,0.33131865
Mean number of persons injured plus killed per reported crash,2018,Day,44397.00000000,179183,0.24777462
Mean number of persons injured plus killed per reported crash,2018,Night,17765.00000000,52365,0.33925332
Mean number of persons injured plus killed per reported crash,2019,Day,43333.00000000,162068,0.26737542
Mean number of persons injured plus killed per reported crash,2019,Night,18302.00000000,49418,0.37035088
Mean number of persons injured plus killed per reported crash,2020,Day,30682.00000000,82633,0.37130444
Mean number of persons injured plus killed per reported crash,2020,Night,14201.00000000,30284,0.46892749
Mean number of persons injured plus killed per reported crash,2021,Day,34680.00000000,77477,0.44761671
Mean number of persons injured plus killed per reported crash,2021,Night,17402.00000000,33080,0.52605804
Mean number of persons injured plus killed per reported crash,2022,Day,35540.00000000,72578,0.48968007
Mean number of persons injured plus killed per reported crash,2022,Night,16683.00000000,31309,0.53284998
Mean number of persons injured plus killed per reported crash,2023,Day,37385.00000000,67304,0.55546476
Mean number of persons injured plus killed per reported crash,2023,Night,17147.00000000,29303,0.58516193
Mean number of persons injured plus killed per reported crash,2024,Day,37314.00000000,63676,0.58599786
Mean number of persons injured plus killed per reported crash,2024,Night,16984.00000000,27640,0.61447178
Mean number of persons injured plus killed per reported crash,2025,Day,34479.00000000,59891,0.57569585
Mean number of persons injured plus killed per reported crash,2025,Night,15380.00000000,25652,0.59956339

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 out/data_check.py
# bash
python3 out/data_check.py
# bash
python3 out/data_check.py
# bash
python3 out/analyze.py
# bash
python3 out/analyze.py
# bash
python3 -c 'import json,pandas as pd; from pathlib import Path; p=Path("out"); o=json.loads((p/"options.json").read_text()); print("options",len(o["options"]),"probability_sum",sum(x["probability"] for x in o["options"]));
for i in (1,2):
 d=pd.read_csv(p/f"values_{i}.csv"); print(i,"rows",len(d),"denominator_sum",int(d.denominator.sum()),"years",d.year.min(),d.year.max(),"latest",d[d.year==2025][["time_period","numerator","denominator","metric_value"]].to_dict("records"),"chart_exists",(p/f"option_{i}.png").exists())'
# bash
python3 -c 'import json,csv,re; from pathlib import Path; p=Path("out");
for f in ("options.json","plan_1.json","plan_2.json"):
 json.loads((p/f).read_text()); print(f,"valid JSON")
o=json.loads((p/"options.json").read_text()); print("probabilities",sum(x["probability"] for x in o["options"]));
for x in o["options"]:
 print("option",x["id"],"interpretation_sentences",len(re.split(r"(?<=[.!?])\\s+(?=[A-Z])",x["interpretation"])))
for f in ("check_1.csv","check_2.csv"):
 with (p/f).open(newline="") as h: rows=list(csv.DictReader(h)); print(f,"columns",list(rows[0]),"facts",len(rows))'
# bash
python3 -c 'import json,re; o=json.load(open("out/options.json")); print([len(re.split(r"(?<=[.!?])\s+",x["interpretation"])) for x in o["options"]])'

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