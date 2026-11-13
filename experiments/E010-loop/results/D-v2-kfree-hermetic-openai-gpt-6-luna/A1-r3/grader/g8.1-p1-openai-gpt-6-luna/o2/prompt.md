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
metric: Annual pedestrians killed
denominator: None; raw annual fatality count in Brooklyn
grouping: Calendar year, 2013–2025
chart_type: Bar chart
probability: 0.3
WRITTEN ANSWER:
Pedestrian deaths rose from 30 in 2013 to 39 in 2025 (30.0% more), with substantial year-to-year variation. This framing addresses whether the most severe pedestrian outcome has improved: the full-year fatality count is higher in 2025 than in 2013. Separating deaths is defensible because a fatality is not equivalent in severity to an injury, but this small, volatile count alone does not describe nonfatal harm or exposure-adjusted risk.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,pedestrian_killed
2013,30
2014,42
2015,46
2016,20
2017,20
2018,23
2019,33
2020,17
2021,32
2022,23
2023,22
2024,31
2025,39

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls data && python -c 'import duckdb; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet('\''data/crashes.parquet'\'')").fetchdf().to_string(index=False)); print(c.execute("SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet('\''data/crashes.parquet'\'')").fetchall())'
# bash
python -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute(f"SELECT borough, count(*) n FROM read_parquet('\''{p}'\'') WHERE borough ILIKE '\''Brooklyn'\'' GROUP BY borough").fetchall()); print(c.execute(f"SELECT year(crash_date) y, count(*) crashrows, sum(coalesce(number_of_pedestrians_injured,0)) pedinj, sum(coalesce(number_of_pedestrians_killed,0)) pedkill, sum(CASE WHEN coalesce(number_of_pedestrians_injured,0)>0 OR coalesce(number_of_pedestrians_killed,0)>0 THEN 1 ELSE 0 END) pedestrian_involved, count(*) FILTER(WHERE number_of_pedestrians_injured IS NULL) null_inj, count(*) FILTER(WHERE number_of_pedestrians_killed IS NULL) null_kill FROM read_parquet('\''{p}'\'') WHERE borough ILIKE '\''Brooklyn'\'' AND year(crash_date) BETWEEN 2013 AND 2026 GROUP BY y ORDER BY y").fetchdf().to_string(index=False))'
# bash
ls . && ls out
# bash
python -c '
import os, json
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

os.makedirs("out", exist_ok=True)
df = duckdb.connect().execute("""
SELECT year(crash_date)::INTEGER AS year,
       sum(coalesce(number_of_pedestrians_injured, 0))::INTEGER AS pedestrian_injured,
       sum(coalesce(number_of_pedestrians_killed, 0))::INTEGER AS pedestrian_killed,
       sum(CASE WHEN coalesce(number_of_pedestrians_injured, 0) > 0 OR coalesce(number_of_pedestrians_killed, 0) > 0 THEN 1 ELSE 0 END)::INTEGER AS crashes_with_pedestrian_injury_or_death
FROM read_parquet(\'data/crashes.parquet\')
WHERE upper(borough) = \'BROOKLYN\' AND crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2026-01-01\'
GROUP BY year ORDER BY year
""").fetchdf()
df["pedestrian_casualties"] = df.pedestrian_injured + df.pedestrian_killed

for option, cols in [(1, ["year", "pedestrian_injured", "pedestrian_killed", "pedestrian_casualties"]), (2, ["year", "pedestrian_killed"]), (3, ["year", "crashes_with_pedestrian_injury_or_death"])]:
    df[cols].to_csv(f"out/values_{option}.csv", index=False)

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold", "axes.titlesize": 16, "axes.labelsize": 10})
navy, blue, orange, gray = "#17324D", "#1479B8", "#D85B32", "#66727D"
years = df.year.to_numpy()

def base(ax, title, subtitle):
    ax.set_title(title, loc="left", color=navy, pad=28)
    ax.text(0, 1.015, subtitle, transform=ax.transAxes, ha="left", va="bottom", fontsize=10, color=gray)
    ax.set_xlim(2012.7, 2025.3)
    ax.set_xticks(range(2013, 2026, 2))
    ax.grid(axis="y", color="#DDE3E8", linewidth=.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#B8C2CA")
    ax.tick_params(axis="y", length=0, colors=gray)
    ax.tick_params(axis="x", colors=gray)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlabel("Calendar year", color=gray, labelpad=9)
    ax.text(0, -0.22, "Brooklyn police-reported motor vehicle crashes; full years only. Counts, not rates; pedestrian exposure is unavailable.", transform=ax.transAxes, ha="left", va="top", fontsize=8, color=gray)

# 1: annual pedestrian casualties (people injured or killed)
fig, ax = plt.subplots(figsize=(10.5, 5.7), layout="constrained")
base(ax, "Pedestrian casualties in Brooklyn are below 2013", "People injured or killed in reported crashes, annually")
ax.plot(years, df.pedestrian_casualties, color=blue, linewidth=2.7, marker="o", markersize=5)
ax.fill_between(years, df.pedestrian_casualties, color=blue, alpha=.10)
for x in [2013, 2025]:
    val = int(df.loc[df.year.eq(x), "pedestrian_casualties"].iloc[0])
    ax.annotate(f"{val:,}", (x, val), xytext=(0, 12 if x == 2013 else -20), textcoords="offset points", ha="center", color=navy, fontsize=10, fontweight="bold")
ax.set_ylim(0, 4200)
fig.savefig("out/option_1.png", dpi=180, facecolor="white")
plt.close(fig)

# 2: pedestrian fatalities alone, shown as annual columns
fig, ax = plt.subplots(figsize=(10.5, 5.7), layout="constrained")
base(ax, "Pedestrian deaths have not fallen since 2013", "Pedestrians killed in reported Brooklyn crashes, annually")
ax.bar(years, df.pedestrian_killed, color=[orange if y == 2025 else blue for y in years], width=.68)
for x in [2013, 2025]:
    val = int(df.loc[df.year.eq(x), "pedestrian_killed"].iloc[0])
    ax.annotate(str(val), (x, val), xytext=(0, 5), textcoords="offset points", ha="center", color=navy, fontsize=9, fontweight="bold")
ax.set_ylim(0, 55)
fig.savefig("out/option_2.png", dpi=180, facecolor="white")
plt.close(fig)

# 3: annual crashes where at least one pedestrian was injured or killed
fig, ax = plt.subplots(figsize=(10.5, 5.7), layout="constrained")
base(ax, "Crashes injuring or killing pedestrians remain below 2013", "Crash events with at least one pedestrian injured or killed, annually")
ax.plot(years, df.crashes_with_pedestrian_injury_or_death, color=navy, linewidth=2.7, marker="o", markersize=5)
ax.fill_between(years, df.crashes_with_pedestrian_injury_or_death, color=navy, alpha=.08)
for x in [2013, 2025]:
    val = int(df.loc[df.year.eq(x), "crashes_with_pedestrian_injury_or_death"].iloc[0])
    ax.annotate(f"{val:,}", (x, val), xytext=(0, 12 if x == 2013 else -20), textcoords="offset points", ha="center", color=navy, fontsize=10, fontweight="bold")
ax.set_ylim(0, 4100)
fig.savefig("out/option_3.png", dpi=180, facecolor="white")
plt.close(fig)

payload = {"options": [
 {"id": 1, "metric": "Annual pedestrian casualties (pedestrians injured plus pedestrians killed)", "denominator": "None; raw annual count of people in Brooklyn crashes", "grouping": "Calendar year, 2013–2025", "chart_type": "Line chart", "reason": "A combined injury-and-death count gives a broad measure of the human toll while retaining the full annual trend.", "probability": 0.45, "answer": "Reported pedestrian casualties fell from 3,671 in 2013 to 2,874 in 2025 (21.7% fewer), although they rose from 1,798 in 2020 to 2,874 in 2025.", "interpretation": "This framing answers whether the overall number of pedestrians harmed in reported Brooklyn crashes has improved since 2013: the 2025 count is lower, but the series has risen from its 2020 low. It is defensible because it counts all reported pedestrian injuries and deaths, but it does not account for changes in walking exposure or distinguish injury severity."},
 {"id": 2, "metric": "Annual pedestrians killed", "denominator": "None; raw annual fatality count in Brooklyn", "grouping": "Calendar year, 2013–2025", "chart_type": "Bar chart", "reason": "Fatalities are the most severe road-safety outcome and warrant a separate view rather than being obscured in a combined count.", "probability": 0.30, "answer": "Pedestrian deaths rose from 30 in 2013 to 39 in 2025 (30.0% more), with substantial year-to-year variation.", "interpretation": "This framing addresses whether the most severe pedestrian outcome has improved: the full-year fatality count is higher in 2025 than in 2013. Separating deaths is defensible because a fatality is not equivalent in severity to an injury, but this small, volatile count alone does not describe nonfatal harm or exposure-adjusted risk."},
 {"id": 3, "metric": "Annual crashes with at least one pedestrian injured or killed", "denominator": "None; crash-event count, each qualifying crash counted once", "grouping": "Calendar year, 2013–2025", "chart_type": "Line chart", "reason": "Counting crash events rather than individual casualties shows how often reported crashes harmed pedestrians, without giving extra weight to events with multiple casualties.", "probability": 0.25, "answer": "Crashes involving a pedestrian injury or death fell from 3,498 in 2013 to 2,766 in 2025 (20.9% fewer), after a low of 1,724 in 2020.", "interpretation": "This framing answers whether the annual number of reported crash events that harmed pedestrians is lower than in 2013: it is, though it has risen since its 2020 low. Counting each qualifying crash once is defensible for event frequency, but it hides how many pedestrians were hurt in each crash and does not measure risk per trip or person."}
]}
with open("out/options.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)
    f.write("\n")
print(df.to_string(index=False))
print("\n2013-2025 changes:", round((df.loc[df.year.eq(2025), "pedestrian_casualties"].iloc[0] / df.loc[df.year.eq(2013), "pedestrian_casualties"].iloc[0] - 1)*100, 1), round((df.loc[df.year.eq(2025), "pedestrian_killed"].iloc[0] / df.loc[df.year.eq(2013), "pedestrian_killed"].iloc[0] - 1)*100, 1), round((df.loc[df.year.eq(2025), "crashes_with_pedestrian_injury_or_death"].iloc[0] / df.loc[df.year.eq(2013), "crashes_with_pedestrian_injury_or_death"].iloc[0] - 1)*100, 1))
'
# bash
python3 out/generate_analysis.py
# bash
ls out
# bash
python3 -m json.tool out/options.json

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