import duckdb
import matplotlib.pyplot as plt
import pandas as pd

DATA = "data/crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

con = duckdb.connect()
counts = con.execute(
    f"""
    SELECT year, road_user, deaths
    FROM (
        SELECT year(crash_date) AS year,
               'Motorist' AS road_user,
               sum(number_of_motorist_killed)::BIGINT AS deaths
        FROM read_parquet('{DATA}')
        WHERE crash_date >= DATE '{START_YEAR}-01-01'
          AND crash_date < DATE '{END_YEAR + 1}-01-01'
        GROUP BY year
        UNION ALL
        SELECT year(crash_date) AS year,
               'Cyclist' AS road_user,
               sum(number_of_cyclist_killed)::BIGINT AS deaths
        FROM read_parquet('{DATA}')
        WHERE crash_date >= DATE '{START_YEAR}-01-01'
          AND crash_date < DATE '{END_YEAR + 1}-01-01'
        GROUP BY year
    )
    ORDER BY year, road_user
    """
).df()

counts.to_csv("out/values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.8))
for road_user, color, marker in [
    ("Motorist", "#315A9B", "o"),
    ("Cyclist", "#D26A32", "s"),
]:
    series = counts[counts["road_user"] == road_user]
    ax.plot(series["year"], series["deaths"], marker=marker, linewidth=2.2,
            markersize=5, label=road_user, color=color)
ax.set_title("Annual deaths by road-user group in NYC police-reported crashes, 2013–2025",
             fontsize=13, pad=25)
fig.text(0.5, 0.92,
         "Counts, not exposure-adjusted rates; full date spans do not prove complete reporting.",
         ha="center", va="center", fontsize=9, color="#444444")
ax.set_xlabel("Crash year")
ax.set_ylabel("Deaths (count)")
ax.set_xticks(range(START_YEAR, END_YEAR + 1, 1))
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
fig.tight_layout(rect=(0, 0, 1, 0.9))
fig.savefig("out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

shares = counts.copy()
shares["combined_deaths_denominator"] = shares.groupby("year")["deaths"].transform("sum")
shares["share_percent"] = (
    100 * shares["deaths"] / shares["combined_deaths_denominator"]
)
shares.to_csv("out/values_2.csv", index=False, float_format="%.4f")

pivot = shares.pivot(index="year", columns="road_user", values="share_percent")
fig, ax = plt.subplots(figsize=(10, 5.8))
ax.bar(pivot.index, pivot["Motorist"], color="#315A9B", label="Motorist")
ax.bar(pivot.index, pivot["Cyclist"], bottom=pivot["Motorist"],
       color="#D26A32", label="Cyclist")
ax.set_title("Annual share of motorist + cyclist deaths in NYC police-reported crashes, 2013–2025",
             fontsize=13, pad=25)
fig.text(0.5, 0.92,
         "Denominator is only motorist and cyclist deaths; not all traffic deaths or exposure-adjusted.",
         ha="center", va="center", fontsize=9, color="#444444")
ax.set_xlabel("Crash year")
ax.set_ylabel("Share of combined motorist + cyclist deaths (%)")
ax.set_xticks(range(START_YEAR, END_YEAR + 1, 1))
ax.tick_params(axis="x", rotation=45)
ax.set_ylim(0, 100)
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False, loc="lower left")
fig.tight_layout(rect=(0, 0, 1, 0.9))
fig.savefig("out/option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
