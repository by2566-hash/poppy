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

QUESTION ASKED: How many pedestrians were killed in NYC motor vehicle crashes each year from 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Pedestrians killed
denominator: None; annual count
grouping: Crash year and recorded borough (including not recorded)
chart_type: Stacked bar chart
probability: 0.3
WRITTEN ANSWER:
Summing the borough segments gives these annual totals: 2013: 176; 2014: 133; 2015: 133; 2016: 149; 2017: 127; 2018: 123; 2019: 131; 2020: 101; 2021: 132; 2022: 135; 2023: 107; 2024: 124; 2025: 119; the chart also shows the recorded-borough composition, with missing boroughs retained as Not recorded.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,borough,pedestrians_killed
2013,BRONX,25
2013,BROOKLYN,30
2013,MANHATTAN,29
2013,QUEENS,45
2013,STATEN ISLAND,3
2013,Not recorded,44
2014,BRONX,10
2014,BROOKLYN,42
2014,MANHATTAN,25
2014,QUEENS,26
2014,STATEN ISLAND,5
2014,Not recorded,25
2015,BRONX,11
2015,BROOKLYN,46
2015,MANHATTAN,18
2015,QUEENS,25
2015,STATEN ISLAND,5
2015,Not recorded,28
2016,BRONX,14
2016,BROOKLYN,20
2016,MANHATTAN,30
2016,QUEENS,19
2016,STATEN ISLAND,3
2016,Not recorded,63
2017,BRONX,10
2017,BROOKLYN,20
2017,MANHATTAN,21
2017,QUEENS,23
2017,STATEN ISLAND,4
2017,Not recorded,49
2018,BRONX,10
2018,BROOKLYN,23
2018,MANHATTAN,13
2018,QUEENS,31
2018,STATEN ISLAND,3
2018,Not recorded,43
2019,BRONX,9
2019,BROOKLYN,33
2019,MANHATTAN,20
2019,QUEENS,26
2019,STATEN ISLAND,2
2019,Not recorded,41
2020,BRONX,10
2020,BROOKLYN,17
2020,MANHATTAN,9
2020,QUEENS,20
2020,STATEN ISLAND,3
2020,Not recorded,42
2021,BRONX,5
2021,BROOKLYN,32
2021,MANHATTAN,17
2021,QUEENS,16
2021,STATEN ISLAND,2
2021,Not recorded,60
2022,BRONX,13
2022,BROOKLYN,23
2022,MANHATTAN,18
2022,QUEENS,14
2022,STATEN ISLAND,3
2022,Not recorded,64
... (truncated)

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
# bash
# bash
# bash
python3 -c "import duckdb; print(duckdb.sql(\"select min(crash_date), max(crash_date), count(*), sum(number_of_pedestrians_killed) from read_parquet('./data/crashes.parquet')\").fetchall()); print(duckdb.sql(\"select extract(year from crash_date)::int as year, sum(number_of_pedestrians_killed)::bigint as pedestrians_killed from read_parquet('./data/crashes.parquet') where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1 order by 1\").df().to_string(index=False))"
# bash
source = "read_parquet(\"./data/crashes.parquet\")"
base = f"select extract(year from crash_date)::int year, number_of_pedestrians_killed killed from {source} where crash_date >= date \"2013-01-01\" and crash_date < date \"2026-01-01\""
annual = con.execute(f"select year, sum(killed)::bigint pedestrians_killed from ({base}) group by year order by year").df()
annual.to_csv("out/values_1.csv", index=False)
ax.bar(annual.year.astype(str), annual.pedestrians_killed, color="#2878B5")
ax.set(title="Pedestrians killed in NYC motor vehicle crashes", xlabel="Crash year", ylabel="Pedestrians killed")
fig.tight_layout(); fig.savefig("out/option_1.png", dpi=160); plt.close(fig)
borough = con.execute(f"select year, coalesce(borough, \"Not recorded\") borough, sum(killed)::bigint pedestrians_killed from ({base}) group by year, borough order by year, borough").df()
borough.to_csv("out/values_2.csv", index=False)
wide = borough.pivot(index="year", columns="borough", values="pedestrians_killed").fillna(0)
ax.set(title="Pedestrians killed by crash year and recorded borough", xlabel="Crash year", ylabel="Pedestrians killed")
ax.legend(title="Borough", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
ax.grid(axis="y", alpha=.25); fig.tight_layout(); fig.savefig("out/option_2.png", dpi=160); plt.close(fig)
monthly = con.execute(f"select year, extract(month from crash_date)::int month, sum(killed)::bigint pedestrians_killed from ({base}) group by year, month order by year, month").df()
full = pd.MultiIndex.from_product([range(2013, 2026), range(1, 13)], names=["year", "month"]).to_frame(index=False)
monthly = full.merge(monthly, on=["year", "month"], how="left").fillna({"pedestrians_killed": 0})
monthly.to_csv("out/values_3.csv", index=False)
pivot = monthly.pivot(index="year", columns="month", values="pedestrians_killed")
ax.set(title="Monthly pedestrian deaths by crash year", xlabel="Crash month", ylabel="Crash year")
fig.tight_layout(); fig.savefig("out/option_3.png", dpi=160); plt.close(fig)
all_yearly = annual.set_index("year").pedestrians_killed.astype(int).to_dict()
answer_list = "; ".join(f"{year}: {value}" for year, value in all_yearly.items())
 {"id": 1, "metric": "Pedestrians killed", "denominator": "None; annual count", "grouping": "Crash year", "chart_type": "Vertical bar chart", "reason": "A direct annual bar chart makes year-to-year differences and individual totals easy to compare.", "probability": 0.45, "answer": f"Pedestrians killed by year: {answer_list}."},
 {"id": 2, "metric": "Pedestrians killed", "denominator": "None; annual count", "grouping": "Crash year and recorded borough (including not recorded)", "chart_type": "Stacked bar chart", "reason": "The borough stacks show each annual total while revealing how recorded locations contribute to it.", "probability": 0.30, "answer": f"Summing the borough segments gives these annual totals: {answer_list}; the chart also shows the recorded-borough composition, with missing boroughs retained as Not recorded."},
 {"id": 3, "metric": "Pedestrians killed", "denominator": "None; monthly counts summed to annual totals", "grouping": "Crash year and crash month", "chart_type": "Annotated heatmap", "reason": "Monthly shading preserves the requested annual totals while showing how pedestrian deaths vary within each year.", "probability": 0.25, "answer": f"Summing the monthly cells gives these annual totals: {answer_list}; the heatmap also displays their month-by-month distribution."}
with open("out/options.json", "w") as f: json.dump(options, f, indent=2); f.write("\n")
print("borough sums match:", borough.groupby("year").pedestrians_killed.sum().astype(int).to_dict() == all_yearly)
print("monthly sums match:", monthly.groupby("year").pedestrians_killed.sum().astype(int).to_dict() == all_yearly)
# bash
source = "read_parquet(\"./data/crashes.parquet\")"
base = f"select extract(year from crash_date)::int as crash_year, number_of_pedestrians_killed as killed, borough, extract(month from crash_date)::int as crash_month from {source} where crash_date >= make_date(2013,1,1) and crash_date < make_date(2026,1,1)"
annual = con.execute(f"select crash_year as year, sum(killed)::bigint pedestrians_killed from ({base}) group by crash_year order by crash_year").df()
annual.to_csv("out/values_1.csv", index=False)
ax.bar(annual.year.astype(str), annual.pedestrians_killed, color="#2878B5")
ax.set(title="Pedestrians killed in NYC motor vehicle crashes", xlabel="Crash year", ylabel="Pedestrians killed")
fig.tight_layout(); fig.savefig("out/option_1.png", dpi=160); plt.close(fig)
borough = con.execute(f"select crash_year as year, coalesce(borough, \"Not recorded\") as borough, sum(killed)::bigint pedestrians_killed from ({base}) group by crash_year, borough order by crash_year, borough").df()
borough.to_csv("out/values_2.csv", index=False)
wide = borough.pivot(index="year", columns="borough", values="pedestrians_killed").fillna(0)
ax.set(title="Pedestrians killed by crash year and recorded borough", xlabel="Crash year", ylabel="Pedestrians killed")
ax.set_xticklabels(wide.index.astype(str), rotation=0); ax.legend(title="Borough", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
ax.grid(axis="y", alpha=.25); fig.tight_layout(); fig.savefig("out/option_2.png", dpi=160); plt.close(fig)
monthly = con.execute(f"select crash_year as year, crash_month as month, sum(killed)::bigint pedestrians_killed from ({base}) group by crash_year, crash_month order by crash_year, crash_month").df()
full = pd.MultiIndex.from_product([range(2013, 2026), range(1, 13)], names=["year", "month"]).to_frame(index=False)
monthly = full.merge(monthly, on=["year", "month"], how="left").fillna({"pedestrians_killed": 0})
monthly.to_csv("out/values_3.csv", index=False)
pivot = monthly.pivot(index="year", columns="month", values="pedestrians_killed")
ax.set_yticks(range(len(pivot.index)), pivot.index.astype(str)); ax.set(title="Monthly pedestrian deaths by crash year", xlabel="Crash month", ylabel="Crash year")
fig.tight_layout(); fig.savefig("out/option_3.png", dpi=160); plt.close(fig)
all_yearly = annual.set_index("year").pedestrians_killed.astype(int).to_dict()
answer_list = "; ".join(f"{year}: {value}" for year, value in all_yearly.items())
 {"id": 1, "metric": "Pedestrians killed", "denominator": "None; annual count", "grouping": "Crash year", "chart_type": "Vertical bar chart", "reason": "A direct annual bar chart makes year-to-year differences and individual totals easy to compare.", "probability": 0.45, "answer": f"Pedestrians killed by year: {answer_list}."},
 {"id": 2, "metric": "Pedestrians killed", "denominator": "None; annual count", "grouping": "Crash year and recorded borough (including not recorded)", "chart_type": "Stacked bar chart", "reason": "The borough stacks show each annual total while revealing how recorded locations contribute to it.", "probability": 0.30, "answer": f"Summing the borough segments gives these annual totals: {answer_list}; the chart also shows the recorded-borough composition, with missing boroughs retained as Not recorded."},
 {"id": 3, "metric": "Pedestrians killed", "denominator": "None; monthly counts summed to annual totals", "grouping": "Crash year and crash month", "chart_type": "Annotated heatmap", "reason": "Monthly shading preserves the requested annual totals while showing how pedestrian deaths vary within each year.", "probability": 0.25, "answer": f"Summing the monthly cells gives these annual totals: {answer_list}; the heatmap also displays their month-by-month distribution."}
with open("out/options.json", "w") as f: json.dump(options, f, indent=2); f.write("\n")
print("borough sums match:", borough.groupby("year").pedestrians_killed.sum().astype(int).to_dict() == all_yearly)
print("monthly sums match:", monthly.groupby("year").pedestrians_killed.sum().astype(int).to_dict() == all_yearly)
# bash
source = "read_parquet(\"./data/crashes.parquet\")"
base = f"select extract(year from crash_date)::int as crash_year, number_of_pedestrians_killed as killed, borough, extract(month from crash_date)::int as crash_month from {source} where crash_date >= make_date(2013,1,1) and crash_date < make_date(2026,1,1)"
annual = con.execute(f"select crash_year as year, sum(killed)::bigint pedestrians_killed from ({base}) group by crash_year order by crash_year").df()
annual.to_csv("out/values_1.csv", index=False)
ax.bar(annual.year.astype(str), annual.pedestrians_killed, color="#2878B5")
ax.set(title="Pedestrians killed in NYC motor vehicle crashes", xlabel="Crash year", ylabel="Pedestrians killed")
fig.tight_layout(); fig.savefig("out/option_1.png", dpi=160); plt.close(fig)
borough = con.execute(f"select crash_year as year, borough, sum(killed)::bigint pedestrians_killed from ({base}) group by crash_year, borough order by crash_year, borough").df()
borough["borough"] = borough.borough.fillna("Not recorded")
borough.to_csv("out/values_2.csv", index=False)
wide = borough.pivot(index="year", columns="borough", values="pedestrians_killed").fillna(0)
ax.set(title="Pedestrians killed by crash year and recorded borough", xlabel="Crash year", ylabel="Pedestrians killed")
ax.set_xticklabels(wide.index.astype(str), rotation=0); ax.legend(title="Borough", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
ax.grid(axis="y", alpha=.25); fig.tight_layout(); fig.savefig("out/option_2.png", dpi=160); plt.close(fig)
monthly = con.execute(f"select crash_year as year, crash_month as month, sum(killed)::bigint pedestrians_killed from ({base}) group by crash_year, crash_month order by crash_year, crash_month").df()
full = pd.MultiIndex.from_product([range(2013, 2026), range(1, 13)], names=["year", "month"]).to_frame(index=False)
monthly = full.merge(monthly, on=["year", "month"], how="left").fillna({"pedestrians_killed": 0})
monthly.to_csv("out/values_3.csv", index=False)
pivot = monthly.pivot(index="year", columns="month", values="pedestrians_killed")
ax.set_yticks(range(len(pivot.index)), pivot.index.astype(str)); ax.set(title="Monthly pedestrian deaths by crash year", xlabel="Crash month", ylabel="Crash year")
fig.tight_layout(); fig.savefig("out/option_3.png", dpi=160); plt.close(fig)
all_yearly = annual.set_index("year").pedestrians_killed.astype(int).to_dict()
answer_list = "; ".join(f"{year}: {value}" for year, value in all_yearly.items())
 {"id": 1, "metric": "Pedestrians killed", "denominator": "None; annual count", "grouping": "Crash year", "chart_type": "Vertical bar chart", "reason": "A direct annual bar chart makes year-to-year differences and individual totals easy to compare.", "probability": 0.45, "answer": f"Pedestrians killed by year: {answer_list}."},
 {"id": 2, "metric": "Pedestrians killed", "denominator": "None; annual count", "grouping": "Crash year and recorded borough (including not recorded)", "chart_type": "Stacked bar chart", "reason": "The borough stacks show each annual total while revealing how recorded locations contribute to it.", "probability": 0.30, "answer": f"Summing the borough segments gives these annual totals: {answer_list}; the chart also shows the recorded-borough composition, with missing boroughs retained as Not recorded."},
 {"id": 3, "metric": "Pedestrians killed", "denominator": "None; monthly counts summed to annual totals", "grouping": "Crash year and crash month", "chart_type": "Annotated heatmap", "reason": "Monthly shading preserves the requested annual totals while showing how pedes
... (code lines filtered to those about filters, windows and denominators; truncated)

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR07: The output does not present the open-data death counts as the official NYC toll. The counts are qualified when the written output (answer, interpretation or declared framing fields) ties them to this data in any wording: reported, recorded, police-reported crashes, in this dataset (e.g. 'pedestrians killed in reported motor vehicle crashes' qualifies). A qualification or source note that appears only inside the chart image does not count, and a chart title without one is fine when the written output has it. FAIL only when no such qualification appears in the written output (Bo 2026-11-04, refined 2026-11-06).
- tr_CAUSAL: The output makes no causal attribution (e.g. 'because of the pandemic') that the data cannot support.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.