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

QUESTION ASKED: Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Annual motorist deaths recorded in crashes
denominator: None (annual count)
grouping: Crash year, 2013–2025
chart_type: Line chart
probability: 0.5
WRITTEN ANSWER:
Recorded motorist deaths decreased from 110 in 2013 to 81 in 2025 (26.4% lower), but these counts cannot determine whether deaths per mile driven declined. This addresses whether the annual number of motorists killed in NYC crashes fell, and the chart shows a lower count in 2025 than in 2013 despite substantial intervening variation. This count is a defensible measure of fatality burden, but it leaves the per-mile risk question unanswered because the crash data contain no miles-driven denominator.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_deaths
2013,110.0
2014,109.0
2015,95.0
2016,72.0
2017,107.0
2018,98.0
2019,82.0
2020,139.0
2021,134.0
2022,116.0
2023,123.0
2024,111.0
2025,81.0

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c 'import duckdb; print(duckdb.__version__)'
# bash
ls out
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.sql(f"SELECT year(crash_date) AS year, count(*) AS crashes, sum(number_of_motorist_killed) AS motorist_deaths, count(*) FILTER (WHERE number_of_motorist_killed > 0) AS crashes_with_motorist_death FROM read_parquet(\"{p}\") WHERE crash_date >= DATE \"2013-01-01\" AND crash_date < DATE \"2026-01-01\" GROUP BY 1 ORDER BY 1").df().to_string(index=False))'
# bash
python3 -c 'import duckdb; print(duckdb.sql("SELECT year(crash_date) AS year, count(*) AS crashes, sum(number_of_motorist_killed) AS motorist_deaths, count(*) FILTER (WHERE number_of_motorist_killed > 0) AS crashes_with_motorist_death FROM read_parquet(\047data/crashes.parquet\047) WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1").df().to_string(index=False))'
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt; from pathlib import Path; out=Path("out"); df=duckdb.sql("SELECT year(crash_date) AS year, count(*) AS crashes, sum(number_of_motorist_killed) AS motorist_deaths, count(*) FILTER (WHERE number_of_motorist_killed > 0) AS motorist_fatal_crashes FROM read_parquet(\"data/crashes.parquet\") WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1").df(); df["motorist_fatal_crashes_per_1000_reported_crashes"] = df["motorist_fatal_crashes"] / df["crashes"] * 1000; df.to_csv(out / "values_1.csv", index=False); df[["year", "crashes", "motorist_deaths", "motorist_fatal_crashes", "motorist_fatal_crashes_per_1000_reported_crashes"]].to_csv(out / "values_2.csv", index=False); plt.figure(figsize=(9, 5.2)); plt.plot(df["year"], df["motorist_deaths"], marker="o", linewidth=2.3, color="#1769aa"); plt.xticks(df["year"], rotation=45); plt.ylabel("Motorists killed (persons)"); plt.xlabel("Crash year"); plt.title("Motorists killed in NYC crashes, 2013–2025"); plt.suptitle("Annual count; does not account for miles driven", y=0.94, fontsize=10, color="#555555"); plt.grid(axis="y", alpha=0.25); plt.annotate("110", (2013, 110), xytext=(6, 8), textcoords="offset points", fontsize=9); plt.annotate("81", (2025, 81), xytext=(-18, 8), textcoords="offset points", fontsize=9); plt.tight_layout(rect=(0, 0, 1, 0.92)); plt.savefig(out / "option_1.png", dpi=180, bbox_inches="tight"); plt.close(); plt.figure(figsize=(9, 5.2)); plt.plot(df["year"], df["motorist_fatal_crashes_per_1000_reported_crashes"], marker="o", linewidth=2.3, color="#b34b36"); plt.xticks(df["year"], rotation=45); plt.ylabel("Motorist-fatal crashes per 1,000 reported crashes"); plt.xlabel("Crash year"); plt.title("Share of reported crashes with a motorist death, 2013–2025"); plt.suptitle("Crash-based severity proxy; not a per-mile risk measure", y=0.94, fontsize=10, color="#555555"); plt.grid(axis="y", alpha=0.25); start=df.loc[df.year.eq(2013), "motorist_fatal_crashes_per_1000_reported_crashes"].iloc[0]; end=df.loc[df.year.eq(2025), "motorist_fatal_crashes_per_1000_reported_crashes"].iloc[0]; plt.annotate(f"{start:.3f}", (2013, start), xytext=(6, 8), textcoords="offset points", fontsize=9); plt.annotate(f"{end:.3f}", (2025, end), xytext=(-30, 8), textcoords="offset points", fontsize=9); plt.tight_layout(rect=(0, 0, 1, 0.92)); plt.savefig(out / "option_2.png", dpi=180, bbox_inches="tight"); plt.close(); print(df.to_string(index=False))'
# bash
python3 -c 'import duckdb, matplotlib.pyplot as plt; from pathlib import Path; out=Path("out"); df=duckdb.sql("SELECT year(crash_date) AS year, count(*) AS crashes, sum(number_of_motorist_killed) AS motorist_deaths, count(*) FILTER (WHERE number_of_motorist_killed > 0) AS motorist_fatal_crashes FROM read_parquet(\"data/crashes.parquet\") WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1").df(); df["motorist_fatal_crashes_per_1000_reported_crashes"] = df["motorist_fatal_crashes"] / df["crashes"] * 1000; df[["year", "motorist_deaths"]].to_csv(out / "values_1.csv", index=False); df[["year", "crashes", "motorist_fatal_crashes", "motorist_fatal_crashes_per_1000_reported_crashes"]].to_csv(out / "values_2.csv", index=False); plt.figure(figsize=(9, 5.2)); plt.plot(df["year"], df["motorist_deaths"], marker="o", linewidth=2.3, color="#1769aa"); plt.xticks(df["year"], rotation=45); plt.ylim(0, 150); plt.ylabel("Motorists killed (persons)"); plt.xlabel("Crash year"); plt.title("Motorists killed in NYC crashes, 2013–2025"); plt.suptitle("Annual count; does not account for miles driven", y=0.94, fontsize=10, color="#555555"); plt.grid(axis="y", alpha=0.25); plt.annotate("110", (2013, 110), xytext=(6, 8), textcoords="offset points", fontsize=9); plt.annotate("81", (2025, 81), xytext=(-18, 8), textcoords="offset points", fontsize=9); plt.tight_layout(rect=(0, 0, 1, 0.92)); plt.savefig(out / "option_1.png", dpi=180, bbox_inches="tight"); plt.close(); plt.figure(figsize=(9, 5.2)); plt.plot(df["year"], df["motorist_fatal_crashes_per_1000_reported_crashes"], marker="o", linewidth=2.3, color="#b34b36"); plt.xticks(df["year"], rotation=45); plt.ylim(0, 1.3); plt.ylabel("Motorist-fatal crashes per 1,000 reported crashes"); plt.xlabel("Crash year"); plt.title("Share of reported crashes with a motorist death, 2013–2025"); plt.suptitle("Crash-based severity proxy; not a per-mile risk measure", y=0.94, fontsize=10, color="#555555"); plt.grid(axis="y", alpha=0.25); start=df.loc[df.year.eq(2013), "motorist_fatal_crashes_per_1000_reported_crashes"].iloc[0]; end=df.loc[df.year.eq(2025), "motorist_fatal_crashes_per_1000_reported_crashes"].iloc[0]; plt.annotate(f"{start:.3f}", (2013, start), xytext=(6, 8), textcoords="offset points", fontsize=9); plt.annotate(f"{end:.3f}", (2025, end), xytext=(-30, 8), textcoords="offset points", fontsize=9); plt.tight_layout(rect=(0, 0, 1, 0.92)); plt.savefig(out / "option_2.png", dpi=180, bbox_inches="tight"); plt.close(); print("Outputs refreshed with zero-based y-axes.")'
# bash
python3 -c 'import json; from pathlib import Path; d=json.loads(Path("out/options.json").read_text()); assert abs(sum(o["probability"] for o in d["options"])-1)<1e-9; assert len(d["options"])==2; required=["option_1.png","option_2.png","values_1.csv","values_2.csv","options.json"]; assert all((Path("out")/name).is_file() and (Path("out")/name).stat().st_size>0 for name in required); print("JSON valid; option probabilities sum to 1; all requested outputs exist.")'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording (fewer minor crashes reported).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.