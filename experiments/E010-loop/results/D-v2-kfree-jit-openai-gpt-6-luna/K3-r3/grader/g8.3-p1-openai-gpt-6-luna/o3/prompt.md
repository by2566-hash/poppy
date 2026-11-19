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
metric: Annual motorist deaths minus cyclist deaths
denominator: None; difference between annual death counts
grouping: Year
chart_type: Zero-baseline bar chart
probability: 0.2
WRITTEN ANSWER:
Motorist deaths exceeded cyclist deaths every year; the gap was widest in 2021 at 115 deaths and narrowest in 2019 at 51. This framing answers the size and year-to-year variation of the absolute gap between the two groups. The bars show a positive motorist excess in every year, but the difference alone does not show either group’s exposure-adjusted risk or the reasons for the gap.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,motorist_deaths,cyclist_deaths,motorist_minus_cyclist_deaths
2013,110,11,99
2014,109,20,89
2015,95,15,80
2016,72,18,54
2017,107,27,80
2018,98,10,88
2019,82,31,51
2020,139,29,110
2021,134,19,115
2022,116,19,97
2023,123,31,92
2024,111,24,87
2025,81,23,58

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
ls out
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; print(duckdb.query(f\"SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet('{p}')\").fetchall()); print(duckdb.query(f\"SELECT year(crash_date) AS yr, sum(coalesce(number_of_motorist_killed,0)) AS motorist_deaths, sum(coalesce(number_of_cyclist_killed,0)) AS cyclist_deaths, sum(coalesce(number_of_persons_killed,0)) AS total_deaths FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr\").df().to_string(index=False))"
# bash
python3 -c "import duckdb; print(duckdb.query(\"SELECT year(crash_date) yr, min(crash_date), max(crash_date), count(DISTINCT crash_date) days FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr\").df().to_string(index=False))"
# bash
python3 -c "import duckdb; print(duckdb.query(\"SELECT year(crash_date) yr, min(crash_date) first_date, max(crash_date) last_date, count(DISTINCT crash_date) day_count FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr\").df().to_string(index=False))"
# bash
python3 -c 'import os, json, duckdb, pandas as pd, matplotlib.pyplot as plt
os.makedirs("out", exist_ok=True)
data = duckdb.query("SELECT year(crash_date) AS year, SUM(COALESCE(number_of_motorist_killed, 0))::BIGINT AS motorist_deaths, SUM(COALESCE(number_of_cyclist_killed, 0))::BIGINT AS cyclist_deaths FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= DATE \"2013-01-01\" AND crash_date < DATE \"2026-01-01\" GROUP BY year ORDER BY year").df()
# Ensure the result covers all requested full calendar years.
assert data["year"].tolist() == list(range(2013, 2026))
assert len(data) == 13

def style(ax):
    ax.set_xticks(data["year"])
    ax.set_xticklabels(data["year"].astype(str), rotation=45, ha="right")
    ax.set_xlabel("Year")
    ax.set_ylabel("Deaths (people)")
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

# Option 1: paired line chart of annual counts.
data.to_csv("out/values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(data["year"], data["motorist_deaths"], marker="o", linewidth=2, color="#2457A7", label="Motorists")
ax.plot(data["year"], data["cyclist_deaths"], marker="o", linewidth=2, color="#D97706", label="Cyclists")
style(ax)
ax.set_title("Motorist and cyclist deaths in NYC, 2013–2025")
ax.legend(frameon=False, ncol=2)
fig.tight_layout()
fig.savefig("out/option_1.png", dpi=180)
plt.close(fig)

# Option 2: grouped bars of the same yearly death counts.
data.to_csv("out/values_2.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.5))
width = 0.38
ax.bar(data["year"] - width / 2, data["motorist_deaths"], width, color="#2457A7", label="Motorists")
ax.bar(data["year"] + width / 2, data["cyclist_deaths"], width, color="#D97706", label="Cyclists")
style(ax)
ax.set_title("Annual motorist and cyclist deaths in NYC, 2013–2025")
ax.legend(frameon=False, ncol=2)
fig.tight_layout()
fig.savefig("out/option_2.png", dpi=180)
plt.close(fig)

# Option 3: annual absolute count difference (motorist minus cyclist).
gap = data.copy()
gap["motorist_minus_cyclist_deaths"] = gap["motorist_deaths"] - gap["cyclist_deaths"]
gap.to_csv("out/values_3.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.5))
colors = ["#2457A7" if value >= 0 else "#D97706" for value in gap["motorist_minus_cyclist_deaths"]]
ax.bar(gap["year"], gap["motorist_minus_cyclist_deaths"], color=colors, width=0.72)
ax.axhline(0, color="#333333", linewidth=0.8)
ax.set_xticks(gap["year"])
ax.set_xticklabels(gap["year"].astype(str), rotation=45, ha="right")
ax.set_xlabel("Year")
ax.set_ylabel("More motorist than cyclist deaths (people)")
ax.set_title("Annual motorist–cyclist death-count gap in NYC, 2013–2025")
ax.grid(axis="y", alpha=0.25)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("out/option_3.png", dpi=180)
plt.close(fig)
print(data.to_string(index=False))
print(gap[["year", "motorist_minus_cyclist_deaths"]].to_string(index=False))'
# bash
python3 -c 'import os, duckdb, matplotlib.pyplot as plt
os.makedirs("out", exist_ok=True)
data = duckdb.query("SELECT year(crash_date) AS year, SUM(COALESCE(number_of_motorist_killed, 0))::BIGINT AS motorist_deaths, SUM(COALESCE(number_of_cyclist_killed, 0))::BIGINT AS cyclist_deaths FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= make_date(2013, 1, 1) AND crash_date < make_date(2026, 1, 1) GROUP BY year ORDER BY year").df()
assert data["year"].tolist() == list(range(2013, 2026))
assert len(data) == 13

def style(ax):
    ax.set_xticks(data["year"])
    ax.set_xticklabels(data["year"].astype(str), rotation=45, ha="right")
    ax.set_xlabel("Year")
    ax.set_ylabel("Deaths (people)")
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

data.to_csv("out/values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(data["year"], data["motorist_deaths"], marker="o", linewidth=2, color="#2457A7", label="Motorists")
ax.plot(data["year"], data["cyclist_deaths"], marker="o", linewidth=2, color="#D97706", label="Cyclists")
style(ax)
ax.set_title("Motorist and cyclist deaths in NYC, 2013–2025")
ax.legend(frameon=False, ncol=2)
fig.tight_layout()
fig.savefig("out/option_1.png", dpi=180)
plt.close(fig)

data.to_csv("out/values_2.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.5))
width = 0.38
ax.bar(data["year"] - width / 2, data["motorist_deaths"], width, color="#2457A7", label="Motorists")
ax.bar(data["year"] + width / 2, data["cyclist_deaths"], width, color="#D97706", label="Cyclists")
style(ax)
ax.set_title("Annual motorist and cyclist deaths in NYC, 2013–2025")
ax.legend(frameon=False, ncol=2)
fig.tight_layout()
fig.savefig("out/option_2.png", dpi=180)
plt.close(fig)

gap = data.copy()
gap["motorist_minus_cyclist_deaths"] = gap["motorist_deaths"] - gap["cyclist_deaths"]
gap.to_csv("out/values_3.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.5))
colors = ["#2457A7" if value >= 0 else "#D97706" for value in gap["motorist_minus_cyclist_deaths"]]
ax.bar(gap["year"], gap["motorist_minus_cyclist_deaths"], color=colors, width=0.72)
ax.axhline(0, color="#333333", linewidth=0.8)
ax.set_xticks(gap["year"])
ax.set_xticklabels(gap["year"].astype(str), rotation=45, ha="right")
ax.set_xlabel("Year")
ax.set_ylabel("More motorist than cyclist deaths (people)")
ax.set_title("Annual motorist–cyclist death-count gap in NYC, 2013–2025")
ax.grid(axis="y", alpha=0.25)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("out/option_3.png", dpi=180)
plt.close(fig)
print(data.to_string(index=False))
print(gap[["year", "motorist_minus_cyclist_deaths"]].to_string(index=False))'
# bash
python3 -c 'import json
options = {
  "options": [
    {
      "id": 1,
      "metric": "Annual number of deaths by road-user type",
      "denominator": "None; annual death counts",
      "grouping": "Year and road-user type (motorist or cyclist)",
      "chart_type": "Two-series line chart",
      "reason": "A paired time-series chart makes the year-to-year trends and persistent difference between the two groups easy to follow.",
      "probability": 0.45,
      "answer": "Motorist deaths exceeded cyclist deaths in every year, ranging from 72–139 annually versus 10–31; motorist deaths peaked at 139 in 2020, while cyclist deaths peaked at 31 in 2019 and 2023.",
      "interpretation": "This framing directly answers how the two annual death counts changed from 2013 through 2025. The lines show motorist deaths consistently higher, while cyclist deaths fluctuate at a lower level; the counts do not adjust for travel exposure or explain causes."
    },
    {
      "id": 2,
      "metric": "Annual number of deaths by road-user type",
      "denominator": "None; annual death counts",
      "grouping": "Year and road-user type (motorist or cyclist)",
      "chart_type": "Grouped bar chart",
      "reason": "Side-by-side bars make the absolute motorist-versus-cyclist count comparison within each individual year especially direct.",
      "probability": 0.35,
      "answer": "Grouped annual counts show motorists outnumbered cyclists in all 13 years, with the widest gap in 2021 (134 versus 19) and the narrowest in 2019 (82 versus 31).",
      "interpretation": "This framing compares the absolute number of deaths in each group year by year. The paired bars make the size of each yearly difference easy to inspect, but they do not compare risk adjusted for the number of people or trips in each group."
    },
    {
      "id": 3,
      "metric": "Annual motorist deaths minus cyclist deaths",
      "denominator": "None; difference between annual death counts",
      "grouping": "Year",
      "chart_type": "Zero-baseline bar chart",
      "reason": "Plotting the count difference directly isolates how many more motorist than cyclist deaths were recorded in each year.",
      "probability": 0.2,
      "answer": "Motorist deaths exceeded cyclist deaths every year; the gap was widest in 2021 at 115 deaths and narrowest in 2019 at 51.",
      "interpretation": "This framing answers the size and year-to-year variation of the absolute gap between the two groups. The bars show a positive motorist excess in every year, but the difference alone does not show either group’s exposure-adjusted risk or the reasons for the gap."
    }
  ]
}
with open("out/options.json", "w", encoding="utf-8") as f:
    json.dump(options, f, ensure_ascii=False, indent=2)
    f.write("\\n")'
# bash
python3 -c "import json; p='out/options.json'; d=json.load(open(p)); print(len(d['options']), sum(o['probability'] for o in d['options']))"
# bash
python3 -c "p='out/options.json'; s=open(p).read(); assert s.endswith(chr(92)+'n'); open(p,'w').write(s[:-2]+chr(10))" && python3 -c "import json; d=json.load(open('out/options.json')); print('options:', len(d['options']), 'probability sum:', sum(o['probability'] for o in d['options']))"
# bash
python3 -c "import os, json, pandas as pd; d=json.load(open('out/options.json')); assert [o['id'] for o in d['options']]==[1,2,3]; assert abs(sum(o['probability'] for o in d['options'])-1)<1e-9; base=pd.read_csv('out/values_1.csv'); assert base.equals(pd.read_csv('out/values_2.csv')); v3=pd.read_csv('out/values_3.csv'); assert (v3.motorist_minus_cyclist_deaths == v3.motorist_deaths-v3.cyclist_deaths).all(); assert all(os.path.exists(f'out/option_{i}.png') and os.path.exists(f'out/values_{i}.csv') for i in (1,2,3)); print('All option files present; plotted values and gaps agree.')"

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