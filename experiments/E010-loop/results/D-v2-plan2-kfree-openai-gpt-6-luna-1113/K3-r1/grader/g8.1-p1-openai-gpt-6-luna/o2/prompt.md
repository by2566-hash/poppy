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
metric: Annual percentage of combined reported motorist and cyclist deaths attributable to each category, 2013–2025.
denominator: For each calendar year, the sum of reported motorist deaths and reported cyclist deaths; excludes all other road-user categories.
grouping: Calendar year of crash_date and category defined by the motorist or cyclist killed-count field.
chart_type: 100% stacked bar chart
probability: 0.25
WRITTEN ANSWER:
Cyclists accounted for 9.1% of combined motorist-and-cyclist deaths in 2013, reached a high of 27.4% in 2019, and accounted for 22.1% in 2025. This partly answers the year-by-year comparison as composition: for each calendar year of police-reported crashes dated 2013–2025 inclusive, each category's reported deaths are divided by that year's combined motorist and cyclist deaths. Cyclists' share was 9.1% in 2013, peaked at 27.4% in 2019, and was 22.1% in 2025, with motorist deaths making up the remainder. This share is a defensible way to compare the two categories' composition across years, but it does not show absolute death counts, deaths among other road users, or per-trip/per-person risk. The check found 2,132,218 in-scope crash rows, zero missing values in either death field, zero missing crash dates and zero dates at 1970-01-01 within scope, and date bounds spanning January 1–December 31 in every year; all in-scope rows were retained, though full date bounds do not establish reporting completeness.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,combined_deaths,category,reported_deaths,share_percent
2013,121,Motorist,110,90.9090909090909
2014,129,Motorist,109,84.49612403100775
2015,110,Motorist,95,86.36363636363636
2016,90,Motorist,72,80.0
2017,134,Motorist,107,79.8507462686567
2018,108,Motorist,98,90.74074074074075
2019,113,Motorist,82,72.56637168141593
2020,168,Motorist,139,82.73809523809523
2021,153,Motorist,134,87.58169934640523
2022,135,Motorist,116,85.92592592592592
2023,154,Motorist,123,79.87012987012987
2024,135,Motorist,111,82.22222222222221
2025,104,Motorist,81,77.88461538461539
2013,121,Cyclist,11,9.090909090909092
2014,129,Cyclist,20,15.503875968992247
2015,110,Cyclist,15,13.636363636363635
2016,90,Cyclist,18,20.0
2017,134,Cyclist,27,20.149253731343283
2018,108,Cyclist,10,9.25925925925926
2019,113,Cyclist,31,27.43362831858407
2020,168,Cyclist,29,17.261904761904763
2021,153,Cyclist,19,12.418300653594772
2022,135,Cyclist,19,14.074074074074074
2023,154,Cyclist,31,20.12987012987013
2024,135,Cyclist,24,17.77777777777778
2025,104,Cyclist,23,22.115384615384613

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