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
metric: Share of reported crashes with at least one person killed
denominator: All police-reported crashes with a recorded crash time in the period
grouping: Night (8 p.m.–5:59 a.m.) versus day (6 a.m.–7:59 p.m.)
chart_type: bar chart
probability: 0.25
WRITTEN ANSWER:
At least one person was killed in 0.29% of nighttime crashes versus 0.11% of daytime crashes, about 2.7 times the share. This framing answers whether a reported crash was more likely to be fatal at night; the fatal-crash share was higher at night in these data. It isolates deaths rather than combining outcomes, but conditions on a reported crash and lacks traffic-exposure data, so it does not measure fatality risk per road user, trip, or mile.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
period,crashes,fatal_crashes,fatal_share
Night (8 p.m.–5:59 a.m.),559004,1622,0.002901589255175276
Day (6 a.m.–7:59 p.m.),1710183,1847,0.0010800013799692782

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c "import duckdb, pathlib; p=pathlib.Path('out'); print('out:', list(p.iterdir()) if p.exists() else 'missing'); con=duckdb.connect(); print(con.execute(\"select count(*) n, min(crash_date), max(crash_date), count(*) filter (where crash_time is null) time_null, count(*) filter (where crash_date is null) date_null from read_parquet('data/crashes.parquet')\").fetchdf().to_string(index=False)); print(con.execute(\"select extract(hour from crash_time) hr, count(*) n, sum(number_of_persons_injured) injured, sum(number_of_persons_killed) killed, count(*) filter (where number_of_persons_injured > 0 or number_of_persons_killed > 0) injury_or_fatal_crashes from read_parquet('data/crashes.parquet') where crash_time is not null group by hr order by hr\").fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"with x as (select crash_date, extract(hour from crash_time) h, number_of_persons_injured i, number_of_persons_killed k from read_parquet('data/crashes.parquet')), g as (select case when h >= 20 or h < 6 then 'Night (8 p.m.–5:59 a.m.)' else 'Day (6 a.m.–7:59 p.m.)' end period, count(*) crashes, count(*) filter (where i>0 or k>0) injury_or_fatal_crashes, sum(i) injured_people, sum(k) killed_people, count(*) filter (where k>0) fatal_crashes from x group by period) select * from g order by period\").fetchdf().to_string(index=False)); print(c.execute(\"select count(distinct crash_date) dates, date_diff('day', min(crash_date), max(crash_date))+1 days_inclusive from read_parquet('data/crashes.parquet')\").fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"with x as (select extract(hour from crash_time) h, number_of_persons_injured i, number_of_persons_killed k from read_parquet('data/crashes.parquet')), g as (select case when h>=20 or h<6 then 'Night' else 'Day' end p, count(*) n, count(*) filter(where i>0 or k>0) serious, count(*) filter(where k>0) fatal from x group by p) select p,n,case when p='Night' then n::double/(5094*10) else n::double/(5094*14) end crashes_per_clock_hour, serious, serious::double/n serious_pct, fatal, fatal::double/n fatal_pct from g\").fetchdf().to_string(index=False))"
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt, pathlib; out=pathlib.Path("out"); out.mkdir(exist_ok=True); db=duckdb.connect(); q="""WITH x AS (SELECT crash_date, EXTRACT(hour FROM crash_time)::INTEGER AS h, number_of_persons_injured AS injured, number_of_persons_killed AS killed FROM read_parquet(\"data/crashes.parquet\")), g AS (SELECT CASE WHEN h >= 20 OR h < 6 THEN 1 ELSE 0 END AS night, COUNT(*) AS crashes, COUNT(*) FILTER (WHERE injured > 0 OR killed > 0) AS injury_or_fatal_crashes, COUNT(*) FILTER (WHERE killed > 0) AS fatal_crashes FROM x GROUP BY night), d AS (SELECT COUNT(DISTINCT crash_date) AS days FROM read_parquet(\"data/crashes.parquet\")) SELECT CASE WHEN g.night=1 THEN \"Night (8 p.m.–5:59 a.m.)\" ELSE \"Day (6 a.m.–7:59 p.m.)\" END AS period, g.crashes, g.injury_or_fatal_crashes, g.fatal_crashes, d.days, CASE WHEN g.night=1 THEN d.days*10 ELSE d.days*14 END AS clock_hours FROM g CROSS JOIN d ORDER BY g.night DESC"""; df=db.execute(q).fetchdf(); df["crashes_per_clock_hour"]=df.crashes/df.clock_hours; df["injury_or_fatal_share"]=df.injury_or_fatal_crashes/df.crashes; df["fatal_share"]=df.fatal_crashes/df.crashes; order=["Night (8 p.m.–5:59 a.m.)","Day (6 a.m.–7:59 p.m.)"]; df["period"]=pd.Categorical(df.period,categories=order,ordered=True); df=df.sort_values("period"); specs=[(1,["period","crashes","clock_hours","crashes_per_clock_hour"],"crashes_per_clock_hour","Reported crashes per clock-hour","Average reported motor-vehicle crashes per clock-hour\nNight: 8 p.m.–5:59 a.m.; Day: 6 a.m.–7:59 p.m.","crashes/hour"),(2,["period","crashes","injury_or_fatal_crashes","injury_or_fatal_share"],"injury_or_fatal_share","injury_or_fatal_share","Share of reported crashes involving injury or death\nNight: 8 p.m.–5:59 a.m.; Day: 6 a.m.–7:59 p.m.","share"),(3,["period","crashes","fatal_crashes","fatal_share"],"fatal_share","fatal_share","Share of reported crashes with at least one death\nNight: 8 p.m.–5:59 a.m.; Day: 6 a.m.–7:59 p.m.","share")]; colors=["#b44d28","#477da8"]; plt.rcParams.update({"font.size":11,"axes.titlesize":14});
for id,cols,col,ylabel,title,fmt in specs:
 data=df[cols].copy(); data["period"]=data.period.astype(str); data.to_csv(out/f"values_{id}.csv",index=False); fig,ax=plt.subplots(figsize=(8.0,5.0)); bars=ax.bar(data.period,data[col],color=colors,width=.58); ax.set_ylabel(ylabel); ax.set_title(title,pad=14); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True); ax.spines[["top","right"]].set_visible(False); 
 for bar,val in zip(bars,data[col]): ax.annotate(f"{val:.1%}" if fmt=="share" else f"{val:.2f}", (bar.get_x()+bar.get_width()/2,bar.get_height()),xytext=(0,5),textcoords="offset points",ha="center",va="bottom",fontweight="bold");
 ax.margins(y=.18); fig.tight_layout(); fig.savefig(out/f"option_{id}.png",dpi=170,bbox_inches="tight"); plt.close(fig); print(f"option_{id}:\n{data.to_string(index=False)}")'
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt, pathlib; out=pathlib.Path("out"); out.mkdir(exist_ok=True); db=duckdb.connect(); q="""WITH x AS (SELECT crash_date, EXTRACT(hour FROM crash_time)::INTEGER AS h, number_of_persons_injured AS injured, number_of_persons_killed AS killed FROM read_parquet(\"data/crashes.parquet\")), g AS (SELECT CASE WHEN h >= 20 OR h < 6 THEN 1 ELSE 0 END AS night, COUNT(*) AS crashes, COUNT(*) FILTER (WHERE injured > 0 OR killed > 0) AS injury_or_fatal_crashes, COUNT(*) FILTER (WHERE killed > 0) AS fatal_crashes FROM x GROUP BY night), d AS (SELECT COUNT(DISTINCT crash_date) AS days FROM read_parquet(\"data/crashes.parquet\")) SELECT CASE WHEN g.night=1 THEN '\''Night (8 p.m.–5:59 a.m.)'\'' ELSE '\''Day (6 a.m.–7:59 p.m.)'\'' END AS period, g.crashes, g.injury_or_fatal_crashes, g.fatal_crashes, d.days, CASE WHEN g.night=1 THEN d.days*10 ELSE d.days*14 END AS clock_hours FROM g CROSS JOIN d ORDER BY g.night DESC"""; df=db.execute(q).fetchdf(); df["crashes_per_clock_hour"]=df.crashes/df.clock_hours; df["injury_or_fatal_share"]=df.injury_or_fatal_crashes/df.crashes; df["fatal_share"]=df.fatal_crashes/df.crashes; order=["Night (8 p.m.–5:59 a.m.)","Day (6 a.m.–7:59 p.m.)"]; df["period"]=pd.Categorical(df.period,categories=order,ordered=True); df=df.sort_values("period"); specs=[(1,["period","crashes","clock_hours","crashes_per_clock_hour"],"crashes_per_clock_hour","Reported crashes per clock-hour","Average reported motor-vehicle crashes per clock-hour\nNight: 8 p.m.–5:59 a.m.; Day: 6 a.m.–7:59 p.m.","crashes/hour"),(2,["period","crashes","injury_or_fatal_crashes","injury_or_fatal_share"],"injury_or_fatal_share","Share of reported crashes involving injury or death","Share of reported crashes involving injury or death\nNight: 8 p.m.–5:59 a.m.; Day: 6 a.m.–7:59 p.m.","share"),(3,["period","crashes","fatal_crashes","fatal_share"],"fatal_share","Share of reported crashes with at least one death","Share of reported crashes with at least one death\nNight: 8 p.m.–5:59 a.m.; Day: 6 a.m.–7:59 p.m.","share")]; colors=["#b44d28","#477da8"]; plt.rcParams.update({"font.size":11,"axes.titlesize":14});
for id,cols,col,ylabel,title,fmt in specs:
 data=df[cols].copy(); data["period"]=data.period.astype(str); data.to_csv(out/f"values_{id}.csv",index=False); fig,ax=plt.subplots(figsize=(8.0,5.0)); bars=ax.bar(data.period,data[col],color=colors,width=.58); ax.set_ylabel(ylabel); ax.set_title(title,pad=14); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True); ax.spines[["top","right"]].set_visible(False);
 for bar,val in zip(bars,data[col]): ax.annotate(f"{val:.1%}" if fmt=="share" else f"{val:.2f}", (bar.get_x()+bar.get_width()/2,bar.get_height()),xytext=(0,5),textcoords="offset points",ha="center",va="bottom",fontweight="bold");
 ax.margins(y=.18); fig.tight_layout(); fig.savefig(out/f"option_{id}.png",dpi=170,bbox_inches="tight"); plt.close(fig); print(f"option_{id}:\n{data.to_string(index=False)}")'
# bash
python3 -c 'import pandas as pd, matplotlib.pyplot as plt, matplotlib.ticker as mtick, pathlib; out=pathlib.Path("out"); titles={1:("Average reported motor-vehicle crashes per clock-hour","Reported crashes per clock-hour","crashes_per_clock_hour"),2:("Share of reported crashes involving injury or death","Share of crashes","injury_or_fatal_share"),3:("Share of reported crashes with at least one death","Share of crashes","fatal_share")}; colors=["#b44d28","#477da8"]; plt.rcParams.update({"font.size":11,"axes.titlesize":14});
for i,(title,ylabel,col) in titles.items():
 d=pd.read_csv(out/f"values_{i}.csv"); fig,ax=plt.subplots(figsize=(8,5)); bars=ax.bar(d.period,d[col],color=colors,width=.58); ax.set_ylabel(ylabel); ax.set_title(title+"\nNight: 8 p.m.–5:59 a.m.; Day: 6 a.m.–7:59 p.m.",pad=14); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True); ax.spines[["top","right"]].set_visible(False);
 if i>1: ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1,decimals=1)); ax.set_ylim(0,d[col].max()*1.38);
 for bar,val in zip(bars,d[col]):
  label=(f"{val*100:.2f}%" if i==3 else f"{val:.1%}") if i>1 else f"{val:.2f}"; ax.annotate(label,(bar.get_x()+bar.get_width()/2,bar.get_height()),xytext=(0,5),textcoords="offset points",ha="center",va="bottom",fontweight="bold");
 ax.margins(y=.16); fig.text(.5,.015,"Source: NYC police-reported crashes, July 2012–June 2026; no traffic-exposure denominator.",ha="center",fontsize=9,color="#555555"); fig.tight_layout(rect=[0,.055,1,1]); fig.savefig(out/f"option_{i}.png",dpi=170,bbox_inches="tight"); plt.close(fig)'
# bash
python3 -c 'import pandas as pd, matplotlib.pyplot as plt, matplotlib.ticker as mtick, pathlib; out=pathlib.Path("out"); d=pd.read_csv(out/"values_3.csv"); fig,ax=plt.subplots(figsize=(8,5)); bars=ax.bar(d.period,d.fatal_share,color=["#b44d28","#477da8"],width=.58); ax.set_ylabel("Share of crashes"); ax.set_title("Share of reported crashes with at least one death\nNight: 8 p.m.–5:59 a.m.; Day: 6 a.m.–7:59 p.m.",pad=14); ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1,decimals=2)); ax.set_ylim(0,d.fatal_share.max()*1.38); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True); ax.spines[["top","right"]].set_visible(False);
for bar,val in zip(bars,d.fatal_share): ax.annotate(f"{val*100:.2f}%",(bar.get_x()+bar.get_width()/2,bar.get_height()),xytext=(0,5),textcoords="offset points",ha="center",va="bottom",fontweight="bold");
ax.margins(y=.16); fig.text(.5,.015,"Source: NYC police-reported crashes, July 2012–June 2026; no traffic-exposure denominator.",ha="center",fontsize=9,color="#555555"); fig.tight_layout(rect=[0,.055,1,1]); fig.savefig(out/"option_3.png",dpi=170,bbox_inches="tight"); plt.close(fig)'
# bash
python3 -c 'import json, pathlib; p=pathlib.Path("out"); data=json.loads((p/"options.json").read_text()); print("options",len(data["options"]),"probability_sum",sum(o["probability"] for o in data["options"])); print("files",[(x.name,x.stat().st_size) for x in sorted(p.iterdir())]); assert len(data["options"])==3 and abs(sum(o["probability"] for o in data["options"])-1)<1e-9; assert all((p/f"option_{i}.png").is_file() and (p/f"values_{i}.csv").is_file() for i in (1,2,3))'

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