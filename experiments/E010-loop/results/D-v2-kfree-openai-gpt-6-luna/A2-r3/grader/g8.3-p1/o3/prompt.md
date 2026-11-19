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

QUESTION ASKED: Are NYC's streets more dangerous at night? Make a chart and give a conclusion for a news report.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Persons injured plus persons killed per reported crash
denominator: All crashes with a reported crash time in each period
grouping: Day (6 a.m.–7:59 p.m.) vs. night (8 p.m.–5:59 a.m.)
chart_type: Two-bar comparison of average casualties per crash
probability: 0.2
WRITTEN ANSWER:
NYC recorded 0.408 people injured or killed per nighttime crash versus 0.311 per daytime crash, indicating a greater casualty burden per reported crash at night, not necessarily greater risk per trip. This measures the average number of people injured or killed in each reported crash, which was higher at night (0.408 vs. 0.311). It captures casualty burden per crash, but cannot establish danger per traveler or mile without traffic-exposure data.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
period,crashes,persons_injured,persons_killed,total_persons_injured_or_killed,persons_per_crash
Day (6 a.m.–7:59 p.m.),1710183,530247.00000000,1898.00000000,532145.00000000,0.31116261
Night (8 p.m.–5:59 a.m.),559004,226106.00000000,1719.00000000,227825.00000000,0.40755522

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("describe select * from read_parquet(?)", [p]).fetchall()); print(c.execute("select count(*) n, min(crash_date), max(crash_date), min(crash_time), max(crash_time), count(*) filter(where crash_time is null) null_times from read_parquet(?)", [p]).fetchall()); print(c.execute("select hour(crash_time) hr, count(*) crashes, sum(number_of_persons_injured) injured, sum(number_of_persons_killed) killed from read_parquet(?) group by 1 order by 1", [p]).fetchall())'
# bash
ls -ld . data && python3 -c 'import duckdb, matplotlib, pandas; print("duckdb", duckdb.__version__, "pandas", pandas.__version__, "matplotlib", matplotlib.__version__)'
# bash
python3 - <<'PY'
from pathlib import Path
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
query = '''
WITH tagged AS (
  SELECT
    CASE WHEN hour(crash_time) >= 20 OR hour(crash_time) < 6 THEN 'Night (8 p.m.–5:59 a.m.)'
         ELSE 'Day (6 a.m.–7:59 p.m.)' END AS period,
    coalesce(number_of_persons_injured, 0) AS injured,
    coalesce(number_of_persons_killed, 0) AS killed
  FROM read_parquet('data/crashes.parquet')
  WHERE crash_time IS NOT NULL
)
SELECT period,
       count(*) AS crashes,
       count(*) FILTER (WHERE injured > 0 OR killed > 0) AS injury_or_fatal_crashes,
       count(*) FILTER (WHERE killed > 0) AS fatal_crashes,
       sum(injured) AS persons_injured,
       sum(killed) AS persons_killed
FROM tagged
GROUP BY period
ORDER BY CASE WHEN period LIKE 'Day%' THEN 1 ELSE 2 END
'''
df = con.execute(query).df()
df['injury_or_fatal_rate_pct'] = df.injury_or_fatal_crashes / df.crashes * 100
df['fatal_crash_rate_pct'] = df.fatal_crashes / df.crashes * 100
df['casualties_per_crash'] = (df.persons_injured + df.persons_killed) / df.crashes

specs = [
    (1, 'injury_or_fatal_rate_pct', 'injury_or_fatal_crashes', 'Crashes with injury or death (%)', 'Share of reported crashes', 'Percent of crashes involving at least one person injured or killed', 'Percent of crashes', 'Blues'),
    (2, 'fatal_crash_rate_pct', 'fatal_crashes', 'Fatal crashes (%)', 'Share of reported crashes', 'Percent of crashes with at least one person killed', 'Percent of crashes', 'Reds'),
    (3, 'casualties_per_crash', None, 'People injured or killed per crash', 'Reported injured and killed persons / reported crashes', 'Injured and killed persons per reported crash', 'Persons per crash', 'Purples'),
]
for oid, value_col, num_col, title, denominator, metric, ylabel, cmap in specs:
    labels = ['Day\n6 a.m.–7:59 p.m.', 'Night\n8 p.m.–5:59 a.m.']
    vals = df[value_col].tolist()
    fig, ax = plt.subplots(figsize=(7.3, 4.8))
    bars = ax.bar(labels, vals, color=['#4C78A8', '#F28E2B'], width=0.58)
    ax.set_title(title, fontsize=14, pad=14)
    ax.set_ylabel(ylabel)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', alpha=0.22)
    ax.set_axisbelow(True)
    for i, bar in enumerate(bars):
        if num_col:
            annotation = f"{vals[i]:.2f}%\n({int(df.iloc[i][num_col]):,} / {int(df.iloc[i]['crashes']):,} crashes)"
        else:
            annotation = f"{vals[i]:.3f}\n({int(df.iloc[i]['persons_injured'] + df.iloc[i]['persons_killed']):,} people / {int(df.iloc[i]['crashes']):,} crashes)"
        ax.annotate(annotation, (bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 6), textcoords='offset points', ha='center', va='bottom', fontsize=9)
    ax.set_ylim(0, max(vals) * 1.26)
    fig.text(.5, .015, 'NYC police-reported crashes, July 2012–June 2026; time-of-day groups as labeled. No traffic-exposure adjustment.',
             ha='center', fontsize=8, color='#555555')
    fig.tight_layout(rect=(0, .06, 1, 1))
    fig.savefig(out / f'option_{oid}.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
    if num_col:
        value_table = pd.DataFrame({
            'period': df.period,
            'crashes': df.crashes,
            'metric_numerator_crashes': df[num_col],
            'metric_denominator_crashes': df.crashes,
            'metric_percent': df[value_col],
        })
    else:
        value_table = pd.DataFrame({
            'period': df.period,
            'crashes': df.crashes,
            'persons_injured': df.persons_injured,
            'persons_killed': df.persons_killed,
            'total_persons_injured_or_killed': df.persons_injured + df.persons_killed,
            'persons_per_crash': df[value_col],
        })
    value_table.to_csv(out / f'values_{oid}.csv', index=False, float_format='%.8f')

print(df.to_string(index=False))
PY
# bash
python3 -c 'import json; from pathlib import Path; p=Path("out"); d=json.loads((p/"options.json").read_text()); print("json valid:", len(d["options"]), "options; probability sum:", sum(x["probability"] for x in d["options"])); print("files:", [(f.name, f.stat().st_size) for f in sorted(p.iterdir())])'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR11: Severity per crash (deaths or injuries per crash) is described as such, not as the risk of being on the street at night (no traffic volume by hour exists).
- tr_TR08: NA if the option uses no killed or injured counts. Otherwise the analysis window excludes 2026, or the 2026 rows with NULL killed counts (87.8% of May-2026, 100% of June-2026) are excluded or the resulting bias is disclosed; COALESCE to 0 alone is not handling (decided by Bo 2026-11-04).
- tr_NIGHTDEF: The definition of 'night' (hours) is stated.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.