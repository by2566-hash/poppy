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
metric: Pedestrians killed in Brooklyn-reported crashes
denominator: None; annual death count
grouping: Calendar year, Brooklyn, 2013–2025
chart_type: Bar chart
probability: 0.25
WRITTEN ANSWER:
This dataset cannot establish exposure-adjusted pedestrian safety, and the annual pedestrian death count was higher in 2025 than in 2013 (39 versus 30, up 30%). This framing focuses on the most severe outcome and shows no endpoint improvement: pedestrian deaths fluctuated year to year, with 39 recorded in 2025 versus 30 in 2013. It is defensible because deaths should not be obscured within a larger injury total, but it does not describe nonfatal injuries or adjust for how much people walked.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,pedestrians_killed
2013,30.0
2014,42.0
2015,46.0
2016,20.0
2017,20.0
2018,23.0
2019,33.0
2020,17.0
2021,32.0
2022,23.0
2023,22.0
2024,31.0
2025,39.0

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.sql(f"SELECT year(crash_date) year, count(*) crashes, sum(number_of_pedestrians_injured) ped_injured, sum(number_of_pedestrians_killed) ped_killed, sum(number_of_pedestrians_injured + number_of_pedestrians_killed) ped_casualties, count(*) FILTER (WHERE number_of_pedestrians_injured + number_of_pedestrians_killed > 0) crashes_with_ped_casualty FROM read_parquet(\"{p}\") WHERE borough=\'BROOKLYN\' AND crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2026-01-01\' GROUP BY year ORDER BY year").df().to_string(index=False))'
# bash
python -c 'import duckdb; q="""SELECT year(crash_date) AS yr, count(*) AS crashes, sum(number_of_pedestrians_injured) AS ped_injured, sum(number_of_pedestrians_killed) AS ped_killed, sum(number_of_pedestrians_injured + number_of_pedestrians_killed) AS ped_casualties, count(*) FILTER (WHERE number_of_pedestrians_injured + number_of_pedestrians_killed > 0) AS crashes_with_ped_casualty FROM read_parquet(?) WHERE borough = ? AND crash_date >= make_date(2013,1,1) AND crash_date < make_date(2026,1,1) GROUP BY yr ORDER BY yr"""; print(duckdb.connect().execute(q,["data/crashes.parquet","BROOKLYN"]).df().to_string(index=False))'
# bash
ls
# bash
python - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True)
query = '''
SELECT year(crash_date) AS year,
       count(*) AS brooklyn_crashes,
       sum(number_of_pedestrians_injured) AS pedestrians_injured,
       sum(number_of_pedestrians_killed) AS pedestrians_killed,
       sum(number_of_pedestrians_injured + number_of_pedestrians_killed) AS pedestrian_casualties,
       count(*) FILTER (WHERE number_of_pedestrians_injured + number_of_pedestrians_killed > 0) AS crashes_with_pedestrian_casualty
FROM read_parquet(?)
WHERE borough = ? AND crash_date >= make_date(2013,1,1) AND crash_date < make_date(2026,1,1)
GROUP BY year ORDER BY year
'''
df = duckdb.connect().execute(query, ['data/crashes.parquet', 'BROOKLYN']).df()
df['casualty_crashes_per_1000'] = df['crashes_with_pedestrian_casualty'] / df['brooklyn_crashes'] * 1000

plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.titleweight': 'bold', 'axes.spines.top': False, 'axes.spines.right': False})
navy, blue, red, gray = '#15324b', '#1677a8', '#c43c39', '#667785'

# Option 1: annual people injured or killed
values1 = df[['year','pedestrians_injured','pedestrians_killed','pedestrian_casualties']].copy()
values1.to_csv(out/'values_1.csv', index=False)
fig, ax = plt.subplots(figsize=(10.5, 5.8), layout='constrained')
ax.plot(df.year, df.pedestrian_casualties, color=blue, linewidth=3, marker='o', markersize=5)
ax.fill_between(df.year, df.pedestrian_casualties, color=blue, alpha=.10)
ax.set_title('Pedestrian casualties in Brooklyn fell from 2013, then rose', loc='left', color=navy, fontsize=16, pad=14)
ax.text(0, 1.02, 'People injured or killed in reported crashes · annual totals', transform=ax.transAxes, fontsize=10, color=gray)
ax.set_ylabel('Pedestrians injured or killed')
ax.set_xticks(df.year)
ax.set_xticklabels(df.year.astype(str), rotation=45, ha='right')
ax.grid(axis='y', color='#d9e0e5', linewidth=.8)
ax.set_axisbelow(True)
ax.annotate(f"{int(df.iloc[0].pedestrian_casualties):,}", (df.iloc[0].year, df.iloc[0].pedestrian_casualties), xytext=(0,10), textcoords='offset points', ha='center', color=navy, fontweight='bold')
ax.annotate(f"{int(df.iloc[-1].pedestrian_casualties):,}", (df.iloc[-1].year, df.iloc[-1].pedestrian_casualties), xytext=(0,10), textcoords='offset points', ha='center', color=navy, fontweight='bold')
fig.text(.01, .005, 'Source: NYC police-reported motor vehicle crashes. Brooklyn borough records; 2013–2025. Counts do not adjust for pedestrian exposure.', fontsize=8, color=gray)
fig.savefig(out/'option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Option 2: annual pedestrian deaths
values2 = df[['year','pedestrians_killed']].copy()
values2.to_csv(out/'values_2.csv', index=False)
fig, ax = plt.subplots(figsize=(10.5, 5.8), layout='constrained')
bars = ax.bar(df.year, df.pedestrians_killed, color=red, width=.72)
ax.set_title('Brooklyn pedestrian deaths were higher in 2025 than in 2013', loc='left', color=navy, fontsize=16, pad=14)
ax.text(0, 1.02, 'Pedestrians killed in reported crashes · annual counts', transform=ax.transAxes, fontsize=10, color=gray)
ax.set_ylabel('Pedestrians killed')
ax.set_xticks(df.year)
ax.set_xticklabels(df.year.astype(str), rotation=45, ha='right')
ax.set_ylim(0, max(df.pedestrians_killed)*1.22)
ax.grid(axis='y', color='#d9e0e5', linewidth=.8)
ax.set_axisbelow(True)
for i in [0, len(df)-1]:
    b = bars[i]
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+.7, f'{int(b.get_height())}', ha='center', va='bottom', color=navy, fontweight='bold')
fig.text(.01, .005, 'Source: NYC police-reported motor vehicle crashes. Brooklyn borough records; 2013–2025. Counts do not adjust for pedestrian exposure.', fontsize=8, color=gray)
fig.savefig(out/'option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Option 3: casualty-involved crashes per 1,000 reported Brooklyn crashes
values3 = df[['year','brooklyn_crashes','crashes_with_pedestrian_casualty','casualty_crashes_per_1000']].copy()
values3.to_csv(out/'values_3.csv', index=False)
fig, ax = plt.subplots(figsize=(10.5, 5.8), layout='constrained')
ax.plot(df.year, df.casualty_crashes_per_1000, color=navy, linewidth=3, marker='o', markersize=5)
ax.set_title('Pedestrian-casualty crashes became a larger share of Brooklyn crashes', loc='left', color=navy, fontsize=15, pad=14)
ax.text(0, 1.02, 'Crashes with ≥1 pedestrian injured or killed · per 1,000 reported Brooklyn crashes', transform=ax.transAxes, fontsize=9.5, color=gray)
ax.set_ylabel('Casualty-involved crashes per 1,000 crashes')
ax.set_xticks(df.year)
ax.set_xticklabels(df.year.astype(str), rotation=45, ha='right')
ax.grid(axis='y', color='#d9e0e5', linewidth=.8)
ax.set_axisbelow(True)
ax.annotate(f"{df.iloc[0].casualty_crashes_per_1000:.1f}", (df.iloc[0].year, df.iloc[0].casualty_crashes_per_1000), xytext=(0,10), textcoords='offset points', ha='center', color=navy, fontweight='bold')
ax.annotate(f"{df.iloc[-1].casualty_crashes_per_1000:.1f}", (df.iloc[-1].year, df.iloc[-1].casualty_crashes_per_1000), xytext=(0,10), textcoords='offset points', ha='center', color=navy, fontweight='bold')
fig.text(.01, .005, 'Source: NYC police-reported motor vehicle crashes. Brooklyn borough records; 2013–2025. Share of crash reports, not risk per pedestrian trip.', fontsize=8, color=gray)
fig.savefig(out/'option_3.png', dpi=180, bbox_inches='tight')
plt.close(fig)

print(df.to_string(index=False, formatters={'casualty_crashes_per_1000': '{:.3f}'.format}))
PY
# bash
python -c 'import json; d=json.load(open("out/options.json")); print("valid JSON; option ids:", [x["id"] for x in d["options"]], "; probability sum:", sum(x["probability"] for x in d["options"]))'

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