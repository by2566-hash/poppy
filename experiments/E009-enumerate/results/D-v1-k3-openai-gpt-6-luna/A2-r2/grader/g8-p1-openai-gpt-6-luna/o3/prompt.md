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
metric: People injured plus people killed per 100 complete-record crashes
denominator: Crashes with nonmissing person-injury and person-killed counts
grouping: Night (8pm–5:59am) vs day (6am–7:59pm)
chart_type: Stacked bar chart
probability: 0.3
WRITTEN ANSWER:
Complete records show 40.65 people injured or killed per 100 nighttime crashes, compared with 31.00 per 100 daytime crashes. This is the reported casualty burden per crash and cannot establish risk per trip without traffic-exposure data.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
period,complete_crashes,injured_people,killed_people,injuries_per_100_crashes,deaths_per_100_crashes,casualties_per_100_crashes
Night (8pm–5:59am),556333,224444.000000,1719.000000,40.343463,0.308988,40.652451
Day (6am–7:59pm),1703935,526264.000000,1898.000000,30.885216,0.111389,30.996605

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT COUNT(*) rows, MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE crash_time IS NULL) null_time FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT CAST(crash_time AS VARCHAR) hour, COUNT(*) n FROM read_parquet(?) GROUP BY 1 ORDER BY n DESC LIMIT 12", [p]).fetchdf().to_string(index=False))'
# bash
python -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT COUNT(*) AS n_rows, MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE crash_time IS NULL) AS null_time FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT CAST(crash_time AS VARCHAR) AS hour, COUNT(*) AS n FROM read_parquet(?) GROUP BY 1 ORDER BY n DESC LIMIT 12", [p]).fetchdf().to_string(index=False))'
# bash
python -c 'import duckdb; c=duckdb.connect(); q="""WITH base AS (SELECT *, CASE WHEN hour(crash_time) >= 20 OR hour(crash_time) < 6 THEN '\''Night (8pm–5:59am)'\'' ELSE '\''Day (6am–7:59pm)'\'' END AS period FROM read_parquet('\''data/crashes.parquet'\'')), s AS (SELECT period, COUNT(*) crashes, COUNT(*) FILTER (WHERE coalesce(number_of_persons_injured,0)>0 OR coalesce(number_of_persons_killed,0)>0) casualty_crashes, SUM(coalesce(number_of_persons_injured,0)) injured, SUM(coalesce(number_of_persons_killed,0)) killed FROM base GROUP BY period) SELECT *, crashes / CASE WHEN period LIKE '\''Night%'\'' THEN 10.0 ELSE 14.0 END AS crashes_per_clock_hour, casualty_crashes*100.0/crashes AS casualty_crash_pct, (injured+killed)*100.0/crashes AS casualties_per_100_crashes FROM s ORDER BY period"""; print(c.execute(q).fetchdf().to_string(index=False)); print(c.execute("SELECT count(distinct crash_date), min(crash_date), max(crash_date), count(*) FILTER (WHERE number_of_persons_injured IS NULL), count(*) FILTER (WHERE number_of_persons_killed IS NULL) FROM read_parquet('\''data/crashes.parquet'\'')").fetchdf().to_string(index=False))'
# bash
python out/build_charts.py
# bash
python out/build_charts.py
# bash
python -c 'import json, pathlib; p=pathlib.Path("out"); d=json.loads((p/"options.json").read_text()); opts=d["options"]; assert len(opts)==3; assert abs(sum(o["probability"] for o in opts)-1)<1e-9; assert all((p/f"option_{i}.png").is_file() and (p/f"values_{i}.csv").is_file() for i in (1,2,3)); print("JSON valid; probabilities sum to", sum(o["probability"] for o in opts)); print("Output files:", ", ".join(sorted(x.name for x in p.iterdir())))'

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