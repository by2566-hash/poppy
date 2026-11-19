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
metric: Share of reported crashes with any injury or any fatality
denominator: All reported crashes with a recorded crash time in the corresponding day/night period
grouping: Day versus night; injury and fatality outcomes shown separately
chart_type: Two-panel bar chart of percentages
probability: 0.7
WRITTEN ANSWER:
Night crashes were more severe per reported crash: 28.1% involved an injury versus 23.0% by day, and 0.268% involved a death versus 0.099%, but missing traffic exposure prevents a per-trip danger conclusion. This framing answers whether a reported crash is more likely to involve injury or death at night; the chart shows higher shares for both outcomes at night, by 5.1 percentage points for injury and 2.7 times the fatal-crash share. It is defensible as a comparison of crash severity conditional on a crash being reported, but it leaves unanswered the chance of a crash per trip, mile, or person out at night.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
period,reported_crashes,crashes_with_injury,crashes_with_fatality,injury_crash_pct,fatal_crash_pct
Day (7am–6:59pm),1543368,354903,1522,22.995358,0.098615
Night (7pm–6:59am),725819,203700,1947,28.064848,0.268249

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"
# bash
python -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(f\"select count(*) n, min(crash_date), max(crash_date), count(*) filter(where crash_time is null) null_time, count(*) filter(where number_of_persons_injured>0) injury_crashes, count(*) filter(where number_of_persons_killed>0) fatal_crashes from read_parquet('{p}')\").fetchdf().to_string(index=False)); print(c.execute(f\"select strftime(crash_time, '%H') hr, count(*) n, sum(number_of_persons_injured) injured, sum(number_of_persons_killed) killed from read_parquet('{p}') where crash_time is not null group by 1 order by 1\").fetchdf().to_string(index=False))"
# bash
python -c "import duckdb; c=duckdb.connect(); q=\"with x as (select extract(hour from crash_time)::int h, number_of_persons_injured i, number_of_persons_killed k from read_parquet('data/crashes.parquet')) select case when h between 7 and 18 then 'Day (7am–6:59pm)' else 'Night (7pm–6:59am)' end period, count(*) crashes, sum(case when i>0 then 1 else 0 end) injury_crashes, sum(case when k>0 then 1 else 0 end) fatal_crashes, sum(i) injured_people, sum(k) killed_people, round(100.0*sum(case when i>0 then 1 else 0 end)/count(*),3) injury_crash_pct, round(100.0*sum(case when k>0 then 1 else 0 end)/count(*),4) fatal_crash_pct, round(1.0*sum(i)/count(*),4) injured_people_per_crash, round(1.0*sum(k)/count(*),5) killed_people_per_crash from x group by 1 order by 1\"; print(c.execute(q).fetchdf().to_string(index=False))"
# bash
python out/generate.py
# bash
python out/generate.py && python -c "import json, pandas as pd; o=json.load(open('out/options.json')); a=pd.read_csv('out/values_1.csv'); b=pd.read_csv('out/values_2.csv'); assert abs(sum(x['probability'] for x in o['options'])-1)<1e-12; assert len(a)==len(b)==2; assert list(a['reported_crashes'])==list(b['reported_crashes']); assert round(b.loc[1,'injury_crash_pct'],3)==28.065 and round(b.loc[0,'injury_crash_pct'],3)==22.995; print('JSON valid; probabilities sum to', sum(x['probability'] for x in o['options'])); print('Crash totals and outcome percentages match plotted data.')"

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