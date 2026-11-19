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

QUESTION ASKED: How do motorist and cyclist deaths compare year by year in NYC, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Annual share of the combined motorist and cyclist death count for each group
denominator: Motorist deaths plus cyclist deaths in the same year
grouping: Year and road-user group
chart_type: 100% stacked bar chart
probability: 0.25
WRITTEN ANSWER:
Cyclists accounted for 9.1% to 27.4% of motorist-plus-cyclist deaths, lowest in 2013 and highest in 2019. This framing answers the question as a relative comparison: cyclists made up 9.1% to 27.4% of the combined motorist-and-cyclist death total, with the low in 2013 and high in 2019. The 100% stacked bars show how the relative shares shift year by year. It does not show absolute yearly death counts, and the denominator excludes deaths among pedestrians and any other road-user category. No rows are left out for NULL values in the two death-count fields, and none of 2013–2025 is partial in this file.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,cyclist_deaths,combined_motorist_cyclist_deaths,motorist_share_pct,cyclist_share_pct
2013,110,11,121,90.909091,9.090909
2014,109,20,129,84.496124,15.503876
2015,95,15,110,86.363636,13.636364
2016,72,18,90,80.000000,20.000000
2017,107,27,134,79.850746,20.149254
2018,98,10,108,90.740741,9.259259
2019,82,31,113,72.566372,27.433628
2020,139,29,168,82.738095,17.261905
2021,134,19,153,87.581699,12.418301
2022,116,19,135,85.925926,14.074074
2023,123,31,154,79.870130,20.129870
2024,111,24,135,82.222222,17.777778
2025,81,23,104,77.884615,22.115385

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)",[p]).fetchdf().to_string(index=False)); print(c.execute("SELECT COUNT(*) rows, MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL) motorist_nulls, COUNT(*) FILTER (WHERE number_of_cyclist_killed IS NULL) cyclist_nulls FROM read_parquet(?)",[p]).fetchdf().to_string(index=False)); print(c.execute("SELECT year(crash_date) year, COUNT(*) rows, SUM(number_of_motorist_killed) motorist_deaths, SUM(number_of_cyclist_killed) cyclist_deaths, COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL) rows_missing_either FROM read_parquet(?) WHERE crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2026-01-01\' GROUP BY 1 ORDER BY 1",[p]).fetchdf().to_string(index=False))'
# bash
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)",[p]).fetchdf().to_string(index=False)); print(c.execute("SELECT COUNT(*) rows, MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL) motorist_nulls, COUNT(*) FILTER (WHERE number_of_cyclist_killed IS NULL) cyclist_nulls FROM read_parquet(?)",[p]).fetchdf().to_string(index=False)); print(c.execute("SELECT year(crash_date) year, COUNT(*) rows, SUM(number_of_motorist_killed) motorist_deaths, SUM(number_of_cyclist_killed) cyclist_deaths, COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL) rows_missing_either FROM read_parquet(?) WHERE crash_date >= ? AND crash_date < ? GROUP BY 1 ORDER BY 1",[p,"2013-01-01","2026-01-01"]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT COUNT(*) AS n_rows, MIN(crash_date) AS min_date, MAX(crash_date) AS max_date, COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS motorist_nulls, COUNT(*) FILTER (WHERE number_of_cyclist_killed IS NULL) AS cyclist_nulls FROM read_parquet(?)",[p]).fetchdf().to_string(index=False)); print(c.execute("SELECT year(crash_date) AS yr, COUNT(*) AS n_rows, SUM(number_of_motorist_killed) AS motorist_deaths, SUM(number_of_cyclist_killed) AS cyclist_deaths, COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL) AS rows_missing_either FROM read_parquet(?) WHERE crash_date >= ? AND crash_date < ? GROUP BY 1 ORDER BY 1",[p,"2013-01-01","2026-01-01"]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); print(c.execute("SELECT year(crash_date) AS yr, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date, COUNT(*) AS n_crashes FROM read_parquet(?) GROUP BY 1 ORDER BY 1",["data/crashes.parquet"]).fetchdf().to_string(index=False))'
# bash
    SELECT year(crash_date) AS year,
           SUM(number_of_motorist_killed)::INTEGER AS motorist_deaths,
           SUM(number_of_cyclist_killed)::INTEGER AS cyclist_deaths,
           COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL) AS rows_missing_needed_values
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
assert list(df['year']) == list(range(2013, 2026))
assert df['rows_missing_needed_values'].sum() == 0
# Option 1: compare absolute annual death counts.
values1 = df[['year', 'motorist_deaths', 'cyclist_deaths']].copy()
values1.to_csv(out / 'values_1.csv', index=False)
ax.bar(x - w/2, values1.motorist_deaths, w, label='Motorists', color='#355C9A')
ax.bar(x + w/2, values1.cyclist_deaths, w, label='Cyclists', color='#E4863A')
ax.set_xticks(x, values1.year.astype(str))
ax.set_xlabel('Year')
ax.set_title('NYC motorist and cyclist deaths by year, 2013–2025')
fig.savefig(out / 'option_1.png', dpi=180)
# Option 2: compare the relative composition of the combined two-group total.
values2 = df[['year', 'motorist_deaths', 'cyclist_deaths']].copy()
values2['motorist_share_pct'] = values2.motorist_deaths / values2.combined_motorist_cyclist_deaths * 100
values2['cyclist_share_pct'] = values2.cyclist_deaths / values2.combined_motorist_cyclist_deaths * 100
values2.to_csv(out / 'values_2.csv', index=False, float_format='%.6f')
ax.bar(values2.year.astype(str), values2.motorist_share_pct, label='Motorists', color='#355C9A')
ax.bar(values2.year.astype(str), values2.cyclist_share_pct, bottom=values2.motorist_share_pct, label='Cyclists', color='#E4863A')
ax.set_xlabel('Year')
ax.set_title('Share of combined NYC motorist and cyclist deaths, 2013–2025')
    ax.text(i, 100 - share / 2, f'{share:.1f}%', ha='center', va='center', color='white', fontsize=8, fontweight='bold')
fig.savefig(out / 'option_2.png', dpi=180)
            'grouping': 'Year and road-user group',
            'answer': f"Motorist deaths were higher in every year, ranging from {values1.motorist_deaths.min()} to {values1.motorist_deaths.max()} annually versus {values1.cyclist_deaths.min()} to {values1.cyclist_deaths.max()} cyclist deaths; motorist deaths peaked in {int(values1.loc[values1.motorist_deaths.idxmax(), 'year'])} ({int(values1.motorist_deaths.max())}) and cyclist deaths peaked in {int(values1.loc[values1.cyclist_deaths.idxmax(), 'year'])} ({int(values1.cyclist_deaths.max())}).",
            'interpretation': 'This framing answers the question in terms of annual death counts: motorist deaths exceeded cyclist deaths in all 13 complete years, with respective annual ranges of 72–139 and 10–31. The grouped bars make the absolute scale and yearly peaks visible, so counts directly compare the two groups. It leaves unanswered how the balance looks relative to their combined total. No rows are left out for NULL values in the two death-count fields, and none of 2013–2025 is partial in this file.'
            'denominator': 'Motorist deaths plus cyclist deaths in the same year',
            'grouping': 'Year and road-user group',
            'reason': 'The combined-total share makes the relative balance between the two groups comparable across years regardless of their differing totals.',
            'answer': f"Cyclists accounted for {cyclist_min.cyclist_share_pct:.1f}% to {cyclist_max.cyclist_share_pct:.1f}% of motorist-plus-cyclist deaths, lowest in {int(cyclist_min.year)} and highest in {int(cyclist_max.year)}.",
            'interpretation': f"This framing answers the question as a relative comparison: cyclists made up {cyclist_min.cyclist_share_pct:.1f}% to {cyclist_max.cyclist_share_pct:.1f}% of the combined motorist-and-cyclist death total, with the low in {int(cyclist_min.year)} and high in {int(cyclist_max.year)}. The 100% stacked bars show how the two groups' relative shares shift year by year. It does not show absolute yearly death counts, and the denominator excludes deaths among pedestrians and any other road-user category. No rows are left out for NULL values in the two death-count fields, and none of 2013–2025 is partial in this file.'
(out / 'options.json').write_text(json.dumps(options, indent=2) + '\n')
print(df[['year', 'crashes', 'motorist_deaths', 'cyclist_deaths', 'rows_missing_needed_values']].to_string(index=False))
print('\nCyclist share range:', f'{cyclist_min.cyclist_share_pct:.6f}% ({int(cyclist_min.year)}) to {cyclist_max.cyclist_share_pct:.6f}% ({int(cyclist_max.year)})')
print('\nSaved:', ', '.join(str(p) for p in [out/'option_1.png', out/'values_1.csv', out/'option_2.png', out/'values_2.csv', out/'options.json']))
# bash
    SELECT year(crash_date) AS year,
           SUM(number_of_motorist_killed)::INTEGER AS motorist_deaths,
           SUM(number_of_cyclist_killed)::INTEGER AS cyclist_deaths,
           COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL) AS rows_missing_needed_values
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
assert list(df['year']) == list(range(2013, 2026))
assert df['rows_missing_needed_values'].sum() == 0
values1 = df[['year', 'motorist_deaths', 'cyclist_deaths']].copy()
values1.to_csv(out / 'values_1.csv', index=False)
ax.bar(x - w/2, values1.motorist_deaths, w, label='Motorists', color='#355C9A')
ax.bar(x + w/2, values1.cyclist_deaths, w, label='Cyclists', color='#E4863A')
ax.set_xticks(x, values1.year.astype(str))
ax.set_xlabel('Year')
ax.set_title('NYC motorist and cyclist deaths by year, 2013–2025')
fig.savefig(out / 'option_1.png', dpi=180)
values2 = df[['year', 'motorist_deaths', 'cyclist_deaths']].copy()
values2['motorist_share_pct'] = values2.motorist_deaths / values2.combined_motorist_cyclist_deaths * 100
values2['cyclist_share_pct'] = values2.cyclist_deaths / values2.combined_motorist_cyclist_deaths * 100
values2.to_csv(out / 'values_2.csv', index=False, float_format='%.6f')
ax.bar(values2.year.astype(str), values2.motorist_share_pct, label='Motorists', color='#355C9A')
ax.bar(values2.year.astype(str), values2.cyclist_share_pct, bottom=values2.motorist_share_pct, label='Cyclists', color='#E4863A')
ax.set_xlabel('Year')
ax.set_title('Share of combined NYC motorist and cyclist deaths, 2013–2025')
    ax.text(i, 100 - share / 2, f'{share:.1f}%', ha='center', va='center', color='white', fontsize=8, fontweight='bold')
fig.savefig(out / 'option_2.png', dpi=180)
            'grouping': 'Year and road-user group',
            'answer': f"Motorist deaths were higher in every year, ranging from {values1.motorist_deaths.min()} to {values1.motorist_deaths.max()} annually versus {values1.cyclist_deaths.min()} to {values1.cyclist_deaths.max()} cyclist deaths; motorist deaths peaked in {int(values1.loc[values1.motorist_deaths.idxmax(), 'year'])} ({int(values1.motorist_deaths.max())}) and cyclist deaths peaked in {int(values1.loc[values1.cyclist_deaths.idxmax(), 'year'])} ({int(values1.cyclist_deaths.max())}).",
            'interpretation': 'This framing answers the question in terms of annual death counts: motorist deaths exceeded cyclist deaths in all 13 complete years, with respective annual ranges of 72–139 and 10–31. The grouped bars make the absolute scale and yearly peaks visible, so counts directly compare the two groups. It leaves unanswered how the balance looks relative to their combined total. No rows are left out for NULL values in the two death-count fields, and none of 2013–2025 is partial in this file.'
            'denominator': 'Motorist deaths plus cyclist deaths in the same year',
            'grouping': 'Year and road-user group',
            'reason': 'The combined-total share makes the relative balance between the two groups comparable across years regardless of their differing totals.',
            'answer': f"Cyclists accounted for {cyclist_min.cyclist_share_pct:.1f}% to {cyclist_max.cyclist_share_pct:.1f}% of motorist-plus-cyclist deaths, lowest in {int(cyclist_min.year)} and highest in {int(cyclist_max.year)}.",
            'interpretation': f"This framing answers the question as a relative comparison: cyclists made up {cyclist_min.cyclist_share_pct:.1f}% to {cyclist_max.cyclist_share_pct:.1f}% of the combined motorist-and-cyclist death total, with the low in {int(cyclist_min.year)} and high in {int(cyclist_max.year)}. The 100% stacked bars show how the relative shares shift year by year. It does not show absolute yearly death counts, and the denominator excludes deaths among pedestrians and any other road-user category. No rows are left out for NULL values in the two death-count fields, and none of 2013–2025 is partial in this file."
(out / 'options.json').write_text(json.dumps(options, indent=2) + '\n')
print(df[['year', 'crashes', 'motorist_deaths', 'cyclist_deaths', 'rows_missing_needed_values']].to_string(index=False))
print('\nCyclist share range:', f'{cyclist_min.cyclist_share_pct:.6f}% ({int(cyclist_min.year)}
... (code lines filtered to those about filters, windows and denominators; truncated)

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