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
metric: Category share of combined motorist and cyclist deaths
denominator: Motorist deaths plus cyclist deaths in that year
grouping: Year, with motorist and cyclist shares
chart_type: 100% stacked bar chart
probability: 0.35
WRITTEN ANSWER:
Motorists made up the majority of combined motorist-and-cyclist deaths every year, while the cyclist share ranged from 9.1% in 2013 to 27.4% in 2019. This view answers how the two categories compare as a share of their combined deaths: cyclists accounted for 9.1%–27.4%, with the highest share in 2019, and motorists remained the majority each year. The fixed denominator makes relative composition clear, but it leaves out changes in the absolute annual death counts and is not a share of all people killed in crashes.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,cyclist_deaths,combined_deaths,motorist_share_pct,cyclist_share_pct
2013,110,11,121,90.9091,9.0909
2014,109,20,129,84.4961,15.5039
2015,95,15,110,86.3636,13.6364
2016,72,18,90,80.0000,20.0000
2017,107,27,134,79.8507,20.1493
2018,98,10,108,90.7407,9.2593
2019,82,31,113,72.5664,27.4336
2020,139,29,168,82.7381,17.2619
2021,134,19,153,87.5817,12.4183
2022,116,19,135,85.9259,14.0741
2023,123,31,154,79.8701,20.1299
2024,111,24,135,82.2222,17.7778
2025,81,23,104,77.8846,22.1154

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__); print('pandas', pandas.__version__); print('matplotlib', matplotlib.__version__)"
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"SELECT year(crash_date) AS year, sum(number_of_motorist_killed) AS motorist_deaths, sum(number_of_cyclist_killed) AS cyclist_deaths, sum(number_of_persons_killed) AS all_persons_killed, count(*) AS crashes, count(*) FILTER (WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL) AS null_counts FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").df().to_string(index=False)")
# bash
python3 -c 'import duckdb; q="""SELECT year(crash_date) AS year, sum(number_of_motorist_killed) AS motorist_deaths, sum(number_of_cyclist_killed) AS cyclist_deaths, sum(number_of_persons_killed) AS all_persons_killed, count(*) AS crashes, count(*) FILTER (WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL) AS null_counts FROM read_parquet(\"data/crashes.parquet\") WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1"""; print(duckdb.sql(q).df().to_string(index=False))'
# bash
ls -la
# bash
python3 - <<'PY'
import duckdb
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True)
df = duckdb.sql('''
SELECT year(crash_date) AS year,
       sum(number_of_motorist_killed)::INTEGER AS motorist_deaths,
       sum(number_of_cyclist_killed)::INTEGER AS cyclist_deaths
FROM read_parquet('data/crashes.parquet')
WHERE year(crash_date) BETWEEN 2013 AND 2025
GROUP BY 1 ORDER BY 1
''').df()
df['combined_deaths'] = df.motorist_deaths + df.cyclist_deaths
df['motorist_share_pct'] = df.motorist_deaths / df.combined_deaths * 100
df['cyclist_share_pct'] = df.cyclist_deaths / df.combined_deaths * 100

# Option 1: annual absolute death counts, grouped bars.
df[['year', 'motorist_deaths', 'cyclist_deaths']].to_csv(out / 'values_1.csv', index=False)
x = np.arange(len(df))
width = 0.37
fig, ax = plt.subplots(figsize=(11, 5.8), layout='constrained')
b1 = ax.bar(x - width/2, df.motorist_deaths, width, label='Motorist deaths', color='#315a7d')
b2 = ax.bar(x + width/2, df.cyclist_deaths, width, label='Cyclist deaths', color='#e28e2c')
ax.set_title('Motorist and cyclist deaths in NYC, 2013–2025')
ax.set_ylabel('Deaths (people)')
ax.set_xlabel('Year')
ax.set_xticks(x, df.year.astype(str))
ax.set_ylim(0, 155)
ax.grid(axis='y', alpha=.25)
ax.set_axisbelow(True)
ax.legend(frameon=False, ncol=2, loc='upper left')
fig.savefig(out / 'option_1.png', dpi=180)
plt.close(fig)

# Option 2: annual share of the combined motorist + cyclist deaths.
df[['year', 'motorist_deaths', 'cyclist_deaths', 'combined_deaths', 'motorist_share_pct', 'cyclist_share_pct']].to_csv(out / 'values_2.csv', index=False, float_format='%.4f')
fig, ax = plt.subplots(figsize=(11, 5.8), layout='constrained')
ax.bar(x, df.motorist_share_pct, label='Motorist share', color='#315a7d')
ax.bar(x, df.cyclist_share_pct, bottom=df.motorist_share_pct, label='Cyclist share', color='#e28e2c')
ax.set_title('Share of combined motorist and cyclist deaths in NYC, 2013–2025')
ax.set_ylabel('Share of motorist + cyclist deaths (%)')
ax.set_xlabel('Year')
ax.set_xticks(x, df.year.astype(str))
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=.25)
ax.set_axisbelow(True)
ax.legend(frameon=False, ncol=2, loc='upper right')
fig.savefig(out / 'option_2.png', dpi=180)
plt.close(fig)
print(df.to_string(index=False, formatters={'motorist_share_pct': '{:.2f}'.format, 'cyclist_share_pct': '{:.2f}'.format}))
PY
# bash
python3 - <<'PY'
import duckdb
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

df = duckdb.sql('''
SELECT year(crash_date) AS year,
       sum(number_of_motorist_killed)::INTEGER AS motorist_deaths,
       sum(number_of_cyclist_killed)::INTEGER AS cyclist_deaths
FROM read_parquet('data/crashes.parquet')
WHERE year(crash_date) BETWEEN 2013 AND 2025
GROUP BY 1 ORDER BY 1
''').df()
df['combined_deaths'] = df.motorist_deaths + df.cyclist_deaths
df['motorist_share_pct'] = df.motorist_deaths / df.combined_deaths * 100
df['cyclist_share_pct'] = df.cyclist_deaths / df.combined_deaths * 100
x = np.arange(len(df))
fig, ax = plt.subplots(figsize=(11, 5.8), layout='constrained')
ax.bar(x, df.motorist_share_pct, label='Motorist share', color='#315a7d')
ax.bar(x, df.cyclist_share_pct, bottom=df.motorist_share_pct, label='Cyclist share', color='#e28e2c')
ax.set_title('Share of combined motorist and cyclist deaths in NYC, 2013–2025')
ax.set_ylabel('Share of motorist + cyclist deaths (%)')
ax.set_xlabel('Year')
ax.set_xticks(x, df.year.astype(str))
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=.25)
ax.set_axisbelow(True)
ax.legend(frameon=False, ncol=2, loc='lower center', bbox_to_anchor=(0.5, 1.01))
fig.savefig(Path('out/option_2.png'), dpi=180)
plt.close(fig)
PY
# bash
python3 -c 'import json; d=json.load(open("out/options.json")); print("valid JSON; probability sum =", sum(x["probability"] for x in d["options"])); print("files =", __import__("os").listdir("out"))'
# bash
python3 - <<'PY'
import duckdb
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

df = duckdb.sql('''SELECT year(crash_date) AS year, sum(number_of_motorist_killed)::INTEGER AS motorist_deaths, sum(number_of_cyclist_killed)::INTEGER AS cyclist_deaths FROM read_parquet('data/crashes.parquet') WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1''').df()
total = df.motorist_deaths + df.cyclist_deaths
mshare = df.motorist_deaths / total * 100
cshare = df.cyclist_deaths / total * 100
x = np.arange(len(df))
fig, ax = plt.subplots(figsize=(11, 5.8), layout='constrained')
ax.bar(x, mshare, label='Motorist share', color='#315a7d')
ax.bar(x, cshare, bottom=mshare, label='Cyclist share', color='#e28e2c')
ax.set_title('Share of combined motorist and cyclist deaths in NYC, 2013–2025', pad=42)
ax.set_ylabel('Share of motorist + cyclist deaths (%)')
ax.set_xlabel('Year')
ax.set_xticks(x, df.year.astype(str))
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=.25)
ax.set_axisbelow(True)
ax.legend(frameon=False, ncol=2, loc='lower center', bbox_to_anchor=(0.5, 1.01))
fig.savefig(Path('out/option_2.png'), dpi=180)
plt.close(fig)
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
- tr_TR15: Claims about cyclist deaths changing sharply (e.g. 'tripled') are qualified by the small counts (10 → 31).
- tr_TR03: The output does not claim that motorist + cyclist deaths are all deaths (pedestrians and unclassified deaths exist).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.