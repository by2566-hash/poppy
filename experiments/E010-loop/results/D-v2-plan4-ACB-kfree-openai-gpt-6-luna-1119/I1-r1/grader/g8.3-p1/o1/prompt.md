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
metric: Sum of number_of_motorist_killed by calendar year of crash_date (reported motorist deaths).
denominator: None; an annual count, not a rate.
grouping: Calendar year of crash_date, 2013-2025 inclusive.
chart_type: Vertical bar chart
probability: 0.45
WRITTEN ANSWER:
This crash file cannot establish whether motorist-death risk per mile declined; it records 110 motorist deaths in 2013 and 81 in 2025, with yearly counts varying in between. This partly answers the question by showing the annual sum of reported motorist deaths among NYC police-reported crashes with an assignable date in calendar years 2013-2025: the count is 110 in 2013 and 81 in 2025. An annual count is a defensible description of reported fatality burden, but it is not adjusted for travel exposure. The file has no miles-driven or vehicle-miles-traveled denominator, so it leaves unanswered whether the per-mile risk declined. The check found 0 missing motorist-death counts among 2,132,218 in-range crashes, so none were excluded for that reason; observed date endpoints span Jan 1-Dec 31 in every year but do not prove day-by-day completeness, and records without an assignable crash year are outside the plan's year filter.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_deaths,crash_records
2013,110.0,203742
2014,109.0,206046
2015,95.0,217708
2016,72.0,229833
2017,107.0,231007
2018,98.0,231564
2019,82.0,211486
2020,139.0,112918
2021,134.0,110558
2022,116.0,103887
2023,123.0,96607
2024,111.0,91316
2025,81.0,85546

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
mkdir out
# bash
python3 out/check_plans.py
# bash
python3 out/analyze.py
# bash
python3 -c 'import json,pathlib; p=pathlib.Path("out"); d=json.loads((p/"options.json").read_text()); print("probability_sum",sum(x["probability"] for x in d["options"])); print("interpretation_sentences",[x["interpretation"].count(".") for x in d["options"]]); print("artifacts",[(n,(p/n).exists(),(p/n).stat().st_size if (p/n).exists() else 0) for n in ["option_1.png","option_2.png","values_1.csv","values_2.csv","check_1.csv","check_2.csv"]])'

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