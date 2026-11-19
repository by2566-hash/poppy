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
metric: Mean number of persons injured or killed per usable reported crash, calculated as the sum of number_of_persons_injured plus number_of_persons_killed divided by usable crash rows in each time group.
denominator: Usable reported crash rows in each time group with nonmissing values for both person outcome fields; each crash is one denominator unit.
grouping: Night (20:00–23:59 and 00:01–05:59), day (06:00–19:59), and exactly 00:00 (possibly default), pooled over complete calendar years 2013–2025.
chart_type: Bar chart
probability: 0.45
WRITTEN ANSWER:
This file cannot establish whether NYC streets are more dangerous at night; the mean was 0.409 injured or killed persons per nighttime crash versus 0.310 per daytime crash. This partly answers the question as recorded casualty burden: in complete calendar years 2013–2025, the mean of injured plus killed persons per usable crash was 0.409 at night (20:00–23:59 and 00:01–05:59) and 0.310 by day (06:00–19:59), with exact 00:00 separate at 0.359. This mean is defensible because it divides total recorded injured and killed persons by crash rows, so crashes with multiple casualties contribute more than crashes with one. It leaves relative risk per trip or person exposed unanswered because the file has no traffic, trip, or pedestrian exposure denominator. The checks found 2,132,218 crashes in complete years and 2,132,176 usable rows after 42 rows (0.002%) with a missing injury or killed field were excluded (18 injury and 36 killed entries missing, with overlap); 136,969 rows from partial 2012/2026 were excluded, no crash times were missing, and 23,787 exact-midnight rows (1.12%) were kept as their own possibly-default group (23,786 remained after outcome exclusions).

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
time_group,crash_count,injured_persons,killed_persons,total_casualties,mean_casualties_per_crash
Day,1607466,496258.0,1798.0,498056.0,0.30983921277339616
Night,500924,203447.0,1611.0,205058.0,0.4093595036372783
00:00 (possibly default),23786,8542.0,3.0,8545.0,0.35924493399478685

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python out/data_check.py
# bash
python out/data_check.py
# bash
python out/analyze.py
# bash
python out/analyze.py
# bash
python out/analyze.py
# bash
python out/data_check.py
# bash
python -c 'import json, pathlib; root=pathlib.Path("out"); opts=json.loads((root/"options.json").read_text()); plans=[json.loads((root/f"plan_{i}.json").read_text()) for i in (1,2)]; print("options:", len(opts["options"]), "probability sum:", sum(x["probability"] for x in opts["options"])); print("plans valid:", all("final_plan" in p for p in plans)); print("artifacts:", all((root/f"{stem}_{i}.{ext}").exists() for i in (1,2) for stem,ext in (("check","csv"),("values","csv"),("option","png"))))'

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