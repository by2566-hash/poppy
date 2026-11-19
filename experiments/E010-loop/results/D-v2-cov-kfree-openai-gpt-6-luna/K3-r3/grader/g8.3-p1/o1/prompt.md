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
metric: Annual number of motorist deaths and cyclist deaths
denominator: None (absolute death counts)
grouping: Calendar year and road-user type
chart_type: Grouped bar chart
probability: 0.7
WRITTEN ANSWER:
Motorist deaths exceeded cyclist deaths in all 13 years; the counts ranged from 72–139 motorist deaths and 10–31 cyclist deaths, and were 81 versus 23 in 2025. The grouped bars answer the year-by-year comparison in absolute numbers: motorist deaths exceeded cyclist deaths in every year, including 81 versus 23 in 2025. This is a defensible framing because the question asks how the annual death counts compare, while retaining the size of the difference. It does not express the cyclist count relative to the motorist count or adjust deaths for exposure, population, or crash volume. No in-period rows are omitted for NULL death counts (0 of 2,132,218, 0.00%); all rows outside 2013–2025 are excluded (2012: 100,545 rows (4.43% of file); 2026: 36,424 rows (1.61% of file)), and no included year is partial.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
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
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT count(*) n, min(crash_date), max(crash_date), count(*) FILTER (WHERE crash_date IS NULL) date_null, count(*) FILTER (WHERE number_of_motorist_killed IS NULL) motorist_null, count(*) FILTER (WHERE number_of_cyclist_killed IS NULL) cyclist_null FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT year(crash_date) yr, count(*) crashes, count(*) FILTER (WHERE number_of_motorist_killed IS NULL) motorist_null, count(*) FILTER (WHERE number_of_cyclist_killed IS NULL) cyclist_null, sum(number_of_motorist_killed) motorist_killed, sum(number_of_cyclist_killed) cyclist_killed, min(crash_date) min_date, max(crash_date) max_date FROM read_parquet(?) GROUP BY yr ORDER BY yr", [p]).fetchdf().to_string(index=False))'
# bash
python3 - <<'PY'
import json
from pathlib import Path
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

root = Path('.')
out = root / 'out'
out.mkdir(exist_ok=True)
path = root / 'data' / 'crashes.parquet'
con = duckdb.connect()
annual = con.execute('''
    SELECT year(crash_date)::INTEGER AS year,
           sum(number_of_motorist_killed)::BIGINT AS motorist_deaths,
           sum(number_of_cyclist_killed)::BIGINT AS cyclist_deaths,
           count(*)::BIGINT AS crash_rows,
           count(*) FILTER (WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL)::BIGINT AS missing_death_rows
    FROM read_parquet(?)
    WHERE year(crash_date) BETWEEN 2013 AND 2025
    GROUP BY year
    ORDER BY year
''', [str(path)]).fetchdf()
annual['year'] = annual['year'].astype(int)
annual['motorist_deaths'] = annual['motorist_deaths'].astype(int)
annual['cyclist_deaths'] = annual['cyclist_deaths'].astype(int)
annual['crash_rows'] = annual['crash_rows'].astype(int)
annual['missing_death_rows'] = annual['missing_death_rows'].astype(int)
assert annual['year'].tolist() == list(range(2013, 2026))

# Export option 1 values and chart.
values1 = annual[['year', 'motorist_deaths', 'cyclist_deaths']].copy()
values1.to_csv(out / 'values_1.csv', index=False)
x = np.arange(len(values1))
width = 0.38
fig, ax = plt.subplots(figsize=(11, 5.8), layout='constrained')
ax.bar(x - width/2, values1['motorist_deaths'], width, label='Motorist deaths', color='#3767A6')
ax.bar(x + width/2, values1['cyclist_deaths'], width, label='Cyclist deaths', color='#E58B36')
ax.set_title('Motorist and cyclist deaths by year in NYC (2013–2025)')
ax.set_xlabel('Crash year')
ax.set_ylabel('Deaths (sum of reported crash deaths)')
ax.set_xticks(x, values1['year'])
ax.set_ylim(0, max(values1['motorist_deaths']) * 1.16)
ax.grid(axis='y', alpha=.25)
ax.legend(frameon=False, ncols=2, loc='upper right')
fig.savefig(out / 'option_1.png', dpi=180)
plt.close(fig)

# Export option 2 values and chart.
values2 = annual[['year', 'motorist_deaths', 'cyclist_deaths']].copy()
values2['cyclist_as_pct_of_motorist'] = values2['cyclist_deaths'] / values2['motorist_deaths'] * 100
values2.to_csv(out / 'values_2.csv', index=False, float_format='%.4f')
fig, ax = plt.subplots(figsize=(11, 5.8), layout='constrained')
ax.plot(values2['year'], values2['cyclist_as_pct_of_motorist'], marker='o', linewidth=2.4, color='#7A4E9B')
ax.set_title('Cyclist deaths relative to motorist deaths in NYC (2013–2025)')
ax.set_xlabel('Crash year')
ax.set_ylabel('Cyclist deaths as % of motorist deaths')
ax.set_xticks(values2['year'])
ax.set_ylim(0, max(values2['cyclist_as_pct_of_motorist']) * 1.25)
ax.grid(alpha=.25)
for _, r in values2.iterrows():
    ax.annotate(f"{r['cyclist_as_pct_of_motorist']:.0f}%", (r['year'], r['cyclist_as_pct_of_motorist']), xytext=(0, 7), textcoords='offset points', ha='center', fontsize=8)
fig.savefig(out / 'option_2.png', dpi=180)
plt.close(fig)

# Compute coverage and missing-value omission shares for exact caveats.
coverage = con.execute('''
    SELECT year(crash_date)::INTEGER AS year, count(*)::BIGINT AS rows
    FROM read_parquet(?)
    WHERE year(crash_date) NOT BETWEEN 2013 AND 2025
    GROUP BY year ORDER BY year
''', [str(path)]).fetchdf()
file_rows = int(con.execute('SELECT count(*) FROM read_parquet(?)', [str(path)]).fetchone()[0])
all_in = int(annual['crash_rows'].sum())
missing_in = int(annual['missing_death_rows'].sum())
excluded_text = '; '.join(f"{int(r.year)}: {int(r.rows):,} rows ({100*int(r.rows)/file_rows:.2f}% of file)" for r in coverage.itertuples())
missing_share = 100 * missing_in / all_in if all_in else 0

m = values1['motorist_deaths']
c = values1['cyclist_deaths']
peak_ratio_idx = values2['cyclist_as_pct_of_motorist'].idxmax()
peak = values2.loc[peak_ratio_idx]
last = values2.iloc[-1]
min_motor_idx = values1['motorist_deaths'].idxmin()
options = {
    'options': [
        {
            'id': 1,
            'metric': 'Annual number of motorist deaths and cyclist deaths',
            'denominator': 'None (absolute death counts)',
            'grouping': 'Calendar year and road-user type',
            'chart_type': 'Grouped bar chart',
            'reason': 'Absolute counts directly answer how many motorist and cyclist deaths were reported in each year.',
            'probability': 0.7,
            'answer': f"Motorist deaths exceeded cyclist deaths in all 13 years; the counts ranged from {int(m.min())}–{int(m.max())} motorist deaths and {int(c.min())}–{int(c.max())} cyclist deaths, and were {int(last.motorist_deaths)} versus {int(last.cyclist_deaths)} in 2025.",
            'interpretation': f"The grouped bars answer the year-by-year comparison in absolute numbers: motorist deaths exceeded cyclist deaths in every year, including {int(last.motorist_deaths)} versus {int(last.cyclist_deaths)} in 2025. This is a defensible framing because the question asks how the annual death counts compare, while retaining the size of the difference. It does not express the cyclist count relative to the motorist count or adjust deaths for exposure, population, or crash volume. No in-period rows are omitted for NULL death counts ({missing_in:,} of {all_in:,}, {missing_share:.2f}%); all rows outside 2013–2025 are excluded ({excluded_text}), and no included year is partial.",
        },
        {
            'id': 2,
            'metric': 'Cyclist deaths as a percentage of motorist deaths',
            'denominator': 'Annual motorist deaths',
            'grouping': 'Calendar year',
            'chart_type': 'Line chart',
            'reason': 'A ratio makes the relative scale of cyclist deaths against motorist deaths easy to compare across years.',
            'probability': 0.3,
            'answer': f"Cyclist deaths peaked relative to motorist deaths in {int(peak.year)} at {peak.cyclist_as_pct_of_motorist:.1f}% ({int(peak.cyclist_deaths)} versus {int(peak.motorist_deaths)}), and were {last.cyclist_as_pct_of_motorist:.1f}% ({int(last.cyclist_deaths)} versus {int(last.motorist_deaths)}) in 2025.",
            'interpretation': f"The line shows the year-by-year relative comparison: cyclist deaths were highest against motorist deaths in {int(peak.year)} at {peak.cyclist_as_pct_of_motorist:.1f}%, and stood at {last.cyclist_as_pct_of_motorist:.1f}% in 2025. This ratio is defensible because it compares cyclist deaths with the motorist-death count within each year, making the relative gap visible over time. It leaves the absolute number of deaths less prominent, so a similar ratio can represent different annual totals. No in-period rows are omitted for NULL death counts ({missing_in:,} of {all_in:,}, {missing_share:.2f}%); all rows outside 2013–2025 are excluded ({excluded_text}), and no included year is partial.",
        }
    ]
}
with open(out / 'options.json', 'w', encoding='utf-8') as f:
    json.dump(options, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('Annual values:')
print(annual[['year', 'motorist_deaths', 'cyclist_deaths']].to_string(index=False))
print(f'Rows in requested years: {all_in:,}; death-field NULL rows omitted: {missing_in:,} ({missing_share:.2f}%).')
print(f'Rows outside interval: {excluded_text}; file total {file_rows:,}.')
print(f'Peak ratio: {int(peak.year)} {peak.cyclist_as_pct_of_motorist:.4f}% ({int(peak.cyclist_deaths)}/{int(peak.motorist_deaths)}).')
PY
# bash
python3 -c 'import json, pathlib; p=pathlib.Path("out"); x=json.loads((p/"options.json").read_text()); assert abs(sum(o["probability"] for o in x["options"])-1)<1e-9; assert all((p/f"option_{i}.png").is_file() and (p/f"values_{i}.csv").is_file() for i in (1,2)); print("JSON valid; probability sum:", sum(o["probability"] for o in x["options"])); print("Output files:", ", ".join(sorted(f.name for f in p.iterdir())))'

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