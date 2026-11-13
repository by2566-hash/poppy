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

QUESTION ASKED: How many pedestrians were killed in NYC motor vehicle crashes each year from 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Annual total pedestrians killed (sum of number_of_pedestrians_killed)
denominator: All crash records in each calendar year; the metric is a sum, not a rate
grouping: Calendar year, 2013–2025
chart_type: Line chart with markers
probability: 0.35
WRITTEN ANSWER:
Pedestrians killed by year: 2013: 176; 2014: 133; 2015: 133; 2016: 149; 2017: 127; 2018: 123; 2019: 131; 2020: 101; 2021: 132; 2022: 135; 2023: 107; 2024: 124; 2025: 119. This framing answers the requested year-by-year count and highlights its movement over time, with a high of 176 in 2013 and a low of 101 in 2020. It is defensible because the years are sequential and the connected markers show the direction and size of changes between annual totals. It does not answer how pedestrian fatality risk changed relative to population, walking volume, or vehicle travel, because those exposure denominators are absent. It excludes rows outside the requested years—2012: 100,545 rows (4.43% of all file rows); 2026: 36,424 rows (1.61% of all file rows); it excludes no 2013–2025 rows for NULL crash dates or pedestrian-fatality counts, and no included year is partial.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,pedestrians_killed
2013,176
2014,133
2015,133
2016,149
2017,127
2018,123
2019,131
2020,101
2021,132
2022,135
2023,107
2024,124
2025,119

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"
# bash
ls -ld . data && mkdir -p out && python3 -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"SELECT year(crash_date) AS year, count(*) AS crash_rows, sum(number_of_pedestrians_killed) AS pedestrians_killed, count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS null_pedestrian_killed, count(*) FILTER (WHERE crash_date IS NULL) AS null_crash_date FROM read_parquet('{p}') WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1\").df().to_string(index=False)); print('ALL_ROWS',duckdb.sql(f\"SELECT count(*) FROM read_parquet('{p}')\").fetchone()[0]); print('OUTSIDE',duckdb.sql(f\"SELECT year(crash_date) AS year, count(*) AS rows FROM read_parquet('{p}') WHERE year(crash_date) NOT BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1\").df().to_string(index=False))"
# bash
python3 - <<'PY'
import json
from pathlib import Path
import duckdb
import matplotlib.pyplot as plt

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
df = con.execute("""
    SELECT year(crash_date)::INTEGER AS year,
           sum(number_of_pedestrians_killed)::BIGINT AS pedestrians_killed
    FROM read_parquet('data/crashes.parquet')
    WHERE year(crash_date) BETWEEN 2013 AND 2025
    GROUP BY 1 ORDER BY 1
""").df()
assert df['year'].tolist() == list(range(2013, 2026))

# Persist exact plotted values independently for each framing.
for option_id in (1, 2):
    df.to_csv(out / f'values_{option_id}.csv', index=False)

years = df['year'].tolist()
counts = df['pedestrians_killed'].tolist()

plt.figure(figsize=(10, 5.5))
plt.bar(years, counts, color='#2878A5', width=0.72)
plt.title('Pedestrians killed in NYC motor vehicle crashes by year')
plt.xlabel('Crash year')
plt.ylabel('Pedestrians killed (people)')
plt.xticks(years, rotation=45)
plt.yticks(range(0, 201, 25))
plt.grid(axis='y', alpha=0.25)
plt.tight_layout()
plt.savefig(out / 'option_1.png', dpi=160)
plt.close()

plt.figure(figsize=(10, 5.5))
plt.plot(years, counts, color='#B14B31', marker='o', linewidth=2)
plt.title('Annual trend in pedestrians killed in NYC motor vehicle crashes')
plt.xlabel('Crash year')
plt.ylabel('Pedestrians killed (people)')
plt.xticks(years, rotation=45)
plt.yticks(range(0, 201, 25))
plt.grid(alpha=0.25)
plt.tight_layout()
plt.savefig(out / 'option_2.png', dpi=160)
plt.close()

all_rows = con.execute("SELECT count(*) FROM read_parquet('data/crashes.parquet')").fetchone()[0]
outside = con.execute("""
    SELECT year(crash_date)::INTEGER AS year, count(*) AS n
    FROM read_parquet('data/crashes.parquet')
    WHERE year(crash_date) NOT BETWEEN 2013 AND 2025
    GROUP BY 1 ORDER BY 1
""").df()
exclusion = '; '.join(f"{int(r.year)}: {int(r.n):,} rows ({100*r.n/all_rows:.2f}% of all file rows)" for r in outside.itertuples())
answer = 'Pedestrians killed by year: ' + '; '.join(f'{y}: {n}' for y, n in zip(years, counts)) + '.'
interp_tail = (f"It excludes rows outside the requested years—{exclusion}; it excludes no 2013–2025 rows for NULL crash dates or pedestrian-fatality counts, and no included year is partial.")
options = {
    'options': [
        {
            'id': 1,
            'metric': 'Annual total pedestrians killed (sum of number_of_pedestrians_killed)',
            'denominator': 'All crash records in each calendar year; the metric is a sum, not a rate',
            'grouping': 'Calendar year, 2013–2025',
            'chart_type': 'Vertical bar chart',
            'reason': 'A bar chart makes the requested discrete year-by-year totals easy to compare.',
            'probability': 0.65,
            'answer': answer,
            'interpretation': 'This framing answers the requested year-by-year count; the annual totals are highest in 2013 (176) and lowest in 2020 (101). It is defensible because it sums the pedestrian-killed field across all crash records for each requested calendar year, and bars make discrete annual values straightforward to compare. It does not answer how pedestrian fatality risk changed relative to population, walking volume, or vehicle travel, because those exposure denominators are absent. ' + interp_tail
        },
        {
            'id': 2,
            'metric': 'Annual total pedestrians killed (sum of number_of_pedestrians_killed)',
            'denominator': 'All crash records in each calendar year; the metric is a sum, not a rate',
            'grouping': 'Calendar year, 2013–2025',
            'chart_type': 'Line chart with markers',
            'reason': 'A line chart emphasizes how the requested annual count rises and falls over time.',
            'probability': 0.35,
            'answer': answer,
            'interpretation': 'This framing answers the requested year-by-year count and highlights its movement over time, with a high of 176 in 2013 and a low of 101 in 2020. It is defensible because the years are sequential and the connected markers show the direction and size of changes between annual totals. It does not answer how pedestrian fatality risk changed relative to population, walking volume, or vehicle travel, because those exposure denominators are absent. ' + interp_tail
        }
    ]
}
assert abs(sum(x['probability'] for x in options['options']) - 1) < 1e-12
(out / 'options.json').write_text(json.dumps(options, indent=2) + '\n')
print('Created charts, CSVs, and options.json')
print('Pedestrian fatality counts:', dict(zip(years, counts)))
print('Excluded years:', exclusion)
print('Total:', sum(counts))
PY
# bash
python3 - <<'PY'
import csv, json
from pathlib import Path
out = Path('out')
opts = json.loads((out / 'options.json').read_text())['options']
assert len(opts) == 2 and abs(sum(o['probability'] for o in opts) - 1) < 1e-12
for i in (1, 2):
    rows = list(csv.DictReader((out / f'values_{i}.csv').open()))
    assert [int(r['year']) for r in rows] == list(range(2013, 2026))
    counts = [int(r['pedestrians_killed']) for r in rows]
    assert f"2013: {counts[0]}" in opts[i-1]['answer'] and f"2025: {counts[-1]}" in opts[i-1]['answer']
    assert (out / f'option_{i}.png').is_file() and (out / f'option_{i}.png').stat().st_size > 0
    assert opts[i-1]['id'] == i and len(opts[i-1]['interpretation'].split('. ')) == 4
print('Validated JSON structure, probability total, plotted year ranges/counts, answer anchors, chart files, and four-sentence interpretations.')
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
- tr_TR07: The output does not present the open-data death counts as the official NYC toll. The counts are qualified when the written output (answer, interpretation or declared framing fields) ties them to this data in any wording: reported, recorded, police-reported crashes, in this dataset (e.g. 'pedestrians killed in reported motor vehicle crashes' qualifies). A qualification or source note that appears only inside the chart image does not count, and a chart title without one is fine when the written output has it. FAIL only when no such qualification appears in the written output (Bo 2026-11-04, refined 2026-11-06).
- tr_CAUSAL: The output makes no causal attribution (e.g. 'because of the pandemic') that the data cannot support.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.