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
denominator: None; total crash records from 2013-01-01 through 2025-12-31
grouping: Weekday (Monday through Sunday)
chart_type: Bar chart
probability: 0.62
WRITTEN ANSWER:
Thursday had the most recorded crashes (338,800), while Saturday had the fewest (257,544) from 2013 through 2025. This framing answers how the total number of police-reported crashes is distributed across weekdays, with Thursday highest and Saturday lowest. Totals are a direct summary of recorded crash volume over the requested period. It does not adjust for how many calendar dates of each weekday occurred or show year-to-year changes.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crashes
Monday,313488
Tuesday,311111
Wednesday,318376
Thursday,338800
Friday,288381
Saturday,257544
Sunday,304518

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"select min(crash_date), max(crash_date), count(*), count(distinct crash_date) from read_parquet('{p}')\").fetchall()); print(c.execute(f\"select year(crash_date) yr, count(*) n, min(crash_date), max(crash_date) from read_parquet('{p}') group by yr order by yr\").fetchdf().to_string(index=False)); print(c.execute(f\"select dayofweek(crash_date) dow, dayname(crash_date) day, count(*) n from read_parquet('{p}') where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by dow, day order by dow\").fetchdf().to_string(index=False))"
# bash
ls
# bash
python - <<'PY'
from datetime import date, timedelta
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

out = Path("out")
out.mkdir(exist_ok=True)
con = duckdb.connect()
raw = con.execute("""
    SELECT CASE dayofweek(crash_date)
             WHEN 1 THEN 'Sunday'
             WHEN 2 THEN 'Monday'
             WHEN 3 THEN 'Tuesday'
             WHEN 4 THEN 'Wednesday'
             WHEN 5 THEN 'Thursday'
             WHEN 6 THEN 'Friday'
             WHEN 0 THEN 'Saturday'
           END AS weekday,
           count(*)::BIGINT AS crashes
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY dayofweek(crash_date)
""").fetchdf()
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
raw = raw.set_index("weekday").reindex(order).reset_index()
raw["crashes"] = raw["crashes"].astype("int64")

occurrences = {day: 0 for day in order}
d = date(2013, 1, 1)
end = date(2025, 12, 31)
while d <= end:
    occurrences[d.strftime("%A")] += 1
    d += timedelta(days=1)
per_day = raw.copy()
per_day["weekday_dates"] = per_day["weekday"].map(occurrences).astype("int64")
per_day["mean_crashes_per_date"] = per_day["crashes"] / per_day["weekday_dates"]

plt.rcParams.update({"font.size": 10, "axes.titlesize": 13, "axes.labelsize": 11})
for idx, (df, metric, title, ylabel, fmt) in enumerate([
    (raw, "crashes", "NYC police-reported crashes by weekday, 2013–2025", "Crashes (total)", "{:,}"),
    (per_day, "mean_crashes_per_date", "Average NYC crashes per calendar date, by weekday\n2013–2025", "Average crashes per date", "{:.1f}"),
], start=1):
    csv_cols = ["weekday", metric] if idx == 1 else ["weekday", "crashes", "weekday_dates", metric]
    df[csv_cols].to_csv(out / f"values_{idx}.csv", index=False, float_format="%.6f")
    fig, ax = plt.subplots(figsize=(9, 5.2))
    bars = ax.bar(df["weekday"], df[metric], color="#4472C4", width=0.72)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Day of week")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    pad = df[metric].max() * 0.012
    for bar, value in zip(bars, df[metric]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + pad, fmt.format(value), ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0, df[metric].max() * 1.12)
    fig.tight_layout()
    fig.savefig(out / f"option_{idx}.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

print("Raw counts:")
print(raw.to_string(index=False))
print("\nWeekday-date counts and normalized means:")
print(per_day[["weekday", "weekday_dates", "crashes", "mean_crashes_per_date"]].to_string(index=False))
print("\nTotal:", int(raw["crashes"].sum()))
PY
# bash
python -c "import json, pathlib; p=pathlib.Path('out/options.json'); d=json.loads(p.read_text()); print('options', len(d['options']), 'probability_sum', sum(x['probability'] for x in d['options'])); print('files', sorted(x.name for x in pathlib.Path('out').iterdir()))"

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