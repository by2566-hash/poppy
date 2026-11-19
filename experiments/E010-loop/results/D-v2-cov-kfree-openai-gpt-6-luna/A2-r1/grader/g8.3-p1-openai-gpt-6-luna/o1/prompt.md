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
metric: Police-reported crash frequency
denominator: Observed clock-hours in each equal-length 12-hour period
grouping: Day (7 a.m.–6:59 p.m.) vs night (7 p.m.–6:59 a.m.)
chart_type: Two-bar comparison
probability: 0.55
WRITTEN ANSWER:
NYC recorded 25.5 police-reported crashes per clock-hour by day versus 12.0 at night in 2013–2025, so reported crash frequency was higher by day. This addresses whether police-reported crashes occur more frequently at night by comparing the mean count per clock-hour, with equal 12-hour day and night windows. The chart shows the per-hour crash frequency in each window, a defensible count-based proxy for danger when no traffic-exposure measure is available. It does not answer whether an individual trip or road user faces greater risk, because the file has no traffic volume, travel distance, or road-user exposure; it also does not compare injury severity. Rows excluded are all rows from the partial coverage years 2012 (100,545 rows, 4.43% of the file) and 2026 (36,424 rows, 1.61% of the file); no rows are excluded for missing crash date/time.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
period,crash_rows,observed_dates,clock_hours,crashes_per_clock_hour
Day (7 a.m.–6:59 p.m.),1450687,4748,56976,25.461370
Night (7 p.m.–6:59 a.m.),681531,4748,56976,11.961721

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT count(*) n, min(crash_date), max(crash_date), count(*) FILTER (WHERE crash_time IS NULL) null_time FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT strftime(crash_time, '%H') hr, count(*) n, sum(number_of_persons_injured) inj, sum(number_of_persons_killed) deaths FROM read_parquet(?) GROUP BY 1 ORDER BY 1", [p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; qs=["SELECT EXTRACT(HOUR FROM crash_time) hr, count(*) n, sum(number_of_persons_injured) inj, sum(number_of_persons_killed) deaths FROM read_parquet(?) GROUP BY 1 ORDER BY 1", "SELECT EXTRACT(YEAR FROM crash_date) yr, min(crash_date), max(crash_date), count(distinct crash_date) dates, count(*) n, count(*) FILTER (WHERE number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL) missing_severity FROM read_parquet(?) GROUP BY 1 ORDER BY 1", "SELECT count(*) FILTER (WHERE number_of_persons_injured IS NULL) null_inj, count(*) FILTER (WHERE number_of_persons_killed IS NULL) null_killed, count(*) FILTER (WHERE crash_date IS NULL) null_date, count(DISTINCT crash_date) dates FROM read_parquet(?)"]; [print(c.execute(q,[p]).fetchdf().to_string(index=False)) for q in qs]'
# bash
python3 out/generate_options.py
# bash
python3 out/generate_options.py
# bash
python3 out/generate_options.py
# bash
python3 -c 'import json, pandas as pd; from pathlib import Path; o=json.loads(Path("out/options.json").read_text()); assert abs(sum(x["probability"] for x in o["options"])-1)<1e-9; a=pd.read_csv("out/values_1.csv"); b=pd.read_csv("out/values_2.csv"); assert len(a)==len(b)==2; assert (a.clock_hours==56976).all(); assert abs(a.loc[0,"crashes_per_clock_hour"]-25.461370)<1e-6; assert abs(a.loc[1,"crashes_per_clock_hour"]-11.961721)<1e-6; assert abs(b.loc[0,"injury_or_fatal_share_pct"]-22.988295)<1e-6; assert abs(b.loc[1,"injury_or_fatal_share_pct"]-28.215919)<1e-6; print("JSON, option probabilities, and plotted-value checks passed")'
# bash
python3 out/generate_options.py
# bash
python3 -c 'import json, re; from pathlib import Path; d=json.loads(Path("out/options.json").read_text()); assert abs(sum(x["probability"] for x in d["options"])-1)<1e-9; [print(i["id"], len(re.findall(r"[.!?](?:\s|$)", i["interpretation"])), "sentences") for i in d["options"]]; assert all(3 <= len(re.findall(r"[.!?](?:\s|$)", i["interpretation"])) <= 4 for i in d["options"]); print("options.json validation passed")'

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