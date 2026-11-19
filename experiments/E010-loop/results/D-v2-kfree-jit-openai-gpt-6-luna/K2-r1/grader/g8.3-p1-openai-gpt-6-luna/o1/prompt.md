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
metric: Number of police-reported crashes
denominator: No denominator; total crash records during 2013–2025
grouping: Day of week
chart_type: Horizontal bar chart
probability: 0.65
WRITTEN ANSWER:
Friday had the most crashes (338,800, 15.9% of 2,132,218), while Sunday had the fewest (257,544, 12.1%). This framing answers how the total number of NYC police-reported crashes from 2013 through 2025 is divided among weekdays; the chart shows Friday highest and Sunday lowest. It is defensible when the interest is total recorded crash burden, but it does not adjust for how many dates each weekday has or traffic exposure.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crashes,share_of_crashes_pct
Monday,304518,14.282
Tuesday,313488,14.702
Wednesday,311111,14.591
Thursday,318376,14.932
Friday,338800,15.89
Saturday,288381,13.525
Sunday,257544,12.079

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls data && python3 -c 'import duckdb; print(duckdb.query("SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(\"data/crashes.parquet\")").fetchall())'
# bash
python3 -c 'import duckdb; q="""SELECT strftime(crash_date, \u0027%w\u0027) AS dow, dayname(crash_date) AS day, count(*) AS crashes, count(DISTINCT crash_date) AS observed_dates FROM read_parquet(\u0027data/crashes.parquet\u0027) WHERE crash_date >= DATE \u00272013-01-01\u0027 AND crash_date < DATE \u00272026-01-01\u0027 GROUP BY 1,2 ORDER BY 1"""; print(duckdb.query(q).df().to_string(index=False)); print(duckdb.query("SELECT count(*), min(crash_date), max(crash_date) FROM read_parquet(\u0027data/crashes.parquet\u0027) WHERE crash_date >= DATE \u00272013-01-01\u0027 AND crash_date < DATE \u00272026-01-01\u0027").fetchall())'
# bash
ls . && mkdir -p out && python3 -c 'import duckdb,pandas,matplotlib; print("dependencies ok")'
# bash
python3 - <<'PY'
import json
from pathlib import Path
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

out = Path('out')
out.mkdir(exist_ok=True)
query = """
SELECT CAST(strftime(crash_date, '%w') AS INTEGER) AS dow_sun0,
       COUNT(*) AS crashes
FROM read_parquet('data/crashes.parquet')
WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
GROUP BY 1
"""
counts = dict(duckdb.query(query).fetchall())
# Use a full calendar denominator, including any weekday dates with no reported crash rows.
days = pd.date_range('2013-01-01', '2025-12-31', freq='D')
weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
calendar_counts = {i: int((days.weekday == i).sum()) for i in range(7)}
rows = []
for i, name in enumerate(weekday_names):
    # DuckDB %w convention: Sunday=0; pandas weekday convention: Monday=0.
    sun0 = (i + 1) % 7
    n = int(counts.get(sun0, 0))
    rows.append({'weekday': name, 'crashes': n, 'share_of_crashes_pct': 100*n/sum(counts.values()),
                 'calendar_days': calendar_counts[i], 'crashes_per_calendar_day': n/calendar_counts[i]})
df = pd.DataFrame(rows)

total = int(df.crashes.sum())
assert total == 2132218
# Option 1: total counts
opt1 = df[['weekday', 'crashes', 'share_of_crashes_pct']].copy()
opt1['share_of_crashes_pct'] = opt1.share_of_crashes_pct.round(3)
opt1.to_csv(out/'values_1.csv', index=False)
fig, ax = plt.subplots(figsize=(9, 5.2))
bars = ax.barh(df.weekday, df.crashes, color='#31688e')
ax.invert_yaxis()
ax.set_title('NYC police-reported crashes by weekday, 2013–2025')
ax.set_xlabel('Number of crashes')
ax.set_ylabel('Day of week')
ax.xaxis.grid(True, alpha=.25)
ax.set_axisbelow(True)
ax.bar_label(bars, labels=[f'{v:,.0f}' for v in df.crashes], padding=4, fontsize=9)
ax.set_xlim(0, df.crashes.max()*1.15)
fig.tight_layout()
fig.savefig(out/'option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Option 2: average daily count, normalized for the number of calendar instances of each weekday.
opt2 = df[['weekday', 'crashes', 'calendar_days', 'crashes_per_calendar_day']].copy()
opt2['crashes_per_calendar_day'] = opt2.crashes_per_calendar_day.round(3)
opt2.to_csv(out/'values_2.csv', index=False)
fig, ax = plt.subplots(figsize=(9, 5.2))
bars = ax.barh(df.weekday, df.crashes_per_calendar_day, color='#35a779')
ax.invert_yaxis()
ax.set_title('Average NYC crashes per calendar date by weekday, 2013–2025')
ax.set_xlabel('Crashes per date (weekday totals ÷ calendar dates)')
ax.set_ylabel('Day of week')
ax.xaxis.grid(True, alpha=.25)
ax.set_axisbelow(True)
ax.bar_label(bars, labels=[f'{v:.1f}' for v in df.crashes_per_calendar_day], padding=4, fontsize=9)
ax.set_xlim(0, df.crashes_per_calendar_day.max()*1.15)
fig.tight_layout()
fig.savefig(out/'option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)

friday = df.loc[df.weekday == 'Friday'].iloc[0]
sunday = df.loc[df.weekday == 'Sunday'].iloc[0]
options = {'options': [
    {'id': 1, 'metric': 'Number of police-reported crashes', 'denominator': 'No denominator; total crash records during 2013–2025', 'grouping': 'Day of week', 'chart_type': 'Horizontal bar chart',
     'reason': 'Total counts directly show how the recorded crash burden is distributed across weekdays over the requested period.',
     'probability': 0.65,
     'answer': f"Friday had the most crashes ({int(friday.crashes):,}, {friday.share_of_crashes_pct:.1f}% of {total:,}), while Sunday had the fewest ({int(sunday.crashes):,}, {sunday.share_of_crashes_pct:.1f}%).",
     'interpretation': 'This framing answers how the total number of NYC police-reported crashes from 2013 through 2025 is divided among weekdays; the chart shows Friday highest and Sunday lowest. It is defensible when the interest is total recorded crash burden, but it does not adjust for how many dates each weekday has or traffic exposure.'},
    {'id': 2, 'metric': 'Average number of police-reported crashes per calendar date', 'denominator': 'Number of calendar dates of each weekday from 2013-01-01 through 2025-12-31', 'grouping': 'Day of week', 'chart_type': 'Horizontal bar chart',
     'reason': 'A per-date average adjusts for the slight differences in how often each weekday occurs in the 13-year period.',
     'probability': 0.35,
     'answer': f"Friday averaged {friday.crashes_per_calendar_day:.1f} crashes per date, the highest, while Sunday averaged {sunday.crashes_per_calendar_day:.1f}, the lowest.",
     'interpretation': 'This framing answers which weekday tends to have more recorded crashes on a typical calendar date, accounting for weekday date counts; Friday is highest and Sunday lowest on that basis. It is defensible as a normalized weekday comparison, but it does not measure risk per trip, vehicle, or mile traveled.'}
]}
(out/'options.json').write_text(json.dumps(options, indent=2) + '\n')
print(df.to_string(index=False))
print('Total:', total)
PY
# bash
python3 -c 'import json,pandas as pd; from pathlib import Path; p=Path("out"); o=json.loads((p/"options.json").read_text()); assert abs(sum(x["probability"] for x in o["options"])-1)<1e-9; assert all((p/f"option_{i}.png").is_file() and (p/f"values_{i}.csv").is_file() for i in (1,2)); a=pd.read_csv(p/"values_1.csv"); b=pd.read_csv(p/"values_2.csv"); assert a.loc[a.crashes.idxmax(),"weekday"]=="Friday" and a.loc[a.crashes.idxmin(),"weekday"]=="Sunday"; assert b.loc[b.crashes_per_calendar_day.idxmax(),"weekday"]=="Friday" and b.loc[b.crashes_per_calendar_day.idxmin(),"weekday"]=="Sunday"; print("Validated JSON, probabilities, CSVs, chart files, and weekday conclusions.")'

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