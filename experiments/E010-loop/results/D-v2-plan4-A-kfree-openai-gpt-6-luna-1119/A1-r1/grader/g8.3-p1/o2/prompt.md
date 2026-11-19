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
metric: Annual count of crashes with at least one recorded pedestrian injury or death (number_of_pedestrians_injured > 0 or number_of_pedestrians_killed > 0).
denominator: No denominator; annual count of qualifying crashes.
grouping: Calendar year of crash_date.
chart_type: line chart
probability: 0.3
WRITTEN ANSWER:
This only partly answers whether pedestrian safety improved: Brooklyn police-reported crashes with at least one pedestrian injured or killed numbered 3,498 in 2013, reached 1,724 in 2020, and numbered 2,766 in 2025; the partial 2026 year is excluded. This answers the frequency of casualty crashes, not overall pedestrian risk: it counts each Brooklyn police-reported crash record once if either pedestrian injury or pedestrian death is greater than zero, grouped by complete calendar year 2013–2025, without an exposure denominator. The count was 3,498 in 2013, reached a series low of 1,724 in 2020, and was 2,766 in 2025; this is defensible for describing how often a pedestrian-casualty crash was recorded, but it does not establish risk per pedestrian trip. The data check found zero missing borough, date, or pedestrian injury/death fields among 483,501 Brooklyn records from 2013 onward; borough matching trims and normalizes uppercase values. The chart excludes the 9,700 partial-2026 records (2.0% of the check population; coverage ends June 11) and uses complete years 2013–2025.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,casualty_crashes
2013,3498
2014,3234
2015,2962
2016,2797
2017,2550
2018,2697
2019,2623
2020,1724
2021,1856
2022,2185
2023,2310
2024,2576
2025,2766

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 out/check_plans.py
# bash
python3 out/check_plans.py
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(\"SELECT borough, COUNT(*) FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' GROUP BY borough ORDER BY COUNT(*) DESC\", [p]).fetchall())"
# bash
python3 out/check_plans.py
# bash
python3 out/check_plans.py
# bash
python3 out/analyze_plans.py
# bash
python3 out/check_plans.py
# bash
python3 out/analyze_plans.py
# bash
python3 -c "import json, pathlib; p=pathlib.Path('out/options.json'); d=json.loads(p.read_text()); print('valid_json', len(d['options']), 'options; probability_sum', sum(x['probability'] for x in d['options'])); [print(i, pathlib.Path(f'out/option_{i}.png').exists(), pathlib.Path(f'out/values_{i}.csv').exists(), pathlib.Path(f'out/plan_{i}.json').exists(), pathlib.Path(f'out/check_{i}.csv').exists()) for i in (1,2,3)]"

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