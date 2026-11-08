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
metric: Annual count of reported cyclist deaths and annual count of reported motorist deaths, calculated by summing the corresponding per-crash fields
denominator: None; these are counts, not rates
grouping: Calendar year and victim group (cyclist, motorist)
chart_type: Two-series line chart
probability: 0.65
WRITTEN ANSWER:
Motorist deaths exceeded cyclist deaths in every year, ranging from 72–139 motorist deaths versus 10–31 cyclist deaths annually; motorist deaths peaked at 139 in 2020, while cyclist deaths peaked at 31 in 2019 and 2023. This framing answers the year-by-year comparison in absolute numbers: motorist deaths exceeded cyclist deaths in every year, with annual counts of 72–139 for motorists and 10–31 for cyclists. A two-series annual line chart is defensible because it preserves the actual count scale and shows both groups over the same calendar years. It does not adjust for the number of travelers or distance traveled, so it cannot compare individual risk; 2,132,218 crash rows are included and every year from 2013 through 2025 has a full-year date span. Neither death field has any NULL or negative values; 2,131,942 cyclist-field values (99.99%) and 2,130,945 motorist-field values (99.94%) are zero, and we kept these as valid no-death counts rather than dropping them; full-year date spans do not establish reporting completeness.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,cyclist_deaths,motorist_deaths
2013,11,110
2014,20,109
2015,15,95
2016,18,72
2017,27,107
2018,10,98
2019,31,82
2020,29,139
2021,19,134
2022,19,116
2023,31,123
2024,24,111
2025,23,81

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
ls
# bash
python3 out/check_data.py
# bash
python3 out/check_data.py
# bash
python3 out/analyze.py
# bash
python3 -c 'import csv,json,pathlib; p=pathlib.Path("out"); plans=[json.loads((p/f"plan_{i}.json").read_text()) for i in (1,2)]; opts=json.loads((p/"options.json").read_text()); a=list(csv.DictReader((p/"values_1.csv").open())); b=list(csv.DictReader((p/"values_2.csv").open())); assert len(a)==len(b)==13; assert all(x["year"]==y["year"] and int(y["motorist_minus_cyclist_deaths"])==int(y["motorist_deaths"])-int(y["cyclist_deaths"]) for x,y in zip(a,b)); assert abs(sum(o["probability"] for o in opts["options"])-1)<1e-9; assert len(opts["options"])==2; print("JSON valid; 13 years aligned; gap values reconcile; option probabilities sum to 1.")'

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