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
metric: Annual count of pedestrians killed in Brooklyn police-reported crashes; grouped by crash calendar year.
denominator: None; absolute annual count, not an exposure-adjusted rate.
grouping: Calendar year of crash_date, 2013 onward; 2026 is partial through June 11.
chart_type: Annual line chart for full years, with the incomplete 2026 point separately marked and not connected.
probability: 0.45
WRITTEN ANSWER:
Pedestrian deaths rose 30% from 30 in 2013 to 39 in 2025, so recorded fatalities did not improve over that comparison; exposure-adjusted risk is unavailable. This framing answers the fatality component by summing pedestrians killed in police-reported crashes whose borough label normalizes to BROOKLYN (upper(trim(borough)) = BROOKLYN), grouped by crash calendar year from 2013 onward, with no denominator: deaths were 30 in 2013 and 39 in 2025, with 46 in 2015 and 17 in 2020; the partial 2026 total is 9 through June 11. Fatalities are a defensible severity indicator, but this framing leaves nonfatal injuries and exposure-adjusted risk unanswered. The check found 668,406 dated 2013-on records with borough missing or unknown, excluded because Brooklyn could not be assigned; it found zero Brooklyn rows with missing dates and zero missing pedestrian-death values in the selected population, so no rows were dropped for missing outcomes. All 9,700 Brooklyn crash rows through June 11, 2026 were kept but shown as partial rather than comparable to full years.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,value,coverage,period_end
2013,30,full,2013-12-31
2014,42,full,2014-12-31
2015,46,full,2015-12-31
2016,20,full,2016-12-31
2017,20,full,2017-12-31
2018,23,full,2018-12-31
2019,33,full,2019-12-31
2020,17,full,2020-12-31
2021,32,full,2021-12-31
2022,23,full,2022-12-31
2023,22,full,2023-12-31
2024,31,full,2024-12-31
2025,39,full,2025-12-31
2026,9,partial,2026-06-11

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python out/check_data.py
# bash
python out/check_data.py
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"select borough, count(*) n from read_parquet(?) where crash_date >= date '2013-01-01' group by borough order by n desc limit 20\",[p]).fetchall())"
# bash
python out/check_data.py
# bash
python out/analyze.py
# bash
python out/analyze.py
# bash
python -c "import json; p='out/options.json'; d=json.load(open(p)); print('options',len(d['options']),'probability_sum',sum(x['probability'] for x in d['options'])); print('keys',list(d['options'][0])); assert abs(sum(x['probability'] for x in d['options'])-1)<1e-9; assert len(d['options'])==2"
# bash
python -c "import pandas as pd; a=pd.read_csv('out/values_1.csv'); b=pd.read_csv('out/values_2.csv'); print('casualties 2013, 2020, 2025, 2026:',a.set_index('year').loc[[2013,2020,2025,2026],'value'].to_dict()); print('deaths 2013, 2015, 2020, 2025, 2026:',b.set_index('year').loc[[2013,2015,2020,2025,2026],'value'].to_dict()); print('casualty change pct',round((a.loc[a.year.eq(2025),'value'].iloc[0]/a.loc[a.year.eq(2013),'value'].iloc[0]-1)*100,1)); print('death change pct',round((b.loc[b.year.eq(2025),'value'].iloc[0]/b.loc[b.year.eq(2013),'value'].iloc[0]-1)*100,1)); assert a.iloc[-1]['coverage']=='partial' and b.iloc[-1]['coverage']=='partial'"
# bash
python out/analyze.py
# bash
python out/check_data.py
# bash
python -m py_compile out/check_data.py out/analyze.py && python -c "import json; [json.load(open(p)) for p in ['out/plan_1.json','out/plan_2.json','out/options.json']]; print('JSON and Python syntax valid')"
# bash
python -c "import shutil; shutil.rmtree('out/__pycache__')"
# bash
python -c "import ast,json,pathlib; ast.parse(pathlib.Path('out/check_data.py').read_text()); ast.parse(pathlib.Path('out/analyze.py').read_text()); data=json.loads(pathlib.Path('out/options.json').read_text()); plans=[json.loads(pathlib.Path(f'out/plan_{i}.json').read_text()) for i in (1,2)]; assert abs(sum(o['probability'] for o in data['options'])-1)<1e-9; assert all(p['final_plan']['limitations'] and 'data_check' not in p['final_plan'] for p in plans); files=['out/check_1.csv','out/check_2.csv','out/values_1.csv','out/values_2.csv','out/option_1.png','out/option_2.png']; assert all(pathlib.Path(f).is_file() for f in files); print('Final artifact and JSON checks passed')"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR05: If a borough filter (borough = 'BROOKLYN') is used, the output discloses that crashes with no borough recorded (19.9–38.1% per year) are excluded.
- tr_TR11: The output does not call Brooklyn 'safer' or 'less safe' from counts alone without saying that there is no pedestrian exposure measure.
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.