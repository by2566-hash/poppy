You are grading ONE output of a data-analysis agent against a written standard. The chart is attached as an image.
Judge from the materials below only. Do not fix anything, do not redo the analysis. For each item answer PASS or FAIL
(NA if the item does not apply to this output) and quote the sentence, number or chart element that decides it.
Be strict: a limitation that matters but is not stated is a FAIL on the item that asks for it.
If the QUESTION TYPE is "insufficient", the data cannot answer the question as asked; the appropriate output states that
(required_statement) and shows a measure the data does support. Do not FAIL c1 or c2 merely because the measure is not the
one the question named (e.g. not per mile); FAIL them only if the output pretends to answer the unanswerable question.

QUESTION ASKED: A2
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Crashes with at least one person killed per 100,000 complete-record crashes
denominator: Crashes with nonmissing person-injury and person-killed counts
grouping: Night (8pm–5:59am) vs day (6am–7:59pm)
chart_type: Dot plot
probability: 0.36
WRITTEN ANSWER:
Among complete records, 291.6 of every 100,000 nighttime crashes involved at least one death, versus 108.4 daytime crashes. This compares fatal outcomes among reported crashes, not risk per trip, which the data cannot determine without traffic exposure.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
period,fatal_crashes,complete_crashes,fatal_crashes_per_100k
Night (8pm–5:59am),1622,556333,291.552002
Day (6am–7:59pm),1847,1703935,108.396154

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
- tr_TR08: The analysis window is 2013–2025, or 2026 rows (killed count NULL in 87.8% of May-2026 and 100% of June-2026 rows) are excluded or handled, and sums are NULL-safe.
- tr_NIGHTDEF: The definition of 'night' (hours) is stated.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.