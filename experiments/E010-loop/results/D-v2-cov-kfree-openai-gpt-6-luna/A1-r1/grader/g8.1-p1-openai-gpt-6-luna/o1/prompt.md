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

QUESTION ASKED: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Annual number of pedestrians injured in Brooklyn crashes
denominator: None; absolute sum of recorded pedestrian injuries
grouping: Crash year, 2013–2025, borough = BROOKLYN
chart_type: Line chart
probability: 0.45
WRITTEN ANSWER:
Brooklyn reported 3,641 pedestrian injuries in 2013 and 2,835 in 2025 (22% fewer), but injuries have risen 49% since 2021, so these counts alone do not establish safer conditions. This answers whether the annual number of reported pedestrian injuries changed: the count fell from 3,641 in 2013 to 1,905 in 2021, then rose each year to 2,835 in 2025. Absolute injury burden is a defensible way to assess how many pedestrians were hurt, but it is not injury risk per pedestrian or trip because exposure is unavailable. It leaves fatalities and individual risk unanswered. The analysis uses Brooklyn crashes in full years 2013–2025; it excludes 659,713 records with NULL borough among 2,132,218 NYC crashes in those years (30.94%; pedestrian injury and death fields themselves have no NULLs) and excludes 9,700 Brooklyn records from partial 2026 through June 11 (2.006% of Brooklyn records from 2013 through June 11, 2026).

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrians_injured
2013,3641
2014,3349
2015,3029
2016,2917
2017,2663
2018,2785
2019,2700
2020,1781
2021,1905
2022,2275
2023,2385
2024,2645
2025,2835

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"DESCRIBE SELECT * FROM read_parquet(?)\",[p]).fetchdf().to_string(index=False)); print(c.execute(\"SELECT count(*) n, min(crash_date) min_date, max(crash_date) max_date FROM read_parquet(?)\",[p]).fetchdf().to_string(index=False)); print(c.execute(\"SELECT borough, count(*) n FROM read_parquet(?) GROUP BY borough ORDER BY n DESC\",[p]).fetchdf().to_string(index=False)); print(c.execute(\"SELECT count(*) n, countif(number_of_pedestrians_injured IS NULL) p_inj_null, countif(number_of_pedestrians_killed IS NULL) p_kill_null, countif(crash_date IS NULL) date_null, countif(borough IS NULL) borough_null FROM read_parquet(?)\",[p]).fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"WITH x AS (SELECT *, year(crash_date) y FROM read_parquet(?) WHERE borough='BROOKLYN') SELECT y, count(*) crashes, sum(number_of_pedestrians_injured) ped_inj, sum(number_of_pedestrians_killed) ped_kill, countif(number_of_pedestrians_injured+number_of_pedestrians_killed>0) crashes_ped_harm FROM x GROUP BY y ORDER BY y\",[p]).fetchdf().to_string(index=False)); print(c.execute(\"SELECT year(crash_date) y, count(*) n, countif(borough IS NULL) null_borough, countif(borough='BROOKLYN') bk FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2013 AND 2026 GROUP BY y ORDER BY y\",[p]).fetchdf().to_string(index=False)); print(c.execute(\"SELECT min(crash_date), max(crash_date), countif(borough='BROOKLYN') FROM read_parquet(?) WHERE year(crash_date)=2026\",[p]).fetchdf().to_string(index=False))"
# bash
ls
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"WITH x AS (SELECT *, year(crash_date) y FROM read_parquet(?) WHERE y BETWEEN 2013 AND 2025) SELECT count(*) total, countif(borough IS NULL) null_borough, round(100.0*countif(borough IS NULL)/count(*),3) null_pct, countif(number_of_pedestrians_injured IS NULL) pedinj_null, countif(number_of_pedestrians_killed IS NULL) pedkill_null FROM x\",[p]).fetchdf().to_string(index=False)); print(c.execute(\"WITH x AS (SELECT *, year(crash_date) y FROM read_parquet(?) WHERE borough='BROOKLYN' AND y BETWEEN 2013 AND 2026) SELECT sum(CASE WHEN y<2026 THEN 1 ELSE 0 END) full_year_bk, count(*) bk_through_2026, countif(y=2026) bk_partial, round(100.0*countif(y=2026)/count(*),3) partial_share_of_bk_2013_26 FROM x\",[p]).fetchdf().to_string(index=False)); print(c.execute(\"WITH x AS (SELECT *, year(crash_date) y FROM read_parquet(?) WHERE borough='BROOKLYN' AND y BETWEEN 2013 AND 2025), a AS (SELECT y, count(*) crashes, sum(number_of_pedestrians_injured) inj, sum(number_of_pedestrians_killed) killed, countif(number_of_pedestrians_injured>0 OR number_of_pedestrians_killed>0) harm FROM x GROUP BY y) SELECT y, crashes, inj, killed, harm, round(100.0*harm/crashes,3) harm_pct, inj+killed total_casualties FROM a ORDER BY y\",[p]).fetchdf().to_string(index=False))"
# bash
python3 - <<'PY'
from pathlib import Path
import duckdb
import matplotlib.pyplot as plt
import pandas as pd

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
annual = con.execute("""
    WITH brooklyn AS (
        SELECT year(crash_date) AS year,
               number_of_pedestrians_injured AS pedestrian_injured,
               number_of_pedestrians_killed AS pedestrian_killed
        FROM read_parquet('data/crashes.parquet')
        WHERE borough = 'BROOKLYN'
          AND crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
    )
    SELECT year,
           count(*) AS brooklyn_crashes,
           sum(pedestrian_injured)::BIGINT AS pedestrians_injured,
           sum(pedestrian_killed)::BIGINT AS pedestrians_killed,
           count(*) FILTER (WHERE pedestrian_injured > 0 OR pedestrian_killed > 0)::BIGINT AS crashes_with_pedestrian_harm
    FROM brooklyn
    GROUP BY year
    ORDER BY year
""").df()
annual['share_crashes_with_pedestrian_harm_pct'] = 100 * annual['crashes_with_pedestrian_harm'] / annual['brooklyn_crashes']

plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False})

# Option 1: annual counts of pedestrians injured
injuries = annual[['year', 'pedestrians_injured']].copy()
injuries.to_csv(out / 'values_1.csv', index=False)
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(injuries['year'], injuries['pedestrians_injured'], color='#1769aa', marker='o', linewidth=2.8, markersize=5)
ax.fill_between(injuries['year'], injuries['pedestrians_injured'], color='#1769aa', alpha=.10)
ax.annotate('3,641', (2013, 3641), xytext=(0, 11), textcoords='offset points', ha='center', color='#174a73', fontweight='bold')
ax.annotate('2,835', (2025, 2835), xytext=(0, 11), textcoords='offset points', ha='center', color='#174a73', fontweight='bold')
ax.set_title('Brooklyn pedestrian injuries fell from 2013, then climbed', loc='left', fontsize=15, fontweight='bold', pad=15)
ax.set_ylabel('Pedestrians injured in reported crashes')
ax.set_xlabel('Crash year')
ax.set_xticks(injuries['year'])
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', color='#d9e0e6', linewidth=.8)
ax.set_ylim(0, 4200)
fig.text(.01, .01, 'Source: NYC motor vehicle crash records. Full calendar years only; Brooklyn records, 2013–2025.', fontsize=8.5, color='#555')
fig.tight_layout(rect=(0, .05, 1, 1))
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Option 2: annual counts of pedestrians killed
fatalities = annual[['year', 'pedestrians_killed']].copy()
fatalities.to_csv(out / 'values_2.csv', index=False)
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.bar(fatalities['year'], fatalities['pedestrians_killed'], color='#b23a48', width=.72)
ax.set_title('Brooklyn pedestrian deaths vary year to year', loc='left', fontsize=15, fontweight='bold', pad=15)
ax.set_ylabel('Pedestrians killed in reported crashes')
ax.set_xlabel('Crash year')
ax.set_xticks(fatalities['year'])
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', color='#e4d9da', linewidth=.8)
ax.set_axisbelow(True)
ax.set_ylim(0, 55)
ax.annotate('30', (2013, 30), xytext=(0, 5), textcoords='offset points', ha='center', fontsize=9)
ax.annotate('39', (2025, 39), xytext=(0, 5), textcoords='offset points', ha='center', fontsize=9)
fig.text(.01, .01, 'Source: NYC motor vehicle crash records. Full calendar years only; Brooklyn records, 2013–2025.', fontsize=8.5, color='#555')
fig.tight_layout(rect=(0, .05, 1, 1))
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Option 3: share of all Brooklyn reported crashes with pedestrian injury or death
share = annual[['year', 'crashes_with_pedestrian_harm', 'brooklyn_crashes', 'share_crashes_with_pedestrian_harm_pct']].copy()
share.to_csv(out / 'values_3.csv', index=False)
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(share['year'], share['share_crashes_with_pedestrian_harm_pct'], color='#b05a00', marker='o', linewidth=2.8, markersize=5)
ax.fill_between(share['year'], share['share_crashes_with_pedestrian_harm_pct'], color='#e9a44a', alpha=.16)
start = share.iloc[0]
end = share.iloc[-1]
ax.annotate(f"{start['share_crashes_with_pedestrian_harm_pct']:.1f}%", (start['year'], start['share_crashes_with_pedestrian_harm_pct']), xytext=(0, 11), textcoords='offset points', ha='center', color='#794000', fontweight='bold')
ax.annotate(f"{end['share_crashes_with_pedestrian_harm_pct']:.1f}%", (end['year'], end['share_crashes_with_pedestrian_harm_pct']), xytext=(0, 11), textcoords='offset points', ha='center', color='#794000', fontweight='bold')
ax.set_title('Pedestrian harm became a larger share of Brooklyn crashes', loc='left', fontsize=15, fontweight='bold', pad=15)
ax.set_ylabel('Share of Brooklyn crashes with pedestrian injury or death')
ax.set_xlabel('Crash year')
ax.set_xticks(share['year'])
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', color='#e5ded4', linewidth=.8)
ax.set_ylim(0, 13)
fig.text(.01, .01, 'Source: NYC motor vehicle crash records. Full calendar years only; Brooklyn records, 2013–2025.', fontsize=8.5, color='#555')
fig.tight_layout(rect=(0, .05, 1, 1))
fig.savefig(out / 'option_3.png', dpi=180, bbox_inches='tight')
plt.close(fig)

print(annual.to_string(index=False))
PY
# bash
python3 -c "import json, pathlib; p=pathlib.Path('out/options.json'); d=json.loads(p.read_text()); print('options',len(d['options']),'probability_sum',sum(x['probability'] for x in d['options'])); print('outputs',[(f, pathlib.Path('out',f).exists()) for f in ['option_1.png','option_2.png','option_3.png','values_1.csv','values_2.csv','values_3.csv']])"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR05: If a borough filter (borough = 'BROOKLYN') is used, the output discloses that crashes with no borough recorded (19.9–38.1% per year) are excluded.
- tr_TR11: The output does not call Brooklyn 'safer' or 'less safe' from counts alone without saying that there is no pedestrian exposure measure.
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.