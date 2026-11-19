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
metric: Police-reported crash count
denominator: No denominator; total crashes in 2013–2025 (2,132,218)
grouping: Day of week
chart_type: Bar chart
probability: 0.55
WRITTEN ANSWER:
Friday had the most crashes (338,800; 15.9% of the total), while Sunday had the fewest (257,544; 12.1%). This answers how the total reported crashes are allocated across weekdays: Friday is the largest category and Sunday the smallest. Total counts describe overall frequency over 2013–2025, but do not adjust for the slight differences in the number of each weekday or show severity.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crash_count,share_pct,calendar_days,avg_crashes_per_day
Monday,304518,14.2817,678,449.1416
Tuesday,313488,14.7024,679,461.6907
Wednesday,311111,14.5910,679,458.1900
Thursday,318376,14.9317,678,469.5811
Friday,338800,15.8896,678,499.7050
Saturday,288381,13.5249,678,425.3407
Sunday,257544,12.0787,678,379.8584

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
ls out
# bash
ls data
# bash
python -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt; from pathlib import Path; out=Path("out"); conn=duckdb.connect(); raw=conn.execute("SELECT dayofweek(crash_date) AS dow, COUNT(*) AS crash_count FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2026-01-01\' GROUP BY 1").df(); order=[1,2,3,4,5,6,0]; names={0:"Sunday",1:"Monday",2:"Tuesday",3:"Wednesday",4:"Thursday",5:"Friday",6:"Saturday"}; frame=raw.set_index("dow").reindex(order).reset_index(); frame["weekday"]=[names[int(x)] for x in frame.dow]; dates=pd.date_range("2013-01-01","2025-12-31",freq="D"); exposure=pd.Series(dates.dayofweek).value_counts().sort_index(); frame["calendar_days"]=[int(exposure.loc[(d+6)%7]) for d in order]; frame["share_pct"]=frame.crash_count/frame.crash_count.sum()*100; frame["avg_crashes_per_day"]=frame.crash_count/frame.calendar_days; frame=frame[["weekday","crash_count","share_pct","calendar_days","avg_crashes_per_day"]]; frame.to_csv(out/"values_1.csv",index=False,float_format="%.4f"); frame.to_csv(out/"values_2.csv",index=False,float_format="%.4f"); plt.figure(figsize=(9,5)); bars=plt.bar(frame.weekday,frame.crash_count,color="#4472C4"); plt.title("NYC police-reported crashes by weekday, 2013–2025"); plt.ylabel("Crash count"); plt.xlabel("Day of week"); plt.grid(axis="y",alpha=.25); plt.bar_label(bars,labels=[f"{int(x):,}" for x in frame.crash_count],padding=3,fontsize=8); plt.tight_layout(); plt.savefig(out/"option_1.png",dpi=160); plt.close(); plt.figure(figsize=(9,5)); bars=plt.bar(frame.weekday,frame.avg_crashes_per_day,color="#ED7D31"); plt.title("Average NYC crashes per calendar weekday, 2013–2025"); plt.ylabel("Average crashes per occurrence of weekday"); plt.xlabel("Day of week"); plt.grid(axis="y",alpha=.25); plt.bar_label(bars,labels=[f"{x:,.1f}" for x in frame.avg_crashes_per_day],padding=3,fontsize=8); plt.tight_layout(); plt.savefig(out/"option_2.png",dpi=160); plt.close(); print(frame.to_string(index=False)); print("TOTAL",int(frame.crash_count.sum()))'
# bash
python - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

out = Path("out")
con = duckdb.connect()
raw = con.execute("""
    SELECT dayofweek(crash_date) AS dow, COUNT(*) AS crash_count
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY 1
""").df()
order = [1, 2, 3, 4, 5, 6, 0]
names = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}
frame = raw.set_index("dow").reindex(order).reset_index()
frame["weekday"] = [names[int(x)] for x in frame.dow]
dates = pd.date_range("2013-01-01", "2025-12-31", freq="D")
exposure = pd.Series(dates.dayofweek).value_counts().sort_index()
frame["calendar_days"] = [int(exposure.loc[(int(d) + 6) % 7]) for d in order]
frame["share_pct"] = frame.crash_count / frame.crash_count.sum() * 100
frame["avg_crashes_per_day"] = frame.crash_count / frame.calendar_days
frame = frame[["weekday", "crash_count", "share_pct", "calendar_days", "avg_crashes_per_day"]]
frame.to_csv(out / "values_1.csv", index=False, float_format="%.4f")
frame.to_csv(out / "values_2.csv", index=False, float_format="%.4f")

plt.figure(figsize=(9, 5))
bars = plt.bar(frame.weekday, frame.crash_count, color="#4472C4")
plt.title("NYC police-reported crashes by weekday, 2013–2025")
plt.ylabel("Crash count")
plt.xlabel("Day of week")
plt.grid(axis="y", alpha=.25)
plt.bar_label(bars, labels=[f"{int(x):,}" for x in frame.crash_count], padding=3, fontsize=8)
plt.tight_layout()
plt.savefig(out / "option_1.png", dpi=160)
plt.close()

plt.figure(figsize=(9, 5))
bars = plt.bar(frame.weekday, frame.avg_crashes_per_day, color="#ED7D31")
plt.title("Average NYC crashes per calendar weekday, 2013–2025")
plt.ylabel("Average crashes per occurrence of weekday")
plt.xlabel("Day of week")
plt.grid(axis="y", alpha=.25)
plt.bar_label(bars, labels=[f"{x:,.1f}" for x in frame.avg_crashes_per_day], padding=3, fontsize=8)
plt.tight_layout()
plt.savefig(out / "option_2.png", dpi=160)
plt.close()
print(frame.to_string(index=False))
print("TOTAL", int(frame.crash_count.sum()))
PY
# bash
ls out
# bash
python -c 'import json, pathlib; p=pathlib.Path("out/options.json"); d=json.loads(p.read_text()); assert len(d["options"])==2; assert abs(sum(o["probability"] for o in d["options"])-1)<1e-9; print("Valid JSON; probabilities sum to", sum(o["probability"] for o in d["options"]))'

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