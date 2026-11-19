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
metric: Annual share of eligible reported crashes with at least one person injured or killed
denominator: Count of eligible police-reported crash rows in each calendar year and time-of-day group; rows have nonmissing crash_date, crash_time, number_of_persons_injured, and number_of_persons_killed
grouping: Calendar year 2013–2025 and time of day: night 20:00–05:59; day 06:00–19:59
chart_type: line chart
probability: 0.55
WRITTEN ANSWER:
This answers only part of whether NYC streets are more dangerous at night: in 2025, 42.5% of eligible night crashes and 44.3% of eligible day crashes involved at least one person injured or killed, but the data cannot determine travel-level danger. This answers only part of the question: for each year from 2013–2025, the chart gives the share of police-reported crash rows with nonmissing date, time, injury count and death count that had at least one person injured or killed; night is 20:00–05:59 and day is 06:00–19:59, with 2025 values of 42.5% and 44.3%, respectively. This per-crash injury-or-death share is a defensible severity-prevalence measure because it uses the reported crash count in each year/time group as its denominator. It leaves unanswered whether an individual trip or street user faces more danger at night because traffic and other exposure denominators are absent. The check found 2012 (100,545 dated rows) and 2026 (36,424) partial by observed dates and excluded them; of 2,132,218 rows in candidate full years, 18 lacked injury counts and 36 lacked death counts (42 distinct rows excluded), no crash times were missing, and 23,787 00:00 records were retained in night though they may be defaults; date bounds cannot prove source completeness, and annual dated rows fell by 98,568 from 211,486 in 2019 to 112,918 in 2020, so any change in this share across those years could come from the denominator shift rather than outcome counts.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
metric,year,time_period,numerator,denominator,metric_value
Share of reported crashes with ≥1 person injured or killed,2013,Day,29566,158695,0.18630707
Share of reported crashes with ≥1 person injured or killed,2013,Night,10707,45047,0.23768508
Share of reported crashes with ≥1 person injured or killed,2014,Day,27421,160471,0.17087823
Share of reported crashes with ≥1 person injured or killed,2014,Night,10283,45575,0.22562809
Share of reported crashes with ≥1 person injured or killed,2015,Day,27827,169298,0.16436697
Share of reported crashes with ≥1 person injured or killed,2015,Night,10213,48410,0.21096881
Share of reported crashes with ≥1 person injured or killed,2016,Day,31976,176645,0.18101843
Share of reported crashes with ≥1 person injured or killed,2016,Night,12263,53186,0.23056819
Share of reported crashes with ≥1 person injured or killed,2017,Day,32366,177547,0.18229539
Share of reported crashes with ≥1 person injured or killed,2017,Night,12308,53441,0.23031006
Share of reported crashes with ≥1 person injured or killed,2018,Day,33341,179183,0.18607234
Share of reported crashes with ≥1 person injured or killed,2018,Night,12426,52365,0.23729590
Share of reported crashes with ≥1 person injured or killed,2019,Day,32670,162068,0.20158205
Share of reported crashes with ≥1 person injured or killed,2019,Night,12769,49418,0.25838763
Share of reported crashes with ≥1 person injured or killed,2020,Day,23507,82633,0.28447473
Share of reported crashes with ≥1 person injured or killed,2020,Night,9854,30284,0.32538634
Share of reported crashes with ≥1 person injured or killed,2021,Day,26743,77477,0.34517341
Share of reported crashes with ≥1 person injured or killed,2021,Night,12066,33080,0.36475212
Share of reported crashes with ≥1 person injured or killed,2022,Day,27531,72578,0.37932982
Share of reported crashes with ≥1 person injured or killed,2022,Night,11805,31309,0.37704813
Share of reported crashes with ≥1 person injured or killed,2023,Day,28497,67304,0.42340723
Share of reported crashes with ≥1 person injured or killed,2023,Night,11975,29303,0.40866123
Share of reported crashes with ≥1 person injured or killed,2024,Day,28390,63676,0.44585087
Share of reported crashes with ≥1 person injured or killed,2024,Night,11839,27640,0.42832851
Share of reported crashes with ≥1 person injured or killed,2025,Day,26526,59891,0.44290461
Share of reported crashes with ≥1 person injured or killed,2025,Night,10891,25652,0.42456729

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