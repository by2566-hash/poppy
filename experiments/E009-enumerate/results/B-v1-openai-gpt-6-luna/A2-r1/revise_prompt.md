Revise an analysis based on a reviewer's numbered issues.

Question:
Are NYC's streets more dangerous at night? Make a chart and give a conclusion for a news report.

Data description:
Data file: ./data/crashes.parquet (one row per police-reported motor vehicle crash in New York City; read it with DuckDB or pandas).
Columns: crash_date (DATE), crash_time (TIME), borough (VARCHAR, may be NULL), zip_code, latitude, longitude,
on_street_name, cross_street_name, number_of_persons_injured (INT), number_of_persons_killed (INT),
number_of_pedestrians_injured, number_of_pedestrians_killed, number_of_cyclist_injured, number_of_cyclist_killed,
number_of_motorist_injured, number_of_motorist_killed, contributing_factor_vehicle_1 ... contributing_factor_vehicle_5 (VARCHAR),
collision_id (BIGINT), vehicle_type_code1 ... vehicle_type_code5 (VARCHAR).
Python 3 with duckdb, pandas and matplotlib is available.

Current code:
pwd && python -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"

python -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"

python -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(\"select count(*) n, min(crash_date), max(crash_date), sum(crash_time is null) null_times from read_parquet(?)\", [p]).fetchdf().to_string(index=False)); print(c.execute(\"select extract(hour from crash_time) h, count(*) crashes, sum(case when number_of_persons_injured>0 then 1 else 0 end) injury_crashes, sum(case when number_of_persons_killed>0 then 1 else 0 end) fatal_crashes, sum(coalesce(number_of_persons_injured,0)) injured, sum(coalesce(number_of_persons_killed,0)) killed from read_parquet(?) where crash_time is not null group by 1 order by 1\", [p]).fetchdf().to_string(index=False))"

python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"with x as (select *, extract(hour from crash_time) h from read_parquet(?) where crash_time is not null), y as (select case when h>=20 or h<6 then 'Night (8pm-5:59am)' else 'Day (6am-7:59pm)' end period, * from x) select period,count(*) crashes, sum((coalesce(number_of_persons_injured,0)>0)::int) injury_crashes, sum((coalesce(number_of_persons_killed,0)>0)::int) fatal_crashes, sum(coalesce(number_of_persons_injured,0)) injured_people,sum(coalesce(number_of_persons_killed,0)) killed_people, count(distinct crash_date) dates, sum((number_of_persons_injured is null)::int) null_injured_fields, sum((number_of_persons_killed is null)::int) null_killed_fields from y group by period order by period\", [p]).fetchdf().to_string(index=False)); print(c.execute(\"select count(distinct crash_date) observed_dates, date_diff('day', min(crash_date), max(crash_date))+1 span_days from read_parquet(?)\", [p]).fetchdf().to_string(index=False))"

python -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt
p = "data/crashes.parquet"
con = duckdb.connect()
summary = con.execute("""
select case when extract(hour from crash_time) >= 20 or extract(hour from crash_time) < 6 then 1 else 0 end as is_night,
       count(*) as crashes,
       count(number_of_persons_injured) as known_injury,
       sum((number_of_persons_injured > 0)::int) as injury_crashes,
       count(number_of_persons_killed) as known_fatal,
       sum((number_of_persons_killed > 0)::int) as fatal_crashes,
       min(crash_date) as first_date, max(crash_date) as last_date,
       count(distinct crash_date) as observed_dates
from read_parquet(?) where crash_time is not null group by 1 order by 1
""", [p]).fetchdf()
labels = {0: "Day (6am–7:59pm)", 1: "Night (8pm–5:59am)"}
summary["period"] = summary["is_night"].map(labels)
summary["injury_rate_per_1000"] = 1000 * summary["injury_crashes"] / summary["known_injury"]
summary["fatal_rate_per_1000"] = 1000 * summary["fatal_crashes"] / summary["known_fatal"]
summary["avg_crashes_per_clock_hour_per_day"] = summary.apply(lambda r: r["crashes"] / (r["observed_dates"] * (10 if r["is_night"] else 14)), axis=1)
rows = []
for _, r in summary.iterrows():
    rows.append({"period": r["period"], "outcome": "Crashes with at least one person injured", "events": int(r["injury_crashes"]), "denominator_crashes_with_known_injury": int(r["known_injury"]), "rate_per_1000_crashes": r["injury_rate_per_1000"]})
    rows.append({"period": r["period"], "outcome": "Crashes with at least one person killed", "events": int(r["fatal_crashes"]), "denominator_crashes_with_known_killed": int(r["known_fatal"]), "rate_per_1000_crashes": r["fatal_rate_per_1000"]})
values = pd.DataFrame(rows)
values.to_csv("out/values.csv", index=False)
fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))
colors = ["#4C78A8", "#E45756"]
for ax, rate_col, title, event_col, denominator_col in [
    (axes[0], "injury_rate_per_1000", "Crashes involving injury", "injury_crashes", "known_injury"),
    (axes[1], "fatal_rate_per_1000", "Crashes involving a death", "fatal_crashes", "known_fatal")]:
    vals = [float(summary.loc[summary["is_night"] == i, rate_col].iloc[0]) for i in (0, 1)]
    bars = ax.bar(["Day", "Night"], vals, color=colors, width=0.62)
    ax.set_title(title, fontsize=13, weight="bold", pad=12)
    ax.set_ylabel("Crashes per 1,000 crashes")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(vals) * 1.27)
    for i, (bar, val) in enumerate(zip(bars, vals)):
        rec = summary.loc[summary["is_night"] == i].iloc[0]
        ax.text(bar.get_x() + bar.get_width()/2, val + max(vals)*0.035,
                f"{val:.1f}\n({int(rec[event_col]):,} / {int(rec[denominator_col]):,})",
                ha="center", va="bottom", fontsize=9)
fig.suptitle("Nighttime NYC crashes are more likely to be severe", fontsize=16, weight="bold", y=1.04)
fig.text(0.5, -0.015, "Day: 6am–7:59pm  |  Night: 8pm–5:59am  |  Rates use crashes with a recorded outcome; not adjusted for traffic exposure.", ha="center", fontsize=9, color="#444444")
fig.tight_layout()
fig.savefig("out/initial.png", dpi=180, bbox_inches="tight")
print("Reporting window:", summary["first_date"].min(), "to", summary["last_date"].max(), "| observed dates:", int(summary["observed_dates"].iloc[0]))
for _, r in summary.iterrows():
    print(f"{r[\"period\"]}: {int(r[\"crashes\"]):,} crashes; injury {r[\"injury_rate_per_1000\"]:.2f}/1,000 ({int(r[\"injury_crashes\"]):,}/{int(r[\"known_injury\"]):,}); fatal {r[\"fatal_rate_per_1000\"]:.2f}/1,000 ({int(r[\"fatal_crashes\"]):,}/{int(r[\"known_fatal\"]):,}); average crashes per clock hour/day {r[\"avg_crashes_per_clock_hour_per_day\"]:.2f}")
print("Night/day rate ratios: injury", summary.loc[summary.is_night == 1, "injury_rate_per_1000"].iloc[0] / summary.loc[summary.is_night == 0, "injury_rate_per_1000"].iloc[0], "fatal", summary.loc[summary.is_night == 1, "fatal
... [truncated, 4793 more characters]

Current plotted values (values.csv):
period,outcome,events,denominator_crashes_with_known_outcome,rate_per_1000_crashes
Day (6am–7:59pm),Crashes with at least one person injured,400420,1710168.0,234.14073938934655
Day (6am–7:59pm),Crashes with at least one person killed,1847,1703940.0,1.0839583553411505
Night (8pm–5:59am),Crashes with at least one person injured,158183,559001.0,282.97444906180846
Night (8pm–5:59am),Crashes with at least one person killed,1622,556334.0,2.915514780689298


Current written answer:
Among police-reported crashes from July 2012 through June 2026, nighttime crashes (8pm–5:59am) were more severe: 283 per 1,000 involved an injury, versus 234 by day, and the fatal-crash rate was 2.7 times higher (2.92 vs. 1.08 per 1,000). Crash counts averaged about 11 per nighttime clock-hour per day, compared with 24 during daytime hours. This points to worse outcomes per reported crash at night; without traffic or travel exposure data, it cannot establish that an individual trip is riskier.

Reviewer's issues:
1. The chart note and written answer do not disclose that crashes with a missing `crash_time` were excluded (`where crash_time is not null`). Clarify that the rates describe crashes with a recorded time as well as a recorded outcome.
2. “2.7 times higher” is ambiguous and can mean 3.7 times as high. The shown rates give a ratio of about 2.69, so say “2.7 times as high” (or “about 169% higher”).

Instructions:
- Go through the issues one by one. For each, either fix it, or check it and keep the original if the reviewer was wrong, or state that it cannot be addressed with this data.
- Change nothing the reviewer did not flag: same data, filters, numbers, chart type and wording of the written answer, unless fixing an issue requires it.
- Write and run the revised code yourself. Save the chart to ./out/revised.png and the plotted data to ./out/revised_values.csv, even if only the written answer changes.
- When finished, reply in exactly this format, with one line per issue in the reviewer's numbering:
CHANGES:
1. <fixed | kept | cannot address>: <what you changed, or why you kept it or could not address it>
2. ...
ANSWER: <the revised short written answer, based on the numbers you computed>
