from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"

con = duckdb.connect()
annual = con.execute(
    """
    SELECT
        EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
        SUM(number_of_motorist_killed)::BIGINT AS motorist_deaths,
        COUNT(*)::BIGINT AS crashes,
        COUNT(*) FILTER (WHERE number_of_motorist_killed > 0)::BIGINT AS crashes_with_motorist_death
    FROM read_parquet(?)
    WHERE crash_date >= CAST(? AS DATE)
      AND crash_date < CAST(? AS DATE)
    GROUP BY year
    ORDER BY year
    """,
    [str(DATA), "2013-01-01", "2026-01-01"],
).df()

expected_years = list(range(2013, 2026))
if annual["year"].tolist() != expected_years:
    raise ValueError("Expected one row for each complete year from 2013 through 2025")

# Option 1: annual total motorist deaths (no exposure denominator).
values_1 = annual[["year", "motorist_deaths"]].copy()
values_1.to_csv(OUT / "values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(values_1["year"], values_1["motorist_deaths"], marker="o", color="#1769aa")
ax.set_title("Annual motorist deaths in police-reported NYC crashes (2013–2025)", pad=26)
ax.text(
    0.5,
    1.015,
    "Annual count; miles driven are unavailable, so this is not a per-mile risk rate.",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=9,
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Motorists killed (count)")
ax.set_xticks(expected_years)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 2: share of all crashes in a year with one or more motorist deaths.
values_2 = annual[["year", "crashes", "crashes_with_motorist_death"]].copy()
values_2["crashes_with_motorist_death_pct"] = (
    100 * values_2["crashes_with_motorist_death"] / values_2["crashes"]
)
values_2.to_csv(OUT / "values_2.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(
    values_2["year"],
    values_2["crashes_with_motorist_death_pct"],
    marker="o",
    color="#b04a2f",
)
ax.set_title(
    "Share of police-reported NYC crashes involving ≥1 motorist death (2013–2025)",
    pad=26,
)
ax.text(
    0.5,
    1.015,
    "Crash share, not deaths per mile or individual motorist risk; miles driven are unavailable.",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=9,
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Crashes with ≥1 motorist death (%)")
ax.set_xticks(expected_years)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print("Option 1 annual motorist deaths:")
print(values_1.to_string(index=False))
print("\nOption 2 annual crash share:")
print(values_2.to_string(index=False))
