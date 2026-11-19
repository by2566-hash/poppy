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
metric: Annual absolute reported deaths: sum number_of_motorist_killed or number_of_cyclist_killed across crash records, by category and calendar year, 2013–2025.
denominator: None; absolute counts, not rates.
grouping: Calendar year of crash_date and category defined by the motorist or cyclist killed-count field.
chart_type: Two-series line chart
probability: 0.75
WRITTEN ANSWER:
Reported motorist deaths exceeded cyclist deaths in all 13 years; in 2025 the counts were 81 motorist deaths and 23 cyclist deaths, with respective series highs of 139 in 2020 and 31 in both 2019 and 2023. This directly compares absolute reported deaths by calendar year: the plotted motorist and cyclist values are the sums of their respective killed-count fields across all police-reported crashes with crash_date from 2013 through 2025 inclusive, with no denominator. Motorist deaths exceed cyclist deaths in all 13 years; motorist deaths peak at 139 in 2020, while cyclist deaths peak at 31 in both 2019 and 2023. Absolute counts are a defensible measure of annual burden, but they do not compare per-trip or per-person risk because travel exposure is not provided. The check found 2,132,218 in-scope crash rows, zero missing values in either death field, zero missing crash dates and zero dates at 1970-01-01 within scope, and date bounds spanning January 1–December 31 in every year; all in-scope rows were retained, although date bounds alone do not establish reporting completeness.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,category,reported_deaths
2013,Motorist,110
2014,Motorist,109
2015,Motorist,95
2016,Motorist,72
2017,Motorist,107
2018,Motorist,98
2019,Motorist,82
2020,Motorist,139
2021,Motorist,134
2022,Motorist,116
2023,Motorist,123
2024,Motorist,111
2025,Motorist,81
2013,Cyclist,11
2014,Cyclist,20
2015,Cyclist,15
2016,Cyclist,18
2017,Cyclist,27
2018,Cyclist,10
2019,Cyclist,31
2020,Cyclist,29
2021,Cyclist,19
2022,Cyclist,19
2023,Cyclist,31
2024,Cyclist,24
2025,Cyclist,23

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 out/check_data.py
# bash
python3 out/check_data.py
# bash
python3 out/analyze.py
# bash
python3 -c 'import csv,json,math,pathlib; root=pathlib.Path("out"); opts=json.loads((root/"options.json").read_text())["options"]; plans=[json.loads((root/f"plan_{i}.json").read_text()) for i in (1,2)]; assert len(opts)==2 and math.isclose(sum(x["probability"] for x in opts),1); assert all(p["final_plan"]["limitations"] for p in plans); rows1=list(csv.DictReader((root/"values_1.csv").open())); rows2=list(csv.DictReader((root/"values_2.csv").open())); assert len(rows1)==26 and len(rows2)==26; counts={(int(r["year"]),r["category"]):int(r["reported_deaths"]) for r in rows1}; shares={(int(r["year"]),r["category"]):float(r["share_percent"]) for r in rows2}; assert all(counts[(y,"Motorist")]>counts[(y,"Cyclist")] for y in range(2013,2026)); assert all(abs(shares[(y,"Motorist")]+shares[(y,"Cyclist")]-100)<1e-9 for y in range(2013,2026)); assert all((root/f"option_{i}.png").stat().st_size>0 for i in (1,2)); print("Validated JSON, 13 annual comparisons, annual shares, and both chart files.")'

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