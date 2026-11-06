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
- Qualifications (reported, recorded in this dataset) count when they are in the WRITTEN ANSWER or the DECLARED FRAMING; text
  that appears only inside the chart image (title, footnote, source note) does not satisfy an item on its own. The official-count
  part of unsupported_claim follows the same test as TR07.

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Is it more dangerous to be on NYC's streets at night? Make a chart and say what you conclude for a news report.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Share of crashes involving at least one reported injury
denominator: Crashes with a nonmissing number_of_persons_injured value
grouping: Day (06:00–19:59) versus night (20:00–05:59)
chart_type: Bar chart
probability: 0.42
WRITTEN ANSWER:
Among crashes with known injury counts, 28.3% at night involved an injury, compared with 23.4% by day; this is conditional on a crash, not personal nighttime risk. This addresses whether a police-reported crash is more likely to involve injury at night, and the chart shows a higher injury-involved share at night. It is a defensible severity comparison because its denominator is crashes rather than time or road users, but it leaves unanswered how likely people are to be involved in a crash while traveling at each time.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
period,crashes_with_known_injury_count,crashes_with_injury,injury_crash_percent
Day,1710168,400420,23.414074
Night,559001,158183,28.297445

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && git status --short
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; con=duckdb.connect(); print(con.execute(f"SELECT count(*) n, min(crash_date), max(crash_date), count(*) FILTER (WHERE crash_time IS NULL) missing_time, count(*) FILTER (WHERE number_of_persons_injured IS NULL) missing_injured FROM read_parquet('\''{p}'\'')").fetchdf().to_string(index=False)); print(con.execute(f"SELECT extract(hour from crash_time) hr, count(*) n FROM read_parquet('\''{p}'\'') GROUP BY 1 ORDER BY 1").fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q=f"""WITH base AS (SELECT *, EXTRACT(hour FROM crash_time) h FROM read_parquet('\''{p}'\'')), tagged AS (SELECT *, CASE WHEN h >= 20 OR h < 6 THEN '\''Night'\'' ELSE '\''Day'\'' END period FROM base) SELECT period, COUNT(*) crashes, SUM(number_of_persons_injured) injured, SUM(number_of_persons_killed) killed, COUNT(*) FILTER (WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0) casualty_crashes, COUNT(*) FILTER (WHERE number_of_persons_killed > 0) fatal_crashes, COUNT(*) FILTER (WHERE number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL) incomplete, AVG(number_of_persons_injured) avg_injured, AVG(number_of_persons_killed) avg_killed, AVG(number_of_persons_injured + number_of_persons_killed) avg_casualties FROM tagged GROUP BY period ORDER BY period"""; print(c.execute(q).fetchdf().to_string(index=False)); print(c.execute(f"SELECT COUNT(DISTINCT crash_date) dates, MIN(crash_date), MAX(crash_date) FROM read_parquet('\''{p}'\'')").fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q=f"""WITH x AS (SELECT *, EXTRACT(hour FROM crash_time) h FROM read_parquet('\''{p}'\'')), y AS (SELECT *, CASE WHEN h >=20 OR h<6 THEN '\''Night'\'' ELSE '\''Day'\'' END period FROM x) SELECT period, COUNT(*) n, COUNT(number_of_persons_injured) known_injury, COUNT(number_of_persons_killed) known_killed, COUNT(*) FILTER (WHERE number_of_persons_injured>0) injury_crashes, COUNT(*) FILTER (WHERE number_of_persons_killed>0) fatal_crashes FROM y GROUP BY period ORDER BY period"""; print(c.execute(q).fetchdf().to_string(index=False)); print(c.execute(f"SELECT COUNT(DISTINCT crash_date) FROM read_parquet('\''{p}'\'')").fetchone()[0])'
# bash
ls . && mkdir -p out
# bash
python3 out/build_options.py
# bash
python3 -c 'import json, pathlib, pandas as pd; o=pathlib.Path("out"); opts=json.loads((o/"options.json").read_text())["options"]; assert len(opts)==3 and abs(sum(x["probability"] for x in opts)-1)<1e-9; assert all((o/f"option_{i}.png").stat().st_size>0 and (o/f"values_{i}.csv").stat().st_size>0 for i in (1,2,3)); a=pd.read_csv(o/"values_1.csv").set_index("period"); b=pd.read_csv(o/"values_2.csv").set_index("period"); c=pd.read_csv(o/"values_3.csv").set_index("period"); assert round(a.loc["Day","crashes_per_clock_hour"],1)==24.0 and round(a.loc["Night","crashes_per_clock_hour"],1)==11.0; assert round(b.loc["Day","injury_crash_percent"],1)==23.4 and round(b.loc["Night","injury_crash_percent"],1)==28.3; assert round(c.loc["Day","fatal_crashes_per_1000"],2)==1.08 and round(c.loc["Night","fatal_crashes_per_1000"],2)==2.92; print("Validated JSON, probability sum, chart/value files, and plotted answer values."); print("Files:", ", ".join(sorted(p.name for p in o.iterdir())))'

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