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

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: From 2013 to 2025, how were NYC crashes spread across the days of the week?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Crash count and share of all crashes
denominator: All police-reported crashes dated 2013-01-01 through 2025-12-31
grouping: Day of week
chart_type: bar chart
probability: 0.65
WRITTEN ANSWER:
Of 2,132,218 crashes, Fridays had the most (338,800; 15.9%) and Sundays the fewest (257,544; 12.1%). This framing answers how the total recorded crash volume was distributed among weekdays; the chart shows Friday with the largest share and Sunday with the smallest. It is defensible because each crash contributes once to an overall distribution across the full period. It does not show year-to-year changes or crash risk relative to traffic or travel exposure.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crashes,share_pct
Sunday,257544,12.0787
Monday,304518,14.2817
Tuesday,313488,14.7024
Wednesday,311111,14.591
Thursday,318376,14.9317
Friday,338800,15.8896
Saturday,288381,13.5249

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"SELECT min(crash_date), max(crash_date), count(*), count(distinct crash_date) FROM read_parquet('{p}')\").fetchall()); print(duckdb.sql(f\"SELECT date_part('year', crash_date)::INT yr, min(crash_date), max(crash_date), count(*) FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr\").df().to_string(index=False))"
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"WITH d AS (SELECT crash_date, count(*) n, dayname(crash_date) weekday FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1) SELECT weekday, count(*) dates, sum(n) crashes, round(avg(n),2) avg_per_date FROM d GROUP BY weekday ORDER BY CASE weekday WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 ELSE 7 END\").df().to_string(index=False)); print(duckdb.sql(f\"SELECT count(*) days, count(*) FILTER (WHERE n=0) zero_crash_days FROM (SELECT d::DATE day, count(c.crash_date) n FROM generate_series(DATE '2013-01-01', DATE '2025-12-31', INTERVAL 1 DAY) g(d) LEFT JOIN read_parquet('{p}') c ON c.crash_date=g.d GROUP BY d)\").fetchall())"
# bash
ls
# bash
python -c 'import duckdb; p="data/crashes.parquet"; q=f"WITH by_day AS (SELECT crash_date, count(*) AS n FROM read_parquet(\"{p}\") WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' GROUP BY crash_date), calendar AS (SELECT d::DATE AS day, coalesce(n, 0) AS n FROM generate_series(DATE '\''2013-01-01'\'', DATE '\''2025-12-31'\'', INTERVAL 1 DAY) g(d) LEFT JOIN by_day ON by_day.crash_date = g.d), agg AS (SELECT dayofweek(day) AS wd, strftime(day, '\''%A'\'') AS weekday, count(*) AS calendar_days, sum(n) AS crashes, avg(n) AS avg_per_day FROM calendar GROUP BY wd, weekday) SELECT weekday, calendar_days, crashes, round(100.0 * crashes / sum(crashes) OVER (), 4) AS share_pct, avg_per_day FROM agg ORDER BY wd"; df=duckdb.sql(q).df(); print(df.to_string(index=False)); print("total", int(df.crashes.sum()), "days", int(df.calendar_days.sum()), "zero_crash_days", duckdb.sql(f"WITH d AS (SELECT crash_date, count(*) n FROM read_parquet(\"{p}\") WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' GROUP BY crash_date) SELECT count(*) FROM generate_series(DATE '\''2013-01-01'\'', DATE '\''2025-12-31'\'', INTERVAL 1 DAY) g(day) LEFT JOIN d ON d.crash_date=g.day WHERE coalesce(n,0)=0").fetchone()[0])'
# bash
python -c 'exec("import duckdb, pandas as pd, matplotlib.pyplot as plt\nfrom pathlib import Path\nout=Path(\"out\"); out.mkdir(exist_ok=True)\np=\"data/crashes.parquet\"\nq=f\"\"\"WITH by_day AS (SELECT crash_date, count(*) AS n FROM read_parquet(\047{p}\047) WHERE crash_date >= DATE \0472013-01-01\047 AND crash_date < DATE \0472026-01-01\047 GROUP BY crash_date), calendar AS (SELECT d::DATE AS day, coalesce(n, 0) AS n FROM generate_series(DATE \0472013-01-01\047, DATE \0472025-12-31\047, INTERVAL 1 DAY) g(d) LEFT JOIN by_day ON by_day.crash_date = g.d), agg AS (SELECT dayofweek(day) AS wd, strftime(day, \047%A\047) AS weekday, count(*) AS calendar_days, sum(n) AS crashes, avg(n) AS avg_per_day FROM calendar GROUP BY wd, weekday) SELECT weekday, calendar_days, crashes, 100.0 * crashes / sum(crashes) OVER () AS share_pct, avg_per_day FROM agg ORDER BY wd\"\"\"\ndf=duckdb.sql(q).df()\ndf[\"calendar_days\"]=df[\"calendar_days\"].astype(int); df[\"crashes\"]=df[\"crashes\"].astype(int)\n# Option 1: the full-period distribution by share of all reported crashes.\none=df[[\"weekday\",\"crashes\",\"share_pct\"]].copy(); one[\"share_pct\"]=one[\"share_pct\"].round(4); one.to_csv(out/\"values_1.csv\",index=False)\nfig,ax=plt.subplots(figsize=(10,5.6)); bars=ax.bar(one.weekday,one.crashes,color=\"#3478a8\")\nax.set_title(\"NYC crashes by day of week, 2013–2025\"); ax.set_ylabel(\"Police-reported crashes\"); ax.set_xlabel(\"Day of week\"); ax.grid(axis=\"y\",alpha=.25); ax.set_axisbelow(True)\nax.set_ylim(0,one.crashes.max()*1.14)\nfor bar, row in zip(bars,one.itertuples()): ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+one.crashes.max()*.018,f\"{row.crashes:,}\\n{row.share_pct:.1f}%\",ha=\"center\",va=\"bottom\",fontsize=9)\nfig.tight_layout(); fig.savefig(out/\"option_1.png\",dpi=160); plt.close(fig)\n# Option 2: average counts per occurrence of each weekday, treating all calendar dates in range equally.\ntwo=df[[\"weekday\",\"crashes\",\"calendar_days\",\"avg_per_day\"]].copy(); two[\"avg_per_day\"]=two[\"avg_per_day\"].round(4); two.to_csv(out/\"values_2.csv\",index=False)\nfig,ax=plt.subplots(figsize=(10,5.6)); bars=ax.bar(two.weekday,two.avg_per_day,color=\"#d47b35\")\nax.set_title(\"Average NYC crashes per calendar day by weekday, 2013–2025\"); ax.set_ylabel(\"Average police-reported crashes per day\"); ax.set_xlabel(\"Day of week\"); ax.grid(axis=\"y\",alpha=.25); ax.set_axisbelow(True); ax.set_ylim(0,two.avg_per_day.max()*1.15)\nfor bar,row in zip(bars,two.itertuples()): ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+two.avg_per_day.max()*.018,f\"{row.avg_per_day:.1f}\",ha=\"center\",va=\"bottom\",fontsize=9)\nfig.tight_layout(); fig.savefig(out/\"option_2.png\",dpi=160); plt.close(fig)\nprint(df.to_string(index=False)); print(\"Total crashes:\",int(df.crashes.sum()),\"calendar days:\",int(df.calendar_days.sum()))")'
# bash
python -c 'import json, pathlib; p=pathlib.Path("out"); data=json.loads((p/"options.json").read_text()); assert len(data["options"])==2; assert abs(sum(x["probability"] for x in data["options"])-1)<1e-9; required=[p/"option_1.png",p/"option_2.png",p/"values_1.csv",p/"values_2.csv"]; assert all(x.is_file() and x.stat().st_size>0 for x in required); print("JSON valid; probabilities sum to",sum(x["probability"] for x in data["options"])); print("All chart and values files exist and are nonempty.")'

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