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
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Annual number of pedestrians injured
denominator: None (annual count)
grouping: Crash year in Brooklyn, 2013–2025
chart_type: Line chart
probability: 0.4
WRITTEN ANSWER:
Whether pedestrian safety per trip improved cannot be determined because the data has no pedestrian-exposure measure; as a reported-outcome indicator, annual pedestrian injuries fell from 3,641 in 2013 to 2,835 in 2025 (-22.1%), after reaching a low of 1,781 in 2020 and then rising.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrian_injuries
2013,3641
2014,3349
2015,3029
2016,2917
2017,2663
2018,2785
2019,2700
2020,1781
2021,1905
2022,2275
2023,2385
2024,2645
2025,2835

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print("rows", c.execute("SELECT count(*) FROM read_parquet(?)", [p]).fetchone()[0])'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("SELECT min(crash_date), max(crash_date), count(*) FILTER (WHERE borough = '\''BROOKLYN'\'') FROM read_parquet(?)",[p]).fetchall()); print(c.execute("SELECT year(crash_date) y, count(*) crashes, sum(coalesce(number_of_pedestrians_injured,0)) ped_injured, sum(coalesce(number_of_pedestrians_killed,0)) ped_killed, sum(coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0)) ped_casualties FROM read_parquet(?) WHERE borough = '\''BROOKLYN'\'' GROUP BY y ORDER BY y",[p]).fetchdf().to_string(index=False))'
# bash
python3 - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import json

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
annual = con.execute("""
    SELECT year(crash_date) AS year,
           count(*) AS brooklyn_reported_crashes,
           sum(coalesce(number_of_pedestrians_injured, 0))::BIGINT AS pedestrian_injuries,
           sum(coalesce(number_of_pedestrians_killed, 0))::BIGINT AS pedestrian_deaths,
           sum(coalesce(number_of_pedestrians_injured, 0) + coalesce(number_of_pedestrians_killed, 0))::BIGINT AS pedestrian_casualties
    FROM read_parquet('data/crashes.parquet')
    WHERE borough = 'BROOKLYN'
      AND crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
""").fetchdf()
assert annual.year.tolist() == list(range(2013, 2026)), annual.year.tolist()
annual['casualties_per_1000_crashes'] = annual.pedestrian_casualties / annual.brooklyn_reported_crashes * 1000

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.titleweight': 'bold',
    'axes.titlesize': 17,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
})
navy = '#18324b'
blue = '#176b87'
red = '#bd4b3b'
gray = '#65727e'

# Option 1: annual pedestrian injuries (count)
d1 = annual[['year', 'pedestrian_injuries']].copy()
d1.to_csv(out / 'values_1.csv', index=False)
fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.plot(d1.year, d1.pedestrian_injuries, color=blue, linewidth=2.8, marker='o', markersize=5)
ax.fill_between(d1.year, d1.pedestrian_injuries, color=blue, alpha=.10)
ax.set_title('Pedestrian injuries in Brooklyn fell from 2013—but rose after 2020', loc='left', color=navy, pad=15)
ax.set_ylabel('Pedestrians injured (people)')
ax.set_xlabel('Crash year')
ax.set_xticks(d1.year)
ax.tick_params(axis='x', rotation=0)
ax.grid(axis='y', color='#d9e0e5', linewidth=.8)
ax.set_axisbelow(True)
for idx in [0, len(d1)-1]:
    row = d1.iloc[idx]
    ax.annotate(f"{int(row.pedestrian_injuries):,}", (row.year, row.pedestrian_injuries), xytext=(0, 11), textcoords='offset points', ha='center', fontsize=10, fontweight='bold', color=navy)
ax.text(.01, -.22, 'Source: NYC police-reported motor vehicle crashes, Brooklyn, 2013–2025. Counts do not account for pedestrian exposure.', transform=ax.transAxes, fontsize=9, color=gray)
ax.margins(x=.04, y=.16)
fig.tight_layout()
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Option 2: annual pedestrian deaths (count)
d2 = annual[['year', 'pedestrian_deaths']].copy()
d2.to_csv(out / 'values_2.csv', index=False)
fig, ax = plt.subplots(figsize=(10.5, 5.8))
bars = ax.bar(d2.year, d2.pedestrian_deaths, color=red, width=.68)
ax.set_title('Pedestrian deaths in Brooklyn: 39 in 2025, up from 30 in 2013', loc='left', color=navy, pad=15)
ax.set_ylabel('Pedestrians killed (people)')
ax.set_xlabel('Crash year')
ax.set_xticks(d2.year)
ax.grid(axis='y', color='#d9e0e5', linewidth=.8)
ax.set_axisbelow(True)
for bar, value in zip(bars, d2.pedestrian_deaths):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + .7, f'{int(value)}', ha='center', va='bottom', fontsize=9, color=navy)
ax.text(.01, -.22, 'Source: NYC police-reported motor vehicle crashes, Brooklyn, 2013–2025. Counts do not account for pedestrian exposure.', transform=ax.transAxes, fontsize=9, color=gray)
ax.set_ylim(0, max(d2.pedestrian_deaths) * 1.22)
fig.tight_layout()
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Option 3: combined pedestrian injuries and deaths per 1,000 reported Brooklyn crashes
d3 = annual[['year', 'pedestrian_casualties', 'brooklyn_reported_crashes', 'casualties_per_1000_crashes']].copy()
d3.to_csv(out / 'values_3.csv', index=False, float_format='%.4f')
fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.plot(d3.year, d3.casualties_per_1000_crashes, color=navy, linewidth=2.8, marker='o', markersize=5)
ax.fill_between(d3.year, d3.casualties_per_1000_crashes, color=navy, alpha=.09)
ax.set_title('Pedestrian casualties per 1,000 Brooklyn crashes are higher than in 2013', loc='left', color=navy, pad=15)
ax.set_ylabel('Pedestrian injuries + deaths per 1,000 reported crashes')
ax.set_xlabel('Crash year')
ax.set_xticks(d3.year)
ax.grid(axis='y', color='#d9e0e5', linewidth=.8)
ax.set_axisbelow(True)
for idx in [0, len(d3)-1]:
    row = d3.iloc[idx]
    ax.annotate(f"{row.casualties_per_1000_crashes:.1f}", (row.year, row.casualties_per_1000_crashes), xytext=(0, 11), textcoords='offset points', ha='center', fontsize=10, fontweight='bold', color=navy)
ax.text(.01, -.22, 'Source: NYC police-reported crashes, Brooklyn, 2013–2025. This is a per-crash measure, not risk per pedestrian trip.', transform=ax.transAxes, fontsize=9, color=gray)
ax.margins(x=.04, y=.16)
fig.tight_layout()
fig.savefig(out / 'option_3.png', dpi=180, bbox_inches='tight')
plt.close(fig)

inj13, inj25 = int(d1.iloc[0].pedestrian_injuries), int(d1.iloc[-1].pedestrian_injuries)
dth13, dth25 = int(d2.iloc[0].pedestrian_deaths), int(d2.iloc[-1].pedestrian_deaths)
rate13, rate25 = float(d3.iloc[0].casualties_per_1000_crashes), float(d3.iloc[-1].casualties_per_1000_crashes)
options = {
    'options': [
        {
            'id': 1,
            'metric': 'Annual number of pedestrians injured',
            'denominator': 'None (annual count)',
            'grouping': 'Crash year in Brooklyn, 2013–2025',
            'chart_type': 'Line chart',
            'reason': 'A count directly communicates how many reported pedestrian injury casualties occurred each year.',
            'probability': 0.4,
            'answer': f"Whether pedestrian safety per trip improved cannot be determined because the data has no pedestrian-exposure measure; as a reported-outcome indicator, annual pedestrian injuries fell from {inj13:,} in 2013 to {inj25:,} in 2025 ({(inj25/inj13-1)*100:.1f}%), after reaching a low of {int(d1.pedestrian_injuries.min()):,} in {int(d1.loc[d1.pedestrian_injuries.idxmin(), 'year'])} and then rising."
        },
        {
            'id': 2,
            'metric': 'Annual number of pedestrians killed',
            'denominator': 'None (annual count)',
            'grouping': 'Crash year in Brooklyn, 2013–2025',
            'chart_type': 'Bar chart',
            'reason': 'Showing deaths separately makes the most severe pedestrian outcome visible without combining it with nonfatal injuries.',
            'probability': 0.3,
            'answer': f"Whether pedestrian safety per trip improved cannot be determined because the data has no pedestrian-exposure measure; reported pedestrian deaths rose from {dth13} in 2013 to {dth25} in 2025 ({(dth25/dth13-1)*100:.1f}%), with substantial year-to-year variation."
        },
        {
            'id': 3,
            'metric': 'Pedestrian injuries plus deaths per 1,000 reported crashes',
            'denominator': 'All police-reported Brooklyn crashes in the same year, scaled to 1,000',
            'grouping': 'Crash year in Brooklyn, 2013–2025',
            'chart_type': 'Line chart',
            'reason': 'Normalizing combined pedestrian casualties by total crashes helps distinguish casualty burden from changes in overall crash volume.',
            'probability': 0.3,
            'answer': f"Whether pedestrian safety per trip improved cannot be determined because the data has no pedestrian-exposure measure; the per-crash indicator increased from {rate13:.1f} pedestrian injuries or deaths per 1,000 reported crashes in 2013 to {rate25:.1f} in 2025 ({(rate25/rate13-1)*100:.1f}%)."
        }
    ]
}
(out / 'options.json').write_text(json.dumps(options, indent=2) + '\n')
print(annual.to_string(index=False))
print('\nEnd-point changes: injuries %.1f%%; deaths %.1f%%; casualties per 1,000 crashes %.1f%%' % ((inj25/inj13-1)*100, (dth25/dth13-1)*100, (rate25/rate13-1)*100))
print('Wrote options and chart/value files under out/.')
PY
# bash
python3 - <<'PY'
import json
from pathlib import Path
p = Path('out')
d = json.loads((p / 'options.json').read_text())
assert len(d['options']) == 3
assert abs(sum(o['probability'] for o in d['options']) - 1) < 1e-9
for i in (1, 2, 3):
    assert (p / f'option_{i}.png').is_file()
    assert (p / f'values_{i}.csv').is_file()
print('Valid JSON; three options; probabilities sum to', sum(o['probability'] for o in d['options']))
print('All 3 chart and CSV pairs exist.')
PY

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
- tr_TR01: If a per-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording.
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.