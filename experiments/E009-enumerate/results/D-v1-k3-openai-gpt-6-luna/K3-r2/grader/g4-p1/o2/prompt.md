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

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts fall sharply in 2020 (TR01): a per-reported-crash rate or a pooled count COMPARED ACROSS YEARS spanning 2020 needs a caveat; a comparison between groups within one pooled window (e.g. day vs night) does not (decided 2026-11-04).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: How do motorist and cyclist deaths compare year by year in NYC, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Annual deaths among motorists and cyclists
denominator: None; counts of reported deaths
grouping: Year, with separate series for motorists and cyclists
chart_type: Two-series line chart
probability: 0.34
WRITTEN ANSWER:
Motorist deaths peaked at 139 in 2020 and were lowest at 72 in 2016, while cyclist deaths peaked at 31 in both 2019 and 2023 and were lowest at 10 in 2018.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,cyclist_deaths
2013,110,11
2014,109,20
2015,95,15
2016,72,18
2017,107,27
2018,98,10
2019,82,31
2020,139,29
2021,134,19
2022,116,19
2023,123,31
2024,111,24
2025,81,23

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c 'import duckdb; print(duckdb.__version__)'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute(f"SELECT MIN(crash_date), MAX(crash_date), COUNT(*) FROM read_parquet(\"{p}\")").fetchdf().to_string(index=False)); print(c.execute(f"SELECT YEAR(crash_date) year, SUM(COALESCE(number_of_motorist_killed,0)) motorist_deaths, SUM(COALESCE(number_of_cyclist_killed,0)) cyclist_deaths, SUM(COALESCE(number_of_persons_killed,0)) total_person_deaths, COUNT(*) crashes FROM read_parquet(\"{p}\") WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1").fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute(f"SELECT YEAR(crash_date) AS crash_year, SUM(COALESCE(number_of_motorist_killed,0)) AS motorist_deaths, SUM(COALESCE(number_of_cyclist_killed,0)) AS cyclist_deaths, SUM(COALESCE(number_of_persons_killed,0)) AS total_person_deaths, COUNT(*) AS crashes FROM read_parquet(\"{p}\") WHERE crash_date >= DATE '"'"'2013-01-01'"'"' AND crash_date < DATE '"'"'2026-01-01'"'"' GROUP BY 1 ORDER BY 1").fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); print(c.execute("SELECT YEAR(crash_date) AS crash_year, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date, SUM(COALESCE(number_of_motorist_killed,0)) AS motorist_deaths, SUM(COALESCE(number_of_cyclist_killed,0)) AS cyclist_deaths FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= DATE '"'"'2013-01-01'"'"' AND crash_date < DATE '"'"'2026-01-01'"'"' GROUP BY 1 ORDER BY 1").fetchdf().to_string(index=False))'
# bash
python3 _make_crash_options.py
# bash
python3 _make_crash_options.py
# bash
python3 -c 'import json, pathlib; p=pathlib.Path("out/options.json"); o=json.loads(p.read_text()); print("options",len(o["options"]),"probability_sum",sum(x["probability"] for x in o["options"])); print("files", all(pathlib.Path(f"out/{name}").exists() for name in ["option_1.png","option_2.png","option_3.png","values_1.csv","values_2.csv","values_3.csv"]))'

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