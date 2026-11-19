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
metric: Percentage of crashes with at least one person injured or killed, using number_of_persons_injured + number_of_persons_killed > 0
denominator: All crashes with both person outcome counts present in the same time group
grouping: Night: 21:00-05:59 inclusive; Day: 06:00-20:59; 2013-2025
chart_type: bar chart
probability: 0.44
WRITTEN ANSWER:
A higher share of NYC police-reported crashes involved injury or death at night than by day in 2013-2025 (28.3% versus 23.7%), but without traffic or travel exposure the data cannot establish whether NYC streets are more dangerous at night overall. This framing addresses how often a police-reported crash involved harm by comparing the percentage with at least one injured or killed person, where Night is 21:00-05:59 and Day is 06:00-20:59 over 2013-2025; the denominator is all crashes with both person outcome counts present. The chart shows a casualty in 28.3% of nighttime crashes and 23.7% of daytime crashes, a 4.6 percentage-point difference; this is defensible as a measure of the frequency of harmful crashes conditional on a crash. It does not show whether a person, trip, or mile of travel faces more danger at night because the data have no traffic or travel-exposure denominator. The check found partial coverage for 2012 (July-December) and 2026 (January-June; 8,877/36,424 or 24.37% missing death counts), so those years were excluded; 42/2,132,218 (0.001970%) 2013-2025 rows missing an outcome count were excluded, and 23,786 (1.115574%) selected records at valid 00:00 times were retained as night despite possible default coding (no selected crash times were missing).

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
time_period,crashes,reported_casualties,mean_casualties_per_crash,crashes_with_casualty,share_crashes_with_casualty_pct
Day,1698036,534039.0,0.31450393277881034,402703.0,23.715810501073005
Night,434140,177620.0,0.4091306951674575,123057.0,28.345003915787533

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls -la
# bash
./.bin/python3 out/check_data.py
# bash
python3 out/check_data.py
# bash
python3 out/check_data.py
# bash
python3 out/check_data.py
# bash
python3 out/analyze.py
# bash
python3 -c 'import json,csv,pathlib; p=pathlib.Path("out"); plans=[json.loads((p/f"plan_{i}.json").read_text()) for i in (1,2)]; opts=json.loads((p/"options.json").read_text()); print("plans", len(plans), "options", len(opts["options"]), "probability_sum", sum(o["probability"] for o in opts["options"])); [(print(o["id"], list(csv.DictReader((p/f"values_{o[\"id\"]}.csv").open())), (p/f"option_{o[\"id\"]}.png").exists())) for o in opts["options"]]'
# bash
python3 -c 'import json,pathlib,csv; p=pathlib.Path("out"); plans=[json.loads((p/ ("plan_"+str(i)+".json")).read_text()) for i in (1,2)]; opts=json.loads((p/"options.json").read_text()); print("valid plans:",len(plans),"options:",len(opts["options"]),"probability sum:",sum(o["probability"] for o in opts["options"])); print([(o["id"],len(list(csv.DictReader((p/("values_"+str(o["id"])+".csv")).open()))),(p/("option_"+str(o["id"])+".png")).exists()) for o in opts["options"]])'
# bash
python3 -c 'import json,pathlib,csv; p=pathlib.Path("out"); plans=[json.loads((p/("plan_"+str(i)+".json")).read_text()) for i in (1,2)]; opts=json.loads((p/"options.json").read_text()); print("valid plans:",len(plans),"options:",len(opts["options"]),"probability sum:",sum(o["probability"] for o in opts["options"])); print([(o["id"],len(list(csv.DictReader((p/("values_"+str(o["id"])+".csv")).open()))),(p/("option_"+str(o["id"])+".png")).exists()) for o in opts["options"]])'
# bash
python3 out/analyze.py
# bash
python3 -c 'import json,pathlib,csv; p=pathlib.Path("out"); plans=[json.loads((p/("plan_"+str(i)+".json")).read_text()) for i in (1,2)]; opts=json.loads((p/"options.json").read_text()); assert len(opts["options"])==2 and abs(sum(o["probability"] for o in opts["options"])-1)<1e-9; print("JSON valid; probabilities sum to",sum(o["probability"] for o in opts["options"])); print([(o["id"],len(list(csv.DictReader((p/("values_"+str(o["id"])+".csv")).open()))),(p/("option_"+str(o["id"])+".png")).exists()) for o in opts["options"]])'

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