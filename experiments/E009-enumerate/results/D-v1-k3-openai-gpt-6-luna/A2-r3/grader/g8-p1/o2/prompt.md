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
metric: People injured and killed per reported crash
denominator: Total reported crashes in each period, expressed per 100 crashes
grouping: Night (8pm–5:59am) versus day (6am–7:59pm)
chart_type: Two-panel horizontal bar chart
probability: 0.38
WRITTEN ANSWER:
These records cannot establish whether night is more dangerous per trip or mile because traffic exposure is not recorded; per 100 reported crashes, night had 40.45 people injured and 0.308 killed, compared with 31.01 injured and 0.111 killed by day.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
period,crash_count,persons_injured,persons_killed,injuries_per_100_crashes,deaths_per_100_crashes
Night,559004,226106.000000,1719.000000,40.448011,0.307511
Day,1710183,530247.000000,1898.000000,31.005278,0.110982

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT COUNT(*) rows, MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) FILTER (WHERE crash_time IS NULL) missing_time, COUNT(DISTINCT crash_date) days FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT typeof(crash_time) FROM read_parquet(?) LIMIT 1", [p]).fetchall())'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT COUNT(*) AS n_rows, MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) FILTER (WHERE crash_time IS NULL) missing_time, COUNT(DISTINCT crash_date) days FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT typeof(crash_time) FROM read_parquet(?) LIMIT 1", [p]).fetchall())'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT COUNT(*) AS n_rows, MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) FILTER (WHERE crash_time IS NULL) missing_time, COUNT(DISTINCT crash_date) distinct_dates FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT typeof(crash_time) FROM read_parquet(?) LIMIT 1", [p]).fetchall())'
# bash
# bash
p="data/crashes.parquet"
dates=int(con.execute("SELECT COUNT(DISTINCT crash_date) FROM read_parquet(?)",[p]).fetchone()[0])
SELECT CASE WHEN EXTRACT(HOUR FROM crash_time) >= 20 OR EXTRACT(HOUR FROM crash_time) < 6 THEN ''Night'' ELSE ''Day'' END AS period,
 SUM(COALESCE(number_of_persons_injured,0)) AS persons_injured,
 SUM(COALESCE(number_of_persons_killed,0)) AS persons_killed,
 COUNT(*) FILTER (WHERE COALESCE(number_of_persons_injured,0)>0) AS injury_crashes,
 COUNT(*) FILTER (WHERE COALESCE(number_of_persons_injured,0)>0 OR COALESCE(number_of_persons_killed,0)>0) AS casualty_crashes,
 COUNT(*) FILTER (WHERE COALESCE(number_of_persons_killed,0)>0) AS fatal_crashes
FROM read_parquet(?) GROUP BY period ORDER BY CASE period WHEN ''Night'' THEN 1 ELSE 2 END
base["observed_dates"]=dates
base["clock_hours_per_day"]=base["period"].map({"Night":10,"Day":14})
base["crashes_per_clock_hour"]=base.crash_count/(base.observed_dates*base.clock_hours_per_day)
base["injuries_per_100_crashes"]=100*base.persons_injured/base.crash_count
base["deaths_per_100_crashes"]=100*base.persons_killed/base.crash_count
base["pct_crashes_with_injury_or_fatality"]=100*base.casualty_crashes/base.crash_count
base["pct_fatal_crashes"]=100*base.fatal_crashes/base.crash_count
order=["Night","Day"]
values1=base[["period","crash_count","observed_dates","clock_hours_per_day","crashes_per_clock_hour"]]
values1.to_csv(out/"values_1.csv",index=False,float_format="%.6f")
values2=base[["period","crash_count","persons_injured","persons_killed","injuries_per_100_crashes","deaths_per_100_crashes"]]
values2.to_csv(out/"values_2.csv",index=False,float_format="%.6f")
values3.to_csv(out/"values_3.csv",index=False,float_format="%.6f")
labels=["Night\n8pm–5:59am","Day\n6am–7:59pm"]
bars=ax.bar(labels,base.crashes_per_clock_hour,color=colors,width=.58)
ax.set_ylabel("Reported crashes per clock-hour per recorded date")
ax.set_title("NYC reported crashes by time of day")
ax.text(.5,1.01,"Night/day rates account for the different number of hours in each period",transform=ax.transAxes,ha="center",fontsize=9)
ax.set_ylim(0,max(base.crashes_per_clock_hour)*1.18)
fig.tight_layout(); fig.savefig(out/"option_1.png",dpi=180,bbox_inches="tight"); plt.close(fig)
b1=ax.bar([i-width/2 for i in x],base.injuries_per_100_crashes,width,label="People injured",color="#315b7d")
b2=ax.bar([i+width/2 for i in x],base.deaths_per_100_crashes,width,label="People killed",color="#b45045")
ax.set_ylim(0,max(base.injuries_per_100_crashes)*1.22)
fig.tight_layout(); fig.savefig(out/"option_2.png",dpi=180,bbox_inches="tight"); plt.close(fig)
b1=ax.bar([i-width/2 for i in x],base.pct_crashes_with_injury_or_fatality,width,label="At least one person injured or killed",color="#315b7d")
b2=ax.bar([i+width/2 for i in x],base.pct_fatal_crashes,width,label="At least one person killed",color="#b45045")
fig.tight_layout(); fig.savefig(out/"option_3.png",dpi=180,bbox_inches="tight"); plt.close(fig)
print("Distinct crash dates:",dates)
print(base[["period","crash_count","persons_injured","persons_killed","injury_crashes","casualty_crashes","fatal_crashes","crashes_per_clock_hour","injuries_per_100_crashes","deaths_per_100_crashes","pct_crashes_with_injury_or_fatality","pct_fatal_crashes"]].to_string(index=False))
# bash
p="data/crashes.parquet"
dates=int(con.execute("SELECT COUNT(DISTINCT crash_date) FROM read_parquet(?)",[p]).fetchone()[0])
SELECT CASE WHEN EXTRACT(HOUR FROM crash_time) >= 20 OR EXTRACT(HOUR FROM crash_time) < 6 THEN 0 ELSE 1 END AS period_order,
 SUM(COALESCE(number_of_persons_injured,0)) AS persons_injured,
 SUM(COALESCE(number_of_persons_killed,0)) AS persons_killed,
 COUNT(*) FILTER (WHERE COALESCE(number_of_persons_injured,0)>0) AS injury_crashes,
 COUNT(*) FILTER (WHERE COALESCE(number_of_persons_injured,0)>0 OR COALESCE(number_of_persons_killed,0)>0) AS casualty_crashes,
 COUNT(*) FILTER (WHERE COALESCE(number_of_persons_killed,0)>0) AS fatal_crashes
base["period"]=base.period_order.map({0:"Night",1:"Day"})
base["observed_dates"]=dates
base["clock_hours_per_day"]=base["period"].map({"Night":10,"Day":14})
base["crashes_per_clock_hour"]=base.crash_count/(base.observed_dates*base.clock_hours_per_day)
base["injuries_per_100_crashes"]=100*base.persons_injured/base.crash_count
base["deaths_per_100_crashes"]=100*base.persons_killed/base.crash_count
base["pct_crashes_with_injury_or_fatality"]=100*base.casualty_crashes/base.crash_count
base["pct_fatal_crashes"]=100*base.fatal_crashes/base.crash_count
base=base[["Night","Day"]==base.period] if False else base
base=base.set_index("period").loc[["Night","Day"]].reset_index()
values1=base[["period","crash_count","observed_dates","clock_hours_per_day","crashes_per_clock_hour"]]
values1.to_csv(out/"values_1.csv",index=False,float_format="%.6f")
values2=base[["period","crash_count","persons_injured","persons_killed","injuries_per_100_crashes","deaths_per_100_crashes"]]
values2.to_csv(out/"values_2.csv",index=False,float_format="%.6f")
values3.to_csv(out/"values_3.csv",index=False,float_format="%.6f")
labels=["Night\n8pm–5:59am","Day\n6am–7:59pm"]
bars=ax.bar(labels,base.crashes_per_clock_hour,color=colors,width=.58)
ax.set_ylabel("Reported crashes per clock-hour per recorded date")
ax.set_title("NYC reported crashes by time of day")
ax.text(.5,1.01,"Night/day rates account for the different number of hours in each period",transform=ax.transAxes,ha="center",fontsize=9)
ax.spines[["top","right"]].set_visible(False); ax.set_ylim(0,max(base.crashes_per_clock_hour)*1.18)
fig.tight_layout(); fig.savefig(out/"option_1.png",dpi=180,bbox_inches="tight"); plt.close(fig)
b1=ax.bar([i-width/2 for i in x],base.injuries_per_100_crashes,width,label="People injured",color="#315b7d")
b2=ax.bar([i+width/2 for i in x],base.deaths_per_100_crashes,width,label="People killed",color="#b45045")
ax.legend(frameon=False); ax.spines[["top","right"]].set_visible(False); ax.set_ylim(0,max(base.injuries_per_100_crashes)*1.22)
fig.tight_layout(); fig.savefig(out/"option_2.png",dpi=180,bbox_inches="tight"); plt.close(fig)
b1=ax.bar([i-width/2 for i in x],base.pct_crashes_with_injury_or_fatality,width,label="At least one person injured or killed",color="#315b7d")
b2=ax.bar([i+width/2 for i in x],base.pct_fatal_crashes,width,label="At least one person killed",color="#b45045")
fig.tight_layout(); fig.savefig(out/"option_3.png",dpi=180,bbox_inches="tight"); plt.close(fig)
print("Distinct crash dates:",dates)
print(base[["period","crash_count","persons_injured","persons_killed","injury_crashes","casualty_crashes","fatal_crashes","crashes_per_clock_hour","injuries_per_100_crashes","deaths_per_100_crashes","pct_crashes_with_injury_or_fatality","pct_fatal_crashes"]].to_string(index=False))
# bash
labels=["Night\n8pm–5:59am","Day\n6am–7:59pm"]
v1=pd.read_csv(out/"values_1.csv")
v2=pd.read_csv(out/"values_2.csv")
v3=pd.read_csv(out/"values_3.csv")
bars=ax.bar(labels,v1.crashes_per_clock_hour,color=colors,width=.58)
ax.set_ylabel("Average reported crashes per clock-hour\n(across 5,094 recorded dates)")
ax.set_title("NYC reported crashes by time of day",pad=12)
ax.spines[["top","right"]].set_visible(False); ax.set_ylim(0,max(v1.crashes_per_clock_hour)*1.18)
fig.tight_layout(); fig.savefig(out/"option_1.png",dpi=180,bbox_inches="tight"); plt.close(fig)
for ax,col,title in zip(axs,["injuries_per_100_crashes","deaths_per_100_crashes"],["People injured per 100 crashes","People killed per 100 crashes"]):
 vals=v2[col]; bars=ax.barh(["Night","Day"],vals,color=colors)
fig.tight_layout(); fig.savefig(out/"option_2.png",dpi=180,bbox_inches="tight"); plt.close(fig)
 vals=v3[col]; bars=ax.barh(["Night","Day"],vals,color=colors)
fig.tight_layout(); fig.savefig(out/"option_3.png",dpi=180,bbox_inches="tight"); plt.close(fig)
 {"id":1,"metric":"Reported crash frequency","denominator":"Clock-hours in each period across the 5,094 dates with recorded crashes (10 night hours or 14 daytime hours per date)","grouping":"Night (8pm–5:59am) versus day (6am–7:59pm)","chart_type":"Bar chart","reason":"A careful analyst may choose this framing to compare collision frequency while accounting for the unequal lengths of the night and daytime periods.","probability":0.34,"answer":"These records cannot establish whether night is more dangerous per trip or mile because traffic exposure is not recorded; they show 10.97 reported crashes per clock-hour per recorded date at night versus 23.98 during the day."},
 {"id":2,"metric":"People injured and killed per reported crash","denominator":"Total reported crashes in each period, expressed per 100 crashes","grouping":"Night (8pm–5:59am) versus day (6am–7:59pm)","chart_type":"Two-panel horizontal bar chart","reason":"A careful analyst may choose this framing to compare the human toll per collision, including both nonfatal injuries and deaths.","probability":0.38,"answer":"These records cannot establish whether night is more dangerous per trip or mile because traffic exposure is not recorded; per 100 reported crashes, night had 40.45 people injured and 0.308 killed, compared with 31.01 injured and 0.111 killed by day."},
 {"id":3,"metric":"Share of reported crashes with injured or killed people","denominator":"Total reported crashes in each period","grouping":"Night (8pm–5:59am) versus day (6am–7:59pm)","chart_type":"Two-panel horizontal bar chart","reason":"A careful analyst may choose this framing to show how often a reported crash involved casualties, independently of how many people were harmed in each crash.","probability":0.28,"answer":"These records cannot establish whether night is more dangerous per trip or mile because traffic exposure is not recorded; 28.51% of night crashes involved at least one injury or death versus 23.50% of daytime crashes, while fatal crashes were 0.290% versus 0.108%."}
with open(out/"options.json","w") as f: json.dump(options,f,indent=2,ensure_ascii=False); f.write("\n")
# bash
days=(pd.Timestamp("2026-06-11")-pd.Timestamp("2012-07-01")).days+1
v=pd.read_csv(out/"values_1.csv")
v["calendar_dates"]=days
v["crashes_per_clock_hour"]=v.crash_count/(days*v.clock_hours_per_day)
v=v[["period","crash_count","calendar_dates","clock_hours_per_day","crashes_per_clock_hour"]]
v.to_csv(out/"values_1.csv",index=False,float_format="%.6f")
labels=["Night\n8pm–5:59am","Day\n6am–7:59pm"]
fig,ax=plt.subplots(figsize=(8,5)); bars=ax.bar(labels,v.crashes_per_clock_hour,color=["#315b7d","#d48a32"],width=.58)
ax.set_ylabel("Average reported crashes per clock-hour\n(5,103 calendar days, 2012-07-01 to 2026-06-11)")
ax.set_title("NYC reported crashes by time of day",pad=12)
ax.spines[["top","right"]].set_visible(False); ax.set_ylim(0,max(v.crashes_per_clock_hour)*1.18)
f
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
- tr_TR11: Severity per crash (deaths or injuries per crash) is described as such, not as the risk of being on the street at night (no traffic volume by hour exists).
- tr_TR08: NA if the option uses no killed or injured counts. Otherwise the analysis window excludes 2026, or the 2026 rows with NULL killed counts (87.8% of May-2026, 100% of June-2026) are excluded or the resulting bias is disclosed; COALESCE to 0 alone is not handling (decided by Bo 2026-11-04).
- tr_NIGHTDEF: The definition of 'night' (hours) is stated.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.