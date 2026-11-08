from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


out = Path("out")
out.mkdir(exist_ok=True)
db = duckdb.connect()
df = db.execute(
    """
    SELECT
        year(crash_date) AS year,
        sum(number_of_motorist_killed)::BIGINT AS motorist_deaths,
        sum(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
    FROM read_parquet('./data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY 1
    ORDER BY 1
    """
).df()
assert df["year"].tolist() == list(range(2013, 2026))
assert df[["motorist_deaths", "cyclist_deaths"]].notna().all().all()

df.to_csv(out / "values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(df.year, df.motorist_deaths, marker="o", linewidth=2.4, label="Motorists")
ax.plot(df.year, df.cyclist_deaths, marker="o", linewidth=2.4, label="Cyclists")
ax.set(
    title="Motorist and cyclist deaths in NYC, 2013–2025",
    xlabel="Year",
    ylabel="Deaths (people)",
)
ax.set_xticks(df.year)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(out / "option_1.png", dpi=180)
plt.close(fig)

shares = df.copy()
total = shares.motorist_deaths + shares.cyclist_deaths
shares["motorist_share_percent"] = shares.motorist_deaths / total * 100
shares["cyclist_share_percent"] = shares.cyclist_deaths / total * 100
shares.to_csv(out / "values_2.csv", index=False, float_format="%.6f")

fig, ax = plt.subplots(figsize=(10, 5.8))
ax.bar(shares.year, shares.motorist_share_percent, label="Motorists", color="#3973ac")
ax.bar(
    shares.year,
    shares.cyclist_share_percent,
    bottom=shares.motorist_share_percent,
    label="Cyclists",
    color="#e38b35",
)
ax.set(
    title="Share of motorist and cyclist deaths in NYC, 2013–2025",
    xlabel="Year",
    ylabel="Share of these deaths (%)",
    ylim=(0, 100),
)
ax.set_xticks(shares.year)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False, loc="center left", bbox_to_anchor=(1, 0.5))
fig.tight_layout()
fig.savefig(out / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print(df.to_string(index=False))
print("\nShares (%):")
print(shares[["year", "motorist_share_percent", "cyclist_share_percent"]].round(2).to_string(index=False))
