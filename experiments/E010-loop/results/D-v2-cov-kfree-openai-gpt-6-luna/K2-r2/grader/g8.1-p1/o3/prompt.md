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
metric: Share of each calendar year’s reported crashes
denominator: All reported crashes in the same year
grouping: Weekday within year (2013–2025)
chart_type: Multi-series line chart
probability: 0.2
WRITTEN ANSWER:
Friday had the largest weekday share in every year (15.32%–16.25%), while Sunday had the smallest (11.47%–13.61%). This year-by-year share framing answers how the weekday mix varied from 2013 through 2025: Friday was highest and Sunday lowest in each year, while the lines show modest annual shifts in their shares. Annual percentages make the weekday pattern comparable across years with different total crash counts, but this view does not give pooled crash totals or crashes per calendar date. The date filter selects 2013–2025; 136,969/2,269,187 file rows (6.04%) fall outside that window. Rows omitted because crash_date is NULL: none; partial years included: none.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,dow,weekday,crashes,year_total,share_pct,source_rows,rows_in_2013_2025,rows_outside_requested_dates,outside_requested_dates_pct,null_crash_date_rows
2013,0,Sunday,24136,203742,11.84635470349756,2269187,2132218,136969,6.036038457826526,0
2013,1,Monday,29454,203742,14.456518538151192,2269187,2132218,136969,6.036038457826526,0
2013,2,Tuesday,30216,203742,14.830520952969932,2269187,2132218,136969,6.036038457826526,0
2013,3,Wednesday,29395,203742,14.427560345927692,2269187,2132218,136969,6.036038457826526,0
2013,4,Thursday,29727,203742,14.59051152928704,2269187,2132218,136969,6.036038457826526,0
2013,5,Friday,33111,203742,16.251435639190742,2269187,2132218,136969,6.036038457826526,0
2013,6,Saturday,27703,203742,13.597098290975842,2269187,2132218,136969,6.036038457826526,0
2014,0,Sunday,23847,206046,11.57362918959844,2269187,2132218,136969,6.036038457826526,0
2014,1,Monday,29963,206046,14.54189841103443,2269187,2132218,136969,6.036038457826526,0
2014,2,Tuesday,30791,206046,14.943750424662454,2269187,2132218,136969,6.036038457826526,0
2014,3,Wednesday,30588,206046,14.845228735330943,2269187,2132218,136969,6.036038457826526,0
2014,4,Thursday,30778,206046,14.937441153917089,2269187,2132218,136969,6.036038457826526,0
2014,5,Friday,32417,206046,15.73289459635227,2269187,2132218,136969,6.036038457826526,0
2014,6,Saturday,27662,206046,13.425157489104375,2269187,2132218,136969,6.036038457826526,0
2015,0,Sunday,26259,217708,12.061568706708067,2269187,2132218,136969,6.036038457826526,0
2015,1,Monday,31061,217708,14.267275433148988,2269187,2132218,136969,6.036038457826526,0
2015,2,Tuesday,32685,217708,15.013228728388484,2269187,2132218,136969,6.036038457826526,0
2015,3,Wednesday,32405,217708,14.884616091278223,2269187,2132218,136969,6.036038457826526,0
2015,4,Thursday,32909,217708,15.116118838076687,2269187,2132218,136969,6.036038457826526,0
2015,5,Friday,34408,217708,15.804655777463392,2269187,2132218,136969,6.036038457826526,0
2015,6,Saturday,27981,217708,12.852536424936153,2269187,2132218,136969,6.036038457826526,0
2016,0,Sunday,26367,229833,11.472242889402304,2269187,2132218,136969,6.036038457826526,0
2016,1,Monday,32291,229833,14.049766569639695,2269187,2132218,136969,6.036038457826526,0
2016,2,Tuesday,34314,229833,14.929970891908471,2269187,2132218,136969,6.036038457826526,0
2016,3,Wednesday,34236,229833,14.89603320671966,2269187,2132218,136969,6.036038457826526,0
2016,4,Thursday,34682,229833,15.09008715023517,2269187,2132218,136969,6.036038457826526,0
2016,5,Friday,37147,229833,16.16260502190721,2269187,2132218,136969,6.036038457826526,0
2016,6,Saturday,30796,229833,13.399294270187484,2269187,2132218,136969,6.036038457826526,0
2017,0,Sunday,27464,231007,11.888817221988944,2269187,2132218,136969,6.036038457826526,0
2017,1,Monday,33049,231007,14.30649287683923,2269187,2132218,136969,6.036038457826526,0
2017,2,Tuesday,33721,231007,14.597393152588449,2269187,2132218,136969,6.036038457826526,0
2017,3,Wednesday,33856,231007,14.655832940127356,2269187,2132218,136969,6.036038457826526,0
2017,4,Thursday,35356,231007,15.305163912781865,2269187,2132218,136969,6.036038457826526,0
2017,5,Friday,36921,231007,15.982632560918068,2269187,2132218,136969,6.036038457826526,0
2017,6,Saturday,30640,231007,13.26366733475609,2269187,2132218,136969,6.036038457826526,0
2018,0,Sunday,26589,231564,11.48235477017153,2269187,2132218,136969,6.036038457826526,0
2018,1,Monday,33594,231564,14.50743638907602,2269187,2132218,136969,6.036038457826526,0
2018,2,Tuesday,34469,231564,14.885301687654383,2269187,2132218,136969,6.036038457826526,0
2018,3,Wednesday,33916,231564,14.64649081895286,2269187,2132218,136969,6.036038457826526,0
2018,4,Thursday,35585,231564,15.367241885612616,2269187,2132218,136969,6.036038457826526,0
2018,5,Friday,36928,231564,15.947211138173463,2269187,2132218,136969,6.036038457826526,0
2018,6,Saturday,30483,231564,13.163963310359124,2269187,2132218,136969,6.036038457826526,0
2019,0,Sunday,24702,211486,11.680205781943013,2269187,2132218,136969,6.036038457826526,0
2019,1,Monday,30478,211486,14.411355834428756,2269187,2132218,136969,6.036038457826526,0
2019,2,Tuesday,31833,211486,15.052060183652818,2269187,2132218,136969,6.036038457826526,0
2019,3,Wednesday,30932,211486,14.62602725475918,2269187,2132218,136969,6.036038457826526,0
2019,4,Thursday,31693,211486,14.985861948308637,2269187,2132218,136969,6.036038457826526,0
2019,5,Friday,33724,211486,15.94620920533747,2269187,2132218,136969,6.036038457826526,0
2019,6,Saturday,28124,211486,13.298279791570128,2269187,2132218,136969,6.036038457826526,0
2020,0,Sunday,13843,112918,12.259338635115748,2269187,2132218,136969,6.036038457826526,0
2020,1,Monday,15846,112918,14.033192227988453,2269187,2132218,136969,6.036038457826526,0
2020,2,Tuesday,16184,112918,14.332524486795728,2269187,2132218,136969,6.036038457826526,0
2020,3,Wednesday,16258,112918,14.398058768309747,2269187,2132218,136969,6.036038457826526,0
2020,4,Thursday,16817,112918,14.893108273260244,2269187,2132218,136969,6.036038457826526,0
2020,5,Friday,18104,112918,16.03287341256487,2269187,2132218,136969,6.036038457826526,0
2020,6,Saturday,15866,112918,14.050904195965211,2269187,2132218,136969,6.036038457826526,0
2021,0,Sunday,14292,110558,12.927151359467429,2269187,2132218,136969,6.036038457826526,0
2021,1,Monday,15567,110558,14.080392192333436,2269187,2132218,136969,6.036038457826526,0
2021,2,Tuesday,15674,110558,14.17717397203278,2269187,2132218,136969,6.036038457826526,0
2021,3,Wednesday,15794,110558,14.285714285714286,2269187,2132218,136969,6.036038457826526,0
... (truncated)

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(f\"DESCRIBE SELECT * FROM read_parquet('{p}')\").fetchdf().to_string(index=False)); print(c.execute(f\"SELECT COUNT(*) n, MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) FILTER (WHERE crash_date IS NULL) null_date FROM read_parquet('{p}')\").fetchdf().to_string(index=False))"
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"SELECT year(crash_date) y, COUNT(*) n, MIN(crash_date) lo, MAX(crash_date) hi FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").fetchdf().to_string(index=False)); print(c.execute(f\"SELECT COUNT(*) total, COUNT(*) FILTER (WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01') in_period, COUNT(*) FILTER (WHERE crash_date IS NULL) null_date FROM read_parquet('{p}')\").fetchdf().to_string(index=False)); print(c.execute(f\"SELECT dayofweek(crash_date) dow, dayname(crash_date) day, COUNT(*) n FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1,2 ORDER BY 1\").fetchdf().to_string(index=False))"
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=f\"SELECT dayofweek(crash_date) dow, dayname(crash_date) weekday, COUNT(*) crashes, COUNT(DISTINCT crash_date) dates FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1,2 ORDER BY 1\"; print(c.execute(q).fetchdf().to_string(index=False)); print(c.execute(f\"SELECT year(crash_date) yr, dayofweek(crash_date) dow, dayname(crash_date) weekday, COUNT(*) crashes FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1,2,3 ORDER BY 1,2\").fetchdf().to_string(index=False))"
# bash
# bash
source = "data/crashes.parquet"
base = f"FROM read_parquet(\"{source}\") WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\''"
week = db.execute(f"SELECT dayofweek(crash_date) AS dow, dayname(crash_date) AS weekday, COUNT(*) AS crashes, COUNT(DISTINCT crash_date) AS dates FROM {base} GROUP BY 1,2 ORDER BY 1").fetchdf()
week["share_pct"] = 100 * week.crashes / week.crashes.sum()
week["crashes_per_calendar_day"] = week.crashes / week.dates
week.to_csv(out / "values_1.csv", index=False)
bars = ax.bar(week.weekday, week.crashes, color="#3676a8")
ax.set(title="NYC reported crashes by weekday, 2013–2025", ylabel="Reported crashes", xlabel="Day of week")
fig.tight_layout(); fig.savefig(out / "option_1.png", dpi=170); plt.close(fig)
week[["weekday", "dates", "crashes", "crashes_per_calendar_day", "share_pct"]].to_csv(out / "values_2.csv", index=False)
bars = ax.bar(week.weekday, week.crashes_per_calendar_day, color="#4b9675")
ax.bar_label(bars, labels=[f"{x:.1f}" for x in week.crashes_per_calendar_day], padding=3, fontsize=9)
ax.set(title="Average NYC reported crashes per calendar date, by weekday (2013–2025)", ylabel="Crashes per occurrence of weekday", xlabel="Day of week")
ax.set_ylim(0, week.crashes_per_calendar_day.max() * 1.12)
fig.tight_layout(); fig.savefig(out / "option_2.png", dpi=170); plt.close(fig)
year = db.execute(f"SELECT year(crash_date) AS year, dayofweek(crash_date) AS dow, dayname(crash_date) AS weekday, COUNT(*) AS crashes FROM {base} GROUP BY 1,2,3 ORDER BY 1,2").fetchdf()
year["year_total"] = year.groupby("year").crashes.transform("sum")
year["share_pct"] = 100 * year.crashes / year.year_total
year.to_csv(out / "values_3.csv", index=False)
for name, grp in year.groupby("weekday", sort=False):
    ax.plot(grp.year, grp.share_pct, marker="o", linewidth=1.8, markersize=3, label=name)
ax.set(title="Weekday share of NYC reported crashes by year, 2013–2025", ylabel="Share of that year’s crashes (%)", xlabel="Year", xticks=list(range(2013, 2026)))
fig.tight_layout(); fig.savefig(out / "option_3.png", dpi=170); plt.close(fig)
print("TOTAL", int(week.crashes.sum()), "weekday aggregate:\n", week.to_string(index=False))
print("Annual weekday leaders/laggards:")
for yr, grp in year.groupby("year"):
    print(int(yr), grp.loc[grp.crashes.idxmax(), "weekday"], round(grp.loc[grp.crashes.idxmax(), "share_pct"], 2), grp.loc[grp.crashes.idxmin(), "weekday"], round(grp.loc[grp.crashes.idxmin(), "share_pct"], 2))
# bash
source = "data/crashes.parquet"
base = f"read_parquet(\"{source}\") WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\''"
week = db.execute(f"SELECT dayofweek(crash_date) AS dow, dayname(crash_date) AS weekday, COUNT(*) AS crashes, COUNT(DISTINCT crash_date) AS dates FROM {base} GROUP BY 1,2 ORDER BY 1").fetchdf()
week["share_pct"] = 100 * week.crashes / week.crashes.sum()
week["crashes_per_calendar_day"] = week.crashes / week.dates
week.to_csv(out / "values_1.csv", index=False)
bars = ax.bar(week.weekday, week.crashes, color="#3676a8")
ax.set(title="NYC reported crashes by weekday, 2013–2025", ylabel="Reported crashes", xlabel="Day of week")
fig.tight_layout(); fig.savefig(out / "option_1.png", dpi=170); plt.close(fig)
week[["weekday", "dates", "crashes", "crashes_per_calendar_day", "share_pct"]].to_csv(out / "values_2.csv", index=False)
bars = ax.bar(week.weekday, week.crashes_per_calendar_day, color="#4b9675")
ax.bar_label(bars, labels=[f"{x:.1f}" for x in week.crashes_per_calendar_day], padding=3, fontsize=9)
ax.set(title="Average NYC reported crashes per calendar date, by weekday (2013–2025)", ylabel="Crashes per occurrence of weekday", xlabel="Day of week")
ax.set_ylim(0, week.crashes_per_calendar_day.max() * 1.12); ax.grid(axis="y", alpha=.22)
fig.tight_layout(); fig.savefig(out / "option_2.png", dpi=170); plt.close(fig)
year = db.execute(f"SELECT year(crash_date) AS year, dayofweek(crash_date) AS dow, dayname(crash_date) AS weekday, COUNT(*) AS crashes FROM {base} GROUP BY 1,2,3 ORDER BY 1,2").fetchdf()
year["year_total"] = year.groupby("year").crashes.transform("sum")
year["share_pct"] = 100 * year.crashes / year.year_total
year.to_csv(out / "values_3.csv", index=False)
for name, grp in year.groupby("weekday", sort=False): ax.plot(grp.year, grp.share_pct, marker="o", linewidth=1.8, markersize=3, label=name)
ax.set(title="Weekday share of NYC reported crashes by year, 2013–2025", ylabel="Share of that year’s crashes (%)", xlabel="Year", xticks=list(range(2013, 2026)))
fig.tight_layout(); fig.savefig(out / "option_3.png", dpi=170); plt.close(fig)
print("TOTAL", int(week.crashes.sum()), "weekday aggregate:\n", week.to_string(index=False))
print("Annual weekday leaders/laggards:")
for yr, grp in year.groupby("year"):
    print(int(yr), hi.weekday, round(hi.share_pct, 2), lo.weekday, round(lo.share_pct, 2))
# bash
total=int(db.execute("SELECT COUNT(*) FROM read_parquet('\''data/crashes.parquet'\'')").fetchone()[0])
scope=int(db.execute("SELECT COUNT(*) FROM read_parquet('\''data/crashes.parquet'\'') WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\''").fetchone()[0])
null_dates=int(db.execute("SELECT COUNT(*) FROM read_parquet('\''data/crashes.parquet'\'') WHERE crash_date IS NULL").fetchone()[0])
meta={"source_rows":total,"rows_in_2013_2025":scope,"rows_outside_requested_dates":total-scope,"outside_requested_dates_pct":100*(total-scope)/total,"null_crash_date_rows":null_dates}
    p=out/f"values_{i}.csv"
excluded=f"The date filter selects 2013–2025; {total-scope:,}/{total:,} file rows ({(total-scope)/total:.2%}) fall outside that window. Rows omitted for a NULL crash_date: {null_dates:,}/{total:,} ({null_dates/total:.2%}); partial years included: none."
 {"id":1,"metric":"Number of reported crashes","denominator":"None (raw count)","grouping":"Weekday, pooled across 2013–2025","chart_type":"Bar chart","reason":"Raw totals directly describe how many reported crashes fell on each weekday over the requested period.","probability":0.55,"answer":"Friday had the most crashes (338,800; 15.89% of the period total), while Sunday had the fewest (257,544; 12.08%).","interpretation":f"This pooled-count framing answers how many reported crashes occurred on each weekday across 2013–2025, with Friday highest and Sunday lowest. Counting crashes directly is a clear overall distribution, but this view does not adjust for weekday-date frequency or reveal year-to-year changes. {excluded}"},
 {"id":2,"metric":"Average number of reported crashes per calendar date","denominator":"Number of calendar dates of each weekday in 2013–2025","grouping":"Weekday, pooled across 2013–2025","chart_type":"Bar chart","reason":"Per-date averages adjust for the small difference in the number of occurrences of each weekday during the period.","probability":0.25,"answer":"Friday averaged 499.7 crashes per Friday, the highest rate, versus 379.9 per Sunday, the lowest.","interpretation":f"This rate framing answers how the weekday distribution looks after accounting for the number of dates available for each weekday: Fridays averaged 499.7 crashes per date and Sundays 379.9. Dividing pooled counts by the corresponding weekday-date counts is defensible because some weekdays occurred 678 times while others occurred 679 times; this pooled average does not show year-to-year changes. {excluded}"},
 {"id":3,"metric":"Share of each calendar year’s reported crashes","denominator":"All reported crashes in the same year","grouping":"Weekday within year (2013–2025)","chart_type":"Multi-series line chart","reason":"Annual shares show whether the weekday mix is consistent over time without conflating it with changes in total crash volume.","probability":0.20,"answer":"Friday had the largest weekday share in every year (15.32%–16.25%), while Sunday had the smallest (11.47%–13.61%).","interpretation":f"This year-by-year share framing answers how the weekday mix varied from 2013 through 2025: Friday was highest and Sunday lowest in each year, while the lines show modest annual shifts in their shares. Annual percentages make the weekday pattern comparable across years with different total crash counts, but this view does not give pooled crash totals or crashes per calendar date. {excluded}"}
with open(out/"options.json","w") as f: json.dump({"options":options},f,indent=2,ensure_ascii=False); f.write("\n")
print("wrote out/options.json")
# bash
python -c 'import json; from pathlib import Path; p=Path("out/options.json"); d=json.loads(p.read_text());
for o in d["options"]: o["interpretation"]=o["interpretation"].replace("Rows omitted for a NULL crash_date: 0/2,269,187 (0.00%); partial years included: none.", "Rows omitted because crash_date is NULL: none; partial years included: none.")
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n"); print("probability sum:",sum(o["probability"] for o in d["options"])); print("options:",len(d["options"])); print("interpretations:",[len(o["interpretation"].split(". ")) for o in d["options"]])'
# bash
python -c 'import json, math; from pathlib import Path; p=Path("out"); d=json.loads((p/"options.json").read_text()); expected={"id","metric","denominator","grouping","chart_type","reason","probability","answer","interpretation"}; assert all(set(o)==expected for o in d["options"]); assert abs(sum(o["probability"] for o in d["options"])-1)<1e-9; assert all((p/f"option_{i}.png").is_file() and (p/f"values_{i}.csv").is_file() for i in (1,2,3)); assert all(len(o["interpretation"].split(". "))==4 for o in d["options"]); print("Validated options JSON schema, probabilities, interpretation length, and all output files.")'
... (code lines filtered to those about filters, windows and denominators)

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