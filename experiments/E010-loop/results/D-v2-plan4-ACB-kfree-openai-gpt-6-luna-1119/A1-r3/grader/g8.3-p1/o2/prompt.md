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
metric: Annual percentage of eligible Brooklyn crash reports with one or more pedestrians injured or killed; numerator counts reports with number_of_pedestrians_injured > 0 or number_of_pedestrians_killed > 0.
denominator: All police-reported Brooklyn crash rows in that calendar year with both pedestrian outcome fields nonmissing; these fields are complete for every included Brooklyn row, so this is all Brooklyn crash rows.
grouping: Calendar year of crash_date.
chart_type: Line chart
probability: 0.35
WRITTEN ANSWER:
Only partly answerable: pedestrian-casualty crashes made up 7.44% of Brooklyn crash reports in 2013, 5.68% in 2017, and 11.38% in 2025. Only partly: this chart shows, for each full calendar year, the percentage of one-row-per-crash Brooklyn police reports that had one or more pedestrians injured or killed; the share was 7.44% in 2013, 5.68% in 2017, and 11.38% in 2025. This is a defensible measure of how often pedestrian casualties appeared among reported crashes, but it is not a pedestrian-trip or per-person risk measure and cannot establish whether walking became safer. The check found 659,713 of 2,132,218 rows in 2013–2025 (30.9%) had missing, blank, unknown, or nonstandard borough labels and excluded them; no Brooklyn rows had either pedestrian outcome missing, and partial 2026 (through June 11) was excluded. The denominator fell by 19,006 Brooklyn crash rows between 2019 (44,479) and 2020 (25,473), the largest neighboring-year change; across those years the share can change because of this denominator change and not the outcome, so compare it with that caution.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,crash_rows_with_pedestrian_casualty,all_eligible_brooklyn_crash_rows_denominator,share_pct
2013,3498,47024,7.438754678462062
2014,3234,47761,6.77121500806097
2015,2962,50851,5.824860868026194
2016,2797,47464,5.892887240856228
2017,2550,44915,5.677390626739396
2018,2697,47313,5.700336059856699
2019,2623,44479,5.897164954248072
2020,1724,25473,6.76795037883249
2021,1856,25174,7.37268610471121
2022,2185,23369,9.349993581240104
2023,2310,22890,10.091743119266056
2024,2576,22785,11.30568356374808
2025,2766,24303,11.381310949265522

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 out/check_plans.py
# bash
python3 out/check_plans.py
# bash
python3 out/analyze.py
# bash
python3 -c "import json, pathlib, pandas as pd; out=pathlib.Path('out'); opts=json.loads((out/'options.json').read_text()); assert len(opts['options'])==3; assert abs(sum(o['probability'] for o in opts['options'])-1)<1e-9; [json.loads((out/f'plan_{i}.json').read_text()) for i in range(1,4)]; [(pd.read_csv(out/f'values_{i}.csv').shape[0], (out/f'option_{i}.png').stat().st_size) for i in range(1,4)]; print('JSON valid; probabilities sum to 1; all three plans, values CSVs, and PNG charts are present.')"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR05: If a borough filter (borough = 'BROOKLYN') is used, the output discloses that crashes with no borough recorded are left out of the borough figure. Saying that such rows exist and are excluded is enough; a number is not required, and an overall share or a per-year share both count (for reference only: 19.9–38.1% of rows per year have no borough). Saying only that other boroughs or non-matching rows are excluded, or that no borough values are missing among the Brooklyn rows, does not count.
- tr_TR11: The output does not call Brooklyn 'safer' or 'less safe' from counts alone without saying that there is no pedestrian exposure measure.
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.