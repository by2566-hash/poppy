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

QUESTION ASKED: Has pedestrian road safety in Brooklyn improved since 2013? Produce a chart appropriate for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Share of Brooklyn crashes involving at least one pedestrian injury or death
denominator: All police-reported Brooklyn crashes in the same calendar year
grouping: Calendar year, Brooklyn crashes
chart_type: Line chart
probability: 0.25
WRITTEN ANSWER:
The share of reported Brooklyn crashes involving pedestrian injury or death rose from 7.4% (3,498/47,024) in 2013 to 11.4% (2,766/24,303) in 2025, up 3.9 percentage points. This framing answers whether pedestrian injury crashes account for a larger share of Brooklyn crash reports, and the chart shows that share rising between 2013 and 2025. It is defensible as a comparison to overall crash volume, but not as pedestrian injury risk per walker or walking trip.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,brooklyn_crashes,pedestrian_involved_crashes,pedestrian_involved_crash_share_pct
2013,47024,3498,7.438754678462062
2014,47761,3234,6.771215008060969
2015,50851,2962,5.824860868026194
2016,47464,2797,5.892887240856228
2017,44915,2550,5.677390626739396
2018,47313,2697,5.700336059856699
2019,44479,2623,5.897164954248072
2020,25473,1724,6.76795037883249
2021,25174,1856,7.372686104711209
2022,23369,2185,9.349993581240104
2023,22890,2310,10.091743119266056
2024,22785,2576,11.30568356374808
2025,24303,2766,11.381310949265524

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute(f"SELECT COUNT(*), MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE borough = '\''BROOKLYN'\'') FROM read_parquet('\''{p}'\'')").fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print("year | crashes | pedestrian injured | pedestrian killed | injured-or-killed crashes"); print(*c.execute(f"SELECT year(crash_date), count(*), sum(coalesce(number_of_pedestrians_injured,0)), sum(coalesce(number_of_pedestrians_killed,0)), count(*) FILTER (WHERE coalesce(number_of_pedestrians_injured,0)>0 OR coalesce(number_of_pedestrians_killed,0)>0) FROM read_parquet('\''{p}'\'') WHERE borough='\''BROOKLYN'\'' AND crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' GROUP BY 1 ORDER BY 1").fetchall(), sep="\n")'
# bash
ls -ld . data
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute(f"SELECT count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL), count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL), count(*) FILTER (WHERE borough IS NULL) FROM read_parquet('\''{p}'\'') WHERE borough='\''BROOKLYN'\'' AND crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\''").fetchall()); print(c.execute(f"SELECT count(*) FROM read_parquet('\''{p}'\'') WHERE borough='\''BROOKLYN'\'' AND crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' AND number_of_pedestrians_injured IS NULL AND number_of_pedestrians_killed IS NULL").fetchall())'
# bash
mkdir -p out && python3 - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import json
from pathlib import Path

out = Path('out')
con = duckdb.connect()
rows = con.execute("""
    SELECT year(crash_date) AS year,
           count(*) AS brooklyn_crashes,
           sum(number_of_pedestrians_injured) AS pedestrian_injured,
           sum(number_of_pedestrians_killed) AS pedestrian_killed,
           count(*) FILTER (WHERE number_of_pedestrians_injured > 0 OR number_of_pedestrians_killed > 0) AS pedestrian_involved_crashes
    FROM read_parquet('data/crashes.parquet')
    WHERE borough = 'BROOKLYN'
      AND crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY 1
    ORDER BY 1
""").df()
rows['year'] = rows['year'].astype(int)
rows['pedestrian_casualties'] = rows['pedestrian_injured'] + rows['pedestrian_killed']
rows['pedestrian_involved_crash_share_pct'] = rows['pedestrian_involved_crashes'] / rows['brooklyn_crashes'] * 100

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titlesize': 16, 'axes.labelsize': 11})
navy, blue, red = '#164E75', '#2878B5', '#C13C37'

def base(ax, title, ylabel):
    ax.set_title(title, loc='left', fontweight='bold', pad=14)
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Calendar year')
    ax.set_xticks(rows['year'])
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', color='#D9E0E6', linewidth=.8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(2012.7, 2025.7)
    ax.text(0, -0.25, 'Source: NYC police-reported motor vehicle crashes; Brooklyn; complete years 2013–2025.',
            transform=ax.transAxes, fontsize=8, color='#4D5963')

# Option 1: count of pedestrian casualties (injured + killed)
fig, ax = plt.subplots(figsize=(10, 5.7), constrained_layout=True)
ax.plot(rows['year'], rows['pedestrian_casualties'], color=navy, linewidth=2.8, marker='o', markersize=5)
ax.fill_between(rows['year'], rows['pedestrian_casualties'], color=blue, alpha=.12)
base(ax, 'Brooklyn pedestrian injuries and deaths fell from 2013, then rebounded', 'Pedestrians injured or killed (people)')
first, last = rows.iloc[0], rows.iloc[-1]
ax.annotate(f"{int(first['pedestrian_casualties']):,}", (first['year'], first['pedestrian_casualties']), xytext=(6, 10), textcoords='offset points', fontweight='bold', color=navy)
ax.annotate(f"{int(last['pedestrian_casualties']):,}", (last['year'], last['pedestrian_casualties']), xytext=(-31, 10), textcoords='offset points', fontweight='bold', color=navy)
ax.set_ylim(bottom=0)
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)
rows[['year', 'pedestrian_injured', 'pedestrian_killed', 'pedestrian_casualties']].to_csv(out / 'values_1.csv', index=False)

# Option 2: annual pedestrian fatalities
fig, ax = plt.subplots(figsize=(10, 5.7), constrained_layout=True)
ax.plot(rows['year'], rows['pedestrian_killed'], color=red, linewidth=2.8, marker='o', markersize=5)
base(ax, 'Pedestrian deaths in Brooklyn fluctuate year to year', 'Pedestrians killed (people)')
ax.annotate(f"{int(first['pedestrian_killed'])}", (first['year'], first['pedestrian_killed']), xytext=(6, 9), textcoords='offset points', fontweight='bold', color=red)
ax.annotate(f"{int(last['pedestrian_killed'])}", (last['year'], last['pedestrian_killed']), xytext=(-25, 9), textcoords='offset points', fontweight='bold', color=red)
ax.set_ylim(bottom=0)
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)
rows[['year', 'pedestrian_killed']].to_csv(out / 'values_2.csv', index=False)

# Option 3: share of reported Brooklyn crashes involving pedestrian injury or death
fig, ax = plt.subplots(figsize=(10, 5.7), constrained_layout=True)
ax.plot(rows['year'], rows['pedestrian_involved_crash_share_pct'], color=blue, linewidth=2.8, marker='o', markersize=5)
base(ax, 'Pedestrian-injury crashes make up a larger share of Brooklyn crashes', 'Brooklyn crashes with pedestrian injury or death (%)')
ax.annotate(f"{first['pedestrian_involved_crash_share_pct']:.1f}%", (first['year'], first['pedestrian_involved_crash_share_pct']), xytext=(6, 10), textcoords='offset points', fontweight='bold', color=blue)
ax.annotate(f"{last['pedestrian_involved_crash_share_pct']:.1f}%", (last['year'], last['pedestrian_involved_crash_share_pct']), xytext=(-34, 10), textcoords='offset points', fontweight='bold', color=blue)
ax.set_ylim(bottom=0)
fig.savefig(out / 'option_3.png', dpi=180, bbox_inches='tight')
plt.close(fig)
rows[['year', 'brooklyn_crashes', 'pedestrian_involved_crashes', 'pedestrian_involved_crash_share_pct']].to_csv(out / 'values_3.csv', index=False)

injury_change = (last['pedestrian_casualties'] / first['pedestrian_casualties'] - 1) * 100
fatal_change = (last['pedestrian_killed'] / first['pedestrian_killed'] - 1) * 100
share_change = last['pedestrian_involved_crash_share_pct'] - first['pedestrian_involved_crash_share_pct']
options = {'options': [
    {'id': 1, 'metric': 'Annual pedestrian casualties (pedestrians injured plus pedestrians killed)', 'denominator': 'None; annual count of pedestrian people harmed', 'grouping': 'Calendar year, Brooklyn crashes', 'chart_type': 'Line chart', 'reason': 'A combined injury-and-death count captures the overall number of pedestrians harmed each year.', 'probability': 0.45, 'answer': f"Reported pedestrian injuries and deaths fell from {int(first['pedestrian_casualties']):,} in 2013 to {int(last['pedestrian_casualties']):,} in 2025 ({injury_change:.1f}%), but the count rose {((last['pedestrian_casualties'] / rows.loc[rows.year == 2020, 'pedestrian_casualties'].iloc[0]) - 1) * 100:.1f}% from its 2020 low.", 'interpretation': 'This framing answers whether the total number of pedestrians harmed has improved, and the chart shows a lower 2025 count than in 2013 despite a substantial rebound after 2020. It is defensible as a simple harm-count trend, but without pedestrian exposure data it does not measure risk per trip or walking population.'},
    {'id': 2, 'metric': 'Annual pedestrian fatalities', 'denominator': 'None; annual count of pedestrians killed', 'grouping': 'Calendar year, Brooklyn crashes', 'chart_type': 'Line chart', 'reason': 'Fatalities isolate the most severe pedestrian outcome, which is often the central concern in road-safety coverage.', 'probability': 0.30, 'answer': f"Pedestrian deaths increased from {int(first['pedestrian_killed'])} in 2013 to {int(last['pedestrian_killed'])} in 2025 ({fatal_change:.0f}%), with sizable year-to-year fluctuations.", 'interpretation': 'This framing answers whether the most severe pedestrian outcome improved, and the chart shows more recorded pedestrian deaths in 2025 than in 2013 amid irregular annual variation. Fatalities alone omit nonfatal injuries and do not provide a risk rate adjusted for walking exposure.'},
    {'id': 3, 'metric': 'Share of Brooklyn crashes involving at least one pedestrian injury or death', 'denominator': 'All police-reported Brooklyn crashes in the same calendar year', 'grouping': 'Calendar year, Brooklyn crashes', 'chart_type': 'Line chart', 'reason': 'A within-crash share shows whether pedestrian-injury crashes have become more common relative to all reported Brooklyn crashes.', 'probability': 0.25, 'answer': f"The share of reported Brooklyn crashes involving pedestrian injury or death rose from {first['pedestrian_involved_crash_share_pct']:.1f}% ({int(first['pedestrian_involved_crashes']):,}/{int(first['brooklyn_crashes']):,}) in 2013 to {last['pedestrian_involved_crash_share_pct']:.1f}% ({int(last['pedestrian_involved_crashes']):,}/{int(last['brooklyn_crashes']):,}) in 2025, up {share_change:.1f} percentage points.", 'interpretation': 'This framing answers whether pedestrian injury crashes account for a larger share of Brooklyn crash reports, and the chart shows that share rising between 2013 and 2025. It is defensible as a comparison to overall crash volume, but not as pedestrian injury risk per walker or walking trip.'}
]}
(out / 'options.json').write_text(json.dumps(options, indent=2) + '\n')
print(rows.to_string(index=False))
print(f"Endpoint changes: casualties {injury_change:.1f}%; fatalities {fatal_change:.0f}%; crash share {share_change:.2f} percentage points")
PY
# bash
python3 -c 'import json; from pathlib import Path; p=Path("out"); x=json.loads((p/"options.json").read_text()); print("valid JSON; probability sum:", sum(o["probability"] for o in x["options"])); print("outputs:", sorted(f.name for f in p.iterdir()))'

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