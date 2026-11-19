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

QUESTION ASKED: How are NYC crashes distributed across the days of the week, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Crash records per weekday, with share of all selected crash records shown
denominator: All crash records dated 2013-01-01 through 2025-12-31 (2,132,218 records)
grouping: Day of week pooled across 2013–2025
chart_type: Horizontal bar chart
probability: 0.65
WRITTEN ANSWER:
Friday had the most crashes (338,800; 15.89% of the period total), while Sunday had the fewest (257,544; 12.08%). This framing answers the overall distribution across weekdays: Friday leads with 338,800 records and Sunday has the fewest, out of 2,132,218 selected crashes. It is defensible because pooled counts measure absolute reported crash volume and their displayed shares show each weekday's portion of that total. It leaves unanswered whether the weekday mix changes from year to year, since the chart pools the years. The date filter leaves out 2012: 100,545 rows (4.43%), 2026: 36,424 rows (1.61%); neither partial year is included, and no selected rows are omitted for a NULL date or weekday.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crash_count,share_of_selected_crashes_pct
Monday,304518,14.281748
Tuesday,313488,14.702437
Wednesday,311111,14.590956
Thursday,318376,14.931681
Friday,338800,15.889557
Saturday,288381,13.524930
Sunday,257544,12.078690

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
# bash
# bash
python -c 'import duckdb; p="data/crashes.parquet"; con=duckdb.connect(); print(con.execute("SELECT COUNT(*), MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE crash_date >= DATE ''2013-01-01'' AND crash_date < DATE ''2026-01-01'') FROM read_parquet(?)", [p]).fetchone()); print(con.execute("SELECT strftime(crash_date, ''%A'') AS weekday, COUNT(*) AS crashes, COUNT(DISTINCT crash_date) AS dates FROM read_parquet(?) WHERE crash_date >= DATE ''2013-01-01'' AND crash_date < DATE ''2026-01-01'' GROUP BY 1 ORDER BY MIN(isodow(crash_date))", [p]).fetchall())'
# bash
p='data/crashes.parquet'
print(con.execute("SELECT COUNT(*), MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01') FROM read_parquet(?)", [p]).fetchone())
print(con.execute("SELECT strftime(crash_date, '%A') AS weekday, COUNT(*) AS crashes, COUNT(DISTINCT crash_date) AS dates FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY MIN(isodow(crash_date))", [p]).fetchall())
# bash
p='data/crashes.parquet'
q="""SELECT year(crash_date) AS year, strftime(crash_date, '%A') AS weekday,
WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
GROUP BY 1,2 ORDER BY 1, MIN(isodow(crash_date))"""
df['share']=df.groupby('year').crashes.transform(lambda x: x/x.sum()*100)
print('excluded',con.execute("SELECT year(crash_date), COUNT(*) FROM read_parquet(?) WHERE crash_date < DATE '2013-01-01' OR crash_date >= DATE '2026-01-01' GROUP BY 1 ORDER BY 1",[p]).fetchall())
print('yearly top weekday:')
print(df.loc[df.groupby('year').share.idxmax(), ['year','weekday','share']].to_string(index=False))
print(df.groupby('weekday').share.agg(['mean','min','max']).reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']).to_string())
# bash
p='data/crashes.parquet'; c=duckdb.connect()
r=c.execute("""WITH d AS (SELECT year(crash_date) y, strftime(crash_date,'%A') w, count(*) n FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1,2), s AS (SELECT *, n/SUM(n) OVER(PARTITION BY y) pct FROM d) SELECT y, arg_min(w,pct), min(pct), arg_max(w,pct), max(pct) FROM s GROUP BY y ORDER BY y""",[p]).fetchall()
print(c.execute("SELECT year(crash_date), COUNT(*) * 100.0 / (SELECT COUNT(*) FROM read_parquet(?)) FROM read_parquet(?) WHERE crash_date < DATE '2013-01-01' OR crash_date >= DATE '2026-01-01' GROUP BY 1 ORDER BY 1",[p,p]).fetchall())
# bash
source = 'data/crashes.parquet'
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
base = """FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"""
# Overall weekday totals and proportions.
overall = con.execute(f"""SELECT strftime(crash_date, '%A') AS weekday, COUNT(*) AS crash_count
overall['weekday'] = pd.Categorical(overall['weekday'], categories=weekdays, ordered=True)
overall = overall.sort_values('weekday').reset_index(drop=True)
overall['share_of_selected_crashes_pct'] = overall['crash_count'] / overall['crash_count'].sum() * 100
overall['weekday'] = overall['weekday'].astype(str)
overall.to_csv(out / 'values_1.csv', index=False, float_format='%.6f')
# Annual weekday totals and shares.
annual = con.execute(f"""SELECT year(crash_date) AS year, strftime(crash_date, '%A') AS weekday, COUNT(*) AS crash_count
annual['weekday'] = pd.Categorical(annual['weekday'], categories=weekdays, ordered=True)
annual = annual.sort_values(['year', 'weekday']).reset_index(drop=True)
annual['share_of_year_crashes_pct'] = annual['crash_count'] / annual.groupby('year')['crash_count'].transform('sum') * 100
annual['weekday'] = annual['weekday'].astype(str)
annual.to_csv(out / 'values_2.csv', index=False, float_format='%.6f')
# Omitted-row accounting directly from the file.
omitted = con.execute("""SELECT year(crash_date) AS year, COUNT(*) AS row_count
WHERE crash_date < DATE '2013-01-01' OR crash_date >= DATE '2026-01-01'
# Verify the selected date field is complete and the years in scope are complete.
null_dates = con.execute(f"SELECT COUNT(*) {base} AND crash_date IS NULL", [source]).fetchone()[0]
# Chart 1: absolute burden and composition by weekday.
colors[weekdays.index(overall.loc[overall['crash_count'].idxmax(), 'weekday'])] = '#E45756'
bars = ax.barh(overall['weekday'], overall['crash_count'], color=colors, height=0.68)
ax.set_title('NYC reported crashes by weekday, 2013–2025', loc='left', fontsize=16, weight='bold', pad=14)
            bar.get_y() + bar.get_height() / 2,
ax.text(0, -0.15, f"Total: {overall['crash_count'].sum():,} crash records", transform=ax.transAxes, fontsize=9, color='#555555')
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
# Chart 2: within-year shares, with annual totals normalized out.
heat = annual.pivot(index='year', columns='weekday', values='share_of_year_crashes_pct').reindex(columns=weekdays)
            cbar_kws={'label': 'Share of crashes in that year (%)'}, ax=ax, vmin=11, vmax=17)
ax.set_title('Weekday share of NYC crashes in each year, 2013–2025', loc='left', fontsize=15, weight='bold', pad=14)
ax.set_xlabel('Day of week')
ax.set_ylabel('Year')
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
# Values for exact answer statements.
friday = overall.loc[overall['weekday'] == 'Friday'].iloc[0]
sunday = overall.loc[overall['weekday'] == 'Sunday'].iloc[0]
friday_range = annual.loc[annual['weekday'] == 'Friday', 'share_of_year_crashes_pct']
sunday_range = annual.loc[annual['weekday'] == 'Sunday', 'share_of_year_crashes_pct']
excl_text = ', '.join(f"{year}: {count:,} rows ({count / file_n * 100:.2f}%)" for year, count in omitted)
exclusion_sentence = f"The date filter leaves out {excl_text}; neither partial year is included, and no selected rows are omitted for a NULL date or weekday."
      'metric': 'Crash records per weekday, with share of all selected crash records shown',
      'denominator': 'All crash records dated 2013-01-01 through 2025-12-31 (2,132,218 records)',
      'grouping': 'Day of week pooled across 2013–2025',
      'reason': 'Pooled counts directly show the absolute volume and relative weekday mix across the full requested period.',
      'answer': f"Friday had the most crashes ({int(friday.crash_count):,}; {friday.share_of_selected_crashes_pct:.2f}% of the period total), while Sunday had the fewest ({int(sunday.crash_count):,}; {sunday.share_of_selected_crashes_pct:.2f}%).",
      'interpretation': f"This framing answers the overall distribution across weekdays: Friday leads with {int(friday.crash_count):,} records and Sunday has the fewest, out of {int(overall['crash_count'].sum()):,} selected crashes. It is defensible because pooled counts measure absolute reported crash volume and their displayed shares show each weekday's portion of that total. It leaves unanswered whether the weekday mix changes from year to year, since the chart pools the years. {exclusion_sentence}"
      'metric': 'Crash records for each weekday as a percentage of that calendar year’s crash records',
      'denominator': 'All crash records in the same year, for each year from 2013 through 2025',
      'grouping': 'Year by day of week',
      'reason': 'Year-specific shares make the weekday pattern comparable across years despite differences in annual crash totals.',
      'answer': f"Friday had the largest weekday share in all 13 years ({friday_range.min():.2f}%–{friday_range.max():.2f}%); Sunday had the smallest each year ({sunday_range.min():.2f}%–{sunday_range.max():.2f}%).",
      'interpretation': f"This framing answers how the weekday distribution looks within each year: Friday is the largest share in all 13 years ({friday_range.min():.2f}%–{friday_range.max():.2f}%), and Sunday is the smallest ({sunday_range.min():.2f}%–{sunday_range.max():.2f}%). It is defensible because each year's percentages use that year's total, making patterns comparable when annual crash totals differ. It leaves absolute year-to-year crash volume unanswered because the heatmap shows shares rather than counts. {exclusion_sentence}"
(out / 'options.json').write_text(json.dumps(options, indent=2) + '\n', encoding='utf-8')
print('overall rows:', len(overall), 'selected crashes:', int(overall['crash_count'].sum()), 'null dates:', null_dates)
print('yearly lowest/top checked:', (annual.loc[annual.groupby('year')['share_of_year_crashes_pct'].idxmin(), 'weekday'] == 'Sunday').all(), (annual.loc[annual.groupby('year')['share_of_year_crashes_pct'].idxmax(), 'weekday'] == 'Friday').all())
# bash
source = 'data/crashes.parquet'
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
base = """FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"""
overall = con.execute(f"""SELECT strftime(crash_date, '%A') AS weekday, COUNT(*) AS crash_count
overall['weekday'] = pd.Categorical(overall['weekday'], categories=weekdays, ordered=True)
overall = overall.sort_values('weekday').reset_index(drop=True)
overall['share_of_selected_crashes_pct'] = overall['crash_count'] / overall['crash_count'].sum() * 100
overall['weekday'] = overall['weekday'].astype(str)
overall.to_csv(out / 'values_1.csv', index=False, float_format='%.6f')
annual = con.execute(f"""SELECT year(crash_date) AS year, strftime(crash_date, '%A') AS weekday, COUNT(*) AS crash_count
annual['weekday'] = pd.Categorical(annual['weekday'], categories=weekdays, ordered=True)
annual = annual.sort_values(['year', 'weekday']).reset_index(drop=True)
annual['share_of_year_crashes_pct'] = annual['crash_count'] / annual.groupby('year')['crash_count'].transform('sum') * 100
annual['weekday'] = annual['weekday'].astype(str)
annual.to_csv(out / 'values_2.csv', index=False, float_format='%.6f')
omitted = con.execute("""SELECT year(crash_date) AS year, COUNT(*) AS row_count
WHERE crash_date < DATE '2013-01-01' OR crash_date >= DATE '2026-01-01'
null_dates = con.execute(f"SELECT COUNT(*) {base} AND crash_date IS NULL", [source]).fetchone()[0]
plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False})
max_weekday = overall.loc[overall['crash_count'].idxmax(), 'weekday']
colors = ['#E45756' if day == max_weekday else '#4C78A8' for day in overall['weekday']]
bars = ax.barh(overall['weekday'], overall['crash_count'], color=colors, height=0.68)
ax.set_title('NYC reported crashes by weekday, 2013–2025', loc='left', fontsize=16, weight='bold', pad=14)
            bar.get_y() + bar.get_height() / 2,
ax.text(0, -0.15, f"Total: {overall['crash_count'].sum():,} crash records", transform=ax.transAxes, fontsize=9, color='#555555')
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
heat = annual.pivot(index='year', columns='weekday', values='share_of_year_crashes_pct').reindex(columns=weekdays)
ax.set_xticks(range(len(weekdays)), weekdays)
ax.set_title('Weekday share of NYC crashes in each year, 2013–2025', loc='left', fontsize=15, weight='bold', pad=14)
ax.set_xlabel('Day of week')
ax.set_ylabel('Year')
cb.set_label('Share of crashes in that year (%)')
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
friday = overall.loc[overall['weekday'] == 'Friday'].iloc[0]
sunday = overall.loc[overall['weekday'] == 'Sunday'].iloc[0]
friday_range = annual.loc[annual['weekday'] == 'Friday', 'share_of_year_crashes_pct']
sunday_range = annual.loc[annual['weekday'] == 'Sunday', 'share_of_year_crashes_pct']
excl_text = ', '.join(f"{year}: {count:,} rows ({count / file_n * 100:.2f}%)" for year, count in omitted)
exclusion_sentence = f"The date filter leaves out {excl_text}; neither partial year is included, and no selected rows are omitted for a NULL date or weekday."
   'metric': 'Crash records per weekday, with share of all selected crash records shown',
   'denominator': 'All crash records dated 2013-01-01 through 2025-12-31
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
- tr_DAYCOUNT: If per-day averages or 'X% fewer on <day>' comparisons are given, the arithmetic is right (e.g. Sunday has 24% fewer than the mean weekday, Friday 32% more) and unequal day counts (678/679) are handled or noted.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.