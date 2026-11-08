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
metric: Crashes with at least one pedestrian injured or killed
denominator: Not applicable (annual crash count; no pedestrian-exposure denominator)
grouping: Annual count of crashes involving a pedestrian casualty
chart_type: line chart
probability: 0.28
WRITTEN ANSWER:
Crashes recorded in Brooklyn with a pedestrian injured or killed fell from 3,498 in 2013 to 2,766 in 2025 (-20.9%), but this event count does not measure pedestrian exposure. This framing answers whether the annual number of Brooklyn-recorded crashes causing at least one pedestrian injury or death fell: the count declined from 2013 to 2025, with a sharp 2020 dip and a partial rebound afterward. It is a defensible event-frequency measure, but it excludes crashes with borough missing and cannot indicate the chance of being struck per trip or the number harmed in each crash.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,crashes_with_pedestrian_casualty
2013,3498
2014,3234
2015,2962
2016,2797
2017,2550
2018,2697
2019,2623
2020,1724
2021,1856
2022,2185
2023,2310
2024,2576
2025,2766

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
# bash
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f'DESCRIBE SELECT * FROM read_parquet(\'{p}\')').fetchdf().to_string(index=False)); print(c.execute(f\"SELECT min(crash_date) min_date, max(crash_date) max_date, count(*) n, count(*) FILTER (WHERE borough='BROOKLYN') brooklyn FROM read_parquet('{p}')\").fetchdf().to_string(index=False)); print(c.execute(f\"SELECT year(crash_date) year, count(*) crashes, sum(number_of_pedestrians_injured) injured, sum(number_of_pedestrians_killed) killed FROM read_parquet('{p}') WHERE borough='BROOKLYN' GROUP BY 1 ORDER BY 1\").fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=\"SELECT year(crash_date) AS yr, count(*) AS known_borough_crashes, sum(coalesce(number_of_pedestrians_injured,0)) AS pedestrian_injuries, sum(coalesce(number_of_pedestrians_killed,0)) AS pedestrian_deaths, count(*) FILTER (WHERE coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0)>0) AS ped_casualty_crashes, count(*) FILTER (WHERE borough IS NULL) AS borough_missing FROM read_parquet(?) WHERE borough='BROOKLYN' OR borough IS NULL GROUP BY yr ORDER BY yr\"; print(c.execute(q,[p]).fetchdf().to_string(index=False)); print(c.execute(\"SELECT year(crash_date) AS yr, count(*) AS n, sum(coalesce(number_of_pedestrians_injured,0)) AS inj, sum(coalesce(number_of_pedestrians_killed,0)) AS deaths FROM read_parquet(?) WHERE borough='BROOKLYN' GROUP BY yr ORDER BY yr\",[p]).fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=\"SELECT year(crash_date) AS yr, count(*) AS brooklyn_crashes, sum(coalesce(number_of_pedestrians_injured,0)) AS pedestrian_injuries, sum(coalesce(number_of_pedestrians_killed,0)) AS pedestrian_deaths, sum(coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0)) AS pedestrian_casualties, count(*) FILTER (WHERE coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0)>0) AS ped_casualty_crashes, count(*) FILTER (WHERE coalesce(number_of_pedestrians_killed,0)>0) AS fatal_ped_crashes FROM read_parquet(?) WHERE borough='BROOKLYN' AND crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr\"; print(c.execute(q,[p]).fetchdf().to_string(index=False))"
# bash
    SELECT year(crash_date) AS year,
           sum(coalesce(number_of_pedestrians_injured, 0) + coalesce(number_of_pedestrians_killed, 0))::BIGINT AS pedestrian_casualties,
           sum(coalesce(number_of_pedestrians_killed, 0))::BIGINT AS pedestrian_deaths,
           count(*) FILTER (WHERE coalesce(number_of_pedestrians_injured, 0) + coalesce(number_of_pedestrians_killed, 0) > 0)::BIGINT AS crashes_with_pedestrian_casualty
    FROM read_parquet('data/crashes.parquet')
    WHERE borough = 'BROOKLYN'
      AND crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    (1, 'pedestrian_casualties', 'Pedestrian injuries + deaths (people)', 'Annual count of pedestrian casualties', 'Pedestrian casualties in Brooklyn', 'People injured or killed', 'No exposure denominator; borough is as recorded.'),
    (2, 'pedestrian_deaths', 'Pedestrian deaths (people)', 'Annual count of pedestrian deaths', 'Pedestrian deaths in Brooklyn', 'People killed', 'Fatalities are a severe outcome; borough is as recorded.'),
    (3, 'crashes_with_pedestrian_casualty', 'Crashes with at least one pedestrian injured or killed (crashes)', 'Annual count of crashes involving a pedestrian casualty', 'Brooklyn crashes involving a pedestrian casualty', 'Crashes', 'Counts crashes once, regardless of how many pedestrians were injured or killed; borough is as recorded.'),
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titleweight': 'bold'})
    values = df[['year', col]].copy()
    values.to_csv(f'out/values_{idx}.csv', index=False)
    ax.plot(values.year, values[col], color=color, linewidth=2.8, marker='o', markersize=5.5)
    ax.fill_between(values.year, values[col], alpha=.10, color=color)
    ax.text(0, 1.02, 'Annual counts, 2013–2025 • crashes recorded in Brooklyn', transform=ax.transAxes, fontsize=10, color='#555555')
    ax.set_xlabel('Year')
    ax.set_xticks(values.year)
    pct = 100 * (end - start) / start
    ax.annotate(f'2013: {start:,}', (2013, start), xytext=(7, 10), textcoords='offset points', color=color, fontsize=9, weight='bold')
    ax.annotate(f'2025: {end:,} ({sign}{pct:.1f}%)', (2025, end), xytext=(-8, 12 if end >= start else -18), textcoords='offset points', ha='right', color=color, fontsize=9, weight='bold')
    fig.text(.01, .01, 'Source: NYC police-reported motor vehicle crashes. 2026 omitted as incomplete. ' + note, fontsize=8, color='#555555')
    fig.savefig(f'out/option_{idx}.png', dpi=180, bbox_inches='tight')
        answer = f"Recorded pedestrian casualties fell from {start:,} in 2013 to {end:,} in 2025 ({pct:.1f}%), although the count measures people harmed, not risk per pedestrian."
        interp = 'This framing answers whether the total number of pedestrians injured or killed in recorded Brooklyn crashes fell: it declined between 2013 and 2025, with the plotted year-by-year pattern showing the change was not uniformly downward. It is defensible as a measure of total harm, but it does not show an exposure-adjusted risk because pedestrian trips or population are not in the data.'
        answer = f"Recorded pedestrian deaths rose from {start:,} in 2013 to {end:,} in 2025 ({pct:+.1f}%), so the most severe outcome did not improve over that comparison."
        interp = 'This framing answers whether fatal pedestrian harm improved: annual deaths were higher in 2025 than in 2013, despite year-to-year fluctuations. It is a defensible severity measure, but it says nothing about nonfatal injuries or the risk per walking trip.'
        answer = f"Crashes with a pedestrian injured or killed fell from {start:,} in 2013 to {end:,} in 2025 ({pct:.1f}%), but this event count does not measure pedestrian exposure."
        interp = 'This framing answers whether the annual number of crashes causing at least one pedestrian injury or death fell: the count declined from 2013 to 2025, with a sharp pandemic-era dip and a partial rebound afterward. It is defensible as an event-frequency measure, but it does not indicate the chance of being struck per trip or separate severity within each crash.'
with open('out/options.json', 'w') as f:
# bash
    (1, 'pedestrian_casualties', 'Pedestrian casualties in Brooklyn', 'People injured or killed', 'No exposure denominator; only crashes with borough labeled Brooklyn are included.'),
    (2, 'pedestrian_deaths', 'Pedestrian deaths in Brooklyn', 'People killed', 'Fatalities are a severe outcome; only crashes with borough labeled Brooklyn are included.'),
    (3, 'crashes_with_pedestrian_casualty', 'Brooklyn crashes involving a pedestrian casualty', 'Crashes', 'Each crash is counted once; only crashes with borough labeled Brooklyn are included.'),
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titleweight': 'bold'})
    values = pd.read_csv(f'out/values_{idx}.csv')
    ax.plot(values.year, values[col], color=color, linewidth=2.8, marker='o', markersize=5.5)
    ax.fill_between(values.year, values[col], alpha=.10, color=color)
    ax.text(0, 1.02, 'Annual counts, 2013–2025 • crashes recorded in Brooklyn', transform=ax.transAxes, fontsize=10, color='#555555')
    ax.set_xlabel('Year')
    ax.set_xticks(values.year)
    ax.set_xlim(2012.4, 2027.7)
    pct = 100 * (end - start) / start
    ax.annotate(f'2013: {start:,}', (2013, start), xytext=(7, 10), textcoords='offset points', color=color, fontsize=9, weight='bold')
    ax.annotate(f'2025: {end:,} ({sign}{pct:.1f}%)', (2025, end), xytext=(10, 0), textcoords='offset points', ha='left', va='center', color=color, fontsize=9, weight='bold')
    fig.text(.01, .01, 'Source: NYC police-reported motor vehicle crashes. 2026 omitted as incomplete. ' + note, fontsize=8, color='#555555')
    fig.savefig(f'out/option_{idx}.png', dpi=180, bbox_inches='tight')
with open('out/options.json') as f:
opts[0].update({
    'answer': 'Among crashes recorded with Brooklyn as the borough, pedestrian casualties fell from 3,671 in 2013 to 2,874 in 2025 (-21.7%), but this count does not measure risk per pedestrian.',
    'interpretation': 'This framing answers whether the recorded number of pedestrians injured or killed in Brooklyn crashes fell: it declined between 2013 and 2025, though not uniformly year to year. It is a defensible measure of total harm among records labeled Brooklyn, but borough-missing crashes are excluded and the data lack pedestrian-trip exposure, so it cannot establish risk per pedestrian.'
opts[1].update({
    'answer': 'Among crashes recorded with Brooklyn as the borough, pedestrian deaths rose from 30 in 2013 to 39 in 2025 (+30.0%), so the most severe outcome did not improve over that comparison.',
    'interpretation': 'This framing answers whether fatal pedestrian harm improved: annual deaths recorded in Brooklyn crashes were higher in 2025 than in 2013, despite year-to-year fluctuations. It is a defensible severity measure, but borough-missing crashes are excluded and it does not show nonfatal injuries or risk per walking trip.'
opts[2].update({
    'answer': 'Crashes recorded in Brooklyn with a pedestrian injured or killed fell from 3,498 in 2013 to 2,766 in 2025 (-20.9%), but this event count does not measure pedestrian exposure.',
    'interpretation': 'This framing answers whether the annual number of Brooklyn-recorded crashes causing at least one pedestrian injury or death fell: the count declined from 2013 to 2025, with a sharp 2020 dip and a partial rebound afterward. It is a defensible event-frequency measure, but it excludes crashes with borough missing and cannot indicate the chance of being struck per trip or the number harmed in each crash.'
with open('out/options.json', 'w') as f:
print('Regenerated charts and updated options.json.')
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