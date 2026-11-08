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
metric: Annual counts of pedestrians injured and pedestrians killed in police-reported crashes assigned to Brooklyn
denominator: None; absolute counts
grouping: Calendar year, 2013–2025
chart_type: Two-panel line chart
probability: 0.65
WRITTEN ANSWER:
From 2013 to 2025, recorded pedestrian injuries fell 22.1% (3,641 to 2,835) while deaths rose 30.0% (30 to 39), so the data show mixed changes in harm but cannot establish whether risk per pedestrian improved. This framing answers how the annual human toll changed: injuries were lower in 2025 than 2013, but deaths were higher, with both series fluctuating over time. Separate panels keep these distinct outcomes legible, making this a direct measure of reported harm. It does not show harm per walking trip or the causes of the trend, and crashes with an unreported borough are not included.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrians_injured,pedestrians_killed
2013,3641,30
2014,3349,42
2015,3029,46
2016,2917,20
2017,2663,20
2018,2785,23
2019,2700,33
2020,1781,17
2021,1905,32
2022,2275,23
2023,2385,22
2024,2645,31
2025,2835,39

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"select min(crash_date), max(crash_date), count(*), count(distinct year(crash_date)) from read_parquet('{p}')\").fetchall()); print(duckdb.sql(f\"select year(crash_date) y, count(*) crashes, sum(number_of_pedestrians_injured) ped_injured, sum(number_of_pedestrians_killed) ped_killed, sum(case when number_of_pedestrians_injured>0 or number_of_pedestrians_killed>0 then 1 else 0 end) ped_involved_crashes from read_parquet('{p}') where upper(borough)='BROOKLYN' group by y order by y\").df().to_string(index=False))"
# bash
mkdir -p out
# bash
python3 - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

con = duckdb.connect()
data = con.execute("""
    SELECT year(crash_date) AS year,
           SUM(number_of_pedestrians_injured) AS pedestrians_injured,
           SUM(number_of_pedestrians_killed) AS pedestrians_killed,
           SUM(CASE WHEN number_of_pedestrians_injured > 0
                         OR number_of_pedestrians_killed > 0 THEN 1 ELSE 0 END)
               AS crashes_with_pedestrian_harm
    FROM read_parquet('data/crashes.parquet')
    WHERE upper(borough) = 'BROOKLYN'
      AND year(crash_date) BETWEEN 2013 AND 2025
    GROUP BY year
    ORDER BY year
""").df()
data['year'] = data['year'].astype(int)
assert data['year'].tolist() == list(range(2013, 2026)), data

plt.rcParams.update({'font.family':'DejaVu Sans', 'axes.titleweight':'bold'})
navy = '#15324B'
blue = '#2676A5'
red = '#C84A3A'
gray = '#61717D'

# Option 1: separate scales make the distinct magnitude of injury and fatality counts legible.
fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.2), sharex=True)
fig.suptitle('Pedestrian harm in Brooklyn has shifted since 2013', x=0.08, y=0.985,
             ha='left', fontsize=18, fontweight='bold', color=navy)
series = [
    ('pedestrians_injured', 'Pedestrians injured', blue),
    ('pedestrians_killed', 'Pedestrians killed', red),
]
for ax, (col, label, color) in zip(axes, series):
    vals = data[col]
    ax.plot(data['year'], vals, color=color, linewidth=2.8, marker='o', markersize=5)
    ax.scatter([2013, 2025], [int(vals.iloc[0]), int(vals.iloc[-1])], color=color, s=55, zorder=3)
    ax.set_ylabel(f'{label}\n(per year)', color=navy, fontsize=10)
    ax.grid(axis='y', color='#DCE3E8', linewidth=0.8)
    ax.spines[['top','right','left']].set_visible(False)
    ax.spines['bottom'].set_color('#C7D0D7')
    ax.tick_params(axis='y', length=0, colors=gray)
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    ax.annotate(f"{int(vals.iloc[0]):,}", (2013, vals.iloc[0]), xytext=(5, 8),
                textcoords='offset points', color=color, fontsize=10, fontweight='bold')
    ax.annotate(f"{int(vals.iloc[-1]):,}", (2025, vals.iloc[-1]), xytext=(-5, 8),
                textcoords='offset points', ha='right', color=color, fontsize=10, fontweight='bold')
axes[-1].set_xticks(data['year'])
axes[-1].tick_params(axis='x', colors=gray, rotation=0, labelsize=9)
fig.text(0.08, 0.025,
         'Annual counts in police-reported crashes assigned to Brooklyn; complete years only (2013–2025).',
         fontsize=9, color=gray)
fig.text(0.08, 0.005,
         'Counts describe reported harm, not risk per pedestrian trip; borough is unreported for some crashes.',
         fontsize=8.5, color=gray)
fig.tight_layout(rect=[0.07, 0.07, 0.98, 0.94], h_pad=1.15)
fig.savefig('out/option_1.png', dpi=180, bbox_inches='tight', facecolor='white')
plt.close(fig)
data[['year','pedestrians_injured','pedestrians_killed']].to_csv('out/values_1.csv', index=False)

# Option 2: crash events with at least one pedestrian harmed, a measure of event frequency.
fig, ax = plt.subplots(figsize=(10.5, 5.8))
vals = data['crashes_with_pedestrian_harm']
ax.plot(data['year'], vals, color=blue, linewidth=3, marker='o', markersize=6)
ax.fill_between(data['year'], vals, color=blue, alpha=0.10)
ax.scatter([2013, 2025], [int(vals.iloc[0]), int(vals.iloc[-1])], color=navy, s=65, zorder=3)
ax.annotate(f"{int(vals.iloc[0]):,}", (2013, vals.iloc[0]), xytext=(6, 10),
            textcoords='offset points', color=navy, fontsize=11, fontweight='bold')
ax.annotate(f"{int(vals.iloc[-1]):,}", (2025, vals.iloc[-1]), xytext=(-6, 10),
            textcoords='offset points', ha='right', color=navy, fontsize=11, fontweight='bold')
ax.set_title('Fewer Brooklyn crashes harmed pedestrians than in 2013', loc='left',
             fontsize=17, color=navy, pad=18)
ax.set_ylabel('Crashes with ≥1 pedestrian injured or killed', color=navy)
ax.set_xlabel('Calendar year')
ax.set_xticks(data['year'])
ax.tick_params(axis='x', colors=gray)
ax.tick_params(axis='y', length=0, colors=gray)
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax.grid(axis='y', color='#DCE3E8', linewidth=0.8)
ax.spines[['top','right','left']].set_visible(False)
ax.spines['bottom'].set_color('#C7D0D7')
fig.text(0.08, 0.025,
         'Annual count of police-reported crashes assigned to Brooklyn with pedestrian injury or death; 2013–2025.',
         fontsize=9, color=gray)
fig.text(0.08, 0.005,
         'A crash count is not adjusted for how many people walked; some crashes have no reported borough.',
         fontsize=8.5, color=gray)
fig.tight_layout(rect=[0.07, 0.08, 0.98, 0.93])
fig.savefig('out/option_2.png', dpi=180, bbox_inches='tight', facecolor='white')
plt.close(fig)
data[['year','crashes_with_pedestrian_harm']].to_csv('out/values_2.csv', index=False)

start, end = data.iloc[0], data.iloc[-1]
for c in ['pedestrians_injured','pedestrians_killed','crashes_with_pedestrian_harm']:
    change = (end[c] / start[c] - 1) * 100
    print(c, int(start[c]), int(end[c]), round(change, 1), 'percent')
print(data.to_string(index=False))
PY
# bash
python3 - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

con = duckdb.connect()
data = con.execute("""
    SELECT year(crash_date) AS year,
           SUM(number_of_pedestrians_injured) AS pedestrians_injured,
           SUM(number_of_pedestrians_killed) AS pedestrians_killed,
           SUM(CASE WHEN number_of_pedestrians_injured > 0
                         OR number_of_pedestrians_killed > 0 THEN 1 ELSE 0 END)
               AS crashes_with_pedestrian_harm
    FROM read_parquet('data/crashes.parquet')
    WHERE upper(borough) = 'BROOKLYN'
      AND year(crash_date) BETWEEN 2013 AND 2025
    GROUP BY year
    ORDER BY year
""").df()
data['year'] = data['year'].astype(int)
for col in ['pedestrians_injured','pedestrians_killed','crashes_with_pedestrian_harm']:
    data[col] = data[col].astype(int)
assert data['year'].tolist() == list(range(2013, 2026))
plt.rcParams.update({'font.family':'DejaVu Sans', 'axes.titleweight':'bold'})
navy, blue, red, gray = '#15324B', '#2676A5', '#C84A3A', '#61717D'

fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.2), sharex=True)
fig.suptitle('Fewer pedestrians injured, more killed in Brooklyn than in 2013',
             x=0.08, y=0.985, ha='left', fontsize=17, fontweight='bold', color=navy)
for ax, col, label, color, top in [
    (axes[0], 'pedestrians_injured', 'Pedestrians injured (per year)', blue, 4000),
    (axes[1], 'pedestrians_killed', 'Pedestrians killed (per year)', red, 50),
]:
    vals = data[col]
    ax.plot(data['year'], vals, color=color, linewidth=2.8, marker='o', markersize=5)
    ax.scatter([2013, 2025], [vals.iloc[0], vals.iloc[-1]], color=color, s=55, zorder=3)
    ax.set_ylabel(label, color=navy, fontsize=10)
    ax.set_ylim(0, top)
    ax.grid(axis='y', color='#DCE3E8', linewidth=0.8)
    ax.spines[['top','right','left']].set_visible(False)
    ax.spines['bottom'].set_color('#C7D0D7')
    ax.tick_params(axis='y', length=0, colors=gray)
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    ax.annotate(f"{vals.iloc[0]:,}", (2013, vals.iloc[0]), xytext=(5, 8),
                textcoords='offset points', color=color, fontsize=10, fontweight='bold')
    ax.annotate(f"{vals.iloc[-1]:,}", (2025, vals.iloc[-1]), xytext=(-5, 8),
                textcoords='offset points', ha='right', color=color, fontsize=10, fontweight='bold')
axes[-1].set_xticks(data['year'])
axes[-1].tick_params(axis='x', colors=gray, rotation=0, labelsize=9)
fig.text(0.08, 0.025,
         'Annual counts in police-reported crashes assigned to Brooklyn; complete years only (2013–2025).',
         fontsize=9, color=gray)
fig.text(0.08, 0.005,
         'Counts describe reported harm, not risk per pedestrian trip; borough is unreported for some crashes.',
         fontsize=8.5, color=gray)
fig.tight_layout(rect=[0.07, 0.07, 0.98, 0.94], h_pad=1.15)
fig.savefig('out/option_1.png', dpi=180, bbox_inches='tight', facecolor='white')
plt.close(fig)
data[['year','pedestrians_injured','pedestrians_killed']].to_csv('out/values_1.csv', index=False)

fig, ax = plt.subplots(figsize=(10.5, 5.8))
vals = data['crashes_with_pedestrian_harm']
ax.plot(data['year'], vals, color=blue, linewidth=3, marker='o', markersize=6)
ax.fill_between(data['year'], vals, color=blue, alpha=0.10)
ax.scatter([2013, 2025], [vals.iloc[0], vals.iloc[-1]], color=navy, s=65, zorder=3)
ax.annotate(f"{vals.iloc[0]:,}", (2013, vals.iloc[0]), xytext=(6, 10),
            textcoords='offset points', color=navy, fontsize=11, fontweight='bold')
ax.annotate(f"{vals.iloc[-1]:,}", (2025, vals.iloc[-1]), xytext=(-6, 10),
            textcoords='offset points', ha='right', color=navy, fontsize=11, fontweight='bold')
ax.set_title('Fewer Brooklyn crashes harmed pedestrians than in 2013', loc='left',
             fontsize=17, color=navy, pad=18)
ax.set_ylabel('Crashes with ≥1 pedestrian injured or killed', color=navy)
ax.set_xlabel('Calendar year')
ax.set_xticks(data['year'])
ax.tick_params(axis='x', colors=gray)
ax.tick_params(axis='y', length=0, colors=gray)
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax.grid(axis='y', color='#DCE3E8', linewidth=0.8)
ax.spines[['top','right','left']].set_visible(False)
ax.spines['bottom'].set_color('#C7D0D7')
fig.text(0.08, 0.025,
         'Annual count of police-reported crashes assigned to Brooklyn with pedestrian injury or death; 2013–2025.',
         fontsize=9, color=gray)
fig.text(0.08, 0.005,
         'A crash count is not adjusted for how many people walked; some crashes have no reported borough.',
         fontsize=8.5, color=gray)
fig.tight_layout(rect=[0.07, 0.08, 0.98, 0.93])
fig.savefig('out/option_2.png', dpi=180, bbox_inches='tight', facecolor='white')
plt.close(fig)
data[['year','crashes_with_pedestrian_harm']].to_csv('out/values_2.csv', index=False)
for col in ['pedestrians_injured','pedestrians_killed','crashes_with_pedestrian_harm']:
    print(col, data[col].iloc[0], data[col].iloc[-1],
          round((data[col].iloc[-1] / data[col].iloc[0] - 1) * 100, 1))
PY
# bash
python3 -c "import json; p='out/options.json'; d=json.load(open(p)); assert len(d['options']) == 2; assert abs(sum(x['probability'] for x in d['options'])-1)<1e-9; print('JSON valid; probabilities sum to',sum(x['probability'] for x in d['options']))"

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