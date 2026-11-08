from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

con = duckdb.connect()
query = f"""
SELECT
  year(crash_date)::INTEGER AS year,
  count(*)::BIGINT AS crash_rows,
  min(crash_date) AS first_date,
  max(crash_date) AS last_date,
  sum(number_of_motorist_killed)::BIGINT AS motorist_deaths,
  sum(number_of_cyclist_killed)::BIGINT AS cyclist_deaths,
  count(*) FILTER (WHERE number_of_motorist_killed IS NULL)::BIGINT AS motorist_null_rows,
  count(*) FILTER (WHERE number_of_cyclist_killed IS NULL)::BIGINT AS cyclist_null_rows
FROM read_parquet('{(ROOT / 'data' / 'crashes.parquet').as_posix()}')
WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
GROUP BY year
ORDER BY year
"""
annual = con.execute(query).df()
assert annual["year"].tolist() == list(range(2013, 2026))
assert annual[["motorist_null_rows", "cyclist_null_rows"]].to_numpy().sum() == 0

# Direct annual counts: deaths recorded in each crash row, summed by road-user type.
counts = annual[["year", "motorist_deaths", "cyclist_deaths"]].copy()
counts.to_csv(OUT / "values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.plot(counts.year, counts.motorist_deaths, marker="o", linewidth=2.3,
        color="#2864a5", label="Motorists")
ax.plot(counts.year, counts.cyclist_deaths, marker="o", linewidth=2.3,
        color="#e2762b", label="Cyclists")
ax.set(title="Motorist and cyclist deaths in NYC by year",
       xlabel="Crash year", ylabel="Deaths (sum of people killed)")
ax.set_xticks(counts.year)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180)
plt.close(fig)

# Composition among the two queried road-user types; excludes pedestrian deaths.
shares = counts.copy()
total = shares.motorist_deaths + shares.cyclist_deaths
shares["motorist_share_pct"] = shares.motorist_deaths / total * 100
shares["cyclist_share_pct"] = shares.cyclist_deaths / total * 100
shares.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")
fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.bar(shares.year, shares.motorist_share_pct, color="#2864a5", width=0.72,
       label="Motorist share")
ax.bar(shares.year, shares.cyclist_share_pct, bottom=shares.motorist_share_pct,
       color="#e2762b", width=0.72, label="Cyclist share")
ax.set(title="Share of motorist and cyclist deaths in NYC by year",
       xlabel="Crash year", ylabel="Share of motorist + cyclist deaths (%)",
       ylim=(0, 100))
ax.set_xticks(shares.year)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False, loc="upper right")
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180)
plt.close(fig)

print(annual.to_string(index=False))
print("\nOption 2 composition values:")
print(shares.to_string(index=False))
print("\nRows included:", int(annual.crash_rows.sum()))
print("Rows in requested years with NULL needed death values:",
      int(annual.motorist_null_rows.sum() + annual.cyclist_null_rows.sum()))
print("Annual coverage:")
print(annual[["year", "first_date", "last_date", "crash_rows"]].to_string(index=False))
