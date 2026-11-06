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

QUESTION ASKED: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Pedestrian injuries (people injured)
denominator: None; annual total
grouping: Calendar year, Brooklyn-assigned crashes
chart_type: Line chart
probability: 0.43
WRITTEN ANSWER:
Recorded pedestrian injuries fell from 3,641 in 2013 to 2,835 in 2025 (22% lower), but rose from the 2020 low of 1,781. These are reported injury counts, not risk per pedestrian trip.

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
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("describe select * from read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("select count(*) n, min(crash_date), max(crash_date) from read_parquet(?)", [p]).fetchall()); print(c.execute("select borough, count(*) n, min(crash_date), max(crash_date) from read_parquet(?) group by borough order by borough", [p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("select year(crash_date) year, count(*) crash_rows, sum(number_of_pedestrians_injured) ped_injured, sum(number_of_pedestrians_killed) ped_killed, sum(case when coalesce(number_of_pedestrians_injured,0)>0 or coalesce(number_of_pedestrians_killed,0)>0 then 1 else 0 end) ped_casualty_crashes, min(crash_date), max(crash_date) from read_parquet(?) where borough='BROOKLYN' and crash_date >= date '2013-01-01' group by 1 order by 1", [p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="select year(crash_date) as calendar_year, count(*) as crash_rows, sum(number_of_pedestrians_injured) as ped_injured, sum(number_of_pedestrians_killed) as ped_killed, sum(case when coalesce(number_of_pedestrians_injured,0)>0 or coalesce(number_of_pedestrians_killed,0)>0 then 1 else 0 end) as ped_casualty_crashes, min(crash_date) as first_date, max(crash_date) as last_date from read_parquet(?) where borough=? and crash_date >= ? group by 1 order by 1"; print(c.execute(q, [p,"BROOKLYN","2013-01-01"]).fetchdf().to_string(index=False))'
# bash
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="select count(*) rows, count(*) filter(where number_of_pedestrians_injured is null) null_inj, count(*) filter(where number_of_pedestrians_killed is null) null_killed, count(*) filter(where number_of_persons_injured is null) null_allinj from read_parquet(?) where borough=? and crash_date between ? and ?"; print(c.execute(q,[p,"BROOKLYN","2013-01-01","2025-12-31"]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="select count(*) as row_count, count(*) filter(where number_of_pedestrians_injured is null) as null_inj, count(*) filter(where number_of_pedestrians_killed is null) as null_killed, count(*) filter(where number_of_persons_injured is null) as null_allinj from read_parquet(?) where borough=? and crash_date between ? and ?"; print(c.execute(q,[p,"BROOKLYN","2013-01-01","2025-12-31"]).fetchdf().to_string(index=False))'
# bash
  year(crash_date) AS year,
  sum(number_of_pedestrians_injured) AS pedestrian_injuries,
  sum(number_of_pedestrians_killed) AS pedestrian_deaths,
  sum(CASE WHEN number_of_pedestrians_injured > 0 OR number_of_pedestrians_killed > 0 THEN 1 ELSE 0 END) AS crashes_with_pedestrian_casualty
WHERE borough = 'BROOKLYN'
  AND crash_date >= DATE '2013-01-01'
  AND crash_date < DATE '2026-01-01'
GROUP BY year
ORDER BY year
df = con.execute(query, ['data/crashes.parquet']).fetchdf()
assert df['year'].tolist() == list(range(2013, 2026))
df['pedestrian_casualty_crashes_per_1000_records'] = 1000 * df['crashes_with_pedestrian_casualty'] / df['brooklyn_crash_records']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.titleweight': 'bold'})
# Option 1: Annual pedestrian injury count, line chart.
df[['year', 'pedestrian_injuries']].to_csv(out / 'values_1.csv', index=False)
ax.plot(df['year'], df['pedestrian_injuries'], color=blue, linewidth=2.8, marker='o', markersize=5)
ax.fill_between(df['year'], df['pedestrian_injuries'], color=blue, alpha=0.10)
ax.set_title('Brooklyn pedestrian injuries fell from 2013, then climbed', loc='left', fontsize=16, pad=14)
ax.set_xlabel('Calendar year')
ax.set_xticks(df['year'])
ax.annotate(f"{int(df.iloc[0]['pedestrian_injuries']):,}", (2013, df.iloc[0]['pedestrian_injuries']), xytext=(0, 12), textcoords='offset points', ha='center', color=navy, weight='bold')
ax.annotate(f"{int(df.iloc[-1]['pedestrian_injuries']):,}", (2025, df.iloc[-1]['pedestrian_injuries']), xytext=(0, 12), textcoords='offset points', ha='center', color=navy, weight='bold')
fig.text(0.01, 0.015, 'Full calendar years 2013–2025; 2026 excluded as partial. Counts in NYC police-reported crash records assigned to Brooklyn. Not adjusted for walking volume.', fontsize=8.5, color=gray)
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
# Option 2: Annual pedestrian death count, bar chart.
df[['year', 'pedestrian_deaths']].to_csv(out / 'values_2.csv', index=False)
bars = ax.bar(df['year'], df['pedestrian_deaths'], color=[red if y in (2013, 2025) else '#D88981' for y in df['year']], width=0.72)
ax.set_title('Pedestrian deaths in Brooklyn remain volatile—and above 2013', loc='left', fontsize=16, pad=14)
ax.set_xlabel('Calendar year')
ax.set_xticks(df['year'])
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.7, f'{int(b.get_height())}', ha='center', va='bottom', color=navy, weight='bold')
fig.text(0.01, 0.015, 'Full calendar years 2013–2025; 2026 excluded as partial. Counts in NYC police-reported crash records assigned to Brooklyn. Not adjusted for walking volume.', fontsize=8.5, color=gray)
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
# Option 3: Pedestrian-casualty crashes as a share of all Brooklyn-assigned crash records.
df[['year', 'crashes_with_pedestrian_casualty', 'brooklyn_crash_records', 'pedestrian_casualty_crashes_per_1000_records']].to_csv(out / 'values_3.csv', index=False)
rates = df['pedestrian_casualty_crashes_per_1000_records']
ax.plot(df['year'], rates, color=navy, linewidth=2.8, marker='o', markersize=5)
ax.fill_between(df['year'], rates, color=navy, alpha=0.09)
ax.set_xlabel('Calendar year')
ax.set_xticks(df['year'])
ax.annotate(f'{rates.iloc[0]:.1f}', (2013, rates.iloc[0]), xytext=(0, 12), textcoords='offset points', ha='center', color=navy, weight='bold')
ax.annotate(f'{rates.iloc[-1]:.1f}', (2025, rates.iloc[-1]), xytext=(0, 12), textcoords='offset points', ha='center', color=navy, weight='bold')
fig.text(0.01, 0.015, 'Numerator: Brooklyn-assigned crashes with ≥1 pedestrian injured or killed. Denominator: all Brooklyn-assigned crash records. Full years 2013–2025; not adjusted for walking volume.', fontsize=8.5, color=gray)
fig.savefig(out / 'option_3.png', dpi=180, bbox_inches='tight')
injury_change = (df.iloc[-1]['pedestrian_injuries'] / df.iloc[0]['pedestrian_injuries'] - 1) * 100
death_change = (df.iloc[-1]['pedestrian_deaths'] / df.iloc[0]['pedestrian_deaths'] - 1) * 100
      'grouping': 'Calendar year, Brooklyn-assigned crashes',
      'answer': f"Recorded pedestrian injuries fell from {int(df.iloc[0]['pedestrian_injuries']):,} in 2013 to {int(df.iloc[-1]['pedestrian_injuries']):,} in 2025 ({abs(injury_change):.0f}% lower), but rose from the 2020 low of {int(df.loc[df.year == 2020, 'pedestrian_injuries'].iloc[0]):,}. These are reported injury counts, not risk per pedestrian trip."
      'grouping': 'Calendar year, Brooklyn-assigned crashes',
      'reason': 'Deaths isolate the most severe outcome and annual bars make the year-to-year toll easy to compare.',
      'answer': f"Pedestrian deaths increased from {int(df.iloc[0]['pedestrian_deaths'])} in 2013 to {int(df.iloc[-1]['pedestrian_deaths'])} in 2025 ({death_change:.0f}% higher), with substantial year-to-year variation. The count is not adjusted for pedestrian exposure."
      'denominator': 'All Brooklyn-assigned crash records in the same calendar year',
      'grouping': 'Calendar year',
      'answer': f"The share of Brooklyn-assigned crash records involving a pedestrian injured or killed rose from {rates.iloc[0]/10:.1f}% in 2013 to {rates.iloc[-1]/10:.1f}% in 2025 (up {rate_change_pp/10:.1f} percentage points). That indicates a larger pedestrian-casualty share of recorded crashes, not exposure-adjusted risk."
with (out / 'options.json').open('w', encoding='utf-8') as f:
print('injury change %:', injury_change, 'death change %:', death_change, 'rate change pp:', rate_change_pp/10)
# bash
    path = out / filename
path = out / 'values_3.csv'
values['pedestrian_casualty_crash_share_pct'] = 100 * values['crashes_with_pedestrian_casualty'] / values['brooklyn_crash_records']
with (out / 'options.json').open(encoding='utf-8') as f:
assert abs(sum(o['probability'] for o in options['options']) - 1) < 1e-9
    assert (out / f"option_{option['id']}.png").is_file()
    assert (out / f"values_{option['id']}.csv").is_file()
print('JSON valid; probabilities sum to', sum(o['probability'] for o in options['options']))
# bash
python3 -c 'import json; x=json.load(open("out/options.json")); print(len(x["options"]), [o["answer"] for o in x["options"]])'
... (code lines filtered to those about filters, windows and denominators)

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