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

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: From 2013 to 2025, did the risk of a motorist being killed for each mile driven in NYC go down? Use this crash data to make a chart and answer the question.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Motorist fatalities per 100,000 police-reported crashes
denominator: All police-reported crashes in that year
grouping: Calendar year, 2013–2025
chart_type: Line chart
probability: 0.45
WRITTEN ANSWER:
Motorist fatalities per 100,000 reported crashes rose from 54.0 in 2013 to 94.7 in 2025 (about 75% higher), but this is not a per-mile rate and cannot establish whether per-mile risk fell. This framing answers how the number of motorist deaths compares with the volume of reported crashes: the ratio was higher in 2025 than 2013 and surged in 2020. It is a defensible crash-based severity indicator, but it leaves risk per mile unanswered because crashes are not a measure of miles driven.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,reported_crashes,motorist_fatalities,motorist_fatalities_per_100k_crashes
2013,203742,110,53.989850
2014,206046,109,52.900809
2015,217708,95,43.636430
2016,229833,72,31.327094
2017,231007,107,46.318943
2018,231564,98,42.320913
2019,211486,82,38.773252
2020,112918,139,123.098177
2021,110558,134,121.203350
2022,103887,116,111.659784
2023,96607,123,127.319966
2024,91316,111,121.555916
2025,85546,81,94.685900

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.sql(f"SELECT MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) rows, SUM(number_of_motorist_killed) motorist_killed, SUM(number_of_persons_killed) all_killed FROM read_parquet(\"{p}\")").df().to_string(index=False)); print(duckdb.sql(f"SELECT year(crash_date) year, COUNT(*) crashes, SUM(number_of_motorist_killed) motorist_killed, COUNT(*) FILTER (WHERE number_of_motorist_killed > 0) crashes_with_motorist_fatality, SUM(number_of_persons_killed) persons_killed FROM read_parquet(\"{p}\") WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' GROUP BY 1 ORDER BY 1").df().to_string(index=False))'
# bash
python -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.sql(f"SELECT MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) row_count, SUM(number_of_motorist_killed) motorist_killed, SUM(number_of_persons_killed) all_killed FROM read_parquet(\"{p}\")").df().to_string(index=False)); print(duckdb.sql(f"SELECT year(crash_date) year, COUNT(*) crashes, SUM(number_of_motorist_killed) motorist_killed, COUNT(*) FILTER (WHERE number_of_motorist_killed > 0) crashes_with_motorist_fatality, SUM(number_of_persons_killed) persons_killed FROM read_parquet(\"{p}\") WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' GROUP BY 1 ORDER BY 1").df().to_string(index=False))'
# bash
python -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.sql(f"SELECT year(crash_date) yr, COUNT(*) crashes, SUM(number_of_motorist_killed) motorist_killed, COUNT(*) FILTER (WHERE number_of_motorist_killed > 0) fatal_crashes, SUM(number_of_persons_killed) persons_killed, MIN(crash_date) first_date, MAX(crash_date) last_date FROM read_parquet(\"{p}\") WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' GROUP BY 1 ORDER BY 1").df().to_string(index=False))'
# bash
ls -ld . data
# bash
mkdir out
# bash
ls -ld out
# bash
python - <<'PY'
import duckdb
import matplotlib.pyplot as plt
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True)
df = duckdb.sql("""
    SELECT year(crash_date) AS year,
           COUNT(*) AS reported_crashes,
           SUM(number_of_motorist_killed) AS motorist_fatalities,
           COUNT(*) FILTER (WHERE number_of_motorist_killed > 0) AS crashes_with_motorist_fatality
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY 1 ORDER BY 1
""").df()
df['motorist_fatalities'] = df['motorist_fatalities'].astype(int)
df['reported_crashes'] = df['reported_crashes'].astype(int)
df['crashes_with_motorist_fatality'] = df['crashes_with_motorist_fatality'].astype(int)
df['motorist_fatalities_per_100k_crashes'] = df['motorist_fatalities'] / df['reported_crashes'] * 100000

# Option 1: annual burden (absolute motorist deaths)
values1 = df[['year', 'motorist_fatalities']]
values1.to_csv(out / 'values_1.csv', index=False)
fig, ax = plt.subplots(figsize=(9.5, 5.4))
ax.plot(values1['year'], values1['motorist_fatalities'], marker='o', color='#176B87', linewidth=2.4)
ax.set(title='Motorists killed in NYC police-reported crashes, 2013–2025',
       xlabel='Year', ylabel='Motorist fatalities')
ax.set_xticks(df['year'])
ax.grid(axis='y', alpha=.25)
ax.spines[['top', 'right']].set_visible(False)
fig.text(.01, .01, 'Annual counts; crash data does not include vehicle-miles traveled.', fontsize=9, color='#555555')
fig.tight_layout(rect=(0, .04, 1, 1))
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Option 2: deaths normalized by number of reported crashes (not by miles driven)
values2 = df[['year', 'reported_crashes', 'motorist_fatalities', 'motorist_fatalities_per_100k_crashes']]
values2.to_csv(out / 'values_2.csv', index=False, float_format='%.6f')
fig, ax = plt.subplots(figsize=(9.5, 5.4))
ax.plot(values2['year'], values2['motorist_fatalities_per_100k_crashes'], marker='o', color='#A54824', linewidth=2.4)
ax.set(title='Motorist fatalities per 100,000 reported crashes, NYC, 2013–2025',
       xlabel='Year', ylabel='Motorist fatalities per 100,000 crashes')
ax.set_xticks(df['year'])
ax.grid(axis='y', alpha=.25)
ax.spines[['top', 'right']].set_visible(False)
fig.text(.01, .01, 'Denominator is all police-reported crashes, not vehicle-miles traveled.', fontsize=9, color='#555555')
fig.tight_layout(rect=(0, .04, 1, 1))
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)

print(df.to_string(index=False))
PY
# bash
python -c 'print("count change %",(81/110-1)*100); print("fatalities per crash change %",(94.685900/53.989850-1)*100)'
# bash
python -c 'import json, pathlib; p=pathlib.Path("out/options.json"); d=json.loads(p.read_text()); print("valid JSON; options=",len(d["options"]),"probability sum=",sum(o["probability"] for o in d["options"])); print("artifacts:",[(str(x),x.stat().st_size) for x in sorted(pathlib.Path("out").iterdir())])'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording (fewer minor crashes reported).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.