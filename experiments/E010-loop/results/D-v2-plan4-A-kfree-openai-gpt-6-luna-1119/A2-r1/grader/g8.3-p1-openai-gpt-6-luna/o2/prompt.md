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
metric: Share of eligible crash records with at least one person injured or killed, calculated as 100 × records where number_of_persons_injured + number_of_persons_killed ≥ 1 divided by eligible records
denominator: Within each time group, crash records with both number_of_persons_injured and number_of_persons_killed present
grouping: Night (20:00–05:59) versus daytime (06:00–19:59); missing/unclassifiable time is a separate group if present
chart_type: bar chart
probability: 0.5
WRITTEN ANSWER:
Partly: among crash records with both outcome counts reported, 28.4% of nighttime reports and 23.4% of daytime reports involved at least one injury or death, a crash-level share rather than traveler risk. This answers only the share-of-crashes-with-harm part: for July 1, 2012–June 11, 2026, night means 20:00–05:59 and daytime means 06:00–19:59; an injury-or-death crash has number_of_persons_injured + number_of_persons_killed ≥ 1, and the denominator in each group is records with both counts present (28.4% at night and 23.4% during daytime); missing/unclassifiable time would be a separate group, but no such rows occurred. This is a defensible crash-level severity comparison because it compares the fraction of reported crashes that involved a reported injury or death, rather than raw crash totals. It leaves risk per traveler unanswered because the dataset has no travel-exposure denominator. The check found zero missing dates, zero at the checked sentinel dates, and no missing/unknown/unparseable times; 18 injury counts and 8,913 death counts are missing, with 8,919 distinct records (0.39% of dated records) missing either field, so exclude those from numerator and denominator, while keeping the 24,566 exact-midnight records as night and disclosing possible defaults, and keeping the partial endpoint years (2012 starts July 1; 2026 ends June 11).

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
time_group,injury_or_death_crashes,eligible_crash_records,share_percent
Night (20:00–05:59),158211,556333,28.43818360586196
Daytime (06:00–19:59),398867,1703935,23.408580726377473

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
ls
# bash
python3 out/data_check.py
# bash
python3 out/data_check.py
# bash
python3 out/analyze.py
# bash
python3 out/data_check.py
# bash
python3 out/analyze.py
# bash
python3 out/data_check.py
# bash
python3 -c "import csv,json,math,pathlib; o=pathlib.Path('out'); opts=json.loads((o/'options.json').read_text())['options']; plans=[json.loads((o/f'plan_{i}.json').read_text()) for i in range(1,4)]; assert [x['id'] for x in opts]==[1,2,3]; assert math.isclose(sum(x['probability'] for x in opts),1); assert all('final_plan' in p and 'limitations' in p['final_plan'] for p in plans); v1=list(csv.DictReader((o/'values_1.csv').open())); v2=list(csv.DictReader((o/'values_2.csv').open())); v3=list(csv.DictReader((o/'values_3.csv').open())); assert sum(int(r['crash_records']) for r in v1)==2269187; assert math.isclose(float(v2[0]['share_percent']),28.43818360586196); assert math.isclose(float(v2[1]['share_percent']),23.408580726377473); assert math.isclose(float(v3[0]['mean_people_per_crash']),0.406524509601264); assert math.isclose(float(v3[1]['mean_people_per_crash']),0.309966049174411); assert all((o/f'option_{i}.png').is_file() for i in (1,2,3)); print('JSON, plans, plotted values, chart files, and probability total verified.')"

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